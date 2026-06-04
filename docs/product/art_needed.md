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

## Missing world sprites (11 of 95 catalog entities, 2026-06)
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

(Catalog coverage: as scenes are built, ensure every world entity appears in at least one scene —
that's also what surfaces the items above and any new ones added to the catalog.)
