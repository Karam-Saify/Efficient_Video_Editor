# Decision Rights

Two lenses decide who may decide: **reversibility** (one-way vs two-way door) and **domain** (whose
question is it). The roles in a decision follow Bain's RAPID model: Recommend, Agree (veto), Perform,
Input, Decide.

## 1. Door types
| Door | Definition | Test question | Who decides | Record |
|---|---|---|---|---|
| Two-way | Reversible in < 1 day with no data loss and no external effect | "If wrong, can we undo it before the next session ends?" | The owning position | LOG entry (T1) or ADR (T2) |
| One-way | Irreversible, external, or expensive to reverse | "Would undoing this require apology, migration, or money?" | Founder, after a recommendation from the owner and Agree from the veto-holders | ADR, Status: Accepted only after Founder sign-off |

One-way examples in this company: publishing content publicly; choosing the canonical timeline
format after M2; deleting any dataset; adopting a paid service; accepting someone else's footage
or music; changing the target market; open-sourcing code; anything involving a contract or money.

## 2. RAPID per decision class
| Decision class | Recommend | Agree (veto) | Perform | Input | Decide |
|---|---|---|---|---|---|
| Milestone scope | Product | Assurance (testability) | All | Research, Eng, Creative | Product (two-way) / Founder (roadmap change) |
| Architecture / tech choice | Engineering | Assurance (security, license) | Engineering | Research, Creative | Engineering (two-way) / Founder (one-way) |
| Experiment design | Research | Assurance (lock), Creative (if quality metric) | Research + Eng + Creative | Product | Research |
| Conclusion from evidence | Research | Assurance (verification) | — | Creative, Eng | Research |
| Quality bar / rubric | Creative | Research (measurement validity) | Creative | Product | Creative |
| Gate pass | Assurance (record) | **Every position** (each may NO-GO in its veto domain) | All | — | Founder |
| Release / publish | Product | Assurance, Creative | Eng | Research | Founder |
| Spending money | Product | Assurance | — | Eng | Founder |

## 3. Veto domains: a veto is valid only inside its domain
| Position | May veto when… | May NOT veto… |
|---|---|---|
| Product | Work does not trace to a milestone goal or user need; scope creep | Technical approach; evidence validity |
| Research | Evidence is below the level the decision needs; design is confounded; threshold moved after results | Product priorities; taste |
| Engineering | Not reproducible; breaks invariants I-3/I-4; security; unmaintainable | Which feature matters more |
| Creative | Output below rubric bar on golden set; Arabic language errors; style-guide breach | Architecture; schedule |
| Assurance | Any claim unverified; any invariant breached; any open Sev-1 risk without mitigation; rights unclear | Nothing is outside its domain at a gate, but it must cite evidence for every NO-GO |

A veto must cite: (a) the domain clause above, (b) evidence path, (c) what would lift it.
A veto without all three is a comment, not a veto.

## 4. Evidence levels required per decision
| Level | Meaning | Example |
|---|---|---|
| E0 | Opinion, intuition, a model's assertion | "Whisper should be fine for Lebanese." |
| E1 | Single observation or demo | One clip transcribed well |
| E2 | Measured on the **golden set** against a **preregistered** metric | WER 14% on 5 golden clips, prereg EXP-001 |
| E3 | E2 replicated on the **held-out set** | WER 15% on held-out |
| E4 | Real-world outcome | Retention of 10 published Shorts vs channel baseline |

| Decision | Minimum evidence |
|---|---|
| T1 inside approved brief | E0 + DoD passed |
| T2 technical choice (two-way) | E1 |
| Adopting a component into the pipeline | E2 |
| Passing a milestone gate claim | E2, and E3 for M3+ claims of "better than baseline" |
| Any one-way door | E3, or explicit Founder waiver in the ADR |
| Pricing / market claims at M6 | E4 |

## 5. Disagree and commit
Dissent is written into the ADR's "Dissent" section with the dissenter's name and prediction.
At the next gate, Assurance checks dissent predictions against outcomes. This builds a calibration
record per position, so we learn whose judgment to weight in which domain.
