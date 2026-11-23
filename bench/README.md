# Device bench (H-0030)

A static page that measures, on the phone itself, whether it can (1) run Whisper speech-to-text and (2) export a
30 s 1080×1920 30 fps H.264 MP4 with burned-in Arabic and English captions. If phones can, ASR and render cost us
about $0 per export (ADR-0011, `docs/COST_BASELINE.md`: render is 11 % and ASR 9 % of today's median cost).

Static files only, no build step: `index.html`, `bench.js` (runner), `env.js` (device probe, memory, watchdog),
`asr.js` (Whisper ladder), `export.js` (canvas → WebCodecs → MP4), `libs.js` (every external URL).
Nothing is uploaded anywhere. There is no server code, no analytics.

## Run it on a phone (Founder)

WebGPU and WebCodecs only work in a **secure context** (HTTPS or `localhost`), so the page must come over HTTPS.

**Codespace port-forward (recommended, nothing public):**
1. In the Codespace terminal: `cd bench && python3 -m http.server 8000`
2. VS Code → **Ports** tab → port 8000 → copy the *Forwarded Address*
   (`https://<codespace-name>-8000.app.github.dev/`). Leave visibility **Private**.
3. On the phone, open that address in the phone's main browser (Chrome on Android, Safari on iPhone).
   Private ports ask you to sign in to GitHub with the account that owns the Codespace; do that once.
4. Tap **Run benchmark**. Keep the screen on and the tab in front until the status line says `done`
   (about 1 to 5 minutes; the first run downloads 40 to 200 MB of Whisper weights, so use Wi-Fi).
5. Tap **Copy results** and paste the text into the chat. Run it a second time: the second run's
   `model_load_ms` is the cached load time.
6. Optional: pick one of your own clips under "Optional own clip". It is read on the phone and never leaves it.

If the tab crashes or the phone reloads it, open the page again: a yellow box says
`Last run ... crashed at step "<step>"` and the partial results are shown, ready to copy. Untick ASR to rerun the
rest.

**GitHub Pages (alternative, not enabled):** Pages serves `bench/` over HTTPS as-is. It would make the page
public, so it is the Operator's and Founder's call (brief §6 puts public hosting out of scope).

## What it runs (each step isolated: a FAIL in one step does not stop the next)

| step id | what | pass means |
|---|---|---|
| `env` | UA, platform, `navigator.deviceMemory`, `hardwareConcurrency`, screen, WebGPU adapter, WebCodecs presence | always ok |
| `fonts` | loads Noto Sans Arabic + Noto Sans (EXP-008 pair) as webfonts | both pass `document.fonts.check` |
| `export_1080` | synthetic 30 s clip (canvas animation + 440 Hz beep), 1080×1920, 30 fps, H.264, captions burned on canvas | MP4 finalised |
| `export_720` | same at 720×1280. Runs **only** if `export_1080` FAILED (or "also 720" is ticked); the 1080 FAIL stays in the results. Never a silent downgrade. | MP4 finalised |
| `sample_asr` | Whisper on the JFK speech sample (11 s, English). Ladder: whisper-base/WebGPU → whisper-tiny/WebGPU → whisper-tiny/WASM; first rung that loads and transcribes wins, every rung tried is in `attempts` | transcript returned |
| `file_asr` | same ladder on the first 30 s of the picked clip (language from the selector) | transcript returned |
| `file_export` | picked clip as background (seek per frame), captions burned, 1080×1920 (720×1280 if `export_1080` failed) | MP4 finalised |

Audio codec: AAC (`mp4a.40.2`) if the browser has an AAC encoder, else Opus, else no audio track. The one used is
in `audio_codec`. Captions follow the `clean` preset in `src/presets.py` (80 px at 1080 wide, white, 4 px black
outline, 320 px bottom margin), scaled with width. The browser shapes the text, not libass, so this is a parity
approximation of `src/render`, not the same renderer.

## External URLs (all pinned; checked to exist on 2026-11-23)

| what | URL | licence |
|---|---|---|
| transformers.js 4.3.2 (self-contained bundle) | https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2/dist/transformers.min.js | Apache-2.0 |
| ONNX Runtime Web wasm (transformers 4.3.2's pinned dependency) | https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.0-dev.20260914-8d85527a0/dist/ | MIT |
| mp4-muxer 5.2.2 | https://cdn.jsdelivr.net/npm/mp4-muxer@5.2.2/build/mp4-muxer.mjs | MIT |
| Noto Sans Arabic 400 (fontsource 5.3.0) | https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-arabic@5.3.0/files/noto-sans-arabic-arabic-400-normal.woff2 | OFL-1.1 |
| Noto Sans 400 latin (fontsource 5.3.0) | https://cdn.jsdelivr.net/npm/@fontsource/noto-sans@5.3.0/files/noto-sans-latin-400-normal.woff2 | OFL-1.1 |
| Whisper base weights | https://huggingface.co/Xenova/whisper-base at revision `64da57285918e20ea79ea5c88eed7197933abaa8` | Apache-2.0 |
| Whisper tiny weights | https://huggingface.co/Xenova/whisper-tiny at revision `5332fcc35e32a33b86612b9a57a89be7906102b1` | Apache-2.0 |
| JFK speech sample | https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/542437c29cc5273cfd29e25c77696f2b349badd7/jfk.wav | public domain, see below |

`mp4-muxer` is deprecated upstream in favour of Mediabunny (same author). It still works and is pinned; moving
to Mediabunny is a follow-up, not needed for the bench.

## Test media

- **Synthetic clip:** drawn in the page from the frame index (no clock, no randomness) plus a generated 440 Hz
  beep. Nothing is downloaded or bundled.
- **Speech sample:** 11 s from President John F. Kennedy's inaugural address (20 January 1961). A speech made by
  a US federal officer as part of official duties is a work of the US Government and is not under copyright in the
  US (17 U.S.C. §105). The same clip ships as `tests/jfk.flac` in the MIT-licensed openai/whisper repo and in the
  transformers.js docs. The hosting dataset (`Xenova/transformers.js-docs`) declares no licence of its own; our
  basis is the public-domain status of the speech. It is fetched at run time and never stored in this repo.
- **Own clip (optional):** read from the phone with a file picker, processed in memory, never sent anywhere.
- No TikTok or dev clip is bundled, referenced or uploaded (ADR-0006). `tests/unit/test_bench_static.py` checks
  the code files for references to `quarantine/`, `samples/`, `data/`, `cache/` and dev clip names.

## Results JSON (`schema: "bench-results/1"`)

"Copy results" copies a short text summary, a blank line, then this JSON. It is also saved to `localStorage`
after every step.

```
{
  schema: "bench-results/1", page_version: "H-0030 v1", run_id: string,
  started_at: ISO time, finished_at: ISO time | null (null = run did not finish),
  options: { asr: bool, also_720: bool, local_file: {size_bytes, type} | null, file_language: string, simulate: string | null },
  libs: { transformers, ort_wasm, mp4_muxer, fonts: [..], models: {name: {id, revision}}, speech_sample },
  device: {
    user_agent, platform, mobile: bool | null, device_memory_gb: number | "n/a", hardware_concurrency: number | "n/a",
    screen: {width, height, dpr}, secure_context: bool, cross_origin_isolated: bool,
    webgpu_available: bool, webgpu_adapter: {vendor, architecture, description} | null, webgpu_error: string | null,
    webcodecs: {video_encoder, audio_encoder, video_frame}, memory_api: string
  },
  steps: [ {
    id: "env" | "fonts" | "export_1080" | "export_720" | "sample_asr" | "file_asr" | "file_export",
    status: "ok" | "fail" | "skipped", error: string | null, reason?: string (skipped / why 720 ran),
    started_at, duration_ms, peak_memory_bytes: number | "n/a", memory_source: string,
    // export steps:
    width, height, fps, seconds, frames, video_codec, audio_codec, codec_candidates: ["codec:supported"],
    export_ms, export_fps (frames / export seconds), bytes,
    // ASR steps:
    model, model_id, revision, backend: "webgpu" | "wasm", dtype, language, model_load_ms, audio_s,
    transcribe_ms, rtf (transcribe seconds / audio seconds; < 1 is faster than real time), text,
    attempts: [ {model, device, dtype, status, error, model_load_ms?, transcribe_ms?, text?} ],
    reference?: string (sample_asr only)
  } ]
}
```

**Memory caveat:** `peak_memory_bytes` is the largest JS-heap sample (`performance.memory`, Chromium only, every
250 ms). Chrome rounds that value unless started with `--enable-precise-memory-info`, and it does not count GPU or
WebCodecs buffers. `measureUserAgentSpecificMemory` needs cross-origin isolation, which a plain static host does
not give. Safari and Firefox report `"n/a"`. Read it as a rough lower bound; a tab crash is the real signal.

## Smoke test (desktop, headless Chromium)

Playwright lives outside the repo (no new project dependency):
```
D=/tmp/pw && mkdir -p $D && (cd $D && npm init -y && npm i playwright@1.57.0 && PLAYWRIGHT_BROWSERS_PATH=$D/browsers npx playwright install chromium)
(cd bench && python3 -m http.server 8765) &
BENCH_CHANNEL=chromium NODE_PATH=$D/node_modules PLAYWRIGHT_BROWSERS_PATH=$D/browsers node experiments/bench_smoke.mjs http://localhost:8765/ out/h0030
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration -of compact out/h0030/export_1080.mp4
```
`BENCH_CHANNEL=chromium` selects the full Chrome-for-Testing build: the default headless shell (and Playwright
1.48's open-source Chromium) has **no H.264 encoder**, so both exports FAIL there (that is a correct FAIL record).
Extra modes: `BENCH_QUERY="simulate=fail1080"` forces the 720 fallback; `BENCH_FILE=<clip>` exercises the file
picker; `BENCH_CRASH_TEST=1` reloads mid-run and checks the crash banner.
