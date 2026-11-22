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
    "i6_float_ms.json": "E_SCHEMA",  # H-0009: integral float (2000.0) where v0 needs an int
    "i7_source_path.json": "E_SOURCE_PATH",  # H-0009: source path escapes the repo
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def codes(tl: Any) -> list[str]:
    return [e.code for e in validate(tl, base_dir=ROOT)]


def base() -> dict[str, Any]:
    return copy.deepcopy(load(FIX / "valid" / "v3_captions_rtl_ltr.json"))


def test_fixture_counts() -> None:
    assert len(VALID) >= 5 and len(INVALID_EXPECTED) >= 5
    assert sorted(p.name for p in (FIX / "invalid").glob("*.json")) == sorted(INVALID_EXPECTED)
    assert len(set(INVALID_EXPECTED.values())) == len(INVALID_EXPECTED)  # each breaks a different rule


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


def test_relative_paths_resolve_against_base_dir() -> None:
    # H-0009: base_dir must sit inside the repo now (E_SOURCE_PATH otherwise), so use a repo subdir.
    assert [e.code for e in validate(base(), base_dir=ROOT / "tests")] == ["E_SOURCE_MISSING"]


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


# H-0009 (H-0004 review F1): integral floats are JSON Schema "integers"; v0 needs real ints, coded, no crash.
@pytest.mark.parametrize(
    ("where", "value"),
    [(("tracks", "video", 0, "in_ms"), 2000.0), (("canvas", "fps"), 30.0), (("target_duration_ms",), 6000.0),
     (("target_duration_ms",), 9000.0), (("canvas", "width"), 1080.0), (("sources", 0, "duration_ms"), 10000.0),
     (("tracks", "captions", 0, "end_ms"), 1800.0), (("canvas", "fps"), True)],
)
def test_non_int_numbers_are_coded_schema_errors(where: tuple[Any, ...], value: Any) -> None:
    tl = base()
    node = tl
    for k in where[:-1]:
        node = node[k]
    node[where[-1]] = value
    issues = validate(tl, base_dir=ROOT)  # 9000.0 is also off-target: used to crash in the ':+d' format
    assert issues and {i.code for i in issues} == {"E_SCHEMA"}, issues
    assert any("integer" in i.message for i in issues)


def test_float_ms_cli_is_a_coded_line_not_a_crash() -> None:
    r = run(str(FIX / "invalid" / "i6_float_ms.json"))
    assert r.returncode == 1 and r.stdout.startswith("E_SCHEMA /tracks/video/0/in_ms:") and not r.stderr


# H-0009 (H-0004 review F3): source paths stay inside the repo and outside the protected roots.
def _protected_paths() -> list[str]:
    from src.validate import PROTECTED_SOURCE_ROOTS

    out = ["/etc/passwd", str(ROOT / "tests/fixtures/media/src_a.txt"), "../outside.txt",
           "tests/../../outside.txt"]
    for r in PROTECTED_SOURCE_ROOTS:
        out += [f"{r}/x.mp4", f"./{r}/../{r.split('/')[-1]}/x.mp4", f"tests/../{r}/sub/x.mp4"]
    return out


@pytest.mark.parametrize("path", _protected_paths())
def test_source_path_outside_repo_or_in_protected_root_is_rejected(path: str, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.validate as vmod

    opened: list[Any] = []
    monkeypatch.setattr(vmod, "_sha256", lambda p: opened.append(p) or "0" * 64)
    monkeypatch.setattr(vmod.Path, "is_file", lambda p: opened.append(p) or True)
    tl = base()
    tl["sources"][0]["path"] = path
    issues = validate(tl, base_dir=ROOT)
    assert [i.code for i in issues] == ["E_SOURCE_PATH"] and issues[0].path == "/sources/0/path"
    assert opened == []  # neither stat'ed as a file nor hashed


def test_protected_roots_cover_the_constitution_list() -> None:
    from src.validate import PROTECTED_SOURCE_ROOTS

    assert {"quarantine", "data/golden"} <= set(PROTECTED_SOURCE_ROOTS) and len(PROTECTED_SOURCE_ROOTS) == 3


def test_source_symlink_into_protected_root_is_rejected() -> None:
    link = ROOT / "tests" / "fixtures" / "media" / "_tmp_link_h0009.txt"
    link.symlink_to(ROOT / "quarantine" / "x.mp4")
    try:
        tl = base()
        tl["sources"][0]["path"] = "tests/fixtures/media/_tmp_link_h0009.txt"
        assert codes(tl) == ["E_SOURCE_PATH"]
    finally:
        link.unlink()


# H-0009 (H-0004 review F2): v0 can say "this source has no audio"; the renderer then uses silence.
def test_has_audio_false_renders_silence_for_that_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import src.render as render_mod

    monkeypatch.chdir(ROOT)
    calls: list[list[str]] = []
    monkeypatch.setattr(render_mod.subprocess, "run", lambda cmd, check: calls.append(cmd))
    tl = load(FIX / "valid" / "v6_no_audio_source.json")
    assert validate(tl, base_dir=ROOT) == []
    render_mod.render(tl, tmp_path / "o.mp4")
    cmd = calls[0]
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "[0:a]" not in graph and "[2:a]atrim=duration=3.0" in graph and "[1:a]atrim=start=1.0" in graph
    assert "anullsrc" in " ".join(cmd)


def test_has_audio_defaults_true_and_must_be_boolean() -> None:
    from src.render.adapter import to_render_model

    assert all(s["has_audio"] is True for s in to_render_model(base())["sources"].values())
    tl = base()
    tl["sources"][0]["has_audio"] = "no"
    assert codes(tl) == ["E_SCHEMA"]


# H-0009 (H-0003 review F5): unreadable JSON gives one clean error line, no traceback, no manifest.
@pytest.mark.parametrize("content", [b"", b"{not json", b"\xff\xfe\x00"])
def test_bad_json_input_is_a_clean_error(tmp_path: Path, content: bytes) -> None:
    bad = tmp_path / "bad.json"
    bad.write_bytes(content)
    for args in ([str(bad)], ["--input", str(bad), "--out", str(tmp_path / "o")]):
        r = run(*args)
        out = r.stdout + r.stderr
        assert r.returncode == 1 and "Traceback" not in out and "validate: error:" in out, out
        assert len(out.strip().splitlines()) == 1, out
    assert not (tmp_path / "o" / "manifest.json").exists()


# H-0009 (H-0004 review F4): the pre-v0 E6 script stops with a clear message instead of a validation crash.
def test_e6_captions_is_deprecated_with_clear_error() -> None:
    r = subprocess.run([sys.executable, "experiments/e6_captions.py"], cwd=ROOT, capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 2 and "deprecated" in r.stderr and "Traceback" not in r.stderr
