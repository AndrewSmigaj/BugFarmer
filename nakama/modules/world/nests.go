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

	// honeyPerDeposit: combs added per provisioning trip (before the hive's honey_mult).
	// One comb ≈ 2 trips at the default 0.5 — a working colony fills a basic box in ~8 trips.
	honeyPerDeposit = 0.5
)

// Wasp nests (architecture_swarm_sync.md §14): the fruit-tree pattern — occupant-backed
// in-memory states scanned at chunk load, swept when the occupant disappears, no
// persistence (a destroyed nest resurrects on server restart, like every broken
// occupant; documented). The nest OWNS a resident swarm and converts brood deposits
// into hatches via the shared growSwarm id-math (SWARM_REPRODUCED — zero new ledger
// vocabulary). NestState is deliberately species-generic (bees later: a `Deposit`
// field + a yield item on the nest def).

// speciesForNestOccupant finds the species whose nest this occupant type is — either the
// primary (wild) NestOccupant or one of the player-placeable NestOccupantsExtra hive boxes.
// The bool reports whether it is an EXTRA (a box → registers DORMANT, no free colony).
func (m *Match) speciesForNestOccupant(state *WorldState, occupantID string) (string, *entities.BugSpecies, bool) {
	for id, sp := range state.Species {
		if sp.Predation == nil {
			continue
		}
		if sp.Predation.NestOccupant == occupantID {
			return id, sp, false
		}
		for _, extra := range sp.Predation.NestOccupantsExtra {
			if extra == occupantID {
				return id, sp, true
			}
		}
	}
	return "", nil, false
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
			speciesID, species, isBox := m.speciesForNestOccupant(state, cell.Occupant.ID)
			if species == nil {
				continue
			}

			gx := cx*chunkSize + lx
			gy := cy*chunkSize + ly
			m.registerNestAt(state, gx, gy, cell.Occupant.ID, speciesID, species, isBox, logger)
		}
	}
}

