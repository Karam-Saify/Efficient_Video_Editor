# Evidence Library
Format: see PLAYBOOK SOP-R1. Seeded from the founding research session (2026-11-21).

## ELLMPEG (MMSys '26) · 10.1145/3793853.3795760
- Claim relevant to us: an agentic LLM can generate executable FFmpeg/VVenC commands locally with zero API cost.
- Setting: English queries, 480-prompt dataset, open models 2–8B, CPU edge device.
- Method: tool-aware RAG over FFmpeg/VVenC docs → generate → execute locally → self-reflect → retry.
- Key numbers: Qwen2.5 + ELLMPEG ≈ 78% command-generation accuracy; self-reflection lowers tokens/sec by about 26–40%.
- Limitations: command generation only, not editorial decisions; CPU latency is high.
- Transferability: High for the "execute → verify → fix" loop.
- Adopt: validator-feedback retry loop (max 2). Reject: RAG over FFmpeg docs (we use a schema instead of raw commands).

## EditDuet (SIGGRAPH '25) · 10.1145/3721238.3730761
- Claim: Editor + Critic LLM agents can produce B-roll timelines from a large footage collection.
- Setting: English documentary footage (280+ min), Llama 3.1-8B both agents, structured generation.
- Method: TW-FINCH sub-clip clustering; per-segment caption (LLaVA-NeXt, 16 frames), shot type, camera motion;
  CLIP search returning top 5; tools search/add/remove/swap/move/DONE; Critic sees timeline as text only.
- Key numbers: exploration-based in-context examples cut system-breaking failures from 19.5% to 8.2%.
- Limitations: no transitions, pixel or audio editing; A-roll fixed.
- Transferability: High for tool design and footage-as-text representation.
- Adopt: tool set, top-5 search, structured output, critic over text. Note: dominant failures are hallucinated functions and out-of-bounds times → validator.

## RankCut (IUI '26) · 10.1145/3742413.3789115
- Claim: a 3-stage LLM pipeline produces strong extractive cuts of long transcripts.
- Setting: English meetings (MeetingBank), GPT-4.1 nano, Premiere Pro transcripts.
- Method: Stage 1 coverage summary (T≈0.7–0.8) → Stage 2 JSON RULE_OBJECT (T≈0.4–0.6) → Stage 3 ranking in ~50-sentence windows (T=0.2) + redundancy removal with MiniLM embeddings.
- Key numbers: windows ≥ 400 sentences show early-position bias; ~50 is the chosen balance.
- Transferability: Medium-High (must re-test on Arabic dialect).
- Adopt: rule object, ~50-sentence windows, strictly extractive spans with original timecodes.

## Precise Duration Control (UIST '26) · 10.1145/3830398.3830510
- Claim: LLM scoring + MILP gives millisecond-exact durations; LLM-only editing cannot reliably hit durations.
- Setting: 40 videos (2–82 min), Speechmatics transcripts, Gemini captions, GPT-5.4 scoring, PuLP/CBC.
- Method: tokens = sentences / gaps / visual segments; content-selection MILP with feasibility bounds; second LP distributes gaps.
- Key point: after one-time labelling, new target durations need no LLM calls; deterministic.
- Transferability: High.
- Adopt: the entire selection layer (Constitution I-4).

## LAVE (IUI '24) · 10.1145/3640543.3645143
- Claim: LLM agent plus language-augmented clips makes editing easier for beginners.
- Method: 1 fps frames → LLaVA captions → GPT-4 title/summary per clip; agent plans and executes functions.
- Limitations stated: single agent, linear functions; suggests multi-agent setup and non-LLM tools.
- Adopt: clip-level text summaries as the "gallery" representation.

## MAST: Why Do Multi-Agent LLM Systems Fail? (NeurIPS '25 D&B) · arXiv 2503.13657
- Relevance: design of this company's agent OS. 14 failure modes in 3 categories; structural fixes beat prompt tweaks.
- Adopted in: `company/governance/FAILURE_MODES.md`.

## Anthropic: How we built our multi-agent research system (2025)
- Relevance: brief contents (objective, output format, tool guidance, boundaries), effort scaling,
  artifacts to filesystem instead of passing through the coordinator, end-state evaluation, ~20 cases suffice early.
- Adopted in: `company/OPERATING_MODEL.md` §3–5.
