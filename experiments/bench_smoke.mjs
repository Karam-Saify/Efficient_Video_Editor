// H-0030 desktop smoke test for bench/ in headless Chromium (Playwright). Not part of the static page.
// Usage (Playwright is installed outside the repo, see bench/README.md "Smoke test"):
//   (cd bench && python3 -m http.server 8765) &
//   NODE_PATH=<dir>/node_modules PLAYWRIGHT_BROWSERS_PATH=<dir>/browsers node experiments/bench_smoke.mjs http://localhost:8765/ out/h0030
// Writes <outdir>/smoke.json (console errors, failed requests, results JSON) and <outdir>/<step>.mp4.
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const [url = "http://localhost:8765/", outDir = "out/h0030", ...flags] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });

const channel = process.env.BENCH_CHANNEL || undefined; // "chromium" = full build in new headless mode
const browser = await chromium.launch({ headless: true, channel, args: flags });
const browserVersion = browser.version();
const page = await browser.newPage();
const consoleErrors = [], pageErrors = [], failedRequests = [], consoleAll = [];
page.on("console", (m) => { consoleAll.push(`${m.type()}: ${m.text()}`); if (m.type() === "error") consoleErrors.push(m.text()); });
page.on("pageerror", (e) => pageErrors.push(String(e)));
page.on("requestfailed", (r) => failedRequests.push(`${r.url()} ${r.failure()?.errorText}`));

// BENCH_QUERY adds query params (e.g. "simulate=fail1080&asr=0"); BENCH_FILE picks a local clip;
// BENCH_CRASH_TEST=1 reloads mid-run and records the watchdog banner instead of finishing.
const query = process.env.BENCH_QUERY ? `&${process.env.BENCH_QUERY}` : "";
let crashBanner = null;
if (process.env.BENCH_CRASH_TEST === "1") {
  await page.goto(`${url}?autorun=1${query}`);
  await page.waitForFunction(() => document.getElementById("progress").textContent.startsWith("export_1080"), null, { timeout: 120000 });
  await page.goto(url); // simulated tab death: the run never reaches "finished"
  crashBanner = await page.textContent("#crash");
  writeFileSync(join(outDir, "crash.json"), JSON.stringify({ crashBanner, consoleErrors, pageErrors }, null, 2));
  console.log(`crash banner: ${crashBanner}`);
  await browser.close();
  process.exit(crashBanner && crashBanner.includes("export_1080") ? 0 : 1);
}
if (process.env.BENCH_FILE) {
  await page.goto(`${url}?x=1${query}`);
  await page.setInputFiles("#file", process.env.BENCH_FILE);
  await page.selectOption("#lang", "english");
  await page.click("#run");
} else {
  await page.goto(`${url}?autorun=1${query}`);
}
await page.waitForFunction(() => window.__bench?.results?.finished_at, null, { timeout: 20 * 60 * 1000, polling: 1000 });
const results = await page.evaluate(() => window.__bench.results);
const ids = await page.evaluate(() => Object.keys(window.__bench.exportsById));
for (const id of ids) {
  const b64 = await page.evaluate(async (k) => {
    const buf = new Uint8Array(await window.__bench.exportsById[k].arrayBuffer());
    let s = ""; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
    return btoa(s);
  }, id);
  writeFileSync(join(outDir, `${id}.mp4`), Buffer.from(b64, "base64"));
}
const summary = await page.textContent("#summary");
writeFileSync(join(outDir, "smoke.json"), JSON.stringify({ url, channel, browserVersion, flags, consoleErrors, pageErrors, failedRequests, consoleAll, summary, results }, null, 2));
console.log(summary);
console.log(`console errors: ${consoleErrors.length}, page errors: ${pageErrors.length}, failed requests: ${failedRequests.length}`);
await browser.close();
process.exit(consoleErrors.length + pageErrors.length ? 1 : 0);
