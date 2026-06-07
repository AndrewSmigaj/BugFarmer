# Scaffolding scratchpad — notes to fold into skills/guides

Running list of things learned while building (so we don't re-investigate). Each note says
WHERE it should land. Promote items into the real skill/guide, then strike them here.
Working doc — not canonical; the skills/guides are.

> **FOLDED (2026 session) — the sections below are now in the real docs:**
> add-object/object_pipeline notes → `add-object` skill + `object_pipeline.md` (art data model);
> author-zone/house notes → `author-zone` skill + `house-building.md` + `feature-yard.md`;
> item & inventory model → `architecture_items.md §0` + `game_design.md §11.5/§19`.
> Kept below for reference; the **general tooling TODO** at the bottom is the only still-open item.

## → add-object skill / object_pipeline.md
- **Quality axis is just `sell_price`.** The game treats every placeable as an independent
  item — it does NOT need variant/tier grouping. "Fancy vs plain" lives in the AUTHORING
  scaffolding (furniture collections), never in entity data. (Hard-won: we briefly added
  variant_group/tier/menu_group/happiness to placeables.json and reverted it.)
- **Don't add gameplay fields to the schema ahead of the feature.** e.g. power/fuel flags,
  happiness — add them only when the system that reads them is being built.
- **Bulk content adds:** a simple spec→entry emitter is fine for many new entries, BUT:
  - the entity JSONs have INCONSISTENT hand-formatting and do NOT survive a `json.dumps`
    round-trip → prefer text-insertion that matches the file's style, or accept a
    one-time normalization. (TODO below: a canonical formatter would remove this pain.)
  - `json.dumps({id:entry}, indent=2)[2:-2]` is already 2-space-indented at the entry level
    — do NOT re-indent it (I added 2 extra spaces and produced 4-space entries the first time).
- **Drops must reference a real item id.** placeables ARE items (drop self is fine). For
  `occupants`/`natural` that should be gatherable, ADD the matching `items.json` resource
  entry (e.g. flora → `chamomile`, `berries`) so server load stays valid.
- **Data-but-no-art renders as a category-colored placeholder** automatically
  (`make_scene.CATEGORY_COLORS`) — so add data first, lay out scenes, generate art last.
- **OBJECT_MATS** needs an override for non-wood materials or the keyword guesser defaults to
  wood: stone/marble tops (counter_fancy, dining_table_fancy), metal (range_stove, mirror),
  glass-ish (aquarium). Check the prompt with `--dry-run` before spending.

## → author-zone skill + docs/guides/house-building.md
- **Furniture COLLECTIONS** (`features/furniture.py`): a collection = a self-contained
  look/feel set mapping role→id; `pick(role, collection)` falls back to BASIC. Add/remove a
  collection as a UNIT (basic, fancy now; tropical/modern/rustic later — ideally own modules).
  Templates take `coll=` and call `pick(role, coll)`; bind per-room via
  `house.styled_rooms(specs, collection)`. (NEW — document in the guide + skill feature index.)
- **Footprint must match across a role's basic/fancy ids**, or `wall_run`/anchor math shifts
  the piece. Exception: flat, non-reserved decor (rug) can differ in footprint (drawn under
  furniture). Keep tier siblings the same footprint.
- **New feature modules to index in the skill:**
  - `features/yard.py` — `fence_rect`, `yard(... gate, path_to, ground, decor)`
  - `features/terrain.py` — `hpath`, `vpath`, `pond`
  - `features/garden.py` — `crop_bed`, `flower_patch`, `fruit_around`
  - `houses/layouts.py` — `row_house`/`t_house`/`plus_house` (3/4/5 rooms) + `bbox`
- **Scene dressing placed near reserved cells:** run `is_free()` AFTER the fence/occupants are
  placed, not before — pre-filtering against a stale state put lamp posts on the fence (18
  warnings). Or place dressing strictly outside/inside the perimeter line.
- The player house (`houses/player_house.py`) now uses the **fancy** collection (it's the
  "rich showcase"); scene1 re-renders fully once fancy art exists.

## → docs/guides/game_design.md (design captured this session)
- §11.6 Power & electrification (windmill/hydro/generator, linked-placement line tool shared
  with rail/track, coverage-radius aura, fuel-fed vs electric machines).
- §11.7 Cooking & stoves (wood stove 1 dish + fuel → bigger → electric range needs power).
- TODO still: content-diversity philosophy note (AI artists → lean into variety; price = quality).

## → item & inventory model (fold into docs/product/architecture_items.md + add-object skill)
The kinds of thing in the game, and how art maps to them:
- **Tiles** (`Resources/Tiles/`, opaque, per-cell ground): grass, dirt, garden_plot, floors, paths. NOT rugs.
- **Placeables** (`Objects/`, `placeables.json`, grid footprint ≥1, ownable, can grant bonuses):
  - furniture / decor / lighting / structures;
  - **flat placeables** (rug): `flat:true`, drawn under furniture, ON TOP of the floor tile — a rug is an
    OWNED inventory item with a footprint + bonus, **not a tile**;
  - **blocks** (dirt/stone/ore/wood/wall): placeable subtype that tiles into a grid; breakable.
- **Free/collectible items** (no grid cell; placed-anywhere, picked up): the bobbing drops — broken
  blocks, tree-drop wood, fallen fruit, **cut flowers/herbs/mushrooms**.
- **Tools/weapons** (`items.json`): held/swung; own icons; swing visuals later (player-held gear = Pipeline B).
- **Resources/seeds/consumables** (`items.json`): wood, fiber, ore, bars, crystal, seeds, potions, fish.
- **Bugs**: free-placed via a later RELEASE mechanic.

Decisions (2026 session):
- **Plants are FREELY placeable (NOT grid-locked) — updated design.** The engine places flowers/herbs/
  mushrooms/small flora at any sub-cell float position, at varied scale, in varied shapes/sizes (some ~2
  units tall); NOT one-per-cell, NOT uniform. Only constraint: can't overlap occupied space (block /
  placeable footprint / deep water). Cut plants are still inventory items. Engine: fine with the
  frontier-gated sync — static non-colliding decor, not swarm entities; placement just needs an is-free
  check. (See `architecture_items.md`.)
