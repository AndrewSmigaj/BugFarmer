# BugFarmer Sprite Pipeline (tested, working — 2026-06-03)

The pure-Python pipeline that turns gpt-image-1 output into clean, cohesive,
correctly-scaled pixel art. Three scripts, run in order. No ComfyUI, no jq.
(Supersedes `COMFYUI_CLEANUP_PIPELINE.md`, which described a ComfyUI flow we
don't use.)

```
gen_sprites.py   →  Resources/{Tiles,Objects}/*.png   (raw, fuzzy, 1024px)
pixelclean.py    →  tools/pixelclean_out/{Tiles,Objects}/*.png  (crisp, clean)
make_scene.py    →  tools/previews/scene.png           (eyeball without Unity)
```

All paths below are relative to repo root `C:\Users\emily\BugFarmer\`.

---

## 1. gen_sprites.py — generate

Reads entity JSON (`nakama/data/entities/*.json`, `nakama/data/tiles.json`),
builds a category/pivot-aware prompt, calls gpt-image-1, decodes the b64, and
writes the PNG into `BugFarmerClient/Assets/Resources/{Tiles,Objects}/`.

- Model: **gpt-image-1** (gpt-image-2 rejects `background:"transparent"`).
- Tiles: `background:"opaque"`. Objects: `background:"transparent"`.
- `--dry-run` prints the prompt and spends nothing — always preview first.
- Canvas AR is the distortion lever: `canvas_size_for()` picks portrait /
  landscape / square from `sprite_w:sprite_h` so the runtime per-axis stretch
  doesn't squish the art.

```bash
python3 gen_sprites.py --category structure --keys wall_wood --dry-run
python3 gen_sprites.py --category structure --keys wall_wood        # spends $
```

**Output is "pixel-art-styled", not pixel art**: 1024px, anti-aliased edges,
messy near-duplicate colors, and a dark vignette toward the borders (which
causes visible grid seams on tiles). That's what step 2 fixes.

---

## 2. pixelclean.py — clean  ← the key lever

Turns the fuzzy 1024px output into true low-res pixel art. Writes to
`tools/pixelclean_out/` and **leaves the Resources originals untouched**.

Four transforms (`clean()` / `small_rgba()`):

1. **ALPHA-TRIM (objects only)** — `alpha_trim()` crops to the sprite's alpha
   bounding box BEFORE downscaling. **Critical**: raw gpt-image-1 output keeps a
   huge transparent margin; without trimming, the object collapses to a few
   pixels floating in the frame and reads tiny + off-anchor in-game. *(This was
   the bug that made the fence look wrong vs. the compare — re-added 2026-06-03.)*
2. **DOWNSCALE (area-average / `Image.BOX`)** to the asset's true target size,
   so anti-aliasing collapses into solid pixels. `PPC = 2` → clean to 2× the
   logical sprite size (32px per cell); the scene/game then NEAREST-upscale by a
   whole number, keeping pixels crisp. Tiles → `TILE_PX = 32` square.
3. **PALETTE-QUANTIZE (k-means, `scipy.cluster.vq.kmeans2`)** per asset, or one
   shared palette with `--shared` for set-wide cohesion. (sklearn is broken in
   this env — NumPy 2.x ABI clash — so we use scipy.)
4. **DE-VIGNETTE (flat-field, opaque tiles only)** so center and edges match in
   brightness and tiles copy seam-free. Objects instead get a hard alpha
   threshold (128) so edges are clean cutouts, not feathered.

```bash
python3 pixelclean.py                          # per-asset palette
python3 pixelclean.py --shared                 # one palette across the whole set
python3 pixelclean.py --compare wall_wood,fence_wood   # also writes before/after
```

`--compare` writes `tools/previews/cleanup_compare.png` (left = raw downscaled,
right = cleaned, each NEAREST-upscaled to fill a box). Good for judging a single
asset — but note it normalizes every asset to one box, so it does **not** show
relative scale or footprint; use the scene for that.

---

## 3. make_scene.py — preview

Composes a house+yard mockup PNG, faithfully reproducing the game's placement:
ground tiles + bottom-center-anchored occupants, y-sorted, each occupant
stretched to its `sprite_w × sprite_h` target (per-axis, like `TilemapManager`).
So distortion you see here is distortion you'd see in-game.

```bash
python3 make_scene.py                       # renders from game Resources
python3 make_scene.py --assets pixelclean_out   # renders from CLEANED assets
```

Output → `tools/previews/scene.png`
(= `C:\Users\emily\BugFarmer\tools\previews\scene.png`).
Layout (grid, ground rects, object placements) is editable at the top of the
script.

---

## Scaling model (verified — the preview IS the game)

- Everything renders at **PPU 16, cellSize = 1 world unit/cell** (16 logical px
  = 1 cell).
- Tiles = exactly 1 cell.
- Objects: world size = `sprite_w/16 × sprite_h/16` cells (runtime sets
  `localScale = targetSize / sprite.rect.width`, per-axis). So 16 → 1 cell,
  32 → 2 cells.
- Player sprites 32×48px @ PPU 16 = **2 cells wide × 3 tall**.

Because the runtime stretches the PNG to `sprite_w × sprite_h`, the PNG should be
**tightly-trimmed art** (hence step-2 alpha-trim). If the trimmed art's aspect
ratio ≠ the meta `sprite_w:sprite_h`, the stretch distorts it — fix by adjusting
the data, not the art.

---

## Known caveats / open items

- **Meta aspect mismatch** distorts some objects (e.g. `tree_oak` art is ~square
  but meta is 32×48 → stretched narrow). Fix per-asset in
  `nakama/data/entities/*.json` + the client copy.
- **Fence/wall "doubled posts"** in a row: current art is a self-contained
  segment, so adjacent cells double the posts. Needs a neighbor-aware piece
  system (or edge-bleeding connector art via `is_linear_connector` in
  gen_sprites). Tracked separately.
- gpt-image-1 **billing hard limit** has been hit mid-batch before; regen stalls
  until the limit is raised.
