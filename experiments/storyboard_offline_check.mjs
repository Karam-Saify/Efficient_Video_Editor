// H-0035: open a storyboard from file://, log every request that is not file:/data:/blob:, edit one scene,
// press Export corrections and save the download. Exit 1 on any network request or console error.
//   NODE_PATH=<dir>/node_modules PLAYWRIGHT_BROWSERS_PATH=<dir>/browsers \
//     node experiments/storyboard_offline_check.mjs <storyboard/index.html> <out.json> [scene_id] [role]
import { createRequire } from "node:module";
import { resolve } from "node:path";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const [page_path, out, scene = "1", role = "demo"] = process.argv.slice(2);
const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ acceptDownloads: true });
const page = await ctx.newPage();
const external = [], errors = [];
page.on("request", (r) => { if (!/^(file|data|blob):/.test(r.url())) external.push(r.url()); });
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push(String(e)));
await page.goto("file://" + resolve(page_path));
await page.waitForLoadState("networkidle");
const sel = `.scene[data-scene="${scene}"]`;
await page.fill(`${sel} .desc`, "تعديل من المتصفح (headless check)");
await page.selectOption(`${sel} .role`, role);
const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#export")]);
await dl.saveAs(out);
const imgs = await page.$$eval("img", (els) => els.filter((e) => e.naturalWidth > 0).length);
console.log(JSON.stringify({ external_requests: external, console_errors: errors, images_rendered: imgs, download: out }));
await browser.close();
process.exit(external.length || errors.length ? 1 : 0);
