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


def test_every_preset_is_an_ass_style_with_the_pair_regular_and_auto_direction(tmp_path: Path) -> None:
    """H-0025: one ASS style per preset; each Dialogue line uses its caption's preset (default clean)."""
    from src.presets import CAPTION_PRESETS
    caps = [{"id": n, "text": "مرحبا Link", "start_ms": i * 500, "end_ms": i * 500 + 400, "dir": "rtl", "style": n}
            for i, n in enumerate(CAPTION_PRESETS)]
    caps.append({"id": "d", "text": "plain", "start_ms": 1600, "end_ms": 1900, "dir": "ltr"})
    ass = _ass(tmp_path, caps)
    styles = [ln[len("Style: "):].split(",") for ln in ass.splitlines() if ln.startswith("Style:")]
    assert [s[0] for s in styles] == list(CAPTION_PRESETS)
    assert all(s[1] == "Noto Sans Arabic" and s[7] == "0" and s[-1] == "-1" for s in styles)
    used = [ln.split(",")[3] for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert used == [*CAPTION_PRESETS, "clean"]


def test_zoom_is_an_enabled_overlay_before_the_captions(tmp_path: Path) -> None:
    from src.render import build_command
    tl = json.loads((ROOT / "tests/fixtures/timelines/valid/v4_effects_zoom.json").read_text("utf-8"))
    graph = build_command(to_render_model(tl), tmp_path / "o.mp4", tmp_path / "o.ass", "veryfast", 20)
    graph = graph[graph.index("-filter_complex") + 1]
    assert "crop=w=trunc(iw/1.15/2)*2:h=trunc(ih/1.15/2)*2,scale=1080:1920" in graph
    assert "enable='gte(t,1.0)*lt(t,1.4)'" in graph and "enable='gte(t,5.0)*lt(t,5.3)'" in graph  # default 1.2
    assert "crop=w=trunc(iw/1.2/2)*2" in graph
    assert graph.index("[z1]ass=filename=") > graph.index("overlay")
    assert "[0:v]fps=30,trim=start=0.0:end=4.0" in graph  # fps before trim: frame-exact cuts
