// save_stress.mjs — play marking sessions against misbehaving storage and check nothing the owner writes is lost
// (docs/plans/review-app.md, Test plan). Made-up data only; nothing is published.
//   node tools/gdd/tests/save_stress.mjs [scenario ...]      (default: every scenario)
// Builds tools/gdd/_build/review_app_test.html (the app with tests/mock_db.js as its storage), then runs each scenario
// in a fresh browser: a first visit, then a reload. Every scenario checks, besides its own expectations:
//   - every stored document holds exactly what was last answered (mark, note, choice, own answer, approval);
//   - the page never sends an older answer after a newer one, and every document ENDS on its newest answer (another
//     device's older answer can land last; the page notices and sends its newer one again);
//   - writes went only to the right path (an item's mark to its current group; never the old item_marks store);
//   - the screen shows the same answers, each "Stored";
//   - no page errors.
// Exit 1 on any failure; the details go to tools/gdd/_build/save_stress.json.
import { execFileSync } from "child_process";
import { writeFileSync } from "fs";
import { resolve } from "path";
import { chromium } from "./pw.mjs";

const ROOT = resolve(new URL("../../..", import.meta.url).pathname);
const PAGE = resolve(ROOT, "tools/gdd/_build/review_app_test.html");
const sleep = ms => new Promise(r => setTimeout(r, ms));
let seed = 11;
const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
const between = (a, b) => a + Math.floor(rnd() * (b - a + 1));
const pickOne = a => a[Math.floor(rnd() * a.length)];

execFileSync("python3", [resolve(ROOT, "tools/gdd/build_app.py"), "--test-mock"], { cwd: ROOT, stdio: "pipe" });

// ------------------------------------------------------------------ the data, read once from the built page
const browser = await chromium.launch();
const D = await (async () => {
  const ctx = await browser.newContext(); const p = await ctx.newPage();
  await p.addInitScript(() => { window.__MOCKCFG = { scenario: "probe" }; });
  await p.goto(`file://${PAGE}#zones`);
  const d = await p.evaluate(() => ({
    items: DATA.items.map(i => ({ id: i.id, group: i.group, verdict: i.verdict, decided: i.decided || "" })),
    zones: DATA.zones.map(z => z.id), groups: DATA.stored_groups,
    questions: DATA.sections.flatMap(s => s.questions.map(q => ({ sec: s.id, key: q.key, options: q.options.map(o => o.key) }))),
  }));
  await ctx.close();
  return d;
})();
const itemById = new Map(D.items.map(i => [i.id, i]));
const undecided = g => D.items.filter(i => i.group === g && !i.decided && i.verdict !== "cut");
const markPath = id => `marks/${itemById.get(id).group}/items/${id}`;
const pathOfK = k => (k.startsWith("i:") ? markPath(k.slice(2)) : k);
const FIELDS = ["mark", "note", "choice", "other", "level"];
const VALID = new RegExp("^(marks/(" + D.groups.join("|") + ")/items/[^/]+|notes/(zone|bug|gdd|section|system)/items/[^/]+|signoff/(zone|bug|section|system)/items/[^/]+)$");

// ------------------------------------------------------------------ a session: one page (or one device) and its expectations
class Session {
  constructor(name, page, exp) { this.name = name; this.page = page; this.exp = exp; this.problems = []; }
  e(path) { return this.exp[path] || (this.exp[path] = {}); }
  sel(k, act, v) { return `[data-k="${k}"]` + (act ? `[data-act="${act}"]` : "") + (v ? `[data-v="${v}"]` : ""); }
  async go(route) { await this.page.evaluate(r => { location.hash = r; }, route); await sleep(250); }
  async click(k, act, v) {
    await this.page.locator(this.sel(k, act, v)).first().click();
    const e = this.e(pathOfK(k));
    if (act === "mark" || act === "note") e.mark = (e.mark || "") === v ? "" : v;
    else if (act === "choice") e.choice = (e.choice || "") === v ? "" : v;
    else if (act === "approve") e.level = e.level === "approved" ? "" : "approved";
  }
  async type(k, field, text, { slow = false } = {}) {     // types at the end of what's there, then leaves the box
    const loc = this.page.locator(`[data-k="${k}"][data-f="${field}"]`).first();
    await loc.click();
    await this.page.keyboard.press("End");
    for (const ch of text) {
      await this.page.keyboard.type(ch);
      await sleep(slow ? between(30, rnd() < 0.15 ? 1400 : 250) : between(5, 40));
    }
    const v = await loc.inputValue();
    await this.page.locator("h1").first().click();           // leave the box: the page sends at once
    this.e(pathOfK(k))[field] = v;
  }
  fail(msg) { this.problems.push(msg); }
}

