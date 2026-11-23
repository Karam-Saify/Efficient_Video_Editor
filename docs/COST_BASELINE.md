# Cost baseline: what one exported video costs today (H-0027)

Status: baseline, measured 2026-11-23 on branch `t2/install-company-os`. It answers ADR-0011: is the total
marginal cost per exported free-tier video ≤ $0.01 (stretch ≤ $0.005)? Nothing here is optimised (out of scope).

## Verdict (ADR-0011)

| | median | P90 | $0.01 ceiling | $0.005 stretch |
|---|---|---|---|---|
| Full pipeline, miss rate 0.2, Sonnet 5.5 on miss (LLM rows are estimates) | **$0.0080** | **$0.0111** | median **under**, P90 **OVER** | **OVER** |
| Measured stages only (no LLM: miss rate 0, small-model rows still estimated) | $0.0030 | $0.0061 | under | median under, P90 **OVER** |

- **The stage that breaks the ceiling is planning.** In this model, planning is the big-model call on a miss.
  At a 20 % miss rate that one term is about $0.005 per export, which is 68 % of the median cost. On its own it
  uses up the whole stretch budget.
  - The ceiling holds at the median only while the miss rate is at most about 0.2 with Sonnet 5.5, or at most
    about 0.1 with Opus 5.5 (§5).
  - The P90 clip is the 503 s source (`Download (2)`). It goes over $0.01 because of planning, plus scene
    detection on 8 minutes of video, plus 30 days of storage for a 111 MB source.
- **What is measured today** (ASR, scenes, edit, render, storage) has a median of about $0.0025 per export. That
  fits the stretch target. Everything about the LLM is an estimate until a prompt exists.
- **Top 3 cost drivers (median share):**
  1. Planning, big-model miss: 68 % (estimate).
  2. Render: 11 %, measured. It is about 80 CPU-s for a 30 s 1080×1920 export.
  3. ASR: 9 %, measured. It is about 45 to 125 CPU-s, and roughly 20 CPU-s of that is model load.
  Storage (7.5 %) is a close fourth, and it dominates for long sources.

## 1. Method

- **Clips.** Every unique dev clip in `quarantine/dev/` (internal development testing only, ADR-0006), deduplicated
  by sha256: 9 files, `Download (4).mp4` is byte-identical to `Download (2).mp4`, so there are **8 unique clips**.
  The Founder asked for 10. **There is a shortfall of 2 clips.** I did not invent any.
- **Pipeline per clip, cold cache.** `experiments/cost_baseline.py measure` first deletes the clip's cached transcript,
  scenes, keyframes, edit and timings. It writes one ops file per clip (default `clean` captions, because a no-speech clip has no captions to restyle; `set_duration` to
  min(30 s, source), one 1.2× zoom), then runs:
  1. `python -m src.demo`. This runs ingest ASR (faster-whisper `large-v3-turbo`, CPU int8, beam 5, VAD, language
     auto), then captions and ops and validate (`edit`), then the render at 1080×1920, 30 fps, libx264 `veryfast`,
     CRF 20.
  2. `python -m src.ingest <clip>` with the transcript already cached. This runs only scene detection and one
     keyframe per scene (`scenes_keyframes`), which is the code half of "understanding".
- **Instrumentation (reusable).** `src/timings.py`:
  - `run_measured` reads the child's own rusage via `os.wait4`. This gives exact CPU (user + sys) and peak RSS
    for that process tree.
  - `measure()` covers in-process work. Its peak RSS is the process high-water mark, an upper bound.
  - `record()` writes `cache/<video_id>/timings.json` (`schema: timings/1`). `src.demo` now records `ingest`,
    `edit` and `render` on every run. Bytes per stage are recorded next to the timings.
  - Tests: `tests/unit/test_timings.py`, `tests/unit/test_cost_baseline.py`.
- **Measurement file.** `experiments/results/H-0027_cost_measurements.json` holds numbers only: timings, bytes,
  word, segment and scene counts. It holds no transcript text and no media.
