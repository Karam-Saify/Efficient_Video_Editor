"""Per-stage resource instrumentation (H-0027) and the per-video cost model.

Measurement:
- `run_measured(cmd)` runs a child process and reads its own rusage with `os.wait4`, so CPU time and peak RSS
  cover exactly that child and the descendants it waited for (e.g. ffmpeg under the ingest CLI):
  `rss_scope = "process_tree"`.
- `measure()` is a context manager for in-process work: CPU is the delta of self + children rusage; peak RSS
  is this process's own high-water mark at exit (`rss_scope = "self_hwm"`, an upper bound for the block). It
  excludes children: RUSAGE_CHILDREN maxrss is the largest child ever reaped (in the demo, the ASR child), not
  the block's. H-0027's measurement file predates this fix, so its `edit` rows carry the ASR child's RSS.
- `record(path, stage, metrics)` merges one stage into `cache/<video_id>/timings.json` (atomic write).

Timings are provenance, not outputs: they are never part of a cache key or a determinism check.

Cost model (pure arithmetic in code, I-4): `compute_cost` (vCPU-hours + GB-hours of peak RSS over wall time,
the Fargate billing shape), `storage_cost`, `llm_cost`, `planning_cost` (small model always, big model on a
miss), `percentile`.
"""
from __future__ import annotations

import json
import math
import os
import resource
import statistics
import subprocess
import tempfile
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

TIMINGS_SCHEMA = "timings/1"
TIMINGS = "timings.json"


def _rss_mb(kb: int) -> float:
    return round(kb / 1024, 1)  # Linux ru_maxrss is in KiB


def run_measured(cmd: Sequence[str], *, cwd: Path | None = None) -> tuple[int, str, str, dict[str, Any]]:
    """Run `cmd`; return (returncode, stdout, stderr, metrics). Raises OSError if it cannot start."""
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        t0 = time.perf_counter()
        p = subprocess.Popen(list(cmd), cwd=cwd, stdout=fo, stderr=fe)
        _, status, ru = os.wait4(p.pid, 0)
        wall = time.perf_counter() - t0
        p.returncode = os.waitstatus_to_exitcode(status)
        fo.seek(0)
        fe.seek(0)
        out = fo.read().decode("utf-8", "replace")
        err = fe.read().decode("utf-8", "replace")
    m = {
        "wall_s": round(wall, 3),
        "cpu_user_s": round(ru.ru_utime, 3),
        "cpu_sys_s": round(ru.ru_stime, 3),
        "cpu_s": round(ru.ru_utime + ru.ru_stime, 3),
        "peak_rss_mb": _rss_mb(ru.ru_maxrss),
        "rss_scope": "process_tree",
    }
    return p.returncode, out, err, m


@contextmanager
def measure() -> Iterator[dict[str, Any]]:
    """In-process measurement; the yielded dict is filled when the block exits."""
    m: dict[str, Any] = {}
    s0, c0 = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    try:
        yield m
    finally:
        wall = time.perf_counter() - t0
        s1, c1 = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        user = (s1.ru_utime - s0.ru_utime) + (c1.ru_utime - c0.ru_utime)
        sys_ = (s1.ru_stime - s0.ru_stime) + (c1.ru_stime - c0.ru_stime)
        m.update({
            "wall_s": round(wall, 3),
            "cpu_user_s": round(user, 3),
            "cpu_sys_s": round(sys_, 3),
            "cpu_s": round(user + sys_, 3),
            "peak_rss_mb": _rss_mb(s1.ru_maxrss),
            "rss_scope": "self_hwm",
        })


def record(path: Path, stage: str, metrics: Mapping[str, Any]) -> dict[str, Any]:
    """Merge `metrics` under `stages[stage]` in `path` (created if absent or unreadable)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("stages"), dict):
            raise ValueError
    except (OSError, ValueError):
        data = {"schema": TIMINGS_SCHEMA, "stages": {}}
    data["schema"] = TIMINGS_SCHEMA
    data["stages"][stage] = dict(metrics)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return data


def tree_bytes(paths: Sequence[Path]) -> int:
    """Total bytes of the given files and every file under the given dirs; missing paths count 0."""
    n = 0
    for p in paths:
        if p.is_file():
            n += p.stat().st_size
        elif p.is_dir():
            n += sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    return n


# ---- cost model ----

def compute_cost(m: Mapping[str, Any], a: Mapping[str, Any]) -> float:
    """USD for one measured stage: cpu_s as vCPU-seconds + peak RSS (GB) held for wall_s."""
    vcpu_h = float(m["cpu_s"]) / 3600
    gb_h = float(m["peak_rss_mb"]) / 1024 * float(m["wall_s"]) / 3600
    return vcpu_h * float(a["vcpu_hour_usd"]) + gb_h * float(a["gb_hour_usd"])


def storage_cost(nbytes: int, a: Mapping[str, Any]) -> float:
    return nbytes / 1024**3 * float(a["storage_gb_month_usd"]) * float(a["retention_months"])


def llm_cost(input_tokens: float, output_tokens: float, price: Mapping[str, Any]) -> float:
    usd_in = input_tokens * float(price["input_usd_per_mtok"])
    return (usd_in + output_tokens * float(price["output_usd_per_mtok"])) / 1e6


def planning_cost(small_in: float, small_out: float, big_in: float, big_out: float,
                  small: Mapping[str, Any], big: Mapping[str, Any], *, miss_rate: float) -> float:
    """ADR-0008: the small model always runs; the big model runs on a miss (probability `miss_rate`)."""
    if not 0 <= miss_rate <= 1:
        raise ValueError(f"miss_rate must be in [0, 1], got {miss_rate}")
    return llm_cost(small_in, small_out, small) + miss_rate * llm_cost(big_in, big_out, big)


def percentile(xs: Sequence[float], q: float) -> float:
    """q=50 -> statistics.median; otherwise nearest-rank percentile (no interpolation)."""
    if not xs:
        raise ValueError("percentile of an empty sequence")
    if q == 50:
        return float(statistics.median(xs))
    s = sorted(xs)
    return float(s[max(0, math.ceil(q / 100 * len(s)) - 1)])
