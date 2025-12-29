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

// === Bug System Messages (Server → Client) ===

// SwarmData represents a single swarm in updates (OpCode 20)
type SwarmData struct {
	ID        string  `json:"id"`
	SpeciesID string  `json:"species_id"`
	X         float32 `json:"x"`
	Y         float32 `json:"y"`
	Radius    float32 `json:"radius"`
	Count     int     `json:"count"`
	Facing    int     `json:"facing"`
}

// SwarmUpdateMessage is broadcast to clients (OpCode 20)
type SwarmUpdateMessage struct {
	Swarms []SwarmData `json:"swarms"`
}

// === Bug Catching Messages (Phase 2a) ===

// CatchBugMessage is sent by client (OpCode 24)
// Client detects flies in radius and sends count per swarm
type CatchBugMessage struct {
	ClickX      float32 `json:"click_x"`      // World X where player clicked
	ClickY      float32 `json:"click_y"`      // World Y where player clicked
	SwarmID     string  `json:"swarm_id"`     // Which swarm was caught from
	CaughtCount int     `json:"caught_count"` // Client-detected count
}

// BugCaughtMessage is broadcast to all clients (OpCode 25)
// Allows other clients to update swarm visuals and show catch animation
type BugCaughtMessage struct {
	SwarmID   string  `json:"swarm_id"`
	CatcherID string  `json:"catcher_id"`
	Count     int     `json:"count"`     // How many bugs caught
	NewTotal  int     `json:"new_total"` // Swarm's new count
	X         float32 `json:"x"`         // Catch position for animation
	Y         float32 `json:"y"`
}

// EquipToolMessage is sent by client (OpCode 27)
type EquipToolMessage struct {
	ToolID string `json:"tool_id"` // "" for hand, "small_net" for small net, etc.
}

// === Inventory Messages (Phase 3) ===

// SlotUpdateMessage is sent when a single slot changes (OpCode 26 for bugs, 37 for items)
type SlotUpdateMessage struct {
	SlotIndex int    `json:"slot_index"`
	ItemID    string `json:"item_id"` // "" = empty slot
	Count     int    `json:"count"`
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
	SourceType  string `json:"source_type"`  // "bug" or "item"
	SourceIndex int    `json:"source_index"`
	DestType    string `json:"dest_type"`    // "bug" or "item"
	DestIndex   int    `json:"dest_index"`
	Count       int    `json:"count"`        // -1 = all, else specific amount
}

// ErrorMessage is sent when an operation fails (OpCode 40)
type ErrorMessage struct {
	Error string `json:"error"`
}
