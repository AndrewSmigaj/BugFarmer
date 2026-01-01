package world

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"time"

	"bugfarmer/entities"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"
)

// Match implements runtime.Match for world simulation
type Match struct{}

// MatchLabel is the JSON structure for match listing
type MatchLabel struct {
	WorldID      string `json:"world_id"`
	Name         string `json:"name"`
	PlayerCount  int    `json:"player_count"`
	MaxPlayers   int    `json:"max_players"`
	AccessPolicy string `json:"access_policy"`
}

// NewMatch is the constructor registered with Nakama
func NewMatch(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule) (runtime.Match, error) {
	return &Match{}, nil
}

// MatchInit initializes the match state
func (m *Match) MatchInit(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, params map[string]interface{}) (interface{}, int, string) {
	// Extract params
	worldID, ok := params["world_id"].(string)
	if !ok || worldID == "" {
		logger.Error("MatchInit: missing world_id")
		return nil, 0, ""
	}

	ownerID, ok := params["owner_id"].(string)
	if !ok || ownerID == "" {
		logger.Error("MatchInit: missing owner_id")
		return nil, 0, ""
	}

	name, ok := params["name"].(string)
	if !ok || name == "" {
		name = "Unnamed World"
	}

	accessPolicy, ok := params["access_policy"].(string)
	if !ok || (accessPolicy != "public" && accessPolicy != "private") {
		accessPolicy = "public"
	}

	// Create world state
	state := NewWorldState(worldID, ownerID, name, accessPolicy)

	// Load species from config
	species, err := entities.LoadSpecies("data/species.json")
	if err != nil {
		logger.Warn("Failed to load species config: %v - using defaults", err)
		state.Species = defaultFlySpecies()
	} else {
		state.Species = species
	}
	logger.Info("Loaded %d species", len(state.Species))

	// Load zone data (Phase 4)
	zonePath := "data/zones/underground_passages_31"
	zoneConfig, err := LoadZoneConfig(zonePath)
	if err != nil {
		logger.Warn("Failed to load zone config: %v - using default", err)
		zoneConfig = &ZoneConfig{ZoneID: "underground_passages_31", BiomeType: "cave"}
	}
	state.CurrentZone = zoneConfig
	logger.Info("Loaded zone: %s", zoneConfig.ZoneID)

	// Load tile and occupant definitions (Phase 4)
	state.TileDefs, err = LoadTileDefinitions("data/tiles.json")
	if err != nil {
		logger.Warn("Failed to load tile definitions: %v", err)
	} else {
		logger.Info("Loaded %d tile definitions", len(state.TileDefs))
	}
	state.OccupantDefs, err = LoadOccupantDefinitions("data/occupants.json")
	if err != nil {
		logger.Warn("Failed to load occupant definitions: %v", err)
	} else {
		logger.Info("Loaded %d occupant definitions", len(state.OccupantDefs))
	}

	// Spawn initial swarms for testing
	m.spawnInitialSwarms(state, logger)

	// Create label for match listing
	label := MatchLabel{
		WorldID:      worldID,
		Name:         name,
		PlayerCount:  0,
		MaxPlayers:   state.Config.MaxPlayers,
		AccessPolicy: accessPolicy,
	}
	labelJSON, err := json.Marshal(label)
	if err != nil {
		logger.Error("MatchInit: failed to marshal label: %v", err)
		return nil, 0, ""
	}

	logger.Info("World match initialized: %s (%s)", name, worldID)

	return state, state.Config.TickRate, string(labelJSON)
}

// MatchJoinAttempt validates if a player can join
func (m *Match) MatchJoinAttempt(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presence runtime.Presence, metadata map[string]string) (interface{}, bool, string) {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchJoinAttempt: invalid state type")
		return state, false, "internal error"
	}

	// Check max players
	if len(worldState.Players) >= worldState.Config.MaxPlayers {
		logger.Warn("World %s is full, rejecting %s", worldState.WorldID, presence.GetUserId())
		return state, false, "world is full"
	}

	// Check access policy
	if worldState.AccessPolicy == "private" {
		// For now, only owner can join private worlds
		// TODO: Add invite list
		if presence.GetUserId() != worldState.OwnerID {
			logger.Warn("Private world %s, rejecting non-owner %s", worldState.WorldID, presence.GetUserId())
			return state, false, "private world"
		}
	}

	logger.Info("Player %s approved to join world %s", presence.GetUserId(), worldState.WorldID)
	return state, true, ""
}

