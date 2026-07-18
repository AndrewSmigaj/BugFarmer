package world

import "encoding/json"

// Client → Server OpCodes
const (
	OpCodeMovement       int64 = 1 // Player position update
	OpCodeAction         int64 = 2 // Generic interaction (talk to NPC, open chest)
	OpCodeChunkSubscribe int64 = 3 // Subscribe to chunk updates
	OpCodeChunkUnsub     int64 = 4 // Unsubscribe from chunk updates
	OpCodeTilePlace      int64 = 5 // Place floor/wall tile
	OpCodeTileBreak      int64 = 6 // Remove floor/wall tile
	OpCodeToolUse        int64 = 7 // Use tool on target (axe, net, spray)
	// 8-9 reserved for future
)

// Server → Client OpCodes
const (
	OpCodeStateUpdate  int64 = 10 // Chunk tile changes
	OpCodeEntityUpdate int64 = 11 // Entity updates (bugs, trees, players - anything with dynamic state)
	OpCodeChat         int64 = 12 // Chat messages
)

// Bug System OpCodes (Server → Client)
const (
	OpCodeSwarmUpdate int64 = 20 // Batched swarm positions
)

// Bug Catching OpCodes (Phase 2a)
const (
	OpCodeCatchBug  int64 = 24 // C→S: Player clicks to catch
	OpCodeBugCaught int64 = 25 // S→C: Broadcast catch event
	OpCodeEquipTool int64 = 27 // C→S: Player equips/unequips a tool
)

// Inventory OpCodes (Phase 3)
const (
	OpCodeBugSlotUpdate     int64 = 26 // S→C: Single bug slot changed
	OpCodeMoveSlot          int64 = 28 // C→S: Move/swap items between slots
	OpCodeReleaseBugs       int64 = 29 // C→S: Release bugs from slot
	OpCodeItemSlotUpdate    int64 = 37 // S→C: Single item slot changed
	OpCodeFullInventorySync int64 = 38 // S→C: Complete inventory on join
	OpCodeErrorMessage      int64 = 40 // S→C: Operation failed
)

// World Building OpCodes (Phase 4) - Server → Client
const (
	OpCodeChunkData     int64 = 44 // S→C: Full chunk data on subscribe
	OpCodeBreakProgress int64 = 45 // S→C: Breaking progress update
	OpCodeWorldUpdate   int64 = 46 // S→C: Single cell changed
)

// Ground Item OpCodes (Phase 5)
const (
	OpCodeGroundItemSpawn  int64 = 47 // S→C: Item dropped on ground
	OpCodeGroundItemRemove int64 = 48 // S→C: Item picked up/despawned
	OpCodePickupItem       int64 = 49 // C→S: Player picks up item
)

// Bug Simulation OpCodes (Phase 6 - Deterministic Per-Bug)
const (
	OpCodeRequestSample       int64 = 61 // S→C: Request positions for specific bug IDs
	OpCodeSampleResponse      int64 = 62 // C→S: Positions for requested bugs
	OpCodeSampleBroadcast     int64 = 63 // S→C: Sample for comparison by all clients
	OpCodeRequestSnapshot     int64 = 66 // C→S: Client requests full snapshot (drift detected)
	OpCodeFullSnapshot        int64 = 67 // S→C: Full bug positions for swarm
	OpCodeWorldInit           int64 = 68 // S→C: WorldSeed on join (sent once)
	OpCodeRequestInteractions int64 = 69 // S→C: Request aggregated interaction counts
	OpCodeInteractionReport   int64 = 70 // C→S: Aggregated interaction counts per swarm
)

// Influence Event OpCodes (Server-Authored Bug Sync)
const (
	OpCodeInfluenceBroadcast int64 = 71 // S→C: Player cell change events (deterministic bug AI)
	OpCodeLateJoinSnapshot   int64 = 72 // S→C: Full state for late joiner (fixed tick range)
	OpCodeZoneHandoff        int64 = 73 // S→C: Handoff watermark after late join (confirms live)
	OpCodeZoneSnapshot       int64 = 75 // C→S: Authority sends periodic snapshot
	OpCodeZoneAuthority      int64 = 76 // S→C: Authority assigned/changed
	OpCodeZoneHash           int64 = 77 // C→S: Client sends state hash for validation
	OpCodeZoneTickBroadcast  int64 = 78 // S→C: Tick frontier update (every tick, 10Hz)
)

// Farming OpCodes
const (
	OpCodeCropUpdate      int64 = 50 // S→C: Crop state changed (water, stage, HP)
	OpCodeTreeWaterUpdate int64 = 51 // S→C: Tree water charges changed (droplet indicator; display-only)
	OpCodePlantInteract   int64 = 55 // C→S: Harvest or destroy plant

	// Stations (player-fillable processors: compost bin etc.)
	OpCodeStationDeposit int64 = 85  // C→S: Deposit an inventory item into a station
	OpCodeStationUpdate  int64 = 86  // S→C: Station fill changed (UI meter; display-only)
	OpCodeCompostHarvest int64 = 115 // C→S {gx,gy}: scoop the finished compost units out of a bin into the bag

	// Dev tuning (debug builds): live-override ecology parameters on the server
	OpCodeEcologyTuning int64 = 87 // C→S: apply EcologyTuningMessage to a species

	// Combat (melee weapons: sword/spear). One message per SWING — a swing may hit
	// multiple swarms, carried as entries of one payload (NOT one message per swarm,
	// which would trip the per-player rate limit like the old catch burst did).
	OpCodeMeleeAttack int64 = 88 // C→S: swing with client-detected (swarm, bug-id) hits
	OpCodeMeleeResult int64 = 89 // S→C: validated damage/kills — the SOLE HP display
	// channel + all combat cosmetics. Kills ALSO flow as BUG_REMOVED ledger events
	// (sim-state); damaged HP deliberately does NOT (display-only, never in the ledger).

	// World environment (dev tool + display; frontier-neutral by construction)
	OpCodeDebugWorld int64 = 90 // C→S: set time / force weather / spawn swarm (dev, like 87)
	OpCodeWorldEnv   int64 = 91 // S→C: day offset + weather — on change AND per-joiner

	// Fruit trees
	OpCodeTreeHarvest     int64 = 92 // C→S: hands-pick one fruit from a tree
	OpCodeTreeFruitUpdate int64 = 93 // S→C: a tree's fruit count changed (display-only;
	// the OpCode-51 droplet pattern: broadcast on change + chunk-subscribe re-send)

	// Predators
	OpCodePlayerDamage int64 = 94 // S→C: a bug hurt a player — PRESENCE-TARGETED to the
	// victim only (HP is private; an unfiltered broadcast would knock back every client)
	OpCodeBugTelegraph int64 = 95 // S→C: display-only attack telegraph (windup/strike) —
	// a late joiner missing one in flight loses nothing

	// ARMOR (cosmetic + synced; defense math is a follow-up)
	OpCodeEquipArmor      int64 = 96 // C->S: {equip_slot, inv_slot} equip/unequip/swap
	OpCodeEquipmentUpdate int64 = 97 // S->C: the player's 7 worn-armor slots (echo on change + join)

	// Containers & crafting (chests/dressers + craft stations). One C->S action opcode (the Op
	// field switches move/quick/get_all/collect/set_recipe/craft) + one S->C state echo.
	// NON-deterministic display/inventory state — never enters the sim hash.
	OpCodeContainer       int64 = 98 // C->S: a container/craft-station action (see ContainerActionMessage.Op)
	OpCodeContainerUpdate int64 = 99 // S->C: a container/craft-station's contents + craft progress

	// Character home (sleep in a bed → set this character's respawn/login anchor). Character state,
	// NOT in the sim hash; persisted with the rest of the save.
	OpCodeSetHome    int64 = 100 // C->S: {gx,gy} — set home to the bed at this cell
	OpCodeSetHomeAck int64 = 101 // S->C: {ok,message,home_x,home_y} — confirmation toast

	// AUTHORITATIVE local-player spawn, sent once per join (fresh OR reconnect). The client snaps
	// its local player here — the only reliable signal (the passive entity-update snap races with
	// client movement and is gated by a one-shot flag that survives a reconnect). Mirrors how the
	// faint/respawn path authoritatively repositions the client.
	OpCodePlayerSpawn int64 = 102 // S->C: {x,y} — place the local player on join

	// Per-player appearance + character name. STATIC for the session, so it's sent once on join
	// (roster → joiner, joiner → everyone) instead of riding the per-tick EntityData. Display state
	// only — never in the sim hash; the tick loop is untouched.
	OpCodePlayerInfo int64 = 103 // S->C: {players:[{user_id,name,char_class,char_hair,char_skin}]}

	OpCodeBroodUpdate    int64 = 104 // S->C: a brood's egg/maggot counts changed (display-only nursery, like StationUpdate)
	OpCodeNurseryTake    int64 = 113 // C->S {gx,gy,stage,count}: take brood units from a nursery station into the bag
	OpCodeNurseryDeposit int64 = 114 // C->S {gx,gy,slot,count}: place brood units from a bag slot INTO a compatible nursery

	OpCodeHiveHarvest    int64 = 107 // C->S {gx,gy}: hand-harvest honeycomb from the hive at this cell
	OpCodeHiveHarvestAck int64 = 108 // S->C {ok,count,message}: harvest result toast (SetHomeAck pattern)

	OpCodeZoneCollisionMap int64 = 106 // S->C (on join + resync): the zone's COMPLETE blocks_bugs cell set, so
	// every client runs per-bug collision zone-wide + identically (decoupled from its camera's chunk view).

	OpCodeZoneRoofMap int64 = 109 // S->C (on join + resync): the zone's COMPLETE authored "roof" cell set
	// (underground / no-sun). COSMETIC — the client darkens roofed cells for the underground lighting; it
	// never enters the sim. Authored zone data (chunk.roof), NOT derived like the collision map.

	OpCodePredationStrike int64 = 105 // C->S (authority only): the authority client picked the individual flies a
	// predator struck (it has per-bug positions; the server does not). Server validates + applies via the
	// existing kill path (killBugsInSwarm → BUG_REMOVED + carrion + satiation). See PredationStrikeMessage.

	OpCodeBugPlayerStrike int64 = 110 // C->S (authority only): the authority picked which INDIVIDUAL bug(s) stung
	// a player (the server holds only swarm centres, so the old center-based checkBugAttacks stung near the
	// CENTROID = the "phantom" hit). Server re-gates + funnels through applyBugAttackToPlayer. See BugPlayerStrikeMessage.
	OpCodePlayerDodge int64 = 111 // C->S: the player dodge-rolled → server grants a brief i-frame window.
	OpCodeCorpseConsume int64 = 112 // C->S (authority only): an individual predator finished eating a corpse → remove it.
)

