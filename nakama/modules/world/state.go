package world

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
	"time"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// sortedStringKeys returns a map's string keys in sorted order. Iterate THIS instead of ranging a sim map
// directly in any loop that draws from state.Rng, mints entity IDs, or grabs a shared depletable resource
// — Go randomizes map iteration order per run, which would scramble both the rand-draw sequence and the
// resource-grab order and make runs non-reproducible (defeating seeded RNG). Determinism pairs with the
// seeded Rng: same seed + sorted iteration → same run. (Output-only loops — broadcasts, counting — don't
// need it.)
// nextItemID returns a deterministic, unique ground-item id from the per-match counter (NOT wall-clock).
// Deterministic as long as the spawn happens in a deterministic loop order (fruit drops: sorted tree
// loop; carcasses: sorted death/predation loops) — see GroundItemSeq.
func (s *WorldState) nextItemID(prefix string) string {
	s.GroundItemSeq++
	return fmt.Sprintf("%s_%d", prefix, s.GroundItemSeq)
}

// posHash returns a deterministic non-negative pseudo-random int from (seed, gx, gy, salt) — for per-cell
// world init (e.g. a tree's initial FruitCount/DropTimer) that must NOT depend on chunk-LOAD order. Chunks
// load lazily in non-deterministic order, so drawing such init from the shared sequential Rng made it vary
// run to run; keying off position instead makes it reproducible. FNV-1a; `salt` separates distinct draws
// for the same cell. (Mirrors the client's counter-RNG idea.)
func posHash(seed int64, gx, gy, salt int) int {
	h := uint64(14695981039346656037)
	for _, v := range []int64{seed, int64(gx), int64(gy), int64(salt)} {
		h ^= uint64(v)
		h *= 1099511628211
	}
	return int(h & 0x7fffffff)
}

func sortedStringKeys[V any](m map[string]V) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// WorldConfig holds configurable world parameters
type WorldConfig struct {
	ChunkSize   int // Default: 32 (cells per chunk side)
	BlockSize   int // Default: 16 (pixels per cell)
	TickRate    int // Default: 10 (ticks per second)
	MaxPlayers  int // Default: 100
	WorldWidth  int // Default: 16 (chunks per zone)
	WorldHeight int // Default: 16 (chunks per zone)
	SimBatch    int // Sim-ticks advanced per Nakama call (TEST zones only; default 1 = no batching)
}

