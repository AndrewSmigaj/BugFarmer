package world

import (
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Wasp nests (architecture_swarm_sync.md §14): the fruit-tree pattern — occupant-backed
// in-memory states scanned at chunk load, swept when the occupant disappears, no
// persistence (a destroyed nest resurrects on server restart, like every broken
// occupant; documented). The nest OWNS a resident swarm and converts brood deposits
// into hatches via the shared growSwarm id-math (SWARM_REPRODUCED — zero new ledger
// vocabulary). NestState is deliberately species-generic (bees later: a `Deposit`
// field + a yield item on the nest def).

// speciesForNestOccupant finds the species whose nest this occupant type is.
func (m *Match) speciesForNestOccupant(state *WorldState, occupantID string) (string, *entities.BugSpecies) {
	for id, sp := range state.Species {
		if sp.Predation != nil && sp.Predation.NestOccupant == occupantID {
			return id, sp
		}
	}
	return "", nil
}

// initNestsInChunk scans a loaded chunk for nest occupants and registers their states,
// founding the resident patrol (cap-aware). Mirrors initFruitTreesInChunk: the nest
// "comes alive" when a player first approaches its chunk (same class as fruit trees;
// wild prey spawning is zone-wide from match start — accepted asymmetry).
func (m *Match) initNestsInChunk(
	state *WorldState,
	chunk *ChunkData,
	cx, cy int,
	logger runtime.Logger,
) {
	chunkSize := state.Config.ChunkSize

	for ly := 0; ly < chunkSize; ly++ {
		for lx := 0; lx < chunkSize; lx++ {
			cell, _ := chunk.GetOccupantCell(lx, ly)
			if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
				continue
			}
			speciesID, species := m.speciesForNestOccupant(state, cell.Occupant.ID)
			if species == nil {
				continue
			}

			gx := cx*chunkSize + lx
			gy := cy*chunkSize + ly
			key := fmt.Sprintf("%d,%d", gx, gy)
			if state.NestStates[key] != nil {
				continue
			}

			nest := &entities.NestState{
				GridX: gx, GridY: gy,
				EntityID:  cell.Occupant.ID,
				SpeciesID: speciesID,
			}
			state.NestStates[key] = nest

			// Found the resident patrol (cap-aware; a saturated zone founds dormant)
			m.nestSpawnResident(state, nest, species, entities.NestFoundingSize, logger)
			logger.Debug("Initialized %s nest at %d,%d (resident=%q)", speciesID, gx, gy, nest.ResidentSwarmID)
		}
	}
}

// nestSpawnResident mints a resident swarm of up to n at the nest, honoring the §13
// population cap (partial founding at the boundary; zero = dormant until room exists).
func (m *Match) nestSpawnResident(
	state *WorldState,
	nest *entities.NestState,
	species *entities.BugSpecies,
	n int,
	logger runtime.Logger,
) {
	if maxPop := state.SpeciesMaxPopulation(nest.SpeciesID); maxPop > 0 {
		room := maxPop - state.SpeciesPopulation(nest.SpeciesID)
		if room < n {
			n = room
		}
	}
	if n <= 0 {
		return
	}

	chunkSize := state.Config.ChunkSize
	swarm := m.spawnSwarmAt(state, nest.SpeciesID, n,
		float32(nest.GridX)+0.5, float32(nest.GridY)+1.5, chunkSize)
	if swarm == nil {
		return
	}
	nestKey := fmt.Sprintf("%d,%d", nest.GridX, nest.GridY)
	swarm.NestKey = nestKey
	swarm.HomePos = swarm.Position
	nest.ResidentSwarmID = swarm.ID
	nest.RehatchAtTick = 0
	logger.Info("Nest %s spawned resident %s (%d %s)", nestKey, swarm.ID, n, nest.SpeciesID)
}

