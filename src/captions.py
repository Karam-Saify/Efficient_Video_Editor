"""Transcript -> timeline `tracks.captions` (H-0024 G3). Pure function; all time arithmetic is code (I-4).

Input: an ingest transcript (`segments[].words[]` with `start`/`end` in source seconds; a segment without
word timestamps counts as one unit), the timeline's video clips (`source`, `in_ms`, `out_ms`, played
back-to-back in array order) and the id of the source the transcript belongs to.

Each word is converted to integer source ms, clamped to every clip of that source it intersects, and
shifted to output time (clip offset + (t - in_ms)); zero-length pieces are dropped. Consecutive words in
the same clip and the same segment are grouped into one caption of at most `max_words` words spanning at
most `max_ms`. `dir` comes from the text's strong characters (src/bidi.text_dir).
"""
from __future__ import annotations

from typing import Any

from src.bidi import text_dir


def _units(transcript: dict[str, Any]) -> list[tuple[int, str, int, int]]:
    """(segment index, text, start_ms, end_ms) in source time."""
    out = []
    for si, seg in enumerate(transcript.get("segments", [])):
        words = seg.get("words") or [{"w": seg["text"], "start": seg["start"], "end": seg["end"]}]
        for w in words:
            text = str(w["w"]).strip()
            if text:
                out.append((si, text, round(float(w["start"]) * 1000), round(float(w["end"]) * 1000)))
    return out


def _caption(cid: str, group: list[tuple[int, str, int, int]]) -> dict[str, Any]:
    text = " ".join(g[1] for g in group)
    return {"id": cid, "text": text, "start_ms": group[0][2], "end_ms": group[-1][3], "dir": text_dir(text)}


def caption_track(
    transcript: dict[str, Any], clips: list[dict[str, Any]], source_id: str, *,
    max_words: int = 4, max_ms: int = 2500, id_prefix: str = "cap",
) -> list[dict[str, Any]]:
    units = _units(transcript)
    groups: list[list[tuple[int, str, int, int]]] = []  # each: (segment, text, out_start, out_end)
    offset = 0
    for clip in clips:
        cin, cout = clip["in_ms"], clip["out_ms"]
        if clip["source"] == source_id:
            group: list[tuple[int, str, int, int]] = []
            for seg, text, s, e in units:
                s2, e2 = max(s, cin), min(e, cout)
                if e2 <= s2:
                    continue
                piece = (seg, text, offset + s2 - cin, offset + e2 - cin)
                if group and (group[-1][0] != seg or len(group) >= max_words or piece[3] - group[0][2] > max_ms):
                    groups.append(group)
                    group = []
                group.append(piece)
            if group:
                groups.append(group)
        offset += cout - cin
    return [_caption(f"{id_prefix}{i}", g) for i, g in enumerate(groups, 1)]
