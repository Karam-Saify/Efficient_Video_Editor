# RETURN H-0017
- **From:** engineering-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  N1 fixed: `_source_path_problem` rejects C0/C1 control characters (NUL, newline, DEL...) and lone surrogates up
  front, and turns any `OSError`/`ValueError`/`RuntimeError` from `is_absolute()`/`resolve()` into `E_SOURCE_PATH`;
  the later `is_file()`/hash step turns an `OSError` (Python 3.12 re-raises ENAMETOOLONG/EACCES) into `E_SOURCE_MISSING`.
  New test module, 30 cases: 14 failed before the fix, 30 pass after. N4 docstring reworded. ADR-0004 (Proposed) + INDEX row;
  ARCHITECTURE no longer says ingest fills `has_audio`. Not committed (on `t2/install-company-os`).
- **ARTIFACTS (paths):**
  - `src/validate/__init__.py` (`_source_path_problem`, rule-1 block, `E_SOURCE_PATH` code docstring)
  - `tests/unit/test_validate_source_path_fuzz.py` (new; separate module per N5 lesson)
  - `company/decisions/ADR-0004-source-has-audio.md` (new), `company/decisions/INDEX.md`
  - `company/positions/03-engineering/ARCHITECTURE.md` (validator-rules paragraph)
- **EVIDENCE (commands + outputs / metric files):**
  - Before fix (new tests, parent code): `.venv/bin/python -m pytest -q tests/unit/test_validate_source_path_fuzz.py`
    → `14 failed, 16 passed` (all 12 MUST_REJECT cases, the NUL regression, and the CLI test, which showed a `Traceback`).
  - After fix, same command → `30 passed in 0.62s`.
  - `.venv/bin/ruff check .` → `All checks passed!`
  - `.venv/bin/python -m pytest -q` (Python 3.14.2, dev lock) → `155 passed, 8 skipped in 4.91s` (8 skips = runtime-import tests, full runtime lock not installed in .venv).
  - Fresh Python 3.12.3 virtualenv with `requirements-dev.txt` (scratchpad) → `155 passed, 8 skipped in 4.34s`.
  - CLI: `.venv/bin/python -m src.validate <tl with path "a\u0000b">` →
    `E_SOURCE_PATH /sources/0/path: source 'srcA' path 'a\x00b' contains a control character (e.g. NUL or newline)`, `exit=1`, no traceback.
  - Secrets scan `git diff | grep -iE "key|token|secret"`: one hit, the word "key" in unchanged ARCHITECTURE context ("input-hash key"); benign.
  - **Reproduction (one line):** `.venv/bin/ruff check . && .venv/bin/python -m pytest -q tests/unit/test_validate_source_path_fuzz.py tests/unit/test_validate.py`
- **DONE-WHEN CHECK:**
  - ✅ N1 fixed with a test that failed before: 14 failed → 30 passed (above); `test_nul_byte_in_source_path_is_a_coded_error_not_a_crash` + fuzz params + CLI test.
  - ✅ ADR-0004 + INDEX: `company/decisions/ADR-0004-source-has-audio.md` (Proposed; Assurance and Creative named as consulted); INDEX row added.
  - ✅ ARCHITECTURE wording corrected: now "Nothing fills it yet: ingest is a stub that writes no timeline. It is to be filled by ingest from ffprobe: next ingest brief."
  - ✅ ruff + pytest green (3.14 and 3.12, above).
  - ✅ LOG entry: `company/positions/03-engineering/LOG.md`.
- **Other N-items:**
  - N3 (stale cache real-to-real): **DEFER**; Operator please add "bump `stage_version`" as a Done-when on the first Phase 1 stage brief.
  - N4 (docstring "never stats"): **FIX** in this change ("Never opens the file; it resolves path metadata only").
  - N5 (fails-before via ImportError): **WONTFIX** for H-0009 as Assurance allowed; applied the lesson here (new module imports only existing symbols, failures are by assertion/exception).
- **DEVIATIONS FROM BRIEF:**
  1. Also hardened the rule-1 `is_file()`/`_sha256()` step (OSError → `E_SOURCE_MISSING`, "cannot be read"). Reason: on Python 3.12 `Path.is_file()` re-raises errnos other than ENOENT/ENOTDIR/EBADF/ELOOP (e.g. EACCES), the same crash class as N1. No new code, no schema change. ENAMETOOLONG case passes on both 3.12 and 3.14.
  2. Control characters are rejected policy-wide (C0, DEL, C1), not only NUL, as the review's required action allowed ("a NUL (or any control character)"). A legitimately named file with a newline can no longer be a source; I judge that acceptable.
  3. Schema file untouched (no schema change, so no escalation). Its `has_audio` description still says "Filled from ingest metadata (ffprobe), not by the LLM"; I read that as the provenance rule, not a claim it is filled today, so I left it. Assurance may disagree (see Q2).
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. Operator: add to the next ingest brief the Done-when "write `has_audio` from `probe()`; rerun H-0009 Part F `ha_absent` → render exit 0", and to the first Phase 1 stage brief "bump `stage_version`" (N3).
  2. Assurance: is the schema description wording for `has_audio` acceptable under I-1, or should a follow-up T1 reword it to "to be filled from ingest metadata"?
  3. Creative: acknowledge ADR-0004 (informed, no action needed unless no-speech footage needs more than silence, e.g. a music bed).
- **CONFIDENCE:** High (biggest reason for doubt: the 3.12 run used the dev requirements only, not the full runtime lock; validator code paths do not depend on the runtime lock).
- **NEXT RECOMMENDED STEP:** Assurance spot re-check of N1 (rerun `scripts/adv.py` NUL row and the CLI), then Operator commits Task B with `Reviewed-by:`.
