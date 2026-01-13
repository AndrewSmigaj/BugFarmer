package world

import (
	"math"
	"time"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// WorldConfig holds configurable world parameters
type WorldConfig struct {
	ChunkSize   int // Default: 32 (cells per chunk side)
	BlockSize   int // Default: 16 (pixels per cell)
	TickRate    int // Default: 10 (ticks per second)
	MaxPlayers  int // Default: 100
	WorldWidth  int // Default: 16 (chunks per zone)
	WorldHeight int // Default: 16 (chunks per zone)
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
	WorldSeed    int64 // Global seed for deterministic bug simulation
	Players      map[string]*PlayerState
	Presences    map[string]runtime.Presence

	// Entity maps (Phase 1)
	Swarms      map[string]*entities.SwarmState
	EggClusters map[string]*entities.EggClusterState
	Individuals map[string]*entities.IndividualBugState
	Plants      map[string]*entities.PlantState
	GroundItems map[string]*entities.GroundItem

	// Config
	Species map[string]*entities.BugSpecies // Loaded from config

	// Timing
	LastMergeCheck int64 // Tick of last merge/split check

	// World Building (Phase 4)
	CurrentZone   *ZoneConfig                  // Current zone metadata
	Chunks        map[string]*ChunkData        // "chunkX,chunkY" -> chunk data
	ChunkSubs     map[string]map[string]bool   // "chunkX,chunkY" -> player IDs subscribed
	TileDefs      map[string]*TileDefinition   // Loaded from tiles.json
	Entities      map[string]*EntityDef        // Loaded from entities/*.json (items, occupants, placeables)
	BreakingState map[string]*BreakingProgress // "gx,gy" -> breaking progress

	// Bug spawn tracking (zone-level, per species)
	SwarmsBySpecies  map[string][]string // speciesID → swarmIDs of that species
	SpeciesNextSpawn map[string]float64  // speciesID → next spawn time (seconds since start)

	// Bug sync (late joiner + drift detection)
	LastSampleTick   map[string]int64               // swarmID → last sample tick
	PendingSnapshots map[string]*PendingSnapshotReq // requestID → pending snapshot request

	// Influence event system (server-authored bug sync)
	PlayerCells      map[string]*PlayerCellState // playerID → current cell
	ZoneStates       map[string]*ZoneState       // zoneID → zone authority/sync state
	PendingInfluence []InfluenceEvent            // Events to broadcast this tick
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
	ZoneID       string
	SnapshotTick int64
	Swarms       []SwarmSnapshotData
	StateHash    string
}

// PendingSnapshotReq tracks a snapshot request waiting for response
type PendingSnapshotReq struct {
	RequesterID  string   // Player who needs the snapshot
	SourceID     string   // Current player we're waiting on
	TriedSources []string // Players we've already tried (for fallback on timeout)
	ChunkX       int      // Chunk coordinates
	ChunkY       int
	RequestTick  int64 // Tick when request was made (for timeout)
}

// InventorySlot holds one stack of items (bugs or tools)
type InventorySlot struct {
	ItemID string `json:"item_id"` // species_id for bugs, item_id for tools, "" = empty
	Count  int    `json:"count"`
}

// PlayerState tracks a player within the world
type PlayerState struct {
	UserID   string
	Username string
	Position entities.EntityPosition
	Facing   entities.Direction // For other players to see which way you're facing

	// Inventory (Phase 3)
	Coins     int64              // Currency
	BugSlots  [20]InventorySlot  // Bug inventory (20 slots)
	ItemSlots [20]InventorySlot  // Tool inventory (20 slots, first 10 = hotbar)

	// Bug catching
	LastCatchTime int64  // Unix millis, rate limiting
	EquippedTool  string // "" (hand), "small_net", etc.
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
		Config:       DefaultConfig(),
		WorldID:      worldID,
		OwnerID:      ownerID,
		Name:         name,
		AccessPolicy: accessPolicy,
		CreatedAt:    time.Now().Unix(),
		TickCount:    0,
		Players:      make(map[string]*PlayerState),
		Presences:    make(map[string]runtime.Presence),
		// Entity maps
		Swarms:      make(map[string]*entities.SwarmState),
		EggClusters: make(map[string]*entities.EggClusterState),
		Individuals: make(map[string]*entities.IndividualBugState),
		Plants:      make(map[string]*entities.PlantState),
		GroundItems: make(map[string]*entities.GroundItem),
		Species:     make(map[string]*entities.BugSpecies),
		// World building
		Chunks:        make(map[string]*ChunkData),
		ChunkSubs:     make(map[string]map[string]bool),
		TileDefs:      make(map[string]*TileDefinition),
		Entities:      make(map[string]*EntityDef),
		BreakingState: make(map[string]*BreakingProgress),
		// Bug spawn tracking
		SwarmsBySpecies:  make(map[string][]string),
		SpeciesNextSpawn: make(map[string]float64),
		// Bug sync
		LastSampleTick:   make(map[string]int64),
		PendingSnapshots: make(map[string]*PendingSnapshotReq),
		// Influence event system
		PlayerCells:      make(map[string]*PlayerCellState),
		ZoneStates:       make(map[string]*ZoneState),
		PendingInfluence: make([]InfluenceEvent, 0),
	}
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
	player.SetWorldPosition(spawnX, spawnY, s.Config.ChunkSize)

	// Give new player starting tools in hotbar
	player.ItemSlots[0] = InventorySlot{ItemID: "small_net", Count: 1}
	player.ItemSlots[1] = InventorySlot{ItemID: "pickaxe_wood", Count: 1}
	player.ItemSlots[2] = InventorySlot{ItemID: "axe_wood", Count: 1}
	player.ItemSlots[3] = InventorySlot{ItemID: "shovel_wood", Count: 1}
	player.ItemSlots[4] = InventorySlot{ItemID: "dirt_block", Count: 10} // Test placement
	player.EquippedTool = "small_net"

	s.Players[userID] = player
	s.Presences[userID] = presence
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

	// Get chunk
	chunk := w.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return true // Out of bounds = blocked
	}

	// Check occupant layer (fences, walls, trees)
	cell, err := chunk.GetOccupantCell(lx, ly)
	if err == nil && cell.Occupant != nil {
		entityDef := w.Entities[cell.Occupant.ID]
		if entityDef != nil && entityDef.World != nil && entityDef.World.BlocksBugs {
			return true
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
