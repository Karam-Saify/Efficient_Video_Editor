# BRIEF H-0003 (Task A: repo skeleton)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0 (exit criterion 0.2)
- **Date:** 2026-11-22

1. **Objective (with why):** Turn the repo into a reproducible Python project with a cached CLI stub for every pipeline stage and CI, so every later stage plugs into the same contract (CLAUDE.md core rules 3 and 4: schema first, cache everything with a manifest, never recompute).
2. **Inputs (exact paths):**
   - `CLAUDE.md` (core technical rules), `company/positions/03-engineering/ARCHITECTURE.md`, `company/positions/03-engineering/CONVENTIONS.md`, `company/positions/03-engineering/CHECKLISTS.md`
   - Existing code to keep working: `src/common.py`, `src/ingest/__main__.py`, `src/render/__main__.py`, `src/validate/__main__.py`, `requirements.txt`
   - `.gitignore`
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - `pyproject.toml`: project metadata, `requires-python = ">=3.11"`, **exact pins (`==`)** for runtime and dev deps (pytest, ruff, jsonschema, pulp, etc.). Take the versions from what is installed in `.venv` (`.venv/bin/pip freeze`). Configure ruff (`target-version = "py311"`) and pytest (`testpaths = ["tests"]`). Keep `requirements.txt` consistent (or have it point to pyproject) and say which you chose.
   - **Python 3.11 is not installed on this machine** (only 3.12 and 3.14; `.venv` is 3.14). Run tests locally with `.venv/bin/python -m pytest`. CI must use Python **3.11** (`actions/setup-python`). Record this as a deviation in the return.
   - Folders: `src/{ingest,describe,score,select,edit,validate,render}/`, `src/prompts/`, `schemas/`, `tests/{unit,fixtures}/`, `cache/` (ignored), `samples/` (ignored). Use `.gitkeep`/README so empty folders are tracked.
   - Each stage: `python -m src.<stage> --input <path> --out <dir>` writes `<out>/manifest.json` with `input_hashes` (sha256 per input file), `config_hash`, `versions` (code/tool/python), `duration_s`, plus `stage`, `created_at`. On rerun with the same inputs and config, it prints a skip message and does no work (exit 0). Put the shared logic in one helper (e.g. `src/common.py` or `src/manifest.py`). It must be unit-tested, with at least these cases: first run writes, rerun skips, changed input reruns, changed config reruns.
   - **Do not break existing `ingest`, `validate` and `render` behaviour.** Their stubs may wrap the existing code. Do not run ingest on real media; heavy deps (faster-whisper) must not be imported at module import time in tests.
   - `.github/workflows/ci.yml`: on every push (and PR), checks out, sets up Python 3.11, installs ffmpeg only if tests need it, installs pinned deps, then runs `ruff check .` and `pytest`. Keep CI deps minimal (do not install faster-whisper/opencv in CI unless a test needs them; use an extra/group).
   - **Forbidden:** using any file in `data/golden/`, `data/heldout/`, `quarantine/`; sending video or images to the LLM; editing `company/CONSTITUTION.md`, accepted ADRs, or locked EXPs; `git commit`/`git push` (the Operator commits after review).
   - Do not touch `schemas/timeline.schema.json` or `src/validate/` rules. That is H-0004, the next brief.
4. **Output (format + exact path):** Code in the working tree. Return in `company/handoffs/H-0003-return.md` (OPERATING_MODEL §4), including the exact reproduction commands and pasted output of `ruff check .` and `pytest -q`.
5. **Done when:**
   - [ ] `pyproject.toml` with pinned deps, ruff and pytest config
   - [ ] All 7 stage packages + `src/prompts/` + `tests/unit/` + `tests/fixtures/` exist
   - [ ] `python -m src.<stage> --input X --out D` works for all 7 stages; manifest written; second run skips (shown in the return for at least 2 stages)
   - [ ] Unit tests for the manifest/skip logic pass; `.venv/bin/ruff check .` clean
   - [ ] `.github/workflows/ci.yml` present, Python 3.11, runs ruff + pytest
   - [ ] `cache/` and `samples/` are ignored (verify with `git check-ignore`)
   - [ ] Entry appended to `company/positions/03-engineering/LOG.md`
6. **Out of scope:** Real stage logic (ASR, scoring, MILP, LLM editing); the timeline schema and validator rules (H-0004); EXP-006 (H-0006); ADRs unless you make an architecture decision, in which case draft it as `Proposed`.
7. **Effort budget:** max 60 tool calls · max 2 retries per failing action
8. **Escalate if:**
   - A needed dependency cannot be installed in `.venv` offline/online after 2 tries
   - Keeping existing ingest/render behaviour would require changing a stage boundary (ADR needed)
9. **Termination condition:** All Done-when boxes are ticked, or a blocker is hit; the return file is written; you stop without committing.
10. **Consulted positions (from RACI) and what they must confirm:** Assurance (RACI 13 C) reviews the diff and must be able to reproduce `ruff` + `pytest` from a clean state (H-0003-review.md).
