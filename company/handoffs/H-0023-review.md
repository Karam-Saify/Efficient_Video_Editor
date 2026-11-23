# H-0023 review: Task C (Arabic caption rendering, EXP-006 / EXP-008) plus N1 spot check
- **Reviewer:** assurance-lead · **Tier:** T2 · **Date:** 2026-11-22
- **Reviewed commit:** 43556ca (branch t2/install-company-os). A later commit by another instance (18aa5da, risk register) was not reviewed.
- **Brief:** given inline by the Operator. There is no `company/handoffs/H-0023-brief.md` (see F10).
- **STATUS:** DONE
- **Reproduction log:** `company/handoffs/H-0023-repro.txt` (170 lines). **No PNG was viewed.** I worked from hashes, logs and text only.

## VERDICT: ACCEPT WITH FINDINGS (S1: 0 · S2: 4 · S3: 7)
- I confirm **EXP-006 = INVALID** and **EXP-008 = FAIL (N_correct 8, N_sev1 0)**. Both follow from the locked rules.
- The EXP-008 render reproduces byte-for-byte: **26/26** deterministic artefacts (11 PNG, 11 .ass, 4 check .txt) match the committed `render/exp008/SHA256SUMS`.
- Both locks hold in git history.
- The briefed rerun command cannot prove reproduction as written (F1, F2). That makes it a defect of the verification recipe. It is not a defect of the result.
- The Founder's announced combined verdict conflicts with the locked EXP-008 text. F3 gives a way to record it without breaking I-5.
- N1 is fixed. On N1, Task B is mergeable.

## Verification performed (ladder)
| Level | What | Result | Evidence |
|---|---|---|---|
| L1 | `tests/unit/test_exp008_splitter.py`; full suite + ruff in a clean worktree | 17 passed; 155 passed / 8 skipped; ruff clean | repro §8, §10 |
| L2 | Raw and tagged fingerprints are checked by the instrument (Stop on mismatch). The instrument exited 0. | pass | repro §2 |
| L3 | Determinism: fresh run compared with **committed** sums | 26/26 OK. All 11 raw logs and ENV.txt differ (ENV: timestamp only). | repro §3, §4 |
| L4 | `ffprobe.txt` is byte-identical on rerun (1080×1920 rgb24 is asserted by the instrument, PNG_OK=True) | pass | repro §2, §3 |
| L5 | AR-05/AR-08 through the splitter: tagged text matches the §5.3 table. Arabic edge strings U+061C/U+200F/U+200D fail loudly as class X. | pass | repro §9 A4–A8 |
| L6 | Rubric spot check via Creative | not repeated (Creative already judged; Founder spot check pending, F3) | — |
| L7 | Cost | 0 LLM tokens in the experiment; 2.3 s CPU per run | H-0015, repro §2 |

Lock integrity (check 1), from `git log --follow` (repro §11):
- EXP-006 locked in 7fff041 (16:39:34), single version. EXP-006 render output was committed in 95f37ef (16:51:14), after the lock. The file was not changed after the lock.
- EXP-008: draft 7f4b8c5, then Creative sign 9802832, O1/O2 applied 98398ed, Engineering sign 8ec3e45, **LOCKED b0d76f5 (17:12:21)**. Render 280d314 (17:16:32) came after the lock. No commit touches EXP-008.md after b0d76f5.
- EXP-008-results.md is not a locked file. 43556ca deleted exactly one line, the evidence-level placeholder. Creative's table (§3/§4) is unchanged.

Controls and coverage (check 3), reproduced:
- `coverage_check.txt` is byte-identical on rerun. It shows 10 × `missing=[]` and `COVERAGE_OK=True`. C0 reports exactly `U+0E01 not in NotoSans-Regular.ttf`.
- `logcheck.txt` is byte-identical. C2 flags exactly AR-05/08/10 on the EXP-006 log. C1 fires rule (a) and rule (b) (NotoSansThai-Regular.ttf), and fontselect lines are visible. CTRL_OK and LOG_OK are True.
- My own grep of the fresh logs, without the instrument's checker, agrees. There are 0 `Glyph … not found` lines in the 10 real logs. The resolved files are only the declared pair: {Arabic} for the 6 strings with no L characters, {Arabic, Latin} for AR-04/05/08/10. CTRL-01 adds Thai (repro §6).
- The detector was attacked with 7 synthetic log lines (repro §9 B1–B7). It flags an undeclared file, an empty target, `(null)` and upper-case `GLYPH … NOT FOUND`. It flags a declared basename in a different directory (`/tmp/evil/NotoSans-Regular.ttf`), so the comparison is on the full path. It passes the declared paths.
- The font sha256 values and `fc-match` match EXP-008 §5.1. The instrument hash `c98d1c69…0af6` matches ENV.txt step 1, so INSTRUMENT_UNCHANGED is confirmed independently.

