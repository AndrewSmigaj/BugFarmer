I'll start by confirming the known stale reference and reading the primary docs in parallel.

---

Confirmed the known drift. Now let me read the remaining skills and guides in parallel.

---

Now let me read the remaining skills and start verifying claims in parallel.

---

Now let me verify a large batch of claims. First, file/directory existence and key function locations.

---

Species and key path drifts already emerging. Let me verify the Go function references and remaining paths.

---

Let me verify the remaining function-level claims: carcass, shop struct, ecology config, netcode/frontier symbols, and Go test files.

---

Let me resolve the missing frontier-sync symbols and verify the Go test suite + client files.

---

Client-side frontier symbols confirmed. Now let me check the named guides, the skills catalog, and a few remaining anchors.

---

Let me verify a few code anchors and scan the named guides for code/command references.

---

Let me verify caves/ant scene files and entity ids, and scan the remaining guides.

---

Let me check the README species line, builder module files, and remaining scene/guide references.

---

Object_pipeline.md drift emerging (recolor workflow). Let me verify the remaining art-pipeline files and scan CORRECTIONS.md.

---

Let me do a final verification batch on a few remaining references.

---

Verification complete. Here is the evidence-anchored drift audit.

## DRIFT AUDIT — load-bearing docs vs. current repo

Legend: **DRIFT** = a coder would be actively misled · **MINOR** = imprecise but self-correcting · **OK** = verified accurate.

### `.claude/skills/economy/SKILL.md`
| doc:line | claim | reality |
|---|---|---|
| **L14** | "`nakama/modules/world/entities.go` `LoadEntities`, ~L288-305" | **DRIFT (confirmed).** Function is `LoadAllEntities`, and it's at `entities.go:327` — the name is wrong and the line window is ~40 lines off. |
| L26 | "`breakOccupantAt` rolls `def.GetDrops()` (`handlers_world.go` ~L547)" | **MINOR.** `breakOccupantAt` is at `handlers_world.go:504`; `def.GetDrops()` is at **L553** (not 547). Within the "~" hedge but the number is stale. |
| L31 | `spawnCarcass`, `handlers_combat.go` | OK — `spawnCarcass` at `handlers_combat.go:324`. |
| L32 | shop occupant `world.shop{kind,sells,buys}` on `OpCodeAction(2)` → `handlers_shop.go` | OK — `ShopData{Kind,Sells,Buys}` in `entities.go:176-178`; `OpCodeAction int64 = 2`; `handlers_shop.go` exists. |
| L42 | nests are stations (`brood.go`) | OK — `brood.go` exists. |
| L55 / L72 | `publish_entities.py`, `run_go_tests.sh`, `catalog_coverage.py` | OK — all three exist. |
| L48-49 | `architecture_items.md` §0 accurate / §1-15 retired | OK — file has "## 0. Item & inventory model" and "## 1–15 (retired)". |

### `.claude/skills/author-zone/SKILL.md`
| doc:line | claim | reality |
|---|---|---|
| **L152** | "only species in `species.json` spawn (currently `fly_common`, `butterfly_meadow`, `wasp_common`, `centipede_garden`)" | **DRIFT.** `species.json` now has **11** species — the 4 listed **plus** `millipede`, `beetle_carrion`, `bee_honey`, `dragonfly_blue`, `firefly`, `ant_worker`, `ant_scout`. Half the roster is missing. (The parallel list in `authoring/README.md:84-89` is more current but still omits `ant_worker`/`ant_scout`.) |
| L22 | "Previews live in exactly four folders (`catalog/ examples/ zones/ player/`)" | **MINOR.** `tools/_generated/previews/` also contains `title/` and `ui/` folders (plus loose `_check` PNGs). The "exactly four" invariant is stale. |
| L100 | "`scene_preview.py` is the one render path" | OK — exists at `tools/zonegen/scene_preview.py` (imported as `from scene_preview import render`). |
| L67-90, L120-141 | builder API, `features/`, scenes, `view_world.py`, `make_test_zone.py` | OK — all files/methods verified (`zonebuilder.py`, `render.py`, `previews.py`, `view_world.py`, `tools/world/make_test_zone.py`, all named scenes). |

