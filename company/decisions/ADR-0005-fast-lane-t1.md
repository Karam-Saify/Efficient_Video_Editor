# ADR-0005: Fast lane: docs, tests, fixtures and config-only changes are T1
- **Status:** Accepted
- **Date:** 2026-11-22 · **Tier:** T2 (operating-model change, RACI row 30) · **Door:** two-way
- **Decider:** Founder (2026-11-22, Session 2 decision #3) · **Recommender:** Operator (the "process cost" threat in `company/reports/2026-11-22/README.md`) · **Agree (veto holders):** Assurance keeps its 1-in-5 sampling · **Input:** this session's handoffs H-0002..H-0018

## Context
On 2026-11-22 every small change went through a full brief → return → Assurance review cycle. That was safe, but small doc and test edits took as long as new modules. Reviews found real defects in *code* (stale cache, float crash, path escape, NUL-byte crash) and none in pure docs or fixtures.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Fast lane: docs/tests/fixtures/config-only = T1; several T1 items may share one brief; Assurance samples 1 in 5 | Much less overhead on low-risk work; review effort goes where defects are found | A bad fixture or config could slip through until sampled |
| B. Status quo (classify each change from scratch) | Maximum scrutiny | Slow; reviewer time spent on low-risk diffs |

## Decision
Option A. A change is **T1 (fast lane)** when it touches only documentation, tests, test fixtures or configuration **and** changes no runtime behaviour, schema, CLI contract, dependency, pipeline prompt or protected file. Fast-lane items need a `LOG.md` entry with evidence, not an Assurance review before merge. Several fast-lane items may share one brief. Assurance keeps sampling 1 in 5 T1 items per milestone (OPERATING_MODEL §1).

Still **not** fast lane, whatever the file type: `schemas/`; `pyproject.toml` and lock files (dependency changes); CI workflow changes that remove checks; `.claude/hooks/` and settings; rights-register changes to "usable"; locked experiments; accepted ADRs; the Constitution. Classification rules 1–4 still apply first; if in doubt, go one tier up (I-10).

## Consequences
Positive: faster docs and test work. Negative: there is no pre-merge review on fast-lane items; the 1-in-5 sampling is the safety net.

## Reversal plan
Supersede with a new ADR; there is nothing to migrate.

## Dissent
None recorded.

## Review date / trigger
The M0 gate, or the first sampled fast-lane item that Assurance rejects.
