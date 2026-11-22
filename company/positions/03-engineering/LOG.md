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