// processNests runs the nest upkeep pass (called every 30 ticks — N nests is tiny):
// the occupant-gone sweep (any removal path, belt-and-braces beside the
// breakOccupantAt hook) and the brood-drain RE-HATCH: a dead resident with banked
// brood re-staffs after 2 min at a size equal to the brood consumed — ~3 consecutive
// culls exhaust a nest into readable dormancy.
func (m *Match) processNests(state *WorldState, logger runtime.Logger) {
	chunkSize := state.Config.ChunkSize
	var toDelete []string

	for key, nest := range state.NestStates {
		// Occupant-gone sweep (the processFruitTrees pattern)
		cx, cy, lx, ly := GlobalToChunk(nest.GridX, nest.GridY)
		chunk := state.Chunks[ChunkKey(cx, cy)]
		if chunk == nil {
			continue
		}
		cell, _ := chunk.GetOccupantCell(lx, ly)
		if cell.IsEmpty || cell.Occupant == nil || cell.Occupant.ID != nest.EntityID {
			toDelete = append(toDelete, key)
			m.orphanNestResident(state, nest)
			continue
		}

		// Resident alive? Nothing to do here (deposits/hatches happen at homing arrival).
		if _, alive := state.Swarms[nest.ResidentSwarmID]; alive && nest.ResidentSwarmID != "" {
			continue
		}

		// Resident dead (caught/killed). Brood-drain re-hatch:
		if nest.Brood < entities.NestHatchCost {
			nest.RehatchAtTick = 0 // dormant — a readable axe-at-leisure target
			continue
		}
		if nest.RehatchAtTick == 0 {
			nest.RehatchAtTick = state.TickCount + entities.NestRehatchDelay
			continue
		}
		if state.TickCount >= nest.RehatchAtTick {
			size := nest.Brood
			if size > entities.NestHatchCost {
				size = entities.NestHatchCost
			}
			nest.Brood -= size
			species := state.Species[nest.SpeciesID]
			if species != nil {
				m.nestSpawnResident(state, nest, species, size, logger)
			}
			_ = chunkSize
		}
	}

	for _, key := range toDelete {
		delete(state.NestStates, key)
	}
}

// depositBrood handles a sated resident arriving home: +1 brood (clamped — no banked
// chain-hatching) and the hatch check (+2 into the resident per 3 brood, §13
// partial-litter at the population cap; at zero room the brood stays banked).
func (m *Match) depositBrood(
	state *WorldState,
	swarm *entities.SwarmState,
	nest *entities.NestState,
	logger runtime.Logger,
) {
	if nest.Brood < entities.NestBroodCap {
		nest.Brood++
	}

	if nest.Brood >= entities.NestHatchCost {
		n := entities.NestHatchCount
		if maxPop := state.SpeciesMaxPopulation(swarm.SpeciesID); maxPop > 0 {
			room := maxPop - state.SpeciesPopulation(swarm.SpeciesID)
			if room < n {
				n = room
			}
		}
		if n > 0 {
			nest.Brood -= entities.NestHatchCost
			m.growSwarm(state, swarm, n)
			logger.Info("Nest %d,%d hatched +%d into %s (now %d; brood %d)",
				nest.GridX, nest.GridY, n, swarm.ID, swarm.Count, nest.Brood)
		}
	}
}

// onNestOccupantRemoved is the breakOccupantAt hook: clear the state and ORPHAN the
// resident — it never breeds again, tethers to its last HomePos, still hunts/stings.
func (m *Match) onNestOccupantRemoved(state *WorldState, gx, gy int, logger runtime.Logger) {
	key := fmt.Sprintf("%d,%d", gx, gy)
	nest := state.NestStates[key]
	if nest == nil {
		return
	}
	m.orphanNestResident(state, nest)
	delete(state.NestStates, key)
	logger.Info("Nest at %s destroyed (resident orphaned)", key)
}

func (m *Match) orphanNestResident(state *WorldState, nest *entities.NestState) {
	if resident, ok := state.Swarms[nest.ResidentSwarmID]; ok {
		resident.NestKey = ""
		resident.CarryingBrood = false
		if resident.Phase == "homing" || resident.Phase == "defending" {
			resident.Phase = "feeding"
		}
	}
}

// recallNestDefenders is the AGGRO-ON-DAMAGE hook (called from handleTileBreak's
// damage path): any hit on a nest occupant recalls the resident onto the attacker
// REGARDLESS of distance — axing while the patrol hunts is a head start, not immunity.
func (m *Match) recallNestDefenders(state *WorldState, gx, gy int, attackerID string) {
	key := fmt.Sprintf("%d,%d", gx, gy)
	nest := state.NestStates[key]
	if nest == nil {
		return
	}
	resident, ok := state.Swarms[nest.ResidentSwarmID]
	if !ok {
		return
	}
	resident.Phase = "defending"
	resident.DefendTargetID = attackerID
	resident.DefendUntilTick = state.TickCount + entities.NestDefendTicks
	resident.NextThinkTick = state.TickCount // respond THIS tick
}
