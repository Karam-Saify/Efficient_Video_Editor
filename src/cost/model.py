"""Cost model (H-0027, moved by H-0032): pure arithmetic in code, never by an LLM (I-4).

- `compute_cost`: vCPU-hours + GB-hours of peak RSS over wall time (the Fargate billing shape).
- `storage_cost`, `llm_cost` (uncached input + output), `usage_cost` (ADR-0019: uncached input, cache reads,
  cache writes and output priced separately), `planning_cost` (ADR-0008: small model always, big model on a miss).
- `expected_cost_per_success` (ADR-0015): the closed form of the ledger metric under independent attempt failures.
- `percentile`.
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Mapping, Sequence
from typing import Any

# Anthropic prompt caching: cache reads ~0.1x base input, 5-minute cache writes ~1.25x (claude-api skill,
# "Verifying Cache Hits"). Used only when a price dict has no explicit cache price; some models list their own
# (Sonnet 5.5 cache read $0.10, Opus 5.5 $0.20 per 1M).
CACHE_READ_MULT, CACHE_WRITE_MULT = 0.1, 1.25
TOKEN_CLASSES = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")

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


def _count(usage: Mapping[str, Any], key: str) -> int:
    v = usage.get(key, 0)
    if v is None:
        v = 0
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise ValueError(f"{key} must be a non-negative integer, got {v!r}")
    return v


def usage_cost(usage: Mapping[str, Any], price: Mapping[str, Any]) -> float:
    """USD for one API call from its `usage` block (Anthropic field names). `input_tokens` is the uncached part."""
    base = float(price["input_usd_per_mtok"])
    read = float(price.get("cache_read_usd_per_mtok", base * CACHE_READ_MULT))
    write = float(price.get("cache_write_usd_per_mtok", base * CACHE_WRITE_MULT))
    out = float(price["output_usd_per_mtok"])
    n = {k: _count(usage, k) for k in TOKEN_CLASSES}
    return (n["input_tokens"] * base + n["cache_read_input_tokens"] * read
            + n["cache_creation_input_tokens"] * write + n["output_tokens"] * out) / 1e6


def expected_cost_per_success(attempt_cost_usd: float, *, failure_rate: float, max_retries: int = 2,
                              retry_cost_usd: float | None = None) -> float:
    """Expected total spend / successful exports when each attempt fails independently with `failure_rate`.

    A failed attempt is charged in full (conservative: it failed late, e.g. at validate or render). A job is
    retried up to `max_retries` times (the LLM retry cap), each retry costing `retry_cost_usd` (default: a full
    attempt; less when earlier stages are cached, CLAUDE.md rule 4), then abandoned. Spend per job =
    c + r (f + ... + f^R); P(success) = 1 - f^(R+1).
    """
    f = float(failure_rate)
    if not 0 <= f < 1:
        raise ValueError(f"failure_rate must be in [0, 1), got {failure_rate}")
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    r = attempt_cost_usd if retry_cost_usd is None else retry_cost_usd
    spend = attempt_cost_usd + r * sum(f**k for k in range(1, max_retries + 1))
    return spend / (1 - f ** (max_retries + 1))
