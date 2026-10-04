// views.js — the review app's pages (docs/plans/review-app.md): Zones, Bugs, Items, Design, Status, Explain.
// Every bit of feedback is a "thing" in the store (save.js); the page never writes storage itself.
(() => {
  "use strict";
  const D = DATA;
  const $ = (s, r) => (r || document).querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
  };
  const KA = "bf-app-v1";
  const zoneById = new Map(D.zones.map(z => [z.id, z]));
  const bugById = new Map(D.bugs.map(b => [b.id, b]));
  const itemById = new Map(D.items.map(i => [i.id, i]));
  const secById = new Map(D.sections.map(s => [s.id, s]));
  const groupLabel = Object.fromEntries(D.groups);
  const short = b => b.name.replace(/\s*\(.*?\)/g, "").trim();
  const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
  const VLABEL = { cut: "Cut", change: "Change", add: "Add", later: "Later", keep: "Keep" };
  const WHERE = { game: "In the prototype", designed: "Designed only", both: "Both", new: "New", asked: "Yours, not in the game yet",
    art: "Art only, never spawned", artplan: "Art and a zone plan", plan: "A zone plan only", rows: "Only in my item rows" };
  const RINGL = { home: "Home ring", middle: "Middle ring", far: "Far ring", edge: "Edge ring" };

  // ------------------------------------------------------------ things (everything the owner can answer)
  const T = [];
  for (const it of D.items) T.push({ k: "i:" + it.id, shape: "mark", id: it.id, group: it.group, path: `marks/${it.group}/items/${it.id}`,
    coll: `marks/${it.group}/items`, ls: "items", lid: it.id, decided: it.decided || "" });
  const P = (shape, kind, id, ver, extra) => {
    const path = `${shape === "signoff" ? "signoff" : "notes"}/${kind}/items/${id}`;
    return Object.assign({ k: path, shape, kind, id, path, coll: path.slice(0, path.lastIndexOf("/")), ls: "app", lid: path, ver: ver || "" }, extra || {});
  };
  const noteK = (kind, id) => `notes/${kind}/items/${id}`, signK = (kind, id) => `signoff/${kind}/items/${id}`;
  for (const z of D.zones) {
    T.push(P("note", "zone", z.id + ".map", z.ver_map), P("signoff", "zone", z.id + ".map", z.ver_map));
    T.push(P("note", "zone", z.id + ".plan", z.ver_plan), P("signoff", "zone", z.id + ".plan", z.ver_plan));
  }
  for (const b of D.bugs) T.push(P("note", "bug", b.id, b.ver), P("signoff", "bug", b.id, b.ver));
  // A §03 bug sheet's feedback is the bug's own note, so it is the same answer in the Design and Bugs views.
  const propK = p => (p.key || "").startsWith("bug.") ? noteK("bug", p.key.slice(4)) : noteK("gdd", p.key);
  for (const s of D.sections) {
    T.push(P("note", "section", s.id, s.ver), P("signoff", "section", s.id, s.ver));
    for (const p of s.proposals) if (!(p.key || "").startsWith("bug.")) T.push(P("note", "gdd", p.key, ""));
    for (const q of s.questions) T.push(P("note", "gdd", q.key, "", { question: true }));
  }

  const S = window.BFStore({ things: T, version: D.version, storedGroups: D.stored_groups, noteKinds: D.note_kinds,
    signoffKinds: D.signoff_kinds, onPaint: paint, onStatus: status, onOrphans: () => { if (route().view === "status") render(); } });

  // ------------------------------------------------------------ "changed since you last looked"
  let seen = ls.get(KA + "-seen", null);
  const allVers = () => {
    const v = {};
    for (const z of D.zones) v["z:" + z.id] = z.ver_map + z.ver_plan;
    for (const b of D.bugs) v["b:" + b.id] = b.ver;
    for (const s of D.sections) v["s:" + s.id] = s.ver;
    return v;
  };
  if (!seen) { seen = allVers(); ls.set(KA + "-seen", seen); }      // first visit: nothing is "changed"
  const changed = (key, v) => seen[key] !== undefined && seen[key] !== v || seen[key] === undefined;
  const markSeen = keys => { const v = allVers(); for (const k of keys) seen[k] = v[k]; ls.set(KA + "-seen", seen); render(); };
  const dot = (key, v) => changed(key, v) ? `<span class="new" title="Changed since you last looked">changed</span>` : "";

  // ------------------------------------------------------------ widgets
  function stateHtml(k) { const [c, t] = S.state(k); return `<span class="state${c ? " " + c : ""}" data-state="${esc(k)}" aria-live="polite">${esc(t)}</span>`; }
  function markWidget(k, label) {                                   // an item row: Agree / Disagree + note (unchanged)
    const lm = S.live(k), e = S.get(k);
    return `<div class="fb" data-k="${esc(k)}"><div class="btns">
      <button type="button" class="yes" data-act="mark" data-k="${esc(k)}" data-v="agree" aria-pressed="${lm === "agree"}">Agree</button>
      <button type="button" class="no" data-act="mark" data-k="${esc(k)}" data-v="disagree" aria-pressed="${lm === "disagree"}">Disagree</button>
      ${stateHtml(k)}<span class="was" data-was="${esc(k)}">${esc(S.wasText(k))}</span></div>
      <textarea class="note" data-k="${esc(k)}" data-f="note" rows="1" placeholder="Note" aria-label="Your note on ${esc(label)}">${esc(e.note || "")}</textarea></div>`;
  }
  function noteWidget(k, choices, prompt, label) {                  // a note: a few answer buttons + a note
    const e = S.get(k);
    return `<div class="fb" data-k="${esc(k)}">${prompt ? `<div class="prompt">${esc(prompt)}</div>` : ""}<div class="btns">
      ${choices.map(([v, l, c]) => `<button type="button" class="${c || ""}" data-act="note" data-k="${esc(k)}" data-v="${v}" aria-pressed="${e.mark === v}">${esc(l)}</button>`).join("")}
      ${stateHtml(k)}</div>
      <textarea class="note" data-k="${esc(k)}" data-f="note" rows="1" placeholder="Note (optional)" aria-label="${esc(label || "Your note")}">${esc(e.note || "")}</textarea></div>`;
  }
  const YES_CHANGE_NO = [["yes", "Yes", "yes"], ["change", "Change", "chg"], ["no", "No", "no"]];
  const RIGHT_CHANGE_ASK = [["right", "Looks right", "yes"], ["change", "Change it", "chg"], ["question", "I have a question", "ask"]];
  function questionWidget(k, q) {
    const e = S.get(k);
    return `<div class="fb q" data-k="${esc(k)}"><div class="opts">
      ${q.options.map(o => `<button type="button" class="opt" data-act="choice" data-k="${esc(k)}" data-v="${o.key}" aria-pressed="${e.choice === o.key}">
        <span class="okey">${esc(o.key)}</span><span class="otxt">${o.html}${q.rec && q.rec.key === o.key ? '<span class="pick">My pick</span>' : ""}</span></button>`).join("")}
      <button type="button" class="opt" data-act="choice" data-k="${esc(k)}" data-v="other" aria-pressed="${e.choice === "other"}"><span class="okey">…</span><span class="otxt">Something else</span></button></div>
      <input type="text" class="other" data-k="${esc(k)}" data-f="other" value="${esc(e.other || "")}" placeholder="Your own answer" aria-label="Your own answer">
      <div class="btns">${stateHtml(k)}</div>
      <textarea class="note" data-k="${esc(k)}" data-f="note" rows="1" placeholder="Note (optional)" aria-label="Your note">${esc(e.note || "")}</textarea></div>`;
  }
  function approveWidget(k, label) {
    const e = S.get(k), t = S.things.get(k);
    const on = e.level === "approved", stale = on && e.ver && t && t.ver && e.ver !== t.ver;
    return `<div class="approve" data-k="${esc(k)}"><button type="button" class="appr" data-act="approve" data-k="${esc(k)}" data-label="${esc(label)}" aria-pressed="${on}">${on ? "✓ Approved" : esc(label)}</button>
      ${stale ? `<span class="stale">Changed since you approved it — look again</span>` : ""}${stateHtml(k)}</div>`;
  }
  function approvalState(k) {
    const e = S.get(k), t = S.things.get(k);
    if (e.level !== "approved") return "";
    return e.ver && t && t.ver && e.ver !== t.ver ? "stale" : "ok";
  }

  // repaint every widget bound to one thing
  function paint(k) {
    const e = S.get(k), t = S.things.get(k);
    for (const b of document.querySelectorAll(`[data-k="${CSS.escape(k)}"][data-act]`)) {
      const a = b.dataset.act;
      if (a === "mark") b.setAttribute("aria-pressed", String(S.live(k) === b.dataset.v));
      else if (a === "note") b.setAttribute("aria-pressed", String(e.mark === b.dataset.v));
      else if (a === "choice") b.setAttribute("aria-pressed", String(e.choice === b.dataset.v));
      else if (a === "approve") {
        const on = e.level === "approved"; b.setAttribute("aria-pressed", String(on));
        b.textContent = on ? "✓ Approved" : (b.dataset.label || b.textContent.replace("✓ Approved", "Approve"));
      }
    }
    for (const f of document.querySelectorAll(`[data-k="${CSS.escape(k)}"][data-f]`)) {
      if (document.activeElement === f) continue;
      const v = e[f.dataset.f] || "";
      if (f.value !== v) { f.value = v; if (f.tagName === "TEXTAREA") fit(f); }
    }
    for (const s of document.querySelectorAll(`[data-state="${CSS.escape(k)}"]`)) { const [c, tx] = S.state(k); s.className = "state" + (c ? " " + c : ""); s.textContent = tx; }
    for (const w of document.querySelectorAll(`[data-was="${CSS.escape(k)}"]`)) w.textContent = S.wasText(k);
    if (t && t.shape === "mark") for (const r of document.querySelectorAll(`[data-row="${CSS.escape(t.id)}"]`)) r.classList.toggle("marked", S.filled(k));
  }
  function fit(t) { t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight + 2, 320) + "px"; }

  // ------------------------------------------------------------ events (one set for the whole page)
  const main = $("#main");
  main.addEventListener("click", e => {
    const b = e.target.closest("[data-act]");
    if (b) {
      const k = b.dataset.k, a = b.dataset.act, cur = S.get(k);
      if (a === "mark") S.edit(k, { mark: S.live(k) === b.dataset.v ? "" : b.dataset.v }, 200);
      else if (a === "note") S.edit(k, { mark: cur.mark === b.dataset.v ? "" : b.dataset.v }, 200);
      else if (a === "choice") S.edit(k, { choice: cur.choice === b.dataset.v ? "" : b.dataset.v }, 200);
      else if (a === "approve") { b.dataset.label = b.dataset.label || b.textContent; S.edit(k, { level: cur.level === "approved" ? "" : "approved" }, 0); }
      else if (a === "seen") markSeen(JSON.parse(b.dataset.keys));
      paint(k);
      return;
    }
  });
  main.addEventListener("input", e => {
    const f = e.target.closest("[data-f]"); if (!f) return;
    S.edit(f.dataset.k, { [f.dataset.f]: f.value }, 800);
    if (f.tagName === "TEXTAREA") fit(f);
  });
  main.addEventListener("focusout", e => { const f = e.target.closest && e.target.closest("[data-f]"); if (f) S.flush(f.dataset.k); });

  function status() {
    const s = S.summary();
    $("#status").innerHTML = `<span class="dot ${s.dot}"></span><span>${esc(s.text)}</span>`;
  }

  // ------------------------------------------------------------ routing (bare #anchors only)
  function route() {
    const h = decodeURIComponent(location.hash.slice(1));
    const m = h.match(/^(zh|z|b|k|i|s|p|e)-(.+)$/);
    if (!h || h === "zones") return { view: "zones" };
    if (["bugs", "items", "archive", "design", "status", "explain"].includes(h)) return { view: h };
    if (!m) return { view: "zones" };
    const [, t, rest] = m;
    if (t === "zh") { const i = rest.indexOf("."); return { view: "zone", id: rest.slice(0, i), hl: rest.slice(i + 1) }; }
    return { view: { z: "zone", b: "bug", k: "items", i: "items", s: "section", p: "section", e: "explain" }[t], id: rest, t };
  }
  const TABS = [["zones", "Zones"], ["bugs", "Bugs"], ["items", "Items"], ["design", "Design"], ["status", "Status"], ["explain", "Explain"]];
  const tabOf = v => ({ zone: "zones", bug: "bugs", archive: "items", section: "design" }[v] || v);
  function render() {
    const r = route();
    $("#tabs").innerHTML = TABS.map(([k, l]) => `<a href="#${k}" aria-current="${tabOf(r.view) === k ? "page" : "false"}">${l}</a>`).join("");
    const V = { zones: zonesView, zone: zoneView, bugs: bugsView, bug: bugView, items: itemsView, archive: itemsView,
      design: designView, section: sectionView, status: statusView, explain: explainView }[r.view] || zonesView;
    main.innerHTML = V(r);
    for (const t of main.querySelectorAll("textarea.note")) if (t.value) fit(t);
    if (r.view === "zone") afterZone(r);
    if (r.t === "i" || r.t === "p") { const el = document.getElementById((r.t === "i" ? "row-" : "card-") + r.id); if (el) { el.scrollIntoView({ block: "center" }); el.classList.add("flash"); } }
    else window.scrollTo(0, 0);
    status();
  }
  addEventListener("hashchange", render);

  // ------------------------------------------------------------ Zones
  function zoneCounts(z) { return `${plural(z.spawn.length, "bug")} breed here${z.comes.length ? ` · ${z.comes.length} come in` : ""}`; }
  function zonesView() {
    const rows = [0, 1, 2, 3, 4];
    const layer = ["Surface, far north", "Surface", "Surface, south (home)", "Underground", "Deep underground"];
    let h = `<h1>Zones</h1><p class="lede">The 20 zones, north at the top. Each one's map, what it's for, and every bug that lives
      there — bugs live in many zones. Open one to answer it: first <b>is the map right?</b>, then <b>are the bugs and the
      description right?</b> Where bugs live is my reading of the bestiary and the ecology section; every link says
      <i>proposed</i> until you approve its zone.</p>
      <p><button type="button" class="ghost" data-act="seen" data-k="" data-keys='${esc(JSON.stringify(D.zones.map(z => "z:" + z.id)))}'>Mark every zone as seen</button></p>
      <div class="world" role="list">`;
    for (const r of rows) {
      h += `<div class="layer" aria-hidden="true">${layer[r]}</div>`;
      for (let c = 0; c < 4; c++) {
        const z = D.zones.find(q => q.row === r && q.col === c);
        if (!z) { h += `<div></div>`; continue; }
        const am = approvalState(signK("zone", z.id + ".map")), ap = approvalState(signK("zone", z.id + ".plan"));
        h += `<a role="listitem" class="zcard ring-${z.ring}" href="#z-${z.id}">
          <span class="zname">${esc(z.name)}${dot("z:" + z.id, z.ver_map + z.ver_plan)}</span>
          <span class="zmeta">${esc(RINGL[z.ring])} · ${esc(z.danger)}${z.built ? ` · <b>built</b>` : ""}</span>
          <span class="zmeta">${zoneCounts(z)}</span>
          <span class="zappr"><span class="ap ${am}">map ${am === "ok" ? "✓" : am === "stale" ? "changed" : "—"}</span><span class="ap ${ap}">details ${ap === "ok" ? "✓" : ap === "stale" ? "changed" : "—"}</span></span></a>`;
      }
    }
    return h + `</div>`;
  }
  function bugLink(id) { const b = bugById.get(id); return b ? `<a href="#b-${b.id}">${esc(short(b))}</a>` : esc(id); }
  function zoneLink(id) { const z = zoneById.get(id); return z ? `<a href="#z-${z.id}">${esc(z.name)}</a>` : esc(id); }
  function zoneView(r) {
    const z = zoneById.get(r.id);
    if (!z) return `<p class="empty">No zone ${esc(r.id)}.</p>`;
    const nb = z.neighbours || {};
    const m = D.maps[z.id];
    let h = `<p class="crumb"><a href="#zones">Zones</a> ›</p><h1>${esc(z.name)}</h1>
      <p class="meta">${esc(RINGL[z.ring])} · ${esc(z.danger)} · ${esc(z.layer)} · grid row ${z.row}, column ${z.col}${z.built ? ` · built as <code>${esc(z.built)}</code>` : " · not built yet"}</p>
      <p class="purpose">${esc(z.purpose)}</p>
      <section class="part"><h2>The map</h2>
      <div class="mapbox"><div class="mapwrap"><canvas id="map" aria-label="Map of ${esc(z.name)}, north at the top"></canvas><svg id="mapsvg" class="mapsvg" aria-hidden="true"></svg></div>
      <p class="hover" id="hover">${m ? "Point at the map to see what's there." : "This zone has no layout yet: it comes from the zone-design process, and this map will show it."}</p>
      ${r.hl ? `<p class="hl">Showing where <b>${esc((itemById.get(r.hl) || {}).name || r.hl)}</b> is placed. <a href="#z-${z.id}">Show everything</a></p>` : ""}
      <p class="legend">North is at the top. ${m ? "Circles are where bugs breed (their names above them). Colours: ground as in the game; objects by kind." : ""}</p></div>
      ${noteWidget(noteK("zone", z.id + ".map"), RIGHT_CHANGE_ASK, "Is the map right?", "Your note on the map")}
      ${approveWidget(signK("zone", z.id + ".map"), "Approve this map")}</section>`;
    h += `<section class="part"><h2>Neighbours</h2><p>${["north", "east", "south", "west"].map(d => nb[d] ? `${d}: ${zoneLink(nb[d])}` : `${d}: the edge of the world`).join(" · ")}</p></section>`;
    h += `<section class="part"><h2>Bugs that breed here</h2>${z.spawn.length ? `<ul class="buglist">${z.spawn.map(s =>
      `<li>${bugLink(s.id)}${s.note ? ` <span class="sub">— ${esc(s.note)}</span>` : ""}${s.proposed ? ` <span class="prop">proposed</span>` : ""}</li>`).join("")}</ul>` : `<p class="empty">None listed.</p>`}
      <h2>Bugs that come in from next door</h2>${z.comes.length ? `<ul class="buglist">${z.comes.map(s =>
      `<li>${bugLink(s.id)} <span class="sub">from ${s.from.map(zoneLink).join(" and ")}${s.note ? ` — ${esc(s.note)}` : ""}</span>${s.proposed ? ` <span class="prop">proposed</span>` : ""}</li>`).join("")}</ul>` : `<p class="empty">None listed.</p>`}`;
    if (z.diffs.length) h += `<div class="diffs"><h3>Where the documents disagree</h3><p class="sub">This app's list against the ecology section (§04)${z.built ? " and the game as built" : ""}. I'll propose an answer for each; yours decides.</p>
      <table class="dtab"><thead><tr><th>Bug</th><th>This app</th><th>§04</th>${z.built ? "<th>Built game</th>" : ""}</tr></thead><tbody>${z.diffs.map(d =>
      `<tr><td>${bugLink(d.bug)}</td><td>${{ spawns: "breeds here", comes_in: "comes in", absent: "not listed" }[d.registry]}</td><td>${d.s04 ? "mentions it" : "doesn't mention it"}</td>${z.built ? `<td>${d.built === "spawns" ? "spawns it" : "doesn't"}</td>` : ""}</tr>`).join("")}</tbody></table></div>`;
    h += `${noteWidget(noteK("zone", z.id + ".plan"), RIGHT_CHANGE_ASK, "Are the bugs and the description right?", "Your note on the zone's bugs")}
      ${approveWidget(signK("zone", z.id + ".plan"), "Approve the details")}</section>`;
    if (z.placed.length) {
      const byCat = {};
      for (const p of z.placed) (byCat[p.cat] = byCat[p.cat] || []).push(p);
      h += `<section class="part"><h2>Items placed here <span class="aside">in the built zone</span></h2>${Object.entries(byCat).map(([c, ps]) =>
        `<details class="cat"><summary>${esc(c)} <span class="sub">${ps.length} kinds · ${ps.reduce((a, p) => a + p.n, 0)} placed</span></summary><ul class="placed">${ps.map(p => {
          const it = itemById.get(p.id) || {};
          const flag = it.verdict === "cut" && !it.decided ? ` <span class="flag" title="I recommended cutting it; not decided yet">cut? still in the game</span>` : "";
          return `<li><a href="#zh-${z.id}.${esc(p.id)}">${esc(it.name || p.id)}</a> ×${p.n}${flag} <a class="sub" href="#i-${esc(p.id)}">its row</a></li>`;
        }).join("")}</ul></details>`).join("")}</section>`;
    }
    if ((z.sheets || []).length) h += `<section class="part"><details class="ref"><summary>Older working sheets <span class="sub">for reference; replaced by this page as zones are designed</span></summary><ul>${z.sheets.map(s => `<li><code>${esc(s)}</code></li>`).join("")}</ul></details></section>`;
    return h;
  }
  function afterZone(r) {
    const z = zoneById.get(r.id); if (!z) return;
    const m = D.maps[z.id], cv = $("#map"), svg = $("#mapsvg");
    const names = {}; for (const d of ["north", "south", "east", "west"]) { const n = (z.neighbours || {})[d]; if (n) names[d] = zoneById.get(n).name; }
    if (m) {
      const ok = window.BFMaps.draw(cv, m, { cats: D.colors.category, highlight: r.hl || null });
      if (!ok) { $("#hover").textContent = "Map orientation check failed — the map isn't drawn. (A bug in the builder; tell me.)"; cv.hidden = true; return; }
      window.BFMaps.overlay(svg, m, { edges: names });
      cv.addEventListener("mousemove", ev => {
        const c = window.BFMaps.cellAt(m, cv, ev); if (!c) return;
        const it = c.thing && itemById.get(c.thing);
        const breed = [...new Set(window.BFMaps.areasAt(m, c.x, c.y))];
        $("#hover").textContent = `(${c.x}, ${c.y}) · ${c.ground.replace(/_/g, " ")}${c.thing ? " · " + (it ? it.name : c.thing) : ""}` +
          (breed.length ? ` · breeding area: ${breed.join(", ")}` : "");
      });
    } else { cv.hidden = true; window.BFMaps.overlay(svg, null, { edges: names, empty: "Layout not drawn yet" }); svg.classList.add("blank"); }
  }

  // ------------------------------------------------------------ Bugs
  function bugsView() {
    let h = `<h1>Bugs</h1><p class="lede">The ${D.bugs.length} bugs on the roster, by family. Each one's page has its bestiary sheet, where it
      lives, whether it's in the game, and your answers.</p>
      <p><button type="button" class="ghost" data-act="seen" data-k="" data-keys='${esc(JSON.stringify(D.bugs.map(b => "b:" + b.id)))}'>Mark every bug as seen</button></p>`;
    for (const fam of D.families) {
      const bs = D.bugs.filter(b => b.family === fam); if (!bs.length) continue;
      h += `<section class="fam"><h2>${esc(fam[0].toUpperCase() + fam.slice(1))}</h2><div class="cards3">${bs.map(b => {
        const a = approvalState(signK("bug", b.id));
        const sp = b.zones.filter(e => e.how === "spawns").map(e => zoneById.get(e.zone).name);
        return `<a class="bcard" href="#b-${b.id}"><span class="bname">${esc(short(b))}${dot("b:" + b.id, b.ver)}</span>
          <span class="sub"><i>${esc(b.latin)}</i>${b.species.length ? " · in the game" : ""}</span>
          <span class="sub">${esc(sp.join(", ") || "no zone yet")}</span><span class="ap ${a}">${a === "ok" ? "✓ approved" : a === "stale" ? "changed since approved" : ""}</span></a>`;
      }).join("")}</div></section>`;
    }
    return h;
  }
  function itemRowHtml(it) {
    const k = "i:" + it.id;
    return `<div class="irow${S.filled(k) ? " marked" : ""}" id="row-${esc(it.id)}" data-row="${esc(it.id)}">
      <div class="ihead"><span class="name">${esc(it.name)}</span> <span class="v ${esc(it.verdict)}">${esc(VLABEL[it.verdict] || it.verdict)}</span>
      ${it.decided ? `<span class="dec" title="Settled with your notes on ${esc(it.decided)}">Decided</span>` : ""}<span class="id">${esc(it.id)} · ${esc(groupLabel[it.group] || it.group)} · ${esc(WHERE[it.where] || it.where)}</span></div>
      ${it.change ? `<p class="what">${esc(it.change)}</p>` : ""}<p class="why">${esc(it.reason)}</p>
      ${it.placed ? `<p class="placedin">Placed: ${Object.entries(it.placed).map(([zz, n]) => `<a href="#zh-${zz}.${esc(it.id)}">${esc(zoneById.get(zz).name)} ×${n}</a>`).join(" · ")}</p>` : ""}
      ${markWidget(k, it.name)}</div>`;
  }
  function bugView(r) {
    const b = bugById.get(r.id);
    if (!b) return `<p class="empty">No bug ${esc(r.id)}.</p>`;
    const lu = itemById.get(b.lineup);
    let h = `<p class="crumb"><a href="#bugs">Bugs</a> › ${esc(b.family)}</p><h1>${esc(short(b))}</h1>
      <p class="meta"><i>${esc(b.latin)}</i> · ${b.species.length ? `in the game as <code>${b.species.map(esc).join("</code>, <code>")}</code>` : "not in the game yet"}</p>`;
    h += `<section class="part"><h2>Where it lives</h2><ul class="buglist">${b.zones.map(e => `<li>${zoneLink(e.zone)} — ${e.how === "spawns" ? "breeds here" : `comes in from ${e.from.map(zoneLink).join(" and ")}`}${e.note ? ` <span class="sub">(${esc(e.note)})</span>` : ""}${e.proposed ? ` <span class="prop">proposed</span>` : ""}</li>`).join("")}</ul>
      ${b.diffs.length ? `<p class="sub">The documents disagree about ${plural(b.diffs.length, "zone")} — see each zone's page.</p>` : ""}</section>`;
    h += `<section class="part"><h2>Its design <span class="aside">the bestiary sheet (§03 ${esc(b.sheet.p || "")}) — natural history for now; the game-first sheet replaces it</span></h2>
      <article class="card"><div class="card-head"><h3>${b.sheet.title}</h3></div><div class="prose">${b.sheet.html}</div>
      ${b.sheet.lenses ? `<div class="lenses"><b>Checked against</b> ${b.sheet.lenses}</div>` : ""}
      ${noteWidget(noteK("bug", b.id), YES_CHANGE_NO, "Is this the right design for it?", "Your note on " + short(b))}
      ${approveWidget(signK("bug", b.id), "Approve its design")}</article></section>`;
    if (lu) h += `<section class="part"><h2>Is it in the game? <span class="aside">its row in the roster — the same mark as on the Items page</span></h2>${itemRowHtml(lu)}</section>`;
    const rows = b.bug_table.map(id => itemById.get(id)).filter(Boolean);
    if (rows.length) h += `<section class="part"><details class="ref"><summary>Its older bug-list rows <span class="sub">${rows.length}</span></summary>${rows.map(itemRowHtml).join("")}</details></section>`;
    return h;
  }

  // ------------------------------------------------------------ Items
  const f = Object.assign({ verdict: "", show: "", where: "", group: "", q: "", placed: "" }, ls.get(KA + "-items-filter", {}));
  const archived = it => it.verdict === "cut" && (!!it.decided || S.live("i:" + it.id) === "agree");
  function itemsView(r) {
    const arch = r.view === "archive";
    if (r.t === "k") f.group = r.id;
    if (r.t === "i") { const it = itemById.get(r.id); if (it) { f.group = it.group; f.verdict = ""; f.show = ""; f.q = ""; f.where = ""; f.placed = ""; } }
    const counts = {}; let marked = 0;
    for (const it of D.items) { counts[it.verdict] = (counts[it.verdict] || 0) + 1; if (S.filled("i:" + it.id)) marked++; }
    const nArch = D.items.filter(archived).length;
    const match = it => {
      if (arch !== archived(it) && !(r.t === "i" && it.id === r.id)) return false;
      if (f.verdict && it.verdict !== f.verdict) return false;
      if (f.where && it.where !== f.where) return false;
      if (f.group && it.group !== f.group) return false;
      if (f.placed && !it.placed) return false;
      if (f.show === "todo" && S.filled("i:" + it.id)) return false;
      if (f.show === "done" && !S.filled("i:" + it.id)) return false;
      if (f.show === "notes" && !(S.get("i:" + it.id).note || "").trim()) return false;
      if (f.q && !`${it.name} ${it.id} ${it.change || ""} ${it.reason}`.toLowerCase().includes(f.q.toLowerCase())) return false;
      return true;
    };
    let h = `<h1>${arch ? "The archive" : "Items"}</h1><p class="lede">${arch
      ? `Rows that are settled cuts — decided, or cuts you agreed with. They're kept here, out of the way, with your marks; nothing is deleted. Marking one differently brings it back to the list.`
      : `Every item in the game and in the old designs, with my call and why. Mark each Agree or Disagree, with a note where you'd do it differently. Settled cuts are in the <a href="#archive">archive</a> (${nArch}). Rows marked <b>Decided</b> are settled; a mark you gave before is shown as applied.`}</p>
      <div class="bar"><div class="tallies"><span class="tally"><b>${D.items.length}</b> rows</span>${Object.entries(VLABEL).map(([k, l]) => `<span class="tally"><span class="v ${k}">${l}</span> <b>${counts[k] || 0}</b></span>`).join("")}<span class="tally">· you've marked <b>${marked}</b></span></div>
      <div class="controls" role="toolbar" aria-label="Filters">
        <select data-flt="verdict" aria-label="My call"><option value="">Every call</option>${Object.entries(VLABEL).map(([k, l]) => `<option value="${k}"${f.verdict === k ? " selected" : ""}>${l}</option>`).join("")}</select>
        <select data-flt="show" aria-label="Your marks"><option value="">Marked and not</option><option value="todo"${f.show === "todo" ? " selected" : ""}>Not marked yet</option><option value="done"${f.show === "done" ? " selected" : ""}>Marked</option><option value="notes"${f.show === "notes" ? " selected" : ""}>With a note</option></select>
        <select data-flt="group" aria-label="Kind"><option value="">Every kind</option>${D.groups.map(([k, l]) => `<option value="${k}"${f.group === k ? " selected" : ""}>${esc(l)}</option>`).join("")}</select>
        <select data-flt="where" aria-label="Where it comes from"><option value="">Everywhere</option>${Object.entries(WHERE).map(([k, l]) => `<option value="${k}"${f.where === k ? " selected" : ""}>${esc(l)}</option>`).join("")}</select>
        <select data-flt="placed" aria-label="Placed in a built zone"><option value="">Placed or not</option><option value="1"${f.placed ? " selected" : ""}>Placed in a built zone</option></select>
        <input type="search" data-flt="q" value="${esc(f.q)}" placeholder="Search names, ids and reasons" aria-label="Search"></div></div>`;
    let any = false;
    for (const [g, label] of D.groups) {
      const rows = D.items.filter(it => it.group === g && match(it));
      if (!rows.length) continue;
      any = true;
      h += `<details class="group" open><summary><h2>${esc(label)}</h2><span class="sub">${rows.length} shown</span></summary>${rows.map(itemRowHtml).join("")}</details>`;
    }
    return h + (any ? "" : `<p class="empty">Nothing matches these filters.</p>`);
  }
  main.addEventListener("change", e => {
    const s = e.target.closest("[data-flt]"); if (!s || s.tagName === "INPUT") return;
    f[s.dataset.flt] = s.value; ls.set(KA + "-items-filter", f);
    if (location.hash.startsWith("#k-") || location.hash.startsWith("#i-")) location.hash = "items"; else render();
  });
  let qt; main.addEventListener("input", e => {
    const s = e.target.closest("input[data-flt]"); if (!s) return;
    clearTimeout(qt); qt = setTimeout(() => { f.q = s.value; ls.set(KA + "-items-filter", f); render(); const i = $("input[data-flt=q]"); if (i) { i.focus(); i.setSelectionRange(i.value.length, i.value.length); } }, 250);
  });

  // ------------------------------------------------------------ Design (the GDD sections)
  const SSTAT = { final: "Settled", review: "Ready for your answers", rework: "Being redone", draft: "Not written yet" };
  function answered(s) {
    let n = 0, t = 0;
    for (const p of s.proposals) { t++; if (S.filled(propK(p))) n++; }
    for (const q of s.questions) { t++; if (S.filled(noteK("gdd", q.key))) n++; }
    return [n, t];
  }
  function designView() {
    let h = `<h1>The design document</h1><p class="lede">The game's design, one section at a time. Answer the proposals (yes, change,
      no) and the questions that are yours; approve a section when it's right.</p>
      <p><button type="button" class="ghost" data-act="seen" data-k="" data-keys='${esc(JSON.stringify(D.sections.map(s => "s:" + s.id)))}'>Mark every section as seen</button></p><ol class="secs">`;
    for (const s of D.sections) {
      const [n, t] = answered(s), a = approvalState(signK("section", s.id));
      h += `<li><a href="#s-${s.id}"><span class="sid">${s.id === "OV" ? "★" : "§" + esc(s.id)}</span><span class="stitle">${esc(s.title)}${dot("s:" + s.id, s.ver)}</span>
        <span class="chip ${esc(s.status)}">${esc(SSTAT[s.status] || s.status)}</span>${t ? `<span class="sub">${n} of ${t} answered</span>` : ""}${a ? `<span class="ap ${a}">${a === "ok" ? "✓ approved" : "changed since approved"}</span>` : ""}</a></li>`;
    }
    return h + `</ol>`;
  }
  function sectionView(r) {
    let s = r.t === "s" ? secById.get(r.id) : D.sections.find(x => x.proposals.concat(x.questions).some(i => i.key === r.id));
    if (!s) return `<p class="empty">No section ${esc(r.id)}.</p>`;
    let h = `<p class="crumb"><a href="#design">Design</a> ›</p><h1><span class="sid">${s.id === "OV" ? "★" : "§" + esc(s.id)}</span> ${esc(s.title)}</h1>
      <p class="meta">${esc(SSTAT[s.status] || s.status)}${s.updated ? ` · updated ${esc(s.updated)}` : ""} · <code>${esc(s.file)}</code></p>`;
    if (s.status === "draft") {
      h += `<p class="draftnote">Not written yet.</p>`;
      if (s.decided) h += `<section class="part"><h2>Already decided <span class="aside">in my words — tell me if I got it wrong</span></h2><div class="prose">${s.decided}</div></section>`;
      if (s.settle) h += `<section class="part"><h2>To settle</h2><div class="prose">${s.settle}</div></section>`;
      return h;
    }
    if (s.status === "rework") h += `<p class="draftnote">Being redone — read it as notes. Your answers here are still kept.</p>`;
    if (s.lead) h += `<div class="prose part">${s.lead}</div>`;
    if (s.experience) h += `<section class="part"><h2>The experience</h2><div class="prose">${s.experience}</div></section>`;
    if (s.decided) h += `<section class="part"><h2>Already decided <span class="aside">in my words — tell me if I got it wrong</span></h2><div class="prose">${s.decided}</div></section>`;
    if (s.activities) h += `<section class="part"><h2>The game, activity by activity</h2><div class="prose">${s.activities}</div></section>`;
    for (const ref of s.reference || []) h += `<details class="ref part"><summary>${esc(ref.title)}</summary><div class="prose">${ref.html}</div></details>`;
    if (s.proposals.length) h += `<section class="part"><h2>Proposals <span class="aside">my calls — keep what's right, change or cut what isn't</span></h2>${s.proposals.map(p =>
      `<article class="card" id="card-${esc(p.key)}"><div class="card-head"><span class="tag">${esc(p.id)}</span><h3>${p.title}</h3></div><div class="prose">${p.html}</div>
      ${p.lenses ? `<div class="lenses"><b>Checked against</b> ${p.lenses}</div>` : ""}${noteWidget(propK(p), YES_CHANGE_NO, "", "Your note on " + p.plain)}</article>`).join("")}</section>`;
    if (s.questions.length) h += `<section class="part"><h2>Questions <span class="aside">yours to answer</span></h2>${s.questions.map(q =>
      `<article class="card" id="card-${esc(q.key)}"><div class="card-head"><span class="tag">${esc(q.id)}</span><h3>${q.title}</h3></div><div class="prose">${q.context}</div>
      ${questionWidget(noteK("gdd", q.key), q)}${q.rec ? `<div class="rec"><b>My pick: ${esc(q.rec.key)}.</b> ${q.rec.html}</div>` : ""}</article>`).join("")}</section>`;
    h += `<section class="part"><h2>The whole section</h2>${noteWidget(noteK("section", s.id), [], "Anything else about this section?", "Your note on the section")}
      ${approveWidget(signK("section", s.id), "Approve this section")}</section>`;
    if (s.sources) h += `<details class="ref part"><summary>Sources</summary><div class="prose">${s.sources}</div></details>`;
    return h;
  }

  // ------------------------------------------------------------ Status
  function statusView() {
    const ap = k => { const a = approvalState(k); return a === "ok" ? `<span class="ap ok">✓</span>` : a === "stale" ? `<span class="ap stale">changed</span>` : `<span class="ap">—</span>`; };
    let h = `<h1>Status</h1><p class="lede">Where everything stands. <b>Approved</b> comes only from your own approvals in this app;
      nothing I write can mark something approved.</p>`;
    h += `<section class="part"><h2>Zones</h2><div class="tablewrap"><table class="stab"><thead><tr><th>Zone</th><th>Ring</th><th>Layout</th><th>Map approved</th><th>Details approved</th><th>Built</th></tr></thead><tbody>${D.zones.map(z =>
      `<tr><td>${zoneLink(z.id)}</td><td>${esc(z.ring)}</td><td>${D.maps[z.id] ? "built zone" : z.layout ? "designed" : "not yet"}</td><td>${ap(signK("zone", z.id + ".map"))}</td><td>${ap(signK("zone", z.id + ".plan"))}</td><td>${z.built ? "yes" : "no"}</td></tr>`).join("")}</tbody></table></div></section>`;
    h += `<section class="part"><h2>Bugs</h2><div class="tablewrap"><table class="stab"><thead><tr><th>Bug</th><th>Family</th><th>In the game</th><th>Design approved</th></tr></thead><tbody>${D.bugs.map(b =>
      `<tr><td>${bugLink(b.id)}</td><td>${esc(b.family)}</td><td>${b.species.length ? "yes" : "no"}</td><td>${ap(signK("bug", b.id))}</td></tr>`).join("")}</tbody></table></div></section>`;
    h += `<section class="part"><h2>Design sections</h2><div class="tablewrap"><table class="stab"><thead><tr><th>Section</th><th>Status</th><th>Answered</th><th>Approved</th></tr></thead><tbody>${D.sections.map(s => {
      const [n, t] = answered(s); return `<tr><td><a href="#s-${s.id}">${s.id === "OV" ? "★" : "§" + esc(s.id)} ${esc(s.title)}</a></td><td>${esc(SSTAT[s.status] || s.status)}</td><td>${t ? `${n}/${t}` : "—"}</td><td>${ap(signK("section", s.id))}</td></tr>`;
    }).join("")}</tbody></table></div></section>`;
    h += `<section class="part"><h2>Items, by kind</h2><div class="tablewrap"><table class="stab"><thead><tr><th>Kind</th><th>Rows</th><th>Marked</th><th>Decided</th><th>Archived</th></tr></thead><tbody>${D.groups.map(([g, l]) => {
      const rows = D.items.filter(it => it.group === g); if (!rows.length) return "";
      return `<tr><td><a href="#k-${g}">${esc(l)}</a></td><td>${rows.length}</td><td>${rows.filter(it => S.filled("i:" + it.id)).length}</td><td>${rows.filter(it => it.decided).length}</td><td>${rows.filter(archived).length}</td></tr>`;
    }).join("")}</tbody></table></div></section>`;
    const orph = S.orphans();
    h += `<section class="part"><h2>Older notes <span class="aside">answers you gave on rows or items that no longer exist — kept, never deleted</span></h2>${orph.length
      ? `<ul class="orphans">${orph.map(o => `<li><code>${esc(o.coll)}/${esc(o.id)}</code>${o.body.mark ? ` · ${esc(o.body.mark)}` : ""}${o.body.note ? `<div class="onote">${esc(o.body.note)}</div>` : ""}</li>`).join("")}</ul>`
      : `<p class="empty">None (or the storage hasn't answered yet).</p>`}</section>`;
    if (D.unmatched.length) h += `<section class="part"><h2>Words I couldn't place</h2><p class="sub">Phrases in the ecology section the app couldn't match to a bug.</p><ul>${D.unmatched.map(u => `<li>${esc(u)}</li>`).join("")}</ul></section>`;
    const s = S.summary();
    h += `<section class="part"><h2>About this page</h2><p>Built ${esc(D.built_at)} · data ${esc(D.version)} · ${Object.entries(D.accounting).map(([k, v]) => `${esc(k)}: ${v}`).join(" · ")}</p>
      <p>Storage: ${esc(s.text)}</p></section>`;
    return h;
  }

  // ------------------------------------------------------------ Explain
  function explainView(r) {
    if (r.id) {
      const e = D.explain.find(x => x.slug === r.id);
      if (!e) return `<p class="empty">No page ${esc(r.id)}.</p>`;
      return `<p class="crumb"><a href="#explain">Explain</a> ›</p><h1>${e.title}</h1><div class="prose explain">${e.html}</div>`;
    }
    return `<h1>Explanations</h1><p class="lede">Plain explanations of design ideas and measurements, with diagrams and numbers.</p>${D.explain.length
      ? `<ul class="secs">${D.explain.map(e => `<li><a href="#e-${e.slug}"><span class="stitle">${e.title}</span></a></li>`).join("")}</ul>`
      : `<p class="empty">None yet.</p>`}`;
  }

  // ------------------------------------------------------------ text size
  let scale = ls.get(KA + "-scale", 1);
  const applyScale = () => document.documentElement.style.setProperty("--scale", String(scale));
  $("#smaller").addEventListener("click", () => { scale = Math.max(0.85, +(scale - 0.1).toFixed(2)); ls.set(KA + "-scale", scale); applyScale(); });
  $("#bigger").addEventListener("click", () => { scale = Math.min(1.4, +(scale + 0.1).toFixed(2)); ls.set(KA + "-scale", scale); applyScale(); });
  applyScale();

  render();
  S.connect();
})();
