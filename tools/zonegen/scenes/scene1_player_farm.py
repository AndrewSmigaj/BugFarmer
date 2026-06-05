#!/usr/bin/env python3
"""Scene 1 — the player's private plot (rich showcase).

A cohesive homestead: the ⊥ cottage (north), a fountain GARDEN PLAZA, a wood-fenced FLY PEN
(the fly-farming lifecycle) mirrored by an ORCHARD of close-set rows, a tilled CROP GARDEN of
mixed vegetables, an organic POND, a little well/rest corner, flower planters in front of the
house, and butterflies/bees about. Flowers and fruit are free-floating COLLECTIBLE decor (sub-grid,
not aligned to cells); only structures/furniture/crops are grid occupants.

Renders to ONE canonical file: tools/_generated/previews/scene1_player_farm.png
Run: python3 tools/zonegen/scenes/scene1_player_farm.py
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from render import render_builder                # noqa: E402
from features.scatter import scatter             # noqa: E402
from houses.player_house import place_player_house  # noqa: E402

W, H = 46, 50


# ---- helpers ----------------------------------------------------------------
def hpath(b, x0, x1, y):
    for x in range(x0, x1 + 1):
        b.set_ground(x, y, "stone_path", surface="path")


def vpath(b, x, y0, y1):
    for y in range(y0, y1 + 1):
        b.set_ground(x, y, "stone_path", surface="path")


def fence_rect(b, x0, y0, x1, y1, gate, fence="fence_wood"):
    cells = set()
    for x in range(x0, x1 + 1):
        cells.add((x, y0)); cells.add((x, y1))
    for y in range(y0, y1 + 1):
        cells.add((x0, y)); cells.add((x1, y))
    cells.discard(gate)
    for c in sorted(cells):
        b.place_occupant(fence, *c)
    b.place_occupant("gate_wood", *gate)


def fruit_around(b, tx, ty, fresh="fallen_fruit", n=6):
    """Fallen/rotting fruit as free-floating decor around a tree base (sub-grid, half scale)."""
    rng = random.Random(tx * 131 + ty)
    for _ in range(n):
        dx, dy = rng.uniform(-1.5, 1.5), rng.uniform(-1.2, 0.3)
        fid = "rotten_fruit" if rng.random() < 0.3 else fresh
        b.place_decor(fid, tx + dx, ty + dy, scale=0.5)


def flower_patch(b, x0, y0, x1, y1, kinds, n, seed=0, scale=0.8):
    """Flowers as free-floating COLLECTIBLE decor — sub-grid (not snapped to cells), on grass."""
    rng = random.Random(seed)
    placed = tries = 0
    while placed < n and tries < n * 10:
        tries += 1
        fx, fy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ix, iy = int(round(fx)), int(round(fy))
        if b.in_bounds(ix, iy) and b.is_free(ix, iy) and b.surface[iy][ix] == "grass":
            b.place_decor(rng.choice(kinds), fx, fy, scale=scale)
            placed += 1


def pond(b, cx, cy, rx, ry, seed=3):
    """An ORGANIC water feature: irregular shallow blob with a smaller deep centre + reeds."""
    rng = random.Random(seed)
    bank = []
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if not b.in_bounds(x, y):
                continue
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            d = (nx * nx + ny * ny) ** 0.5
            if d <= 1.0 + rng.uniform(-0.15, 0.15):
                b.set_ground(x, y, "water_deep" if d <= 0.5 else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
            elif d <= 1.5:
                bank.append((x, y))
    for (x, y) in bank:
        if b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.3:
            b.place_occupant("reeds", x, y)


def crop_bed(b, x0, y0, x1, y1, crops):
    """A tilled bed with MIXED crops — each column a different crop, cycling `crops`."""
    b.fill_ground(x0, y0, x1, y1, "garden_plot", surface="farm")
    for i, x in enumerate(range(x0, x1 + 1)):
        crop = crops[i % len(crops)]
        for y in range(y0, y1 + 1):
            if b.is_free(x, y):
                b.place_occupant(crop, x, y, surface="farm")


# ---- the scene --------------------------------------------------------------
def build():
    b = ZoneBuilder("scene1_player_farm", W, H, base_tile="grass", name="Player farm")

    place_player_house(b, ox=4, oy=22)           # door ~ (22,30); stub path x22/23 y26..29
    vpath(b, 22, 1, 25)
    vpath(b, 23, 1, 25)
    hpath(b, 15, 29, 14)                          # gate-level connector: pen <-> plaza <-> orchard

    # --- GARDEN PLAZA (centre): paved, fountain focal point ---
    b.fill_ground(18, 14, 27, 23, "stone_path", surface="path")
    b.place_occupant("fountain", 22, 18)
    b.place_occupant("bench", 19, 16)
    b.place_occupant("bench", 24, 16)
    b.place_occupant("statue_stone", 18, 22)
    b.place_occupant("birdbath", 24, 22)
    b.place_occupant("potted_plant", 27, 15)
    b.place_occupant("potted_plant", 18, 15)
    b.place_occupant("potted_plant", 27, 22)
    b.place_bug("butterfly_monarch", 20, 21, scale=0.7)
    b.place_bug("honeybee", 25, 20, scale=0.7)
    # plaza south entrance: a garden arch over the path, flanked by a hedge row + lamp posts
    b.place_occupant("garden_arch", 22, 13)
    for hx in (19, 20, 21, 24, 25, 26):
        b.place_occupant("hedge", hx, 13)
    b.place_occupant("lamp_post", 18, 13)
    b.place_occupant("lamp_post", 27, 13)

    # --- house-front garden: flower planters + greenery flanking the entrance ---
    b.place_occupant("planter_box", 17, 25)
    b.place_occupant("planter_box", 26, 25)
    b.place_occupant("bush", 15, 25)
    b.place_occupant("bush", 29, 25)
    b.place_occupant("potted_plant", 20, 24)
    b.place_occupant("potted_plant", 25, 24)
    b.place_bug("butterfly_common", 19, 24, scale=0.7)

    # --- FLY PEN (left): trees+fruit | net row | catchers ---
    b.fill_ground(3, 9, 14, 19, "dirt", surface="farm")
    fence_rect(b, 2, 8, 15, 20, gate=(15, 14))
    b.place_occupant("tree_apple", 4, 11)
    b.place_occupant("tree_orange", 4, 16)
    fruit_around(b, 4, 11, fresh="fallen_fruit")
    fruit_around(b, 4, 16, fresh="fallen_orange")
    netrows = (10, 11, 12, 13, 15, 16, 17, 18)   # gap at gate row 14
    for ny in netrows:
        b.place_occupant("fly_netting", 8, ny)
    b.place_occupant("autonet", 11, 10)
    b.place_occupant("compost_bin", 14, 10)
    b.place_occupant("net_post", 11, 17)
    b.place_occupant("apple_crate", 14, 17)
    b.place_occupant("broken_net", 13, 19)
    for ny in netrows:                            # small flies on the net edges
        b.place_bug("fly_common", 7.6, ny + 0.25, scale=0.5)
        b.place_bug("fly_common", 8.4, ny - 0.25, scale=0.5)
    for c in [(6, 11), (6, 16), (5, 13), (12, 12), (13, 11), (12, 18)]:
        b.place_bug("fly_common", c[0], c[1], scale=0.5)
    b.place_player("farmer_down", 16, 14)

    # --- ORCHARD (right): close-spaced rows, fruit matching each row's tree ---
    fence_rect(b, 29, 8, 44, 20, gate=(29, 14))
    rows = [(18, "tree_apple", "fallen_fruit"),
            (15, "tree_orange", "fallen_orange"),
            (11, "tree_apple", "fallen_fruit")]
    cols = (32, 35, 38, 41)
    for ry, sp, _fr in rows:
        for cx in cols:
            b.place_occupant(sp, cx, ry)
    for ry, sp, fr in rows:
        for cx in cols:
            fruit_around(b, cx, ry, fresh=fr, n=4)
    b.place_bug("butterfly_common", 35, 13, scale=0.7)
    b.place_bug("butterfly_monarch", 40, 17, scale=0.7)

    # --- CROP GARDEN (bottom-centre): mixed-crop beds + a scarecrow, and an EMPTY tilled bed ---
    crop_bed(b, 16, 1, 20, 6, ["plant_tomato", "plant_corn", "plant_wheat"])
    crop_bed(b, 25, 1, 29, 6, ["plant_wheat", "plant_tomato", "plant_corn"])
    b.place_occupant("scarecrow", 21, 5)         # overseeing the crops
    b.place_occupant("signpost", 15, 6)
    b.place_bug("butterfly_common", 18, 7, scale=0.7)
    b.place_bug("ladybug", 27, 4, scale=0.7)
    b.fill_ground(31, 1, 36, 5, "garden_plot", surface="farm")  # an EMPTY tilled bed (no crops)

    # --- organic POND (bottom-left) with lily pads ---
    pond(b, 8, 4, 5, 3)
    for lp in [(7, 4), (9.3, 3), (8, 5.5), (6, 4.5)]:
        b.place_decor("lily_pad", lp[0], lp[1], scale=0.8)
    b.place_bug("dragonfly", 9, 6, scale=0.7)

    # --- WELL rest corner (far bottom-right) ---
    b.place_occupant("well", 42, 3)
    b.place_occupant("bench", 39, 6)
    b.place_bug("butterfly_monarch", 40, 7, scale=0.7)

    # --- PINE FOREST framing the plot (also fills the bare margins beside/above the house) ---
    forest = {"tree_pine": 4, "bush": 2, "mushroom_red": 1, "tall_grass": 2}
    scatter(b, 0, 26, 7, 49, forest, density=0.28, min_spacing=1, seed=21, surfaces=("grass",))
    scatter(b, 38, 26, 45, 49, forest, density=0.28, min_spacing=1, seed=22, surfaces=("grass",))
    scatter(b, 0, 1, 1, 25, forest, density=0.25, min_spacing=1, seed=23, surfaces=("grass",))
    scatter(b, 44, 1, 45, 25, forest, density=0.25, min_spacing=1, seed=24, surfaces=("grass",))
    scatter(b, 31, 1, 44, 7, {"bush": 3, "tall_grass": 2, "mushroom_red": 1},
            density=0.1, min_spacing=2, seed=8, surfaces=("grass",))

    # --- flowers as free-floating COLLECTIBLE decor (sub-grid), wrapping AROUND the house too ---
    fkinds = ["flower_red", "flower_blue", "flower_yellow", "flower_wild"]
    flower_patch(b, 1, 1, 15, 9, fkinds, 12, seed=1)        # near the pond
    flower_patch(b, 30, 1, 45, 9, fkinds + ["sunflower"], 12, seed=2)  # well / empty-bed corner
    flower_patch(b, 0, 22, 16, 49, fkinds, 18, seed=3)      # margin beside the house (W)
    flower_patch(b, 30, 22, 45, 49, fkinds, 18, seed=4)     # margin beside the house (E)
    flower_patch(b, 16, 24, 29, 26, fkinds, 6, seed=5)      # by the entrance
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene1_player_farm.png"))
    render_builder(b, out, scale=6)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
