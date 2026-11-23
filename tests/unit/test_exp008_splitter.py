"""Unit tests for the EXP-008 §5.3 run-splitting rule in experiments/exp008_render.py (H-0015).

Pure functions only: no fc-query, no ffmpeg, no rendering. Expected values are the §5.3 table.
"""

import hashlib
import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "experiments" / "exp008_render.py"
_spec = importlib.util.spec_from_file_location("exp008_render", _PATH)
exp008 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp008)

FN_L, FN_A = "{\\fnNoto Sans}", "{\\fnNoto Sans Arabic}"


def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


@pytest.mark.parametrize(
    "raw, runs, n_l, tagged_len, sha16",
    [
        ("السعر 250 دولار فقط", "A6 L3 A10", 3, 54, "ea7a2ee3ba9338bc"),
        ("جربت iPhone 16 Pro امبارح", "A5 L13 A7", 13, 60, "eb85fb62231afbce"),
        ('"اقتباس" و(قوسين)', "L1 A6 L1 A2 L1 A5 L1", 4, 136, "5b8d2ec0094a6c3e"),
        ("١٠٪ خصم – ٢٠٢٦", "A8 L1 A5", 1, 49, "1b138b96859dc198"),
        ("مرحبا بكم في القناة", "A19", 0, 19, "bafd0595bb2e96ed"),
        ("ـــــــ مدّ ـــــــ", "A19", 0, 19, "92079e97c6ad4cb2"),
    ],
)
def test_prereg_table_rows(raw, runs, n_l, tagged_len, sha16):
    tagged, got_runs, k = exp008.split_runs(raw)
    assert got_runs == runs
    assert k.count("L") == n_l
    assert len(tagged) == tagged_len
    assert _sha16(tagged) == sha16


def test_ar05_tagged_text_exact():
    tagged, _, _ = exp008.split_runs("جربت iPhone 16 Pro امبارح")
    assert tagged == "جربت " + FN_L + "iPhone 16 Pro" + FN_A + " امبارح"


def test_no_trailing_tag_and_start_in_arabic():
    tagged, _, _ = exp008.split_runs("abc")
    assert tagged == FN_L + "abc"  # switches away from the A default, never closes at the end


def test_space_rules_edges_and_mixed_neighbours():
    assert exp008.classify(" a ") == ["A", "L", "A"]  # edge runs default to A
    assert exp008.classify("a b") == ["L", "L", "L"]  # equal neighbours keep class
    assert exp008.classify("a  ب") == ["L", "A", "A", "A"]  # differing neighbours -> A


@pytest.mark.parametrize("cp", [" ", "­", "‌", "‫", "ก", "؜"])
def test_class_x_rejected(cp):
    with pytest.raises(ValueError):
        exp008.classify("ب" + cp)


def test_only_two_tags_emitted():
    tagged, _, _ = exp008.split_runs('"اقتباس" و(قوسين)')
    stripped = tagged.replace(FN_A, "").replace(FN_L, "")
    assert not any(c in stripped for c in "{}\\")


def test_control_text_fingerprint():
    assert (len(exp008.CTRL_TEXT), _sha16(exp008.CTRL_TEXT)) == exp008.CTRL_EXPECT