### `CLAUDE.md`
| doc:line | claim | reality |
|---|---|---|
| **L34** | "the test-zone generator (`make_test_zone.py`)" implying `tools/make_test_zone.py` | **DRIFT.** File is at **`tools/world/make_test_zone.py`**; `tools/make_test_zone.py` does not exist. (`authoring/README.md:82` and `author-zone` both use the correct `tools/world/` path.) |
| L60 | "Previews = exactly `catalog/ examples/ zones/ player/`" | **MINOR.** Same as author-zone L22 — `title/` and `ui/` also exist. |
| L43-54 | skill catalog (13 skills) | OK — matches `.claude/skills/` exactly (add-object, author-zone, bug-spawning, certainty-assessment, deep-investigate, ecology-tuning, economy, frontier-sync, perf-tuning, regenerate-sprite, run-backend, test-changes, zone-craft). |
| L78-79 | "`village_21_B`'s big lake is at (x=46, y=48) … SW quadrant" | OK — `zone_village_21_B.py:86`: `lake(b, 46, 48, 52, …) # SW, the lake`. |
| L99-104 | command block (`publish_entities.py`, `gen_sprites.py`, `pixelclean.py`, `make_scene.py`; "default source = placeables") | OK — all exist; `gen_sprites.py:650` `default="placeables"`. |
| L86,110,115-123 | `object_pipeline.md`, `architecture_swarm_sync.md` §0, `.claude/{complex-change-review,lenses,git-guidelines}.md`, `ARCHITECTURE.md`, `BACKLOG.md` | OK — all exist. |

### `.claude/skills/test-changes/SKILL.md`
| doc:line | claim | reality |
|---|---|---|
| **L31** | "Suite: `centipede combat predation nest fruit_tree release swarm_population player_hp equip world_env host_plant brood forage_pool ecology_director predator_starvation shop recipe_unlock`" | **DRIFT (incomplete).** All 17 exist, but the suite now has **30** `*_test.go`. Not listed: `ant_test, bee_test, colony_test, condition_test, craft_stations_test, death_test, initial_spawn_test, predator_breeding_test, resource_query_index_test, station_resolve_test, watering_bed_test, world_save_test`. The skill's own §0 rule ("add its line here") has been skipped repeatedly. |
| **§2.5 (L56-113)** | the "`bug_lab` 6× chart loop … THE living-ecology rig" (`make_bug_lab.py` + `plot_fly_counts.py` + `--duration 150`) | **DRIFT (superseded workflow).** `make_bug_lab.py` still exists and runs, but the dedicated `ecology-tuning` skill §1 says **"`bug_lab` … Archived. Don't balance on it,"** and to tune on `village_21_B` via `run_config.py`. test-changes §2.5 still presents the archived rig as the balance workflow. |
| **§2.5 L80-81 vs L97-102** | internal: L80 says `sim_batch:8`+`call_rate:60` = **48×** (150s ≈ 8.5 game-days); L97-102 says **6×** (600s ≈ 4.3 game-days) | **DRIFT (internal contradiction).** `make_bug_lab.py:33-34` confirms `call_rate:60` + `sim_batch:8` = 48×, so the "6×" arithmetic in L97-102 is the stale half. |
| L32-38 | `shop_test.go` covers `sell_batch` | OK — `shopSellBatch` + `TestShopSellBatch{Mixed,DuplicateSlotNoDoublePayout,NegativeQtyRejected,BugDealer}`. |
| §2-3 | `run_go_tests.sh`, sync-harness (`Scenarios.cs`/`Actions.cs`/`WorldModel.cs`), `harness_persist_test.sh`, `run_sync_latejoin.sh`, `netcode/sync_diff.py`, `HeadlessSyncTest.cs`, `SyncTestBuild.cs`, `sim-determinism`, `match.go checkDriftSampling` | OK — all verified to exist (`checkDriftSampling` at `match.go:3024`). |
| L97 | "`DayLengthTicks = 8400`" | OK — `match.go:51 const DayLengthTicks = 8400`. |

