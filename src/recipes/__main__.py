"""python -m src.recipes compile --recipe <id|path> (--video <path> | --images <dir>) [--set k=v ...]
                                [--out timeline.json] [--result result.json] [--allow-dev]
   python -m src.recipes check [<id|path> ...]

compile reads the cached ingest of the video (cache/<video_id>/meta.json + transcript; run `python -m src.ingest
<video> --language auto --no-scenes` first; no ASR runs here), compiles, and writes the timeline (canonical JSON)
to --out and the full compile result to --result (default: stdout summary only). Exit 0 ok, 2 on a RecipeError
(`recipes: error: <CODE>: <message>` on stderr, plus the UNRENDERED list as JSON on stdout), 1 on bad usage.
`--allow-dev` is an explicit human opt-in for `quarantine/dev/` sources (ADR-0006); it marks the timeline
`ADR-0006 dev-only` in provenance.selection (H-0026 F2).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.captions import words_from_transcript
from src.common import ROOT, cache_dir, read_json, video_id
from src.recipes import RECIPES_DIR, RecipeError, compile_recipe, dumps, load_recipe, parse_set

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


def _video_source(video: Path, model: str, language: str) -> tuple[dict, list, str]:
    from src.ingest.__main__ import transcript_name

    video = video.resolve()
    if not video.is_file():
        raise RecipeError("E_RECIPE_INGEST", f"video not found: {video}")
    if not video.is_relative_to(ROOT):
        raise RecipeError("E_RECIPE_INGEST", "the video must be inside the repository "
                          "(timeline paths are repo-relative)")
    d = cache_dir(video_id(video))
    tr_p = d / transcript_name(model, language)
    if not (d / "meta.json").is_file() or not tr_p.is_file():
        raise RecipeError("E_RECIPE_INGEST", f"no cached ingest at {tr_p}; run python -m src.ingest {video} "
                          f"--language {language} --no-scenes first")
    meta, tr = read_json(d / "meta.json"), read_json(tr_p)
    src = {"kind": "video", "path": video.relative_to(ROOT).as_posix(), "duration_ms": int(meta["duration"] * 1000),
           "has_audio": bool(meta["has_audio"])}
    return src, words_from_transcript(tr, "src0"), str(tr.get("language", ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.recipes", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile")
    c.add_argument("--recipe", required=True)
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--video", type=Path)
    g.add_argument("--images", type=Path, help="directory of still images (photos_to_video)")
    c.add_argument("--set", action="append", default=[], metavar="K=V")
    c.add_argument("--out", type=Path)
    c.add_argument("--result", type=Path)
    c.add_argument("--allow-dev", action="store_true")
    c.add_argument("--model", default="large-v3-turbo")
    c.add_argument("--language", default="auto")
    k = sub.add_parser("check")
    k.add_argument("recipes", nargs="*")
    a = ap.parse_args(argv)

    if a.cmd == "check":
        refs = a.recipes or [str(p) for p in sorted(RECIPES_DIR.glob("*.json"))]
        bad = 0
        for ref in refs:
            try:
                r = load_recipe(ref)
                print(f"ok   {r['id']}@{r['version']}  {ref}")
            except RecipeError as e:
                bad += 1
                print(f"FAIL {ref}: {e}")
            except ValueError as e:  # malformed JSON
                bad += 1
                print(f"FAIL {ref}: E_RECIPE_SCHEMA: {e}")
        return 2 if bad else 0

    try:
        recipe = load_recipe(a.recipe)
        overrides = parse_set(recipe, a.set)
        if a.images is not None:
            paths = sorted(p for p in a.images.glob("*") if p.suffix.lower() in IMAGE_EXT)
            if not paths:
                raise RecipeError("E_RECIPE_SOURCE", f"no images ({', '.join(IMAGE_EXT)}) in {a.images}")
            src, words, lang = {"kind": "images", "paths": [str(p) for p in paths]}, [], ""
        else:
            src, words, lang = _video_source(a.video, a.model, a.language)
        res = compile_recipe(recipe, overrides, words, src, allow_dev=a.allow_dev, base_dir=ROOT, language=lang)
    except RecipeError as e:
        print(f"recipes: error: {e}", file=sys.stderr)
        print(json.dumps({"error": e.code, "unrendered": e.unrendered}, ensure_ascii=False, sort_keys=True))
        return 2
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(dumps(res["timeline"]), encoding="utf-8")
    if a.result:
        a.result.parent.mkdir(parents=True, exist_ok=True)
        a.result.write_text(dumps(res), encoding="utf-8")
    tl = res["timeline"]
    print(json.dumps({"recipe": res["recipe"], "ms": tl["target_duration_ms"], "clips": len(tl["tracks"]["video"]),
                      "captions": len(tl["tracks"].get("captions", [])), "zooms": len(tl["tracks"].get("effects", [])),
                      "unrendered": [u["field"] for u in res["unrendered"]], "warnings": res["warnings"],
                      "out": str(a.out) if a.out else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
