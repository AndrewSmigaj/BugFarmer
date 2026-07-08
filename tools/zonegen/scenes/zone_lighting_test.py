#!/usr/bin/env python3
"""LIGHTING TEST zone (64x64) — the fast iteration vehicle for the underground darkness system.

Layout (zone orientation: HIGH y = NORTH = top of render = SURFACE; LOW y = SOUTH = deep underground):
  - top (high y): a LIT grass surface with a few trees.
  - an ORGANIC (non-straight) boundary.
  - below (low y): UNDERGROUND — a stone block-mass (buried-block darkness) with a carved meandering
    tunnel + a cavern chamber (roofed-tunnel darkness), a `torch` + a `mushroom_glow` (torch reveal).
  The WHOLE underground region (solid AND open cells) is roof-marked, so a runtime-dug cell stays dark.

Not a production zone — kept tiny for fast Play-load + fast PNG render.

  python3 tools/zonegen/scenes/zone_lighting_test.py       # build + save + lint
  python3 tools/world/view_world.py lighting_test --roof   # PNG minimap with the roof overlay
"""
import os
import sys
import json
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder            # noqa: E402
from features import cave                       # noqa: E402

W = H = 64


def _boundary_y(x):
    """Organic (non-straight) surface↔underground boundary. Deterministic. Underground = y below this."""
    return int(34 + 5 * math.sin(x * 0.35) + 3 * math.sin(x * 0.11 + 1.3) + ((x * 7) % 5 - 2))


def build(zone_id="lighting_test"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Lighting Test", seed=7)

    # Underground = every cell below the organic boundary.
    underground = {(x, y) for x in range(W) for y in range(H) if y < _boundary_y(x)}

    # Underground floor reads as dirt (surface stays grass) — makes the split visible in the PNG too.
    for (x, y) in underground:
        Z.set_ground(x, y, "dirt")

    # Carve a meandering tunnel + a cavern chamber (open cells) through the underground.
    tunnel = cave.carve_tunnel(Z, (8, 10), (54, 24), style="natural", width=3, seed=7)
    cavern = cave.carve_cavern(Z, 40, 8, shape="blob", size=6, seed=3)
    open_cells = (tunnel | cavern) & underground   # keep carving inside the underground region

    # Fill the rest of the underground with a stone mass + copper veins (M1 buried-block darkness).
    # `carved` = everything that should NOT be solid = all surface cells + the open tunnel/cavern.
    all_cells = {(x, y) for x in range(W) for y in range(H)}
    carved = (all_cells - underground) | open_cells
    cave.fill_solid(Z, carved, {"base": "stone_block",
                                "veins": [("ore_copper_block", 4, 5, 10, "any")]}, seed=11)

    # Light sources in the open underground (M3 reveal): a torch mid-tunnel + a glow-mushroom in the cavern.
    tlist = sorted(open_cells)
    if tlist:
        tx, ty = tlist[len(tlist) // 2]
        Z.place_occupant("torch", tx, ty)
    clist = sorted(cavern & underground)
    if clist:
        mx, my = clist[len(clist) // 2]
        if (mx, my) != (tlist[len(tlist) // 2] if tlist else None):
            Z.place_occupant("mushroom_glow", mx, my)

    # A little lit surface content up north for contrast.
    for (x, y) in [(16, 52), (40, 56), (52, 48)]:
        if Z.is_free(x, y):
            Z.place_occupant("tree_oak", x, y)

    # ROOF: mark the WHOLE underground region (solid AND open) so runtime-dug cells stay dark.
    Z.mark_roof_region(underground)

    Z.spawn = [32, 60]   # up on the lit surface
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")   # save() writes row/col 0,0 — fine for a test zone
    cfg = json.load(open(cfg_path))
    cfg["row"], cfg["col"] = 0, 0
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    roofed = sum(sum(1 for v in row if v) for row in Z.roof)
    print(f"saved 64x64 lighting_test -> {out} | occupants {len(Z.occ)} | roofed cells {roofed}")
    print("lint:", Z.lint() or "clean")