Rulings follow from the locked rules (check 3):
- EXP-006 §8 lists "different font file resolved" as invalidating. NotoSans-Regular resolved for AR-05/08/10 (render/frames_check/render.log l.135-136, 224-225, 284-285). So the result is INVALID.
- EXP-008 §6 says "PASS iff N_correct = 10 AND N_sev1 = 0". Creative recorded Sev-2 font-switch (b) on AR-04 (1.63×) and AR-05 (1.61×/1.63×), and §6 makes any Sev-2 not correct. So N_correct = 8, which gives FAIL. The margin to the 1.3× anchor is about 14 px, so the verdict does not depend on measurement noise.

Adversarial attempts (≥ 3 required; 17 done, repro §9 and §10):
- empty string; spaces only; a 19 500-code-point string; AR-05; AR-08; U+061C, U+200F and U+200D; ASS braces and `\N` inside the text;
- 7 detector lines;
- 6 control-character and surrogate paths against N1.

Invariants I-1…I-10:
- I-1: every claim in H-0015/16/18 that I checked has an artefact behind it.
- I-2: the builder and the judge are separate.
- I-3: no video went to an LLM, and only 10 stills went to the judge.
- I-4: not applicable.
- I-5: both locks hold, and no threshold was moved (but see F3 and F6).
- I-6: see F11. I report a technical slip of my own there.
- I-7: ADR-0004 and ADR-0005 were not edited by these commits (not reviewed further).
- I-8: not applicable to this review.
- I-9: see F8.
- I-10: the Founder-verdict change was correctly escalated to Assurance.
- I found no secrets in the reviewed diffs.

## Findings
**F1 · S2 · The H-0015 rerun command is self-referential.**
- *Evidence:* `experiments/exp008_render.py` step 9 rewrites `render/exp008/SHA256SUMS` (l.449-451). The command `rm -rf render/exp008 && … exp008_render.py && sha256sum -c render/exp008/SHA256SUMS` therefore checks the new outputs against hashes it has just written. It would report OK even if every PNG had changed.
- *Required action:* Engineering changes the documented rerun recipe, and the EXP-010 prereg uses it, so that the committed sums are saved first, e.g. `git show HEAD:render/exp008/SHA256SUMS > $T/sums && … && grep -v '\.log$\|ENV.txt$' $T/sums | sha256sum -c -`.
- *Verify by:* Assurance runs the new recipe once with a deliberately changed `.ass`, which must fail, and once clean, which must pass. My own comparison against the committed sums passed 26/26 (repro §3), so the EXP-008 result itself stands.

**F2 · S3 · The instrument cannot run from a `git archive` export.**
- *Evidence:* Attempt 1 failed with `CalledProcessError: git status --porcelain -- render/frames_check … exit status 128` (repro §1). I reproduced in a clean detached `git worktree` of the same commit instead.
- *Required action:* the precondition should fail with a coded message ("needs a git checkout"), or EXP-010 should document a worktree as the clean state.
- *Verify by:* a rerun from an export prints the coded message, not a traceback.

**F3 · S2 · The Founder's "combined verdict" conflicts with the locked EXP-008.**
- *Evidence, all in the locked text:* §5.4 step 10 and §10 make creative-lead the sole judge. §8 lists "the judge is not creative-lead" as invalidating, and says "once any PNG has been judged, the result stands… no re-judging". The §8 threats row says the Founder spot check is "non-decisive and does not change the verdict". Folding a second judge into `N_correct`/`N_sev1` after the result is known would therefore be a post-hoc change of the judging rule (I-5).
- *Required action: how to record it.*
  1. Append a new section **"§9 Founder spot-check (2026-11-2x, non-decisive under the locked §8; recorded at Founder request)"** to `EXP-008-results.md`. Never edit EXP-008.md, and never change §1–§8 of the results.
  2. Content, written by the Founder or transcribed verbatim by the Operator:
     - the strings checked (AR-02, AR-05, AR-07, AR-08, which differs from the prereg-recommended AR-04/05/07/08/10; record the difference);
     - a sha256 check of each PNG against `SHA256SUMS` before viewing;
     - the zoom used, with the raw reference string from ARABIC_QA.md alongside;
     - per string: correct yes/no, each defect with category and severity, a one-line note;
     - a statement that the Founder did not view `render/frames_check/` or `render/exp008/control/`.
  3. Then two lines. **"Official verdict (locked rule): FAIL, unchanged"**, and **"Combined reading (Creative + Founder, for decisions)"**, where a string counts as correct only if neither rater records a Sev-1/Sev-2 or a tested-property defect.
