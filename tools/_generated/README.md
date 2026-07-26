# `tools/_generated/` — the map

Everything here is **generated** or **work-in-progress** output. Almost all of it is gitignored (regenerable,
or local-only WIP); only a curated few things are committed (this map, the ecology charts' current-setup, and
the player structure docs). **Read this before saving a generated file or making a folder** — every kind
of output already has a home, and inventing a new top-level bucket is how the mess starts
(`docs/guides/authoring/ORGANIZATION.md`).

| sibling | what it is | who writes it | paid? | in git? |
|---------|-----------|---------------|-------|---------|
| `previews/` | deterministic VIEWS of committed art, to look at | `world/previews.py` (catalog), `zonegen/scene_preview.py` (zones/examples), `make_scene.py` | free · regenerable | no |
| `raw/` | the expensive gpt-image render CACHE (1024px), input to cleaning | `sprites/gen_sprites.py`, `gen_dug_tiles.py` | **PAID — don't delete** | no |
| `ab/` | A/B two-variant generations; `_B` = the parked alternate | `sprites/ab_generate.py` | **PAID** | no |
| `blocklab/` | block/tile variant bake-offs | `sprites/blocklab.py` | **PAID** | no |
| `player/` | player character + wearable art work (see below) | you + the `aipipe` pipeline | mixed | structure only |
| `tiles/` | ground-TILE R&D: candidates + tiling comparison sheets (`README.md` = the findings) | `sprites/tile_experiments.py`, `gen_tiles_handauthored.py`; judge with `sprites/tile_lab.py` | **PAID** raws | findings + 2 sheets |
| `ecology_charts/` | NON-ART sim/ecology charts (the tuning picture) | `ecology/run_config.py` + plotters | free | **yes (curated subset)** |
| `footprints.md` | generated entity-footprint reference | `data/footprints.py` | free | no |

## `previews/` — the four folders (per `ORGANIZATION.md`)
`catalog/<category>/` (every in-game object, rendered from entity data) · `examples/<feature>/` (reusable
technique demos) · `zones/<zone>/` (a place: full render + its composing scenes). The player is **not** here
(see below). One command rebuilds them all: `python3 tools/world/previews.py`. There are also a few
occasional category renders (`ui/`, `title/`, …) that don't fit the four cleanly — an open tidy item; don't add
more without a reason.

## `player/` — player character + wearable art (start at `player/README.md`)
The one home for player art (governed by the **player-sprites** skill). Layout:
- **`current/`** — a preview (`character.png`) of what's LIVE in the game + a note. The real files the game
  loads are `Resources/Player/layers/{slot}/{id}_{dir}.png` (the single "current" — polish those directly).
- **`in-progress/<item>/<YYYY-MM-DD_HHMM_label>/`** — active work, per item, per **DATED attempt** (newest date
  = the latest). Each attempt: `suit.png` (render to cut) + `pieces/` (cut game pieces). "New hat" → a new
  dated attempt folder; never a loose dump.
- **`references/`** — the ONE shared `base` / `bald` / `mannequin` you mask against.
- **`old/`** — finished + abandoned stuff, out of the way.
- On approve → publish an attempt's `pieces/` to `Resources/Player/layers/…`, refresh `current/`. Committed to
  git: `player/README.md`, `player/current/{README.md,character.png}`, `player/HOW_TO_ASEPRITE.md`; WIP images
  are local-only.

## What does NOT belong here
Ad-hoc QA renders (`*_check.png`), scratch experiments, one-off logs — delete them or file them under
`player/old/` (for player art). If something doesn't obviously fit a row above, it's almost certainly a WIP
(→ `player/` for player art) or a throwaway (→ delete). Don't invent a new top-level bucket.
