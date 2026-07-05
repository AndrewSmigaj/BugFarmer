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
    it, flower gardens ringing the south + east (nectar for the hives), Maren at the apiary gate."""
    # The cottage (15×12 four-room home) sits NW, its modest yard facing south.
    place_cottage(b, ox + 2, oy + 24, npc=None, yard_style="modest")

    # THE APIARY — a fenced work-yard: the four hive tiers IN A ROW (the rows rule: this is a
    # working farm, not wild clutter), the extractor + wine rack + barrels along the north fence.
    ax0, ay0, ax1, ay1 = ox + 24, oy + 20, ox + 50, oy + 38
    fence_rect(b, ax0, ay0, ax1, ay1, gate=(ax0 + 13, ay0))
    for i, hive in enumerate(["beehive_basic", "beehive_basic", "beehive_medium",
                              "beehive_large", "beehive_deluxe"]):
        b.place_occupant(hive, ax0 + 3 + i * 5, ay0 + 6)
    b.place_occupant("honey_extractor", ax0 + 2, ay1 - 4)      # 2×2, against the north fence
    b.place_occupant("wine_rack", ax0 + 6, ay1 - 3)
    b.place_occupant("barrel", ax0 + 8, ay1 - 3)
    b.place_occupant("crate", ax0 + 9, ay1 - 4)
    b.place_occupant("compost_bin", ax1 - 3, ay1 - 3)
    b.place_occupant("lamp_post", ax0 + 11, ay0 + 2)

    # Maren (the SHOP vendor occupant) works beside the gate; sign + bench out front.
    b.place_occupant("beekeeper", ax0 + 15, ay0 + 1)
    b.place_occupant("signpost", ax0 + 11, ay0 - 2)
    b.place_occupant("bench", ax0 + 16, ay0 - 2)

    # THE NECTAR ENGINE — flower gardens ringing the apiary, DENSE (these become the ForagePools
    # the colonies live on — flower density IS the honey economy), plus a few inside the yard.
    common = ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "clover", "dandelion"]
    rarer = ["lavender", "chamomile", "poppy"]
    flower_patch(b, ox + 20, oy + 2, ox + 52, oy + 16, common + rarer, 52, seed=11)
    flower_patch(b, ox + 2, oy + 2, ox + 18, oy + 20, common, 28, seed=12)
    flower_patch(b, ax1 + 1, ay0 + 2, min(ax1 + 8, b.W - 2), ay1, common, 16, seed=13)
    flower_patch(b, ax0 + 2, ay0 + 9, ax1 - 2, ay1 - 6, common, 8, seed=14)  # in-yard, between rows
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
