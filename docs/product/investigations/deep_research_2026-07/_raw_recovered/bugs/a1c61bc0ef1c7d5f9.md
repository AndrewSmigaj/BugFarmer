I'll explore the repo systematically. Let me start with the key files in parallel.

---

Now let me read the authoring README, the key builder files, and start searching for backlog/tile evidence in parallel.

---

Now let me read the house builder, village primitive, the village_21_B scene, and its saved zone.json, plus grep for the backlog/DECISIONS notes.

---

Now let me search for the backlog/DECISIONS notes, bridge design, cross-zone requirements, fishing, and the fun-feature inventory in parallel.

---

Let me read the BACKLOG sections for river/bridge, neighbors gap, cross-zone, fishing, and the fun-features (fireflies/frog/dragonfly/lily pads).

---

Now let me check zone registration, the fun-asset entity inventory, a compact zone.json example, and the village zone doc's bridge notes.

---

Let me look at the WorldList RPC, the cross-zone Neighbors config, the fishing entities, and the lakeside/dock scene.

---

Let me check the WorldList RPC body, the bridge_wood tile/walkability switch, and the fishing entity defs.

---

Let me read the walkability tile switch and find how zones get registered into the world storage.

---

Let me read the WorldJoin auto-register logic and how the client WorldMenu lists zones.

---

Let me check the fishing entity defs (mechanic vs decor), the lily_pad/dock/boat defs, and confirm no beach decor exists.

---

Let me check the tile definitions (walkability of bridge_wood/water/sand) and peek at the existing bee farm scene.

---

Let me read the tile walkability defs from the server data and check the world map for the west neighbor + any bee zone doc.

---

The world map confirms a "Bee Meadow" zone directly west of the Village. Let me read that grid section.

---

I have all the evidence needed across the seven deliverables. Here is the grounded report.

---

# Bee-zone authoring: repo grounding (file:line evidence)

The canonical target already exists in the design: **"Bee Meadow (2,0)"** — grid row 2, col 0, directly **WEST** of the Starting Village. `docs/product/architecture/architecture_world.md:26-28` (grid) and `:204-208` ("Bee Meadow (2,0) | Meadow edge | Beekeeper's cottage + hives | Shows bee farming, sells bee supplies"; species: honeybees/mason/leafcutter/sweat bees, `:110-114`). Village_21_B is `row:2, col:1` (`nakama/data/zones/village_21_B/zone.json:4-5`), so the bee zone is the slot immediately west. There is even a **pre-committed preview folder**: `tools/zonegen/scenes/scene_beefarm_woods.py:23` declares `PREVIEW = "zones/bee_meadow/scenes"`, and that scene already builds a fenced apiary + meadow + woods + stream.

## (a) Authoring workflow + primitive list

**Scenes-first-then-compose flow** (`.claude/skills/author-zone/SKILL.md:56-139`, `docs/guides/authoring/README.md:56-75`):
1. Read the zone doc (`docs/product/zones/<zone>.md`) / decide contents; mine `docs/brainstorms/<topic>/`.
2. Author each themed building as a **text grid** (`features/tilemap.stamp`/`dump`) inside a `place_<thing>(b, ox, oy)` fn + thin `build()` wrapper — ONE source of truth per building (SKILL.md:123-127).
3. **Compose-in-place** (preferred for NEW zones, SKILL.md:130-134): lay real `place_*` pieces along organic roads directly in a 256×256 `ZoneBuilder`, in precedence order **water → roads (+`smooth_paths` once, after all roads) → buildings → farms → scatter** (SKILL.md:90-93). `zone_village_21_B.py` is the worked example of this pattern.
4. Verify in TEXT first: `b.lint()` (0 defects) + `features.tilemap.dump`, THEN render a crop and look (`render_builder(b, out, scale, bounds=)`), never call good off a giant PNG (SKILL.md:47-54).
5. `Z.bug_spawning = {...}` then `Z.save()`; view via `python3 tools/world/view_world.py <zone>`.

**ZoneBuilder API** (`tools/zonegen/zonebuilder.py`): grids `ground[]`/`occ{}` + coordination masks `surface[]` (water|path|building|farm|forest|grass) and `reserved[]` (`:52-72`); `place_occupant` refuses overlaps loudly (`:115-149`), `set_ground`/`fill_ground`/`reserve`, `blit(src,ox,oy, transparent=, on_conflict=)` for scene→zone composition (`:152-201`), render-only `place_player`/`place_bug`/`place_decor` (`:204-216`), `missing_art()` (`:219`), `validate()`/`lint()` (`:225-376`), `save()`/`load()` (`:382-436`).

