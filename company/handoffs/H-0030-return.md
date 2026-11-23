# RETURN H-0030 (device benchmark page) · engineering-lead · 2026-11-23

STATUS: DONE

SUMMARY:
- `bench/` is a static page (index.html + 5 ES modules, no build step). It measures on-device Whisper ASR with an automatic ladder (base/WebGPU → tiny/WebGPU → tiny/WASM, every rung recorded) and a 30 s 1080×1920 30 fps H.264 export with burned Arabic + English captions (EXP-008 webfonts). If 1080 fails, the FAIL is logged and the page retries at 720×1280.
- Each step is isolated. Progress is written to localStorage, so after a crash or reload the page shows `crashed at step X`. One click copies a text summary plus the JSON results. Device memory hints and WebGPU/WebCodecs support are in `device`.
- Headless Chrome for Testing 143 ran it with 0 console errors and 0 page errors. ffprobe confirms `export_1080.mp4`: H.264 High, 1080×1920, 30/1 fps, 900 frames, 30.000 s, plus Opus audio. Linux Chrome has no AAC encoder, so AAC was not exercised.
- Every CDN URL is pinned to an exact version and every Hugging Face file to a 40-hex commit. All were checked to exist and are listed in the README. `tests/unit/test_bench_static.py` enforces pins, README parity, no dev media, and caption geometry matching the `clean` preset.

ARTIFACTS:
- bench/index.html, bench/bench.js, bench/env.js, bench/asr.js, bench/export.js, bench/libs.js, bench/README.md (hosting, phone steps, URLs + licences, results schema, smoke recipe)
- tests/unit/test_bench_static.py (23 tests)
- experiments/bench_smoke.mjs (Playwright driver; Playwright is installed outside the repo, so the project has no new dependency)
- experiments/results/H-0030_smoke_main.json, H-0030_smoke_fallback_file.json, H-0030_smoke_crash.json, H-0030_ffprobe.txt
- Commits (not pushed): 902e2ed (page + tests + smoke driver), 1942c6c (evidence), plus this return/log commit

EVIDENCE:
- Reproduction (one line, after the README "Smoke test" install of playwright@1.57.0 into $D):
  `(cd bench && python3 -m http.server 8765) & BENCH_CHANNEL=chromium NODE_PATH=$D/node_modules PLAYWRIGHT_BROWSERS_PATH=$D/browsers node experiments/bench_smoke.mjs http://localhost:8765/ out/h0030`
- Main run (H-0030_smoke_main.json, browser 143.0.7499.4, 2-core 8 GB Codespace, no GPU): `console errors: 0, page errors: 0, failed requests: 0`.
  - export_1080: OK, avc1.640028 + opus, 37 962 ms, 23.71 fps, 28.0 MB.
  - sample_asr: OK, whisper-tiny/wasm (both WebGPU rungs `skipped: WebGPU unavailable`), load 5 056 ms, RTF 0.473. Text: "And so my fellow Americans ask not what your country can do for you, ask what you can do for your country." It matches the reference except for one comma.
- ffprobe (H-0030_ffprobe.txt): `codec_name=h264|profile=High|width=1080|height=1920|r_frame_rate=30/1|duration=30.000000|nb_frames=900`. Audio is `opus … duration=30.020000`. `ffmpeg -xerror -f null` decodes it cleanly.
- 720 fallback (`BENCH_QUERY=simulate=fail1080`, H-0030_smoke_fallback_file.json):
  - export_1080 is recorded as FAIL with the simulated error.
  - export_720 is OK: avc1.64001f, 720×1280, 900 frames, 30.000 s, 58.16 fps, `reason: "retry after export_1080 FAIL"`.
- File picker (`BENCH_FILE` = the page's own synthetic export; no dev clip): file_asr OK and file_export OK at 720×1280, 7.61 fps. Seek-per-frame decode is slow, and the README says this number is a lower bound.
  - 42 `requestfailed` entries are `blob: … net::ERR_ABORTED` range reads that the video element cancels while seeking. They are not console errors.
- Crash watchdog (`BENCH_CRASH_TEST=1`, H-0030_smoke_crash.json): after a reload mid-export the banner reads `Last run (mwtcksjj) crashed at step "export_1080" …`.
- No H.264 encoder in Playwright 1.48's open-source Chromium or in the default headless shell: every codec reports `isConfigSupported:false`. The page recorded both exports as FAIL with the codec list, which is correct behaviour. The README documents `BENCH_CHANNEL=chromium`.
- Tests: `.venv/bin/python -m pytest -q` → `404 passed, 8 skipped`. `ruff check tests/unit/test_bench_static.py` → `All checks passed!`
- Licences (npm view / HF API): transformers Apache-2.0, onnxruntime-web MIT, mp4-muxer MIT, fontsource Noto OFL-1.1, Xenova/whisper-base and Xenova/whisper-tiny Apache-2.0. The JFK speech is a US Government work under 17 U.S.C. §105; the reasoning is in the README.
- Determinism (DoD row): two exports of the same synthetic clip had byte-identical Opus audio (stream sha256 `1380bee7…` both times). The **H.264 packets differ** between runs (`8eaad661…` vs `536c7a2c…`), and so does the whole file. The canvas input is deterministic, so the Chrome WebCodecs encoder is the non-deterministic part.

DEVIATIONS FROM BRIEF:
1. Branch: committed on `t2/install-company-os`, not `t2/H-0030`, to match H-0027/H-0029/H-0032 and the Operator's push flow. The Operator can re-home the branch if wanted.
2. Smoke tests ran in Playwright's Chrome for Testing (`channel: "chromium"`) because the open-source build has no H.264 encoder. The system-wide Chrome install (`--with-deps`, sudo) was blocked, and I did not retry it.
3. Two small test-only hooks were added: `?simulate=fail1080` and `?asr=0`. They are recorded in `options.simulate` and do not affect a normal run.
4. Tool calls: about 33 of 50.

OPEN QUESTIONS:
1. Assurance: please confirm the JFK sample is acceptable for the data-rights register. The basis is public domain under §105, and the hosting dataset declares no licence. The sample is fetched at run time and never stored in the repo.
2. Operator/Founder: how to host. A Private Codespace port needs a GitHub sign-in on each phone. A Public port or GitHub Pages makes the page public, which is out of scope here.
3. Engineering/Research: if on-device export becomes product render, WebCodecs H.264 output is not byte-identical run to run. Our "same input → byte-identical output" rule would need an ADR that scopes it to the timeline and keeps the MP4 out of that guarantee. Who: engineering-lead + assurance-lead.
4. Research: WebGPU rungs and AAC were not exercised here (no GPU, Linux Chrome). The phone runs are the first real evidence for them.

CONFIDENCE: Medium. The biggest doubt is the WebGPU path (whisper-base q4 on WebGPU) and Safari/iOS WebCodecs. Neither could run in this Codespace. The page records their failures instead of crashing, but whether they succeed is unknown until the Founder runs it on phones.

NEXT RECOMMENDED STEP: Founder runs the page on the 3 phones via the Codespace port-forward (bench/README.md "Run it on a phone"), twice each, and pastes "Copy results". Then research-lead tabulates RTF, export fps and crash step against ADR-0011.
