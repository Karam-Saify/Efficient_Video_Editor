# ADR-0022: Data claims need a Founder spot-check before they count as evidence
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (S1 correction to the H-0024 catalog) · **Door:** two-way · **Review:** M1 gate

**Decision:** Any claim about data (language, speech presence, audio/visual quality, duplicates, content type) produced automatically or by an agent is a *candidate label* until the Founder spot-checks it. Only then can it count as evidence in a decision, an experiment or a report. Founder labels override automatic labels. Ground truth for the dev set is `quarantine/dev/LABELS.csv` (git-ignored, Founder-filled).

**Trigger:** the H-0024 dev catalog labelled clips with Arabic speech as English or no-speech (faster-whisper auto-detect on music-heavy audio). Downstream work used those labels as facts (H-0025 demo clip choice, H-0027 cost "no-speech" counts, H-0029 "3 English speech clips").
