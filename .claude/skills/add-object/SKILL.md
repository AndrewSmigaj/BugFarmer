---
name: add-object
description: Use when adding a new world object, occupant, placeable, or item to the game (a tree, piece of furniture, structure, inventory item, etc.). Covers data entry, sprite generation, and on-grid placement. Does NOT cover the player sprite or player gear (that is the hand-authored pipeline).
---

# Add a world object

Always pipeline A (gpt-image-1). Canonical reference: `docs/guides/object_pipeline.md`.

1. **Pick the source file**: `occupants.json` (world creatures/structures placed in zones),
   `placeables.json` (player-placed furniture/objects), or `items.json` (inventory).
2. **Add the entry to the canonical `nakama/data/entities/<source>.json`** (never the client copy).
   Set `category`, `sprite_w`, `sprite_h`, `world.footprint`, and `world.pivot`
   (`bc` = bottom-center for grounded objects, `c` = centered).
3. **If the silhouette isn't obvious from the name**, add an `OBJECT_DESC` entry (and `OBJECT_MATS`
   if the material guess is wrong) in `tools/gen_sprites.py`.
4. **Publish the data to the client**: `python3 tools/publish_entities.py`
5. **Generate + clean the sprite**:
   ```bash
   python3 tools/gen_sprites.py --source <occupants|placeables|items> --keys <key>
   python3 tools/pixelclean.py
   ```
   (Use `--dry-run` first to inspect the prompt without spending on the API.)
6. **Preview and check**: `python3 tools/make_scene.py`, open
   `tools/_generated/previews/scene.png`, and run the acceptance checklist in the guide
   (reads as the intended object, transparent background, even-width objects sit on-grid).
