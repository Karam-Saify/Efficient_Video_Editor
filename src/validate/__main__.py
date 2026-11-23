"""python -m src.validate timeline.json [--allow-dev]  — exits 0 if valid; exits 1 and prints one issue per line
if invalid.

Relative source paths resolve against the current working directory (run from the repo root).

Stage-contract interface (H-0003): validates, writes <dir>/report.json, then the manifest.
An invalid timeline exits 1 and writes no manifest, so it is never cached as a success.

    python -m src.validate --input <timeline.json> --out <dir>
"""
import json
import sys
from pathlib import Path
from typing import Any

from src.common import read_json
from src.manifest import StageError, cli, wants_stage_cli
from src.validate import total_duration_ms, validate


def load_timeline(path: Path) -> Any:
    """Read the timeline JSON; unreadable or non-JSON input is a StageError with one plain line (H-0009)."""
    try:
        return read_json(path)
    except (OSError, ValueError) as e:  # ValueError covers JSONDecodeError and UnicodeDecodeError
        reason = " ".join(str(e).split()) or type(e).__name__
        raise StageError(f"cannot read timeline JSON from {path}: {reason}") from None


def main(argv: list[str]) -> None:
    allow_dev = "--allow-dev" in argv  # admit quarantine/dev/ sources (ADR-0006, dev testing only)
    argv = [a for a in argv if a != "--allow-dev"]
    if len(argv) != 1:
        sys.exit(__doc__)
    try:
        tl = load_timeline(Path(argv[0]))
    except StageError as e:
        print(f"validate: error: {e}", file=sys.stderr)
        sys.exit(1)
    errors = validate(tl, allow_dev=allow_dev)
    if errors:
        print("\n".join(map(str, errors)))
        sys.exit(1)
    print(f"OK: {len(tl['tracks']['video'])} clips, {total_duration_ms(tl)} ms")


def stage_work(inputs: list[Path], out_dir: Path, config: dict[str, Any]) -> str:
    if len(inputs) != 1 or not inputs[0].is_file():
        raise StageError("validate expects exactly one timeline.json file as --input")
    errors = validate(load_timeline(inputs[0]))
    report = {"valid": not errors, "errors": [e.to_dict() for e in errors]}
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        lines = "\n".join(map(str, errors))
        raise StageError(f"{len(errors)} validation error(s); see {out_dir / 'report.json'}:\n{lines}")
    return "ok"


if __name__ == "__main__":
    if wants_stage_cli(sys.argv[1:]):
        sys.exit(cli("validate", work=stage_work))
    main(sys.argv[1:])
