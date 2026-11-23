"""Attempt ledger (ADR-0015, H-0032): every export attempt is a JSON line; the metric is $ per SUCCESSFUL export.

Outcomes: `success` (terminal), `failed` (terminal: abandoned), `retried` (this attempt failed and another
attempt of the same export follows). Total spend counts every attempt; the denominator counts successes only.
No successes -> cost per success is +inf (never 0 and never a silent division error).
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

LEDGER = "ledger.jsonl"
LEDGER_SCHEMA = "ledger/1"
OUTCOMES = ("success", "failed", "retried")
TERMINAL = ("success", "failed")


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.rows: list[dict[str, Any]] = []
        if path.is_file():
            self.rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def add(self, export_id: str, *, attempt: int, outcome: str, cost_usd: float,
            stages: Mapping[str, float] | None = None, error: str | None = None) -> dict[str, Any]:
        if not export_id:
            raise ValueError("export_id is required")
        if outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {OUTCOMES}, got {outcome!r}")
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
            raise ValueError(f"attempt must be an integer >= 1, got {attempt!r}")
        if not cost_usd >= 0:
            raise ValueError(f"cost_usd must be >= 0, got {cost_usd!r}")
        if any(r["export_id"] == export_id and r["outcome"] in TERMINAL for r in self.rows):
            raise ValueError(f"export {export_id!r} already has a terminal outcome")
        row: dict[str, Any] = {"schema": LEDGER_SCHEMA, "export_id": export_id, "attempt": attempt,
                               "outcome": outcome, "cost_usd": float(cost_usd)}
        if stages:
            row["stages"] = {k: float(v) for k, v in stages.items()}
        if error:
            row["error"] = error
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        self.rows.append(row)
        return row

    def summary(self) -> dict[str, Any]:
        n = {o: sum(1 for r in self.rows if r["outcome"] == o) for o in OUTCOMES}
        total = sum(float(r["cost_usd"]) for r in self.rows)
        attempts = len(self.rows)
        return {
            "attempts": attempts, "exports": len({r["export_id"] for r in self.rows}),
            "successes": n["success"], "failed": n["failed"], "retried": n["retried"],
            "total_usd": total,
            "cost_per_successful_export_usd": total / n["success"] if n["success"] else float("inf"),
            "attempt_failure_rate": (n["failed"] + n["retried"]) / attempts if attempts else 0.0,
        }
