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
	MatchID      string `json:"match_id"`
	CreatedAt    int64  `json:"created_at"`
}

// Request/Response types

type WorldCreateRequest struct {
	Name         string `json:"name"`
	AccessPolicy string `json:"access_policy"`
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

// Helper function for error responses
func errorResponse(message, code string) (string, error) {
	resp := ErrorResponse{
		Error: message,
		Code:  code,
	}
	respJSON, _ := json.Marshal(resp)
	return string(respJSON), nil
}