// WorldState is the match state for a world instance
type WorldState struct {
	Config       WorldConfig
	WorldID      string
	OwnerID      string
	Name         string
	AccessPolicy string // "public" or "private"
	CreatedAt    int64  // Unix timestamp
	TickCount    int64
	WorldSeed    int64  // Global seed for deterministic bug simulation
	// Rng is the per-match seeded RNG for ALL server-side sim randomness (breeding counts, forage rolls,
	// wander angles, spawn positions, predation re-aims, weather rolls). Seeded from WorldSeed at match
	// init so a fixed seed reproduces a run byte-for-byte — the tuning harness pins the seed; production
	// leaves it random. Per-match instance (NOT global math/rand) so concurrent matches don't share a
	// stream. The authoritative swarm legs we broadcast are what clients replay, so changing this stream
	// only changes WHICH legs broadcast (identically to all clients) — it never desyncs the frontier-gated
	// tick. MUST be paired with deterministic iteration order (sorted swarm/nest/brood loops) for true
	// reproducibility — map range order alone would still scramble which swarm draws which value.
	Rng          *rand.Rand
	// GroundItemSeq: per-match monotonic counter for ground-item ids. Item ids used to be
	// fmt.Sprintf("...%d", time.Now().UnixNano()) — WALL-CLOCK, so they varied run to run; since ids are
	// the FindNearbyFood distance-tiebreak key, that made food selection (and the whole sim) irreproducible.
	// A deterministic counter (incremented in the sorted spawn loops) fixes it. Soft state, never hashed.
	GroundItemSeq int64
	ZoneID        string // Which zone was loaded (for logging)
	StaticSim    bool   // Disables split/merge, continuous spawning (set from zone bug_spawning.static)
	Players      map[string]*PlayerState
	Presences    map[string]runtime.Presence

	// Active character per joining user, set in MatchJoinAttempt (from join metadata) and
	// consumed in MatchJoin — Nakama runs both serially on the match goroutine, so this is
	// race-free without a mutex.
	PendingCharacters map[string]string // userID -> charID

	// Cross-zone entry position from join metadata (entry_x/entry_y): when a player walks off a zone
	// edge, they join the neighbor at the matching edge instead of the save's last-pos. Stashed in
	// MatchJoinAttempt, consumed in MatchJoin (top-priority spawn). Same serial-callback safety as above.
	PendingEntryPositions map[string][2]float32 // userID -> (worldX, worldY)

	// Entity maps (Phase 1)
	Swarms      map[string]*entities.SwarmState
	EggClusters map[string]*entities.EggClusterState
	Individuals map[string]*entities.IndividualBugState
	Plants      map[string]*entities.PlantState
	GroundItems map[string]*entities.GroundItem
	// ItemsByChunk is a chunk-bucketed index OVER GroundItems (ChunkKey -> itemID -> item), maintained
	// incrementally via putGroundItem/deleteGroundItem (see item_index.go). Lets FindNearbyFood scan only
	// the chunks near a swarm instead of the whole item map. Pure derived view — never the source of truth.
	ItemsByChunk map[string]map[string]*entities.GroundItem

	// Config
	Species map[string]*entities.BugSpecies // Loaded from config

	// Timing
	LastMergeCheck int64 // Tick of last merge/split check

	// World environment (time-of-day debug offset + weather). NONE of this feeds the
	// deterministic bug sim — time's only server consumer is the day rollover, and rain
	// lands as ordinary server-side watering. Time-of-day = ((TickCount+DayOffsetTicks)
	// % DayLengthTicks) on BOTH sides (clients get the offset via WorldEnv, OpCode 91).
	DayOffsetTicks    int64  // Debug set-time shifts the APPARENT time; the tick never jumps
	LastRolloverDay   int64  // Epoch compare (NOT modulo): a set-time crossing a boundary must not skip/double the daily reset
	WeatherKind       string // "" or "rain" or "drought" (drought = the Director suppressing rain; soft, display-only)
	WeatherUntilTick  int64  // Raw-tick end of the current weather
	ScheduledRainTick int64  // Raw tick the next shower starts (0 = none scheduled)
	DroughtUntilTick  int64  // Raw tick a Director-triggered drought lifts (0 = none); while active, the daily rain roll auto-fails

	// Tuning: the ecology balance dials (data/ecology_tuning.json), loaded at MatchInit. Soft, never hashed.
	// Defaults = the compiled consts (byte-identical baseline); a config sweep overrides them without a rebuild.
	Tuning *Tuning

	// Stats: the interaction log (births-by-source / deaths-by-cause / predation matrix), accumulated per
	// game-day and flushed at the rollover (ecology_stats.go). Soft, never hashed; tuning telemetry only.
	Stats *EcologyStats

	// Perf: the cost profiler (per-species server-CPU by sub-phase + leg counts + global pass timings +
	// broadcast byte totals), flushed per game-day (profiler.go). Soft, never hashed; nil/disabled unless the
	// zone sets `profile` → zero overhead in production. Pure observation, so a profiled run still reproduces.
	Perf *PerfStats

	// SwarmUpdate (OpCode 20) is event-driven, not per-tick: set true whenever the
	// swarm SET or metadata changes (spawn/despawn/merge/split/phase). Bug centers are
	// derived deterministically from SWARM_SET_TARGET events, so positions are NOT
	// broadcast per tick. Cleared after each broadcast.
	SwarmsDirty bool

	// World Building (Phase 4)
	CurrentZone   *ZoneConfig                  // Current zone metadata
	Chunks        map[string]*ChunkData        // "chunkX,chunkY" -> chunk data
	ChunkSubs     map[string]map[string]bool   // "chunkX,chunkY" -> player IDs subscribed
	TileDefs      map[string]*TileDefinition   // Loaded from tiles.json
	Entities      map[string]*EntityDef        // Loaded from entities/*.json (items, occupants, placeables)
	BreakingState map[string]*BreakingProgress // "gx,gy" -> breaking progress

	// Farming (crops)
	CropStates map[string]*entities.CropState // "gx,gy" -> crop state
	CropDefs   map[string]*entities.CropDef   // cropType -> crop definition

	// Fruit trees
	FruitTreeStates map[string]*entities.FruitTreeState  // "gx,gy" -> fruit tree state
	NestStates      map[string]*entities.NestState       // "gx,gy" -> wasp-nest brood state
	HostPlantStates map[string]*entities.HostPlantState  // "gx,gy" -> milkweed host-plant breeding capacity
	BroodStates     map[string]*entities.BroodState      // "gx,gy" -> visible nursery (compost/milkweed/ground pile)
	ForagePools     map[string]*entities.ForagePoolState // "gx,gy" -> flower nectar feeding pool (depletable)

	// Gnaw damage per occupant cell — its OWN pool, NOT BreakingState (whose owner-
	// reset would let a player "repair" a gnawed fence by hitting it, and vice versa).
	// Whichever pool finishes first wins; dueling crack visuals are accepted cosmetics.
	GnawDamage map[string]int // "gx,gy" -> damage dealt by gnawing

	// Stations (player-fillable processors: compost bin etc.)
	Stations map[string]*entities.StationState // StationKey(gx,gy) -> station state

	// Crafting (recipes-as-data; loaded once at MatchInit). Recipe processing and item
	// containers are NON-deterministic display/inventory state and NEVER enter the sim hash
	// (only a station whose output is an insect food/breeding source registers on the food
	// ledger — that path stays on StationState above, not here).
	Recipes          map[string]*entities.RecipeDef   // recipeID -> recipe
	RecipesByStation map[string][]*entities.RecipeDef // station entity id -> its recipes

	// Item containers (chests/dressers/racks) — lazily created on first open from the
	// occupant's world.container block. Display/inventory state, NOT in the sim hash.
	Containers map[string]*ContainerState // ContainerKey(gx,gy) -> container state

	// Craft stations (recipe processors: furnace/anvil/workbench…) — lazily created on first
	// open for any occupant present in RecipesByStation. Output items are display/inventory
	// state, NOT in the sim hash (an insect-food output would register on the food ledger via
	// StationState instead — separate path).
	CraftStations map[string]*CraftStationState // CraftStationKey(gx,gy) -> craft station state

	// Bug spawn tracking (zone-level, per species)
	SwarmsBySpecies   map[string][]string // speciesID → swarmIDs of that species
	SpeciesNextSpawn  map[string]float64  // speciesID → next spawn time (seconds since start)
	SpeciesSpawnCursor map[string]int     // speciesID → round-robin habitat-circle index (continuous immigration spread)

	// Bug sync (drift detection)
	LastSampleTick map[string]int64       // swarmID → last sample tick
	DriftChecks    map[string]*DriftCheck // chunkKey → in-flight settled-tick hash check

	// Influence event system (server-authored bug sync)
	PlayerCells      map[string]*PlayerCellState // playerID → current cell
	ZoneStates       map[string]*ZoneState       // zoneID → zone authority/sync state
	PendingInfluence []InfluenceEvent            // Events to broadcast this tick

	// Zone/farm persistence (see zone_persist.go). ZoneChunkCache is the prefetched per-chunk save
	// records (loaded once at MatchInit), consumed by handleChunkSubscribe (which has no ctx/nk).
	// LastZoneSaveTick gates the periodic autosave. None of this is in the bug-sim hash.
	ZoneChunkCache   map[string]*ChunkSave // ChunkKey -> persisted delta to apply on chunk load
	LastZoneSaveTick int64
}

