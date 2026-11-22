"""Timeline validation: JSON schema + semantic checks the schema cannot express.

Errors are plain, specific strings so they can be fed back to the LLM verbatim for a fix.
"""
from __future__ import annotations

from typing import Any

import jsonschema

from src.common import SCHEMA_PATH, read_json

_EPS = 1e-6


def total_duration(tl: dict[str, Any]) -> float:
    return sum(c["out"] - c["in"] for c in tl["clips"])


def validate(tl: dict[str, Any]) -> list[str]:
    schema = read_json(SCHEMA_PATH)
    errs = [
        f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in jsonschema.Draft202012Validator(schema).iter_errors(tl)
    ]
    if errs:
        return errs  # semantic checks assume a well-formed document

    frame = 1.0 / tl["output"]["fps"]
    seen: set[str] = set()
    for i, c in enumerate(tl["clips"]):
        where = f"clips[{i}] (id={c['id']})"
        if c["id"] in seen:
            errs.append(f"{where}: duplicate clip id")
        seen.add(c["id"])
        src = tl["sources"].get(c["source"])
        if src is None:
            errs.append(f"{where}: unknown source '{c['source']}' (known: {', '.join(tl['sources'])})")
            continue
        if c["out"] <= c["in"] + _EPS:
            errs.append(f"{where}: out ({c['out']}) must be greater than in ({c['in']})")
        elif c["out"] - c["in"] < frame - _EPS:
            errs.append(f"{where}: clip is shorter than one frame ({c['out'] - c['in']:.3f}s)")
        if c["out"] > src["duration"] + _EPS:
            errs.append(f"{where}: out ({c['out']}) exceeds source duration ({src['duration']})")

    total = total_duration(tl)
    target = tl["output"].get("target_duration")
    if target is not None and abs(total - target) > frame + _EPS:
        errs.append(f"timeline: total duration {total:.3f}s differs from target {target:.3f}s by more than one frame")

    items = tl.get("captions", {}).get("items", [])
    prev_end = 0.0
    for i, cap in sorted(enumerate(items), key=lambda p: p[1]["start"]):
        if cap["end"] <= cap["start"] + _EPS:
            errs.append(f"captions[{i}]: end ({cap['end']}) must be greater than start ({cap['start']})")
        if cap["end"] > total + _EPS:
            errs.append(f"captions[{i}]: end ({cap['end']}) is after timeline end ({total:.3f})")
        if cap["start"] < prev_end - _EPS:
            errs.append(f"captions[{i}]: overlaps previous caption (starts {cap['start']}, previous ends {prev_end})")
        prev_end = max(prev_end, cap["end"])
    return errs
