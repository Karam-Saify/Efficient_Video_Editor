# Work log: 05-assurance
<!-- Append-only. Newest at bottom. Format: company/templates/LOG_ENTRY.md. Read the last 20 lines before starting any task (FM-1.3). -->

### 2026-11-21 · SETUP · T2 · DONE
- Did: position created with charter, playbook, checklists.
- Evidence: company/positions/05-assurance/
- Learned: —
- Next: contribute to M0 pre-mortem.

### 2026-11-22 · H-0002 · T1 · DONE
- Did: recorded RR-001 Noto Sans Arabic as SIL OFL 1.1 (v2.005, commercial use yes); added RR-006..RR-009 (G-C01..04 clips) and RR-010 (quarantined zip) as UNVERIFIED – source unknown, not usable. Media listed by name only.
- Evidence: company/positions/05-assurance/DATA_RIGHTS.md; embedded name table ID 13/14 + /usr/share/doc/fonts-noto-core/copyright; company/handoffs/H-0002-return.md
- Learned: fontTools/otfinfo are not installed; fc-query doesn't show the license, so a stdlib name-table parser is needed. Derived cache artifacts inherit the rights status of their source.
- Next: Founder proof of origin (RR-006..010); Creative to put RR IDs in MANIFEST; Amiri needs a row before use.

### 2026-11-22 · H-0003-review · T2 · DONE
- Did: independent T2 review of Task A (commit 5b2b39e). Clean `git archive` extract: ruff clean and 31/31 tests on fresh 3.14.2 and isolated 3.11.18 venvs; ran all 7 stages twice (done→skip) plus rerun triggers; 14 adversarial attempts; invariant, custody and secrets scan; CI run 45045075352 green on 3.11. Verdict APPROVE WITH FINDINGS (S1:0, S2:3, S3:7).
- Evidence: company/handoffs/H-0003-review.md; company/handoffs/H-0003-repro.txt
- Learned: python3.12 here lacks ensurepip; conda (/opt/conda) can provide an isolated 3.11 for floor checks. Check per-pin wheel availability including transitive deps: the builder checked direct deps only and missed av, orloge and cpsat-logutils. No data/heldout access, so no ACCESS_LOG entry.
- Next: owner responses to F1–F10; re-verify F1/F3/F4/F6 when fixed; Founder decides Python floor (Q1); RR-002 verification before first real ingest (F9).
