"""Recipe language v0 compiler (H-0029): recipe + fill -> src/edit ops -> validated timeline v0. No LLM, no I/O
except reading recipe files/schemas and the validator's own source stat (docs/RECIPE_LANGUAGE.md is the spec).

    check_recipe(recipe)            -> list[(code, message)]   schema + semantic rules (shares, defaults, refs)
    load_recipe(id_or_path)         -> recipe dict             E_RECIPE_UNKNOWN / E_RECIPE_SCHEMA / ...
    resolve_fill(recipe, overrides) -> full param dict         E_PARAM_UNKNOWN / E_PARAM_TYPE / E_PARAM_RANGE
    unrendered(recipe)              -> UNRENDERED entries      one per recipe field the renderer cannot draw
    compile_recipe(recipe, overrides, words, source, ...) -> result dict with the timeline

All times are computed here, by code, in integer ms (I-4). The same recipe, fill, words and source give a
byte-identical timeline (`dumps`). Every failure is a `RecipeError` with a stable code; a recipe field that cannot
be drawn is never silently dropped: it is listed as UNRENDERED in the result and in `provenance.recipe.unrendered`.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

import jsonschema

from src.capabilities import FEATURES
from src.captions import Word, captions_from_words
from src.common import ROOT
from src.edit import ops as edit_ops
from src.edit.ops import PAD_MS, EditContext, OpError, Timeline, present_words, total_ms

RECIPES_DIR = ROOT / "recipes"
RECIPE_SCHEMA_PATH = ROOT / "schemas" / "recipe.schema.json"
SOURCE_ID = "src0"
CANVAS = {"width": 1080, "height": 1920, "fps": 30}
SPEECH_MIN_WPM = 30  # below this many ASR words per minute a source counts as "no speech" (dev manifest: 0-23 vs 123+)
GREETING_WINDOW_MS = 2000
DEV_MARKER = "ADR-0006 dev-only"
# Lower-cased, punctuation-stripped. Conservative: only hesitation sounds and greetings, never content words.
FILLERS = frozenset({"um", "uh", "uhm", "umm", "erm", "er", "hmm", "mm", "euh", "امم", "اممم", "ااا", "إمم"})
GREETINGS = frozenset({"hi", "hello", "hey", "welcome", "bonjour", "salut", "مرحبا", "مرحباً", "أهلا", "اهلا",
                       "هلا", "السلام", "عليكم"})
ADVISORY_FIELDS = ("use_case", "hook.rule", "pacing.wpm", "pacing.cut_interval_s", "pacing.max_dead_air_ms",
                   "language", "notes")


class RecipeError(ValueError):
    def __init__(self, code: str, message: str, unrendered: list[dict[str, str]] | None = None) -> None:
        self.code, self.unrendered = code, unrendered or []
        super().__init__(f"{code}: {message}")


# ---- recipe checks ---------------------------------------------------------------------------------------------
def _schema_validator() -> jsonschema.Draft202012Validator:
    strict = jsonschema.Draft202012Validator.TYPE_CHECKER.redefine("integer", lambda _c, x: type(x) is int)
    cls = jsonschema.validators.extend(jsonschema.Draft202012Validator, type_checker=strict)
    return cls(json.loads(RECIPE_SCHEMA_PATH.read_text(encoding="utf-8")))


def _type_ok(kind: str, v: Any) -> bool:
    if kind == "int":
        return type(v) is int
    if kind == "float":
        return type(v) in (int, float)
    if kind == "bool":
        return type(v) is bool
    return type(v) is str


def _range_error(name: str, spec: dict[str, Any], v: Any, source_ms: int | None) -> str | None:
    if spec["type"] == "enum":
        return None if v in spec["values"] else f"{name}={v!r} not one of {spec['values']}"
    if spec["type"] == "bool":
        return None
    hi = spec["max"]
    if hi == "source_duration":
        if source_ms is None:
            return None if v >= spec["min"] else f"{name}={v} below min {spec['min']}"
        hi = source_ms / 1000
    if not spec["min"] <= v <= hi:
        return f"{name}={v} outside [{spec['min']}, {hi}]"
    return None


def beat_ids(recipe: dict[str, Any]) -> set[str]:
    return {b["id"] for b in recipe["beats"]}


def check_recipe(recipe: Any) -> list[tuple[str, str]]:
    """Schema first (E_RECIPE_SCHEMA, stops there), then semantic rules the schema cannot express."""
    errs = sorted(_schema_validator().iter_errors(recipe), key=lambda e: list(e.absolute_path))
    if errs:
        return [("E_RECIPE_SCHEMA", f"/{'/'.join(map(str, e.absolute_path))}: {e.message}") for e in errs]
    out: list[tuple[str, str]] = []
    shares = sum(b["share_pct"] for b in recipe["beats"])
    if shares != 100:
        out.append(("E_RECIPE_SHARES", f"beat shares sum to {shares}, not 100"))
    ids = [b["id"] for b in recipe["beats"]]
    if len(set(ids)) != len(ids):
        out.append(("E_RECIPE_REF", f"duplicate beat id in {ids}"))
    params = recipe["params"]
    for name, spec in params.items():
        if not _type_ok(spec["type"], spec["default"]):
            out.append(("E_RECIPE_PARAM", f"default of {name} is not a {spec['type']}"))
        elif (msg := _range_error(name, spec, spec["default"], None)) is not None:
            out.append(("E_RECIPE_PARAM", f"default {msg}"))
    refs = [("zoom.beats", b) for b in recipe["zoom"].get("beats", [])]
    refs += [("captions.per_beat", b) for b in recipe["captions"].get("per_beat", {})]
    refs += [(f"overlays[{i}].beat", o["beat"]) for i, o in enumerate(recipe.get("overlays", []))]
    refs += [(f"pacing.wpm.{b}", b) for b in recipe["pacing"].get("wpm", {})]
    out += [("E_RECIPE_REF", f"{where} names unknown beat {b!r}") for where, b in refs if b not in beat_ids(recipe)]
    need = {"length_s": True, "punch_in_strength": recipe["zoom"]["placement"] != "none",
            "punch_in_every_s": recipe["zoom"]["placement"] == "rhythm",
            "caption_look": recipe["captions"]["preset"] != "none",
            "item_count": any("repeat_param" in b for b in recipe["beats"])}
    out += [("E_RECIPE_PARAM", f"recipe needs param {p!r}") for p, yes in need.items() if yes and p not in params]
    if "caption_look" in params and params["caption_look"]["type"] != "enum":
        out.append(("E_RECIPE_PARAM", "caption_look must be an enum"))
    return out


def load_recipe(ref: str | Path, recipes_dir: Path = RECIPES_DIR) -> dict[str, Any]:
    """A recipe by file path (ends in .json) or by id (looked up in recipes/), checked."""
    p = Path(ref)
    if p.suffix == ".json":
        if not p.is_file():
            raise RecipeError("E_RECIPE_UNKNOWN", f"no recipe file {p}")
        recipe = json.loads(p.read_text(encoding="utf-8"))
    else:
        found = [r for f in sorted(recipes_dir.glob("*.json"))
                 if (r := json.loads(f.read_text(encoding="utf-8"))).get("id") == str(ref)]
        if not found:
            known = sorted(json.loads(f.read_text(encoding="utf-8")).get("id", "?") for f in recipes_dir.glob("*.json"))
            raise RecipeError("E_RECIPE_UNKNOWN", f"unknown recipe id {ref!r}; known: {', '.join(known)}")
        recipe = found[0]
    issues = check_recipe(recipe)
    if issues:
        raise RecipeError(issues[0][0], "; ".join(m for _, m in issues))
    return recipe


# ---- fill ------------------------------------------------------------------------------------------------------
def parse_set(recipe: dict[str, Any], pairs: list[str]) -> dict[str, Any]:
    """CLI `--set k=v` strings -> typed values (by the param's declared type)."""
    out: dict[str, Any] = {}
    for pair in pairs:
        k, sep, v = pair.partition("=")
        if not sep:
            raise RecipeError("E_PARAM_TYPE", f"--set needs k=v, got {pair!r}")
        spec = recipe["params"].get(k)
        if spec is None:
            raise RecipeError("E_PARAM_UNKNOWN", f"recipe {recipe['id']} has no param {k!r}; "
                              f"known: {', '.join(sorted(recipe['params']))}")
        try:
            if spec["type"] == "int":
                out[k] = int(v)
            elif spec["type"] == "float":
                out[k] = float(v)
            elif spec["type"] == "bool":
                if v.lower() not in ("true", "false"):
                    raise ValueError(v)
                out[k] = v.lower() == "true"
            else:
                out[k] = v
        except ValueError:
            raise RecipeError("E_PARAM_TYPE", f"{k}={v!r} is not a {spec['type']}") from None
    return out


def resolve_fill(recipe: dict[str, Any], overrides: dict[str, Any], source_ms: int | None = None) -> dict[str, Any]:
    """Defaults overlaid with `overrides`; every value type- and range-checked. Returned in sorted key order."""
    params = recipe["params"]
    unknown = sorted(set(overrides) - set(params))
    if unknown:
        raise RecipeError("E_PARAM_UNKNOWN", f"recipe {recipe['id']} has no param(s) {', '.join(unknown)}; "
                          f"known: {', '.join(sorted(params))}")
    fill = {}
    for name in sorted(params):
        spec = params[name]
        v = overrides.get(name, spec["default"])
        if not _type_ok(spec["type"], v):
            raise RecipeError("E_PARAM_TYPE", f"{name}={v!r} is not a {spec['type']}")
        if (msg := _range_error(name, spec, v, source_ms)) is not None:
            raise RecipeError("E_PARAM_RANGE", msg)
        fill[name] = float(v) if spec["type"] == "float" else v
    return fill


# ---- honesty ---------------------------------------------------------------------------------------------------
def unrendered(recipe: dict[str, Any]) -> list[dict[str, str]]:
    """One UNRENDERED entry per recipe field (or list item) that asks for a feature the renderer cannot draw."""
    by_field = {f.recipe_field: f for f in FEATURES}
    out = []

    def add(field: str, key: str) -> None:
        f = by_field[key]
        if not f.rendered:
            out.append({"code": "UNRENDERED", "field": field, "feature": f.name, "reason": f.notes})

    if "music_bed" in recipe["sound"]:
        add("sound.music_bed", "sound.music_bed")
    if "sfx" in recipe["sound"]:
        add("sound.sfx", "sound.sfx")
    for i, o in enumerate(recipe.get("overlays", [])):
        add(f"overlays[{i}]:{o['id']}", "overlays")
    if recipe["captions"].get("per_beat"):
        add("captions.per_beat", "captions.per_beat")
    if recipe.get("structure", {}).get("reorder", "none") != "none":
        add("structure.reorder", "structure.reorder")
    for n in recipe.get("needs", []):
        add(f"needs[]={n}", f"needs[]={n}")
    return out


def advisory(recipe: dict[str, Any]) -> list[str]:
    """Fields kept for explanations only (the compiler cannot measure or act on them without a model)."""
    out = []
    for path in ADVISORY_FIELDS:
        node: Any = recipe
        for seg in path.split("."):
            node = node.get(seg) if isinstance(node, dict) else None
        if node is not None:
            out.append(path)
    return out


# ---- compile ---------------------------------------------------------------------------------------------------
def _norm(text: str) -> str:
    return "".join(ch for ch in text.lower() if not unicodedata.category(ch).startswith("P"))


def beat_windows(recipe: dict[str, Any], fill: dict[str, Any], total: int) -> list[dict[str, Any]]:
    """Beats as proportional output-time windows (integer ms). A repeat beat becomes <id>1..<id>N equal parts.
    Proportional only: without a model the compiler does not know where a beat's content is (docs)."""
    n = fill.get("item_count", 1)
    parts: list[tuple[str, str, int]] = []  # (id, group, units of 1/(100*n))
    for b in recipe["beats"]:
        if "repeat_param" in b:
            parts += [(f"{b['id']}{j}", b["id"], b["share_pct"]) for j in range(1, n + 1)]
        else:
            parts.append((b["id"], b["id"], b["share_pct"] * n))
    out, cum, units = [], 0, 100 * n
    for bid, group, u in parts:
        a = total * cum // units
        cum += u
        out.append({"id": bid, "group": group, "start_ms": a, "end_ms": total * cum // units})
    return out


def _zoom_times(recipe: dict[str, Any], fill: dict[str, Any], beats: list[dict[str, Any]], starts: list[int],
                total: int, fps: int, dur: int) -> list[int]:
    z = recipe["zoom"]

    def snap(t: int, window: int) -> int:
        t = next((s for s in starts if t <= s < t + window), t)  # the first word that starts in the window
        return t * fps // 1000 * 1000 // fps  # floor to the frame grid

    if z["placement"] == "rhythm":
        every = round(fill["punch_in_every_s"] * 1000)
        raw = [(k * every, every // 2) for k in range(1, total // every + 1)]
    elif z["placement"] == "beats":
        raw = [(b["start_ms"], (b["end_ms"] - b["start_ms"]) // 2) for b in beats if b["group"] in z["beats"]]
    elif z["placement"] == "fraction":
        raw = [(total * round(z["fraction"] * 1000) // 1000, 0)]
    else:
        raw = []
    out: list[int] = []
    for t, window in raw:
        at = snap(t, window) if window > 0 else t * fps // 1000 * 1000 // fps
        if at + dur <= total and (not out or out[-1] + dur <= at):
            out.append(at)
    return out


def compile_recipe(recipe: dict[str, Any], overrides: dict[str, Any], words: list[Word], source: dict[str, Any], *,
                   allow_dev: bool = False, base_dir: Path | None = ROOT, language: str = "") -> dict[str, Any]:
    """Compile one recipe + fill on one source. `source`: {"kind": "video", "path" (repo-relative), "duration_ms",
    "has_audio"} or {"kind": "images", "paths": [...]}. Returns {recipe, version, fill, beats, ops, unrendered,
    advisory, warnings, timeline}; raises RecipeError."""
    unr = unrendered(recipe)
    kind = source.get("kind", "video")
    want = recipe["source"].get("kind", "video")
    fill = resolve_fill(recipe, overrides, source.get("duration_ms"))
    if want == "images" or kind != want:
        why = ("image sources cannot be expressed in timeline v0 or rendered (no still-image input, no pan/zoom)"
               if want == "images" else f"recipe {recipe['id']} needs a {want} source, got {kind}")
        raise RecipeError("E_RECIPE_SOURCE_KIND", why, unr)
    dur = source["duration_ms"]
    wpm = len(words) * 60000 / dur
    speech = recipe["source"]["speech"]
    if speech == "required" and wpm < SPEECH_MIN_WPM:
        raise RecipeError("E_RECIPE_SOURCE", f"recipe {recipe['id']} needs speech; the source has {wpm:.1f} ASR "
                          f"words/min (< {SPEECH_MIN_WPM})", unr)
    if speech == "forbidden" and wpm >= SPEECH_MIN_WPM:
        raise RecipeError("E_RECIPE_SOURCE", f"recipe {recipe['id']} is for no-speech sources; the source has "
                          f"{wpm:.1f} ASR words/min (>= {SPEECH_MIN_WPM})", unr)
    captions_on = recipe["captions"]["preset"] != "none"
    ctx = EditContext(words=tuple(words) if captions_on else (), source_id=SOURCE_ID, base_dir=base_dir,
                      allow_dev=allow_dev)
    clips = [{"id": "c1", "source": SOURCE_ID, "in_ms": 0, "out_ms": dur}]
    selection = f"src.recipes {recipe['id']}@{recipe['version']}" + (f" language={language}" if language else "")
    tl: Timeline = {
        "version": "0.1", "canvas": dict(CANVAS), "target_duration_ms": dur,
        "sources": [{"id": SOURCE_ID, "path": source["path"], "duration_ms": dur,
                     "has_audio": bool(source.get("has_audio", True))}],
        "tracks": {"video": clips, "captions": captions_from_words(list(ctx.words), clips, SOURCE_ID)},
        "provenance": {"selection": selection + (f" {DEV_MARKER}" if allow_dev else "")},
    }
    log: list[dict[str, Any]] = []
    warnings: list[str] = []

    def run(op: str, **kw: Any) -> None:
        nonlocal tl
        try:
            tl = edit_ops.OPS[op](tl, ctx, **kw)
        except OpError as e:
            raise RecipeError("E_RECIPE_OP", f"{op} {kw}: {e}", unr) from None
        log.append({"op": op, **kw})

    if fill.get("start_at_s", 0) > 0:
        start = round(fill["start_at_s"] * 1000)
        if start >= total_ms(tl):
            raise RecipeError("E_PARAM_RANGE", f"start_at_s={fill['start_at_s']} is at or after the source end", unr)
        run("trim", start_ms=start, end_ms=total_ms(tl))
    if recipe["hook"]["cut_greeting"]:
        ids = [w["id"] for w, s, _ in present_words(tl, ctx)
               if s < GREETING_WINDOW_MS and _norm(w["text"]) in GREETINGS]
        if ids:
            run("delete_words", word_ids=ids)
    pw = present_words(tl, ctx)
    if pw and pw[0][1] > recipe["hook"]["lead_in_ms"]:
        run("trim", start_ms=pw[0][1] - PAD_MS, end_ms=total_ms(tl))
    if fill.get("cut_fillers"):
        ids = [w["id"] for w, _, _ in present_words(tl, ctx) if _norm(w["text"]) in FILLERS]
        if ids:
            run("delete_words", word_ids=ids)
    target, now = fill["length_s"] * 1000, total_ms(tl)
    if now < recipe["params"]["length_s"]["min"] * 1000:
        raise RecipeError("E_RECIPE_SOURCE", f"after the hook steps the source has {now} ms, shorter than the "
                          f"recipe minimum {recipe['params']['length_s']['min']} s", unr)
    if now > target:
        if recipe["pacing"]["duration_mode"] == "tighten":
            run("set_duration", target_ms=target)
        else:
            run("trim", start_ms=0, end_ms=target)
    else:
        warnings.append(f"SHORT_SOURCE: {now} ms <= length_s target {target} ms; nothing cut for length")
    if captions_on:
        if tl["tracks"].get("captions"):
            run("set_caption_style", preset=fill["caption_look"])
        else:
            unr.append({"code": "UNRENDERED", "field": "captions.preset", "feature": "captions",
                        "reason": "the source has no ASR words in the kept range; captions come from speech only"})
    total, fps = total_ms(tl), tl["canvas"]["fps"]
    beats = beat_windows(recipe, fill, total)
    if recipe["zoom"]["placement"] != "none":
        zdur = recipe["zoom"].get("duration_ms", 800)
        starts = [s for _, s, _ in present_words(tl, ctx)]
        for at in _zoom_times(recipe, fill, beats, starts, total, fps, zdur):
            run("add_zoom", at_ms=at, scale=fill["punch_in_strength"], duration_ms=zdur)
    tl["provenance"]["recipe"] = {"id": recipe["id"], "version": recipe["version"], "params": fill,
                                  "principles": list(recipe["principles"]),
                                  "unrendered": [u["field"] for u in unr]}
    from src.validate import validate

    issues = validate(tl, base_dir, allow_dev=allow_dev)
    if issues:
        raise RecipeError("E_RECIPE_INVALID", "; ".join(map(str, issues)), unr)
    return {"recipe": recipe["id"], "version": recipe["version"], "fill": fill, "beats": beats, "ops": log,
            "unrendered": unr, "advisory": advisory(recipe), "warnings": warnings, "timeline": tl}


def dumps(obj: Any) -> str:
    """Canonical JSON (sorted keys, UTF-8, 2-space indent, trailing newline): the byte-identity contract."""
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