- **Pricing.** `experiments/cost_baseline.py report` computes every table below from that file and from the
  `ASSUMPTIONS` / `ESTIMATE` dicts in the same script. All arithmetic is done in code, so I typed no number in the
  tables by hand. Reproduce with:
  `.venv/bin/python experiments/cost_baseline.py measure && .venv/bin/python experiments/cost_baseline.py report`
- **Compute pricing.** Compute is priced like Fargate: CPU-seconds as vCPU-seconds, plus peak RSS (GB) held for the
  stage's wall time. Wall time on this box (2 vCPU) includes model load (whisper loads per run, about 1.5 GB).
- **Machine.** Codespace, 2 vCPU Intel Xeon Platinum 8370C @ 2.8 GHz, 7 GB RAM, no GPU. Measurements ran one after
  another, with nothing else heavy running.

## 2. Assumptions

| # | Assumption | Value | Source |
|---|---|---|---|
| A1 | Cloud compute, vCPU | $0.040478 / vCPU-hour ($0.000011244 / vCPU-s) | AWS Fargate pricing, Linux/x86, us-east-1, on-demand, https://aws.amazon.com/fargate/pricing/ (fetched 2026-11-23) |
| A2 | Cloud compute, memory | $0.004446 / GB-hour ($0.000001235 / GB-s) | same page as A1 |
| A3 | Object storage | $0.015 / GB-month; egress free | Cloudflare R2 Standard, https://developers.cloudflare.com/r2/pricing/ (fetched 2026-11-23); free tier ignored (marginal cost) |
| A4 | Retention | source + cache + export kept 1 month, then deleted | our assumption (two-way door); lever L3 varies it |
| A5 | Small model (understanding, planning) | Claude Haiku 5.5: $0.10 in / $0.50 out per 1M tokens | `claude-api` skill model table (cached 2026-11-03) |
| A6 | Big model (planning, miss only) | Sonnet 5.5 $2 / $10; Opus 5.5 $4 / $20 per 1M tokens | same as A5 |
| A7 | Miss rate (ADR-0008) | 0.2 default; sweep 0 to 1 in §5 | our assumption, no recipe exists yet |
| A8 | Tokens per char | 4 chars/token Latin, 2 chars/token Arabic | engineering heuristic (ESTIMATE); replace with `count_tokens` once prompts exist |
| A9 | Prompt sizes | understanding: 800 fixed + transcript + 6/segment + 6/scene in, 15/segment out; planning small: 2500 + 5/segment in, 300 out; planning big: 5000 + transcript + 6/segment in, 1500 out | ESTIMATE, sized for ADR-0008 (recipe catalogue in the prompt, ~50-sentence windows, JSON out); `ESTIMATE` dict in `experiments/cost_baseline.py` |
| A10 | No retries, no prompt caching | each LLM call once | conservative on caching, optimistic on retries (2 validator retries would at most triple an LLM row) |
| A11 | Client-side alternative | ASR + render run on the user's device → cost to us ≈ 0 | e.g. whisper.cpp / platform STT and ffmpeg.wasm / native; quality and speed not measured |

Not in ADR-0011's stage list, so not in the totals: delivery egress (R2 egress is free; on S3-style egress it would
not be), CDN, request operations (R2 Class A $4.50 / M: a few writes per video ≈ $0.00002), and the platform.

## 3. Results (generated by `experiments/cost_baseline.py report`, unedited)

### Measured resources per clip × stage (cold cache, 2 vCPU Xeon 8370C)

