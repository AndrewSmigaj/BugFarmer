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
// growSwarm is THE single id-math for adding n bugs to an existing swarm: lazy
// NextBugID init, ascending new ids from the base, Count, and the SWARM_REPRODUCED
// ledger event (clients SpawnBugAt the center at the event tick — idempotent).
// Three callers share it (reproduceSwarm, release-join, nest hatch); callers own
// caps, meters, cooldowns, and food costs. Returns the first new bug id.
func (m *Match) growSwarm(state *WorldState, swarm *entities.SwarmState, n int) int {
	if swarm.NextBugID == 0 {
		swarm.NextBugID = swarm.Count // lazy-init guard
	}
	base := swarm.NextBugID
	swarm.NextBugID += n
	swarm.Count += n
	// New bugs are born now → schedule their natural death.
	assignDeathTicks(swarm, state.Species[swarm.SpeciesID], base, base+n, state.TickCount, SimRate)
	if state.CurrentZone != nil {
		state.AddSwarmReproducedEvent(state.CurrentZone.ZoneID, swarm.ID, n, base)
	}
	return base
}

// assignDeathTicks schedules natural death for bug ids [idStart,idEnd) born at bornTick: each gets
// DeathTick = bornTick + lifespan ± a deterministic per-bug spread (so a cohort doesn't all die at
// once). No-op for immortal species (lifespan_secs<=0). The value is stored + carried with the bug
// (NOT recomputed from ids, which change on merge/split).
func assignDeathTicks(swarm *entities.SwarmState, species *entities.BugSpecies, idStart, idEnd int, bornTick int64, tickRate int) {
	if species == nil || species.LifespanSecs <= 0 || idEnd <= idStart {
		return
	}
	if tickRate <= 0 {
		tickRate = 10
	}
	if swarm.DeathTick == nil {
		swarm.DeathTick = make(map[int]int64)
	}
	lifeTicks := int64(species.LifespanSecs * float32(tickRate))
	spreadTicks := int64(species.LifespanSpreadSecs * float32(tickRate))
	for id := idStart; id < idEnd; id++ {
		off := int64(0)
		if spreadTicks > 0 {
			off = (deathVarianceHash(swarm.ID, id) % (2*spreadTicks + 1)) - spreadTicks
		}
		swarm.DeathTick[id] = bornTick + lifeTicks + off
	}
}

// deathVarianceHash: deterministic non-negative hash of (swarmID, bugID) → per-bug lifespan spread.
func deathVarianceHash(swarmID string, bugID int) int64 {
	h := uint64(14695981039346656037) // FNV-1a 64 offset basis
	for i := 0; i < len(swarmID); i++ {
		h ^= uint64(swarmID[i])
		h *= 1099511628211
	}
	h ^= uint64(bugID)
	h *= 1099511628211
	return int64(h & 0x7fffffffffffffff)
}

// spawnSwarmAt creates a new swarm of n bugs at a world point — the single mint path
// shared by player releases and the F8 debug spawn (same on-receipt mid-tick class as
// §12.2 releases: the swarm Thinks THIS tick and anchors via SWARM_SET_TARGET).
// Callers do their own cap checks and wall clamping. Returns nil for unknown species.
func (m *Match) spawnSwarmAt(state *WorldState, speciesID string, n int, x, y float32, chunkSize int) *entities.SwarmState {
	species := state.Species[speciesID]
	if species == nil || n <= 0 {
		return nil
	}

	pos := entities.EntityPosition{LocalX: x, LocalY: y}
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
	assignDeathTicks(swarm, species, 0, n, state.TickCount, SimRate)

	state.Swarms[swarm.ID] = swarm
	state.SwarmsBySpecies[speciesID] = append(state.SwarmsBySpecies[speciesID], swarm.ID)
	state.SwarmsDirty = true
	// NextThinkTick stays 0: the swarm Thinks THIS tick, emitting its anchoring
	// SWARM_SET_TARGET leg after the SwarmUpdate and before the frontier.
	return swarm
}

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

	// HARD population cap (the crash guard, §13): a release near the cap must reject
	// VISIBLY with the slot untouched — before any mutation, covering BOTH branches
	// (join and new-swarm). Without this, "catch a jar of flies, walk to the overrun
	// orchard, release" would mint unbounded entities.
	if maxPop := state.SpeciesMaxPopulation(speciesID); maxPop > 0 &&
		state.SpeciesPopulation(speciesID)+n > maxPop {
		m.sendWorldError(dispatcher, state, playerID, "The zone is overrun — they won't stay")
		return
	}

	// Nearest same-species swarm whose snap radius covers the click → the bugs JOIN it.
	// Track the nearest swarm at ANY distance too: at the swarm-COUNT cap a release
	// can't mint a new swarm, so the bugs force-join the nearest one instead (§12.2
	// resolved — the player keeps their bugs; the split pass rebalances overgrowth).
	var target, nearest *entities.SwarmState
	bestDistSq, nearestDistSq := float32(0), float32(0)
	for _, swarmID := range state.SwarmsBySpecies[speciesID] {
		swarm, ok := state.Swarms[swarmID]
		if !ok {
			continue
		}
		sdx := msg.X - swarm.WorldX(chunkSize)
		sdy := msg.Y - swarm.WorldY(chunkSize)
		distSq := sdx*sdx + sdy*sdy
		if nearest == nil || distSq < nearestDistSq {
			nearest = swarm
			nearestDistSq = distSq
		}
		snap := species.MergeRadius
		if swarm.Radius > snap {
			snap = swarm.Radius
		}
		if distSq <= snap*snap && (target == nil || distSq < bestDistSq) {
			target = swarm
			bestDistSq = distSq
		}
	}

	// Swarm-count cap (spawn back-pressure): no new swarm at/over it — force-join.
	if target == nil && state.CurrentZone != nil && state.CurrentZone.BugSpawning != nil {
		if cap, ok := state.CurrentZone.BugSpawning.SpeciesCaps[speciesID]; ok && cap.Max > 0 &&
			state.AliveSwarmCount(speciesID) >= cap.Max {
			if nearest == nil {
				// Unreachable while Max > 0 (at-cap implies swarms exist) — belt+braces.
				m.sendWorldError(dispatcher, state, playerID, "The zone is overrun — they won't stay")
				return
			}
			target = nearest
			logger.Info("Release at the %s swarm cap: force-joining nearest swarm %s", speciesID, nearest.ID)
		}
	}

	// The only fallible op — after every reject path, before every mutation.
	if !player.RemoveBugs(msg.SlotIndex, n) {
		return
	}

	if target != nil {
		// JOIN: the shared growSwarm id-math, WITHOUT touching meters.
		// Over MaxSwarmSize is fine — the population pass (600-tick cadence) splits it;
		// note the split pair sums past MaxSwarmSize, so merges never re-fuse it (the
		// documented, bounded swarm-count overage — see SpeciesCap).
		m.growSwarm(state, target, n)
		logger.Info("Player %s released %d %s into swarm %s (now %d)",
			playerID, n, speciesID, target.ID, target.Count)
	} else {
		// NEW swarm at the click, clamped so it can't land inside a wall.
		rx, ry := entities.RaycastClamp(px, py, msg.X, msg.Y, func(x, y float32) bool {
			return state.IsBlocked(x, y)
		})
		swarm := m.spawnSwarmAt(state, speciesID, n, rx, ry, chunkSize)
		if swarm == nil {
			player.AddBugs(speciesID, n) // shouldn't happen; don't eat the bugs
			return
		}
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
