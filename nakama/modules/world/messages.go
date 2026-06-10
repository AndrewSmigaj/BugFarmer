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
	OpCodeStationDeposit int64 = 85 // C→S: Deposit an inventory item into a station
	OpCodeStationUpdate  int64 = 86 // S→C: Station fill changed (UI meter; display-only)

	// Dev tuning (debug builds): live-override ecology parameters on the server
	OpCodeEcologyTuning int64 = 87 // C→S: apply EcologyTuningMessage to a species

	// Combat (melee weapons: sword/spear). One message per SWING — a swing may hit
	// multiple swarms, carried as entries of one payload (NOT one message per swarm,
	// which would trip the per-player rate limit like the old catch burst did).
	OpCodeMeleeAttack int64 = 88 // C→S: swing with client-detected (swarm, bug-id) hits
	OpCodeMeleeResult int64 = 89 // S→C: validated damage/kills — the SOLE HP display
	// channel + all combat cosmetics. Kills ALSO flow as BUG_REMOVED ledger events
	// (sim-state); damaged HP deliberately does NOT (display-only, never in the ledger).
)

// TreeWaterUpdateMessage (OpCode 51): a fruit tree's water charges changed. Display-only —
// clients show a droplet indicator over dry trees (charges == 0); bug AI doesn't read this.
type TreeWaterUpdateMessage struct {
	GridX        int `json:"grid_x"`
	GridY        int `json:"grid_y"`
	WaterCharges int `json:"water_charges"`
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
	BugSlots  []InventorySlot `json:"bug_slots"`  // All 20 bug slots
	ItemSlots []InventorySlot `json:"item_slots"` // All 10 item slots (= hotbar)
	Coins     int64           `json:"coins"`
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
	SwarmID string          `json:"swarm_id"`
	Bugs    []BugSampleData `json:"bugs"` // All bugs in swarm
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

	// SWARM_SET_TARGET leg fields (fixed-point ×1000). Self-describes one movement
	// leg so clients re-anchor center to Origin and walk toward Target at Speed/tick.
	OriginX int `json:"origin_x,omitempty"`
	OriginY int `json:"origin_y,omitempty"`
	TargetX int `json:"target_x,omitempty"`
	TargetY int `json:"target_y,omitempty"`
	Speed   int `json:"speed,omitempty"` // World units per tick (×1000)

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
}
