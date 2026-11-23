# Checklists: Engineering

## DoD for any T1/T2 code change (DO-CONFIRM)
- [ ] Tests written first and passing locally; CI green
- [ ] Schema / fixtures / validator updated first if any interface changed
- [ ] No raw video or frames sent to an LLM; no LLM arithmetic on time (I-3, I-4)
- [ ] Versions pinned; new dependency has an intake record (SOP-E3)
- [ ] Stage writes a manifest with hashes; determinism check (run twice → identical outputs) passes
- [ ] Tokens and minutes impact measured and stated
- [ ] One-line reproduction command in the RETURN
- [ ] No secrets in diff (`git diff | grep -iE "key|token|secret"` reviewed)

## Gate checklist (blind)
- [ ] Assurance reproduced every exit criterion from a clean checkout with documented commands
- [ ] `main` green; tag candidate created
- [ ] All pipeline LLM calls have validators, retry caps and usage logging
- [ ] ADRs exist for every architecture decision made this milestone
- [ ] Performance: runtime and tokens per stage recorded in METRICS.md
- [ ] Known tech debt listed with a risk score
- [ ] Top 3 risks for next milestone · one checkable prediction

## Pre-mortem prompt (Engineering perspective)
"We failed because the system broke, couldn't be reproduced, or was too slow or expensive." List ≤ 7 ways.
