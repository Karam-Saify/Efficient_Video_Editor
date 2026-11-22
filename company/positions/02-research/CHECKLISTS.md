# Checklists: Research & Evidence

## Before locking a preregistration (DO-CONFIRM)
- [ ] The decision this result feeds is written down
- [ ] H1 and H0 are falsifiable
- [ ] Every metric has a formula and a numeric pass threshold and kill threshold
- [ ] Dataset IDs listed; held-out NOT used
- [ ] Controlled variables include model versions and seeds
- [ ] Threats to validity listed with mitigations
- [ ] Engineering confirmed instrumentation; Creative confirmed the quality metric; Assurance confirmed verifiability

## Before declaring a result (DO-CONFIRM)
- [ ] Ran exactly the locked procedure; deviations listed
- [ ] Environment recorded (versions, model IDs, hardware)
- [ ] Each metric reported against its threshold: pass / kill / neither
- [ ] Evidence level assigned; downgraded if deviations affect validity
- [ ] ASSUMPTIONS.md updated
- [ ] Sent to Assurance for verification

## Gate checklist (blind)
- [ ] Every gate claim meets its required evidence level (DECISION_RIGHTS §4)
- [ ] No locked preregistration was edited (check git history of `company/experiments/`)
- [ ] Every experiment of this milestone has a results file, including failed ones
- [ ] Assumptions tested this milestone have updated statuses
- [ ] Held-out results (M3+) are consistent with golden results, or the gap is explained
- [ ] Open research questions for the next milestone listed with database + keywords
- [ ] Top 3 risks for next milestone · one checkable prediction

## Pre-mortem prompt (Research perspective)
"We failed because we believed something that wasn't true." List ≤ 7 beliefs we have not tested yet.
