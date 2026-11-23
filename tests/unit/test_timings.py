"""H-0027: per-stage resource instrumentation (wall, CPU, peak RSS, bytes) and the cost model."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src import timings as T

BURN = "import time\nt=time.process_time()\nwhile time.process_time()-t<0.3: pass\n"
ALLOC = "b=bytearray(150*1024*1024)\nb[::4096]=b'x'*len(b[::4096])\n"


def test_run_measured_reports_child_cpu_and_rss() -> None:
    rc, out, err, m = T.run_measured([sys.executable, "-c", BURN + ALLOC + "print('hi')"])
    assert rc == 0 and out.strip() == "hi" and err == ""
    assert set(m) >= {"wall_s", "cpu_user_s", "cpu_sys_s", "cpu_s", "peak_rss_mb", "rss_scope"}
    assert m["cpu_s"] >= 0.25, m  # the busy loop burns >= 0.3 s CPU in the child
    assert m["wall_s"] >= m["cpu_s"] * 0.5
    assert m["peak_rss_mb"] >= 140, m  # 150 MiB touched in the child
    assert m["rss_scope"] == "process_tree"


def test_run_measured_returns_nonzero_exit_and_stderr() -> None:
    rc, _, err, m = T.run_measured([sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"])
    assert rc == 3 and err == "boom" and m["wall_s"] >= 0


def test_run_measured_missing_binary_raises() -> None:
    with pytest.raises(OSError):
        T.run_measured(["/nonexistent/definitely-not-a-binary"])


def test_measure_in_process_counts_cpu() -> None:
    with T.measure() as m:
        exec(BURN)  # noqa: S102 - fixed literal
    assert m["cpu_s"] >= 0.25 and m["wall_s"] > 0 and m["rss_scope"] == "self_hwm"
    assert m["peak_rss_mb"] > 0


def test_record_merges_stages_atomically(tmp_path: Path) -> None:
    p = tmp_path / "c" / "timings.json"
    T.record(p, "asr", {"wall_s": 1.0})
    T.record(p, "render", {"wall_s": 2.0})
    T.record(p, "asr", {"wall_s": 3.0})
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["schema"] == T.TIMINGS_SCHEMA
    assert d["stages"] == {"asr": {"wall_s": 3.0}, "render": {"wall_s": 2.0}}
    assert not list(p.parent.glob("*.tmp"))


def test_record_replaces_corrupt_file(tmp_path: Path) -> None:
    p = tmp_path / "timings.json"
    p.write_text("{not json", encoding="utf-8")
    T.record(p, "asr", {"wall_s": 1.0})
    assert json.loads(p.read_text(encoding="utf-8"))["stages"] == {"asr": {"wall_s": 1.0}}


def test_tree_bytes_counts_files_and_dirs(tmp_path: Path) -> None:
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a").write_bytes(b"x" * 10)
    (tmp_path / "b").write_bytes(b"y" * 5)
    assert T.tree_bytes([tmp_path / "d", tmp_path / "b", tmp_path / "missing"]) == 15


# ---- cost model (pure arithmetic in code, I-4) ----

def test_compute_cost_matches_hand_calculation() -> None:
    a = {"vcpu_hour_usd": 0.04, "gb_hour_usd": 0.004, "storage_gb_month_usd": 0.015, "retention_months": 1.0}
    m = {"cpu_s": 3600.0, "wall_s": 3600.0, "peak_rss_mb": 1024.0}
    # 1 vCPU-hour + 1 GB for 1 wall-hour
    assert T.compute_cost(m, a) == pytest.approx(0.044)
    assert T.storage_cost(1024**3, a) == pytest.approx(0.015)


def test_llm_cost_and_miss_rate() -> None:
    small = {"input_usd_per_mtok": 0.10, "output_usd_per_mtok": 0.50}
    big = {"input_usd_per_mtok": 4.0, "output_usd_per_mtok": 20.0}
    assert T.llm_cost(1_000_000, 0, small) == pytest.approx(0.10)
    assert T.llm_cost(0, 1_000_000, big) == pytest.approx(20.0)
    c0 = T.planning_cost(1000, 200, 3000, 800, small, big, miss_rate=0.0)
    c1 = T.planning_cost(1000, 200, 3000, 800, small, big, miss_rate=1.0)
    assert c0 == pytest.approx(T.llm_cost(1000, 200, small))
    assert c1 == pytest.approx(T.llm_cost(1000, 200, small) + T.llm_cost(3000, 800, big))
    with pytest.raises(ValueError):
        T.planning_cost(1, 1, 1, 1, small, big, miss_rate=1.5)


def test_percentile_nearest_rank() -> None:
    xs = [5.0, 1.0, 3.0, 2.0, 4.0, 8.0, 7.0, 6.0]
    assert T.percentile(xs, 50) == pytest.approx(4.5)  # median of 8 = mean of the two middle values
    assert T.percentile(xs, 90) == 8.0  # nearest rank: ceil(0.9*8)=8th value
    with pytest.raises(ValueError):
        T.percentile([], 50)
