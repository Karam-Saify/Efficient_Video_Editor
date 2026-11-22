"""H-0004: timeline schema v0 + validator. Fixtures in tests/fixtures/timelines/{valid,invalid}/."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from src.validate import validate

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "timelines"
VALID = sorted((FIX / "valid").glob("*.json"))
INVALID_EXPECTED = {  # fixture -> the one code it must produce (rule number in the name of the code's docstring)
    "i1_source_missing.json": "E_SOURCE_MISSING",  # rule 1
    "i2_range.json": "E_RANGE",  # rule 2
    "i3_overlap.json": "E_OVERLAP",  # rule 3
    "i4_caption_bounds.json": "E_CAPTION_BOUNDS",  # rule 4
    "i5_duration.json": "E_DURATION",  # rule 5
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def codes(tl: Any) -> list[str]:
    return [e.code for e in validate(tl, base_dir=ROOT)]


def base() -> dict[str, Any]:
    return copy.deepcopy(load(FIX / "valid" / "v3_captions_rtl_ltr.json"))


def test_fixture_counts() -> None:
    assert len(VALID) == 5
    assert sorted(p.name for p in (FIX / "invalid").glob("*.json")) == sorted(INVALID_EXPECTED)
    assert len(set(INVALID_EXPECTED.values())) == 5  # each breaks a different rule


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_fixture_passes(path: Path) -> None:
    assert validate(load(path), base_dir=ROOT) == []


@pytest.mark.parametrize("name", sorted(INVALID_EXPECTED))
def test_invalid_fixture_fails_with_exactly_the_expected_code(name: str) -> None:
    assert codes(load(FIX / "invalid" / name)) == [INVALID_EXPECTED[name]]


# Rules 6 and 7 have no invalid fixture; they are covered here.
@pytest.mark.parametrize("value", [None, "auto", "RTL"])
def test_rule6_caption_dir_missing_or_unknown(value: str | None) -> None:
    tl = base()
    if value is None:
        del tl["tracks"]["captions"][1]["dir"]
    else:
        tl["tracks"]["captions"][1]["dir"] = value
    assert codes(tl) == ["E_CAPTION_DIR"]


def test_rule7_unknown_effect_type() -> None:
    tl = load(FIX / "valid" / "v4_effects.json")
    tl["tracks"]["effects"][1]["type"] = "blur"
    assert codes(tl) == ["E_EFFECT_TYPE"]


# Rule 1 variants: missing file, hash mismatch, undeclared audio source.
def test_rule1_declared_source_file_missing() -> None:
    tl = base()
    tl["sources"][0]["path"] = "tests/fixtures/media/does_not_exist.txt"
    assert codes(tl) == ["E_SOURCE_MISSING"]


def test_rule1_hash_mismatch_only_when_sha256_given() -> None:
    tl = base()
    tl["sources"][0]["sha256"] = "0" * 64
    assert codes(tl) == ["E_SOURCE_HASH"]
    del tl["sources"][0]["sha256"]
    assert codes(tl) == []


def test_rule1_undeclared_audio_source() -> None:
    tl = load(FIX / "valid" / "v5_audio.json")
    tl["tracks"]["audio"][0]["source"] = "nope"
    assert codes(tl) == ["E_SOURCE_MISSING"]


def test_relative_paths_resolve_against_base_dir(tmp_path: Path) -> None:
    assert [e.code for e in validate(base(), base_dir=tmp_path)] == ["E_SOURCE_MISSING"]


# Rule 2 variants.
@pytest.mark.parametrize(("in_ms", "out_ms"), [(-1, 6000), (3000, 3000), (5000, 4000)])
def test_rule2_range_variants(in_ms: int, out_ms: int) -> None:
    tl = base()
    tl["tracks"]["video"][0].update(in_ms=in_ms, out_ms=out_ms)
    tl["tracks"]["captions"] = []
    tl["target_duration_ms"] = max(1, out_ms - in_ms)
    got = codes(tl)
    assert "E_RANGE" in got and set(got) <= {"E_RANGE", "E_DURATION"}  # a negative clip also breaks the total


def test_rule3_adjacent_clips_same_source_do_not_overlap() -> None:
    tl = load(FIX / "invalid" / "i3_overlap.json")
    tl["tracks"]["video"][1].update(in_ms=3000, out_ms=5000)
    assert codes(tl) == []


def test_rule4_caption_end_not_after_start() -> None:
    tl = base()
    tl["tracks"]["captions"][0]["end_ms"] = 0
    assert codes(tl) == ["E_CAPTION_BOUNDS"]


@pytest.mark.parametrize(("fps", "delta", "ok"), [(30, 33, True), (30, 34, False), (30, -33, True), (25, 40, True),
                                                  (25, 41, False), (60, 16, True), (60, 17, False)])
def test_rule5_one_frame_tolerance_is_integer_exact(fps: int, delta: int, ok: bool) -> None:
    tl = base()
    tl["canvas"]["fps"] = fps
    tl["target_duration_ms"] = 6000 + delta
    assert codes(tl) == ([] if ok else ["E_DURATION"])


def test_extra_rules_duplicate_id_and_effect_target() -> None:
    tl = load(FIX / "valid" / "v4_effects.json")
    tl["tracks"]["video"][1]["id"] = "c1"
    assert codes(tl) == ["E_DUPLICATE_ID", "E_EFFECT_TARGET"]  # effect on 'c2' now has no clip


def test_structural_error_is_e_schema_and_stops_semantics() -> None:
    tl = base()
    tl["tracks"]["video"][0]["in_ms"] = 1.5  # ms are integers
    tl["tracks"]["video"][0]["source"] = "srcZ"  # would be E_SOURCE_MISSING, but semantics are skipped
    errs = validate(tl, base_dir=ROOT)
    assert [e.code for e in errs] == ["E_SCHEMA"] and errs[0].path == "/tracks/video/0/in_ms"
    assert codes({"version": "0.1"}) == ["E_SCHEMA"] * 4  # every missing required field reported


def test_all_errors_returned_not_just_first() -> None:
    tl = base()
    tl["tracks"]["video"][0]["source"] = "srcZ"
    tl["tracks"]["captions"][0]["dir"] = "auto"
    tl["tracks"]["captions"][2]["end_ms"] = 9999
    tl["target_duration_ms"] = 1000
    assert sorted(codes(tl)) == ["E_CAPTION_BOUNDS", "E_CAPTION_DIR", "E_DURATION", "E_SOURCE_MISSING"]


def test_issues_are_structured_and_deterministic() -> None:
    tl = load(FIX / "invalid" / "i3_overlap.json")
    a, b = validate(tl, base_dir=ROOT), validate(copy.deepcopy(tl), base_dir=ROOT)
    assert a == b and a[0].to_dict() == {"code": "E_OVERLAP", "path": "/tracks/video/1", "message": a[0].message}


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "src.validate", *args], cwd=ROOT, capture_output=True, text=True,
                          timeout=60)


def test_cli_exit_codes() -> None:
    assert run(str(FIX / "valid" / "v2_multi_clip.json")).returncode == 0
    r = run(str(FIX / "invalid" / "i5_duration.json"))
    assert r.returncode == 1 and r.stdout.startswith("E_DURATION /target_duration_ms:")


def test_stage_cli_report_has_structured_errors(tmp_path: Path) -> None:
    r = run("--input", str(FIX / "invalid" / "i2_range.json"), "--out", str(tmp_path))
    assert r.returncode == 1 and not (tmp_path / "manifest.json").exists()
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["valid"] is False and [e["code"] for e in report["errors"]] == ["E_RANGE"]


def test_render_accepts_valid_v0_timeline_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.render as render_mod

    monkeypatch.chdir(ROOT)
    calls: list[list[str]] = []
    monkeypatch.setattr(render_mod.subprocess, "run", lambda cmd, check: calls.append(cmd))
    render_mod.render(load(FIX / "valid" / "v3_captions_rtl_ltr.json"), tmp_path / "o.mp4")
    cmd = calls[0]
    assert cmd[0] == "ffmpeg" and str(tmp_path / "o.mp4") in cmd
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "trim=start=2.0:end=8.0" in graph and "ass=filename=" in graph
    ass = (tmp_path / "o.ass").read_text(encoding="utf-8")
    assert "Dialogue: 0,0:00:00.00,0:00:01.80,Default,,0,0,0,,السعر الحقيقي؟" in ass


def test_render_rejects_invalid_timeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.render as render_mod

    monkeypatch.chdir(ROOT)
    with pytest.raises(ValueError, match="E_OVERLAP"):
        render_mod.render(load(FIX / "invalid" / "i3_overlap.json"), tmp_path / "o.mp4")
