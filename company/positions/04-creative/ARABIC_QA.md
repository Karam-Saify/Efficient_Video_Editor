# Arabic Correctness QA
Used at every T2 touching captions, ASR or text rendering, and in EXP-006.

## Severity
- **Sev-1 (blocks):** disconnected letters (missing shaping), reversed word/letter order, wrong word
  that changes meaning, missing lam-alef ligature, caption cut mid-word.
- **Sev-2:** digits in wrong direction inside a sentence, Latin words breaking line order, inconsistent
  dialect spelling within one Short, caption > 300 ms out of sync.
- **Sev-3:** punctuation direction (؟ vs ?), comma style (، vs ,), minor kerning.

## Test strings (EXP-006 must render all correctly)
| ID | String | What it tests |
|---|---|---|
| AR-01 | مرحبا بكم في القناة | basic shaping |
| AR-02 | لا، هذا ليس صحيحاً | lam-alef ligature + Arabic comma + tanween |
| AR-03 | السعر ٢٥٠ دولار فقط | Arabic-Indic digits in RTL |
| AR-04 | السعر 250 دولار فقط | Western digits inside RTL |
| AR-05 | جربت iPhone 16 Pro امبارح | Latin + digits mixed in Lebanese dialect |
| AR-06 | شو رأيك؟ | Levantine word + Arabic question mark |
| AR-07 | قُلْ هُوَ | diacritics (harakat) stacking |
| AR-08 | "اقتباس" و(قوسين) | quotes and brackets mirroring |
| AR-09 | ـــــــ مدّ ـــــــ | tatweel / kashida |
| AR-10 | ١٠٪ خصم – ٢٠٢٦ | percent sign + dash + digits |

## Check procedure
1. Render each string as a caption over a neutral frame at 1080×1920 → `render/frames_check/AR-xx.png`.
2. Creative inspects each image (zoom 200%); records pass/fail + severity in the T2 return.
3. Any Sev-1 → Creative veto on the change.

## Dialect policy (Founder to confirm)
- Spelling follows the speaker (Lebanese stays Lebanese: "شو"، "هيك"، "منيح"); captions do not "correct" dialect into MSA.
- English and French words stay in Latin script unless the style guide says otherwise.
