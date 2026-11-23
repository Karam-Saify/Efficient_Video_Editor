# H-0008 return: rights record for Noto Sans Regular (libass Latin fallback)

STATUS: DONE

SUMMARY
- EXP-006 render.log lines 135-136 show libass falling back from Noto Sans Arabic to `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf` for glyph 0x69 ('i'). Under I-9 it needed its own record.
- Added RR-011 to the rights register. License **SIL OFL 1.1** is confirmed from two primary sources on this machine. The status is recorded, not pending.
- Commercial use: yes. Restrictions: the "Noto" reserved name/trademark, and the font may not be sold by itself. Same terms as RR-001.

ARTIFACTS
- company/positions/05-assurance/DATA_RIGHTS.md (row RR-011 added after RR-010)
- company/positions/05-assurance/LOG.md (H-0008 entry appended)

EVIDENCE
- `sha256sum`: 89c3c497f618fdaa0b2d1e98fef93582f28c71debd2c4a8cdf41f190ced2909d (512672 bytes)
- `dpkg -S` gives fonts-noto-core. `dpkg-query` gives fonts-noto-core 20201225-2.
- `fc-query`: family Noto Sans, style Regular, fontversion 131334. fc-query does not show the license fields. fontTools is not installed, so I read the name table with a stdlib struct parser.
- name table (platform 3, 0x409) entries:
  - ID 0: "Copyright 2015 Google LLC. All Rights Reserved."
  - ID 5: "Version 2.004; ttfautohint (v1.8.3)…"
  - ID 7: "Noto is a trademark of Google LLC."
  - ID 13: "This Font Software is licensed under the SIL Open Font License, Version 1.1. …"
  - ID 14: http://scripts.sil.org/OFL
- `/usr/share/doc/fonts-noto-core/copyright`: stanza `Files: *` (Google Inc. 2010,2012-2020; Google LLC 2015-2020) has `License: OFL-1.1`.
- Not committed, as instructed. I did not access data/heldout/ or touch H-0004 files.

OPEN QUESTION
- The fallback was implicit. Should EXP-006 / the renderer pin the Latin font explicitly, so that another host cannot pick an unrecorded font? That decision belongs to Engineering/Creative.
