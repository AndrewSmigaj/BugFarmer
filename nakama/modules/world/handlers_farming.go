package world

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// handleToolUse routes tool actions based on equipped tool type
func (m *Match) handleToolUse(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg ToolUseMessage,
	tick int64,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	toolID := player.EquippedTool
	if toolID == "" {
		m.sendWorldError(dispatcher, state, userID, "No tool equipped")
		return
	}

	toolDef := state.Entities[toolID]
	if toolDef == nil {
		m.sendWorldError(dispatcher, state, userID, "Unknown tool")
		return
	}

	// Route based on tool type
	switch toolDef.ToolType {
	case "hoe":
		m.handleHoe(logger, dispatcher, state, userID, msg.GridX, msg.GridY, tick)
	case "watering_can":
		m.handleWatering(logger, dispatcher, state, userID, msg.GridX, msg.GridY, tick)
	default:
		m.sendWorldError(dispatcher, state, userID, "Use left-click for this tool")
	}
}

// validateToolCooldown checks if enough time has passed since last tool use
func (m *Match) validateToolCooldown(state *WorldState, player *PlayerState, tick int64) bool {
	toolDef := state.Entities[player.EquippedTool]
	if toolDef == nil {
		return true // No tool = no cooldown
	}

	cooldown := int64(toolDef.CooldownTicks)
	if cooldown <= 0 {
		cooldown = 3 // Default 3 ticks (0.3s at 10Hz)
	}

	if tick-player.LastToolTick < cooldown {
		return false
	}

	player.LastToolTick = tick
	return true
}

// handleHoe converts grass/dirt to garden_plot
func (m *Match) handleHoe(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	gx, gy int,
	tick int64,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Validate cooldown
	if !m.validateToolCooldown(state, player, tick) {
		return
	}

	// Get chunk and local coords
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		m.sendWorldError(dispatcher, state, userID, "Chunk not loaded")
		return
	}

	// Get tile at position
	tile := chunk.GetGroundTile(lx, ly)
	tileDef := state.TileDefs[tile]
	if tileDef == nil {
		m.sendWorldError(dispatcher, state, userID, "Unknown tile")
		return
	}

	// Check tile supports hoeing
	newTile := tileDef.GetToolActionResult("hoe")
	if newTile == "" {
		m.sendWorldError(dispatcher, state, userID, "Cannot hoe here")
		return
	}

	// Check cell is empty (no occupant)
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if !cell.IsEmpty {
		m.sendWorldError(dispatcher, state, userID, "Cell is occupied")
		return
	}

	// Change ground tile
	chunk.Ground[ly][lx] = newTile

	// Broadcast WorldUpdate with new ground tile
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, gx, gy, newTile, nil)

	logger.Debug("Player %s hoed tile at %d,%d -> %s", userID, gx, gy, newTile)
}

