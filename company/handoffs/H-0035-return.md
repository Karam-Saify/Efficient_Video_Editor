# RETURN H-0035 (pilot · annotation schema + Footage Intelligence v0)
- **From:** engineering-lead · **Tier:** T2 · **Date:** 2026-11-23 · **Branch:** `t2/H-0035` (from `t2/install-company-os` @ b4565f0; not pushed, not merged; waits for Assurance ACCEPT)
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  1. `schemas/annotation.schema.json` v0.1 (source + job records) with validator `src/describe/schema.py`; label_origin on every label, rights_id required, the 11 job keys 1:1 with PARTNER_FEEDBACK_FORM (origins fixed by `const`). ADR-0025 Proposed.
  2. `src/describe`: `annotate` (cached ingest + ebur128 loudness + silero VAD + numpy energy/music proxy + roles-v0) → record + `descriptions.todo.json` (≤ 4 keyframes) + offline storyboard; `apply-descriptions`, `import-corrections`, `storyboard`, `validate`.
  3. Two dev clips ran the whole loop, including a real headless-browser Export download imported back; both records validate with machine and human_verified labels.
  4. Zero cost: no API call. I wrote the 8 descriptions in-session from 4 keyframes per clip.
- **ARTIFACTS (paths):**
  - `schemas/annotation.schema.json`, `src/describe/schema.py`, `tests/fixtures/annotations/{valid(6),invalid(12)}/`, `tests/unit/test_annotation_schema.py`, `company/decisions/ADR-0025-annotation-schema.md` + INDEX row (commit 3644b41)
  - `src/describe/{__init__,__main__,annotate,audio,roles,storyboard}.py`, `tests/unit/test_describe_rules.py`, `tests/unit/test_describe_pipeline.py` (bb67e00)
  - `docs/FOOTAGE_INTELLIGENCE.md`, `experiments/storyboard_offline_check.mjs`, ARCHITECTURE.md module-map row (726c845)
  - Dev-clip outputs (git-ignored, not committed), for `quarantine/dev/Download (1).mp4` (RR-007) and `Download (7).mp4` (RR-021):
    `cache/Download (1)-dec8a22656/{describe/annotation.json, describe/descriptions.todo.json, describe/simulated_corrections.json, describe/browser_corrections.json, describe/corrections/, storyboard/index.html}` and the same under `cache/Download (7)-61494d967d/` (plus `describe/browser_export_probe.json`, exported but not imported)
- **EVIDENCE (commands + outputs / metric files):**
  - Reproduction (one line): `.venv/bin/python -m pytest -q tests/unit/test_annotation_schema.py tests/unit/test_describe_rules.py tests/unit/test_describe_pipeline.py` → 59 passed (43 + 9 + 8; the pipeline tests make their own synthetic ffmpeg testsrc/smptebars/color + sine clip in tmp).
  - Full suite: `.venv/bin/python -m pytest -q` → `463 passed, 8 skipped`; `.venv/bin/ruff check .` → `All checks passed!`
  - Dev loop: `annotate` (cached transcripts reused, ~1 s each) → `apply-descriptions` → `import-corrections` → `validate` → `valid` for both. Label counts: Download (1) `{'machine': 27, 'human_verified': 4}` after the simulated import (then +2 human_verified after the browser import); Download (7) `{'machine': 23, 'human_verified': 4}`. Example: scene 6 of (1) `{'value': 'other', 'label_origin': 'human_verified', 'machine_value': 'cta'}`.
  - Offline proof, grep: both storyboards: `grep -c '://'` → 0; `grep -o -i 'http[a-z-]*'` → only `http-equiv` (the CSP meta `default-src 'none'; img-src data:`).
  - Offline proof, headless (Playwright 1.57.0 + chromium-headless-shell, installed in the session scratchpad, not a project dependency): `node experiments/storyboard_offline_check.mjs <index.html> <out.json> 1 other` → `{"external_requests":[],"console_errors":[],"images_rendered":7,...}` exit 0 for (1); `images_rendered":6` exit 0 for (7). The (1) download was imported, and the record validates.
  - Determinism: `test_annotate_is_byte_identical_on_rerun` (annotation.json + index.html sha256 equal after delete + rerun); real clip: storyboard regenerated twice → `IDENTICAL 15994faae61841dc`.
  - Audio on the dev clips: (1) I −13.7 LUFS, LRA 3.7, speech_ratio 0.0, nonspeech_sound_ratio 0.84 → `LOW_VAD_SPEECH`; (7) −14.0 LUFS, 2.2, 0.0, 0.986 → `LOW_VAD_SPEECH`. Both have an empty ASR transcript and are music-only by VAD, so neither is flagged `ASR_SUSPICIOUS` (that path is covered by unit tests only). Neither record says "no speech".
  - Tokens/minutes: 0 API tokens, $0. Session vision input: 2 images (each a 1280×568 tile of the 4 listed 320 px keyframes). Uncached ASR ~25 s CPU per 20 s clip (runtime_sec 26.5 / 24.8 from the transcripts); everything else ~1 s.
  - Secrets: `git diff` grep for api_key/secret/token= → no hits.
