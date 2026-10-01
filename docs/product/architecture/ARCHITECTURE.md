# Bug Farmer — architecture

How the game is built, as of 2026-10-01: the stack, who decides what, the server, the client, the world, the data,
saving, tools and tests. Each system has its own `architecture_*.md` document with the detail (the map at the end);
this page is the overview. Where a document and the code disagree, the code is right. The design — what the game
should be — is the design document, [`docs/gdd/`](../../gdd/README.md); the plan is the [ROADMAP](../ROADMAP.md).

The December 2024 plan this file used to hold (8-pixel blocks, 64×64 chunks, a client that only draws, meteors and
infection, hired workers) was replaced on 2026-10-01; it is in git history (commit `1a26468e` and earlier).

## The stack

| Part | What | Version |
|---|---|---|
| Game client | Unity 6, 2D, Universal Render Pipeline, the Input System | 6000.2.9f1 (URP 17.2.0) |
| Network client | Nakama's .NET client, in `BugFarmerClient/Assets/Nakama/` | — |
| Game server | [Nakama](https://heroiclabs.com/nakama/) running a Go plugin (`backend.so`) | Nakama 3.35.0 |
| Database | PostgreSQL | 15 |
| Server language | Go | 1.25 (`nakama/modules/go.mod`) |
| Tools | Python 3, plus a .NET test harness | — |

**The plugin's dependencies are locked.** A Go plugin must be built with exactly the dependency versions the Nakama
binary was built with, or it fails to load ("plugin was built with a different version"): `nakama-common v1.44.0`,
`protobuf v1.36.8`, `gofrs/uuid v4.4.0`. Docker builds it: the `builder` container compiles `backend.so` into a
shared volume and exits; `nakama` loads it (`docker compose build builder && docker compose up -d` after a Go change).

## The big picture

One Nakama server hosts the world, and anyone can run it, as in Terraria. **Each zone is one live Nakama match**
(the authoritative match handler `world`), ticking **10 times a second** (`SimRate`, `match.go`). The tick is the
world clock: one in-game day is 8,400 ticks, 14 minutes. Players enter a zone through the `world_enter` RPC and
then talk to its match over a websocket, in JSON messages with numbered codes (`messages.go`).

**Who decides what**

| Thing | Decided by | How every player learns it |
|---|---|---|
| Every bug's movement, feeding and hunting | **One player's game per zone** (the "authority client") runs the bug simulation; every other player's game replays it exactly | The server relays the authority's tick frontier, an ordered event ledger and snapshots; the games compare a hash of their bug state and resync from a snapshot if one ever drifts ([`architecture_swarm_sync.md`](architecture_swarm_sync.md) §0) |
| Bugs appearing, breeding, merging and being removed | The server (the ecology: populations, nests, breeding, predation) | Events in the same ledger |
| Bug attacks on players | The authority client reports a strike; the server checks it (range, calmed bugs, dodges, sting protection) and applies the damage | A damage message to the player hit |
| Catching, killing, inventory, crafting, trading, digging, building, farming | The server, which validates every request | Messages to the players near the change |
| A player's own movement | That player's game moves at once; the server refuses moves into blocked cells | Position updates |
| Drawing, sound, input, animation, visual effects | Each player's game | — |

**The one rule that keeps every player's game identical:** everything the bug simulation reads must arrive through
the zone-wide event ledger or a snapshot, never through a message that only nearby players receive. Breaking it is the
classic way to make two players see different bugs. New bug mechanics follow the recipe in `architecture_swarm_sync.md`
§0 and the `frontier-sync` skill.

## The server — `nakama/modules/`

- **`main.go`** registers everything: the RPCs `world_enter`, `world_create`, `world_join`, `world_list`,
  `character_list`, `character_create` and `character_delete`; the `world` match handler; a shutdown hook that saves
  every zone before the server stops; and, before anything starts, restoring a backup if one is waiting.
- **`rpc/`** — the RPCs: entering zones (`world.go`) and the per-account character roster (`character.go`).
- **`world/`** — the match itself, about 45 files:
  - `match.go` (the match's life: start, join, leave, the tick loop, stop), `state.go` (the zone's live state),
    `zone.go` (zones and chunks), `messages.go` (every message code and ledger event);
  - one `handlers_*.go` file per area: players, combat, bugs, farming, hives, nurseries, containers, shops, homes,
    the world, the environment;
  - the ecology: `ecology_director.go`, `predation.go`, `nests.go`, `brood.go`, `colony.go`, `condition.go` (calming);
  - saving: `world_save.go`, `save_writer.go`, `save_batch.go`, `zone_lease.go`, `char_registry.go`,
    `character_persist.go`, `backup.go`, `restore.go`, `persist_classes.go`.
- **`entities/`** — the game's data types: species, swarms, crops, fruit trees, stations, recipes, items.
- `nakama/modules/world/CLAUDE.md` lists the determinism rules for anyone changing the `world/` code.

## The client — `BugFarmerClient/`

Scripts live under `Assets/Scripts/`, by area:

| Folder | What it does | Key files |
|---|---|---|
| `Networking/` | Connecting, entering zones, message types | `NetworkManager`, `WorldManager` |
| `Bugs/` | The deterministic bug simulation: fixed-point maths, movement styles, the event ledger | `BugAgent`, `InfluenceManager`, `FixedPoint` |
| `Entities/` | Running or replaying the simulation, snapshots and resync; other players | `SwarmManager`, `EntityManager` |
| `World/` | Ground, placed things and items on the ground; day and night, rain, grass tufts, hit effects | `TilemapManager`, `TileDatabase`, `GroundItemManager` |
| `Player/` | Movement, tools (catching, melee, breaking, placing), walking between zones, the outfit | `PlayerController`, `PlayerInputRouter`, `CrossZoneController`, `CharacterComposer` |
| `UI/` | Inventory, hotbar, crafting, character select, the debug panel | `InventoryManager`, `CraftingPanel`, `CharacterSelectPanel` |
| `Data/` | Loading the published game data | `EntityDatabase`, `RecipeDatabase` |
| `Testing/` | The headless player used by the sync tests | `HeadlessSyncTest` |

The game loads its art only from `Assets/Resources/` (`Objects/`, `Tiles/`, `Items/`, `Bugs/`, `Effects/`,
`Player/`), and its data from `Assets/Resources/Data/entities/`, which is published from the server's data.

## The world

- **The map** is twenty zones on a grid four wide and five deep: three rows of surface, two underground
  ([`docs/gdd/01_world.md`](../../gdd/01_world.md)). Built so far: the village (`village_21_B`), the Bee Meadow
  (`bee_meadow_20`), the Ant Tunnels (`ant_tunnels_30`) and the Mining Camp (`underground_passages_31`), plus test
  zones. High y is north.
- **A zone** is 256×256 cells, in an 8×8 grid of 32×32-cell chunks. A cell is one Unity unit. Players load the chunks
  around them; the server keeps only the chunks someone is subscribed to in memory and reads the rest from disk when
  it needs the whole zone.
- **Walking off a zone's edge** enters the neighbouring zone (`CrossZoneController` on the client, `world_enter` on the
  server). Bugs crossing between zones is designed but not built.
