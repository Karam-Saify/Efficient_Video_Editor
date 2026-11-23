# BRIEF H-0002
- **To:** assurance-lead
- **Tier / Milestone:** T1 / M0
- **Date:** 2026-11-22

1. **Objective (with why):** Record the rights status of the four Founder-supplied clips as UNVERIFIED and not usable, and record the license for the caption font. Constitution I-9 says an asset with no rights record cannot be used, and EXP-006 (H-0006) needs the font license on file before it renders anything.
2. **Inputs (exact paths):**
   - `company/positions/05-assurance/DATA_RIGHTS.md` (register, row RR-001 is the font candidate)
   - `data/golden/MANIFEST.md` (G-C01..G-C04, read only)
   - `company/handoffs/H-0001-return.md` (intake profile, read only)
   - Installed font files: `/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf`, `/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf` and Debian copyright `/usr/share/doc/fonts-noto-core/copyright`
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - Do NOT open, probe, decode or hash the media in `data/golden/` and do not touch `quarantine/`. Founder order: list the files by name only (`ls` is fine). No video or images to the LLM.
   - Status for each of the four clips must be exactly: `UNVERIFIED – source unknown, not usable` until the Founder confirms origin.
   - Add a row for `quarantine/Instagram-dataset-samples-main.zip` with the same UNVERIFIED status and note "quarantined, never opened".
   - Font license must come from a primary source: the license text embedded in the font (`fc-query`/`otfinfo`/`fc-scan` name table) and/or the Debian copyright file. Record which source you used.
   - Do not edit the Constitution, ADRs or `data/heldout/`.
4. **Output (format + exact path):** Edited `company/positions/05-assurance/DATA_RIGHTS.md` (new rows RR-006..RR-010, RR-001 updated from candidate/pending to recorded, or flagged if the license can't be verified). Return in `company/handoffs/H-0002-return.md` (Return contract, OPERATING_MODEL §4).
5. **Done when:**
   - [ ] 4 rows for `Download.mp4`, `Download (1).mp4`, `Download (2).mp4`, `Download (3).mp4`, each cross-referenced to G-C01..G-C04, status UNVERIFIED – source unknown, not usable
   - [ ] 1 row for the quarantined zip
   - [ ] RR-001 Noto Sans Arabic: license name + version + where the proof came from + commercial use yes/no + date recorded
   - [ ] Append an entry to `company/positions/05-assurance/LOG.md`
6. **Out of scope:**
   - Deciding whether the clips can become usable; EXP-006 design; any code.
   - Other RR rows (Whisper, FFmpeg, Remotion, PuLP) unless trivially verifiable from the same session; do not research them.
7. **Effort budget:** max 25 tool calls · max 2 retries per failing action
8. **Escalate if:**
   - The Noto Sans Arabic license cannot be confirmed from a primary source on this machine (return BLOCKED for that row; Operator will decide).
9. **Termination condition:** The register is edited, the return file is written, and you stop. Do not commit.
10. **Consulted positions (from RACI) and what they must confirm:** Creative (RACI 18/23 R) is informed via the return; no pre-consultation needed for marking assets as *not usable*.
