"""LLM usage hook (ADR-0019, H-0032): one JSON line per API call in `cache/<video_id>/usage.jsonl`.

Every call is logged, including failed attempts (validator rejects, retries): stage, model ID, attempt number,
ok, latency, and the four Anthropic usage token classes. `input_tokens` is the UNCACHED input; cached input is
`cache_read_input_tokens` (hits) and `cache_creation_input_tokens` (writes). A missing class is written as 0,
never dropped, so sums are always over the same fields. No prompt or response text is logged.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from src.cost.model import TOKEN_CLASSES, _count

USAGE = "usage.jsonl"
USAGE_SCHEMA = "usage/1"


def log_llm_call(path: Path, *, stage: str, model: str, attempt: int, ok: bool, latency_s: float,
                 usage: Mapping[str, Any], error: str | None = None) -> dict[str, Any]:
    """Append one call record to `path` and return it. Raises ValueError on a malformed record."""
    if not stage or not model:
        raise ValueError("stage and model are required")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise ValueError(f"attempt must be an integer >= 1, got {attempt!r}")
    if latency_s < 0:
        raise ValueError("latency_s must be >= 0")
    row: dict[str, Any] = {"schema": USAGE_SCHEMA, "stage": stage, "model": model, "attempt": attempt,
                           "ok": bool(ok), "latency_s": round(float(latency_s), 3)}
    row.update({k: _count(usage, k) for k in TOKEN_CLASSES})
    if error:
        row["error"] = error
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def read_usage(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def summarize_usage(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    s: dict[str, Any] = {"calls": len(rows), "failed_calls": sum(1 for r in rows if not r["ok"])}
    s.update({k: sum(int(r.get(k, 0)) for r in rows) for k in TOKEN_CLASSES})
    inp = s["input_tokens"] + s["cache_read_input_tokens"] + s["cache_creation_input_tokens"]
    s["cached_input_share"] = s["cache_read_input_tokens"] / inp if inp else 0.0
    return s