| clip | src s | export s | lang | words | stage | wall s | CPU s | peak RSS MB | bytes |
|---|---|---|---|---|---|---|---|---|---|
| Download (1).mp4 | 18.1 | 18.1 | en | 0 | ingest | 27.0 | 23.4 | 2053 | 402 |
| Download (1).mp4 | 18.1 | 18.1 | en | 0 | scenes_keyframes | 10.0 | 3.7 | 100 | 136311 |
| Download (1).mp4 | 18.1 | 18.1 | en | 0 | edit | 0.0 | 0.0 | 2053 | 2417 |
| Download (1).mp4 | 18.1 | 18.1 | en | 0 | render | 17.6 | 30.9 | 334 | 6826170 |
| Download (1).mp4 | | | | | source | | | | 2029290 |
| Download (7).mp4 | 21.9 | 21.9 | en | 0 | ingest | 25.4 | 23.7 | 2053 | 406 |
| Download (7).mp4 | 21.9 | 21.9 | en | 0 | scenes_keyframes | 3.3 | 5.0 | 103 | 149318 |
| Download (7).mp4 | 21.9 | 21.9 | en | 0 | edit | 0.0 | 0.0 | 2053 | 2417 |
| Download (7).mp4 | 21.9 | 21.9 | en | 0 | render | 28.0 | 50.6 | 333 | 12843632 |
| Download (7).mp4 | | | | | source | | | | 3161342 |
| Download (6).mp4 | 36.0 | 30.0 | en | 74 | ingest | 62.1 | 61.7 | 2103 | 9625 |
| Download (6).mp4 | 36.0 | 30.0 | en | 74 | scenes_keyframes | 5.4 | 7.7 | 104 | 194010 |
| Download (6).mp4 | 36.0 | 30.0 | en | 74 | edit | 0.0 | 0.0 | 2103 | 23346 |
| Download (6).mp4 | 36.0 | 30.0 | en | 74 | render | 45.2 | 76.0 | 335 | 26368216 |
| Download (6).mp4 | | | | | source | | | | 6999988 |
| Download (5).mp4 | 37.5 | 30.0 | en | 88 | ingest | 63.6 | 64.4 | 2103 | 11771 |
| Download (5).mp4 | 37.5 | 30.0 | en | 88 | scenes_keyframes | 4.6 | 6.5 | 104 | 33430 |
| Download (5).mp4 | 37.5 | 30.0 | en | 88 | edit | 0.0 | 0.0 | 2103 | 30786 |
| Download (5).mp4 | 37.5 | 30.0 | en | 88 | render | 49.1 | 79.7 | 1240 | 31405459 |
| Download (5).mp4 | | | | | source | | | | 8742516 |
| Download (8).mp4 | 60.0 | 30.0 | ar | 3 | ingest | 55.9 | 46.5 | 2096 | 882 |
| Download (8).mp4 | 60.0 | 30.0 | ar | 3 | scenes_keyframes | 7.8 | 10.4 | 104 | 141672 |
| Download (8).mp4 | 60.0 | 30.0 | ar | 3 | edit | 0.0 | 0.0 | 2096 | 3754 |
| Download (8).mp4 | 60.0 | 30.0 | ar | 3 | render | 52.1 | 78.2 | 1999 | 33711460 |
| Download (8).mp4 | | | | | source | | | | 17950330 |
| Download.mp4 | 65.0 | 30.0 | en | 25 | ingest | 47.9 | 43.4 | 2094 | 3559 |
| Download.mp4 | 65.0 | 30.0 | en | 25 | scenes_keyframes | 12.9 | 18.2 | 101 | 645673 |
| Download.mp4 | 65.0 | 30.0 | en | 25 | edit | 0.0 | 0.0 | 2094 | 10538 |
| Download.mp4 | 65.0 | 30.0 | en | 25 | render | 46.2 | 81.6 | 1307 | 26197608 |
| Download.mp4 | | | | | source | | | | 15910523 |
| Download (3).mp4 | 91.1 | 30.0 | en | 209 | ingest | 119.4 | 125.2 | 2158 | 29421 |
| Download (3).mp4 | 91.1 | 30.0 | en | 209 | scenes_keyframes | 16.6 | 20.6 | 105 | 541457 |
| Download (3).mp4 | 91.1 | 30.0 | en | 209 | edit | 0.0 | 0.0 | 2158 | 55717 |
| Download (3).mp4 | 91.1 | 30.0 | en | 209 | render | 53.4 | 90.7 | 1454 | 28689219 |
| Download (3).mp4 | | | | | source | | | | 20792336 |
| Download (2).mp4 | 503.1 | 30.0 | en | 0 | ingest | 34.8 | 28.9 | 2094 | 409 |
| Download (2).mp4 | 503.1 | 30.0 | en | 0 | scenes_keyframes | 104.7 | 140.2 | 106 | 7771173 |
| Download (2).mp4 | 503.1 | 30.0 | en | 0 | edit | 0.0 | 0.0 | 2094 | 2441 |
| Download (2).mp4 | 503.1 | 30.0 | en | 0 | render | 79.9 | 121.7 | 343 | 24209941 |
| Download (2).mp4 | | | | | source | | | | 110821380 |

