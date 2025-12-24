package world

// Client → Server OpCodes
const (
	OpCodeMovement       int64 = 1  // Player position update
	OpCodeAction         int64 = 2  // Generic interaction (talk to NPC, open chest)
	OpCodeChunkSubscribe int64 = 3  // Subscribe to chunk updates
	OpCodeChunkUnsub     int64 = 4  // Unsubscribe from chunk updates
	OpCodeTilePlace      int64 = 5  // Place floor/wall tile
	OpCodeTileBreak      int64 = 6  // Remove floor/wall tile
	OpCodeToolUse        int64 = 7  // Use tool on target (axe, net, spray)
	// 8-9 reserved for future
)

// Server → Client OpCodes
const (
	OpCodeStateUpdate  int64 = 10 // Chunk tile changes
	OpCodeEntityUpdate int64 = 11 // Entity updates (bugs, trees, players - anything with dynamic state)
	OpCodeChat         int64 = 12 // Chat messages
)

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
}

// EntityUpdateMessage is broadcast to clients (OpCode 11)
type EntityUpdateMessage struct {
	Entities []EntityData `json:"entities"`
}
