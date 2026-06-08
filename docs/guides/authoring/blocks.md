# Feature guide: blocks (resource & wall)

How we make the **mineable/placeable BLOCKS** — the cube sprites that tile in a grid (ground blocks like
dirt/stone/clay, **resource/ore blocks**, and **wall blocks** like wood/brick/stone). They all share ONE
recipe so any field of blocks or a wall reads as a coherent surface. Prompt text is data: per-block
**surface/fleck** lives in `tools/art/catalog/blocks.json`; the shape prompt is `build_wall_prompt` (tuned
via the bake-off in [block_prompts.md](../art/block_prompts.md)).

## THE RECIPE
A block is **3D: a wide lit TOP surface + a short, only-slightly-darker FRONT face beneath it.** Stacked in
a grid the **tops line up and the fronts show** — it reads as a wall of blocks, like the stone wall / wood
wall / gold block. It is NOT a flat square (no front face = wrong) and NOT a block on a baked black/white
background (wrong).
- Generated via **`build_wall_prompt` (the cube/top+front prompt) + TRANSPARENT background + crop** — the
  same flow that made the walls. Blocks/walls keep **full width** (`vertical_only` trim) so they abut sideways.
- The exact prompt wording is **still being tuned** — see **[block_prompts.md](../art/block_prompts.md)** for the
  active 3-approach bake-off and the variant-folder workflow. Tune the *wording*; never change the deliverable.

## HARD RULES
- **Blocks use `build_wall_prompt` + transparent + crop.** Never `background="opaque"` on the cube prompt
  (bakes a black/white field), never a flat "seamless texture" (loses the front face → flat squares). The
  deliverable is a 3D block; only the prompt *wording* is iterated, never the kind of thing produced.
- **`gen_sprites.py` and `ab_generate.py` must route blocks identically** (a past drift sent tiles through
  the object prompt and made `cave_floor` a chest).
- **Iterate via variants in a lab folder, don't overwrite live.** Generate into `tools/_generated/blocklab/`,
  review in context (`scene_block_house.py`, `scene_block_mine.py`), pick by looking, then copy the chosen
  variant over the live placeholder. (Full workflow in block_prompts.md.)
- **Verify by LOOKING against the reference (the walls/gold), never by a number.** `coverage==100%` can be a
  baked background or a flat square.

## Adding / changing a block
1. Entity row (lean): ore block → `occupants.json` (`category: ore`, pickaxe-breakable, drops its ore
   item); wall → `placeables.json` (`category: structure`, key `wall_*`). `[1,1]` footprint, `bc` pivot.
   **All WALLS are `sprite_w 16 × sprite_h 32`** (2 cells tall = door height) so they line up with doors and
   each other — keep every wall this size. (Ground/ore blocks are `16×20`.) A past bug left wood/brick walls
   at 16×24 / 16×20 and they fell short of the door; standardized to 16×32.
2. Catalog row in `tools/art/catalog/blocks.json`: `{ "surface": "..." }` (a full-frame material, e.g.
   `"rows of warm red-brown BRICKS with pale mortar"`) or `{ "fleck": "..." }` for an ore (renders as
   "grey STONE studded with {fleck}"). Make the surface a FULL, textured face — bland/low-contrast text
   ("solid grey stone") renders empty; enrich it ("rough cobbled grey ROCK, varied tones, cracks").
3. Generate **2 attempts** with `ab_generate.py` (A live, B in `tools/_generated/ab/`).
4. **Verify tiling AND look:** `python3 tools/zonegen/scenes/scene_block_tiling.py` (3×3 patch per block +
   walls as houses) → view `tools/_generated/previews/block_tiling.png`; or build the direct composite. The
   block must read as one continuous surface with no seam, no border, no band. Reroll the dud variant.

## Variants
Wall **visual variants** (`wall_wood` planks vs `wall_wood2` logs) are for picking a look — keep them out of
gameplay collections until one is chosen; delete the loser.

Cross-cutting: art data model in [object_pipeline.md](../art/object_pipeline.md); underground placement in
[caves.md](caves.md).
