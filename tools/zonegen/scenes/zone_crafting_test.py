#!/usr/bin/env python3
"""CRAFTING test zone (48x48): a flat grass yard with one of every Stage-1 craft station and a
rack of storage containers, so crafting + containers can be exercised end to end. Stock yourself
with materials via the F8 debug "give crafting kit" button, then:

  - workbench / stonecutter / anvil (fast): pick a recipe, Craft -> output grid -> Get all
  - furnace (slow): queue iron_bar -> the bar fills over ~20s -> collect
  - chest / barrel (generic) + wardrobe (clothing) / bookshelf (book) / fridge (food, filtered):
    double-/shift-click a stack to move it; a filtered container rejects non-matching items
  - compost_bin: still works (deterministic food path — untouched by crafting)

  python3 tools/zonegen/scenes/zone_crafting_test.py   # build + save + lint
  python3 tools/world/view_world.py crafting_test            # pixel overview
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402

W = H = 64


def build(zone_id="crafting_test"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Crafting Test", seed=7)

    # A stone-floor working area under the stations (cosmetic; reads as a workshop).
    Z.fill_ground(6, 20, 40, 32, "stone_floor")

    # --- Row 1: craft stations (the Stage-1 set with recipes + a couple for show) ---
    Z.place_occupant("workbench", 8, 22)      # 2x1 — torch, furniture, sword_wood
    Z.place_occupant("furnace", 12, 22)       # 2x2 — {refined ore}+coal -> bars
    Z.place_occupant("anvil", 16, 22)         # 2x1 — metal tools/weapons (<=iron)
    Z.place_occupant("stonecutter", 20, 22)   # 2x1 — brick, wall_stone
    Z.place_occupant("sawmill", 24, 22)       # 2x1 — plank, furniture
    Z.place_occupant("loom", 28, 22)          # 2x1 — thread/cloth

    # --- Row 1b: the mining refine chain + gem cutter + forge + bug extractor (this pass) ---
    Z.place_occupant("rock_crusher", 8, 19)   # 2x1 — {metal}_ore -> {metal}_paydirt
    Z.place_occupant("ore_sluice", 12, 19)    # 2x1 — {metal}_paydirt -> refined_{metal}_ore
    Z.place_occupant("forge", 16, 19)         # 2x1 — bronze/steel + high-tier tools/weapons
    Z.place_occupant("gem_cutter", 20, 19)    # 2x1 — raw gem -> cut gem
    Z.place_occupant("bug_extractor", 24, 19) # dead_<bug> -> chitin/leather
    Z.place_occupant("mannequin_white", 28, 19)  # outfit display (right-click to dress)

    # --- Row 2: storage containers (generic + filtered) ---
    Z.place_occupant("chest_wood", 8, 26)     # 2x1 — generic 24
    Z.place_occupant("chest_iron", 12, 26)    # 2x1 — generic 30
    Z.place_occupant("wardrobe", 16, 26)      # 1x1 — filter: clothing
    Z.place_occupant("bookshelf", 18, 26)     # 2x1 — filter: book
    Z.place_occupant("barrel", 22, 26)        # 1x1 — generic 12
    Z.place_occupant("fridge", 24, 26)        # 2x1 — filter: food

    # The compost bin (deterministic food path) — proves crafting left it untouched.
    Z.place_occupant("compost_bin", 30, 26)

    Z.spawn = [22, 18]  # south of the rows, facing the stations
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 64x64 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    print("lint:", Z.lint() or "clean")
