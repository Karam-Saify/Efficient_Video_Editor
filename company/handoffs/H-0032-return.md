# RETURN H-0032 · engineering-lead · 2026-11-23

STATUS: DONE (deviations D1 to D3)

SUMMARY:
- `src/cost/` now holds four modules:
  - `meter`: the H-0027 instrumentation, moved here.
  - `model`: pure-code pricing, plus `usage_cost` for cached and uncached tokens and `expected_cost_per_success`.
  - `usage`: the `usage.jsonl` LLM hook (ADR-0019).
  - `ledger`: records every attempt (success, failed or retried) and gives $ per successful export (ADR-0015).
  `src/timings.py` is a thin re-export, so `src.demo` is unchanged.
- **Cost per successful export**, re-run from the H-0027 measurement file. Assumptions: miss rate 0.2, Sonnet 5.5 on a miss, cold retries, at most 2 retries, failed attempts charged in full.
  - At 0 % failures: median **$0.0080**, P90 **$0.0111**.
  - At 5 %: median **$0.0084**, P90 **$0.0117**.
  - At 20 %: median **$0.0100** (9.983 m$, under by 0.017 m$), P90 **$0.0139**.
  - The observed failure rate so far is 1 of 9 attempts (11.1 %): median $0.0090, P90 $0.0125.
- The ceiling verdict does not change, but at a 20 % failure rate the median uses up the whole $0.01 ceiling. Cached retries recover only about 0.4 m$, because a retry still pays for planning and render.
- ARCHITECTURE.md now has the ADR-0016 module map and the ADR-0017 router order. No orchestrator or model_router package was created.

ARTIFACTS:
- New:
  - `src/cost/__init__.py`, `src/cost/meter.py` (git mv of `src/timings.py`), `src/cost/model.py`, `src/cost/usage.py`, `src/cost/ledger.py`
  - `tests/unit/test_cost.py` (18 tests)
- Changed:
  - `src/timings.py` (now a re-export)
  - `experiments/cost_baseline.py`: imports from `src.cost`; adds `per_success()`, `OBSERVED`, `FAILURE_SWEEP` and the report section
  - `tests/unit/test_cost_baseline.py`: +1 test
  - `docs/COST_BASELINE.md`: new section "Cost per successful export (ADR-0015, H-0032)"; the §1 instrumentation path and the A10 note are updated
  - `company/positions/03-engineering/ARCHITECTURE.md`: module map and router order
- Commits (not pushed): 258b07d (src/cost), 99f954a (report and doc), d92e7ad (architecture), plus this return and log.

EVIDENCE:
- Red first: `.venv/bin/python -m pytest -q tests/unit/test_cost.py` failed with `1 error during collection` before `src/cost` existed.
- Green:
  - `.venv/bin/python -m pytest -q` gives `381 passed, 8 skipped`. It was 363 + 8 at H-0029: 18 tests are new in test_cost.py and 1 in test_cost_baseline.py.
  - `.venv/bin/ruff check .` gives `All checks passed!`.
- What the tests cover:
  - Ledger math: 5 attempts across 3 exports. Total ÷ successes is checked, and a reload from JSONL gives the same summary.
  - Edge cases: no success gives +inf, not 0. Bad outcome, negative cost and attempt 0 are rejected, and so is a second terminal outcome for one export.
  - Token accounting: uncached input, cache read, cache write and output are each priced separately. When a price has no explicit cache prices, the default 0.1x / 1.25x multipliers apply. Negative or float counts are rejected.
  - The usage.jsonl round trip: a missing token class is written as 0, never dropped.
  - Failure counting: `attempt_failure_rate` = (failed + retried) / attempts.
  - The closed form matches a seeded ledger simulation (20 000 exports, f = 0.2, within 1 %).
  - The `timings` re-export returns the identical objects.
- Report reproduction and determinism:
  - The report was re-run from `experiments/results/H-0027_cost_measurements.json`; nothing was re-measured.
  - Leaving out the new section, the output is identical to the existing doc §3 (blank-line-insensitive diff: `IDENTICAL`).
  - Two report runs are byte-identical (`cmp` OK).
- Checks on the diff: no media and no `cache/` in it; the secrets grep is empty.
- Row for Assurance to check: the Download (5) attempt is 8.111 m$ (doc §3). At f = 0.2 cold, 8.111 × (1 + 0.2 + 0.04) / (1 − 0.008) = 10.139 m$.
- One-line reproduction: `.venv/bin/python -m pytest -q tests/unit/test_cost.py tests/unit/test_cost_baseline.py && .venv/bin/python experiments/cost_baseline.py report | sed -n '/Cost per successful export/,/Client-side/p'`

DONE-WHEN CHECK:
- ✅ `src/cost` exists, with tests for ledger math, cached/uncached token accounting and failure counting (`tests/unit/test_cost.py`).
- ✅ COST_BASELINE.md shows the median and P90 cost per successful export at 0 %, 5 % and 20 %, plus the observed 11.1 %, with the failure and retry assumption stated.
- ✅ ARCHITECTURE.md is updated, and the suite and ruff are green.

DEVIATIONS FROM BRIEF:
- D1: The work went on branch `t2/install-company-os`, not `t2/H-0032`. I kept the branch that H-0025 to H-0029 already stack on, so the Operator can push one branch. Assurance review is still pending, so nothing is merged.
- D2: The observed failure rate is reconstructed, not taken from a ledger. It is the 1 of 9 attempts in the H-0027 return (D1 there: an ops-file error, not a pipeline fault), because no ledger existed before this brief. n = 9, so it is not a production estimate. H-0025 and H-0029 runs were not counted, because their attempts were never recorded.
- D3: Nothing writes to the ledger or the usage hook yet:
  - `src.demo` is unchanged, as the brief required.
  - There is no orchestrator, which is out of scope.
  - There is no LLM call yet.
  The first orchestrator or LLM-stage brief should call `Ledger.add` once per attempt and `log_llm_call` once per API call.

OPEN QUESTIONS:
1. What failure rate should the budget assume? Product-lead should answer. At 20 % the median is at the ceiling, so the miss-rate lever (L1) now also has to pay for failures.
2. Haiku 5.5 cache prices are not listed in the skill table, so the code uses the default 0.1x read and 1.25x write (5-minute cache). The 1-hour write (about 2x) is not modelled. Research-lead should confirm these against live pricing before a real LLM stage is costed.
3. Should a failed attempt keep its storage bytes, or are they deleted at once? Product-lead should answer. The model charges the attempt in full, including storage; retries charge no extra storage.
4. Is a ledger per video (`cache/<id>/ledger.jsonl`) enough, or does the M1 metric need a global ledger across videos? This is for Assurance and product-lead, and an orchestrator brief should decide it.

CONFIDENCE: Medium. The arithmetic is tested, but the biggest doubt is the input. The failure rate is a sweep over an n = 9 observation, and the dominant planning cost is still the H-0027 token estimate, not measured usage.

NEXT RECOMMENDED STEP: In the first orchestrator or LLM-stage brief, wire `Ledger.add` and `log_llm_call` in, then replace `OBSERVED` and the token ESTIMATE with ledger and usage.jsonl actuals.