async function storeOf(page, shared) {
  if (shared) return { latest: new Map([...shared].map(([p, h]) => [p, h[h.length - 1]])), hist: shared };
  const [latest, hist] = await page.evaluate(() => [[...__mock.server], [...__mock.history]]);
  return { latest: new Map(latest), hist: new Map(hist) };
}

// Wait until the page has nothing left to send (status shows all stored, or nothing answered) for 3 checks running.
async function settle(page, { min = 1500, max = 60000 } = {}) {
  const t0 = Date.now(); let calm = 0;
  await sleep(min);
  while (Date.now() - t0 < max) {
    const s = await page.locator("#status").textContent();
    calm = /Saving|not stored|Connecting/.test(s) ? 0 : calm + 1;
    if (calm >= 3) return s;
    await sleep(700);
  }
  return await page.locator("#status").textContent();
}

// The checks every scenario shares.
async function verifyStore(S, shared, { untouched = [] } = {}) {
  const { latest, hist } = await storeOf(S.page, shared);
  for (const [path, e] of Object.entries(S.exp)) {
    const d = latest.get(path) || {};
    for (const f of FIELDS) if (f in e && (e[f] || "") !== (d[f] || "")) S.fail(`${path}: stored ${f}=${JSON.stringify(d[f] || "")}, expected ${JSON.stringify(e[f] || "")}`);
  }
  // Several writers can land out of order (another device's older answer after ours); the store must END on the newest.
  for (const [path, h] of hist) {
    const ats = h.map(b => b.at).filter(a => typeof a === "number");
    if (ats.length && h[h.length - 1].at !== Math.max(...ats)) S.fail(`${path}: the store ends on an older answer (at ${h[h.length - 1].at}, newest ${Math.max(...ats)})`);
  }
  for (const [path, n] of untouched) if ((hist.get(path) || []).length !== n) S.fail(`${path}: was written to (expected untouched)`);
}
async function verifyWrites(S) {
  const m = await S.page.evaluate(() => ({ writes: __mock.writes, errors: __mock.pageErrors }));
  const lastAt = {};
  for (const w of m.writes) {
    if (typeof w.at === "number") {                         // this page never sends an older answer after a newer one
      if (w.at < (lastAt[w.path] ?? -Infinity)) S.fail(`${w.path}: this page sent an older answer (${w.at}) after a newer one (${lastAt[w.path]})`);
      lastAt[w.path] = Math.max(lastAt[w.path] ?? -Infinity, w.at);
    }
    if (!VALID.test(w.path)) S.fail(`wrote to a wrong path: ${w.path}`);
    else if (w.path.startsWith("marks/")) { const id = w.path.split("/").pop(), it = itemById.get(id);
      if (!it || markPath(id) !== w.path) S.fail(`mark written outside its current group: ${w.path}`); }
    if (w.deleted) S.fail(`tried to delete ${w.path}`);
  }
  for (const e of m.errors) S.fail(`page error: ${e.slice(0, 200)}`);
  return m.writes.length;
}
// The screen, for the answers shown on the current route.
async function verifyScreen(S) {
  const shown = await S.page.evaluate(paths => {
    const out = {};
    for (const k of new Set([...document.querySelectorAll("[data-k]")].map(el => el.dataset.k).filter(Boolean))) {
      const path = k.startsWith("i:") ? `marks/${DATA.items.find(i => i.id === k.slice(2)).group}/items/${k.slice(2)}` : k;
      if (!paths.includes(path)) continue;
      const pressed = act => [...document.querySelectorAll(`[data-k="${k}"][data-act="${act}"][aria-pressed="true"]`)].map(b => b.dataset.v);
      const val = f => { const el = document.querySelector(`[data-k="${k}"][data-f="${f}"]`); return el ? el.value : undefined; };
      const st = document.querySelector(`[data-state="${k}"]`);
      out[path] = { mark: [...pressed("mark"), ...pressed("note")].join(","), choice: pressed("choice").join(","),
        level: document.querySelector(`[data-k="${k}"][data-act="approve"][aria-pressed="true"]`) ? "approved" : "",
        note: val("note"), other: val("other"), state: st ? st.textContent : "", hasMark: !!document.querySelector(`[data-k="${k}"][data-act="mark"],[data-k="${k}"][data-act="note"]`),
        hasChoice: !!document.querySelector(`[data-k="${k}"][data-act="choice"]`), hasApprove: !!document.querySelector(`[data-k="${k}"][data-act="approve"]`) };
    }
    return out;
  }, Object.keys(S.exp));
  for (const [path, s] of Object.entries(shown)) {
    const e = S.exp[path];
    if (s.hasMark && "mark" in e && s.mark !== (e.mark || "")) S.fail(`screen ${path}: pressed "${s.mark}", expected "${e.mark || ""}"`);
    if (s.hasChoice && "choice" in e && s.choice !== (e.choice || "")) S.fail(`screen ${path}: choice "${s.choice}", expected "${e.choice || ""}"`);
    if (s.hasApprove && "level" in e && s.level !== (e.level || "")) S.fail(`screen ${path}: approval "${s.level}", expected "${e.level || ""}"`);
    for (const f of ["note", "other"]) if (s[f] !== undefined && f in e && s[f] !== (e[f] || "")) S.fail(`screen ${path}: ${f} ${JSON.stringify(s[f])}, expected ${JSON.stringify(e[f] || "")}`);
    const filled = e.mark || e.choice || e.level || (e.note || "").trim() || (e.other || "").trim();
    if (filled && s.state !== "Stored" && (s.hasMark || s.hasChoice || s.hasApprove)) S.fail(`screen ${path}: shows "${s.state}", not Stored`);
  }
  return Object.keys(shown).length;
}

