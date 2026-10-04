// mock_db.js — a stand-in for the page's storage that misbehaves on purpose (docs/plans/review-app.md, Test plan).
// Built into tools/gdd/_build/review_app_test.html by `python3 tools/gdd/build_app.py --test-mock`; driven by
// tools/gdd/tests/save_stress.mjs. Made-up data only.
//
// What it does wrong, like the real thing can: a stale cached first view, late and out-of-order deliveries, old
// copies (sometimes even flagged as final), failed writes and reads, and other devices writing. It keeps every
// version of every document so the test can check that a stored answer is never replaced by an older one.
//
// Settings come from window.__MOCKCFG (set by the test before the page loads): {scenario, phase, seed, failRate,
// exhaustRate, readFailRate, staleEvery, lateSnapRate, latency, local, docs}. With window.__srv (a Playwright binding) the stored
// documents live in the test runner instead, so two browser contexts — two devices — share one store.
(function () {
  "use strict";
  const C = Object.assign({ scenario: "manual", phase: 1, seed: 7, failRate: 0, exhaustRate: 0, readFailRate: 0,
    staleEvery: 0, lateSnapRate: 0.5, latency: [20, 250], poll: 400 }, window.__MOCKCFG || {});
  let seed = C.seed;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const between = (a, b) => a + Math.floor(rnd() * (b - a + 1));
  const clone = o => (o === undefined ? undefined : JSON.parse(JSON.stringify(o)));
  const collOf = p => p.split("/").slice(0, -1).join("/");
  const idOf = p => p.split("/").pop();
  const err = code => ({ code, message: code });
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // ---------------------------------------------------------------- the store (in this page, or shared via __srv)
  const bridged = typeof window.__srv === "function";
  const server = new Map(), history = new Map();
  const KEY = "__mockserver";
  const saveLocal = () => { try { localStorage.setItem(KEY, JSON.stringify([...history])); } catch (e) {} };
  if (!bridged && C.phase > 1) {                       // a reload: the store outlives the page
    try { for (const [p, h] of JSON.parse(localStorage.getItem(KEY) || "[]")) { history.set(p, h); server.set(p, h[h.length - 1]); } } catch (e) {}
  }
  const srv = bridged ? {
    put: (p, b) => window.__srv("put", p, b),
    list: c => window.__srv("list", c).then(o => new Map(Object.entries(o))),
    hist: c => window.__srv("hist", c).then(o => new Map(Object.entries(o))),
    get: p => window.__srv("get", p),
  } : {
    put(p, b) { server.set(p, clone(b)); if (!history.has(p)) history.set(p, []); history.get(p).push(clone(b)); saveLocal(); return Promise.resolve(); },
    list(c) { const m = new Map(); for (const [p, b] of server) if (collOf(p) === c) m.set(p, clone(b)); return Promise.resolve(m); },
    hist(c) { const m = new Map(); for (const [p, h] of history) if (collOf(p) === c) m.set(p, clone(h)); return Promise.resolve(m); },
    get(p) { return Promise.resolve(clone(server.get(p))); },
  };

  const listeners = [];
  const M = window.__mock = { C, bridged, server, history, listeners, writes: [], failedWrites: 0, staleDeliveries: 0, reads: 0,
    rnd, between, pageErrors: [], srv, expect: {} };

  function makeSnap(bodies, fromCache) {                // bodies: Map path -> {body, pending}
    const docs = [...bodies.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1)).map(([p, v]) => {
      const frozen = Object.freeze(clone(v.body));
      return { id: idOf(p), exists: true, data: () => frozen, metadata: { fromCache, hasPendingWrites: !!v.pending } };
    });
    return { docs, size: docs.length, empty: !docs.length, docChanges: () => [],
      metadata: { fromCache, hasPendingWrites: docs.some(d => d.metadata.hasPendingWrites) } };
  }
  const wrap = m => { const o = new Map(); for (const [p, b] of m) o.set(p, { body: b }); return o; };
  const current = c => srv.list(c).then(wrap);
  async function stale(c) {                             // every doc at an older version, some missing entirely
    const h = await srv.hist(c), m = new Map();
    for (const [p, vs] of h) { if (rnd() < 0.2) continue; m.set(p, { body: vs[Math.max(0, Math.floor(rnd() * vs.length) - 1)] }); }
    return m;
  }
  function deliver(l, bodies, fromCache) {
    if (l.dead) return;
    try { l.next(makeSnap(bodies, fromCache)); } catch (e) { M.pageErrors.push(String((e && e.stack) || e)); }
  }
  async function broadcast(c, lateOk) {
    const snapNow = await current(c);
    for (const l of listeners) if (l.coll === c) {
      const late = lateOk && rnd() < C.lateSnapRate;   // a late copy can arrive after newer writes have landed
      setTimeout(async () => deliver(l, late ? snapNow : await current(c), false), late ? between(200, 2500) : between(0, 60));
    }
  }
  // Another device's write (single-page scenarios); in bridged runs the other device is a real second page.
  M.remoteWrite = async (path, body) => { await srv.put(path, body); broadcast(collOf(path), true); };
  M.seed = (path, body) => srv.put(path, body);         // stored before the page connects

  const DB = {
    doc(path) {
      if (path.split("/").length % 2) throw new TypeError("a document path needs an even number of segments: " + path);
      return {
        id: idOf(path), path,
        get() {
          M.reads++;
          return new Promise((res, rej) => setTimeout(async () => {
            if (rnd() < C.readFailRate) return rej(err("unavailable"));
            const b = await srv.get(path);
            res({ id: idOf(path), exists: b !== undefined && b !== null, data: () => clone(b),
              metadata: { fromCache: false, hasPendingWrites: false } });
          }, between(...C.latency)));
        },
        set(body) {
          if (body === null || typeof body !== "object") return Promise.reject(err("invalid_argument"));
          if (JSON.stringify(body).length > 256 * 1024) return Promise.reject(err("invalid_argument"));
          const c = collOf(path), pending = clone(body);
          M.writes.push({ path, at: body.at });
          current(c).then(m => {                        // this page sees its own write at once
            m.set(path, { body: pending, pending: true });
            for (const l of listeners) if (l.coll === c) deliver(l, m, false);
          });
          return new Promise((res, rej) => setTimeout(async () => {
            const r = rnd();
            if (r < C.failRate) { M.failedWrites++; return rej(err("unavailable")); }
            if (r < C.failRate + C.exhaustRate) { M.failedWrites++; return rej(err("resource_exhausted")); }
            await srv.put(path, pending); res(); broadcast(c, true);
          }, between(...C.latency)));
        },
        update() { return Promise.reject(err("invalid_argument")); },
        delete() { M.writes.push({ path, deleted: true }); return Promise.reject(err("not_granted")); },
        onSnapshot() { throw new Error("document listeners are not mocked"); },
      };
    },
    collection(coll) {
      if (coll.split("/").length % 2 === 0) throw new TypeError("a collection path needs an odd number of segments: " + coll);
      return {
        path: coll,
        get() { M.reads++; return new Promise(res => setTimeout(async () => res(makeSnap(await current(coll), false)), between(...C.latency))); },
        onSnapshot(next, error) {
          const l = { coll, next, error, dead: false, last: "" };
          listeners.push(l);
          setTimeout(async () => deliver(l, await stale(coll), true), 5);                      // a cached, out-of-date first view
          setTimeout(async () => deliver(l, await current(coll), false), between(300, 1500));  // then the real one
          if (bridged) (async function poll() {                                                // the other device's writes
            while (!l.dead) {
              await sleep(C.poll + between(0, 200));
              const m = await current(coll), sig = JSON.stringify([...m].map(([p, v]) => [p, v.body.at]));
              if (sig !== l.last) { l.last = sig; deliver(l, m, false); }
            }
          })();
          return () => { l.dead = true; };
        },
        doc(id) { return DB.doc(coll + "/" + id); },
      };
    },
  };
  if (C.staleEvery) setInterval(async () => {           // now and then a listener gets an old view, half the time flagged final
    if (!listeners.length) return;
    const l = listeners[Math.floor(rnd() * listeners.length)];
    M.staleDeliveries++; deliver(l, await stale(l.coll), rnd() < 0.5);
  }, C.staleEvery);
  addEventListener("error", e => M.pageErrors.push(String(e.message)));
  addEventListener("unhandledrejection", e => M.pageErrors.push("unhandled: " + String(e.reason && (e.reason.stack || e.reason.message) || e.reason)));

  // A scenario's starting state, on its first load only: this browser's saved copies (C.local, key -> value) and
  // stored documents (C.docs, [path, body] pairs). The page connects only once they are in place.
  M.ready = Promise.resolve();
  if (C.phase === 1) {
    for (const [k, v] of Object.entries(C.local || {})) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
    M.ready = Promise.all((C.docs || []).map(([p, b]) => srv.put(p, b)));
  }
  window.claude = { use: name => M.ready.then(() => sleep(50)).then(() => (name === "db" ? DB : null)) };
})();
