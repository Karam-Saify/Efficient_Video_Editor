"""E1: Is faster-whisper good enough for our Arabic?

Transcribes the first N seconds of a clip with several models (default: large-v3 vs large-v3-turbo),
then writes, per model:
  - transcript JSON with word timestamps + runtime / real-time factor
  - WER/CER against a hand-made reference (optional, --ref ref.txt), with Arabic normalization
  - a "cut test" WAV: every other word-group spliced together at the predicted word boundaries.
    Listen to it: clipped syllables or leftover breaths mean timestamp drift.
and a side-by-side report out/e1/<clip>/report.md for hand-checking.

    python experiments/e1_asr.py samples/s01.mp4 --seconds 120 [--ref samples/s01_ref.txt]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.common import ROOT, read_json  # noqa: E402
from src.ingest.__main__ import transcribe  # noqa: E402

_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")  # tashkeel + tatweel
_PUNCT = re.compile(r"[^\w\s]")


def normalize(text: str) -> list[str]:
    """Standard Arabic ASR normalization: strip diacritics/tatweel/punctuation, unify alef/ya/ta-marbuta."""
    t = _DIACRITICS.sub("", text)
    t = re.sub("[إأآٱ]", "ا", t).replace("ى", "ي").replace("ة", "ه")
    t = _PUNCT.sub(" ", t)
    return t.split()


def edit_distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def error_rates(ref: str, hyp: str) -> tuple[float, float]:
    r, h = normalize(ref), normalize(hyp)
    wer = edit_distance(r, h) / max(len(r), 1)
    rc, hc = list("".join(r)), list("".join(h))
    cer = edit_distance(rc, hc) / max(len(rc), 1)
    return wer, cer


def cut_test(audio: Path, words: list[dict], out: Path, group: int = 3) -> None:
    """Keep word-groups 0, 2, 4, … and splice them; bad timestamps become audible."""
    keep = [words[i:i + group] for i in range(0, len(words), group)][::2]
    spans = [(g[0]["start"], g[-1]["end"]) for g in keep if g]
    if not spans:
        return
    parts = [f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[p{i}]" for i, (s, e) in enumerate(spans)]
    graph = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(spans))) + f"concat=n={len(spans)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-filter_complex", graph, "-map", "[o]", str(out)],
                   check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--seconds", type=float, default=120)
    ap.add_argument("--models", nargs="+", default=["large-v3-turbo", "large-v3"])
    ap.add_argument("--language", default="ar")
    ap.add_argument("--ref", type=Path, help="hand-corrected transcript of the same N seconds (plain text)")
    a = ap.parse_args()

    out_dir = ROOT / "out" / "e1" / a.video.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    audio = out_dir / f"first{int(a.seconds)}s.wav"
    if not audio.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.video), "-t", str(a.seconds),
                        "-vn", "-ac", "1", "-ar", "16000", str(audio)], check=True)
    ref = a.ref.read_text(encoding="utf-8") if a.ref else None

    rows, texts = [], {}
    for m in a.models:
        tp = out_dir / f"transcript.{m}.json"
        if tp.exists():
            tr = read_json(tp)
        else:
            print(f"[{m}] transcribing {a.seconds:.0f}s on CPU (first run downloads the model)…")
            tr = transcribe(audio, tp, m, a.language, beam=5)
        words = [w for s in tr["segments"] for w in s["words"]]
        text = " ".join(s["text"] for s in tr["segments"])
        texts[m] = tr["segments"]
        cut_test(audio, words, out_dir / f"cut_test.{m}.wav")
        rtf = tr["runtime_sec"] / max(tr["audio_duration"], 1e-6)
        low = sum(w["p"] < 0.5 for w in words) / max(len(words), 1)
        wer, cer = error_rates(ref, text) if ref else (None, None)
        rows.append((m, tr["runtime_sec"], rtf, len(words), low, wer, cer))
        print(f"[{m}] {tr['runtime_sec']}s, RTF {rtf:.2f}, {len(words)} words, {low:.0%} low-confidence"
              + (f", WER {wer:.1%}, CER {cer:.1%}" if ref else ""))

    lines = [f"# E1 report — {a.video.name}, first {a.seconds:.0f}s", "",
             "| model | runtime s | RTF | words | p<0.5 | WER | CER |", "|---|---|---|---|---|---|---|"]
    for m, rt, rtf, n, low, wer, cer in rows:
        fmt = lambda x: "—" if x is None else f"{x:.1%}"  # noqa: E731
        lines.append(f"| {m} | {rt} | {rtf:.2f} | {n} | {low:.0%} | {fmt(wer)} | {fmt(cer)} |")
    lines += ["", "RTF = runtime / audio length (lower is faster; <1 is faster than realtime).",
              "Listen to `cut_test.<model>.wav` for clipped words at cut points.", "", "## Segments", ""]
    for m, segs in texts.items():
        lines += [f"### {m}", ""] + [f"- `{s['start']:7.2f}–{s['end']:7.2f}` {s['text']}" for s in segs] + [""]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"report: {out_dir / 'report.md'}")


if __name__ == "__main__":
    main()
