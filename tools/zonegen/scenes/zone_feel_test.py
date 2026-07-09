#!/usr/bin/env python3
"""FEEL TEST zone (64x64) — the fast iteration vehicle for the look-&-feel batch (Plan 2).

Surface variety so every improvement shows in one Play session:
  - flowers / bushes / tall-grass / ferns (wind sway + blob shadows)
  - a crop bed (wind on crops)
  - trees (wind canopy + chop feedback + blob shadows)
  - a pond + shore reeds (water overhaul + reed bob)
Ambient dust is runtime (no zone data). NPC + emote added with P2-7.

  python3 tools/zonegen/scenes/zone_feel_test.py       # build + save + lint
  python3 tools/world/view_world.py feel_test          # PNG minimap
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                 # noqa: E402
from features.scatter import scatter                # noqa: E402
from features.garden import crop_bed                # noqa: E402
from features import terrain                        # noqa: E402

W = H = 64


def build(zone_id="feel_test"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Feel Test", seed=11)

    # A pond in the SW (water tiles → water overhaul), with shore reeds (reed sway).
    terrain.pond(Z, 16, 16, 8, 6, seed=3)
    for (rx, ry) in [(26, 16), (6, 16), (16, 24), (16, 8), (25, 12), (7, 20)]:
        if Z.is_free(rx, ry):
            Z.place_occupant("reeds", rx, ry)

    # Lily pads floating on the pond (vertical bob) + a water_lily bloom. Pond water is reserved,
    # so un-reserve → place → re-reserve (the shipped bee_meadow_20 / fishing_docks pattern).
    for (pid, px, py) in [("lily_pad", 14, 15), ("lily_pad", 18, 16), ("lily_pad", 16, 18),
                          ("lily_pad", 13, 14), ("lily_pad", 19, 13), ("water_lily", 15, 17)]:
        if 0 <= px < W and 0 <= py < H and Z.surface[py][px] == "water":
            Z.reserved[py][px] = False
            Z.place_occupant(pid, px, py, surface="water")
            Z.reserve(px, py, surface="water")

    # Trees (wind canopy + chop feedback + blob shadows) — spread AROUND the spawn (32,32) in every
    # direction so they're immediately findable, spaced so the ~2-tall sprites don't overlap, and kept
    # clear of the SW pond (x8-24,y10-22) and the S crop beds (x34-44,y8-16).
    for (tx, ty) in [(40, 44), (48, 50), (34, 52), (52, 38), (44, 30),
                     (24, 36), (28, 46), (20, 52), (30, 26), (22, 42), (36, 24), (26, 30)]:
        if Z.is_free(tx, ty):
            Z.place_occupant("tree_oak", tx, ty)

    # Two beds side by side to show the crop-wind rule: WHEAT sways (grain stalks), VEGETABLES don't.
    crop_bed(Z, 34, 13, 44, 16, ["plant_wheat"])                                  # sways
    crop_bed(Z, 34, 8, 44, 11, ["plant_tomato", "plant_cabbage", "plant_carrot"])  # still

    # Flowers / bushes / tall grass / ferns across the open grass (wind + blob shadows).
    flora = {"flower_red": 3, "chamomile": 2, "dandelion": 2, "bush": 2, "tall_grass": 4, "fern": 1, "lavender": 1}
    scatter(Z, 28, 20, 63, 63, flora, density=0.12, min_spacing=2, seed=7)
    scatter(Z, 2, 30, 27, 63, flora, density=0.10, min_spacing=2, seed=8)

    Z.spawn = [32, 32]
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")   # save() writes row/col 0,0 — fine for a test zone
    cfg = json.load(open(cfg_path))
    cfg["row"], cfg["col"] = 0, 0
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print(f"saved 64x64 feel_test -> {out} | occupants {len(Z.occ)}")
    print("lint:", Z.lint() or "clean")
