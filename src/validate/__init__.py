"""Timeline v0 validation: JSON Schema (draft 2020-12) first, then semantic rules the schema cannot express.

Every problem is an `Issue` with a stable `code`, a JSON-pointer `path` and a plain `message`, so the
list can be fed back to the LLM verbatim for a fix. All issues are returned, not just the first.
All time arithmetic is integer milliseconds, done here in code (I-4).

Codes (rule numbers from brief H-0004 / ARCHITECTURE.md):
  E_SCHEMA          structure/type error not covered by a more specific code. "integer" is strict here:
                    2000.0 is rejected (JSON Schema itself accepts integral floats; H-0009)
  E_SOURCE_PATH     source path is absolute, resolves (after symlinks) outside the repo, or lies under a
                    protected root (held-out, golden, quarantine; I-6, I-9). Checked before any file is opened
  E_SOURCE_MISSING  rule 1: clip/audio `source` not declared, or a declared source file does not exist
  E_SOURCE_HASH     rule 1: file exists, `sha256` given, and the hash differs
  E_RANGE           rule 2: not 0 <= in_ms < out_ms <= source.duration_ms
  E_OVERLAP         rule 3: two video clips use intersecting [in_ms, out_ms) ranges of the same source
  E_CAPTION_BOUNDS  rule 4: not 0 <= start_ms < end_ms <= total duration
  E_DURATION        rule 5: |total - target_duration_ms| > 1 frame (1000/fps ms)
  E_CAPTION_DIR     rule 6: caption `dir` missing or not rtl|ltr
  E_EFFECT_TYPE     rule 7: effect `type` not in the schema enum
  E_DUPLICATE_ID    a source, clip or caption id is used twice
  E_EFFECT_TARGET   an effect `target` is not a video clip id
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import jsonschema

from src.common import ROOT, SCHEMA_PATH, read_json

# Repo-relative roots a timeline source may never point into (CONSTITUTION I-6 held-out, I-9 rights).
PROTECTED_SOURCE_ROOTS = ("data/heldout", "data/golden", "quarantine")

# v0 says "integer milliseconds": a Python int, not an integral float and not a bool.
_STRICT_TYPES = jsonschema.Draft202012Validator.TYPE_CHECKER.redefine(
    "integer", lambda _checker, x: type(x) is int
)
_Validator = jsonschema.validators.extend(jsonschema.Draft202012Validator, type_checker=_STRICT_TYPES)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.code} {self.path or '/'}: {self.message}"


def _pointer(parts: Any) -> str:
    return "".join(f"/{p}" for p in parts)


def _schema_code(err: jsonschema.ValidationError) -> str:
    """Map a schema error to a rule code where the schema is what enforces that rule."""
    p = list(err.absolute_path)
    if len(p) >= 3 and p[0] == "tracks":
        track, field = p[1], (p[3] if len(p) > 3 else None)
        if err.validator == "required":
            missing = set(err.validator_value) - set(err.instance)
            if track == "captions" and len(p) == 3 and missing == {"dir"}:
                return "E_CAPTION_DIR"
        if track == "captions" and field == "dir":
            return "E_CAPTION_DIR"
        if track == "effects" and field == "type" and err.validator == "enum":
            return "E_EFFECT_TYPE"
        if track == "video" and field in ("in_ms", "out_ms") and err.validator == "minimum":
            return "E_RANGE"
        if track == "captions" and field in ("start_ms", "end_ms") and err.validator == "minimum":
            return "E_CAPTION_BOUNDS"
    return "E_SCHEMA"


def schema_issues(tl: Any) -> list[Issue]:
    validator = _Validator(read_json(SCHEMA_PATH))
    out = [Issue(_schema_code(e), _pointer(e.absolute_path), e.message) for e in validator.iter_errors(tl)]
    return sorted(out, key=lambda i: (i.path, i.code, i.message))


def total_duration_ms(tl: dict[str, Any]) -> int:
    """Clips play back-to-back, so the timeline length is the sum of clip lengths."""
    return sum(c["out_ms"] - c["in_ms"] for c in tl["tracks"]["video"])


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _duplicates(items: list[dict[str, Any]], prefix: str) -> list[Issue]:
    seen: dict[str, int] = {}
    out = []
    for i, it in enumerate(items):
        if it["id"] in seen:
            msg = f"id '{it['id']}' already used at index {seen[it['id']]}"
            out.append(Issue("E_DUPLICATE_ID", f"{prefix}/{i}/id", msg))
        seen.setdefault(it["id"], i)
    return out


def _source_path_problem(raw: str, base_dir: Path) -> str | None:
    """Why `raw` may not be used as a source path, or None. Never opens or stats the file itself."""
    if Path(raw).is_absolute():
        return "is absolute; use a path relative to the repo root"
    resolved = (base_dir / raw).resolve()  # follows symlinks, so a link cannot smuggle a protected file in
    root = ROOT.resolve()
    if not resolved.is_relative_to(root):
        return "resolves outside the repository"
    for r in PROTECTED_SOURCE_ROOTS:
        if resolved.is_relative_to(root / r):
            return f"is under the protected root '{r}/'"
    return None


def semantic_issues(tl: dict[str, Any], base_dir: Path) -> list[Issue]:
    """Assumes `tl` passed the structural part of the schema (no E_SCHEMA issues)."""
    errs: list[Issue] = []
    tracks = tl["tracks"]
    clips, caps = tracks["video"], tracks.get("captions", [])
    srcs = {s["id"]: s for s in tl["sources"]}
    errs += _duplicates(tl["sources"], "/sources") + _duplicates(clips, "/tracks/video")
    errs += _duplicates(caps, "/tracks/captions")

    # Rule 1: declared source files exist (the renderer opens every declared source); hash only if given.
    for i, s in enumerate(tl["sources"]):
        why = _source_path_problem(s["path"], base_dir)
        if why:
            errs.append(Issue("E_SOURCE_PATH", f"/sources/{i}/path", f"source '{s['id']}' path {s['path']!r} {why}"))
            continue
        p = base_dir / s["path"]
        if not p.is_file():
            errs.append(Issue("E_SOURCE_MISSING", f"/sources/{i}/path",
                              f"source '{s['id']}' file not found: {s['path']}"))
        elif "sha256" in s and _sha256(p) != s["sha256"]:
            errs.append(Issue("E_SOURCE_HASH", f"/sources/{i}/sha256",
                              f"source '{s['id']}' sha256 does not match {s['path']}"))
    known = ", ".join(srcs)
    for track in ("video", "audio"):
        for i, item in enumerate(tracks.get(track, [])):
            if item["source"] not in srcs:
                errs.append(Issue("E_SOURCE_MISSING", f"/tracks/{track}/{i}/source",
                                  f"unknown source '{item['source']}' (declared: {known})"))

    # Rule 2: 0 <= in_ms is a schema minimum (mapped to E_RANGE); here in_ms < out_ms <= duration_ms.
    for i, c in enumerate(clips):
        if c["out_ms"] <= c["in_ms"]:
            errs.append(Issue("E_RANGE", f"/tracks/video/{i}", f"clip '{c['id']}': out_ms ({c['out_ms']}) must be "
                              f"greater than in_ms ({c['in_ms']})"))
        src = srcs.get(c["source"])
        if src is not None and c["out_ms"] > src["duration_ms"]:
            errs.append(Issue("E_RANGE", f"/tracks/video/{i}/out_ms", f"clip '{c['id']}': out_ms ({c['out_ms']}) "
                              f"exceeds source '{src['id']}' duration_ms ({src['duration_ms']})"))

    # Rule 3: clips are sequential on the timeline, so "overlap" means re-using the same source footage.
    for j, b in enumerate(clips):
        for i in range(j):
            a = clips[i]
            if a["source"] == b["source"] and a["in_ms"] < b["out_ms"] and b["in_ms"] < a["out_ms"]:
                errs.append(Issue("E_OVERLAP", f"/tracks/video/{j}", f"clip '{b['id']}' [{b['in_ms']}, {b['out_ms']}) "
                                  f"overlaps clip '{a['id']}' [{a['in_ms']}, {a['out_ms']}) in source '{a['source']}'"))

    # Rule 4: captions inside the timeline (0 <= start_ms is a schema minimum).
    total = total_duration_ms(tl)
    for i, cap in enumerate(caps):
        if cap["end_ms"] <= cap["start_ms"]:
            errs.append(Issue("E_CAPTION_BOUNDS", f"/tracks/captions/{i}", f"caption '{cap['id']}': end_ms "
                              f"({cap['end_ms']}) must be greater than start_ms ({cap['start_ms']})"))
        if cap["end_ms"] > total:
            errs.append(Issue("E_CAPTION_BOUNDS", f"/tracks/captions/{i}/end_ms", f"caption '{cap['id']}': end_ms "
                              f"({cap['end_ms']}) is after the timeline end ({total} ms)"))

    # Rule 5: |total - target| <= 1000/fps ms, as integers: |total - target| * fps <= 1000.
    fps, target = tl["canvas"]["fps"], tl["target_duration_ms"]
    if abs(total - target) * fps > 1000:
        errs.append(Issue("E_DURATION", "/target_duration_ms", f"total duration {total} ms differs from target "
                          f"{target} ms by {total - target:+} ms; allowed is one frame (1000/{fps} ms)"))

    # Rules 6 and 7 are schema enums (mapped to E_CAPTION_DIR / E_EFFECT_TYPE). Effect targets are clip ids.
    clip_ids = {c["id"] for c in clips}
    for i, eff in enumerate(tracks.get("effects", [])):
        if eff["target"] not in clip_ids:
            errs.append(Issue("E_EFFECT_TARGET", f"/tracks/effects/{i}/target", f"effect target '{eff['target']}' "
                              "is not a video clip id"))
    return errs


def validate(tl: Any, base_dir: Path | None = None) -> list[Issue]:
    """Return every issue found; empty list means valid. Relative source paths resolve against `base_dir`
    (default: the current working directory, which is what the renderer's ffmpeg call uses)."""
    errs = schema_issues(tl)
    if any(e.code == "E_SCHEMA" for e in errs):
        return errs  # semantic rules need a well-formed document
    return errs + semantic_issues(tl, base_dir if base_dir is not None else Path.cwd())
