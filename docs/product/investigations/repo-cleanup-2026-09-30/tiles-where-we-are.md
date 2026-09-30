# Tiles: where we are (checked 2026-09-30)

> **Step A of the tiles trial.** The owner asked on 2026-09-30 for the repo to make it obvious which tiles and which
> tile scripts are official, and which are old experiments. This page only looks: nothing was moved, deleted or
> changed. **The picture:** [tiles-in-the-game.png](tiles-in-the-game.png) shows every tile the game uses, at one size.

## In short
- **The game shows ground tiles from one folder only:** `BugFarmerClient/Assets/Resources/Tiles/`, which holds 29
  files. A tile anywhere else is not in the game.
- **The new grass is in the game.** It shipped on 2026-07-26 (commit `5f6fc1d5`):
  - five 16×16 variants, which the game mixes square by square, the same on every player's screen;
  - grass tufts drawn on top;
  - it's used in 20 of the 21 zones;
  - how it works is written up in `docs/product/architecture/architecture_world.md`, section 0.
- **The other ground tiles are June 2026 art** from the old route: an image generated, then shrunk. The exceptions
  are the eight diagonal road corners (built in code on 2026-06-11) and the dug soil (2026-07-10). BACKLOG's art
  plan ("Now — art") redraws them all.
- **Only four scripts write into the game's tile folder:**
  - `gen_sprites.py` and `pixelclean.py`, the old route;
  - `make_diagonal_tiles.py`, the road corners;
  - `fix_sprite_ppu.py`, which changes only import settings, never the pictures.

  The new grass, its tufts and the dug soil were copied in by hand from research folders.
- **Most of the confusing folders are not in git.** `blocklab/`, `ab/`, `raw/`, `scratch/`, `variants/` and
  `previews/` under `tools/_generated/` exist only on the owner's PC, because git ignores them. Nobody who downloads
  the repo sees them. In `tools/_generated/tiles/`, only the README and two comparison sheets are in git.
- **Found along the way:**
  - The diagonal road corners were cut from the June grass, so they no longer match today's grass; the picture shows
    it.
  - The grass research README still says nothing was published.
  - The catalog preview of tiles dates from 5 July and shows the old grass.
  - The client holds an old copy of the tile list that nothing loads.

## 1. The tiles in the game
Per-zone counts are the number of zones whose saved ground uses the tile.

| Group | Files | Size | Where it's used | Added / last changed | Made by |
|---|---|---|---|---|---|
| New grass | `grass`, `grass_v2`…`grass_v5` | 16×16 | `grass` in 20 of the 21 zones. The game picks one of the five per square (`TilemapManager.cs:984-999`) | 2026-07-26. `v4` and `v5` are new; `grass`, `v2` and `v3` replaced the June files | The July grass research, copied in by hand (section 2) |
| Grass tufts (in `Resources/Objects/`, not tiles) | `grass_tuft_1`…`4` | small | drawn over grass squares by `GrassTuftRenderer.cs` | 2026-07-26 | `tile_tufts.py`, copied in by hand |
| Ground | `dirt` (8 zones), `sand` (5), `mud` (4), `cave_floor` (1), `stone_floor` (5), `wood_floor` (6), `stone_path` (4), `water_shallow` (7), `water_deep` (7), `bridge_wood` (4) | 32×32 | the zones listed | added 2026-06-03; 18 tiles re-saved 2026-06-10 | `gen_sprites.py`, from the prompts in `tools/art/catalog/tiles.json` |
| Garden | `garden_plot` (6 zones), `garden_plot_wet` | 32×32 | the wet plot appears when a plot is watered or rained on (`handlers_farming.go`, `handlers_env.go:366`, `PlacementController.cs`) | 2026-06-03 | `gen_sprites.py` |
| Digging | `dug_soil` | 32×32 | appears when you dig (`handlers_farming.go`) | 2026-07-10 | `gen_dug_tiles.py`, copied in by hand |
| Diagonal road corners | `dirt_path_d_ne/nw/se/sw` (3 zones), `stone_path_d_ne/nw/se/sw` (2 zones) | 32×32 | where a road turns at 45° | 2026-06-11, never rebuilt | `make_diagonal_tiles.py`, from the grass and road tiles as they were that day |
| Unused | `bridge_stone`, `rug_large`, `rug_small` | 32×32 | no zone and no code use them. The Large Rug furniture draws its own picture, `Resources/Objects/rug_large.png` | 2026-06-03 | `gen_sprites.py`: the bridge from `tiles.json`, the rugs from `tools/art/catalog/decor.json` |

