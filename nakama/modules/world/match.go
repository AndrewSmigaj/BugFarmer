package world

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"

	"bugfarmer/entities"

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
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	return worldState
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
