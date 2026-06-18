package world

import (
	"fmt"
	"math"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Daughter-nest founding SEPARATION from the parent (cells). The owner's model: a founding hornet travels
// an ADEQUATE distance to a NEW area, THEN hunts for prey there, and forms the nest where it finds prey —
// so a daughter settles beside a prey cluster that is min..max cells from the parent (≈ the wasp's
// home_range 40 / the authored ~74-cell inter-nest spacing), and the colony WAITS if no such prey exists
// (no doomed hive in an empty field). Overridable via Tuning.NestFoundDistMin/Max. See findNestSiteWithPrey.
const (
	nestFoundDistMin = 40
	nestFoundDistMax = 120
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
			m.registerNestAt(state, gx, gy, cell.Occupant.ID, speciesID, species, logger)
		}
	}
}

// registerNestAt creates the NestState for a nest occupant at (gx,gy) and founds its resident patrol
// (cap-aware). Shared by chunk-load scanning (initNestsInChunk) and DYNAMIC founding (a colony splitting
// off a daughter hive — processNestFounding). No-op if a nest is already registered there.
func (m *Match) registerNestAt(state *WorldState, gx, gy int, occupantID, speciesID string, species *entities.BugSpecies, logger runtime.Logger) *entities.NestState {
	key := fmt.Sprintf("%d,%d", gx, gy)
	if state.NestStates[key] != nil {
		return state.NestStates[key]
	}
	nest := &entities.NestState{GridX: gx, GridY: gy, EntityID: occupantID, SpeciesID: speciesID}
	state.NestStates[key] = nest
	m.nestSpawnResident(state, nest, species, state.Tuning.NestFoundingSize, logger)
	logger.Debug("Registered %s nest at %d,%d (resident=%q)", speciesID, gx, gy, nest.ResidentSwarmID)
	return nest
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
	state.Stats.recordBirth(nest.SpeciesID, BirthNest, n)
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

	for _, key := range sortedStringKeys(state.NestStates) { // sorted: nest hatches mint IDs / draw rand
		nest := state.NestStates[key]
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
		if nest.Brood < state.Tuning.NestHatchCost {
			nest.RehatchAtTick = 0 // dormant — a readable axe-at-leisure target
			continue
		}
		if nest.RehatchAtTick == 0 {
			nest.RehatchAtTick = state.TickCount + entities.NestRehatchDelay
			continue
		}
		if state.TickCount >= nest.RehatchAtTick {
			size := nest.Brood
			if size > state.Tuning.NestHatchCost {
				size = state.Tuning.NestHatchCost
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
	if nest.Brood < state.Tuning.NestBroodCap {
		nest.Brood++
	}

	if nest.Brood >= state.Tuning.NestHatchCost {
		n := state.Tuning.NestHatchCount
		if maxPop := state.SpeciesMaxPopulation(swarm.SpeciesID); maxPop > 0 {
			room := maxPop - state.SpeciesPopulation(swarm.SpeciesID)
			if room < n {
				n = room
			}
		}
		if n > 0 {
			nest.Brood -= state.Tuning.NestHatchCost
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
// processNestFounding lets a THRIVING colony split off a daughter hive — how a nest-based predator
// population GROWS and SPREADS (the owner's "split and make another hive"). A nest founds when its
// resident patrol is saturated (Count >= MaxSwarmSize) AND it has banked surplus brood (>= NestBroodCap,
// the proxy for "well-fed from many kills"), the zone is under its MaxNests cap, and there's population
// headroom for the daughter patrol. Founding drains the parent's brood — a natural cooldown (it must
// rebuild to NestBroodCap before founding again). Collect-then-act (registerNestAt mutates NestStates).
//
// Determinism: placing the wasp_nest occupant is a server-authoritative world-cell mutation broadcast via
// broadcastWorldUpdate (the crop/torch-placement class, replayed not re-decided); the daughter resident
// rides SwarmUpdate. Bug positions — the only hashed state — are untouched by the placement itself.
func (m *Match) processNestFounding(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	if state.CurrentZone == nil || state.CurrentZone.BugSpawning == nil {
		return
	}

	nestCount := map[string]int{}
	for _, n := range state.NestStates {
		nestCount[n.SpeciesID]++
	}

	type founding struct {
		gx, gy     int
		occupantID string
		speciesID  string
		species    *entities.BugSpecies
	}
	var todo []founding

	for _, nkey := range sortedStringKeys(state.NestStates) { // sorted: daughter founding draws rand / mints IDs
		nest := state.NestStates[nkey]
		resident, alive := state.Swarms[nest.ResidentSwarmID]
		if !alive || nest.ResidentSwarmID == "" {
			continue
		}
		species := state.Species[nest.SpeciesID]
		if species == nil {
			continue
		}
		// Thriving: saturated patrol + banked surplus brood (brood only accrues from successful
		// post-kill homing, so a full bank means the colony is well-fed).
		if resident.Count < species.MaxSwarmSize || nest.Brood < state.Tuning.NestBroodCap {
			continue
		}
		maxNests := state.CurrentZone.BugSpawning.SpeciesCaps[nest.SpeciesID].MaxNests
		if maxNests <= 0 || nestCount[nest.SpeciesID] >= maxNests {
			continue
		}
		// Population headroom for the daughter patrol (don't found a dormant hive at the cap).
		if maxPop := state.SpeciesMaxPopulation(nest.SpeciesID); maxPop > 0 &&
			state.SpeciesPopulation(nest.SpeciesID)+state.Tuning.NestFoundingSize > maxPop {
			continue
		}
		gx, gy, ok := m.findNestSiteWithPrey(state, nest.GridX, nest.GridY, species,
			state.Tuning.NestFoundDistMin, state.Tuning.NestFoundDistMax)
		if !ok {
			continue // no prey cluster an adequate distance away yet — the colony WAITS (no doomed hive)
		}
		todo = append(todo, founding{gx, gy, nest.EntityID, nest.SpeciesID, species})
		nest.Brood = 0              // drain the surplus -> founding cooldown (rebuild to NestBroodCap first)
		nestCount[nest.SpeciesID]++ // reserve the slot so two parents can't both overshoot MaxNests this pass
	}

	for _, f := range todo {
		cx, cy, lx, ly := GlobalToChunk(f.gx, f.gy)
		chunk := state.Chunks[ChunkKey(cx, cy)]
		if chunk == nil {
			continue
		}
		occ := &PlacedOccupant{ID: f.occupantID, Dir: 0}
		chunk.SetOccupant(lx, ly, occ)
		m.broadcastWorldUpdate(dispatcher, state, cx, cy, f.gx, f.gy, "", occ, false)
		m.registerNestAt(state, f.gx, f.gy, f.occupantID, f.speciesID, f.species, logger)
		logger.Info("Nest founding: %s colony split a new hive at %d,%d", f.speciesID, f.gx, f.gy)
	}
}

// findNestSiteWithPrey picks a daughter-nest site in a NEW area with prey: the NEAREST prey cluster that
// sits an adequate distance from the parent (minD..maxD cells), then an empty walkable cell beside it.
// Returns !ok when no qualifying prey cluster exists — the colony WAITS rather than found a doomed hive in
// an empty field. (Owner's model: travel an adequate distance, THEN hunt for prey, THEN form the nest.)
// O(swarms); only runs on the slow nest-founding clock for a thriving colony.
func (m *Match) findNestSiteWithPrey(state *WorldState, parentGX, parentGY int, species *entities.BugSpecies, minD, maxD int) (int, int, bool) {
	p := species.Predation
	if p == nil || len(p.Prey) == 0 {
		return 0, 0, false
	}
	cs := state.Config.ChunkSize
	px, py := float32(parentGX)+0.5, float32(parentGY)+0.5
	minSq, maxSq := float32(minD*minD), float32(maxD*maxD)
	bestID := ""
	var bestX, bestY float32
	bestSq := float32(math.MaxFloat32)
	for id, sw := range state.Swarms {
		if sw.Count <= 0 || !containsString(p.Prey, sw.SpeciesID) {
			continue
		}
		sx, sy := sw.WorldX(cs), sw.WorldY(cs)
		dx, dy := sx-px, sy-py
		dsq := dx*dx + dy*dy
		if dsq < minSq || dsq > maxSq {
			continue // too close to the parent (overlapping turf) or too far across the map
		}
		if dsq < bestSq || (dsq == bestSq && id < bestID) { // nearest qualifying prey (deterministic tiebreak)
			bestSq, bestX, bestY, bestID = dsq, sx, sy, id
		}
	}
	if bestID == "" {
		return 0, 0, false
	}
	return m.findEmptyCellNear(state, int(bestX), int(bestY), 1, 8) // an empty cell beside that prey cluster
}

// findEmptyCellNear spirals out (Chebyshev rings minR..maxR, deterministic order) from (gx,gy) for the
// first empty, walkable cell. Used to place a founded daughter nest near its parent.
func (m *Match) findEmptyCellNear(state *WorldState, gx, gy, minR, maxR int) (int, int, bool) {
	for r := minR; r <= maxR; r++ {
		for dy := -r; dy <= r; dy++ {
			for dx := -r; dx <= r; dx++ {
				if dx > -r && dx < r && dy > -r && dy < r {
					continue // ring only: cells at Chebyshev distance exactly r
				}
				nx, ny := gx+dx, gy+dy
				cx, cy, lx, ly := GlobalToChunk(nx, ny)
				chunk := state.Chunks[ChunkKey(cx, cy)]
				if chunk == nil {
					continue
				}
				cell, _ := chunk.GetOccupantCell(lx, ly)
				if !cell.IsEmpty {
					continue
				}
				if state.IsBlocked(float32(nx)+0.5, float32(ny)+0.5) {
					continue // a fence/wall cell
				}
				return nx, ny, true
			}
		}
	}
	return 0, 0, false
}

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
