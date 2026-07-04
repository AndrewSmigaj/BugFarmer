# tools/ — THE MAP

Every script, what it does, and where every output goes. **One rule: all
generated output lands under `tools/_generated/`** — nothing else writes
anywhere else.

## The three entry points
| You want to… | Do |
|---|---|
| **SEE everything that's in the game** | browse `tools/_generated/previews/catalog/` (rebuild: `python3 tools/world/previews.py`) |
| **SEE the zones / scenes** | browse `tools/_generated/previews/zones/<id>/` + the theme folders |
| **Build / iterate a zone or scene** | `tools/zonegen/` — see `docs/guides/authoring/README.md` |
| **Make / fix sprites** | the art pipeline below — see `docs/guides/art/object_pipeline.md` |

## The output tree (`tools/_generated/`)
Plain PNG folders — open them in a file explorer, no html. Previews = exactly 4 folders
(rule: `docs/guides/authoring/ORGANIZATION.md`).
```
previews/
  catalog/<category>/  every IN-GAME object by category (furniture/ blocks/ nature/ bugs/ tiles/ …);
                       each: _sheet.png (all at a glance) + <id>.png per object.
                       Rebuild: python3 tools/world/previews.py  (from entity data — never drifts).
  examples/<feature>/  reusable technique demos (buildings/ blocks/ roads/ water/ gardens/ farming/)
  zones/<id>/          full.png + region crops + scenes/ (the vignettes that compose the zone)
  player/              player sprite + animation previews
raw/ ab/ blocklab/ variants/ scratch/ ecology_charts/   sprite staging + transient QA charts
```

## Scripts — by folder (run `python3 tools/<folder>/<script>.py`)
**`sprites/`** — art generation + cleanup (most hit the paid API or overwrite art — read the warnings)
| Script | One-liner |
|---|---|
| `gen_sprites.py` | gpt-image-1 sprite gen from `art/catalog/*.json` (`--dry-run` first). `--ref <raw.png>` = FAMILY consistency: every key reproduces the reference sprite's exact silhouette/angle/style, changing only its look-row material (feed the hero's RAW 1024px cache from `_generated/raw/`, e.g. the 7 metal bars from one hero ingot) |
| `pixelclean.py` | downscale+quantize sprites IN PLACE under Resources (⚠ no-args sweeps EVERYTHING — use per-key / `--items`) |
| `recolor_sprites.py` | tool-tier recolors from a base sprite |
| `ui_sprites.py` / `veg_sprites.py` | UI kit + vegetation-stage sprites |
| `generate_player_sprites.py` | hand-authored player/gear sprites (pipeline B) |
| `fix_sprite_ppu.py` | normalize all `.png.meta` to PPU 16 (`--dry-run` to preview) |
| `ab_generate.py` | two-attempt A/B generation (blocks/walls flow) |
| `blocklab.py` | the block/tile bake-off tool (see `blocks.md`) |
| `make_diagonal_tiles.py` | composite the 45° road-transition tiles |

**`world/`** — zones, scenes, previews
| `previews.py` | the content CATALOG + ALL scene previews (from entity data + each scene's `PREVIEW`) |
| `view_world.py` | saved-zone minimap → `previews/zones/<zone>/<zone>_detail.png` |
| `make_test_zone.py` | tiny deterministic mechanic-test zones |

**`ecology/`** — sim tuning + charts
| `run_config.py` / `compare_configs.py` | bug-lab config runs + comparison (use `make_bug_lab`) |
| `make_bug_lab.py` | build the ecology test zone |
| `plot_*.py` / `make_dashboard.py` | population / perf charts + the perf dashboard |

**`netcode/`** — determinism-harness analysis
| `sync_diff.py` / `test_sync_diff.py` | hash-stream diff (the sync gate) + its self-test |
| `diag_determinism_provenance.py` / `diag_leg_divergence.py` | determinism diagnostics |

**`data/`** — `publish_entities.py` (canonical `nakama/data/entities` → client Resources, one-way)

**`tools/` root** — `make_scene.py`: the shared renderer **library** (imported by `zonegen`; rarely run directly).
`*.sh` harness/test runners (`run_go_tests.sh`, `run_sync_test.sh`, …).

## Directories
| Dir | What |
|---|---|
| `zonegen/` | the zone/scene builder library + `scenes/` + `scene_preview.py` (the one scene→preview render path) |
| `art/` | art prompt DATA: `style.json` (global) + `catalog/*.json` (per-item) |
| `player_sprites/` | player paper-doll generation modules (imported by `sprites/generate_player_sprites.py`) |
| `sync-harness/` | the headless .NET netcode harness (`dotnet run -- --zone <id>`) |
| `bug_lab_configs/` | ecology tuning experiment configs (json) |
| `archive/` | retired one-off scripts (kept for reference, never run) |

Removed (dead code): `artlab/`, `lab/`, `lab_server.py` (old variant viewers),
`zonegen/gallery.py` + `previews/index.html` (the html gallery), `contact_sheet.py`
(hand-listed sprite sheets — replaced by `previews.py`, which is generated from data).
