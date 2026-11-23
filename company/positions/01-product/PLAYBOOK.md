# Playbook: Product & Strategy

## SOP-P1: Writing / revising the PR/FAQ (M0, then every gate)
1. Read `company/CONSTITUTION.md` §1–2, `docs/RESEARCH.md` "Gap" section, and `PERSONAS.md`.
2. Write a one-page press release dated at the M5 pilot: headline, sub-headline, problem (in the
   persona's words), solution, one quote from the Founder, one quote from a hypothetical creator, how to start.
3. Write FAQ: 5 external (what creators would ask: price, Arabic quality, speed, privacy, "does it
   replace my editor?") and 5 internal (what could kill us: ASR, rights, cost, competition, founder time).
4. For every FAQ answer, tag the assumption ID it depends on (`state/ASSUMPTIONS.md`); add new assumptions if missing.
5. Return to Operator. This is T2: Research checks the evidence claims, Assurance checks the risks.

## SOP-P2: Scope change request
1. Requester writes: what, why, which exit criterion it serves.
2. Product writes impact: added sessions, tokens, which risk changes, what gets dropped to make room.
3. Decide: accept (log in `SCOPE_LOG.md`), defer (backlog with milestone), or reject (reason).
4. A third scope change in one milestone automatically requires Founder approval.

## SOP-P3: Arbitration
1. Both positions submit ≤ 10-line statements with evidence paths.
2. Check veto domains first. If the dispute is inside someone's veto domain, it is not yours: escalate.
3. Decide with the single question "which option better serves the current milestone exit criteria at lower risk?"
4. Record as ADR with a Dissent section. Both parties commit.

## SOP-P4: Unit-economics model (from M2)
Fields per Short: ASR compute min · captioning tokens · scoring tokens · edit tokens · revision
tokens (median × expected revisions) · render min · Founder minutes. Source each number from
METRICS.md (measured), never estimate once measurements exist. Compare to ≥ 3 competitor price points from `COMPETITORS.md`.

## SOP-P5: Competitor log entry
Product name · URL · price tier(s) observed + date · Arabic support (tested or claimed) · core
feature · what we do better/worse · source credibility. Only facts with dates; no marketing adjectives.

## SOP-P6: Kill / pivot review (triggered by a kill criterion)
Write 3 options: persevere with change X, pivot to Y, stop. Each with cost, evidence and risk.
Founder decides. Record as a one-way-door ADR.
