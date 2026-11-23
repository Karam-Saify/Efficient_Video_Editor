"""H-0025 G5: the demo CLI fails loudly (non-zero exit, one `demo: error:` line) before any heavy work."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = sorted((ROOT / "examples" / "ops").glob("*.json"))


def demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "src.demo", *args], cwd=ROOT, capture_output=True, text=True)


def test_missing_video_fails_loudly(tmp_path: Path) -> None:
    r = demo("--video", str(tmp_path / "nope.mp4"), "--ops", str(EXAMPLES[0]), "--out", str(tmp_path))
    assert r.returncode == 1 and r.stderr.startswith("demo: error: input: video not found")


def test_bad_ops_file_fails_loudly(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{\"steps\": []}", encoding="utf-8")
    r = demo("--video", "tests/fixtures/media/src_a.txt", "--ops", str(bad), "--out", str(tmp_path))
    assert r.returncode == 1 and "demo: error: ops:" in r.stderr


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_examples_use_only_known_ops_and_rule_based_times(path: Path) -> None:
    from src.edit.ops import OPS
    steps = json.loads(path.read_text(encoding="utf-8"))["ops"]
    assert steps and all(s["op"] in OPS for s in steps)
    for s in steps:
        for k in ("start", "end", "at"):
            if k in s:
                assert isinstance(s[k], dict), f"{path.name}: {k} must be a rule, not a typed timestamp"
        if "words" in s:
            assert "ids" not in s["words"], f"{path.name}: word ids must be selected by rule"


def test_three_examples() -> None:
    assert [p.name for p in EXAMPLES] == ["delete_words_zoom.json", "fit_30s.json", "trim_and_style.json"]


# ---- ops.json resolvers (code turns rules into ms / word ids) -------------------------------------------------
def test_resolve_time_and_words() -> None:
    from src.demo import resolve_time, resolve_words
    from src.edit.ops import OpError
    from tests.unit.test_edit_ops import CTX, base

    tl = base()
    assert resolve_time({"word": 0, "edge": "start"}, tl, CTX) == 1000
    assert resolve_time({"word": -1, "edge": "end"}, tl, CTX) == 7200
    assert resolve_time({"segment": 1, "edge": "end"}, tl, CTX) == 4700
    assert resolve_time({"fraction": 0.25}, tl, CTX) == 2500
    assert resolve_words({"nth": [1, 2]}, tl, CTX) == ["w0001", "w0002"]
    assert resolve_words({"match": ["UM"]}, tl, CTX) == ["w0001"]
    for bad in ({"word": 99, "edge": "start"}, {"fraction": 1.5}, {"bogus": 1}, 2.5):
        with pytest.raises(OpError):
            resolve_time(bad, tl, CTX)
    with pytest.raises(OpError):
        resolve_words({"match": ["nothing"]}, tl, CTX)