async function open(ctx, cfg, route) {
  await ctx.addInitScript(c => { window.__MOCKCFG = c; }, cfg);
  const page = await ctx.newPage();
  await page.goto(`file://${PAGE}#${route}`);
  await sleep(400);
  return page;
}
async function reload(page, ctx, cfg) {
  await ctx.addInitScript(c => { window.__MOCKCFG = c; }, { ...cfg, phase: 2 });   // the later init script wins
  await page.reload(); await sleep(400);
}
// Check every route an answer is shown on.
async function verifyAllScreens(S, routes) {
  let n = 0;
  for (const r of routes) { await S.go(r); await sleep(300); n += await verifyScreen(S); }
  return n;
}

// ------------------------------------------------------------------ the scenarios
const tools = undecided("tools");
const SC = {};

// Random marking with old views arriving all the time; another device changes two items mid-session.
async function marathon(S, { slowTyping = true } = {}) {
  await S.go("k-tools");
  let pool = tools.slice(0, 45).map(i => "i:" + i.id);
  for (let n = 0; n < 60; n++) {
    const k = pickOne(pool), r = rnd();
    if (r < 0.5) await S.click(k, "mark", rnd() < 0.75 ? "agree" : "disagree");
    else if (r < 0.8) await S.type(k, "note", " n" + n, { slow: slowTyping && rnd() < 0.3 });
    else { await S.click(k, "mark", "agree"); await sleep(between(5, 150)); await S.click(k, "mark", "agree"); }
    await sleep(between(20, 600));
    if (n === 30) {
      for (const rk of [pool[0], pool[pool.length - 1]]) {
        const id = rk.slice(2), p = markPath(id);
        await S.page.evaluate(([p, b]) => __mock.remoteWrite(p, b), [p, { id, group: itemById.get(id).group, mark: "disagree",
          note: "from the other device", at: Date.now() + 5000, on: "", page: "x" }]);
        S.exp[p] = { mark: "disagree", note: "from the other device" };
      }
      pool = pool.slice(1, -1);
    }
  }
  await S.go("z-village");
  const vm = "notes/zone/items/village.map", vp = "notes/zone/items/village.plan";
  for (let n = 0; n < 12; n++) {
    const r = rnd();
    if (r < 0.35) await S.click(pickOne([vm, vp]), "note", pickOne(["right", "change", "question"]));
    else if (r < 0.7) await S.type(pickOne([vm, vp]), "note", " z" + n);
    else await S.click(pickOne(["signoff/zone/items/village.map", "signoff/zone/items/village.plan"]), "approve");
    await sleep(between(20, 500));
  }
  const qs = D.questions.filter(q => q.sec === "04").slice(0, 3);
  await S.go("s-04");
  for (let n = 0; n < 8; n++) {
    const q = pickOne(qs), k = "notes/gdd/items/" + q.key;
    if (rnd() < 0.6) await S.click(k, "choice", pickOne([...q.options, "other"]));
    else await S.type(k, "other", " o" + n);
    await sleep(between(20, 400));
  }
}
const ROUTES = ["k-tools", "z-village", "s-04"];

