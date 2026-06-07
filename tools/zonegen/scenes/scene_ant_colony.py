#!/usr/bin/env python3
"""Scene — ANT COLONY (next zone out), ~2x size: a nest dug through soil fills the left half — a
surface entrance, a meandering main shaft branching into chambers (queen / egg-brood / food), with
files of ants on the trails. One branch opens into a BIG tunnel leading right into a mushroom-packed
cavern, where a centipede and a millipede (assembled from head/body/tail segment sprites) crawl.
See docs/guides/feature-ant-colony.md. Renders to previews/scene_ant_colony.png.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                       # noqa: E402
from render import render_builder                         # noqa: E402
from features.cave import carve_cavern, fill_solid        # noqa: E402

W, H = 76, 92
SOIL = {"base": "dirt_block", "veins": [], "pockets": [("stone_block", 12, 3, "any")]}


def walk(start, end, seed, wobble=0.5, bias=0.4):
    rng = random.Random(seed)
    x, y = start
    ex, ey = end
    heading = math.atan2(ey - y, ex - x)
    path = []
    steps = 0
    while abs(x - ex) + abs(y - ey) > 1 and steps < 600:
        steps += 1
        path.append((x, y))
        goal = math.atan2(ey - y, ex - x)
        heading += bias * math.atan2(math.sin(goal - heading), math.cos(goal - heading))
        heading += rng.uniform(-wobble, wobble)
        x += int(round(math.cos(heading)))
        y += int(round(math.sin(heading)))
    path.append((ex, ey))
    return path


def build():
    b = ZoneBuilder("scene_ant_colony", W, H, base_tile="cave_floor", name="Ant colony")
    rng = random.Random(7)
    nx = 22                                                  # nest column (left half)
    ent = (nx, H - 2)
    queen = (nx, 16)

    shaft = walk(ent, queen, seed=1, wobble=0.7, bias=0.16)
    chambers = [(nx - 12, 34, 5, "eggs"), (nx + 9, 44, 4, "brood"),
                (nx - 13, 22, 4, "food"), (nx + 11, 26, 4, "food")]
    branches = [walk(shaft[len(shaft) * (i + 1) // (len(chambers) + 1)], (c[0], c[1]),
                     seed=10 + i, wobble=0.55) for i, c in enumerate(chambers)]

    # the BIG tunnel from the nest east into a mushroom cavern (right half)
    cav = (W - 16, 40)
    big = walk((nx + 11, 26), (cav[0] - 8, cav[1]), seed=30, wobble=0.4, bias=0.5)

    carved = set()
    for path in [shaft] + branches:
        for (x, y) in path:
            for dx in (-1, 0, 1) if path is shaft else (0,):
                if b.in_bounds(x + dx, y):
                    carved.add((x + dx, y))
    for (x, y) in big:                                       # big tunnel is wider (3)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if b.in_bounds(x + dx, y + dy):
                    carved.add((x + dx, y + dy))

    carved |= carve_cavern(b, queen[0], queen[1], shape="blob", size=5, seed=2)
    for (cx, cy, sz, _) in chambers:
        carved |= carve_cavern(b, cx, cy, shape="blob", size=sz, seed=cx)
    mushroom_cav = carve_cavern(b, cav[0], cav[1], shape="blob", size=13, seed=40)
    carved |= mushroom_cav

    for x in range(ent[0] - 1, ent[0] + 2):                  # surface entrance pocket for the mound
        for y in range(ent[1] - 1, H):
            if b.in_bounds(x, y):
                carved.add((x, y))

    fill_solid(b, carved, SOIL, seed=3)

    mx, my = ent[0] - 1, ent[1]
    if all((mx + dx, my + dy) in carved and b.is_free(mx + dx, my + dy)
           for dx in range(2) for dy in range(2)):
        b.place_occupant("ant_mound", mx, my, surface=None)

    ex0, ey0 = chambers[0][0], chambers[0][1]                # egg clutches in the egg chamber
    for (dx, dy) in [(-1, 0), (1, 0), (0, 1), (0, -1), (0, 0)]:
        if b.in_bounds(ex0 + dx, ey0 + dy) and b.is_free(ex0 + dx, ey0 + dy):
            b.place_occupant("ant_eggs", ex0 + dx, ey0 + dy, surface=None)

    mbag = [k for k, n in [("mushroom_glow", 6), ("mushroom_blue", 5), ("mushroom_brown", 4),
                           ("mushroom_cluster", 4), ("mushroom_morel", 3), ("mushroom_bracket", 2),
                           ("cave_moss", 5)] for _ in range(n)]
    mcells = [c for c in mushroom_cav if b.is_free(*c)]
    rng.shuffle(mcells)
    placed = []
    for (x, y) in mcells:
        if rng.random() > 0.3:
            continue
        if any(abs(x - p) <= 1 and abs(y - q) <= 1 for p, q in placed):
            continue
        if b.place_occupant(rng.choice(mbag), x, y, surface=None):
            placed.append((x, y))

    def ant_file(path, every):
        for i, (x, y) in enumerate(path):
            if i % every == 0:
                b.place_bug("ant_worker", x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), scale=2.2)
    ant_file(shaft, 2)
    for br in branches:
        ant_file(br, 3)
    ant_file(big, 4)
    b.place_bug("ant_queen", queen[0], queen[1], scale=3.0)
    for (cx, cy, _, _) in chambers:
        b.place_bug("ant_worker", cx + 0.5, cy + 0.3, scale=2.0)

    def chain(parts, x, y, dx, dy, step=0.7, scale=1.5):     # assemble a segmented bug from pieces
        for i, p in enumerate(parts):
            b.place_bug(p, x + dx * step * i, y + dy * step * i, scale=scale)
    chain(["centipede_head_a", "centipede_body_a", "centipede_body_a", "centipede_body_a",
           "centipede_tail_a"], nx + 14, 27, 1, 0.2)
    chain(["millipede_head_a"] + ["millipede_body_a"] * 6 + ["millipede_tail_a"],
          cav[0] - 4, cav[1] + 4, 0.3, 1)

    b.spawn = [ent[0], H - 3]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_ant_colony.png"))
    render_builder(b, out, scale=6)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