// DriftCheck accumulates per-client state-hash responses for one settled-tick drift round.
// The server asks every client in a chunk for ComputeStateHash() at the SAME past tick
// (settled behind the frontier so all clients have simulated it). Comparing equal-tick hashes
// is an honest determinism check; clients in the minority get a targeted late-join resync.
type DriftCheck struct {
	SampleTick int64            // The tick all clients hash (TickCount - margin)
	Expected   map[string]bool  // Clients the request was sent to
	Responded  map[string]bool  // Clients that replied (vote OR abstain)
	Votes      map[string]int64 // userID → reported hash (buffered clients only)
}

// BreakingProgress tracks an in-progress tile break
type BreakingProgress struct {
	GridX     int    // Global cell X
	GridY     int    // Global cell Y
	PlayerID  string // Who is breaking
	CurrentHP int    // Remaining HP
	MaxHP     int    // Starting HP
	LastTick  int64  // Tick of last damage (for timeout)
}

// PlayerCellState tracks a player's current cell for influence events
type PlayerCellState struct {
	CellX int
	CellY int
}

// ZoneState tracks authority and sync state for a zone
type ZoneState struct {
	ZoneID string

	// Authority client for this zone (produces snapshots)
	AuthorityUserID string
	Members         map[string]bool // Players currently in this zone

	// Latest snapshot from authority (stored, not inspected)
	LatestSnapshot     *ZoneSnapshot
	LatestSnapshotTick int64
	LatestSnapshotHash string

	// Influence event log (server-owned, authoritative)
	// RULE: Events are zone-scoped, seq is zone-local
	InfluenceLog []InfluenceEvent
	NextSeq      int64 // Zone-local sequence counter (NOT global!)

	// Hash validation
	HashReports map[string]string // player_id -> hash for current validation round
}

// ZoneSnapshot stores bug state from authority client
type ZoneSnapshot struct {
	ZoneID               string
	SnapshotTick         int64
	SnapshotLastEventSeq int64 // Last applied seq included in snapshot state
	Swarms               []SwarmSnapshotData
	Food                 []FoodSnapshotData // Authoritative food registry @ snapshot (late-join hydration)
	StateHash            string
}

// InventorySlot holds one stack of items (bugs or tools)
type InventorySlot struct {
	ItemID   string         `json:"item_id"` // species_id for bugs, item_id for tools, "" = empty
	Count    int            `json:"count"`
	Metadata map[string]int `json:"metadata,omitempty"` // For tools with state (watering can uses)
}

// PlayerState tracks a player within the world
type PlayerState struct {
	UserID   string
	Username string
	Position entities.EntityPosition
	Facing   entities.Direction // For other players to see which way you're facing

	// Inventory (Phase 3)
	Coins     int64             // Currency
	BugSlots  [20]InventorySlot // Bug inventory (20 slots)
	ItemSlots [40]InventorySlot // Tool inventory (first 10 = hotbar; 10..ItemSlotsUnlocked-1 = panel)

	// How many ItemSlots are usable right now: base (baseUnlockedItemSlots) + the equipped
	// backpack's slot_bonus. Items never auto-land in (and can't be dragged to) a locked slot.
	ItemSlotsUnlocked int

	// Bug catching. One swing may hit multiple swarms and arrives as a same-tick BURST of
	// messages (one per swarm) — burst messages share the swing's rate-limit slot.
	LastCatchTick int64  // Tick of the last catch swing
	EquippedTool  string // "" (hand), "small_net", etc.
	// Worn armor by slot: 0 head, 1 body, 2 arms, 3 legs, 4 feet, 5 acc1,
	// 6 acc2, 7 backpack ("" = empty). Cosmetic + synced (EntityData.eqa); items
	// live HERE when worn, not in ItemSlots. The backpack (slot 7) drives capacity.
	Equipment [8]string

	// Tool use
	LastToolTick int64 // Tick of last tool use (cooldown)

	// Health (predators v1). HP is SIM-INERT: bug AI reads player CELLS (already on
	// the ledger); HP travels as the presence-targeted PlayerDamage message (the
	// MeleeResult display class). 1s invuln is server-enforced across ALL attackers.
	HP             int   // current health
	MaxHP          int   // 10 v1
	LastDamageTick int64 // invuln window + regen gating

	// Character identity (Terraria-style). "" = ephemeral default (no-char join, e.g. the
	// sync-harness). Set in MatchJoin from the join metadata; drives save-on-leave. None of
	// these are sim state — they never enter the bug-sim hash.
	CharacterID   string
	CharCreatedAt int64
	IntroSeen     bool
	PendingIntro  bool // transient: first login this session → ride the next FullInventorySync
	Appearance    Appearance
	HomeZone      string // bed-set respawn/login zone ("" = use the zone spawn_point)
	HomeX         float32
	HomeY         float32
}

