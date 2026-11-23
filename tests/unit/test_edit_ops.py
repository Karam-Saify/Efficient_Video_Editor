"""H-0025 G4: pure edit ops (timeline vN -> vN+1, validated), caption re-timing, history + undo, ops.json resolvers."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.captions import captions_from_words
from src.edit import ops
from src.edit.history import History
from src.edit.ops import EditContext, OpError

ROOT = Path(__file__).resolve().parents[2]
FPS = 30
WORDS = [  # (id, seg, text, start_ms, end_ms) in source time
    ("w0000", 0, "Hello", 1000, 1400), ("w0001", 0, "um", 1500, 1700), ("w0002", 0, "world", 1800, 2300),
    ("w0003", 1, "this", 3500, 3800), ("w0004", 1, "is", 3850, 4000), ("w0005", 1, "editing", 4100, 4700),
    ("w0006", 2, "مرحبا", 6000, 6600), ("w0007", 2, "بكم", 6700, 7200),
]
CTX = EditContext(words=tuple({"id": i, "source": "srcA", "seg": s, "text": t, "start_ms": a, "end_ms": b}
                              for i, s, t, a, b in WORDS), source_id="srcA", base_dir=ROOT)


def base() -> dict[str, Any]:
    clips = [{"id": "c1", "source": "srcA", "in_ms": 0, "out_ms": 10000}]
    return {"version": "0.1", "canvas": {"width": 1080, "height": 1920, "fps": FPS}, "target_duration_ms": 10000,
            "sources": [{"id": "srcA", "path": "tests/fixtures/media/src_a.txt", "duration_ms": 10000}],
            "tracks": {"video": clips, "captions": captions_from_words(list(CTX.words), clips, "srcA")}}


def texts(tl: dict[str, Any]) -> str:
    return " ".join(c["text"] for c in tl["tracks"]["captions"])


def on_grid(ms: int) -> bool:
    return ms == ((2 * ms * FPS + 1000) // 2000) * 1000 // FPS


def assert_frame_grid(tl: dict[str, Any]) -> None:
    for c in tl["tracks"]["video"]:
        assert on_grid(c["in_ms"]) and (on_grid(c["out_ms"]) or c["out_ms"] == 10000), c


# ---- trim ----------------------------------------------------------------------------------------------------
def test_trim_keeps_the_window_and_retimes_captions() -> None:
    tl0 = base()
    before = copy.deepcopy(tl0)
    tl = ops.trim(tl0, CTX, 1000, 5000)
    assert tl0 == before  # pure: the input is not mutated
    assert tl["tracks"]["video"] == [{"id": "c1", "source": "srcA", "in_ms": 1000, "out_ms": 5000}]
    assert tl["target_duration_ms"] == 4000
    assert texts(tl) == "Hello um world this is editing"
    assert tl["tracks"]["captions"][0]["start_ms"] == 0


@pytest.mark.parametrize("a, b", [(-1, 5000), (0, 10001), (5000, 5000), (6000, 5000)])
def test_trim_out_of_range(a: int, b: int) -> None:
    with pytest.raises(OpError, match="E_OP_RANGE"):
        ops.trim(base(), CTX, a, b)


# ---- delete_words --------------------------------------------------------------------------------------------
def test_delete_words_cuts_video_and_captions() -> None:
    tl = ops.delete_words(base(), CTX, ["w0001"])
    assert [(c["in_ms"], c["out_ms"]) for c in tl["tracks"]["video"]] == [(0, 1500), (1700, 10000)]
    assert [c["id"] for c in tl["tracks"]["video"]] == ["c1", "c2"]
    assert "um" not in texts(tl).split() and tl["target_duration_ms"] == 9800
    world = next(c for c in tl["tracks"]["captions"] if "world" in c["text"])
    assert texts(tl).startswith("Hello world") and world["end_ms"] == 2300 - 200


def test_delete_words_snaps_outward_to_the_frame_grid() -> None:
    ctx = EditContext(words=(*CTX.words, {"id": "w0008", "source": "srcA", "seg": 3, "text": "x",
                                          "start_ms": 8010, "end_ms": 8050}), source_id="srcA", base_dir=ROOT)
    tl = ops.delete_words(base(), ctx, ["w0008"])
    assert [(c["in_ms"], c["out_ms"]) for c in tl["tracks"]["video"]] == [(0, 8000), (8066, 10000)]
    assert_frame_grid(tl)


@pytest.mark.parametrize("ids, code", [(["w9999"], "E_OP_WORD"), ([], "E_OP_WORD")])
def test_delete_words_invalid(ids: list[str], code: str) -> None:
    with pytest.raises(OpError, match=code):
        ops.delete_words(base(), CTX, ids)


def test_delete_a_word_twice_fails() -> None:
    tl = ops.delete_words(base(), CTX, ["w0001"])
    with pytest.raises(OpError, match="not in the current timeline"):
        ops.delete_words(tl, CTX, ["w0001"])


# ---- set_caption_style ---------------------------------------------------------------------------------------
def test_style_applies_to_all_and_survives_cuts() -> None:
    tl = ops.set_caption_style(base(), CTX, "hook")
    assert {c["style"] for c in tl["tracks"]["captions"]} == {"hook"}
    tl = ops.delete_words(tl, CTX, ["w0003"])
    assert {c["style"] for c in tl["tracks"]["captions"]} == {"hook"}


def test_unknown_preset() -> None:
    with pytest.raises(OpError, match="E_OP_PRESET"):
        ops.set_caption_style(base(), CTX, "neon")


# ---- add_zoom ------------------------------------------------------------------------------------------------
def test_zoom_is_added_and_shifted_by_later_cuts() -> None:
    tl = ops.add_zoom(ops.delete_words(base(), CTX, ["w0001"]), CTX, 3000, 1.3, 1000)
    assert tl["tracks"]["effects"] == [{"type": "zoom", "target": "c2", "at_ms": 3000, "duration_ms": 1000,
                                        "scale": 1.3}]
    tl2 = ops.delete_words(tl, CTX, ["w0000"])  # cut before the zoom: zoom moves left by the cut length
    assert tl2["tracks"]["effects"][0]["at_ms"] == 3000 - 400
    with pytest.raises(OpError, match="E_OP_EFFECT"):  # cut inside the zoom window
        ops.delete_words(tl, CTX, ["w0004"])


@pytest.mark.parametrize("at, scale, dur", [(-1, 1.2, 500), (9500, 1.2, 1000), (100, 0.5, 500), (100, 3.0, 500),
                                            (100, 1.2, 0)])
def test_zoom_invalid(at: int, scale: float, dur: int) -> None:
    with pytest.raises(OpError, match="E_OP_"):
        ops.add_zoom(base(), CTX, at, scale, dur)


def test_overlapping_zooms_fail() -> None:
    tl = ops.add_zoom(base(), CTX, 1000, 1.2, 1000)
    with pytest.raises(OpError, match="E_OP_EFFECT"):
        ops.add_zoom(tl, CTX, 1500, 1.2, 1000)


# ---- set_duration --------------------------------------------------------------------------------------------
def test_set_duration_removes_silence_first_and_keeps_every_word() -> None:
    tl = ops.set_duration(base(), CTX, 5000)
    total = sum(c["out_ms"] - c["in_ms"] for c in tl["tracks"]["video"])
    assert abs(total - 5000) * FPS <= 1000 and tl["target_duration_ms"] == 5000
    assert texts(tl) == texts(base())  # 5580 ms of removable silence >= 5000 ms needed
    assert_frame_grid(tl)
    assert tl == ops.set_duration(base(), CTX, 5000)  # deterministic


def test_set_duration_trims_the_tail_when_silence_is_not_enough() -> None:
    tl = ops.set_duration(base(), CTX, 2000)
    total = sum(c["out_ms"] - c["in_ms"] for c in tl["tracks"]["video"])
    assert abs(total - 2000) * FPS <= 1000
    assert texts(tl).startswith("Hello um world") and "بكم" not in texts(tl)


@pytest.mark.parametrize("target", [0, 10001])
def test_set_duration_cannot_lengthen(target: int) -> None:
    with pytest.raises(OpError, match="E_OP_RANGE"):
        ops.set_duration(base(), CTX, target)


def test_every_op_output_is_valid_v0() -> None:
    from src.validate import validate
    tl = ops.add_zoom(ops.set_caption_style(ops.set_duration(ops.trim(base(), CTX, 500, 9000), CTX, 6000),
                                            CTX, "bold_box"), CTX, 1000, 1.25, 800)
    assert validate(tl, base_dir=ROOT) == []


# ---- history / undo ------------------------------------------------------------------------------------------
def test_history_persists_versions_and_undo_restores_previous(tmp_path: Path) -> None:
    h = History(tmp_path / "history")
    v0 = base()
    v1 = ops.trim(v0, CTX, 1000, 5000)
    assert h.save(v0) == 0 and h.save(v1) == 1
    assert json.loads((tmp_path / "history" / "v1.json").read_text("utf-8")) == v1
    assert h.undo() == v0 and h.versions() == [0]
    with pytest.raises(OpError, match="E_OP_UNDO"):
        h.undo()
