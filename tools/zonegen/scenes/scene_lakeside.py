#!/usr/bin/env python3
"""Scene — LAKE & FISHING DOCK: a big lake filling the south, a sandy beach, and the fishing store set
BACK on the north shore with a stone PATH running down to a dock that reaches out over the water (a
moored boat at the end). The store is arranged like a real shop — shelving + goods in rows, a counter
with the shopkeeper set behind it, nautical decor (ship wheel, anchor) and a fishing pole on the floor.

Authored as a TEXT GRID (features.tilemap) so the layout is reasoned + linted in text, not by eyeballing.
Renders via registry.py to tools/_generated/previews/tests/scene_lakeside.png.
"""
import os
import sys
import math
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.tilemap import stamp, dump                              # noqa: E402

W, H = 28, 34

# fishing store — a SHOP (shelving, goods in rows, the merchant 2 cells behind the counter, nautical
# decor + a fishing pole) over a back SUPPLY room (fish crates, barrels, crates), an internal door between.
STORE = """
WWWWWWWWWWW
Wf.b.c.b.fW
Wc.f...f.cW
WWWWWDWWWWW
WSSSS.SSSSW
Wfbh...afbW
W....M....W
W.........W
W....C....W
W.r.....c.W
Wb.f...f.bW
WWWWWDWWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), "S": ("occ", "shop_shelving"),
       "f": ("occ", "fish_crate"), "b": ("occ", "barrel"), "c": ("occ", "crate"),
       "h": ("occ", "ship_wheel"), "a": ("occ", "anchor_decor"), "M": ("npc", "merchant_down"),
       "C": ("occ", "counter"), "r": ("occ", "fishing_pole"), ".": ("floor",)}


def _safe(b, oid, x, y, **k):
    fw, fh = b.footprint(oid)
    return b.place_occupant(oid, x, y, **k) if all(b.is_free(x + dx, y + dy)
                                                   for dx in range(fw) for dy in range(fh)) else False


def _water_put(b, oid, x, y, **k):                  # stand an object in the water (un-reserve its footprint)
    fw, fh = b.footprint(oid)
    if not all(b.in_bounds(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
        return False
    for dx in range(fw):
        for dy in range(fh):
            b.reserved[y + dy][x + dx] = False
    return b.place_occupant(oid, x, y, surface="water", **k)


def place_boat_store(b, ox, oy, *, dock_len=14):
    """Stamp the 2-room boat store (SW corner ox,oy; door south at ox+5) + the fish sign, then run a
    2-wide path/dock SOUTH from the door — stone on land, bridge_wood over water (un-reserved) — with
    mooring posts, a lantern and a moored boat at the dock's end. The caller lays the lake to the south.
    Composable into the village (`place_boat_store`)."""
    stamp(b, STORE, LEG, ox=ox, oy=oy)
    dx0, dx1 = ox + 4, ox + 5                        # the door is at ox+5
    b.place_occupant("sign_fish_board", ox + 1, oy - 1, surface="grass")
    _safe(b, "anchor_decor", ox + 8, oy - 1, surface="grass")
    end = None
    for y in range(oy - 1, oy - 1 - dock_len, -1):
        if not b.in_bounds(dx1, y):
            break
        for x in (dx0, dx1):
            if not b.in_bounds(x, y):
                continue
            if b.surface[y][x] == "water":
                b.set_ground(x, y, "bridge_wood", surface="path"); b.reserved[y][x] = False
                end = y
            elif b.is_free(x, y):
                b.set_ground(x, y, "stone_path", surface="path")
    if end is not None:                              # dock furniture over the water
        for y in range(oy - 3, end, -3):
            _water_put(b, "mooring_post", dx0 - 1, y); _water_put(b, "mooring_post", dx1 + 1, y)
        _water_put(b, "lantern", dx1 + 1, (oy - 2 + end) // 2)
        _water_put(b, "boat", dx1 + 1, end)          # moored at the dock's south end
    return (ox, oy)


def build():
    b = ZoneBuilder("scene_lakeside", W, H, base_tile="grass", name="Lake & fishing dock")
    rng = random.Random(7)

    # --- BIG LAKE (south + edges) with a wavy shore + a 2-cell SAND beach ---
    shore_y = {}
    for x in range(W):
        s = 12 + int(1.6 * math.sin(x * 0.5)) + rng.choice([0, 0, 1])
        shore_y[x] = s
        for y in range(0, s):
            b.set_ground(x, y, "water_deep" if y < s - 3 else "water_shallow", surface="water")
            b.reserve(x, y, surface="water")
        for y in (s, s + 1):
            if b.in_bounds(x, y):
                b.set_ground(x, y, "sand", surface="grass")

    # --- STORE on the north shore + its path/dock out over the water ---
    place_boat_store(b, 9, 20)

    # --- MARSH PLANTS + reeds at the shoreline, lily pads on open water ---
    for x in range(0, W, 2):
        s = shore_y[x]
        if x in (13, 14):
            continue                                 # keep the dock mouth clear
        if rng.random() < 0.6:                        # marsh/reeds grow IN the shallow water at the edge
            _water_put(b, rng.choice(["marsh_plant", "marsh_plant", "reeds"]), x, max(0, s - 1))
    for (x, y) in [(3, 6), (6, 9), (22, 7), (24, 10), (5, 3), (20, 5), (2, 11), (25, 4)]:
        b.place_decor("lily_pad", x, y, scale=0.8)

    b.spawn = [14, 16]                               # on the path
    return b


if __name__ == "__main__":
    import importlib
    sys.path.insert(0, HERE)
    reg = importlib.import_module("registry") if os.path.exists(os.path.join(ZG, "registry.py")) else None
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_lakeside.png"))
    render_builder(b, out, scale=8)
    print(dump(b, 9, 20, 19, 28))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
