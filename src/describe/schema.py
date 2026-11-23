"""Annotation record validator (schemas/annotation.schema.json + semantic rules; ADR-0025).

    python -m src.describe validate <record.json>

Codes: E_SCHEMA (JSON Schema), E_TIME_ORDER (start >= end or scenes out of order), E_RANGE (time outside the
media or a keyframe outside its scene), E_DUPLICATE (repeated id), E_DIFF_MISSING (a human_verified source label
without the machine_value it replaced), E_PERMISSION (job without evaluation or product_development permission),
E_VERSION_REF (a version label that was never delivered or shown).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any

from src.common import ROOT, read_json

ANNOTATION_SCHEMA = ROOT / "schemas" / "annotation.schema.json"


@dataclass(frozen=True)
class AnnotationError:
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"


@cache
def _validator() -> Any:
    from jsonschema import Draft202012Validator

    schema = read_json(ANNOTATION_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _float_ms(node: Any, path: str = "") -> list[AnnotationError]:
    """JSON Schema accepts 3000.0 as an integer; our data may not (CONVENTIONS: integer ms; H-0009)."""
    out: list[AnnotationError] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k.endswith("_ms") and isinstance(v, float):
                out.append(AnnotationError("E_SCHEMA", f"{path}/{k}", f"{v!r} is not an integer"))
            out += _float_ms(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _float_ms(v, f"{path}/{i}")
    return out


def _schema_errors(rec: Any) -> list[AnnotationError]:
    v = _validator()
    errs = list(v.iter_errors(rec))
    if not errs:
        return _float_ms(rec)
    # oneOf hides the useful message: re-validate against the branch the record claims to be.
    kind = rec.get("record_type") if isinstance(rec, dict) else None
    if kind in ("source", "job"):
        from jsonschema import Draft202012Validator

        sub = Draft202012Validator({"$ref": f"#/$defs/{kind}_record", "$defs": v.schema["$defs"]})
        errs = sorted(sub.iter_errors(rec), key=lambda e: list(e.absolute_path)) or errs
    return [AnnotationError("E_SCHEMA", "/" + "/".join(map(str, e.absolute_path)), e.message) for e in errs]


def _source_rules(rec: dict[str, Any]) -> list[AnnotationError]:
    out: list[AnnotationError] = []
    dur = rec["media"]["duration_ms"]
    prev_end = 0
    seen: set[int] = set()
    for i, sc in enumerate(rec["scenes"]):
        p = f"/scenes/{i}"
        if sc["id"] in seen:
            out.append(AnnotationError("E_DUPLICATE", p, f"scene id {sc['id']} repeated"))
        seen.add(sc["id"])
        if sc["start_ms"] >= sc["end_ms"] or sc["start_ms"] < prev_end:
            out.append(AnnotationError("E_TIME_ORDER", p, "scene must start after the previous one and before its end"))
        if sc["end_ms"] > dur:
            out.append(AnnotationError("E_RANGE", p, f"scene ends at {sc['end_ms']} > duration {dur}"))
        prev_end = sc["end_ms"]
        for k, kf in enumerate(sc["keyframes"]):
            if not sc["start_ms"] <= kf["t_ms"] <= sc["end_ms"]:
                out.append(AnnotationError("E_RANGE", f"{p}/keyframes/{k}", "keyframe outside its scene"))
        for field in ("description", "role"):
            lab = sc[field]
            if lab["label_origin"] == "human_verified" and "machine_value" not in lab:
                out.append(AnnotationError("E_DIFF_MISSING", f"{p}/{field}", "human_verified needs machine_value"))
    for i, seg in enumerate(rec["transcript"]["segments"]):
        p = f"/transcript/segments/{i}"
        if seg["start_ms"] > seg["end_ms"]:
            out.append(AnnotationError("E_TIME_ORDER", p, "segment starts after it ends"))
        if seg["end_ms"] > dur:
            out.append(AnnotationError("E_RANGE", p, f"segment ends at {seg['end_ms']} > duration {dur}"))
        for field in ("text", "language"):
            lab = seg[field]
            if lab["label_origin"] == "human_verified" and "machine_value" not in lab:
                out.append(AnnotationError("E_DIFF_MISSING", f"{p}/{field}", "human_verified needs machine_value"))
    return out


def _job_rules(rec: dict[str, Any]) -> list[AnnotationError]:
    out: list[AnnotationError] = []
    perm = rec["permissions"]
    if not (perm["evaluation"] or perm["product_development"]):
        out.append(AnnotationError("E_PERMISSION", "/permissions", "needs permission 1 or 2 (PARTNER_FEEDBACK_FORM)"))
    delivered = {e["version_label"] for e in rec["edits_delivered"]["value"]}
    if len(delivered) != len(rec["edits_delivered"]["value"]):
        out.append(AnnotationError("E_DUPLICATE", "/edits_delivered", "version label delivered twice"))
    refs: list[tuple[str, str]] = []
    if "partner_choice" in rec:
        pc = rec["partner_choice"]["value"]
        refs += [("/partner_choice/display_order", v) for v in pc["display_order"]]
        if pc["choice"] != "none":
            refs.append(("/partner_choice/choice", pc["choice"]))
    refs += [("/likes_dislikes", v) for v in rec.get("likes_dislikes", {}).get("value", {})]
    refs += [("/corrections", c["version_label"]) for c in rec.get("corrections", {}).get("value", [])]
    pv = rec.get("published_version", {}).get("value", {}).get("version_label")
    if pv:
        refs.append(("/published_version", pv))
    for path, label in refs:
        if label not in delivered:
            out.append(AnnotationError("E_VERSION_REF", path, f"version {label} was not delivered"))
    return out


def validate_annotation(rec: Any) -> list[AnnotationError]:
    """[] when the record is valid; schema errors first, semantic rules only on a schema-valid record."""
    errs = _schema_errors(rec)
    if errs:
        return errs
    return _source_rules(rec) if rec["record_type"] == "source" else _job_rules(rec)
