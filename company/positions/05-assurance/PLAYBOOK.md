# Playbook: Quality, Validation & Risk

## SOP-A1: T2 review
1. Read the BRIEF (not the builder's narrative) and the Done-when list.
2. Fresh clone or `git stash` + checkout the branch; run the reproduction command exactly. Save output to `handoffs/<id>-repro.txt`.
3. Verify each Done-when item independently: ✅ / ❌ + how verified.
4. **Multi-level verification ladder:** run each level that applies:
   L1 unit tests → L2 schema validation of outputs → L3 determinism (run twice, compare hashes) →
   L4 render check (frames_check PNGs exist, duration correct via ffprobe) → L5 Arabic QA strings (if captions touched) →
   L6 rubric spot-check by Creative (if output-visible) → L7 cost check (tokens/minutes vs previous run).
5. Adversarial pass: ≥ 3 break attempts (empty input, very long input, Arabic edge string AR-05/AR-08, out-of-range times).
6. Invariant scan I-1…I-10 against the diff.
7. Write `templates/REVIEW.md` → `handoffs/<id>-review.md`. Verdict + numbered findings with severity.
8. Owner responds to every finding. Re-review only the fixed findings.

## SOP-A2: T1 sampling
Each milestone, sample 1 in 5 T1 log entries per position (random by line number with a recorded seed).
Check: evidence path exists and supports the claim. Record in `AUDIT_PLAN.md`. Two failures in a
position's sample → that position's T1 work becomes T2 for the rest of the milestone.

## SOP-A3: Held-out custody
- `data/heldout/` contents are git-ignored; only `MANIFEST.md` and `ACCESS_LOG.md` are tracked.
- Each access: date · gate · purpose · commands · who. Any access outside a gate = Sev-1 incident (VC-1).

## SOP-A4: Data and asset rights intake
For every video, music track, font, model and dataset, before first use:
ID · type · source/URL · owner · license (name + link/proof) · commercial use? · attribution needed? ·
restrictions · date recorded. No record → asset may not enter the repo, cache or a render.

## SOP-A5: Gate evidence pack and record
See `company/governance/GATE_PROTOCOL.md`. Assurance builds the pack, reproduces every criterion,
runs held-out (M3+), collects blind reviews, writes the record, updates the risk register, and checks
dissent predictions from the previous gate in `CALIBRATION.md`.

## SOP-A6: Incident handling
Open `INC-<n>` within the session the issue is found. Blameless, 5-whys, action items with owners
and a "verified by" field. Close only when actions are verified.

## SOP-A7: Commit-trailer audit (every gate)
`git log --format='%h %s %(trailers:key=Role,valueonly) %(trailers:key=Tier,valueonly)'` for the milestone range.
Flag: T2 commits without `Reviewed-by`; commits in `src/` by a non-engineering role; commits touching locked files.