**Feature primitives in `tools/zonegen/features/`:**
- `terrain.py`: `route_road` (A* least-cost, routes around water/reserved, `end=None` = spur to existing network) `:38`; `path` (organic road, wander/fray/taper) `:295`; `hpath`/`vpath` `:281-292`; `smooth_paths` (road-angle bevel pass, run once after all roads) `:220`; `clear_road_margins` `:152`; `noise_field` (fBm) `:177`; `ring_mask` (forest-ring) `:206`; `stream` (meandering water channel) `:358`; `pond` `:387`; `lake` (multi-blob natural lake, returns info for shore_dress) `:449`; `shore_dress` (per-arc banks: sand/mud/reeds/forest/rocks) `:552`; `forest` `:407`; `rock_mass` (SOLID mineable) `:625`; `rock_patch` `:693`.
- `house.py`: `place_house`, `styled_rooms` (basic/fancy collections), `row_house` (3), `t_house` (⊥, 4), `plus_house`, **`l_house` (`:380`), `u_house` (`:391`), `z_house` (`:414`)**, `courtyard_rect` (`:403`), `sculpt_plan` (`:425`), **`porch(b, specs, depth=2)` (`:493`)**, `bbox`.
- `room.py`: `place_room` (building shell) `:11`. `village.py`: `shop_building` `:19`, `plaza` (carries civic props) `:64`, `shop_frontage` `:109`. `garden.py`: `crop_bed`/`flower_patch`/`fruit_around`/`orchard`. `scatter.py`: `scatter` (density/spacing/`clumping`). `yard.py`: `fence_rect`/`yard`/`property_yard`/`styled_yard`. `furniture.py`, `cave.py`.

**Scene cards** live in `tools/zonegen/scenes/` (44 files). Directly reusable for the bee zone: `scene_beefarm_woods.py` (apiary+meadow+woods, already targets `bee_meadow`), `scene_butterfly_meadow.py`, `scene_meadow_forest_edge.py`, `scene_lakeside.py` (`place_boat_store` + dock), `scene_cottage.py`, `player_house.py`, plus the building pieces (`scene_smith/_carpenter/_market/_mayor/_ecologist/_weaver/_stonemason/_modern_wares`). Zone builders: `zone_village_21_B.py`, `zone_village.py`.

**`save()` writes** (`zonebuilder.py:382-406`): `nakama/data/zones/<id>/zone.json` (fields: `zone_id, name, row:0, col:0, width, height, spawn_point, biome_type, seed`, + `bug_spawning` if set) plus `chunk_<cx>_<cy>.json` for each 32×32 chunk (`{chunk_x, chunk_y, ground, occupants}`). Requires W/H multiples of 32.

**KNOWN GAP — save() drops `neighbors`.** `BACKLOG.md:58-61`: *"**Zone-neighbors builder hardening (deferred — the general #3 fix):** `ZoneBuilder.save()` writes no `neighbors`, so every rebuild drops zone links (we patched village_21_B locally in its scene's post-save block). Add a first-class `ZoneBuilder.neighbors` field written by `save()`, retire the underground post-save hack, and audit all built zones for dropped links."* The patch village_21_B uses is in `zone_village_21_B.py:630-636` — after `b.save()` it re-opens `zone.json` and sets `cfg["row"],cfg["col"]=2,1` and `cfg["neighbors"]={"south":"underground_passages_31"}` (comment `:631-633`: *"save() writes row/col 0,0 and no neighbors — patch the world-grid slot (2,1) and restore the zone link... Without this, walking off the south edge black-screens."*). **A new bee zone must do the same post-save patch** to write its `east: village_21_B` link (and the village scene must be re-patched to add `west: <bee_zone>`).

## (b) River/bridge + beach/water tile status

**`terrain.bridge` / a stream-crossing bridge primitive does NOT exist.** `terrain.py` has `stream` (`:358`) but no `bridge`. The only bridge references are design notes: `BACKLOG.md:582-585` (*"**The river-zone slice**: the stream + `terrain.bridge(b, start, end)` (engine-free — walkability is the tile-id switch; bridge tiles replacing water are walkable both sides). Recorded geometry from review: a gx≈40-50 stream needs TWO bridges (≈(44,130) + ≈(47,182)) or it walls off the west third."*) and `docs/product/zones/village_21_B.md:37-44` (same, plus *"`terrain.bridge` is engine-free (walkability is the hardcoded tile-id switch; bridge tiles replacing water are walkable on both sides with zero Go/C# change)"*).