- **DONE-WHEN CHECK:**
  - ✅ On 2 dev clips: annotate → storyboard HTML → descriptions.todo.json filled for ≤ 4 keyframes per clip → simulated correction JSON → import → the record validates with both machine and human_verified labels. Paths above (cache/, not committed).
  - ✅ Schema tests: 6 valid / 12 invalid fixtures; `test_label_origin_required_on_every_label` deletes every label_origin in every valid fixture, one at a time, and each deletion → E_SCHEMA; `test_rights_id_required` + `test_rights_id_format`; `test_job_fields_match_assurance_mapping_1_to_1` reads PARTNER_FEEDBACK_FORM.
  - ✅ The storyboard makes no network requests: grep (0 `://`) and headless (0 external requests, 0 console errors), plus `test_storyboard_is_offline`.
  - ✅ Suite + ruff green (above).
- **DEVIATIONS FROM BRIEF:**
  1. `job.corrections[].t_start_s` → `t_start_ms` (integer ms, CONVENTIONS + I-4). This is the only place the mapping is not copied literally. Assurance should accept or reject it (Q1).
  2. Roles enum adds `other` (partner needs a "none of these"; also used for scenes under 1 s). Recorded in ADR-0025.
  3. Per-segment `language` is the file-level faster-whisper language until a human corrects it (whisper gives one language per file).
  4. Feedback keys F1–F6 are optional in a job record (a job opens before feedback). J1–J5 + admin keys are required.
  5. Probe metadata (`media`: duration, size, fps) carries no label_origin: these are facts, not labels. Structural items (scenes, segments, keyframes, audio, transcript) do carry it.
  6. I read the 4 keyframes per clip as one tiled image, not 4 files (same frames, fewer calls).
  7. The headless check needed Playwright. I installed the version already pinned in H-0030 into the scratchpad (dev-only, free, not in requirements).
  8. The branch is cut from `t2/install-company-os` (current HEAD), not from `main`, because main does not have ADR-0023/H-0034.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. Accept `t_start_ms` instead of `t_start_s` in the job corrections? **assurance-lead** (owner of the mapping).
  2. Sign ADR-0025? **Founder**, after the Assurance review.
  3. Is the `other` role acceptable, and are the bilingual storyboard strings right in Arabic? **creative-lead** (T1 proofread).
  4. H-0034 F3 (Claude training setting off) must be confirmed before a partner clip runs through a session. **Founder**.
- **CONFIDENCE:** High for the schema, the validator and the offline storyboard. Medium for audio signals. Biggest reason for doubt: neither dev clip has speech by VAD, so `ASR_SUSPICIOUS` and roles `proof` were checked only on synthetic and unit inputs, not real speech; the 60 wpm threshold is a guess until LABELS.csv/EXP-012 gives ground truth.
- **NEXT RECOMMENDED STEP:** assurance-lead reviews `t2/H-0035` (repro command above + the headless check on one storyboard); after ACCEPT, merge, then run it on a dev clip with speech (Download (3) or (5)) to exercise `ASR_SUSPICIOUS`/`proof` before partner #1.