// CorpseConsumeMessage (OpCode 112, C->S, AUTHORITY ONLY): an individual predator ate a corpse (a dead_<prey>
// ground item) to completion. The authority reports it → the server removes it via consumeFood (FOOD_CONSUMED@0 →
// the corpse vanishes on every client + late-joiner). The eat-vs-leave choice is a deterministic per-bug roll;
// only the authority reports (dedup). A LEFT corpse gets no report and rots away naturally.
type CorpseConsumeMessage struct {
	FoodID string `json:"food_id"`
}

// BroodUpdateMessage (OpCode 104): a visible nursery's eggs/maggots changed (a lay, a maturation, a
// hatch, or removal). Display-only — the actual births ride the deterministic SWARM_REPRODUCED ledger,
// so a dropped/late BroodUpdate only delays the on-screen egg/maggot count, never the bug positions.
type BroodUpdateMessage struct {
	GX        int     `json:"gx"`
	GY        int     `json:"gy"`
	Species   string  `json:"species"`
	Eggs      int     `json:"eggs"`
	Maggots   int     `json:"maggots"`   // LARVA stage
	Pupae     int     `json:"pupae"`     // PUPA stage (any pupating species — fly/butterfly/beetle/wasp; 0 for non-pupating)
	Progress  float32 `json:"progress"`  // current stage's fraction toward the next transition (0..1) — the panel's conversion bar
	Residents int     `json:"residents"` // resident adults living IN the station (nests today; 0 otherwise) — the panel's adult slots
	Kind      string  `json:"kind"`      // "station" | "host_plant" | "ground_pile" | "nest" — drives the client visual
	Removed   bool    `json:"removed"`   // true when the brood/pile is cleared (source gone)
}

// NurseryTakeMessage (OpCode 113, C->S): take brood units OUT of a nursery station into the player's bag —
// a plain station item transfer (like hive-harvest / container-collect), NOT a random draw. Stage: 0=egg,
// 1=larva, 2=pupa. Count<=0 means take all available of that stage; otherwise take min(Count, available).
type NurseryTakeMessage struct {
	GX    int `json:"gx"`
	GY    int `json:"gy"`
	Stage int `json:"stage"`
	Count int `json:"count"`
}

// NurseryDepositMessage (OpCode 114, C->S): place brood units FROM a bag slot INTO a nursery — the reciprocal
// of take (relocate/top-up a brood). Slot = the player inventory slot holding the brood item; Count<=0 = the
// whole slot. The server resolves the item's species+stage (reverse lookup) and only accepts it if the
// species matches the nursery's (a fly larva can't go in a wasp nest); it tops up an existing brood or seeds
// an empty NEST (whose species is known). Capacity-clamped.
type NurseryDepositMessage struct {
	GX    int `json:"gx"`
	GY    int `json:"gy"`
	Slot  int `json:"slot"`
	Count int `json:"count"`
}

// PlayerSpawnMessage (OpCode 102): where the server placed this player on join (the character's
// last-logout position, bed home, or the zone spawn — already decided in MatchJoin).
type PlayerSpawnMessage struct {
	X float32 `json:"x"`
	Y float32 `json:"y"`
}

// PlayerInfoEntry is one player's cosmetic identity for remote clients (drives the paper-doll +
// the nameplate). Empty fields (a no-character / sync-harness join) → the client defaults to merchant.
type PlayerInfoEntry struct {
	UserID    string `json:"user_id"`
	Name      string `json:"name,omitempty"`
	CharClass string `json:"char_class,omitempty"`
	CharHair  string `json:"char_hair,omitempty"`
	CharSkin  string `json:"char_skin,omitempty"`
}

// PlayerInfoMessage (OpCode 103): one or more players' appearance+name (a roster on join, or a
// single newcomer broadcast to everyone).
type PlayerInfoMessage struct {
	Players []PlayerInfoEntry `json:"players"`
}

// SetHomeMessage (OpCode 100): the anchor cell of the bed the player slept in.
type SetHomeMessage struct {
	GX int `json:"gx"`
	GY int `json:"gy"`
}

// SetHomeAckMessage (OpCode 101): result of a set-home; the client shows Message as a toast and,
// on ok, can update any "home here" indicator.
type SetHomeAckMessage struct {
	OK      bool    `json:"ok"`
	Message string  `json:"message"`
	HomeX   float32 `json:"home_x"`
	HomeY   float32 `json:"home_y"`
}

// TreeWaterUpdateMessage (OpCode 51): a fruit tree's water/tank state changed. Display-only.
// The droplet ("waterable now") rule is computed CLIENT-side each frame:
//
//	show iff water_level < 3 && last_water_day != clientCurrentDay
//
// where clientCurrentDay = (SimulationTick + day_offset) / 8400 — so the droplet reappears
// at the day rollover with NO extra message (last_water_day is a day index, not a stale bool).
type TreeWaterUpdateMessage struct {
	GridX         int   `json:"grid_x"`
	GridY         int   `json:"grid_y"`
	WaterLevel    int   `json:"water_level"`    // 0..3 tank
	PendingGrowth int   `json:"pending_growth"` // fruits left to grow in the current batch
	LastWaterDay  int64 `json:"last_water_day"` // day index of the last MANUAL watering (-1 = never)
}

