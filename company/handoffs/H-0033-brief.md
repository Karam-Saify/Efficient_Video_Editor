# BRIEF H-0033
- **To:** assurance-lead · **Tier / Milestone:** T2 review: the ONE daily review of Week 1 A–D (ADR-0006) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Decide whether Week 1 A–D can be trusted before the Founder reads the report: cost numbers, recipe compiler, bench page and product consent text.
2. **Inputs:** returns `company/handoffs/H-0027`, `H-0028`, `H-0029`, `H-0030`, `H-0031`, `H-0032` (`-return.md`); `docs/COST_BASELINE.md`, `docs/RECIPE_LANGUAGE.md`, `docs/CAPABILITIES.md`, `company/positions/03-engineering/ARCHITECTURE.md`; ADR-0007..0021 (ADR-0014 is Proposed); `src/cost/`, `src/recipes/`, `recipes/`, `schemas/recipe.schema.json`, `bench/`; product files from H-0031; `company/positions/05-assurance/DATA_POLICY.md`, `DATA_RIGHTS.md`. Diff range `d17e8d4~20..HEAD`; use `git log` to find the first Week 1 commit, `511dbb7`.
3. **Constraints:** Read-only on `src/`, `tests/` and `bench/`. Frames and outputs go to `out/h0033/` (git-ignored). View at most 3 PNG frames. Never commit media. Write only the review, the repro, your LOG.md and DATA_RIGHTS.md rows.
4. **Output:** `company/handoffs/H-0033-review.md` (verdict + S1/S2/S3 findings) + `company/handoffs/H-0033-repro.txt`. Commit them, but do not push.
5. **Done when:**
   - [ ] **Cost (A):** recompute one per-clip row and the median from `experiments/results/H-0027_cost_measurements.json` and the assumptions. Check that every price in the doc cites a source. Check the cost-per-successful-export math (ledger tests + one hand calculation).
   - [ ] **Recipes (C):** reproduce 3 cells of the 36-cell matrix, including one `photos_to_video` designed failure. Check that UNRENDERED really lists every missing feature for 1 degraded recipe. ffprobe one of the `out/h0029/` renders against its timeline. Check captions on 1 frame. Rule on **ADR-0014** (`provenance.recipe`, additive).
   - [ ] **Bench (B):** read the page code for any bundled or uploaded dev clip, any non-pinned CDN URL and any data sent off-device. Check the JFK sample's licence and record it as an RR row (usable or not). Running it headless is optional.
   - [ ] **Product (D):** consent, retention and deletion text in PROMPT_COLLECTION_FORM and EXP-011 versus DATA_POLICY / ADR-0013. Fake doors must be honest: no fake payment capture. Rule on the proposed 90-day retention.
   - [ ] **Hygiene:** no media or dev-derived text in git (`git log --stat` over the range). The auto-push loop's push log has no blocked pushes. Suite + ruff green.
6. **Out of scope:** H-0026 F1–F8 (already reviewed; still open); H-0020 hook work.
7. **Effort budget:** max 40 tool calls · 2 retries.
8. **Escalate if:** media or dev-derived data is committed (S1 → HALT); the bench sends user media off-device; a cost figure cannot be reproduced within 5 %.
9. **Termination condition:** review + repro committed.
10. **Consulted:** none.