The tile list itself lives in three places:
- **`nakama/data/tiles.json`** is the game's definition of the 25 tile types (29 files = 25 types + 4 grass variants).
  It says how each one behaves: walking speed, what can be built on it, and what tools do to it. **This is the source
  of truth.**
- **`nakama/data/entities/ground_recipes.json`** lists the 8 grounds a player can lay.
- **`BugFarmerClient/Assets/Resources/Data/tiles.json`** is an old copy of the list that nothing loads. It lacks the 9
  newest tiles: the 8 road corners and `dug_soil`.

## 2. Where each tile came from (the evidence)
**The new grass (`grass_01`).**
1. On 2026-07-25, `tile_experiments.py` generated grass candidates by ten methods (commit `bb90c857`). `grass_01` is
   method A1 (`tile_scene.py:159`, `tile_variant_sheet.py:33`).
2. On 2026-07-26, every candidate was re-made at the game's true size, 16×16, from the saved renders, with no new
   images bought (commit `cdde04b8`). `tile_variant_sheet.py` drew the variants as one sheet and forced them onto the
   parent tile's six colours. `tile_tufts.py` drew the four tufts.
3. The same day, the chosen set was copied into the game by hand (commit `5f6fc1d5`), together with the game code that
   mixes the variants and draws the tufts. That commit records a headless Unity build with no errors. The grass was
   turned 90° later that day (commit `c04d8e60`).

**The June tiles.**
- `gen_sprites.py` asks the image API for a picture, then shrinks and cleans it in one go. Its prompts live in
  `tools/art/catalog/tiles.json` (14 tiles) and `decor.json` (the two rugs).
- The tiles were first committed on 2026-06-03 (`97a71aba`).
- On 2026-06-10, 18 tiles and 38 objects were re-saved with small changes in one commit about crop art (`17d585d9`).
  No script is in that commit; it was probably a re-clean, but that's not certain.

**The diagonal road corners.** `make_diagonal_tiles.py` builds each corner by cutting a road tile and the grass tile
along the diagonal (its header, and lines 34 and 66). It was run once, on 2026-06-11 (`f51f972c`), before the new
grass existed. That's why the corners still show the June grass.

**The dug soil.** `gen_dug_tiles.py` made candidates into `tools/_generated/previews/dug_experiment/`, with the renders
backed up as `tools/_generated/raw/dug_exp_*`. One was copied in by hand on 2026-07-10 (`17f065fb`).