SC.stress = async ctx => {
  const cfg = { scenario: "stress", seed: 7, staleEvery: 400 };
  const S = new Session("stress", await open(ctx, cfg, "zones"), {});
  await marathon(S);
  const st = await settle(S.page, { min: 20000, max: 90000 });
  if (!/^All \d+ answers? stored/.test(st)) S.fail(`status after saving: "${st}"`);
  await verifyWrites(S); await verifyStore(S); await verifyAllScreens(S, ROUTES);
  await reload(S.page, ctx, cfg); await settle(S.page, { min: 6000 });
  if (await verifyWrites(S)) S.fail("the reload wrote to the store");
  await verifyStore(S); await verifyAllScreens(S, ROUTES);
  return S;
};

SC.failures = async ctx => {
  const cfg = { scenario: "failures", seed: 9, staleEvery: 400, failRate: 0.3, exhaustRate: 0.1, readFailRate: 0.25 };
  const S = new Session("failures", await open(ctx, cfg, "zones"), {});
  await marathon(S, { slowTyping: false });
  const st = await settle(S.page, { min: 30000, max: 240000 });
  if (!/^All \d+ answers? stored/.test(st)) S.fail(`status after saving: "${st}"`);
  await verifyWrites(S); await verifyStore(S); await verifyAllScreens(S, ROUTES);
  await reload(S.page, ctx, { ...cfg, failRate: 0, exhaustRate: 0, readFailRate: 0 }); await settle(S.page, { min: 6000 });
  if (await verifyWrites(S)) S.fail("the reload wrote to the store");
  await verifyStore(S);
  return S;
};

// The storage refuses every write for a whole visit; the next visit sends everything.
SC.recovery = async ctx => {
  const cfg = { scenario: "recovery", seed: 3, failRate: 1 };
  const S = new Session("recovery", await open(ctx, cfg, "k-tools"), {});
  for (const it of tools.slice(0, 5)) await S.click("i:" + it.id, "mark", "agree");
  await S.type("i:" + tools[0].id, "note", "kept while the storage was down");
  await S.go("z-village"); await S.click("notes/zone/items/village.map", "note", "change");
  await sleep(6000);
  const st = await S.page.locator("#status").textContent();
  if (!/not stored yet/.test(st)) S.fail(`while the storage refuses: status "${st}"`);
  const { latest } = await storeOf(S.page);
  if (latest.size) S.fail(`the store holds ${latest.size} documents while every write failed`);
  await reload(S.page, ctx, { ...cfg, failRate: 0 });
  const st2 = await settle(S.page, { min: 4000 });
  if (!/^All 6 answers stored/.test(st2)) S.fail(`after the next visit: status "${st2}"`);
  await verifyWrites(S); await verifyStore(S); await verifyAllScreens(S, ["k-tools", "z-village"]);
  return S;
};

