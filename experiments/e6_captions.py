"""E6: Arabic caption rendering with FFmpeg/libass on CPU.

Generates a synthetic 16:9 source, builds a 3-clip vertical timeline with hard Arabic test strings
(ligatures, diacritics, mixed RTL/LTR, digits, dialect), renders it, and dumps one frame per caption
for visual inspection.

    python experiments/e6_captions.py [--font "Noto Naskh Arabic"] [--seconds 30]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.common import ROOT, probe, write_json  # noqa: E402
from src.render import render  # noqa: E402

TEST_LINES = [
    "مرحبا بكم في القناة",                         # basic joining
    "لا إله إلا الله — لأن الأمل",                 # lam-alef ligatures
    "اَلْعَرَبِيَّةُ لُغَةٌ جَمِيلَةٌ",                  # full diacritics (tashkeel)
    "شو بدك تعمل اليوم؟ يلا نبلش",                 # Lebanese dialect + Arabic question mark
    "جرّبت YouTube Shorts لمدة 30 يوم",            # mixed RTL/LTR + Latin digits
    "السعر ٢٥٠ دولار فقط!",                         # Arabic-Indic digits
    "هذا سطر طويل جداً لاختبار التفاف النص تلقائياً على شاشة عمودية ضيقة",  # wrapping
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Noto Naskh Arabic")
    ap.add_argument("--reframe", default="fit_blur", choices=["crop_center", "fit_blur", "fit_pad"])
    ap.add_argument("--seconds", type=float, default=21.0, help="length of synthetic source")
    a = ap.parse_args()

    out_dir = ROOT / "out" / "e6"
    out_dir.mkdir(parents=True, exist_ok=True)
    src = out_dir / "synthetic_src.mp4"
    if not src.exists():
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y",
             "-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate=30:duration={a.seconds}",
             "-f", "lavfi", "-i", f"sine=frequency=440:duration={a.seconds}",
             "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", str(src)],
            check=True,
        )
    meta = probe(src)

    # Three clips from different parts of the source; captions tile the output timeline.
    clips = [("c1", 1.0, 7.0), ("c2", 9.0, 14.0), ("c3", 15.0, 20.0)]
    total = sum(o - i for _, i, o in clips)
    step = total / len(TEST_LINES)
    tl = {
        "version": "0.1",
        "video_id": "e6-synthetic",
        "output": {"width": 1080, "height": 1920, "fps": 30, "target_duration": total, "reframe": a.reframe},
        "sources": {"src": meta},
        "clips": [{"id": cid, "source": "src", "in": i, "out": o} for cid, i, o in clips],
        "captions": {
            "style": {"font": a.font, "size": 84, "position": "bottom", "margin_v": 360},
            "items": [
                {"start": round(k * step, 3), "end": round((k + 1) * step - 0.05, 3), "text": t}
                for k, t in enumerate(TEST_LINES)
            ],
        },
    }
    tag = a.font.replace(" ", "_")
    write_json(out_dir / f"timeline_{tag}.json", tl)

    out = out_dir / f"render_{tag}.mp4"
    t0 = time.time()
    render(tl, out)
    secs = time.time() - t0
    rmeta = probe(out)
    print(f"render: {secs:.1f}s for {total:.1f}s of output (x{total / secs:.2f} realtime)")
    print(f"output: {rmeta['width']}x{rmeta['height']} {rmeta['duration']:.3f}s (target {total:.3f}s)")

    for k, it in enumerate(tl["captions"]["items"]):
        mid = (it["start"] + it["end"]) / 2
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", str(out), "-frames:v", "1",
             "-vf", "crop=1080:600:0:1100,scale=540:-2", str(out_dir / f"frame_{tag}_{k}.png")],
            check=True,
        )
    print(f"frames: {out_dir}/frame_{tag}_*.png")


if __name__ == "__main__":
    main()
