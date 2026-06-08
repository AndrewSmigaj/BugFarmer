#!/usr/bin/env python3
"""Scene — the STARTING VILLAGE (`village_21`): a lived-in TOWN, not a sparse demo.

Built to the village authoring guide (docs/guides/authoring/village.md): a focal-point PLAZA with a
fountain at the road crossing; ORGANIC roads in a hierarchy (main N-S → E-W connector → side lanes);
buildings CLUSTERED by function — civic (town hall · market · grocer · general store) near the square,
production (carpenter + smith) adjacent, residential cottages on a side lane, the boat store at the
LAKE; an orchard + fly farm at the edges; and a clumped meadow whose density rises toward the forest
rim (the town's soft boundary). North is UP (high Y = top); south-facing doors use door_side "top".

Renders to ONE canonical file: tools/_generated/previews/surface/scene_village.png (via registry.py).
Run: python3 tools/zonegen/scenes/scene_village.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.room import place_room                                  # noqa: E402
from features.house import place_house, styled_rooms, row_house, bbox  # noqa: E402
from features.village import shop_building, plaza                     # noqa: E402
from features.yard import fence_rect, yard                            # noqa: E402
from features.terrain import path, pond                               # noqa: E402
from features.garden import crop_bed, flower_patch, fruit_around      # noqa: E402
from features.scatter import scatter                                  # noqa: E402

W, H = 80, 80
FKINDS = ["flower_red", "flower_blue", "flower_yellow", "flower_aster", "poppy"]


def safe(b, oid, x, y, **k):
    """place_occupant only if the whole footprint lands on free in-bounds cells (warning-free)."""
    fw, fh = b.footprint(oid)
    for dx in range(fw):
        for dy in range(fh):
            if not b.is_free(x + dx, y + dy):
                return False
    return b.place_occupant(oid, x, y, **k)


def picket_cottage(b, ox, oy, coll, *, weathered=False, front=None, garden=True):
    """A 3-room cottage in a PICKET-fenced yard with a little garden. Returns the house bbox."""
    specs, default_front = row_house(ox, oy)
    place_house(b, styled_rooms(specs, collection=coll), front=front or default_front)
    x0, y0, x1, y1 = bbox(specs)
    fence = "fence_picket_weathered" if weathered else "fence_picket"
    gx = (x0 + x1) // 2
    fence_rect(b, x0 - 1, y0 - 1, x1 + 1, y1 + 1, gate=(gx, y0 - 1), fence=fence, gate_id="gate_picket")
    for yy in range(max(0, y0 - 3), y0 - 1):                          # approach path out of the gate
        b.set_ground(gx, yy, "stone_path", surface="path")
    if garden:                                                       # a little bed beside the cottage
        gy = y1 + 2
        crop_bed(b, x0, gy, x0 + 5, gy + 1, ["plant_tomato", "plant_corn", "plant_wheat"])
        for ex in range(x0, x0 + 6):
            safe(b, "garden_border_stone", ex, gy - 1, surface="grass")
        flower_patch(b, x0 + 6, gy - 1, x1, gy + 2, FKINDS, 8, seed=ox + oy)
    return (x0, y0, x1, y1)


# ---- the scene --------------------------------------------------------------
def build():
    b = ZoneBuilder("scene_village", W, H, base_tile="grass", name="Starting Village")

    # 1) BASE is grass. 2) LAKE first (reserves water so roads/scatter part around it). =========
    pond(b, 11, 11, 12, 9, seed=3)                          # bigger SW lake (~x0-23, y2-20)

    # 3) ROADS — organic hierarchy (main 4 -> connector 3 -> side lanes 2). =====================
    path(b, (42, 0), (37, 79), width=4, edge_tile="dirt", wobble=0.13, taper_ends=8, seed=1)   # main N-S
    path(b, (4, 40), (74, 40), width=3, edge_tile="dirt", wobble=0.15, taper_ends=6, seed=2)    # E-W connector
    path(b, (38, 57), (12, 66), width=2, edge_tile="dirt", wobble=0.22, seed=3)                 # NW residential lane
    path(b, (44, 42), (60, 48), width=2, edge_tile="dirt", wobble=0.20, seed=4)                 # E production spur

    # 4) BUILDING CLUSTERS (reserve footprints; varied door sides for orientation variety). =====
    # --- CIVIC cluster (W of the plaza): hall + market (N of road) · grocer + store (S of road) ---
    def townhall_fill(b, I):
        ix0, iy0, ix1, iy1 = I
        cx = (ix0 + ix1) // 2
        safe(b, "rug", cx - 1, (iy0 + iy1) // 2)            # rug under the table (decor base)
        safe(b, "map_table_big", cx - 1, (iy0 + iy1) // 2)
        for it, dx in [("bookshelf", 0), ("bookshelf", 2), ("statue_stone", 5), ("desk", 8)]:
            safe(b, it, ix0 + dx, iy1)                      # back wall: records + a desk
        safe(b, "mirror_standing", ix1, iy1)
        safe(b, "sofa_fancy", ix0 + 1, iy0); safe(b, "sofa", ix1 - 2, iy0)
        safe(b, "plant_large", ix0, iy0); safe(b, "plant_large", ix1, iy0)
        safe(b, "potted_plant", cx, iy0)
    th = place_room(b, 16, 45, 28, 57, floor="wood_floor", wall="wall_marble",
                    door="door_wood", door_side="top")
    if th:
        townhall_fill(b, th)
    safe(b, "sign_crest", 22, 44, surface="grass")
    safe(b, "column_marble", 17, 44); safe(b, "column_marble", 27, 44)
    safe(b, "statue_founder", 22, 58)                       # statue out back

    def market_produce(b, I):                               # shelving+counter come from shop_building
        ix0, iy0, ix1, iy1 = I
        safe(b, "produce_crate", ix0, iy0); safe(b, "produce_crate", ix0 + 1, iy0)
        safe(b, "barrel", ix1, iy0)
    shop_building(b, 30, 45, 41, 55, sign_id="sign_market_board", npc="merchant",
                  door_side="top", shelf_rows=2, extra_fill=market_produce)
    safe(b, "awning", 31, 44); safe(b, "produce_crate", 34, 44); safe(b, "apple_crate", 38, 44)
    b.place_bug("fly_house", 35.4, 43.4, scale=0.45, flip=True)

    def grocer_fill(b, I):
        ix0, iy0, ix1, iy1 = I
        safe(b, "produce_crate", ix1, iy0); safe(b, "barrel", ix0, iy0)
    shop_building(b, 14, 27, 23, 37, sign_id="sign_shop", npc="farmer", npc_dir="up",
                  door_side="bottom", shelf_rows=1, extra_fill=grocer_fill)

    def store_fill(b, I):
        ix0, iy0, ix1, iy1 = I
        safe(b, "chest_wood", ix0, iy0); safe(b, "barrel", ix1, iy0)
    shop_building(b, 25, 27, 34, 37, sign_id="sign_plank", npc="merchant", npc_dir="up",
                  door_side="bottom", shelf_rows=2, extra_fill=store_fill)
    safe(b, "barrel", 26, 38); safe(b, "apple_crate", 28, 38)

    # --- PRODUCTION cluster (E of the plaza): carpenter + smith ADJACENT ---
    def carpenter_fill(b, I):                               # furniture workshop — goods laid out in ROWS
        ix0, iy0, ix1, iy1 = I
        safe(b, "sawmill", ix0, iy1 - 1)                    # the big saw machine, INDOORS at the back
        for it, dx in [("workbench", 3), ("lumber_rack", 5), ("workbench", 7), ("dresser", 9)]:
            safe(b, it, ix0 + dx, iy1)                      # back-wall work stations
        midy = (iy0 + iy1) // 2                             # middle aisle = finished furniture on display
        for it, dx in [("table_wood", 0), ("chair_wood", 2), ("dresser", 4), ("bookshelf", 6), ("chest_wood", 9)]:
            safe(b, it, ix0 + dx, midy)
        for it, dx in [("crate", 0), ("barrel", 2), ("sawhorse", 5), ("chopping_block", 8)]:
            safe(b, it, ix0 + dx, iy0)                      # front = raw materials
    shop_building(b, 50, 45, 62, 55, sign_id="sign_plank", door_side="top",
                  wall="wall_wood", shelf_rows=0, counter_id=None, extra_fill=carpenter_fill)
    safe(b, "log_pile", 50, 44); safe(b, "sawhorse", 53, 44); safe(b, "chopping_block", 56, 44)

    def smith_fill(b, I):                                   # forge interior — tools/anvils/ingots in rows
        ix0, iy0, ix1, iy1 = I
        safe(b, "furnace", ix0, iy1 - 1)                    # an inside forge at the back
        for it, dx in [("tool_rack", 3), ("tool_rack", 4), ("anvil", 6), ("chest_iron", 8)]:
            safe(b, it, ix0 + dx, iy1)
        midy = (iy0 + iy1) // 2
        for it, dx in [("anvil", 0), ("cauldron", 3), ("barrel", 5), ("crate", 7)]:
            safe(b, it, ix0 + dx, midy)
        for it, dx in [("coal_bin", 0), ("crate", 2), ("barrel", 4), ("tool_rack", 7)]:
            safe(b, it, ix0 + dx, iy0)
    shop_building(b, 64, 45, 74, 55, sign_id="sign_anvil", door_side="top",
                  wall="wall_stone", shelf_rows=0, counter_id=None, extra_fill=smith_fill)
    safe(b, "furnace", 64, 44); safe(b, "anvil", 67, 44); safe(b, "coal_bin", 70, 44)
    safe(b, "tool_rack", 72, 44)
    b.place_bug("firefly_blue", 65.5, 43.4, scale=0.4)     # forge ember glow

    # --- ECOLOGIST cottage (W, above the lake) ---
    def eco_fill(b, I):
        ix0, iy0, ix1, iy1 = I
        safe(b, "specimen_shelf", ix0, iy1); safe(b, "bug_terrarium_big", ix0 + 2, iy1)
        safe(b, "desk", ix1, iy1); safe(b, "bookshelf", ix0, iy0 + 1)
    ec = place_room(b, 3, 24, 12, 33, floor="wood_floor", wall="wall_wood",
                    door="door_wood", door_side="right")
    if ec:
        eco_fill(b, ec)
    safe(b, "sign_leaf", 3, 23, surface="grass")
    crop_bed(b, 3, 35, 8, 36, ["plant_tomato", "plant_corn", "plant_wheat"])  # test garden
    b.place_bug("ladybug_orange", 5.0, 35.5, scale=0.5)
    b.place_bug("butterfly_emperor", 9.0, 34.0, scale=0.6, flip=True)

    # --- BOAT & FISHING store (east shore of the lake; docks reach W over the water) ---
    def fishstore(b, I):
        ix0, iy0, ix1, iy1 = I
        safe(b, "bookshelf", ix0, iy1); safe(b, "fish_crate", ix1, iy1)
        safe(b, "barrel", ix1, iy0 + 1)
    fs = place_room(b, 25, 9, 32, 17, floor="wood_floor", wall="wall_wood",
                    door="door_wood", door_side="left")
    if fs:
        fishstore(b, fs)
    safe(b, "sign_anchor", 25, 8, surface="grass")
    safe(b, "fishing_net", 24, 18); safe(b, "fish_crate", 31, 18)
    for dx in range(13, 25):                                # dock deck reaching W over the water
        for dy in (12, 13):
            if b.in_bounds(dx, dy):
                b.set_ground(dx, dy, "bridge_wood", surface="path")
                b.reserved[dy][dx] = False
    for (mx, my) in [(15, 11), (19, 11), (23, 11), (15, 14), (19, 14)]:
        safe(b, "mooring_post", mx, my, surface="path")
    safe(b, "boat", 13, 11, surface="path")
    safe(b, "lamp_post", 24, 11)
    b.place_bug("dragonfly_emperor", 16, 8, scale=0.6)
    b.place_bug("dragonfly_emperor", 8, 15, scale=0.6, flip=True)
    for lp in [(5, 15), (7, 17), (4, 6), (9, 4)]:
        b.place_decor("lily_pad", lp[0], lp[1], scale=0.8)

    # 5) PLAZA + FOUNTAIN at the crossing (the focal point). ====================================
    plaza(b, 39, 40, r=5, flower_kinds=FKINDS, seed=40)
    safe(b, "signpost", 44, 44); safe(b, "well", 34, 35)
    safe(b, "bench_stone", 36, 36); safe(b, "bench_stone", 41, 44)
    safe(b, "lamp_post", 39, 35); safe(b, "potted_plant", 35, 44)
    flower_patch(b, 35, 35, 38, 38, FKINDS, 5, seed=41)
    flower_patch(b, 41, 42, 44, 45, FKINDS, 5, seed=42)
    b.place_bug("butterfly_swallowtail", 40, 37, scale=0.7)
    b.place_bug("bee_carpenter", 37, 41, scale=0.6, flip=True)
    b.place_bug("butterfly_emperor", 42, 38, scale=0.6, flip=True)

    # 6) RESIDENTIAL cottages (NW lane) — picket fences + gardens, varied orientation. ==========
    picket_cottage(b, 6, 64, "fancy")                                          # south-facing door
    picket_cottage(b, 46, 64, "basic", weathered=True, front=("bedroom", "left"))  # west-facing door
    safe(b, "laundry_line", 47, 63); safe(b, "cat_statue", 6, 63)

    # 7) ORCHARD (E edge) — alternating rows + fruit_around (the fly-emergence loop). ===========
    fence_rect(b, 63, 22, 78, 41, gate=(70, 41))
    for i, ry in enumerate((24, 27, 30, 33, 36, 39)):
        sp, fr = ("tree_apple", "fallen_fruit") if i % 2 == 0 else ("tree_orange", "fallen_orange")
        for cx in (65, 69, 73, 76):
            if safe(b, sp, cx, ry):
                fruit_around(b, cx, ry, fresh=fr, n=4)
    safe(b, "ladder", 77, 26); safe(b, "apple_crate", 64, 23); safe(b, "compost_pile", 76, 40)
    for c in [(66, 25), (71, 31), (74, 37)]:
        b.place_bug("fruitfly_common", float(c[0]), float(c[1]), scale=0.4, flip=(c[0] % 2 == 0))

    # 8) FLY FARM (far W edge, S of the ecologist) — fenced ecology demo. =======================
    b.fill_ground(2, 45, 9, 60, "dirt", surface="farm")
    fence_rect(b, 1, 44, 10, 61, gate=(5, 44))
    safe(b, "bait_station", 2, 47); safe(b, "bait_station", 9, 47)
    safe(b, "compost_pile", 2, 58); safe(b, "compost_pile", 8, 58)
    for ny in (48, 51, 54):
        safe(b, "fly_netting", 5, ny)
    safe(b, "autonet", 4, 46); safe(b, "collection_tray", 9, 59); safe(b, "bait_basket", 2, 59)
    for j, c in enumerate([(3, 47), (9, 48), (4, 56), (8, 57), (5, 51)]):
        b.place_bug("fly_house", float(c[0]), float(c[1]), scale=0.4, flip=(j % 2 == 0))
    for fp in [(3, 55.5), (9, 56.5)]:
        b.place_decor("fallen_fruit", fp[0], fp[1], scale=0.5)

    # 9) CLUMPED MEADOW (scatter LAST; density rises toward the forest rim = the town boundary). =
    meadow = {"tall_grass": 5, "bush": 2, "bush_flowering": 1, "flower_wild": 2}
    forest = {"tree_oak": 3, "tree_pine": 2, "bush": 2, "tall_grass": 2}
    # near-town meadow (sparser, patchy) — covers the open ground between clusters
    for (rx0, ry0, rx1, ry1, sd) in [(13, 19, 29, 26, 11), (43, 24, 62, 44, 12),
                                     (13, 38, 30, 44, 13), (35, 57, 62, 63, 14),
                                     (44, 4, 64, 23, 15), (30, 4, 47, 20, 16),
                                     (50, 56, 64, 78, 17)]:
        scatter(b, rx0, ry0, rx1, ry1, meadow, density=0.12, min_spacing=2, seed=sd,
                clumping=0.85, cluster_radius=4)
    # forest rim (dense, walls the town)
    for (rx0, ry0, rx1, ry1, sd) in [(0, 62, 10, 78, 5), (66, 0, 78, 20, 6),
                                     (28, 0, 46, 4, 7), (70, 56, 78, 78, 9)]:
        scatter(b, rx0, ry0, rx1, ry1, forest, density=0.30, min_spacing=1, seed=sd,
                clumping=0.8, cluster_radius=5)

    # 10) FREE-FLOATING flowers along road edges + meadow gaps (sub-grid, off the grid). ========
    flower_patch(b, 13, 19, 29, 30, FKINDS + ["sunflower"], 14, seed=30)
    flower_patch(b, 44, 24, 62, 43, FKINDS, 12, seed=31)
    flower_patch(b, 35, 58, 60, 63, FKINDS, 9, seed=32)
    flower_patch(b, 46, 6, 63, 22, FKINDS + ["sunflower"], 12, seed=33)
    flower_patch(b, 31, 6, 46, 19, FKINDS, 9, seed=34)
    for (bx, by, fl) in [(58, 12, False), (20, 30, True), (50, 30, False), (33, 60, True),
                         (54, 16, True), (38, 14, False)]:
        b.place_bug("butterfly_swallowtail", bx, by, scale=0.7, flip=fl)

    b.spawn = [41, 42]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "surface", "scene_village.png"))
    render_builder(b, out, scale=5)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
    issues = b.validate()
    print("validate:", issues if issues else "OK")
