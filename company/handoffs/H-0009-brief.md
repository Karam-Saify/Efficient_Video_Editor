# BRIEF H-0009 (fix pass for the H-0003 and H-0004 review findings, plus the Python floor)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0
- **Date:** 2026-11-22

1. **Objective (with why):** Close the review findings that block merging Tasks A and B, and settle the Python floor, so main gets a skeleton and validator that are correct on the interpreter we actually run.
2. **Inputs (exact paths):**
   - `company/handoffs/H-0003-review.md`, `company/handoffs/H-0004-review.md` (findings tables; required actions)
   - `pyproject.toml`, `requirements*.txt`, `.github/workflows/ci.yml`, `src/manifest.py`, `src/validate/`, `src/render/adapter.py`, `schemas/timeline.schema.json`, `experiments/e6_captions.py`
   - Founder decision 2026-11-22 (delegated to the Operator, "best decision for medium term"): **Python floor = 3.12**; CI runs on 3.12 and 3.14.
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - FIX: H-0003 **F1** (floor 3.12: `requires-python = ">=3.12"`, ruff `target-version = "py312"`, test_pins updated), **F2** (CI matrix 3.12 + 3.14; one job also installs the full runtime lock, so PuLP/numpy/av are import-tested; install apt `ffmpeg` only if a test needs it), **F3** (the skip key includes the code/stage version; a `status: "stub"` manifest never counts as valid for a non-stub stage), **F5** (clean error on bad JSON input), **F6** (raise `StageError` when `--out` is inside an `--input` dir), and **F4** (opencv duplicate, if a one-line fix).
   - FIX: H-0004 **F1** (reject non-integer ms with a coded error, `E_SCHEMA` or `E_TYPE`, and add a fixture or unit test for `2000.0`; no crash), **F2** (express "source has no audio" in v0 with a minimal, documented optional field `has_audio` default true, or make the adapter probe-free safe; list it under DEVIATIONS for Creative/Assurance), **F3** (reject source paths that are absolute or escape the repo, or that sit under `data/heldout/`, `quarantine/`, `data/golden/`; coded error), **F4** (port `experiments/e6_captions.py` to v0 or mark it deprecated with a clear error), **F8** (draft `company/decisions/ADR-0003-overlap-rule-v0.md` as **Proposed**).
   - Write `company/decisions/ADR-0002-python-floor-3-12.md` (Status: Accepted, Founder-delegated decision 2026-11-22, with context from H-0003-review F1) and add it to `company/decisions/INDEX.md`.
   - Leave everything else DEFER/WONTFIX as the reviews say; answer each finding in the return with FIX / WONTFIX / DEFER.
   - Do not touch `render/frames_check/`, `experiments/exp006_render.py` (EXP-006 evidence), or `company/experiments/`. Forbidden data: `data/golden/`, `data/heldout/`, `quarantine/`. Never view images. No commit/push.
4. **Output (format + exact path):** Code + ADRs in the working tree; return in `company/handoffs/H-0009-return.md` with a finding→action table, pasted `ruff check .` + `pytest -q` output, and the repro command.
5. **Done when:**
   - [ ] Every FIX item above is done, with a test that fails before the fix and passes after
   - [ ] ruff clean, all tests pass locally on 3.14 (and 3.12 via `/usr/bin/python3.12` venv if feasible)
   - [ ] ADR-0002 Accepted, ADR-0003 Proposed, INDEX updated
   - [ ] LOG.md entry
6. **Out of scope:** EXP-007 work, new stage logic, deferred findings, formatter adoption.
7. **Effort budget:** max 60 tool calls · max 2 retries per failing action
8. **Escalate if:** A fix requires a schema change beyond one optional field; the full runtime lock can't be installed in CI-like conditions after 2 tries.
9. **Termination condition:** Done-when ticked or blocked; return written; stop without committing.
10. **Consulted positions (from RACI) and what they must confirm:** Assurance re-reviews (H-0009-review.md) and confirms that each FIX closes its finding; Creative is informed of any schema field added.
