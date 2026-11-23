"""Edit core (H-0025 G4): pure operations on a timeline v0 document. No LLM; all times are computed by code (I-4).

Every op takes timeline vN plus an `EditContext` and returns a NEW timeline vN+1 (the input is never mutated).
The op body is pure computation; its last step is `src.validate.validate()` on the result, and any issue raises
`OpError`, so an op never returns a timeline the renderer would refuse. (`validate` stats the source files and
reads the schema; that is the only I/O, and it is the validator's, not the op's.)

Shared rules
  * Output time: video clips play back-to-back; positions are cumulative clip lengths (integer ms).
  * Words: `EditContext.words` is the immutable word list of one source (ids `w0000`..., source-time ms; built
    by `src.captions.words_from_transcript`, stored by the demo in `cache/<video_id>/edit/words.json`). A word is
    "in the timeline" when some part of its source range is covered by a clip. The timeline schema is unchanged.
  * Captions are rebuilt by code after every op that changes clips (`captions_from_words` over the new clips), so
    a cut word disappears from the captions and every other caption is re-timed. A preset set by
    `set_caption_style` is kept (the style of the current captions is re-applied).
  * Frame grid: every new cut point is snapped, in source time, to the canvas frame grid
    (ms = k * 1000 // fps). The renderer converts to the canvas fps before trimming, so each clip renders an
    exact number of frames and many cuts add no A/V drift. Pieces shorter than one frame are dropped.
  * Clip ids are renumbered `c1..cN` after a cut. Zoom effects keep their place: an effect after a cut moves
    left by the removed length; a cut that intersects a zoom window is refused (add zooms after cuts).
  * `target_duration_ms` becomes the new total, except for `set_duration`, which sets it to the target.

Error codes (`OpError.code`): E_OP_RANGE (time out of range or impossible length), E_OP_WORD (unknown, empty or
already-removed word ids), E_OP_PRESET (unknown caption preset), E_OP_EFFECT (zoom overlap / cut through a zoom),
E_OP_UNDO (nothing to undo), E_OP_INVALID (the result failed `validate`; the issues are attached).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.captions import Word, captions_from_words
from src.presets import CAPTION_PRESETS, ZOOM_MAX_SCALE, ZOOM_MIN_SCALE

Timeline = dict[str, Any]
PAD_MS = 120  # set_duration keeps this much silence on each side of speech
MIN_GAP_CUT_MS = 100  # set_duration ignores removable silence shorter than this


class OpError(ValueError):
    def __init__(self, code: str, message: str, issues: list[str] | None = None) -> None:
        self.code, self.issues = code, issues or []
        super().__init__(f"{code}: {message}" + "".join(f"\n  {i}" for i in self.issues))


@dataclass(frozen=True)
class EditContext:
    words: tuple[Word, ...]
    source_id: str
    base_dir: Path | None = None  # for validate(); default cwd
    allow_dev: bool = False  # ADR-0006 quarantine/dev sources (src.validate)
    caption_opts: dict[str, int] = field(default_factory=dict)  # max_words / max_ms for captions_from_words


# ---- helpers (pure) --------------------------------------------------------------------------------------------
def total_ms(tl: Timeline) -> int:
    return sum(c["out_ms"] - c["in_ms"] for c in tl["tracks"]["video"])


def _offsets(clips: list[dict[str, Any]]) -> list[int]:
    out, off = [], 0
    for c in clips:
        out.append(off)
        off += c["out_ms"] - c["in_ms"]
    return out


def word_pieces(tl: Timeline, ctx: EditContext) -> list[tuple[Word, int, int]]:
    """(word, out_start, out_end) for every covered piece of every word, sorted by output time."""
    clips = tl["tracks"]["video"]
    out = []
    for c, off in zip(clips, _offsets(clips), strict=True):
        if c["source"] != ctx.source_id:
            continue
        for w in ctx.words:
            s, e = max(w["start_ms"], c["in_ms"]), min(w["end_ms"], c["out_ms"])
            if s < e:
                out.append((w, off + s - c["in_ms"], off + e - c["in_ms"]))
    return sorted(out, key=lambda p: (p[1], p[2], p[0]["id"]))


def present_words(tl: Timeline, ctx: EditContext) -> list[tuple[Word, int, int]]:
    """Each word in the timeline once, in output order: (word, start of first piece, end of last piece)."""
    seen: dict[str, list[Any]] = {}
    for w, s, e in word_pieces(tl, ctx):
        if w["id"] in seen:
            seen[w["id"]][2] = max(seen[w["id"]][2], e)
        else:
            seen[w["id"]] = [w, s, e]
    return [(w, s, e) for w, s, e in seen.values()]


def _snap(ms: int, fps: int, mode: str) -> int:
    """Snap source ms to the frame grid: mode floor / ceil / near picks the frame index k; ms = k*1000 // fps."""
    if mode == "floor":
        k = ms * fps // 1000
    elif mode == "ceil":
        k = -((-ms * fps) // 1000)
    else:
        k = (2 * ms * fps + 1000) // 2000
    return k * 1000 // fps


SNAP = {"out": ("floor", "ceil"), "in": ("ceil", "floor"), "near": ("near", "near")}  # (start, end) of a removal


def _merge(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _cut(tl: Timeline, ctx: EditContext, removals: list[tuple[int, int, str]]) -> Timeline:
    """Remove output-time ranges [a, b) (snap mode per range, see SNAP) and return the rebuilt timeline."""
    fps = tl["canvas"]["fps"]
    min_len = -(-1000 // fps)  # one frame, rounded up
    clips = tl["tracks"]["video"]
    new_clips: list[dict[str, Any]] = []
    removed: list[tuple[int, int]] = []  # old output time
    for c, off in zip(clips, _offsets(clips), strict=True):
        cin, cout = c["in_ms"], c["out_ms"]
        cuts = []
        for a, b, mode in removals:
            a2, b2 = max(a, off), min(b, off + cout - cin)
            if a2 >= b2:
                continue
            sa, sb = cin + a2 - off, cin + b2 - off
            ms, me = SNAP[mode]
            sa = max(cin, _snap(sa, fps, ms)) if sa > cin else sa
            sb = min(cout, _snap(sb, fps, me)) if sb < cout else sb
            if sa < sb:
                cuts.append((sa, sb))
        cuts = _merge(cuts)
        keep, pos = [], cin
        for a, b in cuts:
            if a > pos:
                keep.append((pos, a))
            pos = max(pos, b)
        if pos < cout:
            keep.append((pos, cout))
        dropped = [k for k in keep if k[1] - k[0] < min_len]
        keep = [k for k in keep if k[1] - k[0] >= min_len]
        removed += [(off + a - cin, off + b - cin) for a, b in _merge(cuts + dropped)]
        new_clips += [{**c, "in_ms": a, "out_ms": b} for a, b in keep]
    if not new_clips:
        raise OpError("E_OP_RANGE", "the cut would remove the whole timeline")
    for i, c in enumerate(new_clips, 1):
        c["id"] = f"c{i}"
    removed = _merge(removed)

    effects = []
    for e in tl["tracks"].get("effects", []):
        a, b = e["at_ms"], e["at_ms"] + e["duration_ms"]
        hit = [r for r in removed if r[0] < b and a < r[1]]
        if hit:
            raise OpError("E_OP_EFFECT", f"cut {hit[0]} intersects the zoom window [{a}, {b}); add zooms after cuts")
        effects.append({**e, "at_ms": a - sum(r[1] - r[0] for r in removed if r[1] <= a)})
    out = copy.deepcopy(tl)
    out["tracks"]["video"] = new_clips
    if effects:
        offs = _offsets(new_clips)
        for e in effects:
            e["target"] = next(c["id"] for c, o in zip(new_clips, offs, strict=True)
                               if o <= e["at_ms"] < o + c["out_ms"] - c["in_ms"])
        out["tracks"]["effects"] = effects
    _recaption(out, ctx)
    out["target_duration_ms"] = total_ms(out)
    return out


def _recaption(tl: Timeline, ctx: EditContext) -> None:
    styles = {c.get("style") for c in tl["tracks"].get("captions", [])}
    caps = captions_from_words(list(ctx.words), tl["tracks"]["video"], ctx.source_id, **ctx.caption_opts)
    style = styles.pop() if len(styles) == 1 else None
    if style is not None:
        caps = [{**c, "style": style} for c in caps]
    tl["tracks"]["captions"] = caps


def _checked(tl: Timeline, ctx: EditContext) -> Timeline:
    from src.validate import validate

    issues = validate(tl, ctx.base_dir, allow_dev=ctx.allow_dev)
    if issues:
        raise OpError("E_OP_INVALID", "the result is not a valid renderable timeline", [str(i) for i in issues])
    return tl


# ---- ops -------------------------------------------------------------------------------------------------------
def trim(tl: Timeline, ctx: EditContext, start_ms: int, end_ms: int) -> Timeline:
    """Keep only the output-time window [start_ms, end_ms) of vN; everything before and after is cut.

    Requires 0 <= start_ms < end_ms <= total. Both edges snap to the nearest frame. Captions are re-timed so the
    kept part starts at 0; words outside the window leave the captions."""
    total = total_ms(tl)
    if not (0 <= start_ms < end_ms <= total):
        raise OpError("E_OP_RANGE", f"trim needs 0 <= start_ms < end_ms <= {total}, got [{start_ms}, {end_ms})")
    return _checked(_cut(tl, ctx, [(0, start_ms, "near"), (end_ms, total, "near")]), ctx)


def delete_words(tl: Timeline, ctx: EditContext, word_ids: list[str]) -> Timeline:
    """Cut each listed word's source range [start_ms, end_ms) out of the video; it leaves the captions too.

    Every id must be a known word that is still in the timeline. The cut snaps outward (start down, end up to the
    frame grid), so no sliver of the word stays; adjacent words lose at most one frame. Neighbouring deleted
    words merge into one cut."""
    if not word_ids:
        raise OpError("E_OP_WORD", "delete_words needs at least one word id")
    known = {w["id"] for w in ctx.words}
    unknown = [i for i in word_ids if i not in known]
    if unknown:
        raise OpError("E_OP_WORD", f"unknown word id(s): {', '.join(unknown)}")
    pieces = word_pieces(tl, ctx)
    present = {w["id"] for w, _, _ in pieces}
    gone = [i for i in word_ids if i not in present]
    if gone:
        raise OpError("E_OP_WORD", f"word id(s) not in the current timeline (already cut): {', '.join(gone)}")
    wanted = set(word_ids)
    return _checked(_cut(tl, ctx, [(s, e, "out") for w, s, e in pieces if w["id"] in wanted]), ctx)


def set_caption_style(tl: Timeline, ctx: EditContext, preset: str) -> Timeline:
    """Set `style` = preset on every caption (src/presets.py: clean, bold_box, hook). Later ops keep it.
    Fails when the preset is unknown or the timeline has no captions (nothing would change)."""
    if preset not in CAPTION_PRESETS:
        raise OpError("E_OP_PRESET", f"unknown preset {preset!r}; known: {', '.join(CAPTION_PRESETS)}")
    out = copy.deepcopy(tl)
    caps = out["tracks"].get("captions", [])
    if not caps:
        raise OpError("E_OP_PRESET", "the timeline has no captions to style")
    for c in caps:
        c["style"] = preset
    return _checked(out, ctx)


def add_zoom(tl: Timeline, ctx: EditContext, at_ms: int, scale: float, duration_ms: int) -> Timeline:
    """Add a punch-in zoom over output time [at_ms, at_ms + duration_ms): the frame is centre-cropped by 1/scale
    and scaled back to the canvas, with an instant cut in and out; captions are not zoomed.

    Requires 0 <= at_ms, duration_ms >= 1 frame, at_ms + duration_ms <= total, ZOOM_MIN_SCALE <= scale <=
    ZOOM_MAX_SCALE, and no overlap with an existing zoom. `target` is the clip that contains at_ms."""
    total, fps = total_ms(tl), tl["canvas"]["fps"]
    if not (0 <= at_ms and duration_ms * fps >= 1000 and at_ms + duration_ms <= total):
        raise OpError("E_OP_RANGE", f"zoom [{at_ms}, {at_ms + duration_ms}) must lie in [0, {total}] and last at "
                      "least one frame")
    if not ZOOM_MIN_SCALE <= scale <= ZOOM_MAX_SCALE:
        raise OpError("E_OP_RANGE", f"zoom scale {scale} outside [{ZOOM_MIN_SCALE}, {ZOOM_MAX_SCALE}]")
    effects = tl["tracks"].get("effects", [])
    for e in effects:
        if e["at_ms"] < at_ms + duration_ms and at_ms < e["at_ms"] + e["duration_ms"]:
            raise OpError("E_OP_EFFECT", f"zoom overlaps the zoom at {e['at_ms']} ms")
    clips = tl["tracks"]["video"]
    target = next(c["id"] for c, o in zip(clips, _offsets(clips), strict=True)
                  if o <= at_ms < o + c["out_ms"] - c["in_ms"])
    out = copy.deepcopy(tl)
    new = {"type": "zoom", "target": target, "at_ms": at_ms, "duration_ms": duration_ms, "scale": scale}
    out["tracks"]["effects"] = sorted([*copy.deepcopy(effects), new], key=lambda e: e["at_ms"])
    return _checked(out, ctx)


def set_duration(tl: Timeline, ctx: EditContext, target_ms: int) -> Timeline:
    """Shorten vN to target_ms (within one frame). Deterministic; never lengthens (target_ms > total fails).

    1. Silence first. Gaps are the stretches with no word: before the first word, between words, after the last.
       Each gap keeps PAD_MS next to speech; the rest is removable (gaps with < MIN_GAP_CUT_MS removable are
       skipped). Gaps are taken longest first (ties: earlier first), each fully, the last one only as much as is
       still needed. These cuts snap inward, so they never remove more than planned.
    2. If silence was not enough, the tail is cut at target_ms (nearest frame): the end of the clip goes.
    No word is cut in step 1; step 2 drops whatever speech lies after the target."""
    total, fps = total_ms(tl), tl["canvas"]["fps"]
    if not 0 < target_ms <= total:
        raise OpError("E_OP_RANGE", f"set_duration needs 0 < target_ms <= {total} (cannot lengthen), got {target_ms}")
    need = total - target_ms
    if need * fps > 1000:
        bounds, pos = [], 0
        for _, s, e in word_pieces(tl, ctx):
            if s > pos:
                bounds.append((pos, s))
            pos = max(pos, e)
        if pos < total:
            bounds.append((pos, total))
        gaps = []
        for a, b in bounds:
            ra = a if a == 0 else a + PAD_MS
            rb = b if b == total else b - PAD_MS
            if rb - ra >= MIN_GAP_CUT_MS:
                gaps.append((ra, rb))
        plan = []
        for ra, rb in sorted(gaps, key=lambda g: (-(g[1] - g[0]), g[0])):
            if need <= 0:
                break
            take = min(rb - ra, need)
            plan.append((ra, ra + take, "in"))
            need -= take
        cut = _cut(tl, ctx, plan) if plan else copy.deepcopy(tl)
        now = total_ms(cut)
        if (now - target_ms) * fps > 1000:
            cut = _cut(cut, ctx, [(target_ms, now, "near")])
        tl = cut
    out = copy.deepcopy(tl)
    out["target_duration_ms"] = target_ms
    if abs(total_ms(out) - target_ms) * fps > 1000:
        raise OpError("E_OP_RANGE", f"could not reach {target_ms} ms within one frame (got {total_ms(out)} ms)")
    return _checked(out, ctx)


OPS = {"trim": trim, "delete_words": delete_words, "set_caption_style": set_caption_style,
       "add_zoom": add_zoom, "set_duration": set_duration}
