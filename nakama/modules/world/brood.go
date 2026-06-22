package world

import (
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Visible breeding broods. Flies/butterflies LAY eggs into a BroodState at their breeding source
// (compost bin, milkweed, or a transient maggot pile on rotten ground-fruit) instead of growing
// instantly; processBroods matures eggs -> maggots and HATCHES bugs via the proven growSwarm /
// spawnSwarmAt -> SWARM_REPRODUCED paths. Broods are server-only soft state (never hashed, never in the
// late-join snapshot); the BroodUpdate broadcast is display-only. Wasp nests keep their own NestState
// economy (handlers in nests.go) — this file is the non-predator sources only.

const broodHatchJoinRadius = 4.0 // a hatch grows a same-species swarm camped this close, else mints one

// broodKey is the "gx,gy" map key for a brood at a cell.
func broodKey(gx, gy int) string { return fmt.Sprintf("%d,%d", gx, gy) }

// broodAreaSize: ground-pile maggot broods are SHARED across this NxN-cell area (≈ one pile per tree's
// windfall) instead of one-per-apple, so every local fly lays into a single persistent, maturing pile.
const broodAreaSize = 4

// broodAreaKey snaps a cell to its area origin — the shared ground-pile maggot-brood cell for that area.
func broodAreaKey(gx, gy int) (int, int) {
	return (gx / broodAreaSize) * broodAreaSize, (gy / broodAreaSize) * broodAreaSize
}

// getOrCreateBrood returns the brood at (gx,gy), creating it bound to its source if absent.
// Ground-pile (fly) broods get a "g:" key namespace so an area-snapped fly pile can never collide with a
// host-plant (milkweed) or station brood that uses the SAME exact cell — without it, a milkweed sitting on
// an area-origin cell (gx,gy both %4==0) would share a map slot with a fly pile and one species would lay
// into / hatch from the other's brood.
func (m *Match) getOrCreateBrood(state *WorldState, gx, gy int, speciesID, sourceKind, sourceID string, capEggs int) *entities.BroodState {
	key := broodKey(gx, gy)
	if sourceKind == "ground_pile" {
		key = "g:" + key
	}
	b := state.BroodStates[key]
	if b == nil {
		b = &entities.BroodState{
			GridX: gx, GridY: gy, SpeciesID: speciesID,
			SourceKind: sourceKind, SourceID: sourceID, CapEggs: capEggs,
		}
		state.BroodStates[key] = b
	}
	return b
}

// layEggs deposits n eggs into the brood at (gx,gy), clamped at the brood's capacity. Returns how many
// were actually accepted (0 if the nursery is full). Called from the reproduceSwarm redirect.
func (m *Match) layEggs(dispatcher runtime.MatchDispatcher, state *WorldState, b *entities.BroodState, n int) int {
	room := b.CapEggs - (b.Eggs + b.Maggots)
	if room <= 0 {
		return 0
	}
	if n > room {
		n = room
	}
	b.Eggs += n
	m.broadcastBroodUpdate(dispatcher, state, b, false)
	return n
}

// layIntoBrood resolves the reproducing swarm's breeding source (compost station / milkweed host plant /
// rotten-fruit ground pile) and lays `count` eggs into the brood there. Returns true if any were
// accepted (false: unknown source, or the nursery is full). The pile is sized by the food it sits on.
func (m *Match) layIntoBrood(state *WorldState, dispatcher runtime.MatchDispatcher, swarm *entities.SwarmState, count int) bool {
	gx, gy := int(swarm.TargetFoodX), int(swarm.TargetFoodY)
	capEggs := entities.BroodDefaultCapEggs

	var kind, sourceID string
	if state.Stations[swarm.TargetFoodID] != nil {
		kind, sourceID = "station", swarm.TargetFoodID
	} else if state.HostPlantStates[broodKey(gx, gy)] != nil {
		kind = "host_plant"
	} else if it, ok := state.GroundItems[swarm.TargetFoodID]; ok && it.FoodValue > 0 {
		// SHARED per-AREA maggot pile (≈ one per tree's windfall), NOT bound to this single apple. The
		// apple is eaten within seconds (feeding drain + the breed food-cost), but the maggots laid in it
		// must keep developing (10s+ each to mature). So we snap the brood to a coarse area cell — every
		// local fly lays into the SAME persistent pile — and detach it from the apple's lifetime: the food
		// is already paid at lay time, so broodSourceGone never fires for a ground pile and processBroods
		// retires the pile only once it has fully hatched out. capEggs stays the shared default (set above).
		kind, sourceID = "ground_pile", ""
		gx, gy = broodAreaKey(gx, gy)
		_ = it
	} else {
		return false // no recognizable breeding source at the target
	}

	b := m.getOrCreateBrood(state, gx, gy, swarm.SpeciesID, kind, sourceID, capEggs)
	return m.layEggs(dispatcher, state, b, count) > 0
}

// processBroods (slow clock, beside processNests) matures eggs -> maggots and hatches maggots -> bugs,
// and sweeps broods whose source is gone. Collect-then-delete (no map mutation mid-range).
func (m *Match) processBroods(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	const interval = 30 // call cadence (ticks); matches the processNests slow clock
	var toDelete []string

	for _, key := range sortedStringKeys(state.BroodStates) { // sorted: hatches mint swarm IDs
		b := state.BroodStates[key]
		// 1) Source-gone sweep: hatch whatever matured, then clear.
		if m.broodSourceGone(state, b) {
			for b.Maggots > 0 {
				if hatched := m.hatchFromBrood(state, b); hatched == 0 {
					break // at the population/swarm cap — drop the rest with the vanishing source
				}
			}
			m.broadcastBroodUpdate(dispatcher, state, b, true)
			toDelete = append(toDelete, key)
			continue
		}

		changed := false

		// 2) Mature one egg -> maggot per BroodEggMatureTicks.
		if b.Eggs > 0 {
			b.StageProgress += interval
			if b.StageProgress >= entities.BroodEggMatureTicks {
				b.StageProgress -= entities.BroodEggMatureTicks
				b.Eggs--
				b.Maggots++
				changed = true
			}
		}

		// 3) Hatch matured maggots (cap-gated inside hatchFromBrood).
		if b.Maggots > 0 {
			if hatched := m.hatchFromBrood(state, b); hatched > 0 {
				changed = true
			}
		}

		if changed {
			m.broadcastBroodUpdate(dispatcher, state, b, false)
		}

		// A ground pile isn't tied to a vanishing apple: retire it once it has fully hatched out (no eggs
		// or maggots left) so a tree's between-fruitings don't leave empty piles lingering. Active piles
		// (a fly bred there this cycle) keep ≥1 egg and survive.
		if b.SourceKind == "ground_pile" && b.Eggs == 0 && b.Maggots == 0 {
			m.broadcastBroodUpdate(dispatcher, state, b, true)
			toDelete = append(toDelete, key)
		}
	}

	for _, key := range toDelete {
		delete(state.BroodStates, key)
	}
}

// broodSourceGone reports whether the brood's backing source has disappeared.
func (m *Match) broodSourceGone(state *WorldState, b *entities.BroodState) bool {
	switch b.SourceKind {
	case "ground_pile":
		// A laid maggot pile develops on its own (the food was consumed at lay time); it is never
		// "source-gone". processBroods retires it once empty (all eggs matured + hatched out).
		return false
	case "station":
		return state.Stations[b.SourceID] == nil
	case "host_plant":
		return state.HostPlantStates[broodKey(b.GridX, b.GridY)] == nil
	}
	return false
}

// hatchFromBrood turns up to BroodHatchCount maggots into bugs at the brood cell — growing the nearest
// same-species swarm camped there (the breeder) or, failing that, minting a small new swarm. Returns the
// number hatched (0 if held at the population/swarm cap). Mirrors the nest hatch + reproduceSwarm caps.
func (m *Match) hatchFromBrood(state *WorldState, b *entities.BroodState) int {
	species := state.Species[b.SpeciesID]
	if species == nil || b.Maggots <= 0 {
		return 0
	}
	n := entities.BroodHatchCount
	if n > b.Maggots {
		n = b.Maggots
	}

	// Population cap: hold maggots if there's no room (the nest's at-cap banking).
	if maxPop := state.SpeciesMaxPopulation(b.SpeciesID); maxPop > 0 {
		room := maxPop - state.SpeciesPopulation(b.SpeciesID)
		if room < n {
			n = room
		}
		if n <= 0 {
			return 0
		}
	}

	chunkSize := state.Config.ChunkSize
	cellX := float32(b.GridX) + 0.5
	cellY := float32(b.GridY) + 0.5

	if target := m.nearestSwarmNear(state, b.SpeciesID, cellX, cellY, broodHatchJoinRadius, chunkSize); target != nil {
		m.growSwarm(state, target, n) // SWARM_REPRODUCED into the camped swarm
	} else {
		// No swarm to join: mint one, honoring the zone swarm-count cap (else hold).
		if state.CurrentZone != nil && state.CurrentZone.BugSpawning != nil {
			if zcap, ok := state.CurrentZone.BugSpawning.SpeciesCaps[b.SpeciesID]; ok &&
				zcap.Max > 0 && state.AliveSwarmCount(b.SpeciesID) >= zcap.Max {
				return 0
			}
		}
		if m.spawnSwarmAt(state, b.SpeciesID, n, cellX, cellY, chunkSize) == nil {
			return 0
		}
	}
	state.Stats.recordBirth(b.SpeciesID, BirthBrood, n) // both paths minted n bugs from the brood
	b.Maggots -= n
	return n
}

// nearestSwarmNear returns the closest same-species swarm whose centre is within radius of (x,y), or nil.
func (m *Match) nearestSwarmNear(state *WorldState, speciesID string, x, y, radius float32, chunkSize int) *entities.SwarmState {
	var best *entities.SwarmState
	bestD := radius * radius
	for _, id := range state.SwarmsBySpecies[speciesID] {
		sw, ok := state.Swarms[id]
		if !ok {
			continue
		}
		dx := sw.WorldX(chunkSize) - x
		dy := sw.WorldY(chunkSize) - y
		if d := dx*dx + dy*dy; d <= bestD {
			bestD = d
			best = sw
		}
	}
	return best
}

// onBroodSourceRemoved is the breakOccupantAt hook: a broken compost/milkweed clears its brood at once
// (the slow sweep is only a backstop). Hatch nothing — a destroyed source loses its in-progress brood.
func (m *Match) onBroodSourceRemoved(state *WorldState, dispatcher runtime.MatchDispatcher, gx, gy int) {
	key := broodKey(gx, gy)
	if b := state.BroodStates[key]; b != nil {
		m.broadcastBroodUpdate(dispatcher, state, b, true)
		delete(state.BroodStates, key)
	}
}

// broadcastBroodUpdate sends a display-only nursery update to the brood's chunk subscribers.
func (m *Match) broadcastBroodUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, b *entities.BroodState, removed bool) {
	chunkSize := state.Config.ChunkSize
	cx, cy := b.GridX/chunkSize, b.GridY/chunkSize
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBroodUpdate, BroodUpdateMessage{
		GX: b.GridX, GY: b.GridY, Species: b.SpeciesID,
		Eggs: b.Eggs, Maggots: b.Maggots, Kind: b.SourceKind, Removed: removed,
	})
}
