#!/usr/bin/env python3
"""Scene — BUTTERFLY MEADOW (the open meadow proper, `butterfly_meadow_11`).

A bright, drifting flowering meadow thick with milkweed and wildflowers, clouds of pollinators
overhead, and the first hints that it bites back (a paper wasp + a yellowjacket hunt here). Staged
landmarks (south -> north, gentle -> wild):
  * the SOUTH ENTRANCE from the village road — a flower arch, a signpost, a "first bloom" bush.
  * the FLOWER-CLOCK GLADE — a ring of different-colored wildflowers around a birdbath "sundial".
  * the GREAT MILKWEED STAND — an oversized milkweed cluster (milkweed_giant) ringed with milkweed,
    swarming with monarchs (the iconic spot; composed from existing flowers + the new giant prop).
  * the BASKING BOULDER — a big mossy rock in the open, butterflies/beetles sunning on it.
  * the BROKEN FENCE LINE — a half-buried split-rail run with a leaning gate, swallowed by tall grass.
  * the LEPIDOPTERIST'S BLIND — a bug-watcher's camp (tent, specimen case, jars-crate, net post, lantern).
  * a small SPRING/PUDDLE with cattails + lily, scattered open-grown trees, and a heavy flower scatter.

Flowers and bugs are free-floating COLLECTIBLE decor (sub-grid, scaled, NOT grid occupants); only
structures/props are grid occupants. Renders to ONE canonical file:
  tools/_generated/previews/scene_butterfly_meadow.png
Run: python3 tools/zonegen/scenes/scene_butterfly_meadow.py
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
from features.terrain import vpath, pond         # noqa: E402

W, H = 64, 52


def build():
    b = ZoneBuilder("scene_butterfly_meadow", W, H, base_tile="grass",
                    name="Butterfly Meadow", biome="meadow")
    rng = random.Random(11)

    # NOTE: the renderer is NORTH-UP (grid row 0 is at the image BOTTOM = south). So the village
    # road arrives at LOW y (bottom) and the meadow drifts toward the forest at HIGH y (top).

    # --- SOUTH ENTRANCE (bottom): the village road, a flower arch, the "first bloom" greeting ---
    vpath(b, 30, 0, 6, tile="dirt")
    vpath(b, 31, 0, 6, tile="dirt")
    b.place_occupant("garden_arch", 30, 4)             # threshold "you are leaving town"
    b.place_occupant("signpost", 27, 2)                # Village v / Forest ^
    b.place_occupant("bush_flowering", 34, 2)          # the "first bloom" that greets you
    b.place_occupant("bush_flowering", 27, 4)

    # --- a small SPRING / PUDDLE (bottom-left, by the entrance), the meadow's only water ---
    pond(b, 8, 5, 4, 3)
    b.place_occupant("cattail", 2, 9)
    b.place_occupant("cattail", 14, 2)
    for lp in [(7, 5), (9.5, 6), (8, 4)]:
        b.place_decor("water_lily", lp[0], lp[1], scale=0.8)

    # --- FLOWER-CLOCK GLADE (centre-left): a ring of differently-colored blooms, sundial centre ---
    cx, cy = 18, 22
    b.place_occupant("birdbath", cx, cy)               # the "sundial" centre
    ring = [("flower_red", 0, -3), ("flower_yellow", 2, -2), ("flower_aster", 3, 0),
            ("flower_yellow", 2, 2), ("flower_red", 0, 3), ("flower_blue", -2, 2),
            ("flower_aster", -3, 0), ("flower_blue", -2, -2)]
    for fid, dx, dy in ring:
        b.place_decor(fid, cx + 0.5 + dx, cy + 0.5 + dy, scale=1.0)

    # --- GREAT MILKWEED STAND (centre): the iconic spot, oversized giant + a colony of milkweed ---
    b.place_occupant("milkweed_giant", 37, 26)         # 2x1 oversized centrepiece
    for mx, my in [(35, 25), (40, 25), (36, 28), (39, 28), (34, 27), (41, 27), (37, 23), (38, 30)]:
        b.place_occupant("milkweed", mx, my)
    # monarchs swarming the stand (collectible bugs, sub-grid, scaled)
    for _ in range(5):
        b.place_bug("butterfly_monarch", rng.uniform(33, 44), rng.uniform(23, 32), scale=0.9)

    # --- BASKING BOULDER (centre-right): a mossy rock in a sunbeam ---
    b.place_occupant("boulder", 50, 24)
    b.place_occupant("moss_clump", 49, 23)
    b.place_occupant("thyme", 53, 23)
    b.place_bug("butterfly_swallowtail", 50.5, 26.5, scale=0.8)
    b.place_bug("ladybug_orange", 52, 25.5, scale=0.6)

    # --- BROKEN FENCE LINE (centre-left, a half-buried split-rail run swallowed by tall grass) ---
    for fx in range(7, 20):
        b.place_occupant("broken_fence", fx, 36)
    b.place_occupant("gate_wood", 20, 36)              # a leaning gate that opens onto nothing
    for gx in range(8, 19, 2):                          # poppies/weeds along the old fence
        b.place_decor("poppy", gx + 0.4, 36.6, scale=0.8)
    b.place_bug("spider_orb", 13, 36.4, scale=0.7)      # a web strung between the rails
    b.place_bug("butterfly_swallowtail", 16, 36.8, scale=0.8)

    # --- LEPIDOPTERIST'S BLIND (top-right, toward the wilder north): a bug-watcher's camp ---
    b.place_occupant("tent", 53, 43)
    b.place_occupant("specimen_case", 50, 42)
    b.place_occupant("crate", 56, 41)
    b.place_occupant("net_post", 51, 45)
    b.place_occupant("lantern", 57, 44)
    b.place_occupant("stool_wood", 52, 40)
    b.place_occupant("broken_net", 49, 39)              # the abandoned net in the grass
    b.place_occupant("lavender", 55, 39)                # a nectar magnet by the blind
    b.place_bug("moth_brown", 57.2, 43.6, scale=0.7)    # moths at the lantern

    # --- scattered OPEN-GROWN TREES (lone, wide-crown islands the meadow drifts around) ---
    for tx, ty in [(10, 44), (26, 42), (44, 46), (15, 12), (60, 12)]:
        b.place_occupant("tree_oak", tx, ty)
    b.place_occupant("tree_apple", 24, 34)              # relic of the failed farm by the fence
    b.place_occupant("scarecrow", 9, 33)                # forlorn failed-farm sentinel

    # --- meadow scatter: flowers + milkweed + tall grass + bushes + clover (the lush bulk) ---
    # Modest density + spacing so the named landmarks still breathe; a few species dominate.
    scatter(b, 0, 1, W - 1, H - 1,
            {"tall_grass": 7, "flower_aster": 3, "flower_red": 2, "flower_blue": 2,
             "flower_yellow": 2, "milkweed": 2, "clover": 3, "clover_red": 2, "bush": 2,
             "bush_flowering": 2, "poppy": 2, "lavender": 2, "yarrow": 2, "dandelion": 2,
             "chamomile": 1, "wild_berry_bush": 1},
            density=0.13, min_spacing=2, seed=7, surfaces=("grass",))

    # --- free-floating COLLECTIBLE flowers wrapping the meadow (sub-grid, scaled) ---
    # Two denser drifts (a lavender-ish SW band + a poppy-ish NE band) for clumped ecology/mood.
    fkinds = ["flower_red", "flower_blue", "flower_yellow", "flower_aster", "poppy", "dandelion"]
    flower_patch(b, 0, 1, 26, 18, ["lavender", "flower_blue", "clover", "flower_aster"], 16,
                 seed=31, scale=0.7)
    flower_patch(b, 38, 32, W - 1, 50, ["poppy", "flower_red", "flower_yellow", "dandelion"], 16,
                 seed=32, scale=0.7)
    flower_patch(b, 0, 1, W - 1, H - 1, fkinds, 26, seed=3, scale=0.7)

    # --- DRIFTING POLLINATORS + the wasps (predation pressure) across the whole meadow ---
    for _ in range(4):
        b.place_bug("butterfly_monarch", rng.uniform(2, 60), rng.uniform(2, 48), scale=0.85)
    for _ in range(3):
        b.place_bug("butterfly_swallowtail", rng.uniform(2, 60), rng.uniform(2, 48), scale=0.85)
    for _ in range(3):
        b.place_bug("butterfly_common", rng.uniform(2, 60), rng.uniform(2, 48), scale=0.7)
    for _ in range(4):
        b.place_bug(rng.choice(["bumblebee", "honeybee"]),
                    rng.uniform(2, 60), rng.uniform(2, 48), scale=0.6)
    b.place_bug("wasp_paper", 46, 44, scale=0.8)        # the easier wasp, near the camp/oak
    b.place_bug("wasp_yellowjacket", 36, 31, scale=0.85)  # the harder wasp, hunting the milkweed swarm

    b.spawn = [30, 2]                                   # arrive on the road from the village (south)
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_butterfly_meadow.png"))
    render_builder(b, out, scale=6)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
