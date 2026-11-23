"""Ingest: probe → transcript (faster-whisper) → scenes (PySceneDetect) → keyframes.

Every output is cached in cache/<video_id>/ and skipped if present (use --force to redo).

    python -m src.ingest samples/s01.mp4 [--model large-v3-turbo] [--language auto|ar|en|...] [--no-scenes]

The language is auto-detected by default (H-0024); the transcript records `language`,
`language_probability` and `language_requested`. `--language <code>` forces one.

Stage-contract interface: not implemented yet (exits 2, `NOT_IMPLEMENTED: ingest`, no manifest; H-0024):

    python -m src.ingest --input <file> --out <dir> [--set key=value]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.common import cache_dir, probe, read_json, video_id, write_json

if TYPE_CHECKING:  # numpy is imported lazily at call time; keep module import light
    import numpy as np


def load_audio(src: Path) -> np.ndarray:
    """16 kHz mono float32 via the ffmpeg CLI (avoids faster-whisper's PyAV version coupling)."""
    import numpy as np

    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def transcribe(src: Path, out: Path, model_name: str, language: str | None, beam: int) -> dict[str, Any]:
    from faster_whisper import WhisperModel

    t0 = time.time()
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        load_audio(src), language=language, beam_size=beam, word_timestamps=True, vad_filter=True,
    )
    segs = []
    for s in segments:  # generator: decoding happens here
        segs.append({
            "id": s.id,
            "start": round(s.start, 3),
            "end": round(s.end, 3),
            "text": s.text.strip(),
            "words": [
                {"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)}
                for w in (s.words or [])
            ],
        })
    data = {
        "model": model_name,
        "language_requested": language or "auto",
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "audio_duration": round(info.duration, 3),
        "runtime_sec": round(time.time() - t0, 1),
        "segments": segs,
    }
    write_json(out, data)
    return data


def detect_scenes(src: Path, out: Path) -> list[dict[str, Any]]:
    from scenedetect import ContentDetector, detect

    scenes = [
        {"id": i, "start": round(a.get_seconds(), 3), "end": round(b.get_seconds(), 3)}
        for i, (a, b) in enumerate(detect(str(src), ContentDetector()))
    ]
    if not scenes:  # single continuous shot
        scenes = [{"id": 0, "start": 0.0, "end": round(probe(src)["duration"], 3)}]
    write_json(out, scenes)
    return scenes


def keyframes(src: Path, scenes: list[dict[str, Any]], out_dir: Path, per_scene: int = 1) -> None:
    """Small JPEGs (320px wide) at evenly spaced points inside each scene."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for sc in scenes:
        span = sc["end"] - sc["start"]
        for k in range(per_scene):
            t = sc["start"] + span * (k + 1) / (per_scene + 1)
            dst = out_dir / f"scene{sc['id']:03d}_{k}.jpg"
            if dst.exists():
                continue
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src),
                 "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "5", str(dst)],
                check=True,
            )


def asr_language(requested: str) -> str | None:
    """'auto' -> None (faster-whisper detects); anything else is passed through as an ISO code."""
    return None if requested == "auto" else requested


def transcript_name(model: str, language: str) -> str:
    """The requested language is part of the cache key: a forced-language transcript is a different output."""
    return f"transcript.{model}.{language}.json"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--model", default="large-v3-turbo",
                    help="faster-whisper model name (e.g. large-v3, large-v3-turbo, small)")
    ap.add_argument("--language", default="auto", help="'auto' (default) to detect, or an ISO code to force")
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--no-scenes", action="store_true")
    ap.add_argument("--keyframes", type=int, default=1, help="keyframes per scene (0 to skip)")
    ap.add_argument("--force", action="store_true", help="recompute even if cached")
    return ap


def main() -> None:
    a = build_parser().parse_args()

    src = a.video.resolve()
    vid = video_id(src)
    d = cache_dir(vid)
    print(f"video_id: {vid}\ncache:    {d}")

    meta_p = d / "meta.json"
    if a.force or not meta_p.exists():
        write_json(meta_p, {"video_id": vid, **probe(src)})
    meta = read_json(meta_p)
    print(f"duration: {meta['duration']:.1f}s  {meta.get('width')}x{meta.get('height')} @ {meta.get('fps')}fps")

    tr_p = d / transcript_name(a.model, a.language)
    if a.force or not tr_p.exists():
        print(f"transcribing with {a.model} (cpu/int8)…")
        tr = transcribe(src, tr_p, a.model, asr_language(a.language), a.beam)
        rtf = tr["runtime_sec"] / max(tr["audio_duration"], 1e-6)
        print(f"  {len(tr['segments'])} segments in {tr['runtime_sec']}s (RTF {rtf:.2f}); "
              f"language {tr['language']} (p={tr['language_probability']})")
    else:
        print(f"transcript cached: {tr_p.name}")

    if not a.no_scenes:
        sc_p = d / "scenes.json"
        scenes = read_json(sc_p) if sc_p.exists() and not a.force else detect_scenes(src, sc_p)
        print(f"scenes:   {len(scenes)}")
        if a.keyframes:
            keyframes(src, scenes, d / "keyframes", a.keyframes)


STAGE_DEFAULTS: dict[str, Any] = {"asr_model": "large-v3-turbo", "language": "auto", "beam": 5}

if __name__ == "__main__":
    from src.manifest import cli, wants_stage_cli

    if wants_stage_cli(sys.argv[1:]):
        sys.exit(cli("ingest", defaults=STAGE_DEFAULTS, tools=("ffmpeg",)))
    main()
