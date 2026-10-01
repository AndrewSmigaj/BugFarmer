package rpc

import (
	"context"
	"database/sql"
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"time"

	"bugfarmer/world"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"
)

// Storage constants
const (
	CollectionWorlds = "worlds"
)

// zonesRoot is where the authored zone folders live — the same root world.LoadZoneConfig reads
// ("data/zones/<id>/zone.json", relative to the server's working directory). A var so tests can
// point it at a temp dir.
var zonesRoot = "data/zones"

var zoneIDPattern = regexp.MustCompile(`^[A-Za-z0-9_]{1,64}$`) // e.g. village_21_B

// zoneExists reports whether zoneID names a real, authored zone. Unknown ids MUST be refused: the
// match used to fall back to "village_21" for an unknown zone and then load and WRITE village_21's
// save from a second match (e.g. walking into the not-yet-built ant_colony_40).
func zoneExists(zoneID string) bool {
	if !zoneIDPattern.MatchString(zoneID) {
		return false
	}
	info, err := os.Stat(filepath.Join(zonesRoot, zoneID, "zone.json"))
	return err == nil && !info.IsDir()
}

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

// ZoneNeighbors is the fixed-field form of a zone's adjacency (Unity's JsonUtility can't parse a map).
type ZoneNeighbors struct {
	North string `json:"north,omitempty"`
	South string `json:"south,omitempty"`
	East  string `json:"east,omitempty"`
	West  string `json:"west,omitempty"`
}

type WorldJoinResponse struct {
	MatchID   string         `json:"match_id"`
	Neighbors *ZoneNeighbors `json:"neighbors,omitempty"` // cross-zone adjacency (edge -> neighbor zoneID)
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
	case "collision_test":
		return "Collision Test"
	case "split_test2":
		return "Split Test"
	case "merge_test2":
		return "Merge Test"
	case "repro_test":
		return "Fly Farm Test"
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
	if req.ZoneID != "" && !zoneExists(req.ZoneID) {
		logger.Warn("WorldCreate: refusing unknown zone %q", req.ZoneID)
		return errorResponse("unknown zone", "UNKNOWN_ZONE")
	}

	if req.ZoneID == "" {
		req.ZoneID = "village_21" // MatchInit's default — the zone's lease must be keyed by the zone that will run
	}

	// Generate world ID
	worldID := uuid.Must(uuid.NewV4()).String()

	// Create the match — through the zone's lease (D73: one live copy per zone). A zone's save is per zone, not per
	// world, so a new world for a zone that is already running is refused instead of starting a second copy.
	ctx, cancel := context.WithTimeout(ctx, zoneEntryBudget)
	defer cancel()
	matchID, live, err := world.ZoneMatch(ctx, req.ZoneID, func(extra map[string]interface{}) (string, error) {
		return nk.MatchCreate(ctx, "world", withParams(map[string]interface{}{
			"world_id":      worldID,
			"owner_id":      userID,
			"name":          req.Name,
			"access_policy": req.AccessPolicy,
			"zone_id":       req.ZoneID,
		}, extra))
	})
	if err == nil && live {
		err = world.ErrZoneRunning
	}
	if err != nil {
		logger.Error("WorldCreate: zone %s: %v", req.ZoneID, err)
		msg, code := world.DescribeZoneError(err)
		return errorResponse(msg, code)
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
		// Match doesn't exist (server restarted) - recreate it, through the zone's lease (D73: one live copy per
		// zone — if another world's match already runs this zone, the request is refused).
		logger.Info("Match %s not found, recreating for world %s", matchID, req.WorldID)
		zoneID := metadata.ZoneID
		if zoneID == "" {
			zoneID = "village_21"
		}
		ctx, cancel := context.WithTimeout(ctx, zoneEntryBudget)
		defer cancel()
		newMatchID, live, err := world.ZoneMatch(ctx, zoneID, func(extra map[string]interface{}) (string, error) {
			return nk.MatchCreate(ctx, "world", withParams(map[string]interface{}{
				"world_id":      metadata.WorldID,
				"owner_id":      metadata.OwnerID,
				"name":          metadata.Name,
				"access_policy": metadata.AccessPolicy,
				"zone_id":       zoneID,
			}, extra))
		})
		if err == nil && live {
			err = world.ErrZoneRunning
		}
		if err != nil {
			logger.Error("WorldJoin: recreating world %s (zone %s): %v", req.WorldID, zoneID, err)
			msg, code := world.DescribeZoneError(err)
			return errorResponse(msg, code)
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
	if !zoneExists(req.ZoneID) {
		logger.Warn("WorldEnter: refusing unknown zone %q", req.ZoneID)
		return errorResponse("unknown zone", "UNKNOWN_ZONE")
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

	// The zone's live match, or a new one — through the zone's lease (D73: one live copy per zone; two players
	// arriving at once used to start two copies). Every wait shares one budget, under Nakama's 10 s request limit.
	ownerID := userID
	if haveMetadata && metadata.OwnerID != "" {
		ownerID = metadata.OwnerID
	}
	ctx, cancel := context.WithTimeout(ctx, zoneEntryBudget)
	defer cancel()
	matchID, live, err := world.ZoneMatch(ctx, req.ZoneID, func(extra map[string]interface{}) (string, error) {
		return nk.MatchCreate(ctx, "world", withParams(map[string]interface{}{
			"world_id":      worldID,
			"owner_id":      ownerID,
			"name":          friendlyZoneName(req.ZoneID),
			"access_policy": "public",
			"zone_id":       req.ZoneID,
		}, extra))
	})
	if err != nil {
		logger.Error("WorldEnter: zone %s: %v", req.ZoneID, err)
		msg, code := world.DescribeZoneError(err)
		return errorResponse(msg, code)
	}

	if !live {
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

	// Include the zone's cross-zone neighbors so the client can hidden-swap at edges (best-effort).
	var neighbors *ZoneNeighbors
	if zc, err := world.LoadZoneConfig("data/zones/" + req.ZoneID); err == nil && zc != nil && zc.Neighbors != nil {
		neighbors = &ZoneNeighbors{
			North: zc.Neighbors["north"], South: zc.Neighbors["south"],
			East: zc.Neighbors["east"], West: zc.Neighbors["west"],
		}
	}

	responseJSON, _ := json.Marshal(WorldJoinResponse{MatchID: matchID, Neighbors: neighbors})
	return string(responseJSON), nil
}

// zoneEntryBudget bounds every wait a zone request makes (the zone's lock, an old copy's saves, a character's
// release): Nakama cuts a request off at 10 s (socket.write_timeout_ms) with no reply at all, so the answer — even
// "busy, try again" — must come first.
const zoneEntryBudget = 8 * time.Second

// withParams adds extra (the zone epoch ZoneMatch reserved) to a match's creation params.
func withParams(params, extra map[string]interface{}) map[string]interface{} {
	for k, v := range extra {
		params[k] = v
	}
	return params
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
