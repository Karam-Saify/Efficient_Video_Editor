# Example ops files (H-0025)

Input for `python -m src.demo --video <clip> --ops examples/ops/<file>.json --out out/`. The format is documented
in `src/demo/__init__.py`. Every time is a rule resolved by code (word / segment / fraction of the current
timeline), so the files work on any clip with enough speech.

| file | does |
|---|---|
| `trim_and_style.json` | keep first word start .. end of the 3rd segment; `hook` preset |
| `delete_words_zoom.json` | cut the 2nd and 3rd words (video + captions); `clean`; zooms at word 4 and at 60 % |
| `fit_30s.json` | `bold_box`; shorten to 30 s (silence first, then tail); zoom on the first word |
