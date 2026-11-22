# ADR-0002: Python floor is 3.12; CI runs 3.12 and 3.14
- **Status:** Accepted
- **Date:** 2026-11-22 · **Tier:** T2 · **Door:** two-way (lowering the floor later only needs older pins)
- **Decider:** Founder, delegated to the Operator on 2026-11-22 ("best decision for medium term") · **Recommender:** engineering-lead · **Input:** assurance-lead risk opinion in `company/handoffs/H-0003-review.md`

## Context
H-0003 declared `requires-python = ">=3.11"`, but the runtime lock (`requirements.txt`, frozen from the
3.14 `.venv`) contains 5 pins with no 3.11 wheel: `av`, `cpsat-logutils`, `numpy`, `orloge`, `PuLP`
(H-0003 review F1, Part A3). `av` is required by faster-whisper, so ingest was broken on 3.11 as well as
MILP `select`. CI ran on 3.11 with core + dev only, so the interpreter and dependency set we actually use
had no CI coverage (F2). The Codespace already ships 3.12 and 3.14.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Floor 3.12, CI matrix 3.12 + 3.14, full-lock CI job | `requires-python` becomes true; keeps the exact pins that produced E6/EXP-006 evidence; CI covers MILP/ASR deps | Excludes 3.11 users (none: the product runs locally in a Codespace with 3.12/3.14) |
| B. Keep 3.11, downgrade pins to 3.11-compatible versions | Wider interpreter support | Re-pins numpy/PuLP/av; invalidates evidence produced on current pins; PuLP 4 API differs from 3.x |
| C. Floor 3.14 only | One interpreter | Excludes the system 3.12; no floor/ceiling check |

## Decision
Option A. `pyproject.toml`: `requires-python = ">=3.12"`, ruff `target-version = "py312"`. CI: `test` job
(core + dev) and `runtime` job (full `requirements.txt` + dev, `pip check`, `VAC_FULL_RUNTIME=1` import
and MILP smoke tests), each on 3.12 and 3.14. `tests/unit/test_pins.py::test_python_floor_is_3_12` guards it.

## Consequences
+ Declared floor matches the lock (verified: fresh 3.12 venv installs `requirements.txt` + dev, `pip check` clean).
+ Phase 1 `select` (PuLP + CBC) is testable in CI. − Runtime CI job adds about a minute and needs apt `coinor-cbc`.

## Reversal plan
Set `requires-python` and ruff target back, re-pin the 5 packages to 3.11 wheels, drop 3.12 from the matrix. About 1 hour plus re-running evidence.

## Dissent
None recorded.
