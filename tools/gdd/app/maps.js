// maps.js — draw a zone's map, north up (docs/plans/review-app.md). The data is y-up (row 0 = the SOUTH edge, the
// game's convention: high y = north), so every drawn row is flipped through ONE function, toScreen. A probe (the
// village's deep water, which must lie south-west) is checked before drawing; if it lands wrong the map isn't drawn.
window.BFMaps = (function () {
  "use strict";
  const unrle = s => { const out = []; for (const p of s.split(",")) { const i = p.indexOf("*"); if (i < 0) out.push(+p); else { const v = +p.slice(0, i), n = +p.slice(i + 1); for (let j = 0; j < n; j++) out.push(v); } } return out; };
  const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const toScreen = (m, x, y) => ({ x: x, y: m.h - 1 - y });     // the one flip: data y-up -> screen y-down

  function probeOk(m) {
    if (!m.probe) return true;
    const p = toScreen(m, m.probe.x, m.probe.y);
    return p.x < m.w / 2 && p.y > m.h / 2;                     // south-west = left half, lower half on screen
  }

  // Draw ground and objects into `canvas` (one pixel per cell, scaled up by CSS). `opts.highlight` = an object id to
  // light up (other objects dimmed); `opts.cats` = category colours.
  function draw(canvas, m, opts) {
    opts = opts || {};
    if (!probeOk(m)) return false;
    canvas.width = m.w; canvas.height = m.h;
    const ctx = canvas.getContext("2d");
    const img = ctx.createImageData(m.w, m.h);
    const gcol = m.ground_colors.map(hex);
    const tcol = m.thing_palette.map(t => t ? hex((opts.cats || {})[(m.things[t] || {}).cat] || "#d04ad0") : null);
    const hi = opts.highlight ? m.thing_palette.indexOf(opts.highlight) : -1;
    for (let y = 0; y < m.h; y++) {
      const g = unrle(m.ground_rle[y]), t = unrle(m.thing_rle[y]);
      const sy = toScreen(m, 0, y).y;
      for (let x = 0; x < m.w; x++) {
        let c = gcol[g[x]];
        const ti = t[x];
        if (ti) {
          if (hi >= 0) c = ti === hi ? [255, 40, 160] : mix(c, tcol[ti], 0.35);
          else c = mix(c, tcol[ti], 0.85);
        } else if (hi >= 0) c = mix(c, [128, 128, 128], 0.25);
        const o = (sy * m.w + x) * 4;
        img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2]; img.data[o + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return true;
  }
  const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];

  // The labelled layer on top: spawn circles named by bug, the neighbours at each edge, the compass.
  function overlay(svg, m, opts) {
    opts = opts || {};
    const w = m ? m.w : 256, h = m ? m.h : 256;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    let s = "";
    const label = (x, y, text, anchor, cls) =>
      `<text x="${x}" y="${y}" text-anchor="${anchor || "middle"}" class="${cls || "lab"}">${text}</text>`;
    if (m && opts.spawn !== false) {
      for (const a of m.spawn_areas || []) {
        const p = toScreen(m, a.x, a.y);
        const names = (a.bugs || []).join(", ");
        s += `<circle cx="${p.x + .5}" cy="${p.y + .5}" r="${a.r}" class="spawn"/>`;
        if (names) s += label(p.x + .5, p.y + .5 - a.r - 2, names, "middle", "lab small");
      }
    }
    const e = opts.edges || {};
    if (e.north) s += label(w / 2, 9, "↑ " + e.north);
    if (e.south) s += label(w / 2, h - 4, "↓ " + e.south);
    if (e.west) s += `<text x="7" y="${h / 2}" class="lab" transform="rotate(-90 7 ${h / 2})" text-anchor="middle">← ${e.west}</text>`;
    if (e.east) s += `<text x="${w - 5}" y="${h / 2}" class="lab" transform="rotate(90 ${w - 5} ${h / 2})" text-anchor="middle">${e.east} →</text>`;
    s += `<g class="compass"><text x="${w - 14}" y="20" text-anchor="middle" class="lab">N</text><path d="M${w - 14} 24 l-4 9 h8 z"/></g>`;
    if (!m) s += label(w / 2, h / 2, opts.empty || "Layout not drawn yet", "middle", "lab big");
    svg.innerHTML = s;
  }

  // What's under the pointer: ground, object and the cell (in the game's own coordinates).
  function cellAt(m, canvas, ev) {
    const r = canvas.getBoundingClientRect();
    const sx = Math.floor((ev.clientX - r.left) / r.width * m.w), sy = Math.floor((ev.clientY - r.top) / r.height * m.h);
    if (sx < 0 || sy < 0 || sx >= m.w || sy >= m.h) return null;
    const y = m.h - 1 - sy;                                      // back through the flip
    const g = unrle(m.ground_rle[y])[sx], t = unrle(m.thing_rle[y])[sx];
    return { x: sx, y, ground: m.ground_palette[g], thing: t ? m.thing_palette[t] : null };
  }

  return { draw, overlay, cellAt, probeOk, toScreen, unrle };
})();
