"""H-0024 G2b/G2c: the validator rejects every field the renderer does not implement (UNSUPPORTED_FIELD + JSON
path), and docs/CAPABILITIES.md is generated from the same table, so neither can drift."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src import capabilities as cap
from src.common import SCHEMA_PATH, read_json
from src.validate import validate

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "timelines"
UNSUPPORTED_EXPECTED = {  # fixture -> exact (code, path) list
    "u1_effects.json": [f"/tracks/effects/0/{k}" for k in ("at_ms", "duration_ms", "scale", "target", "type")]
    + [f"/tracks/effects/1/{k}" for k in ("at_ms", "duration_ms", "target", "type")],
    "u2_audio.json": [f"/tracks/audio/0/{k}" for k in ("duck_under_speech", "gain_db", "source")],
    "u3_crop_auto_face.json": ["/tracks/video/1/crop"],
    "u4_caption_style.json": ["/tracks/captions/0/style", "/tracks/captions/2/style"],
    "u5_dir_mismatch.json": ["/tracks/captions/2/dir"],
}


def load(name: str) -> dict[str, Any]:
    return json.loads((FIX / "unsupported" / name).read_text(encoding="utf-8"))


def issues(tl: Any) -> list[tuple[str, str]]:
    return [(e.code, e.path) for e in validate(tl, base_dir=ROOT)]


def test_unsupported_fixture_set_is_complete() -> None:
    assert sorted(p.name for p in (FIX / "unsupported").glob("*.json")) == sorted(UNSUPPORTED_EXPECTED)


@pytest.mark.parametrize("name", sorted(UNSUPPORTED_EXPECTED))
def test_unsupported_fixture_is_rejected_with_exact_paths(name: str) -> None:
    assert issues(load(name)) == [("UNSUPPORTED_FIELD", p) for p in UNSUPPORTED_EXPECTED[name]]


@pytest.mark.parametrize("name", sorted(UNSUPPORTED_EXPECTED))
def test_unsupported_fixture_is_otherwise_valid(name: str) -> None:
    """The only problem in each fixture is the unsupported field (schema + semantic rules pass)."""
    assert validate(load(name), base_dir=ROOT, check_support=False) == []


def test_crop_center_is_supported_auto_face_is_not() -> None:
    tl = load("u3_crop_auto_face.json")
    tl["tracks"]["video"][1]["crop"] = "center"
    assert issues(tl) == []


def test_empty_effects_and_audio_tracks_are_fine() -> None:
    tl = load("u1_effects.json")
    tl["tracks"]["effects"] = []
    tl["tracks"]["audio"] = []
    assert issues(tl) == []


@pytest.mark.parametrize("text, dir_, ok", [
    ("Link in bio", "ltr", True), ("Link in bio", "rtl", False),
    ("مرحبا", "rtl", True), ("مرحبا", "ltr", False),
    ("iPhone جديد جدا جدا", "rtl", False),  # libass lays this out LTR (first strong char is Latin)
    ("250", "rtl", True), ("250", "ltr", True),  # no strong character: either direction renders the same
])
def test_caption_dir_must_match_renderer_base_direction(text: str, dir_: str, ok: bool) -> None:
    tl = load("u5_dir_mismatch.json")
    tl["tracks"]["captions"][2].update(text=text, dir=dir_)
    assert issues(tl) == ([] if ok else [("UNSUPPORTED_FIELD", "/tracks/captions/2/dir")])


def test_unsupported_message_names_the_field() -> None:
    e = validate(load("u2_audio.json"), base_dir=ROOT)[0]
    assert "tracks.audio[].duck_under_speech" in e.message and "not implemented" in e.message


def test_render_refuses_unsupported_fields(tmp_path: Path) -> None:
    from src.render import render

    with pytest.raises(ValueError, match="UNSUPPORTED_FIELD"):
        render(load("u4_caption_style.json"), tmp_path / "o.mp4")


def _schema_paths(node: dict[str, Any], prefix: str = "") -> set[str]:
    out: set[str] = set()
    for k, sub in node.get("properties", {}).items():
        p = f"{prefix}{k}"
        if "properties" in sub:
            out |= _schema_paths(sub, p + ".")
        elif sub.get("type") == "array" and "properties" in sub.get("items", {}):
            out |= _schema_paths(sub["items"], p + "[].")
        else:
            out.add(p)
    return out


def test_every_schema_field_has_exactly_the_table_rows() -> None:
    assert {f.path for f in cap.FIELDS} == _schema_paths(read_json(SCHEMA_PATH))


def test_value_rows_cover_the_enum() -> None:
    schema = read_json(SCHEMA_PATH)
    crop = schema["properties"]["tracks"]["properties"]["video"]["items"]["properties"]["crop"]["enum"]
    assert sorted(f.value for f in cap.FIELDS if f.path == "tracks.video[].crop") == sorted(crop)


def test_capabilities_doc_is_generated_and_current() -> None:
    assert cap.DOC_PATH.read_text(encoding="utf-8") == cap.markdown(), "run: python -m src.capabilities --write"


def test_table_values_are_y_or_n() -> None:
    for f in cap.FIELDS:
        assert f.kind in ("render", "meta") and f.validated in "yn" and f.rendered in "yn", f
        assert len(f.validated) == len(f.rendered) == 1


def test_find_reports_json_pointers() -> None:
    tl = copy.deepcopy(load("u1_effects.json"))
    assert [p for p, _ in cap.find(tl, "tracks.effects[].type")] == ["/tracks/effects/0/type", "/tracks/effects/1/type"]
