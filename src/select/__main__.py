"""python -m src.select --input <path> --out <dir> [--set key=value]

Stage-contract stub (H-0003): hashes inputs + config, writes <dir>/manifest.json (status "stub"),
skips on identical rerun. Real logic arrives in a later milestone; see ARCHITECTURE.md.
"""
import sys

from src.manifest import cli

STAGE_DEFAULTS: dict[str, object] = {"target_duration_ms": 45000}

if __name__ == "__main__":
    sys.exit(cli("select", defaults=STAGE_DEFAULTS))
