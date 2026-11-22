"""Timeline v0 (integer ms, ARCHITECTURE.md) -> the renderer's internal model (seconds, pre-H-0004 shape).

Input adapter only: the FFmpeg graph and ASS writer are unchanged (H-0004 keeps rendering out of scope).
Not rendered yet (v0 fields accepted by the schema but ignored here): clip `crop` (always centre crop),
caption `style` and `dir` (ASS uses one default style with Encoding -1, see experiments/E6.md),
`effects`, `audio`. ms -> s conversion is code, never LLM (I-4).
"""
from __future__ import annotations

from typing import Any


def to_render_model(tl: dict[str, Any]) -> dict[str, Any]:
    c = tl["canvas"]
    model: dict[str, Any] = {
        "output": {"width": c["width"], "height": c["height"], "fps": c["fps"], "reframe": "crop_center"},
        "sources": {s["id"]: {"path": s["path"], "duration": s["duration_ms"] / 1000} for s in tl["sources"]},
        "clips": [{"id": v["id"], "source": v["source"], "in": v["in_ms"] / 1000, "out": v["out_ms"] / 1000}
                  for v in tl["tracks"]["video"]],
    }
    caps = tl["tracks"].get("captions", [])
    if caps:
        model["captions"] = {"items": [{"text": t["text"], "start": t["start_ms"] / 1000, "end": t["end_ms"] / 1000}
                                       for t in caps]}
    return model
