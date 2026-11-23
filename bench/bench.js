// Device benchmark runner (H-0030). Each step is isolated: a thrown error becomes that step's FAIL record and
// the next step still runs. Progress goes to localStorage first, so a tab crash leaves "crashed at step X".
import { SCHEMA_VERSION, watchdog, probeDevice, MemorySampler } from "./env.js";
import * as L from "./libs.js";
import { runAsr, decodeTo16k } from "./asr.js";
import { runExport, drawSynthetic, syntheticTone, videoBackground, decodeTo48k, CAPTION_AR, CAPTION_EN } from "./export.js";

export const PAGE_VERSION = "H-0030 v1";
const $ = (id) => document.getElementById(id);
const exportsById = {};
let results = null;

function log(msg) { const el = $("progress"); if (el) el.textContent = msg; }

function render() {
  $("json").value = JSON.stringify(results, null, 2);
  $("summary").textContent = summaryText(results);
}

export function summaryText(r) {
  if (!r) return "";
  const d = r.device ?? {};
  const lines = [
    `bench ${r.page_version} run ${r.run_id} ${r.finished_at ? "finished" : "INCOMPLETE"}`,
    `device: mem ${d.device_memory_gb} GB, ${d.hardware_concurrency} cores, WebGPU ${d.webgpu_available ? "yes" : "no"}`,
  ];
  for (const s of r.steps) {
    let extra = "";
    if (s.id.includes("export") && s.status === "ok") extra = ` ${s.width}x${s.height} ${s.export_ms} ms ${s.export_fps} fps ${s.video_codec}+${s.audio_codec}`;
    if (s.id.endsWith("asr") && s.status === "ok") extra = ` ${s.model}/${s.backend} load ${s.model_load_ms} ms RTF ${s.rtf}`;
    const mem = s.peak_memory_bytes === "n/a" || s.peak_memory_bytes == null ? "n/a" : `${Math.round(s.peak_memory_bytes / 1048576)} MB`;
    lines.push(`${s.id}: ${s.status.toUpperCase()}${extra} peak ${mem}${s.error ? ` (${s.error})` : ""}`);
  }
  return lines.join("\n");
}

async function step(id, fn) {
  watchdog.step(results.run_id, id);
  log(`running ${id}`);
  const rec = { id, status: "fail", started_at: new Date().toISOString(), duration_ms: null, error: null };
  const mem = new MemorySampler();
  mem.start();
  const t0 = performance.now();
  try {
    const out = await fn((m) => log(`${id}: ${m}`));
    Object.assign(rec, out);
    if (!out || !out.status) rec.status = "ok";
  } catch (e) {
    rec.status = "fail";
    rec.error = String(e?.message ?? e);
  }
  rec.duration_ms = Math.round(performance.now() - t0);
  Object.assign(rec, await mem.stop());
  if (rec.blob) { exportsById[id] = rec.blob; delete rec.blob; showVideo(id); }
  results.steps.push(rec);
  watchdog.saveResults(results);
  render();
  return rec;
}

function showVideo(id) {
  const url = URL.createObjectURL(exportsById[id]);
  const li = document.createElement("li");
  li.innerHTML = `<a download="${id}.mp4" href="${url}">${id}.mp4</a>`;
  $("downloads").appendChild(li);
}

async function loadFonts() {
  const faces = [new FontFace("Noto Sans Arabic", `url(${L.FONT_ARABIC_URL})`), new FontFace("Noto Sans", `url(${L.FONT_LATIN_URL})`)];
  for (const f of faces) { await f.load(); document.fonts.add(f); }
  const ok = document.fonts.check("80px 'Noto Sans Arabic'", CAPTION_AR) && document.fonts.check("80px 'Noto Sans'", CAPTION_EN);
  if (!ok) throw new Error("fonts loaded but document.fonts.check() is false");
  return { status: "ok", fonts: [L.FONT_ARABIC_URL, L.FONT_LATIN_URL] };
}

async function exportStep(width, height, onProgress, source) {
  const seconds = source?.seconds ?? 30;
  return runExport({ width, height, seconds, onProgress,
    drawBackground: source?.draw ?? drawSynthetic, audio: source ? source.audio : syntheticTone(seconds) });
}

