"""python -m src.validate timeline.json  — exits 1 and prints errors if invalid.

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
from src.validate import total_duration, validate


def main(argv: list[str]) -> None:
    if len(argv) != 1:
        sys.exit(__doc__)
    tl = read_json(Path(argv[0]))
    errors = validate(tl)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(tl['clips'])} clips, {total_duration(tl):.3f}s")


def stage_work(inputs: list[Path], out_dir: Path, config: dict[str, Any]) -> str:
    if len(inputs) != 1 or not inputs[0].is_file():
        raise StageError("validate expects exactly one timeline.json file as --input")
    errors = validate(read_json(inputs[0]))
    report = {"valid": not errors, "errors": errors}
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise StageError(f"{len(errors)} validation error(s); see {out_dir / 'report.json'}:\n" + "\n".join(errors))
    return "ok"


if __name__ == "__main__":
    if wants_stage_cli(sys.argv[1:]):
        sys.exit(cli("validate", work=stage_work))
    main(sys.argv[1:])
