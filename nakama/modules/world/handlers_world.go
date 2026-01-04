package world

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	"bugfarmer/entities"

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

		// Send ground items in this chunk
		cs := state.Config.ChunkSize
		for _, item := range state.GroundItems {
			if item.Position.ChunkX == cx && item.Position.ChunkY == cy {
				spawnMsg := GroundItemSpawnMessage{
					ID:       item.ID,
					ItemType: item.ItemType,
					Count:    item.Count,
					X:        float32(cx*cs) + item.Position.LocalX,
					Y:        float32(cy*cs) + item.Position.LocalY,
				}
				spawnData, _ := json.Marshal(spawnMsg)
				dispatcher.BroadcastMessage(OpCodeGroundItemSpawn, spawnData, []runtime.Presence{presence}, nil, true)
			}
		}
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
	// Get entity definition
	def, exists := state.Entities[msg.OccupantID]
	if !exists {
		m.sendWorldError(dispatcher, state, userID, "Unknown item type")
		return
	}

	// Check entity can be placed in world
	if !def.IsPlaceable() {
		m.sendWorldError(dispatcher, state, userID, "Cannot place this item")
		return
	}

	// Validate player has item in inventory
	player := state.Players[userID]
	if player == nil {
		return
	}
	slotIndex := player.FindItem(msg.OccupantID)
	if slotIndex < 0 {
		m.sendWorldError(dispatcher, state, userID, "You don't have this item")
		return
	}

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

	// Consume item from inventory
	player.RemoveItem(slotIndex, 1)

	// Send inventory update to player
	slotMsg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    player.ItemSlots[slotIndex].ItemID,
		Count:     player.ItemSlots[slotIndex].Count,
	}
	slotData, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
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
	def, exists := state.Entities[occ.ID]
	if !exists || !def.IsBreakable() {
		return
	}

	// Get player's equipped tool
	player := state.Players[userID]
	if player == nil {
		return
	}
	toolType, toolTier := m.getToolStats(state, player.EquippedTool)

	// Check tool requirements
	if !def.CanBreakWith(toolType, toolTier) {
		m.sendWorldError(dispatcher, state, userID, "Need better tool")
		return
	}

	// Get or create breaking progress
	breakKey := fmt.Sprintf("%d,%d", msg.GridX, msg.GridY)
	hp := def.GetHP()
	progress, exists := state.BreakingState[breakKey]
	if !exists || progress.PlayerID != userID {
		progress = &BreakingProgress{
			GridX:     msg.GridX,
			GridY:     msg.GridY,
			PlayerID:  userID,
			CurrentHP: hp,
			MaxHP:     hp,
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
	logger.Debug("Broadcasting BreakProgress: %d,%d HP=%d/%d", msg.GridX, msg.GridY, progress.CurrentHP, progress.MaxHP)
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

		// Drop items to ground (with chance-based multi-drop)
		drops := def.GetDrops()
		cs := float32(state.Config.ChunkSize)
		for _, drop := range drops {
			// Roll for chance
			if rand.Float32() > drop.Chance {
				continue
			}

			// Create unique ground item ID
			itemID := fmt.Sprintf("item_%d_%d_%d", msg.GridX, msg.GridY, time.Now().UnixNano())

			// World position at cell center with random offset to prevent stacking
			worldX := float32(msg.GridX) + 0.5 + (rand.Float32()-0.5)*0.3
			worldY := float32(msg.GridY) + 0.5 + (rand.Float32()-0.5)*0.3

			// Local position within chunk
			localX := worldX - float32(cx)*cs
			localY := worldY - float32(cy)*cs

			groundItem := &entities.GroundItem{
				ID:       itemID,
				ItemType: drop.ItemID,
				Count:    drop.Count,
				Position: entities.EntityPosition{
					ChunkX: cx,
					ChunkY: cy,
					LocalX: localX,
					LocalY: localY,
				},
				Lifetime: 60.0,
			}
			state.GroundItems[itemID] = groundItem

			// Broadcast spawn to chunk subscribers
			spawnMsg := GroundItemSpawnMessage{
				ID:       itemID,
				ItemType: drop.ItemID,
				Count:    drop.Count,
				X:        worldX,
				Y:        worldY,
			}
			m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)

			logger.Debug("Spawned ground item %s x%d at %.1f,%.1f", drop.ItemID, drop.Count, worldX, worldY)
		}

		logger.Debug("Player %s broke %s at %d,%d", userID, occ.ID, msg.GridX, msg.GridY)

		// Clear breaking state
		delete(state.BreakingState, breakKey)

		// Broadcast removal
		m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", nil)
	}
}

// canPlace checks if an occupant can be placed at the given location
func (m *Match) canPlace(state *WorldState, gx, gy int, def *EntityDef, dir int) bool {
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
func (m *Match) getToolStats(state *WorldState, toolID string) (toolType string, tier int) {
	if toolID == "" {
		return "", 0 // Bare hands
	}

	// Look up tool from entity definitions
	if def, exists := state.Entities[toolID]; exists && def.Category == "tool" {
		return def.ToolType, def.ToolTier
	}

	return "", 0
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

// handlePickupItem processes a player's request to pick up a ground item
func (m *Match) handlePickupItem(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg PickupItemMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	item, exists := state.GroundItems[msg.ID]
	if !exists {
		// Item already picked up by another player - silently ignore
		return
	}

	// Distance check (server allows 3.0 vs client 2.0 to account for latency)
	cs := state.Config.ChunkSize
	playerX := player.WorldX(cs)
	playerY := player.WorldY(cs)
	itemX := float32(item.Position.ChunkX*cs) + item.Position.LocalX
	itemY := float32(item.Position.ChunkY*cs) + item.Position.LocalY

	dx := playerX - itemX
	dy := playerY - itemY
	if dx*dx+dy*dy > 9.0 { // 3.0 squared
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	slotIndex := player.AddItem(item.ItemType, item.Count)
	if slotIndex < 0 {
		m.sendWorldError(dispatcher, state, userID, "Inventory full")
		return
	}

	// Remove from ground
	delete(state.GroundItems, msg.ID)

	// Send inventory update to player
	slotMsg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    player.ItemSlots[slotIndex].ItemID,
		Count:     player.ItemSlots[slotIndex].Count,
	}
	slotData, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
	}

	// Broadcast removal to chunk subscribers
	removeMsg := GroundItemRemoveMessage{ID: msg.ID}
	m.broadcastToChunk(dispatcher, state, item.Position.ChunkX, item.Position.ChunkY, OpCodeGroundItemRemove, removeMsg)

	logger.Debug("Player %s picked up %s x%d", userID, item.ItemType, item.Count)
}
