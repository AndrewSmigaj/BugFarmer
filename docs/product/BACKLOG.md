# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

## Done (recent) — Village rebuild (guide-driven quality pass)
- **Village authoring guide** `docs/guides/authoring/village.md` — 13 town-design principles (focal
  point, road hierarchy, function clusters, density gradients, …) mapped to the primitives + a
  build-order recipe; linked from `authoring/README.md` + the author-zone skill.
- **New helpers** `tools/zonegen/features/village.py`: `shop_building()` (shell + wide sign + shelf
  rows + counter + NPC) and `plaza()` (paved square + fountain + benches/lamps + corner beds).
- **`place_bug` gains `flip=`** (zonebuilder + render + make_scene) so bugs face either way.
- **`scene_village.py` rebuilt**: organic road hierarchy (main 4 → connector 3 → side lanes 2),
  bigger lake, central fountain plaza, CLUSTERED buildings (civic: hall·market·grocer·store;
  production: carpenter+smith adjacent; residential cottages; lakeside boat store), market is now a
  shop building w/ merchant behind a counter, carpenter has the sawmill + goods in rows indoors,
  picket-fenced cottage + garden, clumped meadow with a forest rim. 0 warnings, validate OK.
- **New entities** (data + art): `sign_market_board`, `shop_shelving`, `fence_picket`/`gate_picket`/
  `fence_picket_weathered`, `garden_border_stone`/`_log`.
- FOLLOW-UP: build the real 256×256 `village_21` zone (save()-based) on this scene; iterate art.

## Done (recent) — Butterfly Meadow scenes
- **`tools/zonegen/scenes/scene_butterfly_meadow.py`** (64×52, **0 warnings**, validate OK) — the open
  meadow for `butterfly_meadow_11`: south village-road entrance (flower arch, signpost, spring/puddle),
  the **Flower-Clock Glade** (a colored-flower ring around a birdbath "sundial", composed from existing
  flowers), the **Great Milkweed Stand** (`milkweed_giant` + a milkweed colony swarming with monarchs),
  the **Basking Boulder**, the **Broken Fence Line** (split-rail run + leaning gate + orb-web), the
  **Lepidopterist's Blind** (tent/specimen case/crate/net post/lantern), scattered open-grown oaks +
  failed-farm relics, heavy flower/milkweed/tall-grass scatter, drifting butterflies/bees + a paper
  wasp and a yellowjacket.
- **`tools/zonegen/scenes/scene_meadow_forest_edge.py`** (60×46, **0 warnings**, validate OK) — the
  northern transition (renderer is north-up): warm flowery meadow at the bottom darkening to **dirt**,
  **threshold stumps** (`stump`/`stump_mossy`) with bracket fungus, the **fallen-log bridge**
  (`log_fallen`) across a boggy seam, a thickening **tree band** of pine/oak/dead-tree clusters, log
  piles + brambles + fern/mushroom understory, and the edge threats — a **millipede** and a
  **centipede** assembled from the existing segmented head/body/tail part sprites.
- **7 new lean placeholder entities** (catalog `look` rows in place): `milkweed_giant`, `clover_red`,
  `stump_mossy`, `log_fallen` (occupants); `broken_fence`, `boulder`, `specimen_case` (placeables).
  Queued in `art_needed.md`. PLACEHOLDERS only — no art generated.

## Done (recent) — starting-village town scene
- **`tools/zonegen/scenes/scene_village.py`** (80×80, **0 placement warnings**, validate OK): the
  full lived-in town for `village_21` — a N–S × E–W stone road crossing at a central **civic square**
  (well, fast-travel signpost, notice board, benches, founder statue, flower beds, lamp posts); the
  **six shops** ringing it (Town Hall in marble w/ columns + map table + mirror; open-air Market w/
  stalls + awnings + produce; General Store; Carpenter w/ furniture display + log/sawhorse/chopping
  block; Smith w/ exterior forge + anvil + coal bin + tool rack; Boat & Fishing Store on the SW
  **lake** with docks, a moored boat, anchor sign, nets, fish crates); an **Ecologist's cottage**
  (specimen shelves, terrarium, test garden), **3 themed NPC cottages** (window boxes / cat statue /
  laundry + veg patch) via `features/house` layouts + furniture collections; an **orchard** + **fly farm** on
  the edges; meadow scatter, road lamps, pollinators. PLACEHOLDERS only — no art generated.