- **Zone data** — the authored ground and objects — is in `nakama/data/zones/<zone>/`, made with the zone builder
  (`tools/zonegen/`). Changes players make are saved separately, as a difference from the authored zone.
- Detail: [`architecture_world.md`](architecture_world.md), [`architecture_shaped_ground.md`](architecture_shaped_ground.md).

## The game's data

- **Items, objects, plants and crops** are defined once, in `nakama/data/entities/` (`items.json`, `occupants.json`,
  `placeables.json`, `crops.json`, `recipes.json`). The server reads them there; `python3 tools/data/publish_entities.py`
  copies them to the client. The client's copy is output: never edit it by hand.
- **Bug species** are in `nakama/data/species.json`; ecology tuning in `nakama/data/ecology_tuning.json`.
- Server settings are in `nakama/data/local.yml`.

## Saving

- Each zone saves as **one document** (storage key `<zone>:world`) holding its whole state, including its clock, so time
  carries on after a restart. Characters are documents owned by their player's account.
- **One ordered save queue** writes each zone together with the characters in it: every minute while players are
  there, when a player leaves, and when the server shuts down. A crash loses at most about a minute and never
  duplicates or deletes items.
- **One live copy per zone**, and **one zone at a time per character**, so two copies can never overwrite each other.
- **Rolling backups** of every zone and character every 30 minutes while something changes, kept 10 recent, 7 daily and
  4 weekly; `tools/saves/restore_backup.py` restores one.
- Detail: [`architecture_persistence.md`](architecture_persistence.md).

