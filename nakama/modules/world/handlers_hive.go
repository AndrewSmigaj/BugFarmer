package world

import (
	"encoding/json"
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"
)

// Hive harvest (beekeeping): right-click a hive → pull the whole honeycombs into the bag
// (the tree-harvest pattern, no panel). Harvesting a live colony's hive RECALLS ITS
// DEFENDERS onto you unless the hive was freshly smoked — the bee suit negates the stings,
// not the anger (angry cloud + calm keeper is the fantasy). Honey/honeycomb are
// display/inventory yield only — never a bug-sim input, never hashed; the recall rides the
// ordinary defend legs (SWARM_SET_TARGET), so no new ledger vocabulary.

func (m *Match) handleHiveHarvest(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg HiveHarvestMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Range check (same 3.0 allowance as container/station/shop interactions).
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendHiveHarvestAck(dispatcher, state, userID, false, 0, "Too far away")
		return
	}

	nest := state.NestStates[fmt.Sprintf("%d,%d", msg.GX, msg.GY)]
	if nest == nil {
		m.sendHiveHarvestAck(dispatcher, state, userID, false, 0, "No hive there")
		return
	}

	// Poking a live colony's hive angers it — harvest OR empty-handed prodding alike —
	// unless the smoke is fresh (recallNestDefenders no-ops while smoked). This is what
	// makes the smoker/suit loop real.
	m.recallNestDefenders(state, msg.GX, msg.GY, userID)

	combs := int(nest.Honey)
	if combs <= 0 {
		m.sendHiveHarvestAck(dispatcher, state, userID, false, 0, "No honeycomb in this hive yet")
		return
	}
	if player.AddItem("honeycomb", combs) < 0 {
		m.sendHiveHarvestAck(dispatcher, state, userID, false, 0, "Your bag is full")
		return
	}
	nest.Honey -= float32(combs)

	if presence, ok := state.Presences[userID]; ok && presence != nil {
		_ = m.sendInventorySync(logger, dispatcher, player, presence)
	}
	smoked := nest.SmokedUntilTick > state.TickCount
	note := "The hive SEETHES!"
	if smoked {
		note = "The smoke keeps them calm."
	} else if _, alive := state.Swarms[nest.ResidentSwarmID]; !alive || nest.ResidentSwarmID == "" {
		note = "The hive is quiet."
	}
	m.sendHiveHarvestAck(dispatcher, state, userID, true, combs,
		fmt.Sprintf("+%d honeycomb. %s", combs, note))
	logger.Info("HiveHarvest: %s took %d honeycomb at %d,%d (smoked=%v)", userID, combs, msg.GX, msg.GY, smoked)
}

// sendHiveHarvestAck: presence-targeted result toast (the SetHomeAck pattern).
func (m *Match) sendHiveHarvestAck(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, ok bool, count int, message string) {
	msg := HiveHarvestAckMessage{OK: ok, Count: count, Message: message}
	data, err := json.Marshal(msg)
	if err != nil {
		return
	}
	if presence, exists := state.Presences[userID]; exists && presence != nil {
		dispatcher.BroadcastMessage(OpCodeHiveHarvestAck, data, []runtime.Presence{presence}, nil, true)
	}
}