### Cost per clip × stage, m$ (miss rate 0.2, big model Sonnet 5.5; understanding/planning LLM parts are ESTIMATES)

| clip | asr | understanding | planning | render | storage | total | vs $0.01 | vs $0.005 |
|---|---|---|---|---|---|---|---|---|
| Download (1).mp4 | 0.330 | 0.152 | 5.400 | 0.355 | 0.126 | **6.363** | under | OVER |
| Download (7).mp4 | 0.330 | 0.165 | 5.400 | 0.580 | 0.226 | **6.701** | under | OVER |
| Download (6).mp4 | 0.851 | 0.214 | 5.450 | 0.872 | 0.469 | **7.857** | under | OVER |
| Download (5).mp4 | 0.885 | 0.224 | 5.471 | 0.970 | 0.562 | **8.111** | under | OVER |
| Download (8).mp4 | 0.664 | 0.227 | 5.405 | 1.005 | 0.724 | **8.025** | under | OVER |
| Download.mp4 | 0.609 | 0.333 | 5.418 | 0.991 | 0.597 | **7.948** | under | OVER |
| Download (3).mp4 | 1.718 | 0.662 | 5.613 | 1.114 | 0.700 | **9.807** | under | OVER |
| Download (2).mp4 | 0.412 | 1.879 | 5.400 | 1.401 | 1.995 | **11.087** | OVER | OVER |
| **median** | 0.636 | 0.225 | 5.412 | 0.980 | 0.580 | **7.986** | under | OVER |
| **P90 (nearest rank)** | 1.718 | 1.879 | 5.613 | 1.401 | 1.995 | **11.087** | OVER | OVER |

### Share of the median-clip cost by stage (mean of per-clip shares)

- planning: 68.0%  (median 5.412 m$)
- render: 10.8%  (median 0.980 m$)
- asr: 8.6%  (median 0.636 m$)
- storage: 7.5%  (median 0.580 m$)
- understanding: 5.1%  (median 0.225 m$)

### Sensitivity: miss rate × big model, median / P90 total (m$)

| miss rate | big = Sonnet 5.5 median | P90 | big = Opus 5.5 median | P90 |
|---|---|---|---|---|
| 0.0 | 2.975 | 6.087 | 2.975 | 6.087 |
| 0.1 | 5.481 | 8.587 | 7.986 | 11.087 |
| 0.2 | 7.986 | 11.087 | 12.997 | 16.087 |
| 0.5 | 15.502 | 18.587 | 28.047 | 31.087 |
| 1.0 | 28.047 | 31.087 | 53.194 | 56.548 |

### Client-side alternative (ASR + render on the user's device: cost to us = 0)

median 6.302 m$, P90 9.274 m$

### Levers (median $ saved per export, from the same model)

- miss rate 0.2 -> 0.1 (more recipes / small-model retry before escalating): saves median 2.505 m$ (31% of median)
- render on device (ffmpeg.wasm / native app): saves median 0.980 m$ (12% of median)
- ASR on device (whisper.cpp / platform STT): saves median 0.636 m$ (8% of median)
- retention 30 d -> 7 d (source + cache + export): saves median 0.444 m$ (6% of median)