- *If the Founder finds a Sev-1:* the official verdict stays FAIL, which it already is, and the official `N_sev1` stays 0. The combined reading records it. Research must then withdraw or downgrade the "what passed" component claims in results §8.2 item 3 for that category. Assurance logs a judge miss in CALIBRATION.md. EXP-010 must preregister two raters.
- *If the Founder disagrees towards leniency* (e.g. finds AR-05 acceptable): FAIL cannot become PASS (§8: the result stands). The disagreement is calibration input for the 1.3× anchor before the EXP-010 lock, as H-0018 §8.5 recommends. If the Founder wants to adopt the configuration anyway, that is a Founder decision recorded in an ADR with an explicit waiver citing EXP-008 FAIL. It is not a reinterpretation of the experiment.
- *If the two agree:* record agreement as calibration evidence for creative-lead.
- To make a Founder verdict genuinely "count together", preregister it in **EXP-010** §5/§6 before lock: a rater panel of creative-lead plus the Founder, with a combination rule fixed at lock.
- *Verify by:* Assurance diffs EXP-008-results.md after the append. Only new lines below §8, and `git log` shows no EXP-008.md change.

**F4 · S3 · Log nondeterminism is wider than results D1 says.**
- *Evidence:* in my rerun all 11 raw `.log` files differ from the committed ones. After normalising pointers and dropping `frame=`/`speed=` lines, 3 of 11 (AR-01, AR-06, AR-09) still differ. The difference is the stderr ordering of an `image2 … image sequence pattern` warning and an `out#0/image2` muxing line (repro §4). Neither line is rule (a) or rule (b), so this is non-invalidating under §8, and `logcheck.txt` is byte-identical.
- *Required action:* EXP-010 locks `-nostats -loglevel <fixed>` and names `logcheck.txt` as the reproducibility artefact for logs.
- *Verify by:* the EXP-010 prereg text and its rerun.