## 3. Every other place that holds tiles
| Place | In git? | What's in it | Made by | What it is |
|---|---|---|---|---|
| `tools/_generated/tiles/` | README + 2 sheets | the July grass research: 27 candidates at 32×32, 40 at 16×16, 28 paid renders, 8 references, the 4 tufts, 11 comparison sheets | `tile_experiments.py`, `tile_variant_sheet.py`, `tile_tufts.py`, `gen_tiles_handauthored.py`, `tile_lab.py`, `tile_scene.py` | **Research record.** The grass came from here. Its README (2026-07-25) still says nothing was published. |
| `tools/_generated/raw/` | no | 739 full-size renders (1.16 GB) of all kinds of art; 37 are ground tiles or dug-soil tests | `gen_sprites.py` and others | **Backup of paid renders.** Scripts read it (`gen_sprites.py`, `tile_variants.py` and others), so it stays where it is. |
| `tools/_generated/blocklab/` | no | 44 files, 6–7 June: a block-prompt contest in three rounds, plus three cave-floor tries | `blocklab.py` | **Old experiment**, mostly blocks |
| `tools/_generated/ab/` | no | 128 alternate versions of all kinds of art (5–6 June), a few of them tiles (e.g. `cave_floor_B`) | `ab_generate.py` | **Old experiment** |
| `tools/_generated/variants/` | no | variant sheets for cave floor, blocks and walls (7–8 June); `selection.json` records the picks made then | the Art Lab variant viewer (`tools/artlab/`), added 2026-06-08 and removed as dead code 2026-06-12 | **Old experiment.** Nothing uses it now. |
| `tools/_generated/scratch/` | no | 276 files, December–July: block-prompt tests, contact sheets, old zone pictures, and more | several; `tools/ecology/plot_fly_counts.py` still writes a chart here | **Scratch.** Mixed and still written to, so it's not a tiles question. |
| `tools/_generated/previews/catalog/tiles/` | no | 25 pictures, one per tile type, from 2026-07-05 | `tools/world/previews.py` | **Preview, out of date.** It predates the new grass. |
| `tools/_generated/previews/dug_experiment/` | no | 7 dug-soil candidates (2026-07-10) | `gen_dug_tiles.py` | **Candidates.** `dug_soil` was chosen from here. |
| `tools/_generated/previews/examples/shaped_ground/` | no | 4 sheets of blended ground shapes (2026-07-10) | `composite_tiles.py` | **Preview** |
| `tools/_generated/previews/examples/ground-edges/` | no | the two laying-ground pictures (2026-09-29) | `tools/gdd/ground_edges_sheet.py`, `ground_shapes_mockup.py` | **Design pictures** |
| `grass_necesse.png`, `grass_stardew.png`, `grass_stardew_closeup.png` (top of the repo) | yes | grass from other games, the references for the July research (committed 2026-07-25) | — | **Research references in the wrong place** (question 3) |
| `tools/art/catalog/tiles.json` (and `decor.json`, for the rugs) | yes | the image prompts behind the June tiles | read by `gen_sprites.py` | **Prompts for the old route.** They're the owner's; the art pass decides what replaces them. |

## 4. Every tile script
**Write into the game's tile folder:**

