package world

import (
	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// The Ecology Director — a per-species THREE-TIER control ladder that keeps a zone lively and bounded
// without the player, with NATURAL oscillation (food/predation/starvation) owning the middle band. On a
// slow clock it watches each species vs its bands and acts only at the edges, gentlest-first:
//
//	pop < MinPopulation (extreme low)  -> RE-SEED              (last-resort anti-extinction floor)
//	pop < EventLow      (moderate low) -> EXTRA-RAIN  request  (environmental: more fruit/nectar -> food up)
//	[EventLow .. EventHigh]            -> nothing              (natural dynamics own this band)
//	pop > EventHigh     (moderate high)-> DROUGHT     request  (environmental: suppress rain -> food tightens)
//	pop > CullAt        (extreme high) -> HARD CULL            (last resort; CullWith predator pulse or direct)
//
// The environmental tier doesn't touch bugs at all — it nudges the WEATHER (the food governor), so the
// population eases toward the band on its own. Rain is ONE global, so requests are resolved per pass by
// "relief beats suppression": any extra-rain request (a species near collapse) cancels every drought
// request (an overshoot we can still hard-cull) — losing a species is worse than an overshoot.
//
// All actions are server-authoritative and ride the existing vocabulary (spawnSwarmForSpecies /
// spawnSwarmAt -> SwarmUpdate+SWARM_SET_TARGET, killBugsNaturally -> BUG_REMOVED, weather = soft display
// state) — zero new sim event types, determinism intact. The player-facing TASK tier layers on in P-ECO-6.

const (
	directorIntervalTicks = 1200 // run every ~2 sim-min: populations move slowly; don't over-react
	directorPredatorCount = 3    // bugs in a released predator pulse
	droughtDays           = 2    // game-days a moderate-high drought suppresses rain (re-armed each pass if still high)
)

func (m *Match) processEcologyDirector(logger runtime.Logger, dispatcher runtime.MatchDispatcher, state *WorldState, chunkSize int) {
	if state.StaticSim || state.CurrentZone == nil || state.CurrentZone.BugSpawning == nil {
		return
	}
	wantRain, wantDrought := false, false

	for _, speciesID := range sortedStringKeys(state.CurrentZone.BugSpawning.SpeciesCaps) { // sorted: reseed mints IDs
		cap := state.CurrentZone.BugSpawning.SpeciesCaps[speciesID]
		if cap.MinPopulation <= 0 && cap.EventLow <= 0 && cap.EventHigh <= 0 && cap.CullAt <= 0 {
			continue // no director bands configured for this species
		}
		pop := state.SpeciesPopulation(speciesID)

		// LOW side. Re-seed only at the extreme floor; request extra-rain anywhere below EventLow (food
		// help is additive with a re-seed — a critically low prey base needs both bugs AND fruit).
		if cap.MinPopulation > 0 && pop < cap.MinPopulation {
			if sw := m.spawnSwarmForSpecies(state, speciesID, logger); sw != nil {
				state.Stats.recordBirth(speciesID, BirthReseed, sw.Count)
				logger.Info("Director: re-seeded %s (pop %d < min %d)", speciesID, pop, cap.MinPopulation)
			}
		}
		if cap.EventLow > 0 && pop < cap.EventLow {
			wantRain = true
		}

		// HIGH side (graded, not additive): hard-cull at the extreme ceiling, ELSE a drought nudge in the
		// moderate-high band. Culling already brings it to CullAt, so don't also drought it.
		if cap.CullAt > 0 && pop > cap.CullAt {
			if cap.CullWith != "" {
				cx, cy := m.speciesCentroid(state, speciesID, chunkSize)
				if sw := m.spawnSwarmAt(state, cap.CullWith, directorPredatorCount, cx, cy, chunkSize); sw != nil {
					state.Stats.recordBirth(cap.CullWith, BirthReseed, sw.Count)
					logger.Info("Director: released %s on %s (pop %d > cull_at %d)", cap.CullWith, speciesID, pop, cap.CullAt)
				}
			} else {
				m.directorCull(logger, dispatcher, state, speciesID, pop-cap.CullAt, chunkSize)
				logger.Info("Director: overcrowding cull of %s (pop %d -> %d)", speciesID, pop, cap.CullAt)
			}
		} else if cap.EventHigh > 0 && pop > cap.EventHigh {
			wantDrought = true
		}
	}

	// Resolve the shared global weather: relief beats suppression (one action per pass).
	if wantRain {
		m.requestExtraRain(state, dispatcher, logger)
	} else if wantDrought {
		m.requestDrought(state, logger, state.Tuning.DroughtDays)
	}
}

// speciesCentroid returns the average world position of a species' swarms (where to drop a predator).
func (m *Match) speciesCentroid(state *WorldState, speciesID string, chunkSize int) (float32, float32) {
	var sx, sy float32
	var n int
	for _, id := range state.SwarmsBySpecies[speciesID] {
		if sw, ok := state.Swarms[id]; ok {
			sx += sw.WorldX(chunkSize)
			sy += sw.WorldY(chunkSize)
			n++
		}
	}
	if n == 0 {
		return 0, 0
	}
	return sx / float32(n), sy / float32(n)
}

// directorCull removes `total` bugs of a species, spread across its swarms proportionally (largest
// first), to bring it down to the band. Collect-then-act so killBugsNaturally's empty-swarm despawn
// can't mutate the map mid-range.
func (m *Match) directorCull(logger runtime.Logger, dispatcher runtime.MatchDispatcher, state *WorldState, speciesID string, total, chunkSize int) {
	if total <= 0 {
		return
	}
	species := state.Species[speciesID]
	pop := state.SpeciesPopulation(speciesID)
	if pop <= 0 {
		return
	}
	type cull struct {
		swarm *entities.SwarmState
		ids   []int
	}
	var culls []cull
	for _, id := range state.SwarmsBySpecies[speciesID] {
		sw, ok := state.Swarms[id]
		if !ok || sw.Count <= 0 {
			continue
		}
		// this swarm's share of the total cull, proportional to its size
		n := int(float32(total) * float32(sw.Count) / float32(pop))
		if n < 1 {
			n = 1
		}
		if n > sw.Count {
			n = sw.Count
		}
		if ids := sw.FirstAliveBugIDs(n); len(ids) > 0 {
			culls = append(culls, cull{sw, ids})
		}
	}
	for _, c := range culls {
		state.Stats.recordDeath(c.swarm.SpeciesID, DeathCull, len(c.ids))
		m.killBugsNaturally(logger, dispatcher, state, c.swarm, species, c.ids, chunkSize)
	}
}
