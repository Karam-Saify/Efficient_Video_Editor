# BRIEF H-0029 (Week 1 · C, part 2 of 2)
- **To:** engineering-lead · **Tier / Milestone:** T2 (new module + new interface; daily Assurance review) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Turn creative-lead's 12 recipes into a typed recipe language that compiles to `timeline.json` through `src/edit` ops. This is the engine behind recipe-first intelligence (ADR-0008) and provenance explanations (ADR-0009).
2. **Inputs:** `company/handoffs/H-0028-recipes.md` + `H-0028-return.md`; `src/edit/ops.py`, `src/edit/history.py`, `src/demo/`, `src/validate/`, `src/capabilities.py`, `docs/CAPABILITIES.md`; `schemas/timeline.schema.json`; `quarantine/dev/` (dev testing only).
3. **Constraints:**
   - The recipe schema is a JSON Schema at `schemas/recipe.schema.json`. A recipe has: id, version, structure beats, hook, pacing curve, caption style, sound, typed params with defaults and ranges, principle ids. Fill = recipe + param values (from a model later; from defaults/tests now).
   - The compiler is pure Python (`src/recipe/`). It runs fill → ops list → `src/edit` ops → a validated timeline. All times are computed by code. The provenance (recipe id + version, param values, principle ids) is written into `timeline.provenance`, and the `ADR-0006 dev-only` marker is set when `allow_dev` is used (H-0026 F2).
   - Honesty: a recipe field the renderer cannot draw (e.g. `sound.music_bed`) must either compile to nothing *and* be reported as `UNRENDERED` in the compile result, or be rejected. It must never be silently dropped. Reuse `src/capabilities.py`.
   - Fewer timeline-schema changes is better. Any change gets a `Proposed` ADR (next free number, ADR-0014).
   - No new dependencies, no LLM.
4. **Output:** `docs/RECIPE_LANGUAGE.md` v0 (spec, examples, compile semantics, error codes); `schemas/recipe.schema.json`; `recipes/*.json` (12 files); `src/recipe/` compiler + CLI `python -m src.recipe compile --recipe … --video … [--set k=v]`; tests. Return at `company/handoffs/H-0029-return.md` with the test matrix.
5. **Done when:**
   - [ ] All 12 recipes validate against `recipe.schema.json`.
   - [ ] **Every recipe compiles to a valid timeline on 3 dev clips** (36 compiles; pick 3 unique speech clips, and say which). The matrix is in the return. A recipe that cannot fit a clip (e.g. music-only on a talking head) must fail with a coded error, and that counts as a pass if the error is the designed one. Say which ones.
   - [ ] Render 3 of the 36 timelines (different recipes) to `out/h0029/` for the Assurance review; give the paths.
   - [ ] Unit tests: param type/range errors, unknown recipe id, UNRENDERED reporting, provenance content, determinism (same fill → byte-identical timeline).
   - [ ] Suite + ruff green.
6. **Out of scope:** model selection/fill (no LLM); the bench (task B); H-0026 fixes other than the F2 marker.
7. **Effort budget:** max 60 tool calls · 2 retries.
8. **Escalate if:** fewer than 9 recipes can compile with today's ops; a timeline-schema change would break existing valid timelines.
9. **Termination condition:** committed (do not push), return written.
10. **Consulted:** creative-lead's H-0028 is the content source. If you change a recipe's meaning, list it under DEVIATIONS.

## Addendum (Operator, after H-0028 return)
- **Escalation reading:** degraded recipes count toward the "≥ 9 compile" rule **only if** the compile result lists every missing feature as `UNRENDERED` (by recipe field). Creative's status per recipe: 4 full (R01, R03, R07, R08), 7 degraded (R02, R04, R05, R06, R09, R10, R12), 1 not worth building (R11, music-only).
- **R11:** it must still have a recipe file. On speech clips and on clips without captions it either compiles with captions off, or fails with a designed coded error. Pick one, document it, and test it.
- **Stretch (only if the core is done within ~40 tool calls):** a text overlay (non-spoken on-screen text, rendered via ASS with the EXP-008 font pair). It unblocks 8 recipes. It must be added to `src/capabilities.py` and CAPABILITIES.md; if you skip it, it stays UNRENDERED. Do not do a reorder op, a music bed or per-beat style today. List them as backlog in RECIPE_LANGUAGE.md.
- R12 stays out of the golden set until the EXP-008 per-script size fix lands. Compile only.
