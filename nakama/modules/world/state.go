package world

import (
	"time"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// WorldConfig holds configurable world parameters
type WorldConfig struct {
	ChunkSize   int // Default: 32
	TickRate    int // Default: 10 (ticks per second)
	MaxPlayers  int // Default: 100
	WorldWidth  int // Default: 16 (chunks)
	WorldHeight int // Default: 16 (chunks)
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
}

// PlayerState tracks a player within the world
type PlayerState struct {
	UserID     string
	Username   string
	Position   entities.EntityPosition
	FacingLeft bool // For other players to see which way you're facing
}

// DefaultConfig returns sensible defaults from architecture doc
func DefaultConfig() WorldConfig {
	return WorldConfig{
		ChunkSize:   32,
		TickRate:    10,
		MaxPlayers:  100,
		WorldWidth:  16,
		WorldHeight: 16,
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
	}
}

// AddPlayer adds a new player to the world
func (s *WorldState) AddPlayer(userID, username string, presence runtime.Presence) {
	s.Players[userID] = &PlayerState{
		UserID:     userID,
		Username:   username,
		Position:   entities.EntityPosition{ChunkX: 8, ChunkY: 8, LocalX: 16, LocalY: 16}, // Spawn at center
		FacingLeft: false,
	}
	s.Presences[userID] = presence
}

// RemovePlayer removes a player from the world
func (s *WorldState) RemovePlayer(userID string) {
	delete(s.Players, userID)
	delete(s.Presences, userID)
}
