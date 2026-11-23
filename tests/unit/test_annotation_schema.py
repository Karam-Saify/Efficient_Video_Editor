"""H-0035: annotation schema v0.1 (ADR-0025). Fixtures in tests/fixtures/annotations/{valid,invalid}/."""
from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from src.describe.schema import validate_annotation

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "annotations"
VALID = sorted((FIX / "valid").glob("*.json"))
INVALID_EXPECTED = {
    "i01_scene_role_no_origin.json": "E_SCHEMA",
    "i02_no_rights_id.json": "E_SCHEMA",
    "i03_training_usable_true.json": "E_SCHEMA",
    "i04_segment_end_before_start.json": "E_TIME_ORDER",
    "i05_job_no_permission.json": "E_PERMISSION",
    "i06_human_verified_no_machine_value.json": "E_DIFF_MISSING",
    "i07_edits_delivered_human_origin.json": "E_SCHEMA",
    "i08_choice_not_delivered.json": "E_VERSION_REF",
    "i09_keyframe_outside_scene.json": "E_RANGE",
    "i10_float_ms.json": "E_SCHEMA",
    "i11_bad_origin_value.json": "E_SCHEMA",
    "i12_job_field_no_origin.json": "E_SCHEMA",
}
# The 11 ADR-0023 job fields, keyed as in PARTNER_FEEDBACK_FORM FF-v0.1, with the mapped label_origin.
JOB_FIELDS = {
    "brief": "human_verified", "audience": "human_verified", "platform": "human_verified",
    "objective": "human_verified", "published_version": "human_verified", "likes_dislikes": "human_verified",
    "edits_delivered": "machine", "partner_choice": "human_verified", "corrections": "human_verified",
    "would_publish": "human_verified", "would_pay": "human_verified",
}


def load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def codes(rec: Any) -> list[str]:
    return sorted({e.code for e in validate_annotation(rec)})


def origin_paths(node: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
    if isinstance(node, dict):
        if "label_origin" in node:
            yield path
        for k, v in node.items():
            yield from origin_paths(v, (*path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from origin_paths(v, (*path, i))


def test_fixture_counts() -> None:
    assert len(VALID) >= 5 and len(INVALID_EXPECTED) >= 5
    assert sorted(p.name for p in (FIX / "invalid").glob("*.json")) == sorted(INVALID_EXPECTED)


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_fixture_passes(path: Path) -> None:
    assert validate_annotation(load(path)) == []


@pytest.mark.parametrize("name", sorted(INVALID_EXPECTED))
def test_invalid_fixture_fails_with_expected_code(name: str) -> None:
    assert codes(load(FIX / "invalid" / name)) == [INVALID_EXPECTED[name]]


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_label_origin_required_on_every_label(path: Path) -> None:
    rec = load(path)
    paths = list(origin_paths(rec))
    assert paths, "fixture carries no labels"
    for p in paths:
        r = copy.deepcopy(rec)
        node = r
        for k in p:
            node = node[k]
        del node["label_origin"]
        assert "E_SCHEMA" in codes(r), f"label_origin removable at {p}"


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_rights_id_required(path: Path) -> None:
    rec = load(path)
    key = "rights_id" if rec["record_type"] == "source" else "rights_ids"
    rec.pop(key)
    assert codes(rec) == ["E_SCHEMA"]


@pytest.mark.parametrize("bad", ["RR-7", "rr-007", "RR-P1-01", "", "RR-P003-02x"])
def test_rights_id_format(bad: str) -> None:
    rec = load(FIX / "valid" / "v1_source_machine.json")
    rec["rights_id"] = bad
    assert codes(rec) == ["E_SCHEMA"]


def test_job_fields_match_assurance_mapping_1_to_1() -> None:
    schema = load(ROOT / "schemas" / "annotation.schema.json")
    props = schema["$defs"]["job_record"]["properties"]
    admin = {"record_type", "annotation_version", "job_id", "partner_id", "rights_ids", "consent_version",
             "permissions", "training_usable"}
    assert set(props) - admin == set(JOB_FIELDS)
    for k, origin in JOB_FIELDS.items():
        assert props[k]["properties"]["label_origin"] == {"const": origin}, k
    form = (ROOT / "company/positions/05-assurance/PARTNER_FEEDBACK_FORM.md").read_text(encoding="utf-8")
    for k in JOB_FIELDS:
        assert f"`job.{k}`" in form, k


def test_version_not_delivered_is_caught_semantically() -> None:
    rec = load(FIX / "valid" / "v5_job_full.json")
    rec["corrections"]["value"][0]["version_label"] = "C"
    assert codes(rec) == ["E_VERSION_REF"]


def test_training_usable_cannot_be_true_even_if_consented() -> None:
    rec = load(FIX / "valid" / "v5_job_full.json")
    rec["permissions"]["training_consented"] = True
    assert validate_annotation(rec) == []
    rec["training_usable"] = True
    assert codes(rec) == ["E_SCHEMA"]


def test_integral_float_ms_rejected() -> None:
    rec = load(FIX / "valid" / "v1_source_machine.json")
    rec["scenes"][0]["end_ms"] = 3000.0
    assert codes(rec) == ["E_SCHEMA"]


def test_free_text_is_bounded() -> None:
    rec = load(FIX / "valid" / "v5_job_full.json")
    rec["likes_dislikes"]["value"]["A"]["likes"] = "x" * 501
    assert codes(rec) == ["E_SCHEMA"]


def test_scene_overlap_is_time_order() -> None:
    rec = load(FIX / "valid" / "v1_source_machine.json")
    rec["scenes"][1]["start_ms"] = 2500
    assert codes(rec) == ["E_TIME_ORDER"]
