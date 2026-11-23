# RETURN H-0036 (pilot · Common Voice Arabic baseline)
- **From:** research-lead · **Tier:** T2 · **Date:** 2026-11-23
- **STATUS:** BLOCKED (brief field 3 stop rule). EXP-013 is NOT written or locked and nothing was downloaded or run.
- **SUMMARY:**
  1. H-0034 / RR-026 marks Common Voice ar 27.0 USABLE (CC0-1.0), but the download gate is unverified (F7). The Mozilla Data Collective (MDC) platform terms require a registered User Account (age 18+), and RR-026 says "the Founder, as the account holder, accepts the MDC terms". So the dataset is not downloadable without the Founder's personal account and terms acceptance.
  2. I tried one extra probe of the MDC download endpoint to verify the gate. The auto-mode classifier denied it, and I did not retry or work around it. The block rests on H-0034 evidence, not on my own check.
  3. No EXP-013 file was drafted. A prereg whose dataset ID, split and sample cannot be fixed before access would be hollow, and the brief says to stop.

## Founder steps (exact; I never create accounts or accept terms)
1. Open https://mozilladatacollective.com/datasets/cmu5wom3z00ceo107guxtg4xa (Common Voice Scripted Speech 27.0, Arabic, cv-corpus-27.0-2026-09-11).
2. Sign in, or register an MDC User Account (you must be 18+) and accept the platform terms (https://mozilladatacollective.com/terms/consumers) and the dataset conditions (no re-hosting, no speaker identification).
3. Note what the flow showed (sign-in only, terms checkbox, or email link). This closes H-0034 F7 and updates RR-026.
4. Download the Arabic archive. If it is too large, the test split alone is enough (we need only about 200 utterances). Put it in `/workspaces/Efficient_Video_Editor/quarantine/common_voice_ar_27/` (git-ignored; check that `.gitignore` covers `quarantine/` before saving). Do not commit it.
5. Tell the Operator the path and the archive's SHA-256. Then re-issue H-0036 as a continuation.

## Plan once unblocked (not preregistered; for sizing only)
- n = 200 test utterances, seed fixed. Reasoning: CPU large-v3-turbo runs near real time or slower on short clips (about 5 s each), so 200 clips is about 17 min of audio per config. That fits the 90 min cap for 2 configs, with large-v3 added only if the runtime fits. Bootstrap 95 % CI at n=200 is wide (about ±2–3 WER points at a mean near 20 %), and it is enough to set a baseline, not to rank close models.
- Configs: large-v3-turbo auto language vs forced `ar`. Metrics: WER and CER after EXP-001 normalisation (9 steps), LID accuracy under auto, RTF.
- Transfer caveat to state in EXP-013: Common Voice is read, scripted, mostly MSA speech. It does not transfer to dialect Shorts, so the likely evidence level is E1–E2 for "baseline on read MSA", with no claim about Lebanese dialect.

## EVIDENCE
- H-0034 return, table row "Common Voice" and finding F7; DATA_RIGHTS RR-026 (quotes above).
- One denied probe (no output produced). No files created apart from this return and the LOG entry.

## DONE-WHEN CHECK
- ❌ EXP-013 locked before run: not started (blocked).
- ❌ Results table: no run.
- ❌ Evidence level: none assigned (nothing is measured).

## DEVIATIONS FROM BRIEF
- None in the work. The attempted endpoint probe was a guess at an undocumented API and was rightly denied. I should have used only a plain page GET, or asked the Founder.

## OPEN QUESTIONS
1. Founder: will you sign in to MDC and download the test split (steps above)? Alternatively, is there a different CC0 Arabic ASR source that needs no account? I know of none that I have verified.

## CONFIDENCE
High that the block applies under brief field 3 (the platform terms need an account). Medium on the exact gate shape, which is still unverified (F7).

## NEXT RECOMMENDED STEP
Founder completes steps 1–5. Then research-lead drafts and locks EXP-013 (commit first), runs the script, and commits the results.
