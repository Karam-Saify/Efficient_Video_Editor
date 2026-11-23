"""Text direction from Unicode bidi classes (stdlib `unicodedata`; code decides, never the LLM).

strong_counts: number of strong left-to-right (L) and right-to-left (R, AL) characters.
text_dir:      "rtl" when R+AL strong characters outnumber L ones, else "ltr" (H-0024 G3 caption rule).
first_strong_dir: direction of the first strong character, or None; this is what libass's auto base
               direction (ASS `Encoding: -1`, FriBidi P2/P3) picks, i.e. what the renderer will lay out.
"""
from __future__ import annotations

import unicodedata

RTL_CLASSES = frozenset({"R", "AL"})


def strong_counts(text: str) -> tuple[int, int]:
    """(ltr, rtl) strong character counts."""
    ltr = rtl = 0
    for ch in text:
        c = unicodedata.bidirectional(ch)
        if c == "L":
            ltr += 1
        elif c in RTL_CLASSES:
            rtl += 1
    return ltr, rtl


def text_dir(text: str) -> str:
    ltr, rtl = strong_counts(text)
    return "rtl" if rtl > ltr else "ltr"


def first_strong_dir(text: str) -> str | None:
    for ch in text:
        c = unicodedata.bidirectional(ch)
        if c == "L":
            return "ltr"
        if c in RTL_CLASSES:
            return "rtl"
    return None
