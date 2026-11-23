// On-device ASR step: Whisper via transformers.js, automatic model ladder (H-0030 addendum):
//   1. whisper-base on WebGPU  2. whisper-tiny on WebGPU  3. whisper-tiny on WASM
// The first rung that loads AND transcribes wins. Every rung tried is recorded; nothing is silent.
import { TRANSFORMERS_URL, ORT_WASM_BASE, MODELS } from "./libs.js";

const WEBGPU_DTYPE = { encoder_model: "fp32", decoder_model_merged: "q4" };
const WASM_DTYPE = { encoder_model: "q8", decoder_model_merged: "q8" };

export const LADDER = [
  { model: "whisper-base", device: "webgpu", dtype: WEBGPU_DTYPE },
  { model: "whisper-tiny", device: "webgpu", dtype: WEBGPU_DTYPE },
  { model: "whisper-tiny", device: "wasm", dtype: WASM_DTYPE },
];

let tf = null;
async function transformers() {
  if (!tf) {
    tf = await import(TRANSFORMERS_URL);
    tf.env.allowLocalModels = false; // a static host has no /models/ folder; avoid 404s
    if (tf.env.backends?.onnx?.wasm) tf.env.backends.onnx.wasm.wasmPaths = ORT_WASM_BASE;
  }
  return tf;
}

// Decode any audio the browser can read to 16 kHz mono Float32 (Whisper's input), at most maxSeconds.
export async function decodeTo16k(arrayBuffer, maxSeconds = 30) {
  const ctx = new OfflineAudioContext(1, 1, 16000);
  const buf = await ctx.decodeAudioData(arrayBuffer);
  const n = Math.min(buf.length, maxSeconds * 16000);
  const out = new Float32Array(n);
  for (let c = 0; c < buf.numberOfChannels; c++) {
    const ch = buf.getChannelData(c);
    for (let i = 0; i < n; i++) out[i] += ch[i] / buf.numberOfChannels;
  }
  return out;
}

// audio: Float32Array at 16 kHz. language: "english" | "arabic" | null (auto-detect).
export async function runAsr(audio, { language, webgpuAvailable, onProgress }) {
  const audioS = audio.length / 16000;
  const attempts = [];
  const lib = await transformers();
  for (const rung of LADDER) {
    const a = { model: rung.model, device: rung.device, dtype: rung.dtype, status: "fail", error: null };
    attempts.push(a);
    if (rung.device === "webgpu" && !webgpuAvailable) { a.status = "skipped"; a.error = "WebGPU unavailable"; continue; }
    let asr = null;
    try {
      onProgress?.(`loading ${rung.model} on ${rung.device}`);
      const t0 = performance.now();
      asr = await lib.pipeline("automatic-speech-recognition", MODELS[rung.model].id, {
        revision: MODELS[rung.model].revision, device: rung.device, dtype: rung.dtype,
        progress_callback: (p) => { if (p.status === "progress" && p.file) onProgress?.(`${rung.model}: ${p.file} ${Math.round(p.progress ?? 0)}%`); },
      });
      a.model_load_ms = Math.round(performance.now() - t0);
      onProgress?.(`transcribing with ${rung.model} on ${rung.device}`);
      const t1 = performance.now();
      const opts = { task: "transcribe", chunk_length_s: 30, return_timestamps: false };
      if (language) opts.language = language;
      const out = await asr(audio, opts);
      a.transcribe_ms = Math.round(performance.now() - t1);
      a.text = (out?.text ?? "").trim();
      a.status = "ok";
      await asr.dispose?.();
      return {
        status: "ok", model: rung.model, model_id: MODELS[rung.model].id, revision: MODELS[rung.model].revision,
        backend: rung.device, dtype: rung.dtype, language: language ?? "auto",
        model_load_ms: a.model_load_ms, audio_s: Number(audioS.toFixed(3)), transcribe_ms: a.transcribe_ms,
        rtf: Number((a.transcribe_ms / 1000 / audioS).toFixed(4)), text: a.text, attempts,
        note: "model_load_ms includes the download on a first run; run twice for a cached load time",
      };
    } catch (e) {
      a.error = String(e?.message ?? e);
      try { await asr?.dispose?.(); } catch (_) { /* ignore */ }
    }
  }
  return { status: "fail", error: "every ladder rung failed or was skipped", attempts, audio_s: Number(audioS.toFixed(3)) };
}
