"""H-0027: the cost report prices a measured clip record by formula only (no hand-typed numbers)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("cost_baseline", ROOT / "experiments" / "cost_baseline.py")
cb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(cb)

STAGE = {"wall_s": 10.0, "cpu_s": 18.0, "peak_rss_mb": 512.0, "bytes": 1000}
CLIP = {
    "source_bytes": 10_000_000, "text_chars": 400, "arabic_chars": 100, "segments": 10, "scenes": 5,
    "stages": {k: dict(STAGE) for k in ("ingest", "scenes_keyframes", "edit", "render")},
}


def test_tokens_formula() -> None:
    t = cb.tokens(CLIP, cb.ESTIMATE)
    assert t["transcript"] == pytest.approx(300 / 4 + 100 / 2)
    assert t["und_in"] == pytest.approx(800 + 125 + 60 + 30)
    assert t["und_out"] == 150
    assert t["plan_small_in"] == 2550


def test_price_clip_sums_stages_and_on_device_zeroes_asr_and_render() -> None:
    r = cb.price_clip(CLIP, cb.ASSUMPTIONS, cb.ESTIMATE, miss_rate=0.2)
    assert r["total"] == pytest.approx(sum(r[s] for s in cb.STAGES))
    assert r["asr"] == pytest.approx(cb.compute_cost(STAGE, cb.ASSUMPTIONS))
    d = cb.price_clip(CLIP, cb.ASSUMPTIONS, cb.ESTIMATE, miss_rate=0.2, on_device=True)
    assert d["asr"] == d["render"] == 0 and d["planning"] == r["planning"]
    hi = cb.price_clip(CLIP, cb.ASSUMPTIONS, cb.ESTIMATE, miss_rate=1.0)
    assert hi["planning"] > r["planning"] and hi["asr"] == r["asr"]


def test_assumptions_match_cited_sources() -> None:
    a = cb.ASSUMPTIONS
    assert a["vcpu_hour_usd"] == pytest.approx(0.040478, abs=1e-6)
    assert a["gb_hour_usd"] == pytest.approx(0.004446, abs=1e-6)
    assert a["haiku_5_5"] == {"input_usd_per_mtok": 0.10, "output_usd_per_mtok": 0.50}
