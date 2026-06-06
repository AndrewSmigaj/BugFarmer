#!/usr/bin/env python3
"""Scene — MINING CAMP: the N->S rail track descends into a cleared cavern that's the miners' camp,
with tunnels leading out. Campfire + cooking spit, a second campfire, log seats, tents, crates/tools,
a mine cart on the track, ore sacks/sluice, miners, and a custom camp sign.
Renders to tools/_generated/previews/underground/scene_underground_mining_camp.png.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                       # noqa: E402
from render import render_builder                         # noqa: E402
from features.cave import carve_tunnel, carve_cavern, fill_solid  # noqa: E402

W, H = 56, 60
ORE = {"base": "stone_block",
       "veins": [("ore_copper_block", 6, 3, 5), ("ore_coal_block", 6, 3, 5), ("ore_iron_block", 3, 2, 4)],
       "pockets": [("dirt_block", 8, 4, "top"), ("hard_stone_block", 3, 3, "bottom")]}


def build():
    b = ZoneBuilder("scene_underground_mining_camp", W, H, base_tile="cave_floor", name="Mining camp")
    rng = random.Random(9)
    rx = W // 2
    cav_y = 24

    # big camp cavern + the descending rail tunnel + tunnels out
    cavern = carve_cavern(b, rx, cav_y, shape="blob", size=15, seed=1)
    rail = carve_tunnel(b, (rx, H - 2), (rx, cav_y + 6), style="straight", width=5)
    outs = set()
    outs |= carve_tunnel(b, (rx - 8, cav_y), (1, cav_y - 4), style="natural", width=2, seed=2)   # west
    outs |= carve_tunnel(b, (rx + 8, cav_y), (W - 2, cav_y + 3), style="natural", width=2, seed=3)  # east
    outs |= carve_tunnel(b, (rx, cav_y - 9), (rx + 4, 1), style="natural", width=2, seed=4)       # south
    carved = cavern | rail | outs

    fill_solid(b, carved, ORE, seed=5)

    # rail down the track + wood-block supports flanking it
    for y in range(cav_y + 6, H - 1):
        if b.is_free(rx, y):
            b.place_occupant("mine_rail", rx, y, surface=None, reserve=False)
    for y in range(cav_y + 8, H - 2, 6):
        for sx in (rx - 2, rx + 2):
            if (sx, y) in carved and b.is_free(sx, y):
                b.place_occupant("wall_wood", sx, y, surface=None)

    def free_fp(oid, x, y):
        fw, fh = b.footprint(oid)
        return all((x + dx, y + dy) in carved and b.is_free(x + dx, y + dy)
                   for dx in range(fw) for dy in range(fh))

    def put(oid, x, y):
        if free_fp(oid, x, y):
            b.place_occupant(oid, x, y, surface=None)
            return True
        return False

    # camp sign where the track enters the cavern; a mine cart on the track
    put("sign_camp", rx + 3, cav_y + 5)
    put("mine_cart", rx - 1, cav_y + 6)

    # two fires with log seats around them (the social heart of the camp)
    put("campfire_spit", rx - 6, cav_y)
    for s in [(rx - 8, cav_y - 1), (rx - 8, cav_y + 1), (rx - 4, cav_y - 1), (rx - 4, cav_y + 1)]:
        put("log_seat", *s)
    put("campfire", rx + 6, cav_y + 2)
    for s in [(rx + 5, cav_y + 3), (rx + 7, cav_y + 3)]:
        put("log_seat", *s)

    # tents along the back (north) wall of the cavern
    for tx in (rx - 9, rx - 3, rx + 4):
        put("tent", tx, cav_y - 6)

    # work area: crates, barrels, ore sacks, sluice, tools, powder
    for oid, x, y in [("ore_sluice", rx + 7, cav_y - 3), ("tool_rack", rx - 10, cav_y + 3),
                      ("crate", rx - 9, cav_y + 4), ("barrel", rx - 8, cav_y + 4),
                      ("ore_sack", rx + 8, cav_y), ("ore_sack", rx + 9, cav_y),
                      ("powder_keg", rx + 9, cav_y + 3), ("ore_pile", rx - 2, cav_y + 4),
                      ("mining_bucket", rx + 2, cav_y + 4)]:
        put(oid, x, y)

    # torches + a lantern around the camp walls
    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved
    faces = [(x, y) for (x, y) in cavern if b.is_free(x, y)
             and any(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for c in rng.sample(faces, k=min(7, len(faces))):
        b.place_occupant("torch_wall", *c, surface=None)
    put("lamp_post", rx + 2, cav_y)

    # miners around the camp
    b.place_player("miner_down", rx - 6, cav_y - 2)     # by the cooking fire
    b.place_player("miner_left", rx - 1, cav_y + 7)     # by the cart
    b.place_player("miner_down", rx + 6, cav_y + 4)     # by the second fire

    b.spawn = [rx, H - 3]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "underground",
                                       "scene_underground_mining_camp.png"))
    render_builder(b, out, scale=6)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
