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

### 2026-11-22 · H-0008 · T1 · DONE
- Did: added RR-011 (Noto Sans Regular v2.004, sha256 89c3c497…909d, OFL 1.1 confirmed from embedded name table ID 13/14 and Debian copyright `Files: *`), the libass Latin fallback seen in EXP-006 render.log l.135-136. Evidence: company/handoffs/H-0008-return.md

### 2026-11-22 · H-0004-review · T2 · DONE
- Did: independent T2 review of Task B (commit 4c156d8). Clean `git archive` extract, fresh 3.14.2 venv: ruff check clean, 70/70 tests. Ran the CLI on all 10 fixtures (each invalid one gives exactly one different code; exit 0/1 correct). 21 adversarial timelines in scratch. Real L4 render with AR-05/AR-08 captions plus ffprobe. Invariant, custody and secret scan. CI run 45045645473 green on 3.11. Ruled rule 3 (same-source reuse) acceptable for v0 and the render adapter in scope. Verdict APPROVE WITH FINDINGS (S1:0, S2:4, S3:6).
- Evidence: company/handoffs/H-0004-review.md; company/handoffs/H-0004-repro.txt
- Learned: JSON Schema 2020-12 accepts 2000.0 as "integer", so integer-ms contracts need an explicit type(x) is int check (this one crashed the validator). Always do one real render: the dry-run tests missed that audio-less sources validate but fail in ffmpeg. No data/heldout access, so no ACCESS_LOG entry.
- Next: re-verify F1 (A1/A1b files) before merge, then F2 before M0. Tickets for F3/F4/F5/F7. Creative covers F6 and F10(iv) in H-0007.

### 2026-11-22 · TTI-intake · T2 · PARTIAL
- Did: recorded RR-012..RR-017 (TikTok Creative Center, Meta Ad Library, human-observed public URLs, IG Business Discovery/Hashtag Search, IG account connection, TikTok Display API) as pending, not usable, before first use. Terms not yet read from primary sources. Steps 1–2 (taxonomy, EXP-009, coding tool) are research/engineering work and not mine; T2 review pending their returns.
- Evidence: company/positions/05-assurance/DATA_RIGHTS.md rows RR-012..RR-017
- Learned: RR-014 (storing URLs and handles of third-party creators) is personal data; it needs a privacy assessment, not only platform ToS.
- Next: primary-source terms check for each row; T2 review of Step 2 coding tool once engineering returns.

### 2026-11-22 · H-0009-review · T2 · DONE
- Did: T2 re-review of fix pass c179693. Clean `git archive` export. Fresh 3.12.3 venv with the full lock + dev: pip check clean, one opencv, ruff clean, 116 passed. Fresh 3.14 venv with the dev lock: ruff clean, 108 passed + 8 skipped. New tests against the parent code fail. More than 30 adversarial attempts (float/bool/NaN/inf ms, 15 path shapes including symlinks and NUL, bad JSON, out-in-input, strace). L4 silent-source render with an AR caption. CI 45047570814: all 4 jobs green. Every H-0003/H-0004 finding confirmed FIX/DEFER/WONTFIX. Verdict ACCEPT WITH FIXES (S1:0, S2:1, S3:4). Task A mergeable; Task B mergeable after N1.
- Evidence: company/handoffs/H-0009-review.md; company/handoffs/H-0009-repro.txt
- Learned: a fix can add a new crash path (N1: `Path.resolve()` raises on NUL while `is_file()` swallows it), so every new rule needs the earlier adversarial set rerun. The policy hook blocks naming the held-out path in any command, even for a confinement test that never reads it; held-out confinement is verified by inspection outside gates. A grep of the return exposed the builder's CONFIDENCE line before the verdict: grep the return only after the verdict is written.
- Next: re-verify N1 (one row of adv.py); ADR-0004 for has_audio before M0 (N2); add the stage_version Done-when to Phase 1 briefs (N3).

### 2026-11-22 · H-0019 · T1 · DONE
- Did: re-scored all 15 risks and added R-16..R-25. These include the Founder-named R-16 (font fallback), R-18 (single AI judge), R-19 (shell-write hook bypass) and R-20 (false positives on quoted text), plus no footage, trend privacy, stale cache, has_audio, size mismatch and prereg feasibility. Added Was and Check columns. Every row has one owner position. None closed. Sev-1 count is 11.
- Evidence: company/state/RISK_REGISTER.md; company/handoffs/H-0019-return.md
- Learned: R-15's "secret scan in CI" mitigation does not exist (grep of the workflows: no match). A register mitigation is a claim and needs I-1 evidence like any other.
- Next: re-run the hook self-test with shell-write and quoted-text cases on the H-0020 return; verify RR-002 before the first real ingest.

