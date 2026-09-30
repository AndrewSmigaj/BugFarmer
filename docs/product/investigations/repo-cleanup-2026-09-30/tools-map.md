# tools/ — every folder, what it is, and what looks wrong (working map, 2026-09-30)

A throwaway map for the repo clean-up, asked for by the owner on 2026-09-30. It covers every folder and subfolder under
`tools/`, as found on disk today, including what git ignores. **Nothing has been moved or deleted.** The official map is
`tools/README.md`, which has drifted (see "What I noticed"). The full list of all 821 folders, with their numbers, is
generated into the appendix at the end, so none is missed.

**How to read the numbers.**
- **files**: every file on disk, counting subfolders.
- **in git**: how many of those files git tracks. The rest are ignored.
- **size**: size on disk.
- **last change**: the last commit that touched the folder.
- **used by**: how many other tracked files mention the folder's path. 0 means nothing points at it.

**Status words.**
- **live**: in use.
- **stale**: left behind by later work.
- **rejected**: kept only as a record of an idea turned down.
- **junk**: rebuilt automatically, never tracked.
- **archive**: old work kept on purpose.

## At a glance
| Folder | What it is | files | in git | size | last change | used by | status |
|---|---|---|---|---|---|---|---|
| `_generated/` | Everything the tools produce: previews, art runs, charts | 6,738 | 2,887 | 3.7 GB | 2026-09-26 | 106 | live; mostly ignored, except player art |
| `archive/` | Retired one-off scripts from the first months (sprite generators, zone builders, checks) | 30 | 30 | 0.4 MB | 2026-06-26 | 0 | archive; nothing points at it |
| `art/` | Art prompt data: the global look (`style.json`) and a prompt file per kind of object (`catalog/`) | 14 | 14 | 0.1 MB | 2026-07-18 | 23 | live |
| `bug_lab_configs/` | 81 bug-ecology tuning experiments (json) and the 3 scripts that wrote the sweeps | 85 | 85 | 0.1 MB | 2026-09-26 | 11 | live, but mostly finished experiments |
| `data/` | Entity-data tools: publish to the client, footprints, recipe checks, catalog coverage | 5 | 4 | tiny | 2026-07-06 | 22 | live |
| `ecology/` | Bug-ecology tuning: run a config, compare, charts, dashboard, the Bug Lab zone | 13 | 10 | 0.1 MB | 2026-09-26 | 23 | live |
| `gdd/` | Design-document review pages (GDD, item pass) and figures made for the owner | 13 | 6 | 2.5 MB | 2026-09-29 | 5 | live |
| `netcode/` | Checking that players' games agree: the sync diff, its test, two diagnostics | 4 | 4 | tiny | 2026-06-26 | 8 | live |
| `player_sprites/` | The player-art pipeline (whole outfits, gpt-image, pixel snapping), plus many old experiments | 96 | 51 | 1.1 MB | 2026-09-26 | 18 | live, with stale parts |
| `sim-determinism/` | A .NET program that runs the bug simulation headless to prove it's deterministic | 29 | 5 | 0.4 MB | 2026-07-19 | 13 | live |
| `sprites/` | World-art tools: generate, clean, fix import settings, tile experiments, some owner mock-ups | 54 | 37 | 0.5 MB | 2026-09-26 | 29 | live, with stale parts |
| `sync-harness/` | A .NET headless player used by the sync tests and the ecology runs | 56 | 7 | 2.0 MB | 2026-07-05 | 8 | live |
| `world/` | Zone viewing and previews: the catalog previews, the saved-zone viewer, test zones | 4 | 3 | tiny | 2026-09-26 | 27 | live |
| `zonegen/` | The zone and scene builder library, its features, and 53 scene files | 128 | 67 | 1.0 MB | 2026-09-27 | 46 | live |
| `__pycache__/` (and 9 more) | Python's compiled-code cache | — | 0 | tiny | — | — | junk |

## The loose files at the top of tools/
| File | What it is | status |
|---|---|---|
| `README.md` | "THE MAP", the official guide to tools/ | live, drifted |
| `.env` | Local secrets (the image API key). Ignored by git. | live, private |
| `make_scene.py` | The shared scene renderer, a library that `zonegen` imports | live |
| `ui_mock.py` | Paints proposed in-game panels with real data and icons (UI mock-ups) | live? unclear |
| `run_go_tests.sh` | Runs all the Go server tests in Docker | live |
| `run_sync_test.sh` | Headless two-player sync test (do both players see the same bugs?) | live |
| `run_sync_latejoin.sh` | The same for a player joining late: the determinism gate | live |
| `harness_persist_test.sh` | Checks that zones and farms survive a restart, with no Unity | live |
| `run_ecology_client.sh` | Starts one headless Unity client in ecology mode | live |
| `run_sweep.sh` | Runs a list of ecology tuning configs, one after another | live |
| `run_vlab_batch.sh` | Runs a batch of village-lab campaign configs | live? unclear |

## Each folder in detail

### archive/
Thirty retired files from June 2026:
- sixteen early sprite and tile generators (`generate_*_sprites.py`, `generate_garden_tiles.py`);
- the old zone builders (`generate_village_21.py`, `generate_zone.py`, `gen_village_21.py`, `gen_underground_31.py`,
  `gen_test_debug.py`);
- `regen_art.sh`, `finish_water_daynight.sh`, four `verify_*.sh` checks and `probe_fruit.sh`;
- two old guides (`SPRITE_GENERATION_GUIDE.md`, `sprite_guidelines.md`). Nothing in the repo refers
to them. They're superseded by `sprites/`, `zonegen/` and the harnesses. Git history keeps them anyway.

### art/ and art/catalog/
`style.json` is the global look sent with every world-art prompt. `catalog/` holds 13 prompt files, one per kind of
object: blocks, bugs, camp, cave, crops, decor, desert, flora, furniture, items, lighting, structures and tiles.
`sprites/gen_sprites.py` reads them. These are data, not code, so they could live with the other art data.

### bug_lab_configs/
81 json configs, each a set of changes to the ecology tuning, plus `_gen_sweep1.py`, `_gen_sweep2.py` and
`_gen_sweep3.py`, which wrote the sweeps. Used by `run_sweep.sh` and `ecology/run_config.py`. Most are finished
experiments whose results are in `_generated/ecology_charts`.

### data/
- `publish_entities.py` copies the canonical entity data from `nakama/data/entities` into the client.
- `footprints.py`, `recipe_graph.py` and `catalog_coverage.py` are checks on the entity data.
- `__pycache__/` is junk.

### ecology/
Everything for tuning the bug ecology:
- `run_config.py` runs one config end to end, and `compare_configs.py` scores configs against each other.
- `make_bug_lab.py` builds the Bug Lab test zone.
- `make_dashboard.py` and `plot_*.py` (seven of them) chart populations, interactions, performance and bug maps.
- `__pycache__/` is junk.

The shell runners for it sit loose at the top of tools/, and the configs are in `bug_lab_configs/`.

### gdd/, gdd/_build/ and gdd/_build/shots/
- `build_page.py` builds the GDD review page, and `build_items_page.py` builds the item-pass page.
- `ground_edges_sheet.py` and `ground_shapes_mockup.py` draw the owner-facing pictures made for the laying-ground
  design.
- Two templates.
- `_build/` holds the built pages and my test pages; it's ignored. `_build/shots/` holds one screenshot.

### netcode/
- `sync_diff.py` compares two players' streams: it's the sync gate. `test_sync_diff.py` is its test.
- `diag_determinism_provenance.py` and `diag_leg_divergence.py` are two diagnostics from the determinism work.

### player_sprites/ and player_sprites/aipipe/
The player-art pipeline. The approved procedure uses:
- `gen.py`, the only generator, which records every run, and `outfits.py`, the outfit list and prompts;
- `cut_walk_row.py`, `cut_outfit.py`, `flip_side.py`, `build.py` and `official.py`;
- `gallery.py` and `gallery_gif.py`, plus `preview_explore.py`, `procedure.py` and `gait.py`.

Mixed in are about 30 experiment and older scripts:
- swing studies: `swing_lab.py`, `swing_*` (six), `run_swing_lab.py`, `run_front_lab.py`, `motions.py`;
- design studies: `player_designs.py`, `player_designs2.py`, `vector_player.py`, `wearables.py`,
  `make_mannequins.py`, `net_options.py`, `showcase.py`, `walk_candidates.py`, `split_base_arm.py`,
  `rebuild_armor.py`, `gen_side_armor.py`, `gen_side_view.py`;
- the old paper-doll emitter `generate.py`, and `migrate.py`;
- scripts the September plan found stale: `promote.py` (targets a layout nothing uses), `render_animations.py` and
  `preview_all.py`.

`aipipe/` (`common.py`, `pixelsnap.py`, `run_pilot.py`) is the earlier mannequin pipeline. But `pixelsnap.py` in it
is still the live pixel-snapping code: `cut_outfit.py`, `cut_walk_row.py`, `procedure.py`, the two `gen_side_*` scripts
and `sprites/tile_experiments.py` import it. The live code sits inside an old folder. `__pycache__/` appears twice; it's junk.

### sim-determinism/, and its bin/ and obj/
`Program.cs` and `Shims.cs` run the client's bug simulation with no Unity and check that two runs agree. `bin/Debug/`
and `obj/Debug/` hold .NET build output; they're ignored junk.