// TreeFruitUpdateMessage (OpCode 93): a tree's fruit count changed (grew, fell, picked,
// knocked). Display-only — drives the canopy fruit overlay; broadcast on change and
// re-sent per chunk-subscribe for trees with fruit.
type TreeFruitUpdateMessage struct {
	GridX      int    `json:"grid_x"`
	GridY      int    `json:"grid_y"`
	FruitCount int    `json:"fruit_count"`
	FruitType  string `json:"fruit_type"` // item id for the overlay sprite ("apple")
}

// TreeHarvestMessage (OpCode 92): hands-pick ONE fruit from the tree at (gx, gy).
type TreeHarvestMessage struct {
	GX int `json:"gx"`
	GY int `json:"gy"`
}

// DebugWorldMessage (OpCode 90, DEV TOOL like EcologyTuning): set the apparent time of
// day, force weather, or spawn a swarm. Ungated by convention (trusted dev environment),
// loudly logged. JsonUtility can't do optionals → sentinels: set_time_ticks -1 = no-op,
// weather "" = no-op, spawn_species "" = no spawn.
type DebugWorldMessage struct {
	SetTimeTicks int     `json:"set_time_ticks"` // -1 or 0..8399 (position within the day)
	Weather      string  `json:"weather"`        // "" | "rain" | "stop"
	SpawnSpecies string  `json:"spawn_species"`  // "" or a species id
	SpawnCount   int     `json:"spawn_count"`
	SpawnX       float32 `json:"spawn_x"`
	SpawnY       float32 `json:"spawn_y"`
	GiveItem     string  `json:"give_item"`  // "" no-op | "kit" (crafting starter bundle) | an item id
	GiveCount    int     `json:"give_count"` // count for a single item id (kit ignores it)
}

// BugTelegraphMessage (OpCode 95): display-only attack telegraphs. kind = "strike"
// (a predator snatch — flash + THWACK at the attacker) or "windup" (the centipede's
// pre-surge rear-up — flash + hiss). Chunk-scoped; pure cosmetics.
type BugTelegraphMessage struct {
	SwarmID string `json:"swarm_id"`
	Kind    string `json:"kind"`
	// Per-victim strike points (Phase 2): world positions where the snatch/THWACK should play, so an
	// individual-fly strike reads on screen (vs the old predator-centre flash). Display-only.
	VictimX []float32 `json:"victim_x,omitempty"`
	VictimY []float32 `json:"victim_y,omitempty"`
	// Consumed-corpse visual (#20, display-only): the dead_<prey> item the client shows at each victim,
	// held then faded over FeedPauseSecs (the predator's feeding dwell). Additive — older clients ignore.
	CarcassItem  string  `json:"carcass_item,omitempty"`
	FeedPauseSecs float32 `json:"feed_pause_secs,omitempty"`
}

// PredationStrikeMessage (OpCode 105, C->S, AUTHORITY ONLY): the authority client ran the strike
// selection on individual bug positions (which the server lacks) and reports the victims. The server
// validates (sender is authority, predator hunting this prey, cooldown elapsed, ids alive) then applies
// the kill via the existing path (killBugsInSwarm → BUG_REMOVED + carrion + satiation + telegraph), so
// followers/late-joiners stay in sync via the relayed BUG_REMOVED. bug_x/bug_y are the victims' positions
// for the display-only per-victim snatch (not used for the kill itself).
type PredationStrikeMessage struct {
	PredatorSwarmID string    `json:"predator_swarm_id"`
	PreySwarmID     string    `json:"prey_swarm_id"`
	BugIDs          []int     `json:"bug_ids"`
	BugX            []float32 `json:"bug_x,omitempty"`
	BugY            []float32 `json:"bug_y,omitempty"`
	Tick            int64     `json:"tick,omitempty"`
}

// BugPlayerStrikeMessage (OpCode 110, C->S, AUTHORITY ONLY): the authority ran the PER-INDIVIDUAL sting
// selection (the server holds only swarm centres) and reports the attacker bug(s) + victim. Fixes the phantom
// sting (old checkBugAttacks stung near the CENTROID). The server re-gates through applyBugAttackToPlayer
// (StingImmune/subdued/cooldown/invuln + StingsOnlyDefending) so damage stays authoritative + fair.
type BugPlayerStrikeMessage struct {
	SwarmID  string `json:"swarm_id"`
	PlayerID string `json:"player_id"`
	BugIDs   []int  `json:"bug_ids"`
	Tick     int64  `json:"tick,omitempty"`
	// Phase drives the authority-owned two-beat: "windup" = just flash the telegraph (no damage); "strike"
	// (or "") = the wind-up elapsed AND a bug is STILL in range → apply the hit now. The authority owns the
	// timing + the precise per-individual range check, so the server never schedules a centre-fire.
	Phase string `json:"phase,omitempty"`
}

// PlayerDodgeMessage (OpCode 111, C->S): the player dodge-rolled; the server grants a brief i-frame window
// (DodgeInvulnUntilTick) the bug-attack funnel respects. Movement itself stays client-predicted + reconciled.
type PlayerDodgeMessage struct {
	Tick int64 `json:"tick,omitempty"`
}

// ZoneCollisionMapMessage (OpCode 106, S->C, on join + resync): the zone's COMPLETE set of cells that
// block bugs (occupants with World.BlocksBugs). Clients run per-bug collision against this zone-wide set
// instead of their view-scoped chunks, so a bug near a fence collides IDENTICALLY on every client
// regardless of camera position. Cx[i],Cy[i] = a blocked world cell. Dynamic changes ride
// OCCUPANT_BLOCKS_BUGS influence events (frontier-gated) after this baseline.
type ZoneCollisionMapMessage struct {
	Cx []int `json:"cx"`
	Cy []int `json:"cy"`
}

// ZoneRoofMapMessage (OpCode 109, S->C, on join + resync): the zone's COMPLETE set of authored "roofed"
// (underground / no-sun) cells. COSMETIC ONLY — the client darkens these for the underground lighting; it
// never enters the sim or ComputeStateHash. Cx[i],Cy[i] = a roofed world cell. Authored zone data
// (chunk.roof from the builder), unlike the DERIVED collision map.
type ZoneRoofMapMessage struct {
	Cx []int `json:"cx"`
	Cy []int `json:"cy"`
}

// PlayerDamageMessage (OpCode 94): a bug attack landed (or a regen/join echo with
// damage 0). Sent ONLY to the victim's presence. Player HP is sim-inert — bug AI reads
// player CELLS, which already ride the ledger (the MeleeResult display precedent).
type PlayerDamageMessage struct {
	HP            int     `json:"hp"`
	MaxHP         int     `json:"max_hp"`
	Damage        int     `json:"damage"`
	SourceSpecies string  `json:"source_species"`
	KnockDX       float32 `json:"knock_dx"` // unit vector away from the attacker
	KnockDY       float32 `json:"knock_dy"`
	Faint         bool    `json:"faint"`     // HP hit 0: client fades + snaps to respawn
	RespawnX      float32 `json:"respawn_x"` // where the client teleports itself on faint
	RespawnY      float32 `json:"respawn_y"` // (the client is movement-authoritative)
}

// WorldEnvMessage (OpCode 91): the world's environment display state — broadcast on any
// change (set-time, rain start/stop) AND sent to each joiner right after WorldInit.
// weather_until_tick is in the SAME tick domain as the frontier (SimulationTick), so a
// client self-terminates rain visuals even if the stop broadcast is missed; clients apply
// the weather field ON RECEIPT ("" = stop immediately) and use until only as the fallback.
type WorldEnvMessage struct {
	DayOffsetTicks   int64  `json:"day_offset_ticks"`
	Weather          string `json:"weather"` // "" or "rain"
	WeatherUntilTick int64  `json:"weather_until_tick"`
}

