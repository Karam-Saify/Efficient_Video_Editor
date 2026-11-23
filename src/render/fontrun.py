"""EXP-008 font pair for captions (H-0024 G3): Noto Sans Arabic for Arabic runs, Noto Sans for Latin and digits.

A port of the locked EXP-008 §5.3 run-splitting rule (experiments/exp008_render.py, unchanged there):
  A  Arabic ranges -> Noto Sans Arabic        L  Latin/ASCII/punctuation ranges -> Noto Sans
  S  space: takes the class of both neighbours when they agree, else A
  X  anything else (Hebrew, Thai, emoji, U+061C, U+00AD, control characters, ...): refused, because
     libass would pick an undeclared fallback font. The caller fails the render loudly.
Tags are `{\\fn...}` at class changes, starting from A (the ASS style font); never a trailing tag.
`tests/unit/test_fontrun.py` checks this port against the EXP-008 instrument and its §5.3 table.
"""
from __future__ import annotations

FONT_A = "Noto Sans Arabic"  # /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf (EXP-008 §5.1, RR-001)
FONT_L = "Noto Sans"  # /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf (EXP-008 §5.1, RR-011)
TAG = {"A": "{\\fn" + FONT_A + "}", "L": "{\\fn" + FONT_L + "}"}

A_RANGES = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]
L_RANGES = [(0x0021, 0x007E), (0x00A1, 0x024F), (0x2010, 0x2027), (0x2030, 0x205E)]
A_EXCLUDED = {0x061C}
L_EXCLUDED = {0x00AD}


class UnsupportedCharacter(ValueError):
    """Text contains a code point neither declared font is allowed to draw."""


def classify_cp(c: str) -> str:
    o = ord(c)
    if o == 0x20:
        return "S"
    if o not in A_EXCLUDED and any(a <= o <= b for a, b in A_RANGES):
        return "A"
    if o not in L_EXCLUDED and any(a <= o <= b for a, b in L_RANGES):
        return "L"
    return "X"


def classify(s: str) -> list[str]:
    k = [classify_cp(c) for c in s]
    bad = [f"U+{ord(c):04X}" for c, x in zip(s, k, strict=True) if x == "X"]
    if bad:
        raise UnsupportedCharacter(f"outside the EXP-008 font pair ({FONT_A} + {FONT_L}): {', '.join(bad)}")
    i = 0
    while i < len(k):
        if k[i] != "S":
            i += 1
            continue
        j = i
        while j < len(k) and k[j] == "S":
            j += 1
        left = k[i - 1] if i > 0 else None
        right = k[j] if j < len(k) else None
        k[i:j] = [left if (left is not None and left == right) else "A"] * (j - i)
        i = j
    return k


def _tag(s: str, cur: str) -> tuple[str, str]:
    out = []
    for c, x in zip(s, classify(s), strict=True):
        if x != cur:
            out.append(TAG[x])
            cur = x
        out.append(c)
    return "".join(out), cur


def tag_runs(s: str) -> str:
    """One caption line -> text with `{\\fn...}` run tags. Raises UnsupportedCharacter."""
    return _tag(s, "A")[0]


def tag_lines(text: str) -> str:
    """Caption text with `\\n` line breaks -> ASS text (`\\N`). The font tag state carries across `\\N` inside
    one event, so each line is tagged starting from the class the previous line ended in."""
    cur, out = "A", []
    for line in text.split("\n"):
        tagged, cur = _tag(line, cur)
        out.append(tagged)
    return "\\N".join(out)
