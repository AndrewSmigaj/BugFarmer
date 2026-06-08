---
name: add-object
description: Use when adding a new world object, occupant, placeable, item, tile, or block to the game (furniture, structure, flower, ore, tool/weapon icon, etc.). Covers the data entry, the data-driven art prompt, sprite generation, and on-grid placement. Does NOT cover the player sprite or player gear (that is the hand-authored pipeline B).
---

# Add a world object / item

Pipeline A (gpt-image-1). The art is **data-driven**: per-item silhouettes live in
`tools/art/catalog/*.json`; the global look (pixel-art style, palettes, per-family art direction) lives
in `tools/art/style.json`. To add an item you edit **two data files** (the canonical entity JSON + one
catalog row) and run three commands — you do **not** touch `gen_sprites.py` or `style.json`.

## 1. Add the game entity (canonical data, lean)
Edit the canonical `nakama/data/entities/<source>.json` (NEVER the client copy under `Resources/`):
- **`placeables.json`** — player-placed, occupies a grid *footprint*, ownable, can grant farm bonuses:
  furniture, decor, lighting, structures, **blocks** (dirt/stone/ore/wood/wall), **flat placeables** (rugs).
- **`occupants.json`** — world-only (player can't place): trees, **flowers/herbs/mushrooms**, ore deposits, crops.
- **`items.json`** — inventory-only: raw resources, tools/weapons, seeds, consumables/potions, fish.

Fields: `name`, `category`, `sprite_w`, `sprite_h`, `world.footprint` `[w,h]`, `world.pivot`
(`bc` = grounded / `c` = centered), `sell_price`, and `world.breakable` `{hp, required_tool_type, drops}`
where relevant. **Keep it lean** — no art-prompt or bonus fields in game data.
- **Id naming convention:** `{family}_{descriptor}` (`wall_brick`, `window_fancy`, `rug_bearskin`) so
  families stay greppable.
- **Drops must reference a real item id** (placeables are items → drop self; a gatherable occupant needs a
  matching `items.json` resource, e.g. `chamomile`).

## 2. Add the art prompt (one catalog row)
Add a row to the matching `tools/art/catalog/<category>.json` (files are organizational — the loader
merges by id, so any object file works; pick the intuitive one):
```json
"my_id": { "look": "<one line: SHAPE, key parts in CAPS, color, what it must NOT be mistaken for>",
           "materials": ["wood"] }
```
- **`look`** is what makes the model draw the right silhouette — without it the model invents one from the
  bare name. Be concrete (see neighbors in the file for the house style).
- **`materials`** is OPTIONAL — add it only when the keyword guesser is wrong (check with `--dry-run`).
  Palette options: `wood, stone, metal, foliage, dirt, fabric`.
- **Tiles** → `tiles.json` (`look`); **blocks / walls / ore** → `blocks.json` (`surface`, and `fleck` for ores).
- The **global look** lives in `tools/art/style.json`. You edit it only to change how *everything* looks,
  never to add one item.

## 3. Publish data to the client
```bash
python3 tools/publish_entities.py
```

## 4. Generate + clean
```bash
python3 tools/gen_sprites.py --source <placeables|occupants|items|terrain> --keys <id> --dry-run  # read the prompt, no spend
python3 tools/gen_sprites.py --source <...> --keys <id>      # generate
python3 tools/pixelclean.py                                  # downscale + quantize in place
```

## 5. Preview
Render the relevant scene (`tools/zonegen/scenes/<scene>.py`) or `python3 tools/make_scene.py`, open the
PNG, and run the acceptance check.

## Inventory icons
- **Derived (no art to author):** placeables, blocks, and cut flowers/herbs reuse their world sprite as the
  icon (a mini) — same art as the bobbing drop. Do NOT generate a separate `_icon.png` for these.
- **Authored:** only items with NO world sprite (raw resources, tools/weapons, seeds, potions) get
  `Resources/Items/<id>_icon.png` — `--source items` + an icon catalog row.

## Acceptance checklist (per sprite)
- Reads instantly as the intended object at game zoom; correct silhouette.
- Transparent background; no baked ground patch / cast shadow (tiles are the exception: opaque, full-bleed).
- Even-width objects sit on grid in the preview (footprint-X rule).
- Tiles / linear connectors (fence, wall) tile seam-free.

Canonical pipeline detail: `docs/guides/art/object_pipeline.md`.
