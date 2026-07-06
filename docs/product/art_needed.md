# Art needed (placeholder → real sprite)

World entities placed in scenes/zones that have **no sprite PNG yet** render as labeled
placeholder squares (colored by category) in `make_scene` previews, so layout/composition can be
built and reviewed before any art exists. This file is the queue for the batched art pass
(`add-object` / `gen_sprites.py` → `pixelclean.py`).

Regenerate the missing list:
```bash
python3 - <<'PY'
import json, os
ENT, OBJS = "nakama/data/entities", "BugFarmerClient/Assets/Resources/Objects"
for fn in ("occupants.json", "placeables.json", "crops.json"):
    p = os.path.join(ENT, fn)
    if not os.path.exists(p): continue
    for k, v in json.load(open(p)).items():
        if isinstance(v, dict) and not k.startswith("_") and ("sprite_w" in v or "world" in v):
            if not os.path.exists(os.path.join(OBJS, f"{k}.png")):
                print(f"{k} | {v.get('category','')} | {fn.split('.')[0]}")
PY
```

## Village rebuild — new entities ✅ DONE
Generated + cleaned (gpt-image-1): `sign_market_board` (3-wide market board), `shop_shelving` (stocked
store shelves), `fence_picket`, `gate_picket`, `fence_picket_weathered`, `garden_border_stone`,
`garden_border_log`. All live in `scene_village.py` (the market reads as a shop, cottages are
picket-fenced). Re-bake `fence_picket` via the connector bake-off later if the line tiling needs polish.

## Missing world sprites (11 of 114 catalog entities, 2026-06)
Generate via the **add-object** skill: `gen_sprites.py --source <src> --keys <key>` → `pixelclean.py`.

**DONE** (generated via gpt-image-1 + cleaned): the **house set** (fridge, stove, sink, counter,
keg, sofa, armchair, nightstand, dresser, rug, bug_terrarium, vase, window_4pane) and the **farm
set** (fountain, compost_bin, autonet, fly_netting, fallen_fruit, rotten_fruit). Scene 1 (house +
fly farm) renders with full real art except the two backlog items below that appear in it.

### Pre-existing backlog
| id | category | source |
|----|----------|--------|
| apple_crate | natural | occupants |
| bait_basket | structure | placeables |
| broken_net | natural | occupants |
| chopping_block | crafting | placeables |
| collection_tray | structure | placeables |
| compost_pile | natural | occupants |
| ladder | structure | placeables |
| log_pile | natural | occupants |
| net_post | structure | placeables |
| notice_board | structure | occupants |
| stump | natural | occupants |

### Village scene (`scene_village.py`, added 2026-06) — 24 new placeholders
Lean placeholder entities added for the starting-village town scene (`tools/zonegen/scenes/scene_village.py`).
Catalog `look` rows are in place (structures/decor/furniture); generate via **add-object**.

| id | category | source | catalog file |
|----|----------|--------|--------------|
| wall_marble | structure | placeables | structures |
| column_marble | decoration | placeables | structures |
| sign_anchor / sign_anvil / sign_market / sign_shop / sign_crest / sign_plank / sign_leaf | structure | placeables | structures |
| market_stall | structure | placeables | structures |
| awning | decoration | placeables | structures |
| produce_crate | structure | placeables | structures |
| dock_plank* | structure | placeables | structures |
| boat | structure | placeables | structures |
| mooring_post | structure | placeables | structures |
| fish_crate | structure | placeables | structures |
| fishing_net | decoration | placeables | structures |
| coal_bin | structure | placeables | structures |
| lumber_rack | structure | placeables | structures |
| bait_station | structure | placeables | structures |
| veg_patch_sign* | structure | placeables | structures |
| statue_founder | decoration | placeables | decor |
| laundry_line* | decoration | placeables | decor |
| cat_statue | decoration | placeables | decor |
| window_box* | decoration | placeables | decor |
| specimen_shelf | furniture | placeables | furniture |
| bug_terrarium_big | furniture | placeables | furniture |
| map_table_big | furniture | placeables | furniture |
| sofa_modern* | furniture | placeables | furniture |

\* entity + catalog row exist but the item isn't placed in `scene_village.py` yet (added for the
collection/catalog; `dock_plank` is currently rendered as the `bridge_wood` ground tile instead).

### Butterfly Meadow scenes (`scene_butterfly_meadow.py` + `scene_meadow_forest_edge.py`, added 2026-06) — 7 new placeholders
Lean placeholder entities for the Butterfly Meadow zone (`butterfly_meadow_11`). Catalog `look` rows
are in place (flora/structures/decor); generate via **add-object**. The Flower-Clock Glade is composed
from existing flowers (no new entity), and the lepidopterist's blind reuses `tent`/`crate`/`net_post`/
`broken_net`/`stool_wood`/`lantern`.

| id | category | source | catalog file |
|----|----------|--------|--------------|
| milkweed_giant | natural | occupants | flora |
| clover_red | natural | occupants | flora |
| stump_mossy | natural | occupants | flora |
| log_fallen | natural | occupants | flora |
| broken_fence | structure | placeables | structures |
| boulder | natural | placeables | decor |
| specimen_case | decoration | placeables | decor |

## Reconvert to gpt-image-1 (old-style sprites)

