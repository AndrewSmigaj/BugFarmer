---
name: regenerate-sprite
description: Use when redoing the art for an existing world asset whose data entry already exists (the sprite reads wrong, is distorted, or needs a fresh take). Regenerates and cleans the PNG in place; does not touch entity data.
---

# Regenerate an existing sprite

Pipeline A (gpt-image-1). Canonical reference: `docs/guides/art/object_pipeline.md`.
The entity already exists in `nakama/data/entities/*.json`, so this only redoes the art.

1. **(If the silhouette/material was the problem)** refine the `OBJECT_DESC` / `OBJECT_MATS`
   entry for the key in `tools/gen_sprites.py` before regenerating.
2. **Regenerate, overwriting the existing PNG**:
   ```bash
   python3 tools/gen_sprites.py --keys <key> --force
   python3 tools/pixelclean.py
   ```
   Add `--source <occupants|items|terrain>` if the asset isn't a placeable.
3. **Preview**: `python3 tools/make_scene.py` → open `tools/_generated/previews/scene.png`.
4. **Run the acceptance checklist** in the guide. Do **not** hand-resize — the runtime scales to
   `sprite_w × sprite_h`. If it still reads wrong, refine the prompt and repeat.