- **24 new lean placeholder entities** added (`placeables.json` + catalog `look` rows): `wall_marble`,
  `column_marble`, 7 shop signs, `market_stall`, `awning`, `produce_crate`, `dock_plank`, `boat`,
  `mooring_post`, `fish_crate`, `fishing_net`, `coal_bin`, `lumber_rack`, `bait_station`,
  `veg_patch_sign`, `statue_founder`, `laundry_line`, `cat_statue`, `window_box`, `specimen_shelf`,
  `bug_terrarium_big`, `map_table_big`, `sofa_modern`. Queued for the art pass in `art_needed.md`.

## Done (recent) — sync stability + headless test infra
- Fixed the frontier-gated freeze (spurious resync — "caught up" was wrongly treated as a stall)
  and the reconnect seq-desync (stale `PendingInfluence` leaked to the next client). Details in
  `architecture_swarm_sync.md` §11.
- World lifecycle: pause-when-empty + `world_enter` (singleton Normal/Test worlds; the frontend no
  longer creates worlds).
- Test infra: headless `.NET` sync-harness (`tools/sync-harness/`, incl. a reconnect scenario),
  test-zone generator (`tools/make_test_zone.py`), `sim_test` zone; single-source zone config
  (removed `debug_mode` + `species_debug.json`).
- New world-select login (`WorldMenu`).

## Done (recent) — overnight: new scenes + bug pipeline + encyclopedia
- **Blocks/walls — MISTAKE, being corrected:** an opaque-generation change I made (`is_block_like` →
  `background="opaque"`) was WRONG — it baked black/white backgrounds and the blocks didn't tile; a
  related `ab_generate` bug turned `cave_floor` into a chest. Reverted to the standard transparent+crop
  flow; regenerating each block/wall as 2 variants matched to `wall_stone`, verified with
  `scene_block_tiling.py`. `wall_stone` (untouched) is the standard. Guide rewritten with HARD RULES.
- **A/B sprite workflow:** `tools/ab_generate.py` (A live + B in `tools/_generated/ab/`) + `contact_sheet.py`
  A/B sheets in `previews/ab_review/`. Every new sprite has an A/B pair to pick from.
- **Underground scenes:** caves improved (quartz blocks, wider rail tunnel + wood supports, more dirt,
  shape labels); underground house rebuilt **flush in rock**; NEW **mining camp** (campfire+spit, tents,
  miners via a new player palette, custom sign); **ant colony 2×** (egg room + queen + tunnel to a
  mushroom cavern). Previews in `previews/` (flat, one `scene_<name>.png` each).
- **Bug pipeline:** `bugs` source → `Resources/Bugs/` + a `creature` art family; **segmented centipede &
  millipede** (head/body/tail ×2, mix-and-match) + **scorpion**.
- **New surface scenes:** `scene_beefarm_woods` (apiary + meadow + woods + stream) and `scene_desert`
  (sand + sand_block, road, old inn w/ neon sign, weather outpost + antenna + windmill, oasis, cacti,
  scorpions) + ~20 desert entities.
- **Encyclopedia (`docs/product/encyclopedia.md`) + `brainstorm_items.md`:** ~50 bugs (incl. water bugs)
  across ~16 families ×3 difficulty tiers + 21 new plants — data + catalog + A/B sprites being generated.
- `docs/product/underground_review.md` — proposals for camp + ant-colony additions.

## Done (recent) — underground zone scenes + guides + content
- **Caves guide + primitives:** `docs/guides/authoring/caves.md` + `features/cave.py`
  (`carve_tunnel` natural-meander/straight, `carve_cavern` shapes, `place_pool`, `fill_solid` with a
  rarity-tiered ore table). **Mineral art family** (catalog `"family":"mineral"`) so crystals/rubble/bone
  render as faceted rock, not plants. New entities: `ore_tin_block`+`tin_ore`, `mine_rail`, plus
  `crystal_quartz`/`rubble`/`hard_stone_block` and the mining props.