// EcologyTuningMessage (OpCode 87, DEV TOOL): live-overrides a species' ecology parameters so
// they can be tuned from the Unity debug panel without a rebuild. The server is the sole
// decider for all of these, so live changes are determinism-safe (effects still ride the
// ledger). Values <= 0 leave the field unchanged (except forage_chance, where 0 is valid only
// via the explicit set flag... keep it simple: send the full desired state, all > 0).
type EcologyTuningMessage struct {
	SpeciesID          string  `json:"species_id"`
	ForageChance       float32 `json:"forage_chance"`         // 0..1
	ForageModeMinTicks int     `json:"forage_mode_min_ticks"` // chunk duration range
	ForageModeMaxTicks int     `json:"forage_mode_max_ticks"`
	FeedAmount         float32 `json:"feed_amount"`       // satiation/s at food
	BreedAmount        float32 `json:"breed_amount"`      // breed meter/s at source
	SatiationDecay     float32 `json:"satiation_decay"`   // satiation/s away from food
	ConsumeRate        float32 `json:"consume_rate"`      // food/bug/s
	ReproduceCooldown  float32 `json:"reproduce_cooldown"` // seconds between reproductions
}

// StationDepositMessage (OpCode 85): deposit one unit of item_id into the station at (gx, gy).
type StationDepositMessage struct {
	GX     int    `json:"gx"`
	GY     int    `json:"gy"`
	ItemID string `json:"item_id"`
}

// StationUpdateMessage (OpCode 86): a station's meters changed (deposit, processing tick, or
// consumption). Display-only — bug AI reads the deterministic FOOD_CONSUMED ledger instead.
type StationUpdateMessage struct {
	GX       int `json:"gx"`
	GY       int `json:"gy"`
	Input    int `json:"input"`    // Raw deposits awaiting processing
	Fill     int `json:"fill"`     // Processed output (compost) — the food provider
	Capacity int `json:"capacity"`
}

// CompostHarvestMessage (OpCode 115, C→S): scoop every whole compost unit out of the bin at
// (gx,gy) into the bag. The compost is also the flies' food source, so the server drops the
// deterministic food level to match (the hive-harvest pattern; see handleCompostHarvest).
type CompostHarvestMessage struct {
	GX int `json:"gx"`
	GY int `json:"gy"`
}

// ContainerActionMessage (OpCode 98, C→S): one action on the container/craft-station at (gx,gy).
// Op selects the behavior; only the fields that op needs are read:
//   - "quick"      {zone, slot}                  — move a WHOLE stack to the opposite side
//                                                  (double-/shift-click; chest <-> player)
//   - "move"       {zone, slot, to_zone, to_slot, count} — precise drag-drop placement (-1=all)
//   - "set_recipe" {recipe}                       — craft station: select the active recipe
//   - "craft"      {recipe, qty}                  — craft station: pull inputs, queue qty batches
//   - "collect"    {slot}                         — craft station: take ONE output cell's stack
//   - "get_all"    {}                             — craft station: sweep the whole output grid
//                                                  (overflow stays)
// zone/to_zone are "player" | "container". Server is authoritative for every transfer.
type ContainerActionMessage struct {
	GX     int    `json:"gx"`
	GY     int    `json:"gy"`
	Op     string `json:"op"`
	Zone   string `json:"zone,omitempty"`
	Slot   int    `json:"slot,omitempty"`
	ToZone string `json:"to_zone,omitempty"`
	ToSlot int    `json:"to_slot,omitempty"`
	Count  int    `json:"count,omitempty"`  // -1 = whole stack
	Recipe string `json:"recipe,omitempty"`
	Qty    int    `json:"qty,omitempty"`
	Proc   int    `json:"proc,omitempty"` // craft/set_recipe: which processor lane (NOT Slot — that's collect's output cell)
}

// ShopActionMessage (OpCode 2 / OpCodeAction, C→S): one buy/sell at the NPC vendor occupant at (gx,gy).
//   - "buy"  {id, qty}            — buy `id` from the NPC's sells list (server-priced)
//   - "sell" {id, qty, slot, slot_type} — sell `qty` from your own slot; slot_type "item"|"bug"
//   - "sell_batch" {lines}        — the barter basket: sell every line atomically (validate each,
//                                   pay once); invalid lines are skipped + reported, valid ones sell
// Server is authoritative: price comes from shop/entity data, never the client. The response is the
// existing FullInventorySync echo (coins + item + bug slots) — no shop-specific S→C opcode.
type ShopActionMessage struct {
	GX       int            `json:"gx"`
	GY       int            `json:"gy"`
	Op       string         `json:"op"`              // "buy" | "sell" | "sell_batch"
	ID       string         `json:"id"`              // item or species id
	Qty      int            `json:"qty,omitempty"`   // default 1
	Slot     int            `json:"slot,omitempty"`  // sell: which of the player's slots
	SlotType string         `json:"slot_type,omitempty"` // "item" | "bug" (sell)
	Lines    []ShopSellLine `json:"lines,omitempty"` // sell_batch: the staged basket
}

// HiveHarvestMessage (OpCode 107, C→S): hand-harvest the hive at (gx,gy) — pull every whole
// honeycomb into the bag. Angers the resident colony unless the hive was smoked.
type HiveHarvestMessage struct {
	GX int `json:"gx"`
	GY int `json:"gy"`
}

// HiveHarvestAckMessage (OpCode 108, S→C, presence-targeted): the harvest result toast.
type HiveHarvestAckMessage struct {
	OK      bool   `json:"ok"`
	Count   int    `json:"count,omitempty"`
	Message string `json:"message,omitempty"`
}

// ShopSellLine is one staged basket line of a sell_batch. Each line is validated with the exact
// single-sell rules (the slot must hold `id` with at least `qty`); qty <= 0 is REJECTED per line
// (the shared handler clamp covers only the top-level Qty — a negative line qty would otherwise
// pass RemoveItem's `Count < count` guard and GROW the stack).
type ShopSellLine struct {
	SlotType string `json:"slot_type"` // "item" | "bug"
	Slot     int    `json:"slot"`      // the player's slot index
	ID       string `json:"id"`        // item or species id the slot is expected to hold
	Qty      int    `json:"qty"`       // how many to sell from that slot
}

// ContainerUpdateMessage (OpCode 99, S→C): the full contents of a container/craft-station after
// any change (plus per-processor craft progress when it's a station). Display/inventory state
// only — never in the sim hash. Re-sent on open and on every mutation.
type ContainerUpdateMessage struct {
	GX     int             `json:"gx"`
	GY     int             `json:"gy"`
	Slots  []InventorySlot `json:"slots"`            // chest contents OR the craft station's SHARED output grid
	Filter string          `json:"filter,omitempty"` // tag filter (chests)

	// Craft-station fields (zero/absent for plain chests). One CraftProcInfo per processor
	// lane (world.craft_slots of them).
	IsCraft bool            `json:"is_craft,omitempty"`
	Procs   []CraftProcInfo `json:"procs,omitempty"`
}

// CraftProcInfo is one processor lane's display state inside a ContainerUpdateMessage.
type CraftProcInfo struct {
	Recipe   string `json:"recipe,omitempty"`   // the lane's active recipe id
	Progress int    `json:"progress,omitempty"` // ticks into the current batch
	Total    int    `json:"total,omitempty"`    // process_ticks of the current batch
	Queue    int    `json:"queue,omitempty"`    // batches remaining (incl current)
}

// === Client → Server Messages ===

// MovementMessage is sent by clients (OpCode 1)
type MovementMessage struct {
	X      float32 `json:"x"`      // World X coordinate
	Y      float32 `json:"y"`      // World Y coordinate
	Facing int     `json:"facing"` // Direction enum (0-3)
}

// === Server → Client Messages ===

