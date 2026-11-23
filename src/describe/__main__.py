"""Footage Intelligence v0 (H-0035, ADR-0025). Zero cost: no API is called (ADR-0023).

    python -m src.describe annotate <video> --rights-id RR-P001-01 [--asr-model M] [--language auto] [--transcript T]
    python -m src.describe apply-descriptions <video> <descriptions.todo.json>   (filled by a Claude Code session)
    python -m src.describe storyboard <video>                                    (rewrite the HTML)
    python -m src.describe import-corrections <video> <corrections.json>         (partner export -> human_verified)
    python -m src.describe validate <annotation.json>

Outputs live in cache/<video_id>/ (git-ignored); see docs/FOOTAGE_INTELLIGENCE.md.
The generic stage-contract interface (`--input/--out`) is not implemented: exits 2, `NOT_IMPLEMENTED: describe`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.common import CACHE, read_json
from src.manifest import StageError, cli, wants_stage_cli

STAGE_DEFAULTS: dict[str, object] = {}


def main(argv: list[str] | None = None) -> int:
    from src.describe import annotate as fi
    from src.describe.schema import validate_annotation
    from src.describe.storyboard import write_storyboard

    ap = argparse.ArgumentParser(prog="python -m src.describe", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache-root", type=Path, default=CACHE, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("annotate")
    a.add_argument("video", type=Path)
    a.add_argument("--rights-id", required=True, help="DATA_RIGHTS row, RR-<nnn> or RR-P<partner>-<n>")
    a.add_argument("--asr-model", default="large-v3-turbo")
    a.add_argument("--language", default="auto")
    a.add_argument("--transcript", type=Path, help="use this transcript JSON (ingest format) instead of ASR")
    a.add_argument("--force", action="store_true", help="overwrite a record that holds descriptions or corrections")
    d = sub.add_parser("apply-descriptions")
    d.add_argument("video", type=Path)
    d.add_argument("todo", type=Path)
    s = sub.add_parser("storyboard")
    s.add_argument("video", type=Path)
    c = sub.add_parser("import-corrections")
    c.add_argument("video", type=Path)
    c.add_argument("corrections", type=Path)
    v = sub.add_parser("validate")
    v.add_argument("record", type=Path)
    ns = ap.parse_args(argv)
    root = ns.cache_root
    try:
        if ns.cmd == "annotate":
            p = fi.annotate(ns.video, ns.rights_id, asr_model=ns.asr_model, language=ns.language,
                            transcript_path=ns.transcript, cache_root=root, force=ns.force)
        elif ns.cmd == "apply-descriptions":
            p = fi.apply_descriptions(ns.video, ns.todo, root)
        elif ns.cmd == "storyboard":
            p = fi.record_path(ns.video, root)
        elif ns.cmd == "import-corrections":
            p = fi.import_corrections(ns.video, ns.corrections, root)
        else:
            errs = validate_annotation(read_json(ns.record))
            for e in errs:
                print(e, file=sys.stderr)
            print("valid" if not errs else f"invalid: {len(errs)} error(s)")
            return 1 if errs else 0
        sb = write_storyboard(p, p.parent.parent / "storyboard" / "index.html")
    except StageError as e:
        print(f"describe: error: {e}", file=sys.stderr)
        return 1
    print(f"record:     {p}\nstoryboard: {sb}")
    if ns.cmd == "annotate":
        print(f"to-do:      {p.parent / 'descriptions.todo.json'}")
    return 0


if __name__ == "__main__":
    if wants_stage_cli(sys.argv[1:]):
        sys.exit(cli("describe", defaults=STAGE_DEFAULTS))
    sys.exit(main())
