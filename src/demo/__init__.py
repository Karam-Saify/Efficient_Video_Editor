"""End-to-end demo, no LLM (H-0025 G5): ingest (cached) -> caption track (auto language) -> ops -> validate -> render.

    python -m src.demo --video <path> --ops <ops.json> --out out/ [--language auto] [--model large-v3-turbo]

Prints the output path, the final duration (timeline and ffprobe) and the language; exits non-zero with a
`demo: error: <step>: <reason>` line on any failure. Outputs, all git-ignored:
  out/<clip>__<ops>.mp4 (+ .ass, .timeline.json)   the render, its subtitles and the final timeline
  cache/<video_id>/edit/words.json                 word list with ids (source-time ms), from the transcript
  cache/<video_id>/edit/history/v<N>.json          v0 = whole clip + captions, then one version per op
A video under `quarantine/dev/` is allowed for internal development testing only (ADR-0006); the demo says so.

ops.json format
---------------
    {"ops": [
      {"op": "trim", "start": <time>, "end": <time>},
      {"op": "delete_words", "words": <words>},
      {"op": "set_caption_style", "preset": "clean" | "bold_box" | "hook"},
      {"op": "add_zoom", "at": <time>, "scale": 1.3, "duration_ms": 1200},
      {"op": "set_duration", "target_ms": 30000},
      {"op": "undo"}
    ]}

Ops run in order; each one sees the timeline the previous one produced (semantics: src/edit/ops.py). Times are
OUTPUT time of the current timeline and are resolved by code, never typed in as timestamps (CLAUDE.md rule 2):

    <time>  := {"word": i, "edge": "start" | "end"}     i-th word now in the timeline (0-based; negative = from end)
             | {"segment": i, "edge": "start" | "end"}  i-th transcript segment now in the timeline
             | {"fraction": f}                          f * current duration, 0 <= f <= 1, rounded to ms
             | <int>                                    literal ms (accepted, but avoid it in examples)
    <words> := {"nth": [i, ...]}                        i-th words now in the timeline
             | {"match": ["um", "uh"]}                  every word now in the timeline whose text, lower-cased
                                                        and stripped of punctuation, is in the list (>= 1 match)
             | {"ids": ["w0003", ...]}                  explicit ids from cache/<video_id>/edit/words.json
`duration_ms`, `scale` and `target_ms` are lengths and factors, not timestamps.
"""
from __future__ import annotations

import unicodedata
from typing import Any

from src.edit.ops import EditContext, OpError, Timeline, present_words, total_ms


def _pick(items: list[Any], i: Any, what: str) -> Any:
    if type(i) is not int or not -len(items) <= i < len(items):
        raise OpError("E_OP_RANGE", f"{what} index {i!r} out of range: the timeline has {len(items)} {what}s")
    return items[i]


def _edge(spec: dict[str, Any], s: int, e: int) -> int:
    edge = spec.get("edge")
    if edge not in ("start", "end"):
        raise OpError("E_OP_RANGE", f"edge must be 'start' or 'end', got {edge!r}")
    return s if edge == "start" else e


def resolve_time(spec: Any, tl: Timeline, ctx: EditContext) -> int:
    """A <time> spec -> output ms of the current timeline (see the module docstring)."""
    if type(spec) is int:
        return spec
    if not isinstance(spec, dict) or len({"word", "segment", "fraction"} & set(spec)) != 1:
        raise OpError("E_OP_RANGE", f"time spec must be an int or one of word/segment/fraction, got {spec!r}")
    words = present_words(tl, ctx)
    if "word" in spec:
        _, s, e = _pick(words, spec["word"], "word")
        return _edge(spec, s, e)
    if "segment" in spec:
        segs: dict[int, list[int]] = {}
        for w, s, e in words:
            segs.setdefault(w["seg"], [s, e])[1] = e
        s, e = _pick(list(segs.values()), spec["segment"], "segment")
        return _edge(spec, s, e)
    f = spec["fraction"]
    if not isinstance(f, (int, float)) or isinstance(f, bool) or not 0 <= f <= 1:
        raise OpError("E_OP_RANGE", f"fraction must be a number in [0, 1], got {f!r}")
    return round(total_ms(tl) * f)


def _norm(text: str) -> str:
    return "".join(ch for ch in text.lower() if not unicodedata.category(ch).startswith("P"))


def resolve_words(spec: Any, tl: Timeline, ctx: EditContext) -> list[str]:
    """A <words> spec -> word ids now in the timeline (see the module docstring)."""
    words = [w for w, _, _ in present_words(tl, ctx)]
    if isinstance(spec, dict) and set(spec) == {"nth"} and isinstance(spec["nth"], list):
        return [_pick(words, i, "word")["id"] for i in spec["nth"]]
    if isinstance(spec, dict) and set(spec) == {"match"} and isinstance(spec["match"], list):
        wanted = {_norm(str(m)) for m in spec["match"]}
        ids = [w["id"] for w in words if _norm(w["text"]) in wanted]
        if not ids:
            raise OpError("E_OP_WORD", f"no word in the timeline matches {spec['match']!r}")
        return ids
    if isinstance(spec, dict) and set(spec) == {"ids"} and isinstance(spec["ids"], list):
        return [str(i) for i in spec["ids"]]
    raise OpError("E_OP_WORD", f"words spec must be {{nth|match|ids: [...]}}, got {spec!r}")