// WorldX returns the world X coordinate (ChunkX * chunkSize + LocalX)
func (p *PlayerState) WorldX(chunkSize int) float32 {
	return float32(p.Position.ChunkX*chunkSize) + p.Position.LocalX
}

// WorldY returns the world Y coordinate (ChunkY * chunkSize + LocalY)
func (p *PlayerState) WorldY(chunkSize int) float32 {
	return float32(p.Position.ChunkY*chunkSize) + p.Position.LocalY
}

// SetWorldPosition updates position from world coordinates
func (p *PlayerState) SetWorldPosition(x, y float32, chunkSize int) {
	cs := float32(chunkSize)
	p.Position.ChunkX = int(x / cs)
	p.Position.ChunkY = int(y / cs)
	p.Position.LocalX = x - float32(p.Position.ChunkX)*cs
	p.Position.LocalY = y - float32(p.Position.ChunkY)*cs
	// Handle negative coordinates
	if p.Position.LocalX < 0 {
		p.Position.ChunkX--
		p.Position.LocalX += cs
	}
	if p.Position.LocalY < 0 {
		p.Position.ChunkY--
		p.Position.LocalY += cs
	}
}

// DefaultConfig returns sensible defaults from architecture doc
func DefaultConfig() WorldConfig {
	return WorldConfig{
		ChunkSize:   32, // 32x32 cells per chunk (512x512 pixels)
		BlockSize:   16, // 16x16 pixels per cell
		TickRate:    10,
		MaxPlayers:  100,
		WorldWidth:  16, // 16 chunks per zone
		WorldHeight: 16, // 16 chunks per zone
	}
}

// NewWorldState creates an initialized WorldState
func NewWorldState(worldID, ownerID, name, accessPolicy string) *WorldState {
	return &WorldState{
		Config:                DefaultConfig(),
		WorldID:               worldID,
		OwnerID:               ownerID,
		Name:                  name,
		AccessPolicy:          accessPolicy,
		CreatedAt:             time.Now().Unix(),
		TickCount:             0,
		Players:               make(map[string]*PlayerState),
		Presences:             make(map[string]runtime.Presence),
		PendingCharacters:     make(map[string]string),
		PendingEntryPositions: make(map[string][2]float32),
		// Entity maps
		Swarms:      make(map[string]*entities.SwarmState),
		EggClusters: make(map[string]*entities.EggClusterState),
		Individuals: make(map[string]*entities.IndividualBugState),
		Plants:      make(map[string]*entities.PlantState),
		GroundItems:  make(map[string]*entities.GroundItem),
		ItemsByChunk: make(map[string]map[string]*entities.GroundItem),
		Species:      make(map[string]*entities.BugSpecies),
		// World building
		Chunks:        make(map[string]*ChunkData),
		ChunkSubs:     make(map[string]map[string]bool),
		TileDefs:      make(map[string]*TileDefinition),
		Entities:      make(map[string]*EntityDef),
		BreakingState: make(map[string]*BreakingProgress),
		// Farming
		CropStates:      make(map[string]*entities.CropState),
		CropDefs:        make(map[string]*entities.CropDef),
		FruitTreeStates: make(map[string]*entities.FruitTreeState),
		NestStates:      make(map[string]*entities.NestState),
		HostPlantStates: make(map[string]*entities.HostPlantState),
		BroodStates:     make(map[string]*entities.BroodState),
		ForagePools:     make(map[string]*entities.ForagePoolState),
		GnawDamage:      make(map[string]int),
		Stations:        make(map[string]*entities.StationState),
		// Crafting
		Recipes:          make(map[string]*entities.RecipeDef),
		RecipesByStation: make(map[string][]*entities.RecipeDef),
		Containers:       make(map[string]*ContainerState),
		CraftStations:    make(map[string]*CraftStationState),
		// Bug spawn tracking
		SwarmsBySpecies:    make(map[string][]string),
		SpeciesNextSpawn:   make(map[string]float64),
		SpeciesSpawnCursor: make(map[string]int),
		// Bug sync
		LastSampleTick: make(map[string]int64),
		DriftChecks:    make(map[string]*DriftCheck),
		// Influence event system
		PlayerCells:      make(map[string]*PlayerCellState),
		ZoneStates:       make(map[string]*ZoneState),
		PendingInfluence: make([]InfluenceEvent, 0),
	}
}

// Item-slot capacity. The hotbar is slots 0-9; base unlocks slots 10..29 (the panel). A worn
// backpack (Equipment[backpackSlotIndex]) adds its slot_bonus on top, up to len(ItemSlots).
const (
	baseUnlockedItemSlots = 30
	backpackSlotIndex     = 7
)

// recomputeItemCapacity sets player.ItemSlotsUnlocked from the equipped backpack's slot_bonus.
// Returns the new value. (Items already sitting in slots that become locked stay there but are
// hidden client-side until a pack is re-equipped — nothing is lost.)
func (s *WorldState) recomputeItemCapacity(player *PlayerState) int {
	unlocked := baseUnlockedItemSlots
	if bp := player.Equipment[backpackSlotIndex]; bp != "" {
		if def := s.Entities[bp]; def != nil && def.SlotBonus > 0 {
			unlocked += def.SlotBonus
		}
	}
	if unlocked > len(player.ItemSlots) {
		unlocked = len(player.ItemSlots)
	}
	player.ItemSlotsUnlocked = unlocked
	return unlocked
}