- **Inventory icons split two ways:**
  - **Derived (no art authored):** placeables, blocks, cut flowers/herbs → icon = a MINI of the existing
    world `Objects/{id}.png` (same art as the bobbing drop). Build a downscale step when the inventory
    needs it; do NOT gen `_icon.png` for these.
  - **Authored (`Items/{id}_icon.png`, catalog `items` family):** only items with NO world sprite — raw
    resources, tools/weapons, seeds, potions, fish.
- When a block breaks, the floating drop is a MINI of the ACTUAL block sprite (not a generic icon);
  same principle drives the derived inventory icon.
- TODO: add an `items` family to the art catalog for authored icons; add a derive-icon step (downscale
  world sprite → `_icon.png`) to the pipeline when inventory art is needed.

## → findings from the underground cavern scene (scene_underground_caverns.py)
- **Block/wall tiling reads sparse in the preview:** block occupant sprites (16x20, `bc` pivot) don't
  fully cover their cell, so the ground (cave_floor) shows through as grid lines and a SOLID rock field
  reads as a sparse grey grid. This is the deferred "wall/block visual tiling consistency" BACKLOG item
  — confirmed by the render. Placement logic is correct; it's the sprite coverage. Fix candidates: full-
  bleed block sprites (no transparent margin, top-surface fills the cell) and/or the renderer drawing
  blocks cell-filling. Iterate-heavy.
- **Natural rock features mis-route to the PLANT art family:** `crystal_quartz`/`stalagmite`/`rubble`
  (and existing `crystal_*`/`bone_pile`) are `category: natural` → `build_prompt` uses NATURAL_ART_DIRECTION
  ("PLANT/TREE… leaves/petals"), which is wrong for minerals. BEFORE generating cave art, add a **mineral
  family** (a rock/crystal art-direction in style.json) and route rock-like natural ids to it (e.g. a key
  set, or a `family` hint in the catalog row). Until then, leave cave-feature art as placeholders.
