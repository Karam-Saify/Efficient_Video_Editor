"""H-0029: recipe language v0 (schemas/recipe.schema.json, recipes/*.json) and its compiler (src/recipes)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from src import capabilities as cap
from src.recipes import (
    ADVISORY_FIELDS,
    DEV_MARKER,
    RecipeError,
    beat_windows,
    check_recipe,
    compile_recipe,
    dumps,
    load_recipe,
    parse_set,
    resolve_fill,
    unrendered,
)
from src.validate import validate

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures"
RECIPE_FILES = sorted((ROOT / "recipes").glob("*.json"))
VIDEO_IDS = ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R12"]
INVALID_EXPECTED = {
    "i1_shares_not_100.json": "E_RECIPE_SHARES", "i2_default_out_of_range.json": "E_RECIPE_PARAM",
    "i3_unknown_param_name.json": "E_RECIPE_SCHEMA", "i4_zoom_unknown_beat.json": "E_RECIPE_REF",
    "i5_no_principles.json": "E_RECIPE_SCHEMA", "i6_rhythm_without_every.json": "E_RECIPE_PARAM",
    "i7_float_ms.json": "E_RECIPE_SCHEMA",
}
PROV_INVALID = {"q1_not_object.json": "/provenance/recipe", "q2_missing_id.json": "/provenance/recipe",
                "q3_float_version.json": "/provenance/recipe/version", "q4_bad_principle.json":
                "/provenance/recipe/principles/0", "q5_extra_key.json": "/provenance/recipe",
                "q6_param_list.json": "/provenance/recipe/params/x"}
DUR = 60000


def synth_words(dur: int = DUR, first_ms: int = 900) -> list[dict[str, Any]]:
    """~140 wpm speech with a greeting first, an 'um' every 10th word and a 1.5 s pause every 12 words."""
    out, t, i = [], first_ms, 0
    while t + 350 < dur:
        text = "hello" if i == 0 else ("um" if i % 10 == 5 else f"word{i}")
        out.append({"id": f"w{i:04d}", "source": "src0", "seg": i // 12, "text": text, "start_ms": t,
                    "end_ms": t + 300})
        t += 1800 if i % 12 == 11 else 400
        i += 1
    return out


SOURCE = {"kind": "video", "path": "tests/fixtures/media/src_a.txt", "duration_ms": DUR, "has_audio": True}


def comp(rid: str, overrides: dict[str, Any] | None = None, words: list | None = None, **kw: Any) -> dict[str, Any]:
    return compile_recipe(load_recipe(rid), overrides or {}, synth_words() if words is None else words,
                          kw.pop("source", SOURCE), base_dir=ROOT, **kw)


# ---- recipes and schema ----------------------------------------------------------------------------------------
def test_twelve_recipes_with_unique_ids() -> None:
    ids = [json.loads(p.read_text(encoding="utf-8"))["id"] for p in RECIPE_FILES]
    assert len(ids) == 12 and len(set(ids)) == 12
    assert sorted(ids) == sorted([*VIDEO_IDS, "photos_to_video"])  # R11 replaced (Founder scope change)


@pytest.mark.parametrize("path", RECIPE_FILES, ids=lambda p: p.stem)
def test_every_recipe_validates(path: Path) -> None:
    assert check_recipe(json.loads(path.read_text(encoding="utf-8"))) == []


@pytest.mark.parametrize("path", sorted((FIX / "recipes" / "valid").glob("*.json")), ids=lambda p: p.stem)
def test_valid_recipe_fixtures(path: Path) -> None:
    assert check_recipe(json.loads(path.read_text(encoding="utf-8"))) == []


def test_fixture_sets_are_complete() -> None:
    assert len(list((FIX / "recipes" / "valid").glob("*.json"))) >= 5
    assert sorted(p.name for p in (FIX / "recipes" / "invalid").glob("*.json")) == sorted(INVALID_EXPECTED)
    assert len(list((FIX / "timelines" / "provenance" / "valid").glob("*.json"))) >= 5
    assert sorted(p.name for p in (FIX / "timelines" / "provenance" / "invalid").glob("*.json")) == sorted(PROV_INVALID)


@pytest.mark.parametrize("name", sorted(INVALID_EXPECTED))
def test_invalid_recipe_fixture_gives_its_code(name: str) -> None:
    issues = check_recipe(json.loads((FIX / "recipes" / "invalid" / name).read_text(encoding="utf-8")))
    assert [c for c, _ in issues] == [INVALID_EXPECTED[name]]
    with pytest.raises(RecipeError) as e:
        load_recipe(FIX / "recipes" / "invalid" / name)
    assert e.value.code == INVALID_EXPECTED[name]


@pytest.mark.parametrize("path", sorted((FIX / "timelines" / "provenance" / "valid").glob("*.json")),
                         ids=lambda p: p.stem)
def test_timeline_provenance_recipe_valid(path: Path) -> None:
    assert validate(json.loads(path.read_text(encoding="utf-8")), ROOT) == []


@pytest.mark.parametrize("name", sorted(PROV_INVALID))
def test_timeline_provenance_recipe_invalid(name: str) -> None:
    tl = json.loads((FIX / "timelines" / "provenance" / "invalid" / name).read_text(encoding="utf-8"))
    assert [(i.code, i.path) for i in validate(tl, ROOT)] == [("E_SCHEMA", PROV_INVALID[name])]


def test_existing_timeline_fixtures_still_valid() -> None:  # ADR-0014: the schema change is additive only
    for p in sorted((FIX / "timelines" / "valid").glob("*.json")):
        assert validate(json.loads(p.read_text(encoding="utf-8")), ROOT) == [], p.name


# ---- lookup and fill -------------------------------------------------------------------------------------------
def test_unknown_recipe_id() -> None:
    with pytest.raises(RecipeError) as e:
        load_recipe("R99")
    assert e.value.code == "E_RECIPE_UNKNOWN" and "R01" in str(e.value)
    with pytest.raises(RecipeError) as e:
        load_recipe("recipes/nope.json")
    assert e.value.code == "E_RECIPE_UNKNOWN"


def test_defaults_fill_every_param_sorted() -> None:
    r = load_recipe("R01")
    fill = resolve_fill(r, {})
    assert list(fill) == sorted(r["params"]) and fill["length_s"] == 35 and fill["punch_in_strength"] == 1.10


@pytest.mark.parametrize("overrides, code", [
    ({"speed": 2}, "E_PARAM_UNKNOWN"),
    ({"length_s": 30.5}, "E_PARAM_TYPE"), ({"length_s": True}, "E_PARAM_TYPE"), ({"length_s": "30"}, "E_PARAM_TYPE"),
    ({"cut_fillers": 1}, "E_PARAM_TYPE"), ({"punch_in_strength": "1.1"}, "E_PARAM_TYPE"),
    ({"length_s": 19}, "E_PARAM_RANGE"), ({"length_s": 61}, "E_PARAM_RANGE"),
    ({"punch_in_strength": 1.3}, "E_PARAM_RANGE"), ({"caption_look": "neon"}, "E_PARAM_RANGE"),
])
def test_param_errors(overrides: dict[str, Any], code: str) -> None:
    with pytest.raises(RecipeError) as e:
        resolve_fill(load_recipe("R01"), overrides)
    assert e.value.code == code


def test_start_at_range_is_the_source_length() -> None:
    r = load_recipe("R09")
    assert resolve_fill(r, {"start_at_s": 59.0}, DUR)["start_at_s"] == 59.0
    with pytest.raises(RecipeError, match="E_PARAM_RANGE"):
        resolve_fill(r, {"start_at_s": 61.0}, DUR)


def test_parse_set_types() -> None:
    r = load_recipe("R01")
    assert parse_set(r, ["length_s=30", "cut_fillers=false", "punch_in_strength=1.2", "caption_look=hook"]) == {
        "length_s": 30, "cut_fillers": False, "punch_in_strength": 1.2, "caption_look": "hook"}
    for bad, code in (["length_s=abc"], "E_PARAM_TYPE"), (["cut_fillers=yes"], "E_PARAM_TYPE"), (["x=1"],
                      "E_PARAM_UNKNOWN"), (["length_s"], "E_PARAM_TYPE"):
        with pytest.raises(RecipeError) as e:
            parse_set(r, bad)
        assert e.value.code == code


# ---- honesty: UNRENDERED ----------------------------------------------------------------------------------------
def test_unrendered_lists_every_missing_feature_by_field() -> None:
    assert [u["field"] for u in unrendered(load_recipe("R02"))] == [
        "sound.music_bed", "sound.sfx", "overlays[0]:price_cta", "captions.per_beat", "needs[]=b_roll"]
    assert unrendered(load_recipe("R08")) == [{"code": "UNRENDERED", "field": "needs[]=keyword_highlight",
                                               "feature": "keyword_highlight", "reason": "no caption emphasis"}]


def test_every_recipe_schema_property_is_classified() -> None:
    """No recipe field can be silently dropped: each top-level property is compiled, a feature source
    (UNRENDERED when unrendered) or advisory."""
    schema = json.loads((ROOT / "schemas" / "recipe.schema.json").read_text(encoding="utf-8"))
    compiled = {"$schema", "id", "version", "name", "tier", "golden_set", "source", "beats", "hook", "pacing",
                "captions", "zoom", "params", "principles"}
    feature_roots = {f.recipe_field.split(".")[0].split("[")[0] for f in cap.FEATURES}
    advisory = {a.split(".")[0] for a in ADVISORY_FIELDS}
    assert set(schema["properties"]) <= compiled | feature_roots | advisory | {"sound"}
    needs = set(schema["properties"]["needs"]["items"]["enum"])
    assert needs == {f.recipe_field.removeprefix("needs[]=") for f in cap.FEATURES
                     if f.recipe_field.startswith("needs")}


def test_no_feature_claims_to_render_today() -> None:  # the compiler has no handler for any feature yet
    assert [f.name for f in cap.FEATURES if f.rendered] == []


def test_compile_result_and_provenance_carry_unrendered() -> None:
    res = comp("R02")
    assert [u["field"] for u in res["unrendered"]] == res["timeline"]["provenance"]["recipe"]["unrendered"]
    assert "sound.music_bed" in res["timeline"]["provenance"]["recipe"]["unrendered"]
    assert "tracks" in res["timeline"] and "audio" not in res["timeline"]["tracks"]  # nothing unrendered leaks in


# ---- compile ---------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("rid", VIDEO_IDS)
def test_every_video_recipe_compiles_to_a_valid_timeline(rid: str) -> None:
    res = comp(rid)
    tl = res["timeline"]
    assert validate(tl, ROOT) == []
    assert abs(tl["target_duration_ms"] - res["fill"]["length_s"] * 1000) <= 34
    style = load_recipe(rid)["params"]["caption_look"]["default"]
    assert {c["style"] for c in tl["tracks"]["captions"]} == {style}


def test_provenance_content() -> None:
    res = comp("R01", {"length_s": 30})
    p = res["timeline"]["provenance"]
    assert p["recipe"] == {"id": "R01", "version": 1, "params": res["fill"], "unrendered": [
        "sound.music_bed", "captions.per_beat", "needs[]=keyword_highlight"],
        "principles": ["P-HOOK-3S", "P-MUTED-CAPTION", "P-ZOOM-RHYTHM"]}
    assert p["recipe"]["params"]["length_s"] == 30
    assert p["selection"] == "src.recipes R01@1" and DEV_MARKER not in p["selection"]


def test_allow_dev_sets_the_adr0006_marker() -> None:
    res = comp("R01", allow_dev=True)
    assert res["timeline"]["provenance"]["selection"].endswith("ADR-0006 dev-only")


def test_hook_steps_cut_greeting_lead_in_and_fillers() -> None:
    res = comp("R01")
    ops = [o["op"] for o in res["ops"]]
    assert ops[:3] == ["delete_words", "trim", "delete_words"]  # greeting, lead-in, fillers
    texts = " ".join(c["text"] for c in res["timeline"]["tracks"]["captions"])
    assert "hello" not in texts and " um " not in f" {texts} "
    assert res["timeline"]["tracks"]["captions"][0]["start_ms"] <= 300
    kept = comp("R03")  # cut_fillers default false: the 'um's stay (H-0028: the human voice is the proof)
    assert " um " in " " + " ".join(c["text"] for c in kept["timeline"]["tracks"]["captions"]) + " "


def test_zooms_follow_placement_and_style_guide_limits() -> None:
    r01 = comp("R01")["timeline"]["tracks"]["effects"]
    assert len(r01) >= 5 and all(b["at_ms"] - a["at_ms"] >= 3000 for a, b in zip(r01, r01[1:], strict=False))
    r05 = comp("R05", {"item_count": 4})
    items = [b for b in r05["beats"] if b["group"] == "item"]
    assert [b["id"] for b in items] == ["item1", "item2", "item3", "item4"]
    assert len(r05["timeline"]["tracks"]["effects"]) == 4
    assert all(i["start_ms"] <= z["at_ms"] < i["end_ms"] for i, z in zip(items, r05["timeline"]["tracks"]["effects"],
                                                                          strict=True))
    r04 = comp("R04")["timeline"]
    assert [e["at_ms"] for e in r04["tracks"]["effects"]] == [25000 * 650 // 1000 * 30 // 1000 * 1000 // 30]


def test_beat_windows_cover_the_timeline_exactly() -> None:
    b = beat_windows(load_recipe("R05"), {"item_count": 3}, 35000)
    assert b[0]["start_ms"] == 0 and b[-1]["end_ms"] == 35000
    assert all(x["end_ms"] == y["start_ms"] for x, y in zip(b, b[1:], strict=False))


def test_determinism_same_fill_byte_identical() -> None:
    a = dumps(comp("R09", {"length_s": 40, "start_at_s": 2.0})["timeline"])
    b = dumps(comp("R09", {"start_at_s": 2.0, "length_s": 40})["timeline"])
    assert a == b
    assert dumps(comp("R09", {"length_s": 40, "start_at_s": 2.0})) == dumps(comp("R09", {"start_at_s": 2.0,
                                                                                         "length_s": 40}))


def test_speech_recipe_on_no_speech_source_fails_coded() -> None:
    with pytest.raises(RecipeError) as e:
        comp("R01", words=synth_words()[:5])
    assert e.value.code == "E_RECIPE_SOURCE" and e.value.unrendered


def test_short_source_below_recipe_minimum_fails_coded() -> None:
    src = {**SOURCE, "duration_ms": 15000}
    with pytest.raises(RecipeError) as e:
        comp("R01", words=synth_words(15000), source=src)
    assert e.value.code == "E_RECIPE_SOURCE"


def test_r04_any_speech_on_silent_source_reports_captions_unrendered() -> None:
    res = comp("R04", words=[])
    assert res["timeline"]["tracks"]["captions"] == []
    assert res["unrendered"][-1]["field"] == "captions.preset"


# ---- photos_to_video (replaces R11; Founder scope change) ------------------------------------------------------
def _images(d: Path, n: int) -> list[str]:
    d.mkdir()
    for j in range(n):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        f"testsrc=size=320x568:rate=1:duration=1,hue=h={j * 60}", "-frames:v", "1",
                        str(d / f"img{j}.png")], check=True)
    return sorted(str(p) for p in d.glob("*.png"))


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
@pytest.mark.parametrize("n", [3, 4, 5])
def test_photos_to_video_fails_with_designed_code_and_lists_unrendered(tmp_path: Path, n: int) -> None:
    paths = _images(tmp_path / "set", n)
    with pytest.raises(RecipeError) as e:
        compile_recipe(load_recipe("photos_to_video"), {}, [], {"kind": "images", "paths": paths}, base_dir=ROOT)
    assert e.value.code == "E_RECIPE_SOURCE_KIND"
    fields = [u["field"] for u in e.value.unrendered]
    assert {"needs[]=image_source", "needs[]=pan_zoom", "sound.music_bed", "overlays[1]:brand_offer"} <= set(fields)


def test_photos_to_video_param_errors_come_first() -> None:
    with pytest.raises(RecipeError, match="E_PARAM_RANGE"):
        compile_recipe(load_recipe("photos_to_video"), {"seconds_per_image": 9.0}, [], {"kind": "images",
                       "paths": ["a.png"]}, base_dir=ROOT)


def test_video_recipe_given_images_fails_coded() -> None:
    with pytest.raises(RecipeError) as e:
        compile_recipe(load_recipe("R01"), {}, [], {"kind": "images", "paths": ["a.png"]}, base_dir=ROOT)
    assert e.value.code == "E_RECIPE_SOURCE_KIND"


# ---- CLI -------------------------------------------------------------------------------------------------------
def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "src.recipes", *args], cwd=ROOT, capture_output=True, text=True)


def test_cli_check_all_recipes() -> None:
    r = _cli("check")
    assert r.returncode == 0 and r.stdout.count("ok ") == 12


def test_cli_unknown_recipe_exits_2() -> None:
    r = _cli("compile", "--recipe", "R99", "--video", "tests/fixtures/media/src_a.txt")
    assert r.returncode == 2 and "E_RECIPE_UNKNOWN" in r.stderr


def test_cli_missing_ingest_exits_2() -> None:
    r = _cli("compile", "--recipe", "R01", "--video", "tests/fixtures/media/src_a.txt")
    assert r.returncode == 2 and "E_RECIPE_INGEST" in r.stderr