// AddPlayer adds a new player to the world
func (s *WorldState) AddPlayer(userID, username string, presence runtime.Presence) {
	// Use zone's spawn point, or default to center if not set
	spawnX := float32(256)
	spawnY := float32(256)
	if s.CurrentZone != nil {
		spawnX = float32(s.CurrentZone.SpawnPoint[0])
		spawnY = float32(s.CurrentZone.SpawnPoint[1])
	}

	player := &PlayerState{
		UserID:   userID,
		Username: username,
		Facing:   entities.DirDown, // Default: facing camera
		// BugSlots are zero-initialized (empty)
		// Coins defaults to 0
	}
	applyStartingKit(player)
	player.SetWorldPosition(spawnX, spawnY, s.Config.ChunkSize)

	s.Players[userID] = player
	s.Presences[userID] = presence
}

// applyStartingKit stamps a fresh PlayerState with the new-player starting inventory/equipment/HP.
// SINGLE source of truth shared by AddPlayer (the no-character fallback) and DefaultCharacterSave (a
// newly-created character). Does NOT set position/facing/identity.
func applyStartingKit(player *PlayerState) {
	player.MaxHP = 10
	player.HP = 10

	// Slot 0 left EMPTY for now — the "hands" grab verb is pulled pending the
	// grabbing/pushing/shoving rework (BACKLOG). Empty slots still behave as a bare-hand
	// grab, so nothing is lost functionally; this just removes the hands icon.
	player.ItemSlots[1] = InventorySlot{ItemID: "small_net", Count: 1}
	player.ItemSlots[2] = InventorySlot{ItemID: "pickaxe_wood", Count: 1}
	player.ItemSlots[3] = InventorySlot{ItemID: "axe_wood", Count: 1}
	player.ItemSlots[4] = InventorySlot{ItemID: "sword_wood", Count: 1}
	// Farming tools and seeds
	player.ItemSlots[5] = InventorySlot{ItemID: "hoe_wood", Count: 1}
	player.ItemSlots[6] = InventorySlot{
		ItemID:   "watering_can_basic",
		Count:    1,
		Metadata: map[string]int{"uses": 40, "capacity": 40},
	}
	player.ItemSlots[7] = InventorySlot{ItemID: "seed_tomato", Count: 10}
	player.ItemSlots[8] = InventorySlot{ItemID: "scythe_wood", Count: 1}
	// Torches: HELD for light at night (select the hotbar slot — the personal night light
	// grows warm and wide), or placed as fixed lamps. Seeds for wheat come from the shop.
	player.ItemSlots[9] = InventorySlot{ItemID: "torch", Count: 3}
	// Panel slots (10-19): blocks live here now — also exercises panel drag + cursor-place
	player.ItemSlots[10] = InventorySlot{ItemID: "dirt_block", Count: 10}
	player.ItemSlots[11] = InventorySlot{ItemID: "spear_wood", Count: 1}
	// Building/decor starter set (placeables to exercise cursor-place + fences/gates).
	player.ItemSlots[12] = InventorySlot{ItemID: "bench", Count: 1}
	player.ItemSlots[13] = InventorySlot{ItemID: "fence_wood", Count: 50}
	player.ItemSlots[14] = InventorySlot{ItemID: "shovel_wood", Count: 1}
	player.ItemSlots[15] = InventorySlot{ItemID: "flashlight", Count: 1}
	// New vegetable seeds (no shop system yet — starting inventory is the
	// seed source; seed_drop_chance keeps them renewable after that)
	player.ItemSlots[16] = InventorySlot{ItemID: "seed_carrot", Count: 6}
	player.ItemSlots[17] = InventorySlot{ItemID: "seed_eggplant", Count: 6}
	player.ItemSlots[18] = InventorySlot{ItemID: "gate_wood", Count: 1}
	// Slots 19-29 stay FREE so pickups + crafting output work at spawn (panel grew to 30).
	player.EquippedTool = "hands"
	// Spawn WEARING the leather set (cosmetic armor v1): visible immediately,
	// zero inventory slots used; unequipping exercises the free slots. Slot 7
	// (backpack) starts empty.
	player.Equipment = [8]string{"leather_cap", "leather_chest", "leather_gloves",
		"leather_pants", "leather_boots", "", "", ""}
	player.ItemSlotsUnlocked = baseUnlockedItemSlots // grows when a backpack is worn
}

// RemovePlayer removes a player from the world
func (s *WorldState) RemovePlayer(userID string) {
	delete(s.Players, userID)
	delete(s.Presences, userID)
}

// floorDiv performs floor division (always rounds toward negative infinity).
// Go's integer division truncates toward zero, which is wrong for negative coords.
func floorDiv(a, b int) int {
	if a >= 0 {
		return a / b
	}
	return (a - b + 1) / b
}

// IsBlocked checks if a world position blocks swarm center movement.
// Returns true if the position has a blocking occupant or impassable ground.
func (w *WorldState) IsBlocked(worldX, worldY float32) bool {
	return w.isBlockedImpl(worldX, worldY, false, false)
}

// IsBlockedForSpawn is the walkability check used when PLACING a swarm. Unlike the per-tick checks, it
// consults the AUTHORED map — loading a not-yet-subscribed chunk transiently from disk (chunkForCollision)
// when it isn't in the lazily-loaded state.Chunks cache. That cache is EMPTY at MatchInit (chunks load per
// subscription), so the per-tick check would call every cell "blocked" and the initial spawn would place
// zero bugs; this one sees the real walls and actually places them. Same authored source the zone collision
// map uses — determinism-safe (read-only, no init, not stored). Only the spawn path pays the disk load.
func (w *WorldState) IsBlockedForSpawn(worldX, worldY float32) bool {
	return w.isBlockedImpl(worldX, worldY, false, true)
}