| Script | What it does (from its own header) | What it is |
|---|---|---|
| `tools/sprites/gen_sprites.py` | the old image route: prompt, paid render, shrink, then save into the game (tiles go to `Resources/Tiles/`) | **Old route.** It made the June tiles. Paid. |
| `tools/sprites/pixelclean.py` | re-cleans sprites in place | **Old route.** Its header still says it writes to `tools/pixelclean_out/`, but the code writes in place (line 50 sets its output to the game's own sprite folder). |
| `tools/sprites/make_diagonal_tiles.py` | builds the 8 road corners from a road tile and the grass tile | **Made tiles in the game.** Rebuilding the corners is a later decision: the grass is now 16×16 and the roads 32×32, so it isn't a simple re-run. |
| `tools/sprites/fix_sprite_ppu.py` | sets import settings (sharp pixels) for tiles and other sprites | **Live maintenance.** It touches settings only. |

**Read the game's tiles and draw pictures elsewhere:**

| Script | What it does | What it is |
|---|---|---|
| `tools/sprites/composite_tiles.py` | a Python copy of the game's shaped-ground blending, for previews without Unity | **Live helper.** `shovel_panel_mockup.py` also uses it. |
| `tools/world/previews.py` | draws the catalog previews, tiles included | **Live** |

**The July grass research.** None of these writes into the game, and `tile_experiments.py` says so in its header.

| Script | What it does | What it is |
|---|---|---|
| `tile_experiments.py` | grass by ten methods; `grass_01` is its A1 | **Research** |
| `tile_variant_sheet.py` | variants drawn as one sheet on the parent's colours | **Research** that made the shipped variants |
| `tile_tufts.py` | the tuft sprites | **Research** that made the shipped tufts |
| `tile_variants.py` | the first way of making variants. Their colours drifted, which is what `tile_variant_sheet.py` was written to fix (its header says so) | **Research, earlier method** |
| `tile_lab.py` | measures a tile and shows it repeated | **Research tool**, useful again for the art pass |
| `tile_scene.py` | shows a tile with the player and a tree standing on it, at true size | **Research** |
| `gen_tiles_handauthored.py` | three hand-drawn candidates, H1–H3; none shipped | **Research** |

These research scripts depend on each other:
- `tile_tufts.py`, `tile_variants.py` and `tile_variant_sheet.py` import `tile_experiments.py`;
- `tile_experiments.py` imports `gen_sprites.py` and `pixelclean.py`;
- all of them find the repo by counting parent folders.

Moving them would therefore mean changing their code. It isn't a simple tidy.

**Dug soil, June experiments, and retired scripts:**

| Script | What it does | What it is |
|---|---|---|
| `tools/sprites/gen_dug_tiles.py` | paid dug-soil candidates | **Research** that shipped one tile |
| `tools/sprites/dug_context_sheet.py` | shows those candidates in context | **Research** |
| `tools/sprites/blocklab.py` | the June block and tile prompt contest | **Old experiment** |
| `tools/sprites/ab_generate.py` | the June alternates ("A" went into the game, "B" was parked in `ab/`) | **Old experiment** |
| `tools/sprites/drawn/tiles.py` | grass, dirt and 16 transition tiles drawn in code (September) | **Rejected** for game art (`tools/sprites/drawn/README.md`) |
| `tools/archive/generate_garden_tiles.py` | the first 16×16 garden tiles, written to a folder that no longer exists | **Archived** |

## 5. Not sure — questions for the owner
1. **The grass density.** BACKLOG's art plan (2026-09-26) says the July grass is 16 pixels per square and should be
   redone at 32, like every other tile. On 2026-09-30 the owner thought the new grass is probably fine. Which holds?
   If the grass stays, the diagonal road corners still need redrawing to match it.
2. **`bridge_stone`, `rug_large` and `rug_small`** are ground tiles nothing uses. Keep them for later, or mark them as
   old?
3. **The three screenshots of other games' grass** in the repo's top folder. The repo is public, so they're shared with
   everyone. Move them out of git (kept on the owner's PC with the other research), or keep them?
4. **The 2026-06-10 re-save** of 18 tiles, in a commit about crop art with no script in it. It was probably a
   re-clean. It changes nothing today; this is just a note.

## 6. Step B: what would change, only with the owner's yes
**On the owner's PC only.** These folders aren't in git, so nothing changes on GitHub.
- **Move the June experiment folders** (`blocklab/`, `ab/`, `variants/`) into one folder,
  `tools/_generated/old-experiments/`, each keeping its name.
  - They're mostly blocks and other art, with only a few tiles; it can wait for the objects area if you prefer.
  - Checked: no script reads them (all of `tools/` and the hooks searched). Re-running `blocklab.py` or
    `ab_generate.py` would simply make a fresh folder.
- **Leave `raw/` and `tiles/` where they are,** because scripts read them. Add a short README to each saying what it
  is.
- **Refresh the catalog previews** (`python3 tools/world/previews.py`), so they show today's grass.

**In git:**
- **Correct the grass research README:** the grass shipped on 2026-07-26 as `grass_01`.
- **Label the tile scripts in `tools/README.md`** as in section 4 (official, research, old), so the folder reads
  without guessing. The scripts stay where they are.
- **Add to BACKLOG:**
  - the road corners showing the June grass;
  - the unused client copy of `tiles.json`;
  - the out-of-date header in `pixelclean.py`.

Nothing is deleted. Everything else waits for the answers in section 5.
