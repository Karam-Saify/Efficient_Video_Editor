# Daily report: 2026-11-22 (Session 2)
Operator summary for the Founder. Branch `t2/install-company-os` · CI green · everything committed and pushed.
Still running when this was written: creative-lead judging the EXP-008 images (H-0016), followed by the Assurance review of Task C.

## What was done
| Phase | Result | Evidence |
|---|---|---|
| 1. Install Company OS | Done | `d95cd73` |
| 2. Verify install | Done. Hooks blocked an edit to the Constitution, a write into the held-out set and a hard git reset; a normal write was allowed | `company/gates/M0/hook-test.txt`, `4d638ec` |
| Data hygiene | Instagram zip quarantined, never opened (`quarantine/`, git-ignored). The 4 `Download*.mp4` clips are **UNVERIFIED, not usable** (RR-006..RR-010). Font licences recorded: Noto Sans Arabic RR-001, Noto Sans RR-011 (SIL OFL 1.1) | `company/positions/05-assurance/DATA_RIGHTS.md` |
| Task A: repo skeleton | Done. Pinned `pyproject.toml` with lock files, 7 cached stage CLI stubs (`src/manifest.py`), CI on Python 3.12 + 3.14 plus a job with the full runtime lock. **Reviewed, mergeable.** | H-0003, H-0009 (+ reviews) |
| Task B: schema v0 + validator | Done. JSON Schema plus 7 rules with stable error codes, path confinement (data/heldout, quarantine and data/golden rejected), 6 valid and 7 invalid fixtures, 155 tests. Last blocker N1 fixed (`890f225`). | H-0004, H-0009, H-0017 (+ reviews) |
| Task C: Arabic captions | **EXP-006 INVALID**: libass fell back to an undeclared font for Latin glyphs, caught before any image was judged. Successor **EXP-008** (declared pair Noto Sans Arabic + Noto Sans) signed by Engineering and Creative, LOCKED, then rendered with every gate passing (0 missing glyphs, 3 controls fired, 2 identical runs). **Judging in progress.** | `company/experiments/EXP-006*`, `EXP-008.md`, `render/exp008/` |
| Decisions | ADR-0002 Python floor 3.12 (Accepted, Founder-delegated). ADR-0003 overlap rule and ADR-0004 `has_audio` (Proposed) | `company/decisions/` |

## Progress against the M0 exit criteria
| # | Criterion | Status |
|---|---|---|
| 0.1 | Hooks tested | ✅ Met |
| 0.2 | Skeleton + green CI | ✅ Met |
| 0.3 | Schema + validator + fixtures | ✅ Met (merge after the final review spot check) |
| 0.4 | Golden set, 5 clips with rights | 🔴 Blocked: no usable footage |
| 0.5 | Held-out set, 3 clips sealed | 🔴 Blocked: no usable footage |
| 0.6 | Rubric v1 + calibration round | ⚪ Not started |
| 0.7 | EXP-001 + caption experiment locked | 🟡 Half: EXP-008 locked; EXP-001 (ASR) not yet |
| 0.8 | Risk register, ≥ 12 risks | ⚪ Not started |
| 0.9 | Target user + PR/FAQ draft | ⚪ Not started |

**About 3 of 9 met.**

## Blockers
1. **No usable footage.** Blocks 0.4 and 0.5 and every real pipeline test. Founder: supply raw 2–10 min Arabic sources with rights.
2. **Where the 4 clips and the zip came from.** They stay "not usable" until the Founder confirms.

## Threats
- **The caption verdict is still open.** A Sev-1 defect means the Noto pair fails and another experiment is needed.
- **The judge is an AI.** It may miss subtle Arabic defects. Recommended: a Founder spot check of AR-02, AR-05, AR-07 and AR-08.
- **Unchecked thresholds.** Creative's font-switch limits (1.3× / 0.6× of alef height) are a guess, not yet checked against Founder taste.
- **The Trend & Technique request came from outside the Operator's briefs.** It raises privacy and platform-terms risk. Six sources are recorded (RR-012..RR-017), none cleared.
- **Hook gaps.** False positives on text that only mentions a forbidden command (e.g. a commit message), and no block on shell redirects into protected files.
- **Process cost.** The full brief and review cycle per small task is safe but slow.
- **Not built yet.** Ingest does not set `has_audio` yet (next ingest brief), and a stage version must be bumped whenever real logic replaces a stub (H-0009 N3).

## Self-score: 7 / 10
- **(+)** No unsafe action and no rule broken. Reviews caught real bugs before merge: stale cache, float crash, path escape, NUL-byte crash. The font fallback was caught before judging. Every result is reproducible and committed.
- **(−)** EXP-006 was wasted. The cause was the Operator's brief, which required a lock before Engineering and Creative were consulted. STOP POINT 3 is not reached yet. Two ID collisions (EXP-007; brief numbering) needed renames. The unblocked M0 items (0.8, 0.9, EXP-001 draft) were not started in parallel.

## Next
1. Creative's EXP-008 verdict → Assurance review of Task C + N1 spot check → **STOP POINT 3**
2. Phase 4: `/close`, then a PR to `main`
3. Start 0.8 risk register, 0.9 PR/FAQ and the EXP-001 prereg in parallel (no footage needed)
