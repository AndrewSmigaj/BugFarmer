package world

import (
	"context"
	"encoding/json"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

// handleSetHome processes a player sleeping in a bed (OpCode 100): validate a sleepable occupant is
// anchored at the clicked cell and is in range, set the CHARACTER's home (the respawn + login
// anchor) to that bed, persist it immediately (async, best-effort), and ack the client.
//
// Character state only — home is part of the CharacterSave, never the bug-sim hash. Mirrors the
// occupant-lookup + range-check used by stations/containers.
func (m *Match) handleSetHome(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	nk runtime.NakamaModule,
	state *WorldState,
	userID string,
	msg SetHomeMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// A sleepable occupant must be ANCHORED at the clicked cell (footprint cells carry no back-ref,
	// so the client targets the anchor — same contract as opening a container).
	cx, cy, lx, ly := GlobalToChunk(msg.GX, msg.GY)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		m.sendWorldError(dispatcher, state, userID, "No bed there")
		return
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
		m.sendWorldError(dispatcher, state, userID, "No bed there")
		return
	}
	def := state.Entities[cell.Occupant.ID]
	if def == nil || def.World == nil || !def.World.Interactable || def.World.InteractionType != "sleep" {
		m.sendWorldError(dispatcher, state, userID, "That's not a bed")
		return
	}

	// Range check (same 3.0 allowance as stations/containers).
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendWorldError(dispatcher, state, userID, "Too far from the bed")
		return
	}

	zoneID := ""
	if state.CurrentZone != nil {
		zoneID = state.CurrentZone.ZoneID
	}
	player.HomeZone = zoneID
	player.HomeX = float32(msg.GX) + 0.5
	player.HomeY = float32(msg.GY) + 0.5

	// Persist now (async, best-effort) so the home survives a crash — not only a clean leave.
	// No-op for an ephemeral (no-character) session, e.g. the sync-harness.
	if player.CharacterID != "" {
		save := buildCharacterSave(player, zoneID, cs, time.Now().Unix())
		go func() {
			if err := WriteCharacterSave(context.Background(), nk, userID, save); err != nil {
				logger.Error("set-home save failed for %s/%s: %v", userID, save.CharID, err)
			}
		}()
	}

	ack := SetHomeAckMessage{
		OK: true, Message: "Home set — you'll wake here.",
		HomeX: player.HomeX, HomeY: player.HomeY,
	}
	data, _ := json.Marshal(ack)
	if presence, exists := state.Presences[userID]; exists && presence != nil {
		dispatcher.BroadcastMessage(OpCodeSetHomeAck, data, []runtime.Presence{presence}, nil, true)
	}
	logger.Info("Player %s set home at (%d,%d) in zone %s", userID, msg.GX, msg.GY, zoneID)
}
