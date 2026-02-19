package world

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"runtime/debug"
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

	// Extract zone_id param (default to village_21)
	zoneID, ok := params["zone_id"].(string)
	if !ok || zoneID == "" {
		zoneID = "village_21"
	}

	// Extract debug_mode param
	debugMode, _ := params["debug_mode"].(bool)

	if debugMode {
		logger.Info("DEBUG MODE ENABLED - zone: %s", zoneID)
	}

	// Create world state
	state := NewWorldState(worldID, ownerID, name, accessPolicy)
	state.ZoneID = zoneID
	state.DebugMode = debugMode

	// Initialize world seed for deterministic bug simulation
	state.WorldSeed = rand.Int63()
	logger.Info("World seed: %d", state.WorldSeed)

	// Load species from config (use debug config in debug mode)
	speciesPath := "data/species.json"
	if debugMode {
		speciesPath = "data/species_debug.json"
	}
	species, err := entities.LoadSpecies(speciesPath)
	if err != nil {
		logger.Warn("Failed to load species config: %v - using defaults", err)
		state.Species = defaultFlySpecies()
	} else {
		state.Species = species
	}
	logger.Info("Loaded %d species", len(state.Species))

	// Load zone data (Phase 4)
	zonePath := fmt.Sprintf("data/zones/%s", zoneID)
	zoneConfig, err := LoadZoneConfig(zonePath)
	if err != nil {
		logger.Warn("Failed to load zone config: %v - using default", err)
		zoneConfig = &ZoneConfig{ZoneID: "village_21", BiomeType: "village"}
	}
	state.CurrentZone = zoneConfig
	logger.Info("Loaded zone: %s", zoneConfig.ZoneID)

	// Load tile definitions (Phase 4)
	state.TileDefs, err = LoadTileDefinitions("data/tiles.json")
	if err != nil {
		logger.Warn("Failed to load tile definitions: %v", err)
	} else {
		logger.Info("Loaded %d tile definitions", len(state.TileDefs))
	}

	// Load entity definitions from unified entity system
	var warnings []string
	state.Entities, warnings, err = LoadAllEntities("data")
	if err != nil {
		logger.Warn("Failed to load entity definitions: %v", err)
	} else {
		logger.Info("Loaded %d entity definitions", len(state.Entities))
		for _, w := range warnings {
			logger.Warn("Entity loading: %s", w)
		}
	}

	// Load crop definitions
	state.CropDefs, err = LoadCropDefs("data")
	if err != nil {
		logger.Warn("Failed to load crop definitions: %v", err)
	} else {
		logger.Info("Loaded %d crop definitions", len(state.CropDefs))
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
	logger.Info(">>> MatchJoinAttempt called for %s at tick %d", presence.GetUserId(), tick)
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
	logger.Info(">>> MatchJoin called with %d presences at tick %d", len(presences), tick)
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchJoin: invalid state type")
		return state
	}

	for _, presence := range presences {
		userID := presence.GetUserId()
		worldState.AddPlayer(userID, presence.GetUsername(), presence)
		logger.Info("Player %s joined world %s", presence.GetUsername(), worldState.WorldID)

		// Send WorldInit for deterministic bug simulation
		worldInit := WorldInitMessage{
			WorldSeed: worldState.WorldSeed,
			Tick:      worldState.TickCount,
		}
		initData, _ := json.Marshal(worldInit)
		dispatcher.BroadcastMessage(OpCodeWorldInit, initData, []runtime.Presence{presence}, nil, true)

		// Send full inventory sync to the joining player
		player := worldState.Players[userID]
		if err := m.sendInventorySync(logger, dispatcher, player, presence); err != nil {
			logger.Warn("Failed to send inventory sync to %s: %v", userID, err)
		}

		// Emit initial cell event for spawn position (deterministic bug AI)
		zoneID := ""
		if worldState.CurrentZone != nil {
			zoneID = worldState.CurrentZone.ZoneID
		}
		spawnX := player.WorldX(worldState.Config.ChunkSize)
		spawnY := player.WorldY(worldState.Config.ChunkSize)
		worldState.CheckPlayerCellChange(userID, spawnX, spawnY, zoneID)

		// === ZONE AUTHORITY ASSIGNMENT ===
		// First player in zone becomes authority, late joiners get snapshot
		if worldState.CurrentZone != nil {
			zone := worldState.GetOrCreateZone(zoneID)
			zone.Members[userID] = true

			if zone.AuthorityUserID == "" || zone.AuthorityUserID == userID {
				// First player OR authority reconnecting - assign/confirm as authority
				zone.AuthorityUserID = userID
				logger.Info("Assigned %s as authority for zone %s (reconnect=%v)", userID, zoneID, zone.AuthorityUserID == userID)

				// Send ZoneAuthority with bootstrap tick
				// Bootstrap Rule: LastEventSeq = -1 for first client
				// This indicates no prior influence events exist or are required.
				// The cell event just created will be broadcast in next MatchLoop tick,
				// and the first ZoneTickBroadcast will carry the real watermark.
				authMsg := ZoneAuthorityMessage{
					ZoneID:            zoneID,
					AuthorityID:       userID,
					AuthoritativeTick: worldState.TickCount,
					LastEventSeq:      -1, // FIRST CLIENT BOOTSTRAP - no prior events
				}
				authData, _ := json.Marshal(authMsg)
				dispatcher.BroadcastMessage(OpCodeZoneAuthority, authData, []runtime.Presence{presence}, nil, true)
			} else {
				// Late joiner - needs snapshot from authority
				logger.Info("Late joiner %s in zone %s, authority is %s", userID, zoneID, zone.AuthorityUserID)
				m.sendLateJoinSnapshot(logger, dispatcher, worldState, userID, presence)
			}
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
	logger.Info(">>> MatchLeave called with %d presences at tick %d", len(presences), tick)
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLeave: invalid state type")
		return state
	}

	for _, presence := range presences {
		userID := presence.GetUserId()
		worldState.RemovePlayer(userID)

		// Emit PLAYER_CELL_LEAVE influence event before deleting cell state
		// This ensures other clients' InfluenceManager removes the phantom player cell
		if cell, exists := worldState.PlayerCells[userID]; exists {
			zoneID := ""
			if worldState.CurrentZone != nil {
				zoneID = worldState.CurrentZone.ZoneID
			}
			worldState.AddInfluenceEvent(zoneID, InfluencePlayerCellLeave, userID, cell.CellX, cell.CellY, "", 0)
		}

		// Clean up player cell state
		delete(worldState.PlayerCells, userID)

		// Clean up chunk subscriptions
		for _, subs := range worldState.ChunkSubs {
			delete(subs, userID)
		}

		// === ZONE AUTHORITY REASSIGNMENT ===
		// If leaving player was authority, reassign to another member
		if worldState.CurrentZone != nil {
			zoneID := worldState.CurrentZone.ZoneID
			zone := worldState.GetZone(zoneID)
			if zone != nil {
				delete(zone.Members, userID)

				// Check if zone is now completely empty - reset ALL sync state
				// This prevents watermark mismatch when next player joins
				if len(zone.Members) == 0 {
					zone.NextSeq = 0
					zone.InfluenceLog = nil
					zone.LatestSnapshot = nil
					zone.LatestSnapshotTick = 0
					zone.LatestSnapshotHash = ""
					zone.AuthorityUserID = ""
					logger.Info("Zone %s is now empty - reset all sync state (NextSeq, InfluenceLog, Snapshot, Authority)", zoneID)
				} else if zone.AuthorityUserID == userID {
					// Authority is leaving but zone still has members - reassign
					zone.AuthorityUserID = ""
					var newAuthority string
					for memberID := range zone.Members {
						if _, connected := worldState.Presences[memberID]; connected {
							newAuthority = memberID
							break
						}
					}

					if newAuthority != "" {
						zone.AuthorityUserID = newAuthority
						logger.Info("Reassigned authority for zone %s to %s", zoneID, newAuthority)

						// Broadcast new authority to all remaining players
						// Note: This is NOT a bootstrap, so use current watermark
						authMsg := ZoneAuthorityMessage{
							ZoneID:            zoneID,
							AuthorityID:       newAuthority,
							AuthoritativeTick: worldState.TickCount,
							LastEventSeq:      zone.NextSeq - 1,
						}
						authData, _ := json.Marshal(authMsg)
						dispatcher.BroadcastMessage(OpCodeZoneAuthority, authData, nil, nil, true)
					} else {
						// Members exist but none are connected - this is a transient state
						// Zone will be reset when the last member actually leaves
						logger.Info("No connected players in zone %s, authority cleared (waiting for full empty)", zoneID)
					}
				}
			}
		}

		logger.Info("Player %s left world %s", presence.GetUsername(), worldState.WorldID)
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	// Return state to keep match alive (persistent world)
	return worldState
}

// MatchLoop is called every tick
func (m *Match) MatchLoop(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, messages []runtime.MatchData) (result interface{}) {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLoop: invalid state type")
		return nil // End match on invalid state
	}

	// PANIC RECOVERY: Catch any hidden panics and log them
	// IMPORTANT: We set result = worldState so if panic occurs, match continues
	defer func() {
		if r := recover(); r != nil {
			logger.Error("PANIC in MatchLoop: %v", r)
			logger.Error("Stack trace:\n%s", debug.Stack())
			result = worldState // Keep match alive after panic
		}
	}()

	worldState.TickCount++
	chunkSize := worldState.Config.ChunkSize

	// Process incoming messages
	for _, msg := range messages {
		userID := msg.GetUserId()
		player, exists := worldState.Players[userID]
		if !exists {
			continue
		}

		opCode := msg.GetOpCode()
		// Don't log high-frequency messages
		if opCode != OpCodeMovement && opCode != OpCodeChunkSubscribe && opCode != OpCodeChunkUnsub {
			logger.Info("Received OpCode %d from %s", opCode, userID)
		}

		switch opCode {
		case OpCodeMovement:
			var movement MovementMessage
			if err := json.Unmarshal(msg.GetData(), &movement); err != nil {
				logger.Warn("Invalid movement message from %s: %v", userID, err)
				continue
			}
			// Update player state
			player.SetWorldPosition(movement.X, movement.Y, chunkSize)
			player.Facing = entities.Direction(movement.Facing)

			// Track cell changes for deterministic bug AI
			zoneID := ""
			if worldState.CurrentZone != nil {
				zoneID = worldState.CurrentZone.ZoneID
			}
			worldState.CheckPlayerCellChange(userID, movement.X, movement.Y, zoneID)

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

		case OpCodeToolUse:
			var toolMsg ToolUseMessage
			if err := json.Unmarshal(msg.GetData(), &toolMsg); err != nil {
				logger.Warn("Invalid tool use from %s: %v", userID, err)
				continue
			}
			m.handleToolUse(logger, dispatcher, worldState, userID, toolMsg, worldState.TickCount)

		case OpCodePlantInteract:
			var plantMsg PlantInteractMessage
			if err := json.Unmarshal(msg.GetData(), &plantMsg); err != nil {
				logger.Warn("Invalid plant interact from %s: %v", userID, err)
				continue
			}
			m.handlePlantInteract(logger, dispatcher, worldState, userID, plantMsg, worldState.TickCount)

		case OpCodePickupItem:
			var pickupMsg PickupItemMessage
			if err := json.Unmarshal(msg.GetData(), &pickupMsg); err != nil {
				continue
			}
			m.handlePickupItem(logger, dispatcher, worldState, userID, pickupMsg)

		case OpCodeInteractionReport:
			var reportMsg InteractionReportMessage
			if err := json.Unmarshal(msg.GetData(), &reportMsg); err != nil {
				logger.Warn("Invalid interaction report from %s: %v", userID, err)
				continue
			}
			m.handleInteractionReport(worldState, reportMsg)

		// Bug Sync (Late Joiner + Drift Detection)
		case OpCodeSampleResponse:
			var respMsg SampleResponseMessage
			if err := json.Unmarshal(msg.GetData(), &respMsg); err != nil {
				logger.Warn("Invalid sample response from %s: %v", userID, err)
				continue
			}
			m.handleSampleResponse(logger, dispatcher, worldState, userID, respMsg)

		case OpCodeRequestSnapshot:
			var reqMsg SnapshotRequestMessage
			if err := json.Unmarshal(msg.GetData(), &reqMsg); err != nil {
				logger.Warn("Invalid snapshot request from %s: %v", userID, err)
				continue
			}
			m.handleSnapshotRequest(logger, dispatcher, worldState, userID, reqMsg)

		case OpCodeZoneSnapshot:
			// Authority client sends periodic snapshots (OpCode 75)
			var snapMsg ZoneSnapshotMessage
			if err := json.Unmarshal(msg.GetData(), &snapMsg); err != nil {
				logger.Warn("Invalid zone snapshot from %s: %v", userID, err)
				continue
			}
			m.handleZoneSnapshot(logger, worldState, userID, snapMsg)
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

	// === Crop Growth ===
	cropCount := len(worldState.CropStates)
	if cropCount > 0 && worldState.TickCount%100 == 0 {
		logger.Debug("DEBUG: processCropGrowth starting with %d crops at tick %d", cropCount, worldState.TickCount)
	}
	m.processCropGrowth(worldState, dispatcher)

	// === Fruit Trees & Ground Item Decay ===
	m.processFruitTrees(worldState, dispatcher, logger)
	m.processGroundItemDecay(worldState, dispatcher)

	// === Swarm Simulation ===
	deltaTime := 1.0 / float32(worldState.Config.TickRate)

	// Blocked checker for collision detection
	isBlocked := func(x, y float32) bool {
		return worldState.IsBlocked(x, y)
	}

	// Simulate swarms
	for _, swarm := range worldState.Swarms {
		species := worldState.Species[swarm.SpeciesID]
		if species == nil {
			continue
		}

		// THINK: Every few seconds, pick new target (expensive)
		if worldState.TickCount >= swarm.NextThinkTick {
			// Query resources only when thinking
			var resourceX, resourceY float32 = float32(math.NaN()), float32(math.NaN())
			attractions := swarm.GetCurrentAttractions(species)
			if len(attractions) > 0 {
				hits := FindNearbyResources(worldState, swarm.Position, species.VisionRange, attractions)
				if len(hits) > 0 {
					resourceX, resourceY = hits[0].X, hits[0].Y
				}
			}

			swarm.Think(species, chunkSize, resourceX, resourceY, isBlocked)

			// Schedule next think: 30-50 ticks (3-5 seconds at 10 ticks/sec)
			swarm.NextThinkTick = worldState.TickCount + 30 + rand.Int63n(21)
		}

		// MOVE: Every tick, move toward target (cheap)
		swarm.Move(deltaTime, species, chunkSize)

		// Check phase transitions
		swarm.CheckPhaseTransition(species)
	}

	// Check merge/split every 50 ticks (5 seconds)
	if worldState.TickCount-worldState.LastMergeCheck >= 50 {
		m.checkSwarmMerging(worldState, chunkSize, logger)
		m.checkSwarmSplitting(worldState, chunkSize, logger)
		worldState.LastMergeCheck = worldState.TickCount
	}

	// Check continuous spawning every 100 ticks (10 seconds)
	if worldState.TickCount%100 == 0 {
		m.checkContinuousSpawning(worldState, worldState.TickCount, logger)
	}

	// Broadcast swarm updates
	if len(worldState.Swarms) > 0 {
		swarmData := make([]SwarmData, 0, len(worldState.Swarms))
		for _, swarm := range worldState.Swarms {
			spriteID := swarm.SpeciesID // fallback
			if species, ok := worldState.Species[swarm.SpeciesID]; ok {
				spriteID = species.SpriteID
			}
			swarmData = append(swarmData, SwarmData{
				ID:         swarm.ID,
				SpeciesID:  swarm.SpeciesID,
				SpriteID:   spriteID,
				X:          swarm.WorldX(chunkSize),
				Y:          swarm.WorldY(chunkSize),
				Radius:     swarm.Radius,
				Count:      swarm.Count,
				Facing:     int(swarm.Facing),
				Phase:      swarm.Phase,
				NextBugID:  swarm.NextBugID,
				RemovedIDs: swarm.GetRemovedIDs(),
			})
		}

		swarmUpdate := SwarmUpdateMessage{Tick: worldState.TickCount, Swarms: swarmData}
		data, err := json.Marshal(swarmUpdate)
		if err != nil {
			logger.Error("Failed to marshal swarm update: %v", err)
		} else {
			dispatcher.BroadcastMessage(OpCodeSwarmUpdate, data, nil, nil, true)
		}
	}

	// Update ground item lifetimes
	m.updateGroundItemLifetimes(logger, dispatcher, worldState, deltaTime)

	// Bug sync: check for pending snapshot timeouts (frozen players)
	m.checkPendingSnapshotTimeouts(logger, dispatcher, worldState)

	// Bug sync: periodic drift sampling every 300 ticks (30 seconds at 10Hz)
	if worldState.TickCount%300 == 0 {
		m.checkDriftSampling(logger, dispatcher, worldState)
	}

	// Broadcast pending influence events (server-authored bug sync)
	if len(worldState.PendingInfluence) > 0 {
		influenceMsg := InfluenceBroadcastMessage{Events: worldState.PendingInfluence}
		data, err := json.Marshal(influenceMsg)
		if err != nil {
			logger.Error("Failed to marshal influence broadcast: %v", err)
		} else {
			dispatcher.BroadcastMessage(OpCodeInfluenceBroadcast, data, nil, nil, true)
		}
		worldState.ClearPendingInfluence()
	}

	// === TICK FRONTIER BROADCAST (OpCode 78) ===
	// CRITICAL: Must be broadcast EVERY tick, AFTER influence events
	// This is the safety mechanism for frontier-gated simulation:
	// Server guarantees all events for tick t are broadcast BEFORE frontier t
	// DEBUG: Log when broadcast is skipped
	if worldState.CurrentZone == nil {
		if worldState.TickCount%100 == 0 {
			logger.Warn("ZoneTickBroadcast SKIPPED: CurrentZone is nil at tick %d", worldState.TickCount)
		}
	} else if len(worldState.Players) == 0 && len(worldState.Presences) == 0 {
		if worldState.TickCount%100 == 0 {
			logger.Warn("ZoneTickBroadcast SKIPPED: No players/presences at tick %d", worldState.TickCount)
		}
	}
	if worldState.CurrentZone != nil && (len(worldState.Players) > 0 || len(worldState.Presences) > 0) {
		zone := worldState.GetOrCreateZone(worldState.CurrentZone.ZoneID)
		tickMsg := ZoneTickBroadcastMessage{
			ZoneID:            worldState.CurrentZone.ZoneID,
			AuthoritativeTick: worldState.TickCount,
			LastEventSeq:      zone.NextSeq - 1, // Last assigned seq (NextSeq is next to assign)
			AuthorityID:       zone.AuthorityUserID,
		}
		tickData, err := json.Marshal(tickMsg)
		if err != nil {
			logger.Error("Failed to marshal tick broadcast: %v", err)
		} else {
			dispatcher.BroadcastMessage(OpCodeZoneTickBroadcast, tickData, nil, nil, true)
		}
	}

	// Prune influence log periodically (every 100 ticks)
	if worldState.TickCount%100 == 0 && worldState.CurrentZone != nil {
		worldState.PruneInfluenceLog(worldState.CurrentZone.ZoneID, worldState.TickCount)
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

// spawnInitialSwarms seeds the world with swarms using zone-level species caps.
// Initial seeding spawns cap.Initial swarms per species immediately on match init.
func (m *Match) spawnInitialSwarms(state *WorldState, logger runtime.Logger) {
	cfg := state.CurrentZone.BugSpawning
	if cfg == nil {
		logger.Info("No bug spawning config for zone")
		return
	}

	totalSpawned := 0

	// Initialize species tracking and spawn initial swarms
	for speciesID, cap := range cfg.SpeciesCaps {
		state.SwarmsBySpecies[speciesID] = []string{}

		// Schedule first continuous spawn check
		state.SpeciesNextSpawn[speciesID] = float64(cap.SpawnInterval)

		// Initial seeding
		for i := 0; i < cap.Initial; i++ {
			if swarm := m.spawnSwarmForSpecies(state, speciesID, logger); swarm != nil {
				totalSpawned++
			}
		}

		logger.Debug("Species %s: seeded %d/%d swarms", speciesID, cap.Initial, cap.Max)
	}

	logger.Info("Seeded world with %d swarms across %d species",
		totalSpawned, len(cfg.SpeciesCaps))
}

// spawnSwarmForSpecies creates a new swarm for the given species in a valid spawn area.
// Returns nil if species is at zone cap or has no valid spawn areas.
func (m *Match) spawnSwarmForSpecies(state *WorldState, speciesID string, logger runtime.Logger) *entities.SwarmState {
	cfg := state.CurrentZone.BugSpawning
	cap := cfg.SpeciesCaps[speciesID]

	// Check zone-level cap for this species
	aliveCount := 0
	for _, swarmID := range state.SwarmsBySpecies[speciesID] {
		if _, exists := state.Swarms[swarmID]; exists {
			aliveCount++
		}
	}
	if aliveCount >= cap.Max {
		return nil
	}

	// Get species definition
	species := state.Species[speciesID]
	if species == nil {
		logger.Warn("Unknown species %s", speciesID)
		return nil
	}

	// Find spawn areas that include this species
	var validAreas []SpawnArea
	for _, area := range cfg.SpawnAreas {
		for _, s := range area.Species {
			if s == speciesID {
				validAreas = append(validAreas, area)
				break
			}
		}
	}
	if len(validAreas) == 0 {
		logger.Warn("No spawn areas defined for species %s", speciesID)
		return nil
	}

	// Pick random area
	area := validAreas[rand.Intn(len(validAreas))]

	// Generate position based on area type
	var worldX, worldY float32
	if area.Type == "zone" {
		// Anywhere in zone
		worldX = float32(rand.Intn(state.CurrentZone.Width))
		worldY = float32(rand.Intn(state.CurrentZone.Height))
	} else {
		// Circle: random point within radius
		angle := rand.Float64() * 2 * math.Pi
		r := float64(area.Radius) * math.Sqrt(rand.Float64()) // sqrt for uniform distribution
		worldX = float32(area.CX) + float32(r*math.Cos(angle))
		worldY = float32(area.CY) + float32(r*math.Sin(angle))
	}

	// Convert to chunk position
	chunkSize := state.Config.ChunkSize
	pos := entities.EntityPosition{
		ChunkX: int(worldX) / chunkSize,
		ChunkY: int(worldY) / chunkSize,
		LocalX: worldX - float32(int(worldX)/chunkSize*chunkSize),
		LocalY: worldY - float32(int(worldY)/chunkSize*chunkSize),
	}

	// Create swarm with count in lower-middle range
	countRange := species.MaxSwarmSize / 2
	if countRange < 1 {
		countRange = 1
	}
	id, _ := uuid.NewV4()
	swarm := &entities.SwarmState{
		ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
		SpeciesID: speciesID,
		Position:  pos,
		Radius:    species.SwarmRadius,
		Count:     species.MinSwarmSize + rand.Intn(countRange),
		WanderRad: species.WanderRadius,
		HomePos:   pos,
	}
	swarm.InitializeBugIDs()

	state.Swarms[swarm.ID] = swarm
	state.SwarmsBySpecies[speciesID] = append(state.SwarmsBySpecies[speciesID], swarm.ID)

	logger.Debug("Spawned swarm %s (%s) in %s at (%.0f, %.0f)",
		swarm.ID, speciesID, area.ID, worldX, worldY)

	return swarm
}

// checkContinuousSpawning spawns new swarms over time until species caps are reached.
// Should be called periodically from the tick loop.
func (m *Match) checkContinuousSpawning(state *WorldState, tick int64, logger runtime.Logger) {
	if state.DebugMode {
		return // Skip continuous spawning in debug mode
	}

	cfg := state.CurrentZone.BugSpawning
	if cfg == nil {
		return
	}

	currentTime := float64(tick) / float64(state.Config.TickRate)

	for speciesID, cap := range cfg.SpeciesCaps {
		// Check if it's time to try spawning
		if currentTime < state.SpeciesNextSpawn[speciesID] {
			continue
		}

		// Clean up dead/caught swarms from species tracking
		var aliveSwarms []string
		for _, swarmID := range state.SwarmsBySpecies[speciesID] {
			if _, exists := state.Swarms[swarmID]; exists {
				aliveSwarms = append(aliveSwarms, swarmID)
			}
		}
		state.SwarmsBySpecies[speciesID] = aliveSwarms

		// Spawn one new swarm if below cap
		if len(aliveSwarms) < cap.Max {
			if swarm := m.spawnSwarmForSpecies(state, speciesID, logger); swarm != nil {
				logger.Debug("Continuous spawn: %s (%s) [%d/%d]",
					swarm.ID, speciesID, len(aliveSwarms)+1, cap.Max)
			}
		}

		// Schedule next spawn attempt
		state.SpeciesNextSpawn[speciesID] = currentTime + float64(cap.SpawnInterval)
	}
}

// checkSwarmMerging merges nearby swarms of the same species
func (m *Match) checkSwarmMerging(state *WorldState, chunkSize int, logger runtime.Logger) {
	if state.DebugMode {
		return // Skip merging in debug mode
	}

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
	if state.DebugMode {
		return // Skip splitting in debug mode
	}

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

	// Cap bug IDs by tool (hand=5, small_net=15)
	maxCatch := 5
	if player.EquippedTool == "small_net" {
		maxCatch = 15
	}
	bugIDs := msg.BugIDs
	if len(bugIDs) > maxCatch {
		bugIDs = bugIDs[:maxCatch]
	}

	// Validate and remove bugs - returns only valid, alive IDs
	removed := swarm.RemoveBugs(bugIDs)
	if len(removed) == 0 {
		return
	}

	// Emit BUG_REMOVED influence events for deterministic late joiner replay
	// Each removed bug gets its own event so replay can process them individually
	if state.CurrentZone != nil {
		zoneID := state.CurrentZone.ZoneID
		for _, bugID := range removed {
			state.AddInfluenceEvent(zoneID, InfluenceBugRemoved, "", 0, 0, swarm.ID, bugID)
		}
	}

	// Add to player's bug inventory
	slotIdx := player.AddBugs(swarm.SpeciesID, len(removed))

	// Broadcast catch event to all clients with validated bug IDs
	caughtMsg := BugCaughtMessage{
		SwarmID:   swarm.ID,
		CatcherID: playerID,
		BugIDs:    removed,
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

// updateGroundItemLifetimes decrements item lifetimes and removes expired items
func (m *Match) updateGroundItemLifetimes(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	deltaTime float32,
) {
	var expired []string

	for id, item := range state.GroundItems {
		item.Lifetime -= deltaTime
		if item.Lifetime <= 0 {
			expired = append(expired, id)
		}
	}

	for _, id := range expired {
		item := state.GroundItems[id]
		delete(state.GroundItems, id)

		removeMsg := GroundItemRemoveMessage{ID: id}
		m.broadcastToChunk(dispatcher, state, item.Position.ChunkX, item.Position.ChunkY, OpCodeGroundItemRemove, removeMsg)
	}
}

// handleInteractionReport processes aggregated bug-resource interactions from a client
func (m *Match) handleInteractionReport(state *WorldState, msg InteractionReportMessage) {
	for _, report := range msg.Reports {
		swarm, exists := state.Swarms[report.SwarmID]
		if !exists {
			continue
		}

		species := state.Species[swarm.SpeciesID]
		if species == nil {
			continue
		}

		// Sanity check - cap at reasonable max per report period
		foodCount := report.FoodCount
		if foodCount > 50 {
			foodCount = 50
		}
		breedCount := report.BreedCount
		if breedCount > 50 {
			breedCount = 50
		}

		// Update lifecycle meters based on current phase
		if swarm.Phase == "feeding" && foodCount > 0 {
			swarm.Satiation += float32(foodCount) * species.FeedAmount
			if swarm.Satiation > 100 {
				swarm.Satiation = 100
			}
		}
		if swarm.Phase == "reproducing" && breedCount > 0 {
			swarm.ReproductionMeter += float32(breedCount) * species.BreedAmount
			if swarm.ReproductionMeter > 100 {
				swarm.ReproductionMeter = 100
			}
		}
	}
}

// === Bug Sync (Late Joiner + Drift Detection) ===

// requestSnapshotForLateJoiner sends OpCode 61 to source player requesting all bug positions in chunk.
// Called from handleChunkSubscribe when a late joiner enters an active chunk.
func (m *Match) requestSnapshotForLateJoiner(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	sourceID string,
	requesterID string,
	cx, cy int,
) {
	// Build list of all bugs in swarms that are in this chunk
	var queries []BugSampleQuery
	for _, swarm := range state.Swarms {
		if swarm.Position.ChunkX != cx || swarm.Position.ChunkY != cy {
			continue
		}
		// Add all alive bugs in this swarm
		for bugID := 0; bugID < swarm.NextBugID; bugID++ {
			if swarm.IsBugAlive(bugID) {
				queries = append(queries, BugSampleQuery{
					SwarmID: swarm.ID,
					BugID:   bugID,
				})
			}
		}
	}

	if len(queries) == 0 {
		logger.Debug("No bugs in chunk %d,%d for late joiner %s", cx, cy, requesterID)
		return
	}

	// Create pending request
	reqID := fmt.Sprintf("%s_%d", requesterID, time.Now().UnixNano())
	state.PendingSnapshots[reqID] = &PendingSnapshotReq{
		RequesterID:  requesterID,
		SourceID:     sourceID,
		TriedSources: []string{sourceID},
		ChunkX:       cx,
		ChunkY:       cy,
		RequestTick:  state.TickCount,
	}

	// Send sample request to source player
	reqMsg := SampleRequestMessage{
		ChunkX:  cx,
		ChunkY:  cy,
		Tick:    state.TickCount,
		Samples: queries,
	}
	data, _ := json.Marshal(reqMsg)

	if presence, ok := state.Presences[sourceID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeRequestSample, data, []runtime.Presence{presence}, nil, true)
		logger.Debug("Requested snapshot from %s for late joiner %s in chunk %d,%d (%d bugs)",
			sourceID, requesterID, cx, cy, len(queries))
	}
}

// handleSampleResponse processes OpCode 62 from a client.
// Either relays as full snapshot to late joiner, or broadcasts for drift comparison.
func (m *Match) handleSampleResponse(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	senderID string,
	msg SampleResponseMessage,
) {
	// Check if this is a response to a pending late joiner request
	for reqID, pending := range state.PendingSnapshots {
		if pending.SourceID == senderID && pending.ChunkX == msg.ChunkX && pending.ChunkY == msg.ChunkY {
			// Convert samples to full snapshot format
			swarmMap := make(map[string][]BugSampleData)
			for _, sample := range msg.Samples {
				swarmMap[sample.SwarmID] = append(swarmMap[sample.SwarmID], sample)
			}

			var swarmSnapshots []SwarmSnapshotData
			for swarmID, bugs := range swarmMap {
				swarmSnapshots = append(swarmSnapshots, SwarmSnapshotData{
					SwarmID: swarmID,
					Bugs:    bugs,
				})
			}

			snapshotMsg := FullSnapshotMessage{
				ChunkX: msg.ChunkX,
				ChunkY: msg.ChunkY,
				Tick:   msg.Tick,
				Swarms: swarmSnapshots,
			}
			data, _ := json.Marshal(snapshotMsg)

			// Send to requester
			if presence, ok := state.Presences[pending.RequesterID]; ok && presence != nil {
				dispatcher.BroadcastMessage(OpCodeFullSnapshot, data, []runtime.Presence{presence}, nil, true)
				logger.Debug("Relayed snapshot to late joiner %s for chunk %d,%d (%d samples)",
					pending.RequesterID, msg.ChunkX, msg.ChunkY, len(msg.Samples))
			}

			delete(state.PendingSnapshots, reqID)
			return
		}
	}

	// Not for a late joiner - broadcast as drift sample to all others in chunk
	chunkKey := ChunkKey(msg.ChunkX, msg.ChunkY)
	subs := state.ChunkSubs[chunkKey]
	if len(subs) == 0 {
		return
	}

	var presences []runtime.Presence
	for userID := range subs {
		if userID == senderID {
			continue // Don't send back to sender
		}
		if p, exists := state.Presences[userID]; exists && p != nil {
			presences = append(presences, p)
		}
	}

	if len(presences) > 0 {
		data, _ := json.Marshal(msg)
		dispatcher.BroadcastMessage(OpCodeSampleBroadcast, data, presences, nil, true)
		logger.Debug("Broadcast drift sample for chunk %d,%d to %d clients", msg.ChunkX, msg.ChunkY, len(presences))
	}
}

// handleSnapshotRequest processes OpCode 66 from a client that detected drift.
// Finds another player in the chunk and requests a snapshot from them.
func (m *Match) handleSnapshotRequest(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	requesterID string,
	msg SnapshotRequestMessage,
) {
	chunkKey := ChunkKey(msg.ChunkX, msg.ChunkY)
	subs := state.ChunkSubs[chunkKey]

	// Find a connected player other than requester
	var sourceID string
	for playerID := range subs {
		if playerID == requesterID {
			continue
		}
		if _, connected := state.Presences[playerID]; connected {
			sourceID = playerID
			break
		}
	}

	if sourceID == "" {
		logger.Debug("No other players in chunk %d,%d to provide snapshot for %s", msg.ChunkX, msg.ChunkY, requesterID)
		return
	}

	// Request snapshot from source player
	m.requestSnapshotForLateJoiner(logger, dispatcher, state, sourceID, requesterID, msg.ChunkX, msg.ChunkY)
}

// checkPendingSnapshotTimeouts checks for pending snapshot requests that have timed out.
// If a source player doesn't respond within 50 ticks (5 seconds), try another player.
func (m *Match) checkPendingSnapshotTimeouts(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
) {
	const timeoutTicks = 50 // 5 seconds at 10Hz

	for reqID, pending := range state.PendingSnapshots {
		if state.TickCount-pending.RequestTick < timeoutTicks {
			continue
		}

		// Timed out - try to find another source
		chunkKey := ChunkKey(pending.ChunkX, pending.ChunkY)
		subs := state.ChunkSubs[chunkKey]

		var newSource string
		for playerID := range subs {
			if playerID == pending.RequesterID {
				continue
			}
			// Skip already tried sources
			tried := false
			for _, s := range pending.TriedSources {
				if s == playerID {
					tried = true
					break
				}
			}
			if tried {
				continue
			}
			if _, connected := state.Presences[playerID]; connected {
				newSource = playerID
				break
			}
		}

		if newSource == "" {
			// No more players to try - give up
			logger.Warn("Snapshot request timed out for %s in chunk %d,%d - no more sources",
				pending.RequesterID, pending.ChunkX, pending.ChunkY)
			delete(state.PendingSnapshots, reqID)
			continue
		}

		// Update pending request with new source
		pending.SourceID = newSource
		pending.TriedSources = append(pending.TriedSources, newSource)
		pending.RequestTick = state.TickCount

		// Build query list again and send to new source
		var queries []BugSampleQuery
		for _, swarm := range state.Swarms {
			if swarm.Position.ChunkX != pending.ChunkX || swarm.Position.ChunkY != pending.ChunkY {
				continue
			}
			for bugID := 0; bugID < swarm.NextBugID; bugID++ {
				if swarm.IsBugAlive(bugID) {
					queries = append(queries, BugSampleQuery{
						SwarmID: swarm.ID,
						BugID:   bugID,
					})
				}
			}
		}

		reqMsg := SampleRequestMessage{
			ChunkX:  pending.ChunkX,
			ChunkY:  pending.ChunkY,
			Tick:    state.TickCount,
			Samples: queries,
		}
		data, _ := json.Marshal(reqMsg)

		if presence, ok := state.Presences[newSource]; ok && presence != nil {
			dispatcher.BroadcastMessage(OpCodeRequestSample, data, []runtime.Presence{presence}, nil, true)
			logger.Debug("Retrying snapshot from %s for %s in chunk %d,%d (attempt %d)",
				newSource, pending.RequesterID, pending.ChunkX, pending.ChunkY, len(pending.TriedSources))
		}
	}
}

// handleZoneSnapshot stores a snapshot from the authority client (OpCode 75).
// The server stores (but does not inspect) the snapshot for late joiners.
func (m *Match) handleZoneSnapshot(
	logger runtime.Logger,
	state *WorldState,
	senderID string,
	msg ZoneSnapshotMessage,
) {
	zone := state.GetOrCreateZone(msg.ZoneID)

	// Only accept snapshots from the current authority
	if zone.AuthorityUserID != senderID {
		logger.Warn("Ignoring snapshot from non-authority %s (authority is %s)", senderID, zone.AuthorityUserID)
		return
	}

	// Store the snapshot (opaque to server)
	zone.LatestSnapshot = &ZoneSnapshot{
		ZoneID:               msg.ZoneID,
		SnapshotTick:         msg.SnapshotTick,
		SnapshotLastEventSeq: msg.SnapshotLastEventSeq,
		Swarms:               msg.Swarms,
		StateHash:            msg.StateHash,
	}
	zone.LatestSnapshotTick = msg.SnapshotTick
	zone.LatestSnapshotHash = msg.StateHash

	logger.Debug("Stored snapshot from authority %s at tick %d, last_event_seq=%d", senderID, msg.SnapshotTick, msg.SnapshotLastEventSeq)
}

// sendLateJoinSnapshot sends a LateJoinSnapshot (OpCode 72) to a joining player.
// This contains the authority's snapshot plus the influence log for replay.
func (m *Match) sendLateJoinSnapshot(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	joinerID string,
	presence runtime.Presence,
) {
	if state.CurrentZone == nil {
		logger.Warn("Cannot send late join snapshot - no current zone")
		return
	}

	zoneID := state.CurrentZone.ZoneID
	zone := state.GetOrCreateZone(zoneID)

	// Check if we have a snapshot from authority
	// If no snapshot yet, create bootstrap snapshot - client will get swarms via SwarmUpdate
	if zone.LatestSnapshot == nil {
		logger.Info("No authority snapshot yet, creating bootstrap for late joiner %s in zone %s", joinerID, zoneID)
		zone.LatestSnapshot = &ZoneSnapshot{
			ZoneID:               zoneID,
			SnapshotTick:         state.TickCount,
			SnapshotLastEventSeq: zone.NextSeq - 1, // All events to date are "in" the bootstrap state
			Swarms:               []SwarmSnapshotData{}, // Empty - SwarmUpdate provides swarm data
			StateHash:            "",
		}
		zone.LatestSnapshotTick = state.TickCount
	}

	snapshotTick := zone.LatestSnapshotTick
	endTick := state.TickCount
	snapshotLastSeq := zone.LatestSnapshot.SnapshotLastEventSeq
	endLastSeq := zone.NextSeq - 1 // Current watermark

	// Build influence log by seq interval (spec §8.2: "Do not filter by tick alone. Use seq intervals.")
	// Include events where seq ∈ (snapshotLastSeq, endLastSeq]
	var influenceLog []InfluenceEvent
	for _, evt := range zone.InfluenceLog {
		if evt.Seq > snapshotLastSeq && evt.Seq <= endLastSeq {
			influenceLog = append(influenceLog, evt)
		}
	}

	// Server packaging verification (spec §7.5)
	if len(influenceLog) > 0 {
		firstSeq := influenceLog[0].Seq
		lastSeq := influenceLog[len(influenceLog)-1].Seq
		logger.Info("LateJoinSnapshot packaging: seq interval (%d, %d], events=%d, first_seq=%d, last_seq=%d",
			snapshotLastSeq, endLastSeq, len(influenceLog), firstSeq, lastSeq)
	} else {
		logger.Info("LateJoinSnapshot packaging: seq interval (%d, %d], events=0 (empty)",
			snapshotLastSeq, endLastSeq)
	}

	// Collect current player cell positions from authoritative state
	// This is snapshot state, NOT event reconstruction
	// Only include players currently in zone.Members (connected, zone-resident)
	var playerCells []PlayerCellData
	for playerID := range zone.Members {
		if cell, ok := state.PlayerCells[playerID]; ok {
			playerCells = append(playerCells, PlayerCellData{
				PlayerID: playerID,
				CellX:    cell.CellX,
				CellY:    cell.CellY,
			})
		}
	}

	// Sanity check: playerCells should match zone.Members count
	// If mismatch, state.PlayerCells wasn't updated correctly on join/leave
	if len(playerCells) != len(zone.Members) {
		logger.Warn("LateJoinSnapshot: playerCells=%d but zone.Members=%d - possible state sync bug",
			len(playerCells), len(zone.Members))
	}

	// Collect swarm metadata for creating swarm visuals on client
	// This allows clients to create swarms BEFORE replay, so snapshot positions can be applied
	chunkSize := state.Config.ChunkSize
	var swarmMetadata []SwarmData
	for _, swarmSnapshot := range zone.LatestSnapshot.Swarms {
		if swarm, ok := state.Swarms[swarmSnapshot.SwarmID]; ok {
			spriteID := swarm.SpeciesID // fallback
			if species, ok := state.Species[swarm.SpeciesID]; ok {
				spriteID = species.SpriteID
			}
			swarmMetadata = append(swarmMetadata, SwarmData{
				ID:         swarm.ID,
				SpeciesID:  swarm.SpeciesID,
				SpriteID:   spriteID,
				X:          swarm.WorldX(chunkSize),
				Y:          swarm.WorldY(chunkSize),
				Radius:     swarm.Radius,
				Count:      swarm.Count,
				Facing:     int(swarm.Facing),
				Phase:      swarm.Phase,
				NextBugID:  swarm.NextBugID,
				RemovedIDs: swarm.GetRemovedIDs(),
			})
		}
	}

	msg := LateJoinSnapshot{
		ZoneID:               zoneID,
		WorldSeed:            state.WorldSeed,
		SnapshotTick:         snapshotTick,
		EndTick:              endTick,
		SnapshotLastEventSeq: snapshotLastSeq,
		EndLastEventSeq:      endLastSeq,
		Swarms:               zone.LatestSnapshot.Swarms,
		SwarmMetadata:        swarmMetadata,
		InfluenceLog:         influenceLog,
		AuthorityID:          zone.AuthorityUserID,
		PlayerCells:          playerCells,
	}

	data, err := json.Marshal(msg)
	if err != nil {
		logger.Error("Failed to marshal late join snapshot: %v", err)
		return
	}

	dispatcher.BroadcastMessage(OpCodeLateJoinSnapshot, data, []runtime.Presence{presence}, nil, true)
	swarmCount := 0
	if zone.LatestSnapshot != nil && zone.LatestSnapshot.Swarms != nil {
		swarmCount = len(zone.LatestSnapshot.Swarms)
	}
	logger.Info("Sent LateJoinSnapshot to %s: tick range %d to %d, seq range (%d, %d], %d events, %d player_cells, %d swarms, %d swarm_metadata",
		joinerID, snapshotTick, endTick, snapshotLastSeq, endLastSeq, len(influenceLog), len(playerCells), swarmCount, len(swarmMetadata))
	for _, cell := range playerCells {
		logger.Info("  PlayerCell: %s at (%d, %d)", cell.PlayerID, cell.CellX, cell.CellY)
	}

	// Send ZoneHandoff to confirm the tick range
	// This guarantees: "no undisclosed events <= end_tick"
	handoffMsg := ZoneHandoffMessage{
		ZoneID:        zoneID,
		LiveStartTick: endTick + 1,
		LastEventSeq:  endLastSeq, // Watermark at handoff time (spec §3.6)
	}
	handoffData, _ := json.Marshal(handoffMsg)
	dispatcher.BroadcastMessage(OpCodeZoneHandoff, handoffData, []runtime.Presence{presence}, nil, true)
	logger.Info("Sent ZoneHandoff to %s: live_start_tick=%d, last_event_seq=%d", joinerID, endTick+1, endLastSeq)
}

// checkDriftSampling performs periodic drift detection by sampling bug positions.
// Called every 300 ticks (30 seconds). Samples 10 random bugs from one player per chunk.
func (m *Match) checkDriftSampling(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
) {
	// For each chunk with subscribers, sample bugs
	for chunkKey, subs := range state.ChunkSubs {
		if len(subs) < 2 {
			continue // Need at least 2 players for drift comparison
		}

		// Parse chunk coordinates
		var cx, cy int
		fmt.Sscanf(chunkKey, "%d,%d", &cx, &cy)

		// Find swarms in this chunk
		var queries []BugSampleQuery
		for _, swarm := range state.Swarms {
			if swarm.Position.ChunkX != cx || swarm.Position.ChunkY != cy {
				continue
			}

			// Sample up to 10 random bugs from this swarm
			aliveBugs := []int{}
			for bugID := 0; bugID < swarm.NextBugID; bugID++ {
				if swarm.IsBugAlive(bugID) {
					aliveBugs = append(aliveBugs, bugID)
				}
			}

			// Shuffle and take up to 10
			rand.Shuffle(len(aliveBugs), func(i, j int) {
				aliveBugs[i], aliveBugs[j] = aliveBugs[j], aliveBugs[i]
			})
			sampleCount := 10
			if len(aliveBugs) < sampleCount {
				sampleCount = len(aliveBugs)
			}
			for i := 0; i < sampleCount; i++ {
				queries = append(queries, BugSampleQuery{
					SwarmID: swarm.ID,
					BugID:   aliveBugs[i],
				})
			}
		}

		if len(queries) == 0 {
			continue
		}

		// Pick one connected player to sample
		var sourceID string
		for playerID := range subs {
			if _, connected := state.Presences[playerID]; connected {
				sourceID = playerID
				break
			}
		}
		if sourceID == "" {
			continue
		}

		// Send sample request
		reqMsg := SampleRequestMessage{
			ChunkX:  cx,
			ChunkY:  cy,
			Tick:    state.TickCount,
			Samples: queries,
		}
		data, _ := json.Marshal(reqMsg)

		if presence, ok := state.Presences[sourceID]; ok && presence != nil {
			dispatcher.BroadcastMessage(OpCodeRequestSample, data, []runtime.Presence{presence}, nil, true)
			logger.Debug("Drift sample request sent to %s for chunk %d,%d (%d bugs)",
				sourceID, cx, cy, len(queries))
		}
	}
}
