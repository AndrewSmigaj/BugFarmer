package world

import (
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
	CurrentZone   *ZoneConfig                    // Current zone metadata
	Chunks        map[string]*ChunkData          // "chunkX,chunkY" -> chunk data
	ChunkSubs     map[string]map[string]bool     // "chunkX,chunkY" -> player IDs subscribed
	TileDefs      map[string]*TileDefinition     // Loaded from tiles.json
	OccupantDefs  map[string]*OccupantDefinition // Loaded from occupants.json
	BreakingState map[string]*BreakingProgress   // "gx,gy" -> breaking progress
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
		OccupantDefs:  make(map[string]*OccupantDefinition),
		BreakingState: make(map[string]*BreakingProgress),
	}
}

// AddPlayer adds a new player to the world
func (s *WorldState) AddPlayer(userID, username string, presence runtime.Presence) {
	player := &PlayerState{
		UserID:   userID,
		Username: username,
		Position: entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 10, LocalY: 10}, // Spawn near origin
		Facing:   entities.DirDown,                                                      // Default: facing camera
		// BugSlots are zero-initialized (empty)
		// Coins defaults to 0
	}
	// Give new player a Small Net in hotbar slot 1 (ItemSlots[0])
	player.ItemSlots[0] = InventorySlot{ItemID: "small_net", Count: 1}
	player.EquippedTool = "small_net"

	s.Players[userID] = player
	s.Presences[userID] = presence
}

// RemovePlayer removes a player from the world
func (s *WorldState) RemovePlayer(userID string) {
	delete(s.Players, userID)
	delete(s.Presences, userID)
}