// handleWatering waters a crop or refills from water tile
func (m *Match) handleWatering(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	gx, gy int,
	tick int64,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Validate cooldown
	if !m.validateToolCooldown(state, player, tick) {
		return
	}

	// Find which slot has the watering can
	slotIndex := -1
	for i := 0; i < 10; i++ { // Check hotbar first
		if player.ItemSlots[i].ItemID == player.EquippedTool {
			slotIndex = i
			break
		}
	}
	if slotIndex < 0 {
		return
	}

	slot := &player.ItemSlots[slotIndex]

	// Get chunk and tile
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return
	}

	tile := chunk.GetGroundTile(lx, ly)

	// Check if target is water tile (refill)
	if tile == "water_shallow" || tile == "water_deep" {
		// Refill watering can
		if slot.Metadata == nil {
			slot.Metadata = make(map[string]int)
		}

		toolDef := state.Entities[player.EquippedTool]
		capacity := 40 // Default
		if toolDef != nil && toolDef.MetadataDefaults != nil {
			if cap, ok := toolDef.MetadataDefaults["capacity"]; ok {
				capacity = cap
			}
		}

		slot.Metadata["uses"] = capacity
		slot.Metadata["capacity"] = capacity
		m.sendSlotUpdate(dispatcher, state, userID, slotIndex, slot)
		logger.Debug("Player %s refilled watering can", userID)
		return
	}

	// Check uses remaining
	if slot.Metadata == nil || slot.Metadata["uses"] <= 0 {
		m.sendWorldError(dispatcher, state, userID, "Watering can is empty")
		return
	}

	// Find crop at gx,gy
	cropKey := fmt.Sprintf("%d,%d", gx, gy)
	crop := state.CropStates[cropKey]
	if crop == nil {
		m.sendWorldError(dispatcher, state, userID, "No crop here")
		return
	}

	cropDef := state.CropDefs[crop.PlantType]
	if cropDef == nil {
		m.sendWorldError(dispatcher, state, userID, "Unknown crop type")
		return
	}

	if crop.WateringsToday >= cropDef.MaxDailyWaterings {
		m.sendWorldError(dispatcher, state, userID, "Crop already watered today")
		return
	}

	// Apply watering
	crop.Water++
	crop.WateringsToday++
	slot.Metadata["uses"]--

	// Send updates
	m.sendSlotUpdate(dispatcher, state, userID, slotIndex, slot)
	m.broadcastCropUpdate(dispatcher, state, gx, gy, crop)

	logger.Debug("Player %s watered crop at %d,%d (water=%d)", userID, gx, gy, crop.Water)
}

// sendSlotUpdate sends an item slot update to a specific player
func (m *Match) sendSlotUpdate(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	slotIndex int,
	slot *InventorySlot,
) {
	msg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    slot.ItemID,
		Count:     slot.Count,
		Metadata:  slot.Metadata,
	}

	presence, ok := state.Presences[userID]
	if ok && presence != nil {
		data, _ := json.Marshal(msg)
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, data, []runtime.Presence{presence}, nil, true)
	}
}

// broadcastCropUpdate sends crop state to chunk subscribers
func (m *Match) broadcastCropUpdate(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	gx, gy int,
	crop *entities.CropState,
) {
	cx, cy, _, _ := GlobalToChunk(gx, gy)

	msg := CropUpdateMessage{
		GridX: gx,
		GridY: gy,
		Stage: crop.Stage,
		HP:    crop.HP,
		Water: crop.Water,
		Flags: int(crop.Flags),
	}

	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeCropUpdate, msg)
}

// handlePlantInteract handles harvesting or destroying a crop
func (m *Match) handlePlantInteract(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg PlantInteractMessage,
	tick int64,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Find crop at position
	cropKey := fmt.Sprintf("%d,%d", msg.GridX, msg.GridY)
	crop := state.CropStates[cropKey]
	if crop == nil {
		m.sendWorldError(dispatcher, state, userID, "No crop here")
		return
	}

	cropDef := state.CropDefs[crop.PlantType]
	if cropDef == nil {
		return
	}

	cx, cy, lx, ly := GlobalToChunk(msg.GridX, msg.GridY)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return
	}

	if msg.DestroyIntent {
		// Destroy the crop regardless of stage
		m.destroyCrop(logger, dispatcher, state, crop, cropKey, cx, cy, lx, ly)
		logger.Debug("Player %s destroyed crop at %d,%d", userID, msg.GridX, msg.GridY)
		return
	}

	// Harvest attempt
	matureStage := cropDef.GrowthStages - 1
	if crop.Stage < matureStage {
		m.sendWorldError(dispatcher, state, userID, "Crop is not ready")
		return
	}

	// Calculate drops
	dropCount := cropDef.HarvestCountMin
	if cropDef.HarvestCountMax > cropDef.HarvestCountMin {
		dropCount += rand.Intn(cropDef.HarvestCountMax - cropDef.HarvestCountMin + 1)
	}

	// Spawn harvest items on ground
	m.spawnHarvestDrops(dispatcher, state, cropDef.HarvestItem, dropCount, msg.GridX, msg.GridY, cx, cy)

	// Seed drop chance
	if cropDef.SeedDropChance > 0 && rand.Float32() < cropDef.SeedDropChance {
		seedID := "seed_" + crop.PlantType
		m.spawnHarvestDrops(dispatcher, state, seedID, 1, msg.GridX, msg.GridY, cx, cy)
	}

	// Handle multi-harvest vs single-harvest
	if cropDef.MultiHarvest && crop.HarvestsRemaining > 1 {
		// Multi-harvest: reset to earlier stage, decrement remaining
		crop.HarvestsRemaining--
		crop.Stage = 1 // Reset to sprout stage
		crop.Water = 0 // Reset water
		m.broadcastCropUpdate(dispatcher, state, msg.GridX, msg.GridY, crop)
		logger.Debug("Player %s harvested %s (multi), %d harvests remaining",
			userID, crop.PlantType, crop.HarvestsRemaining)
	} else {
		// Single harvest or last harvest: remove crop
		m.destroyCrop(logger, dispatcher, state, crop, cropKey, cx, cy, lx, ly)
		logger.Debug("Player %s harvested %s (final)", userID, crop.PlantType)
	}
}