- **Scenes (all 64×64-ish, full real art, 0 warnings):** `scene_underground_caverns` (man-made rail
  tunnel vs natural meandering tunnels, varied caverns, cave mouth, ore veins, pool, fauna),
  `scene_underground_house` (stone house dug into a cave), `scene_ant_colony` (`ant-colony.md`:
  branching nest + ant-file trails).
- **Content batch (+27, art generated):** mushrooms (blue/cluster/morel/bracket/inkcap), geode, mining
  equipment (tool_rack, wheelbarrow, ore_pile, powder_keg, mining_bucket), furniture (ottoman,
  chaise_lounge, vanity, kitchen_island, bunk_bed, throne, bar_cart, bathtub, stone stool/bench),
  decorations (statue_bug, suit_of_armor, globe, gramophone, easel, telescope).

## Done (recent) — data-driven art layer + content + house collections
- **Art is data-driven:** `tools/art/style.json` (global look + per-family blocks + palettes) +
  `tools/art/catalog/*.json` (per-item `look`/`materials`, one file per category). `gen_sprites.py`
  is now a thin assembler (1350→~740 lines); prompt output is byte-identical to before. Dead
  player-art spikes removed (kept `segment_sheet` + frame helpers for the multi-frame item).
- **Furniture/decor +34** plain valued entries (quality = `sell_price`); **+12 wild flora** occupants
  + **+12 resource items**. Art generated for the new furniture + flora (data-driven catalog).
- **Furniture collections** (`features/furniture.py`, basic/fancy, `pick(role, coll)`, `styled_rooms`)
  — fancy/appropriate-for-wealth knowledge lives in the scaffolding, NOT game data. New scene
  `scenes/scene_houses.py` (room counts × collections, each in a yard). New primitives:
  `features/{yard,terrain,garden}.py`, `features/house.py` layouts (3/4/5-room). Guides: `house.md`
  (updated), `yard.md` (new); `object_pipeline.md` + `add-object` skill rewritten around the catalog.
- **Item/inventory model written down** (`architecture_items.md §0`): placeable vs free/collectible,
  derived vs authored icons, bonus diminishing-returns keyed off `id`. Content-diversity philosophy
  (`game_design.md §19`). Power/cooking design (`§11.6/11.7`).

## Done (recent) — zone-authoring scaffolding + house system
- Builder library `tools/zonegen/` (ZoneBuilder + occupancy masks), `make_scene` renders from data
  with category placeholders, `author-zone` skill, `feature-building`/`feature-vegetation` guides.
- **House composer** (`features/house.py`): multi-room buildings from shared-wall rects (⊥/L),
  interior doors + windows + doorway-avoidance, and a reusable room-template library
  (living/bedroom/kitchen/crafting) following the south-facing **facing rule**. Guide:
  `docs/guides/authoring/house.md`; reusable house `scenes/player_house.py`; scenes live in
  `scenes/` and compose houses (e.g. `scenes/scene1_player_farm.py`).
- New entities (data + `OBJECT_DESC` ready, art pending): fridge, stove, sink, counter, keg, sofa,
  armchair, nightstand, dresser, rug, bug_terrarium, vase, window_4pane, door_square.
- **Engine fix**: `TilemapManager` tall-sprite vertical baseline (center-pivot PNGs + zeroed bc
  offset made beds overshoot); preview renderer flipped to match game orientation (+Y north).

## Now — Scene 1: player house + fly farm
- House DONE (the ⊥ cottage, full real art). Fly farm FIRST PASS done
  (`scenes/scene1_player_farm.py`): netted fly pen (apple trees, fallen/rotting fruit, flies on
  ground + netting, autonet, compost bin, broken net, apple crate, the farmer), orchard, garden
  (fountain, benches, beds, lamps), paths, scattered decor + butterflies/bee. Pending:
  - **Generate the farm art** (placeholders now): fountain, compost_bin, autonet, fly_netting,
    fallen_fruit, rotten_fruit, rock_small, rock_mossy — `OBJECT_DESC` ready in `gen_sprites.py`.
  - Iterate the garden/pen layout; confirm the **decorative-rock** decision (vs the old
    "no standalone rocks, use stone_block" rule).
  - **Unity Play test** of the tall-sprite pivot fix + orientation (verify in-game vs preview).

