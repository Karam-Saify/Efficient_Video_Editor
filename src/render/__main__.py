"""python -m src.render timeline.json out/short.mp4 [--preset veryfast] [--crf 20]"""
import argparse
import time
from pathlib import Path

from src.common import read_json
from src.render import render

ap = argparse.ArgumentParser()
ap.add_argument("timeline", type=Path)
ap.add_argument("out", type=Path)
ap.add_argument("--preset", default="veryfast")
ap.add_argument("--crf", type=int, default=20)
a = ap.parse_args()
t0 = time.time()
render(read_json(a.timeline), a.out, a.preset, a.crf)
print(f"rendered {a.out} in {time.time() - t0:.1f}s")
