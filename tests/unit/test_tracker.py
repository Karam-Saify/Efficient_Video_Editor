"""tools/tracker.py: Done-without-evidence fails, stale stats fail, the real tracker passes."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("tracker", ROOT / "tools" / "tracker.py")
tracker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tracker)

HDR = "| ID | Item | Owner | Status | Evidence | Updated |\n|---|---|---|---|---|---|\n"


def _write(tmp_path, rows):
    p = tmp_path / "T.md"
    text = "<!-- stats:start -->\n<!-- stats:end -->\n\n" + HDR + rows
    p.write_text(text, encoding="utf-8")
    tracker.main(["--file", str(p)])  # regenerate stats
    return p


def test_real_tracker_passes():
    assert tracker.main(["--check"]) == 0


def test_done_without_evidence_fails(tmp_path):
    p = _write(tmp_path, "| T-1 | x | eng | Done | — | d |\n")
    assert tracker.main(["--check", "--file", str(p)]) == 1


def test_done_with_missing_path_fails(tmp_path):
    p = _write(tmp_path, "| T-1 | x | eng | Done | `docs/does_not_exist.md` | d |\n")
    assert tracker.main(["--check", "--file", str(p)]) == 1


def test_done_with_existing_path_and_ignored_root_passes(tmp_path):
    p = _write(tmp_path, "| T-1 | x | eng | Done | `tools/tracker.py`, `out/x.mp4` | d |\n")
    assert tracker.main(["--check", "--file", str(p)]) == 0


def test_bad_status_and_duplicate_id_fail(tmp_path):
    p = _write(tmp_path, "| T-1 | x | eng | Finished | n | d |\n| T-1 | y | eng | Todo | — | d |\n")
    errs = tracker.check_rows(tracker.parse_rows(p.read_text())[0])
    assert any("status" in e for e in errs) and any("duplicate" in e for e in errs)


def test_stale_stats_fail(tmp_path):
    p = _write(tmp_path, "| T-1 | x | eng | Todo | — | d |\n")
    p.write_text(p.read_text() + "| T-2 | y | eng | Todo | — | d |\n", encoding="utf-8")
    assert tracker.main(["--check", "--file", str(p)]) == 1
