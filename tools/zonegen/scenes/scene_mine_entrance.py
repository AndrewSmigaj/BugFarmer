#!/usr/bin/env python3
"""SCENE — mine entrance / cliff + the open-air mining CAMP (the surface→underground transition).

ORIENTATION: north = HIGH y = TOP of the render. Grass + camp at high y; an IRREGULAR cliff face drops into a
cave MOUTH; a rail descends SOUTH (low y / bottom) into the first cavern.

COMPOSITION RULES (see docs/guides/authoring/camps.md):
- cliff/grass↔rock edge is IRREGULAR (noise-wobbled) with broken rubble/boulders at its base — never a flat line.
- the camp reads as ORGANISED WORK-SITES clustered by function, never salt-and-peppered:
  campsite = tents RINGED round a campfire (+ log seats); smithy = forge+anvil ADJACENT (+ coal bin, quench
  barrel, tool rack); processing = ore_sluice AT the pond edge (+ staged ore piles/sacks, wheelbarrow);
  mine-head = the rail head at the mouth (cart, ore pile, sign, lantern); storage = crates/barrels/lumber rack.
- flora is SCATTERED naturally (loose tree stand, clumped bush/fern/grass/flowers), a few boulders/stumps.

The camp PROPS live in `place_camp(b, ox, oy, surf_y, mx, base, H)` — terrain-free (no grass/carve/fill/struts)
so the ZONE (zone_underground_passages) can paint its own full-width cliff + dense ore and just drop the camp
on top. `build()` below renders the standalone vignette (paints its own grass/cliff, then calls place_camp).

  python3 tools/zonegen/scenes/scene_mine_entrance.py
"""
import os
import sys
import math
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                      # noqa: E402
from render import render_builder                                       # noqa: E402
from features.terrain import pond, noise_field                          # noqa: E402
from features.cave import carve_tunnel, carve_cavern, fill_solid, place_pool   # noqa: E402
from features.scatter import scatter                                    # noqa: E402

W, H = 64, 60
ORE = {"base": "stone_block",
       "veins": [("ore_copper_block", 7, 3, 5), ("ore_coal_block", 7, 3, 5), ("ore_iron_block", 4, 2, 4)],
       "pockets": [("dirt_block", 8, 4, "top")]}


PREVIEW = "zones/underground_passages_31/scenes"
SCALE = 8


def cliff_surface(seed=4):
    """The irregular grass↔rock cliff line: `base` (the flat surface level) + a per-column wobbled `surf_y`
    (grass for y >= surf_y[x]). Shared so the zone can reuse the same edge technique."""
    nf = noise_field(W, 8, wavelength=10, octaves=2, seed=seed)
    base = H - 24                                                       # taller surface so the camp can breathe
    return base, [base + int(round(5 * (float(nf[0][x]) - 0.5) * 2)) for x in range(W)]


