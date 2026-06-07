# Block prompts — the bake-off workflow

How we dial in the **block** sprites. A block is **3D**: a wide lit **TOP** surface with a short, only-
slightly-darker **FRONT** face beneath it. Stacked in a grid the **tops line up and the fronts show** — it
reads as a wall of blocks, exactly like the stone wall / wood wall / gold block. (A flat square with no
front face is WRONG; a baked black/white background is WRONG.)

The prompt that gets there is **still being tuned**, so we tune it with a bake-off instead of guessing.

## The bake-off
- **Prompt approaches** — three *different prompts*, same block, **shared style block**, different technique;
  defined in `tools/blocklab.py` (`SHARED_STYLE` + `APPROACHES`), in descriptively-named folders:
  `01_described`, `02_explicit_dimensions`, `03_grid_check`.
- **Variants `1 / 2 / 3`** — three random samples of one prompt (gpt-image-1 is stochastic). NOT different prompts.
- Run: `python3 tools/blocklab.py` → fills `tools/_generated/blocklab/<approach>/<block>_{1,2,3}.png`.
  Scope it: `--approaches 02_explicit_dimensions --blocks stone_block --variants 3`.

### The three approaches (technique differs, goal identical)
- **Shared style (all):** front-on, slightly-above orthographic (not isometric/3D); wide lit top + short
  darker front; tops line up, fronts show; **grey stone (no green/blue)**; thin/soft seams (no thick black
  lines, no dark border); minimal bevel; full-width bleed; crisp.
- **`01_described`:** plain prose describing the top/front and that stacked tops line up.
- **`02_explicit_dimensions`:** exact proportions (top ≈ upper 80%, front ≈ lower 20%, ≤1px bevel, front
  ~15% darker, no outline).
- **`03_grid_check`:** describes the 3×3 tiling and tells the model to ensure the tops connect with no
  gap/offset and seams stay thin — "would the tops line up? if not, widen the top, lighten the seam."

## The review + promote workflow (reusable for any iterate-heavy art)
1. Generate variants into the lab folder (above) — never over the live sprite.
2. **Run the Design Lab:** `python3 tools/lab_server.py` → open `http://localhost:8765`. It renders the
   scenes (the SAME ones in `tools/_generated/previews/`), recording each block/tile's draw position.
3. **Review in context:** pick a scene, zoom, step each block/tile's approach/variant — the scene redraws
   live (variant overlaid back-to-front; nothing is pre-rendered per variant).
4. **Apply (set live):** the **Apply** button promotes the chosen variants to the live game sprites
   (`Resources/Objects|Tiles/{key}.png`, `.meta` patched) and re-renders the previews; the selection is
   saved in `blocklab/selection.json` and remembered. See `tools/lab/README.md`.
5. The live sprite is a **placeholder until replaced** — never overwritten by an unreviewed gen.

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

## The viewer is reusable; a Unity panel is later-maybe
The Design Lab server (`tools/lab_server.py`) is generic: add a variants folder + a scene
that places the item, re-run it, and you get the same flip-and-pick flow for bugs/plants/furniture/etc. A
Unity in-engine EditorWindow (sliders inside the running game) is a possible later addition — not built
(the lightweight HTML viewer was chosen for now).

See also [feature-blocks.md](feature-blocks.md) (block entity/catalog setup).
