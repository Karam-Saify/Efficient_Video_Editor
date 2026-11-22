# ADR-0003: What "overlap" means for timeline v0 video clips
- **Status:** Proposed
- **Date:** 2026-11-22 · **Tier:** T2 · **Door:** two-way (a validator rule; no stored data depends on it)
- **Decider:** Founder (via Operator) · **Recommender:** engineering-lead · **Agree:** creative-lead (whether repeats are needed, H-0007) · **Input:** `company/handoffs/H-0004-review.md` F8 and ruling (a)

## Context
ARCHITECTURE.md lists the validator rule "no overlapping clips on the video track". In timeline v0, video
clips have no timeline position: they play back-to-back in array order, and their timeline start is the
cumulative sum computed by code (I-4). Two clips therefore can never overlap *in time on the track*. The
rule as enforced (H-0004, `src/validate` rule 3, code `E_OVERLAP`) is different: two video clips may not use
intersecting `[in_ms, out_ms)` ranges of the **same source**. The review (F8) flagged the wording gap.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Keep the enforced rule: no reuse of the same source range | Blocks accidental duplicate footage (a common LLM edit error); matches the code today | Forbids deliberate repeats (instant replay, callback hooks) |
| B. Drop rule 3 entirely (sequential clips cannot overlap) | Simplest; allows repeats | Duplicate footage passes silently |
| C. Rule A by default, plus an explicit per-clip `repeat: true` opt-out | Allows intentional repeats | Schema change; needs Creative to say repeats are wanted |

## Decision (proposed)
Option A for v0. ARCHITECTURE wording becomes: "no two video clips use intersecting `[in_ms, out_ms)`
ranges of the same source (`E_OVERLAP`)", which matches the `E_OVERLAP` docstring in
`src/validate/__init__.py`. Revisit as option C if Creative confirms in H-0007 that repeats are needed.

## Consequences
+ Wording and code agree. − Intentional repeats are impossible until option C. − Issue count is pairwise
O(n²) (H-0004 review F5, deferred).

## Reversal plan
Delete the rule-3 block in `semantic_issues` and fixture `i3_overlap.json`; under 15 minutes.

## Dissent
None recorded.