def place_camp(b, ox, oy, surf_y, mx, base, H):
    """Drop the open-air mining CAMP (props/flora/road/dressing only — NO grass paint, NO carve, NO fill, NO
    rail struts) at offset (ox,oy). Cells are guarded by `is_free` over the footprint, so anything landing on
    rock (a filled block) or water is skipped — call AFTER the terrain + fill_solid. `surf_y`/`base` describe
    the cliff line in LOCAL coords; `mx` is the local mouth/rail column."""
    rng = random.Random(5)

    def free(oid, x, y):
        fw, fh = b.footprint(oid)
        return all(b.is_free(ox + x + dx, oy + y + dy) for dx in range(fw) for dy in range(fh))

    def put(oid, x, y):
        return b.place_occupant(oid, ox + x, oy + y, surface=None) if free(oid, x, y) else False

    def player(sid, x, y):
        b.place_player(sid, ox + x, oy + y)

    def is_grass(x, y):
        return b.in_bounds(ox + x, oy + y) and b.ground[oy + y][ox + x] == "grass"

    def set_path(x, y):
        if is_grass(x, y):
            b.set_ground(ox + x, oy + y, "dirt", surface="path")

    def road_curve(y0, y1, w=3):                                       # a MEANDERING dirt road (never a ruler)
        ylo, yhi = min(y0, y1), max(y0, y1)
        for yy in range(ylo, yhi + 1):
            t = (yy - ylo) / max(1, yhi - ylo)                         # 0 at the mouth (low y), 1 at north edge
            cx = mx + int(round(6.0 * math.sin(t * 1.6)))             # one smooth eastward arc, no jog
            for xx in range(cx - w // 2, cx + w // 2 + 1):
                set_path(xx, yy)

    def trail(x0, y0, x1, y1):                                         # a thin trodden link between clusters
        x, y = x0, y0
        while (x, y) != (x1, y1):
            set_path(x, y)
            x += (x1 > x) - (x1 < x)
            y += (y1 > y) - (y1 < y)

    # main road in from the north edge down to the mouth (laid first so clusters sit beside it)
    road_curve(surf_y[mx], H - 1, w=3)

    # === MINE-HEAD (at the mouth, top-centre): rail-head cart, loaded ore, sign, lantern, supports ====
    hy = base + 1
    put("sign_camp", mx + 4, hy + 1)
    put("lantern", mx - 4, hy)
    put("mine_cart", mx - 1, base - 1)            # cart at the rail head, ready to roll down
    put("ore_pile", mx + 3, hy)
    put("ore_pile", mx - 5, hy + 2)
    put("mining_bucket", mx + 5, hy + 2)
    put("ladder", mx + 6, base)
    put("powder_keg", mx + 5, hy)                 # blasting supply at the head
    put("ore_sack", mx - 3, hy + 1)
    player("miner_down", mx - 2, base - 2)        # loading the cart at the rail-head
    # a guard-rail fence along the cliff lip flanking the mouth (open at the road/rail)
    for dx in list(range(-10, -3)) + list(range(4, 11)):
        gx = mx + dx
        if 0 <= gx < W:
            gy = surf_y[gx]
            if is_grass(gx, gy) and free("fence_wood", gx, gy):
                b.place_occupant("fence_wood", ox + gx, oy + gy, surface=None)

    # === SMITHY (centre-left, beside the road): forge+anvil adjacent + coal bin + quench + tools ======
    sx0, sy0 = 22, base + 5
    put("forge", sx0, sy0)
    put("anvil", sx0 + 2, sy0)                    # the smith works the anvil beside the forge
    put("coal_bin", sx0 - 1, sy0 + 1)
    put("water_bucket", sx0 + 3, sy0 + 1)         # quench
    put("tool_rack", sx0 - 2, sy0 - 1)
    put("ore_pile", sx0 + 3, sy0 - 1)
    put("keg", sx0 - 1, sy0 - 1)                  # fuel/oil at the forge
    put("workbench", sx0 + 4, sy0)               # bench for finishing tools
    put("sign_anvil", sx0 - 2, sy0 + 1)          # smithy marker

    # === CAMPSITE (far west): tents RINGED round a campfire, log seats facing it, small fence ========
    fx, fy = 9, base + 9
    put("campfire_spit", fx, fy)
    put("cooking_pot", fx + 1, fy)                # a pot on the fire
    for (tx, ty) in [(fx - 4, fy + 4), (fx + 4, fy + 4), (fx - 4, fy - 3), (fx + 4, fy - 3)]:
        put("tent", tx, ty)
    for (sx, sy) in [(fx - 2, fy), (fx + 2, fy), (fx, fy - 2), (fx, fy + 2)]:
        put("log_seat", sx, sy)
    put("barrel", fx - 3, fy + 1)
    put("crate", fx + 3, fy + 1)
    put("chest_wood", fx + 3, fy - 1)             # the crew's stash
    put("well", fx - 3, fy - 2)                   # the camp's water source

    # === PROCESSING (east, by the water): pond + ore_sluice at its edge + staged ore + wheelbarrow ====
    pcx, pcy = 50, base + 5
    pond(b, ox + pcx, oy + pcy, 4, 3, seed=7)
    for (rx, ry) in [(pcx - 4, pcy - 3), (pcx + 4, pcy - 2), (pcx + 3, pcy + 3), (pcx - 3, pcy + 3)]:
        put("reeds", rx, ry)                      # natural reedy pond edge
    put("ore_sluice", pcx - 5, pcy)               # sluice at the water's edge
    for (oxp, oyp) in [(pcx - 6, pcy + 1), (pcx - 7, pcy), (pcx - 6, pcy - 1)]:
        put("ore_pile" if (oxp + oyp) % 2 else "ore_sack", oxp, oyp)
    put("wheelbarrow", pcx - 8, pcy)

    # === STORAGE (far-east corner): lumber rack + crates/barrels ======================================
    for oid, x, y in [("lumber_rack", 59, base + 4), ("crate", 60, base + 6), ("barrel", 61, base + 7),
                      ("crate", 58, base + 6), ("notice_board", 56, base + 2)]:
        put(oid, x, y)

    # === LUMBER YARD (west-centre): where the mine's SUPPORT TIMBER is cut — sawmill + sawhorses + rack ==
    lx, ly = 15, base + 2
    put("sawmill", lx, ly)
    put("sawhorse", lx + 3, ly + 1)
    put("sawhorse", lx + 4, ly - 1)
    put("lumber_rack", lx - 2, ly + 1)
    put("crate", lx + 2, ly + 2)
    put("barrel", lx - 1, ly - 1)

    # === QUARRY SCAR (right of the mine-head): cut stone worked at the surface — stonecutter + spoil ====
    qx, qy = 42, base + 6
    put("stonecutter", qx, qy)
    put("ore_pile", qx + 2, qy)
    put("ore_sack", qx + 1, qy + 1)
    for (rx, ry) in [(qx - 1, qy + 1), (qx + 2, qy - 1), (qx + 3, qy + 1)]:
        put("standing_stone", rx, ry) or put("rubble", rx, ry)
    put("sandstone_formation", qx + 4, qy)

    # trails linking the clusters to the road + lamp posts for light
    trail(sx0 + 1, sy0, mx - 4, base + 2)
    trail(fx + 4, fy, sx0 - 2, sy0)
    trail(mx + 5, base + 2, pcx - 7, pcy)
    trail(pcx - 1, pcy, 57, base + 4)
    put("lamp_post", mx - 6, base + 2)
    put("lamp_post", pcx + 2, pcy)
    # entrance from the village (north): a signpost + a gate framing the road through the cliff-lip fence + lamps
    put("signpost", mx + 9, H - 3)
    put("gate_wood", mx - 3, surf_y[mx - 3])
    put("gate_wood", mx + 3, surf_y[mx + 3])
    for ly2 in (H - 6, base + 13):                                     # lamps lighting the worked road at night
        t = (ly2 - surf_y[mx]) / max(1, H - 1 - surf_y[mx])
        cx = mx + int(round(6.0 * math.sin(t * 1.6)))
        put("lamp_post", cx + 3, ly2)

    # === FLORA: loose tree stands + clumped undergrowth (scatter, never rows), keep paths clear ======
    for (tx, ty) in [(4, H - 3), (15, base + 14), (43, base + 1), (47, H - 3), (62, base + 1),
                     (26, H - 2), (46, H - 4)]:
        put(rng.choice(["tree_oak", "tree_pine", "tree_oak", "tree_apple"]), tx, ty)
    scatter(b, ox + 0, oy + base, ox + W - 1, oy + H - 1,
            {"bush": 3, "fern": 4, "tall_grass": 7, "clover": 5, "flower_red": 1, "flower_yellow": 1,
             "flower_blue": 1, "flower_wild": 2, "bush_flowering": 1, "mushroom_brown": 1},
            density=0.11, min_spacing=1, seed=8, surfaces=("grass",), clumping=0.65, cluster_radius=4)
    # broken cliff base: a band of rubble + the odd boulder where the rock breaks up into the grass
    for x in range(1, W - 1):
        for y in (surf_y[x] - 1, surf_y[x] - 2):
            if free("rubble", x, y) and rng.random() < 0.16:
                b.place_occupant(rng.choice(["rubble", "rubble", "rubble", "standing_stone", "standing_stone"]),
                                 ox + x, oy + y, surface=None, reserve=False)
    for (bx, by) in [(18, base + 1), (40, base + 2), (54, base + 8), (6, base + 2)]:
        put("stump", bx, by) or put("standing_stone", bx, by) or put("rubble", bx, by)

    player("miner_down", sx0 + 1, sy0 - 2)        # at the forge
    player("miner_left", pcx - 4, pcy)            # at the sluice


def build():
    b = ZoneBuilder("scene_mine_entrance", W, H, base_tile="cave_floor", name="Mine entrance")
    rng = random.Random(5)

    # --- IRREGULAR cliff: a TALL grass surface (north/top), rock (cliff) below the wobbled line --------
    base, surf_y = cliff_surface()
    for x in range(W):
        for y in range(surf_y[x], H):
            b.set_ground(x, y, "grass", surface="grass")

    # --- the cave MOUTH bitten up into the cliff, + rail descending south into a first cavern ---------
    # an ASYMMETRIC chamber system: mouth -> straight man-made shaft -> main cavern, with a natural SIDE-DIG
    # branching east off the shaft (an exploratory working) so the void never reads as a symmetric hourglass.
    mx = 33
    mouth = carve_cavern(b, mx, base - 3, shape="rocky", size=9, seed=2)
    rail = carve_tunnel(b, (mx, base - 1), (mx, 11), style="straight", width=5)
    cav = carve_cavern(b, mx - 2, 11, shape="lobed", size=12, seed=3)        # offset + lobed = off-centre void
    branch = carve_tunnel(b, (mx + 2, 22), (mx + 11, 19), style="natural", width=2, seed=6)
    sidecav = carve_cavern(b, mx + 12, 18, shape="rocky", size=5, seed=8)    # the exploratory side-working
    carved = {(x, y) for x in range(W) for y in range(surf_y[x], H)} | mouth | rail | cav | branch | sidecav
    fill_solid(b, carved, ORE, seed=5)
    place_pool(b, mx - 5, 8, 3, 2, carved, seed=9)            # still water in a cavern low spot (west side)

    place_camp(b, 0, 0, surf_y, mx, base, H)

    # === RAIL + WALL TORCHES down the shaft (a lit man-made descent — no timber struts) ===============
    for y in range(11, base):
        if (mx, y) in carved and b.is_free(mx, y):
            b.place_occupant("mine_rail", mx, y, surface=None, reserve=False)
    for y in range(base - 5, 12, -5):
        for s in (mx - 2, mx + 2):
            if (s, y) in carved and b.is_free(s, y) and ((s - 1, y) not in carved or (s + 1, y) not in carved):
                b.place_occupant("torch_wall", s, y, surface=None, reserve=False)

    # cave dressing + working miners (main cavern + the side-dig): glow, crystal, spoil, staged ore
    fw, fh = b.footprint("mine_cart")
    if all(b.is_free(mx + 11 + dx, 18 + dy) for dx in range(fw) for dy in range(fh)):
        b.place_occupant("mine_cart", mx + 11, 18, surface=None)        # a cart parked at the side-working
    cavefloor = [c for c in (cav | sidecav) if b.is_free(*c)]
    for c in rng.sample(cavefloor, k=min(18, len(cavefloor))):
        b.place_occupant(rng.choice(["mushroom_glow", "mushroom_glow", "mushroom_blue", "rubble",
                                     "bone_pile", "crystal_small", "crystal_small", "ore_pile"]),
                         *c, surface=None, reserve=False)
    b.spawn = [mx, H - 2]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