export async function runAll() {
  const sim = new URLSearchParams(location.search).get("simulate"); // test hook: "fail1080"
  const opts = { asr: $("opt-asr").checked, also720: $("opt-720").checked, file: $("file").files[0] ?? null, lang: $("lang").value || null };
  results = { schema: SCHEMA_VERSION, page_version: PAGE_VERSION, run_id: `${Date.now().toString(36)}`,
    started_at: new Date().toISOString(), finished_at: null, options: { asr: opts.asr, also_720: opts.also720,
      local_file: opts.file ? { size_bytes: opts.file.size, type: opts.file.type } : null, file_language: opts.lang ?? "auto", simulate: sim },
    libs: { transformers: L.TRANSFORMERS_URL, ort_wasm: L.ORT_WASM_BASE, mp4_muxer: L.MP4_MUXER_URL,
      fonts: [L.FONT_ARABIC_URL, L.FONT_LATIN_URL], models: L.MODELS, speech_sample: L.SPEECH_SAMPLE_URL },
    device: null, steps: [] };
  $("downloads").innerHTML = "";
  $("run").disabled = true;
  watchdog.begin(results.run_id);

  await step("env", async () => { results.device = await probeDevice(); return { status: "ok" }; });
  await step("fonts", () => loadFonts());
  const e1080 = await step("export_1080", async (p) => {
    if (sim === "fail1080") throw new Error("simulated FAIL (?simulate=fail1080 test hook)");
    return exportStep(1080, 1920, p);
  });
  if (e1080.status !== "ok" || opts.also720) {
    await step("export_720", async (p) => ({ ...(await exportStep(720, 1280, p)),
      reason: e1080.status !== "ok" ? "retry after export_1080 FAIL" : "also_720 option" }));
  } else {
    results.steps.push({ id: "export_720", status: "skipped", error: null, reason: "export_1080 ok; tick 'also 720' to run" });
  }
  const gpu = results.device?.webgpu_available === true;
  if (opts.asr) {
    await step("sample_asr", async (p) => {
      const buf = await (await fetch(L.SPEECH_SAMPLE_URL)).arrayBuffer();
      const out = await runAsr(await decodeTo16k(buf), { language: "english", webgpuAvailable: gpu, onProgress: p });
      return { ...out, reference: L.SPEECH_SAMPLE_REFERENCE };
    });
  } else {
    results.steps.push({ id: "sample_asr", status: "skipped", error: null, reason: "ASR unticked" });
  }
  if (opts.file) {
    const bytes = await opts.file.arrayBuffer();
    if (opts.asr) {
      await step("file_asr", async (p) => runAsr(await decodeTo16k(bytes.slice(0)), { language: opts.lang, webgpuAvailable: gpu, onProgress: p }));
    }
    const ok1080 = e1080.status === "ok";
    await step("file_export", async (p) => {
      const bg = await videoBackground(opts.file);
      let audio = null;
      try { audio = await decodeTo48k(bytes.slice(0), bg.seconds); } catch (_) { audio = null; }
      const out = await exportStep(ok1080 ? 1080 : 720, ok1080 ? 1920 : 1280, p, { ...bg, audio });
      bg.release();
      return { ...out, note: "seek-per-frame decode; export_fps is a lower bound" };
    });
  }
  results.finished_at = new Date().toISOString();
  watchdog.saveResults(results);
  watchdog.finish(results.run_id);
  render();
  log("done");
  $("run").disabled = false;
  return results;
}

async function copyResults() {
  const text = `${summaryText(results)}\n\n${JSON.stringify(results, null, 2)}`;
  try { await navigator.clipboard.writeText(text); log("copied results to the clipboard"); return; } catch (_) { /* fallback */ }
  const ta = $("json"); ta.value = text; ta.select();
  log(document.execCommand("copy") ? "copied results to the clipboard" : "copy failed: select the text box and copy by hand");
}

function init() {
  const crash = watchdog.previousCrash();
  if (crash) {
    $("crash").hidden = false;
    $("crash").textContent = `Last run (${crash.run_id}) crashed at step "${crash.step}" (${crash.at}). Its partial results are loaded below.`;
    results = watchdog.previousResults();
    if (results) render();
  }
  $("run").addEventListener("click", () => runAll());
  $("copy").addEventListener("click", () => copyResults());
  window.__bench = { runAll, get results() { return results; }, exportsById };
  const q = new URLSearchParams(location.search);
  if (q.get("asr") === "0") $("opt-asr").checked = false;
  if (q.get("autorun") === "1") runAll();
}

init();
