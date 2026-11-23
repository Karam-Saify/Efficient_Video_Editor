"""Transcript -> timeline `tracks.captions` (H-0024 G3). Pure function; all time arithmetic is code (I-4).

Input: an ingest transcript (`segments[].words[]` with `start`/`end` in source seconds; a segment without
word timestamps counts as one unit), the timeline's video clips (`source`, `in_ms`, `out_ms`, played
back-to-back in array order) and the id of the source the transcript belongs to.

Each word is converted to integer source ms, clamped to every clip of that source it intersects, and
shifted to output time (clip offset + (t - in_ms)); zero-length pieces are dropped. Consecutive words in
the same clip and the same segment are grouped into one caption of at most `max_words` words spanning at
most `max_ms`. `dir` is the direction of the first strong character (src/bidi.first_strong_dir), which is what
libass lays out (ASS Encoding -1), so the track never carries a `dir` the validator rejects (H-0025 addendum,
Operator decision on H-0024 OQ1); text with no strong character gets "ltr" (either renders the same).

H-0025: `words_from_transcript` gives every word a stable id (`w0000`, transcript order) and integer source ms;
`captions_from_words` builds the track from such a word list, so the edit ops can re-time captions after any
cut. `caption_track(transcript, ...)` is the two composed.
"""
from __future__ import annotations

from typing import Any

from src.bidi import first_strong_dir

Word = dict[str, Any]  # {"id", "source", "seg", "text", "start_ms", "end_ms"}; source time, integer ms


def words_from_transcript(transcript: dict[str, Any], source_id: str) -> list[Word]:
    """Every non-empty word with id `w<NNNN>` in transcript order. A segment without word timestamps is one word."""
    out: list[Word] = []
    for si, seg in enumerate(transcript.get("segments", [])):
        words = seg.get("words") or [{"w": seg["text"], "start": seg["start"], "end": seg["end"]}]
        for w in words:
            text = str(w["w"]).strip()
            if text:
                out.append({"id": f"w{len(out):04d}", "source": source_id, "seg": si, "text": text,
                            "start_ms": round(float(w["start"]) * 1000), "end_ms": round(float(w["end"]) * 1000)})
    return out


def _caption(cid: str, group: list[tuple[int, str, int, int]]) -> dict[str, Any]:
    text = " ".join(g[1] for g in group)
    return {"id": cid, "text": text, "start_ms": group[0][2], "end_ms": group[-1][3],
            "dir": first_strong_dir(text) or "ltr"}


def captions_from_words(
    words: list[Word], clips: list[dict[str, Any]], source_id: str, *,
    max_words: int = 4, max_ms: int = 2500, id_prefix: str = "cap",
) -> list[dict[str, Any]]:
    units = [(w["seg"], w["text"], w["start_ms"], w["end_ms"]) for w in words if w["source"] == source_id]
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


def caption_track(
    transcript: dict[str, Any], clips: list[dict[str, Any]], source_id: str, *,
    max_words: int = 4, max_ms: int = 2500, id_prefix: str = "cap",
) -> list[dict[str, Any]]:
    return captions_from_words(words_from_transcript(transcript, source_id), clips, source_id,
                               max_words=max_words, max_ms=max_ms, id_prefix=id_prefix)