// IsBlockedForSpecies is the species-aware blocking check: flies_over_fences species
// skip the OCCUPANT branch ONLY (fences, walls, houses — there are no roofs yet).
// The nil-chunk zone edge STILL blocks everyone — never hand movement code a nil
// checker. Ground tiles block bugs only via tiles.json blocks_bugs (currently NONE:
// water stops PEOPLE only — bugs fly over it). The client per-bug collision applies
// the identical rule (architecture_swarm_sync.md §14: BOTH collision sites).
func (w *WorldState) IsBlockedForSpecies(worldX, worldY float32, species *entities.BugSpecies) bool {
	skipOccupants := species != nil && species.FliesOverFences
	return w.isBlockedImpl(worldX, worldY, skipOccupants, false)
}

func (w *WorldState) isBlockedImpl(worldX, worldY float32, skipOccupants, loadAuthored bool) bool {
	cs := w.Config.ChunkSize

	// Convert to integer grid coordinates using floor (consistent for negative coords)
	gx := int(math.Floor(float64(worldX)))
	gy := int(math.Floor(float64(worldY)))

	// Get chunk coordinates using floor division
	cx := floorDiv(gx, cs)
	cy := floorDiv(gy, cs)

	// Get local coordinates (always positive within chunk)
	lx := gx - cx*cs
	ly := gy - cy*cs

	// Get chunk. Spawn-time checks (loadAuthored) fall back to the authored map on disk when the chunk
	// isn't subscribed yet — otherwise an unloaded chunk reads as "blocked" and spawning fails at MatchInit.
	chunk := w.Chunks[ChunkKey(cx, cy)]
	if chunk == nil && loadAuthored && w.CurrentZone != nil {
		chunk = w.chunkForCollision("data/zones/"+w.CurrentZone.ZoneID, cx, cy)
	}
	if chunk == nil {
		return true // Out of bounds / no authored chunk = blocked
	}

	// Check occupant layer (fences, walls, trees) — skipped for flying species
	if !skipOccupants {
		cell, err := chunk.GetOccupantCell(lx, ly)
		if err == nil && cell.Occupant != nil {
			entityDef := w.Entities[cell.Occupant.ID]
			if entityDef != nil && entityDef.World != nil && entityDef.World.BlocksBugs {
				return true
			}
		}
	}

	// Check ground tile (water, lava, etc.)
	tileID := chunk.GetGroundTile(lx, ly)
	if tileID != "" {
		tileDef := w.TileDefs[tileID]
		if tileDef != nil && tileDef.BlocksBugs {
			return true
		}
	}

	return false
}

// IsBlockedForPlayers mirrors IsBlocked but for PLAYER movement (occupant blocks_players, or impassable
// ground). Authoritative collision: the movement handler rejects moves into a blocked cell.
func (w *WorldState) IsBlockedForPlayers(worldX, worldY float32) bool {
	cs := w.Config.ChunkSize
	gx := int(math.Floor(float64(worldX)))
	gy := int(math.Floor(float64(worldY)))
	cx := floorDiv(gx, cs)
	cy := floorDiv(gy, cs)
	lx := gx - cx*cs
	ly := gy - cy*cs

	chunk := w.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return true // out of bounds
	}

	cell, err := chunk.GetOccupantCell(lx, ly)
	if err == nil && cell.Occupant != nil {
		entityDef := w.Entities[cell.Occupant.ID]
		if entityDef != nil && entityDef.World != nil && entityDef.World.BlocksPlayers {
			return true
		}
	}

	switch chunk.GetGroundTile(lx, ly) {
	case "water_shallow", "water_deep", "lava":
		return true
	}
	return false
}

// === Influence Event System ===

// GetOrCreateZone returns existing zone state or creates a new one
func (s *WorldState) GetOrCreateZone(zoneID string) *ZoneState {
	if zone, exists := s.ZoneStates[zoneID]; exists {
		return zone
	}
	zone := &ZoneState{
		ZoneID:       zoneID,
		Members:      make(map[string]bool),
		InfluenceLog: make([]InfluenceEvent, 0),
		HashReports:  make(map[string]string),
	}
	s.ZoneStates[zoneID] = zone
	return zone
}

// GetZone returns zone state if it exists
func (s *WorldState) GetZone(zoneID string) *ZoneState {
	return s.ZoneStates[zoneID]
}

