"""H-0032: src/cost — ledger math, cached/uncached token accounting, failure counting, timings re-export."""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from src import cost as C
from src import timings as T

HAIKU = {"input_usd_per_mtok": 0.10, "output_usd_per_mtok": 0.50}
SONNET = {"input_usd_per_mtok": 2.00, "output_usd_per_mtok": 10.00, "cache_read_usd_per_mtok": 0.10,
          "cache_write_usd_per_mtok": 2.50}


# ---- timings stays a thin re-export (no behaviour change for src.demo) ----

def test_timings_reexports_the_same_objects() -> None:
    for name in ("run_measured", "measure", "record", "tree_bytes", "TIMINGS", "TIMINGS_SCHEMA",
                 "compute_cost", "storage_cost", "llm_cost", "planning_cost", "percentile"):
        assert getattr(T, name) is getattr(C, name), name


# ---- cached / uncached token accounting (ADR-0019) ----

def test_usage_cost_prices_each_token_class_separately() -> None:
    u = {"input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000,
         "cache_creation_input_tokens": 1_000_000, "output_tokens": 1_000_000}
    # 2.00 uncached + 0.10 cache read + 2.50 cache write + 10.00 output
    assert C.usage_cost(u, SONNET) == pytest.approx(14.60)


def test_usage_cost_default_cache_multipliers_when_price_has_none() -> None:
    u = {"input_tokens": 0, "cache_read_input_tokens": 1_000_000, "cache_creation_input_tokens": 1_000_000,
         "output_tokens": 0}
    # 0.1x and 1.25x of the 0.10 base input price
    assert C.usage_cost(u, HAIKU) == pytest.approx(0.01 + 0.125)


def test_usage_cost_equals_llm_cost_with_no_caching() -> None:
    u = {"input_tokens": 5000, "output_tokens": 1500}
    assert C.usage_cost(u, SONNET) == pytest.approx(C.llm_cost(5000, 1500, SONNET))


def test_usage_cost_rejects_negative_or_non_integer_counts() -> None:
    with pytest.raises(ValueError):
        C.usage_cost({"input_tokens": -1, "output_tokens": 0}, HAIKU)
    with pytest.raises(ValueError):
        C.usage_cost({"input_tokens": 1.5, "output_tokens": 0}, HAIKU)


def test_log_llm_call_appends_jsonl_and_summarises(tmp_path: Path) -> None:
    p = tmp_path / "vid" / C.USAGE
    C.log_llm_call(p, stage="score", model="claude-haiku-5-5", attempt=1, ok=False, latency_s=0.8,
                   usage={"input_tokens": 300, "cache_read_input_tokens": 2000, "output_tokens": 40},
                   error="E_SCHEMA")
    C.log_llm_call(p, stage="score", model="claude-haiku-5-5", attempt=2, ok=True, latency_s=0.7,
                   usage={"input_tokens": 320, "cache_read_input_tokens": 2000,
                          "cache_creation_input_tokens": 0, "output_tokens": 45})
    rows = C.read_usage(p)
    assert [r["attempt"] for r in rows] == [1, 2]
    assert rows[0]["cache_creation_input_tokens"] == 0  # missing class written as 0, never dropped
    assert set(rows[0]) >= {"stage", "model", "input_tokens", "cache_read_input_tokens",
                            "cache_creation_input_tokens", "output_tokens", "latency_s", "attempt", "ok"}
    s = C.summarize_usage(rows)
    assert s == {"calls": 2, "failed_calls": 1, "input_tokens": 620, "cache_read_input_tokens": 4000,
                 "cache_creation_input_tokens": 0, "output_tokens": 85,
                 "cached_input_share": pytest.approx(4000 / 4620)}
    assert p.read_text(encoding="utf-8").count("\n") == 2