### `.claude/skills/ecology-tuning/SKILL.md`
| doc:line | claim | reality |
|---|---|---|
| **description / §0** | "6-species food web (fly, butterfly, wasp, centipede, millipede, beetle)" | **DRIFT.** `species.json` now has **11** species; the web also includes `bee_honey`, `dragonfly_blue`, `firefly`, `ant_worker`, `ant_scout`. The "6-species" framing understates the current roster. |
| **§4 (L100-106)** | "Shared dials (`ecology_tuning.json`): … `spawn_satiation`, nest economy (`nest_brood_cap`/`nest_hatch_*`/`nest_founding_size`/`nest_found_dist_*`), and `max_litter`/`litter_regen_per_tick`" | **DRIFT.** `ecology_tuning.json` actually contains only 8 keys: `max_nectar, nectar_regen_per_tick, max_host_capacity, host_regen_per_tick, host_breed_cost, predator_breed_satiation, litter_regen_per_tick, starvation_death_secs`. **`max_litter`, `spawn_satiation`, and all `nest_*` dials are NOT in this file** — a tuner told they live here will not find them. |
| §1-2 | tune on `village_21_B`; `run_config.py`; `bug_lab_configs/*.json`; `v21b_baseline` = no deltas; seed 1337 | OK — `run_config.py`, `tools/bug_lab_configs/`, and `v21b_baseline.json` all exist. |
| §4 | levers in `species.json`, `handlers_farming.go` (fruit→rot), `ecology_director.go` | OK — files/vars exist (`nectarRegenPerTick`/`hostRegenPerTick` at `handlers_farming.go:1486/1429`). |

### `docs/guides/art/object_pipeline.md`
| doc:line | claim | reality |
|---|---|---|
| **L147, L157** | "Tiers are PALETTE RECOLORS of the family's wood base (`recolor_sprites.py`) … `recolor_sprites.py --family pickaxe # derive {family}_{tier} icons`" | **DRIFT (superseded workflow).** `add-object/SKILL.md:80-85` states this was **replaced on 2026-07-04**: "the old `recolor_sprites.py` palette-tints read as 'tinted copies' and were replaced" by `--ref` reference generation. `object_pipeline.md` (the "read first" art doc per CLAUDE.md L123) still documents the deprecated recolor path as current. The script file still exists but the workflow it documents is retired. |
| L14 | "`generate_player_sprites.py`, `veg_sprites.py` (both on `tools/player_sprites/pixkit.py`)" | **MINOR.** `pixkit.py` path is correct (`tools/player_sprites/pixkit.py`), but the two scripts themselves live in **`tools/sprites/`**, not `tools/player_sprites/`. Doc names them without a path, so borderline. |
| L27-121 | `gen_sprites.py`, `pixelclean.py`, `make_scene.py`, `fix_sprite_ppu.py`, flags/outputs | OK — all files exist; flags match (`--source {placeables,occupants,items,terrain}`). |

