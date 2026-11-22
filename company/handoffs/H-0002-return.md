# RETURN H-0002
- **From:** assurance-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  - RR-006..RR-009 added for the four Founder clips (G-C01..G-C04), each `UNVERIFIED – source unknown, not usable` (I-9).
  - RR-010 added for `quarantine/Instagram-dataset-samples-main.zip`: same status, "quarantined, never opened".
  - RR-001 Noto Sans Arabic moved from candidate/pending to **recorded**: SIL OFL 1.1, v2.005, commercial use Yes, proven from two primary sources on this machine.
  - Media in `data/golden/` and `quarantine/` were listed by name only (`ls`); nothing was opened, probed, decoded or hashed.
- **ARTIFACTS (paths):**
  - `/workspaces/Efficient_Video_Editor/company/positions/05-assurance/DATA_RIGHTS.md` (RR-001 updated; RR-006..RR-010 new; note on derived cache artifacts)
  - `/workspaces/Efficient_Video_Editor/company/positions/05-assurance/LOG.md` (entry appended)
- **EVIDENCE (commands + outputs / metric files):**
  - `ls data/golden/ quarantine/` → `Download.mp4`, `Download (1).mp4`, `Download (2).mp4`, `Download (3).mp4`, `MANIFEST.md`; `Instagram-dataset-samples-main.zip`. Mapping to G-C01..04 is from `data/golden/MANIFEST.md`.
  - Embedded name table (stdlib parser, script in scratchpad; `fontTools` and `otfinfo` are not installed, `fc-query` only exposes family/version), identical for both Regular and Bold:
    - ID 0 `Copyright 2015-2020 Google LLC. All Rights Reserved.` · ID 5 `Version 2.005` · ID 7 `Noto is a trademark of Google LLC`
    - ID 13 `This Font Software is licensed under the SIL Open Font License, Version 1.1. ...` · ID 14 `http://scripts.sil.org/OFL`
  - `fc-query` → `Noto Sans Arabic|Regular|131400|GOOG` and `...|Bold|131400|GOOG`
  - `/usr/share/doc/fonts-noto-core/copyright` lines 7-14: `Files: *` / Copyright Google Inc./Google LLC / `License: OFL-1.1`; OFL text clauses 1-4 (no selling alone, Reserved Font Name, no endorsement).
  - `dpkg -s fonts-noto-core` → Version `20201225-2`
  - `sha256sum`: Regular `504d7407d86875acf7d04dfaa0fd7524d0b8797723bc4aa18022f29db25b0b6e`, Bold `ded6fc7359ca36d15d7aab9ef0c066e21ce48b26a069994d6602fa2cb9a1b952` (system font files, not golden media)
  - `git check-ignore -v`: `cache/`, `data/golden/*`, `quarantine/` all git-ignored, so no unverified media or derivatives are tracked.
- **DONE-WHEN CHECK:**
  - ✅ 4 rows for `Download.mp4`, `Download (1).mp4`, `Download (2).mp4`, `Download (3).mp4`, each cross-referenced to G-C01..G-C04, status UNVERIFIED – source unknown, not usable: RR-006..RR-009 in DATA_RIGHTS.md
  - ✅ 1 row for the quarantined zip: RR-010
  - ✅ RR-001 Noto Sans Arabic: license name (SIL OFL) + version (licence 1.1; font v2.005) + where the proof came from (embedded name ID 13/14 + Debian copyright file) + commercial use Yes + date recorded 2026-11-22
  - ✅ LOG.md entry appended
- **FINDINGS:**
  1. **S2: derived artifacts of unverified media exist.** H-0001 produced `cache/Download*-*/` (meta, scenes, transcripts) and 144-px contact sheets from RR-006..009. Under I-9 they inherit UNVERIFIED status. Required action: nobody uses them for outputs, rubric anchors or golden-set work until rights are cleared; if the Founder can't prove rights, delete them along with the media. Verify by: the register note (added) plus a check at the M0 gate that no tracked artifact references them. I did not write a HALT: the files are local, git-ignored and were used only to profile intake, not to produce outputs.
  2. **S3: the manifest's Rights ID column says `NONE` for G-C01..04.** It should cite RR-006..RR-009. MANIFEST.md belongs to Creative and was read-only for this brief. Required action: Creative updates the Rights ID cells. Verify by: grep the manifest for RR-006..009.
  3. **S3: the Amiri font (`fonts-hosny-amiri`) is in the CLAUDE.md setup but has no register row.** It cannot be used until it has one. Not researched (out of scope).
- **DEVIATIONS FROM BRIEF:** I read the CHARTER/CHECKLISTS position files (standard first step). I added a register note saying derived cache artifacts inherit UNVERIFIED status. I checked git-ignore status by path name only. No other deviations; RR-002..005 untouched.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (Founder) Origin of and permission for the four clips and the Instagram zip. Proof lifts RR-006..010.
  2. (Creative) Update the MANIFEST Rights ID cells to RR-006..RR-009.
  3. (Operator) Should Amiri get a register row before EXP-006, if EXP-006 might use it as a fallback font?
- **CONFIDENCE:** High (biggest reason for doubt: the "commercial use Yes" call relies on my reading of the OFL 1.1 text, not on legal counsel; the OFL is widely understood to allow use in rendered output).
- **NEXT RECOMMENDED STEP:** Operator unblocks EXP-006 (H-0006) on the font, restricted to Noto Sans Arabic v2.005 from fonts-noto-core 20201225-2. The Founder answers Q1.