### sprites/ and sprites/drawn/
World-art tools, several kinds in one folder:
- **The pipeline:** `gen_sprites.py` (generate from `art/`), `ab_generate.py`, `pixelclean.py` (the old downscale
  cleaner, which the 2026-09 art decision replaces with snapping), `fix_sprite_ppu.py` (import-setting fix),
  `recolor_sprites.py`, `make_diagonal_tiles.py` and `composite_tiles.py`.
- **Tile research:** `tile_lab.py`, `tile_experiments.py`, `tile_variants.py`, `tile_variant_sheet.py`,
  `tile_tufts.py`, `tile_scene.py`, `gen_tiles_handauthored.py`, `gen_dug_tiles.py`, `dug_context_sheet.py` and
  `blocklab.py`.
- **Code-drawn and placeholder art:** `generate_player_sprites.py` (the old hand-drawn player, "Pipeline B"),
  `placeholder_sprites.py`, `ui_sprites.py` and `veg_sprites.py`.
- **Owner-facing pictures:** `shovel_panel_mockup.py`, `title_art.py` and `tool_swing_gif.py`.

`drawn/` is the September code-drawn art, marked REJECTED for game art (11 modules and a README). Interface and block
art are still mine to draw in code, so parts of `canvas.py`, `palette.py` and `ui.py` may be worth keeping for that.
`__pycache__/` appears twice; it's junk.

### sync-harness/, and its bin/ and obj/
A headless .NET player (`Program.cs`, `Actions.cs`, `Scenarios.cs`, `WorldModel.cs`) that the sync tests and the
ecology runs drive. `bin/{Debug,Release}/net8.0` and `obj/{Debug,Release}/net8.0` hold .NET build output; they're
ignored junk.

### world/
- `previews.py` rebuilds the content catalog previews from the entity data.
- `view_world.py` renders a saved zone north-up.
- `make_test_zone.py` builds small test zones.
- `__pycache__/` is junk.

### zonegen/, zonegen/features/ and zonegen/scenes/
The zone-authoring library:
- `zonebuilder.py` is the builder, `render.py` renders a builder straight to an image, and `scene_preview.py` is the one
  way a scene becomes a preview.
- `features/` holds 10 building blocks: cave, furniture, garden, house, room, scatter, terrain, tilemap, village and
  yard.
- `scenes/` holds 53 scene files:
  - 16 `zone_*` builders: ant_colony_40, ant_lab, ant_tunnels_30, arena, bee_meadow_20, bug_zoo, collision_test,
    crafting_test, crawler_lab, feel_test, lighting_test, repro_test, underground_passages, village, village_21_B and
    village_21_lab;
  - 37 crafted places: ant_colony, ant_entrance, beach_cove, beefarm_woods, beekeeper_cottage, block_house,
    block_mine, block_tiling, butterfly_meadow, carpenter, colony_districts, cottage, desert, ecologist,
    fishing_docks, fly_farm, houses, lakeside, market, mayor, meadow_forest_edge, mine_entrance, modern_wares,
    orchard, queen_cathedral, road_angles, shore_arcs, smith, stonemason, underground_caverns, underground_house,
    underground_mining_camp, village, weaver, player_house, scene1_player_farm and a `_sketch_colony_layouts`.
- `__pycache__/` appears in all three folders; it's junk.

### _generated/ — the output tree
The README's rule is that all generated output lands here. Git ignores it all except `README.md`, the whole of
`player/`, two tile previews, and the `current/` and `comparisons/` chart folders.

- **`ab/`** (128 png, ignored): A/B sprite attempts from `ab_generate.py`.
- **`blocklab/`** (ignored): the block-prompt bake-off, in three rounds (`01_described`, `02_explicit_dimensions`,
  `03_grid_check`) plus `tiles/`.
- **`ecology_charts/`** (1,675 files, 298 MB; only 33 in git):
  - `_data/` holds raw CSV and logs.
  - There's one folder per zone: `ant_lab/`, `bug_lab/` (marked ARCHIVED, "do not tune here"), `village_21_B/` (the
    live tuning target) and `village_21_lab/`.
  - Each zone folder has `current/` (in git), `archive/` (ignored) and, for village_21_B, `comparisons/`.
- **`player/`** (2,874 files, **1.8 GB, all in git**): the player art.
  - Loose at its top: a README, `RUNS.txt`, `gallery.html` and a dozen comparison images and gifs.
  - `APPROVED/`, with `APPROVED/hands/`: the owner-approved picks and `DECISIONS.md`.
  - `bases/`: the two armless base bodies, which 122 files point at.
  - `hands/`: hand sets.
  - `props/practice-dummy/`: a practice dummy.
  - `outfits/`: 24 outfits (ant-carapace, beekeeper, beetle-shell, blackant, bronze, copper, entomologist, farmer,
    fireant, fisherman, glowworm, gold, hornet-stinger, iron, leather, moth-wool, padded, platinum, ranger, silver,
    steel, swamp-gear, wizard-robe and wood). Each has `animations/`. The built ones also have `frames/`,
    `gauntlet/` and `anim/`, and some have `archive/` and `tries/` with dated subfolders.
  - `explore/`: 127 generation runs, 120 of them with a RECORD.txt, plus their renders. By outfit: fireant 35, blackant 16,
    tip 14, ant 9, copper 8, bronze 7, platinum 6, wood 5, steel 5, beetle 3, and 1–2 each for wasp, ranger, leather,
    killer-bee, iron, hornet, fancy, swamp, scorpion, glowworm, gilded and fisherman.
  - `reviews/`: 35 dated review folders for the owner, 2026-08-03 to 2026-09-26: swing studies, hands, base ladders,
    rerolls, pixel proof, the art demo, the base pass, copper.
  - `archive/`: **1.1 GB in git.** It holds `2026-08-01_pre-redo/` (764 MB), `old/` (263 MB), `in-progress/`
    (38 MB), three 2026-07-28 copper runs, `bronze-helmet/`, `bronze-no-helmet/`, `_player_duplicate/`,
    `dead-ant-run-1601/`, `references/`, `runs/`, `current/` and a `RUNS.txt`.
- **`previews/`** (833 files, ignored):
  - `catalog/`: 21 categories (armor, beekeeping, blocks, bugs, consumables, crafting, crops, decorations, food,
    furniture, gear, lighting, nature, ore, resources, seeds, storage, structures, tiles, tools and weapon), 731
    pictures from `world/previews.py`.
  - `examples/`: 7 technique demos (blocks, buildings, ground-edges, roads, shaped_ground, tool_swings and water).
  - `zones/`: 12 zone renders (ant_colony, ant_colony_40, ant_tunnels_30, bee_meadow, bee_meadow_20, bug_zoo,
    butterfly_meadow_11, desert, feel_test, lighting_test, underground_passages_31 and village_21_B).
  - Four more that the rules don't list: `brood/`, `dug_experiment/`, `title/` and `ui/`.
- **`raw/`** (739 png, 1.16 GB, ignored; `raw/walk/` is inside): full-size gpt-image renders kept as a backup.
- **`scratch/`** (276 files, 267 MB, ignored): throwaway work in `ab_review/`, `bugs/`, `output/`, `plants/` and
  `refexp/`. `refexp/` holds 20 reference experiments: bed_side, bfly15, book_back, book_fix, book_ref, book_side,
  book_side2, book_side3, book_sweep, book_top, butterfly, fly, furn, oneeach, player, player2, sheet15, sheetraw,
  smoke and strips.
- **`tiles/`** (119 files, 47 MB; 3 in git): ground-tile research (`candidates/`, `candidates16/`, `previews/`,
  `raw/`, `refs/` and `tufts/`).
- **`variants/`** (ignored): block and wall variant sheets for cave_floor, dirt_block, stone_block, wall_marble,
  wall_stone and wall_wood.

## What I noticed (for the clean-up plan — nothing changed yet)
1. **Weight.**
   - `_generated/player/` is 1.8 GB and fully in git, and its `archive/` alone is 1.1 GB. That's most of the repo's
     size.
   - Removing files wouldn't shrink the history git already holds. Rewriting history is possible but risky.
   - Moving old archives to an outside backup, or to large-file storage (Git LFS), would keep new clones light.
   - It's the owner's art history, and the outfit procedure reads `RUNS.txt` and the RECORD files. So it's the owner's
     decision.
2. **The same job in several places.**
   - **Player art** is in `player_sprites/` (current) and in `sprites/generate_player_sprites.py` (old hand-drawn), and
     `player_sprites/generate.py` is the old paper-doll version.
   - **Pictures of zones and scenes** come from four places: `make_scene.py` (top level), `world/previews.py` and
     `view_world.py`, and `zonegen/render.py` and `scene_preview.py`.
   - **Testing and ecology** spread over the six shell runners at the top level, `ecology/`, `netcode/`,
     `sync-harness/`, `sim-determinism/` and `bug_lab_configs/`.
   - **Pictures made for the owner** are in `gdd/`, `sprites/` (`shovel_panel_mockup.py`, `title_art.py`,
     `tool_swing_gif.py`) and the top level (`ui_mock.py`).
   - **Art data** sits in `art/`, away from the art tools.
3. **Probably stale** (each needs checking against every reference before anything moves):
   - `archive/`: nothing points at it;
   - about 30 experiment scripts in `player_sprites/`, three of which the September plan already found stale;
   - the six tile-research scripts in `sprites/`;
   - `sprites/drawn/`, rejected, though parts may serve interface art;
   - `sprites/pixelclean.py`, the old downscaling route, still named in docs;
   - `bug_lab/` in the ecology charts, marked archived.