def test_log_llm_call_requires_stage_and_model(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        C.log_llm_call(tmp_path / C.USAGE, stage="", model="m", attempt=1, ok=True, latency_s=0.1,
                       usage={"input_tokens": 1, "output_tokens": 1})


# ---- ledger: every attempt, $ per successful export (ADR-0015) ----

def test_ledger_counts_every_attempt_and_divides_by_successes(tmp_path: Path) -> None:
    led = C.Ledger(tmp_path / C.LEDGER)
    led.add("e1", attempt=1, outcome="retried", cost_usd=0.004, error="E_VALIDATE")
    led.add("e1", attempt=2, outcome="success", cost_usd=0.006)
    led.add("e2", attempt=1, outcome="success", cost_usd=0.005)
    led.add("e3", attempt=1, outcome="retried", cost_usd=0.003)
    led.add("e3", attempt=2, outcome="failed", cost_usd=0.003)  # abandoned
    s = led.summary()
    assert s["attempts"] == 5 and s["exports"] == 3
    assert s["successes"] == 2 and s["failed"] == 1 and s["retried"] == 2
    assert s["total_usd"] == pytest.approx(0.021)
    assert s["cost_per_successful_export_usd"] == pytest.approx(0.021 / 2)
    assert s["attempt_failure_rate"] == pytest.approx(3 / 5)
    # persisted as JSON lines and re-read identically
    assert C.Ledger(tmp_path / C.LEDGER).summary() == s
    assert len((tmp_path / C.LEDGER).read_text(encoding="utf-8").splitlines()) == 5


def test_ledger_no_success_is_infinite_not_zero(tmp_path: Path) -> None:
    led = C.Ledger(tmp_path / C.LEDGER)
    led.add("e1", attempt=1, outcome="failed", cost_usd=0.002)
    assert led.summary()["cost_per_successful_export_usd"] == float("inf")
    assert C.Ledger(tmp_path / "empty.jsonl").summary()["attempts"] == 0


@pytest.mark.parametrize("bad", [
    {"outcome": "ok"}, {"cost_usd": -0.1}, {"attempt": 0}, {"export_id": ""},
])
def test_ledger_rejects_bad_entries(tmp_path: Path, bad: dict) -> None:
    kw = {"export_id": "e1", "attempt": 1, "outcome": "success", "cost_usd": 0.001} | bad
    with pytest.raises(ValueError):
        C.Ledger(tmp_path / C.LEDGER).add(kw.pop("export_id"), **kw)


def test_ledger_rejects_a_second_terminal_outcome_for_one_export(tmp_path: Path) -> None:
    led = C.Ledger(tmp_path / C.LEDGER)
    led.add("e1", attempt=1, outcome="success", cost_usd=0.001)
    with pytest.raises(ValueError):
        led.add("e1", attempt=2, outcome="success", cost_usd=0.001)


# ---- expected cost per success under a failure rate ----

def test_expected_cost_per_success_closed_form() -> None:
    assert C.expected_cost_per_success(0.01, failure_rate=0.0) == pytest.approx(0.01)
    # no retries: spend c per attempt, success prob (1 - f)
    assert C.expected_cost_per_success(0.01, failure_rate=0.2, max_retries=0) == pytest.approx(0.01 / 0.8)
    # 2 retries at full cost: c (1 + f + f^2) / (1 - f^3)
    f = 0.2
    want = 0.01 * (1 + f + f * f) / (1 - f**3)
    assert C.expected_cost_per_success(0.01, failure_rate=f, max_retries=2) == pytest.approx(want)
    # cheaper (cached) retries: c + rc (f + f^2), same denominator
    want = (0.01 + 0.004 * (f + f * f)) / (1 - f**3)
    assert C.expected_cost_per_success(0.01, failure_rate=f, retry_cost_usd=0.004) == pytest.approx(want)
    with pytest.raises(ValueError):
        C.expected_cost_per_success(0.01, failure_rate=1.0)


def test_closed_form_matches_a_seeded_ledger_simulation(tmp_path: Path) -> None:
    """The ledger, fed independent failures at rate f with <= 2 retries, converges to the closed form."""
    rng, f, full, retry = random.Random(20261123), 0.2, 0.010, 0.004
    led = C.Ledger(tmp_path / C.LEDGER)
    for i in range(20000):
        for a in range(1, 4):
            fail = rng.random() < f
            outcome = ("retried" if a < 3 else "failed") if fail else "success"
            led.add(f"e{i}", attempt=a, outcome=outcome, cost_usd=full if a == 1 else retry)
            if not fail:
                break
    sim = led.summary()["cost_per_successful_export_usd"]
    assert sim == pytest.approx(C.expected_cost_per_success(full, failure_rate=f, retry_cost_usd=retry), rel=0.01)


def test_ledger_file_is_json_lines_with_schema(tmp_path: Path) -> None:
    led = C.Ledger(tmp_path / C.LEDGER)
    led.add("e1", attempt=1, outcome="success", cost_usd=0.001, stages={"render": 0.0009})
    row = json.loads((tmp_path / C.LEDGER).read_text(encoding="utf-8"))
    assert row["schema"] == C.LEDGER_SCHEMA and row["stages"] == {"render": 0.0009}
