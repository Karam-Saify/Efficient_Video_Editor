# RETURN H-0003
- **From:** engineering-lead
- **STATUS:** DONE (one known gap, see Deviations 2 and Open question 1)
- **SUMMARY (≤5 lines):**
  The repo is now a pinned Python project (`pyproject.toml` + two lock files). All 7 stages run as `python -m src.<stage> --input X --out D`, going through one helper, `src/manifest.py`. Each run writes `manifest.json` (input sha256s, config hash, versions, duration, output sha256s) and skips an identical rerun.
  The legacy positional CLIs for ingest, validate and render still work. `validate --input` runs the real validator and writes `report.json`. The other 6 stages are stubs (`status: "stub"`).
  CI (`.github/workflows/ci.yml`) runs `ruff check .` and `pytest` on Python 3.11 with only the core+dev lock installed. 31 tests pass and ruff is clean, both locally and in a fresh venv on a clean copy.
  Gap: PuLP 4.3.1 and numpy 2.5.5 (the versions in `.venv`) need Python >= 3.12, so the `milp` and `media` extras cannot install on 3.11.
- **ARTIFACTS (paths):**
  - New: `pyproject.toml`, `requirements-dev.txt`, `.github/workflows/ci.yml`, `src/manifest.py`,
    `src/describe/__init__.py`, `src/{describe,score,select,edit}/__main__.py`, `src/prompts/README.md`,
    `tests/__init__.py`, `tests/unit/__init__.py`, `tests/unit/test_manifest.py`, `tests/unit/test_stage_cli.py`,
    `tests/unit/test_pins.py`, `tests/fixtures/README.md`, `tests/fixtures/timeline_min.json`
  - Changed: `requirements.txt` (now a full runtime lock), `src/__init__.py` (`__version__`),
    `src/ingest/__main__.py` (new-CLI dispatch, `TYPE_CHECKING` numpy import, one wrapped line; ASR logic untouched),
    `src/render/__main__.py` (legacy body moved into `main()`, dispatch added),
    `src/validate/__main__.py` (legacy body moved into `main()`, `stage_work` added)
  - Not touched: `schemas/timeline.schema.json`, `src/validate/__init__.py` (validator rules), `src/render/__init__.py`, `src/common.py`
- **EVIDENCE (commands + outputs / metric files):**
  - Reproduce from a clean state (one line):
    `python -m venv .v && .v/bin/pip install pip==26.3 -r requirements-dev.txt && .v/bin/ruff check . && .v/bin/python -m pytest -q`
  - `.venv/bin/ruff check .` → `All checks passed!`
  - `.venv/bin/python -m pytest -q` → `31 passed in 2.12s`
  - Clean-copy reproduction: `git ls-files -co --exclude-standard` was copied into the scratchpad, a fresh venv was created (Python 3.14.2) and given only `requirements-dev.txt`, and `pip freeze` matched the 12 lock lines exactly. Result: `All checks passed!` and `31 passed in 2.02s`.
  - Python 3.12 run: pinned wheels went into a `--target` dir and `PYTHONPATH=… python3.12 -m pytest -q` gave `31 passed in 1.91s`. It was not run on 3.11, which is not installed (Deviation 1).
  - 3.11 installability check: `pip download --only-binary=:all: --python-version 3.11` gave OK for every pin in `requirements-dev.txt`, plus faster-whisper, scenedetect, opencv-python-headless and pip 26.3. It failed for `PuLP==4.3.1` (the latest for 3.11 is 3.3.2) and `numpy==2.5.5`. Their METADATA says `Requires-Python: >=3.12`.
  - Stage CLI, all 7 stages run twice on `tests/fixtures/timeline_min.json`. Excerpt:
    ```
    select: done (stub) in 0.0s -> …/demo1/select/manifest.json
    select: skip (inputs and config unchanged; …/demo1/select/manifest.json)
    validate: done (ok) in 0.001s -> …/demo1/validate/manifest.json
    validate: skip (inputs and config unchanged; …/demo1/validate/manifest.json)
    select: done (stub) …          # after --set target_duration_ms=30000 (config change reruns)
    ```
    The other 5 stages printed the same done/skip pair. The same check is automated for all 7 stages in `tests/unit/test_stage_cli.py::test_stage_writes_manifest_then_skips`, which also asserts the manifest stays byte-identical after a skip.
  - Example manifest (`validate`): keys `stage, status, created_at, duration_s, input_hashes, config, config_hash, versions{code,python,tools}, outputs`. Here `input_hashes = {"tests/fixtures/timeline_min.json": "d46bbae8…"}` and `outputs = {"report.json": "655823ac…"}`.
  - Required manifest test cases are in `tests/unit/test_manifest.py`:
    - `test_first_run_writes_manifest`
    - `test_rerun_same_inputs_and_config_skips`
    - `test_changed_input_reruns`
    - `test_changed_config_reruns`
  - Extra manifest test cases:
    - stage_version bump reruns
    - a tampered or deleted output reruns
    - another stage's manifest is not reused
    - failed work leaves no manifest
    - unknown `--set` key is rejected
  - Determinism: `test_validate_report_is_byte_identical_across_runs`.
  - Legacy behaviour:
    - `test_legacy_validate_cli_still_works` (`OK: 1 clips, 2.500s`)
    - `test_legacy_render_command_builder_still_works`
    - `python -m src.ingest --help` still shows the positional legacy usage
  - Heavy imports: `test_heavy_deps_not_imported_at_module_import` imports all 7 stage packages and `src.ingest.__main__`. It asserts that faster_whisper, scenedetect, cv2, ctranslate2 and pulp are not in `sys.modules`.
  - Ignore check: `git check-ignore -v cache/ samples/foo.mp4 samples/notes.txt` gave `.gitignore:9:cache/`, `.gitignore:13:*.mp4` and `.gitignore:10:samples/*`.
  - Secrets: `git diff | grep -iE "api[_-]?key|secret|password"` returned nothing.
  - No real media was ingested or rendered. No file under `data/golden/`, `data/heldout/` or `quarantine/` was read. No LLM calls were made (I-3 and I-4 do not apply).
