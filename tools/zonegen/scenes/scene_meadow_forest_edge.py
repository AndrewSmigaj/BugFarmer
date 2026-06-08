#!/usr/bin/env python3
"""Scene — MEADOW / FOREST EDGE (the northern transition of `butterfly_meadow_11`).

The cool, shaded seam where the bright meadow gives way to woodland and the danger ramps up. The
renderer is NORTH-UP (grid row 0 is the image BOTTOM = south), so this scene reads bottom -> top as
warm meadow -> dark forest:
  * SOUTH (bottom): lush grass with the last drifting butterflies + a few milkweed/flowers.
  * MID: the ground darkens to scuffed DIRT; THRESHOLD STUMPS (stump / stump_mossy) mark the old
    clearing's end; ferns + edge mushrooms creep in.
  * THE FALLEN-LOG BRIDGE: a long log (log_fallen) laid across a boggy seam, furred with mushrooms —
    the literal crossing into harder ground (a centipede highway).
  * NORTH (top): a thickening TREE BAND of pine/oak/dead-tree CLUSTERS closing into gloom, with
    log piles, bramble, bracken-ferns, mushroom clusters on the deadwood.
  * EDGE THREATS: a slow armored MILLIPEDE and a fast venomous CENTIPEDE, each assembled from the
    existing segmented head/body/tail part sprites (the difficulty step toward the forest zones).

Flowers/bugs are free-floating COLLECTIBLE decor (sub-grid, scaled); only props are grid occupants.
Renders to ONE canonical file: tools/_generated/previews/scene_meadow_forest_edge.png
Run: python3 tools/zonegen/scenes/scene_meadow_forest_edge.py
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
from features.garden import flower_patch         # noqa: E402

W, H = 60, 46


def build():
    b = ZoneBuilder("scene_meadow_forest_edge", W, H, base_tile="grass",
                    name="Meadow / Forest Edge", biome="forest")
    rng = random.Random(13)

    # --- GROUND GRADIENT: grass (south/bottom) darkens to scuffed DIRT toward the forest (north) ---
    # irregular dirt patches thicken with height so the "temperature drop" reads in the floor itself.
    for y in range(24, H):
        for x in range(W):
            t = (y - 24) / float(H - 24)                # 0 at the seam -> 1 at the top
            if rng.random() < 0.25 + 0.6 * t:
                b.set_ground(x, y, "dirt")
    b.fill_ground(0, 40, W - 1, H - 1, "dirt")          # solid forest floor along the top

    # --- THE FALLEN-LOG BRIDGE: a long log across a boggy dirt seam (the crossing into the woods) ---
    b.fill_ground(20, 26, 31, 29, "dirt")               # the boggy seam it lies across
    b.place_occupant("log_fallen", 22, 27)              # 4x1 fallen trunk
    b.place_occupant("mushroom_bracket", 21, 26)        # oyster/turkeytail fungus on the log
    b.place_occupant("mushroom_cluster", 27, 26)
    b.place_bug("moth_brown", 25, 28.4, scale=0.6)

    # --- THRESHOLD STUMPS: where the old clearing ends (mid-band) ---
    for sx, sy, sid in [(8, 24, "stump"), (12, 26, "stump_mossy"), (40, 25, "stump"),
                        (45, 27, "stump_mossy"), (33, 23, "stump")]:
        b.place_occupant(sid, sx, sy)
        b.place_occupant("mushroom_bracket", sx + 1, sy)  # bracket fungus on the dead wood

    # --- THE NORTHERN TREE BAND: clusters of forest trees thickening into gloom (top) ---
    def tree_cluster(cx, cy, kinds, n, spread=3, seed=0):
        r = random.Random(seed)
        for _ in range(n):
            tx = cx + r.randint(-spread, spread)
            ty = cy + r.randint(-spread, spread)
            if b.in_bounds(tx, ty) and b.is_free(tx, ty):
                b.place_occupant(r.choice(kinds), tx, ty)

    tree_cluster(8, 40, ["tree_pine", "tree_oak"], 8, 4, seed=1)
    tree_cluster(20, 42, ["tree_pine", "tree_dead", "tree_oak"], 9, 4, seed=2)
    tree_cluster(34, 41, ["tree_pine", "tree_oak"], 8, 4, seed=3)
    tree_cluster(48, 42, ["tree_pine", "tree_dead"], 9, 4, seed=4)
    tree_cluster(56, 38, ["tree_pine"], 5, 3, seed=5)
    # a few scouts reaching south into the meadow (the band frays at its edge)
    for tx, ty in [(5, 33), (16, 34), (30, 35), (43, 33), (54, 34), (24, 37)]:
        if b.is_free(tx, ty):
            b.place_occupant(rng.choice(["tree_pine", "tree_oak"]), tx, ty)

    # --- DEADWOOD + DECOMPOSITION LAYER: log piles, brambles, fungus on the forest floor ---
    for lx, ly in [(14, 38), (38, 37), (50, 36)]:
        b.place_occupant("log_pile", lx, ly)
    for bx, by in [(11, 35), (28, 39), (46, 38)]:
        b.place_occupant("bramble", bx, by)

    # --- forest-edge SCATTER: ferns + edge mushrooms + bushes (darker understory) ---
    scatter(b, 0, 22, W - 1, H - 1,
            {"fern": 7, "mushroom_brown": 3, "mushroom_cluster": 2, "mushroom_bracket": 1,
             "mushroom_chanterelle": 1, "mushroom_morel": 1, "bush": 3, "clubmoss": 2,
             "moss_clump": 3, "tall_grass": 3, "wild_berry_bush": 1},
            density=0.16, min_spacing=2, seed=7, surfaces=("grass",))

    # --- SOUTH (bottom): the warm meadow we're leaving — lighter flower scatter + tall grass ---
    scatter(b, 0, 0, W - 1, 20,
            {"tall_grass": 6, "flower_aster": 3, "flower_red": 2, "flower_blue": 2,
             "flower_yellow": 2, "milkweed": 2, "clover": 3, "bush_flowering": 2, "lavender": 2,
             "poppy": 2, "yarrow": 1, "bush": 2},
            density=0.12, min_spacing=2, seed=8, surfaces=("grass",))
    flower_patch(b, 0, 0, W - 1, 18,
                 ["flower_red", "flower_blue", "flower_yellow", "flower_aster", "poppy", "dandelion"],
                 28, seed=3, scale=0.7)

    # --- THE EDGE THREATS: a millipede + a centipede, assembled from segmented part sprites ---
    def chain(parts, x, y, dx, dy, step=0.7, scale=1.3):
        for i, p in enumerate(parts):
            b.place_bug(p, x + dx * step * i, y + dy * step * i, scale=scale)

    # millipede — slow, armored, longer/rounder; crawling out from under the log-pile deadwood
    chain(["millipede_head_a"] + ["millipede_body_a"] * 6 + ["millipede_tail_a"],
          12, 33, 1, 0.25, scale=1.25)
    # centipede — fast, venomous, flatter; emerging from the boggy seam by the fallen-log bridge
    chain(["centipede_head_a", "centipede_body_a", "centipede_body_a", "centipede_body_a",
           "centipede_tail_a"], 30, 30, -1, 0.3, scale=1.3)

    # --- a few LINGERING pollinators down south + dusk life at the gloom ---
    for _ in range(3):
        b.place_bug(rng.choice(["butterfly_monarch", "butterfly_common"]),
                    rng.uniform(2, 56), rng.uniform(2, 18), scale=0.8)
    b.place_bug("butterfly_swallowtail", 40, 14, scale=0.85)
    b.place_bug("firefly_blue", 50, 39, scale=0.6)      # dusk glow at the forest edge
    b.place_bug("moth_luna", 20, 41, scale=0.8)         # a forest-edge dusk moth

    b.spawn = [30, 2]                                   # enter from the warm meadow (south)
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_meadow_forest_edge.png"))
    render_builder(b, out, scale=6)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