// Unsaved copies from an earlier visit: the newer of browser copy and stored copy wins, each way round.
SC.leftover = async ctx => {
  const [a, b] = tools, pa = markPath(a.id), pb = markPath(b.id);
  const vm = "notes/zone/items/village.map", bm = "notes/zone/items/bee_meadow.map";
  const cfg = { scenario: "leftover", seed: 5,
    local: { "bf-items-v2-local": { [a.id]: { mark: "agree", note: "", at: 100 }, [b.id]: { mark: "agree", note: "net note", at: 300 } },
      "bf-app-v1-local": { [vm]: { mark: "right", note: "local newer", at: 400 }, [bm]: { mark: "change", note: "local older", at: 100 } } },
    docs: [[pa, { id: a.id, group: "tools", mark: "", note: "", at: 50 }], [pa, { id: a.id, group: "tools", mark: "disagree", note: "other device", at: 200 }],
      [pb, { id: b.id, group: "tools", mark: "disagree", note: "", at: 200 }],
      [vm, { id: "village.map", kind: "zone", mark: "question", note: "stored older", at: 300 }],
      [bm, { id: "bee_meadow.map", kind: "zone", mark: "right", note: "stored newer", at: 250 }]] };
  const S = new Session("leftover", await open(ctx, cfg, "k-tools"), {
    [pa]: { mark: "disagree", note: "other device" }, [pb]: { mark: "agree", note: "net note" },
    [vm]: { mark: "right", note: "local newer" }, [bm]: { mark: "right", note: "stored newer" } });
  await settle(S.page, { min: 5000 });
  await verifyWrites(S); await verifyStore(S); await verifyAllScreens(S, ["k-tools", "z-village", "z-bee_meadow"]);
  await reload(S.page, ctx, cfg); await settle(S.page, { min: 5000 });
  if (await verifyWrites(S)) S.fail("the reload wrote to the store");
  await verifyStore(S);
  return S;
};

// Marks the very first items page kept (old store + this browser's dated key) come over once; a stored mark wins.
SC.legacy_import = async ctx => {
  const [x1, x2, x3, x4, x5] = tools.map(i => i.id);
  const cfg = { scenario: "legacy_import", seed: 13,
    local: { "bf-items-2026-09-28-marks": { tools: { [x1]: { mark: "agree" }, [x2]: { mark: "disagree", note: "old note" }, [x3]: { mark: "", note: "x3 note" }, [x4]: { mark: "" } } } },
    docs: [["item_marks/tools", { group: "tools", marks: { [x1]: { mark: "agree" }, [x5]: { mark: "agree" } }, updatedAt: "2026-09-29T22:02:49.821Z" }],
      [markPath(x2), { id: x2, group: "tools", mark: "agree", note: "", at: 1000, page: "x" }]] };
  const S = new Session("legacy_import", await open(ctx, cfg, "k-tools"), {
    [markPath(x1)]: { mark: "agree", note: "" }, [markPath(x2)]: { mark: "agree", note: "" }, [markPath(x3)]: { mark: "", note: "x3 note" },
    [markPath(x5)]: { mark: "agree", note: "" } });
  const st = await settle(S.page, { min: 6000 });
  if (!/brought back 3 from the first items page/.test(st)) S.fail(`status: "${st}"`);
  const { latest } = await storeOf(S.page);
  const rec = [x1, x3, x5].filter(id => (latest.get(markPath(id)) || {}).recovered);
  if (rec.length !== 3) S.fail(`recovered flags on ${rec.length} of 3 brought-back marks`);
  if ((latest.get(markPath(x2)) || {}).recovered) S.fail("a stored mark was overwritten by the old copy");
  if (latest.has(markPath(x4))) S.fail("an empty old mark was brought back");
  await verifyWrites(S); await verifyStore(S, null, { untouched: [["item_marks/tools", 1], [markPath(x2), 1]] }); await verifyScreen(S);
  await reload(S.page, ctx, cfg); await settle(S.page, { min: 5000 });
  if (await verifyWrites(S)) S.fail("the reload brought the old marks back again");
  return S;
};