## Now — Safe cleanup only (no refactoring, no splitting files)
Tidy what's clearly safe; leave anything risky alone.
- ~~Delete dead player-art spikes in `gen_sprites.py`~~ DONE (removed `recolor_skin`/`SKIN_*`/
  `PLAYER_STYLE`/`char_sample_prompt`/`body_prompt`/`walk_sheet_prompt`/`build_walk_set` + their CLI
  flags; kept `segment_sheet` + frame helpers per the multi-frame item).
- Remove scratch/clutter and any empty dirs left over from earlier reorgs.
- No structural refactors, no god-class splits — those are deferred until we have a way to verify
  them (there are currently no automated tests).

## Next — Get multi-frame sprites working (hands-on, together)
Experimental and human-in-the-loop — we try things and look at the output together, not plan it up
front.
- First: see if gpt-image-1 will output a clean sprite sheet we can crop. Start with the garden
  bed (dry vs watered).
- If it won't: fall back to a base bed plus a separate water-drops layer (procedural or old-style).
  The plant is drawn on top as its own layer either way.
- Once a method works, reuse it for crop growth stages, then later bug animation frames.
- **Segmented bugs (centipede/millipede): head/body/tail sprite sheets** — the agreed next hands-on task.
  BLOCKER: `gen_sprites.py` has no `bugs` source/dest yet (bug sprites are hand-made in `Resources/Bugs/`);
  add a bug art path + family + a bug species data file before generating. Then chain head→segments→tail.

## Next — Zone-design guides cleanup
- ~~Consolidate the scattered/contradictory guides into one coherent set~~ **DONE** — `docs/guides/`
  split into `art/` (look & pipeline) + `authoring/` (zone/scene building, indexed by
  `authoring/README.md`); the dead `generate_zone.py` system (+ its `ZONE_GENERATION_GUIDE`/
  `BUILDING_TEMPLATES` guides) archived; zonegen code consolidated (`houses/`+`builds/` folded into
  `features/`+`scenes/`; scene registry → `zonegen/registry.py`; `artlab/` is now purely the viewer).
- REMAINING (design, its own plan): make generation **natural & non-rigid** — no dead-straight roads,
  no uniform scatter; encode that into the authoring primitives + guides.

## Next — Zone graphics: 6 preview scenes
Fill missing entity data, generate/clean remaining sprites, render 3 surface + 3 mining preview
scenes. Depends on the two items above.

## Later — captured, not scoped yet
- **Power & electrification + cooking progression** (design captured in `game_design.md §11.6/11.7`):
  windmill/hydro/generator → power unit with a coverage-radius aura (highlight covered cells at
  placement); a shared "linked placement" line tool (power lines AND rail/track — click start/end,
  reject if it clips); machines split into fuel-fed (wood stove) vs electric; stove cooking-capacity
  tiers. Add the power/fuel-requirement entity flag only when building this. Author a small
  **power/electronics demo scene** to tinker with it visually.
- **Placeable wall/block visual tiling consistency** — make placeable walls/blocks (wood/brick/iron/
  glass/marble + wood/stone) tile together cleanly. Iterate-heavy, token-spend; its own pass.
- **General-store catalog scene** — a shop (next to the produce market) with a buy-catalog of
  furniture/decor/valuables (gold pieces, piano, fancy whatevers).
- **Building-materials + rug/valuables content** — wall_brick/iron/glass/marble, window_wood/metal/
  fancy, rug_bearskin/fancy-patterns/simple, piano & gilded valuables (data + art via the catalog).
- Bug behaviour / AI.
- Authoring brand-new zones.
- Weapons / tools rework (currently weak).
- An enemy.
- Active/inactive zones: simulate bugs in detail only in zones that have players; cheaply
  aggregate the rest; pause a zone entirely when it has no one. Finer-grained than today's
  per-match pause-when-empty (which only idles when the *whole* world is empty).
- Free long-idle matches + clean up accumulated world metadata (matches currently idle when
  empty but are never freed; harness `world_create` runs leave stale metadata).