// destroyCrop removes a crop from the world
func (m *Match) destroyCrop(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	crop *entities.CropState,
	cropKey string,
	cx, cy, lx, ly int,
) {
	// Remove from crop states
	delete(state.CropStates, cropKey)

	// Remove occupant
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk != nil {
		chunk.ClearOccupant(lx, ly)
	}

	// Broadcast removal
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, crop.GridX, crop.GridY, "", nil)
}

// spawnHarvestDrops creates ground items from harvest
func (m *Match) spawnHarvestDrops(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	itemType string,
	count int,
	gx, gy, cx, cy int,
) {
	cs := float32(state.Config.ChunkSize)

	// Create ground item with slight random offset
	itemID := fmt.Sprintf("harvest_%d_%d_%d", gx, gy, time.Now().UnixNano())
	worldX := float32(gx) + 0.5 + (rand.Float32()-0.5)*0.3
	worldY := float32(gy) + 0.5 + (rand.Float32()-0.5)*0.3
	localX := worldX - float32(cx)*cs
	localY := worldY - float32(cy)*cs

	groundItem := &entities.GroundItem{
		ID:       itemID,
		ItemType: itemType,
		Count:    count,
		Position: entities.EntityPosition{
			ChunkX: cx,
			ChunkY: cy,
			LocalX: localX,
			LocalY: localY,
		},
		Lifetime: 60.0,
	}
	state.GroundItems[itemID] = groundItem

	// Broadcast spawn
	spawnMsg := GroundItemSpawnMessage{
		ID:       itemID,
		ItemType: itemType,
		Count:    count,
		X:        worldX,
		Y:        worldY,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)
}

// processCropGrowth advances crop growth based on water accumulation
func (m *Match) processCropGrowth(state *WorldState, dispatcher runtime.MatchDispatcher) {
	for cropKey, crop := range state.CropStates {
		cropDef := state.CropDefs[crop.PlantType]
		if cropDef == nil {
			continue
		}

		matureStage := cropDef.GrowthStages - 1
		if crop.Stage >= matureStage {
			continue // Already mature
		}

		// Check if water meets threshold for next stage
		requiredWater := (crop.Stage + 1) * cropDef.WateringsPerStage
		if crop.Water >= requiredWater {
			crop.Stage++
			m.broadcastCropUpdate(dispatcher, state, crop.GridX, crop.GridY, crop)

			// Parse cropKey back to gx,gy for logging
			_ = cropKey // suppress unused warning
		}
	}
}

