# Data and Asset Rights Register
No record → the asset cannot be used (Constitution I-9). Owner: Assurance.

| ID | Type | Name / file | Source | Owner | License + proof | Commercial use | Attribution | Restrictions | Recorded |
|---|---|---|---|---|---|---|---|---|---|
| RR-001 | font | Noto Sans Arabic Regular + Bold, v2.005 (`/usr/share/fonts/truetype/noto/NotoSansArabic-{Regular,Bold}.ttf`, Debian pkg fonts-noto-core 20201225-2; sha256 Regular 504d7407…b6e, Bold ded6fc73…6e) | Debian fonts-noto-core (upstream github.com/googlei18n/noto-fonts) | Google LLC (© 2015-2020) | **SIL OFL 1.1**. Proof (primary, on this machine): (a) embedded OpenType `name` table ID 13 "licensed under the SIL Open Font License, Version 1.1", ID 14 http://scripts.sil.org/OFL, both files, read with a stdlib name-table parser (fontTools/otfinfo not installed; fc-query gave family/version only); (b) `/usr/share/doc/fonts-noto-core/copyright` stanza `Files: *` → `License: OFL-1.1` | Yes (OFL permits commercial use and embedding in rendered video; font may not be sold by itself) | Not required in rendered output; keep copyright + OFL text if the font file is redistributed | No modified version may use the name "Noto" (Reserved Font Name / Google trademark); do not sell the font alone | 2026-11-22 (H-0002, recorded) |
| RR-002 | model | (candidate) Whisper weights | OpenAI GitHub | OpenAI | MIT, verify | Yes | Keep license | — | pending |
| RR-003 | library | (candidate) FFmpeg | ffmpeg.org | FFmpeg devs | LGPL/GPL depending on build, verify build flags | Check | Yes | GPL components | pending |
| RR-004 | library | (candidate) Remotion | remotion.dev | Remotion | **Special company license: may need a paid license for companies above a size; verify** | Check | — | — | pending |
| RR-005 | library | PuLP / CBC | COIN-OR | COIN-OR | MIT / EPL, verify | Yes | — | — | pending |
| RR-006 | video | `data/golden/Download.mp4` (golden G-C01) | Founder-supplied; origin not stated. H-0001 notes third-party TikTok watermark (@atyab_farooj) | Unknown | none | No | — | **UNVERIFIED – source unknown, not usable** | 2026-11-22 (H-0002) |
| RR-007 | video | `data/golden/Download (1).mp4` (golden G-C02) | Founder-supplied; origin not stated. H-0001 notes third-party TikTok watermark (@atyab_farooj) | Unknown | none | No | — | **UNVERIFIED – source unknown, not usable** | 2026-11-22 (H-0002) |
| RR-008 | video | `data/golden/Download (2).mp4` (golden G-C03) | Founder-supplied; origin not stated. H-0001 notes agency content ("Two Media") | Unknown | none | No | — | **UNVERIFIED – source unknown, not usable** | 2026-11-22 (H-0002) |
| RR-009 | video | `data/golden/Download (3).mp4` (golden G-C04) | Founder-supplied; origin not stated | Unknown | none | No | — | **UNVERIFIED – source unknown, not usable** | 2026-11-22 (H-0002) |
| RR-010 | dataset (archive) | `quarantine/Instagram-dataset-samples-main.zip` | Unknown | Unknown | none | No | — | **UNVERIFIED – source unknown, not usable**; quarantined, never opened | 2026-11-22 (H-0002) |

Notes: "pending" rows are candidates whose license must be checked from the primary source before use.
RR-004 is flagged because Remotion's licensing differs from typical open-source packages. Check it before M1's renderer ADR.
RR-006..RR-010: status is UNVERIFIED until the Founder supplies proof of origin/permission. Derived artifacts of RR-006..009
(`cache/Download*-*/`: meta, scenes, transcripts from H-0001) inherit the same status and must not be used for outputs, rubric anchors or the golden set.