// EntityData represents a single entity in updates
type EntityData struct {
	ID     string  `json:"id"`     // Entity ID (e.g., "player_abc", "bug_123")
	Type   string  `json:"type"`   // Entity type ("player", "bug")
	X      float32 `json:"x"`      // World X coordinate
	Y      float32 `json:"y"`      // World Y coordinate
	Facing int     `json:"facing"` // Direction enum (0-3)
	// Equipped item id (players): drives the held-at-rest display on remote clients.
	// Riding the per-tick broadcast solves change-sync AND joiner bootstrap in one
	// path (~15 bytes/player/tick; omitted bare-handed). If EntityData ever grows a
	// 3rd rarely-changing field, introduce a player-state snapshot message instead.
	Equipped string `json:"eq,omitempty"`
	Eqa      string `json:"eqa,omitempty"` // worn armor: 7 comma-joined ids (head,body,arms,legs,feet,acc1,acc2)
}

// EntityUpdateMessage is broadcast to clients (OpCode 11)
type EntityUpdateMessage struct {
	Entities []EntityData `json:"entities"`
}

// === Bug System Messages (Server → Client) ===

// SwarmData represents a single swarm in updates (OpCode 20)
type SwarmData struct {
	ID         string  `json:"id"`
	SpeciesID  string  `json:"species_id"`
	SpriteID   string  `json:"sprite_id"`
	X          float32 `json:"x"`
	Y          float32 `json:"y"`
	Radius     float32 `json:"radius"`
	Count      int     `json:"count"`
	Facing     int     `json:"facing"`
	Phase      string  `json:"phase"`                 // "feeding", "reproducing", "idle"
	NextBugID  int     `json:"next_bug_id,omitempty"` // Total bugs ever spawned (for late joiners)
	RemovedIDs []int   `json:"removed_ids,omitempty"` // Bug IDs to skip when spawning (for late joiners)
	BugHP      []BugHPEntry `json:"bug_hp,omitempty"` // Damaged bugs' remaining HP (late-join display seed;
	// populated ONLY by sendLateJoinSnapshot — the regular SwarmUpdate leaves it nil/omitted)
	// NOTE: X,Y is the swarm's CURRENT center, used by a client only as the initial/fallback
	// center until the first SWARM_SET_TARGET leg event arrives. Per-tick motion is NOT here.

	// In-flight movement leg active at the snapshot tick (late-join hydration only).
	// Lets a resyncing/late-joining client re-anchor the swarm center BEFORE replay instead
	// of freezing at X,Y until the next Think. Values are fixed-point (×1000), identical to
	// the originating SWARM_SET_TARGET event so the hydrated leg reproduces the live march
	// bit-for-bit. Legs that begin after the snapshot tick arrive via the replayed influence log.
	HasTarget    bool  `json:"has_target,omitempty"`
	LegOriginX   int   `json:"leg_origin_x,omitempty"`
	LegOriginY   int   `json:"leg_origin_y,omitempty"`
	LegTargetX   int   `json:"leg_target_x,omitempty"`
	LegTargetY   int   `json:"leg_target_y,omitempty"`
	LegSpeed     int   `json:"leg_speed,omitempty"`
	LegStartTick int64 `json:"leg_start_tick,omitempty"`
}

// SwarmUpdateMessage is broadcast to clients (OpCode 20)
type SwarmUpdateMessage struct {
	Tick   int64       `json:"tick"`
	Swarms []SwarmData `json:"swarms"`
}

// === Bug Catching Messages (Phase 2a) ===

// CatchBugMessage is sent by client (OpCode 24)
// Client detects bugs by ID and sends the list to server for validation
type CatchBugMessage struct {
	ClickX  float32 `json:"click_x"`  // World X where player clicked
	ClickY  float32 `json:"click_y"`  // World Y where player clicked
	SwarmID string  `json:"swarm_id"` // Which swarm was caught from
	BugIDs  []int   `json:"bug_ids"`  // IDs of bugs client detected in radius
}

// BugCaughtMessage is broadcast to all clients (OpCode 25)
// All clients use validated bug IDs for deterministic removal
type BugCaughtMessage struct {
	SwarmID   string  `json:"swarm_id"`
	CatcherID string  `json:"catcher_id"`
	BugIDs    []int   `json:"bug_ids"`   // Server-validated bug IDs to remove
	NewTotal  int     `json:"new_total"` // Swarm's new count
	X         float32 `json:"x"`         // Catch position for animation
	Y         float32 `json:"y"`
}

// MeleeAttackMessage is sent by client (OpCode 88): ONE swing. hits lists every swarm
// the swept sector intercepted with the client-detected bug ids (per-bug positions are
// client-deterministic; the server validates alive-ids + player→click reach + caps).
type MeleeAttackMessage struct {
	ClickX float32          `json:"click_x"`
	ClickY float32          `json:"click_y"`
	Move   string           `json:"move,omitempty"` // input slot ("primary"/"secondary"); empty = primary
	Hits   []MeleeSwarmHits `json:"hits"`
}

// MeleeSwarmHits is one swarm's worth of hits inside a single swing.
type MeleeSwarmHits struct {
	SwarmID string `json:"swarm_id"`
	BugIDs  []int  `json:"bug_ids"`
}

// MeleeResultMessage is broadcast to all clients (OpCode 89). It is the SOLE channel for
// per-bug HP display (clients keep a display-only copy; the deterministic ledger never
// carries HP) and for combat cosmetics (hit flash, kill pop, attacker attribution).
// Kills land authoritatively via BUG_REMOVED ledger events in the same network flush.
// NOTE: slices are always initialized server-side — Go marshals nil as JSON null and
// the client's JsonUtility would surface null arrays.
type MeleeResultMessage struct {
	AttackerID string             `json:"attacker_id"`
	ClickX     float32            `json:"click_x"`
	ClickY     float32            `json:"click_y"`
	Weapon     string             `json:"weapon"` // self-describing remote replay: no eq-lookup race
	Move       string             `json:"move"`   // RESOLVED move name ("" normalized to "primary")
	Results    []MeleeSwarmResult `json:"results"`
}

// MeleeSwarmResult is one swarm's validated outcome within a swing.
type MeleeSwarmResult struct {
	SwarmID string       `json:"swarm_id"`
	Damaged []BugHPEntry `json:"damaged"` // survivors: absolute hp_left (last-writer-wins)
	Killed  []int        `json:"killed"`  // removed ids (cosmetic timing; removal = ledger)
}

// BugHPEntry is a (bug id, remaining hp) pair — an ARRAY entry, not a map, because the
// client's JsonUtility cannot deserialize dictionaries (same reason RemovedIDs is []int).
type BugHPEntry struct {
	BugID int `json:"bug_id"`
	HP    int `json:"hp"`
}

// EquipToolMessage is sent by client (OpCode 27)
type EquipToolMessage struct {
	ToolID string `json:"tool_id"` // "" for hand, "small_net" for small net, etc.
}

// EquipArmorMessage (OpCode 96, C->S): equip the armor item in ItemSlots[inv_slot]
// into equipment slot equip_slot (0 head, 1 body, 2 arms, 3 legs, 4 feet,
// 5/6 accessories). inv_slot = -1 unequips equip_slot back to the inventory.
// A swap (slot occupied) puts the old piece INTO inv_slot — never "full".
type EquipArmorMessage struct {
	EquipSlot int `json:"equip_slot"`
	InvSlot   int `json:"inv_slot"`
}

// EquipmentUpdateMessage (OpCode 97, S->C): the authoritative worn-armor state,
// echoed to the owner on every change (and on join via full sync).
type EquipmentUpdateMessage struct {
	Equipment []string `json:"equipment"` // 7 entries
}

// === Inventory Messages (Phase 3) ===

// SlotUpdateMessage is sent when a single slot changes (OpCode 26 for bugs, 37 for items)
type SlotUpdateMessage struct {
	SlotIndex int            `json:"slot_index"`
	ItemID    string         `json:"item_id"` // "" = empty slot
	Count     int            `json:"count"`
	Metadata  map[string]int `json:"metadata,omitempty"` // For tools with state (watering can uses)
}

