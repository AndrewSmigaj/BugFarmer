---
name: regenerate-sprite
description: Use when redoing the art for an existing world asset whose data entry already exists (the sprite reads wrong, is distorted, or needs a different size/take). Regenerates + cleans the PNG in place in ONE command; touches only that sprite. Does not touch entity data (except sprite_w/h for a resize).
---

# Regenerate an existing sprite (or change its size)

Pipeline A (gpt-image-1). Canonical reference: `docs/guides/art/object_pipeline.md`.
The entity already exists in `nakama/data/entities/*.json`, so this only redoes the art.

1. **Refine the prompt** — the `look` / `materials` row for the key in `tools/art/catalog/*.json`
   (per-THEME files: `lighting.json`, `furniture.json`, `flora.json`, `structures.json`, …; the art
   prompts are DATA — never edit `gen_sprites.py`). **Not every key has a row yet** — older assets fell
   back to name+category. If the key is missing, ADD a row in the matching theme file (that's likely the
   real reason the art read wrong). Preview the prompt with no API spend first:
   `python3 tools/sprites/gen_sprites.py --keys <key> --dry-run`.

2. **Regenerate — ONE command, touches ONLY that sprite:**
   ```bash
   python3 tools/sprites/gen_sprites.py --keys <key> --force
   ```
   `gen_sprites` now **generates + cleans in one pass** (downscale to `sprite_w×sprite_h`, trim, quantize)
   and writes the finished `Resources/<...>/<key>.png` + patches its `.meta`. **No separate `pixelclean`
   step, no `git checkout` revert dance** — `git status` should show only your sprite (+ its `.meta`). If
   the Unity Editor is open it re-imports just that one sprite.
   - Add `--source <occupants|items|terrain>` if the asset isn't a placeable (items → `Items/<key>_icon.png`).
   - **Tool TIER icons** (`pickaxe_stone`, etc.) are NOT generated — re-run
     `python3 tools/sprites/recolor_sprites.py --family <family>` after regenerating the family's `_wood` base.

3. **Change a sprite's SIZE** — edit `sprite_w` / `sprite_h` in `nakama/data/entities/*.json`, then run the
   **same one regen command**. Changing dims is DATA, not a hand-resize — re-genning makes the new art fill
   the new aspect (the runtime scales to `sprite_w × sprite_h`, so those dims ARE the on-screen aspect).
   - **ASPECT FIRST (the #1 "still looks wrong" cause):** a tall/thin object (torch, post, candle) in a
     SQUARE sprite gets squished wide — the torch read as a mushroom until set tall (`12×20`). Compare
     siblings (`lamp_post` 16×32, `candelabra` 12×20).

4. **Preview + accept:** `python3 tools/make_scene.py` → open `tools/_generated/previews/scene.png` (or render
   the relevant scene). Run the acceptance checklist in the guide. If it still reads wrong, refine the prompt /
   dims and repeat.
   - **Icon legibility:** if a world sprite doubles as the ~40px hotbar/inventory icon, confirm it READS that
     small; a dedicated `Items/<id>_icon` override is the fallback.

**Bulk re-clean (rare, NOT part of a single regen):** `python3 tools/sprites/pixelclean.py` re-cleans the whole
set; `--keys a,b,c` cleans only those existing sprites in place. Use it for re-cleaning EXISTING art across the
set, never as the path to regenerate one sprite.
