# EXP-<NNN>: <title>
- **Lock:** DRAFT  <!-- change to LOCKED before running; a hook then blocks edits. Results go in EXP-<NNN>-results.md -->
- **Owner:** research-lead · **Milestone:** · **Linked assumption(s):** A-xx · **Decision it feeds:**

## 0. Decision brief (ADR-0012; fill first, ≤ 10 lines)
- **Recommendation:** what we should do
- **Reasoning:** why, with evidence level
- **First experiment:** the smallest test that could change the recommendation
- **Success threshold (numeric):** e.g. "≥ 60 % of blind picks", "≤ $0.01 / video"
- **If it fails, then:** the pre-committed next action

## 1. Question
## 2. Hypothesis (falsifiable)
H1: … H0: …
## 3. Variables
- Independent (what we change):
- Dependent (what we measure, with formula):
- Controlled (held constant, incl. model versions, seeds, hardware):
## 4. Dataset
Which golden-set items (IDs). Held-out used? (only at gate, by Assurance)
## 5. Procedure (numbered, reproducible commands)
## 6. Metrics and thresholds (set NOW, never changed after)
| Metric | Threshold for "pass" | Threshold for "kill" |
|---|---|---|
## 7. Analysis plan
Statistic, sample size rationale, how ties/outliers are handled.
## 8. Threats to validity
Internal / external / construct, and mitigation.
## 9. Budget
Max tool calls, max compute minutes, max tokens.
## 10. Roles
Research (design/analysis) · Engineering (instrumentation) · Creative (human ratings, blinding) · Assurance (lock + verification)