// FullInventorySyncMessage is sent on player join (OpCode 38)
// Uses InventorySlot from state.go
type FullInventorySyncMessage struct {
	BugSlots          []InventorySlot `json:"bug_slots"`            // All 20 bug slots
	ItemSlots         []InventorySlot `json:"item_slots"`           // All item slots (0-9 hotbar, 10+ panel)
	Coins             int64           `json:"coins"`
	ItemSlotsUnlocked int             `json:"item_slots_unlocked"` // usable item slots (base + backpack)
	Intro             bool            `json:"intro,omitempty"`     // first login of this character → show the intro
	KnownRecipes      []string        `json:"known_recipes,omitempty"` // gated recipe ids the player has learned (for the crafting-panel filter)
}

// MoveSlotMessage is sent by client (OpCode 28)
// Handles drag/drop and stack splitting
type MoveSlotMessage struct {
	SourceType  string `json:"source_type"` // "bug" or "item"
	SourceIndex int    `json:"source_index"`
	DestType    string `json:"dest_type"` // "bug" or "item"
	DestIndex   int    `json:"dest_index"`
	Count       int    `json:"count"` // -1 = all, else specific amount
}

// ReleaseBugsMessage is sent by client (OpCode 29): release n bugs from a bug slot AT a
// world point (the click) — growing a nearby same-species swarm or creating a new one.
type ReleaseBugsMessage struct {
	SlotIndex int     `json:"slot_index"`
	Count     int     `json:"count"` // -1 = all in slot
	X         float32 `json:"x"`     // world release point (the click)
	Y         float32 `json:"y"`
}

// ErrorMessage is sent when an operation fails (OpCode 40)
type ErrorMessage struct {
	Error string `json:"error"`
}

// === World Building Messages (Phase 4) ===

// ChunkSubscribeMessage is sent by client (OpCode 3/4)
type ChunkSubscribeMessage struct {
	ChunkX int `json:"chunk_x"`
	ChunkY int `json:"chunk_y"`
}

// TilePlaceMessage is sent by client (OpCode 5)
type TilePlaceMessage struct {
	GridX      int    `json:"grid_x"`      // Global cell X
	GridY      int    `json:"grid_y"`      // Global cell Y
	OccupantID string `json:"occupant_id"` // What to place
	Direction  int    `json:"direction"`   // 0-3 facing direction
	// Cursor-place: consume from THIS item slot (the drag cursor's source) instead of
	// FindItem's first match. A POINTER deliberately — an absent field decodes to nil,
	// never to the falsy-but-valid slot 0 (an int-with-default design would let any
	// field-omitting sender silently eat hotbar slot 0).
	SourceSlot *int `json:"source_slot,omitempty"`
}

// TileBreakMessage is sent by client (OpCode 6)
type TileBreakMessage struct {
	GridX int `json:"grid_x"` // Global cell X
	GridY int `json:"grid_y"` // Global cell Y
}

// ToolUseMessage is sent by client (OpCode 7)
// Server looks up player.EquippedTool to determine action (hoe, watering can)
type ToolUseMessage struct {
	GridX int `json:"grid_x"` // Target cell X
	GridY int `json:"grid_y"` // Target cell Y
	// GroundID: the player-chosen ground id for the SHOVEL (shaped-ground builder), e.g. "grass~dirt~diagNE".
	// Empty/ignored for every other tool (which compute their result server-side). Validated in handleShovel.
	GroundID string `json:"ground_id,omitempty"`
	// Dig: SHOVEL only — true = DIG (revert the cell to dirt, grant the material block), false = PLACE.
	Dig bool `json:"dig,omitempty"`
}

// PlantInteractMessage is sent by client (OpCode 55)
type PlantInteractMessage struct {
	GridX         int  `json:"grid_x"`
	GridY         int  `json:"grid_y"`
	DestroyIntent bool `json:"destroy_intent"` // true = destroy, false = harvest
}

// CropUpdateMessage is sent to client (OpCode 50)
type CropUpdateMessage struct {
	GridX int `json:"grid_x"`
	GridY int `json:"grid_y"`
	Stage int `json:"stage"`
	HP    int `json:"hp"`
	Water int `json:"water"`
	Flags int `json:"flags"` // fertilized, etc.
}

// ChunkDataMessage is sent to client (OpCode 44)
// Contains full chunk data for client to render
type ChunkDataMessage struct {
	ChunkX    int                 `json:"chunk_x"`
	ChunkY    int                 `json:"chunk_y"`
	Ground    [][]string          `json:"ground"`    // 32x32 tile IDs
	Occupants [][]json.RawMessage `json:"occupants"` // 32x32: null or {id,dir,anchor}
}

// WorldUpdateMessage is sent to client (OpCode 46)
// Single cell change notification
type WorldUpdateMessage struct {
	GridX    int         `json:"grid_x"`
	GridY    int         `json:"grid_y"`
	Ground   string      `json:"ground,omitempty"`   // New ground tile (if changed)
	Occupant interface{} `json:"occupant,omitempty"` // nil clears, *PlacedOccupant sets
}

// BreakProgressMessage is sent to client (OpCode 45)
// Shows breaking progress for client animation
type BreakProgressMessage struct {
	GridX     int    `json:"grid_x"`
	GridY     int    `json:"grid_y"`
	CurrentHP int    `json:"current_hp"`
	MaxHP     int    `json:"max_hp"`
	PlayerID  string `json:"player_id"`
}

// === Ground Item Messages (Phase 5) ===

// GroundItemSpawnMessage is sent to client (OpCode 47)
type GroundItemSpawnMessage struct {
	ID       string  `json:"id"`        // Unique instance ID
	ItemType string  `json:"item_type"` // Type of item (e.g., "rock_small")
	Count    int     `json:"count"`     // Stack count
	X        float32 `json:"x"`         // World X position
	Y        float32 `json:"y"`         // World Y position
}

// GroundItemRemoveMessage is sent to client (OpCode 48)
type GroundItemRemoveMessage struct {
	ID string `json:"id"` // Unique instance ID to remove
}

// PickupItemMessage is sent by client (OpCode 49)
type PickupItemMessage struct {
	ID string `json:"id"` // Unique instance ID to pick up
}

// === Bug Simulation Messages (Phase 6 - Deterministic Per-Bug) ===

// WorldInitMessage sent to client on join (OpCode 68)
type WorldInitMessage struct {
	WorldSeed int64 `json:"world_seed"`
	Tick      int64 `json:"tick"`
	Peaceful  bool  `json:"peaceful,omitempty"` // observation zone: client suppresses the cosmetic attack/flee reaction
}

// BugSampleQuery identifies a single bug for sampling
type BugSampleQuery struct {
	SwarmID string `json:"swarm_id"`
	BugID   int    `json:"bug_id"`
}

// BugSampleData contains full state for a single bug (fixed-point)
// Includes all state needed for deterministic sync
type BugSampleData struct {
	// Core state
	SwarmID  string `json:"swarm_id"`
	BugID    int    `json:"bug_id"`
	X        int    `json:"x"`         // FixedPoint value: actual = X / 1000.0
	Y        int    `json:"y"`         // FixedPoint value: actual = Y / 1000.0
	Vx       int    `json:"vx"`        // Velocity X (fixed-point)
	Vy       int    `json:"vy"`        // Velocity Y (fixed-point)
	RngState uint32 `json:"rng_state"` // RNG state for deterministic sync

	// Behavior state
	Behavior      string `json:"behavior"`  // "wander", "flee", "attack", "curious"
	TargetID      string `json:"target_id"` // Player ID bug is reacting to (empty if none)
	IsAlerted     bool   `json:"is_alerted"`
	AlertCooldown int    `json:"alert_cooldown"`

	// Movement state
	TicksUntilChange int `json:"ticks_until_change"`
	IntentDirX       int `json:"intent_dir_x"` // Brownian: intent direction
	IntentDirY       int `json:"intent_dir_y"`
	IntentTargetX    int `json:"intent_target_x"` // Gliding: intent target
	IntentTargetY    int `json:"intent_target_y"`
	CurrentDirX      int `json:"current_dir_x"` // Gliding: current direction
	CurrentDirY      int `json:"current_dir_y"`
	LandTicks        int `json:"land_ticks,omitempty"` // feed land/hold timer (history-dependent — rides snapshot)
}