// An item moved to another kind: its stored mark (under the old kind) still shows, and the next answer goes to the new kind.
SC.moved_group = async ctx => {
  const y = undecided("weapons")[0], old = `marks/tools/items/${y.id}`;
  const cfg = { scenario: "moved_group", seed: 17, docs: [[old, { id: y.id, group: "tools", mark: "agree", note: "from before the move", at: 500 }]] };
  const S = new Session("moved_group", await open(ctx, cfg, "k-weapons"), { [markPath(y.id)]: { mark: "agree", note: "from before the move" } });
  await settle(S.page, { min: 4000 });
  await verifyScreen(S);
  await S.click("i:" + y.id, "mark", "disagree");
  await settle(S.page, { min: 2000 });
  await verifyWrites(S); await verifyStore(S, null, { untouched: [[old, 1]] }); await verifyScreen(S);
  return S;
};

// Stored answers on rows that no longer exist are listed under "Older notes", never written to.
SC.orphan = async ctx => {
  const docs = [["marks/tools/items/zz_gone_item", { id: "zz_gone_item", group: "tools", mark: "agree", note: "kept old note", at: 10 }],
    ["notes/zone/items/atlantis.map", { id: "atlantis.map", kind: "zone", mark: "change", note: "a removed zone", at: 20 }],
    ["notes/gdd/items/04.removed-key", { id: "04.removed-key", kind: "gdd", mark: "", note: "old answer", at: 30 }]];
  const S = new Session("orphan", await open(ctx, { scenario: "orphan", seed: 19, docs }, "status"), {});
  await settle(S.page, { min: 5000 });
  await S.go("items"); await S.go("status"); await sleep(500);
  const txt = await S.page.locator(".orphans").textContent().catch(() => "");
  for (const w of ["kept old note", "a removed zone", "old answer"]) if (!txt.includes(w)) S.fail(`Older notes is missing "${w}"`);
  if (await verifyWrites(S)) S.fail("something was written");
  await verifyStore(S, null, { untouched: docs.map(([p]) => [p, 1]) });
  return S;
};

// A mark given before a row was decided shows as applied; one given after shows as pressed; answering again records it.
SC.applied_mark = async ctx => {
  const dec = D.items.filter(i => i.decided);
  const [d1, d2] = dec;
  const cfg = { scenario: "applied_mark", seed: 23, docs: [[markPath(d1.id), { id: d1.id, group: d1.group, mark: "agree", note: "", at: 10, on: "" }],
    [markPath(d2.id), { id: d2.id, group: d2.group, mark: "disagree", note: "", at: 10, on: d2.decided }]] };
  const S = new Session("applied_mark", await open(ctx, cfg, "i-" + d1.id), {});
  await settle(S.page, { min: 4000 });
  const look = async id => S.page.evaluate(id => ({ pressed: [...document.querySelectorAll(`[data-k="i:${id}"][aria-pressed="true"]`)].map(b => b.dataset.v).join(","),
    was: (document.querySelector(`[data-was="i:${id}"]`) || {}).textContent || "" }), id);
  let s = await look(d1.id);
  if (s.pressed !== "" || !/earlier Agree is applied/.test(s.was)) S.fail(`applied mark shows pressed="${s.pressed}" was="${s.was}"`);
  await S.go("i-" + d2.id); s = await look(d2.id);
  if (s.pressed !== "disagree" || s.was) S.fail(`a mark given after the decision shows pressed="${s.pressed}" was="${s.was}"`);
  await S.go("i-" + d1.id);
  await S.page.locator(`[data-k="i:${d1.id}"][data-act="mark"][data-v="agree"]`).click();
  await settle(S.page, { min: 2000 });
  s = await look(d1.id);
  const { latest } = await storeOf(S.page), b = latest.get(markPath(d1.id)) || {};
  if (s.pressed !== "agree" || s.was || b.mark !== "agree" || b.on !== d1.decided) S.fail(`answering again: pressed="${s.pressed}" was="${s.was}" stored=${JSON.stringify(b)}`);
  await verifyWrites(S);
  return S;
};

