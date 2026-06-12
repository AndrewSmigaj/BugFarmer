# tools/ — THE MAP

Every script, what it does, and where every output goes. **One rule: all
generated output lands under `tools/_generated/`** — nothing else writes
anywhere else.

## The three entry points
| You want to… | Do |
|---|---|
| **SEE everything** (scene cards, zone renders, maps) | open `tools/_generated/previews/index.html` (regen: `python3 tools/zonegen/gallery.py`) |
| **Build / iterate a zone or scene** | `tools/zonegen/` — see `docs/guides/authoring/README.md` |
| **Make / fix sprites** | the art pipeline below — see `docs/guides/art/object_pipeline.md` |

## The output tree (`tools/_generated/`)
```
previews/
  index.html        ← THE GALLERY (open this)
  zones/<id>/       real-art zone renders: full.png + region crops
  maps/             annotated + view_world minimaps
  pieces/ surface/ tests/ underground/ desert/   scene cards by category
  art_review/       one-off art QA images
raw/                gen_sprites' raw API output (pre-clean)
ab/  blocklab/      A/B + block bake-off staging
variants/           sprite variant candidates
scratch/            transient QA (fly_counts.png etc.)
```

## Scripts (tools/ root)
| Script | One-liner |
|---|---|
| `gen_sprites.py` | gpt-image-1 sprite generation from `art/catalog/*.json` (`--dry-run` first) |
| `pixelclean.py` | downscale+quantize raw sprites IN PLACE under Resources (⚠ no-args sweeps EVERYTHING — use per-key snippets / `--items`) |
| `recolor_sprites.py` | tool-tier recolors from a base sprite |
| `ab_generate.py` | two-attempt A/B generation (blocks/walls flow) |
| `blocklab.py` | the block/tile bake-off tool (see blocks.md) |
| `fix_sprite_ppu.py` | normalize all .png.meta to PPU 16 (run after Unity imports new art) |
| `make_diagonal_tiles.py` | composite the 45° road-transition tiles from existing tile art |
| `generate_player_sprites.py` | hand-authored player/gear sprites (pipeline B) |
| `publish_entities.py` | canonical `nakama/data/entities` → client Resources (one-way) |
| `make_scene.py` | the renderer engine (zonegen calls it; rarely run directly) |
| `make_test_zone.py` | tiny deterministic mechanic-test zones |
| `view_world.py` | saved-zone minimap → `previews/maps/<zone>_detail.png` |
| `contact_sheet.py` | sprite contact sheets for review |
| `plot_fly_counts.py` | population graph from a harness run → `scratch/` |
| `run_go_tests.sh` | the Go suite in the builder container |

## Directories
| Dir | What |
|---|---|
| `zonegen/` | the zone/scene builder library + `scenes/` + `registry.py` + `gallery.py` |
| `art/` | art prompt DATA: `style.json` (global) + `catalog/*.json` (per-item) |
| `sync-harness/` | the headless .NET netcode harness (`dotnet run -- --zone <id>`) |
| `archive/` | retired one-off scripts (kept for reference, never run) |

Removed 2026-06 (dead code): `artlab/`, `lab/`, `lab_server.py` (the old variant
viewers — superseded by the gallery + direct renders), `tools/output/` (folded
into `_generated/previews/maps/`).