// NOTE: BugSampleData above is now UNUSED by the relay — SwarmSnapshotData.Bugs is a verbatim json.RawMessage
// passthrough (see below). The server never reads per-bug fields, so it must NOT re-declare them: a field the
// client sends but the server omits here is silently dropped from the LateJoinSnapshot (that was the late-join
// predation desync — hunt_target/feed_until/feed_corpse_id were missing). Kept only for reference/other decoders.

// FoodSnapshotData is one entry of the deterministic food registry, embedded in the authority's ZoneSnapshot
// and relayed in the late-join package. The registry is event-sourced (ITEM_ROTTED/FOOD_CONSUMED) and pruned,
// so — like swarm legs — the authority's live registry is the reliable late-join source. Coords are raw
// FixedPoint values (×1000) for bit-exact hydration. The server relays these opaquely (never interprets them).
type FoodSnapshotData struct {
	FoodID string `json:"food_id"`
	X      int    `json:"x"`     // FixedPoint value
	Y      int    `json:"y"`     // FixedPoint value
	Level  int    `json:"level"` // remaining food value (>0)
}

// SampleRequestMessage sent to every client in a chunk (OpCode 61).
// Server asks each client for its ComputeStateHash() at the settled tick Tick.
type SampleRequestMessage struct {
	ChunkX int   `json:"chunk_x"`
	ChunkY int   `json:"chunk_y"`
	Tick   int64 `json:"tick"` // Settled tick the client should hash (behind the frontier)
}

// SampleResponseMessage from client (OpCode 62).
// Carries the client's state hash at Tick. HasHash=false means the client no longer has
// that tick buffered (e.g. just resynced) and abstains from the comparison.
type SampleResponseMessage struct {
	ChunkX  int   `json:"chunk_x"`
	ChunkY  int   `json:"chunk_y"`
	Tick    int64 `json:"tick"`     // Tick this hash is from (echoes the request)
	Hash    int64 `json:"hash"`     // ComputeStateHash() at Tick
	HasHash bool  `json:"has_hash"` // False = tick not buffered, abstain
}

// SnapshotRequestMessage from client (OpCode 66)
// Client requests full snapshot when drift detected
type SnapshotRequestMessage struct {
	ChunkX int `json:"chunk_x"`
	ChunkY int `json:"chunk_y"`
}

// SwarmSnapshotData contains all bug positions for a single swarm
type SwarmSnapshotData struct {
	SwarmID string `json:"swarm_id"`
	// Bugs is the authority's per-bug snapshot, relayed VERBATIM (the server never reads it — see BugSampleData
	// note). json.RawMessage means every per-bug field the client sends round-trips untouched, so no field can
	// ever be silently dropped by a stale server struct (the late-join predation desync). Do NOT re-type this.
	Bugs json.RawMessage `json:"bugs"`

	// Current movement leg AT the snapshot tick (authority-embedded). Used for late-join center
	// hydration: the InfluenceLog is pruned each tick, so a slow swarm's last SWARM_SET_TARGET may
	// be gone — the authority's live leg is the reliable source. HasLeg=false ⇒ no leg yet.
	HasLeg      bool  `json:"has_leg,omitempty"`
	LegOriginX  int   `json:"leg_origin_x,omitempty"`
	LegOriginY  int   `json:"leg_origin_y,omitempty"`
	LegTargetX  int   `json:"leg_target_x,omitempty"`
	LegTargetY  int   `json:"leg_target_y,omitempty"`
	LegSpeed    int   `json:"leg_speed,omitempty"`
	LegStartTick int64 `json:"leg_start_tick,omitempty"`
}

// FullSnapshotMessage for late joiners or drift correction (OpCode 67)
type FullSnapshotMessage struct {
	ChunkX int                 `json:"chunk_x"`
	ChunkY int                 `json:"chunk_y"`
	Tick   int64               `json:"tick"` // Tick this snapshot is from
	Swarms []SwarmSnapshotData `json:"swarms"`
}

// === Bug Lifecycle Interaction Messages ===

// SwarmInteractionReport contains aggregated interaction counts for one swarm
type SwarmInteractionReport struct {
	SwarmID    string `json:"swarm_id"`
	FoodCount  int    `json:"food_count"`  // Number of feeding interactions since last report
	BreedCount int    `json:"breed_count"` // Number of breeding interactions since last report
}

// InteractionReportMessage is sent by client (OpCode 70)
// Contains aggregated bug-resource interactions for lifecycle meter updates
type InteractionReportMessage struct {
	Reports []SwarmInteractionReport `json:"reports"`
}

// === Influence Event Messages (Server-Authored Bug Sync) ===

// Influence event types
const (
	InfluencePlayerCellEnter = "PLAYER_CELL_ENTER"
	InfluencePlayerCellLeave = "PLAYER_CELL_LEAVE"
	InfluenceSwarmSetTarget  = "SWARM_SET_TARGET" // Re-anchoring movement leg for a swarm center
	InfluenceBugRemoved      = "BUG_REMOVED"
	InfluenceBugSpawned      = "BUG_SPAWNED"
	InfluenceSwarmSplit      = "SWARM_SPLIT" // Over-size swarm sheds its highest bug-ids into a new swarm
	InfluenceSwarmMerge      = "SWARM_MERGE" // Overlapping swarm absorbed into a survivor
	// Farming/ecology events
	InfluenceTreeFruitGrow = "TREE_FRUIT_GROW"
	InfluenceTreeFruitDrop = "TREE_FRUIT_DROP"
	InfluenceItemRotted    = "ITEM_ROTTED"     // a ground item became bug food (FoodID + world cell + Level=food value)
	InfluenceFoodConsumed  = "FOOD_CONSUMED"   // a food source's level crossed a threshold (Level=remaining; 0 = gone)
	InfluenceSwarmReproduced = "SWARM_REPRODUCED" // sated swarm bred at a food source: SplitCount new bugs at NewBugIDBase
	// A brand-new swarm appears (continuous spawn, initial seed, release-new, nest hatch, director, reproduce-at-cap
	// child). Rides the tick-ordered ledger so EVERY client (live + late-join replay) creates it at the SAME tick
	// with the same seed → bit-identical spawn-seeded wander. SwarmID=new id, SpeciesID, SplitCount=count,
	// CenterX/CenterY=spawn world pos (×1000, == the swarm's first leg origin). NOT used for split (SWARM_SPLIT)
	// or reproduce-into-existing (SWARM_REPRODUCED).
	InfluenceSwarmSpawned = "SWARM_SPAWNED"

	// A blocks_bugs occupant (fence/wall) was placed or removed at a cell — the per-bug COLLISION change,
	// rides the tick-ordered ledger so every client updates its zone-wide collision set at the SAME tick
	// (the chunk-scoped WorldUpdate that renders it can't reach far clients). CellX/CellY = world cell;
	// Level = 1 (now blocks bugs) or 0 (no longer). Phase 1b — see architecture_swarm_sync.md.
	InfluenceOccupantBlocksBugs = "OCCUPANT_BLOCKS_BUGS"
)