- Cave-field logic is inline in the scene; if it settles, promote to `features/cave.py`
  (`stone_field` + `carve_cavern` + `ore_vein`) — analogous to house.py.

## → findings from the underground build (caves, house, ant colony)
- **No bug-art pipeline:** `gen_sprites.py` has sources placeables/occupants/items/terrain but **no
  `bugs` source/dest** → can't generate new bug sprites (they live hand-made in `Resources/Bugs/`).
  The NEXT task (segmented centipede/millipede sprite sheets) needs a bug path: add a `bugs` source →
  `Resources/Bugs/{id}.png` + a bug art family in style.json, and a bug species data file.
- **Mineral family works:** catalog `"family": "mineral"` routes crystals/rubble/bone to a faceted-rock
  art direction (not the plant family) — crystals now render as crystal. Reuse the `family` override for
  any future non-plant `natural` id.
- **Bug sprites are ≈8px** (swarm-sized); in scene previews place them at `scale≈2.4` to read (ants on
  dark cave floor are still lowish-contrast — a lighter preview "trail" variant would help).
- `features/cave.py` (carve_tunnel/carve_cavern/place_pool/fill_solid) is the underground analogue of
  house.py. The ant-nest tunnel/file logic is inline in `scene_ant_colony.py`; promote to `features/ant.py`
  if reused. `place_pool`/`fill_solid` guard against flooding/overwriting occupied cells.

## → findings from the overnight block/bug/encyclopedia run (fold into object_pipeline.md + add-object)
- **CORRECTION (final) — blocks use a SEAMLESS OPAQUE MATERIAL FACE, like a ground tile** (`build_block_prompt`, mirrors `build_tile_prompt`): opaque (transparent comes back BLANK ~half the time — verified raw `alpha[0-4]`), fills the whole frame with the material (no baked bg, no border), NO top-surface/front-lip (that cube prompt banded everything + put a non-brick top on the brick wall). 2 attempts each, pick the tiling one, verify by LOOKING (coverage==100% can be a baked bg). See `feature-blocks.md`. NEVER change the flow to fix a few sprites — reroll.

## → PLANT art + placement system (brainstorm — fold into a plants guide + scaffolding)
Start a PLANT section mirroring blocks (own prompt approaches + variants + viewer + guide). Approaches/Qs:
- **Free placement (not grid):** a `scatter`-style feature that drops plants at FLOAT positions with jitter,
  varied per-instance scale, and an **is-free check** (no overlap with occupant footprints / blocks / deep
  water). Support patches (clusters) and lone plants. Reuse the existing sub-grid float path that
  `place_decor` / `place_bug` already use (cx,cy floats + `mult` scale), instead of one-per-cell occupants.
- **Scale & shape:** plants render sub-cell (often < 1 cell); some span ~2 cells tall (tall flora, saplings,
  big mushrooms). Author art at a known unit height so the renderer scales correctly; allow non-uniform.
- **Art prompt approaches (like block_prompts):** e.g. (a) single clear specimen on transparent, (b) a small
  natural clump, (c) top-down vs 3/4 framing — choose per plant type. Variants in a plant-lab folder; same
  viewer flips them (the viewer is already generic — needs a "free-placed decor" scene record, see below).
- **Viewer wiring:** plants are decor (floats), not grid occupants — to make them swappable in the viewer
  we'd record decor draw-rects too (like the block/tile rects) and overlay variants there. Small extension.
- **Depth/biome variation** (the "floor/plants match as you go deeper" idea): a later ZONE-system behavior
  (swap tile/flora sets by depth/biome), NOT a single sprite — capture as its own design item.
- **Engine/sync:** static non-colliding decor, no swarm-sim load; validate a real place-plant action with
  the sync-harness when it exists, but expect no frontier-gating stress.

## → general tooling TODO (separable, low-risk)
- **`tools/format_entities.py`** — canonical pretty-printer for the entity JSONs so they
  round-trip and bulk edits (by hand OR tool) stay clean. Optional but would remove the
  formatting friction above.
- Consider category-level **defaults** in the entity schema later (touches Go + Python loaders)
  so a fancy variant is ~4 lines instead of a full 25-line `world`/`breakable` block.
