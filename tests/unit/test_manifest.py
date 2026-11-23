"""Stage cache contract (src/manifest.py): first run writes, rerun skips, changes rerun."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src import manifest as m


class Counter:
    """Work function that records calls and writes one deterministic output."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, inputs: list[Path], out: Path, config: dict[str, Any]) -> str:
        self.calls += 1
        text = "".join(p.read_text(encoding="utf-8") for p in inputs) + json.dumps(config, sort_keys=True)
        (out / "result.txt").write_text(text, encoding="utf-8")
        return "ok"


@pytest.fixture
def setup(tmp_path: Path) -> tuple[Path, Path, Counter]:
    inp = tmp_path / "in.txt"
    inp.write_text("hello", encoding="utf-8")
    return inp, tmp_path / "out", Counter()


CFG = {"k": 1, "stage_version": "0"}


def test_first_run_writes_manifest(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    ran, man = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 1
    on_disk = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk == man
    for key in ("stage", "created_at", "duration_s", "input_hashes", "config_hash", "versions", "outputs"):
        assert key in on_disk, key
    assert on_disk["stage"] == "demo"
    assert list(on_disk["input_hashes"].values()) == [m.sha256_file(inp)]
    assert on_disk["config_hash"] == m.config_hash(CFG)
    assert set(on_disk["versions"]) == {"code", "python", "tools"}
    assert on_disk["outputs"] == {"result.txt": m.sha256_file(out / "result.txt")}


def test_rerun_same_inputs_and_config_skips(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    before = (out / "manifest.json").read_bytes()
    ran, _ = m.run_stage("demo", [inp], out, dict(CFG), work)
    assert not ran and work.calls == 1
    assert (out / "manifest.json").read_bytes() == before


def test_changed_input_reruns(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    inp.write_text("hello!", encoding="utf-8")
    ran, man = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 2
    assert list(man["input_hashes"].values()) == [m.sha256_file(inp)]


def test_changed_config_reruns(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    ran, man = m.run_stage("demo", [inp], out, {**CFG, "k": 2}, work)
    assert ran and work.calls == 2
    assert man["config_hash"] == m.config_hash({**CFG, "k": 2})


def test_stage_version_bump_reruns(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    ran, _ = m.run_stage("demo", [inp], out, {**CFG, "stage_version": "1"}, work)
    assert ran and work.calls == 2


def test_tampered_output_reruns(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    (out / "result.txt").write_text("corrupted", encoding="utf-8")
    ran, _ = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 2


def test_deleted_output_reruns(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    (out / "result.txt").unlink()
    ran, _ = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 2


def test_other_stage_manifest_does_not_count(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    ran, _ = m.run_stage("other", [inp], out, CFG, work)
    assert ran and work.calls == 2


def test_failed_work_leaves_no_manifest(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    inp.write_text("changed", encoding="utf-8")

    def boom(*_: Any) -> str:
        raise m.StageError("boom")

    with pytest.raises(m.StageError):
        m.run_stage("demo", [inp], out, CFG, boom)
    assert not (out / "manifest.json").exists()


def test_config_hash_is_key_order_independent() -> None:
    assert m.config_hash({"a": 1, "b": "ب"}) == m.config_hash({"b": "ب", "a": 1})
    assert m.config_hash({"a": 1}) != m.config_hash({"a": "1"})


def test_directory_input_hashes_every_file(tmp_path: Path) -> None:
    d = tmp_path / "d"
    (d / "sub").mkdir(parents=True)
    (d / "a.txt").write_text("a", encoding="utf-8")
    (d / "sub" / "b.txt").write_text("b", encoding="utf-8")
    hashes = m.hash_inputs([d])
    assert len(hashes) == 2
    assert list(hashes) == sorted(hashes)


def test_missing_input_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(m.StageError, match="input not found"):
        m.hash_inputs([tmp_path / "nope"])


def test_build_config_overrides_and_rejects_unknown_keys() -> None:
    cfg = m.build_config("3", {"crf": 20, "preset": "veryfast"}, ["crf=18", "preset=slow"])
    assert cfg == {"crf": 18, "preset": "slow", "stage_version": "3"}
    with pytest.raises(m.StageError, match="unknown config key"):
        m.build_config("3", {"crf": 20}, ["crff=18"])
    with pytest.raises(m.StageError, match="key=value"):
        m.build_config("3", {"crf": 20}, ["crf"])


def test_cli_prints_skip_on_rerun(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inp = tmp_path / "in.txt"
    inp.write_text("x", encoding="utf-8")
    argv = ["--input", str(inp), "--out", str(tmp_path / "o")]
    work = Counter()
    assert m.cli("demo", argv, work=work) == 0
    assert "demo: done (ok)" in capsys.readouterr().out
    assert m.cli("demo", argv, work=work) == 0
    assert "demo: skip" in capsys.readouterr().out
    assert m.cli("demo", [*argv, "--set", "nope=1"], work=work) == 1


# H-0024 G2a: a stage without real work fails loudly and never writes a success manifest.
def test_cli_stub_is_not_implemented(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inp = tmp_path / "in.txt"
    inp.write_text("x", encoding="utf-8")
    out = tmp_path / "o"
    assert m.cli("demo", ["--input", str(inp), "--out", str(out)]) == 2
    cap = capsys.readouterr()
    assert "NOT_IMPLEMENTED: demo" in cap.err and cap.out == ""
    assert not (out / "manifest.json").exists()
    with pytest.raises(m.StageNotImplemented):
        m.run_stage("demo", [inp], out, CFG, m.stub_work)
    assert not (out / "manifest.json").exists()


def test_wants_stage_cli() -> None:
    assert m.wants_stage_cli(["--input", "x", "--out", "y"])
    assert m.wants_stage_cli(["--input=x"])
    assert not m.wants_stage_cli(["samples/clip.mp4", "--model", "small"])


# H-0009 (H-0003 review F3): the skip key must not let a stub manifest stand in for real work.
def test_stub_manifest_never_satisfies_real_work(setup: tuple[Path, Path, Counter]) -> None:
    inp, out, work = setup
    ran, man = m.run_stage("demo", [inp], out, CFG, lambda i, o, c: "stub")  # a pre-H-0024 stub manifest
    assert ran and man["status"] == "stub"
    ran, man = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 1 and man["status"] == "ok"
    ran, _ = m.run_stage("demo", [inp], out, CFG, work)  # now fresh: skips
    assert not ran and work.calls == 1


def test_code_version_change_reruns(setup: tuple[Path, Path, Counter], monkeypatch: pytest.MonkeyPatch) -> None:
    inp, out, work = setup
    m.run_stage("demo", [inp], out, CFG, work)
    monkeypatch.setattr(m, "__version__", "999.0.0")
    ran, man = m.run_stage("demo", [inp], out, CFG, work)
    assert ran and work.calls == 2 and man["versions"]["code"] == "999.0.0"


# H-0009 (H-0003 review F6): --out inside an --input dir would hash its own outputs and never skip.
def test_out_inside_input_dir_is_an_error(tmp_path: Path) -> None:
    d = tmp_path / "d"
    d.mkdir()
    (d / "a.txt").write_text("a", encoding="utf-8")
    work = Counter()
    for out in (d / "out", d):
        with pytest.raises(m.StageError, match="inside input"):
            m.run_stage("demo", [d], out, CFG, work)
    assert work.calls == 0 and not (d / "out" / "manifest.json").exists()
