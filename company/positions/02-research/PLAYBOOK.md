# Playbook: Research & Evidence

## SOP-R1: Literature question (T1, or T2 if it feeds a decision)
1. Write the question and the decision it feeds at the top of `SEARCH_LOG.md`.
2. **Start broad, then narrow** (Anthropic's research-agent lesson): 2–3 short queries first, judge the
   landscape, then specific queries. Max 12 sources per question at T2.
3. Search order: arXiv (open) → ACM DL / IEEE Xplore / Scopus lists provided by the Founder → official docs.
4. Log every query: database · query string · date · hits · selected IDs.
5. For each selected paper, add an `EVIDENCE_LIBRARY.md` entry (format below). Read the method,
   results and limitations sections; the abstract alone is never enough.
6. Ask the Founder for PDFs only when needed: list title, DOI, which section matters and why.
7. Conclude with: answer · evidence level · confidence · what remains unknown · recommended experiment.

### Evidence library entry format
```
## <Short name> (<venue year>) · DOI
- Claim relevant to us:
- Setting (data, language, model, hardware): ← compare to ours
- Method in 3 lines:
- Key numbers (with table/figure reference):
- Limitations stated by authors:
- Transferability to Arabic Shorts: High/Med/Low + why
- What we adopt / reject:
```

## SOP-R2: Designing and locking an experiment (T2)
1. Copy `templates/EXPERIMENT.md` → `company/experiments/EXP-<NNN>.md`.
2. Fill every section. Thresholds must be numbers. Sample size must be justified, even if small: state
   the smallest effect that would change the decision.
3. Consult: Engineering (can it be instrumented?), Creative (is the quality metric valid?), Assurance (is it verifiable?).
4. Set `Lock: LOCKED`, commit with `Tier: T2`. From now on the hook blocks edits. Any change = a new EXP id that references the old one.
5. Exploration runs go under `experiments/explore/`; only locked confirm runs count.

## SOP-R3: Analysis and conclusion
1. Run exactly the preregistered procedure. Record environment: package versions, model IDs, seeds, hardware.
2. Write `EXP-<NNN>-results.md`: each preregistered metric → value → pass/kill/neither.
3. Deviations from the protocol are listed, never hidden. If a deviation affects validity, the result is downgraded one evidence level.
4. Update `ASSUMPTIONS.md` status and evidence path.
5. Hand to Assurance for verification (T2 review) before anyone uses the conclusion.

## SOP-R4: Human-rating studies (with Creative)
- Raters see outputs in **random order with labels hidden** (blinding is set up by Assurance).
- Minimum 2 raters (Founder + creative-lead's rubric pass, or 2 humans). Compute agreement
  (Cohen's kappa for categorical, Spearman for ordinal 1–5). If agreement is below 0.4, fix the rubric before trusting results.

## Planned experiment register
| ID | Question | Milestone |
|---|---|---|
| EXP-001 | Arabic ASR quality (WER, timestamp drift) across ≥ 2 models | M1 |
| EXP-002 | Transcript-only vs transcript + visual captions | M3 |
| EXP-003 | Timeline JSON validity rate from the LLM | M4 |
| EXP-004 | LLM-scored + MILP selection vs no-LLM baseline | M3 |
| EXP-005 | Cost per Short by stage | M3 |
| EXP-006 | Arabic caption rendering correctness: FFmpeg/libass vs Remotion | M1 |
| EXP-007 | Revision diff size and tokens | M4 |
