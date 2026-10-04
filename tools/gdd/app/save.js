// save.js — the review app's storage engine (docs/plans/review-app.md). Generalised from the items page's engine
// (tools/gdd/items_page.template.html), which survived its stress tests: one stored document per thing, newest `at`
// wins, at most three writes at once with backoff, the browser keeps its own copy until the storage confirms.
//
// A "thing" is anything the owner gives feedback on: an item row (marks/<group>/items/<id> — the items page's paths,
// browser key and applied rule, unchanged), a note (notes/<kind>/items/<id>) or an approval (signoff/<kind>/items/<id>).
// Approvals are separate documents so a note typed on a device that hasn't caught up can never withdraw one.
// Stored documents whose thing no longer exists are kept and listed as "older notes" — nothing the owner wrote vanishes.
window.BFStore = function BFStore(cfg) {
  "use strict";
  const things = new Map(cfg.things.map(t => [t.k, t]));           // k -> {k, shape, path, coll, id, group, ls, lid, decided, kind}
  const itemByRowId = new Map(cfg.things.filter(t => t.shape === "mark").map(t => [t.id, t]));
  const byPath = new Map(cfg.things.filter(t => t.shape !== "mark").map(t => [t.path, t]));
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    keys() { try { return Object.keys(localStorage); } catch (e) { return []; } },
  };
  const KI = "bf-items-v2", KA = "bf-app-v1";                       // items page key kept as is; new kinds separate
  const str = v => (typeof v === "string" ? v : "");
  const FIELDS = ["mark", "note", "choice", "other", "level", "ver", "on"];
  const clean = b => { const o = {}; for (const f of FIELDS) o[f] = str(b && b[f]); return o; };
  const filled = e => !!(e && (e.mark || e.choice || e.level || (e.note && e.note.trim()) || (e.other && e.other.trim())));

  // ------------------------------------------------------------ the browser's copy
  const local = {};
  const lsKeyOf = t => (t.ls === "items" ? KI : KA) + "-local";
  for (const [key, space] of [[KI, "items"], [KA, "app"]]) {
    for (const [lid, e] of Object.entries(ls.get(key + "-local", {}))) {
      const t = space === "items" ? itemByRowId.get(lid) : byPath.get(lid);
      if (t && e && typeof e.at === "number") local[t.k] = { ...clean(e), at: e.at, rec: !!e.rec };
    }
  }
  const stored = {};
  let clock = 0;
  for (const k in local) clock = Math.max(clock, local[k].at);
  const stamp = () => (clock = Math.max(Date.now(), clock + 1));
  const unsaved = k => !!local[k] && (stored[k] ?? -1) < local[k].at;
  function persist() {
    for (const space of ["items", "app"]) {
      const key = (space === "items" ? KI : KA) + "-local";
      const disk = ls.get(key, {});
      for (const k in local) {
        const t = things.get(k); if (!t || t.ls !== space) continue;
        if (!disk[t.lid] || !(disk[t.lid].at > local[k].at)) disk[t.lid] = local[k];
      }
      ls.set(key, disk);
    }
  }

  // ------------------------------------------------------------ the "applied" rule (item rows only, unchanged)
  const appliedOn = (t, e) => !!(t && t.shape === "mark" && t.decided && e && e.mark && str(e.on) !== t.decided);
  const live = k => (appliedOn(things.get(k), local[k]) ? "" : (local[k] || {}).mark || "");
  const wasText = k => appliedOn(things.get(k), local[k])
    ? `Your earlier ${local[k].mark === "agree" ? "Agree" : "Disagree"} is applied` : "";

  // ------------------------------------------------------------ editing
  const timers = {}, inflight = {}, again = {}, failing = {}, tries = {}, queue = [], settled = {};
  const FATAL = new Set(["invalid_argument", "quota_exceeded", "not_granted", "capability_disabled", "capability_removed", "revoked", "transform_error"]);
  const MAX_WRITES = 3;
  let db = null, blocked = "", recovered = 0, lastStored = null, active = 0;
  const orphans = new Map();                                        // "coll/id" -> {coll, id, body}

  function edit(k, patch, delay) {
    const t = things.get(k); if (!t) return;
    const cur = local[k] || {};
    const base = { ...clean(cur), mark: t.shape === "mark" ? live(k) : str(cur.mark) };
    local[k] = { ...base, ...patch, on: t.shape === "mark" ? (t.decided || "") : str(base.on), at: stamp(), rec: false };
    if (t.ver !== undefined && t.shape !== "mark") local[k].ver = t.ver;
    persist(); schedule(k, delay); cfg.onPaint(k); cfg.onStatus();
  }
  function schedule(k, delay) { clearTimeout(timers[k]); timers[k] = setTimeout(() => { timers[k] = 0; enqueue(k); }, delay); }
  function flush(k) { if (timers[k]) { clearTimeout(timers[k]); timers[k] = 0; enqueue(k); } }
  function enqueue(k) {
    if (!db || blocked || !unsaved(k)) { cfg.onStatus(); return; }
    if (inflight[k]) { again[k] = true; return; }
    if (!queue.includes(k)) queue.push(k);
    pump();
  }
  function pump() { while (active < MAX_WRITES && queue.length) { const k = queue.shift(); if (!inflight[k] && unsaved(k)) write(k); } }
  function body(k) {
    const t = things.get(k), e = local[k];
    if (t.shape === "mark") {
      const b = { id: t.id, group: t.group, mark: e.mark, note: e.note, at: e.at, on: e.on || "", page: cfg.version };
      if (e.rec) b.recovered = true;
      return b;
    }
    if (t.shape === "signoff") return { id: t.id, kind: t.kind, level: e.level, at: e.at, ver: e.ver || "", page: cfg.version };
    const b = { id: t.id, kind: t.kind, mark: e.mark, note: e.note, at: e.at, ver: e.ver || "", page: cfg.version };
    if (t.question) { b.choice = e.choice; b.other = e.other; }
    return b;
  }
  async function write(k) {
    inflight[k] = true; active++;
    const b = body(k);
    try {
      await db.doc(things.get(k).path).set(b);
      stored[k] = Math.max(stored[k] ?? -1, b.at);
      failing[k] = false; tries[k] = 0; lastStored = new Date();
    } catch (err) {
      const code = (err && err.code) || "unavailable";
      if (FATAL.has(code)) blocked = code;
      else {
        failing[k] = true; tries[k] = (tries[k] || 0) + 1;
        const wait = Math.min(60000, 1500 * 2 ** Math.min(tries[k] - 1, 6)) * (0.8 + Math.random() * 0.4);
        schedule(k, code === "resource_exhausted" ? Math.max(wait, 5000) : wait);
      }
    } finally {
      inflight[k] = false; active--;
      if (again[k]) { again[k] = false; if (!failing[k]) enqueue(k); }
      cfg.onPaint(k); cfg.onStatus(); pump();
    }
  }

  // ------------------------------------------------------------ reading
  const typing = k => { const a = document.activeElement; return !!(a && a.dataset && a.dataset.k === k && (a.tagName === "TEXTAREA" || a.tagName === "INPUT")); };
  function thingFor(coll, id) {
    if (coll.startsWith("marks/")) return itemByRowId.get(id);       // by id, whatever group it arrives from
    return byPath.get(coll + "/" + id);
  }
  function onSnap(coll, snap) {
    const touched = [];
    let orphansChanged = false;
    for (const d of snap.docs) {
      if (!d.exists) continue;
      const b = d.data(); if (!b || typeof b.at !== "number") continue;
      const t = thingFor(coll, d.id);
      if (!t) {
        if (filled(b)) { orphans.set(coll + "/" + d.id, { coll, id: d.id, body: b }); orphansChanged = true; }
        continue;
      }
      const k = t.k;
      if (b.at > clock) clock = b.at;
      if (!(d.metadata && d.metadata.hasPendingWrites)) stored[k] = Math.max(stored[k] ?? -1, b.at);
      const l = local[k];
      if (l && l.at >= b.at) continue;
      if (typing(k)) continue;
      local[k] = { ...clean(b), at: b.at, rec: false };
      touched.push(k);
    }
    if (touched.length) { persist(); touched.forEach(cfg.onPaint); }
    if (orphansChanged && cfg.onOrphans) cfg.onOrphans();
    if (!settled[coll] && !(snap.metadata && snap.metadata.fromCache)) { settled[coll] = true; settle(coll); }
    cfg.onStatus();
  }
  function subscribe(coll) {
    db.collection(coll).onSnapshot(snap => onSnap(coll, snap), err => {
      const code = (err && err.code) || "unavailable";
      if (FATAL.has(code)) { blocked = code; cfg.onStatus(); return; }
      setTimeout(() => subscribe(coll), code === "resource_exhausted" ? 15000 : 3000);
    });
  }
  async function readStored(k) {
    try {
      const s = await db.doc(things.get(k).path).get();
      if (!s.exists) return null;
      const b = s.data();
      if (!b || typeof b.at !== "number") return null;
      if (b.at > clock) clock = b.at;
      stored[k] = Math.max(stored[k] ?? -1, b.at);
      return b;
    } catch (e) { return undefined; }
  }

  // The marks the very first items page kept (old storage and this browser's dated keys) — brought over once.
  let legacy = {}, legacyReady = Promise.resolve();
  function loadLegacy() {
    for (const key of ls.keys()) {
      if (!/^bf-items-\d{4}-\d{2}-\d{2}-marks$/.test(key)) continue;
      const old = ls.get(key, {});
      for (const g in old) for (const id in (old[g] || {})) if (itemByRowId.has(id) && filled(old[g][id]) && !legacy[id]) legacy[id] = old[g][id];
    }
    legacyReady = db.collection("item_marks").get().then(snap => {
      for (const d of snap.docs) {
        const m = d.exists && d.data() && d.data().marks;
        if (m && typeof m === "object") for (const id in m) if (itemByRowId.has(id) && filled(m[id]) && !legacy[id]) legacy[id] = m[id];
      }
    }).catch(() => {});
  }
  async function settle(coll) {
    const inColl = [...things.values()].filter(t => t.shape === "mark" ? coll === `marks/${t.group}/items` : t.coll === coll);
    if (coll.startsWith("marks/")) {
      await legacyReady;
      const g = coll.split("/")[1];
      const imported = ls.get(KI + "-imported", []);
      if (!imported.includes(g)) {
        let complete = true;
        for (const [id, e] of Object.entries(legacy)) {
          const t = itemByRowId.get(id);
          if (!t || t.group !== g || local[t.k] || stored[t.k] !== undefined) continue;
          const b = await readStored(t.k);
          if (b === undefined) { complete = false; continue; }
          if (b || local[t.k]) continue;
          local[t.k] = { ...clean({ mark: e.mark, note: e.note }), at: stamp(), rec: true, on: "" };
          recovered++; persist(); cfg.onPaint(t.k); enqueue(t.k);
        }
        if (complete) ls.set(KI + "-imported", [...ls.get(KI + "-imported", []), g]);
      }
    }
    for (const t of inColl) await sendLeftover(t.k);
    cfg.onStatus();
  }
  async function sendLeftover(k) {
    if (!unsaved(k) || timers[k] || inflight[k]) return;
    const b = await readStored(k);
    if (b === undefined) { setTimeout(() => sendLeftover(k), 15000); return; }
    if (b && local[k] && b.at >= local[k].at) {
      if (!typing(k)) { local[k] = { ...clean(b), at: b.at, rec: false }; persist(); cfg.onPaint(k); }
      return;
    }
    enqueue(k);
  }

  function collections() {
    const c = cfg.storedGroups.map(g => `marks/${g}/items`);
    for (const kind of cfg.noteKinds) c.push(`notes/${kind}/items`);
    for (const kind of cfg.signoffKinds) c.push(`signoff/${kind}/items`);
    return c;
  }
  function connect() {
    const use = window.claude && typeof window.claude.use === "function" ? window.claude.use("db") : null;
    Promise.resolve(use).then(ns => {
      if (!ns) { blocked = "absent"; cfg.onStatus(); return; }
      db = ns; loadLegacy(); cfg.onStatus();
      const colls = collections();
      for (const c of colls) subscribe(c);
      setTimeout(() => { for (const c of colls) if (!settled[c]) { settled[c] = true; settle(c); } }, 10000);
    }).catch(() => { blocked = "absent"; cfg.onStatus(); });
  }
  const flushAll = () => { for (const k in timers) if (timers[k]) { clearTimeout(timers[k]); timers[k] = 0; enqueue(k); } };
  addEventListener("pagehide", flushAll);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flushAll(); });

  function state(k) {
    const e = local[k];
    if (!e || (!filled(e) && !unsaved(k))) return ["", ""];
    if (!unsaved(k)) return ["", "Stored"];
    return failing[k] || blocked ? ["bad", "Not stored yet"] : ["wait", "Saving…"];
  }
  function summary() {
    const ks = Object.keys(local);
    const marked = ks.filter(k => filled(local[k])).length;
    const waiting = ks.filter(unsaved).length;
    const stuck = ks.some(k => unsaved(k) && failing[k]);
    const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
    let dot, text;
    if (blocked === "absent") [dot, text] = ["bad", "Not connected to the page's storage — your answers stay in this browser. Open the page on claude.ai to store them."];
    else if (blocked) [dot, text] = ["bad", `The storage refused to save (${blocked}). Your answers are kept in this browser.`];
    else if (!db) [dot, text] = ["busy", "Connecting to the page's storage…"];
    else if (waiting && stuck) [dot, text] = ["bad", `${plural(waiting, "answer")} not stored yet — retrying.`];
    else if (waiting) [dot, text] = ["busy", `Saving ${plural(waiting, "answer")}…`];
    else if (!marked) [dot, text] = ["ok", "Connected — nothing answered yet"];
    else [dot, text] = ["ok", `All ${plural(marked, "answer")} stored` + (lastStored ? ` · last saved ${lastStored.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "")];
    if (recovered) text += ` · brought back ${recovered} from the first items page`;
    return { dot, text, waiting, marked, connected: !!db };
  }

  return {
    get: k => local[k] || {}, live, wasText, filled: k => filled(local[k]), edit, flush, state, summary, connect,
    orphans: () => [...orphans.values()], things, unsaved, _local: local,
  };
};
