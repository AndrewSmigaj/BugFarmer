#!/usr/bin/env python3
"""Scenes — ant_colony_40 DISTRICT pieces (zone-craft crafted scenes; composed into the zone).

Each is a composable `place_*(b, cx, cy)` piece, laid DELIBERATELY (the ROWS rule for cultivated /
stored things; clusters for brood), NOT scattered. The zone carves the chamber; these place props.
Rendered together as one district preview under previews/zones/ant_colony_40/scenes/.
- place_fungus_terrace  — cultivated mushroom ROWS on stepped shelves + a compost edge.
- place_brood_nursery   — clustered ant_brood + ant_eggs with a clear nurse lane, warm moss.
- place_granary         — food caches stacked in tidy ROWS.
- place_ore_wall        — the SECRET: a stone pocket salted with row-4 ore behind a 1-block window.
- place_deep_sump       — a flooded gallery (cave_pool), the row-5 tease.
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__)); ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                          # noqa: E402
from features.cave import carve_chamber, cave_pool                          # noqa: E402

PREVIEW = "zones/ant_colony_40/scenes"
SCALE = 5


def _occ(b, oid, x, y):
    if b.in_bounds(x, y) and b.is_free(x, y):
        try:
            return b.place_occupant(oid, x, y, surface=None, reserve=False) or True
        except Exception:
            return False
    return False


# ---- ORGANIC PLACEMENT ENGINE (natural, not geometric) --------------------------------------
# The fix for "haphazardly sprinkled": growth/piles gather in irregular CLUSTERS that hug the
# chamber WALLS and corners, dense-core + ragged falloff, leaving the CENTRE open (ant traffic).
# No rows, no rings, no even spacing.

def _chamber(b, cx, cy, R):
    """The free floor cells of a carved chamber around (cx,cy)."""
    return [(x, y) for x in range(cx - R, cx + R + 1) for y in range(cy - R, cy + R + 1)
            if b.in_bounds(x, y) and b.is_free(x, y)]


def _wallness(cells):
    """Per-cell count of missing (solid/OOB) 3x3 neighbours — higher = closer to a wall/corner."""
    cs = set(cells)
    return {(x, y): sum((x + dx, y + dy) not in cs for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            for (x, y) in cells}


def organic(b, cells, spec, rng, *, clusters=4, radius=3, fill=0.6, wall_bias=2.0,
            open_center=0.35, spacing=1):
    """Grow occupants in ORGANIC clusters over `cells`. spec=[(id,weight),...]. Cluster seeds prefer
    WALL-hugging cells (wall_bias), each grows a dense-core/ragged-edge blob of one dominant species
    (fill, distance falloff), sizes vary ~3:1 (C13), the chamber CENTRE stays open (open_center =
    fraction of radius kept clear). spacing=1 packs contiguous masses; spacing>=2 spreads patches."""
    if not cells:
        return []
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    maxr = max((((x - mx) ** 2 + (y - my) ** 2) ** 0.5) for (x, y) in cells) or 1.0
    wall = _wallness(cells)
    cand = [(x, y) for (x, y) in cells if ((x - mx) ** 2 + (y - my) ** 2) ** 0.5 >= open_center * maxr] or cells
    ids = [s[0] for s in spec]; wts = [s[1] for s in spec]
    placed = []
    for _ in range(clusters):
        w = [(wall[c] + 0.3) ** wall_bias for c in cand]
        sx, sy = rng.choices(cand, w)[0]
        dom = rng.choices(ids, wts)[0]
        r = max(1, int(round(radius * rng.uniform(0.5, 1.5))))          # size varies ~3:1
        blob = [(x, y) for (x, y) in cells if ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5 <= r]
        rng.shuffle(blob)
        for (x, y) in blob:
            d = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
            if rng.random() > fill * (1 - d / (r + 0.6)):               # dense core, ragged edge
                continue
            if spacing > 1 and any(max(abs(x - px), abs(y - py)) < spacing for (px, py) in placed):
                continue
            oid = dom if rng.random() < 0.8 else rng.choices(ids, wts)[0]  # mostly dominant, a little mix
            if b.place_occupant(oid, x, y, surface=None, reserve=False):
                placed.append((x, y))
    return placed


def place_fungus_terrace(b, cx, cy):
    """The nest's FUNGUS GARDEN — the ants' fungus growing in irregular PATCHES that creep over the
    floor and hug the walls, brightest where the glow-caps cluster, damp moss threading between, open
    traffic down the middle. Organic growth, never planted rows. (A proper fungus-comb sprite is TBD;
    real cave mushrooms + moss stand in to prove the placement.)"""
    rng = random.Random(cx * 3 + cy + 1)
    cells = _chamber(b, cx, cy, 10)
    wall = _wallness(cells)
    # damp fungal floor (mud) creeping in from the walls, patchy — where the fungus takes hold
    for (x, y) in cells:
        if wall[(x, y)] >= 1 and rng.random() < 0.45:
            b.set_ground(x, y, "mud")
    # the fungus GROWTH — dense patches of pale + glow caps hugging the walls, ragged, open centre
    organic(b, cells, [("mushroom_inkcap", 4), ("mushroom_brown", 3), ("mushroom_glow", 2)], rng,
            clusters=6, radius=3, fill=0.6, wall_bias=2.5, open_center=0.42, spacing=1)
    # damp moss threading between the fungus patches (sparser)
    organic(b, cells, [("moss_clump", 4)], rng, clusters=4, radius=2, fill=0.5,
            wall_bias=1.2, open_center=0.2, spacing=2)
    # a couple of tending workers among the growth (not on a grid)
    for _ in range(4):
        x, y = rng.choice(cells)
        b.place_bug("ant_worker", x, y, scale=1.9)


def place_brood_nursery(b, cx, cy):
    """The nest's NURSERY — brood PILED in irregular heaps that gather in the warm damp corners and
    hug the walls, tended by nurse ants moving among them; the centre stays open for traffic. Purely
    organic — no rows, no cells, no human props."""
    rng = random.Random(cx * 7 + cy)
    cells = _chamber(b, cx, cy, 10)
    wall = _wallness(cells)
    # damp warm floor where brood gathers (the wall corners), patchy not uniform
    for (x, y) in cells:
        if wall[(x, y)] >= 2 and rng.random() < 0.55:
            b.set_ground(x, y, "mud")
    # brood HEAPS — dense masses clustered against the walls, the centre left open
    heaps = organic(b, cells, [("ant_brood", 5)], rng, clusters=6, radius=3, fill=0.8,
                    wall_bias=3.0, open_center=0.42, spacing=1)
    # a little damp moss + glow among the heaps (sparser patches, for warmth/light)
    organic(b, cells, [("moss_clump", 3), ("mushroom_glow", 1)], rng, clusters=3, radius=2,
            fill=0.5, wall_bias=1.5, open_center=0.2, spacing=2)
    # nurse ants tending — placed NEXT TO the brood heaps, not on a grid
    for _ in range(7):
        if not heaps:
            break
        hx, hy = rng.choice(heaps)
        b.place_bug("ant_worker", hx + rng.randint(-1, 1), hy + rng.randint(-1, 1), scale=1.8)


def place_granary(b, cx, cy):
    """A sectioned STOREROOM (not a crate clone-grid): the leafcutter LEAF store (W), stacked crate &
    basket tiers on the N wall, a LIQUID/grain bay (barrels, kegs, sacks, E), a clear loading AISLE
    with a tally board + torchlight, a hauling ant file, and overflow spilling from a full crate."""
    row1 = ["produce_crate", "apple_crate", "basket", "crate", "produce_crate", "apple_crate"]
    for i, gx in enumerate(range(cx - 6, cx + 7, 2)):                 # N-wall tier of varied crates
        _occ(b, row1[i % len(row1)], gx, cy - 6)
    for i, gx in enumerate(range(cx - 5, cx + 6, 2)):                 # a lower second tier
        _occ(b, ["apple_crate", "basket", "produce_crate"][i % 3], gx, cy - 4)
    # W bay: the LEAF/plant store (leafcutter harvest) — leaf litter + log piles (log_pile is 2-wide)
    for (lx, ly) in [(cx - 8, cy - 1), (cx - 8, cy + 1), (cx - 8, cy + 3)]:
        _occ(b, "log_pile", lx, ly)
    for (dx, dy) in [(cx - 6, cy - 2), (cx - 5, cy), (cx - 6, cy + 2), (cx - 5, cy + 4)]:
        _occ(b, "leaf_litter", dx, dy)
    # E bay: the LIQUID/grain store — honeydew barrels, kegs, grain sacks (all 1x1)
    for (dx, dy, oid) in [(6, -2, "barrel"), (7, -1, "keg"), (6, 0, "ore_sack"),
                          (7, 1, "barrel"), (6, 2, "ore_sack"), (7, 3, "keg")]:
        _occ(b, oid, cx + dx, cy + dy)
    # S tier + OVERFLOW spilling from a full crate
    for i, gx in enumerate(range(cx - 4, cx + 6, 3)):
        _occ(b, ["crate", "produce_crate", "basket"][i % 3], gx, cy + 6)
    for (dx, dy) in [(-2, 5), (-1, 5), (-3, 6)]:                      # spilled produce on the floor
        _occ(b, "mushroom_brown", cx + dx, cy + dy)
    # loading AISLE: a tally board + torchlight; a hauling ant file down the centre
    _occ(b, "notice_board", cx, cy + 7)
    _occ(b, "torch", cx - 8, cy - 3); _occ(b, "torch", cx + 8, cy + 4)
    for i in range(3):
        b.place_bug("ant_worker", cx + (i - 1), cy + 1 + i, scale=1.9)


def place_ore_wall(b, cx, cy):
    """The SECRET geode — a crystal-lined pocket with a rich ore CORE, hidden in solid dirt behind a
    thin cracked veneer with a TELL (a crystal peeking through). An old collapsed dig beside it — the
    lost miner's bones, a dropped lantern, rubble, his last ore chunk — tells why it was never claimed."""
    orng = random.Random(cx + cy)
    for dy in range(-4, 5):                                        # the stone POCKET
        for dx in range(-4, 5):
            _occ(b, "stone_block", cx + dx, cy + dy)

    def _swap(x, y, oid):                                          # replace a stone cell with something
        b.occ.pop((x, y), None); b.reserved[y][x] = False
        b.place_occupant(oid, x, y, surface=None, reserve=False)
    for (oid, n) in [("ore_gold_block", 4), ("ore_diamond_block", 3),
                     ("ore_platinum_block", 3), ("ore_silver_block", 3)]:   # rich ore CORE (centre)
        for _ in range(n):
            _swap(cx + orng.randint(-2, 2), cy + orng.randint(-2, 2), oid)
    for (dx, dy) in [(-3, -2), (3, -2), (-3, 2), (3, 2), (0, -3), (0, 3)]:  # crystal geode LINING
        _swap(cx + dx, cy + dy, orng.choice(["crystal_small", "quartz_block"]))
    _swap(cx - 4, cy, "crystal_small")                            # the TELL — a crystal in the west face
    # the old COLLAPSED DIG beside it (the lost miner's story)
    for (dx, dy, oid) in [(-6, 0, "rubble"), (-6, -1, "lantern"), (-7, 0, "bone_pile"),
                          (-6, 1, "rubble"), (-5, 0, "ore_gold_block")]:
        x, y = cx + dx, cy + dy
        b.occ.pop((x, y), None); b.reserved[y][x] = False; b.set_ground(x, y, "cave_floor")
        _occ(b, oid, x, y)