// registerNestAt creates the NestState for a nest occupant at (gx,gy). Wild nests (dormant=false)
// found their resident patrol immediately (cap-aware); PLAYER-PLACED hive boxes (dormant=true)
// register empty — a colony must claim them via daughter-founding/recovery, so placing a box never
// mints free bees. Shared by chunk-load scanning, runtime placement, and dynamic founding.
// No-op if a nest is already registered there.
func (m *Match) registerNestAt(state *WorldState, gx, gy int, occupantID, speciesID string, species *entities.BugSpecies, dormant bool, logger runtime.Logger) *entities.NestState {
	key := fmt.Sprintf("%d,%d", gx, gy)
	if state.NestStates[key] != nil {
		return state.NestStates[key]
	}
	nest := &entities.NestState{GridX: gx, GridY: gy, EntityID: occupantID, SpeciesID: speciesID}
	state.NestStates[key] = nest
	if !dormant {
		m.nestSpawnResident(state, nest, species, state.Tuning.NestFoundingSize, logger)
	}
	logger.Debug("Registered %s nest at %d,%d (dormant=%v resident=%q)", speciesID, gx, gy, dormant, nest.ResidentSwarmID)
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
	nest.Founded = true
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
			// Brood exhausted → the colony would otherwise be permanently dormant (the bug behind the
			// collapsing wasp colonies). Since wasps are NEST-ONLY, this is their sole way back, so a dead
			// colony RE-FOUNDS a fresh founding patrol — but FOOD-GATED (live prey for hunters, live
			// nectar for bee-class nectar foragers, within home range) and after a longer recovery delay,
			// so we never re-staff a hive in an emptied field and dormancy stays readable where the food
			// is genuinely gone. Only nests that ONCE HELD a colony recover — a never-founded placed hive
			// box waits for a daughter-founding to claim it (no colonies from nowhere).
			species := state.Species[nest.SpeciesID]
			if species == nil || !nest.Founded || !m.nestCanFeedNearby(state, nest, species) {
				nest.RehatchAtTick = 0 // no food (or never founded) — stay dormant
				continue
			}
			if nest.RehatchAtTick == 0 {
				nest.RehatchAtTick = state.TickCount + entities.NestRecoveryDelay
				continue
			}
			if state.TickCount >= nest.RehatchAtTick {
				m.nestSpawnResident(state, nest, species, state.Tuning.NestFoundingSize, logger)
				logger.Info("Nest %s recovered: re-founded a %d-patrol (prey returned)", key, state.Tuning.NestFoundingSize)
			}
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

	// Bees: every provisioning trip also makes honey (foraging IS the honey economy), up to
	// the hive def's cap. Wasp nests have no world.hive → no-op. Display/inventory yield only.
	if def := state.Entities[nest.EntityID]; def != nil && def.World != nil && def.World.Hive != nil {
		h := def.World.Hive
		mult := h.HoneyMult
		if mult <= 0 {
			mult = 1.0
		}
		nest.Honey += honeyPerDeposit * mult
		if h.HoneyCap > 0 && nest.Honey > h.HoneyCap {
			nest.Honey = h.HoneyCap
		}
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
		claimKey   string // non-empty: colonize this EXISTING dormant hive box (no occupant placed)
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

		if len(species.Predation.Prey) == 0 {
			// BEE-CLASS nectar forager: a swarming colony PREFERS an empty player-placed hive
			// box (that's how an apiary comes alive), else founds a wild hive beside nectar.
			if boxKey, ok := m.findClaimableBox(state, nest, species); ok {
				todo = append(todo, founding{speciesID: nest.SpeciesID, species: species, claimKey: boxKey})
				nest.Brood = 0
				nestCount[nest.SpeciesID]++
				continue
			}
			gx, gy, ok := m.findNestSiteWithNectar(state, nest.GridX, nest.GridY, species,
				state.Tuning.NestFoundDistMin, state.Tuning.NestFoundDistMax)
			if !ok {
				continue // no flower field an adequate distance away — the colony WAITS
			}
			todo = append(todo, founding{gx: gx, gy: gy, occupantID: species.Predation.NestOccupant,
				speciesID: nest.SpeciesID, species: species})
			nest.Brood = 0
			nestCount[nest.SpeciesID]++
			continue
		}

		gx, gy, ok := m.findNestSiteWithPrey(state, nest.GridX, nest.GridY, species,
			state.Tuning.NestFoundDistMin, state.Tuning.NestFoundDistMax)
		if !ok {
			continue // no prey cluster an adequate distance away yet — the colony WAITS (no doomed hive)
		}
		todo = append(todo, founding{gx: gx, gy: gy, occupantID: nest.EntityID,
			speciesID: nest.SpeciesID, species: species})
		nest.Brood = 0              // drain the surplus -> founding cooldown (rebuild to NestBroodCap first)
		nestCount[nest.SpeciesID]++ // reserve the slot so two parents can't both overshoot MaxNests this pass
	}

	for _, f := range todo {
		if f.claimKey != "" {
			// Colonize the existing dormant box: no occupant change, just staff it.
			nest := state.NestStates[f.claimKey]
			if nest == nil || nest.ResidentSwarmID != "" {
				continue // raced/claimed meanwhile
			}
			m.nestSpawnResident(state, nest, f.species, state.Tuning.NestFoundingSize, logger)
			logger.Info("Nest founding: %s colony moved into the hive box at %s", f.speciesID, f.claimKey)
			continue
		}
		cx, cy, lx, ly := GlobalToChunk(f.gx, f.gy)
		chunk := state.Chunks[ChunkKey(cx, cy)]
		if chunk == nil {
			continue
		}
		occ := &PlacedOccupant{ID: f.occupantID, Dir: 0}
		chunk.SetOccupant(lx, ly, occ)
		m.broadcastWorldUpdate(dispatcher, state, cx, cy, f.gx, f.gy, "", occ, false)
		m.registerNestAt(state, f.gx, f.gy, f.occupantID, f.speciesID, f.species, false, logger)
		logger.Info("Nest founding: %s colony split a new hive at %d,%d", f.speciesID, f.gx, f.gy)
	}
}

// findClaimableBox picks the nearest EMPTY registered hive box (a dormant NestState of this
// species with no resident) within the founding band of the parent — sorted iteration +
// nearest/lowest-key tiebreak (deterministic). Boxes may sit close to the parent (min 4 cells):
// side-by-side boxes ARE an apiary.
func (m *Match) findClaimableBox(state *WorldState, parent *entities.NestState, species *entities.BugSpecies) (string, bool) {
	px, py := float32(parent.GridX)+0.5, float32(parent.GridY)+0.5
	maxD := float32(state.Tuning.NestFoundDistMax)
	minSq, maxSq := float32(4*4), maxD*maxD
	bestKey := ""
	bestSq := float32(math.MaxFloat32)
	for _, key := range sortedStringKeys(state.NestStates) {
		n := state.NestStates[key]
		if n.SpeciesID != parent.SpeciesID || n.ResidentSwarmID != "" || key == fmt.Sprintf("%d,%d", parent.GridX, parent.GridY) {
			continue
		}
		if _, alive := state.Swarms[n.ResidentSwarmID]; alive {
			continue
		}
		// Only player-placeable boxes are "claimable" targets; wild hives recover on their own.
		isBox := false
		for _, extra := range species.Predation.NestOccupantsExtra {
			if extra == n.EntityID {
				isBox = true
				break
			}
		}
		if !isBox {
			continue
		}
		dx, dy := float32(n.GridX)+0.5-px, float32(n.GridY)+0.5-py
		dsq := dx*dx + dy*dy
		if dsq < minSq || dsq > maxSq {
			continue
		}
		if dsq < bestSq || (dsq == bestSq && key < bestKey) {
			bestSq, bestKey = dsq, key
		}
	}
	return bestKey, bestKey != ""
}