// MatchJoin is called when player(s) successfully join
func (m *Match) MatchJoin(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presences []runtime.Presence) interface{} {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchJoin: invalid state type")
		return state
	}

	for _, presence := range presences {
		worldState.AddPlayer(presence.GetUserId(), presence.GetUsername(), presence)
		logger.Info("Player %s joined world %s", presence.GetUsername(), worldState.WorldID)

		// Send full inventory sync to the joining player
		player := worldState.Players[presence.GetUserId()]
		if err := m.sendInventorySync(logger, dispatcher, player, presence); err != nil {
			logger.Warn("Failed to send inventory sync to %s: %v", presence.GetUserId(), err)
		}
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	return worldState
}

// sendInventorySync sends the player's full inventory state
func (m *Match) sendInventorySync(logger runtime.Logger, dispatcher runtime.MatchDispatcher, player *PlayerState, presence runtime.Presence) error {
	// Convert fixed arrays to slices for JSON
	bugSlots := make([]InventorySlot, len(player.BugSlots))
	copy(bugSlots, player.BugSlots[:])

	itemSlots := make([]InventorySlot, len(player.ItemSlots))
	copy(itemSlots, player.ItemSlots[:])

	msg := FullInventorySyncMessage{
		BugSlots:  bugSlots,
		ItemSlots: itemSlots,
		Coins:     player.Coins,
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	dispatcher.BroadcastMessage(OpCodeFullInventorySync, data, []runtime.Presence{presence}, nil, true)
	logger.Info("Sent inventory sync to %s: %d bug slots, %d item slots, %d coins",
		presence.GetUserId(), len(bugSlots), len(itemSlots), player.Coins)
	return nil
}

// MatchLeave is called when player(s) leave
func (m *Match) MatchLeave(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presences []runtime.Presence) interface{} {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLeave: invalid state type")
		return state
	}

	for _, presence := range presences {
		worldState.RemovePlayer(presence.GetUserId())
		logger.Info("Player %s left world %s", presence.GetUsername(), worldState.WorldID)
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	// Return state to keep match alive (persistent world)
	return worldState
}

// MatchLoop is called every tick
func (m *Match) MatchLoop(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, messages []runtime.MatchData) interface{} {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLoop: invalid state type")
		return nil // End match on invalid state
	}

	worldState.TickCount++
	chunkSize := worldState.Config.ChunkSize

	// Process incoming messages
	for _, msg := range messages {
		userID := msg.GetUserId()
		player, exists := worldState.Players[userID]
		if !exists {
			continue
		}

		switch msg.GetOpCode() {
		case OpCodeMovement:
			var movement MovementMessage
			if err := json.Unmarshal(msg.GetData(), &movement); err != nil {
				logger.Warn("Invalid movement message from %s: %v", userID, err)
				continue
			}
			// Update player state
			player.SetWorldPosition(movement.X, movement.Y, chunkSize)
			player.Facing = entities.Direction(movement.Facing)

		case OpCodeCatchBug:
			var catchMsg CatchBugMessage
			if err := json.Unmarshal(msg.GetData(), &catchMsg); err != nil {
				logger.Warn("Invalid catch message from %s: %v", userID, err)
				continue
			}
			m.handleCatchBug(logger, dispatcher, worldState, catchMsg, userID, chunkSize)

		case OpCodeEquipTool:
			var equipMsg EquipToolMessage
			if err := json.Unmarshal(msg.GetData(), &equipMsg); err != nil {
				logger.Warn("Invalid equip message from %s: %v", userID, err)
				continue
			}
			player.EquippedTool = equipMsg.ToolID
			logger.Info("Player %s equipped tool: %q", userID, equipMsg.ToolID)

		case OpCodeMoveSlot:
			var moveMsg MoveSlotMessage
			if err := json.Unmarshal(msg.GetData(), &moveMsg); err != nil {
				logger.Warn("Invalid move slot message from %s: %v", userID, err)
				continue
			}
			m.handleMoveSlot(logger, dispatcher, worldState, moveMsg, userID)

		// World Building (Phase 4)
		case OpCodeChunkSubscribe:
			var subMsg ChunkSubscribeMessage
			if err := json.Unmarshal(msg.GetData(), &subMsg); err != nil {
				logger.Warn("Invalid chunk subscribe from %s: %v", userID, err)
				continue
			}
			m.handleChunkSubscribe(logger, dispatcher, worldState, userID, subMsg.ChunkX, subMsg.ChunkY)

		case OpCodeChunkUnsub:
			var subMsg ChunkSubscribeMessage
			if err := json.Unmarshal(msg.GetData(), &subMsg); err != nil {
				continue
			}
			m.handleChunkUnsub(worldState, userID, subMsg.ChunkX, subMsg.ChunkY)

		case OpCodeTilePlace:
			var placeMsg TilePlaceMessage
			if err := json.Unmarshal(msg.GetData(), &placeMsg); err != nil {
				logger.Warn("Invalid tile place from %s: %v", userID, err)
				continue
			}
			m.handleTilePlace(logger, dispatcher, worldState, userID, placeMsg)

		case OpCodeTileBreak:
			var breakMsg TileBreakMessage
			if err := json.Unmarshal(msg.GetData(), &breakMsg); err != nil {
				logger.Warn("Invalid tile break from %s: %v", userID, err)
				continue
			}
			m.handleTileBreak(logger, dispatcher, worldState, userID, breakMsg, worldState.TickCount)
		}
	}

	// Broadcast entity updates to all clients
	if len(worldState.Players) > 0 {
		entityData := make([]EntityData, 0, len(worldState.Players))
		for userID, player := range worldState.Players {
			entityData = append(entityData, EntityData{
				ID:     "player_" + userID,
				Type:   "player",
				X:      player.WorldX(chunkSize),
				Y:      player.WorldY(chunkSize),
				Facing: int(player.Facing),
			})
		}

		update := EntityUpdateMessage{Entities: entityData}
		data, err := json.Marshal(update)
		if err != nil {
			logger.Error("Failed to marshal entity update: %v", err)
		} else {
			dispatcher.BroadcastMessage(OpCodeEntityUpdate, data, nil, nil, true)
		}
	}

	// === Swarm Simulation ===
	deltaTime := 1.0 / float32(worldState.Config.TickRate)

	// Simulate swarms - update wandering behavior
	for _, swarm := range worldState.Swarms {
		if species := worldState.Species[swarm.SpeciesID]; species != nil {
			swarm.UpdateWander(deltaTime, species, chunkSize)
		}
	}

	// Check merge/split every 50 ticks (5 seconds)
	if worldState.TickCount-worldState.LastMergeCheck >= 50 {
		m.checkSwarmMerging(worldState, chunkSize, logger)
		m.checkSwarmSplitting(worldState, chunkSize, logger)
		worldState.LastMergeCheck = worldState.TickCount
	}

	// Broadcast swarm updates
	if len(worldState.Swarms) > 0 {
		swarmData := make([]SwarmData, 0, len(worldState.Swarms))
		for _, swarm := range worldState.Swarms {
			swarmData = append(swarmData, SwarmData{
				ID:        swarm.ID,
				SpeciesID: swarm.SpeciesID,
				X:         swarm.WorldX(chunkSize),
				Y:         swarm.WorldY(chunkSize),
				Radius:    swarm.Radius,
				Count:     swarm.Count,
				Facing:    int(swarm.Facing),
			})
		}

		swarmUpdate := SwarmUpdateMessage{Swarms: swarmData}
		data, err := json.Marshal(swarmUpdate)
		if err != nil {
			logger.Error("Failed to marshal swarm update: %v", err)
		} else {
			dispatcher.BroadcastMessage(OpCodeSwarmUpdate, data, nil, nil, true)
		}
	}

	// Return state to continue (never nil for persistent world)
	return worldState
}

