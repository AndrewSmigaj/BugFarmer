#!/usr/bin/env python3
"""Scene — UNDERGROUND mining features (the worked example for docs/guides/authoring/caves.md).

A ~1/16-zone slab of solid rock showing the underground vocabulary and the spatial rules:
- a MAN-MADE straight RAIL tunnel crossing the map (rail + supports + a cart) — straight because built;
- NATURAL meandering / burrowed tunnels off it (never straight);
- caverns of varied SHAPE: a central blob (with a still pool), a long gallery, a rocky chamber with
  interior rock columns, and a cave MOUTH clipping the south edge;
- ore placed as rarity-tiered VEINS per the beginning-mining-zone table (copper/coal common, iron
  uncommon, tiny tin + silver, dirt pockets, hard-stone deep) — NO clay (that's other zones);
- cave dressing (crystals, glow/regular mushrooms, rubble, bones, moss, a mossy treasure chest) and
  fauna (ants in a burrow, a cave spider, a beetle, a cricket).

Renders to tools/_generated/previews/underground/scene_underground_caverns.png (its theme folder).
Run: python3 tools/zonegen/scenes/scene_underground_caverns.py
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                         # noqa: E402
from render import render_builder                                          # noqa: E402
from features.cave import carve_tunnel, carve_cavern, carve_chamber, cave_pool, fill_solid  # noqa: E402

W, H = 64, 64

# Beginning mining zone (underground_passages_31) ore table — see authoring/caves.md §4.
ORE_TABLE = {
    "base": "stone_block",
    "veins": [
        ("ore_copper_block", 9, 3, 6),    # common
        ("ore_coal_block", 8, 3, 6),      # common
        ("ore_iron_block", 6, 3, 5),      # uncommon
        ("ore_tin_block", 4, 2, 3),       # rare, tiny
        ("ore_silver_block", 4, 2, 3),    # rare, tiny
    ],
    "pockets": [                          # MORE DIRT, less bare stone overall
        ("dirt_block", 14, 4, "top"),     # soft, plentiful near the entrance (north/high-y)
        ("dirt_block", 7, 3, "bottom"),   # more dirt deep too
    ],
}


PREVIEW = "zones/underground_passages_31/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_underground_caverns", W, H, base_tile="cave_floor",
                    name="Underground caverns")
    rng = random.Random(11)
    rail_y = 50

    # --- caverns (varied shapes) ---
    central = carve_chamber(b, 32, 30, 13, seed=1)                      # irregular multi-blob chamber (not a bowl)
    gallery = carve_cavern(b, 49, 22, shape="long", size=9, seed=2)
    rocky = carve_cavern(b, 15, 25, shape="rocky", size=9, seed=3)
    mouth = carve_cavern(b, 33, 5, shape="blob", size=8, seed=4)        # clips the south edge = cave mouth

    # --- man-made straight RAIL tunnel across the map (built => straight; wide so it doesn't read as rows) ---
    rail = carve_tunnel(b, (1, rail_y), (W - 2, rail_y), style="straight", width=5)

    # --- natural meandering tunnels connecting things (never straight) ---
    nat = set()
    nat |= carve_tunnel(b, (32, rail_y), (32, 36), style="natural", width=2, seed=5)   # rail -> central
    nat |= carve_tunnel(b, (32, 26), (33, 10), style="natural", width=2, seed=6)       # central -> mouth
    nat |= carve_tunnel(b, (27, 30), (18, 26), style="natural", width=2, seed=7)       # central -> rocky
    nat |= carve_tunnel(b, (37, 29), (47, 23), style="natural", width=2, seed=8)       # central -> gallery
    nat |= carve_tunnel(b, (8, 44), (26, 33), style="natural", width=1, seed=9)        # a wandering burrow

    carved = central | gallery | rocky | mouth | rail | nat

    # --- irregular pools (lake-grade waterline + re-derived wet-rock shore) in two caverns ---
    pool = cave_pool(b, 31, 31, 7, carved, seed=2)                      # central chamber
    pool |= cave_pool(b, 49, 22, 5, carved, seed=12)                    # gallery end

    # --- fill all remaining rock with blocks + rarity-tiered ore veins ---
    fill_solid(b, carved, ORE_TABLE, seed=4)

    open_cells = (carved - pool)

    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved

    def free_fp(oid, x, y):
        fw, fh = b.footprint(oid)
        return all((x + dx, y + dy) in carved and (x + dx, y + dy) not in pool
                   and b.is_free(x + dx, y + dy) for dx in range(fw) for dy in range(fh))

    # --- interior rock columns in the rocky chamber (the "stalagmite" clumps) ---
    rocky_inner = [c for c in rocky if c not in pool
                   and all(is_rock(c[0] + dx, c[1] + dy) is False for dx, dy in ((0, 0),))]
    for (clx, cly) in rng.sample(sorted(rocky), k=min(5, len(rocky))):
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            x, y = clx + dx, cly + dy
            if (x, y) in rocky and (x, y) not in pool and b.is_free(x, y) and rng.random() < 0.7:
                b.place_occupant("stone_block", x, y)

    # --- the man-made tunnel: rail down the centre + WOOD-BLOCK supports along the walls ---
    # (no clutter on the track here — mining gear is the camp scene's job)
    for x in range(2, W - 2):
        if b.is_free(x, rail_y):
            b.place_occupant("mine_rail", x, rail_y, surface=None, reserve=False)
    for x in (7, 17, 27, 41, 55):                       # wood pillars flanking the 5-wide track, here & there
        for sy in (rail_y - 2, rail_y + 2):
            if (x, sy) in carved and b.is_free(x, sy):
                b.place_occupant("wall_wood", x, sy, surface=None)

    # --- quartz embedded in the wall faces + the occasional wall torch ---
    faces = [(x, y) for (x, y) in open_cells
             if any(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    rng.shuffle(faces)
    for (x, y) in faces:
        if not b.is_free(x, y):
            continue
        rock_nbrs = sum(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        r = rng.random()
        if r < 0.06 and rock_nbrs >= 2:
            b.place_occupant("quartz_block", x, y, surface=None)   # quartz nestled in a wall seam (never open floor)
        elif r < 0.10:
            b.place_occupant("torch_wall", x, y, surface=None)

    # --- mossy treasure chest by the pool, ringed with glow mushrooms + moss ---
    if free_fp("chest_mossy", 36, 31):
        b.place_occupant("chest_mossy", 36, 31, surface=None)
    for _ in range(8):
        x, y = 31 + rng.randint(-6, 7), 31 + rng.randint(-4, 4)
        if (x, y) in open_cells and b.is_free(x, y):
            b.place_occupant(rng.choice(["mushroom_glow", "mushroom_glow", "cave_moss"]),
                             x, y, surface=None)

    # --- cave dressing: FUNGUS clusters in light-pools against the walls + a sparse earthtone floor scatter ---
    # (quartz is a WALL mineral, embedded in faces above — never floor litter)
    import math as _m
    cells = [c for c in open_cells if b.is_free(*c)]
    wall_cells = [c for c in cells if any(is_rock(c[0] + dx, c[1] + dy)
                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    rng.shuffle(wall_cells)
    clumps = []
    for c in wall_cells:
        if len(clumps) >= 9:
            break
        if any(_m.hypot(c[0] - gx, c[1] - gy) < 6 for gx, gy in clumps):
            continue
        clumps.append(c)
    fungus = ["mushroom_glow", "mushroom_glow", "mushroom_blue", "mushroom_brown",
              "mushroom_red", "mushroom_puffball", "cave_moss", "crystal_small"]   # the odd crystal sparkle
    dressed = set()
    for (gx, gy) in clumps:
        for (x, y) in cells:
            if _m.hypot(x - gx, y - gy) <= 2.2 and rng.random() < 0.55 and b.is_free(x, y):
                if b.place_occupant(rng.choice(fungus), x, y, surface=None):
                    dressed.add((x, y))
    # sparse earthtone litter on the open floor (rubble/moss/bone) — keeps the cave readable
    earth = [k for k, n in [("rubble", 6), ("cave_moss", 3), ("bone_pile", 2)] for _ in range(n)]
    for (x, y) in cells:
        if (x, y) in dressed or not b.is_free(x, y):
            continue
        if rng.random() < 0.05 and not any(abs(x - p) <= 1 and abs(y - q) <= 1 for p, q in dressed):
            if b.place_occupant(rng.choice(earth), x, y, surface=None):
                dressed.add((x, y))

    # --- fauna (free-floating bug sprites) ---
    for i, (bx, by) in enumerate(sorted(nat)):
        if i % 9 == 0:                                  # ants strung along a natural/burrow tunnel
            b.place_bug("ant_worker", bx + 0.2, by + 0.2, scale=0.6)
    b.place_bug("cave_spider", 15.0, 25.0, scale=0.95)
    b.place_bug("beetle_common", 49.0, 22.0, scale=0.8)
    b.place_bug("cricket", 33.0, 6.0, scale=0.7)

    b.spawn = [4, rail_y - 1]                            # west mouth of the rail tunnel (off the rail)
    return b


# cave-shape labels (text, cell_x, cell_y) drawn on the render for the guide
LABELS = [("blob cavern + pool", 24, 33), ("long gallery", 43, 24), ("rocky chamber", 8, 27),
          ("cave mouth", 27, 8), ("rail tunnel (man-made)", 2, 53), ("burrow", 5, 42)]


def _label(out):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(out).convert("RGBA")
    cpx = img.width / W
    d = ImageDraw.Draw(img)
    f = ImageFont.load_default()
    for text, cx, cy in LABELS:
        px, py = int(cx * cpx), int((H - 1 - cy) * cpx)
        d.rectangle([px - 2, py - 2, px + 7 * len(text), py + 12], fill=(0, 0, 0, 170))
        d.text((px, py), text, fill=(255, 240, 150), font=f)
    img.save(out)


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
