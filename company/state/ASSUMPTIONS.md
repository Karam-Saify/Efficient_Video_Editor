# Assumption Register
Owner: Research (A), Product (R for business assumptions).
Every important belief the plan rests on is listed here, along with how it will be tested.
An assumption moves from **Untested → Testing → Validated / Invalidated**, with the evidence level and path.
When an assumption is invalidated, Product must open a scope review within one session.

| ID | Assumption | Type | If false, impact | Test | Evidence | Status |
|---|---|---|---|---|---|---|
| A-01 | For talking-head content, the transcript carries enough information to choose good cuts | Technical | Need visual captioning (more cost) | EXP-002 | — | Untested |
| A-02 | Word timestamps from ASR are accurate enough (< 150 ms drift) for clean cuts | Technical | Need forced alignment stage | EXP-001 | — | Untested |
| A-03 | An LLM can judge "hook strength" in Arabic content as well as a human rater | Technical | Need human-in-the-loop scoring | EXP-004 (correlation with Creative ratings) | — | Untested |
| A-04 | MILP selection keeps narrative coherence when cutting 10 min → 45 s | Technical | Need coherence constraints / LLM check | M2 rubric "coherence" item | — | Untested |
| A-05 | Revisions as timeline diffs stay small (< 2k tokens) | Technical / cost | Revision cost erodes the thesis | EXP-007 | — | Untested |
| A-06 | Rendering on CPU is fast enough for creator workflows (< 5 min per Short) | Technical | Need GPU / cloud render cost | M2 runtime metric | — | Untested |
| A-07 | Arabic creators find current AI-editing tools too expensive or weak in Arabic | Market | No differentiation | ≥ 10 creator interviews (M6) + competitor audit | — | Untested |
| A-08 | Creators will accept a code/text-based editing workflow (or a UI on top of it) | Market | Need full GUI before value | Founder usage at M4, interviews at M6 | — | Untested |
| A-09 | Our rubric score predicts audience retention | Quality | Optimising the wrong target | M5 correlation | — | Untested |
| A-10 | Cost per Short can be < 10% of comparable paid AI-editing tools | Business | Thesis fails | M3 cost + competitor pricing log | — | Untested |
| A-11 | FFmpeg + libass renders Arabic captions correctly on our caption style | Technical | Caption-style fix (Latin/digit size factor) or an alternative renderer needed | EXP-006 (INVALID), EXP-008 (FAIL), successor EXP-010 (registered, not drafted) | E2, `company/experiments/EXP-008-results.md` §8 | Refuted for the EXP-008 configuration (Latin/digit size mismatch; Arabic shaping and bidi passed, E2) |