## Tools

Python tools under `tools/`: the sprite pipeline, the zone builder (`zonegen/`), the zone viewer, previews, data
publishing, ecology charts, the .NET sync harness (`sync-harness/`) and the determinism check (`sim-determinism/`).
[`tools/README.md`](../../../tools/README.md) maps every script and where its output goes.

## Tests

- **Go unit tests** run in Docker: `bash tools/run_go_tests.sh`.
- **Determinism:** `tools/sim-determinism/` checks two simulations stay hash-identical, and
  `tools/run_sync_latejoin.sh` runs two headless Unity players, one joining late, and checks they see the same bugs.
- **The sync harness** (`tools/sync-harness/`) drives the real server from .NET, without Unity.
- **Client code** is compiled headless with Unity in batch mode.
- How and when to run each: the [`test-changes`](../../../.claude/skills/test-changes/SKILL.md) skill.

## Documentation map

**How the game is built (`docs/product/architecture/`)**
- [architecture_world.md](architecture_world.md) — zones, chunks, ground and object rendering
- [architecture_shaped_ground.md](architecture_shaped_ground.md) — laying and digging shaped ground: composite ground ids, the mask shader, the material loop
- [architecture_bugs.md](architecture_bugs.md) — bug species, behaviour, life cycle
- [architecture_swarm_sync.md](architecture_swarm_sync.md) — how every player's game runs the same bugs (§0 first)
- [architecture_combat.md](architecture_combat.md) — **design** for combat: attack timing, dodging, threat
- [architecture_farming.md](architecture_farming.md) — crops, planting, watering, growth, fruit trees
- [architecture_weather.md](architecture_weather.md) — time of day, day rollover, rain, night
- [architecture_items.md](architecture_items.md) and [architecture_inventory.md](architecture_inventory.md) — items and the inventory; the item lists are the [catalogs](../economy/catalogs/)
- [architecture_input.md](architecture_input.md) — which click does what (catching, combat, tools)
- [architecture_crafting.md](architecture_crafting.md) — recipes as data, stations, containers
- [architecture_beekeeping.md](architecture_beekeeping.md) — the bee loop and the calming system
- [architecture_nursery_stations.md](architecture_nursery_stations.md) — breeding: nurseries as stations
- [architecture_persistence.md](architecture_persistence.md) — saving, backups, restoring
- [architecture_entity_sync.md](architecture_entity_sync.md) — entity replication (its bug half is replaced by swarm sync)
- [architecture_lighting.md](architecture_lighting.md) — **design** for lighting, including the dark underground

**The design and the plan**
- [docs/gdd/](../../gdd/README.md) — the design document · [DECISIONS.md](../economy/DECISIONS.md) — every decision
- [ROADMAP.md](../ROADMAP.md) — the plan · [BACKLOG.md](../BACKLOG.md) — open items · [CHANGELOG.md](../CHANGELOG.md) — finished work
- [zones/](../zones/) — design notes for the zones that exist
- Older: [game_design.md](../design/game_design.md) (January 2026), [requirements.md](../design/requirements.md) (December 2025)

**Art (`docs/guides/art/`)**
- [object_pipeline.md](../../guides/art/object_pipeline.md) — how world art is made; player outfits are the `player-sprites` skill
- [tools/_generated/README.md](../../../tools/_generated/README.md) — where generated art lives on disk
- [MASTER_STYLE_GUIDE.md](../../guides/art/MASTER_STYLE_GUIDE.md), [PERSPECTIVE_GUIDE.md](../../guides/art/PERSPECTIVE_GUIDE.md), [CHARACTER_DESIGN_GUIDE.md](../../guides/art/CHARACTER_DESIGN_GUIDE.md), [BIOME_PALETTES.md](../../guides/art/BIOME_PALETTES.md) — art direction

**Building zones (`docs/guides/authoring/`)**
- [README.md](../../guides/authoring/README.md) — the zone-building system; read first
- feature guides: [house](../../guides/authoring/house.md), [building](../../guides/authoring/building.md), [yard](../../guides/authoring/yard.md), [vegetation](../../guides/authoring/vegetation.md), [caves](../../guides/authoring/caves.md), [blocks](../../guides/authoring/blocks.md), [water](../../guides/authoring/water.md), [forest](../../guides/authoring/forest.md), [biome-feature-map](../../guides/authoring/biome-feature-map.md)
