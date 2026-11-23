"""Suggested creative roles, rules `roles-v0` (deterministic; every suggestion is a `machine` label).

Position first: the first scene is the hook, the last the call to action, the second introduces the product.
Middle scenes: at least half covered by VAD speech -> proof (someone vouching), otherwise demo (showing).
A single-scene clip is a hook. Scene length decides only when a middle scene is too short to show anything
(< 1 s): it is `other`.
"""
from __future__ import annotations

from src.describe.audio import overlap_ms

RULES_VERSION = "roles-v0"
MIN_DEMO_MS = 1000


def suggest_roles(scenes: list[tuple[int, int]], speech: list[tuple[int, int]]) -> list[str]:
    n = len(scenes)
    out: list[str] = []
    for i, (s, e) in enumerate(scenes):
        if i == 0:
            out.append("hook")
        elif i == n - 1:
            out.append("cta")
        elif i == 1 and n >= 4:
            out.append("product_intro")
        elif e - s < MIN_DEMO_MS:
            out.append("other")
        elif 2 * overlap_ms((s, e), speech) >= e - s:
            out.append("proof")
        else:
            out.append("demo")
    return out
