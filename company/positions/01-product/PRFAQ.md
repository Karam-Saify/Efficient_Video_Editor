# PR/FAQ (draft v0, M0 exit criterion 0.9): chat-editor MVP, working backwards
Status: DRAFT v0 · Author: product-lead · Brief: H-0021 · Date: 2026-11-22
Evidence levels: every business claim here is **E0** (no interviews, no measured cost yet). Numbers are labelled
**[H]** = hypothesis or **[S#]** = external source (see Sources). No number here is a measured fact.

## 0. Reading of "chat-editor MVP" (stated because the Founder's pivot prompt was not available)
> A creator edits one Arabic Short by **chatting with an assistant**. Each chat message ("cut the intro",
> "make the captions bigger", "end on the joke") becomes a small change to `timeline.json`. The **LLM decides**
> what to change; **code enforces** every duration, timestamp and constraint (validator, MILP); a **local renderer**
> (FFmpeg / libass) produces the 1080×1920 MP4. Footage never goes to the LLM, only transcript text and timeline JSON.

Everything below depends on this reading. Each part of it is an open question for the Founder (§5).

## 1. Target user v0 and problem statement
**Primary (MVP) persona: P1, the Founder-creator** (`PERSONAS.md`). This is the only real persona. He runs an Arabic
channel, aims for 3 Shorts/week, is technical and cost-sensitive, and edits in his spare time.
**Secondary (hypothesis, not served by the MVP on purpose): P2, the Arabic explainer creator.** P2 talks to camera in dialect,
makes 1 long video/week, wants 3–5 Shorts from it and edits on a laptop. P3 (no-speech product clips) is **out** of the
MVP because the chat loop leans on the transcript.

**Problem statement (v0):** P1 wants to turn his long or avatar videos into publishable Arabic Shorts without paying
per-minute AI-editing fees. Today he has two options. Manual timeline editors take his scarce spare time. AI clip tools
charge a subscription and handle Arabic script and right-to-left captions badly or not at all: OpusClip's help centre says RTL languages,
Arabic included, are not supported [S2], and Descript transcribes only Latin-script languages [S4]. What he lacks is a way
to *say* what he wants in plain words and get a correct Arabic Short back, at close to zero marginal cost.
(The "badly or not at all" part is sourced for 2 tools only. A-07, that Arabic creators feel this pain, is Untested.)

## 2. Press release (dated at the M5 pilot; hypothetical)
**Headline:** Edit your Arabic Short by talking to it
**Sub-headline:** A chat-based editor for Arabic Shorts. You describe the change, it rewrites the edit and renders it on
your own laptop, with Arabic captions joined and right-to-left by default.

**Problem (in P1's words, paraphrasing `PERSONAS.md`):** "I have a 10-minute video and maybe an hour a week. The AI clip
tools want a monthly fee, and when they support Arabic at all, the captions come out broken. Editors cost time I don't have."

**Solution:** Drop in a video. The tool transcribes it, proposes a 30–60 s vertical cut and shows it. Then you chat:
"start with the question", "remove the part about prices", "45 seconds max". Each message becomes a small, checked
change to the edit. The tool never asks the AI to do arithmetic. It cuts exactly to the length you asked for and renders
locally, so the footage never leaves your machine. Undo is one message, because every version of the edit is kept.

**Founder quote (draft, for the Founder to rewrite):** "The video is not the thing we edit. The edit is. Once the edit is a
small text file, changing it costs a few words, not a cloud render."

**Creator quote (hypothetical, labelled as such; no real creator said this):** "I asked for three versions of the same
Short in five minutes and the captions were right every time."

**How to start (MVP):** Install locally, run one command on a video, then chat in the terminal or a minimal chat window. [H]

## 3. Customer FAQ (each answer tagged with the assumptions it rests on)
1. **What does it cost?** For the MVP, nothing beyond your own laptop and the LLM tokens per edit. The target is a cost per
   Short under 10% of paid tools [H, A-10]. For reference, OpusClip lists Starter at $15/month and Pro at $29/month [S1, S3], and
   Descript's Creator plan is reported at about $24/month billed annually [S5]. No price is set (pricing is out of scope).
2. **Is the Arabic good?** The captions use declared Arabic and Latin fonts with correct shaping and RTL. EXP-008 rendered all
   10 test strings with every gate passing, but the judgement FAILED its threshold (8/10 correct, 0 Sev-1). Caption quality
   is therefore *not yet proven* (`company/experiments/EXP-008.md`). Transcription quality on dialect is untested (A-02, EXP-001).
3. **How fast is it?** Target: under 5 min to render a Short on a CPU [H, A-06]. Not measured until M2 (2.5).
4. **Does my video go to the cloud / an AI?** No raw video or frames ever go to the AI. Only the transcript text and the edit
   file are sent (I-3). Rendering is local. The LLM provider still sees your transcript (open question Q6).
5. **Does it replace my editor?** No. It replaces the tedious first cut and the small revisions. It does not do colour, sound design,
   motion graphics or multi-track edits in the MVP [A-08].

## 4. Internal FAQ (what could kill us)
1. **What does one Short cost us?** Unknown. The model (SOP-P4) fills in from measurements at M2/M3. Hypothesised cost line per
   Short [all H]: ASR on CPU, a few minutes of compute for a 10-min source, done once and cached · scoring, done once at
   ~50-sentence windows · edit turns of **< 2k tokens each** (A-05, EXP-007 target) × an expected 3–5 turns · render < 5 min CPU (A-06)
   · **Founder minutes per Short: target < 15 [H]**, measured at M4 4.4. Kill signal: revision tokens grow with session length
   instead of staying diff-sized (A-05 invalidated).
2. **What if dialect ASR is bad?** Then the chat has nothing reliable to talk about. The M1 kill criterion applies: narrow
   to MSA, or allow a manual transcript import (A-02, EXP-001).
3. **What if the LLM edits break the timeline?** The validator rejects them. The M4 target is ≥ 90% valid on the first try, the rest fixed in 1 retry
   (EXP-003). If chat edits often fail, the MVP feels broken even when the renderer is fine.
4. **Competition?** OpusClip and Descript are strong in Latin-script markets and weak in Arabic RTL today [S2, S4]. This is a
   window, not a moat: either could ship RTL. Our durable bet is cost structure (edit-as-code, local render), not Arabic alone (A-07, A-10).
   Note: CapCut and other tools with Arabic caption support are **not yet logged** (`COMPETITORS.md` is empty).
5. **Rights and Founder time?** There is no usable footage yet (M0 0.4/0.5 blocked), so nothing can be shown or tested until the
   Founder supplies sources with rights (I-9). The Founder is also persona P1, the only tester and the signer, so the risk of
   building for one person is high. P2 evidence waits for M6 interviews.

**What we will NOT build in the MVP:** a GUI timeline editor · cloud rendering or a GPU path · sending video or frames to the LLM ·
P3 no-speech product clips · multi-language UI · accounts, billing or pricing · templates marketplace · auto-publishing to platforms ·
LLM-computed timings (I-4).

## 5. Open questions for the Founder (from the §0 reading)
1. Is the chat editor the **M4 loop** (on top of M1–M3), or does it **replace or come before** M2–M3 auto-selection? (Roadmap impact; see return.)
2. Who is the MVP for: only you (P1), or P2 creators from day one?
3. Where does the chat happen: terminal, a local web UI, or an existing chat app?
4. Does the MVP start from a proposed cut (MILP), or from the full video with the user cutting by chat?
5. Which footage type comes first: talking-head, HeyGen avatar, or mixed? (Root `CLAUDE.md` still says TBD.)
6. Is it acceptable for transcript text to go to a cloud LLM, or must the LLM be local too?
7. Lebanese dialect, MSA or code-switched with English/French: which do we optimise for first?
8. What is "done" for an MVP session: a published Short, or a rendered file you would publish?
9. Is there a per-Short token budget you want as a hard limit?

## Sources (web research 2026-11-22, via search summaries; not independently fetched, so treat as E1 at best)
- [S1] OpusClip pricing page: https://opus.pro/pricing
- [S2] OpusClip help centre, RTL languages: https://help.opus.pro/docs/article/does-opusclip-support-languages-right-left
- [S3] Castmagic, OpusClip pricing 2026: https://www.castmagic.io/blog/opus-clip-pricing
- [S4] Descript help, supported transcription languages: https://help.descript.com/script-editing/supported-transcription-languages.md
- [S5] Sonix, Descript pricing 2026: https://sonix.ai/resources/descript-pricing/