// findNestSiteWithNectar picks a wild-founding site beside the RICHEST flower field an adequate
// distance from the parent — the bee analog of findNestSiteWithPrey (same band, same WAIT-if-none
// semantics, deterministic tiebreaks: highest nectar then lowest key).
func (m *Match) findNestSiteWithNectar(state *WorldState, parentGX, parentGY int, species *entities.BugSpecies, minD, maxD int) (int, int, bool) {
	px, py := float32(parentGX)+0.5, float32(parentGY)+0.5
	minSq, maxSq := float32(minD*minD), float32(maxD*maxD)
	const nectarFloor = 20.0
	bestKey := ""
	var bestX, bestY int
	bestNectar := float32(-1)
	for _, key := range sortedStringKeys(state.ForagePools) {
		fp := state.ForagePools[key]
		if fp.Nectar < nectarFloor {
			continue
		}
		dx, dy := float32(fp.GridX)+0.5-px, float32(fp.GridY)+0.5-py
		dsq := dx*dx + dy*dy
		if dsq < minSq || dsq > maxSq {
			continue
		}
		if fp.Nectar > bestNectar || (fp.Nectar == bestNectar && key < bestKey) {
			bestNectar, bestKey, bestX, bestY = fp.Nectar, key, fp.GridX, fp.GridY
		}
	}
	if bestKey == "" {
		return 0, 0, false
	}
	return m.findEmptyCellNear(state, bestX, bestY, 1, 8)
}

// nestCanFeedNearby is the species-shape-aware food gate for recovery/founding checks:
// hunters need live prey in range (nestHasPreyNearby); bee-class nectar foragers (a nest
// species with an EMPTY prey list) need a live flower (a ForagePool with meaningful nectar)
// within the same home-range tether.
func (m *Match) nestCanFeedNearby(state *WorldState, nest *entities.NestState, species *entities.BugSpecies) bool {
	p := species.Predation
	if p == nil {
		return false
	}
	if len(p.Prey) == 0 {
		return m.nestHasNectarNearby(state, nest, species)
	}
	return m.nestHasPreyNearby(state, nest, species)
}

// nestHasNectarNearby: any registered flower ForagePool with nectar above a graze-floor within
// the species' home range of the nest. The bee analog of nestHasPreyNearby.
func (m *Match) nestHasNectarNearby(state *WorldState, nest *entities.NestState, species *entities.BugSpecies) bool {
	p := species.Predation
	if p == nil {
		return false
	}
	reach := p.HomeRange
	if reach <= 0 {
		reach = 40
	}
	reachSq := reach * reach
	nx, ny := float32(nest.GridX)+0.5, float32(nest.GridY)+0.5
	const nectarFloor = 20.0 // a grazed-out field doesn't count as "can feed a colony"
	for _, fp := range state.ForagePools {
		if fp.Nectar < nectarFloor {
			continue
		}
		dx, dy := float32(fp.GridX)+0.5-nx, float32(fp.GridY)+0.5-ny
		if dx*dx+dy*dy <= reachSq {
			return true
		}
	}
	return false
}

// nestHasPreyNearby reports whether any live prey swarm sits within the species' home range of the nest —
// the gate for re-founding a brood-exhausted colony. Reuses species.Predation.Prey / HomeRange (the same
// tether the resident hunts within), so "recover here" means exactly "this nest can feed a patrol again".
func (m *Match) nestHasPreyNearby(state *WorldState, nest *entities.NestState, species *entities.BugSpecies) bool {
	p := species.Predation
	if p == nil || len(p.Prey) == 0 {
		return false
	}
	reach := p.HomeRange
	if reach <= 0 {
		reach = 40 // sane default tether if a species omits home_range
	}
	reachSq := reach * reach
	cs := state.Config.ChunkSize
	nx, ny := float32(nest.GridX)+0.5, float32(nest.GridY)+0.5
	for _, sw := range state.Swarms {
		if sw.Count <= 0 || !containsString(p.Prey, sw.SpeciesID) {
			continue
		}
		dx, dy := sw.WorldX(cs)-nx, sw.WorldY(cs)-ny
		if dx*dx+dy*dy <= reachSq {
			return true
		}
	}
	return false
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
	// §C precedence rule (all three defend entries): suppressed while the resident is
	// subdued OR the nest is smoked — the calm harvest window.
	if nestDefenseSuppressed(state, nest, resident) {
		return
	}
	resident.Phase = "defending"
	resident.DefendTargetID = attackerID
	resident.DefendUntilTick = state.TickCount + entities.NestDefendTicks
	resident.NextThinkTick = state.TickCount // respond THIS tick
}
