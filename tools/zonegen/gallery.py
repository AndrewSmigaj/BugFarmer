#!/usr/bin/env python3
"""The PREVIEW GALLERY — previews/index.html, the visual entry point.

Every registered scene card is the visual representation of what its guide
currently produces; this page puts them all in one place with their guide links,
so "what does the orchard/fly farm/house system look like right now?" is one
open-in-browser away.

    python3 tools/zonegen/gallery.py      # regenerate index.html
(registry.py's render_all also regenerates it after a full render.)
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from registry import REGISTRY, PREVIEWS                     # noqa: E402

# scene -> (the guide it illustrates, one-line caption)
GUIDE_OF = {
    "scene1_player_farm":            ("house.md", "the player farm: ⊥ house + pens + beds"),
    "scene_houses":                  ("house.md", "HOUSE SHAPES: L+porch · U+court · Z+annex · sculpted seeds"),
    "scene_beefarm_woods":           ("biome-feature-map.md", "bee farm at the woods' edge"),
    "scene_village":                 ("village.md", "the original composed town (the blit pattern)"),
    "scene_butterfly_meadow":        ("vegetation.md", "flowering meadow: clumped scatter"),
    "scene_meadow_forest_edge":      ("forest.md", "the meadow→forest gradient (dirt floor)"),
    "scene_underground_caverns":     ("caves.md", "carved caverns + tunnels + ore veins"),
    "scene_underground_house":       ("caves.md", "an underground dwelling"),
    "scene_underground_mining_camp": ("caves.md", "the mining camp"),
    "scene_ant_colony":              ("ant-colony.md", "the ant nest + marching files"),
    "scene_desert":                  ("biome-feature-map.md", "desert biome palette"),
    "scene_road_angles":             ("roads.md", "RAW vs SMOOTHED roads (the diagonal tiles)"),
    "scene_shore_arcs":              ("water.md", "one lake, four different banks"),
    "scene_orchard":                 ("vegetation.md", "the orchard: crisp rows + lanes + crates"),
    "scene_fly_farm":                ("village_21_B.md", "FLY FARMING: mini orchard → compost pens → nets/catchers"),
    "scene_block_house":             ("blocks.md", "wall blocks as houses"),
    "scene_block_mine":              ("blocks.md", "ore blocks in rock"),
    "scene_block_tiling":            ("blocks.md", "block tiling QA (no seams)"),
    "scene_catalog":                 ("README.md", "every world entity, placed once"),
    "scene_smith":                   ("house.md", "the smith piece (text-grid building)"),
    "scene_carpenter":               ("house.md", "the carpenter piece"),
    "scene_market":                  ("village.md", "the market piece (stall line out front)"),
    "scene_mayor":                   ("village.md", "the town hall / mayor estate piece"),
    "scene_cottage":                 ("house.md", "the 2-room cottage piece + yard"),
    "scene_ecologist":               ("village.md", "the ecologist cabin (unfenced)"),
    "scene_lakeside":                ("water.md", "the boat store + dock over water"),
}

ORDER = ["zones", "surface", "pieces", "tests", "underground", "desert"]

# the playable ZONES (maps rendered by view_world + the annotation pass) — shown
# first; these are what the game actually loads.
# (zone_id, [(image, caption), ...]) — REAL-ART renders first, the annotated
# minimap last. zones/<id>/ renders regenerate on every zone --save.
ZONE_MAPS = [
    ("village_21_B", [
        ("zones/village_21_B/full.png", "the full zone (real art)"),
        ("zones/village_21_B/plaza.png", "the plaza + civic core"),
        ("zones/village_21_B/residential.png", "the residential street (yard styles)"),
        ("zones/village_21_B/fly_farm.png", "the fly farm (the loop)"),
        ("zones/village_21_B/farms_orchard.png", "farms + orchard rows"),
        ("zones/village_21_B/lake_boatstore.png", "the lake + boat store"),
        ("zones/village_21_B/mining.png", "the rock belt + rails"),
        ("maps/village_21_B_map.png", "annotated minimap (landmarks)"),
    ]),
    ("village_21", [
        ("maps/predators_map_full.png", "the original village (kept for comparison)"),
    ]),
]


def generate():
    by_cat = {}
    for name, (cat, _scale) in REGISTRY.items():
        by_cat.setdefault(cat, []).append(name)
    rows = ["<!doctype html><meta charset='utf-8'><title>BugFarmer scene gallery</title>",
            "<style>body{background:#1d1f24;color:#ddd;font-family:sans-serif;margin:24px}",
            "h1{font-size:20px} h2{margin-top:32px;border-bottom:1px solid #444}",
            ".card{display:inline-block;vertical-align:top;margin:10px;max-width:460px}",
            ".card img{max-width:460px;border:1px solid #555;display:block}",
            ".card b{font-size:14px} .card i{color:#9ab;font-size:12px}",
            "a{color:#8cf}</style>",
            "<h1>Scene gallery — what each guide currently produces</h1>",
            "<p>Cards re-render via <code>python3 tools/zonegen/registry.py</code>. "
            "Zone maps live in <a href='maps/'>maps/</a>; one-off art QA in "
            "<a href='art_review/'>art_review/</a>.</p>"]
    rows.append("<h2>zones (the playable maps — real art)</h2>")
    for zid, imgs in ZONE_MAPS:
        rows.append(f"<h3>{zid}</h3>")
        for png, cap in imgs:
            exists = os.path.exists(os.path.join(PREVIEWS, png))
            img = f"<img src='{png}' loading='lazy'>" if exists else "<i>not rendered — run the zone --save</i>"
            rows.append(f"<div class='card'><b>{html.escape(cap)}</b><br>{img}</div>")
    for cat in ORDER + sorted(set(by_cat) - set(ORDER)):
        if cat == "zones":
            continue
        if cat not in by_cat:
            continue
        rows.append(f"<h2>{cat}</h2>")
        for name in sorted(by_cat[cat]):
            png = f"{cat}/{name}.png"
            exists = os.path.exists(os.path.join(PREVIEWS, png))
            guide, cap = GUIDE_OF.get(name, ("", ""))
            glink = (f" · <a href='../../../docs/guides/authoring/{guide}'>{guide}</a>"
                     if guide and not guide.endswith("_B.md")
                     else (f" · <a href='../../../docs/product/zones/{guide}'>{guide}</a>" if guide else ""))
            img = (f"<img src='{png}' loading='lazy'>" if exists
                   else "<div style='width:460px;height:80px;border:1px dashed #966'>"
                        "not rendered yet — run registry.py</div>")
            rows.append(f"<div class='card'><b>{html.escape(name)}</b>{glink}<br>"
                        f"<i>{html.escape(cap)}</i><br>{img}</div>")
    out = os.path.join(PREVIEWS, "index.html")
    with open(out, "w") as f:
        f.write("\n".join(rows))
    print(f"gallery -> {out}")
    return out


if __name__ == "__main__":
    generate()
