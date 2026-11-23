// Device probe, memory sampler and crash watchdog for the device benchmark (H-0030).
// No network, no media: everything here reads browser APIs only.

export const SCHEMA_VERSION = "bench-results/1";
const WATCHDOG_KEY = "evb.bench.progress";
const RESULTS_KEY = "evb.bench.lastResults";

// localStorage can throw (private mode, blocked storage); the bench must still run without it.
function store(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* storage unavailable */ }
}
function load(key) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : null; } catch (_) { return null; }
}

export const watchdog = {
  // Returns the progress record of a run that never reached "finished", or null.
  previousCrash() {
    const p = load(WATCHDOG_KEY);
    return p && p.status === "running" ? p : null;
  },
  previousResults() { return load(RESULTS_KEY); },
  begin(runId) { store(WATCHDOG_KEY, { run_id: runId, status: "running", step: "start", at: new Date().toISOString() }); },
  step(runId, step) { store(WATCHDOG_KEY, { run_id: runId, status: "running", step, at: new Date().toISOString() }); },
  saveResults(results) { store(RESULTS_KEY, results); },
  finish(runId) { store(WATCHDOG_KEY, { run_id: runId, status: "finished", step: "done", at: new Date().toISOString() }); },
};

export async function probeDevice() {
  const nav = navigator;
  const d = {
    user_agent: nav.userAgent,
    platform: nav.userAgentData?.platform ?? nav.platform ?? "n/a",
    mobile: nav.userAgentData?.mobile ?? null,
    device_memory_gb: nav.deviceMemory ?? "n/a",
    hardware_concurrency: nav.hardwareConcurrency ?? "n/a",
    screen: { width: screen.width, height: screen.height, dpr: window.devicePixelRatio },
    secure_context: window.isSecureContext,
    cross_origin_isolated: window.crossOriginIsolated === true,
    webgpu_available: false,
    webgpu_adapter: null,
    webgpu_error: null,
    webcodecs: {
      video_encoder: typeof window.VideoEncoder === "function",
      audio_encoder: typeof window.AudioEncoder === "function",
      video_frame: typeof window.VideoFrame === "function",
    },
    memory_api: typeof performance.measureUserAgentSpecificMemory === "function" && window.crossOriginIsolated
      ? "measureUserAgentSpecificMemory" : (performance.memory ? "performance.memory" : "n/a"),
  };
  if (nav.gpu) {
    try {
      const adapter = await nav.gpu.requestAdapter();
      if (adapter) {
        d.webgpu_available = true;
        const info = adapter.info ?? (adapter.requestAdapterInfo ? await adapter.requestAdapterInfo() : {});
        d.webgpu_adapter = { vendor: info.vendor ?? "", architecture: info.architecture ?? "", description: info.description ?? "" };
      } else {
        d.webgpu_error = "navigator.gpu present but requestAdapter() returned null";
      }
    } catch (e) {
      d.webgpu_error = String(e?.message ?? e);
    }
  } else {
    d.webgpu_error = "navigator.gpu missing";
  }
  return d;
}

// Samples JS heap every 250 ms while a step runs. Peak is the largest sample, or "n/a" if no API exists.
// measureUserAgentSpecificMemory needs cross-origin isolation, which a plain static host does not give,
// so on most hosts the source is performance.memory (Chromium only) and Safari/Firefox report "n/a".
export class MemorySampler {
  constructor() { this.peak = null; this.source = "n/a"; this.timer = null; }
  start() {
    this.peak = null;
    if (performance.memory) {
      this.source = "performance.memory.usedJSHeapSize";
      const sample = () => { const v = performance.memory.usedJSHeapSize; if (this.peak === null || v > this.peak) this.peak = v; };
      sample();
      this.timer = setInterval(sample, 250);
    }
  }
  async stop() {
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    if (typeof performance.measureUserAgentSpecificMemory === "function" && window.crossOriginIsolated) {
      try {
        const m = await Promise.race([
          performance.measureUserAgentSpecificMemory(),
          new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 5000)),
        ]);
        if (this.peak === null || m.bytes > this.peak) { this.peak = m.bytes; this.source = "measureUserAgentSpecificMemory"; }
      } catch (_) { /* keep heap samples */ }
    }
    return { peak_memory_bytes: this.peak ?? "n/a", memory_source: this.peak === null ? "n/a" : this.source };
  }
}
