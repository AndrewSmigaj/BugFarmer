// screens.mjs — look at the built review app in a real browser (docs/plans/review-app.md).
//   node tools/gdd/tests/screens.mjs [tools/gdd/_build/review_app.html] [out dir]
// Opens every page at 1440 and 400 px wide, light and dark, saves screenshots, and fails (exit 1) on:
// sideways scrolling, visible text under 16 px (map labels excepted), the village map not north-up, or console errors.
// Playwright is found by pw.mjs (PLAYWRIGHT_DIR or the npx cache).
import { mkdirSync, writeFileSync } from "fs";
import { join, resolve } from "path";
import { chromium } from "./pw.mjs";

const page = resolve(process.argv[2] || "tools/gdd/_build/review_app.html");
const day = new Date().toISOString().slice(0, 10);
const out = resolve(process.argv[3] || `tools/gdd/_build/shots/${day}`);
mkdirSync(out, { recursive: true });
const ROUTES = ["zones", "z-village", "zh-village.fence_picket_weathered", "z-spider_vale_east", "b-house_fly", "bugs", "items", "k-decoration", "archive", "design", "s-03", "s-08", "status", "explain", "e-01-behaviour-model", "e-03-scaling"];
const VIEWS = [[1440, 900], [400, 800]];
const SCHEMES = ["light", "dark"];
const failures = [], notes = [];

const browser = await chromium.launch();
for (const [w, h] of VIEWS) for (const scheme of SCHEMES) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme });
  const p = await ctx.newPage();
  const errors = [];
  p.on("pageerror", e => errors.push(String(e)));
  p.on("console", m => { if (m.type() === "error" && !/fonts\.g|ERR_|net::/.test(m.text())) errors.push(m.text()); });
  for (const r of ROUTES) {
    await p.goto(`file://${page}#${r}`);
    await p.waitForTimeout(r.startsWith("z") ? 900 : 300);
    const tag = `${w}_${scheme}_${r.replace(/[^a-z0-9_-]+/gi, "_")}`;
    await p.screenshot({ path: join(out, tag + ".png"), fullPage: false });
    const m = await p.evaluate(() => {
      const sw = document.documentElement.scrollWidth, vw = window.innerWidth;
      let small = [];
      const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walk.nextNode()) {
        const n = walk.currentNode, el = n.parentElement;
        if (!n.textContent.trim() || !el || el.closest("svg") || el.closest("[hidden]") || el.closest("details:not([open])")) continue;
        const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < 15.95) small.push(`${el.tagName}.${el.className}: ${fs}px "${n.textContent.trim().slice(0, 30)}"`);
      }
      return { sw, vw, small: small.slice(0, 5), title: document.title };
    });
    if (m.sw > m.vw + 1) failures.push(`${tag}: page is ${m.sw}px wide in a ${m.vw}px window (sideways scroll)`);
    if (m.small.length) failures.push(`${tag}: text under 16px: ${m.small.join(" | ")}`);
    if (r === "z-village") {
      const probe = await p.evaluate(() => {
        const cv = document.getElementById("map"); const mp = DATA.maps.village;
        if (!cv || cv.hidden || !mp.probe) return { ok: false, why: "no map" };
        const px = cv.getContext("2d").getImageData(mp.probe.x, mp.h - 1 - mp.probe.y, 1, 1).data;
        const labels = [...document.querySelectorAll("#mapsvg text")].map(t => t.textContent);
        return { ok: true, px: [...px], west: labels.some(t => t.includes("Bee Meadow")), south: labels.some(t => t.includes("Mining Camp")) };
      });
      if (!probe.ok) failures.push(`${tag}: village map not drawn (${probe.why})`);
      else {
        const [r2, g, b] = probe.px;
        if (!(b > 150 && r2 < 120)) failures.push(`${tag}: the probe pixel isn't deep water: ${probe.px}`);
        if (!probe.west || !probe.south) failures.push(`${tag}: edge labels wrong (west Bee Meadow: ${probe.west}, south Mining Camp: ${probe.south})`);
      }
    }
  }
  if (errors.length) failures.push(`${w}_${scheme}: console errors: ${errors.slice(0, 5).join(" | ")}`);
  await ctx.close();
}
await browser.close();
writeFileSync(join(out, "report.json"), JSON.stringify({ page, failures, notes }, null, 2));
console.log(`${ROUTES.length * VIEWS.length * SCHEMES.length} screenshots -> ${out}`);
if (failures.length) { console.log("FAILURES:\n  " + failures.join("\n  ")); process.exit(1); }
console.log("all checks passed");
