---
description: Run a milestone gate review (T3), all five positions + Founder sign-off
argument-hint: <milestone, e.g. M0>
---
Run the gate for $ARGUMENTS exactly per `company/governance/GATE_PROTOCOL.md`:
1. Check the preconditions. If any fails, stop and list what is missing.
2. Dispatch assurance-lead to build `company/gates/$ARGUMENTS/evidence-pack.md` and reproduce every exit criterion (held-out run only from M3).
3. Dispatch all five positions **separately and in fresh contexts** to write `company/gates/$ARGUMENTS/review-<position>.md` from the evidence pack + their own gate checklist. They must not read each other's reviews.
4. Write `synthesis.md`, run at most 2 challenge rounds per contradiction, then apply the Phase 4 decision rules.
5. assurance-lead writes `gate-record.md` from `company/templates/GATE_RECORD.md`. Present it to the Founder for sign-off. Do not tag `gate-$ARGUMENTS-passed` before the Founder signs.