### Token estimates (per clip)

| clip | transcript tok | understanding in/out | plan small in/out | plan big in/out |
|---|---|---|---|---|
| Download (1).mp4 | 0 | 842/50 | 2500/300 | 5000/1500 |
| Download (7).mp4 | 0 | 836/50 | 2500/300 | 5000/1500 |
| Download (6).mp4 | 96 | 962/60 | 2520/300 | 5120/1500 |
| Download (5).mp4 | 126 | 974/105 | 2535/300 | 5168/1500 |
| Download (8).mp4 | 6 | 842/50 | 2505/300 | 5012/1500 |
| Download.mp4 | 30 | 1016/50 | 2510/300 | 5042/1500 |
| Download (3).mp4 | 256 | 1428/570 | 2690/300 | 5484/1500 |
| Download (2).mp4 | 0 | 2636/50 | 2500/300 | 5000/1500 |

## 4. Reading the numbers

- "m$" means a milli-dollar, so 1 m$ = $0.001. The ceiling is 10 m$ and the stretch target is 5 m$.
- **ASR includes model load.** Every run loads `large-v3-turbo` (about 2.1 GB peak RSS). The two no-speech clips
  of 18 s and 22 s still cost about 23 CPU-s, so model load is a floor of roughly 20 CPU-s. A warm ASR worker
  would remove most of it.
  - `Download (2)` is 503 s but needs only 29 CPU-s of ASR, because VAD drops its music-only audio.
- **Render RSS varies.** It ranges from 333 MB to 2.0 GB depending on the source. Render cost is mostly CPU
  (about 80 CPU-s at `veryfast`, on 2 cores) and grows with export length, not source length.
- **The `edit` row's RSS (about 2 GB) is a measurement artefact.** That instrumentation reported the largest
  reaped child, which was the ASR process. `measure()` now reports only its own process (`self_hwm`). Edit work
  takes under 0.03 CPU-s, so its cost rounds to 0 either way.
- **Storage.** Storage is the source plus every cached and exported byte (transcript, scenes, keyframes, edit
  history, timeline, MP4, ASS), held for 1 month on R2.
  - The 1080×1920 CRF-20 export (6 to 34 MB) is usually the largest item, larger than the TikTok-compressed
    sources.
- **Sensitivity.**
  - The verdict depends almost entirely on the miss rate (A7) and on the size of the big model's output (A9).
  - Doubling every small-model (Haiku 5.5) token estimate adds about 0.5 m$ (the small-model calls total about 0.5 m$ per export).
  - The ×2 Arabic-token heuristic matters little at these transcript sizes, at most about 256 tokens.

## 5. Levers ranked by $ saved (median per export)

These come from §3 and are listed only. Optimising is out of scope (H-0027).

| rank | lever | median saved | why |
|---|---|---|---|
| L1 | Cut the big-model miss rate from 0.2 to 0.1: more recipes, and a small-model repair retry with the validator error before escalating | 2.5 m$ (31 %) | the miss term is the dominant cost; it is linear in the miss rate |
| L2 | Render on the user's device (ffmpeg.wasm / native) | 1.0 m$ (12 %) | the largest measured CPU stage |
| L3 | ASR on the user's device, or a warm shared ASR worker | 0.6 m$ (8 %) | about 20 CPU-s per run is model load |

Retention cut from 30 to 7 days would save 0.44 m$ (6 %). Combining client-side ASR and render gives a median of
6.3 m$, which is still over the stretch target until L1 lands.

## 6. Gaps

- There are 8 unique clips, not 10. The two missing clips were not substituted.
- None of the clips is Arabic speech. `Download (8)` is detected as `ar` but has 3 words.
- Understanding and planning token counts are formulas, not measured prompts. Replace them with
  `count_tokens` and `usage.jsonl` once the LLM stages exist.
- Each clip was measured once. There is no repeat-run variance. The Codespace had other light load (editor
  processes).

