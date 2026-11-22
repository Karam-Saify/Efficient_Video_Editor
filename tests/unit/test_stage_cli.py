"""Every stage runs as `python -m src.<stage> --input X --out D`, writes a manifest and skips on rerun."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "timeline_min.json"
STAGES = ["ingest", "describe", "score", "select", "edit", "validate", "render"]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_writes_manifest_then_skips(stage: str, tmp_path: Path) -> None:
    out = tmp_path / stage
    first = run("-m", f"src.{stage}", "--input", str(FIXTURE), "--out", str(out))
    assert first.returncode == 0, first.stderr
    assert f"{stage}: done" in first.stdout
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert man["stage"] == stage
    assert man["input_hashes"] == {"tests/fixtures/timeline_min.json": man["input_hashes"][
        "tests/fixtures/timeline_min.json"]}
    before = (out / "manifest.json").read_bytes()

    second = run("-m", f"src.{stage}", "--input", str(FIXTURE), "--out", str(out))
    assert second.returncode == 0, second.stderr
    assert f"{stage}: skip" in second.stdout
    assert (out / "manifest.json").read_bytes() == before


def test_validate_stage_rejects_invalid_timeline_without_manifest(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    tl = json.loads(FIXTURE.read_text(encoding="utf-8"))
    tl["clips"][0]["out"] = 99.0  # beyond source duration
    bad.write_text(json.dumps(tl), encoding="utf-8")
    r = run("-m", "src.validate", "--input", str(bad), "--out", str(tmp_path / "v"))
    assert r.returncode == 1
    assert not (tmp_path / "v" / "manifest.json").exists()
    report = json.loads((tmp_path / "v" / "report.json").read_text(encoding="utf-8"))
    assert report["valid"] is False and report["errors"]


def test_validate_report_is_byte_identical_across_runs(tmp_path: Path) -> None:
    for d in ("a", "b"):
        assert run("-m", "src.validate", "--input", str(FIXTURE), "--out", str(tmp_path / d)).returncode == 0
    assert (tmp_path / "a" / "report.json").read_bytes() == (tmp_path / "b" / "report.json").read_bytes()


def test_legacy_validate_cli_still_works() -> None:
    r = run("-m", "src.validate", str(FIXTURE))
    assert r.returncode == 0 and r.stdout.startswith("OK: 1 clips, 2.500s")


def test_legacy_render_command_builder_still_works(tmp_path: Path) -> None:
    from src.render import build_command

    tl = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cmd = build_command(tl, tmp_path / "o.mp4", None, "veryfast", 20)
    assert cmd[0] == "ffmpeg" and str(tmp_path / "o.mp4") in cmd


def test_heavy_deps_not_imported_at_module_import() -> None:
    code = (
        "import sys, importlib\n"
        "for s in ['ingest','describe','score','select','edit','validate','render']:\n"
        "    importlib.import_module(f'src.{s}')\n"
        "importlib.import_module('src.ingest.__main__')\n"
        "bad = [m for m in ('faster_whisper','scenedetect','cv2','ctranslate2','pulp') if m in sys.modules]\n"
        "assert not bad, bad\n"
    )
    r = run("-c", code)
    assert r.returncode == 0, r.stderr
