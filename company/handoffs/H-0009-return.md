# RETURN H-0009
- **From:** engineering-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  Every FIX item in the brief is closed with tests: Python floor 3.12 (ADR-0002 Accepted), a CI matrix on 3.12 and 3.14 plus a full-runtime-lock job, a stub- and code-aware cache key, `--out`-in-input guard, clean bad-JSON errors, strict integer ms, `E_SOURCE_PATH` confinement, optional `has_audio`, and a deprecated `e6_captions.py`. I dropped the duplicate opencv. ADR-0003 (overlap wording) is Proposed.
  Results: 116 passed on 3.14 (.venv, full runtime), 116 passed on a fresh 3.12 venv with the full lock, 108 passed and 8 skipped on 3.12 and 3.14 with the dev lock only. `ruff check .` is clean.
  Nothing is committed. The work is in the working tree on `t2/install-company-os`, as the brief says.
- **ARTIFACTS (paths):**
  - Code: `src/manifest.py`, `src/validate/__init__.py`, `src/validate/__main__.py`, `src/render/adapter.py`, `schemas/timeline.schema.json`, `experiments/e6_captions.py`
  - Build/CI: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.github/workflows/ci.yml`
  - Tests: `tests/unit/test_manifest.py`, `tests/unit/test_pins.py`, `tests/unit/test_validate.py`, new `tests/unit/test_runtime_imports.py`; fixtures `tests/fixtures/timelines/valid/v6_no_audio_source.json`, `tests/fixtures/timelines/invalid/i6_float_ms.json`, `tests/fixtures/timelines/invalid/i7_source_path.json`, `tests/fixtures/README.md`
  - Docs: `company/decisions/ADR-0002-python-floor-3-12.md` (Accepted), `company/decisions/ADR-0003-overlap-rule-v0.md` (Proposed), `company/decisions/INDEX.md`, `company/positions/03-engineering/ARCHITECTURE.md`

## Finding → action
| Review | # | Action | What changed | Test (failed before, passes after) |
|---|---|---|---|---|
| H-0003 | F1 | **FIX** | `requires-python = ">=3.12"`, ruff `py312`. The KNOWN GAP comment is replaced and names all 5 pins (av, cpsat-logutils, numpy, orloge, PuLP). Lock headers are corrected. | `test_pins.py::test_python_floor_is_3_12` |
| H-0003 | F2 | **FIX** | CI `test` job: matrix 3.12 + 3.14 (dev lock). New `runtime` job: matrix 3.12 + 3.14, installs `requirements.txt` + dev, runs `pip check`, sets `VAC_FULL_RUNTIME=1`, apt `coinor-cbc` only. No ffmpeg, because no test needs it. | `test_runtime_imports.py` (imports pulp, numpy, av, faster_whisper, scenedetect, cv2, jsonschema; tiny CBC MILP). It skips when the env var is unset. |
| H-0003 | F3 | **FIX** | `is_fresh` also requires the same `versions.code`. A `status: "stub"` manifest only satisfies `stub_work`. | `test_manifest.py::test_stub_manifest_never_satisfies_real_work`, `::test_code_version_change_reruns` |
| H-0003 | F4 | **FIX** | Removed `opencv-python-headless` from the `media` extra and `requirements.txt`. scenedetect requires `opencv-python`. | `test_pins.py::test_one_opencv_distribution_in_runtime_lock`. Fresh 3.12 venv: `pip freeze \| grep -i opencv` gives `opencv-python==5.1.0.95` only, and `pip check` gives "No broken requirements found." |
| H-0003 | F5 | **FIX** | `load_timeline()` turns OSError, JSONDecodeError and UnicodeDecodeError into a `StageError`. Both CLIs print one `validate: error:` line, exit 1 and write no manifest. | `test_validate.py::test_bad_json_input_is_a_clean_error` (empty, `{not json`, invalid UTF-8; legacy and stage CLI) |
| H-0003 | F6 | **FIX** | `run_stage` raises `StageError` when the resolved `--out` is inside, or equal to, any `--input` dir. | `test_manifest.py::test_out_inside_input_dir_is_an_error` |
| H-0003 | F7 | DEFER | As the review says, this goes to each stage's real-logic brief. | — |
| H-0003 | F8 | WONTFIX | Recorded as a known property in ARCHITECTURE.md ("Stage cache known properties"). | doc line present |
| H-0003 | F9 | DEFER | Ticket to Assurance: RR-002 before E1 or the first real ingest. | — |
| H-0003 | F10 | WONTFIX | Informational. | — |
| H-0004 | F1 | **FIX** | The validator uses a strict type checker: `"integer"` means `type(x) is int`, so `2000.0` and `True` are rejected. The error is coded `E_SCHEMA`, and semantic rules are not reached. The `E_DURATION` message uses `:+` instead of `:+d`, so it cannot crash. New invalid fixture `i6_float_ms.json`. | `test_validate.py::test_non_int_numbers_are_coded_schema_errors` (8 cases: `in_ms` 2000.0, `fps` 30.0, `target_duration_ms` 6000.0 and 9000.0 (off target), width, `duration_ms`, `end_ms`, `fps` True), `::test_float_ms_cli_is_a_coded_line_not_a_crash`, fixture i6 |
| H-0004 | F2 | **FIX** (one optional schema field) | `sources[].has_audio`: boolean, default true, documented in the schema and ARCHITECTURE. The adapter passes it through, and the existing renderer branch uses `anullsrc`. New valid fixture `v6_no_audio_source.json`. | `test_validate.py::test_has_audio_false_renders_silence_for_that_source`, `::test_has_audio_defaults_true_and_must_be_boolean`. Real render: see Evidence |
| H-0004 | F3 | **FIX** (pulled forward from DEFER by the brief) | New `E_SOURCE_PATH` rule. It rejects absolute paths, paths that resolve outside the repo after `resolve()` (symlinks followed), and paths under `PROTECTED_SOURCE_ROOTS` (held-out, `data/golden`, `quarantine`). It runs before `is_file`/sha256, so no protected file is opened or stat'ed. New invalid fixture `i7_source_path.json`. | `test_validate.py::test_source_path_outside_repo_or_in_protected_root_is_rejected` (13 paths; `is_file` and `_sha256` are mocked to prove they are never called), `::test_source_symlink_into_protected_root_is_rejected`, `::test_protected_roots_cover_the_constitution_list` |
| H-0004 | F4 | **FIX** (deprecate) | `e6_captions.py` exits 2 and prints "deprecated, use experiments/exp006_render.py". The body is kept as the E6 record. Porting was not possible, because v0 has no font or reframe fields. | `test_validate.py::test_e6_captions_is_deprecated_with_clear_error` |
| H-0004 | F5 | DEFER | O(n²) overlap issues. Ticket from the review stands. | — |
| H-0004 | F6 | DEFER | To Creative (H-0007). | — |
| H-0004 | F7 | DEFER | Until effects and audio are rendered. | — |
| H-0004 | F8 | **FIX** (ADR) | `ADR-0003-overlap-rule-v0.md` is **Proposed**. Its wording matches the `E_OVERLAP` docstring. ARCHITECTURE points to it. | doc |
| H-0004 | F9 | WONTFIX | No formatter adoption (out of scope). | — |
| H-0004 | F10 | WONTFIX (i)–(iii), DEFER (iv) | As the review says. | — |

## EVIDENCE (commands + outputs)
- **Before the fix**, tests written first (`VAC_FULL_RUNTIME=1 .venv/bin/python -m pytest -q --continue-on-collection-errors`):
  ```
  ERROR tests/unit/test_validate.py            (ImportError: PROTECTED_SOURCE_ROOTS, so all new validate tests fail)
  FAILED tests/unit/test_manifest.py::test_stub_manifest_never_satisfies_real_work
  FAILED tests/unit/test_manifest.py::test_code_version_change_reruns
  FAILED tests/unit/test_manifest.py::test_out_inside_input_dir_is_an_error
  FAILED tests/unit/test_pins.py::test_python_floor_is_3_12
  FAILED tests/unit/test_pins.py::test_one_opencv_distribution_in_runtime_lock
  6 failed, 38 passed, 1 error
  ```
  (`test_pulp_solves_a_tiny_milp` was in that list too. It failed because of my own PuLP 3 API usage, and I fixed it to the PuLP 4 API. Not a product failure.)
- **After the fix:**
  ```
  $ .venv/bin/ruff check .
  All checks passed!
  $ VAC_FULL_RUNTIME=1 .venv/bin/python -m pytest -q          # Python 3.14.2, full runtime
  116 passed in 4.87s
  $ .venv/bin/python -m pytest -q                              # 3.14, runtime tests skipped
  108 passed, 8 skipped in 3.87s
  $ <scratch>/v312/bin/python -m pytest -q                     # fresh 3.12.3 venv, requirements-dev.txt only
  108 passed, 8 skipped in 3.28s       (ruff check . on 3.12: All checks passed!)
  $ VAC_FULL_RUNTIME=1 <scratch>/v312full/bin/python -m pytest -q   # fresh 3.12.3, requirements.txt + dev
  116 passed in 3.73s                  (pip check: No broken requirements found; opencv: opencv-python==5.1.0.95 only)
  ```
  The 3.12 venvs were built with `/usr/bin/python3.12 -m venv --without-pip` plus `.venv/bin/pip --python <venv>/bin/python install ...`, because `python3.12-venv` (ensurepip) is not installed in the Codespace.
- **CLI spot checks:**
  ```
  i6_float_ms.json   -> E_SCHEMA /tracks/video/0/in_ms: 1000.0 is not of type 'integer'      exit=1
  i7_source_path.json-> E_SOURCE_PATH /sources/0/path: source 'srcA' path '../outside/src_a.mp4' resolves outside the repository  exit=1
  v6_no_audio_source -> OK: 2 clips, 6000 ms                                                exit=0
  empty file         -> validate: error: cannot read timeline JSON from …/empty.json: Expecting value: line 1 column 1 (char 0)  exit=1
  ```
- **Real silent-source render (H-0004 F2):** I generated a 4 s 1920×1080 video with no audio stream in `out/h0009/` (git-ignored) and rendered a v0 timeline with `has_audio: false` and one Arabic caption. Result: exit 0, and ffprobe shows `video 1080x1920 | audio channels=2 | duration=3.000000`. The same timeline without the field fails in ffmpeg with exit 234, as expected. That gap is the reason ingest must fill the field (Q2).
- **Repro command** (clean checkout, repo root):
  `python3.12 -m venv /tmp/v && /tmp/v/bin/pip install -r requirements.txt -r requirements-dev.txt && /tmp/v/bin/ruff check . && VAC_FULL_RUNTIME=1 /tmp/v/bin/python -m pytest -q` (needs apt `coinor-cbc`; expect 116 passed)

## DONE-WHEN CHECK
- ✅ Every FIX item is done, with a test that fails before and passes after (table above, "Before the fix" output).
- ✅ ruff is clean, and all tests pass on 3.14 and on a 3.12 venv (dev-only and full lock).
- ✅ ADR-0002 is Accepted, ADR-0003 is Proposed, and INDEX.md is updated.
- ✅ LOG.md entry appended.

## DEVIATIONS FROM BRIEF
1. **Schema field added: `sources[].has_audio`** (optional boolean, default true). This is the single optional field the brief allows. **Creative and Assurance: please note.** It changes no existing document: all old fixtures stay valid.
2. **Behaviour change: absolute source paths are now rejected** (`E_SOURCE_PATH`), even if they point inside the repo. Relative paths that resolve outside the repo are rejected as well, so running `validate` from outside the repo root now fails with E_SOURCE_PATH. I updated `test_relative_paths_resolve_against_base_dir` to use a repo subdirectory. No experiment script I own builds absolute source paths. `exp006_render.py` does not use timelines.
3. The CI `runtime` job installs apt `coinor-cbc`, not ffmpeg. The brief covered only ffmpeg ("only if a test needs it"). CBC is needed by the MILP smoke test, because PuLP 4 does not bundle a solver.
4. `.venv` (local) still has both opencv distributions installed. I did not uninstall either, because uninstalling one of two packages that share `cv2/` breaks the other. A fresh venv from the new lock gets only one. To clean up locally: `pip uninstall -y opencv-python-headless opencv-python && pip install opencv-python==5.1.0.95`.
5. ARCHITECTURE.md gained an H-0009 rules paragraph and the H-0003 F8 known-property line. These were needed for the WONTFIX verification and to document `has_audio`.
6. The repo's protect hook blocks the held-out path literal in Bash commands. Tests therefore read `PROTECTED_SOURCE_ROOTS` from `src.validate` instead of spelling the path, and the symlink test targets `quarantine/` (the same code path).

## OPEN QUESTIONS
1. Assurance: does the strict-integer approach (a custom JSON Schema type checker, so `E_SCHEMA`) close H-0004 F1, or do you want a separate `E_TYPE` code?
2. Engineering, next stage brief: ingest must write `has_audio` from `probe()` into the timeline `sources`. Until then, a silent source that lacks the field still fails in ffmpeg. Should the validator also probe? I recommend against it: that would make the validator depend on media.
3. Operator: the CI `runtime` job is untested on GitHub until this is pushed. Its first run is the evidence for H-0003 F2.

- **CONFIDENCE:** High (biggest reason for doubt: the GitHub CI matrix has not run yet. A full-lock wheel could be missing for 3.14 on the runner's platform, but it installs locally on 3.14 and 3.12.)
- **NEXT RECOMMENDED STEP:** Assurance re-reviews H-0003 F1, F3, F4, F6 and H-0004 F1, F2, F3 (H-0009-review.md). After ACCEPT, the Operator commits on the T2 branch with `Role: engineering`, `Tier: T2`, `Reviewed-by: assurance-lead`, pushes, and checks both CI jobs on both Python versions.