// processFruitTrees handles fruit growth and natural dropping
func (m *Match) processFruitTrees(
	state *WorldState,
	dispatcher runtime.MatchDispatcher,
	logger runtime.Logger,
) {
	for treeKey, tree := range state.FruitTreeStates {
		// Get tree entity definition
		cx, cy, lx, ly := GlobalToChunk(tree.GridX, tree.GridY)
		chunk := state.Chunks[ChunkKey(cx, cy)]
		if chunk == nil {
			continue
		}

		cell, _ := chunk.GetOccupantCell(lx, ly)
		if cell.IsEmpty || cell.Occupant == nil {
			// Tree was removed, clean up state
			delete(state.FruitTreeStates, treeKey)
			continue
		}

		treeDef := state.Entities[cell.Occupant.ID]
		if treeDef == nil || treeDef.World == nil || treeDef.World.FruitType == "" {
			continue // Not a fruit tree
		}

		// Fruit growth
		tree.GrowthProgress++
		if tree.GrowthProgress >= treeDef.World.FruitGrowTicks && tree.FruitCount < tree.MaxFruit {
			tree.FruitCount++
			tree.GrowthProgress = 0
			tree.DropTimer = 0 // Reset drop timer when new fruit grows

			// Emit influence event for deterministic sync
			zoneID := ""
			if state.CurrentZone != nil {
				zoneID = state.CurrentZone.ZoneID
			}
			state.AddInfluenceEvent(zoneID, InfluenceTreeFruitGrow, "",
				tree.GridX, tree.GridY, tree.TreeID, tree.FruitCount)
		}

		// Fruit drop (overripe)
		if tree.FruitCount > 0 {
			tree.DropTimer++
			if tree.DropTimer >= treeDef.World.FruitDropTicks {
				tree.FruitCount--
				tree.DropTimer = 0

				// Drop fruit on ground (will eventually rot)
				m.dropFruitFromTree(dispatcher, state, tree, treeDef.World.FruitType, logger)
			}
		}
	}
}

// dropFruitFromTree creates a ground item that will decay
func (m *Match) dropFruitFromTree(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	tree *entities.FruitTreeState,
	fruitType string,
	logger runtime.Logger,
) {
	cx, cy, _, _ := GlobalToChunk(tree.GridX, tree.GridY)
	cs := float32(state.Config.ChunkSize)

	// Create ground item with slight offset from tree
	itemID := fmt.Sprintf("fruit_%d_%d_%d", tree.GridX, tree.GridY, time.Now().UnixNano())
	worldX := float32(tree.GridX) + 0.5 + (rand.Float32()-0.5)*0.8
	worldY := float32(tree.GridY) + 0.5 + (rand.Float32()-0.5)*0.8
	localX := worldX - float32(cx)*cs
	localY := worldY - float32(cy)*cs

	groundItem := &entities.GroundItem{
		ID:       itemID,
		ItemType: fruitType, // "apple", "orange"
		Count:    1,
		Position: entities.EntityPosition{
			ChunkX: cx,
			ChunkY: cy,
			LocalX: localX,
			LocalY: localY,
		},
		Lifetime: 16800, // ~28 minutes at 10Hz (time until rot)
		DecaysTo: "rotten_" + fruitType,
	}
	state.GroundItems[itemID] = groundItem

	// Emit influence event
	zoneID := ""
	if state.CurrentZone != nil {
		zoneID = state.CurrentZone.ZoneID
	}
	state.AddInfluenceEvent(zoneID, InfluenceTreeFruitDrop, "",
		tree.GridX, tree.GridY, tree.TreeID, 0)

	// Broadcast spawn
	spawnMsg := GroundItemSpawnMessage{
		ID:       itemID,
		ItemType: fruitType,
		Count:    1,
		X:        worldX,
		Y:        worldY,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)

	logger.Debug("Fruit dropped from tree at %d,%d: %s", tree.GridX, tree.GridY, fruitType)
}

