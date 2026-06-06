# Object & Sprite Pipeline

How art gets into Bug Farmer. This is the canonical guide; it supersedes the old
`architecture_new_object_pipeline.md`, `OBJECT_CREATION_GUIDE.md`, and
`creating_objects.md` (all removed). There is **no ComfyUI** anywhere in the flow.

## Two pipelines, scoped by *what* you are making

The pipeline is chosen by the asset type — you never pick per-task:

| Pipeline | Use for | Tooling | API? |
|----------|---------|---------|------|
| **A — gpt-image-1** | **All world art**: objects, occupants, placeables, tiles, items, bugs | `gen_sprites.py` → `pixelclean.py` → `make_scene.py` | yes (OpenAI) |
| **B — hand-authored** | **Player sprite + player armor/clothing only** | `generate_player_sprites.py` | no |

Pipeline B writes explicit RGBA pixel grids in Python (no API, no cleanup) sized to the
entity's `sprite_w × sprite_h`, saving straight to `Resources/Player/`. It is a narrow,
dedicated lane — never use it for world objects. Everything else is Pipeline A.

---

## Pipeline A: gpt-image-1 → clean → preview

### 1. `gen_sprites.py` — generate
Reads the canonical entity JSON, builds a category-aware prompt, calls gpt-image-1,
decodes the base64 with Python (no `jq`), trims to the alpha bounding box with PIL,
saves into `Resources/`, and patches the `.meta` to pixel-art import settings
(`spriteMode:1`, `filterMode:0`).

```bash
# Preview the prompt only, no API spend:
python3 tools/gen_sprites.py --keys table_wood --dry-run

# Generate specific keys (default source = placeables.json):
python3 tools/gen_sprites.py --keys table_wood,chair_wood

# Generate a whole category:
python3 tools/gen_sprites.py --category furniture

# Other sources: occupants, items, terrain (tiles):
python3 tools/gen_sprites.py --source items --keys wood,fiber
python3 tools/gen_sprites.py --source terrain --keys grass --variants 3
```

Key flags: `--source {placeables,occupants,items,terrain}`, `--category`, `--keys`,
`--quality {low,medium,high}`, `--force` (overwrite existing), `--dry-run`, `--limit`.

Output destinations (the `dest_path` contract):
- `items` → `Resources/Items/{key}_icon.png`
- `terrain` → `Resources/Tiles/{key}.png` (opaque, full-bleed, no trim; `--variants` adds `_v2`, `_v3`…)
- `placeables` / `occupants` → `Resources/Objects/{key}.png`

## Art data model (prompts are DATA)

The prompt "knowledge" is **not** hardcoded in `gen_sprites.py` — it's data under `tools/art/`, and
`gen_sprites.py` is a thin assembler:

- **`tools/art/catalog/*.json`** — the per-item art, ONE FILE PER CATEGORY (`furniture, lighting,
  decor, kitchen?, structures, flora, crops, tiles, blocks`). Each row keyed by entity id:
  `{ "look": "<silhouette>", "materials": ["wood"] }`. `look` is the concrete description (without it
  the model invents a wrong silhouette — a "Wooden Door" came back as a cabinet). `materials` is
  optional — add it only when the keyword guesser is wrong (e.g. `range_stove` → metal). Files are
  organizational: the loader **globs and merges by id**, and special-cases `tiles.json` (`look`) and
  `blocks.json` (`surface`/`fleck`). Add an item = add a row (see the **add-object** skill).
- **`tools/art/style.json`** — the GLOBAL look in one place: `palettes` (the 6 material ramps) and
  per-FAMILY art-direction blocks (`object` face-on, `flora` organic, `block`/wall cube-tiling, `tile`
  seamless, plus `connector` and `net`). Edit this to change how *everything* looks; you don't touch it
  to add one item.

The assembled recipe (in `build_prompt`), driven by the entity's `category` + `world.pivot`:
`shared family art-direction → asset/category → catalog look → spatial(pivot) → design(category) →
[connector for fence/wall] → palette(materials) → closer`. Natural/crop ids use the organic `flora`
family (not the face-on style, which made foliage read as boxy blobs); walls (`wall*`) and linear
connectors (`fence*`) get the cube/tiling prompts so they join seam-free.

### 2. `pixelclean.py` — clean **in place**
gpt-image-1 returns fuzzy 1024px art with anti-aliased edges, near-duplicate colors, and
edge vignetting. `pixelclean.py` fixes all three and **overwrites the sprites in place**
under `Resources/{Objects,Tiles}` (single source of truth — no side directory to hand-copy):

