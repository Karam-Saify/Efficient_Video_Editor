// On-device export step: canvas frames -> WebCodecs H.264 (+ AAC, else Opus, else no audio) -> MP4 (mp4-muxer).
// Captions are burned on the canvas with the EXP-008 font pair, sized from the `clean` preset in src/presets.py
// (80 px at 1080 wide, white fill, 4 px black outline, 320 px bottom margin), scaled with the frame width.
// All timing arithmetic is integer microseconds computed here, from the frame index.
import { MP4_MUXER_URL } from "./libs.js";

export const FPS = 30;
export const CAPTION_AR = "هذا اختبار للتصدير على الهاتف";
export const CAPTION_EN = "On-device export test";
const CLEAN = { size: 80, outline: 4, margin_v: 320, color: "#FFFFFF", outline_color: "#000000" };
const FONT_STACK = "'Noto Sans Arabic', 'Noto Sans'";

const CODECS = {
  "1080x1920": ["avc1.640028", "avc1.64002a", "avc1.4d0028", "avc1.42e028"],
  "720x1280": ["avc1.64001f", "avc1.4d001f", "avc1.42e01f"],
};
const BITRATE = { "1080x1920": 8_000_000, "720x1280": 4_000_000 };
const SAMPLE_RATE = 48000;

const tsUs = (i) => Math.round((i * 1_000_000) / FPS);

// Deterministic synthetic picture: frame index only, no clock, no randomness.
export function drawSynthetic(ctx, i, W, H) {
  const hue = (i * 2) % 360;
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, `hsl(${hue}, 60%, 35%)`);
  g.addColorStop(1, `hsl(${(hue + 120) % 360}, 60%, 15%)`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  const r = W * 0.12;
  const x = W / 2 + Math.sin((i / FPS) * Math.PI) * (W / 2 - r);
  const y = H * 0.35 + Math.cos((i / FPS) * Math.PI * 0.5) * H * 0.1;
  ctx.fillStyle = "rgba(255,255,255,0.85)";
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "rgba(0,0,0,0.6)";
  ctx.font = `${Math.round(W * 0.05)}px ${FONT_STACK}`;
  ctx.textAlign = "left"; ctx.direction = "ltr";
  ctx.fillText(`frame ${i}`, W * 0.05, H * 0.08);
}

// 440 Hz tone, beeping on for the first 0.25 s of every second.
export function syntheticTone(seconds) {
  const n = seconds * SAMPLE_RATE;
  const out = new Float32Array(n);
  for (let s = 0; s < n; s++) {
    const on = (s % SAMPLE_RATE) < SAMPLE_RATE / 4;
    out[s] = on ? 0.3 * Math.sin((2 * Math.PI * 440 * s) / SAMPLE_RATE) : 0;
  }
  return out;
}

export function drawCaptions(ctx, W, H) {
  const k = W / 1080;
  const size = Math.round(CLEAN.size * k);
  const lineH = Math.round(size * 1.3);
  const bottom = H - Math.round(CLEAN.margin_v * k);
  ctx.textAlign = "center";
  ctx.lineJoin = "round";
  ctx.lineWidth = 2 * CLEAN.outline * k; // canvas strokes centred on the path; ASS outline is outside only
  ctx.strokeStyle = CLEAN.outline_color;
  ctx.fillStyle = CLEAN.color;
  ctx.font = `${size}px ${FONT_STACK}`;
  const lines = [[CAPTION_AR, "rtl", bottom - lineH], [CAPTION_EN, "ltr", bottom]];
  for (const [text, dir, y] of lines) {
    ctx.direction = dir;
    ctx.strokeText(text, W / 2, y);
    ctx.fillText(text, W / 2, y);
  }
}

async function pickVideoCodec(W, H) {
  const key = `${W}x${H}`;
  const tried = [];
  for (const codec of CODECS[key]) {
    const cfg = { codec, width: W, height: H, bitrate: BITRATE[key], framerate: FPS, avc: { format: "avc" } };
    try {
      const s = await VideoEncoder.isConfigSupported(cfg);
      tried.push(`${codec}:${s.supported}`);
      if (s.supported) return { cfg, tried };
    } catch (e) { tried.push(`${codec}:error ${e?.message ?? e}`); }
  }
  return { cfg: null, tried };
}

async function pickAudioCodec() {
  if (typeof AudioEncoder !== "function") return null;
  for (const [codec, muxCodec] of [["mp4a.40.2", "aac"], ["opus", "opus"]]) {
    const cfg = { codec, sampleRate: SAMPLE_RATE, numberOfChannels: 1, bitrate: 128000 };
    try { if ((await AudioEncoder.isConfigSupported(cfg)).supported) return { cfg, muxCodec }; } catch (_) { /* next */ }
  }
  return null;
}

async function encodeAudio(muxer, acfg, samples) {
  let err = null;
  const enc = new AudioEncoder({ output: (c, m) => muxer.addAudioChunk(c, m), error: (e) => { err = e; } });
  enc.configure(acfg);
  const block = SAMPLE_RATE / 10;
  for (let s = 0; s < samples.length; s += block) {
    const part = samples.subarray(s, Math.min(s + block, samples.length));
    const ad = new AudioData({ format: "f32-planar", sampleRate: SAMPLE_RATE, numberOfFrames: part.length,
      numberOfChannels: 1, timestamp: Math.round((s * 1_000_000) / SAMPLE_RATE), data: part });
    enc.encode(ad); ad.close();
  }
  await enc.flush(); enc.close();
  if (err) throw err;
}