// processGroundItemDecay handles fresh -> rotten transitions
func (m *Match) processGroundItemDecay(state *WorldState, dispatcher runtime.MatchDispatcher) {
	tickDelta := 0.1 // 10Hz = 0.1 seconds per tick

	for itemID, item := range state.GroundItems {
		// Skip items that don't decay
		if item.DecaysTo == "" {
			// Check normal lifetime despawn
			item.Lifetime -= float32(tickDelta)
			if item.Lifetime <= 0 {
				m.removeGroundItem(state, dispatcher, itemID, item)
			}
			continue
		}

		// Decay timer
		item.Lifetime -= float32(tickDelta)
		if item.Lifetime <= 0 {
			// Transform to rotten version
			oldType := item.ItemType
			item.ItemType = item.DecaysTo // "apple" -> "rotten_apple"
			item.DecaysTo = ""            // No further decay
			item.FoodValue = 100          // Flies can eat this
			item.Lifetime = 999999        // No more time decay

			// Emit influence event (fly AI now targets this)
			zoneID := ""
			if state.CurrentZone != nil {
				zoneID = state.CurrentZone.ZoneID
			}
			state.AddInfluenceEvent(zoneID, InfluenceItemRotted, "",
				int(item.Position.LocalX), int(item.Position.LocalY), itemID, 0)

			// Broadcast visual update (remove old, spawn new)
			cx, cy := item.Position.ChunkX, item.Position.ChunkY
			cs := float32(state.Config.ChunkSize)
			worldX := float32(cx)*cs + item.Position.LocalX
			worldY := float32(cy)*cs + item.Position.LocalY

			removeMsg := GroundItemRemoveMessage{ID: itemID}
			m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemRemove, removeMsg)

			spawnMsg := GroundItemSpawnMessage{
				ID:       itemID,
				ItemType: item.ItemType,
				Count:    item.Count,
				X:        worldX,
				Y:        worldY,
			}
			m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)

			_ = oldType // suppress unused warning
		}
	}
}

// removeGroundItem removes a ground item and broadcasts removal
func (m *Match) removeGroundItem(
	state *WorldState,
	dispatcher runtime.MatchDispatcher,
	itemID string,
	item *entities.GroundItem,
) {
	cx, cy := item.Position.ChunkX, item.Position.ChunkY
	delete(state.GroundItems, itemID)

	removeMsg := GroundItemRemoveMessage{ID: itemID}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemRemove, removeMsg)
}

// initFruitTreesInChunk scans a loaded chunk for fruit trees and creates states
func (m *Match) initFruitTreesInChunk(
	state *WorldState,
	chunk *ChunkData,
	cx, cy int,
	logger runtime.Logger,
) {
	chunkSize := state.Config.ChunkSize

	for ly := 0; ly < chunkSize; ly++ {
		for lx := 0; lx < chunkSize; lx++ {
			cell, _ := chunk.GetOccupantCell(lx, ly)
			if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
				continue
			}

			entityDef := state.Entities[cell.Occupant.ID]
			if entityDef == nil || entityDef.World == nil {
				continue
			}

			// Check if this is a fruit tree
			if entityDef.World.FruitType == "" {
				continue
			}

			// Calculate global coordinates
			gx := cx*chunkSize + lx
			gy := cy*chunkSize + ly
			treeKey := fmt.Sprintf("%d,%d", gx, gy)

			// Skip if already registered
			if state.FruitTreeStates[treeKey] != nil {
				continue
			}

			// Create fruit tree state
			maxFruit := entityDef.World.MaxFruit
			if maxFruit == 0 {
				maxFruit = 5
			}

			tree := &entities.FruitTreeState{
				TreeID:   fmt.Sprintf("tree_%d_%d", gx, gy),
				GridX:    gx,
				GridY:    gy,
				MaxFruit: maxFruit,
				// Start with some random fruit and progress
				FruitCount:     rand.Intn(maxFruit + 1),
				GrowthProgress: rand.Intn(entityDef.World.FruitGrowTicks / 2),
			}
			state.FruitTreeStates[treeKey] = tree

			logger.Debug("Initialized fruit tree at %d,%d (%s) with %d fruit",
				gx, gy, entityDef.World.FruitType, tree.FruitCount)
		}
	}
}
