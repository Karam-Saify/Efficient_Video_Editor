"""python -m src.edit --input <path> --out <dir> [--set key=value]

Not implemented yet: exits 2 with `NOT_IMPLEMENTED: edit` on stderr and writes no manifest (H-0024).
Real logic arrives in a later brief; see ARCHITECTURE.md.
"""
import sys

from src.manifest import cli

STAGE_DEFAULTS: dict[str, object] = {"prompt_version": "v0"}

if __name__ == "__main__":
    sys.exit(cli("edit", defaults=STAGE_DEFAULTS))