// drawBackground(ctx, i, W, H) may be async (the local-file path seeks a <video>).
export async function runExport({ width: W, height: H, seconds, drawBackground, audio, onProgress }) {
  const r = { status: "fail", width: W, height: H, fps: FPS, seconds, frames: seconds * FPS, video_codec: null,
    audio_codec: "none", codec_candidates: null, export_ms: null, export_fps: null, bytes: null, error: null };
  if (typeof VideoEncoder !== "function" || typeof VideoFrame !== "function") {
    r.error = "WebCodecs VideoEncoder/VideoFrame unavailable"; return r;
  }
  const { Muxer, ArrayBufferTarget } = await import(MP4_MUXER_URL);
  const { cfg, tried } = await pickVideoCodec(W, H);
  r.codec_candidates = tried;
  if (!cfg) { r.error = `no supported H.264 config at ${W}x${H}`; return r; }
  r.video_codec = cfg.codec;
  const a = audio ? await pickAudioCodec() : null;
  r.audio_codec = a ? a.cfg.codec : (audio ? "none (no AAC/Opus encoder)" : "none");

  const target = new ArrayBufferTarget();
  const muxer = new Muxer({ target, fastStart: "in-memory", firstTimestampBehavior: "offset",
    video: { codec: "avc", width: W, height: H, frameRate: FPS },
    ...(a ? { audio: { codec: a.muxCodec, numberOfChannels: 1, sampleRate: SAMPLE_RATE } } : {}) });
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d", { alpha: false });

  let encErr = null;
  const enc = new VideoEncoder({ output: (c, m) => muxer.addVideoChunk(c, m), error: (e) => { encErr = e; } });
  const t0 = performance.now();
  try {
    enc.configure({ ...cfg, latencyMode: "quality" });
    if (a) await encodeAudio(muxer, a.cfg, audio.subarray(0, seconds * SAMPLE_RATE));
    for (let i = 0; i < r.frames; i++) {
      await drawBackground(ctx, i, W, H);
      drawCaptions(ctx, W, H);
      const vf = new VideoFrame(canvas, { timestamp: tsUs(i), duration: tsUs(i + 1) - tsUs(i) });
      enc.encode(vf, { keyFrame: i % (2 * FPS) === 0 });
      vf.close();
      while (enc.encodeQueueSize > 2 && !encErr) await new Promise((res) => setTimeout(res, 1));
      if (encErr) throw encErr;
      if (i % FPS === 0) onProgress?.(`${W}x${H} frame ${i}/${r.frames}`);
    }
    await enc.flush();
    if (encErr) throw encErr;
    muxer.finalize();
    r.export_ms = Math.round(performance.now() - t0);
    r.export_fps = Number((r.frames / (r.export_ms / 1000)).toFixed(2));
    r.bytes = target.buffer.byteLength;
    r.status = "ok";
    r.blob = new Blob([target.buffer], { type: "video/mp4" });
  } catch (e) {
    r.error = String(e?.message ?? e);
  } finally {
    try { enc.close(); } catch (_) { /* already closed */ }
  }
  return r;
}

// Local file: seek a muted <video> to each frame time and cover-fit it into the canvas. The file never
// leaves the device. Seeking is slower than a real decoder pipeline, so export_fps here is a lower bound.
export async function videoBackground(file) {
  const v = document.createElement("video");
  v.muted = true; v.playsInline = true; v.preload = "auto";
  v.src = URL.createObjectURL(file);
  await new Promise((res, rej) => { v.onloadeddata = res; v.onerror = () => rej(new Error("video element cannot decode this file")); });
  const seconds = Math.max(1, Math.min(30, Math.floor(v.duration)));
  const draw = async (ctx, i, W, H) => {
    v.currentTime = i / FPS;
    await new Promise((res) => { const t = setTimeout(res, 3000); v.onseeked = () => { clearTimeout(t); res(); }; });
    const s = Math.max(W / v.videoWidth, H / v.videoHeight);
    const dw = v.videoWidth * s, dh = v.videoHeight * s;
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
    ctx.drawImage(v, (W - dw) / 2, (H - dh) / 2, dw, dh);
  };
  return { seconds, draw, release: () => URL.revokeObjectURL(v.src) };
}

export async function decodeTo48k(arrayBuffer, seconds) {
  const ctx = new OfflineAudioContext(1, 1, SAMPLE_RATE);
  const buf = await ctx.decodeAudioData(arrayBuffer);
  const n = seconds * SAMPLE_RATE;
  const out = new Float32Array(n);
  const m = Math.min(n, buf.length);
  for (let c = 0; c < buf.numberOfChannels; c++) {
    const ch = buf.getChannelData(c);
    for (let i = 0; i < m; i++) out[i] += ch[i] / buf.numberOfChannels;
  }
  return out;
}
