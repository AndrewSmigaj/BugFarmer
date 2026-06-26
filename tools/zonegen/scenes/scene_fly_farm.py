#!/usr/bin/env python3
"""scene_fly_farm — FLY FARMING as a place (the game loop, not decoration).

The loop: grow fruit trees → fruit drops/rots → COMPOST BINS feed the flies →
flies REPRODUCE in the pens → catch by hand, on the net lines (flies accumulate),
or from the AUTO-CATCHERS you empty. The piece makes every step visible, in this
order on the ground, and everything sits in ROWS:

    [mini orchard: 2 tight rows of apple trees]      ← the food source
    [PEN A]  [PEN B]   ← two large fenced pens, compost-bin rows inside,
                          fly swarms over the bins (fences genuinely contain
                          flies: flies_over_fences=false + fences block bugs)
    [net lines along the outer flanks · autonet at each far corner]
    [collection trays in a row by the gates · a crate stack]

The zone composes `place_fly_farm(b, ox, oy)` beside a straight road and centers
the fly spawn circle on the pens — the farm is mechanically real today.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                    # noqa: E402
from features.terrain import hpath                     # noqa: E402
from features.yard import fence_rect                   # noqa: E402
from features.garden import fruit_around               # noqa: E402

PW, PH = 13, 13            # pen outer size
W, H = 40, 42              # the piece's canvas (standalone scene)


def _row(b, oid, cells, **kw):
    for (x, y) in cells:
        fw, fh = b.footprint(oid)
        if all(b.is_free(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
            b.place_occupant(oid, x, y, **kw)


def place_fly_farm(b, ox, oy):
    """The fly farm at SW corner (ox,oy), ~34×36. Gates face SOUTH (the road side).
    Returns ((cx, cy), r) — the pen-centered spawn circle for the zone config."""
    # --- the two PENS (south half), gates centered on the south fences ---
    a0x, a0y = ox + 2, oy + 6
    b0x = a0x + PW + 3                                # 3-cell work aisle between pens
    fence_rect(b, a0x, a0y, a0x + PW - 1, a0y + PH - 1, gate=(a0x + PW // 2, a0y))
    fence_rect(b, b0x, a0y, b0x + PW - 1, a0y + PH - 1, gate=(b0x + PW // 2, a0y))
    for px in (a0x, b0x):
        # compost-bin ROW along each pen's back (north) fence, evenly spaced
        _row(b, "compost_bin", [(px + 2, a0y + PH - 3), (px + 5, a0y + PH - 3),
                                (px + 8, a0y + PH - 3)])
        # the food on the ground: rotten fruit by the bins (render decor; the live
        # rot comes from fruit aging server-side)
        for i, (fx, fy) in enumerate([(px + 3.2, a0y + PH - 4.2), (px + 6.5, a0y + PH - 4.6),
                                      (px + 8.8, a0y + PH - 4.0)]):
            b.place_decor("rotten_fruit", fx, fy, scale=0.5)
        # the flies: a feeding cloud over the bin row (render-only; in-game swarms
        # spawn from the circle and are CONTAINED by the fences)
        for i in range(7):
            b.place_bug("fly_common", px + 2.5 + i * 1.2, a0y + PH - 3.5 - (i % 3) * 0.8,
                        scale=1.6, flip=(i % 2 == 0))

    # --- the catch gear lives INSIDE the pens (2026-06: where the flies are —
    # no net posts): NETTING runs along each pen's inner side walls (flies
    # accumulate on it — sticky-net mechanics later), and the AUTONET
    # auto-catcher sits in each pen's back corner (emptied on rounds).
    for px in (a0x, b0x):
        for y in range(a0y + 2, a0y + PH - 3, 2):
            _row(b, "fly_netting", [(px + 1, y), (px + PW - 2, y)])
        _row(b, "autonet", [(px + 1, a0y + PH - 4)])

    # --- the emptying station: collection trays in a ROW beside the gates + crates
    _row(b, "collection_tray", [(a0x + PW // 2 + 2, oy + 3), (a0x + PW // 2 + 5, oy + 3),
                                (b0x + PW // 2 + 2, oy + 3)])
    _row(b, "crate", [(a0x - 1, oy + 3), (a0x - 1, oy + 4)])
    # ONE earned failure read: the old torn net at pen A's SW corner
    _row(b, "broken_net", [(a0x - 2, a0y - 1)])

    # --- the MINI ORCHARD north of the pens: 2 tight rows × 4, a lane between ---
    t0y = a0y + PH + 4
    for ry in (t0y, t0y + 4):
        for tx in range(a0x + 2, a0x + 2 + 4 * 5, 5):
            if b.is_free(tx, ry):
                if b.place_occupant("tree_apple", tx, ry, surface="farm"):
                    fruit_around(b, tx, ry, n=3)

    cx = (a0x + b0x + PW) // 2
    cy = a0y + PH // 2
    return ((cx, cy), 13)


PREVIEW = "examples/farming"
SCALE = 4


def build():
    b = ZoneBuilder("scene_fly_farm", W, H, base_tile="grass", name="The fly farm")
    hpath(b, 2, W - 3, 2, tile="dirt")                  # the road it fronts
    hpath(b, 2, W - 3, 3, tile="dirt")
    place_fly_farm(b, 2, 4)
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
