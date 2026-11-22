---
description: Run a milestone pre-mortem with all five positions
argument-hint: <milestone, e.g. M1>
---
Run a pre-mortem for $ARGUMENTS using `company/templates/PREMORTEM.md` → `company/gates/$ARGUMENTS/premortem.md`.
Dispatch each of the five positions **separately, in parallel, in fresh contexts**, each with: the milestone entry from `company/state/ROADMAP.md`, its own CHECKLISTS.md pre-mortem prompt, and the instruction to write ≤ 7 failure stories into its section without reading other sections.
Then dispatch assurance-lead to synthesise: cluster the stories, map each to new or existing risks in `company/state/RISK_REGISTER.md`, and assign mitigation owners.
