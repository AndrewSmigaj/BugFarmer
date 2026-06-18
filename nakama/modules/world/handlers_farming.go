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
// Fruit tree tuning. A tree's tank holds 3 waterings (max 1 manual/day; rain adds 1 free)
// and a FULL tank buys exactly ONE batch of MaxFruit — triggered only when the tree is
// EMPTY, so a banked tank is never wasted on a partial batch. Without water a tree grows
// NO new fruit — the brake on infinite fly food. Ripe fruit falls only during the evening
// window, staggered >= treeFallSpacingTicks apart (you watch the tree shed).
const (
	treeTankCap          = 3
	treeFallSpacingTicks = 500
	treeEveningStart     = 0.40 // ~15:30 on the clock (t of the 8400-tick day)
	treeEveningEnd       = 0.62 // ~21:00
)

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
		logger.Warn("ToolUse: player %s not found", userID)
		return
	}

	toolID := player.EquippedTool
	logger.Info("ToolUse received from %s: grid(%d,%d), equipped=%s", userID, msg.GridX, msg.GridY, toolID)
	if toolID == "" {
		m.sendWorldError(dispatcher, state, userID, "No tool equipped")
		return
	}

	toolDef := state.Entities[toolID]
	if toolDef == nil {
		logger.Warn("ToolUse: toolDef for %s not found in Entities", toolID)
		m.sendWorldError(dispatcher, state, userID, "Unknown tool")
		return
	}

	logger.Info("ToolUse: tool %s has type=%s", toolID, toolDef.ToolType)

	// Route based on tool type
	switch toolDef.ToolType {
	case "hoe":
		m.handleHoe(logger, dispatcher, state, userID, msg.GridX, msg.GridY, tick)
	case "watering_can":
		m.handleWatering(logger, dispatcher, state, userID, msg.GridX, msg.GridY, tick)
	case "scythe":
		m.handleScythe(logger, dispatcher, state, userID, msg.GridX, msg.GridY, tick)
	default:
		m.sendWorldError(dispatcher, state, userID, "Use left-click for this tool")
	}
}

// validateCooldownTicks is THE cooldown gate: one body enforcing the shared LastToolTick
// invariant (farming tools, weapon moves — sword<->hoe<->jab all throttle each other,
// which closes alternating-spam and the weapon-swap bypass). Stamps ONLY on success.
// cooldownTicks <= 0 falls back to the 3-tick default (0.3s at 10Hz).
func (m *Match) validateCooldownTicks(player *PlayerState, tick int64, cooldownTicks int) bool {
	cooldown := int64(cooldownTicks)
	if cooldown <= 0 {
		cooldown = 3
	}
	if tick-player.LastToolTick < cooldown {
		return false
	}
	player.LastToolTick = tick
	return true
}

// validateToolCooldown checks the equipped tool's top-level cooldown (farming tools).
// Thin delegate over validateCooldownTicks — weapons use their per-MOVE cooldowns.
func (m *Match) validateToolCooldown(state *WorldState, player *PlayerState, tick int64) bool {
	toolDef := state.Entities[player.EquippedTool]
	if toolDef == nil {
		return true // No tool = no cooldown (and no stamp)
	}
	return m.validateCooldownTicks(player, tick, toolDef.CooldownTicks)
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
		logger.Debug("Hoe: cooldown not passed for %s", userID)
		return
	}

	// Get chunk and local coords
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		logger.Warn("Hoe: chunk %s not loaded for gx=%d, gy=%d", chunkKey, gx, gy)
		m.sendWorldError(dispatcher, state, userID, "Chunk not loaded")
		return
	}

	// Get tile at position
	tile := chunk.GetGroundTile(lx, ly)
	logger.Debug("Hoe: tile at (%d,%d) = %s", gx, gy, tile)
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

	// Broadcast WorldUpdate with new ground tile (no occupant change)
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, gx, gy, newTile, nil, false)

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
		// Not a crop — a FRUIT TREE? Trees fill a 3-watering tank (one manual watering
		// per day) that buys one full fruit batch. Without water, flies are finite.
		if tree := state.FruitTreeStates[cropKey]; tree != nil {
			if ok, errMsg := waterTree(state, tree, true); !ok {
				m.sendWorldError(dispatcher, state, userID, errMsg)
				return
			}
			slot.Metadata["uses"]--
			m.sendSlotUpdate(dispatcher, state, userID, slotIndex, slot)
			m.broadcastTreeWaterUpdate(dispatcher, state, tree)
			logger.Debug("Player %s watered tree at %d,%d (tank=%d/%d)",
				userID, gx, gy, tree.WaterLevel, treeTankCap)
			return
		}
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

	// Change ground tile to wet variant for visual feedback (no occupant change)
	if tile == "garden_plot" {
		chunk.Ground[ly][lx] = "garden_plot_wet"
		m.broadcastWorldUpdate(dispatcher, state, cx, cy, gx, gy, "garden_plot_wet", nil, false)
	}

	// Send updates
	m.sendSlotUpdate(dispatcher, state, userID, slotIndex, slot)
	m.broadcastCropUpdate(dispatcher, state, gx, gy, crop)

	logger.Debug("Player %s watered crop at %d,%d (water=%d)", userID, gx, gy, crop.Water)
}

