---
name: author-zone
description: Use when creating or editing a game zone, or building an example scene/vignette for the zone guides. Covers the zonegen builder-library (feature primitives that coordinate through a shared occupancy model), placeholder-first composition, and rendering preview PNGs to review. Does NOT cover sprite generation (that's add-object / object_pipeline.md).
---

# Author a zone / scene

> **Craft vs mechanics:** deciding WHAT to build, whether it's interesting, and reviewing it as
> a PLACE → the **zone-craft** skill (brief → options → lenses → corrections ledger). This
> skill is HOW: the builder, primitives, previews, gates. For a NEW zone or an improvement
> pass, START in zone-craft; come here for the building.

Build zones and example scenes from reusable **feature primitives** that coordinate through a
shared occupancy model, compose with **placeholder squares** (never wait on art), and review by
**rendering a preview PNG and looking at it**. The preview is the test — there's no live game to
watch here.

## Where things go — READ THIS FIRST (so you don't invent folders)
**`docs/guides/authoring/ORGANIZATION.md`** is the rule. One question decides everything:
**reusable technique → `examples/<feature>`; a specific place → `zones/<zone>`; game content → `catalog/`.**
Previews live in exactly four folders (`catalog/ examples/ zones/ player/`); a scene renders to the folder
named in its own `PREVIEW = "..."` constant, via `python3 tools/world/previews.py`. Don't make new
top-level buckets, don't hand-type output paths — if a thing doesn't fit, it's a technique or a place; ask.

## Where the world lives (orient here first)
- **The system index:** `docs/guides/authoring/README.md` — the parts (builder · guides · scenes · the
  scene→zone→`view_world`→test pipeline) and how they fit. Read it first.
- **The whole map:** `docs/product/architecture/architecture_world.md` — the 24-zone grid, layout, river/roads,
  coordinates, per-zone species.
- **Per-zone design docs:** `docs/product/zones/<zone_id>.md` (intent: biome, species, landmarks, ecology).
  Start a new one from `docs/product/zones/_TEMPLATE.md`. Current build scope: `docs/product/zones/demo_slice.md`.
- **Which primitives per biome:** `docs/guides/authoring/biome-feature-map.md`.
- **Content to draw from:** `docs/brainstorms/<topic>/` (flora, fungus, trees, bugs, landmarks, decorations,
  materials, …) — mine these for what to place; `ecology_proposal.md` for how species relate.

## Make it RICH — brainstorm, don't do the bare minimum
A scene is a crafted vignette, not a checklist — too sparse reads as a tech demo; we have AI
artists, so content is cheap (`game_design.md §19`). **The brainstorm process, fields and
QUOTAS live in the zone-craft skill's brief** (one home for the numbers — fill it there and
persist it to the zone doc before building). New entities the brainstorm needs come in via the
**add-object** skill (placeholder renders immediately; layout never waits on art).

## Go slow; check before you call it done
This is an iterative craft loop, not a one-shot. Deliberately:
- Plan → build a first pass with placeholders → **render and actually LOOK at the PNG** → adjust
  composition → repeat. Crop regions (`render_builder(..., bounds=...)` to `/tmp`) to inspect detail.
