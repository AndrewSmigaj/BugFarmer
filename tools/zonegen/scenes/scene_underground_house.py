#!/usr/bin/env python3
"""Scene — UNDERGROUND HOME: the scene1 idea, but dug into the rock. A stone-walled, stone-floored
house carved into a cavern hollow, with a mined entrance tunnel from the south, a little cave "yard"
(crystals, glow mushrooms, a pool, a stone bench), ore veins in the surrounding rock, and torches.

Shows that the house composer + collections work with non-wood materials and a cave surround.
Renders to tools/_generated/previews/scene_underground_house.png.
Run: python3 tools/zonegen/scenes/scene_underground_house.py
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                    # noqa: E402
from features.house import place_house, styled_rooms, bathroom_template  # noqa: E402
from features.cave import carve_tunnel, fill_solid                   # noqa: E402
from features.house import row_house, bbox                            # noqa: E402

W, H = 52, 44
ORE = {"base": "stone_block",
       "veins": [("ore_copper_block", 5, 3, 5), ("ore_coal_block", 5, 3, 5),
                 ("ore_iron_block", 3, 2, 4), ("ore_silver_block", 2, 2, 3)],
       "pockets": [("dirt_block", 3, 3, "top"), ("hard_stone_block", 2, 3, "bottom")]}


def _ellipse(cx, cy, rx, ry):
    return {(x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0}


PREVIEW = "examples/buildings"
SCALE = 3


def build():
    b = ZoneBuilder("scene_underground_house", W, H, base_tile="cave_floor", name="Underground home")
    rng = random.Random(5)

    # stone house (3-room bar) DUG INTO the rock
    specs, front = row_house(12, 16)
    # the full-home standard: even underground, a home has a bathroom (a stem
    # off the middle room, north)
    specs = specs + [("bathroom", (12 + 11, 16 + 9, 12 + 19, 16 + 16), bathroom_template)]
    bx0, by0, bx1, by1 = bbox(specs)
    door_x = (bx0 + bx1) // 2

    # carved = the house's OWN footprint (so rock sits FLUSH against its outer walls — no gap ring),
    # plus a SMALL front clearing south of the door, a little pond, and the entrance tunnel.
    from features.cave import place_pool
    house_cells = {(x, y) for x in range(bx0, bx1 + 1) for y in range(by0, by1 + 1)}
    clearing = {(x, y) for x in range(door_x - 4, door_x + 5) for y in range(by0 - 6, by0)
                if 0 <= x < W and 0 <= y < H}
    tunnel = carve_tunnel(b, (door_x, 1), (door_x, by0 - 6), style="natural", width=2, seed=3)
    carved = house_cells | clearing | tunnel

    rooms = styled_rooms(specs, collection="basic")          # stone walls/floors, rugs + furniture
    place_house(b, rooms, front=front, floor="stone_floor", wall="wall_stone",
                interior_door="door_square", front_door="door_square", windows=False)

    fill_solid(b, carved, ORE, seed=5)                       # rock + light ore, flush around the house

    pool = place_pool(b, door_x - 3, by0 - 3, 2, 2, carved, seed=1)   # little pond in the clearing
    for y in range(1, by0):                                  # stone path: door -> tunnel mouth
        if b.in_bounds(door_x, y):
            b.set_ground(door_x, y, "stone_path", surface="path")

    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved

    # dressing in the front clearing only (house interior is furnished by the templates)
    clear_open = [(x, y) for (x, y) in (clearing | tunnel) if (x, y) not in pool
                  and b.is_free(x, y) and b.surface[y][x] != "path"]
    faces = [c for c in clear_open if any(is_rock(c[0] + dx, c[1] + dy)
             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for c in rng.sample(faces, k=min(5, len(faces))):
        if b.is_free(*c):
            b.place_occupant("torch_wall", *c, surface=None)
    bag = [k for k, n in [("mushroom_glow", 5), ("cave_moss", 5), ("rubble", 3),
                          ("mushroom_blue", 3)] for _ in range(n)]
    rng.shuffle(clear_open)
    placed = []
    for (x, y) in clear_open:
        if rng.random() > 0.18 or not b.is_free(x, y):
            continue
        if any(abs(x - p) <= 1 and abs(y - q) <= 1 for p, q in placed):
            continue
        if b.place_occupant(rng.choice(bag), x, y, surface=None):
            placed.append((x, y))

    b.place_bug("firefly", door_x + 0.5, by0 - 3.0, scale=0.6)
    b.spawn = [door_x, 2]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
