---
description: Write a 10-field brief and dispatch it to a position
argument-hint: <position> <task>
---
Task: $ARGUMENTS
1. Classify the task (as in /classify). If T0, just do it and log it.
2. Pick the next handoff id `H-<NNNN>` (highest in `company/handoffs/` + 1).
3. Write `company/handoffs/H-<NNNN>-brief.md` from `company/templates/BRIEF.md`, filling all 10 fields with exact file paths. Leave no field empty.
4. Dispatch to the named position's subagent with: "Execute brief company/handoffs/H-<NNNN>-brief.md".
5. When the return arrives: if T2+, dispatch `assurance-lead` with "Review H-<NNNN> per SOP-A1". Do not merge or mark done before the review verdict.
6. Update `company/state/STATE.md` "Now" table.
