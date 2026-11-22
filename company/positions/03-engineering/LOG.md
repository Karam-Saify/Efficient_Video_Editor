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
