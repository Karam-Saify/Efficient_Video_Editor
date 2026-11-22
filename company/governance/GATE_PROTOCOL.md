# Milestone Gate Protocol (T3)

Inspired by Stage-Gate (Cooper), aviation crew resource management (independent cross-checks,
challenge-and-response), and the Delphi method (independent judgments before discussion, to avoid
anchoring and groupthink). Run with `/gate Mx`.

## Preconditions: the gate cannot open unless all are true
- [ ] All milestone exit criteria in `state/ROADMAP.md` have an evidence path filled in.
- [ ] No open `HALT` in STATE.md.
- [ ] All T2 items in the milestone have an Assurance verdict.
- [ ] Working tree clean; `main` pushed; tag candidate `gate-Mx-candidate` created.
- [ ] Pre-mortem for this milestone exists (`gates/Mx/premortem.md`) and each of its risks is
      closed, mitigated, or accepted by the Founder.

## Phase 1: Evidence pack (Assurance, ≤ 1 session)
Assurance assembles `gates/Mx/evidence-pack.md`: each exit criterion → claim → evidence path →
how to reproduce (exact commands) → Assurance's own reproduction result.
For M3+ Assurance runs the pipeline on `data/heldout/` (the only time it is touched) and records results.

## Phase 2: Independent reviews (all five positions, blind)
- Each position is dispatched **in a fresh context** with only: the evidence pack, its own CHARTER,
  its own gate checklist (in its `CHECKLISTS.md`), and the ROADMAP entry.
- Each writes `gates/Mx/review-<position>.md` **before seeing any other review**.
- Each review contains:
  1. Verdict: `GO` | `GO-WITH-CONDITIONS` | `NO-GO`
  2. Gate checklist with every item ticked or failed, and evidence for each tick.
  3. Top 3 risks it sees for the *next* milestone.
  4. Conditions (if any): each with owner, due milestone, verification method.
  5. NO-GO only: domain clause + evidence + what would lift it (see DECISION_RIGHTS §3).
  6. Confidence (H/M/L) + one prediction about next milestone that can later be checked.

## Phase 3: Challenge round
- Operator places all five reviews side by side in `gates/Mx/synthesis.md`.
- Any contradiction between reviews (one says a criterion passes, another says it fails) gets one
  challenge-response exchange: the challenger states the evidence, the challenged position answers
  once. No more than two rounds per contradiction, then it is escalated to the Founder.

## Phase 4: Decision rules
| Situation | Outcome |
|---|---|
| 5 × GO | Gate passes, pending Founder sign-off |
| Any GO-WITH-CONDITIONS, no NO-GO | Passes; conditions become first items of next milestone and are checked at the next gate |
| NO-GO from Assurance | **Blocked.** Only the Founder can override, with an ADR stating why |
| NO-GO from another position, inside its veto domain | Blocked unless the Founder overrides with an ADR |
| NO-GO outside the position's veto domain | Recorded as dissent; does not block |
| Kill criterion of the milestone triggered | Gate converts into a **pivot/kill review**: Product writes options, Founder decides |

## Phase 5: Record and seal
`gates/Mx/gate-record.md` (template `templates/GATE_RECORD.md`) records: verdicts, conditions,
overrides, dissent predictions, Founder signature line, final tag `gate-Mx-passed`.
Assurance then updates `state/RISK_REGISTER.md`, Product updates `state/ROADMAP.md`, and the Operator updates STATE.md.

## Anti-patterns that invalidate a gate
- A reviewer read another review before writing its own.
- A criterion marked passed with E0/E1 evidence where E2+ was required.
- The held-out set was used before the gate (check `data/heldout/ACCESS_LOG.md`).
- Thresholds in a locked preregistration differ from those used in the evidence pack.
