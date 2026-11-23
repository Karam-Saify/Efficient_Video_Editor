# Research Notes and Experiment Plan

## Key papers (all ACM Digital Library)
| Paper | DOI | What we take from it |
|---|---|---|
| ELLMPEG (MMSys '26) | 10.1145/3793853.3795760 | LLM generates FFmpeg commands with RAG over docs + execute → self-reflect → fix loop. Small local model (Qwen2.5) reached 78% valid commands at zero API cost. |
| EditDuet (SIGGRAPH '25) | 10.1145/3721238.3730761 | Footage segmented into sub-clips, each stored as text (caption, shot type, camera motion). Agents search (top-5 results) instead of seeing all footage. Editor tools: search, add_to_timeline, remove, swap, move, DONE. Critic reviews timeline as text → feedback or RENDER. Main failures: hallucinated functions, out-of-bounds times → validate everything. |
| RankCut (IUI '26) | 10.1145/3742413.3789115 | Transcript-only, strictly extractive. 3 stages: coverage summary → JSON RULE_OBJECT → rule-conditioned ranking in ~50-sentence windows. Large windows (400+) cause early-position bias. Cheap model (GPT-4.1 nano) suffices. |
| Precise Duration Control (UIST '26) | 10.1145/3830398.3830510 | LLMs cannot reliably hit exact durations. LLM scores sentences/scenes once (informativity, entertainment, needs-context); PuLP/CBC MILP selects content, a second LP distributes gaps for millisecond-exact length. After scoring, new target lengths need zero LLM calls. |
| LAVE (IUI '24) | 10.1145/3640543.3645143 | Baseline: 1 fps frame captions → LLM title/summary per clip; agent plans and executes edit functions. Suggests multi-agent + non-LLM tools as future work. |

## Gap this project fills
No paper covers Arabic content, Shorts-specific editing (vertical, captions, hooks, pacing),
or a fully open-source low-cost local pipeline with an LLM only in the decision loop.

## Experiments (fixed test set: 3–5 real clips in `samples/`)
| ID | Question | Method | Pass criterion |
|---|---|---|---|
| E1 | Is Whisper good enough for our Arabic? | faster-whisper large-v3 vs turbo; hand-check 2 min for WER and timestamp drift | Few errors; cuts land cleanly on words |
| E2 | Are visual captions needed? | Edit same clip with transcript-only vs transcript + scene captions | If no quality difference, skip captioning |
| E3 | Does the LLM produce valid timeline JSON? | 20 edit requests, validate against schema + bounds | ≥90% valid first try; rest fixed in 1 retry |
| E4 | MILP vs LLM-only selection | Targets 30/45/58s; exact-length rate + human 1–5 quality | MILP exact, quality ≥ LLM-only |
| E5 | Cost per video | Log tokens per stage | Within a set per-Short budget |
| E6 | Render + Arabic captions | FFmpeg/libass vs Remotion; RTL and letter shaping; render time on CPU | Correct Arabic shaping; render in minutes |
| E7 | Are revisions cheap? | "shorten intro", "bigger captions" → diff size | Small diffs, <2k tokens per revision |

Priority: E1 and E6 first (Arabic is the highest risk).

## Open research questions (search keywords)
1. Short-form editing craft (hooks, pacing, retention): "short-form video engagement",
   "video retention hook", "TikTok editing pacing". Sources: Communication Source, Business Source Ultimate, ACM.
2. Arabic / dialect ASR + alignment: "Arabic dialect ASR Whisper", "Levantine speech recognition",
   "forced alignment Arabic". Sources: arXiv, IEEE.
3. Best timeline representation for LLMs: OpenTimelineIO vs custom JSON vs Remotion code;
   "domain-specific language video editing", "declarative video composition".
4. Automatic quality evaluation: EditDuet's LLM-as-judge section, SST-EM metrics.
5. Reframing 16:9 → 9:16 (only if source is horizontal): "automatic video reframing", "saliency cropping".

## Phases
- Phase 0: skeleton, schema, samples, E1 + E6.
- Phase 1: transcript → MILP cut → render, no LLM.
- Phase 2: LLM scoring + rule object; E2, E4, E5.
- Phase 3: natural-language revisions + validate/fix loop, captions, zooms; E3, E7.
- Phase 4: critic pass; integrate with Shorts automation (GitHub Actions → YouTube Data API).

## Environment notes
Codespace has no GPU and limited monthly core-hours. Use faster-whisper int8 / turbo, short test
clips. If transcription is too slow, run that stage on a local PC and commit the cached transcript.
