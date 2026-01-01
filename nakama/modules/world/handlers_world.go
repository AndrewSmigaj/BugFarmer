package world

import (
	"encoding/json"
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"
)

// handleChunkSubscribe loads a chunk and sends it to the subscribing player
func (m *Match) handleChunkSubscribe(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	cx, cy int,
) {
	chunkKey := ChunkKey(cx, cy)

	// Load chunk if not in memory
	if _, exists := state.Chunks[chunkKey]; !exists {
		zonePath := "data/zones/" + state.CurrentZone.ZoneID
		chunk, err := LoadChunk(zonePath, cx, cy)
		if err != nil {
			// Create empty chunk if file doesn't exist
			chunk = NewEmptyChunk(cx, cy, "grass")
			logger.Debug("Created empty chunk %d,%d (no file)", cx, cy)
		}
		state.Chunks[chunkKey] = chunk
	}

	// Add player to chunk subscribers
	if state.ChunkSubs[chunkKey] == nil {
		state.ChunkSubs[chunkKey] = make(map[string]bool)
	}
	state.ChunkSubs[chunkKey][userID] = true

	// Send chunk data to player
	chunk := state.Chunks[chunkKey]
	msg := ChunkDataMessage{
		ChunkX:    cx,
		ChunkY:    cy,
		Ground:    chunk.Ground,
		Occupants: chunk.Occupants,
	}
	data, _ := json.Marshal(msg)

	presence, ok := state.Presences[userID]
	if ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeChunkData, data, []runtime.Presence{presence}, nil, true)
	}
}

// handleChunkUnsub removes a player from chunk subscribers
func (m *Match) handleChunkUnsub(
	state *WorldState,
	userID string,
	cx, cy int,
) {
	chunkKey := ChunkKey(cx, cy)
	if subs, exists := state.ChunkSubs[chunkKey]; exists {
		delete(subs, userID)
	}
}

// handleTilePlace places an occupant at the specified location
func (m *Match) handleTilePlace(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg TilePlaceMessage,
) {
	// Get occupant definition
	def, exists := state.OccupantDefs[msg.OccupantID]
	if !exists {
		m.sendWorldError(dispatcher, state, userID, "Unknown occupant type")
		return
	}

	// TODO: Validate player has item in inventory

	// Check placement is valid
	if !m.canPlace(state, msg.GridX, msg.GridY, def, msg.Direction) {
		m.sendWorldError(dispatcher, state, userID, "Cannot place here")
		return
	}

	// Place occupant in chunk data
	cx, cy, lx, ly := GlobalToChunk(msg.GridX, msg.GridY)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		m.sendWorldError(dispatcher, state, userID, "Chunk not loaded")
		return
	}

	occ := &PlacedOccupant{ID: msg.OccupantID, Dir: msg.Direction}
	chunk.SetOccupant(lx, ly, occ)

	// Mark blocked cells for multi-cell occupants
	w, h := def.GetFootprint(msg.Direction)
	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			if dx == 0 && dy == 0 {
				continue // Skip anchor
			}
			bx, by := msg.GridX+dx, msg.GridY+dy
			bcx, bcy, blx, bly := GlobalToChunk(bx, by)
			bChunk := state.Chunks[ChunkKey(bcx, bcy)]
			if bChunk != nil {
				bChunk.SetBlockedMarker(blx, bly)
			}
		}
	}

	logger.Debug("Player %s placed %s at %d,%d", userID, msg.OccupantID, msg.GridX, msg.GridY)

	// Broadcast update to chunk subscribers
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", occ)
}