**The bridge design is already PROVEN by the dock code** — `scene_lakeside.py:80-84` (`place_boat_store`): where `surface=="water"`, it does `b.set_ground(x,y,"bridge_wood", surface="path"); b.reserved[y][x]=False` — i.e. swap the water tile for `bridge_wood` and un-reserve → walkable. A `terrain.bridge(b,start,end)` would just generalize that swap across a stream span. So this is a small **to-build** primitive built entirely from existing pieces.

**Tiles that exist** (`nakama/data/tiles.json`, PNGs in `BugFarmerClient/Assets/Resources/Tiles/`):
- `water_deep` → `blocks_players: true` (impassable). `water_shallow` → `movement_mult 0.5`, walkable-but-slow, does NOT block players. `bridge_wood` → `movement_mult 1.0`, **walkable, no blocks_players** (this IS the tile-id walkability switch — `IsWalkable()` = `!BlocksPlayers`, `tiles.go:69-72`). `sand` → `movement_mult 0.8`, walkable, accepts furniture/structure (beaches are walkable ground). `mud` → `0.6`. All have PNGs: `water_deep.png`, `water_shallow.png`, `bridge_wood.png`, `sand.png`, plus `stone_path`, `dirt`, diagonal families `stone_path_d_*`/`dirt_path_d_*`.
- zonegen uses tile ids: `water_deep`, `water_shallow`, `sand`, `mud`, `dirt`, `stone_floor`, `bridge_wood`, `grass` (see `terrain.py` water/lake/shore code). No dedicated "beach"/"cove"/"coast" tile — beaches are just `sand`/`mud` via `lake(shore="sand")` + `shore_dress` arcs. **The natural west boundary (beach + water strip + coves) is buildable today** from `lake`/`stream` + `sand`/`mud` shore + `shore_dress`; no new tiles needed. `water_deep` correctly walls off the water strip; a `bridge_wood` swap (dock pattern) reopens any crossing.

## (c) village_21_B west-edge geometry + neighbors block

