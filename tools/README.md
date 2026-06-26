# tools/ — THE MAP

Every script, what it does, and where every output goes. **One rule: all
generated output lands under `tools/_generated/`** — nothing else writes
anywhere else.

## The three entry points
| You want to… | Do |
|---|---|
| **SEE everything that's in the game** | browse `tools/_generated/previews/catalog/` (rebuild: `python3 tools/previews.py`) |
| **SEE the zones / scenes** | browse `tools/_generated/previews/zones/<id>/` + the theme folders |
| **Build / iterate a zone or scene** | `tools/zonegen/` — see `docs/guides/authoring/README.md` |
| **Make / fix sprites** | the art pipeline below — see `docs/guides/art/object_pipeline.md` |

## The output tree (`tools/_generated/`)
Plain PNG folders — open them in a file explorer, no html.
```
previews/
  catalog/<group>/  every IN-GAME object by category (furniture/ blocks/ nature/ bugs/ tiles/ …)
                    each group: _sheet.png (all at a glance) + <id>.png per object.
                    generated from entity data by tools/previews.py — never drifts.
  zones/<id>/       full.png + region crops + scenes/ (the vignettes that compose the zone)
  examples/<theme>/ generic example/test scene cards (surface/ underground/ desert/ pieces/ tests/ + ui/ veg/)
  player/           player sprite + animation previews
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
| `view_world.py` | saved-zone minimap → `previews/zones/<zone>/<zone>_detail.png` |
| `previews.py` | the content CATALOG: every in-game object by category → `previews/catalog/` (from entity data) |
| `plot_fly_counts.py` | population graph from a harness run → `scratch/` |
| `run_go_tests.sh` | the Go suite in the builder container |

## Directories
| Dir | What |
|---|---|
| `zonegen/` | the zone/scene builder library + `scenes/` + `registry.py` (scene scale catalog) |
| `art/` | art prompt DATA: `style.json` (global) + `catalog/*.json` (per-item) |
| `sync-harness/` | the headless .NET netcode harness (`dotnet run -- --zone <id>`) |
| `archive/` | retired one-off scripts (kept for reference, never run) |

Removed (dead code): `artlab/`, `lab/`, `lab_server.py` (old variant viewers),
`zonegen/gallery.py` + `previews/index.html` (the html gallery), `contact_sheet.py`
(hand-listed sprite sheets — replaced by `previews.py`, which is generated from data).
