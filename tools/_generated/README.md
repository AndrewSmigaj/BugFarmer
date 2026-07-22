# `tools/_generated/` — the map

Everything here is **generated** or **work-in-progress** output. Almost all of it is gitignored (regenerable,
or local-only WIP); only a curated few things are committed (this map, the ecology charts' current-setup, and
the player workspace tier docs). **Read this before saving a generated file or making a folder** — every kind
of output already has a home, and inventing a new top-level bucket is how the mess starts
(`docs/guides/authoring/ORGANIZATION.md`).

| sibling | what it is | who writes it | paid? | in git? |
|---------|-----------|---------------|-------|---------|
| `previews/` | deterministic VIEWS of committed art, to look at | `world/previews.py` (catalog), `zonegen/scene_preview.py` (zones/examples), `make_scene.py` | free · regenerable | no |
| `raw/` | the expensive gpt-image render CACHE (1024px), input to cleaning | `sprites/gen_sprites.py`, `gen_dug_tiles.py` | **PAID — don't delete** | no |
| `ab/` | A/B two-variant generations; `_B` = the parked alternate | `sprites/ab_generate.py` | **PAID** | no |
| `blocklab/` | block/tile variant bake-offs | `sprites/blocklab.py` | **PAID** | no |
| `workspace/` | WORK-IN-PROGRESS art creation (see below) | you + the `aipipe` pipeline | mixed | structure only |
| `ecology_charts/` | NON-ART sim/ecology charts (the tuning picture) | `ecology/run_config.py` + plotters | free | **yes (curated subset)** |
| `footprints.md` | generated entity-footprint reference | `data/footprints.py` | free | no |

## `previews/` — the four folders (per `ORGANIZATION.md`)
`catalog/<category>/` (every in-game object, rendered from entity data) · `examples/<feature>/` (reusable
technique demos) · `zones/<zone>/` (a place: full render + its composing scenes). The player is **not** here
(see below). One command rebuilds them all: `python3 tools/world/previews.py`. There are also a few
occasional category renders (`ui/`, `title/`, …) that don't fit the four cleanly — an open tidy item; don't add
more without a reason.

## `workspace/` — work-in-progress art creation
The one place active WIP lives. Today it holds `player/`; other asset types get their own subfolder only
if/when there's real work (don't create one speculatively).

### `workspace/player/` — the player character + wearables
Governed by the **player-sprites** skill (`.claude/skills/player-sprites/SKILL.md`).
- `refs/` — durable references you generate/mask against: the locked base, the bald base, the green mannequin.
- `in-progress/<slug>/` — active creation of a NEW sprite/set (e.g. `in-progress/copper_armor/`). **"New hat"
  starts here.** When done, the pieces publish to `Resources/Player/layers/…`.
- `archived/` — dated old experiments / superseded versions.
- The FINISHED sprite the game loads is **`Resources/Player/layers/{slot}/{id}_{dir}.png`** — that is the
  single "current"; **polish it by editing that file directly.** No copy of it lives here (no `current/`, no
  `.ase` masters — a second copy just drifts). `README.md` + `CATALOG.md` here are committed; WIP images are
  local-only.

## What does NOT belong here
Ad-hoc QA renders (`*_check.png`), scratch experiments, one-off logs — delete them or file them under a
`workspace/…/archived/`. If something doesn't obviously fit a row above, it's almost certainly a WIP
(→ `workspace/`) or a throwaway (→ delete). Don't invent a new top-level bucket.
