"""FFmpeg renderer: timeline.json → MP4 (cuts + reframe + burned-in ASS captions via libass).

libass shapes Arabic with HarfBuzz and handles RTL with FriBidi. Fonts are the EXP-008 pair (H-0024):
the style font is Noto Sans Arabic (Regular), Latin/digit runs get `{\fnNoto Sans}` tags by the locked
§5.3 rule (src/render/fontrun.py); a character outside both fonts fails the render instead of falling back.

H-0025:
  * caption presets (src/presets.py) are one ASS style each; a Dialogue line uses its caption's preset;
  * zoom effects are punch-ins on the concatenated output: `split` -> centre `crop` by 1/scale -> `scale` back to
    the canvas -> `overlay` with `enable='gte(t,a)*lt(t,b)'`; applied before the captions, so text never zooms;
  * each clip is converted to the canvas frame rate BEFORE `trim`, so a cut point on the canvas frame grid (the
    edit ops snap to it, src/edit/ops.py) keeps an exact frame count per clip and no A/V drift across many cuts.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from src.presets import CAPTION_PRESETS, DEFAULT_PRESET
from src.render.adapter import to_render_model
from src.render.fontrun import FONT_A, tag_lines
from src.validate import validate


def _ass_color(hex_rgb: str, alpha: int = 0) -> str:
    r, g, b = hex_rgb[1:3], hex_rgb[3:5], hex_rgb[5:7]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ass_style(name: str, st: dict[str, Any]) -> str:
    """Bold 0 (Regular files only, EXP-008) and Encoding -1 (libass auto base direction, E6) for every preset."""
    return (f"Style: {name},{FONT_A},{st['size']},{_ass_color(st['color'])},&H000000FF,"
            f"{_ass_color(st['outline_color'], st['outline_alpha'])},{_ass_color(st['back_color'], st['back_alpha'])},"
            f"0,0,0,0,100,100,0,0,{st['border_style']},{st['outline']},{st['shadow']},{st['alignment']},60,60,"
            f"{st['margin_v']},-1")


def _ass_time(t: float) -> str:
    cs = round(t * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(tl: dict[str, Any], path: Path) -> None:
    cap = tl["captions"]
    w, h = tl["output"]["width"], tl["output"]["height"]
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        *(_ass_style(n, st) for n, st in CAPTION_PRESETS.items()),
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for it in sorted(cap["items"], key=lambda x: x["start"]):
        text = tag_lines(it["text"].replace("{", "(").replace("}", ")"))
        style = it.get("style", DEFAULT_PRESET)
        lines.append(f"Dialogue: 0,{_ass_time(it['start'])},{_ass_time(it['end'])},{style},,0,0,0,,{text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _reframe(mode: str, w: int, h: int, label_in: str, label_out: str, i: int) -> str:
    if mode == "fit_pad":
        return (f"[{label_in}]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[{label_out}]")
    if mode == "fit_blur":
        return (f"[{label_in}]split[bg{i}][fg{i}];"
                f"[bg{i}]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bgb{i}];"
                f"[fg{i}]scale={w}:{h}:force_original_aspect_ratio=decrease[fgs{i}];"
                f"[bgb{i}][fgs{i}]overlay=(W-w)/2:(H-h)/2,setsar=1[{label_out}]")
    return (f"[{label_in}]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},setsar=1[{label_out}]")


def build_command(tl: dict[str, Any], out: Path, ass_path: Path | None, preset: str, crf: int) -> list[str]:
    o = tl["output"]
    w, h, fps = o["width"], o["height"], o["fps"]
    mode = o.get("reframe", "crop_center")
    src_ids = list(tl["sources"])
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for sid in src_ids:
        cmd += ["-i", tl["sources"][sid]["path"]]
    silence_idx = len(src_ids)
    cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]

    parts, cat = [], []
    for i, c in enumerate(tl["clips"]):
        si = src_ids.index(c["source"])
        src = tl["sources"][c["source"]]
        dur = c["out"] - c["in"]
        parts.append(f"[{si}:v]fps={fps},trim=start={c['in']}:end={c['out']},setpts=PTS-STARTPTS[vt{i}]")
        parts.append(_reframe(mode, w, h, f"vt{i}", f"v{i}", i))
        if src.get("has_audio", True):
            parts.append(f"[{si}:a]atrim=start={c['in']}:end={c['out']},asetpts=PTS-STARTPTS,"
                         f"aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            parts.append(f"[{silence_idx}:a]atrim=duration={dur},asetpts=PTS-STARTPTS[a{i}]")
        cat.append(f"[v{i}][a{i}]")
    parts.append(f"{''.join(cat)}concat=n={len(cat)}:v=1:a=1[vc][ac]")
    vout = "vc"
    for i, z in enumerate(tl.get("zooms", [])):
        parts.append(f"[{vout}]split[zb{i}][zs{i}];"
                     f"[zs{i}]crop=w=trunc(iw/{z['scale']}/2)*2:h=trunc(ih/{z['scale']}/2)*2,scale={w}:{h},setsar=1[zz{i}];"
                     f"[zb{i}][zz{i}]overlay=0:0:enable='gte(t,{z['at']})*lt(t,{z['end']})'[z{i}]")
        vout = f"z{i}"
    if ass_path is not None:
        parts.append(f"[{vout}]ass=filename='{ass_path}':shaping=complex[vs]")
        vout = "vs"
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{vout}]", "-map", "[ac]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    return cmd


def render(tl: dict[str, Any], out: Path, preset: str = "veryfast", crf: int = 20, *,
           allow_dev: bool = False) -> Path:
    """`tl` is a timeline v0 document; it is validated, then adapted to the internal render model.
    `allow_dev` admits `quarantine/dev/` sources only (ADR-0006, src.validate)."""
    errors = validate(tl, allow_dev=allow_dev)
    if errors:
        raise ValueError("invalid timeline:\n" + "\n".join(map(str, errors)))
    model = to_render_model(tl)
    out.parent.mkdir(parents=True, exist_ok=True)
    ass_path = None
    if model.get("captions", {}).get("items"):
        ass_path = out.with_suffix(".ass")
        write_ass(model, ass_path)
    subprocess.run(build_command(model, out, ass_path, preset, crf), check=True)
    return out
