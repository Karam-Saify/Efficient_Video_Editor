# BRIEF H-0032 (Week 1 · A, follow-up per Founder memo 2)
- **To:** engineering-lead · **Tier / Milestone:** T2 (new package; daily Assurance review) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Move the H-0027 instrumentation into `src/cost/` (ADR-0016). Measure cost per **successful** export, including retries and failures (ADR-0015). Retries and failures are what break a cost ceiling in production.
2. **Inputs:** `company/decisions/ADR-0015..0021`; `src/timings.py`, `experiments/cost_baseline.py`, `docs/COST_BASELINE.md`, `company/handoffs/H-0027-return.md`; `company/positions/03-engineering/ARCHITECTURE.md`; `company/state/METRICS.md`.
3. **Constraints:**
   - `src/cost/` holds the per-stage cost/time logger: wall, CPU, peak RSS, bytes, and an LLM usage hook with cached/uncached input tokens (ADR-0019; write to `cache/<id>/usage.jsonl`). It also holds a ledger that records every attempt (success / failed / retried) and computes $ per successful export.
   - Keep `src/timings.py` as a thin re-export, or update its callers; no behaviour change for `src.demo`.
   - Re-run the cost report from the existing measurement file. Add a "cost per successful export" section to `docs/COST_BASELINE.md` with a stated failure/retry assumption (failure rate observed so far + a sweep). There is no need to re-measure the clips.
   - Update `ARCHITECTURE.md` with the ADR-0016 module map (orchestrator, model_router, recipes, cost; describe/score/select new roles; learning later) and the ADR-0017 router order. Do **not** create empty orchestrator/model_router packages.
   - Build-mode rules. No new dependencies. Never commit media or derived data.
4. **Output:** code + tests + doc updates, committed (do not push). Return at `company/handoffs/H-0032-return.md`.
5. **Done when:**
   - [ ] `src/cost` exists with tests: ledger math, cached/uncached token accounting, failure counting.
   - [ ] COST_BASELINE.md shows cost per successful export (median, P90) at a 0 %, 5 % and 20 % failure rate.
   - [ ] ARCHITECTURE.md is updated. Suite + ruff green.
6. **Out of scope:** the router or orchestrator implementation; FrameBudgetAllocator; the bench; recipes.
7. **Effort budget:** max 35 tool calls · 2 retries.
8. **Escalate if:** moving the code would break the stage-contract CLI or the existing tests in a way that needs a schema change.
9. **Termination condition:** committed, return written.
10. **Consulted:** none (covered by the daily Assurance review).
- **Commit cadence (Founder):** commit each finished unit, with tests passing, about every 5 min of work. Do not push; the Operator pushes.