// handleTileBreak attempts to break/mine an occupant
func (m *Match) handleTileBreak(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg TileBreakMessage,
	tick int64,
) {
	cx, cy, lx, ly := GlobalToChunk(msg.GridX, msg.GridY)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		return // Chunk not loaded
	}

	// Get what's at this cell
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty {
		return // Nothing to break
	}
	if cell.IsBlocked {
		// TODO: Find anchor cell and break that instead
		return
	}

	occ := cell.Occupant
	def, exists := state.OccupantDefs[occ.ID]
	if !exists || !def.IsBreakable {
		return
	}

	// Get player's equipped tool
	player := state.Players[userID]
	if player == nil {
		return
	}
	toolType, toolTier := m.getToolStats(player.EquippedTool)

	// Check tool requirements
	if !def.CanBreakWith(toolType, toolTier) {
		m.sendWorldError(dispatcher, state, userID, "Need better tool")
		return
	}

	// Get or create breaking progress
	breakKey := fmt.Sprintf("%d,%d", msg.GridX, msg.GridY)
	progress, exists := state.BreakingState[breakKey]
	if !exists || progress.PlayerID != userID {
		progress = &BreakingProgress{
			GridX:     msg.GridX,
			GridY:     msg.GridY,
			PlayerID:  userID,
			CurrentHP: def.HP,
			MaxHP:     def.HP,
			LastTick:  tick,
		}
		state.BreakingState[breakKey] = progress
	}

	// Apply damage
	progress.CurrentHP--
	progress.LastTick = tick

	// Broadcast progress
	progressMsg := BreakProgressMessage{
		GridX:     msg.GridX,
		GridY:     msg.GridY,
		CurrentHP: progress.CurrentHP,
		MaxHP:     progress.MaxHP,
		PlayerID:  userID,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBreakProgress, progressMsg)

	// Check if broken
	if progress.CurrentHP <= 0 {
		// Remove occupant
		chunk.ClearOccupant(lx, ly)

		// Clear blocked cells for multi-cell
		w, h := def.GetFootprint(occ.Dir)
		for dy := 0; dy < h; dy++ {
			for dx := 0; dx < w; dx++ {
				bx, by := msg.GridX+dx, msg.GridY+dy
				bcx, bcy, blx, bly := GlobalToChunk(bx, by)
				bChunk := state.Chunks[ChunkKey(bcx, bcy)]
				if bChunk != nil {
					bChunk.ClearOccupant(blx, bly)
				}
			}
		}

		// TODO: Drop items to ground or give to player inventory

		logger.Debug("Player %s broke %s at %d,%d", userID, occ.ID, msg.GridX, msg.GridY)

		// Clear breaking state
		delete(state.BreakingState, breakKey)

		// Broadcast removal
		m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", nil)
	}
}

// canPlace checks if an occupant can be placed at the given location
func (m *Match) canPlace(state *WorldState, gx, gy int, def *OccupantDefinition, dir int) bool {
	w, h := def.GetFootprint(dir)

	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			cx, cy, lx, ly := GlobalToChunk(gx+dx, gy+dy)
			chunkKey := ChunkKey(cx, cy)
			chunk, exists := state.Chunks[chunkKey]
			if !exists {
				return false
			}

			cell, _ := chunk.GetOccupantCell(lx, ly)
			if !cell.IsEmpty {
				return false
			}
		}
	}
	return true
}

// broadcastToChunk sends a message to all players subscribed to a chunk
func (m *Match) broadcastToChunk(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	cx, cy int,
	opCode int64,
	msg interface{},
) {
	chunkKey := ChunkKey(cx, cy)
	subs := state.ChunkSubs[chunkKey]
	if len(subs) == 0 {
		return
	}

	var presences []runtime.Presence
	for userID := range subs {
		if p, exists := state.Presences[userID]; exists && p != nil {
			presences = append(presences, p)
		}
	}

	if len(presences) == 0 {
		return
	}

	data, _ := json.Marshal(msg)
	dispatcher.BroadcastMessage(opCode, data, presences, nil, true)
}

// broadcastWorldUpdate sends a world cell update to chunk subscribers
func (m *Match) broadcastWorldUpdate(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	cx, cy, gx, gy int,
	ground string,
	occupant *PlacedOccupant,
) {
	msg := WorldUpdateMessage{
		GridX:    gx,
		GridY:    gy,
		Ground:   ground,
		Occupant: occupant,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeWorldUpdate, msg)
}

// getToolStats returns the tool type and tier for a given tool ID
func (m *Match) getToolStats(toolID string) (toolType string, tier int) {
	// TODO: Look up from item definitions
	// For now, hardcode some basics
	switch toolID {
	case "pickaxe_wood":
		return "pickaxe", 1
	case "pickaxe_stone":
		return "pickaxe", 2
	case "pickaxe_copper":
		return "pickaxe", 3
	case "pickaxe_iron":
		return "pickaxe", 4
	case "axe_wood":
		return "axe", 1
	case "axe_stone":
		return "axe", 2
	case "axe_copper":
		return "axe", 3
	case "axe_iron":
		return "axe", 4
	case "shovel_wood":
		return "shovel", 1
	case "shovel_stone":
		return "shovel", 2
	default:
		return "", 0
	}
}

// sendWorldError sends an error message to a specific player
func (m *Match) sendWorldError(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	message string,
) {
	msg := ErrorMessage{Error: message}
	data, _ := json.Marshal(msg)
	if presence, exists := state.Presences[userID]; exists && presence != nil {
		dispatcher.BroadcastMessage(OpCodeErrorMessage, data, []runtime.Presence{presence}, nil, true)
	}
}
