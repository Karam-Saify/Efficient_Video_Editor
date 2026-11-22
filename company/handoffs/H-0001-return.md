# H-0001 return: golden-set intake profile (Operator, T1 tagging)
STATUS: PARTIAL (blocked on rights, I-9)
SUMMARY:
- 4 Founder-supplied clips profiled locally (ffprobe, volumedetect, ffmpeg scene score, faster-whisper large-v3-turbo int8 CPU, PySceneDetect). No video or frames sent to any LLM except 4 tiny 144-px contact sheets used once to label content type.
- All 4 are **finished, already-edited TikTok Shorts** (9:16, 576×1024, 18–84 s) with visible third-party watermarks, **not** 2–10 min raw sources as SOP-C1 expects.
- 2/4 have no speech (music only), so a transcript-driven cut does nothing; 2/4 are Lebanese dialect, one heavily code-switched with English.
- No rights records exist → under I-9 they cannot enter the golden set or be used for outputs.
ARTIFACTS: data/golden/MANIFEST.md (4 DRAFT rows G-C01..04) · cache/<video_id>/{meta,scenes,transcript.large-v3-turbo}.json
EVIDENCE: `.venv/bin/python -m src.ingest "data/golden/<file>.mp4"` per clip; ASR RTF 0.8–2.9 on CPU (see cache meta).
FINDINGS USEFUL BEYOND THIS INTAKE (inputs for Research/Engineering, not decisions):
1. **Whisper hallucination on music/silence**: "اشتركوا في القناة" emitted with p=0.93 on a music-only clip and in a 3 s trailing silence. Ingest needs a filter (blocklist of known phrases + no-speech prob + music detection) → candidate risk + EXP-001 metric.
2. **Code-switching**: forced `--language ar` turns English words into mixed-script garbage (Latin/Cyrillic/Vietnamese characters inside Arabic lines). EXP-001 should compare `ar` vs auto vs per-segment detection on Lebanese+English.
3. **No-speech input type is real**: promo/food clips need a visual/beat path (scene + audio-onset selection), not transcript scoring. Affects ROADMAP scope (Product).
4. These clips are high-value as **style references ("answer key")**: cut rate 0.04–1.1 scenes/s, sticker overlays, on-screen text; worth encoding as rubric anchors, if rights allow.
DEVIATIONS FROM BRIEF: no formal brief (Founder asked directly in session). Manifest rows marked DRAFT for Creative to confirm.
OPEN QUESTIONS:
1. (Founder) Do you own or have permission for these clips (e.g. you work with Two Media / Atyab Farooj)? If yes, give proof → Assurance records RR-0xx.
2. (Founder) Can you supply 5 raw, unedited 2–10 min sources (+3 for held-out)? These finished Shorts cannot satisfy M0 criterion 0.4.
3. (Product) Is the no-speech promo type in scope for M1?
CONFIDENCE: High on measurements; Medium on content labels (from 4 thumbnails each).
NEXT RECOMMENDED STEP: Founder answers Q1–Q2; Research folds findings 1–2 into EXP-001 prereg.
