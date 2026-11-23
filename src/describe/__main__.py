"""python -m src.describe --input <path> --out <dir> [--set key=value]

Not implemented yet: exits 2 with `NOT_IMPLEMENTED: describe` on stderr and writes no manifest (H-0024).
Real logic arrives in a later brief; see ARCHITECTURE.md.
"""
import sys

from src.manifest import cli

STAGE_DEFAULTS: dict[str, object] = {}

if __name__ == "__main__":
    sys.exit(cli("describe", defaults=STAGE_DEFAULTS))
