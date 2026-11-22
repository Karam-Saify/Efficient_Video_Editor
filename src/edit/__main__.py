"""python -m src.edit --input <path> --out <dir> [--set key=value]

Stage-contract stub (H-0003): hashes inputs + config, writes <dir>/manifest.json (status "stub"),
skips on identical rerun. Real logic arrives in a later milestone; see ARCHITECTURE.md.
"""
import sys

from src.manifest import cli

STAGE_DEFAULTS: dict[str, object] = {"prompt_version": "v0"}

if __name__ == "__main__":
    sys.exit(cli("edit", defaults=STAGE_DEFAULTS))