// MatchTerminate is called when match is ending
func (m *Match) MatchTerminate(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, graceSeconds int) interface{} {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchTerminate: invalid state type")
		return state
	}

	logger.Info("World %s terminating, grace period %d seconds", worldState.WorldID, graceSeconds)

	// TODO: Persist world state to storage

	return worldState
}

// MatchSignal handles external commands (e.g., from RPC)
func (m *Match) MatchSignal(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, data string) (interface{}, string) {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchSignal: invalid state type")
		return state, `{"error": "internal error"}`
	}

	// Parse signal command
	var cmd map[string]interface{}
	if err := json.Unmarshal([]byte(data), &cmd); err != nil {
		return worldState, `{"error": "invalid signal format"}`
	}

	action, _ := cmd["action"].(string)

	switch action {
	case "get_info":
		info := map[string]interface{}{
			"world_id":     worldState.WorldID,
			"name":         worldState.Name,
			"player_count": len(worldState.Players),
			"tick_count":   worldState.TickCount,
		}
		response, _ := json.Marshal(info)
		return worldState, string(response)

	default:
		return worldState, fmt.Sprintf(`{"error": "unknown action: %s"}`, action)
	}
}

// updateLabel updates the match label with current player count
func (m *Match) updateLabel(dispatcher runtime.MatchDispatcher, state *WorldState) {
	label := MatchLabel{
		WorldID:      state.WorldID,
		Name:         state.Name,
		PlayerCount:  len(state.Players),
		MaxPlayers:   state.Config.MaxPlayers,
		AccessPolicy: state.AccessPolicy,
	}
	labelJSON, _ := json.Marshal(label)
	dispatcher.MatchLabelUpdate(string(labelJSON))
}

