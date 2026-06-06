#!/usr/bin/env python3
"""Scene — CATALOG / showroom: lays the newly-added content out on a floor grid so every new sprite
appears in a scene (catalog coverage + visual QA). Grouped in bands by kind. No gameplay meaning.
Renders to tools/_generated/previews/scene_catalog.png.
Run: python3 tools/zonegen/scenes/scene_catalog.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from render import render_builder                # noqa: E402

GROUPS = [
    ("furniture", ["ottoman", "chaise_lounge", "vanity", "kitchen_island", "bunk_bed", "throne",
                   "bar_cart", "bathtub", "stool_stone", "bench_stone"]),
    ("decor", ["statue_bug", "suit_of_armor", "globe", "gramophone", "easel", "telescope",
               "ore_pile", "mining_bucket"]),
    ("mining", ["tool_rack", "wheelbarrow", "powder_keg", "mine_cart", "mine_support", "tnt",
                "ore_sack", "mine_rail"]),
    ("cave", ["crystal_quartz", "rubble", "geode", "hard_stone_block", "ore_tin_block",
              "mushroom_blue", "mushroom_cluster", "mushroom_morel", "mushroom_bracket",
              "mushroom_inkcap"]),
]
COLS = 6
PAD, STEP = 2, 4


def build():
    rows = sum((len(ids) + COLS - 1) // COLS for _, ids in GROUPS)
    W = PAD * 2 + COLS * STEP
    H = PAD * 2 + (rows + len(GROUPS)) * STEP
    b = ZoneBuilder("scene_catalog", W, H, base_tile="wood_floor", name="Catalog")
    y = H - PAD - 2
    for _, ids in GROUPS:
        for i, oid in enumerate(ids):
            if i and i % COLS == 0:
                y -= STEP
            x = PAD + (i % COLS) * STEP
            b.place_occupant(oid, x, y, surface=None)
        y -= STEP + 1                                    # gap between groups
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_catalog.png"))
    render_builder(b, out, scale=8)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
