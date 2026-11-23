"""Timeline v0 (integer ms, ARCHITECTURE.md) -> the renderer's internal model (seconds, pre-H-0004 shape).

Input adapter only: the FFmpeg graph and ASS writer are unchanged (H-0004 keeps rendering out of scope).
Fields the renderer does not implement are rejected by the validator (UNSUPPORTED_FIELD, src/capabilities.py,
docs/CAPABILITIES.md; H-0024), so they never reach this adapter: clip `crop` other than centre,
caption `style`, `effects`, `audio`. Caption `dir` is not passed on: ASS Encoding -1 lets libass pick the base
direction from the first strong character, and the validator rejects a `dir` that disagrees (experiments/E6.md).
ms -> s conversion is code, never LLM (I-4).
Source `has_audio` (optional, default true; H-0009) is passed through: false makes the FFmpeg graph use
silence (anullsrc) for that source's clips instead of `[i:a]`, so silent sources render.
"""
from __future__ import annotations

from typing import Any


def to_render_model(tl: dict[str, Any]) -> dict[str, Any]:
    c = tl["canvas"]
    model: dict[str, Any] = {
        "output": {"width": c["width"], "height": c["height"], "fps": c["fps"], "reframe": "crop_center"},
        "sources": {s["id"]: {"path": s["path"], "duration": s["duration_ms"] / 1000,
                              "has_audio": s.get("has_audio", True)} for s in tl["sources"]},
        "clips": [{"id": v["id"], "source": v["source"], "in": v["in_ms"] / 1000, "out": v["out_ms"] / 1000}
                  for v in tl["tracks"]["video"]],
    }
    caps = tl["tracks"].get("captions", [])
    if caps:
        model["captions"] = {"items": [{"text": t["text"], "start": t["start_ms"] / 1000, "end": t["end_ms"] / 1000}
                                       for t in caps]}
    return model
