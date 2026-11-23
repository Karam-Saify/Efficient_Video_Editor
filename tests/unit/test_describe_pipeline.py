"""H-0035: annotate -> to-do -> apply descriptions -> storyboard -> import corrections, on synthetic media only."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from src.describe import annotate as fi
from src.describe.schema import validate_annotation
from src.manifest import StageError, sha256_file

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


@pytest.fixture(scope="module")
def clip(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """6 s, 3 hard cuts (testsrc / smptebars / color), a 440 Hz tone: synthetic, nothing committed."""
    d = tmp_path_factory.mktemp("media")
    out = d / "synthetic.mp4"
    lav = ["-f", "lavfi", "-i"]
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *lav, "testsrc=size=320x568:rate=30:duration=2",
         *lav, "smptebars=size=320x568:rate=30:duration=2", *lav, "color=c=red:size=320x568:rate=30:duration=2",
         *lav, "sine=frequency=440:duration=6:sample_rate=16000",
         "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0[v]", "-map", "[v]", "-map", "3:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-threads", "1", "-c:a", "aac", "-shortest", str(out)],
        check=True,
    )
    return out


@pytest.fixture()
def env(clip: Path, tmp_path: Path) -> tuple[Path, Path, Path]:
    tr = tmp_path / "transcript.json"
    tr.write_text(json.dumps({"language": "ar", "language_probability": 0.9, "segments": [
        {"id": 0, "start": 0.2, "end": 1.8, "text": "أهلا", "words": [{"w": "أهلا"}]}]}, ensure_ascii=False),
        encoding="utf-8")
    return clip, tmp_path / "cache", tr


def run_annotate(clip: Path, cache: Path, tr: Path, **kw: object) -> Path:
    return fi.annotate(clip, "RR-P001-01", transcript_path=tr, cache_root=cache, **kw)  # type: ignore[arg-type]


def test_annotate_writes_valid_machine_record(env: tuple[Path, Path, Path]) -> None:
    clip, cache, tr = env
    rec_p = run_annotate(clip, cache, tr)
    rec = json.loads(rec_p.read_text(encoding="utf-8"))
    assert validate_annotation(rec) == []
    assert len(rec["scenes"]) == 3
    assert [s["role"]["value"] for s in rec["scenes"]] == ["hook", "demo", "cta"]
    assert rec["audio"]["speech_ratio"] < 0.1 and "LOW_VAD_SPEECH" in rec["audio"]["flags"]
    assert rec["audio"]["nonspeech_sound_ratio"] > 0.8  # the tone: sound that is not speech
    assert "human_verified" not in rec_p.read_text(encoding="utf-8")
    todo = json.loads((rec_p.parent / "descriptions.todo.json").read_text(encoding="utf-8"))
    assert 1 <= len(todo["items"]) <= fi.MAX_DESCRIBED
    assert (rec_p.parent / "manifest.json").is_file()


def test_annotate_is_byte_identical_on_rerun(env: tuple[Path, Path, Path], tmp_path: Path) -> None:
    clip, cache, tr = env
    a = run_annotate(clip, cache, tr)
    first = {p: sha256_file(a.parent.parent / p) for p in ("describe/annotation.json", "storyboard/index.html")}
    shutil.rmtree(a.parent)
    shutil.rmtree(a.parent.parent / "storyboard")
    run_annotate(clip, cache, tr)
    assert {p: sha256_file(a.parent.parent / p) for p in first} == first


def test_pick_described_caps_at_four() -> None:
    assert fi.pick_described(3) == [0, 1, 2]
    assert fi.pick_described(10) == [0, 3, 6, 9]
    assert all(len(fi.pick_described(n)) <= 4 for n in range(50))


def full_cycle(clip: Path, cache: Path, tr: Path) -> Path:
    rec_p = run_annotate(clip, cache, tr)
    todo_p = rec_p.parent / "descriptions.todo.json"
    todo = json.loads(todo_p.read_text(encoding="utf-8"))
    todo["describer"] = "test"
    for it in todo["items"]:
        it["description"] = f"synthetic pattern {it['scene_id']}"
    todo_p.write_text(json.dumps(todo), encoding="utf-8")
    fi.apply_descriptions(clip, todo_p, cache)
    corr = {"format": fi.CORRECTIONS_FORMAT, "video_id": json.loads(rec_p.read_text())["video_id"],
            "record_sha256": sha256_file(rec_p), "corrected_on": "2026-11-24",
            "scenes": [{"scene_id": 1, "description": "ألوان اختبار", "role": "product_intro"}],
            "segments": [{"segment_id": 0, "text": "أهلاً", "language": "ar"}]}
    cp = cache / "corr.json"
    cp.write_text(json.dumps(corr, ensure_ascii=False), encoding="utf-8")
    return fi.import_corrections(clip, cp, cache)


def test_full_cycle_keeps_machine_and_human_labels(env: tuple[Path, Path, Path]) -> None:
    clip, cache, tr = env
    rec_p = full_cycle(clip, cache, tr)
    rec = json.loads(rec_p.read_text(encoding="utf-8"))
    assert validate_annotation(rec) == []
    s1 = rec["scenes"][1]
    assert s1["role"] == {"value": "product_intro", "label_origin": "human_verified", "machine_value": "demo"}
    assert s1["description"]["machine_value"] == "synthetic pattern 1"
    assert rec["scenes"][0]["role"]["label_origin"] == "machine"
    assert rec["transcript"]["segments"][0]["text"]["machine_value"] == "أهلا"
    assert rec["provenance"]["describer"] == "test" and len(rec["provenance"]["corrections"]) == 1
    assert list((rec_p.parent / "corrections").glob("*.json"))
    with pytest.raises(StageError, match="refusing to overwrite"):
        run_annotate(clip, cache, tr)


def test_stale_corrections_rejected(env: tuple[Path, Path, Path]) -> None:
    clip, cache, tr = env
    rec_p = full_cycle(clip, cache, tr)
    with pytest.raises(StageError, match="older storyboard"):
        fi.import_corrections(clip, cache / "corr.json", cache)  # record changed since that export
    assert json.loads(rec_p.read_text())["provenance"]["corrections"].__len__() == 1


def test_too_many_descriptions_rejected(env: tuple[Path, Path, Path]) -> None:
    clip, cache, tr = env
    rec_p = run_annotate(clip, cache, tr)
    todo_p = rec_p.parent / "descriptions.todo.json"
    todo = json.loads(todo_p.read_text(encoding="utf-8"))
    todo["describer"] = "test"
    todo["items"] = todo["items"] * 2
    todo_p.write_text(json.dumps(todo), encoding="utf-8")
    with pytest.raises(StageError, match="rule 1"):
        fi.apply_descriptions(clip, todo_p, cache)


def test_storyboard_is_offline(env: tuple[Path, Path, Path]) -> None:
    clip, cache, tr = env
    rec_p = full_cycle(clip, cache, tr)
    page = (rec_p.parent.parent / "storyboard" / "index.html").read_text(encoding="utf-8")
    assert "://" not in page
    assert set(re.findall(r"http[\w-]*", page, re.I)) == {"http-equiv"}  # only the CSP meta tag
    assert "default-src 'none'" in page
    markup = page.split("<script>")[0]  # HTML attributes; the inline JS is checked below
    srcs = re.findall(r"""\b(?:src|href|action|data)\s*=\s*["']?([^"'\s>]+)""", markup)
    assert srcs and all(s.startswith("data:image/jpeg;base64,") for s in srcs)
    js = page.split("<script>")[1]
    assert re.findall(r"\.(?:src|href)\s*=", js) == [".href="]  # the one assignment: a local blob download
    assert "a.href=URL.createObjectURL(blob)" in js
    for bad in ("fetch(", "XMLHttpRequest", "import(", "<link", "@import", "url("):
        assert bad not in page
    assert 'id="export"' in page


def test_cli_validate_and_stage_contract(tmp_path: Path) -> None:
    fx = ROOT / "tests/fixtures/annotations"
    ok = subprocess.run([sys.executable, "-m", "src.describe", "validate", str(fx / "valid/v5_job_full.json")],
                        cwd=ROOT, capture_output=True, text=True)
    bad = subprocess.run([sys.executable, "-m", "src.describe", "validate", str(fx / "invalid/i02_no_rights_id.json")],
                         cwd=ROOT, capture_output=True, text=True)
    assert ok.returncode == 0 and bad.returncode == 1 and "E_SCHEMA" in bad.stderr
