# Work log: 03-engineering
<!-- Append-only. Newest at bottom. Format: company/templates/LOG_ENTRY.md. Read the last 20 lines before starting any task (FM-1.3). -->

### 2026-11-21 · SETUP · T2 · DONE
- Did: position created with charter, playbook, checklists.
- Evidence: company/positions/03-engineering/
- Learned: —
- Next: contribute to M0 pre-mortem.

### 2026-11-22 · H-0003 · T2 · DONE
- Did: pyproject + pinned locks, src/manifest.py stage cache contract, CLI stubs for all 7 stages (legacy ingest/validate/render CLIs kept), tests (31), CI on Python 3.11.
- Evidence: company/handoffs/H-0003-return.md; `.venv/bin/ruff check .` clean; `.venv/bin/python -m pytest -q` 31 passed; clean-copy fresh-venv repro passed.
- Learned: PuLP 4.3.1 and numpy 2.5.5 require Python >= 3.12; a 3.11 floor conflicts with the .venv pins (open question to Founder).
- Next: Assurance review (H-0003-review.md); then H-0004 schema, updating tests/fixtures/timeline_min.json with it.

### 2026-11-22 · H-0004 · T2 · DONE
- Did: timeline schema v0 (int ms, ARCHITECTURE shape), validator with stable codes returning all issues, 5 valid + 5 invalid fixtures, v0→render input adapter; migrated timeline_min.json and stage-CLI tests. Uncommitted.
- Evidence: company/handoffs/H-0004-return.md; `.venv/bin/python -m pytest -q` 70 passed; `.venv/bin/ruff check .` clean; clean-copy run 70 passed; validate report byte-identical twice.
- Learned: v0 clips are back-to-back, so rule 3 "overlap" only makes sense as same-source range reuse (flagged). experiments/e6_captions.py still builds the old shape and now fails validation.
- Next: Assurance review H-0004; port e6_captions.py to v0 before H-0006.

### 2026-11-22 · H-0006 · T2 · DONE
- Did: ran EXP-006 §5 (preconditions, ENV, fingerprint check, 10 renders, SHA256SUMS) via new experiments/exp006_render.py, twice; not judged, images never viewed. Uncommitted.
- Evidence: company/handoffs/H-0006-return.md; render/frames_check/strings_check.txt ALL_MATCH=True; 10× png,1080,1920,rgb24; SHA256SUMS identical across 2 runs.
- Learned: libass falls back to NotoSans-Regular.ttf for 'i', '"', '–' (AR-05/08/10); libass wording is "Glyph 0x.. not found", which my first regex missed, so always grep render.log by hand.
- Next: Research classifies fallback (§8) before H-0007; Assurance RR row for NotoSans-Regular.

### 2026-11-22 · H-0009 · T2 · DONE
- Did: fixed H-0003 F1–F6 and H-0004 F1–F4 (floor 3.12, CI 3.12+3.14 with a full-lock job, stub/code-aware skip key, out-in-input guard, clean bad-JSON error, strict int, E_SOURCE_PATH, optional has_audio, e6 deprecated, one opencv). ADR-0002 Accepted, ADR-0003 Proposed. Uncommitted.
- Evidence: company/handoffs/H-0009-return.md; `ruff check .` clean; 116 passed on 3.14 (.venv) and on a fresh 3.12 full-lock venv; 108 passed + 8 skipped with the dev lock only.
- Learned: JSON Schema "integer" accepts 2000.0 (spec-correct), so v0 needs a strict type checker; PuLP 4 replaced LpVariable(...) with prob.add_variable(...); the protect hook blocks the held-out literal in Bash, so tests read PROTECTED_SOURCE_ROOTS.
- Next: Assurance H-0009 review; ingest must write has_audio from probe().

### 2026-11-22 · H-0013 · T2 · DONE
- Did: EXP-008 consultation; scratch probe reproduced the §5.3 tagged-text table, ran the fc-query coverage check, rendered AR-05 tagged + CTRL-01 + 3 invariance variants (images never viewed); signed the Engineering line with objections G1–G3 (paths exp007→exp008, exact regex for rule (b) not-found case, `0xE01` upper-case). Uncommitted.
- Evidence: company/handoffs/H-0013-return.md; probe MISMATCHES 0; AR-05 log resolves exactly the two declared files; CTRL-01 fires rule (a)+(b) on NotoSansThai; C2 flags AR-05/08/10; two runs identical; 5× png,1080,1920,rgb24.
- Learned: libass prints glyph codes in upper-case hex (`0xE01`) and may log `Glyph … not found` after the fallback fontselect line; redundant `\fn` tags (same font) leave the PNG byte-identical, even mid-word.
- Next: research applies G1–G3 and locks; then the render brief (experiments/exp008_render.py, render/exp008/).

### 2026-11-22 · H-0015 · T2 · DONE
- Did: wrote experiments/exp008_render.py (EXP-008 §5.4 steps 1–9) + tests/unit/test_exp008_splitter.py; ran it twice from a clean render/exp008/; not judged, images never viewed. Uncommitted.
- Evidence: company/handoffs/H-0015-return.md; COVERAGE_OK/CTRL_OK/LOG_OK/PNG_OK/INSTRUMENT_UNCHANGED all True; C2 flags AR-05/08/10; 10× png,1080,1920,rgb24; PNG/.ass/check files identical across runs; ruff clean, 125 passed.
- Learned: ffmpeg default-level logs are not byte-reproducible (context pointers + stats lines); compare the normalised logcheck.txt instead, and add -nostats to future locked commands. §5.3 has U+061C both in the A range and the X list.
- Next: Assurance review of H-0015; then Creative judges AR-01..10 (step 10).

### 2026-11-22 · H-0017 · T2 · DONE
- Did: closed H-0009 review N1 (control char / lone surrogate / unresolvable source path → E_SOURCE_PATH; is_file/hash OSError → E_SOURCE_MISSING) and N4 docstring; wrote ADR-0004 (has_audio, Proposed) + INDEX; corrected ARCHITECTURE has_audio wording. Uncommitted.
- Evidence: company/handoffs/H-0017-return.md; new tests 14 failed before, 30 passed after; ruff clean; 155 passed + 8 skipped on 3.14 and on a fresh 3.12.3 dev venv.
- Learned: Python 3.12 Path.is_file() re-raises errnos outside ENOENT/ENOTDIR/EBADF/ELOOP (3.14 swallows them), so validator stat calls need their own try; python3.12 -m venv lacks ensurepip here, use `virtualenv -p python3.12`.
- Next: Assurance N1 spot re-check; ingest brief must write has_audio from probe().
