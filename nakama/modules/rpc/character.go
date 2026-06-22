package rpc

import (
	"context"
	"database/sql"
	"encoding/json"
	"strings"
	"time"

	"bugfarmer/world"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"
)

// Character RPCs. A player ACCOUNT (one device-auth userID) owns several CHARACTERS (Terraria-style);
// each persists independently in the "character" storage collection (user-owned, server-only write —
// see world/character_persist.go). These three RPCs manage the roster the select screen shows; the
// actual inventory/coins are written only by the match (on leave), never by a client.

const maxCharactersPerAccount = 8

type CharacterCreateRequest struct {
	Name  string `json:"name"`
	Class string `json:"class"`
	Hair  string `json:"hair"`
	Skin  string `json:"skin"`
}

type CharacterCreateResponse struct {
	Character world.CharacterSummary `json:"character"`
}

type CharacterListResponse struct {
	Characters []world.CharacterSummary `json:"characters"`
}

type CharacterDeleteRequest struct {
	CharID string `json:"char_id"`
}

type CharacterDeleteResponse struct {
	Deleted string `json:"deleted"`
}

// CharacterList returns the caller's characters (lightweight view for the select screen).
func CharacterList(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	summaries, err := world.ListCharacterSummaries(ctx, nk, userID)
	if err != nil {
		logger.Error("character_list failed for %s: %v", userID, err)
		return errorResponse("failed to list characters", "STORAGE_LIST_FAILED")
	}

	resp, _ := json.Marshal(CharacterListResponse{Characters: summaries})
	return string(resp), nil
}

// CharacterCreate makes a new character from the shared starting kit + chosen name/appearance.
func CharacterCreate(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	var req CharacterCreateRequest
	if err := json.Unmarshal([]byte(payload), &req); err != nil {
		return errorResponse("invalid request format", "INVALID_REQUEST")
	}

	req.Name = strings.TrimSpace(req.Name)
	if n := len([]rune(req.Name)); n < 1 || n > 20 {
		return errorResponse("name must be 1-20 characters", "INVALID_NAME")
	}

	// Enforce the per-account cap (and reuse the listing as a uniqueness check on name).
	existing, err := world.ListCharacterSummaries(ctx, nk, userID)
	if err != nil {
		logger.Error("character_create list-check failed for %s: %v", userID, err)
		return errorResponse("failed to create character", "STORAGE_LIST_FAILED")
	}
	if len(existing) >= maxCharactersPerAccount {
		return errorResponse("character limit reached", "LIMIT_REACHED")
	}
	for _, c := range existing {
		if strings.EqualFold(c.Name, req.Name) {
			return errorResponse("a character with that name already exists", "NAME_TAKEN")
		}
	}

	app := world.Appearance{Class: req.Class, Hair: req.Hair, Skin: req.Skin}
	if app.Class == "" {
		app.Class = "merchant"
	}
	if app.Hair == "" {
		app.Hair = "blonde"
	}
	if app.Skin == "" {
		app.Skin = "default"
	}

	charID := uuid.Must(uuid.NewV4()).String()
	save := world.DefaultCharacterSave(charID, req.Name, app, time.Now().Unix())
	if err := world.WriteCharacterSave(ctx, nk, userID, save); err != nil {
		logger.Error("character_create write failed for %s: %v", userID, err)
		return errorResponse("failed to create character", "STORAGE_WRITE_FAILED")
	}

	logger.Info("character created: %s (%s) for user %s", req.Name, charID, userID)
	resp, _ := json.Marshal(CharacterCreateResponse{Character: world.CharacterSummary{
		CharID: charID, Name: req.Name, Appearance: app, LastZone: "", LastPlayedAt: save.LastPlayedAt,
	}})
	return string(resp), nil
}

// CharacterDelete removes one of the caller's characters (ownership enforced by user-scoped storage).
func CharacterDelete(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, payload string) (string, error) {
	userID, ok := ctx.Value(runtime.RUNTIME_CTX_USER_ID).(string)
	if !ok || userID == "" {
		return errorResponse("authentication required", "AUTH_REQUIRED")
	}

	var req CharacterDeleteRequest
	if err := json.Unmarshal([]byte(payload), &req); err != nil {
		return errorResponse("invalid request format", "INVALID_REQUEST")
	}
	if req.CharID == "" {
		return errorResponse("char_id required", "INVALID_REQUEST")
	}

	// Verify the character exists and is owned by this account before deleting.
	save, err := world.LoadCharacterSave(ctx, nk, userID, req.CharID)
	if err != nil {
		logger.Error("character_delete read failed for %s: %v", userID, err)
		return errorResponse("failed to delete character", "STORAGE_READ_FAILED")
	}
	if save == nil {
		return errorResponse("character not found", "NOT_FOUND")
	}
	if err := world.DeleteCharacterSave(ctx, nk, userID, req.CharID); err != nil {
		logger.Error("character_delete failed for %s: %v", userID, err)
		return errorResponse("failed to delete character", "STORAGE_DELETE_FAILED")
	}

	logger.Info("character deleted: %s for user %s", req.CharID, userID)
	resp, _ := json.Marshal(CharacterDeleteResponse{Deleted: req.CharID})
	return string(resp), nil
}
