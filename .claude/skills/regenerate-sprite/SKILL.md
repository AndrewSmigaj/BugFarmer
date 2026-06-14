---
name: regenerate-sprite
description: Use when redoing the art for an existing world asset whose data entry already exists (the sprite reads wrong, is distorted, or needs a fresh take). Regenerates and cleans the PNG in place; does not touch entity data.
---

# Regenerate an existing sprite

Pipeline A (gpt-image-1). Canonical reference: `docs/guides/art/object_pipeline.md`.
The entity already exists in `nakama/data/entities/*.json`, so this only redoes the art.

1. **Refine the prompt** — the `look` / `materials` row for the key in `tools/art/catalog/*.json`
   (per-THEME files: `lighting.json`, `furniture.json`, `flora.json`, …; the art prompts are DATA —
   never edit `gen_sprites.py`). **Not every key has a row yet** — older assets fell back to
   name+category. If the key is missing, ADD a row in the matching theme file (that's likely the
   real reason the art read wrong).
2. **Regenerate, overwriting the existing PNG**:
   ```bash
   python3 tools/gen_sprites.py --keys <key> --force
   python3 tools/pixelclean.py
   ```
   Add `--source <occupants|items|terrain>` if the asset isn't a placeable.
   **⚠ A bare `pixelclean.py` RE-CLEANS EVERY sprite under `Resources/`** (re-quantizes ~hundreds of
   PNGs) — after running it, `git status` and **revert every PNG except your key** so you don't churn
   unrelated art (`git checkout -- <those.png>`).
   **Item icons**: pixelclean is OPT-IN per key — `python3 tools/pixelclean.py --k 8 --items <key>`
   (a bare run never touches Items/; icons quantize to 8 colors). **Tool TIER icons**
   (`pickaxe_stone` etc.) are NOT generated — re-run `python3 tools/recolor_sprites.py
   --family <family>` after regenerating the family's `_wood` base.
3. **Preview**: `python3 tools/make_scene.py` → open `tools/_generated/previews/scene.png`.
4. **Run the acceptance checklist** in the guide. Do **not** hand-resize — the runtime scales to
   `sprite_w × sprite_h`, so those dims ARE the on-screen aspect.
   - **ASPECT FIRST (the #1 "still looks wrong" cause):** check `sprite_w`/`sprite_h` match the
     object's silhouette. A tall/thin object (torch, post, candle) in a SQUARE sprite gets squished
     wide — the torch read as a mushroom (fat base) until set tall (`12×20`). Compare siblings
     (`lamp_post` 16×32, `candelabra` 12×20). Changing dims is data, NOT a hand-resize — then
     re-`gen_sprites --force` + `pixelclean` so the art fills the new aspect.
   - **Icon legibility:** if the world sprite doubles as the ~40px hotbar/inventory icon, confirm it
     READS that small; a dedicated `Items/{id}_icon` override is the fallback.
   If it still reads wrong, refine the prompt and repeat.
