# Operating Model

How work flows. The Operator (main Claude Code session) follows this file literally.
Design basis: ITIL change classes (standard / normal / emergency), Bezos's one-way vs two-way
doors, Anthropic's lessons on orchestrator-worker agents, and the MAST failure taxonomy
(see `governance/FAILURE_MODES.md`).

---

## 1. Work tiers: classify every request before doing anything

| Tier | Name | Typical examples | Who is involved | Review required | Record |
|---|---|---|---|---|---|
| **T0** | Trivial | Typo, comment, formatting, renaming a local variable | Operator or any position | None | One line in owner's `LOG.md` |
| **T1** | Standard | A function inside an approved design; a unit test; a doc section; a literature search; tagging 10 clips | 1 owner position | Owner runs their Definition of Done (DoD); Assurance samples 1 in 5 T1 items per milestone | `LOG.md` entry with evidence |
| **T2** | Significant | New module or stage; schema change; new dependency; running an experiment; changing a prompt used in the pipeline; anything touching ≥2 positions' artifacts | Owner + every position listed as C in `governance/RACI.md` | **Assurance review mandatory** before merge | Brief + Return in `handoffs/`; ADR if any decision was made |
| **T3** | Milestone gate | Closing M0…M6; changing the roadmap; pivot; publishing to real audiences | **All five positions + Founder** | Full gate protocol (`governance/GATE_PROTOCOL.md`) | Gate record in `gates/Mx/` |
| **E** | Emergency | Main branch broken; data at risk; secret leaked; budget overrun >50% | Engineering acts immediately; Assurance informed | Postmortem within next session | `incidents/INC-xxxx.md` |

### Classification rules (apply in order, stop at first match)
1. Could it lose data, leak a secret, or break `main`? → **E** if happening now, else at least **T2**.
2. Is it irreversible or expensive to reverse (a one-way door)? Examples: public release, data deletion,
   license choice, choice of core timeline format, publishing to a channel. → **T3** or Founder approval.
3. Does it change an interface that another position depends on (schema, CLI contract, rubric, golden set)? → **T2**.
4. Does it produce a claim that will be used in a decision? → **T2** (it needs independent verification).
5. Is it inside an already-approved brief and reversible in minutes? → **T1**.
6. Otherwise → **T0**.
7. **Uncertain? Go one tier up** (Constitution I-10).

### Tier escalation mid-task
If a T1 task turns out to need a schema change, a new dependency or a decision, the owner **stops**,
returns with `STATUS: ESCALATE`, and the Operator re-briefs as T2. Never silently grow scope.

---

## 2. Lifecycle of a unit of work

```
REQUEST → CLASSIFY → BRIEF → EXECUTE → RETURN → VERIFY → INTEGRATE → RECORD
   │          │          │        │         │         │          │          │
 Founder   Operator   Operator  Owner    Owner   Assurance   Engineering  Operator
 or plan   (tier)     (brief)  position  (return  (T2+) /    (merge,     (STATE,
                                         contract) owner DoD   commit)    LOG, ADR)
                                                   (T1)
```

---

## 3. The Brief: every delegation uses this shape
Anthropic found that short delegation prompts ("research X") caused duplicated work, gaps and
misread tasks. Every brief from the Operator to a position contains all of the following; missing
fields mean the brief is invalid. Template: `templates/BRIEF.md`.

1. **Objective**: one sentence, with the *why* attached.
2. **Tier and milestone**, e.g. T2, M1.
3. **Inputs**: exact file paths. Never paraphrase a file; point to it.
4. **Constraints**: invariants that apply, budget, tools allowed or forbidden.
5. **Output**: exact format and exact path where it must be written.
6. **Done when**: verifiable acceptance criteria, as checkboxes.
7. **Out of scope**: what *not* to touch, to prevent derailment (MAST FM-2.3).
8. **Effort budget**: max tool calls and max retries (see §5).
9. **Escalate if**: the specific conditions that must stop the work and return.
10. **Termination condition**: the exact state at which the agent must stop (MAST FM-1.5).

## 4. The Return: every position answers in this shape
Written to `handoffs/<id>-return.md`. The chat reply is only a ≤10-line pointer to that file.
This avoids the "game of telephone", where information degrades as it passes through the coordinator.

```
STATUS: DONE | PARTIAL | BLOCKED | ESCALATE
SUMMARY: ≤5 lines
ARTIFACTS: paths created/changed
EVIDENCE: commands run + their outputs, metric files, test results (paths)
DEVIATIONS FROM BRIEF: none | list + why
OPEN QUESTIONS: numbered, each with who should answer
CONFIDENCE: High | Medium | Low, with the single biggest reason for doubt
NEXT RECOMMENDED STEP: one line
```

---

## 5. Effort budgets (prevents step repetition and endless search, MAST FM-1.3)
| Tier | Max tool calls per brief | Max retries of the same failing action | Max literature sources per question |
|---|---|---|---|
| T0 | 5 | 1 | n/a |
| T1 | 25 | 2 | 5 |
| T2 | 60 | 2 | 12 |
| T3 | No cap, but each position's review ≤ 40 | 2 | n/a |

After 2 failed retries of the same action: stop, write what was tried in the return, `STATUS: BLOCKED`.
Before starting any task, the owner reads the last 20 lines of its own `LOG.md` to avoid redoing work.

---

## 6. Session protocol (Operator)
**Start** (`/start`):
1. Read `company/state/STATE.md` (the SessionStart hook prints it automatically).
2. `git status` and `git log --oneline -10`. If the working tree is dirty and unexplained, it is a recovery case → `company/RECOVERY.md`.
3. State today's goal in one sentence and its tier. Confirm with the Founder if it is T3.

**During**:
- One active T2 at a time per position. Parallel work is allowed only across different positions with non-overlapping file scopes.
- Commit after every completed T1/T2 with trailer lines: `Role: <position>` and `Tier: T<n>`.

**Close** (`/close`):
1. Update `STATE.md`: what changed, what is next, blockers, open decisions.
2. Append to each active position's `LOG.md`.
3. Commit with message `chore(state): session close <date>`, then `git push`. **A session is not closed until pushed** (I-8).

---

## 7. Escalation ladder
1. Owner position resolves within its decision rights (`governance/DECISION_RIGHTS.md`).
2. Disagreement between two positions → each writes a ≤10-line position statement in the handoff → **Product** arbitrates, unless the dispute falls inside another position's veto domain.
3. Veto invoked → Founder decides. Overriding a veto requires a written reason in an ADR.
4. **Andon rule (stop the line):** any position may halt all work by writing `HALT: <reason>` at the top of
   `STATE.md` if it sees data loss, an invariant breach or a legal/rights risk. Only the Founder clears a HALT.

## 8. Cadence
| Rhythm | What | Output |
|---|---|---|
| Every session | Start/close protocol | STATE.md, LOG entries, push |
| Every T2 | Brief → Return → Assurance review | `handoffs/` |
| Start of each milestone | **Pre-mortem**: all five imagine the milestone failed and write why (Gary Klein's method) | `gates/Mx/premortem.md` → new risks |
| End of each milestone | Gate review (T3) | `gates/Mx/gate-record.md` |
| Every incident | Blameless postmortem (Google SRE style) | `incidents/` |
| Every 2 milestones | Retrospective on the operating model itself; amendments via ADR | ADR |
