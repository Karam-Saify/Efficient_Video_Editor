"""H-0024 G3 font: the renderer's run splitter is the EXP-008 §5.3 rule, and the ASS uses only the declared pair."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from src.render import write_ass
from src.render.adapter import to_render_model
from src.render.fontrun import UnsupportedCharacter, tag_runs

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("exp008_render", ROOT / "experiments" / "exp008_render.py")
exp008 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp008)

STRINGS = ["السعر 250 دولار فقط", "جربت iPhone 16 Pro امبارح", '"اقتباس" و(قوسين)', "١٠٪ خصم – ٢٠٢٦",
           "مرحبا بكم في القناة", "ـــــــ مدّ ـــــــ", "Link in bio", "Bonjour à tous, ça va ?", "iPhone جديد",
           "  leading spaces", "trailing ", "a  b  ج"]


@pytest.mark.parametrize("s", STRINGS)
def test_port_matches_the_exp008_instrument(s: str) -> None:
    assert tag_runs(s) == exp008.split_runs(s)[0]


@pytest.mark.parametrize("s", ["שלום", "สวัสดี", "مرحبا 😀", "a؜b", "soft­hyphen", "tab\there"])
def test_characters_outside_the_pair_are_refused(s: str) -> None:
    with pytest.raises(UnsupportedCharacter, match="U\\+"):
        tag_runs(s)
    with pytest.raises(ValueError):
        exp008.split_runs(s)


def _ass(tmp_path: Path, captions: list[dict]) -> str:
    tl = json.loads((ROOT / "tests/fixtures/timelines/valid/v7_multilingual_captions.json").read_text("utf-8"))
    tl["tracks"]["captions"] = captions
    p = tmp_path / "o.ass"
    write_ass(to_render_model(tl), p)
    return p.read_text(encoding="utf-8")


def test_ass_uses_the_declared_pair_regular_weight_and_auto_direction(tmp_path: Path) -> None:
    ass = _ass(tmp_path, [{"id": "a", "text": "جربت iPhone 16 امبارح", "start_ms": 0, "end_ms": 1000, "dir": "rtl"},
                          {"id": "b", "text": "Link in bio", "start_ms": 1000, "end_ms": 2000, "dir": "ltr"}])
    style = next(ln for ln in ass.splitlines() if ln.startswith("Style:")).split(",")
    assert style[1] == "Noto Sans Arabic"  # style font = class A, as in EXP-008
    assert style[7] == "0"  # Bold 0: EXP-008 used the Regular files; bold would select an undeclared face
    assert style[-1] == "-1"  # Encoding -1: libass auto base direction (E6)
    dialogue = [ln.split(",,", 2)[-1] for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert dialogue == ["جربت {\\fnNoto Sans}iPhone 16{\\fnNoto Sans Arabic} امبارح", "{\\fnNoto Sans}Link in bio"]
    fonts = {t for t in ("Noto Naskh Arabic", "DejaVu", "Amiri") if t in ass}
    assert not fonts


def test_multiline_caption_tags_each_line(tmp_path: Path) -> None:
    ass = _ass(tmp_path, [{"id": "a", "text": "Hello\nمرحبا", "start_ms": 0, "end_ms": 1000, "dir": "ltr"}])
    assert "{\\fnNoto Sans}Hello\\N{\\fnNoto Sans Arabic}مرحبا" in ass


def test_unsupported_character_fails_the_render(tmp_path: Path) -> None:
    with pytest.raises(UnsupportedCharacter):
        _ass(tmp_path, [{"id": "a", "text": "שלום", "start_ms": 0, "end_ms": 1000, "dir": "rtl"}])