// defaultFlySpecies returns a fallback species map if config fails to load
func defaultFlySpecies() map[string]*entities.BugSpecies {
	return map[string]*entities.BugSpecies{
		"fly": {
			ID:             "fly",
			Name:           "Common Fly",
			Category:       "swarm",
			BaseSpeed:      1.5,
			WanderRadius:   8.0,
			MinSwarmSize:   5,
			MaxSwarmSize:   50,
			SwarmRadius:    4.0,
			MergeRadius:    4.0,
			SplitThreshold: 40,
			SplitChance:    0.01,
		},
	}
}

// spawnInitialSwarms creates test swarms near origin
func (m *Match) spawnInitialSwarms(state *WorldState, logger runtime.Logger) {
	chunkSize := state.Config.ChunkSize

	// Spawn near origin (0,0) for easier testing
	// Spread swarms in a 20x20 area around (10, 10)
	for i := 0; i < 5; i++ {
		id, _ := uuid.NewV4()
		pos := entities.EntityPosition{
			ChunkX: 0,
			ChunkY: 0,
			LocalX: 10 + float32(rand.Intn(20)-10),
			LocalY: 10 + float32(rand.Intn(20)-10),
		}
		pos.Normalize(chunkSize)

		species := state.Species["fly"]
		swarm := &entities.SwarmState{
			ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
			SpeciesID: "fly",
			Position:  pos,
			Radius:    species.SwarmRadius,
			Count:     10 + rand.Intn(20),
			WanderRad: species.WanderRadius,
			HomePos:   pos,
		}
		state.Swarms[swarm.ID] = swarm
	}

	logger.Info("Spawned %d initial swarms", len(state.Swarms))
}