### 2026-11-22 · H-0023-review · T2 · DONE
- Did: T2 review of Task C (EXP-006 INVALID, EXP-008 FAIL) plus N1 spot check. Lock history checked with `git log --follow`: both locks predate their render commits and nothing changed after them. EXP-008 rerun in a clean detached worktree of 43556ca (a `git archive` export fails on the instrument's git-status precondition): 26/26 PNG, .ass and check-txt hashes match the committed SHA256SUMS. Logs differ, which is non-invalidating. Controls and coverage confirmed, plus an independent log grep. 17 adversarial attempts. N1 closed (6 path cases give E_SOURCE_PATH, exit 1; 155 tests pass). Verdict ACCEPT WITH FINDINGS (S1:0, S2:4, S3:7). Founder combined verdict to be recorded as an appended, non-decisive §9 in EXP-008-results.md (F3).
- Evidence: company/handoffs/H-0023-review.md; company/handoffs/H-0023-repro.txt
- Learned: a rerun recipe that regenerates its own SHA256SUMS proves nothing. Always save the committed sums before rerunning. Self-slip: a non-gate command named the held-out path (`ls`, output discarded). This is self-reported as F11 and the Operator must record it in ACCESS_LOG. New personal check: never name that path outside gates.
- Next: add an RR row for NotoSansThai-Regular and update the RR-011 usage text (F8). Verify the Founder §9 append (F3) and the fixed rerun recipe (F1) before EXP-010 is locked.

### 2026-11-23 · H-0026-review · T2 (daily engine review, ADR-0006) · DONE
- Did: Reviewed H-0024 and H-0025 (85dca48..HEAD). Reproduced demo run 1 in a detached worktree with no cache, writing to a fresh out/h0026. Timeline and .ass are byte-identical to the original; the MP4 is not. ffprobe on all 4 demo outputs: within 1 frame, 1080x1920, 30/1. Checked 3 frames at times I chose from the caption tracks, all mid-zoom, plus the libass fontselect logs. Honesty checks: stubs exit 2 and leave no manifest, a stale manifest is deleted, UNSUPPORTED_FIELD fires, and 2 CAPABILITIES rows were checked against the renderer. Suite (266 passed, 8 skipped) and ruff clean in the worktree. 31 adversarial attempts, 7 of them on allow_dev paths. Ruled D1 accepted with F2, and set_duration on music acceptable for now (F3). Verdict ACCEPT WITH FINDINGS (S1:0, S2:1, S3:7).
- Evidence: company/handoffs/H-0026-review.md; company/handoffs/H-0026-repro.txt
- Learned: One matching rerun does not prove determinism. The same timeline rendered 4 times gave 4 different hashes (PSNR > 50 dB, audio identical), while the builder's single rerun matched by chance. Determinism checks need at least 3 renders, under load. The builder rated determinism High; this calibration miss goes to CALIBRATION. Output containers inherit source metadata (the platform video ID), so redact third-party IDs in repro logs.
- Next: Tomorrow's daily review reruns the 5-render determinism check (§C4) and the malformed ops.json cases (§L). Add a RISK/DATA_RIGHTS note on watermark cropping and the source-metadata leak (F8).

### 2026-11-23 · H-0033-review · T2 (daily review, ADR-0006) · DONE
- Did: Reviewed Week 1 A–D (511dbb7~1..e655739). Cost: recomputed the Download (1) row (6.363 m$), the median and P90 (7.986 / 11.087) and the per-success figures with my own script, which matched the doc and the code within 0.01 %. Ledger tests passed (17). Recipes: 2 cells byte-identical, the photos_to_video designed failure reproduced, R02 UNRENDERED complete, ffprobe of R01×D5 = 1050 frames / 35 s, 1 caption frame checked. Bench static read: pinned URLs, no uploads. RR-025 (JFK) added. Product consent checked against DATA_POLICY. Suite 404 passed, ruff clean in a clean worktree. 21 adversarial attempts. Verdict ACCEPT WITH FINDINGS (S1:0, S2:5, S3:8). Rulings: ADR-0014 accept-recommended with a condition (F13), JFK usable restricted, 90-day retention approved as a maximum with conditions and an ADR needed. ADR-0022 label dependencies listed (F4).
- Evidence: company/handoffs/H-0033-review.md; company/handoffs/H-0033-repro.txt; company/positions/05-assurance/DATA_RIGHTS.md RR-025
- Learned: a committed transcript in a smoke result looked like dev-derived text. A file-size match against quarantine/ and out/ proved it was a Whisper hallucination on the synthetic beep. Check provenance by size or hash before calling S1. Consent text that says "not shared with anyone" is false as soon as a hosted form or an LLM API is involved.
- Next: re-read the F1–F3 consent revisions before publication; record F5 bench RR rows from Engineering's proofs; F4 re-measure after the Founder label spot-check; the H-0026 §C4 5-render determinism check is still pending.

### 2026-11-23 · H-0034 · T2 (pilot consent kit + eval-set licences) · ESCALATE
- Did: Wrote CONSENT_KIT CK-v0.1 (AR+EN; 3 separate unticked revocable permissions, training OFF and unused; 4 processors; warranty for people, minors and music; 90 days; deletion by keyword + code), PARTNER_INTAKE_FORM (per-clip rights + reject rules), PARTNER_FEEDBACK_FORM (11 ADR-0023 job fields mapped 1:1), ADR-0024 Proposed (retention), RR-026..037, fast-lane patches to PROMPT_COLLECTION_FORM and EXP-011 (closes H-0033 F1-F3; F5 closed by RR-031..037). Licences read from primary pages 14:31-14:34 UTC.
- Evidence: company/handoffs/H-0034-return.md; company/positions/05-assurance/DATA_RIGHTS.md RR-026..RR-037
- Learned: a dataset card's licence is a claim, not proof. SHAMS says its LangMedia rows are BY-SA "following LangMedia's license", but LangMedia's own page says BY-NC-SA. Always read the upstream licence one hop back. ADR-0023's "ASC non-commercial" was also wrong (it is BY 4.0): ADR premises need I-1 evidence too.
- Next: SHAMS stays blocked until written permission or a lawyer opinion; update DATA_POLICY item 4 once ADR-0024 is signed; re-read the filled placeholders (form tool, contact) before anything is sent; confirm the Claude training setting before the first partner ingest.
