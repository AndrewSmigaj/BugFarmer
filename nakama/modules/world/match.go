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

	// Create world state
	state := NewWorldState(worldID, ownerID, name, accessPolicy)
	state.ZoneID = zoneID

	// Load species from the canonical config
	species, err := entities.LoadSpecies("data/species.json")
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

	// Static-sim zones (test/deterministic) disable continuous spawn, merge, and split.
	if zoneConfig.BugSpawning != nil {
		state.StaticSim = zoneConfig.BugSpawning.Static
	}

	// World seed: fixed from zone config for deterministic runs, else random.
	if zoneConfig.Seed != 0 {
		state.WorldSeed = zoneConfig.Seed
	} else {
		state.WorldSeed = rand.Int63()
	}
	logger.Info("Loaded zone: %s (static=%v, seed=%d)", zoneConfig.ZoneID, state.StaticSim, state.WorldSeed)

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

		// RECONNECTION DETECTION: If this user already has a presence (old session),
		// log it. The old session's MatchLeave will fire later but will be ignored
		// by the stale session guard (session ID mismatch).
		if oldPresence, exists := worldState.Presences[userID]; exists {
			logger.Info("Player %s reconnecting: replacing session %s with %s",
				userID, oldPresence.GetSessionId(), presence.GetSessionId())
		}

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

	// SwarmUpdate is event-driven, so bootstrap a joiner's swarm set on the next tick.
	// (Late joiners also receive swarm_metadata in the snapshot; this re-broadcast is a
	// harmless reconcile and is the ONLY swarm set the first/authority client receives.)
	worldState.SwarmsDirty = true

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

		// STALE SESSION GUARD: If a newer session has already replaced this one
		// (reconnection), skip the leave cleanup entirely. The new session is still
		// active and should not be wiped out by the old session disconnecting.
		if currentPresence, exists := worldState.Presences[userID]; exists {
			if currentPresence.GetSessionId() != presence.GetSessionId() {
				logger.Info("Ignoring stale MatchLeave for %s: leaving session %s != current session %s",
					userID, presence.GetSessionId(), currentPresence.GetSessionId())
				continue
			}
		}

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

	// Pause when no one is connected. A world must not "run" (advance ticks, simulate bugs,
	// merge/split, broadcast) with zero players — that both wastes work and was crashing
	// long-idle matches in merge/split. Returning state keeps the match alive but fully idle;
	// TickCount freezes, so every tick-delta pauses cleanly and resumes when a player joins.
	if len(worldState.Players) == 0 && len(worldState.Presences) == 0 {
		return worldState
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

			// Origin = center BEFORE this leg starts (pre-Move). Emit a sparse,
			// self-describing leg event so clients re-anchor + move deterministically.
			originX := swarm.WorldX(chunkSize)
			originY := swarm.WorldY(chunkSize)

			swarm.Think(species, chunkSize, resourceX, resourceY, isBlocked)

			if worldState.CurrentZone != nil {
				worldState.AddSwarmTargetEvent(
					worldState.CurrentZone.ZoneID, swarm.ID,
					toFixed(originX), toFixed(originY),
					toFixed(swarm.TargetX), toFixed(swarm.TargetY),
					toFixed(species.BaseSpeed*deltaTime),
				)
			}

			// Schedule next think: 30-50 ticks (3-5 seconds at 10 ticks/sec)
			swarm.NextThinkTick = worldState.TickCount + 30 + rand.Int63n(21)
		}

		// MOVE: Every tick, move toward target (cheap)
		swarm.Move(deltaTime, species, chunkSize)

		// Check phase transitions (metadata change → re-broadcast swarm set)
		prevPhase := swarm.Phase
		swarm.CheckPhaseTransition(species)
		if swarm.Phase != prevPhase {
			worldState.SwarmsDirty = true
		}
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

	// Broadcast swarm SET/metadata only when it changes (NOT per tick). Positions are
	// derived deterministically on clients from SWARM_SET_TARGET events, so this carries
	// lifecycle/metadata + the current leg for clients creating a swarm's visual.
	if worldState.SwarmsDirty {
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
		worldState.SwarmsDirty = false
	}

	// Update ground item lifetimes
	m.updateGroundItemLifetimes(logger, dispatcher, worldState, deltaTime)

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

	// Determine bug count: fixed swarm_size if set (deterministic test zones),
	// else species MinSwarmSize plus a random amount in the lower-middle range.
	countRange := species.MaxSwarmSize / 2
	if countRange < 1 {
		countRange = 1
	}
	count := species.MinSwarmSize + rand.Intn(countRange)
	if cap.SwarmSize > 0 {
		count = cap.SwarmSize
	}
	id, _ := uuid.NewV4()
	swarm := &entities.SwarmState{
		ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
		SpeciesID: speciesID,
		Position:  pos,
		Radius:    species.SwarmRadius,
		Count:     count,
		WanderRad: species.WanderRadius,
		HomePos:   pos,
	}
	swarm.InitializeBugIDs()

	state.Swarms[swarm.ID] = swarm
	state.SwarmsBySpecies[speciesID] = append(state.SwarmsBySpecies[speciesID], swarm.ID)
	state.SwarmsDirty = true

	logger.Debug("Spawned swarm %s (%s) in %s at (%.0f, %.0f)",
		swarm.ID, speciesID, area.ID, worldX, worldY)

	return swarm
}