### `docs/guides/authoring/` (README, ORGANIZATION, caves, ant-colony, CORRECTIONS, camps)
| doc:line | claim | reality |
|---|---|---|
| **README.md:84-89** | species list = 9 (`fly_common … firefly`) | **MINOR DRIFT.** Missing `ant_worker` + `ant_scout` (species.json has 11). More current than author-zone but still lagging. |
| ORGANIZATION.md:25-26 | "`previews/` contains exactly: catalog/ examples/ zones/ player/" | **MINOR.** Also has `title/` + `ui/` (same as CLAUDE/author-zone). |
| ant-colony.md:6 | "`ant_worker`, `ant_queen`, `ant_mound` already exist" | **MINOR.** `ant_mound` (occupants.json:1769) and `ant_worker` (species.json) exist; `ant_queen` exists **only as a sprite** (`Resources/Bugs/ant_queen.png`) with **no entity/occupant def** — placing it as an occupant would fail. |
| ant-colony.md:57 | "promote it to `features/ant.py`" | OK — explicitly aspirational ("if it settles"); `features/ant.py` correctly absent. |
| caves.md | `features/cave.py`, `scene_underground_caverns.py`, §4 = ore doctrine | OK — both files exist; §4 "Ore placement" present (matches zone-craft L98 + CLAUDE L75 "Rule 4"). |
| camps.md | `scene_mine_entrance.py`, `make_scene.py` Y-flip | OK — file exists. |
| CORRECTIONS.md | taste ledger; cites `water.md:16` / `house.md:194` as inline-style examples | OK — no stale code/command/entity references (88-line taste index; not a code pointer doc). |

### `.claude/skills/{zone-craft, frontier-sync, run-backend}/SKILL.md` — no drift found
- **zone-craft**: `footprints.py`, `CORRECTIONS.md`, `gallery.md`, `caves.md §4`, `.claude/lenses.md`, all four `research_*.md` packs — **all verified OK**.
- **frontier-sync**: `messages.go` (`OpCodeInfluenceBroadcast=71`, `BUG_REMOVED`/`ITEM_ROTTED`/`FOOD_CONSUMED`), `state.go` (`AddInfluenceEvent:678`, `NextSeq++`, `PendingInfluence`), `broadcastWorldUpdate` (`handlers_world.go:651`), client `BugMessages.cs` + `InfluenceManager.cs` (`ProcessInfluenceEvent`, `ExportFood`, `HydrateFood`, `HydrateFoodExact`), `SwarmManager.ProcessEventsForTick`, `architecture_swarm_sync.md` §0/§12.3/§14 — **all verified OK** (the food-registry funcs are client-side C#, exactly where the skill implies).
- **run-backend**: container names (`bugfarmer-{postgres,builder,nakama}`), ports 7349/7350/7351, "Bug Farmer module loaded successfully", `NetworkManager.cs:61 new Client("http","127.0.0.1",7350,"defaultkey")`, restart logic — **all verified OK**.

### `docs/product/architecture/architecture_swarm_sync.md` §0 — OK
§0 exists (`## §0. As-built quick reference`), and its cross-refs (§12.3 Phase-1b collision, §14 predation strike, `OCCUPANT_BLOCKS_BUGS`, `OpCodeZoneCollisionMap`) are all present. Accurately referenced by frontier-sync and test-changes.

---

### Highest-priority rewrites (what a coder would actually trip on)
1. **`economy/SKILL.md:14`** — wrong function name (`LoadEntities`→`LoadAllEntities`) + wrong line (`~288-305`→`327`). The one the owner flagged; confirmed.
2. **`object_pipeline.md:147-162`** — documents the retired `recolor_sprites.py` tier workflow as current; `add-object` says it was replaced 2026-07-04. Two "read-first" art docs now contradict.
3. **Species roster is stale in 3 places** — `author-zone:152` (4 species), `authoring/README.md:84` (9), `ecology-tuning` "6-species" framing — vs **11** actual. author-zone is the worst (misses 7).
4. **`CLAUDE.md:34`** — `make_test_zone.py` path moved to `tools/world/`.
5. **`ecology-tuning/SKILL.md:100-106`** — `max_litter`/`spawn_satiation`/`nest_*` dials cited as living in `ecology_tuning.json` but aren't there.
6. **`test-changes/SKILL.md`** — §1 suite list missing 13 test files; §2.5 promotes the `bug_lab` rig that `ecology-tuning` says is archived, and contains a 48×-vs-6× internal contradiction.

Minor/self-correcting: the "exactly four preview folders" invariant (now also `title/`+`ui/`) in CLAUDE.md, author-zone, and ORGANIZATION.md; `ant_queen` sprite-without-entity in ant-colony.md.

Note: I did not modify anything — this is evidence only.