package world

import (
	"github.com/heroiclabs/nakama-common/runtime"
)

// Nursery take: a nursery is a modified STATION — its egg/larva/pupa counts are collectable output units
// (the way a hive makes honeycomb and a furnace makes steel bars). Taking a stage pulls those units into the
// bag as the per-species stage item (species.<stage>_sprite_id). A plain item transfer — NO random yield, and
// nothing perishes on take (what you leave keeps developing). Broods are server-only soft state (never hashed),
// so this touches no sim/hashed state; the resident swarm (hashed) is untouched. Mirrors handleHiveHarvest.
func (m *Match) handleNurseryTake(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg NurseryTakeMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Range check (same 3.0 allowance as container/station/hive interactions).
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		return
	}

	b := state.BroodStates[broodKey(msg.GX, msg.GY)]
	if b == nil {
		return
	}
	sp := state.Species[b.SpeciesID]
	if sp == nil {
		return
	}

	// Pick the stage the player asked for: 0=egg, 1=larva, 2=pupa.
	var avail *int
	var itemID string
	switch msg.Stage {
	case 0:
		avail, itemID = &b.Eggs, sp.EggSpriteID
	case 1:
		avail, itemID = &b.Maggots, sp.LarvaSpriteID
	case 2:
		avail, itemID = &b.Pupae, sp.PupaSpriteID
	default:
		return
	}
	if *avail <= 0 || itemID == "" {
		return
	}

	take := *avail
	if msg.Count > 0 && msg.Count < take {
		take = msg.Count // partial take (a quantity picker can send this); default (Count<=0) is take-all
	}
	if player.AddItem(itemID, take) < 0 {
		return // bag full — leave the brood untouched
	}
	*avail -= take

	// Refresh the panel (the count drops; if the whole brood is now empty and residentless the client clears
	// it) and push the player's new inventory. The source keeps developing new brood as normal.
	m.broadcastBroodUpdate(dispatcher, state, b, false)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		_ = m.sendInventorySync(logger, dispatcher, player, presence)
	}
	logger.Info("NurseryTake: %s took %d %s (stage %d) at %d,%d", userID, take, itemID, msg.Stage, msg.GX, msg.GY)
}
