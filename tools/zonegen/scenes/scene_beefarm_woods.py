#!/usr/bin/env python3
"""Scene — BEE FARM + WOODS (half and half). Left: a flower meadow + a fenced APIARY (beehives of every
size + a honey extractor) with bees and butterflies. Right: WOODS — a meandering stream, a dirt woods
path, mixed trees, ferns/mushrooms/berry bushes, and forest fauna. A bee-farm sign out front.
Renders to tools/_generated/previews/scene_beefarm_woods.png.
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
from features.terrain import stream              # noqa: E402
from features.garden import flower_patch         # noqa: E402
from features.yard import fence_rect             # noqa: E402

W, H = 70, 54


PREVIEW = "zones/bee_meadow/scenes"
SCALE = 3


def build():
    b = ZoneBuilder("scene_beefarm_woods", W, H, base_tile="grass", name="Bee farm & woods", biome="meadow")
    rng = random.Random(4)

    # --- a meandering stream down the right (woods) side ---
    stream(b, (54, H - 1), (60, 1), width=2, seed=2)

    # --- dirt woods path winding from the farm into the woods ---
    x = 24
    for y in range(2, H - 2):
        for dx in (0, 1):
            if b.is_free(x + dx, y):
                b.set_ground(x + dx, y, "dirt", surface="path")
        x += rng.choice([-1, 0, 0, 1])
        x = max(20, min(40, x))

    # --- the apiary: a fenced yard of beehives + honey extractor (left) ---
    fence_rect(b, 3, 6, 18, 20, gate=(10, 20))
    for hive, hx in [("beehive_basic", 5), ("beehive_medium", 7), ("beehive_large", 10),
                     ("beehive_deluxe", 13)]:
        b.place_occupant(hive, hx, 16)
    b.place_occupant("honey_extractor", 5, 11)
    b.place_occupant("signpost", 10, 4)               # bee-farm sign out front (custom sign later)
    b.place_occupant("bench", 15, 9)
    b.place_occupant("lamp_post", 3, 5)

    # --- flower meadow around the farm (collectible flowers, common + a few rarer) ---
    common = ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "clover", "dandelion"]
    rarer = ["lavender", "chamomile", "poppy", "sunflower"]
    flower_patch(b, 1, 22, 22, H - 1, common, 26, seed=1)
    flower_patch(b, 20, 2, 40, 20, common + rarer, 16, seed=2)

    # --- woods (right half): trees, ferns, mushrooms, berry bushes ---
    scatter(b, 42, 1, W - 1, H - 1,
            {"tree_pine": 7, "tree_oak": 5, "bush": 5, "fern": 4, "wild_berry_bush": 3,
             "mushroom_brown": 3, "mushroom_chanterelle": 2, "tall_grass": 4},
            density=0.16, min_spacing=2, seed=3, surfaces=("grass",))
    flower_patch(b, 42, 1, W - 1, H - 1, ["flower_wild", "flower_blue", "fern"], 14, seed=4)

    # --- fauna: bees + butterflies over the farm, forest bugs in the woods ---
    for _ in range(8):
        b.place_bug(rng.choice(["honeybee", "bumblebee"]), rng.uniform(3, 20), rng.uniform(8, 24), scale=1.0)
    for _ in range(5):
        b.place_bug(rng.choice(["butterfly_common", "butterfly_monarch"]),
                    rng.uniform(2, 38), rng.uniform(2, H - 2), scale=1.0)
    b.place_bug("beetle_common", 50.0, 20.0, scale=1.0)
    b.place_bug("dragonfly", 58.0, 30.0, scale=1.0)

    b.spawn = [10, 22]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