4. **The written rules don't match the folders.**
   - The README says all output goes to `_generated/`, but `gdd/_build/` is outside it.
   - It says previews have exactly four folders; there are seven, and `player/` isn't one of them.
   - It leaves out 14 scripts in `sprites/` and about 35 in `player_sprites/`.
5. **Junk on disk:** `__pycache__/` in 10 places and .NET `bin/` and `obj/` in two harnesses. They're ignored and
   harmless, but they add clutter.
6. **Nine loose scripts at the top level** could sit in folders by purpose, for example the test runners together.
7. **The item catalog web app** the owner asked for (2026-09-30) needs a home: a web page of every item with its
   description, sprite and stats, built from the entity data. It would sit naturally beside the catalog previews and
   the entity tools.

## Appendix: every folder under tools/ (generated 2026-09-30)
Each line gives: path | files (in git) | size | last change | used by.

- `tools` | 7281 (3220 in git) | 3681.9 MB | 2026-09-29 | 136
- `tools/__pycache__` | 1 (0 in git) | tiny | — | 0
- `tools/_generated` | 6738 (2887 in git) | 3673.6 MB | 2026-09-26 | 106
- `tools/_generated/ab` | 128 (0 in git) | 0.2 MB | — | 3
- `tools/_generated/blocklab` | 44 (0 in git) | tiny | — | 3
- `tools/_generated/blocklab/01_described` | 13 (0 in git) | tiny | — | 0
- `tools/_generated/blocklab/02_explicit_dimensions` | 13 (0 in git) | tiny | — | 0
- `tools/_generated/blocklab/03_grid_check` | 13 (0 in git) | tiny | — | 0
- `tools/_generated/blocklab/tiles` | 3 (0 in git) | tiny | — | 0
- `tools/_generated/ecology_charts` | 1675 (33 in git) | 297.9 MB | 2026-07-14 | 14
- `tools/_generated/ecology_charts/_data` | 243 (0 in git) | 30.9 MB | — | 1
- `tools/_generated/ecology_charts/ant_lab` | 182 (6 in git) | 9.9 MB | 2026-07-06 | 0
- `tools/_generated/ecology_charts/ant_lab/archive` | 176 (0 in git) | 9.4 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1734_ant_lab` | 13 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1734_ant_lab/bugmap` | 9 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1751_ant_lab` | 13 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1751_ant_lab/bugmap` | 9 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1804_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1804_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1830_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1830_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1836_ant_lab` | 7 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1836_ant_lab/bugmap` | 3 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1849_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1849_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1915_ant_lab` | 13 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1915_ant_lab/bugmap` | 9 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1931_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1931_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1944_ant_lab` | 13 (0 in git) | 0.8 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1944_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1957_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_1957_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2011_ant_lab` | 13 (0 in git) | 0.8 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2011_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2025_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2025_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2039_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2039_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2053_ant_lab` | 13 (0 in git) | 0.7 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/archive/2026-07-06_2053_ant_lab/bugmap` | 9 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/ant_lab/current` | 6 (6 in git) | 0.5 MB | 2026-07-06 | 0
- `tools/_generated/ecology_charts/bug_lab` | 126 (7 in git) | 17.7 MB | 2026-07-05 | 0
- `tools/_generated/ecology_charts/bug_lab/archive` | 119 (0 in git) | 16.6 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1331_P-ECO-4_director` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1511_P-ECO-phase0_predator-fix` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1537_P-ECO-phase123_three-tier` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1611_P-ECO-phase4_lifespans` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1714_P-ECO-phase4b_trophic` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1759_P-ECO-phase4c_balanced` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_1822_P-ECO-phase4d_drought-nectar` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_2050_00_baseline` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-17_2057_01_no_cull` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0132_A1_reach_vision_lo` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0137_A2_reach_vision_hi` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0142_A3_reach_speed` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0200_A5_reach_all` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0204_B1_feed_up` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0209_B2_strike_fast` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0218_B3_breed_bar_down` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0223_B4_hunt_always` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0228_B5_lethality_all` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0237_C1_fruit_fast` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0242_C2_fruit_plenty` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0247_C3_fly_breed_fast` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0251_C4_prey_rich` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0256_C5_prey_max` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0327_D3_nectar_amplitude` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0332_D4_nectar_rich` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0336_D5_survival_combo` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0349_E1_flycap400` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0354_E2_seal` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0359_E3_seal_default_fly` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0403_E4_centi_butterfly` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0408_E5_seal_centi_butterfly` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0418_F1_seal_reach` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0440_F3_seal_breedbar` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0458_F5_seal_full_dense` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0525_G2_immig_seal` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0529_G3_immig_fast` | 2 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0534_G4_immig_reach` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0539_G5_immig_lethal` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0544_G6_immig_breedbar` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0558_G8_immig_full_fast` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0603_G9_immig_centi_butterfly` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0607_G10_immig_full_culled` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0615_G7_immig_full` | 2 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-18_0727_chart_test` | 1 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-06-30_1212_00_baseline` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-07-05_1329_bee_arena` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-07-05_1333_bee_arena` | 18 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-07-05_1333_bee_arena/bugmap` | 15 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-07-05_1343_bee_arena` | 18 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/archive/2026-07-05_1343_bee_arena/bugmap` | 15 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/bug_lab/current` | 6 (6 in git) | 1.1 MB | 2026-07-05 | 0
- `tools/_generated/ecology_charts/village_21_B` | 811 (14 in git) | 173.0 MB | 2026-07-14 | 0
- `tools/_generated/ecology_charts/village_21_B/archive` | 797 (0 in git) | 170.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_0803_village_first` | 2 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_0923_v21b_03_rain` | 2 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1056_v21b_butterfly_tighten` | 3 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1105_v21b_fly_carrion` | 3 (0 in git) | 0.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1438_v21b_wasp_range` | 3 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1451_v21b_wasp_survive` | 3 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1532_baseline_forager-trig90` | 3 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1607_v21b_nocaps` | 3 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1714_v21b_nocaps` | 13 (0 in git) | 1.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1714_v21b_nocaps/bugmap` | 10 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1842_v21b_nocaps` | 9 (0 in git) | 1.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1842_v21b_nocaps/bugmap` | 6 (0 in git) | 1.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1853_v21b_nocaps` | 9 (0 in git) | 1.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_1853_v21b_nocaps/bugmap` | 6 (0 in git) | 1.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2017_v21b_nocaps` | 12 (0 in git) | 2.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2017_v21b_nocaps/bugmap` | 9 (0 in git) | 1.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2046_v21b_nocaps` | 12 (0 in git) | 2.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2046_v21b_nocaps/bugmap` | 9 (0 in git) | 1.8 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2118_v21b_nocaps` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2118_v21b_nocaps/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2141_v21b_nocaps` | 21 (0 in git) | 4.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-18_2141_v21b_nocaps/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0705_v21b_litter` | 21 (0 in git) | 4.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0705_v21b_litter/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0714_v21b_litter_scarce` | 20 (0 in git) | 4.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0714_v21b_litter_scarce/bugmap` | 17 (0 in git) | 3.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0723_v21b_litter` | 20 (0 in git) | 4.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0723_v21b_litter/bugmap` | 17 (0 in git) | 3.8 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0740_v21b_milli` | 21 (0 in git) | 4.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0740_v21b_milli/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0802_v21b_litter` | 51 (0 in git) | 12.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0802_v21b_litter/bugmap` | 48 (0 in git) | 11.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0825_v21b_milli50` | 51 (0 in git) | 11.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0825_v21b_milli50/bugmap` | 48 (0 in git) | 11.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0848_v21b_milli_life` | 49 (0 in git) | 11.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0848_v21b_milli_life/bugmap` | 46 (0 in git) | 10.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0912_v21b_milli_cap` | 46 (0 in git) | 10.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0912_v21b_milli_cap/bugmap` | 43 (0 in git) | 10.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0930_v21b_emergent` | 26 (0 in git) | 5.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_0930_v21b_emergent/bugmap` | 23 (0 in git) | 5.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1100_v21b_emergent2` | 29 (0 in git) | 6.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1100_v21b_emergent2/bugmap` | 26 (0 in git) | 6.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1154_v21b_relocate` | 29 (0 in git) | 6.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1154_v21b_relocate/bugmap` | 26 (0 in git) | 6.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1240_v21b_relocate2` | 24 (0 in git) | 5.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1240_v21b_relocate2/bugmap` | 21 (0 in git) | 4.8 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1419_v21b_bands` | 47 (0 in git) | 11.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1419_v21b_bands/bugmap` | 44 (0 in git) | 10.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1517_v21b_bands` | 15 (0 in git) | 3.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1517_v21b_bands/bugmap` | 11 (0 in git) | 2.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1540_v21b_rebalance` | 15 (0 in git) | 3.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1540_v21b_rebalance/bugmap` | 11 (0 in git) | 2.3 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1548_v21b_rebalance2` | 22 (0 in git) | 4.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1548_v21b_rebalance2/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1557_v21b_rebalance3` | 22 (0 in git) | 4.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1557_v21b_rebalance3/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1606_v21b_rebalance4` | 22 (0 in git) | 4.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1606_v21b_rebalance4/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1615_v21b_rebalance5` | 22 (0 in git) | 4.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1615_v21b_rebalance5/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1624_v21b_rebalance6` | 22 (0 in git) | 4.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1624_v21b_rebalance6/bugmap` | 18 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1633_v21b_rebalance6` | 10 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1633_v21b_rebalance6/bugmap` | 6 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1635_v21b_rebalance6` | 10 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-19_1635_v21b_rebalance6/bugmap` | 6 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_1842_00_baseline` | 13 (0 in git) | 2.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_1842_00_baseline/bugmap` | 9 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_2056_00_baseline` | 13 (0 in git) | 2.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_2056_00_baseline/bugmap` | 9 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_2150_00_baseline` | 13 (0 in git) | 2.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-22_2150_00_baseline/bugmap` | 9 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-06-30_1219_00_baseline` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-13_1054_v21b_baseline` | 17 (0 in git) | 3.7 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-13_1054_v21b_baseline/bugmap` | 13 (0 in git) | 2.8 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-13_1154_v21b_baseline` | 17 (0 in git) | 3.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-13_1154_v21b_baseline/bugmap` | 13 (0 in git) | 2.8 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-14_1116_v21b_baseline` | 10 (0 in git) | 1.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/archive/2026-07-14_1116_v21b_baseline/bugmap` | 6 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_B/comparisons` | 5 (5 in git) | 0.9 MB | 2026-06-18 | 0
- `tools/_generated/ecology_charts/village_21_B/current` | 8 (8 in git) | 1.4 MB | 2026-07-14 | 0
- `tools/_generated/ecology_charts/village_21_lab` | 312 (5 in git) | 66.2 MB | 2026-06-19 | 0
- `tools/_generated/ecology_charts/village_21_lab/archive` | 307 (0 in git) | 64.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2151_vlab_base` | 20 (0 in git) | 4.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2151_vlab_base/bugmap` | 17 (0 in git) | 3.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2159_vlab_E1_centi40` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2159_vlab_E1_centi40/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2207_vlab_E2_milli_throttle` | 20 (0 in git) | 4.2 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2207_vlab_E2_milli_throttle/bugmap` | 17 (0 in git) | 3.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2214_vlab_E5_wasp_reach60` | 21 (0 in git) | 4.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2214_vlab_E5_wasp_reach60/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2221_vlab_E6_fly_immig` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2221_vlab_E6_fly_immig/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2229_vlab_P1_fly_life` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2229_vlab_P1_fly_life/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2236_vlab_P2_rotlag` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2236_vlab_P2_rotlag/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2244_vlab_P3_wasp_feed` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2244_vlab_P3_wasp_feed/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2251_vlab_P4_pred_vision` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2251_vlab_P4_pred_vision/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2258_vlab_P5_bf_breed` | 20 (0 in git) | 4.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2258_vlab_P5_bf_breed/bugmap` | 17 (0 in git) | 3.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2308_vlab_S1_synth` | 20 (0 in git) | 4.1 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2308_vlab_S1_synth/bugmap` | 17 (0 in git) | 3.6 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2317_vlab_S2_centi_vis` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2317_vlab_S2_centi_vis/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2326_vlab_base` | 19 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2326_vlab_base/bugmap` | 16 (0 in git) | 3.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2341_vlab_base` | 19 (0 in git) | 4.0 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-18_2341_vlab_base/bugmap` | 16 (0 in git) | 3.5 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-19_0604_vlab_C1_centi_breed` | 21 (0 in git) | 4.4 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/archive/2026-06-19_0604_vlab_C1_centi_breed/bugmap` | 18 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/ecology_charts/village_21_lab/current` | 5 (5 in git) | 2.1 MB | 2026-06-19 | 0
- `tools/_generated/player` | 2874 (2850 in git) | 1795.7 MB | 2026-09-26 | 33
- `tools/_generated/player/APPROVED` | 13 (13 in git) | 45.8 MB | 2026-09-26 | 11
- `tools/_generated/player/APPROVED/hands` | 5 (5 in git) | 0.4 MB | 2026-08-06 | 6
- `tools/_generated/player/archive` | 754 (731 in git) | 1123.3 MB | 2026-09-26 | 0
- `tools/_generated/player/archive/2026-07-28-1457-copper-front-side-helmet` | 4 (4 in git) | 1.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-07-28-1501-copper-side-walk-frames` | 8 (8 in git) | 2.0 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-07-28-1505-copper-side-walk-frames-2` | 15 (15 in git) | 2.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo` | 154 (131 in git) | 799.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/contact-sheets` | 5 (5 in git) | 4.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/hand-experiments` | 22 (22 in git) | 4.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/hand-experiments/hand-A-anatomical` | 3 (3 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/hand-experiments/hand-B-analogy` | 3 (3 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/hand-experiments/hand-C-silhouette` | 8 (8 in git) | 1.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/hand-experiments/hand-D-pixel` | 8 (8 in git) | 1.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders` | 127 (104 in git) | 790.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/ant-carapace` | 1 (0 in git) | 28.2 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/beekeeper` | 1 (0 in git) | 27.3 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/beetle-shell` | 1 (0 in git) | 25.2 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/bronze` | 106 (104 in git) | 60.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/copper` | 1 (0 in git) | 45.4 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/entomologist` | 1 (0 in git) | 48.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/farmer` | 1 (0 in git) | 24.7 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/fisherman` | 1 (0 in git) | 21.4 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/glowworm` | 1 (0 in git) | 28.0 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/gold` | 1 (0 in git) | 10.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/hornet-stinger` | 1 (0 in git) | 30.0 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/iron` | 1 (0 in git) | 40.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/leather` | 1 (0 in git) | 40.9 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/moth-wool` | 1 (0 in git) | 49.8 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/padded` | 1 (0 in git) | 47.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/platinum` | 1 (0 in git) | 32.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/ranger` | 1 (0 in git) | 52.2 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/silver` | 1 (0 in git) | 27.6 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/steel` | 1 (0 in git) | 20.1 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/swamp-gear` | 1 (0 in git) | 52.8 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/wizard-robe` | 1 (0 in git) | 46.9 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/iteration-renders/wood` | 1 (0 in git) | 29.5 MB | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/ant-carapace` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/beekeeper` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/beetle-shell` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/bronze` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/copper` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/entomologist` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/farmer` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/fisherman` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/glowworm` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/gold` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/hornet-stinger` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/iron` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/leather` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/moth-wool` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/padded` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/platinum` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/ranger` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/silver` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/steel` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/swamp-gear` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/wizard-robe` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/2026-08-01_pre-redo/preview-renders/wood` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/_player_duplicate` | 2 (2 in git) | 0.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/_player_duplicate/bases` | 2 (2 in git) | 0.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/_player_duplicate/side_view` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/_player_duplicate/side_view/copper_armor` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/_player_duplicate/side_view/copper_armor/in_progress` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/bronze-helmet` | 4 (4 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/bronze-no-helmet` | 47 (47 in git) | 3.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/current` | 2 (2 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/dead-ant-run-1601` | 4 (4 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress` | 42 (42 in git) | 39.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/arm-split` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/in-progress/armless-fists` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/in-progress/bronze-armor` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/in-progress/copper-armor` | 24 (24 in git) | 15.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/copper-armor/2026-07-22_masking` | 9 (9 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/copper-armor/2026-07-22_masking/pieces` | 6 (6 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/copper-armor/2026-07-27_side` | 15 (15 in git) | 15.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/copper-armor/2026-07-27_side/candidates` | 5 (5 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/copper-armor/2026-07-27_side/raw` | 8 (8 in git) | 15.5 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/side-view` | 17 (17 in git) | 23.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/side-view/2026-07-27_attempt` | 17 (17 in git) | 23.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/side-view/2026-07-27_attempt/candidates` | 3 (3 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/side-view/2026-07-27_attempt/raw` | 11 (11 in git) | 22.5 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/silver-armor` | 1 (1 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/silver-armor/2026-07-22_masking` | 1 (1 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/in-progress/silver-armor/2026-07-22_masking/pieces` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/old` | 453 (453 in git) | 273.9 MB | 2026-09-26 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments` | 74 (74 in git) | 30.7 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/arm-split` | 14 (14 in git) | 0.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/arm-split/2026-07-28_arm-split` | 14 (14 in git) | 0.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/arm-split/2026-07-28_arm-split/down` | 4 (4 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/arm-split/2026-07-28_arm-split/side` | 4 (4 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/armless-fists` | 2 (2 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/armless-fists/2026-07-28_first-look` | 2 (2 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/bronze-armor` | 3 (3 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/bronze-armor/2026-07-28_front-and-side` | 3 (3 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/bronze-armor/2026-07-28_front-and-side/raw` | 1 (1 in git) | 0.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/copper-armor` | 7 (7 in git) | 2.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/copper-armor/2026-07-28_side-armless` | 4 (4 in git) | 1.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/copper-armor/2026-07-28_side-armless-g2` | 3 (3 in git) | 0.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/copper-armor/2026-07-28_side-armless-g2/raw` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/copper-armor/2026-07-28_side-armless/raw` | 1 (1 in git) | 1.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view` | 48 (48 in git) | 27.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless` | 10 (10 in git) | 12.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless/aligned` | 3 (3 in git) | 6.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless/raw` | 3 (3 in git) | 6.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless_highres` | 5 (5 in git) | 4.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless_highres/raw` | 1 (1 in git) | 2.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless_minidelta` | 4 (4 in git) | 4.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_armless_minidelta/raw` | 2 (2 in git) | 4.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_chatgpt-armless-side` | 9 (9 in git) | 1.0 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_gpt-image-2-nomask` | 7 (7 in git) | 1.7 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_gpt_image_2` | 2 (2 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_side_armless_masked` | 11 (11 in git) | 2.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/2026-07-28_experiments/side-view/2026-07-28_side_armless_masked/raw` | 1 (1 in git) | 2.0 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/iteration_history` | 44 (44 in git) | 14.1 MB | 2026-09-26 | 0
- `tools/_generated/player/archive/old/iteration_history/copper_masking` | 4 (4 in git) | 4.7 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/masking_temp` | 21 (21 in git) | 32.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/masking_temp/1_mannequins` | 3 (3 in git) | 0.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/masking_temp/2_bases` | 4 (4 in git) | 8.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/masking_temp/3_gear_to_mask` | 8 (8 in git) | 15.5 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/masking_temp/4_experimental` | 4 (4 in git) | 7.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_design_spikes` | 22 (22 in git) | 0.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_design_spikes/designs` | 7 (7 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_design_spikes/designs2` | 4 (4 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_design_spikes/vector` | 4 (4 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_design_spikes/walk_candidates` | 7 (7 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/old_showcase` | 10 (10 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/raw_base_gens` | 74 (74 in git) | 67.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/raw_base_gens/bald` | 60 (60 in git) | 54.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/raw_base_gens/base_set` | 7 (7 in git) | 10.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/raw_base_gens/mannequin` | 7 (7 in git) | 2.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike` | 206 (206 in git) | 128.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/base64` | 6 (6 in git) | 0.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/boots_match` | 6 (6 in git) | 6.5 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/copper` | 16 (16 in git) | 17.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/gear_exp` | 8 (8 in git) | 6.2 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/gear_test` | 6 (6 in git) | 3.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/hair` | 8 (8 in git) | 10.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/leather` | 3 (3 in git) | 2.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/mask_v2` | 2 (2 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/mask_v3` | 3 (3 in git) | 1.7 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/mask_v4` | 2 (2 in git) | 0.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/mask_v5` | 3 (3 in git) | 2.1 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/mask_v6` | 9 (9 in git) | 0.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/owner_mask` | 3 (3 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/pilot` | 61 (61 in git) | 34.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/pilot/down` | 30 (30 in git) | 15.9 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/pilot/right` | 17 (17 in git) | 10.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/run_fbf` | 14 (14 in git) | 3.5 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/run_side` | 6 (6 in git) | 0.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/run_v2` | 14 (14 in git) | 4.8 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/side_bases` | 7 (7 in git) | 10.7 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/silver` | 5 (5 in git) | 7.0 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/old/refart_spike/turnaround` | 2 (2 in git) | 4.4 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/references` | 7 (7 in git) | tiny | 2026-08-06 | 0
- `tools/_generated/player/archive/runs` | 11 (11 in git) | 1.6 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/runs/2026-07-28-1321-copper-front-and-side` | 7 (7 in git) | 1.3 MB | 2026-08-06 | 0
- `tools/_generated/player/archive/runs/2026-07-28-1438-all-poses-one-image` | 4 (4 in git) | 0.3 MB | 2026-08-06 | 0
- `tools/_generated/player/bases` | 2 (2 in git) | tiny | 2026-07-28 | 122
- `tools/_generated/player/explore` | 563 (563 in git) | 196.9 MB | 2026-09-26 | 12
- `tools/_generated/player/explore/ant-carapace` | 5 (5 in git) | 2.5 MB | 2026-08-05 | 2
- `tools/_generated/player/explore/ant-carapace-black` | 5 (5 in git) | 2.5 MB | 2026-08-05 | 2
- `tools/_generated/player/explore/ant-carapace-black2` | 4 (4 in git) | 2.4 MB | 2026-08-05 | 0
- `tools/_generated/player/explore/ant-carapace-black3` | 3 (3 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/ant-carapace-black4` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/ant-carapace-open` | 4 (4 in git) | 2.1 MB | 2026-08-05 | 0
- `tools/_generated/player/explore/ant-carapace-red` | 4 (4 in git) | 2.3 MB | 2026-08-05 | 0
- `tools/_generated/player/explore/ant-carapace-red2` | 5 (5 in git) | 2.8 MB | 2026-08-18 | 1
- `tools/_generated/player/explore/ant-carapace-soldier` | 5 (5 in git) | 2.6 MB | 2026-08-05 | 0
- `tools/_generated/player/explore/beetle-shell` | 4 (4 in git) | 2.2 MB | 2026-08-01 | 0
- `tools/_generated/player/explore/beetle-shell-r2` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/beetle-shell-r3` | 4 (4 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-backwalk` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-backwalk-r2` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-frontwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-gauntlet` | 6 (6 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-sidewalk` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-sidewalk-r2` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-sidewalk-r3` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v2-turnaround` | 7 (7 in git) | 1.7 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-backwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-backwalk-r2` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-frontwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-frontwalk-r2` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-gauntlet` | 6 (6 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-sidewalk` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-v3-turnaround` | 7 (7 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/blackant-walks` | 12 (12 in git) | 0.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-r2` | 4 (4 in git) | 2.4 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/bronze-r3` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-v2-backwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-v2-frontwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-v2-gauntlet` | 6 (6 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-v2-sidewalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/bronze-v2-turnaround` | 7 (7 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/copper` | 4 (4 in git) | 2.1 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/copper-backwalk` | 5 (5 in git) | 1.5 MB | 2026-09-26 | 0
- `tools/_generated/player/explore/copper-frontwalk` | 5 (5 in git) | 1.6 MB | 2026-09-26 | 0
- `tools/_generated/player/explore/copper-gauntlet` | 7 (7 in git) | 1.5 MB | 2026-09-26 | 0
- `tools/_generated/player/explore/copper-r2` | 4 (4 in git) | 2.4 MB | 2026-08-14 | 0
- `tools/_generated/player/explore/copper-r3` | 5 (5 in git) | 1.7 MB | 2026-09-26 | 1
- `tools/_generated/player/explore/copper-sidewalk` | 5 (5 in git) | 1.4 MB | 2026-09-26 | 0
- `tools/_generated/player/explore/copper-turnaround` | 8 (8 in git) | 1.5 MB | 2026-09-26 | 0
- `tools/_generated/player/explore/fancy` | 4 (4 in git) | 1.7 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fancy-r2` | 4 (4 in git) | 1.9 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-a` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-b` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-backwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-backwalk-r3` | 5 (5 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-backwalk-r4` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-c` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-d` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-frontwalk` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-frontwalk-r2` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-frontwalk-r3` | 5 (5 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-frontwalk-r4` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-13` | 12 (12 in git) | 0.7 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-13/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-box` | 7 (7 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-box2` | 6 (6 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-char` | 6 (6 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-char2` | 6 (6 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-tall` | 12 (12 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-gauntlet-tall/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-genA` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-genA2` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-genA3` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-genA4` | 3 (3 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-genA5` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-pair` | 4 (4 in git) | 1.6 MB | 2026-08-18 | 2
- `tools/_generated/player/explore/fireant-pair2` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-r2` | 5 (5 in git) | 2.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-r3` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-sidewalk` | 10 (10 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-v2-board` | 1 (1 in git) | tiny | 2026-08-18 | 2
- `tools/_generated/player/explore/fireant-v2-edited` | 3 (3 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-v2-template` | 1 (1 in git) | 0.1 MB | 2026-08-18 | 1
- `tools/_generated/player/explore/fireant-v2-turnaround` | 7 (7 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-v2-walk` | 3 (3 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-v2-walk2` | 3 (3 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-walks` | 12 (12 in git) | 0.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fireant-walks4` | 24 (24 in git) | 1.1 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/fisherman` | 4 (4 in git) | 2.3 MB | 2026-08-01 | 0
- `tools/_generated/player/explore/gilded-steel` | 4 (4 in git) | 1.9 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/glowworm` | 4 (4 in git) | 2.2 MB | 2026-08-01 | 0
- `tools/_generated/player/explore/hornet-stinger-r2` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/hornet-thorn` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/iron` | 4 (4 in git) | 3.1 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/iron-r2` | 5 (5 in git) | 2.5 MB | 2026-08-14 | 1
- `tools/_generated/player/explore/killer-bee-stinger` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/killer-bee-thorn` | 3 (3 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/leather` | 4 (4 in git) | 2.4 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/leather-r2` | 4 (4 in git) | 1.6 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/platinum` | 4 (4 in git) | 2.1 MB | 2026-08-01 | 0
- `tools/_generated/player/explore/platinum-r2` | 3 (3 in git) | 1.4 MB | 2026-08-14 | 0
- `tools/_generated/player/explore/platinum-r3` | 3 (3 in git) | 1.4 MB | 2026-08-14 | 0
- `tools/_generated/player/explore/platinum-r4` | 4 (4 in git) | 1.7 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/platinum-r5` | 4 (4 in git) | 1.7 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/platinum-r6` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/ranger` | 4 (4 in git) | 2.5 MB | 2026-08-01 | 1
- `tools/_generated/player/explore/ranger-r2` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/scorpion` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/steel` | 4 (4 in git) | 2.4 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/steel-r2` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/steel-r3` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/steel-r4` | 3 (3 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/steel-r5` | 4 (4 in git) | 1.6 MB | 2026-08-18 | 1
- `tools/_generated/player/explore/swamp-gear` | 4 (4 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/explore/tip-D1-arms` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-D2-repeat` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-D3-samechar` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-D4-nolegs` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-E1-fromsnap` | 3 (3 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-E2-repeat` | 3 (3 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-V1-variants` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-V2-variants` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-board` | 1 (1 in git) | tiny | 2026-08-18 | 1
- `tools/_generated/player/explore/tip-pixref` | 1 (1 in git) | tiny | 2026-08-18 | 2
- `tools/_generated/player/explore/tip-tipA` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-tipB` | 4 (4 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-tipC` | 4 (4 in git) | 1.3 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/tip-walkB` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/wasp-stinger` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/wasp-thorn` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/wood` | 4 (4 in git) | 2.8 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/wood-r2` | 4 (4 in git) | 2.7 MB | 2026-08-07 | 1
- `tools/_generated/player/explore/wood-r3` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/wood-r4` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/explore/wood-r5` | 3 (3 in git) | 1.4 MB | 2026-08-18 | 0
- `tools/_generated/player/hands` | 7 (7 in git) | 1.2 MB | 2026-08-06 | 0
- `tools/_generated/player/outfits` | 1057 (1057 in git) | 225.2 MB | 2026-09-26 | 9
- `tools/_generated/player/outfits/ant-carapace` | 72 (72 in git) | 24.4 MB | 2026-09-26 | 1
- `tools/_generated/player/outfits/ant-carapace/archive` | 15 (15 in git) | 3.7 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/archive/2026-08-05-stale-renders` | 15 (15 in git) | 3.7 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/archive/2026-08-05-stale-renders/animations` | 12 (12 in git) | 3.4 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/current` | 26 (26 in git) | 3.7 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/current/anim` | 13 (13 in git) | 3.1 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad` | 31 (31 in git) | 17.1 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates` | 31 (31 in git) | 17.1 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-07-28-1604-original-sheet` | 4 (4 in git) | 0.9 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-black-ant-faces-A` | 3 (3 in git) | 2.2 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-black-ant-faces-B` | 3 (3 in git) | 2.4 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-open-no-direction` | 4 (4 in git) | 2.1 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-red-fireant-faces-A` | 4 (4 in git) | 2.2 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-red-fireant-faces-B` | 3 (3 in git) | 2.4 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-soldier-three-variants` | 5 (5 in git) | 2.6 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/ant-carapace/scratchpad/1-candidates/2026-08-05-three-armour-options` | 4 (4 in git) | 2.2 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/beekeeper` | 33 (33 in git) | 5.1 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/beekeeper/animations` | 14 (14 in git) | 3.2 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/beetle-shell` | 27 (27 in git) | 4.8 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/beetle-shell/animations` | 14 (14 in git) | 2.9 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/blackant` | 92 (92 in git) | 17.8 MB | 2026-08-18 | 2
- `tools/_generated/player/outfits/blackant/anim` | 14 (14 in git) | 3.7 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/archive` | 34 (34 in git) | 5.3 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/archive/2026-08-05-free-designed-gauntlets` | 7 (7 in git) | 2.3 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/blackant/archive/2026-08-18-superseded-raw` | 27 (27 in git) | 3.0 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/archive/2026-08-18-superseded-raw/anim` | 13 (13 in git) | 2.4 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/archive/2026-08-18-superseded-raw/frames` | 9 (9 in git) | 0.6 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/archive/2026-08-18-superseded-raw/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/frames` | 12 (12 in git) | 0.1 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/blackant/tries` | 22 (22 in git) | 6.8 MB | 2026-08-06 | 1
- `tools/_generated/player/outfits/blackant/tries/2026-08-05-gauntlet-4hand` | 8 (8 in git) | 2.5 MB | 2026-08-06 | 0
- `tools/_generated/player/outfits/blackant/tries/2026-08-05-original-sheet` | 5 (5 in git) | 2.0 MB | 2026-08-06 | 1
- `tools/_generated/player/outfits/blackant/tries/2026-08-06-official-gauntlet` | 9 (9 in git) | 2.2 MB | 2026-08-06 | 0
- `tools/_generated/player/outfits/bronze` | 130 (130 in git) | 48.3 MB | 2026-08-18 | 5
- `tools/_generated/player/outfits/bronze/anim` | 14 (14 in git) | 2.4 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/archive` | 50 (50 in git) | 11.2 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-04-superseded-side-sword` | 1 (1 in git) | 0.8 MB | 2026-08-04 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-04-unsettled-tools` | 5 (5 in git) | 2.3 MB | 2026-08-04 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-05-pre-migration-animations` | 14 (14 in git) | 4.5 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-18-superseded-raw` | 30 (30 in git) | 3.6 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-18-superseded-raw/anim` | 13 (13 in git) | 3.0 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-18-superseded-raw/frames` | 12 (12 in git) | 0.5 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/archive/2026-08-18-superseded-raw/gauntlet` | 5 (5 in git) | 0.1 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/frames` | 12 (12 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/bronze/hands` | 40 (40 in git) | 33.1 MB | 2026-08-02 | 1
- `tools/_generated/player/outfits/bronze/hands/candidates` | 38 (38 in git) | 33.0 MB | 2026-08-02 | 1
- `tools/_generated/player/outfits/bronze/hands/candidates/fingered_gauntlet` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/game_sprite_sheet` | 3 (3 in git) | 2.1 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/grip_first` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/profile_option_1` | 4 (4 in git) | 2.2 MB | 2026-08-02 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/profile_option_2` | 4 (4 in git) | 2.2 MB | 2026-08-02 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/segmented_plate` | 3 (3 in git) | 2.1 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/set_a` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/set_b` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/set_c` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/bronze/hands/candidates/smooth_mitt` | 3 (3 in git) | 2.0 MB | 2026-08-01 | 0
- `tools/_generated/player/outfits/copper` | 94 (94 in git) | 11.2 MB | 2026-09-26 | 1
- `tools/_generated/player/outfits/copper/anim` | 14 (14 in git) | 2.6 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/archive` | 18 (18 in git) | 5.3 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/archive/2026-09-26-superseded-sheet` | 18 (18 in git) | 5.3 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/archive/2026-09-26-superseded-sheet/animations` | 14 (14 in git) | 3.4 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/archive/2026-09-26-superseded-sheet/gauntlet` | 4 (4 in git) | 1.9 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/frames` | 12 (12 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/gauntlet` | 5 (5 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/tries` | 31 (31 in git) | 0.9 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/tries/2026-09-26-procedure` | 31 (31 in git) | 0.9 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/tries/2026-09-26-procedure/anim` | 13 (13 in git) | 0.9 MB | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/tries/2026-09-26-procedure/frames` | 12 (12 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/outfits/copper/tries/2026-09-26-procedure/gauntlet` | 5 (5 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/outfits/entomologist` | 27 (27 in git) | 5.1 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/entomologist/animations` | 14 (14 in git) | 2.9 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/farmer` | 33 (33 in git) | 4.4 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/farmer/animations` | 14 (14 in git) | 2.8 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/fireant` | 111 (111 in git) | 21.0 MB | 2026-08-18 | 1
- `tools/_generated/player/outfits/fireant/anim` | 14 (14 in git) | 3.0 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/archive` | 34 (34 in git) | 3.6 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/archive/2026-08-05-free-designed-gauntlets` | 7 (7 in git) | 2.5 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/fireant/archive/2026-08-18-superseded-raw` | 27 (27 in git) | 1.2 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/archive/2026-08-18-superseded-raw/anim` | 13 (13 in git) | 1.1 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/archive/2026-08-18-superseded-raw/frames` | 9 (9 in git) | 0.1 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/archive/2026-08-18-superseded-raw/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/frames` | 12 (12 in git) | 0.1 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/gauntlet` | 5 (5 in git) | tiny | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/tries` | 32 (32 in git) | 12.3 MB | 2026-08-18 | 1
- `tools/_generated/player/outfits/fireant/tries/2026-08-05-gauntlet-4hand` | 8 (8 in git) | 2.7 MB | 2026-08-06 | 0
- `tools/_generated/player/outfits/fireant/tries/2026-08-05-original-sheet` | 5 (5 in git) | 2.1 MB | 2026-08-06 | 1
- `tools/_generated/player/outfits/fireant/tries/2026-08-06-official-gauntlet` | 9 (9 in git) | 2.4 MB | 2026-08-06 | 0
- `tools/_generated/player/outfits/fireant/tries/2026-08-14-16cell` | 4 (4 in git) | 1.9 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/tries/2026-08-14-16cell-b` | 3 (3 in git) | 1.7 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fireant/tries/2026-08-14-16cell-c` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/outfits/fisherman` | 27 (27 in git) | 4.4 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/fisherman/animations` | 14 (14 in git) | 2.5 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/glowworm` | 27 (27 in git) | 4.4 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/glowworm/animations` | 14 (14 in git) | 2.6 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/gold` | 33 (33 in git) | 5.2 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/gold/animations` | 14 (14 in git) | 3.4 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/hornet-stinger` | 27 (27 in git) | 5.5 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/hornet-stinger/animations` | 14 (14 in git) | 3.3 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/iron` | 32 (32 in git) | 8.6 MB | 2026-08-14 | 1
- `tools/_generated/player/outfits/iron/animations` | 14 (14 in git) | 3.6 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/iron/gauntlet` | 4 (4 in git) | 2.3 MB | 2026-08-14 | 0
- `tools/_generated/player/outfits/leather` | 27 (27 in git) | 5.1 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/leather/animations` | 14 (14 in git) | 3.0 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/moth-wool` | 27 (27 in git) | 5.9 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/moth-wool/animations` | 14 (14 in git) | 3.3 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/padded` | 27 (27 in git) | 5.4 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/padded/animations` | 14 (14 in git) | 3.2 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/platinum` | 27 (27 in git) | 5.2 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/platinum/animations` | 14 (14 in git) | 3.1 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/ranger` | 27 (27 in git) | 5.6 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/ranger/animations` | 14 (14 in git) | 3.6 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/silver` | 42 (42 in git) | 5.9 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/silver/animations` | 14 (14 in git) | 3.2 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/steel` | 28 (28 in git) | 5.6 MB | 2026-08-18 | 1
- `tools/_generated/player/outfits/steel/animations` | 14 (14 in git) | 3.3 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/swamp-gear` | 27 (27 in git) | 5.2 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/swamp-gear/animations` | 14 (14 in git) | 3.2 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/wizard-robe` | 27 (27 in git) | 5.1 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/wizard-robe/animations` | 14 (14 in git) | 3.1 MB | 2026-08-05 | 0
- `tools/_generated/player/outfits/wood` | 33 (33 in git) | 5.8 MB | 2026-08-05 | 1
- `tools/_generated/player/outfits/wood/animations` | 14 (14 in git) | 3.7 MB | 2026-08-05 | 0
- `tools/_generated/player/props` | 3 (3 in git) | 0.5 MB | 2026-08-01 | 1
- `tools/_generated/player/props/practice-dummy` | 3 (3 in git) | 0.5 MB | 2026-08-01 | 0
- `tools/_generated/player/reviews` | 457 (457 in git) | 151.7 MB | 2026-09-26 | 12
- `tools/_generated/player/reviews/2026-08-03-facing-and-hands` | 4 (4 in git) | 1.3 MB | 2026-08-03 | 0
- `tools/_generated/player/reviews/2026-08-04-1247-swing-tools` | 15 (15 in git) | 3.9 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1610-swing-tools` | 16 (16 in git) | 4.1 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1617-swing-tools` | 15 (15 in git) | 3.9 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1621-swing-tools` | 16 (16 in git) | 4.0 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1652-swing-tools` | 15 (15 in git) | 4.0 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1700-swing-tools` | 15 (15 in git) | 4.0 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-1742-swing-tools` | 16 (16 in git) | 3.9 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-swing` | 11 (11 in git) | 32.7 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-arm` | 12 (12 in git) | 8.3 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-arm2` | 11 (11 in git) | 7.1 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-facings` | 17 (17 in git) | 11.2 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-five` | 14 (14 in git) | 4.8 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-game` | 8 (8 in git) | 2.6 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-official` | 10 (10 in git) | 7.0 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-tools` | 29 (29 in git) | 6.4 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-04-swing-tools/previous-net-versions` | 12 (12 in git) | 2.4 MB | 2026-08-04 | 0
- `tools/_generated/player/reviews/2026-08-05-ant-outfits-built` | 2 (2 in git) | 0.4 MB | 2026-08-05 | 0
- `tools/_generated/player/reviews/2026-08-06-ant-gauntlets` | 11 (11 in git) | 1.4 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-06-bronze-hands` | 16 (16 in git) | 2.0 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-06-gauntlet-chart` | 1 (1 in git) | 0.2 MB | 2026-08-06 | 0
- `tools/_generated/player/reviews/2026-08-07-base-ladder-candidates` | 1 (1 in git) | tiny | 2026-08-07 | 0
- `tools/_generated/player/reviews/2026-08-13-base-ladder-pick` | 4 (4 in git) | 0.5 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-14-copper-iron-pick` | 20 (20 in git) | 7.1 MB | 2026-08-18 | 0
- `tools/_generated/player/reviews/2026-08-14-prompt` | 3 (3 in git) | 1.5 MB | 2026-08-18 | 0
- `tools/_generated/player/reviews/2026-08-14-run-front-pump` | 11 (11 in git) | 1.6 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-14-swing-while-running` | 5 (5 in git) | 2.0 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-15-blackant` | 15 (15 in git) | 2.2 MB | 2026-08-18 | 0
- `tools/_generated/player/reviews/2026-08-15-blackant-reroll` | 16 (16 in git) | 3.7 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-15-bronze-reroll` | 16 (16 in git) | 2.6 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-15-fireant-v2` | 33 (33 in git) | 12.2 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-18-pixel-proof` | 5 (5 in git) | 0.2 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-08-18-walk-hands` | 4 (4 in git) | 0.2 MB | 2026-08-18 | 0
- `tools/_generated/player/reviews/2026-09-26-art-demo` | 43 (43 in git) | 0.7 MB | 2026-09-26 | 5
- `tools/_generated/player/reviews/2026-09-26-art-demo/sprites` | 16 (16 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-09-26-base-pass` | 7 (7 in git) | 0.1 MB | 2026-09-26 | 2
- `tools/_generated/player/reviews/2026-09-26-base-pass/sprites` | 4 (4 in git) | tiny | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-09-26-copper` | 20 (20 in git) | 3.8 MB | 2026-09-26 | 0
- `tools/_generated/player/reviews/2026-09-26-copper/animations` | 13 (13 in git) | 0.9 MB | 2026-09-26 | 0
- `tools/_generated/previews` | 833 (0 in git) | 106.4 MB | — | 52
- `tools/_generated/previews/brood` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog` | 731 (0 in git) | 1.6 MB | — | 2
- `tools/_generated/previews/catalog/armor` | 18 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/beekeeping` | 6 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/blocks` | 8 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/bugs` | 91 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog/consumables` | 2 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/crafting` | 15 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/crops` | 35 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog/decorations` | 68 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/previews/catalog/food` | 2 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/furniture` | 62 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog/gear` | 2 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/lighting` | 10 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/nature` | 90 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/previews/catalog/ore` | 13 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/resources` | 108 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/previews/catalog/seeds` | 8 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/storage` | 9 (0 in git) | tiny | — | 0
- `tools/_generated/previews/catalog/structures` | 90 (0 in git) | 0.2 MB | — | 0
- `tools/_generated/previews/catalog/tiles` | 25 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog/tools` | 52 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/previews/catalog/weapon` | 17 (0 in git) | tiny | — | 0
- `tools/_generated/previews/dug_experiment` | 7 (0 in git) | 0.6 MB | — | 2
- `tools/_generated/previews/examples` | 26 (0 in git) | 7.8 MB | — | 8
- `tools/_generated/previews/examples/blocks` | 3 (0 in git) | 0.9 MB | — | 0
- `tools/_generated/previews/examples/buildings` | 3 (0 in git) | 3.1 MB | — | 0
- `tools/_generated/previews/examples/ground-edges` | 2 (0 in git) | 0.5 MB | — | 5
- `tools/_generated/previews/examples/roads` | 1 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/previews/examples/shaped_ground` | 4 (0 in git) | 0.1 MB | — | 1
- `tools/_generated/previews/examples/tool_swings` | 12 (0 in git) | 0.9 MB | — | 1
- `tools/_generated/previews/examples/water` | 1 (0 in git) | 1.1 MB | — | 0
- `tools/_generated/previews/title` | 12 (0 in git) | 1.2 MB | — | 0
- `tools/_generated/previews/ui` | 6 (0 in git) | 0.2 MB | — | 2
- `tools/_generated/previews/zones` | 50 (0 in git) | 94.9 MB | — | 10
- `tools/_generated/previews/zones/ant_colony` | 1 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/previews/zones/ant_colony/scenes` | 1 (0 in git) | 0.6 MB | — | 0
- `tools/_generated/previews/zones/ant_colony_40` | 4 (0 in git) | 6.9 MB | — | 0
- `tools/_generated/previews/zones/ant_colony_40/_layout_options` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/previews/zones/ant_colony_40/scenes` | 2 (0 in git) | 1.0 MB | — | 0
- `tools/_generated/previews/zones/ant_tunnels_30` | 9 (0 in git) | 21.2 MB | — | 1
- `tools/_generated/previews/zones/ant_tunnels_30/_cliff_options` | 4 (0 in git) | 10.5 MB | — | 0
- `tools/_generated/previews/zones/ant_tunnels_30/scenes` | 1 (0 in git) | 0.6 MB | — | 1
- `tools/_generated/previews/zones/bee_meadow` | 1 (0 in git) | 1.7 MB | — | 0
- `tools/_generated/previews/zones/bee_meadow/scenes` | 1 (0 in git) | 1.7 MB | — | 0
- `tools/_generated/previews/zones/bee_meadow_20` | 6 (0 in git) | 25.1 MB | — | 3
- `tools/_generated/previews/zones/bee_meadow_20/scenes` | 3 (0 in git) | 3.6 MB | — | 3
- `tools/_generated/previews/zones/bug_zoo` | 2 (0 in git) | 2.5 MB | — | 0
- `tools/_generated/previews/zones/butterfly_meadow_11` | 2 (0 in git) | 2.6 MB | — | 0
- `tools/_generated/previews/zones/butterfly_meadow_11/scenes` | 2 (0 in git) | 2.6 MB | — | 0
- `tools/_generated/previews/zones/desert` | 1 (0 in git) | 0.9 MB | — | 0
- `tools/_generated/previews/zones/desert/scenes` | 1 (0 in git) | 0.9 MB | — | 0
- `tools/_generated/previews/zones/feel_test` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/previews/zones/lighting_test` | 1 (0 in git) | tiny | — | 0
- `tools/_generated/previews/zones/underground_passages_31` | 5 (0 in git) | 9.6 MB | — | 0
- `tools/_generated/previews/zones/underground_passages_31/scenes` | 3 (0 in git) | 3.5 MB | — | 0
- `tools/_generated/previews/zones/village_21_B` | 17 (0 in git) | 23.9 MB | — | 3
- `tools/_generated/previews/zones/village_21_B/scenes` | 14 (0 in git) | 9.6 MB | — | 3
- `tools/_generated/raw` | 739 (0 in git) | 1158.5 MB | — | 6
- `tools/_generated/raw/walk` | 79 (0 in git) | 19.9 MB | — | 0
- `tools/_generated/scratch` | 276 (0 in git) | 266.8 MB | — | 1
- `tools/_generated/scratch/ab_review` | 5 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/scratch/bugs` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/scratch/output` | 6 (0 in git) | 0.4 MB | — | 0
- `tools/_generated/scratch/plants` | 1 (0 in git) | 0.1 MB | — | 0
- `tools/_generated/scratch/refexp` | 254 (0 in git) | 264.8 MB | — | 0
- `tools/_generated/scratch/refexp/bed_side` | 9 (0 in git) | 8.7 MB | — | 0
- `tools/_generated/scratch/refexp/bfly15` | 7 (0 in git) | 5.1 MB | — | 0
- `tools/_generated/scratch/refexp/book_back` | 4 (0 in git) | 2.8 MB | — | 0
- `tools/_generated/scratch/refexp/book_fix` | 4 (0 in git) | 4.5 MB | — | 0
- `tools/_generated/scratch/refexp/book_ref` | 4 (0 in git) | 4.2 MB | — | 0
- `tools/_generated/scratch/refexp/book_side` | 9 (0 in git) | 8.4 MB | — | 0
- `tools/_generated/scratch/refexp/book_side2` | 7 (0 in git) | 9.0 MB | — | 0
- `tools/_generated/scratch/refexp/book_side3` | 10 (0 in git) | 8.6 MB | — | 0
- `tools/_generated/scratch/refexp/book_sweep` | 11 (0 in git) | 16.1 MB | — | 0
- `tools/_generated/scratch/refexp/book_top` | 4 (0 in git) | 4.7 MB | — | 0
- `tools/_generated/scratch/refexp/butterfly` | 9 (0 in git) | 7.5 MB | — | 0
- `tools/_generated/scratch/refexp/fly` | 9 (0 in git) | 4.2 MB | — | 0
- `tools/_generated/scratch/refexp/furn` | 50 (0 in git) | 48.2 MB | — | 0
- `tools/_generated/scratch/refexp/oneeach` | 0 (0 in git) | tiny | — | 0
- `tools/_generated/scratch/refexp/player` | 23 (0 in git) | 23.9 MB | — | 0
- `tools/_generated/scratch/refexp/player2` | 38 (0 in git) | 52.5 MB | — | 0
- `tools/_generated/scratch/refexp/sheet15` | 23 (0 in git) | 19.4 MB | — | 0
- `tools/_generated/scratch/refexp/sheetraw` | 5 (0 in git) | 5.6 MB | — | 0
- `tools/_generated/scratch/refexp/smoke` | 3 (0 in git) | 3.9 MB | — | 0
- `tools/_generated/scratch/refexp/strips` | 16 (0 in git) | 27.5 MB | — | 0
- `tools/_generated/tiles` | 119 (3 in git) | 47.4 MB | 2026-09-26 | 0
- `tools/_generated/tiles/candidates` | 27 (0 in git) | tiny | — | 0
- `tools/_generated/tiles/candidates16` | 40 (0 in git) | tiny | — | 0
- `tools/_generated/tiles/previews` | 11 (2 in git) | 1.5 MB | 2026-07-25 | 0
- `tools/_generated/tiles/raw` | 28 (0 in git) | 37.0 MB | — | 0
- `tools/_generated/tiles/refs` | 8 (0 in git) | 8.9 MB | — | 0
- `tools/_generated/tiles/tufts` | 4 (0 in git) | tiny | — | 0
- `tools/_generated/variants` | 47 (0 in git) | tiny | — | 0
- `tools/_generated/variants/cave_floor` | 3 (0 in git) | tiny | — | 0
- `tools/_generated/variants/dirt_block` | 10 (0 in git) | tiny | — | 0
- `tools/_generated/variants/stone_block` | 10 (0 in git) | tiny | — | 0
- `tools/_generated/variants/wall_marble` | 3 (0 in git) | tiny | — | 0
- `tools/_generated/variants/wall_stone` | 10 (0 in git) | tiny | — | 0
- `tools/_generated/variants/wall_wood` | 10 (0 in git) | tiny | — | 0
- `tools/archive` | 30 (30 in git) | 0.4 MB | 2026-06-26 | 0
- `tools/art` | 14 (14 in git) | 0.1 MB | 2026-07-18 | 23
- `tools/art/catalog` | 13 (13 in git) | 0.1 MB | 2026-07-18 | 21
- `tools/bug_lab_configs` | 85 (85 in git) | 0.1 MB | 2026-09-26 | 11
- `tools/data` | 5 (4 in git) | tiny | 2026-07-06 | 22
- `tools/data/__pycache__` | 1 (0 in git) | tiny | — | 0
- `tools/ecology` | 13 (10 in git) | 0.1 MB | 2026-09-26 | 23
- `tools/ecology/__pycache__` | 3 (0 in git) | tiny | — | 0
- `tools/gdd` | 13 (6 in git) | 2.5 MB | 2026-09-29 | 5
- `tools/gdd/_build` | 7 (0 in git) | 2.4 MB | — | 4
- `tools/gdd/_build/shots` | 1 (0 in git) | 0.2 MB | — | 0
- `tools/netcode` | 4 (4 in git) | tiny | 2026-06-26 | 8
- `tools/player_sprites` | 96 (51 in git) | 1.1 MB | 2026-09-26 | 18
- `tools/player_sprites/__pycache__` | 41 (0 in git) | 0.4 MB | — | 0
- `tools/player_sprites/aipipe` | 8 (4 in git) | 0.1 MB | 2026-09-26 | 2
- `tools/player_sprites/aipipe/__pycache__` | 4 (0 in git) | tiny | — | 0
- `tools/sim-determinism` | 29 (5 in git) | 0.4 MB | 2026-07-19 | 13
- `tools/sim-determinism/bin` | 5 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/bin/Debug` | 5 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/bin/Debug/net8.0` | 5 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/obj` | 19 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/obj/Debug` | 14 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/obj/Debug/net8.0` | 14 (0 in git) | 0.2 MB | — | 0
- `tools/sim-determinism/obj/Debug/net8.0/ref` | 1 (0 in git) | tiny | — | 0
- `tools/sim-determinism/obj/Debug/net8.0/refint` | 1 (0 in git) | tiny | — | 0
- `tools/sprites` | 54 (37 in git) | 0.5 MB | 2026-09-26 | 29
- `tools/sprites/__pycache__` | 6 (0 in git) | 0.1 MB | — | 0
- `tools/sprites/drawn` | 24 (13 in git) | 0.2 MB | 2026-09-26 | 3
- `tools/sprites/drawn/__pycache__` | 11 (0 in git) | 0.1 MB | — | 0
- `tools/sync-harness` | 56 (7 in git) | 2.0 MB | 2026-07-05 | 8
- `tools/sync-harness/bin` | 12 (0 in git) | 1.4 MB | — | 0
- `tools/sync-harness/bin/Debug` | 6 (0 in git) | 0.7 MB | — | 0
- `tools/sync-harness/bin/Debug/net8.0` | 6 (0 in git) | 0.7 MB | — | 0
- `tools/sync-harness/bin/Release` | 6 (0 in git) | 0.7 MB | — | 0
- `tools/sync-harness/bin/Release/net8.0` | 6 (0 in git) | 0.7 MB | — | 0
- `tools/sync-harness/obj` | 37 (0 in git) | 0.5 MB | — | 0
- `tools/sync-harness/obj/Debug` | 16 (0 in git) | 0.2 MB | — | 0
- `tools/sync-harness/obj/Debug/net8.0` | 16 (0 in git) | 0.2 MB | — | 0
- `tools/sync-harness/obj/Debug/net8.0/ref` | 1 (0 in git) | tiny | — | 0
- `tools/sync-harness/obj/Debug/net8.0/refint` | 1 (0 in git) | tiny | — | 0
- `tools/sync-harness/obj/Release` | 16 (0 in git) | 0.2 MB | — | 0
- `tools/sync-harness/obj/Release/net8.0` | 16 (0 in git) | 0.2 MB | — | 0
- `tools/sync-harness/obj/Release/net8.0/ref` | 1 (0 in git) | tiny | — | 0
- `tools/sync-harness/obj/Release/net8.0/refint` | 1 (0 in git) | tiny | — | 0
- `tools/world` | 4 (3 in git) | tiny | 2026-09-26 | 27
- `tools/world/__pycache__` | 1 (0 in git) | tiny | — | 0
- `tools/zonegen` | 128 (67 in git) | 1.0 MB | 2026-09-27 | 46
- `tools/zonegen/__pycache__` | 3 (0 in git) | tiny | — | 0
- `tools/zonegen/features` | 22 (11 in git) | 0.2 MB | 2026-09-27 | 22
- `tools/zonegen/features/__pycache__` | 11 (0 in git) | 0.1 MB | — | 0
- `tools/zonegen/scenes` | 100 (53 in git) | 0.7 MB | 2026-09-26 | 30
- `tools/zonegen/scenes/__pycache__` | 47 (0 in git) | 0.3 MB | — | 0
