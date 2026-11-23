"""python -m src.render timeline.json out/short.mp4 [--preset veryfast] [--crf 20] [--allow-dev]

Stage-contract interface: not implemented yet (exits 2, `NOT_IMPLEMENTED: render`, no manifest; H-0024):

    python -m src.render --input <timeline.json> --out <dir> [--set key=value]
"""
import argparse
import sys
import time
from pathlib import Path

STAGE_DEFAULTS = {"preset": "veryfast", "crf": 20}


def main(argv: list[str] | None = None) -> None:
    from src.common import read_json
    from src.render import render

    ap = argparse.ArgumentParser()
    ap.add_argument("timeline", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--allow-dev", action="store_true", help="admit quarantine/dev/ sources (ADR-0006, dev only)")
    a = ap.parse_args(argv)
    t0 = time.time()
    render(read_json(a.timeline), a.out, a.preset, a.crf, allow_dev=a.allow_dev)
    print(f"rendered {a.out} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    from src.manifest import cli, wants_stage_cli

    if wants_stage_cli(sys.argv[1:]):
        sys.exit(cli("render", defaults=STAGE_DEFAULTS, tools=("ffmpeg",)))
    main()