// checkSwarmMerging merges nearby swarms of the same species
func (m *Match) checkSwarmMerging(state *WorldState, chunkSize int, logger runtime.Logger) {
	merged := make(map[string]bool)
	toDelete := []string{}

	for id1, swarm1 := range state.Swarms {
		if merged[id1] {
			continue
		}
		species1 := state.Species[swarm1.SpeciesID]
		if species1 == nil {
			continue
		}

		for id2, swarm2 := range state.Swarms {
			if id1 == id2 || merged[id2] {
				continue
			}
			if swarm1.SpeciesID != swarm2.SpeciesID {
				continue
			}

			// Calculate distance between swarm centers
			dist := distBetweenSwarms(swarm1, swarm2, chunkSize)

			// Merge if within merge radius (visual overlap)
			if dist <= species1.MergeRadius {
				combined := swarm1.Count + swarm2.Count
				// Only merge if combined doesn't exceed max
				if combined <= species1.MaxSwarmSize {
					swarm1.Count = combined
					merged[id2] = true
					toDelete = append(toDelete, id2)
				}
			}
		}
	}

	// Delete merged swarms after iteration
	for _, id := range toDelete {
		delete(state.Swarms, id)
	}

	if len(toDelete) > 0 {
		logger.Info("Merged %d swarms", len(toDelete))
	}
}

// checkSwarmSplitting randomly splits large swarms
func (m *Match) checkSwarmSplitting(state *WorldState, chunkSize int, logger runtime.Logger) {
	newSwarms := []*entities.SwarmState{}

	for _, swarm := range state.Swarms {
		species := state.Species[swarm.SpeciesID]
		if species == nil {
			continue
		}

		// Only split if above threshold and passes random check
		if swarm.Count > species.SplitThreshold && rand.Float32() < species.SplitChance {
			// Split roughly in half with some variance
			splitCount := swarm.Count/2 + rand.Intn(10) - 5
			if splitCount < species.MinSwarmSize {
				splitCount = species.MinSwarmSize
			}
			if swarm.Count-splitCount < species.MinSwarmSize {
				continue // Would leave too few in original
			}

			swarm.Count -= splitCount

			// Create new swarm offset from original
			id, _ := uuid.NewV4()
			newPos := offsetPosition(swarm.Position, 3.0, chunkSize)

			newSwarm := &entities.SwarmState{
				ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
				SpeciesID: swarm.SpeciesID,
				Position:  newPos,
				Radius:    swarm.Radius,
				Count:     splitCount,
				HomePos:   newPos,
				WanderRad: swarm.WanderRad,
			}
			newSwarms = append(newSwarms, newSwarm)
		}
	}

	// Add new swarms after iteration
	for _, s := range newSwarms {
		state.Swarms[s.ID] = s
	}

	if len(newSwarms) > 0 {
		logger.Info("Split into %d new swarms", len(newSwarms))
	}
}

// distBetweenSwarms calculates world distance between two swarms
func distBetweenSwarms(s1, s2 *entities.SwarmState, chunkSize int) float32 {
	dx := s1.WorldX(chunkSize) - s2.WorldX(chunkSize)
	dy := s1.WorldY(chunkSize) - s2.WorldY(chunkSize)
	return float32(math.Sqrt(float64(dx*dx + dy*dy)))
}

// offsetPosition creates a new position offset by the given distance
func offsetPosition(pos entities.EntityPosition, offset float32, chunkSize int) entities.EntityPosition {
	angle := rand.Float64() * 2 * math.Pi
	newPos := entities.EntityPosition{
		ChunkX: pos.ChunkX,
		ChunkY: pos.ChunkY,
		LocalX: pos.LocalX + float32(math.Cos(angle))*offset,
		LocalY: pos.LocalY + float32(math.Sin(angle))*offset,
	}
	newPos.Normalize(chunkSize)
	return newPos
}

