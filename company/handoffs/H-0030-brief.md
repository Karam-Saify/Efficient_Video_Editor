# BRIEF H-0030 (Week 1 · B)
- **To:** engineering-lead · **Tier / Milestone:** T2 (new standalone component; daily Assurance review) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** A standalone device benchmark page that tells us whether phones can do ASR and a 1080×1920 export on-device. If they can, ASR and render cost us ≈ $0 (ADR-0011 ceiling; see `docs/COST_BASELINE.md`). The Founder will run it on 3 phones.
2. **Inputs:** `docs/COST_BASELINE.md` + `company/handoffs/H-0027-return.md`; `src/render/` (caption presets, for visual parity); the EXP-008 font pair.
3. **Constraints:**
   - `bench/` is static files only (index.html + JS modules), with no build step, so it runs from any static HTTPS host. WebGPU and WebCodecs need a secure context.
   - Libraries come from a CDN with **exact pinned versions** (e.g. `@huggingface/transformers` for Whisper tiny/base, WebGPU with a WASM fallback; an mp4 muxer for WebCodecs). The model weights load from the Hugging Face hub. Record every URL in `bench/README.md`.
   - **No TikTok/dev clip is bundled or uploaded, ever** (ADR-0006). Test media:
     - (a) a synthetic 30 s clip generated in the page (canvas animation + tone);
     - (b) a public-domain or permissively licensed speech sample for ASR, with its licence cited (e.g. the JFK sample used in the Whisper/transformers.js examples, *if* its licence checks out; otherwise pick another and cite it);
     - (c) an optional local file picker, so the Founder can test their own clip. The file stays on the device.
   - Export: 1080×1920, 30 fps, 30 s, H.264 (+ AAC if available), captions burned on canvas with Noto Sans Arabic + Noto Sans (webfont). Include one Arabic and one English caption line.
   - Log per step: device/UA, WebGPU available, backend used, model load ms, ASR RTF, export ms, export fps, peak memory (`performance.measureUserAgentSpecificMemory` or `performance.memory` where available, else "n/a"), success/crash + error text. A crash in one step must not stop the others. Add a **one-click "Copy results"** (JSON + a short text summary).
   - Add a watchdog: write progress to `localStorage`, so after a tab crash or reload the page shows "last run crashed at step X".
4. **Output:** `bench/index.html`, `bench/*.js`, `bench/README.md` (how to host and run, including the Codespace port-forward recipe: `python3 -m http.server` in `bench/` + forwarded HTTPS port; GitHub Pages as an alternative, not enabled). Desktop smoke-test evidence: run it in headless Chromium if available; if not, say so plainly. Return at `company/handoffs/H-0030-return.md`.
5. **Done when:**
   - [ ] The page loads with no console errors in at least one real browser engine you can run. If you can't run any, STATUS must be PARTIAL and the return must say so.
   - [ ] The synthetic export produces a playable MP4 that you verify with ffprobe (1080×1920, 30 fps, ~30 s), if a headless run was possible.
   - [ ] The results JSON schema is documented in the README.
6. **Out of scope:** publishing or hosting it anywhere public; analytics; any server.
7. **Effort budget:** max 50 tool calls · 2 retries.
8. **Escalate if:** no CDN-hosted Whisper runtime works without a build step; a needed lib has a licence problem.
9. **Termination condition:** committed (do not push), return written.
10. **Consulted:** none. The Operator decides hosting with the Founder.

## Addendum (Operator, Founder memo 2)
- The Founder will include the **lowest-end phone** in the 3. Model choice is automatic: try base on WebGPU, then tiny on WebGPU, then tiny on WASM. Record which one ran. Also make the 30 s export resolution-safe: if 1080×1920 encoding is unsupported or fails, log it as FAIL and retry at 720×1280. Report both, and never silently downgrade.
- Show the device's memory hints (`navigator.deviceMemory`, `hardwareConcurrency`) in the results.
