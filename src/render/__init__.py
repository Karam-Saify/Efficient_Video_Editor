"""FFmpeg renderer: timeline.json → MP4 (cuts + reframe + burned-in ASS captions via libass).

libass shapes Arabic with HarfBuzz and handles RTL with FriBidi, so captions need no pre-processing.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from src.validate import validate

POSITION_ALIGN = {"bottom": 2, "middle": 5, "top": 8}  # ASS numpad alignment, centered
STYLE_DEFAULTS = {
    "font": "Noto Naskh Arabic", "size": 80, "color": "#FFFFFF", "outline_color": "#000000",
    "outline": 4, "bold": True, "position": "bottom", "margin_v": 320,
}


def _ass_color(hex_rgb: str) -> str:
    r, g, b = hex_rgb[1:3], hex_rgb[3:5], hex_rgb[5:7]
    return f"&H00{b}{g}{r}".upper()


def _ass_time(t: float) -> str:
    cs = round(t * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(tl: dict[str, Any], path: Path) -> None:
    cap = tl["captions"]
    st = {**STYLE_DEFAULTS, **cap.get("style", {})}
    w, h = tl["output"]["width"], tl["output"]["height"]
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{st['font']},{st['size']},{_ass_color(st['color'])},&H000000FF,"
        f"{_ass_color(st['outline_color'])},&H80000000,{-1 if st['bold'] else 0},0,0,0,100,100,0,0,1,"
        f"{st['outline']},0,{POSITION_ALIGN[st['position']]},60,60,{st['margin_v']},-1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for it in sorted(cap["items"], key=lambda x: x["start"]):
        text = it["text"].replace("{", "(").replace("}", ")").replace("\n", r"\N")
        lines.append(f"Dialogue: 0,{_ass_time(it['start'])},{_ass_time(it['end'])},Default,,0,0,0,,{text}")
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
        parts.append(f"[{si}:v]trim=start={c['in']}:end={c['out']},setpts=PTS-STARTPTS,fps={fps}[vt{i}]")
        parts.append(_reframe(mode, w, h, f"vt{i}", f"v{i}", i))
        if src.get("has_audio", True):
            parts.append(f"[{si}:a]atrim=start={c['in']}:end={c['out']},asetpts=PTS-STARTPTS,"
                         f"aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            parts.append(f"[{silence_idx}:a]atrim=duration={dur},asetpts=PTS-STARTPTS[a{i}]")
        cat.append(f"[v{i}][a{i}]")
    parts.append(f"{''.join(cat)}concat=n={len(cat)}:v=1:a=1[vc][ac]")
    vout = "vc"
    if ass_path is not None:
        parts.append(f"[vc]ass=filename='{ass_path}':shaping=complex[vs]")
        vout = "vs"
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{vout}]", "-map", "[ac]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    return cmd


def render(tl: dict[str, Any], out: Path, preset: str = "veryfast", crf: int = 20) -> Path:
    errors = validate(tl)
    if errors:
        raise ValueError("invalid timeline:\n" + "\n".join(errors))
    out.parent.mkdir(parents=True, exist_ok=True)
    ass_path = None
    if tl.get("captions", {}).get("items"):
        ass_path = out.with_suffix(".ass")
        write_ass(tl, ass_path)
    subprocess.run(build_command(tl, out, ass_path, preset, crf), check=True)
    return out