**F5 · S2 · The §5.3 splitter passes ASS override syntax through. This is a risk for the `src/render` port.**
- *Evidence:* `split_runs("مرحبا {\\b1}")` outputs `مرحبا {\fnNoto Sans}{\b1}`, a live libass tag. `\N` likewise becomes a line break (repro §9 A9, A10). Neither occurs in AR-01..AR-10, so EXP-008 is unaffected. Real captions from ASR or the LLM can contain `{`, `}` or `\`, which would inject tags that EXP-008 §5.2 forbids and change rendering.
- *Required action:* when Engineering ports §5.3 into `src/render`, caption text must be escaped or rejected for `{`, `}` and `\` before tagging, with a coded validator issue and fixtures.
- *Verify by:* Assurance's T2 review of that port runs these two strings and expects either an escaped render or a coded rejection.

**F6 · S3 · Real strings were rendered before the lock during consultation.**
- *Evidence:* the H-0013 probe rendered AR-05 and three AR-04 variants to scratch before b0d76f5. Only hashes and ffprobe output were used, and no image was viewed (H-0013 l.29-34). No threshold could be tuned on pixels, so I-5 is not breached.
- *Required action:* codify in the research SOP that consultation probes may render but never view, and that their outputs stay in scratch and are listed in the consultation return.
- *Verify by:* the SOP text.

**F7 · S3 · The Operator's ruling understates G2.**
- *Evidence:* H-0014 calls G1–G3 "paths and wording". G2 actually widened the gating detector rule (b): it added a `failed to find any fallback` regex and the cases with no `->` or an empty path (b0d76f5 diff). The conclusion still holds, because the gating detector is outside Creative's judging domain, so no Creative re-sign was needed. The lock commit also mixed content edits with the lock flip.
- *Required action:* future locks put the content edits in one commit and the `Lock: LOCKED` flip in another, and rulings name substantive changes as such.
- *Verify by:* the next prereg's git log.

**F8 · S3 · Rights.**
- *Evidence:* RR-001 (Noto Sans Arabic, sha 504d7407…) and RR-011 (Noto Sans, sha 89c3c497…) are recorded with OFL 1.1, and both sha values match my recompute (repro §7). **However**, CTRL-01 resolved `NotoSansThai-Regular.ttf` (logcheck C1), and the committed `render/exp008/control/CTRL-01.png` contains a glyph from it. There is no RR row for that file, and ENV.txt does not record its sha256. The RR-011 usage text still describes only the EXP-006 fallback. This is not a HALT: the font is from the same OFL package, used for an internal control, and never published.
- *Required action:* assurance-lead adds an RR row for NotoSansThai-Regular (sha and licence from primary sources) and updates the RR-011 usage text to "declared Latin font, EXP-008". This is my own follow-up in the DATA_RIGHTS register, not RISK_REGISTER.
- *Verify by:* `grep NotoSansThai DATA_RIGHTS.md`.

**F9 · S3 · Process (check 4).**
- *Consultation:* the order was correct. Creative signed, then O1/O2 were applied, then Engineering signed on the amended draft, then the lock. Both sign-offs cite returns.
- *Renumbering EXP-007 → EXP-008:* justified (EXP-007 is reserved in PLAYBOOK, ROADMAP 4.2 and A-05), done before the lock, and recorded in the header. No `render/exp007` or `exp007_render.py` exists.
- *Deviations D1–D5:* correctly classified as non-invalidating, but see F4.
- *EXP-006:* locked without consultation (EXP-006 l.136). This was root-caused in EXP-006-results §1 and fixed in the EXP-008 process.
- *Inconsistency:* results §6 deviation 1 says research-lead writes the file, while the file was first authored by creative-lead.
- *Required action:* none beyond noting it. Research may clarify the §6 wording in an appended line.

**F10 · S3 · No brief file.**
- *Evidence:* H-0023 has no `company/handoffs/H-0023-brief.md`. The inline brief lacked explicit Done-when, Escalate-if and Termination fields. I treated the 7 numbered checks as Done-when.
- *Required action:* the Operator files the brief.
- *Verify by:* the file exists.

**F11 · S2 · Self-reported custody slip.**
- *Evidence:* one of my commands contained `ls data/heldout >/dev/null 2>&1` (the rights check, repro not affected). It was unintended and outside a gate. Output was discarded, and no file name or content was seen. I may not edit anything under `data/heldout/`, so I cannot append to ACCESS_LOG.md myself.
- *Why not HALT:* I judged this a technical I-6 touch with no exposure, not a breach that needs a HALT, because no held-out content was read. The Operator may overrule.
- *Required action:* the Operator records this entry through the custody procedure, and I add the check "never name the held-out path in non-gate commands" to my CHECKLISTS.
- *Verify by:* an ACCESS_LOG entry dated 2026-11-22 citing H-0023.

**F12 · S3 · Comment only (Research's domain).**
- *Evidence:* ASCII digits are covered by Noto Sans Arabic (EXP-006-results §1). The AR-04 FAIL exists only because §5.3 assigns digits to class L.
- *Required action:* EXP-010 should consider "ASCII digits → Arabic font" as a design alternative to a scale factor, alongside the 1.3× calibration.
- *Verify by:* the EXP-010 draft.

## N1 spot check (check 6)
- Commit 890f225 adds the control-character, surrogate and resolve-error guards to `src/validate`.
- I ran the CLI on v1_single_clip.json with `sources[0].path` replaced by a NUL, a newline, U+007F, U+0085, a lone surrogate and a tab. Every case gives `E_SOURCE_PATH`, a coded message and exit 1. There is no traceback. The base fixture gives exit 0.
- Full suite: 155 passed, 8 skipped. ruff clean. CI on 43556ca is green (run 45049157514).
- **N1 is closed, and Task B is mergeable as far as N1 is concerned.** The schema and ADR-0004 changes in the same commit were not in this review's scope.

## Required before the EXP-008 conclusion is used
1. Record the Founder spot check as described in F3.
2. Fix F1 in the recipe before EXP-010 is locked.

All other findings are non-blocking.

## Builder confidence statement
Not read before this verdict was written. H-0015 l.66 was located by line number only, and its content was not read.