// checkContinuousSpawning spawns new swarms over time until species caps are reached.
// Should be called periodically from the tick loop.
func (m *Match) checkContinuousSpawning(state *WorldState, tick int64, logger runtime.Logger) {
	if state.StaticSim {
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
	if state.StaticSim {
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
		state.SwarmsDirty = true
		logger.Info("Merged %d swarms", len(toDelete))
	}
}

// checkSwarmSplitting randomly splits large swarms
func (m *Match) checkSwarmSplitting(state *WorldState, chunkSize int, logger runtime.Logger) {
	if state.StaticSim {
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
		state.SwarmsDirty = true
		logger.Info("Split into %d new swarms", len(newSwarms))
	}
}

// toFixed converts a float32 world coordinate to the client fixed-point scale (×1000).
// Matches FixedPoint.Scale on the client so leg events deserialize without rescaling.
func toFixed(v float32) int {
	return int(math.Round(float64(v) * 1000.0))
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

	// Remove empty swarm (despawn → re-broadcast set so clients drop the visual)
	if swarm.Count <= 0 {
		delete(state.Swarms, swarm.ID)
		state.SwarmsDirty = true
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

// handleSampleResponse processes OpCode 62 - a client's state hash at the settled drift tick.
// It accumulates responses into the chunk's DriftCheck; once every expected (still-connected)
// client has answered, it compares the equal-tick hashes and issues a targeted late-join
// resync to any minority. Hashes are only ever compared at the SAME tick, so this never
// false-positives on legitimate motion (the bug in the old position-sampling scheme).
func (m *Match) handleSampleResponse(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	senderID string,
	msg SampleResponseMessage,
) {
	chunkKey := ChunkKey(msg.ChunkX, msg.ChunkY)
	check := state.DriftChecks[chunkKey]
	if check == nil || msg.Tick != check.SampleTick || !check.Expected[senderID] {
		return // Stale, unsolicited, or not part of this round
	}

	check.Responded[senderID] = true
	if msg.HasHash {
		check.Votes[senderID] = msg.Hash
	}
	// HasHash==false: client lacks that tick (e.g. just resynced) - abstains, no vote.

	// Wait until every still-connected expected client has responded.
	for userID := range check.Expected {
		if _, connected := state.Presences[userID]; !connected {
			continue // Disconnected mid-round - don't wait on it
		}
		if !check.Responded[userID] {
			return // Still waiting
		}
	}

	// Round complete - tally votes.
	delete(state.DriftChecks, chunkKey)
	counts := make(map[int64]int)
	for _, h := range check.Votes {
		counts[h]++
	}
	if len(counts) <= 1 {
		return // Unanimous (or nobody voted) - no drift
	}

	// Pick the majority hash as the reference. On a tie, skip to avoid resync storms.
	var refHash int64
	bestCount, tie := -1, false
	for h, c := range counts {
		if c > bestCount {
			bestCount, refHash, tie = c, h, false
		} else if c == bestCount {
			tie = true
		}
	}
	if tie {
		logger.Warn("Drift check for chunk %d,%d at tick %d: ambiguous hash split %v - skipping resync",
			msg.ChunkX, msg.ChunkY, check.SampleTick, counts)
		return
	}

	// Resync every voter that disagreed with the majority.
	for userID, h := range check.Votes {
		if h == refHash {
			continue
		}
		if p, ok := state.Presences[userID]; ok && p != nil {
			logger.Warn("Drift detected: client %s hash %d != majority %d at tick %d - resyncing",
				userID, h, refHash, check.SampleTick)
			m.sendLateJoinSnapshot(logger, dispatcher, state, userID, p)
		}
	}
}

// handleSnapshotRequest processes OpCode 66 - a client's request for a full zone resync.
// The frontier system is zone-scoped, so recovery routes through the same proven late-join
// path (snapshot -> influence-log replay -> handoff -> live) rather than partial chunk
// catch-up, which cannot safely rewind the zone-wide simulation tick. The chunk fields in
// the request are ignored; resync is always zone-wide for the requester.
func (m *Match) handleSnapshotRequest(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	requesterID string,
	msg SnapshotRequestMessage,
) {
	presence, ok := state.Presences[requesterID]
	if !ok || presence == nil {
		logger.Warn("Resync request from %s but no presence found", requesterID)
		return
	}

	logger.Info("Zone resync requested by %s - sending late-join snapshot", requesterID)
	m.sendLateJoinSnapshot(logger, dispatcher, state, requesterID, presence)
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
			SnapshotLastEventSeq: zone.NextSeq - 1,      // All events to date are "in" the bootstrap state
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
			meta := SwarmData{
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
			}

			// Hydrate the leg active AT snapshotTick: the most recent SWARM_SET_TARGET for
			// this swarm with Tick <= snapshotTick. Legs started after snapshotTick are NOT
			// included here - they replay from influenceLog and overwrite the hydrated leg at
			// their own tick. Carrying the event's exact fixed-point values keeps the client's
			// closed-form center march bit-identical to the live clients'.
			for i := len(zone.InfluenceLog) - 1; i >= 0; i-- {
				evt := zone.InfluenceLog[i]
				if evt.Type == InfluenceSwarmSetTarget && evt.SwarmID == swarm.ID && evt.Tick <= snapshotTick {
					meta.HasTarget = true
					meta.LegOriginX = evt.OriginX
					meta.LegOriginY = evt.OriginY
					meta.LegTargetX = evt.TargetX
					meta.LegTargetY = evt.TargetY
					meta.LegSpeed = evt.Speed
					meta.LegStartTick = evt.Tick
					break
				}
			}

			swarmMetadata = append(swarmMetadata, meta)
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

// driftSampleMargin is how far behind the frontier the sampled tick sits, so every client
// has already simulated it (and still has it buffered) by the time the request arrives.
const driftSampleMargin = 20 // ticks (~2s at 10Hz)

// checkDriftSampling performs periodic, tick-aligned drift detection.
// Called every 300 ticks (~30s). For each chunk with ≥2 connected clients it asks ALL of
// them for ComputeStateHash() at the SAME settled tick (TickCount - margin) and records the
// expected responders in a DriftCheck. handleSampleResponse compares the equal-tick hashes and
// resyncs any minority. This replaces position sampling, which compared positions across
// mismatched ticks and produced false-positive resyncs every 30s.
func (m *Match) checkDriftSampling(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
) {
	sampleTick := state.TickCount - driftSampleMargin
	if sampleTick < 0 {
		return // Not enough history yet
	}

	for chunkKey, subs := range state.ChunkSubs {
		// Collect connected clients in this chunk
		var presences []runtime.Presence
		expected := make(map[string]bool)
		for playerID := range subs {
			if p, ok := state.Presences[playerID]; ok && p != nil {
				presences = append(presences, p)
				expected[playerID] = true
			}
		}
		if len(expected) < 2 {
			continue // Need at least 2 clients to compare
		}

		// Parse chunk coordinates
		var cx, cy int
		fmt.Sscanf(chunkKey, "%d,%d", &cx, &cy)

		// Open a fresh drift-check round (overwrites any stale one for this chunk)
		state.DriftChecks[chunkKey] = &DriftCheck{
			SampleTick: sampleTick,
			Expected:   expected,
			Responded:  make(map[string]bool),
			Votes:      make(map[string]int64),
		}

		reqMsg := SampleRequestMessage{ChunkX: cx, ChunkY: cy, Tick: sampleTick}
		data, _ := json.Marshal(reqMsg)
		dispatcher.BroadcastMessage(OpCodeRequestSample, data, presences, nil, true)
		logger.Debug("Drift hash request sent to %d clients for chunk %d,%d at tick %d",
			len(presences), cx, cy, sampleTick)
	}
}
