---
name: regenerate-sprite
description: Use when redoing the art for an existing world asset whose data entry already exists (the sprite reads wrong, is distorted, or needs a fresh take). Regenerates and cleans the PNG in place; does not touch entity data.
---

# Regenerate an existing sprite

Pipeline A (gpt-image-1). Canonical reference: `docs/guides/art/object_pipeline.md`.
The entity already exists in `nakama/data/entities/*.json`, so this only redoes the art.

1. **(If the silhouette/material was the problem)** refine the `look` / `materials` row for the
   key in `tools/art/catalog/*.json` (the art prompts are DATA — never edit `gen_sprites.py`).
2. **Regenerate, overwriting the existing PNG**:
   ```bash
   python3 tools/gen_sprites.py --keys <key> --force
   python3 tools/pixelclean.py
   ```
   Add `--source <occupants|items|terrain>` if the asset isn't a placeable.
   **Item icons**: pixelclean is OPT-IN per key — `python3 tools/pixelclean.py --k 8 --items <key>`
   (a bare run never touches Items/; icons quantize to 8 colors). **Tool TIER icons**
   (`pickaxe_stone` etc.) are NOT generated — re-run `python3 tools/recolor_sprites.py
   --family <family>` after regenerating the family's `_wood` base.
3. **Preview**: `python3 tools/make_scene.py` → open `tools/_generated/previews/scene.png`.
4. **Run the acceptance checklist** in the guide. Do **not** hand-resize — the runtime scales to
   `sprite_w × sprite_h`. If it still reads wrong, refine the prompt and repeat.