// InfluenceEvent represents a discrete, replayable signal for bug AI
// Server-authored, ensures all clients process same ordered event stream
type InfluenceEvent struct {
	Tick     int64  `json:"tick"`                // Simulation tick when event occurs
	Seq      int64  `json:"seq"`                 // Strictly increasing sequence number (zone-local)
	Type     string `json:"type"`                // Event type constant
	ZoneID   string `json:"zone_id,omitempty"`   // Zone this event belongs to
	PlayerID string `json:"player_id,omitempty"` // For PLAYER_CELL_* events
	CellX    int    `json:"cell_x,omitempty"`    // Cell coordinates
	CellY    int    `json:"cell_y,omitempty"`
	SwarmID  string `json:"swarm_id,omitempty"` // For BUG_* and SWARM_* events
	BugID    int    `json:"bug_id,omitempty"`   // For BUG_* events
	SpeciesID string `json:"species_id,omitempty"` // For SWARM_SPAWNED (client derives radius/sprite/wander from species data)

	// SWARM_SET_TARGET leg fields (fixed-point ×1000). Self-describes one movement
	// leg so clients re-anchor center to Origin and walk toward Target at Speed/tick.
	OriginX int `json:"origin_x,omitempty"`
	OriginY int `json:"origin_y,omitempty"`
	TargetX int `json:"target_x,omitempty"`
	TargetY int `json:"target_y,omitempty"`
	Speed   int `json:"speed,omitempty"` // World units per tick (×1000)

	// HUNT-leg fields (Phase 2 individual-fly predation): set ONLY on a predator's hunt leg so the
	// authority client can run the strike selection on individual positions. Empty/0 on every other leg.
	// strike_radius is fixed-point ×1000 (compare via FixedPoint multiply, NOT raw int²).
	TargetPreyID      string `json:"target_prey_id,omitempty"`      // which prey SWARM this predator is hunting
	StrikeRadius      int    `json:"strike_radius,omitempty"`       // ×1000; a predator individual within this of a prey individual strikes
	KillsPerStrike    int    `json:"kills_per_strike,omitempty"`    // victims per strike
	StrikeCooldownTks int    `json:"strike_cooldown_ticks,omitempty"` // client-side re-send throttle (server cooldown is authoritative)

	// SWARM_SPLIT / SWARM_MERGE fields. Flat + count/id-based so clients can apply the
	// change deterministically by MOVING existing bugs (positions preserved, never re-spawned).
	//   SWARM_SPLIT: SwarmID=parent, NewSwarmID=child, SplitCount=bugs moved (parent's highest
	//     alive ids → child ids 0..SplitCount-1), CenterX/Y=child seed center (fixed-point ×1000).
	//   SWARM_MERGE: SwarmID=survivor, NewSwarmID=absorbed, SplitCount=bugs moved,
	//     NewBugIDBase=survivor.NextBugID before the merge (moved bugs become these survivor ids).
	NewSwarmID   string `json:"new_swarm_id,omitempty"`
	SplitCount   int    `json:"split_count,omitempty"`
	CenterX      int    `json:"center_x,omitempty"`
	CenterY      int    `json:"center_y,omitempty"`
	NewBugIDBase int    `json:"new_bug_id_base,omitempty"`
	ParentCount  int    `json:"parent_count,omitempty"` // SWARM_SPLIT: parent's POST-split count — lets clients apply idempotently (move AliveCount−ParentCount bugs; 0 if already applied)

	// FOOD events (ITEM_ROTTED / FOOD_CONSUMED): clients maintain a deterministic food registry
	// from these (positions in cell_x/cell_y = WORLD cells).
	FoodID string `json:"food_id,omitempty"` // Ground-item id, or station cell-key "station_x_y"
	Level  int    `json:"level,omitempty"`   // Remaining food value after the change (0 = depleted/removed)
}

// InfluenceBroadcastMessage sent to all clients (OpCode 71)
type InfluenceBroadcastMessage struct {
	Events []InfluenceEvent `json:"events"`
}

// ZoneAuthorityMessage broadcast when authority assigned/changed (OpCode 76)
// Includes bootstrap tick + watermark for first client (FIX #7)
type ZoneAuthorityMessage struct {
	ZoneID            string `json:"zone_id"`
	AuthorityID       string `json:"authority_id"`
	AuthoritativeTick int64  `json:"authoritative_tick"` // Bootstrap tick for first client
	LastEventSeq      int64  `json:"last_event_seq"`     // FIX #7: Initial watermark
	// Seed-baseline for the FIRST joiner: it has no authority snapshot to adopt, so it CREATES the
	// initial swarms from this metadata and seeds their bugs from (worldSeed, swarmId, bugId) at the
	// swarm centre. SwarmUpdate no longer creates swarms — every swarm is born via this baseline,
	// the late-join snapshot, or a SWARM_SPAWNED event. omitempty: only the first joiner gets it.
	Swarms []SwarmData `json:"swarms,omitempty"`
}

// ZoneTickBroadcastMessage sent EVERY tick (10Hz) by server (OpCode 78)
// CRITICAL: Server must broadcast influence events BEFORE this message each tick
// This ensures clients never simulate without all events for that tick
type ZoneTickBroadcastMessage struct {
	ZoneID            string `json:"zone_id"`
	AuthoritativeTick int64  `json:"authoritative_tick"` // Client may simulate up to (but not beyond) this
	LastEventSeq      int64  `json:"last_event_seq"`     // FIX #7: Watermark - all events with seq <= this are finalized
	AuthorityID       string `json:"authority_id"`       // Current zone authority (for late authority setup)
}

// ZoneHandoffMessage sent after late join snapshot (OpCode 73)
// Confirms "no undisclosed events <= EndTick" so client can go LIVE immediately
type ZoneHandoffMessage struct {
	ZoneID        string `json:"zone_id"`
	LiveStartTick int64  `json:"live_start_tick"` // T_end + 1: first tick client is live
	LastEventSeq  int64  `json:"last_event_seq"`  // Watermark at handoff time
}

// ZoneSnapshotMessage from authority client (OpCode 75)
type ZoneSnapshotMessage struct {
	ZoneID               string              `json:"zone_id"`
	SnapshotTick         int64               `json:"snapshot_tick"`
	SnapshotLastEventSeq int64               `json:"snapshot_last_event_seq"` // Last applied seq included in snapshot state
	Swarms               []SwarmSnapshotData `json:"swarms"`
	Food                 []FoodSnapshotData  `json:"food,omitempty"` // Authoritative food registry @ snapshot
	// Hunts = the authority's per-swarm hunt assignments (_swarmStrikes: predator→prey + strike params), relayed
	// VERBATIM (json.RawMessage) exactly like Bugs. Without it, a late-joiner's predators have no prey list and
	// wander while the authority hunts → divergence. The server never interprets it (mirrors the food registry).
	Hunts                json.RawMessage     `json:"hunts,omitempty"`
	StateHash            string              `json:"state_hash"`
}

// ZoneHashMessage from client for validation (OpCode 77)
type ZoneHashMessage struct {
	ZoneID    string `json:"zone_id"`
	Tick      int64  `json:"tick"`       // Tick this hash was computed at
	StateHash string `json:"state_hash"` // Deterministic hash of bug state
}

// PlayerCellData represents a player's current cell position for late join sync.
// This is snapshot STATE, not an event.
type PlayerCellData struct {
	PlayerID string `json:"player_id"`
	CellX    int    `json:"cell_x"`
	CellY    int    `json:"cell_y"`
}

// LateJoinSnapshot sent to joining player (OpCode 72)
type LateJoinSnapshot struct {
	ZoneID               string              `json:"zone_id"`
	WorldSeed            int64               `json:"world_seed"`
	SnapshotTick         int64               `json:"snapshot_tick"`           // T_snapshot (fixed)
	EndTick              int64               `json:"end_tick"`                // T_end (fixed)
	SnapshotLastEventSeq int64               `json:"snapshot_last_event_seq"` // Last seq baked into snapshot state
	EndLastEventSeq      int64               `json:"end_last_event_seq"`      // Current watermark at end_tick
	Swarms               []SwarmSnapshotData `json:"swarms"`                  // Bug state from authority
	SwarmMetadata        []SwarmData         `json:"swarm_metadata"`          // Swarm metadata for creating visuals
	InfluenceLog         []InfluenceEvent    `json:"influence_log"`           // Events in (snapshot_last_seq, end_last_seq]
	AuthorityID          string              `json:"authority_id"`
	PlayerCells          []PlayerCellData    `json:"player_cells"` // Current player positions (state, not events)
	Food                 []FoodSnapshotData  `json:"food,omitempty"` // Authoritative food registry @ snapshot
	Hunts                json.RawMessage     `json:"hunts,omitempty"` // Authoritative hunt assignments @ snapshot (verbatim)
}