### DONE — regenerated 2026-06 (49 sprites incl. the house set; review sheet `_reconvert_review.png`)
Styling rules wired into `gen_sprites.py` and applied:
- **Blocks like wall tiles** — `dirt_block`, `stone_block`, `clay_block` route through the
  cube-tiling wall-block prompt (`build_wall_prompt`) with per-material surface hints.
- **Ores like wall blocks** — all 7 `ore_*_block` (source `occupants`), each with its metal-fleck hint.
- **Walls** — `wall_stone`, `wall_brick` use the wall-block prompt with stone/brick surface + palette.
- **Iron/electric fences** — `fence_iron`, `fence_electric` post-and-rail + metal palette (like `fence_wood`).
- **Furniture / structures** — anvil, barrel, cauldron, chest_iron, cooking_pot, crate, forge,
  furnace, honey_extractor, lamp_table, loom, sawmill, stonecutter, torch, workbench, potted_plant,
  beehive_basic/medium/large/deluxe, bone_pile, ant_mound.

### TODO — orphan sprites with NO entity data (need `add-object` first)
`banner`, `clock`, `mirror`, `painting_small`, `painting_large`, `shelf`, `fence_segment`. Most are
**wall-hung** — they also need the deferred **wall-overlay render feature** before they can be placed.

### TODO — crops (all `plant_*`)
`plant_corn`, `plant_tomato`, `plant_wheat` + their `_stage0..3` and `plant_stage0`: staged growth
frames, reconvert as part of the **multi-frame sprites** backlog item, not one-off.

### TODO — crafting outputs (NEW item icons; batch with `add-object`)
Stage-1 recipes deliberately output EXISTING-art items so crafting shipped without an art batch. As
recipes expand (see [crafting_design.md](design/crafting_design.md)) these new outputs need icons:
- **Metal bars:** `copper_bar`, `tin_bar`, `silver_bar`, `gold_bar`, `platinum_bar`, `steel`
  (only `iron_bar` exists). Recolor pipeline can likely do the bar set from one base.
- **Materials:** `wood_plank`, `glass`, `charcoal`, `coal_dust`, `sawdust`, `thread`, `cloth`,
  `nails`, `fittings`.
- **Dyes** (color set — recolor pipeline), `potion` set.
- **Food:** `flour`, `bread`, `meal_*`.
- **Beekeeping:** `honey`, `honey_wine`.

### TODO — crafting UI art (hand-authored, `tools/sprites/ui_sprites.py` → `Resources/UI/`)
Stage 1 ships a generic panel built from existing UI sprites. The Apico-touch polish pass:
- `panel_craft` frame; per-station header/theming (the smelter's fuel + ore input slots, a fire/heat
  meter, a fuel tank, a themed progress-bar fill). Drives the per-station look (currently identical).

### Excluded (do NOT regenerate)
- `chandelier` — skip (hard to read from overhead).
- `torch_wall` — skip.
- `chest_large` — **removed** (entity + sprite deleted; we use `chest_wood`).

(Catalog coverage: as scenes are built, ensure every world entity appears in at least one scene —
that's also what surfaces the items above and any new ones added to the catalog.)

---

## VILLAGE ECONOMY BUILDOUT (D26) — placeholder art needing real sprites
These ship NOW as flat colored-square placeholders (`tools/sprites/placeholder_sprites.py`, no API) so the
items/stations are fully functional in engine. Replace with real art in a batched pass — **materials/blocks =
gpt-image-1 (Pipeline A); NPC characters = generate_player_sprites (Pipeline B)**.

### Material icons (`Resources/Items/{id}_icon.png`, 16×16) — gpt-image-1
- Metal bars: `copper_bar` `bronze_bar` `steel_bar` `silver_bar` `gold_bar` `platinum_bar`
- Base mats: `plank` `thread` `cloth` `glass` `chitin` `leather` `silk`

### Stations (`Resources/Objects/{id}.png`) — gpt-image-1
- `bug_extractor` (32×24) — the dead-bug → materials station.

### Design TODO (not art): the Bug Extractor dead→material recipe map
`chitin` (from `dead_beetle`) is live. The full mapping — which `dead_<bug>` yields `leather` / `silk` /
more `chitin` — is undecided (village has no spider, so `silk` likely belongs to spider zones). Items exist
(placeholder) so armor recipes can reference them; their EXTRACTOR recipes await Andrew's call.

### TODO — signs should be 2 cells wide (Andrew, 2026-06-27)
All shop/town signs read better at **2×1** (32×24). `sign_weaver` is already 2-wide. Remake the rest to
2-wide (resize sprite_w → 32 + footprint [2,1], regenerate art): `sign_plank`, `sign_shop`, `sign_anvil`,
`sign_market`, `sign_inn`, `sign_camp`, `sign_anchor`, `sign_fish_board`, `sign_leaf`, `sign_crest`,
`sign_weather`, `signpost`. (`sign_market_board` is already 3-wide.)

## Bee-station + bee-decor batch (2026-07-06, placeholders in-game)
- bee_station_small (16x22, placeable) — compact pine bee box, landing lip
- bee_station_large (32x28, placeable, 2x1) — double-super station, tin roof
- skep_basket (16x20) — woven straw skep dome, decorative
- candle_beeswax (16x18) — fat amber candle on a dish
- honey_jar_shelf (16x26) — shelf crowded with amber jars
- rug_honeycomb (32x32 flat, 2x2) — honeycomb-pattern rug
