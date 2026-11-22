# Quality Rubric v1 (draft, to be calibrated in M0)
Scale 1–5 per item; anchors define 1, 3 and 5. Raters score **blind** to which system produced the Short.
Overall score = weighted mean. Any item scored 1 marked ⛔ = automatic fail regardless of the mean.

| # | Item | Weight | 1 (bad) | 3 (acceptable) | 5 (excellent) |
|---|---|---|---|---|---|
| Q1 | **Hook (0–1.5 s)** | 20% | Opens on filler, greeting or silence | Opens on a relevant statement | Opens on a surprising claim, question or payoff that creates a curiosity gap |
| Q2 | **Coherence** | 20% | Ideas cut mid-thought; references missing context ("as I said…") | Understandable with minor jumps | Self-contained mini-story: setup → point → payoff |
| Q3 | **Cut quality** | 10% | Cuts mid-word or mid-breath; audible pops | Clean on words, some awkward pauses | Cuts on natural breath points; pace feels intentional |
| Q4 | ⛔ **Arabic caption correctness** | 15% | Disconnected letters, reversed order, wrong words | Correct, minor timing lag | Correct, synced word-level, dialect-faithful spelling |
| Q5 | **Readability muted** | 10% | Captions too long, too fast, or in UI zones | Readable, occasionally dense | ≤ 2 lines, ≤ ~12 words per screen, in safe zone, high contrast |
| Q6 | **Pacing / retention design** | 10% | Monotonous; one shot > 8 s with nothing changing | Some visual change | A change every 2–4 s (cut, zoom, caption emphasis) that serves the content |
| Q7 | **Ending** | 5% | Abrupt or trailing | Clear end | Strong payoff or loop-friendly ending |
| Q8 | ⛔ **Technical integrity** | 10% | A/V desync, black frames, wrong aspect ratio | Minor issues | Flawless 1080×1920, synced, consistent loudness |

## Calibration protocol (Research co-owns)
1. Pick 3 reference Shorts (one good, one average, one weak, by Founder's judgment).
2. Founder and creative-lead score independently → `calibration-001.csv` (columns: short_id, rater, Q1..Q8).
3. Compute agreement per item (Spearman ρ). Items with ρ < 0.4 get rewritten anchors.
4. Repeat until all items ≥ 0.4; target ≥ 0.6 by M3.