// handleCatchBug processes a catch attempt from a player (Phase 2a)
// Client-trusted: client detects flies and sends count, server trusts it
func (m *Match) handleCatchBug(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg CatchBugMessage,
	playerID string,
	chunkSize int,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}

	// Rate limit: 200ms between catches
	now := time.Now().UnixMilli()
	if now-player.LastCatchTime < 200 {
		return
	}
	player.LastCatchTime = now

	// Get player world position using existing method
	playerX := player.WorldX(chunkSize)
	playerY := player.WorldY(chunkSize)

	// Validate click is within reach (hand=2 blocks, small_net=4.5 blocks)
	maxReach := float32(2.0)
	if player.EquippedTool == "small_net" {
		maxReach = 4.5
	}
	dx := msg.ClickX - playerX
	dy := msg.ClickY - playerY
	if dx*dx+dy*dy > maxReach*maxReach {
		return // Too far
	}

	// Look up the specific swarm
	swarm, exists := state.Swarms[msg.SwarmID]
	if !exists || swarm.Count <= 0 {
		return
	}

	// Trust client count, capped to swarm size
	caught := msg.CaughtCount
	if caught > swarm.Count {
		caught = swarm.Count
	}
	if caught <= 0 {
		return
	}

	// Apply catch - add to player's bug inventory
	swarm.Count -= caught
	slotIdx := player.AddBugs(swarm.SpeciesID, caught)

	// Broadcast catch event to all clients
	caughtMsg := BugCaughtMessage{
		SwarmID:   swarm.ID,
		CatcherID: playerID,
		Count:     caught,
		NewTotal:  swarm.Count,
		X:         msg.ClickX,
		Y:         msg.ClickY,
	}
	data, _ := json.Marshal(caughtMsg)
	dispatcher.BroadcastMessage(OpCodeBugCaught, data, nil, nil, true)

	// Send slot update to catcher only (if bugs were added successfully)
	if slotIdx >= 0 {
		slotMsg := SlotUpdateMessage{
			SlotIndex: slotIdx,
			ItemID:    player.BugSlots[slotIdx].ItemID,
			Count:     player.BugSlots[slotIdx].Count,
		}
		slotData, _ := json.Marshal(slotMsg)
		presence := state.Presences[playerID]
		dispatcher.BroadcastMessage(OpCodeBugSlotUpdate, slotData,
			[]runtime.Presence{presence}, nil, true)
	}

	// Remove empty swarm
	if swarm.Count <= 0 {
		delete(state.Swarms, swarm.ID)
	}
}

// handleMoveSlot processes inventory slot move/swap operations
func (m *Match) handleMoveSlot(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg MoveSlotMessage,
	playerID string,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}

	// Perform the move
	if !player.MoveSlot(msg.SourceType, msg.SourceIndex, msg.DestType, msg.DestIndex, msg.Count) {
		// Move failed - send error to client
		errMsg := ErrorMessage{Error: "Invalid move operation"}
		errData, _ := json.Marshal(errMsg)
		presence := state.Presences[playerID]
		dispatcher.BroadcastMessage(OpCodeErrorMessage, errData,
			[]runtime.Presence{presence}, nil, true)
		return
	}

	// Send slot updates for both affected slots
	presence := state.Presences[playerID]

	// Determine which OpCode to use based on slot type
	opCode := OpCodeBugSlotUpdate
	if msg.SourceType == "item" {
		opCode = OpCodeItemSlotUpdate
	}

	// Source slot update
	var srcSlot InventorySlot
	if msg.SourceType == "bug" {
		srcSlot = player.BugSlots[msg.SourceIndex]
	} else {
		srcSlot = player.ItemSlots[msg.SourceIndex]
	}
	srcMsg := SlotUpdateMessage{
		SlotIndex: msg.SourceIndex,
		ItemID:    srcSlot.ItemID,
		Count:     srcSlot.Count,
	}
	srcData, _ := json.Marshal(srcMsg)
	dispatcher.BroadcastMessage(opCode, srcData, []runtime.Presence{presence}, nil, true)

	// Destination slot update
	var dstSlot InventorySlot
	if msg.DestType == "bug" {
		dstSlot = player.BugSlots[msg.DestIndex]
	} else {
		dstSlot = player.ItemSlots[msg.DestIndex]
	}
	dstMsg := SlotUpdateMessage{
		SlotIndex: msg.DestIndex,
		ItemID:    dstSlot.ItemID,
		Count:     dstSlot.Count,
	}
	dstData, _ := json.Marshal(dstMsg)
	dispatcher.BroadcastMessage(opCode, dstData, []runtime.Presence{presence}, nil, true)

	logger.Debug("Player %s moved slot %s[%d] -> %s[%d]",
		playerID, msg.SourceType, msg.SourceIndex, msg.DestType, msg.DestIndex)
}
