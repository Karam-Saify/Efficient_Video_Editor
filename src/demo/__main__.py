"""python -m src.demo --video <path> --ops <ops.json> --out out/ [--language auto] [--model large-v3-turbo]

See src/demo/__init__.py for the steps, the outputs and the ops.json format.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from src.captions import captions_from_words, words_from_transcript
from src.common import ROOT, cache_dir, probe, read_json, video_id, write_json
from src.demo import resolve_time, resolve_words
from src.edit import ops as edit_ops
from src.edit.history import History
from src.edit.ops import EditContext, OpError, total_ms

SOURCE_ID = "src0"
CANVAS = {"width": 1080, "height": 1920, "fps": 30}


class DemoError(Exception):
    def __init__(self, step: str, reason: str) -> None:
        super().__init__(f"{step}: {reason}")


def _ingest(video: Path, model: str, language: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    from src.ingest.__main__ import transcript_name

    cmd = [sys.executable, "-m", "src.ingest", str(video), "--model", model, "--language", language, "--no-scenes"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise DemoError("ingest", (r.stderr.strip().splitlines() or [f"exit {r.returncode}"])[-1])
    d = cache_dir(video_id(video))
    tr_p = d / transcript_name(model, language)
    if not tr_p.is_file():
        raise DemoError("ingest", f"no transcript at {tr_p}")
    return read_json(d / "meta.json"), read_json(tr_p), d


def _apply(step: dict[str, Any], tl: dict[str, Any], ctx: EditContext, hist: History) -> dict[str, Any]:
    name = step.get("op")
    if name == "undo":
        return hist.undo()
    if name == "trim":
        return edit_ops.trim(tl, ctx, resolve_time(step.get("start"), tl, ctx), resolve_time(step.get("end"), tl, ctx))
    if name == "delete_words":
        return edit_ops.delete_words(tl, ctx, resolve_words(step.get("words"), tl, ctx))
    if name == "set_caption_style":
        return edit_ops.set_caption_style(tl, ctx, str(step.get("preset")))
    if name == "add_zoom":
        return edit_ops.add_zoom(tl, ctx, resolve_time(step.get("at"), tl, ctx), float(step.get("scale", 1.2)),
                                 int(step.get("duration_ms", 0)))
    if name == "set_duration":
        return edit_ops.set_duration(tl, ctx, int(step.get("target_ms", 0)))
    raise OpError("E_OP_UNKNOWN", f"unknown op {name!r}; known: {', '.join([*edit_ops.OPS, 'undo'])}")


def run(video: Path, ops_path: Path, out_dir: Path, language: str, model: str) -> dict[str, Any]:
    from src.render import render
    from src.validate import DEV_SOURCE_ROOT, validate

    t0 = time.time()
    video = video.resolve()
    if not video.is_file():
        raise DemoError("input", f"video not found: {video}")
    if not video.is_relative_to(ROOT):
        raise DemoError("input", "the video must be inside the repository (timeline paths are repo-relative)")
    rel = video.relative_to(ROOT).as_posix()
    allow_dev = video.is_relative_to(ROOT / DEV_SOURCE_ROOT)
    if allow_dev:
        print(f"note: {DEV_SOURCE_ROOT}/ source, internal development testing only (ADR-0006)", file=sys.stderr)
    try:
        spec = json.loads(ops_path.read_text(encoding="utf-8"))
        steps = spec["ops"]
        assert isinstance(steps, list)
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as e:
        raise DemoError("ops", f"cannot read an {{\"ops\": [...]}} list from {ops_path}: {e}") from None

    meta, tr, cdir = _ingest(video, model, language)
    words = words_from_transcript(tr, SOURCE_ID)
    write_json(cdir / "edit" / "words.json", words)
    dur = int(meta["duration"] * 1000)
    clips = [{"id": "c1", "source": SOURCE_ID, "in_ms": 0, "out_ms": dur}]
    ctx = EditContext(words=tuple(words), source_id=SOURCE_ID, base_dir=ROOT, allow_dev=allow_dev)
    tl: dict[str, Any] = {
        "version": "0.1", "canvas": dict(CANVAS), "target_duration_ms": dur,
        "sources": [{"id": SOURCE_ID, "path": rel, "duration_ms": dur, "has_audio": bool(meta["has_audio"])}],
        "tracks": {"video": clips, "captions": captions_from_words(words, clips, SOURCE_ID)},
        "provenance": {"selection": f"src.demo ops={ops_path.name} language={tr['language']}"},
    }
    issues = validate(tl, ROOT, allow_dev=allow_dev)
    if issues:
        raise DemoError("captions", "v0 timeline is invalid:\n  " + "\n  ".join(map(str, issues)))
    hist = History(cdir / "edit" / "history")
    hist.clear()
    hist.save(tl)
    for i, step in enumerate(steps):
        try:
            tl = _apply(step, tl, ctx, hist)
        except OpError as e:
            raise DemoError(f"op {i} ({step.get('op') if isinstance(step, dict) else step!r})", str(e)) from None
        if not (isinstance(step, dict) and step.get("op") == "undo"):
            hist.save(tl)
        print(f"op {i} {step.get('op')}: {total_ms(tl)} ms, {len(tl['tracks']['video'])} clips")

    stem = re.sub(r"[^A-Za-z0-9]+", "_", video.stem).strip("_")
    out = out_dir / f"{stem}__{ops_path.stem}.mp4"
    write_json(out.with_suffix(".timeline.json"), tl)
    try:
        render(tl, out, allow_dev=allow_dev)
    except (ValueError, subprocess.CalledProcessError) as e:
        raise DemoError("render", str(e)) from None
    p = probe(out)
    return {"output": str(out), "timeline_ms": total_ms(tl), "ffprobe_s": p["duration"], "fps": p.get("fps"),
            "size": f"{p.get('width')}x{p.get('height')}", "language": tr["language"],
            "language_probability": tr.get("language_probability"), "versions": hist.versions()[-1],
            "wall_s": round(time.time() - t0, 1)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.demo", description=__doc__)
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--ops", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--language", default="auto", help="'auto' (default) or an ISO code to force (ingest)")
    ap.add_argument("--model", default="large-v3-turbo")
    a = ap.parse_args(argv)
    try:
        r = run(a.video, a.ops, a.out, a.language, a.model)
    except DemoError as e:
        print(f"demo: error: {e}", file=sys.stderr)
        return 1
    print(f"output:   {r['output']}")
    print(f"duration: {r['timeline_ms']} ms (timeline), {r['ffprobe_s']:.3f} s (ffprobe)")
    print(f"language: {r['language']} (p={r['language_probability']})")
    print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
