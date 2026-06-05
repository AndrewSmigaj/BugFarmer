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

### Excluded (do NOT regenerate)
- `chandelier` — skip (hard to read from overhead).
- `torch_wall` — skip.
- `chest_large` — **removed** (entity + sprite deleted; we use `chest_wood`).

(Catalog coverage: as scenes are built, ensure every world entity appears in at least one scene —
that's also what surfaces the items above and any new ones added to the catalog.)
