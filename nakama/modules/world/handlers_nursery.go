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

	// Pick the stage the player asked for: 0=egg, 1=larva, 2=pupa. The TAKE item is the stage's dedicated
	// item id where the design has one (e.g. wasp larva -> wasp_larvae), else the stage's own sprite id (the
	// stackable stage placeable). Display sprite and take item are separate on purpose.
	var avail *int
	var itemID, spriteID string
	switch msg.Stage {
	case 0:
		avail, itemID, spriteID = &b.Eggs, sp.EggItemID, sp.EggSpriteID
	case 1:
		avail, itemID, spriteID = &b.Maggots, sp.LarvaItemID, sp.LarvaSpriteID
	case 2:
		avail, itemID, spriteID = &b.Pupae, sp.PupaItemID, sp.PupaSpriteID
	default:
		return
	}
	if itemID == "" {
		itemID = spriteID
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

// broodItemStage reverse-resolves a stage ITEM id back to its (species, stage) — the exact id the take handler
// grants: the stage's <stage>_item_id, else its <stage>_sprite_id. Stage 0=egg, 1=larva, 2=pupa. Stage item/
// sprite ids are unique per species+stage, so first match is unambiguous (map order irrelevant; not sim state).
func (m *Match) broodItemStage(state *WorldState, itemID string) (string, int, bool) {
	if itemID == "" {
		return "", 0, false
	}
	for sid, sp := range state.Species {
		if sp == nil {
			continue
		}
		stages := [3][2]string{
			{sp.EggItemID, sp.EggSpriteID},
			{sp.LarvaItemID, sp.LarvaSpriteID},
			{sp.PupaItemID, sp.PupaSpriteID},
		}
		for st, pair := range stages {
			id := pair[0]
			if id == "" {
				id = pair[1]
			}
			if id != "" && id == itemID {
				return sid, st, true
			}
		}
	}
	return "", 0, false
}

// handleNurseryDeposit places brood units FROM a bag slot INTO a compatible nursery — the reciprocal of take
// (relocate / top-up a brood). The held item's species+stage is reverse-resolved; the deposit is accepted only
// if the species matches the nursery's (a fly larva can't go in a wasp nest). Tops up an existing brood, or
// seeds an empty NEST (whose species is known via NestState). Capacity-clamped. Server-soft, like take.
func (m *Match) handleNurseryDeposit(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg NurseryDepositMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Range check (same 3.0 allowance).
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		return
	}

	if msg.Slot < 0 || msg.Slot >= len(player.ItemSlots) {
		return
	}
	itemID := player.ItemSlots[msg.Slot].ItemID
	have := player.ItemSlots[msg.Slot].Count
	if itemID == "" || have <= 0 {
		return
	}

	species, stage, ok := m.broodItemStage(state, itemID)
	if !ok {
		return // the held item isn't a brood stage item
	}

	// Resolve the nursery: an existing brood (any species) → must match; else a NEST (species known) → seed it;
	// else reject (an empty non-nest — species is set by whoever breeds there, not by a deposit).
	key := broodKey(msg.GX, msg.GY)
	b := state.BroodStates[key]
	if b == nil {
		nest := state.NestStates[key]
		if nest == nil || nest.SpeciesID != species {
			return
		}
		b = m.getOrCreateBrood(state, msg.GX, msg.GY, species, "nest", "", state.Tuning.NestBroodCap)
	}
	if b.SpeciesID != species {
		return // wrong species for this nursery
	}

	// Capacity-clamp against the brood cap and what the slot actually holds / the player asked for.
	room := b.CapEggs - (b.Eggs + b.Maggots + b.Pupae)
	if room <= 0 {
		return
	}
	n := have
	if msg.Count > 0 && msg.Count < n {
		n = msg.Count
	}
	if n > room {
		n = room
	}
	if n <= 0 {
		return
	}

	switch stage {
	case 0:
		b.Eggs += n
	case 1:
		b.Maggots += n
	case 2:
		b.Pupae += n
	default:
		return
	}
	player.RemoveItem(msg.Slot, n)

	m.broadcastBroodUpdate(dispatcher, state, b, false)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		_ = m.sendInventorySync(logger, dispatcher, player, presence)
	}
	logger.Info("NurseryDeposit: %s placed %d %s (stage %d) into %s brood at %d,%d",
		userID, n, itemID, stage, species, msg.GX, msg.GY)
}