def place_deep_sump(b, cx, cy):
    """An eerie underground LAKE — the deep tease. A still irregular pool with floor STONE SPIRES rising
    from the shallows (C20: floor, not ceiling), a pale evaporite crust ring, glow reflecting at the
    shore, damp cave flora, and a drowned RELIC at the water's edge (the 'what happened here')."""
    cave_pool(b, cx, cy, 6, set((x, y) for x in range(cx - 9, cx + 10) for y in range(cy - 7, cy + 8)), seed=cx)
    for (dx, dy) in [(-5, -3), (4, 3), (-3, 4), (6, -1), (-6, 1)]:          # floor stone SPIRES
        _occ(b, "stone_block", cx + dx, cy + dy)
    for (dx, dy) in [(-8, 0), (8, 0), (0, -6), (0, 6), (-6, -4), (6, -4),   # pale EVAPORITE crust ring
                     (-6, 4), (6, 4), (-7, 2), (7, -2)]:
        x, y = cx + dx, cy + dy
        if b.in_bounds(x, y) and not b.ground[y][x].startswith("water"):
            b.set_ground(x, y, "sand")
    for (mx, my) in [(cx - 7, cy + 4), (cx + 7, cy - 3), (cx - 5, cy - 5), (cx + 5, cy + 4)]:
        _occ(b, "mushroom_glow" if (mx + my) % 2 else "cave_moss", mx, my)  # reflected glow + damp flora
    _occ(b, "bone_pile", cx + 6, cy + 3); _occ(b, "crate", cx - 6, cy - 2)  # a drowned relic


def build():
    W, H = 96, 40
    b = ZoneBuilder("scene_colony_districts", W, H, base_tile="dirt", name="Colony Districts", biome="cave")
    for y in range(H):
        for x in range(W):
            b.place_occupant("dirt_block", x, y)
    slots = [(16, place_fungus_terrace), (34, place_brood_nursery), (52, place_granary),
             (70, place_ore_wall), (86, place_deep_sump)]
    for (sx, fn) in slots:
        if fn is not place_ore_wall:                               # carve a chamber for the room ones
            for (ox, oy) in carve_chamber(b, sx, 20, 10, seed=sx):
                if b.occ.get((ox, oy)):
                    del b.occ[(ox, oy)]; b.reserved[oy][ox] = False
                b.set_ground(ox, oy, "cave_floor")
        fn(b, sx, 20)
    b.spawn = [8, 20]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
