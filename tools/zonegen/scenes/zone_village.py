#!/usr/bin/env python3
"""The full 256x256 `village_21` ZONE: the verified village scene placed in the MIDDLE of a forest
clearing, its main road extended out to the zone edges (so it connects to neighbouring zones), with
the surrounding land filled — a perimeter forest belt, meadow ring, scattered woods and ponds.

Run directly to BUILD + save() the zone to nakama/data/zones/village_21, then view the whole-zone
pixel overview with:  python3 tools/world/view_world.py village_21
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.terrain import lake, forest, rock_patch                 # noqa: E402
from features.scatter import scatter                                  # noqa: E402
from features.garden import flower_patch, crop_bed                    # noqa: E402
import scene_village                                                  # noqa: E402
from scene_ecologist import place_ecologist                           # noqa: E402

FLOWERS = ["flower_red", "flower_blue", "flower_yellow", "poppy", "lavender"]

ZW = ZH = 256


def blit(dst, src, ox, oy):
    """Legacy wrapper — composition is now `ZoneBuilder.blit` (anchor-grouped occupant
    collision, bounds clipping, optional transparency)."""
    dst.blit(src, ox, oy)


def build(zone_id="village_21", vseed=0):
    Z = ZoneBuilder(zone_id, ZW, ZH, base_tile="grass", biome="village", name="Starting Village")

    # 1) VILLAGE scene blitted into the CENTRE (FIRST, so the lakes can flow up to its water)
    vb = scene_village.build()                                        # 120 x 116
    OX, OY = (ZW - vb.W) // 2, (ZH - vb.H) // 2                       # (68, 70)
    blit(Z, vb, OX, OY)

    # 2) LAKES — organic lobed shorelines + beaches (lake(), per trees-and-ponds.md). The HUGE SW lake is
    #    placed AFTER the village and nudged toward it so it CONNECTS to the boat-store's pond — lake()
    #    skips reserved cells, so it flows around the buildings and merges with the existing water.
    lake(Z, 46, 48, 52, seed=(2 + vseed))
    lake(Z, 44, 214, 16, seed=(5 + vseed))
    lake(Z, 226, 58, 14, seed=(6 + vseed))

    # 3) CROSSROADS — extend the streets to all four zone edges (connects to neighbour zones)
    MAINX, COMMY = OX + 58, OY + 59
    for x in (MAINX - 1, MAINX, MAINX + 1):
        for y in list(range(0, OY)) + list(range(OY + vb.H, ZH)):
            if Z.is_free(x, y):
                Z.set_ground(x, y, "stone_path", surface="path")
    for y in (COMMY - 1, COMMY, COMMY + 1):
        for x in list(range(0, OX)) + list(range(OX + vb.W, ZW)):
            if Z.is_free(x, y):
                Z.set_ground(x, y, "stone_path", surface="path")

    def dirt_h(x0, x1, y):
        for xx in range(min(x0, x1), max(x0, x1) + 1):
            for yy in (y, y + 1):
                if Z.is_free(xx, yy):
                    Z.set_ground(xx, yy, "dirt", surface="path")

    def dirt_v(x, y0, y1):
        for yy in range(min(y0, y1), max(y0, y1) + 1):
            for xx in (x, x + 1):
                if Z.is_free(xx, yy):
                    Z.set_ground(xx, yy, "dirt", surface="path")

    # 4) EAST of town: the ECOLOGIST'S cabin (UNFENCED) in a forest, reached by a little DIRT road
    eco = place_ecologist(Z, 206, 150, fenced=False)                 # door faces south at x215, y150
    dirt_h(OX + vb.W - 1, 215, 146); dirt_v(214, 146, 149)           # village E edge -> cabin door
    dirt_v(OX + vb.W - 1, COMMY, 146)                                # tie that dirt road to the E-W street
    forest(Z, 230, 122, 20, 26, density=0.6, seed=(1 + vseed), dirt=False)      # EAST FOREST split into stands
    forest(Z, 233, 184, 20, 28, density=0.6, seed=(3 + vseed), dirt=False)      #   with clearings + a trail
    forest(Z, 201, 150, 13, 16, density=0.55, seed=(7 + vseed), dirt=False)     # a grove hugging the cabin

    # 5) NORTH road -> a DIRT row going EAST into a northern forest stand
    dirt_h(MAINX, 206, 214)
    forest(Z, 220, 222, 30, 28, density=0.58, seed=(2 + vseed), dirt=False)

    # 6) FARMS north of the village (tilled crop fields)
    crop_bed(Z, 80, 196, 96, 206, ["plant_tomato", "plant_corn"])
    crop_bed(Z, 150, 198, 170, 208, ["plant_corn", "plant_tomato"])
    crop_bed(Z, 104, 212, 124, 220, ["plant_tomato", "plant_corn"])

    # 7) WEST of town: large CLEARINGS, patches of forest + flower MEADOWS (above the lake)
    for (cx, cy, rx, ry, sd) in [(26, 150, 16, 20, 3), (48, 196, 15, 17, 4), (20, 232, 13, 15, 5)]:
        forest(Z, cx, cy, rx, ry, seed=sd + vseed)
    for (x0, y0, x1, y1, sd) in [(6, 118, 42, 142, 11), (48, 156, 68, 184, 12), (8, 204, 42, 228, 13),
                                 (186, 54, 214, 82, 22)]:                  # + a BUTTERFLY MEADOW (bug habitat), SE
        flower_patch(Z, x0, y0, x1, y1, FLOWERS, 34, seed=sd + vseed)

    # 8) MORE forest patches scattered around + corner stands. NOTHING dense along the SOUTH road — that
    #    edge opens onto the underground zone below, so the south stays open (just a few stray trees, §8b).
    for (cx, cy, rx, ry, sd) in [(235, 235, 22, 22, 7), (120, 240, 38, 18, 9),     # N + NE edge stands
                                 (190, 102, 15, 17, 14), (96, 142, 13, 16, 15),     # mid patches
                                 (208, 176, 14, 15, 16), (158, 112, 12, 13, 17),
                                 (236, 112, 16, 18, 18), (84, 96, 12, 13, 19)]:
        forest(Z, cx, cy, rx, ry, density=0.6, seed=sd + vseed, dirt=False)

    # 8b) STRAY individual trees across the open grass (sparse, well-spaced); only a FEW in the south,
    #     and scatter() only plants on grass so it skips the road, quarry and water automatically.
    for (a, c, e, f, sd) in [(64, 70, 240, 244, 40), (64, 10, 244, 64, 41)]:
        scatter(Z, a, c, e, f, {"tree_oak": 3, "tree_pine": 2}, density=0.012, min_spacing=6, seed=sd + vseed, clumping=0.0)

    # 9) MINING intro — rocky outcrops SOUTH of town (toward the underground zone below). Stone blocks +
    #    starter ores (coal/copper/iron/tin) for the player to mine before descending. A dirt track leads in.
    rock_patch(Z, 152, 30, 24, seed=(10 + vseed))                              # the main quarry (SE of the south road)
    rock_patch(Z, 120, 30, 13, seed=(11 + vseed))                              # a smaller outcrop (clear of the lake)
    rock_patch(Z, 188, 46, 12, seed=(12 + vseed))                              # spread out, SE
    rock_patch(Z, 216, 118, 10, seed=(14 + vseed))                            # an east deposit at the wood's edge
    rock_patch(Z, 140, 54, 9, seed=(15 + vseed))                              # a small one just S of town (off the road)
    dirt_h(MAINX, 150, 30); dirt_v(MAINX, 30, OY - 1)                # south road -> quarry track

    # 10) BUG-ECOLOGY features — the whole point of the game. A reedy MARSH (dragonflies/damselflies) and a
    #     mushroom-and-stump GLADE (beetles/forest bugs) in a clearing E of town; these give the ecologist
    #     real habitats to study and the player varied bug-catching spots.
    import random as _rng
    lake(Z, 150, 232, 12, seed=(8 + vseed), reeds=36)                # reedy marsh pond, north
    g = _rng.Random(99 + vseed)
    for _ in range(14):                                             # a quiet glade: old stumps + mushroom clumps
        gx, gy = 178 + g.randint(-9, 9), 132 + g.randint(-8, 8)
        if Z.in_bounds(gx, gy) and Z.is_free(gx, gy) and Z.surface[gy][gx] == "grass":
            Z.place_occupant(g.choice(["stump", "mushroom_cluster", "mushroom_cluster", "fern"]), gx, gy)

    # 11) BUG SPAWNING — the server spawns NOTHING if this is absent. Tie spawn areas to the habitats:
    #     butterflies/bees in the meadows, water bugs at the marsh + lakes, beetles in the forest/glade,
    #     ants/flies/ladybugs general about town. static=False -> live continuous spawning + merge/split.
    # Based on the ORIGINAL village_21 spawners (the proven config): only `fly_common` + `butterfly_meadow`
    # are defined in species.json, so use those with the original's generous counts + a "zone_wide" fly
    # area (flies everywhere) and butterfly CIRCLES re-centred on THIS layout's flower meadows. (More bug
    # species = a content task: each needs a full ~40-field behaviour spec in species.json.)
    Z.bug_spawning = {
        "species_caps": {
            "fly_common":       {"initial": 25, "max": 75, "spawn_interval": 45.0},
            "butterfly_meadow": {"initial": 15, "max": 50, "spawn_interval": 90.0},
        },
        "spawn_areas": [
            {"id": "zone_wide", "species": ["fly_common"], "type": "zone"},
            {"id": "fly_farm", "species": ["fly_common"], "type": "circle", "cx": 125, "cy": 206, "radius": 36},
            {"id": "meadow_se", "species": ["butterfly_meadow"], "type": "circle", "cx": 200, "cy": 68, "radius": 30},
            {"id": "meadow_w", "species": ["butterfly_meadow"], "type": "circle", "cx": 30, "cy": 130, "radius": 32},
            {"id": "meadow_sw", "species": ["butterfly_meadow"], "type": "circle", "cx": 30, "cy": 205, "radius": 28},
        ],
    }

    Z.spawn = [MAINX, OY + 53]                                        # on the main street, by the square
    return Z


if __name__ == "__main__":
    import json
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")                        # save() writes row/col 0,0 — restore world pos
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 2, 1
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 256x256 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