- **DONE-WHEN CHECK:**
  - ✅ `pyproject.toml` with pinned deps, ruff and pytest config.
    - Every direct dep is `==`. ruff uses `target-version = "py311"`. pytest uses `testpaths = ["tests"]`.
    - `tests/unit/test_pins.py` enforces the pins.
  - ✅ All 7 stage packages, `src/prompts/`, `tests/unit/` and `tests/fixtures/` exist. Each is tracked via real files or a README.
  - ✅ `python -m src.<stage> --input X --out D` works for all 7 stages. The manifest is written and the second run skips. Shown above for select and validate, and tested for all 7.
  - ✅ The manifest/skip unit tests pass (31/31) and `.venv/bin/ruff check .` is clean.
  - ✅ `.github/workflows/ci.yml` is present: Python 3.11, installs `requirements-dev.txt`, runs `ruff check .` then `python -m pytest -q`, on push and pull_request. It has not been run on GitHub yet because nothing is pushed.
  - ✅ `cache/` and `samples/` are ignored (git check-ignore output above).
  - ✅ Entry appended to `company/positions/03-engineering/LOG.md`.
- **DEVIATIONS FROM BRIEF:**
  1. Local tests ran on Python 3.14.2 (`.venv`), plus a 3.12 check. They did not run on 3.11, which is not installed, as the brief anticipated. CI is the first 3.11 run.
  2. Pins come from `.venv` as instructed. But `PuLP==4.3.1` and `numpy==2.5.5` (pulled in by the `media` extra) need Python >= 3.12. So `requires-python = ">=3.11"` holds only for core+dev, and `requirements.txt` (the full runtime lock) does not install on 3.11. To keep CI on 3.11, PuLP sits in a separate `milp` extra and CI does not install it. This is commented at the top of `pyproject.toml` and `requirements.txt`.
  3. Dependency file layout (my choice, as the brief asked):
     - `pyproject.toml` is the source of truth for direct pins.
     - `requirements.txt` is the full runtime lock (core + milp + media, transitive pins from `pip freeze`), so the CLAUDE.md setup command still works.
     - `requirements-dev.txt` is the core + dev lock that CI installs.
     - `tests/unit/test_pins.py` fails if pyproject and the locks disagree.
     - The lock pins versions but not hashes (no `--require-hashes`).
  4. ruff excludes `.claude/` and `company/`. Both had pre-existing lint findings in files I do not own (`.claude/hooks/protect.py`, `company/gates/M0/hook_selftest.py`), and I did not edit them.
  5. In `--input` mode, `ingest` and `render` are manifest-only stubs. They do not run ASR or FFmpeg, so no real media was processed. Their real logic stays reachable through the legacy positional CLI. Wiring the real logic to `--out` (instead of `cache/<video_id>/`) touches the stage boundary and is left for Phase 1.
  6. `tests/fixtures/timeline_min.json` and two CLI tests target the current (pre-H-0004) schema and must change together with it in H-0004.
  - Not a deviation, a design note: the skip key is input hashes + config hash. Config always includes `stage_version`. Python and tool versions are recorded but do not trigger a rerun. `created_at` and `duration_s` make the manifest itself non-byte-identical across fresh runs. Stage outputs (for example `report.json`) are byte-identical.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. Python floor (Operator → Founder; Engineering recommends): (a) raise `requires-python` to `>=3.12` and run CI on 3.12, which keeps the `.venv` versions and lets CI test the MILP; or (b) stay on 3.11 and downgrade to `PuLP==3.3.2` plus a numpy <= 2.4 pin, which means retesting E6/ingest. Engineering recommends (a). Today's setup cannot test `select` in CI once it has real logic.
  2. Should CI also install `ffmpeg` + `coinor-cbc` when Phase 1 adds a real `select`/`render` test? (Engineering will decide at that point; for Assurance's information.)
  3. Assurance: please confirm the clean-state reproduction above is enough, or say whether you want a run in a GitHub Actions log before ACCEPT.
- **CONFIDENCE:** Medium. The biggest doubt is that CI has never actually run on Python 3.11; local runs were 3.14 and 3.12 only.
- **NEXT RECOMMENDED STEP:** Assurance reviews this diff and reproduces it with the one-line command. The Operator answers Open question 1 before H-0004 / Phase 1 `select` work.
