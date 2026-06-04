package rpc

import (
	"context"
	"database/sql"
	"encoding/json"
	"time"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"
)

// Storage constants
const (
	CollectionWorlds = "worlds"
)

// WorldMetadata is stored in Nakama storage
type WorldMetadata struct {
	WorldID      string `json:"world_id"`
	OwnerID      string `json:"owner_id"`
	Name         string `json:"name"`
	AccessPolicy string `json:"access_policy"`
	ZoneID       string `json:"zone_id"`
	MatchID      string `json:"match_id"`
	CreatedAt    int64  `json:"created_at"`
}

// Request/Response types

type WorldCreateRequest struct {
	Name         string `json:"name"`
	AccessPolicy string `json:"access_policy"`
	ZoneID       string `json:"zone_id,omitempty"` // Optional zone override (default: village_21)
}

type WorldCreateResponse struct {
	WorldID string `json:"world_id"`
	MatchID string `json:"match_id"`
}

type WorldListRequest struct {
	Limit  int    `json:"limit"`
	Cursor string `json:"cursor"`
}

type WorldListResponse struct {
	Worlds []WorldMetadata `json:"worlds"`
	Cursor string          `json:"cursor"`
}

type WorldJoinRequest struct {
	WorldID string `json:"world_id"`
}

type WorldJoinResponse struct {
	MatchID string `json:"match_id"`
}

type WorldEnterRequest struct {
	ZoneID string `json:"zone_id"`
}

// friendlyZoneName maps a zone id to a display name for the canonical (singleton) world.
func friendlyZoneName(zoneID string) string {
	switch zoneID {
	case "village_21":
		return "Normal"
	case "sim_test":
		return "Test"
	default:
		return zoneID
	}
}

type ErrorResponse struct {
	Error string `json:"error"`
	Code  string `json:"code"`
}

// WorldCreate creates a new world
func WorldCreate(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	// Get user ID from context
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	// Parse request
	var req WorldCreateRequest
	if err := json.Unmarshal([]byte(payload), &req); err != nil {
		return errorResponse("invalid request format", "INVALID_REQUEST")
	}

	// Validate and set defaults
	if req.Name == "" {
		req.Name = "Unnamed World"
	}
	if req.AccessPolicy != "public" && req.AccessPolicy != "private" {
		req.AccessPolicy = "public"
	}

	// Generate world ID
	worldID := uuid.Must(uuid.NewV4()).String()

	// Create match
	matchParams := map[string]interface{}{
		"world_id":      worldID,
		"owner_id":      userID,
		"name":          req.Name,
		"access_policy": req.AccessPolicy,
		"zone_id":       req.ZoneID,
	}
	matchID, err := nk.MatchCreate(ctx, "world", matchParams)
	if err != nil {
		logger.Error("Failed to create match: %v", err)
		return errorResponse("failed to create world", "MATCH_CREATE_FAILED")
	}

	// Store world metadata (system-owned for public listing)
	metadata := WorldMetadata{
		WorldID:      worldID,
		OwnerID:      userID,
		Name:         req.Name,
		AccessPolicy: req.AccessPolicy,
		ZoneID:       req.ZoneID,
		MatchID:      matchID,
		CreatedAt:    time.Now().Unix(),
	}
	metadataJSON, _ := json.Marshal(metadata)

	_, err = nk.StorageWrite(ctx, []*runtime.StorageWrite{{
		Collection:      CollectionWorlds,
		Key:             worldID,
		UserID:          "", // System-owned
		Value:           string(metadataJSON),
		PermissionRead:  2, // Public read
		PermissionWrite: 0, // No public write
	}})
	if err != nil {
		logger.Error("Failed to store world metadata: %v", err)
		return errorResponse("failed to save world", "STORAGE_WRITE_FAILED")
	}

	logger.Info("World created: %s (%s) by user %s", req.Name, worldID, userID)

	response := WorldCreateResponse{
		WorldID: worldID,
		MatchID: matchID,
	}
	responseJSON, _ := json.Marshal(response)
	return string(responseJSON), nil
}

