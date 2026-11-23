"""python -m src.select --input <path> --out <dir> [--set key=value]

Not implemented yet: exits 2 with `NOT_IMPLEMENTED: select` on stderr and writes no manifest (H-0024).
Real logic arrives in a later brief; see ARCHITECTURE.md.
"""
import sys

from src.manifest import cli

STAGE_DEFAULTS: dict[str, object] = {"target_duration_ms": 45000}

if __name__ == "__main__":
    sys.exit(cli("select", defaults=STAGE_DEFAULTS))
