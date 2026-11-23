# RACI Matrix

R = Responsible (does the work) · A = Accountable (one per row; signs off) · C = Consulted (must be asked
*before*, two-way) · I = Informed (told *after*). F = Founder.
Rule: exactly one **A** per row. If a row seems to need two A's, split the row.

| # | Activity / artifact | Product | Research | Engineering | Creative | Assurance | F |
|---|---|---|---|---|---|---|---|
| 1 | Vision, mission, Constitution | C | C | C | C | C | **A/R** |
| 2 | Roadmap and milestone definitions (`state/ROADMAP.md`) | **A/R** | C | C | C | C | I (approves at T3) |
| 3 | Milestone scope: what enters / leaves | **A/R** | C | C | C | C | I |
| 4 | Target-user definition, personas, jobs-to-be-done | **A/R** | C | I | C | I | I |
| 5 | Unit economics (cost per Short, pricing hypotheses) | **A/R** | C | C (cost data) | I | C (audit) | I |
| 6 | Competitive landscape | **A/R** | R (evidence) | I | C | I | I |
| 7 | Literature reviews, evidence briefs | C | **A/R** | C | C | I | I |
| 8 | Hypotheses and experiment preregistration | C | **A/R** | C (feasibility) | C (quality metric) | C (lock) | I |
| 9 | Running experiments | I | **A** | R (code/infra) | R (human ratings) | I | I |
| 10 | Experiment analysis and conclusion | I | **A/R** | C | C | C (verify) | I |
| 11 | System architecture, ADRs (technical) | C | C | **A/R** | I | C | I |
| 12 | Timeline schema (`schemas/timeline.schema.json`) | C | C | **A/R** | C (must express style needs) | C | I |
| 13 | Pipeline code, tests, CI | I | I | **A/R** | I | C (review) | — |
| 14 | Prompts used inside the pipeline | C | C (eval) | **A/R** | C (tone/language) | C | — |
| 15 | Dependency / model / tool selection | I | C (evidence) | **A/R** | C (if output-visible) | C (license) | I |
| 16 | Cost and token telemetry | I | I | **R** | I | **A** (audit) | I |
| 17 | Quality rubric for Shorts | C | C (validity) | I | **A/R** | C | I |
| 18 | Golden set curation (`data/golden/`) | C | C (sampling) | I | **A/R** | C (rights) | I |
| 19 | Held-out set (`data/heldout/`) | I | C | I | R (curate once) | **A** (lock & custody) | I |
| 20 | Arabic language, dialect and caption correctness | I | I | C | **A/R** | I | — |
| 21 | Style guide (captions, fonts, motion, pacing) | C | C | C | **A/R** | I | I |
| 22 | Human evaluation sessions (rating outputs) | I | C (protocol) | I | **A/R** | C (blinding) | R (rater) |
| 23 | Data rights register (footage, music, fonts, models) | C | I | C | R | **A** | I |
| 24 | Risk register | C | C | C | C | **A/R** | I |
| 25 | T2 independent review | — | — | — | — | **A/R** | — |
| 26 | Milestone gate facilitation and record | R (vote) | R (vote) | R (vote) | R (vote) | **A/R** (vote + record) | Final sign-off |
| 27 | Release / publish to a real channel | R | C | R | R | C (veto) | **A** |
| 28 | Incidents and postmortems | I | I | R | I | **A** | I |
| 29 | STATE.md upkeep | — | — | — | — | C (audits) | Operator = R |
| 30 | Operating model changes | R (proposes) | C | C | C | C | **A** |

## Interfaces: "contracts" between positions
| From → To | What is handed over | Acceptance condition |
|---|---|---|
| Product → Research | Question to answer + decision it will feed + deadline | Research confirms the question is answerable with evidence ≤ E2 at the stated budget |
| Research → Engineering | Locked preregistration + required instrumentation | Engineering confirms metric is computable and logs exist |
| Creative → Engineering | Style requirement expressed as schema fields | Engineering confirms the schema can express it, or opens an ADR |
| Engineering → Assurance | PR/diff + test output + reproduction command | Assurance can reproduce from a clean checkout |
| Creative → Research | Human ratings in `experiments/EXP-x/ratings.csv` | Inter-rater check passes (see Creative playbook) |
| Assurance → All | Review verdict with numbered findings | Each finding gets FIX / WONTFIX(+reason) / DEFER(+ticket) |
| Any → Product | Scope change request | Written impact on milestone date and kill criteria |
