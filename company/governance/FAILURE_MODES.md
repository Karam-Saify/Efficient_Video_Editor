# Failure Modes and Countermeasures

Source: Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST, NeurIPS 2025 Datasets & Benchmarks;
arXiv 2503.13657). They analysed 7 multi-agent frameworks across 200+ tasks, found 14 failure modes in
3 categories, and observed failure rates up to 66–87% in popular systems such as ChatDev and MetaGPT.
The prevalence column is the share of observed failures in their data. Their key finding: simple
prompt tweaks give inconsistent gains; **structural** fixes (verification, explicit termination,
clear authority, state management) are what matter. Every fix below is structural.

| MAST ID | Failure mode | Prevalence | Our structural countermeasure | Where enforced |
|---|---|---|---|---|
| FM-1.1 | Disobey task specification | 11.8% | 10-field Brief; "Done when" checkboxes; Assurance checks return against brief | `OPERATING_MODEL.md` §3, `templates/BRIEF.md` |
| FM-1.2 | Disobey role specification | 1.5% | Veto domains and "may NOT" lists; tool restrictions per agent | `DECISION_RIGHTS.md` §3, `.claude/agents/*.md` |
| FM-1.3 | Step repetition | 15.7% | Read last 20 LOG lines before starting; max 2 retries; tool-call budgets | `OPERATING_MODEL.md` §5 |
| FM-1.4 | Loss of conversation history | 2.8% | Everything in files; STATE.md injected at session start; returns written to disk | I-8, SessionStart hook |
| FM-1.5 | Unaware of termination conditions | 12.4% | Mandatory "Termination condition" brief field; exit criteria per milestone | Brief field 10, `ROADMAP.md` |
| FM-2.1 | Conversation reset | 2.2% | Fresh-context agents receive full brief + file paths, never "continue from before" | Brief fields 3 and 5 |
| FM-2.2 | Fail to ask for clarification | 6.8% | `STATUS: ESCALATE` is a legitimate, encouraged outcome; "Escalate if" field | Return contract |
| FM-2.3 | Task derailment | 7.4% | "Out of scope" field; tier escalation rule | Brief field 7; `OPERATING_MODEL.md` §1 |
| FM-2.4 | Information withholding | 0.85% | Return contract lists DEVIATIONS and OPEN QUESTIONS explicitly | Return contract |
| FM-2.5 | Ignored other agent's input | 1.9% | Every Assurance finding needs FIX / WONTFIX+reason / DEFER+ticket | `RACI.md` interfaces |
| FM-2.6 | Reasoning–action mismatch | 13.2% | Invariant I-1: claims must cite artifacts; Assurance re-runs commands | Constitution I-1, Assurance playbook |
| FM-3.1 | Premature termination | 6.2% | DoD checklists; PARTIAL status allowed and preferred over false DONE | Position `CHECKLISTS.md` |
| FM-3.2 | No or incomplete verification | 8.2% | Builder ≠ verifier (I-2); multi-level verification: unit → schema → render → rubric → held-out | Assurance playbook §2 |
| FM-3.3 | Incorrect verification | 9.1% | Assurance verifies by **reproduction**, not by reading; blind gate reviews; dissent calibration | `GATE_PROTOCOL.md` |

## Additional failure modes specific to this company
| ID | Failure mode | Countermeasure |
|---|---|---|
| VC-1 | Overfitting the pipeline to the golden set | Held-out set locked by Assurance, used only at gates (I-6) |
| VC-2 | Silent Arabic degradation (wrong dialect words, broken RTL, disconnected letters) | Creative owns an Arabic correctness checklist; render screenshots checked at every T2 touching captions |
| VC-3 | Cost creep (tokens per Short grows unnoticed) | Per-call token logging; budget in `METRICS.md`; Assurance audit per milestone |
| VC-4 | Copyright / platform-policy strike | Data-rights register; every asset has a source and license before entering `samples/` or `data/` |
| VC-5 | Confusing "it rendered" with "it is good" | Two separate gates per output: technical validity (Eng/Assurance) and viewer quality (Creative rubric) |
| VC-6 | Founder bottleneck / bus factor | Every decision and its reasoning is in ADRs; RECOVERY.md lets any new session resume |
| VC-7 | Model or tool updates silently change outputs | Pin versions; record model IDs in run metadata; regression run on golden set after any upgrade |
| VC-8 | Agent sycophancy (agreeing with the Founder or another agent without evidence) | Blind reviews; vetoes must cite evidence; Assurance's charter rewards finding problems |
