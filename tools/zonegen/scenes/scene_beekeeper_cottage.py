#!/usr/bin/env python3
"""Scene — MAREN'S BEE FARM (the Bee Meadow's heart): the beekeeper's full-home cottage, a fenced
APIARY with the four hive-box tiers in a working row + the honey extractor + wine rack + barrel
clutter, Maren herself (the shop NPC) at the gate, a signpost out front, and the flower-garden
ring that IS the farm's nectar engine. Adapts scene_beefarm_woods' apiary idea onto the real
cottage piece + the shop vendor.

`place_bee_farm(b, ox, oy)` is the composable piece (SW anchor). Renders to
tools/_generated/previews/zones/bee_meadow_20/scenes/beekeeper_cottage.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from features.yard import fence_rect             # noqa: E402
from features.garden import flower_patch         # noqa: E402
from scene_cottage import place_cottage          # noqa: E402


def place_bee_farm(b, ox, oy):
    """The bee farm piece (~54 wide × 42 tall, SW anchor ox,oy): cottage NW, apiary yard east of
    it, flower gardens ringing the south + east (nectar for the hives), Maren at the apiary gate.
    Inside the apiary everything reads as a WORKPLACE: a dirt working-strip under the hive row,
    a worn path from the gate to the extraction corner, cultivated flower beds IN ROWS (the
    kept garden vs the wild ring outside), and the keeper's kit (waterer, shelf, table)."""
    # The cottage (15×12 four-room home) sits NW, its modest yard facing south.
    place_cottage(b, ox + 2, oy + 24, npc=None, yard_style="modest")

    # THE APIARY — a fenced work-yard.
    ax0, ay0, ax1, ay1 = ox + 24, oy + 20, ox + 50, oy + 38
    fence_rect(b, ax0, ay0, ax1, ay1, gate=(ax0 + 13, ay0))

    # Working ground FIRST (ground under later occupants): the dirt strip the hive row stands
    # on, and the worn path gate → strip → extraction corner.
    for y in range(ay0 + 5, ay0 + 8):
        for x in range(ax0 + 2, ax0 + 25):
            if b.is_free(x, y) and b.surface[y][x] == "grass":
                b.set_ground(x, y, "dirt")
    for y in range(ay0 + 1, ay0 + 6):                       # gate → strip
        for x in (ax0 + 13, ax0 + 14):
            if b.is_free(x, y) and b.surface[y][x] == "grass":
                b.set_ground(x, y, "dirt")
    for x in range(ax0 + 3, ax0 + 13):                      # strip → work corner (north-west)
        y = ay0 + 8 + (x - ax0 - 3) // 2
        if b.in_bounds(x, ay1 - 5) and b.is_free(ax0 + 3, y):
            pass
    for y in range(ay0 + 8, ay1 - 3):                       # a straight worn lane up the west side
        for x in (ax0 + 3, ax0 + 4):
            if b.is_free(x, y) and b.surface[y][x] == "grass":
                b.set_ground(x, y, "dirt")

    # The hive row ON the strip (tiers left→right — the working progression).
    for i, hive in enumerate(["beehive_basic", "beehive_basic", "beehive_medium",
                              "beehive_large", "beehive_deluxe"]):
        b.place_occupant(hive, ax0 + 3 + i * 5, ay0 + 6)
    # The keeper's kit: a bee waterer by the hives (pebbled water dish — real apiary practice).
    b.place_occupant("bee_waterer", ax0 + 16, ay0 + 8)

    # THE EXTRACTION CORNER (NW, tight against the fence, everything in one workline):
    # extractor → work table → honey shelf → wine rack, crates/barrel behind.
    b.place_occupant("honey_extractor", ax0 + 2, ay1 - 4)   # 2×2
    b.place_occupant("table_wood", ax0 + 5, ay1 - 4)
    b.place_occupant("honey_shelf", ax0 + 7, ay1 - 4)
    b.place_occupant("wine_rack", ax0 + 9, ay1 - 4)
    b.place_occupant("crate", ax0 + 6, ay1 - 2)
    b.place_occupant("barrel", ax0 + 8, ay1 - 2)
    b.place_occupant("compost_bin", ax1 - 3, ay1 - 3)
    b.place_occupant("lamp_post", ax0 + 11, ay0 + 2)

    # CULTIVATED flower beds IN ROWS (human-made = rows; the kept nectar garden): two packed
    # rows north of the hive strip — contiguous alternating blooms so they READ as planted
    # beds at zoom, not scatter.
    bed = ["flower_red", "flower_yellow", "flower_blue"]
    for r, y in enumerate((ay0 + 10, ay0 + 12)):
        for i, x in enumerate(range(ax0 + 8, ax0 + 22)):
            if b.is_free(x, y):
                b.place_occupant(bed[(i + r) % len(bed)], x, y)

    # Maren (the SHOP vendor occupant) works beside the gate; sign + bench out front.
    b.place_occupant("beekeeper", ax0 + 15, ay0 + 1)
    b.place_occupant("signpost", ax0 + 11, ay0 - 2)
    b.place_occupant("bench", ax0 + 17, ay0 - 3)

    # Between cottage and apiary: two blossoming fruit trees (the orchard hint — more forage).
    for tx, ty, t in [(ox + 19, oy + 30, "tree_cherry"), (ox + 21, oy + 25, "tree_apple")]:
        if b.is_free(tx, ty):
            b.place_occupant(t, tx, ty)

    # THE WILD CONTRAST: a wild hive hanging in an oak just OUTSIDE the north-east fence —
    # the kept boxes inside, the free colony without.
    if b.is_free(ax1 + 2, ay1 + 1):
        b.place_occupant("tree_oak", ax1 + 2, ay1 + 1)
    if b.is_free(ax1 + 4, ay1):
        b.place_occupant("bee_hive_wild", ax1 + 4, ay1)

    # The keeper's LANE: a worn dirt line from the cottage yard over to the apiary gate
    # front (Maren walks it a hundred times a day).
    for lx in range(ox + 14, ax0 + 12):
        ly = oy + 19 + (1 if lx % 9 == 0 else 0)
        if b.in_bounds(lx, ly) and b.is_free(lx, ly) and b.surface[ly][lx] == "grass":
            b.set_ground(lx, ly, "dirt", surface="path")

    # THE NECTAR ENGINE — the WILD flower meadow ringing the apiary (scattered, vs the beds'
    # rows), dense: these become the ForagePools the colonies live on.
    common = ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "clover", "dandelion"]
    rarer = ["lavender", "chamomile", "poppy"]
    flower_patch(b, ox + 20, oy + 2, ox + 52, oy + 16, common + rarer, 52, seed=11)
    flower_patch(b, ox + 2, oy + 2, ox + 18, oy + 20, common, 28, seed=12)
    flower_patch(b, ax1 + 1, ay0 + 2, min(ax1 + 8, b.W - 2), ay1, common, 16, seed=13)

    # LIVING DRESSING (render-only): the working bees over the beds and boxes, butterflies
    # in the wild ring — the previews should hum.
    import random as _r
    _rng = _r.Random(59)
    for _ in range(7):
        b.place_bug("honeybee", ax0 + _rng.uniform(3, 24), ay0 + _rng.uniform(5, 14), scale=1.0)
    b.place_bug("honeybee", ax1 + 3.5, ay1 + 0.5, scale=1.0)   # at the wild hive
    for _ in range(3):
        b.place_bug("butterfly_common", ox + _rng.uniform(22, 50), oy + _rng.uniform(4, 15), scale=1.0)
    return (ax0, ay0, ax1, ay1)


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_beekeeper_cottage", 62, 46, base_tile="grass", name="Maren's bee farm",
                    biome="meadow")
    place_bee_farm(b, 2, 2)
    b.spawn = [30, 10]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