// handleTreeHarvest (OpCode 92): hands-pick ONE fruit from the tree at (gx, gy) into the
// player's inventory. Full inventory = error with NO decrement; fruit in a slot is inert
// (never rots). Display rides the 93 broadcast.
func (m *Match) handleTreeHarvest(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg TreeHarvestMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	tree := state.FruitTreeStates[fmt.Sprintf("%d,%d", msg.GX, msg.GY)]
	if tree == nil {
		m.sendWorldError(dispatcher, state, userID, "No fruit tree here")
		return
	}

	// Range: client checks 2.5, server allows 3.0 for latency (the pickup convention)
	cs := state.Config.ChunkSize
	dx := player.WorldX(cs) - (float32(tree.GridX) + 0.5)
	dy := player.WorldY(cs) - (float32(tree.GridY) + 0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	if tree.FruitCount <= 0 {
		m.sendWorldError(dispatcher, state, userID, "No fruit on the tree")
		return
	}

	fruitType := ""
	if def := state.Entities[tree.EntityID]; def != nil && def.World != nil {
		fruitType = def.World.FruitType
	}
	if fruitType == "" {
		return
	}

	slotIndex := player.AddItem(fruitType, 1)
	if slotIndex < 0 {
		m.sendWorldError(dispatcher, state, userID, "Inventory full")
		return // fruit stays on the tree
	}

	tree.FruitCount--
	tree.LastHarvestTick = state.TickCount
	m.sendSlotUpdate(dispatcher, state, userID, slotIndex, &player.ItemSlots[slotIndex])
	m.broadcastTreeFruitUpdate(dispatcher, state, tree, fruitType)
	logger.Debug("Player %s picked %s from tree at %d,%d (%d left)",
		userID, fruitType, tree.GridX, tree.GridY, tree.FruitCount)
}

// treeDefDropTicks reads a tree def's ripeness threshold with a sane floor (rand.Intn
// panics on 0 — a def without fruit_drop_ticks must not crash wild init).
func treeDefDropTicks(def *EntityDef) int {
	if def != nil && def.World != nil && def.World.FruitDropTicks > 0 {
		return def.World.FruitDropTicks
	}
	return 4200
}

// waterTree pours one watering into the tree's tank. Manual waterings are capped at one
// per APPARENT day; rain (manual=false) skips the daily stamp and clamps silently.
// The daily gate is `LastWaterDay == currentDay` — equality, NOT >= — so a debug
// set-time jumping the day index BACKWARD can never block watering for days.
func waterTree(state *WorldState, tree *entities.FruitTreeState, manual bool) (bool, string) {
	if tree.WaterLevel >= treeTankCap {
		if manual {
			return false, "The tree is well watered"
		}
		return false, ""
	}
	if manual {
		currentDay := (state.TickCount + state.DayOffsetTicks) / DayLengthTicks
		if tree.LastWaterDay == currentDay {
			return false, "Already watered today"
		}
		tree.LastWaterDay = currentDay
	}
	tree.WaterLevel++
	return true, ""
}

// inEveningWindow reports whether the APPARENT time of day sits in the fruit-fall window.
func inEveningWindow(state *WorldState) bool {
	t := float64((state.TickCount+state.DayOffsetTicks)%DayLengthTicks) / float64(DayLengthTicks)
	return t >= treeEveningStart && t < treeEveningEnd
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
	// DEBUG: Log entry and validate parameters
	if crop == nil {
		// This would cause a nil pointer dereference - log and return safely
		return
	}

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

	// Harvest attempt (hand-click). The scythe uses the same helper over a 3x3 area.
	matureStage := cropDef.GrowthStages - 1
	if crop.Stage < matureStage {
		m.sendWorldError(dispatcher, state, userID, "Crop is not ready")
		return
	}
	m.harvestMatureCrop(logger, dispatcher, state, userID, msg.GridX, msg.GridY)
}

// harvestMatureCrop harvests the crop at (gx,gy) IF it is mature: spawns produce + seed
// chance, then multi-harvest-resets or removes the plant. Returns true if harvested.
// Shared by hand-clicking (handlePlantInteract) and the scythe's area swing.
func (m *Match) harvestMatureCrop(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	gx, gy int,
) bool {
	cropKey := fmt.Sprintf("%d,%d", gx, gy)
	crop := state.CropStates[cropKey]
	if crop == nil {
		return false
	}
	cropDef := state.CropDefs[crop.PlantType]
	if cropDef == nil {
		return false
	}
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	if state.Chunks[ChunkKey(cx, cy)] == nil {
		return false
	}
	if crop.Stage < cropDef.GrowthStages-1 {
		return false // not mature
	}

	// Calculate drops
	dropCount := cropDef.HarvestCountMin
	if cropDef.HarvestCountMax > cropDef.HarvestCountMin {
		dropCount += rand.Intn(cropDef.HarvestCountMax - cropDef.HarvestCountMin + 1)
	}

	// Spawn harvest items on ground
	m.spawnHarvestDrops(dispatcher, state, cropDef.HarvestItem, dropCount, gx, gy, cx, cy)

	// Seed drop chance
	if cropDef.SeedDropChance > 0 && rand.Float32() < cropDef.SeedDropChance {
		seedID := "seed_" + crop.PlantType
		m.spawnHarvestDrops(dispatcher, state, seedID, 1, gx, gy, cx, cy)
	}

	// Handle multi-harvest vs single-harvest
	if cropDef.MultiHarvest && crop.HarvestsRemaining > 1 {
		// Multi-harvest: reset to earlier stage, decrement remaining
		crop.HarvestsRemaining--
		crop.Stage = 1 // Reset to sprout stage
		crop.Water = 0 // Reset water
		m.broadcastCropUpdate(dispatcher, state, gx, gy, crop)
		logger.Debug("Player %s harvested %s (multi), %d harvests remaining",
			userID, crop.PlantType, crop.HarvestsRemaining)
	} else {
		// Single harvest or last harvest: remove crop
		m.destroyCrop(logger, dispatcher, state, crop, cropKey, cx, cy, lx, ly)
		logger.Debug("Player %s harvested %s (final)", userID, crop.PlantType)
	}
	return true
}

// handleScythe: the scythe's perk over hand-harvesting — one swing harvests every MATURE
// crop in the 3x3 around the target cell (immature crops are untouched; no destroy risk).
func (m *Match) handleScythe(
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
	if !m.validateToolCooldown(state, player, tick) {
		return
	}

	harvested := 0
	for dy := -1; dy <= 1; dy++ {
		for dx := -1; dx <= 1; dx++ {
			if m.harvestMatureCrop(logger, dispatcher, state, userID, gx+dx, gy+dy) {
				harvested++
			}
		}
	}
	if harvested == 0 {
		m.sendWorldError(dispatcher, state, userID, "Nothing ready to scythe")
	} else {
		logger.Debug("Player %s scythed %d crops around %d,%d", userID, harvested, gx, gy)
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

	// Broadcast removal (clear occupant)
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, crop.GridX, crop.GridY, "", nil, true)
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
	// DEBUG: Log if CropStates is not empty (only occasionally to reduce spam)
	cropCount := len(state.CropStates)

	for cropKey, crop := range state.CropStates {
		// DEBUG: Validate crop is not nil
		if crop == nil {
			// ERROR: nil crop in CropStates - this shouldn't happen
			continue
		}

		cropDef := state.CropDefs[crop.PlantType]
		if cropDef == nil {
			// DEBUG: Log when cropDef lookup fails
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

	// Suppress unused warning
	_ = cropCount
}

// processFruitTrees handles fruit growth and natural dropping
func (m *Match) processFruitTrees(
	state *WorldState,
	dispatcher runtime.MatchDispatcher,
	logger runtime.Logger,
) {
	// Collect keys to delete after iteration to avoid map modification during range
	var toDelete []string

	for treeKey, tree := range state.FruitTreeStates {
		// Get tree entity definition
		cx, cy, lx, ly := GlobalToChunk(tree.GridX, tree.GridY)
		chunk := state.Chunks[ChunkKey(cx, cy)]
		if chunk == nil {
			continue
		}

		cell, _ := chunk.GetOccupantCell(lx, ly)
		if cell.IsEmpty || cell.Occupant == nil {
			// Tree was removed, mark for cleanup
			toDelete = append(toDelete, treeKey)
			continue
		}

		treeDef := state.Entities[cell.Occupant.ID]
		if treeDef == nil || treeDef.World == nil || treeDef.World.FruitType == "" {
			continue // Not a fruit tree
		}

		// 1) BATCH TRIGGER — only when the tree is EMPTY: a full tank buys exactly one
		// full batch of MaxFruit. The FruitCount==0 guard closes two holes: a fruited
		// tree can't eat the tank for nothing, and a banked tank can't auto-fire a
		// 1-fruit "batch" the instant a single fruit leaves. Evening falls empty trees
		// nightly, so a banked tank waits at most ~a day.
		if tree.WaterLevel >= treeTankCap && tree.PendingGrowth == 0 && tree.FruitCount == 0 {
			tree.WaterLevel = 0
			tree.PendingGrowth = tree.MaxFruit
			tree.GrowthProgress = 0
			m.broadcastTreeWaterUpdate(dispatcher, state, tree)
			logger.Debug("Tree at %d,%d starts a batch of %d", tree.GridX, tree.GridY, tree.MaxFruit)
		}

		// 2) GROWTH — Pending counts DOWN, one fruit per FruitGrowTicks. The ripeness
		// clock (DropTimer) resets ONLY on the 0->1 transition: a fresh batch gets its
		// full shelf life; later fruit shares the batch's clock (mixed-age canopies
		// approximate — documented).
		if tree.PendingGrowth > 0 {
			tree.GrowthProgress++
			if tree.GrowthProgress >= treeDef.World.FruitGrowTicks && tree.FruitCount < tree.MaxFruit {
				if tree.FruitCount == 0 {
					tree.DropTimer = 0
				}
				tree.FruitCount++
				tree.PendingGrowth--
				tree.GrowthProgress = 0

				// Influence event kept for the ledger (clients display via OpCode 93)
				zoneID := ""
				if state.CurrentZone != nil {
					zoneID = state.CurrentZone.ZoneID
				}
				state.AddInfluenceEvent(zoneID, InfluenceTreeFruitGrow, "",
					tree.GridX, tree.GridY, tree.TreeID, tree.FruitCount)
				m.broadcastTreeFruitUpdate(dispatcher, state, tree, treeDef.World.FruitType)
			}
		}

		// 3) EVENING FALLS — ripe fruit drops one at a time, >= treeFallSpacingTicks
		// apart, only inside the evening window (you watch the tree shed into dusk).
		// DropTimer is NOT reset by falls: once the batch is ripe, the whole canopy
		// sheds across evenings until empty.
		if tree.FruitCount > 0 {
			tree.DropTimer++
			if tree.DropTimer >= treeDef.World.FruitDropTicks &&
				inEveningWindow(state) &&
				state.TickCount-tree.LastFallTick >= treeFallSpacingTicks {
				tree.FruitCount--
				tree.LastFallTick = state.TickCount
				m.dropFruitFromTree(dispatcher, state, tree, treeDef.World.FruitType, logger)
				m.broadcastTreeFruitUpdate(dispatcher, state, tree, treeDef.World.FruitType)
			}
		}
	}

	// Clean up removed trees after iteration
	for _, key := range toDelete {
		delete(state.FruitTreeStates, key)
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

	// Drop position: scattered BESIDE and IN FRONT (south) of the trunk — never on the
	// trunk cell itself, where the canopy y-sorts over the apple and hides it.
	itemID := fmt.Sprintf("fruit_%d_%d_%d", tree.GridX, tree.GridY, time.Now().UnixNano())
	side := float32(1)
	if rand.Float32() < 0.5 {
		side = -1
	}
	worldX := float32(tree.GridX) + 0.5 + side*(0.7+rand.Float32()*0.9) // 0.7-1.6 cells to a side
	worldY := float32(tree.GridY) + 0.2 - rand.Float32()*1.2           // at/below the trunk = in front
	localX := worldX - float32(cx)*cs
	localY := worldY - float32(cy)*cs

	// Rot time is data-driven per tree (world.fruit_rot_ticks; default 16800 ticks = 2 game-days
	// = 28 min). NOTE Lifetime is in SECONDS (decremented by 0.1/tick) — convert ticks/10.
	// (The old hardcoded value treated 16800 as seconds → fruit took ~4.7h to rot. Units fixed.)
	rotTicks := 16800
	if treeDef := state.Entities[tree.EntityID]; treeDef != nil && treeDef.World != nil && treeDef.World.FruitRotTicks > 0 {
		rotTicks = treeDef.World.FruitRotTicks
	}

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
		Lifetime: float32(rotTicks) * 0.1, // seconds until rot
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

	// Collect items to remove after iteration to avoid map modification during range
	type itemToRemove struct {
		id   string
		item *entities.GroundItem
	}
	var toRemove []itemToRemove

	for itemID, item := range state.GroundItems {
		// Skip items that don't decay
		if item.DecaysTo == "" {
			// Check normal lifetime despawn
			item.Lifetime -= float32(tickDelta)
			if item.Lifetime <= 0 {
				toRemove = append(toRemove, itemToRemove{itemID, item})
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

			// Emit food-registry event (fly AI now targets this). WORLD cells + FoodID + level
			// (the old emission used chunk-LOCAL coords and stuffed the id in swarm_id — fixed).
			zoneID := ""
			if state.CurrentZone != nil {
				zoneID = state.CurrentZone.ZoneID
			}
			wcx := item.Position.ChunkX*state.Config.ChunkSize + int(item.Position.LocalX)
			wcy := item.Position.ChunkY*state.Config.ChunkSize + int(item.Position.LocalY)
			state.AddFoodEvent(zoneID, InfluenceItemRotted, itemID, wcx, wcy, item.FoodValue)

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

	// Remove expired items after iteration
	for _, r := range toRemove {
		m.removeGroundItem(state, dispatcher, r.id, r.item)
	}
}

// initStationsInChunk scans a loaded chunk for station occupants (entities with world.station —
// compost bins etc.) and registers their states. Mirrors initFruitTreesInChunk.
func (m *Match) initStationsInChunk(
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
			if entityDef == nil || entityDef.World == nil || entityDef.World.Station == nil {
				continue
			}

			gx := cx*chunkSize + lx
			gy := cy*chunkSize + ly
			key := entities.StationKey(gx, gy)
			if state.Stations[key] != nil {
				continue
			}

			state.Stations[key] = &entities.StationState{
				Key:      key,
				EntityID: cell.Occupant.ID,
				GridX:    gx,
				GridY:    gy,
				Fill:     0,
			}
			logger.Debug("Initialized station %s (%s) at %d,%d", key, cell.Occupant.ID, gx, gy)
		}
	}
}

// handleStationDeposit processes a player depositing one inventory item into a station
// (OpCode 85). Validates the item is accepted + capacity remains, consumes it from the
// player's inventory, raises the fill meter, and publishes BOTH a display update (OpCode 86)
// and a deterministic food-registry event (FOOD_CONSUMED with the new level — level semantics:
// the registry just sets FoodID -> level; deposits move it UP, feeding moves it DOWN).
func (m *Match) handleStationDeposit(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg StationDepositMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	key := entities.StationKey(msg.GX, msg.GY)
	st := state.Stations[key]
	if st == nil {
		m.sendWorldError(dispatcher, state, userID, "No station there")
		return
	}
	def := state.Entities[st.EntityID]
	if def == nil || def.World == nil || def.World.Station == nil {
		return
	}
	sd := def.World.Station

	// Range check (same allowance as pickup: 3.0 server-side)
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	// Accepted item?
	accepted := false
	for _, a := range sd.Accepts {
		if a == msg.ItemID {
			accepted = true
			break
		}
	}
	if !accepted {
		m.sendWorldError(dispatcher, state, userID, "Can't compost that")
		return
	}

	capacity := sd.Capacity
	if capacity <= 0 {
		capacity = 10
	}
	// Deposits land in the INPUT hopper (processing converts them to compost over time)
	if st.InputCount >= capacity {
		m.sendWorldError(dispatcher, state, userID, "The hopper is full")
		return
	}

	// Consume one from the player's inventory
	slot := player.FindItem(msg.ItemID)
	if slot < 0 || !player.RemoveItem(slot, 1) {
		m.sendWorldError(dispatcher, state, userID, "You don't have that")
		return
	}

	st.InputCount++

	// Per-player inventory update
	slotMsg := SlotUpdateMessage{
		SlotIndex: slot,
		ItemID:    player.ItemSlots[slot].ItemID,
		Count:     player.ItemSlots[slot].Count,
	}
	slotData, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
	}

	// Display meter update (on-receipt, UI only). The deterministic FOOD event comes when a
	// unit finishes PROCESSING (processStations), not on deposit — raw input isn't food yet.
	m.broadcastStationUpdate(dispatcher, st, capacity)

	logger.Debug("Player %s deposited %s into %s (input %d/%d, compost %d)", userID, msg.ItemID, key, st.InputCount, capacity, st.Fill)
}

// broadcastTreeWaterUpdate sends a tree's water state (display-only — drives the client's
// droplet indicator; bug AI doesn't read tree water).
func (m *Match) broadcastTreeWaterUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, tree *entities.FruitTreeState) {
	cx, cy, _, _ := GlobalToChunk(tree.GridX, tree.GridY)
	msg := TreeWaterUpdateMessage{
		GridX: tree.GridX, GridY: tree.GridY,
		WaterLevel:    tree.WaterLevel,
		PendingGrowth: tree.PendingGrowth,
		LastWaterDay:  tree.LastWaterDay,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeTreeWaterUpdate, msg)
}

// broadcastTreeFruitUpdate sends a tree's fruit count (OpCode 93, display-only): drives
// the canopy fruit overlay. The droplet twin's pattern: on change + chunk-subscribe re-send.
func (m *Match) broadcastTreeFruitUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, tree *entities.FruitTreeState, fruitType string) {
	cx, cy, _, _ := GlobalToChunk(tree.GridX, tree.GridY)
	msg := TreeFruitUpdateMessage{
		GridX: tree.GridX, GridY: tree.GridY,
		FruitCount: tree.FruitCount,
		FruitType:  fruitType,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeTreeFruitUpdate, msg)
}

// broadcastStationUpdate sends the display meters (input + compost fill) for a station.
func (m *Match) broadcastStationUpdate(dispatcher runtime.MatchDispatcher, st *entities.StationState, capacity int) {
	updMsg := StationUpdateMessage{GX: st.GridX, GY: st.GridY, Input: st.InputCount, Fill: st.Fill, Capacity: capacity}
	updData, _ := json.Marshal(updMsg)
	dispatcher.BroadcastMessage(OpCodeStationUpdate, updData, nil, nil, true)
}

// processStations advances every station's INPUT -> OUTPUT conversion (the material-processor
// loop: one input unit becomes one compost unit every process_ticks). Newly produced compost
// raises the station's food level on the deterministic ledger (bugs start targeting it).
func (m *Match) processStations(state *WorldState, dispatcher runtime.MatchDispatcher) {
	for key, st := range state.Stations {
		if st.InputCount <= 0 {
			st.ProcessProgress = 0
			continue
		}
		def := state.Entities[st.EntityID]
		if def == nil || def.World == nil || def.World.Station == nil {
			continue
		}
		sd := def.World.Station
		capacity := sd.Capacity
		if capacity <= 0 {
			capacity = 10
		}
		if st.Fill >= capacity {
			continue // output full — processing stalls until bugs eat some compost
		}
		processTicks := sd.ProcessTicks
		if processTicks <= 0 {
			processTicks = 300 // default: 30s per unit at 10Hz
		}

		st.ProcessProgress++
		if st.ProcessProgress < processTicks {
			continue
		}
		st.ProcessProgress = 0
		st.InputCount--
		st.Fill++

		m.broadcastStationUpdate(dispatcher, st, capacity)

		// Deterministic food registry: compost level rose
		foodPerUnit := sd.FoodPerUnit
		if foodPerUnit <= 0 {
			foodPerUnit = 100
		}
		level := st.Fill*foodPerUnit - int(st.FoodFrac)
		if state.CurrentZone != nil {
			state.AddFoodEvent(state.CurrentZone.ZoneID, InfluenceFoodConsumed, key, st.GridX, st.GridY, level)
		}
	}
}

// foodSourceAlive reports whether a depletable food source still exists with food left.
// fx,fy are the target's world position — needed for host-plant occupants (milkweed), which are
// depletable food keyed by position (not a unique item/station id).
func (m *Match) foodSourceAlive(state *WorldState, foodID string, fx, fy float32) bool {
	if item, ok := state.GroundItems[foodID]; ok {
		return item.FoodValue > 0
	}
	if st, ok := state.Stations[foodID]; ok {
		return st.Fill > 0
	}
	// Host-plant occupant (milkweed): "alive" as a breeding source while it has capacity. Without
	// this, a depletable milkweed target is cleared every tick (it's neither item nor station), so a
	// reproducing butterfly can never park on it to breed.
	if hp := state.HostPlantStates[fmt.Sprintf("%d,%d", int(fx), int(fy))]; hp != nil {
		return hp.Capacity > 0
	}
	// Flower nectar pool (depletable FEEDING source): alive while it has nectar; grazed-out flowers are
	// cleared as a target so a starving bug re-thinks instead of camping a dry flower.
	if fp := state.ForagePools[fmt.Sprintf("%d,%d", int(fx), int(fy))]; fp != nil {
		return fp.Nectar > 0
	}
	return false
}

// consumeFood drains `amount` (fractional food units) from a depletable source — a rotten
// ground item's FoodValue or a station's fill. Emits FOOD_CONSUMED on each 25-point threshold
// crossing (75/50/25/0) so clients keep a coarse deterministic registry; at 0 a ground item is
// removed from the world (stations keep their occupant, just empty).
func (m *Match) consumeFood(state *WorldState, dispatcher runtime.MatchDispatcher, foodID string, amount float32) {
	if amount <= 0 {
		return
	}
	zoneID := ""
	if state.CurrentZone != nil {
		zoneID = state.CurrentZone.ZoneID
	}
	cs := state.Config.ChunkSize

	crossed := func(old, new int) bool {
		for _, t := range [...]int{75, 50, 25, 0} {
			if old > t && new <= t {
				return true
			}
		}
		return false
	}

	if item, ok := state.GroundItems[foodID]; ok && item.FoodValue > 0 {
		item.FoodFrac += amount
		whole := int(item.FoodFrac)
		if whole <= 0 {
			return
		}
		item.FoodFrac -= float32(whole)
		old := item.FoodValue
		item.FoodValue -= whole
		if item.FoodValue < 0 {
			item.FoodValue = 0
		}
		if crossed(old, item.FoodValue) {
			wcx := item.Position.ChunkX*cs + int(item.Position.LocalX)
			wcy := item.Position.ChunkY*cs + int(item.Position.LocalY)
			state.AddFoodEvent(zoneID, InfluenceFoodConsumed, foodID, wcx, wcy, item.FoodValue)
		}
		if item.FoodValue == 0 {
			delete(state.GroundItems, foodID)
			removeMsg := GroundItemRemoveMessage{ID: foodID}
			m.broadcastToChunk(dispatcher, state, item.Position.ChunkX, item.Position.ChunkY, OpCodeGroundItemRemove, removeMsg)
		}
		return
	}

	if st, ok := state.Stations[foodID]; ok && st.Fill > 0 {
		def := state.Entities[st.EntityID]
		foodPerUnit := 100
		if def != nil && def.World != nil && def.World.Station != nil && def.World.Station.FoodPerUnit > 0 {
			foodPerUnit = def.World.Station.FoodPerUnit
		}
		levelOf := func() int {
			l := st.Fill*foodPerUnit - int(st.FoodFrac)
			if l < 0 {
				l = 0
			}
			return l
		}
		oldLevel := levelOf()
		st.FoodFrac += amount
		for st.FoodFrac >= float32(foodPerUnit) && st.Fill > 0 {
			st.FoodFrac -= float32(foodPerUnit)
			st.Fill--
		}
		if st.Fill == 0 {
			st.FoodFrac = 0
		}
		newLevel := levelOf()
		if crossed(oldLevel, newLevel) {
			state.AddFoodEvent(zoneID, InfluenceFoodConsumed, foodID, st.GridX, st.GridY, newLevel)
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

	// An EDIBLE item leaving the world MUST clear the deterministic food registry.
	// This path is reached by LIFETIME EXPIRY — and carrion (bug_parts, food_value 10,
	// Lifetime 60s) is the first edible item that expires. Without this event every
	// uneaten corpse leaves a permanent phantom registry entry on all live clients
	// (flies eternally landing on bare ground) and a joiner-vs-veteran hash-resync
	// loop. Pickup and eat-to-zero already emit it; expiry didn't (unreachable until
	// carrion existed).
	if item.FoodValue > 0 && state.CurrentZone != nil {
		cs := state.Config.ChunkSize
		wcx := cx*cs + int(item.Position.LocalX)
		wcy := cy*cs + int(item.Position.LocalY)
		state.AddFoodEvent(state.CurrentZone.ZoneID, InfluenceFoodConsumed, itemID, wcx, wcy, 0)
	}

	removeMsg := GroundItemRemoveMessage{ID: itemID}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemRemove, removeMsg)
}

// initFruitTreesInChunk scans a loaded chunk for fruit trees and creates states
// --- Host plants (milkweed): depletable butterfly breeding sites ---

const (
	maxHostCapacity  = 100.0
	hostRegenPerTick = 0.012 // ~0.12/s → ~830s to refill: throttles butterfly BIRTHS so the population
	// settles below the hard cap (breeding-food-limited) instead of pinning it.
	hostBreedCost = 40.0 // capacity drained per butterfly breed event (≈2-3 breeds to exhaust the host)
)

// initHostPlantsInChunk registers milkweed (world.host_plant) occupants in a loaded chunk at full
// breeding capacity. Mirrors initFruitTreesInChunk; idempotent.
func (m *Match) initHostPlantsInChunk(state *WorldState, chunk *ChunkData, cx, cy int, logger runtime.Logger) {
	chunkSize := state.Config.ChunkSize
	for ly := 0; ly < chunkSize; ly++ {
		for lx := 0; lx < chunkSize; lx++ {
			cell, _ := chunk.GetOccupantCell(lx, ly)
			if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
				continue
			}
			def := state.Entities[cell.Occupant.ID]
			if def == nil || def.World == nil || !def.World.HostPlant {
				continue
			}
			gx, gy := cx*chunkSize+lx, cy*chunkSize+ly
			key := fmt.Sprintf("%d,%d", gx, gy)
			if state.HostPlantStates[key] != nil {
				continue
			}
			state.HostPlantStates[key] = &entities.HostPlantState{
				EntityID: cell.Occupant.ID, GridX: gx, GridY: gy, Capacity: maxHostCapacity,
			}
		}
	}
}

// processHostPlants regrows host-plant breeding capacity each tick (a grazed-out milkweed slowly
// becomes breedable again). Server-only soft state.
func (m *Match) processHostPlants(state *WorldState) {
	regen := float32(hostRegenPerTick)
	if state.DroughtUntilTick > state.TickCount {
		regen *= droughtFoodRegenMult // drought: milkweed regrows slower → fewer butterfly births
	}
	for _, hp := range state.HostPlantStates {
		if hp.Capacity < maxHostCapacity {
			hp.Capacity += regen
			if hp.Capacity > maxHostCapacity {
				hp.Capacity = maxHostCapacity
			}
		}
	}
}

// --- Forage pools (flower nectar): depletable FEEDING food (the boom-bust engine) ---

const (
	maxNectar          = 100.0
	nectarRegenPerTick = 0.012 // ~0.12/s → ~830s to refill (slow regen =
	// bigger, slower oscillation — this is the master boom-bust dial, tuned on the population graph).

	// During a Director DROUGHT, ALL plant food regrows far slower (flowers give less nectar, milkweed
	// regrows slower) — so a drought brakes the NECTAR/HOST-fed populations (butterflies) via FOOD, the
	// same way it brakes the fruit-fed flies via the rain-gated trees. The brake is natural, not a cull.
	droughtFoodRegenMult = 0.15
)

// initForagePoolsInChunk registers flower (world.nectar) occupants in a loaded chunk at full nectar.
// Mirrors initHostPlantsInChunk; idempotent.
func (m *Match) initForagePoolsInChunk(state *WorldState, chunk *ChunkData, cx, cy int, logger runtime.Logger) {
	chunkSize := state.Config.ChunkSize
	for ly := 0; ly < chunkSize; ly++ {
		for lx := 0; lx < chunkSize; lx++ {
			cell, _ := chunk.GetOccupantCell(lx, ly)
			if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
				continue
			}
			def := state.Entities[cell.Occupant.ID]
			if def == nil || def.World == nil || !def.World.Nectar {
				continue
			}
			gx, gy := cx*chunkSize+lx, cy*chunkSize+ly
			key := fmt.Sprintf("%d,%d", gx, gy)
			if state.ForagePools[key] != nil {
				continue
			}
			state.ForagePools[key] = &entities.ForagePoolState{
				EntityID: cell.Occupant.ID, GridX: gx, GridY: gy, Nectar: maxNectar,
			}
		}
	}
}

// processForagePools regrows flower nectar each tick (a grazed-out flower slowly becomes a food source
// again). Server-only soft state. The regen rate is the master boom-bust dial.
func (m *Match) processForagePools(state *WorldState) {
	regen := float32(nectarRegenPerTick)
	if state.DroughtUntilTick > state.TickCount {
		regen *= droughtFoodRegenMult // drought: flowers give far less nectar → butterflies food-limited
	}
	for _, fp := range state.ForagePools {
		if fp.Nectar < maxNectar {
			fp.Nectar += regen
			if fp.Nectar > maxNectar {
				fp.Nectar = maxNectar
			}
		}
	}
}

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

			// Wild trees spawn PRE-FRUITED (the early-game forage -> pen loop) but all
			// UNRIPE: DropTimer randomized below the ripeness threshold staggers when
			// each tree starts shedding (some shed the first evening — the deliberate
			// day-1 fly-food bootstrap). The tank starts empty: wild trees re-fruit via
			// RAIN ONLY unless a player tends them. LastWaterDay = -1, NOT 0 — the zero
			// value would read as "already watered on day 0".
			tree := &entities.FruitTreeState{
				TreeID:       fmt.Sprintf("tree_%d_%d", gx, gy),
				EntityID:     cell.Occupant.ID, // entity type ("tree_apple") for def lookups (rot ticks etc.)
				GridX:        gx,
				GridY:        gy,
				MaxFruit:     maxFruit,
				FruitCount:   2 + rand.Intn(2),
				DropTimer:    rand.Intn(treeDefDropTicks(entityDef)),
				LastWaterDay: -1,
			}
			if tree.FruitCount > maxFruit {
				tree.FruitCount = maxFruit
			}
			state.FruitTreeStates[treeKey] = tree

			logger.Debug("Initialized fruit tree at %d,%d (%s) with %d fruit",
				gx, gy, entityDef.World.FruitType, tree.FruitCount)
		}
	}
}