// Two devices on one store: each sees the other's answers; the newer answer wins on both; typing is never overwritten.
SC.two_devices = async () => {
  const shared = new Map();
  const bind = async ctx => ctx.exposeBinding("__srv", (_src, op, p, b) => {
    if (op === "put") { if (!shared.has(p)) shared.set(p, []); shared.get(p).push(JSON.parse(JSON.stringify(b))); return null; }
    const pre = p + "/", pick = m => Object.fromEntries([...shared].filter(([k]) => k.startsWith(pre) && !k.slice(pre.length).includes("/")).map(([k, h]) => [k, m(h)]));
    if (op === "list") return pick(h => h[h.length - 1]);
    if (op === "hist") return pick(h => h);
    if (op === "get") { const h = shared.get(p); return h ? h[h.length - 1] : null; }
  });
  const ca = await browser.newContext(), cb = await browser.newContext();
  await bind(ca); await bind(cb);
  const exp = {};
  const A = new Session("two_devices A", await open(ca, { scenario: "two_devices", seed: 29, poll: 300 }, "z-village"), exp);
  const B = new Session("two_devices B", await open(cb, { scenario: "two_devices", seed: 31, poll: 300 }, "z-village"), exp);
  await sleep(2500);
  const vm = "notes/zone/items/village.map";
  await A.click(vm, "note", "right"); await A.type(vm, "note", "A's note");
  await sleep(3500); await verifyScreen(B);
  await B.click("signoff/zone/items/village.map", "approve");
  await sleep(3500); await verifyScreen(A);
  const z = "i:" + tools[0].id;
  await A.go("k-tools"); await B.go("k-tools"); await sleep(1500);
  await A.click(z, "mark", "agree"); exp[markPath(tools[0].id)].mark = "agree";
  await sleep(300);
  await B.page.locator(B.sel(z, "mark", "disagree")).click(); exp[markPath(tools[0].id)].mark = "disagree";
  await sleep(3500);
  // B starts typing; A's note lands while B is still typing; B finishes later, so B's text is the newest.
  const nb = B.page.locator(`[data-k="${z}"][data-f="note"]`);
  await nb.click(); await B.page.keyboard.type("typed on ", { delay: 60 });
  await A.type(z, "note", "from A");
  await sleep(2500);
  if ((await nb.inputValue()) !== "typed on ") B.fail(`B's box was overwritten while typing: "${await nb.inputValue()}"`);
  await B.page.keyboard.type("B", { delay: 60 }); await B.page.locator("h1").first().click();
  exp[markPath(tools[0].id)].note = "typed on B";
  await settle(A.page, { min: 4000 }); await settle(B.page, { min: 1000 });
  for (const S of [A, B]) { await verifyWrites(S); await verifyStore(S, shared); await verifyAllScreens(S, ["k-tools", "z-village"]); }
  A.problems.push(...B.problems.map(p => "B: " + p));
  await ca.close(); await cb.close();
  return A;
};

