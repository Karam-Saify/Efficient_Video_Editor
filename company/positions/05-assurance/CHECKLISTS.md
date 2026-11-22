# Checklists: Quality, Validation & Risk

## T2 review (DO-CONFIRM)
- [ ] Reproduced from clean state; output saved
- [ ] Every Done-when item independently verified
- [ ] Verification ladder levels L1–L7 applied where relevant
- [ ] ≥ 3 adversarial attempts recorded
- [ ] Invariants I-1…I-10 scanned
- [ ] Findings numbered with severity, evidence, required action
- [ ] Verdict written before reading the builder's confidence statement

## Gate checklist (blind)
- [ ] Evidence pack complete; every exit criterion reproduced by Assurance
- [ ] Held-out run done (M3+), logged in ACCESS_LOG
- [ ] No locked file was modified (git log check on `company/experiments/`, accepted ADRs, CONSTITUTION)
- [ ] All findings from this milestone closed (FIX / WONTFIX+reason / DEFER+ticket)
- [ ] Zero unmitigated Sev-1 risks; register re-scored
- [ ] Rights register covers every asset used
- [ ] Commit-trailer audit clean
- [ ] Operating-health metrics in METRICS.md computed
- [ ] Previous gate's dissent predictions checked in CALIBRATION.md
- [ ] Top 3 risks for next milestone · one checkable prediction

## Pre-mortem prompt (Assurance perspective)
"We shipped something wrong, lost data, or got a strike, and nobody noticed in time. How?" List ≤ 7 ways.
