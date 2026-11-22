# BRIEF H-0004 (Task B: timeline schema v0 + validator)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0 (exit criterion 0.2)
- **Date:** 2026-11-22

1. **Objective (with why):** Formalise timeline schema v0 and a validator that enforces it, because every stage reads/writes the timeline and nothing renders unless it validates (CLAUDE.md core rule 3, "LLM decides, code enforces").
2. **Inputs (exact paths):**
   - `company/positions/03-engineering/ARCHITECTURE.md` §"Timeline schema v0" (authoritative shape + validator rules)
   - Existing `schemas/timeline.schema.json` and `src/validate/` (reconcile; ARCHITECTURE.md wins on conflict, list differences in the return)
   - Skeleton from H-0003 (`pyproject.toml`, `tests/`, manifest helper); `src/render/__main__.py` (consumer: must still accept valid timelines)
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - JSON Schema (draft 2020-12) check first, then these semantic rules, each with a **stable error code** (e.g. `E_SOURCE_MISSING`, `E_RANGE`, `E_OVERLAP`, `E_CAPTION_BOUNDS`, `E_DURATION`, `E_CAPTION_DIR`, `E_EFFECT_TYPE`, plus `E_SCHEMA`):
     1. every clip/audio `source` references a declared source, and the source file exists. Hash check runs only when the file exists and `sha256` is given; keep the existence check testable with fixture files in `tests/fixtures/`.
     2. `0 <= in_ms < out_ms <= source.duration_ms`
     3. no overlapping clips on the video track
     4. every caption has `0 <= start_ms < end_ms <= total duration`
     5. total duration == `target_duration_ms` ± 1 frame (frame = 1000/fps ms); integer arithmetic in code
     6. every caption has `dir` (`rtl`|`ltr`)
     7. only known effect types (define the enum; at minimum `zoom`)
   - Validator returns ALL errors (not just the first), as structured objects; CLI `python -m src.validate <timeline.json>` exits 0 on valid, 1 on invalid, and keeps the H-0003 `--input/--out` manifest stub working.
   - Fixtures: **5 valid** (vary: single clip, multi-clip, captions rtl+ltr, effects, audio) and **5 invalid**, each invalid one breaking exactly one *different* semantic rule (pick 5 of rules 1–7; say which 2 are only covered by extra unit tests, and cover those too). Tests prove each valid passes and each invalid fails with exactly the expected code.
   - Fixture media: tiny generated placeholder files only (or `sources` pointing to small text files). **Never** reference `data/golden/`, `data/heldout/`, `quarantine/`, `samples/`.
   - Schema change is an interface change. Keep field names exactly as in ARCHITECTURE.md. If you must add a field, list it under DEVIATIONS for Creative/Assurance.
   - No commit/push. Do not edit ARCHITECTURE.md (if it needs changes, draft a `Proposed` ADR instead).
4. **Output (format + exact path):** `schemas/timeline.schema.json`, `src/validate/`, `tests/fixtures/timelines/{valid,invalid}/*.json`, `tests/unit/test_validate.py`. Return in `company/handoffs/H-0004-return.md` with the rule→fixture→error-code table and pasted `pytest -q` + `ruff check .` output.
5. **Done when:**
   - [ ] Schema implements the ARCHITECTURE v0 shape; existing render path still works on a valid fixture (dry run / unit test, no real media)
   - [ ] 7 rules implemented with error codes; all errors returned
   - [ ] 5 valid + 5 invalid fixtures; tests green; ruff clean
   - [ ] Entry appended to `company/positions/03-engineering/LOG.md`
6. **Out of scope:** Rendering changes, MILP, LLM tools, EXP-006, caption styling fields beyond v0.
7. **Effort budget:** max 60 tool calls · max 2 retries per failing action
8. **Escalate if:** ARCHITECTURE.md is ambiguous in a way that changes behaviour (e.g. what "total duration" means: sum of clips vs last out). Pick the obvious reading, state it, and flag it; escalate only if the readings conflict with the render code.
9. **Termination condition:** Done-when ticked or blocked; return written; stop without committing.
10. **Consulted positions (from RACI) and what they must confirm:** Creative (RACI 12 C) confirms in H-0007 that v0 caption fields (`text`, `style`, `dir`, timing) can express Arabic caption needs; Assurance reviews (H-0004-review.md) and reproduces tests.
