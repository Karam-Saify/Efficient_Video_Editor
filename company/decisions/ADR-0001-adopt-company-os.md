# ADR-0001: Adopt the Company OS (five positions, work tiers, gated milestones)
- **Status:** Proposed
- **Date:** 2026-11-21 · **Tier:** T3 · **Door:** two-way in mechanics, one-way in culture
- **Decider:** Founder · **Recommender:** Operator (setup session) · **Agree:** all five positions · **Input:** MAST, Anthropic multi-agent lessons

## Context
The Founder wants the project to grow into a company and to be failure-resistant and validation-based,
with no loss of control or precision. Published evidence (MAST, arXiv 2503.13657) shows multi-agent LLM systems fail mostly from
specification issues, inter-agent misalignment and weak verification, and that structural fixes beat prompt tweaks.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Single agent + CLAUDE.md | Cheapest, simplest | No independent verification; everything rests on one context |
| B. Five positions + tiers + gates + hooks (this OS) | Builder≠verifier, explicit authority, persistent state, enforced invariants | More tokens at T2/T3; ceremony risk |
| C. Many specialised agents (10+) | Fine-grained | Coordination overhead; MAST shows complexity hurts |

## Decision
Option B. Proportionality keeps cost in check: T0/T1 stay lean; ceremony only at T2/T3.

## Consequences
+ Every important claim is reproduced by an independent position. + State survives sessions.
− Each T2 costs at least two agent invocations. − The Founder must sign gates.

## Reversal plan
Delete `.claude/agents/` and `.claude/settings.json` hooks; keep `company/` as documentation. Under 10 minutes.

## Dissent
None recorded.

## Review trigger
Retrospective after M2: is ceremony slowing progress without catching defects? (Check operating-health metrics.)