// AddInfluenceEvent adds an event to pending broadcast and zone log
func (s *WorldState) AddInfluenceEvent(zoneID, eventType, playerID string, cellX, cellY int, swarmID string, bugID int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:     s.TickCount,
		Seq:      zone.NextSeq,
		Type:     eventType,
		ZoneID:   zoneID,
		PlayerID: playerID,
		CellX:    cellX,
		CellY:    cellY,
		SwarmID:  swarmID,
		BugID:    bugID,
	}
	zone.NextSeq++

	// Add to zone's historical log (for late joiners)
	zone.InfluenceLog = append(zone.InfluenceLog, event)

	// Add to pending broadcast
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// BlocksBugsCells returns every world cell in the zone whose occupant blocks bugs (World.BlocksBugs) —
// the COMPLETE zone-wide collision set sent to each joiner (OpCodeZoneCollisionMap). Phase 1b: clients run
// per-bug collision against this instead of their view-scoped chunks, so a bug near a fence collides
// IDENTICALLY on every client regardless of camera. Deterministic order (sorted chunk keys). Anchor AND
// footprint cells both carry the occupant id, so iterating every cell covers multi-cell occupants.
func (s *WorldState) BlocksBugsCells() (cx []int, cy []int) {
	if s.CurrentZone == nil {
		return nil, nil
	}
	// Scan the WHOLE zone grid, not just s.Chunks — chunks load lazily (per subscription), so the first
	// joiner has NONE in memory at MatchJoin. We load the missing ones transiently from disk (read-only,
	// no RNG-bearing init, not stored) so the map is zone-COMPLETE and identical for first + late joiners.
	chunksX := s.CurrentZone.Width / ChunkSize
	chunksY := s.CurrentZone.Height / ChunkSize
	if chunksX <= 0 {
		chunksX = 8
	}
	if chunksY <= 0 {
		chunksY = 8
	}
	zonePath := "data/zones/" + s.CurrentZone.ZoneID
	for ccy := 0; ccy < chunksY; ccy++ {
		for ccx := 0; ccx < chunksX; ccx++ {
			chunk := s.chunkForCollision(zonePath, ccx, ccy)
			if chunk == nil {
				continue
			}
			for ly := 0; ly < len(chunk.Occupants); ly++ {
				row := chunk.Occupants[ly]
				for lx := 0; lx < len(row); lx++ {
					cell, err := ParseOccupantCell(row[lx])
					if err != nil || cell.Occupant == nil {
						continue
					}
					def := s.Entities[cell.Occupant.ID]
					if def != nil && def.World != nil && def.World.BlocksBugs {
						cx = append(cx, ccx*ChunkSize+lx)
						cy = append(cy, ccy*ChunkSize+ly)
					}
				}
			}
		}
	}
	return cx, cy
}

// chunkForCollision returns the chunk to scan for blocks_bugs occupants. If the chunk is already in memory
// (subscribed → saved-delta + lazy init already applied) it's returned as-is. Otherwise it's loaded from
// disk TRANSIENTLY with only the occupant delta overlaid (mirrors applyChunkSave's cell loop) — NOT stored
// and NO init, so a later real subscription still runs initFruitTrees/Nests/etc. exactly once (their RNG
// draws stay in their normal order). Result matches the in-memory form, so first + late joiners agree.
func (s *WorldState) chunkForCollision(zonePath string, cx, cy int) *ChunkData {
	if ch, ok := s.Chunks[ChunkKey(cx, cy)]; ok {
		return ch
	}
	ch, err := LoadChunk(zonePath, cx, cy)
	if err != nil {
		return nil // no authored file → no authored occupants here
	}
	if s.ZoneChunkCache != nil {
		if cs := s.ZoneChunkCache[ChunkKey(cx, cy)]; cs != nil {
			for _, e := range cs.Cells {
				if e.LY < 0 || e.LY >= ChunkSize || e.LX < 0 || e.LX >= ChunkSize {
					continue
				}
				if e.OccSet {
					ch.Occupants[e.LY][e.LX] = e.Occ // nil clears a broken authored occupant
				}
			}
		}
	}
	return ch
}

// AddOccupantBlocksBugsEvent logs a tick-ordered OCCUPANT_BLOCKS_BUGS event (a blocks_bugs occupant placed
// or removed at one cell) so every client updates its zone-wide bug-collision set at the SAME tick — the
// chunk-scoped WorldUpdate that renders the change can't reach far clients. Level=1 blocks, 0 clears.
func (s *WorldState) AddOccupantBlocksBugsEvent(zoneID string, cellX, cellY int, blocked bool) {
	zone := s.GetOrCreateZone(zoneID)
	level := 0
	if blocked {
		level = 1
	}
	event := InfluenceEvent{
		Tick:   s.TickCount,
		Seq:    zone.NextSeq,
		Type:   InfluenceOccupantBlocksBugs,
		ZoneID: zoneID,
		CellX:  cellX,
		CellY:  cellY,
		Level:  level,
	}
	zone.NextSeq++
	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// AddSwarmTargetEvent logs a SWARM_SET_TARGET leg through the same seq-gated ledger
// as AddInfluenceEvent. Coordinates/speed are fixed-point (×1000).
func (s *WorldState) AddSwarmTargetEvent(zoneID, swarmID string, originX, originY, targetX, targetY, speed int,
	targetPreyID string, strikeRadius, killsPerStrike, strikeCooldownTicks int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:    s.TickCount,
		Seq:     zone.NextSeq,
		Type:    InfluenceSwarmSetTarget,
		ZoneID:  zoneID,
		SwarmID: swarmID,
		OriginX: originX,
		OriginY: originY,
		TargetX: targetX,
		TargetY: targetY,
		Speed:   speed,
		// Hunt-leg fields (Phase 2) — non-empty only when the predator is actively hunting this prey.
		TargetPreyID:      targetPreyID,
		StrikeRadius:      strikeRadius,
		KillsPerStrike:    killsPerStrike,
		StrikeCooldownTks: strikeCooldownTicks,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)

	// Cost profiler: attribute this movement leg (the dominant per-tick traffic) to its species.
	if sw := s.Swarms[swarmID]; sw != nil {
		s.Perf.Count(sw.SpeciesID, "legs")
	}
}

