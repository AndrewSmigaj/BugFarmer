package world

import (
	"encoding/json"
	"fmt"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// handleReleaseBugs (OpCode 29): release n bugs from a bug slot AT the clicked world point.
// If a same-species swarm is within max(species.MergeRadius, swarm.Radius) of the click,
// the bugs JOIN it — via the same SWARM_REPRODUCED ledger event reproduction uses (the
// client handler is a deterministic, idempotent SpawnBugAt loop; meters untouched here).
// Otherwise a NEW swarm spawns at the click (wall-clamped), announced via SwarmsDirty —
// the same path continuous spawning uses (live clients spawn deterministic visuals from
// the SwarmUpdate metadata; late joiners reconcile via MatchJoin's SwarmsDirty bootstrap).
//
// The snap radius takes max() with the swarm's VISUAL radius deliberately: fly merge_radius
// (2.5) is smaller than swarm_radius (4.0), so a bare-MergeRadius rule would let a click on
// a swarm's visible fringe bugs spawn an overlapping duplicate that the merge pass (center
// distance <= merge_radius) never fuses. max() = "click inside the cloud, join the cloud".
//
// Known caveat (pre-existing class, shared with continuous spawning): SwarmUpdate applies
// on receipt while state hashing is per-tick, so a lagging client can theoretically trip
// one drift-sample round per creation (~0.3-1%/release) — minority resync self-heals.
// BACKLOG: zone swarm-count cap for releases (force add-to-nearest / reject above N).
func (m *Match) handleReleaseBugs(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg ReleaseBugsMessage,
	playerID string,
	chunkSize int,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}
	if msg.SlotIndex < 0 || msg.SlotIndex >= len(player.BugSlots) {
		return
	}
	slot := &player.BugSlots[msg.SlotIndex]
	if slot.ItemID == "" || slot.Count <= 0 {
		return
	}
	speciesID := slot.ItemID
	species := state.Species[speciesID]
	if species == nil {
		logger.Warn("ReleaseBugs: unknown species %s in slot %d", speciesID, msg.SlotIndex)
		return
	}

	n := msg.Count
	if n < 0 {
		n = slot.Count
	}
	if n <= 0 {
		return
	}
	if n > slot.Count {
		n = slot.Count
	}

	// Reach: player -> release point (4.0 client + 0.5 slack, the catch convention)
	px := player.WorldX(chunkSize)
	py := player.WorldY(chunkSize)
	dx := msg.X - px
	dy := msg.Y - py
	const releaseReach = 4.5
	if dx*dx+dy*dy > releaseReach*releaseReach {
		return
	}

	// The only fallible op — do it first.
	if !player.RemoveBugs(msg.SlotIndex, n) {
		return
	}

	// Nearest same-species swarm whose snap radius covers the click → the bugs JOIN it.
	var target *entities.SwarmState
	bestDistSq := float32(0)
	for _, swarmID := range state.SwarmsBySpecies[speciesID] {
		swarm, ok := state.Swarms[swarmID]
		if !ok {
			continue
		}
		sdx := msg.X - swarm.WorldX(chunkSize)
		sdy := msg.Y - swarm.WorldY(chunkSize)
		distSq := sdx*sdx + sdy*sdy
		snap := species.MergeRadius
		if swarm.Radius > snap {
			snap = swarm.Radius
		}
		if distSq <= snap*snap && (target == nil || distSq < bestDistSq) {
			target = swarm
			bestDistSq = distSq
		}
	}

	if target != nil {
		// JOIN: mirror reproduceSwarm's id math exactly, WITHOUT touching meters.
		// Over MaxSwarmSize is fine — the deterministic split pass rebalances next tick.
		if target.NextBugID == 0 {
			target.NextBugID = target.Count // lazy-init guard (reproduceSwarm parity)
		}
		base := target.NextBugID
		target.NextBugID += n
		target.Count += n
		if state.CurrentZone != nil {
			state.AddSwarmReproducedEvent(state.CurrentZone.ZoneID, target.ID, n, base)
		}
		logger.Info("Player %s released %d %s into swarm %s (now %d)",
			playerID, n, speciesID, target.ID, target.Count)
	} else {
		// NEW swarm at the click, clamped so it can't land inside a wall.
		rx, ry := entities.RaycastClamp(px, py, msg.X, msg.Y, func(x, y float32) bool {
			return state.IsBlocked(x, y)
		})
		pos := entities.EntityPosition{LocalX: rx, LocalY: ry}
		pos.Normalize(chunkSize)

		id, _ := uuid.NewV4()
		swarm := &entities.SwarmState{
			ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
			SpeciesID: speciesID,
			Position:  pos,
			Radius:    species.SwarmRadius,
			Count:     n,
			WanderRad: species.WanderRadius,
			HomePos:   pos,
		}
		swarm.InitializeBugIDs()

		state.Swarms[swarm.ID] = swarm
		state.SwarmsBySpecies[speciesID] = append(state.SwarmsBySpecies[speciesID], swarm.ID)
		state.SwarmsDirty = true
		// NextThinkTick stays 0: the swarm Thinks THIS tick, emitting its anchoring
		// SWARM_SET_TARGET leg after the SwarmUpdate and before the frontier.

		logger.Info("Player %s released %d %s as new swarm %s at (%.1f, %.1f)",
			playerID, n, speciesID, swarm.ID, rx, ry)
	}

	// Echo the slot to the releaser only (the cursor echo-interception handles the client).
	slotMsg := SlotUpdateMessage{
		SlotIndex: msg.SlotIndex,
		ItemID:    slot.ItemID,
		Count:     slot.Count,
	}
	data, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[playerID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeBugSlotUpdate, data,
			[]runtime.Presence{presence}, nil, true)
	}
}
