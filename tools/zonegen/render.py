#!/usr/bin/env python3
"""Render a ZoneBuilder directly to a preview PNG (no zone files needed).

For SCENE vignettes we don't want to pollute nakama/data/zones with throwaway zones, so
build scripts build a ZoneBuilder in memory and render it straight to a focused PNG via
the shared make_scene renderer (placeholders + footprint-X + pivot, same as the game).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # tools/
import make_scene  # noqa: E402


def render_builder(b, out, scale=6, bounds=None):
    """Render builder `b` (optionally a (x0,y0,x1,y1) cell viewport) to `out`.
    """
    x0, y0, x1, y1 = bounds or (0, 0, b.W - 1, b.H - 1)
    gw, gh = x1 - x0 + 1, y1 - y0 + 1
    ground = [[b.ground[y0 + yy][x0 + xx] for xx in range(gw)] for yy in range(gh)]
    occ = [(c["id"], x - x0, y - y0) for (x, y), c in b.occ.items()
           if c.get("anchor") and x0 <= x <= x1 and y0 <= y <= y1]
    players = [(s, x - x0, y - y0) for (s, x, y) in getattr(b, "players", [])
               if x0 <= x <= x1 and y0 <= y <= y1]
    bugs = [(t[0], t[1] - x0, t[2] - y0, t[3], t[4] if len(t) > 4 else False)
            for t in getattr(b, "bugs", []) if x0 <= t[1] <= x1 and y0 <= t[2] <= y1]
    decor = [(s, x - x0, y - y0, m) for (s, x, y, m) in getattr(b, "decor", [])
             if x0 <= x <= x1 and y0 <= y <= y1]
    r = make_scene.render_scene(ground, occ, b.meta, scale, out, players=players, bugs=bugs,
                                decor=decor)
    print(f"  rendered {r['gw']}x{r['gh']} -> {r['w']}x{r['h']}px  {out}")
    if r["placeholders"]:
        print(f"  placeholders: {', '.join(r['placeholders'])}")
    if r["missing_tiles"]:
        print(f"  missing tiles: {', '.join(r['missing_tiles'])}")
    return r
