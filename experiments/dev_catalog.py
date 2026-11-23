"""Catalog the internal dev clips (H-0024 G1): quarantine/dev/*.mp4 -> quarantine/dev/dev_manifest.csv.

INTERNAL DEV TESTING ONLY (ADR-0006). The clips, this CSV and anything derived from them stay in the
git-ignored quarantine/ tree; only this script is committed. Nothing here is sent to an LLM (I-3).

    .venv/bin/python experiments/dev_catalog.py [--model large-v3-turbo] [--dir quarantine/dev]

Columns: file, duration_s, width, height, fps, has_audio (ffprobe); language, language_prob,
words_per_min (faster-whisper on CPU/int8, language auto-detected, word count / clip minutes);
scene_cuts (PySceneDetect ContentDetector boundaries), mean_shot_s (duration / shots).
All arithmetic is code. Clips without audio get language '' and words_per_min 0.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.common import probe  # noqa: E402
from src.ingest.__main__ import load_audio  # noqa: E402

COLUMNS = ["file", "duration_s", "width", "height", "fps", "has_audio", "language", "language_prob",
           "words_per_min", "scene_cuts", "mean_shot_s"]


def scene_cuts(path: Path) -> int:
    from scenedetect import ContentDetector, detect

    return max(len(detect(str(path), ContentDetector())) - 1, 0)


def speech(path: Path, model) -> tuple[str, float, int]:
    segments, info = model.transcribe(load_audio(path), language=None, beam_size=5, word_timestamps=True,
                                      vad_filter=True)
    words = sum(len(s.words or []) for s in segments)
    return info.language, round(info.language_probability, 3), words


def row(path: Path, model) -> dict[str, object]:
    meta = probe(path)
    dur = meta["duration"]
    lang, prob, words = speech(path, model) if meta["has_audio"] else ("", 0.0, 0)
    cuts = scene_cuts(path)
    return {
        "file": path.name, "duration_s": round(dur, 3), "width": meta.get("width"), "height": meta.get("height"),
        "fps": meta.get("fps"), "has_audio": meta["has_audio"], "language": lang, "language_prob": prob,
        "words_per_min": round(words / (dur / 60), 1) if dur > 0 else 0, "scene_cuts": cuts,
        "mean_shot_s": round(dur / (cuts + 1), 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", type=Path, default=ROOT / "quarantine" / "dev")
    ap.add_argument("--model", default="large-v3-turbo")
    a = ap.parse_args()
    from faster_whisper import WhisperModel

    clips = sorted(a.dir.glob("*.mp4"))
    if not clips:
        print(f"no .mp4 in {a.dir}", file=sys.stderr)
        return 1
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    rows = []
    for p in clips:
        t0 = time.perf_counter()
        rows.append(row(p, model))
        print(f"{p.name}: {rows[-1]['language']} ({time.perf_counter() - t0:.1f}s)", file=sys.stderr)
    out = a.dir / "dev_manifest.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