// A note never changes an approval: approving, then many notes (one from a stale device) leave the approval as it was.
SC.note_vs_signoff = async ctx => {
  const vm = "notes/zone/items/village.map", vs = "signoff/zone/items/village.map";
  const cfg = { scenario: "note_vs_signoff", seed: 37, docs: [["signoff/zone/items/bee_meadow.map", { id: "bee_meadow.map", kind: "zone", level: "approved", ver: "old-version", at: 5 }]] };
  const S = new Session("note_vs_signoff", await open(ctx, cfg, "z-village"), {});
  await settle(S.page, { min: 3000 });
  await S.click(vs, "approve");
  await settle(S.page, { min: 2000 });
  for (let n = 0; n < 4; n++) { await S.type(vm, "note", ` part ${n}`); await S.click(vm, "note", pickOne(["right", "change", "question"])); await sleep(between(100, 700)); }
  await settle(S.page, { min: 2000 });
  // A device with a slow clock writes an older note over the stored one: the page must put its newer note back.
  await S.page.evaluate(p => __mock.remoteWrite(p, { id: "village.map", kind: "zone", mark: "question", note: "stale device", at: 5, page: "remote" }), vm);
  await settle(S.page, { min: 6000 });
  await verifyWrites(S); await verifyStore(S, null, { untouched: [[vs, 1]] }); await verifyScreen(S);
  await S.go("z-bee_meadow"); await sleep(500);
  if (!(await S.page.locator(".approve .stale").count())) S.fail("an approval of an older version doesn't say it changed");
  return S;
};

// A cut you agreed with is archived; marking it Disagree brings it back to the list. Decided cuts stay archived.
SC.archive_flip = async ctx => {
  const w = D.items.find(i => i.verdict === "cut" && !i.decided), v = D.items.find(i => i.verdict === "cut" && i.decided);
  const cfg = { scenario: "archive_flip", seed: 41, docs: [[markPath(w.id), { id: w.id, group: w.group, mark: "agree", note: "", at: 10, on: "" }]] };
  const S = new Session("archive_flip", await open(ctx, cfg, "archive"), {});
  await settle(S.page, { min: 4000 });
  // Lists are drawn when the page opens; leave and come back so the list reflects the stored marks.
  const has = async (route, id) => { await S.go("zones"); await S.go(route); await sleep(400); return (await S.page.locator(`#row-${id}`).count()) > 0; };
  if (!(await has("archive", w.id))) S.fail("a cut you agreed with isn't in the archive");
  if (!(await has("archive", v.id))) S.fail("a decided cut isn't in the archive");
  if (await has("items", w.id)) S.fail("a cut you agreed with is still in the list");
  await S.go("archive"); await sleep(400);
  await S.click("i:" + w.id, "mark", "disagree");
  await settle(S.page, { min: 2000 });
  if (!(await has("items", w.id))) S.fail("marking it Disagree didn't bring it back to the list");
  if (await has("archive", w.id)) S.fail("it is still in the archive after Disagree");
  await verifyWrites(S); await verifyStore(S);
  return S;
};

// ------------------------------------------------------------------ run
const want = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(SC);
const results = [];
for (const name of want) {
  if (!SC[name]) { console.log(`unknown scenario ${name}`); process.exit(2); }
  const t0 = Date.now(), ctx = await browser.newContext();
  let S;
  try { S = await SC[name](ctx); }
  catch (e) { S = { problems: [`crashed: ${String(e.stack || e).slice(0, 400)}`] }; }
  await ctx.close().catch(() => {});
  results.push({ scenario: name, seconds: Math.round((Date.now() - t0) / 1000), ok: !S.problems.length, problems: S.problems });
  console.log(`${S.problems.length ? "FAIL" : "ok  "} ${name} (${Math.round((Date.now() - t0) / 1000)} s)${S.problems.length ? "\n      " + S.problems.slice(0, 8).join("\n      ") : ""}`);
}
await browser.close();
writeFileSync(resolve(ROOT, "tools/gdd/_build/save_stress.json"), JSON.stringify(results, null, 2));
const bad = results.filter(r => !r.ok).length;
console.log(bad ? `${bad} of ${results.length} scenarios failed` : `all ${results.length} scenarios passed`);
process.exit(bad ? 1 : 0);