// WorldList returns available worlds
func WorldList(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	// Get user ID from context (for filtering private worlds)
	userID, _ := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)

	// Parse request
	var req WorldListRequest
	if payload != "" {
		if err := json.Unmarshal([]byte(payload), &req); err != nil {
			return errorResponse("invalid request format", "INVALID_REQUEST")
		}
	}

	// Set defaults
	if req.Limit <= 0 || req.Limit > 100 {
		req.Limit = 20
	}

	// Query storage (system-owned objects)
	// StorageList params: ctx, callerID, userID, collection, limit, cursor
	objects, cursor, err := nk.StorageList(ctx, "", "", CollectionWorlds, req.Limit, req.Cursor)
	if err != nil {
		logger.Error("Failed to list worlds: %v", err)
		return errorResponse("failed to list worlds", "STORAGE_LIST_FAILED")
	}

	// Filter and parse worlds (initialize as empty slice, not nil)
	worlds := []WorldMetadata{}
	for _, obj := range objects {
		var metadata WorldMetadata
		if err := json.Unmarshal([]byte(obj.Value), &metadata); err != nil {
			logger.Warn("Failed to parse world metadata: %v", err)
			continue
		}

		// Filter: show public worlds OR worlds owned by current user
		if metadata.AccessPolicy == "public" || metadata.OwnerID == userID {
			worlds = append(worlds, metadata)
		}
	}

	response := WorldListResponse{
		Worlds: worlds,
		Cursor: cursor,
	}
	responseJSON, _ := json.Marshal(response)
	return string(responseJSON), nil
}

// WorldJoin returns the match ID for a world (recreates match if server restarted)
func WorldJoin(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	// Get user ID from context
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	// Parse request
	var req WorldJoinRequest
	if err := json.Unmarshal([]byte(payload), &req); err != nil {
		return errorResponse("invalid request format", "INVALID_REQUEST")
	}

	if req.WorldID == "" {
		return errorResponse("world_id required", "INVALID_REQUEST")
	}

	// Lookup world in storage
	objects, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: CollectionWorlds,
		Key:        req.WorldID,
		UserID:     "", // System-owned
	}})
	if err != nil || len(objects) == 0 {
		return errorResponse("world not found", "WORLD_NOT_FOUND")
	}

	var metadata WorldMetadata
	if err := json.Unmarshal([]byte(objects[0].Value), &metadata); err != nil {
		logger.Error("Failed to parse world metadata: %v", err)
		return errorResponse("invalid world data", "INVALID_DATA")
	}

	// Check access policy
	if metadata.AccessPolicy == "private" && metadata.OwnerID != userID {
		return errorResponse("private world", "ACCESS_DENIED")
	}

	// Check if match still exists
	matchID := metadata.MatchID
	match, err := nk.MatchGet(ctx, matchID)
	if err != nil || match == nil {
		// Match doesn't exist (server restarted) - recreate it
		logger.Info("Match %s not found, recreating for world %s", matchID, req.WorldID)

		matchParams := map[string]interface{}{
			"world_id":      metadata.WorldID,
			"owner_id":      metadata.OwnerID,
			"name":          metadata.Name,
			"access_policy": metadata.AccessPolicy,
			"zone_id":       metadata.ZoneID,
		}
		newMatchID, err := nk.MatchCreate(ctx, "world", matchParams)
		if err != nil {
			logger.Error("Failed to recreate match: %v", err)
			return errorResponse("failed to join world", "MATCH_CREATE_FAILED")
		}

		// Update storage with new match ID
		metadata.MatchID = newMatchID
		metadataJSON, _ := json.Marshal(metadata)
		_, err = nk.StorageWrite(ctx, []*runtime.StorageWrite{{
			Collection:      CollectionWorlds,
			Key:             req.WorldID,
			UserID:          "", // System-owned
			Value:           string(metadataJSON),
			PermissionRead:  2,
			PermissionWrite: 0,
		}})
		if err != nil {
			logger.Warn("Failed to update match ID in storage: %v", err)
			// Continue anyway - match was created
		}

		matchID = newMatchID
		logger.Info("Match recreated: %s for world %s", matchID, req.WorldID)
	}

	response := WorldJoinResponse{
		MatchID: matchID,
	}
	responseJSON, _ := json.Marshal(response)
	return string(responseJSON), nil
}

