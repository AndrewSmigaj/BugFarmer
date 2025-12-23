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
