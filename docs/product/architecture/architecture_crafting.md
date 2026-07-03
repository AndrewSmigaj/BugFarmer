# Architecture — crafting & containers

How the crafting system and item containers work in code. The *content* (which recipes, which
stations) lives in [`crafting_design.md`](../design/crafting_design.md); this doc is the **system**.

The one rule that shapes everything: **crafting and container state are non-deterministic
display/inventory state and NEVER enter the bug-sim state hash.** Only an insect food/breeding
source registers on the deterministic food ledger — and that stays on the *compost* `StationState`
path, which crafting does not touch.

## The three pieces of data

1. **Recipes — data** (`nakama/data/entities/recipes.json`, published to the client by
   `publish_entities.py`'s glob). Keyed by recipe id; each has `station` (the placeable entity id
   whose panel offers it), `inputs[]`, `output`, `process_ticks` (the ONLY speed knob), optional
   `catalyst`, and an `unlock` seam (unused by the gate today). Loaded once at `MatchInit` by
   `LoadRecipes` (mirrors `LoadCropDefs`) into `WorldState.Recipes` + `RecipesByStation`. The client
   mirror is `Data/RecipeDatabase.cs`.

2. **Item tags** (`EntityDef.Tags []string`) — `clothing`/`food`/`material`/`metal`/`tool`/`seed`/
   `consumable`. A container's filter is a tag; tags also seed future inventory filtering. Pure data.

3. **`world.container {slots, filter}`** on storage placeables (`interaction_type:"storage"`) — marks
   a chest/dresser/rack and how many slots + an optional tag filter.

## Runtime state (server, in the match — never hashed; persisted per-chunk since zone-persist)

- **`ContainerState`** (`handlers_containers.go`) — a chest's `[]InventorySlot` + filter, keyed
  `container_<gx>_<gy>`.
- **`CraftStationState`** (`craft_stations.go`) — the SHARED output grid (`[]InventorySlot`) +
  **`Procs []CraftProcessor`**: N parallel recipe lanes, each `{Recipe, Queue, Progress}`. Lane
  count = the station def's **`world.craft_slots`** (default 1; the six slow processors — furnace,
  forge, sawmill, ore_sluice, dye_vat, bug_extractor — ship at 2), seeded/topped-up by `ensureProcs`
  at resolve AND restore. Keyed `craft_<gx>_<gy>`. **Legacy saves** (flat `Recipe/Queue/Progress`)
  migrate via `CraftStationState.UnmarshalJSON` → `Procs[0]` — whole structs JSON-round-trip inside
  `ChunkSave`, so both shapes must load forever.

Both are **lazily created on first open** (from the occupant def at the anchor cell) — so pre-placed
(zone-file) *and* runtime-placed stations work with no placement hook, and a station can't process
before it's opened anyway. This deliberately differs from compost, which eager-inits per chunk-load.

## The wire (one action opcode, one echo)

- **`OpCodeContainer` (98, C→S)** — `ContainerActionMessage{gx,gy, op, …}`. `op` switches:
  - `open` — request current contents
  - `quick {zone, slot}` — move a WHOLE stack to the opposite side (double-/shift-click)
  - `move {zone, slot, to_zone, to_slot, count}` — precise drag-drop (server-supported; client drag
    deferred — see backlog)
  - `set_recipe {recipe, proc}` — craft station: select a LANE's active recipe (the client doesn't
    send this on mere browsing; `craft` carries the id)
  - `craft {recipe, qty, proc}` — pull inputs from the player's bag up-front (Terraria-style), queue
    qty batches on lane `proc` (0 default — legacy messages keep working; a lane running a DIFFERENT
    recipe refuses "That processor is busy")
  - `collect {slot}` — take ONE output cell's stack (the grid is station-level; no proc index)
  - `get_all` — sweep the whole output grid (overflow stays)
- **`OpCodeContainerUpdate` (99, S→C)** — `ContainerUpdateMessage{gx,gy, slots[], filter, is_craft,
  procs[]}` where each `CraftProcInfo` is `{recipe, progress, total, queue}` — one per lane;
  broadcast to the cell's chunk so concurrent viewers stay in sync. After an action that changed the
  actor's bag, the server also re-sends that player a full inventory sync (OpCode 38).

`handleContainerAction` (handlers_containers.go) routes craft stations to
`handleCraftStationAction` (craft_stations.go); everything else is a storage container. Range-checked
(3.0) like deposit/pickup. Server is authoritative for every transfer.

## Processing (the tick)

`processCraftStations` runs each tick beside `processStations`: for every station, EVERY lane with a
queue advances `Progress`; at `process_ticks`, if the shared output grid has room (`outputHasRoom` is
per-item-type), produce one batch's output and decrement that lane's `Queue`. Inputs were consumed at
queue time, so a full output grid just **stalls that lane** (holds at full progress) until the player
collects — the OTHER lanes keep producing, and nothing is ever lost. One echo per station covers all
lanes; the client interpolates each row's bar between echoes.