// WorldEnter finds-or-creates the canonical singleton world for a zone and returns a live match
// for it. This is how the frontend enters Normal/Test without a world-creation UI: the server
// guarantees exactly one world per zone (deterministic storage key), recreating the match on
// demand if it has been terminated. Race-free and survives a DB wipe. User-hosted worlds (the
// future menu) still use world_create/world_join.
func WorldEnter(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	var req WorldEnterRequest
	if err := json.Unmarshal([]byte(payload), &req); err != nil {
		return errorResponse("invalid request format", "INVALID_REQUEST")
	}
	if req.ZoneID == "" {
		req.ZoneID = "village_21"
	}

	// Deterministic per-zone identity so there is exactly one canonical world per zone.
	worldID := "default_" + req.ZoneID

	// Load existing canonical metadata (if any).
	var metadata WorldMetadata
	haveMetadata := false
	if objects, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: CollectionWorlds,
		Key:        worldID,
		UserID:     "", // system-owned
	}}); err == nil && len(objects) > 0 {
		if err := json.Unmarshal([]byte(objects[0].Value), &metadata); err == nil {
			haveMetadata = true
		}
	}

	// Reuse the live match if it still exists; otherwise (re)create it.
	matchID := ""
	if haveMetadata && metadata.MatchID != "" {
		if match, err := nk.MatchGet(ctx, metadata.MatchID); err == nil && match != nil {
			matchID = metadata.MatchID
		}
	}

	if matchID == "" {
		ownerID := userID
		if haveMetadata && metadata.OwnerID != "" {
			ownerID = metadata.OwnerID
		}
		newMatchID, err := nk.MatchCreate(ctx, "world", map[string]interface{}{
			"world_id":      worldID,
			"owner_id":      ownerID,
			"name":          friendlyZoneName(req.ZoneID),
			"access_policy": "public",
			"zone_id":       req.ZoneID,
		})
		if err != nil {
			logger.Error("WorldEnter: failed to create match for zone %s: %v", req.ZoneID, err)
			return errorResponse("failed to enter world", "MATCH_CREATE_FAILED")
		}
		matchID = newMatchID

		metadata = WorldMetadata{
			WorldID:      worldID,
			OwnerID:      ownerID,
			Name:         friendlyZoneName(req.ZoneID),
			AccessPolicy: "public",
			ZoneID:       req.ZoneID,
			MatchID:      matchID,
			CreatedAt:    time.Now().Unix(),
		}
		metadataJSON, _ := json.Marshal(metadata)
		if _, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{
			Collection:      CollectionWorlds,
			Key:             worldID,
			UserID:          "", // system-owned
			Value:           string(metadataJSON),
			PermissionRead:  2,
			PermissionWrite: 0,
		}}); err != nil {
			logger.Warn("WorldEnter: failed to persist metadata for zone %s: %v", req.ZoneID, err)
			// Non-fatal: the match exists; a later enter will re-persist.
		}
		logger.Info("WorldEnter: zone %s -> match %s (created)", req.ZoneID, matchID)
	} else {
		logger.Info("WorldEnter: zone %s -> match %s (reused)", req.ZoneID, matchID)
	}

	responseJSON, _ := json.Marshal(WorldJoinResponse{MatchID: matchID})
	return string(responseJSON), nil
}

// Helper function for error responses
func errorResponse(message, code string) (string, error) {
	resp := ErrorResponse{
		Error: message,
		Code:  code,
	}
	respJSON, _ := json.Marshal(resp)
	return string(respJSON), nil
}