1. **Downscale** (area-average / BOX) to 2× the logical size, collapsing anti-aliasing
   into solid pixels. The runtime then NEAREST-upscales by a whole number, keeping pixels
   crisp.
2. **Palette-quantize** (k-means) per asset, or `--shared` for one palette across the set.
3. **De-vignette** (flat-field) opaque tiles so they copy seam-free.

```bash
python3 tools/pixelclean.py                  # clean all tiles + objects
python3 tools/pixelclean.py --shared         # one shared palette (more cohesive)
python3 tools/pixelclean.py --compare bookshelf,fireplace   # write a before/after PNG
```

Re-running is safe/idempotent (the BOX downscale to the same target size and the
re-quantize are stable). It only touches `Resources/{Objects,Tiles}` — never `Player/`,
so Pipeline-B hand-authored art is untouched.

> **"DO NOT RESIZE" — what it actually means.** Do not *hand-resize* in `gen_sprites.py`;
> the sprite is saved trimmed at its natural bitmap size. `pixelclean.py`'s deliberate
> downscale-to-2×-logical **is** the intended clean final, which Unity then NEAREST-scales
> to `sprite_w × sprite_h` at runtime. The rule is "don't manually rescale art," not "never
> change pixel dimensions."

### 3. `make_scene.py` — preview
Composes a preview PNG that mirrors the game's placement rules (ground tiles +
bottom-center-anchored occupants, y-sorted, per-axis stretched to `sprite_w × sprite_h`)
so you can eyeball how sprites read together without opening Unity. It reads straight from
`Resources/`, so no `--assets` flag is needed.

```bash
python3 tools/make_scene.py            # -> tools/_generated/previews/scene.png
```

---

## Placement: the footprint-X rule

`CellToWorld` returns a cell's **center**. A multi-cell-wide footprint occupies cells to
the *right* of its anchor, so the sprite must shift right to center over the whole
footprint, not just the anchor cell:

```
worldPos.x += (footprint.x - 1) * 0.5 * cellSize;
```

Odd widths straddle symmetrically (no shift); **even widths shift half a cell**. Without
this, even-width objects (door, fireplace, bookshelf — `sprite_w` ≈ 2 cells) sit half a
cell off-grid. This is applied in both the game (`TilemapManager.RenderOccupant`) and the
preview (`make_scene.py`, using `world.footprint[0]`, *not* the stretched `sprite_w`).

---

## Entity data is canonical in `nakama/`, published to the client

`nakama/data/entities/{occupants,placeables,items,crops}.json` is the **single source a
human edits**. The Go server and every Python tool read only from there. The Unity client
needs its own runtime copy under `Resources/Data/entities/`, which is **published output —
never hand-edit it**:

```bash
python3 tools/publish_entities.py            # one-way copy canonical -> client
python3 tools/publish_entities.py --check    # report drift, exit non-zero (CI/sanity)
```

---

## Adding a new object — checklist

1. Decide the source file: `occupants.json` (world creatures/structures placed in zones),
   `placeables.json` (player-placed furniture/objects), or `items.json` (inventory).
2. Add the entry to the **canonical** `nakama/data/entities/*.json` with `category`,
   `sprite_w`, `sprite_h`, `world.footprint`, `world.pivot` (`bc` = bottom-center for
   grounded objects, `c` = centered).
3. If the silhouette isn't obvious from the name, add an `OBJECT_DESC` (and `OBJECT_MATS`
   if materials are non-default) entry in `gen_sprites.py`.
4. `python3 tools/publish_entities.py` to push the data to the client.
5. `python3 tools/gen_sprites.py --keys <key>` then `python3 tools/pixelclean.py`.
6. `python3 tools/make_scene.py` and confirm the sprite reads correctly and sits on-grid.

## Acceptance checklist (per sprite)
- Reads instantly as the intended object at game zoom; correct silhouette.
- Transparent background, no baked ground patch or cast shadow (except tiles, which are
  opaque and full-bleed).
- Even-width objects sit on grid squares in `scene.png` (footprint-X rule).
- Tiles/connectors tile seam-free.

## Future direction (not built yet)
Animation support, and a reliable way to crop individual frames out of a gpt-image-1
sprite sheet (the `walk-set` / `segment-sheet` spikes in `gen_sprites.py` are exploratory).