// AddSwarmSplitEvent logs a SWARM_SPLIT through the seq-gated ledger: the parent swarm
// sheds its highest `count` alive bug-ids into a NEW swarm seeded at (cx, cy) (fixed-point
// ×1000). parentCount = the parent's POST-split count, so clients apply idempotently
// (move exactly AliveCount−parentCount bugs — zero when the split is already reflected,
// e.g. a late-joiner whose metadata is post-split). Bugs MOVE; positions preserved.
func (s *WorldState) AddSwarmSplitEvent(zoneID, parentID, childID string, count, parentCount, cx, cy int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:        s.TickCount,
		Seq:         zone.NextSeq,
		Type:        InfluenceSwarmSplit,
		ZoneID:      zoneID,
		SwarmID:     parentID,
		NewSwarmID:  childID,
		SplitCount:  count,
		ParentCount: parentCount,
		CenterX:     cx,
		CenterY:     cy,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// AddSwarmMergeEvent logs a SWARM_MERGE: the absorbed swarm's bugs MOVE into the survivor
// as ids newBugIDBase..newBugIDBase+count-1 (the survivor's pre-merge NextBugID), then the
// absorbed swarm is deleted. Clients apply it at the event tick, preserving bug positions.
func (s *WorldState) AddSwarmMergeEvent(zoneID, survivorID, absorbedID string, count, newBugIDBase int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:         s.TickCount,
		Seq:          zone.NextSeq,
		Type:         InfluenceSwarmMerge,
		ZoneID:       zoneID,
		SwarmID:      survivorID,
		NewSwarmID:   absorbedID,
		SplitCount:   count,
		NewBugIDBase: newBugIDBase,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// AddFoodEvent logs a food-registry change (ITEM_ROTTED = new food appeared; FOOD_CONSUMED =
// level crossed a threshold, 0 = gone). cellX/cellY are WORLD cells; level is the remaining food.
func (s *WorldState) AddFoodEvent(zoneID, eventType, foodID string, cellX, cellY, level int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:   s.TickCount,
		Seq:    zone.NextSeq,
		Type:   eventType,
		ZoneID: zoneID,
		CellX:  cellX,
		CellY:  cellY,
		FoodID: foodID,
		Level:  level,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// AddSwarmReproducedEvent logs a reproduction: the swarm bred at a food source and gains
// `count` new bugs with ids newBugIDBase..newBugIDBase+count-1. Clients spawn them at the
// swarm centre at the event tick (idempotent SpawnBugAt — same pattern as split/merge).
// AddSwarmReproducedEvent: the swarm gains count new bugs with ids newBugIDBase.. —
// emitted by reproduction (bred at a food source) AND by player bug-release into an
// existing swarm (the client handler is the same deterministic spawn loop either way).
// AddSwarmSpawnedEvent logs a SWARM_SPAWNED leg through the same seq-gated ledger so every client
// (live + late-join replay) creates the new swarm at the SAME tick with the same seed → bit-identical
// spawn-seeded wander. centerX/centerY are the spawn world pos ×1000 (== the swarm's first leg origin,
// via toFixed(WorldX)), so the fallback center matches when the first leg arrives. count = initial bug count.
func (s *WorldState) AddSwarmSpawnedEvent(zoneID, swarmID, speciesID string, count, centerX, centerY int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:       s.TickCount,
		Seq:        zone.NextSeq,
		Type:       InfluenceSwarmSpawned,
		ZoneID:     zoneID,
		SwarmID:    swarmID,
		SpeciesID:  speciesID,
		SplitCount: count,
		CenterX:    centerX,
		CenterY:    centerY,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

func (s *WorldState) AddSwarmReproducedEvent(zoneID, swarmID string, count, newBugIDBase int) {
	zone := s.GetOrCreateZone(zoneID)

	event := InfluenceEvent{
		Tick:         s.TickCount,
		Seq:          zone.NextSeq,
		Type:         InfluenceSwarmReproduced,
		ZoneID:       zoneID,
		SwarmID:      swarmID,
		SplitCount:   count,
		NewBugIDBase: newBugIDBase,
	}
	zone.NextSeq++

	zone.InfluenceLog = append(zone.InfluenceLog, event)
	s.PendingInfluence = append(s.PendingInfluence, event)
}

// PruneInfluenceLog removes old events to bound memory usage
// Keeps at least 200 ticks of events (2x snapshot interval)
func (s *WorldState) PruneInfluenceLog(zoneID string, currentTick int64) {
	zone := s.GetZone(zoneID)
	if zone == nil {
		return
	}

	const influenceLogMinTicks = 200
	cutoffTick := currentTick - influenceLogMinTicks
	if cutoffTick < 0 {
		cutoffTick = 0
	}

	// Remove events older than cutoff
	newLog := zone.InfluenceLog[:0]
	for _, evt := range zone.InfluenceLog {
		if evt.Tick >= cutoffTick {
			newLog = append(newLog, evt)
		}
	}
	zone.InfluenceLog = newLog
}

// CheckPlayerCellChange checks if player moved to a new cell and emits events
func (s *WorldState) CheckPlayerCellChange(playerID string, worldX, worldY float32, zoneID string) {
	// Calculate cell coordinates (floor for consistent behavior)
	newCellX := int(math.Floor(float64(worldX)))
	newCellY := int(math.Floor(float64(worldY)))

	old, exists := s.PlayerCells[playerID]
	if !exists || old.CellX != newCellX || old.CellY != newCellY {
		// Emit CELL_LEAVE for old cell (if exists)
		if exists {
			s.AddInfluenceEvent(zoneID, InfluencePlayerCellLeave, playerID, old.CellX, old.CellY, "", 0)
		}
		// Emit CELL_ENTER for new cell
		s.AddInfluenceEvent(zoneID, InfluencePlayerCellEnter, playerID, newCellX, newCellY, "", 0)

		// Update state
		s.PlayerCells[playerID] = &PlayerCellState{CellX: newCellX, CellY: newCellY}
	}
}

// ClearPendingInfluence resets pending events after broadcast
func (s *WorldState) ClearPendingInfluence() {
	s.PendingInfluence = s.PendingInfluence[:0]
}
