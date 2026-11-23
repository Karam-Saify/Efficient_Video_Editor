# Test fixtures
Small, text-only, committed fixtures. Never media, never anything from `data/golden/`, `data/heldout/`,
`quarantine/` or `samples/`.
- `timeline_min.json`: minimal valid timeline v0 (used by the stage-CLI tests).
- `timelines/valid/*.json`: 5 valid, renderable timeline v0 documents; `timelines/invalid/*.json`: 7 invalid
  ones, each breaking exactly one validator rule (expected codes in `tests/unit/test_validate.py`).
- `timelines/unsupported/*.json`: 5 documents that pass the schema and semantic rules but use a field the
  renderer does not implement, so `validate` returns `UNSUPPORTED_FIELD` (expected paths in
  `tests/unit/test_capabilities.py`; H-0024).
- `media/*.txt`: placeholder "source files" so the validator's existence and sha256 checks are testable.
  Source paths are relative to the repo root; run tests and `python -m src.validate` from the repo root.