From `nakama/data/zones/village_21_B/zone.json` and `zone_village_21_B.py`:
- **`neighbors` today:** `{"south": "underground_passages_31"}` ONLY (`zone.json:507-509`). North/east/**west are NOT wired**. (`row:2, col:1`; `spawn_point:[126,118]`, `zone.json:2-13`.) Cross-zone declares the authored pair village_21_B(south)↔underground_passages_31(north) — `BACKLOG.md:257`.
- **Spawn:** `[126,118]` — set in scene at `b.spawn=[px-1,py-5]` off PLAZA `(127,123)` (`zone_village_21_B.py:44,134-136`).
- **Does the road reach the WEST edge (x=0)?** Partially yes — the **W dirt lane** runs `path((120,127),(60,127))` then `route_road((60,127),(2,124))` — a meandering dirt lane reaching **≈(2,124)** (`:119-120`). The zone doc records this as the west taper-out: *"**W** dirt lane tapers ≈(0,~130) toward Bee Meadow"* (`village_21_B.md:33-34`). So there IS a west road stub around **y≈124-130**, within the edge band — this is where a west↔east crossing must line up.
- **Stream at the west edge:** `stream(b,(0,76),(28,66),width=2,...)` — a 2-wide stream **enters the west edge at y≈76**, flowing in to feed the big SW lake (`:100-102`; comment: *"A stream entering from the WEST edge... it continues into the neighbor zone"*). **This is the stream that must continue INTO the bee zone** — the bee zone's east-edge stream should exit at y≈76 to match.
- **Lake vs west edge:** the big lake is centered `(46,48)` r52 (SW quadrant), so its western lobe runs close to the west edge in the lower-south region (`:86`). NW pond at `(44,214)` r16 (`:87`).
- **What else is at the west edge:** a **noise-mask forest ring** favoring edges is painted last (`:354-379`, `mask = score>1.02`) plus W meadow scatter (`:392-393`). So outside the y≈76 stream and the y≈124 dirt-lane stub, the west edge is forest + meadow. **For a clean crossing the village's west dirt-lane stub (y≈124) is the natural door**; the bee zone must present a matching walkable east-edge apron/road at the same y, and `clear_road_margins`/forest-mask already leave the lane cell walkable.

## (d) Cross-zone crossing requirements

Cross-zone movement is BUILT (`BACKLOG.md:252-270`). A working west↔east crossing needs:
1. **Adjacency as data — a matched pair.** `ZoneConfig.Neighbors {north/south/east/west}` (`nakama/modules/world/zone.go:121`, `Neighbors map[string]string`). Need village_21_B `zone.json` to gain `"west":"<bee_zone>"` AND the bee zone `zone.json` to have `"east":"village_21_B"`. `world_enter` returns the entered zone's neighbors (`rpc/world.go:396-403`).
2. **Matching-edge entry.** Server join metadata `entry_x/entry_y` validated within 4 cells of an edge → places player at the neighbor's matching edge (`BACKLOG.md:258-260`); entry insets off the seam `Lo=4/Hi=251` (`:266`).
3. **A walkable entry apron on the destination edge** — the mine precedent, `BACKLOG.md:267`: *"**Content**: a walkable grass strip across the mine's north edge (entry apron) so a crossing lands on walkable ground, not the rock wall."* So the bee zone's EAST edge (x≈255) and the village's WEST edge (x≈0) must both have a walkable strip (road/grass/beach — NOT `water_deep` or forest-reserved) at the matching y≈124, or the player lands stuck.
4. **Client:** `CrossZoneController` edge-detect + `ScreenFade`; `WorldManager.ResetForZoneSwap` tears down entities/tiles (zones share coords 0..255) (`BACKLOG.md:261-266`). Verified via sync-harness `crosszone` scenario (`:269`).

## (e) Zone registration shape

A new zone becomes joinable via TWO things (there is no auto-scan of the zones dir for the menu):
1. **On disk:** `nakama/data/zones/<id>/zone.json` + `chunk_*.json` (what `save()` writes). `zone.json` fields (compact example, `nakama/data/zones/bug_lab/zone.json:1-24`): `zone_id, name, row, col, width, height, spawn_point:[x,y], biome_type, seed`, optional `bug_spawning`, optional `neighbors`, optional `profile` (bool). **`profile` is NOT a joinability flag** — it only toggles the PERFSTATS cost profiler and is "TEST/TUNING ZONES ONLY" (`world/zone.go:113-116`). `LoadZoneConfig("data/zones/<id>")` reads it (`zone.go:197-198`).
2. **Client menu:** `BugFarmerClient/Assets/Scripts/UI/WorldMenu.cs` has a **hardcoded `Builtins` list** of `WorldChoice{label, zoneId}` (`:43-53`, e.g. `{"Village B","village_21_B"}`); `EnsureWorld` guarantees they're present even if the Inspector value is stale (`:70-102`). **Add a `WorldChoice` here to expose the bee zone in the picker.**
3. **Runtime:** picking a zone → `WorldManager.EnterWorld(zoneId)` → `world_enter` RPC (`rpc/world.go:319-403`) find-or-creates one canonical match per zone (`worldID="default_"+zoneID`, `:329`), defaults to `access_policy:"public"`. The `world_list` RPC (`:175-221`) lists worlds from Nakama storage collection `"worlds"` filtered to public/owner — used for user-created worlds, not the built-in picker.

**village_21_B species block** (`zone.json:14-69`): six `species_caps` — `fly_common` (initial 78, max 200, spawn_interval 2000, max_population 1500, event_low 40/high 400), `butterfly_meadow` (initial 30, event_low 30/high 250), `wasp_common` (initial 0, max_nests 7 — nest-only), `centipede_garden` (initial 16), `millipede` (initial 16, max 250), `beetle_carrion` (initial 12). **Only species defined in `nakama/data/species.json` spawn** — currently `fly_common, butterfly_meadow, wasp_common, centipede_garden, millipede, beetle_carrion` (SKILL.md:148-152, and the file). **The bee-zone "bees" (honeybee/mason/leafcutter) do NOT exist as species** — a bee zone today can only spawn the existing six; live bees need new species data (a `bugs.json` id without a species spec silently fails to spawn, SKILL.md:150).

## (f) Fishing status

**No fishing mechanic exists** — confirmed. `BACKLOG.md:1040-1041` (Later/Backlogged): *"**Fishing** — a fishing mini-game + rod tiers + passive capacity-capped fish traps (no harpoons). Bows + cast/thrown nets + bug-size matching... ride along here."* There is **zero fishing code** in Go (`grep fishing nakama/modules/**/*.go` → nothing; `tool_type` has no "fish" action). What exists is **decor + a shop only**:
- `fishing_pole` is `category:"decoration"` with an axe-breakable drop, no tool behavior (`placeables.json:6007-6031`). `fishing_net`, `fish_crate`, `sign_fish_board` are placeables.
- The `fisherman` NPC "Cael" is an `interaction_type:"shop"` selling `fishing_pole` (40), `fishing_net` (30), `boat` (400) — greeting: *"Poles, a boat, and a reed hat... **Fishing's coming.**"* (`occupants.json:3227-3255`). Already placed in the village at the boat store (`zone_village_21_B.py:222`, comment *"fishing mechanic deferred"*).

**So the bee zone just needs fishable-LOOKING water + docks + boats as decor:** `lake`/`stream` water; the dock walkway = `bridge_wood` tile swap over water (the `place_boat_store` pattern, `scene_lakeside.py:62-90`); `dock_plank` (player-placeable structure, exists), `mooring_post` (exists), `boat` (sold, placeable — used in dock code), `rowboat_beached` (`occupants.json`, a 2×1 story prop). No mechanic to wire.

## (g) Fun-asset inventory — exists vs needs creating

| Asset | Status | Evidence |
|---|---|---|
| **fireflies** (glow-at-night critter) | **NOT built** — backlogged | `BACKLOG.md:22-23` *"Night critters + fireflies... New species data + sprites + a day/night spawn gate."* No `firefly` entity. |
| **frog** (lake ambient critter) | **NOT built** — wish only | `BACKLOG.md:592` *"A frog ambient critter for the lake (intent doc wish)."* No `frog` entity. |
| **dragonfly** | **NOT built** — designed as pure data+sprite | `BACKLOG.md:594-595` *"Dragonfly: prey:[wasp_common] — pure data + sprite (the chassis proof)."* No `dragonfly` entity. |
| **lily pads** | Entity EXISTS but **render-only on water** (can't be SAVED as an occupant) | `lily_pad` in `placeables.json` (`category:"flora"`, footprint 1×1). Placed via `place_decor` (render-only float), `scene_lakeside.py:123-124`. Constraint — `BACKLOG.md:588-589`: *"Occupant-on-water support so lily pads can live in SAVED zones (today decor = render-only; the boat-store furniture un-reserves water as a special case)."* So in a SAVED zone, lily pads are preview-only unless you use the water un-reserve hack. |
| **docks** | EXISTS | `dock_plank` (structure, placeable), `mooring_post` (structure), `bridge_wood` tile (the walkable dock surface). Dock builder = `scene_lakeside.place_boat_store` (`:62-90`). `dock_post` does NOT exist (only `mooring_post`). |
| **boats** | EXISTS | `boat` (placeable, sold by fisherman/placed in dock), `rowboat_beached` (`occupants.json`, 2×1 prop, placed at `zone_village_21_B.py:98`). `boat_fishing` (nets-aboard vessel) is brainstorm-only, NOT built. |
| **beach decor (shells/driftwood/sandcastle)** | **NONE exist — need creating** | `seashell`/`shell`/`driftwood`/`sandcastle` all absent from entities. Only `sand`/`mud` shore tiles + `reeds`/`cattail`/`marsh_plant` (all exist) dress a beach today. |
| **bee-farm assets** | Mostly EXIST | `beehive_basic`, `beehive`, `honey_extractor` in `placeables.json`; fenced apiary builder demoed in `scene_beefarm_woods.py`. Missing: `smoker`/`bee_smoker`, `apiary`, `honeycomb`, `bee_box` (brainstorm-only). |
| **shore/water dressing** | EXISTS | `reeds`, `cattail`, `marsh_plant`, `lily_pad`; `shore_dress` arcs (sand/mud/reeds/forest/rocks). |

**Net for the bee zone:** meadows + forest patches + lakes/stream + docks + boats + beach shore + a beekeeper cottage/apiary are **all buildable today** from existing primitives and entities. New work needed: (1) a `terrain.bridge` helper (trivial — generalize the dock's water→`bridge_wood` swap) for the top/bottom stream crossings at the reviewed geometry; (2) new **beach decor** sprites (shells/driftwood/sandcastle) if desired; (3) new **bee species** + optional **frog/firefly/dragonfly** critters if the zone should have live bees/ambient fauna (all data+sprite, via the `add-object` skill) — otherwise reuse the existing six spawnable species; (4) the **neighbors post-save patch** on both zones (village gets `west`, bee zone gets `east`) plus a **`WorldMenu.cs` `WorldChoice`** entry; (5) optionally the **lily-pads-in-saved-zones** un-reserve hack if lily pads must persist.

One correction to a task assumption: `village_21_B.md` explicitly says **"THE RIVER IS DEFERRED to the neighbor-zone slice"** (`:37`) — i.e. the stream/bridge work is precisely the bee-zone (west neighbor) slice you are now authoring, and the reviewed bridge geometry (two crossings, `terrain.bridge` engine-free) was recorded there for this purpose.