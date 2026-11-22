# REVIEW H-0009 (T2 re-review of the fix pass for H-0003 and H-0004), commit c179693
- **Reviewer:** assurance-lead · **Date:** 2026-11-22 · **Branch:** `t2/install-company-os`
- **Evidence:** `company/handoffs/H-0009-repro.txt` (Parts A to H). Scripts and media are in Assurance scratch and are not committed.

## VERDICT: ACCEPT WITH FIXES (S1: 0 · S2: 1 · S3: 4)
- **Task A (H-0003): mergeable now.** F1, F2, F3, F4 and F6 are closed by reproduction, and CI is green on all four jobs.
- **Task B (H-0004): mergeable after N1.** N1 is a validator crash on a NUL byte in a source path, and the new `E_SOURCE_PATH` code introduced it. This is the same defect class as H-0004 F1, which was also required before merge. The fix is about one line plus a test, and Assurance re-verifies it by rerunning one row of Part D.
- **Independence note.** A `grep` for "3.12" in the return printed the builder's CONFIDENCE line before this verdict was written. I disclose this. The verdict rests only on Parts A to H.

## Reproduction (L1 to L4)
| Check | Result | Repro part |
|---|---|---|
| Fresh 3.12.3 venv, full runtime lock + dev | installs; `pip check` clean; `pip freeze` shows only `opencv-python==5.1.0.95` | A |
| ruff (3.12 full, 3.14 dev) | `All checks passed!` on both | B |
| pytest 3.12 full lock, `VAC_FULL_RUNTIME=1` | 116 passed | B |
| pytest 3.14 dev lock | 108 passed, 8 skipped (the runtime-import tests, with a stated reason) | B |
| Runtime gate is real | 3.14 dev lock with `VAC_FULL_RUNTIME=1` gives 7 failed (the imports are actually exercised) | B5 |
| New tests against parent code | 5 failed plus 1 collection error (test_validate: ImportError). So the cache, pins and opencv tests fail before the fix. The validator tests only fail before the fix by import, and Part D covers them | C |
| L4 render, silent source with `has_audio:false`, AR caption with RLM and Arabic-Indic digit | validate 0, render 0; 1080x1920, stereo, 4.000 s; silent clip mean -91 dB, voiced clip -24 dB | F |
| CI run 45047570814 (headSha c179693) | test 3.12 / 3.14 and runtime 3.12 / 3.14 all succeed; runtime jobs install coinor-cbc 2.10.11, `pip check` clean, 116 passed | H |

## Earlier findings: action confirmed
| Finding | Owner action | Assurance check (rerun) | Status |
|---|---|---|---|
| H-0003 F1 floor | FIX | `requires-python >=3.12`, ruff py312, and the comments name all 5 pins. The full lock installs on 3.12 (A), so the per-pin check has 0 FAIL | **Closed** |
| H-0003 F2 CI | FIX (was DEFER) | Both matrix legs green, and `pulp` is imported and a CBC MILP solved in CI (H) | **Closed** |
| H-0003 F3 stale stub cache | FIX | Stub run, then stub skip, then real work on the same inputs gives `ran=True` with outputs; real again skips; a `__version__` change reruns (D). Residual risk: see N3 | **Closed** |
| H-0003 F4 opencv twin | FIX | one opencv line, `pip check` clean (A) | **Closed** |
| H-0003 F5 bad JSON | FIX | empty, non-JSON, non-UTF-8, directory and missing file each give one `validate: error:` line and exit 1. Stage mode writes no manifest (E) | **Closed** |
| H-0003 F6 out inside input | FIX | `--out` inside the input dir, equal to it, or under a symlinked input each give StageError, exit 1 (E) | **Closed** |
| H-0003 F7, F9 | DEFER | recorded in the return table | Recorded |
| H-0003 F8, F10 | WONTFIX | F8 is documented in ARCHITECTURE.md ("Stage cache known properties") | Recorded |
| H-0004 F1 float ms | FIX | `in_ms` 1000.0, float `out_ms` with off duration (the old crash), target 2500.0, fps 30.0, width 1080.0, `True`, NaN and inf each give `E_SCHEMA`, with no crash. The `{:+}` format no longer crashes (D) | **Closed** |
| H-0004 F2 silent source | FIX (schema field) | `has_audio:false` renders with a silent stereo track (F). If the field is absent on a silent source, validation still passes (exit 0) and ffmpeg fails (render exit 1, F). See N2 | **Closed for the field; residual in N2** |
| H-0004 F3 path confinement | FIX (was DEFER) | Absolute paths, `..` escapes, golden, quarantine, `data/./`, `data//`, `src/../`, a symlink out of the repo and a symlink into golden each give `E_SOURCE_PATH`. `data/goldenX` is correctly not matched. base_dir outside the repo is rejected. strace shows no `openat` of a quarantined file that has a sha256 (D, E). See N1 and N4 | **Closed except N1** |
| H-0004 F3, held-out root | FIX | I did not exercise this adversarially: the policy hook blocks any command that names the held-out path outside a gate, and I did not work around the hook. Code inspection shows `PROTECTED_SOURCE_ROOTS` has 3 entries including the held-out root, in the same loop that passes for golden and quarantine. The builder's `i7`/unit tests cover it | Closed by inspection |
| H-0004 F4 e6_captions | FIX (deprecated) | exits 2 with a clear message before doing any work (G) | **Closed** |
| H-0004 F8 overlap wording | FIX (ADR) | ADR-0003 is Proposed. Its context matches `E_OVERLAP` (same-source range reuse) | **Closed** (decision pending) |
| H-0004 F5, F6, F7, F10(iv) | DEFER | recorded | Recorded |
| H-0004 F9, F10(i-iii) | WONTFIX | recorded | Recorded |

