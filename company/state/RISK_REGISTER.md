# Risk Register
Owner: Assurance (A). Every position may add risks. Score = Likelihood (1–5) × Impact (1–5).
Sev-1 = score ≥ 15 (gate-blocking if unmitigated) · Sev-2 = 8–14 · Sev-3 = ≤ 7.
"Trigger" = observable signal that the risk is materialising. Review at every gate.

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger | Status |
|---|---|---|---|---|---|---|---|---|
| R-01 | Whisper-class ASR performs poorly on Lebanese dialect / code-switching | 4 | 5 | 20 | Research | EXP-001 early in M1; compare ≥ 2 models; fallback: manual transcript import | WER above prereg threshold | Open |
| R-02 | Arabic caption rendering breaks (letter shaping, RTL, mixed digits) | 3 | 5 | 15 | Engineering | EXP-006 in M1; test strings set by Creative; HarfBuzz-backed renderer | Any disconnected letter in screenshot | Open |
| R-03 | LLM writes invalid timelines (hallucinated clips, out-of-bounds times) | 4 | 4 | 16 | Engineering | Schema + validator + bounded retry (EditDuet failure data) | Validator failure rate > 10% | Open |
| R-04 | Overfitting to the golden set | 3 | 4 | 12 | Assurance | Held-out set sealed; access log | Held-out score ≪ golden score | Open |
| R-05 | Copyright or platform policy strike (footage, music, fonts, reused content) | 3 | 5 | 15 | Assurance | Data-rights register; only owned/licensed assets; AI disclosure | Any asset without a recorded license | Open |
| R-06 | Codespace compute / free-hours insufficient for ASR and render | 4 | 3 | 12 | Engineering | int8/turbo models, short clips, local PC fallback for heavy stages | Ingest of a 5-min clip > 10 min | Open |
| R-07 | Token cost per Short grows unnoticed | 3 | 3 | 9 | Assurance | Usage logging per call; budget in METRICS | Cost per Short > 1.5× budget | Open |
| R-08 | Loss of work / state (uncommitted, unpushed, context lost) | 3 | 5 | 15 | Operator | I-8, /close, RECOVERY.md, push every session | Session ends with unpushed commits | Open |
| R-09 | Agent drift: positions exceed their role or self-approve | 3 | 4 | 12 | Assurance | Veto domains, builder≠verifier, commit trailers audited | Commit by a role outside its RACI | Open |
| R-10 | Quality rubric does not reflect real audience preference | 3 | 5 | 15 | Creative | Calibrate against real metrics at M5; refine rubric | Rubric score uncorrelated with retention | Open |
| R-11 | Scope creep (montage, music, avatars all at once) | 4 | 3 | 12 | Product | Milestone scope lock; scope change needs written impact | > 2 scope changes per milestone | Open |
| R-12 | Single founder time / bus factor | 4 | 4 | 16 | Product | Everything in repo; sessions resumable; small milestones | No session for 14 days | Open |
| R-13 | Tool / model version changes alter outputs silently | 3 | 3 | 9 | Engineering | Pin versions; record model IDs in run metadata; regression on golden set | Golden score shifts without code change | Open |
| R-14 | Competitors (CapCut, Descript, OpusClip) ship the same at low price | 3 | 4 | 12 | Product | Differentiate on Arabic quality and cost; track competitor log | Competitor launches Arabic auto-edit | Open |
| R-15 | Secrets leaked (API keys, tokens in repo) | 2 | 5 | 10 | Engineering | `.gitignore`, hook blocking `.env` commits, secret scan in CI | Secret scanner hit | Open |