## Client UI

`UI/CraftingPanel.cs` — ONE singleton panel for both craft stations and chests (built by
`UIBootstrap`, opened from `PlayerInputRouter.RouteRightClick` via `CraftingPanel.Instance
.TryHandleRightClick`, which reads `world.interaction_type` `"craft"`/`"storage"`). It renders from the
server echo + `RecipeDatabase`; content rebuilds per-open. Craft: recipe grid → selected inputs as
have/need (red when short) + qty + Craft → **one processor ROW per lane** (icon of what the lane is
making + interpolated bar + "Ns ×Q" queue label) → output grid + Get-all/double-click. `DoCraft`
targets a lane already running the selected recipe, else the first idle one; the Craft button
disables (+ "(all lanes busy)") when no lane can take it. Lane count from published `craft_slots`,
with a server-echo override rebuild if they disagree. Storage: the container grid + your item grid,
double-/shift-click to quick-move.

## What is NOT touched

The compost bin (`entities/station.go` `StationState`, `processStations`) and the deterministic food
ledger (`AddFoodEvent`/`InfluenceFoodConsumed`) are untouched. A future station whose OUTPUT is an
insect food/breeding source registers on that path — not on the container path here.

## AS-BUILT content — the mining refine chain + ladders (2026-06-28)

The recipe/station system is generic (a placeable + a recipe naming it via `station` + `interaction_type:
"craft"` = a working station, zero code). On top of it, the crafting **content** built for Village + Mining
Camp (scope per DECISIONS D17):

- **Mining metal chain** (per-mineral, 6 metals copper/iron/tin/silver/gold/platinum) — replaced the wrong
  one-step smelt with the agreed gather→process→refine loop:
  `raw {m}_ore → [rock_crusher] → {m}_paydirt → [ore_sluice] → refined_{m}_ore → [furnace/forge +coal] → {m}_bar`.
  `rock_crusher` is a NEW craft station; `ore_sluice` was wired (`interaction_type:craft` added). `charcoal`
  (`wood`→furnace) is a coal substitute. Tin has no bar — `refined_tin_ore` → bronze at the forge.
- **Tool + weapon ladders** — metal tiers copper→platinum for pickaxe/axe/hoe/scythe/shovel (`2 {bar}+2 wood`
  @ anvil ≤iron / forge ≥steel) and sword/spear (`2 {bar}+1 wood`, each with a scaled primary swing move) +
  the D12 specials `saw` and `harvest_sickle`. All auto-unlock (`unlock:"default"`). Tool-tier icons are free
  palette recolors (`tools/sprites/recolor_sprites.py`).
- **Gems** (Minecraft/Terraria) — mine a gem block (`ore_{gem}_block`) for the raw gem → cut at the NEW
  `gem_cutter` station → `cut_{gem}` (diamond/quartz/ruby/sapphire/emerald). Gems sellable; jeweler/accessory
  consumers are BACKLOGGED.
- **Bug Extractor** — `dead_beetle/centipede/millipede/wasp → chitin`, `dead_fly/butterfly → leather`.
- **OUT (decision-backlogged):** potions/alchemy (D16), cooked food (D19), armor-tier worn art, accessories/
  jeweler recipes, keg artisan goods, electronics.
- **Integrity gate:** `tools/data/recipe_graph.py` — reachability (no dangling/orphan) + completeness
  ("no half-ladder": every metal chain, tool ladder, gem chain must be full). Run it + `catalog_coverage.py`
  after any recipe/item change.

## Files

- Server NEW: `handlers_containers.go`, `craft_stations.go`, `entities/recipe.go`,
  `data/entities/recipes.json`.
- Server EXTENDED: `entities.go` (`LoadRecipes`, `EntityDef.Tags`, `WorldData.Container`/`ContainerData`,
  `HasTag`), `state.go` (`Recipes`/`RecipesByStation`/`Containers`/`CraftStations` maps), `messages.go`
  (opcodes 98/99 + structs, `DebugWorldMessage.GiveItem`), `match.go` (load + dispatch + tick),
  `handlers_env.go` (`debugGiveItem`).
- Data: `items.json` (`tags`), `placeables.json` (`world.container` on storage furniture).
- Client NEW: `Networking/ContainerMessages.cs`, `Data/RecipeDatabase.cs`, `UI/CraftingPanel.cs`.
- Client EXTENDED: `Data/EntityDatabase.cs` (container parse), `UI/UIBootstrap.cs` (panel),
  `Player/PlayerInputRouter.cs` (routing), `UI/WorldMenu.cs` (`crafting_test`),
  `Networking/NetworkMessages.cs` + `Debug/DebugOverlay.cs` (give-item).
- Test zone: `tools/zonegen/scenes/zone_crafting_test.py` → `nakama/data/zones/crafting_test/`.