## Deviations checked
- **`sources[].has_audio` (optional boolean, default true).** Rejects `"yes"` with `E_SCHEMA`. The adapter passes it through and the graph uses silence. This is a schema change, see N2.
- **ARCHITECTURE.md edit.** It does **not** change a stage boundary: there is no new stage and no stage's inputs or outputs change. It does document a schema change, and that same file (line 18) says schema changes need an ADR. See N2.
- **ADR-0002.** Status Accepted, decider "Founder, delegated to the Operator 2026-11-22", options and reversal plan present, listed in INDEX. Consistent with Assurance's H-0003 risk opinion (option a).
- **ADR-0003.** Proposed, in INDEX.
- **coinor-cbc in CI.** Installed only in the runtime job (2.10.11), and a CBC solve passes there. The runtime job does not run ruff, but the test job does on both versions, so this is acceptable.
- **Invariant scan (I-1 to I-10).** No protected paths were touched (held-out, golden, quarantine, CONSTITUTION, `company/experiments/`, frames_check, exp006_render, ADR-0001). The diff contains no secrets. Commit trailers are present (Role and Tier). The held-out set was not accessed, so there is no ACCESS_LOG entry.

## Adversarial attempts (more than 30, Parts D and E)
Float, bool, NaN and inf ms values · 15 path shapes, including symlinks and NUL · base_dir outside the repo · 5 bad-JSON inputs · 3 out-in-input shapes · Arabic RTL caption with RLM and Arabic-Indic digits in a real render · silent source with the field set and with it absent.

## Findings
| # | Sev | Finding | Evidence | Required action | How the fix is verified |
|---|---|---|---|---|---|
| N1 | **S2** | **Validator crash on a NUL byte in a source path, introduced by the fix.** `_source_path_problem` calls `(base_dir / raw).resolve()`, which raises `ValueError: embedded null byte`. `"\u0000"` is valid JSON, so an LLM or a JSON tool can emit it. `validate()` and the renderer (which calls `validate`) then crash with a traceback instead of returning a coded issue. Before this commit, `Path.is_file()` swallowed the ValueError, so the result was `E_SOURCE_MISSING`. | Part D `path 'a\x00b': CRASH ValueError`; Part E CLI traceback, exit 1 | **FIX before merging Task B.** Return `E_SOURCE_PATH` for a NUL (or any control character) or for any `ValueError`/`OSError` from `resolve()`, and add a unit test | Rerun `scripts/adv.py`: the NUL row gives `E_SOURCE_PATH`, and the CLI prints one line with exit 1 and no traceback |
| N2 | S3 | **The `has_audio` schema field has no ADR, and the docs claim it is populated.** ARCHITECTURE.md l.18 and H-0004 F2's required action both say a schema field needs an ADR. ARCHITECTURE and the schema description say "ingest fills it from ffprobe", but ingest is a stub that writes no timeline, so the claim is not yet true (I-1). If the field is absent on a silent source, validation still passes and the render fails. | Part F `ha_absent`: validate 0, render 1 (`Stream specifier ':a'`) | Before the M0 gate: write a short ADR-0004 (Proposed, two-way) for `has_audio`. Reword the docs to "must be filled by ingest/edit (ticket)". Add a Done-when to the first real ingest or edit brief that writes `has_audio` from `probe()`. Confirm Creative was informed (brief field 10) | The ADR is in INDEX. Rerun Part F `ha_absent` after ingest fills the field: render exit 0 |
| N3 | S3 | **Residual stale cache for real-to-real changes.** The stub trap is closed, but changed real logic still skips when neither `stage_version` nor `__version__` (`0.1.0`, never bumped by any process) changes. | Part D last line: `ran=False` | **DEFER.** Add a Done-when to every real-logic brief: "bump `stage_version`". Optionally, a test that each stage with real `work` has `stage_version != "0"` | That Done-when line appears in the first Phase 1 stage brief |
| N4 | S3 | The `_source_path_problem` docstring says it "never opens or stats the file". In fact `resolve()` runs lstat/readlink on the path components. strace confirms the file content is never opened, so this is not an I-6/I-9 breach, but the claim is inaccurate. | Part E strace: 0 `openat` of q.mp4; code reading | Reword the docstring ("never opens it; resolves path metadata only"). This can go in the same commit as N1 | Read the docstring |
| N5 | S3 | **Weak "fails before" evidence for the validator.** The new validator tests fail against the parent only through an ImportError at collection, not through assertions. | Part C | **WONTFIX ok** this time, because Part D independently reproduces the before-and-after behaviour. In future, import new symbols inside the test or put them in a separate test module | n/a |

## Open questions
1. Operator: should N1 hold the Task B merge (Assurance's view: yes, it is cheap), or merge now with N1 as the very next T1?
2. Operator/Creative: was Creative informed of `has_audio` (brief field 10)? I found no evidence either way.
