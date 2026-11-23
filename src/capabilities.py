"""What the timeline v0 schema allows vs. what the validator checks and the renderer really does (H-0024 G2c).

Single source of truth for two things:
  * `src.validate` rejects every present field (or field value) whose row has kind "render" and rendered "n"
    with code UNSUPPORTED_FIELD and the JSON path, so nothing in a timeline silently does nothing;
  * `docs/CAPABILITIES.md` is generated from `FIELDS` (`python -m src.capabilities --write`); a unit test
    fails if the file drifts or if a schema field has no row.

kind: "render" = an instruction to the renderer; "meta" = bookkeeping/integrity data that is checked but is
not a render instruction (never rejected for being unrendered).
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from src.common import ROOT

DOC_PATH = ROOT / "docs" / "CAPABILITIES.md"


@dataclass(frozen=True)
class Field:
    path: str  # dotted, `[]` = every array item, e.g. "tracks.video[].crop"
    kind: str  # "render" | "meta"
    validated: str  # "y" | "n"
    rendered: str  # "y" | "n"
    notes: str
    value: Any = None  # when set, the row is about this one value of the field (e.g. crop = "auto_face")

    @property
    def unsupported(self) -> bool:
        return self.kind == "render" and self.rendered == "n"


FIELDS: tuple[Field, ...] = (
    Field("version", "meta", "y", "n", 'const "0.1"; document version, not a render input'),
    Field("canvas.width", "render", "y", "y", "output width (scale/crop target)"),
    Field("canvas.height", "render", "y", "y", "output height"),
    Field("canvas.fps", "render", "y", "y", "output frame rate; also the one-frame tolerance of E_DURATION"),
    Field("target_duration_ms", "meta", "y", "n", "checked against the sum of clip lengths (E_DURATION)"),
    Field("sources[].id", "render", "y", "y", "key that clips reference (E_DUPLICATE_ID, E_SOURCE_MISSING)"),
    Field("sources[].path", "render", "y", "y", "ffmpeg input; repo-relative, protected roots refused "
          "(E_SOURCE_PATH, E_SOURCE_MISSING)"),
    Field("sources[].duration_ms", "meta", "y", "n", "bounds clip out_ms (E_RANGE)"),
    Field("sources[].sha256", "meta", "y", "n", "integrity check when given (E_SOURCE_HASH)"),
    Field("sources[].has_audio", "render", "y", "y", "false: that source's clips get silence (anullsrc)"),
    Field("tracks.video[].id", "meta", "y", "n", "unique id (E_DUPLICATE_ID); effect target key"),
    Field("tracks.video[].source", "render", "y", "y", "which input the clip trims"),
    Field("tracks.video[].in_ms", "render", "y", "y", "trim start, source time (E_RANGE)"),
    Field("tracks.video[].out_ms", "render", "y", "y", "trim end, source time (E_RANGE, E_OVERLAP)"),
    Field("tracks.video[].crop", "render", "y", "y", "centre crop to the canvas", value="center"),
    Field("tracks.video[].crop", "render", "y", "n", "no face tracking yet: UNSUPPORTED_FIELD", value="auto_face"),
    Field("tracks.captions[].id", "meta", "y", "n", "unique id (E_DUPLICATE_ID)"),
    Field("tracks.captions[].text", "render", "y", "y", "burned in via libass; EXP-008 font pair (Noto Sans "
          "Arabic + Noto Sans, `\\fn` run tags); a character outside both fonts' ranges fails the render"),
    Field("tracks.captions[].start_ms", "render", "y", "y", "output time (E_CAPTION_BOUNDS)"),
    Field("tracks.captions[].end_ms", "render", "y", "y", "output time (E_CAPTION_BOUNDS)"),
    Field("tracks.captions[].style", "render", "y", "n", "one default style only: UNSUPPORTED_FIELD "
          "(presets arrive in H-0025)"),
    Field("tracks.captions[].dir", "render", "y", "y", "libass auto base direction (ASS Encoding -1) follows the "
          "first strong character; a `dir` that disagrees with it cannot be rendered: UNSUPPORTED_FIELD"),
    Field("tracks.effects[].type", "render", "y", "n", "effects are not rendered yet: UNSUPPORTED_FIELD "
          "(zoom arrives in H-0025)"),
    Field("tracks.effects[].target", "render", "y", "n", "must be a clip id (E_EFFECT_TARGET); not rendered"),
    Field("tracks.effects[].at_ms", "render", "y", "n", "not rendered"),
    Field("tracks.effects[].duration_ms", "render", "y", "n", "not rendered"),
    Field("tracks.effects[].scale", "render", "y", "n", "not rendered"),
    Field("tracks.audio[].source", "render", "y", "n", "extra audio tracks are not mixed: UNSUPPORTED_FIELD"),
    Field("tracks.audio[].gain_db", "render", "y", "n", "not rendered"),
    Field("tracks.audio[].duck_under_speech", "render", "y", "n", "not rendered"),
    Field("provenance.selection", "meta", "y", "n", "free text; type-checked only"),
    Field("provenance.prompt_versions", "meta", "y", "n", "object; type-checked only"),
    Field("provenance.model_ids", "meta", "y", "n", "object; type-checked only"),
)


def find(tl: Any, path: str) -> Iterator[tuple[str, Any]]:
    """Every (JSON pointer, value) present in `tl` at a dotted `path` (`[]` = each array item)."""
    nodes: list[tuple[str, Any]] = [("", tl)]
    for seg in path.split("."):
        key, each = (seg[:-2], True) if seg.endswith("[]") else (seg, False)
        nxt: list[tuple[str, Any]] = []
        for ptr, node in nodes:
            if not isinstance(node, dict) or key not in node:
                continue
            ptr, node = f"{ptr}/{key}", node[key]
            if each:
                if isinstance(node, list):
                    nxt += [(f"{ptr}/{i}", item) for i, item in enumerate(node)]
            else:
                nxt.append((ptr, node))
        nodes = nxt
    yield from nodes


def unsupported_fields(tl: Any) -> list[tuple[str, Field]]:
    """(pointer, row) for every present field/value the renderer does not implement, in document order."""
    out = []
    for f in FIELDS:
        if not f.unsupported:
            continue
        for ptr, val in find(tl, f.path):
            if f.value is None or val == f.value:
                out.append((ptr, f))
    return sorted(out, key=lambda x: x[0])


def markdown() -> str:
    lines = [
        "# Timeline v0 capabilities",
        "",
        "Generated from `src/capabilities.py` by `python -m src.capabilities --write`; "
        "`tests/unit/test_capabilities.py` fails if this file drifts. Do not edit by hand.",
        "",
        "A field with kind `render` and rendered `n` is rejected by `src.validate` with `UNSUPPORTED_FIELD` "
        "and its JSON path, so a timeline never carries an instruction the renderer silently ignores. "
        "`meta` fields are checked but are not render instructions.",
        "",
        "| field | kind | validated | rendered | notes |",
        "|---|---|---|---|---|",
    ]
    for f in FIELDS:
        name = f"`{f.path}`" + (f' = `"{f.value}"`' if f.value is not None else "")
        lines.append(f"| {name} | {f.kind} | {f.validated} | {f.rendered} | {f.notes.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.capabilities")
    ap.add_argument("--write", action="store_true", help=f"write {DOC_PATH.relative_to(ROOT)}")
    a = ap.parse_args(argv)
    if a.write:
        DOC_PATH.write_text(markdown(), encoding="utf-8")
        print(DOC_PATH)
    else:
        sys.stdout.write(markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
