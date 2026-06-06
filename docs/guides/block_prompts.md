# Block prompts — the bake-off workflow

How we dial in the **block** sprites. A block is **3D**: a wide lit **TOP** surface with a short, only-
slightly-darker **FRONT** face beneath it. Stacked in a grid the **tops line up and the fronts show** — it
reads as a wall of blocks, exactly like the stone wall / wood wall / gold block. (A flat square with no
front face is WRONG; a baked black/white background is WRONG.)

The prompt that gets there is **still being tuned**, so we tune it with a bake-off instead of guessing.

## The bake-off
- **Prompt approaches `P1 / P2 / P3`** — three *different prompts*, all aiming at the same block, **sharing
  the style block** (so the look stays consistent) but using different technique. Defined in
  `tools/blocklab.py` (`SHARED_STYLE` + `APPROACHES`).
- **Variants `1 / 2 / 3`** — three random samples of one prompt (gpt-image-1 is stochastic, so the same
  prompt gives different images each call). Variants are NOT different prompts.
- Run: `python3 tools/blocklab.py` → fills `tools/_generated/blocklab/P{1,2,3}/{block}_{1,2,3}.png`.
  Scope it with `--approaches P2 --blocks stone_block --variants 3`.

### The three approaches (technique differs, goal identical)
- **Shared style (all):** front-on, slightly-above orthographic (not isometric/3D); wide lit top + short
  darker front; tops line up, fronts show; **grey stone (no green/blue)**; thin/soft seams (no thick black
  lines, no dark border); minimal bevel; full-width bleed; crisp.
- **P1 — described:** plain prose describing the top/front and that stacked tops line up.
- **P2 — explicit dimensions:** exact proportions (top ≈ upper 80%, front ≈ lower 20%, ≤1px bevel, front
  ~15% darker, no outline).
- **P3 — grid self-check:** describes the 3×3 tiling and tells the model to ensure the tops connect with no
  gap/offset and seams stay thin — "would the tops line up? if not, widen the top, lighten the seam."

## The variant-folder workflow (use this for any iterate-heavy art)
1. Generate into a **lab folder**, not over the live sprite: `tools/_generated/blocklab/P{n}/`.
2. **Review in context** — `scene_block_house.py` (walls in a room) and `scene_block_mine.py` (dirt/stone
   cliff + cave floored with a tile + pond), rendered per approach by swapping the candidate sprite in.
3. **Pick** the winning approach and the best variant per block (by looking — against the reference, never
   a coverage number).
4. **Promote:** copy the chosen `blocklab/P{n}/{block}_{i}.png` over the live placeholder
   `BugFarmerClient/Assets/Resources/Objects/{block}.png`. Keep the rest of the folder as the variant
   library so we can swap later.
5. The live sprite is a **placeholder until replaced** — never overwrite it with an unreviewed gen.

## Generation rules (don't drift again)
- Blocks use `build_wall_prompt` (the cube/top+front prompt) + **transparent background + crop** (the same
  flow that made the walls). **Never** opaque-on-a-field (black/white backgrounds), **never** a flat
  seamless texture (loses the front face). The deliverable is a 3D block — only the prompt *wording* is
  iterated, never the kind of thing produced.
- Blocks/walls keep **full width** (`vertical_only` trim) so they abut horizontally.
- `gen_sprites` and `ab_generate` must route blocks identically — don't let them drift.

## Cleanup / blur
`pixelclean.small_rgba` downscales the 1024 render to the sprite's dims with `Image.BOX` (averaging =
slight softening). Some softness is expected and fine; a 16×20 PNG also looks blurry if your image viewer
smooth-scales it (zoom with nearest-neighbor). Only sharpen the downscale if a block is clearly mushy.

## Later (not built yet): Unity variant panel
A small EditorWindow could list block types and step (slider/stepper) through `blocklab/*` variants,
swapping the live sprite and re-rendering a preview scene — so variants can be compared in real scenes
inside the editor. Feasible but a separate chunk of C# editor work; flagged for a decision, not started.

See also [feature-blocks.md](feature-blocks.md) (block entity/catalog setup).