- Before declaring a scene (or a plan) good: **run `b.lint()` and `dump` the building as a text grid**
  (`features.tilemap.dump`) — verify in TEXT first (0 defects, bar the expected wall-32/door-24 height),
  THEN read a rendered crop with a critical eye. Never call it good off a giant PNG alone, and don't
  rubber-stamp your own work. (Working rule: no "looks good" without lint output + a crop you've seen.)

## The loop
1. Read the zone document (`docs/product/zones/<zone>.md`) or decide the scene's contents.
2. For each feature, read its **feature guide** (below) + the cross-cutting style guide, and
   check **`docs/guides/authoring/CORRECTIONS.md`** for owner corrections touching your features.
3. Build with the `ZoneBuilder` + feature primitives (`tools/zonegen/`). **Author themed buildings as
   TEXT GRIDS** (`features/tilemap.stamp`/`dump`) — reason cell-by-cell, don't guess coordinates.
4. **`b.lint()` (verify in TEXT) → then `Read` a rendered crop**; iterate the layout (and the guide).
   Previews are plain PNG folders under `tools/_generated/previews/` (no html): a scene renders to
   `zones/<zone>/scenes/` (if it composes a real zone) or its theme folder (`surface/`, `underground/`…);
   the content catalog (`catalog/<group>/`) is rebuilt by `python3 tools/world/previews.py`.
   THE ROWS RULE: human-made things (orchard trees, shelves, stalls, bins, nets, trays) sit in
   rows/columns; even-spread is only for deliberately wild nature.
5. Placed a new object with no art yet? It renders as a labeled placeholder — add it to
   `docs/product/art_needed.md`.

## Builder — `tools/zonegen/`
- `ZoneBuilder(zone_id, W, H, base_tile=..., seed=..., name=...)` — the two on-disk grids plus the
  coordination masks `surface[]` (`water|path|building|farm|forest|grass`) and `reserved[]`.
  Key methods: `place_occupant(id, x, y)` (writes anchor + footprint cells; **refuses overlaps
  loudly** — no silent overwrite), `set_ground`/`fill_ground`, `place_player`/`place_bug`/`place_decor`
  (render-only dressing), `missing_art()`, **`lint()`** (text QA gate), **`blit(src, ox, oy)`**
  (scene→zone composition: anchor-grouped occupant collision, bounds clipping, optional
  base-tile transparency), `save()` (chunk-aligned zones) /
  `load(zone_id)` (edit an existing zone; derives masks).
- `features/` — feature primitives: **`tilemap.{stamp,dump}`** (author/verify a building as a char grid),
  `room.place_room` (building shells), `house.place_house` + `styled_rooms` (multi-room houses),
  `furniture` (collection catalog: `pick(role, coll)`), `yard.{fence_rect,yard,property_yard}` (fenced
  enclosures), `terrain.{path,smooth_paths,pond,stream,hpath,vpath,lake,shore_dress,forest,rock_patch,
  rock_mass}` (`lake` = multi-blob natural shapes + `shore_dress` per-arc banks; `smooth_paths` = the
  road-angle pass, run once after ALL roads; `rock_mass` = SOLID mineable masses; `path` = organic road,
  NOT dead-straight), `garden.{crop_bed,flower_patch,fruit_around,orchard}`, `scatter.scatter` (decor;
  `clumping` for organic patches), `village.{plaza,shop_building}` (plaza carries the civic props).
  `house.py` also has ready-made 3/4/5-room floor plans (`row_/t_/plus_house` — WIDE: budget slots per
  house.md's measured sizes). Each has a guide.
- `render.render_builder(b, out, scale, bounds=None)` — render a builder straight to a preview PNG
  (for scene vignettes; no zone files written). For a saved ZONE, use `tools/world/view_world.py` instead.
- **Precedence — place HARD features first so later ones route around them:** biome base → water →
  roads → buildings → farms → scatter. (`place_road` will pathfind around `reserved`; `scatter`
  only fills free grass.) Out-of-order placement is refused/warned.
- **Always** run `b.lint()` (verify in text) AND look at a rendered crop before calling a scene/zone done.

## Build & render an example scene
```bash
python3 tools/zonegen/scenes/<scene>.py    # build + render THAT scene to its PREVIEW folder + print lint
python3 tools/world/previews.py                  # rebuild the content catalog + ALL scene previews
```
`scenes/scene_cottage.py` is the worked piece (a text-grid 2-room home + `property_yard`); `scenes/
zone_village.py` is the full scene→zone example. Each scene declares its destination + render scale in
`PREVIEW = "..."` / `SCALE = N` constants; `scene_preview.py` is the one render path.

## Feature guides
**Full index + one-liners: `docs/guides/authoring/README.md`.** The ones you'll reach for most:
- `docs/guides/authoring/CORRECTIONS.md` — the OWNER-TASTE ledger (every correction, one line +
  pointer). Read whole at zone-craft Step 0; walk at review.
- `docs/guides/authoring/gallery.md` — annotated before/after pairs (what "better" means here).
- `docs/guides/authoring/research_*.md` — distilled domain research (composition, mining feel,
  settlements, coasts) — checkable rules + a counterexample each.
- `docs/guides/authoring/building.md` — rooms, walls, doors, building shells.
- `docs/guides/authoring/house.md` — multi-room houses: the composer, the furniture **facing
  rule**, room templates, ⊥/L shapes, **furniture collections** (basic/fancy), and the 3/4/5-room
  layout generators.
- `docs/guides/authoring/yard.md` — fenced yards/pens: `fence_rect`, `yard` (gate + path + decor).
- `docs/guides/authoring/roads.md` — organic roads: `terrain.path` (wander/fray/taper) — NOT dead-straight.
- `docs/guides/authoring/vegetation.md` — scatter (flowers/bushes/grass): density, spacing, **clumping**.
- `docs/guides/authoring/village.md` — composing a **town**: road hierarchy, function clusters,
  `plaza()`/fountain, `shop_building()`, density gradients, build-order recipe.
- `docs/guides/authoring/water.md` — lakes (multi-blob shapes), `shore_dress` arcs, docks
  (bridge_wood over water). Supersedes trees-and-ponds.md.
- `docs/guides/authoring/biome-feature-map.md` — **which primitive/guide per biome — START HERE to pick the right feature guide for this zone.**
- `docs/guides/authoring/caves.md` — tunnels, caves, water & **ORE (§4 = the ore doctrine)**: the underground.
- `docs/guides/authoring/ant-colony.md` — **ANT NESTS & trails** (blocks + `ant_brood` anchor + files-of-ants). **READ before building any ant zone** — a colony is biology, not a human settlement.
- `docs/guides/authoring/camps.md` — cliff edges, mine entrances & surface work-camps (surface→underground).
- `docs/guides/authoring/blocks.md` — resource & wall blocks (mineable/placeable cubes).
- `docs/guides/authoring/forest.md` — authoring forests: zone-scale balance, clearings.
- Worked multi-feature scene: `tools/zonegen/scenes/scene_houses.py` (room counts × collections, yards).
- Cross-cutting art style/perspective: `docs/guides/art/MASTER_STYLE_GUIDE.md`.

## Scene vs ZONE — and the pipeline to a playable zone
- A **scene** is a render-only vignette (no zone files). A **ZONE** is the 256×256 world the game loads.
- **Building pieces:** author each themed building as a `place_<thing>(b, ox, oy)` fn + a thin `build()`
  wrapper (`scenes/scene_smith.py`, `_carpenter`, `_market`, `_mayor`, `_ecologist`, `_cottage`,
  `_lakeside.place_boat_store`, `player_house`). ONE source of truth per building; the village/zone
  compose the REAL pieces, never cruder re-creations.
- **Compose → zone → save — TWO worked examples:** `scenes/zone_village.py` (the blit pattern: a
  composed scene blitted into a 256×256 builder via `ZoneBuilder.blit`) and
  **`scenes/zone_village_21_B.py` (the COMPOSE-IN-PLACE pattern — preferred for new zones):** real
  `place_*` pieces laid along organic roads directly in the zone builder, no stamped square; water →
  roads (+`smooth_paths` once, after all of them) → buildings → farms → scatter, then
  `Z.bug_spawning` and `Z.save()`. Size must be ×32; `save()` writes row/col 0,0 so patch them after
  for a real world-grid zone.
- **View the whole zone:** `python3 tools/world/view_world.py <zone>` → `tools/_generated/previews/maps/<zone>_detail.png`
  (north-up colour minimap; reads SAVED chunks, so save first).
- **Test in-game (no Unity):** `run-backend` skill starts the server, then the sync-harness joins +
  confirms load/tick/spawn (`tools/sync-harness`, `dotnet run -- --zone <id> --duration 20`). Edit zone
  DATA → `docker compose restart nakama`. Quick isolated mechanic test: `tools/world/make_test_zone.py`.

## EVERYTHING snaps to the grid except BUGS (changed rule)
Trees, plants, flowers, crops are real grid `place_occupant`s (the player plants them; saved to the
zone). `flower_patch` plants on the grid. Only **bugs** (`place_bug`) — and incidental pickups (fallen
fruit, lily-pads-on-water via `place_decor`) — are sub-grid floats. Space trees `min_spacing ≥ 3` so the
~2-tall sprites don't overlap. (See `vegetation.md`.)

## Bug spawning gotcha
A zone spawns NOTHING without a `bug_spawning` block, and **only species in `nakama/data/species.json`
spawn** — read `nakama/data/species.json` for the current roster (it grows as species are added; never
hardcode a list here); `bugs.json` ids lacking a species spec silently
fail. Use a `"zone"`-type area + generous `initial` for ambient bugs; `circle` areas on OPEN grass for
habitats (water/forest/buildings reject spawns).

## Notes
- **One preview file per scene** — overwrite the single canonical PNG in place; render transient crops to
  `/tmp` and delete. No `_crop`/`_v2` files in the previews dir.
- Across scenes, aim to place **every** world entity at least once (catalog coverage).
- Sprite generation is out of scope here — placeholders now, real art later via `add-object`.
