// real_marks.mjs — open the review app on a COPY of the real stored marks, in a local test browser only
// (docs/plans/review-app.md, before publishing). Nothing is published or sent anywhere; the owner's text is never
// printed (ids and counts only).
//   node tools/gdd/tests/real_marks.mjs <export folder>       (an ArtifactData out_dir export; see tools/gdd/marks_diff.py)
// Checks, with the export loaded into the fake storage (tests/mock_db.js, no misbehaviour):
//   - opening the page writes NOTHING (publishing must not rewrite a single stored mark);
//   - every stored mark on a current row shows on that row: the right button pressed (or "applied", for a mark given
//     before the row was decided) and the same note;
//   - "Older notes" lists exactly the filled marks on rows the item table no longer has.
import { execFileSync } from "child_process";
import { readdirSync, readFileSync, statSync } from "fs";
import { join, relative, resolve, sep } from "path";
import { chromium } from "./pw.mjs";

const ROOT = resolve(new URL("../../..", import.meta.url).pathname);
const PAGE = resolve(ROOT, "tools/gdd/_build/review_app_test.html");
const EXPORT = resolve(process.argv[2] || "");
const sleep = ms => new Promise(r => setTimeout(r, ms));
const walk = d => readdirSync(d).flatMap(n => { const p = join(d, n); return statSync(p).isDirectory() ? walk(p) : [p]; });
const docs = walk(EXPORT).filter(p => p.endsWith(".json") && !p.endsWith("MANIFEST.json"))
  .map(p => { const rel = relative(EXPORT, p).split(sep); return [rel.join("/").replace(/\.json$/, ""), JSON.parse(readFileSync(p, "utf8"))]; })
  .filter(([p]) => /^(marks|notes|signoff)\//.test(p) || p.startsWith("item_marks/"));
if (!docs.length) { console.log(`no stored documents under ${EXPORT}`); process.exit(2); }

execFileSync("python3", [resolve(ROOT, "tools/gdd/build_app.py"), "--test-mock"], { cwd: ROOT, stdio: "pipe" });
const browser = await chromium.launch();
const ctx = await browser.newContext();
await ctx.addInitScript(c => { window.__MOCKCFG = c; }, { scenario: "real", seed: 1, latency: [5, 40], lateSnapRate: 0, docs });
const page = await ctx.newPage();
await page.goto(`file://${PAGE}#items`);
const problems = [];
// settle: nothing left to send for 3 checks running
for (let calm = 0, t0 = Date.now(); calm < 3 && Date.now() - t0 < 60000; ) {
  await sleep(1000);
  calm = /Saving|not stored|Connecting/.test(await page.locator("#status").textContent()) ? 0 : calm + 1;
}
const result = await page.evaluate(async docs => {
  const items = new Map(DATA.items.map(i => [i.id, i]));
  const filled = b => ["mark", "note", "choice", "other", "level"].some(k => typeof b[k] === "string" && b[k].trim());
  const want = new Map(), orphans = [];
  for (const [path, b] of docs) {
    if (!path.startsWith("marks/")) continue;
    const id = path.split("/").pop(), it = items.get(id);
    if (!it) { if (filled(b)) orphans.push(path); continue; }
    const prev = want.get(id);
    if (!prev || b.at > prev.at) want.set(id, b);       // a moved row: the newest copy wins, from any group
  }
  const look = () => {
    const out = {};
    for (const [id] of want) {
      const row = document.getElementById("row-" + id); if (!row) continue;
      out[id] = { pressed: [...row.querySelectorAll('[data-act="mark"][aria-pressed="true"]')].map(b => b.dataset.v).join(","),
        note: (row.querySelector("textarea.note") || {}).value || "", was: (row.querySelector(".was") || {}).textContent || "" };
    }
    return out;
  };
  const seen = {};
  for (const r of ["items", "archive"]) {
    location.hash = "zones"; await new Promise(r => setTimeout(r, 200));
    location.hash = r; await new Promise(r => setTimeout(r, 1200));
    Object.assign(seen, look());
  }
  const bad = [];
  for (const [id, b] of want) {
    const it = items.get(id), s = seen[id];
    if (!s) { bad.push(`${id}: row not shown`); continue; }
    const applied = !!(it.decided && b.mark && (b.on || "") !== it.decided);
    const pressed = applied ? "" : (b.mark || "");
    if (s.pressed !== pressed) bad.push(`${id}: pressed "${s.pressed}", stored mark should show "${pressed}"${applied ? " (applied)" : ""}`);
    if (applied && !s.was) bad.push(`${id}: an applied mark doesn't say so`);
    if (s.note !== (b.note || "")) bad.push(`${id}: note differs from the stored note`);
  }
  location.hash = "status"; await new Promise(r => setTimeout(r, 800));
  const shown = document.querySelectorAll(".orphans li").length;
  return { marks: want.size, orphans: orphans.length, shownOrphans: shown, bad, writes: __mock.writes.length,
    errors: __mock.pageErrors, status: document.querySelector("#status").textContent.replace(/last saved.*?(·|$)/, "") };
}, docs);
await browser.close();
if (result.writes) problems.push(`opening the page wrote ${result.writes} document(s) — it must write nothing`);
if (result.shownOrphans !== result.orphans) problems.push(`Older notes lists ${result.shownOrphans}, the export has ${result.orphans}`);
problems.push(...result.bad.slice(0, 20), ...result.errors.map(e => "page error: " + e.slice(0, 160)));
console.log(`${docs.length} stored documents; ${result.marks} marks on current rows, ${result.orphans} on removed rows; ` +
  `writes on opening: ${result.writes}; Older notes shown: ${result.shownOrphans}; status: ${result.status}`);
console.log(problems.length ? "FAIL\n  " + problems.join("\n  ") : "all checks passed");
process.exit(problems.length ? 1 : 0);
