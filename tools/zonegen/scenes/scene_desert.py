#!/usr/bin/env python3
"""Scene — DESERT (drier, fits the world; no palms). A dirt road with an old INN (neon sign) and, up
the road, a WEATHER OUTPOST (brick walls / stone floor, console + desk inside, antenna + radar + a
WINDMILL outside, hand pump + water bucket). Scattered cacti, dead bushes, tumbleweeds, cow skulls,
sandstone formations, mineable rock/sand piles, scorpions, and a small OASIS.
Renders to tools/_generated/previews/scene_desert.png.
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
from features.terrain import pond, hpath         # noqa: E402
from features.room import place_room             # noqa: E402

W, H = 78, 56


def build():
    b = ZoneBuilder("scene_desert", W, H, base_tile="sand", name="Desert", biome="desert")
    rng = random.Random(6)

    # --- the road across the map (dirt) ---
    for y in (27, 28, 29):
        hpath(b, 0, W - 1, y, tile="dirt")

    # --- old INN (south of the road, left) — brick/wood, neon sign out front ---
    inn = place_room(b, 5, 16, 19, 26, floor="wood_floor", wall="wall_brick",
                     door="door_wood", door_side="bottom")
    ix0, iy0, ix1, iy1 = inn
    for oid, x, y in [("counter", ix0, iy1), ("keg", ix0 + 2, iy1), ("table_wood", ix0 + 4, iy0 + 2),
                      ("chair_wood", ix0 + 3, iy0 + 2), ("bed_basic", ix1 - 1, iy0),
                      ("lamp_floor", ix1, iy1)]:
        if b.in_bounds(x, y) and b.is_free(x, y):
            b.place_occupant(oid, x, y, surface=None)
    b.place_occupant("neon_sign", 12, 14)
    b.place_occupant("sign_inn", 16, 30)

    # --- WEATHER OUTPOST (north of the road, right) — brick/stone, with kit outside ---
    out = place_room(b, 46, 31, 60, 42, floor="stone_floor", wall="wall_brick",
                     door="door_wood", door_side="top")
    ox0, oy0, ox1, oy1 = out
    for oid, x, y in [("weather_console", ox0, oy1), ("desk", ox0 + 3, oy1), ("chair_wood", ox0 + 4, oy0 + 2),
                      ("table_wood", ox1 - 2, oy0 + 2), ("lamp_floor", ox1, oy1)]:
        if b.in_bounds(x, y) and b.is_free(x, y):
            b.place_occupant(oid, x, y, surface=None)
    for oid, x, y in [("antenna", 62, 38), ("radar_dish", 49, 44), ("windmill", 66, 36),
                      ("hand_pump", 44, 40), ("water_bucket", 45, 41), ("sign_weather", 52, 30)]:
        if b.in_bounds(x, y) and b.is_free(x, y):
            b.place_occupant(oid, x, y, surface=None)

    # --- a small OASIS (no palms): pond + reeds + a barrel cactus or two ---
    pond(b, 64, 12, 5, 3, seed=7)
    for (x, y) in [(58, 11), (70, 13), (61, 8)]:
        if b.is_free(x, y):
            b.place_occupant("cactus_barrel", x, y, surface=None)

    # --- mineable rock/sand piles in the open desert (break for rock/ore/sand) ---
    for (cx, cy) in [(10, 42), (30, 10), (34, 44), (70, 48)]:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            x, y = cx + dx, cy + dy
            if b.in_bounds(x, y) and b.is_free(x, y) and rng.random() < 0.8:
                b.place_occupant(rng.choice(["sand_block", "stone_block", "rubble"]), x, y, surface=None)

    # --- a few 2x2 sandstone formations (footprint-checked; scatter is anchor-only) ---
    for (x, y) in [(22, 8), (40, 12), (8, 48), (52, 50)]:
        if all(b.in_bounds(x + dx, y + dy) and b.is_free(x + dx, y + dy)
               for dx in (0, 1) for dy in (0, 1)):
            b.place_occupant("sandstone_formation", x, y, surface=None)

    # --- scattered desert flora & decor (1x1 items) ---
    scatter(b, 0, 0, W - 1, H - 1,
            {"cactus_saguaro": 4, "cactus_prickly": 4, "cactus_barrel": 3, "dead_bush": 5,
             "tumbleweed": 4, "cow_skull": 2, "rubble": 4},
            density=0.10, min_spacing=3, seed=3, surfaces=("grass",))

    # --- scorpions ---
    for (x, y) in [(12, 44), (33, 46), (50, 8), (72, 50)]:
        b.place_bug("scorpion", x + 0.3, y + 0.3, scale=1.4)

    b.spawn = [2, 28]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_desert.png"))
    render_builder(b, out, scale=6)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
