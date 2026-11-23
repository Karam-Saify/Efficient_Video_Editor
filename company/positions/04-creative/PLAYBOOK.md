# Playbook: Creative & Arabic Editorial

## SOP-C1: Golden-set curation (M0)
1. Founder supplies candidate videos. For each: rights (owner/licensed + proof) go to Assurance first; no rights, no entry.
2. Select 5 golden videos covering the real mix: dialect vs MSA, talking-head vs avatar vs B-roll,
   good vs bad audio, 2–10 min. Then 3 *different* videos for held-out, handed to Assurance to seal.
3. For each, fill `data/golden/MANIFEST.md`: id · duration · speakers · dialect · audio quality (1–5) ·
   content type · orientation · rights record ID · notes on what a good Short would contain.
4. If available, add 1–2 human-edited reference Shorts per golden video (the "answer key").

## SOP-C2: Reviewing a pipeline output (T1 inside a brief, T2 at experiments)
1. Watch on a phone-sized preview (e.g. 360×640) **muted** first, then with sound.
2. Score with `RUBRIC.md`. Write one sentence of evidence per item (timestamp + what you saw).
3. Run `ARABIC_QA.md` checks on captions.
4. Write the result to `experiments/EXP-x/ratings.csv` or the T2 return.

## SOP-C3: Translating a style need into engineering
Write: the rule · why (rubric item) · an example frame · proposed schema field · how to validate it.
Engineering confirms or opens an ADR. Never ask for "make it more dynamic" without these fields.

## SOP-C4: Calibration with the Founder
Every milestone: 3–5 outputs, both rate blind, compute agreement (with Research), rewrite weak anchors.
Record what the Founder likes and dislikes in his own words in `FOUNDER_TASTE.md`. This becomes few-shot guidance for the scoring prompt.
