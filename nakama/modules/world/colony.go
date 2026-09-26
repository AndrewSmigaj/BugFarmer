package world

// colony.go — the ANT trail mechanics (underground-arc P3.2): scouts breadcrumb their
// walks and register food sites into their colony's memory; workers with nothing in
// sight follow the best-known ROUTE hop-by-hop, so files of small swarms share one
// literal polyline — the trail IS the scout's remembered walk.
//
// Determinism: every choice below is position/sorted-key arithmetic — NO RNG. The only
// outputs are ordinary emitLeg calls (SWARM_SET_TARGET), which clients already replay.
// Memory state is server-only soft state (see entities/colony.go's classification) and
// is deliberately absent from buildWorldSave / ComputeStateHash / the snapshot.

import (
	"fmt"
	"math"
	"sort"

	"bugfarmer/entities"
)

// nestKeyFor formats the NestStates/ColonyMemory key for a nest cell.
func nestKeyFor(gx, gy int) string { return fmt.Sprintf("%d,%d", gx, gy) }

// scoutRegisterStrength is one scout sighting's deposit into a site's strength; with
// SiteDecayPerPass 1.5 every 30 ticks, one sighting sustains a site ~24s — a trail
// needs a scout (or diners) to keep vouching for it.
const scoutRegisterStrength = 12.0

// workerReinforceStrength: one worker ARRIVAL's re-vouch (the ACO traffic loop) —
// enough that steady traffic sustains a trail indefinitely against decay, while a
// dead site (no arrivals) retires in under a game-hour.
const workerReinforceStrength = 8.0

// nearestColonyNest finds the nest an ant swarm belongs to: its OWN nest when it is a
// resident, else the nearest nest whose occupant family matches the species'
// nest_occupant (scouts are spawned, not hatched — they adopt the closest brood).
// Deterministic: min distance, lowest key tiebreak.
func (m *Match) nearestColonyNest(state *WorldState, swarm *entities.SwarmState, species *entities.BugSpecies, chunkSize int) (string, *entities.NestState) {
	if swarm.NestKey != "" {
		if nest := state.NestStates[swarm.NestKey]; nest != nil {
			return swarm.NestKey, nest
		}
	}
	p := species.Predation
	if p == nil {
		return "", nil
	}
	occupant := p.NestOccupant
	if occupant == "" {
		occupant = species.ColonyNestOccupant // link-only castes (scouts)
	}
	if occupant == "" {
		return "", nil
	}
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	bestKey := ""
	var bestNest *entities.NestState
	bestSq := float32(0)
	for _, key := range sortedStringKeys(state.NestStates) {
		nest := state.NestStates[key]
		if nest.EntityID != occupant {
			continue
		}
		dx, dy := float32(nest.GridX)+0.5-sx, float32(nest.GridY)+0.5-sy
		dsq := dx*dx + dy*dy
		if bestKey == "" || dsq < bestSq {
			bestKey, bestNest, bestSq = key, nest, dsq
		}
	}
	return bestKey, bestNest
}

// scoutBreadcrumb appends the scout's position to its walk buffer — RESET whenever it
// passes home (so the buffer is "the walk since leaving the colony", and a stored
// route runs HOME → SITE by construction). Called once per scout think (~3-5s apart,
// which spaces crumbs a few cells naturally).
func (m *Match) scoutBreadcrumb(state *WorldState, swarm *entities.SwarmState, nest *entities.NestState, chunkSize int) {
	if state.ScoutPaths == nil { // defend test/deserialization construction paths
		state.ScoutPaths = make(map[string][]entities.RoutePoint)
	}
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	if nest != nil {
		nx, ny := float32(nest.GridX)+0.5, float32(nest.GridY)+0.5
		dx, dy := sx-nx, sy-ny
		if dx*dx+dy*dy <= entities.NestDepositRange*entities.NestDepositRange*4 {
			state.ScoutPaths[swarm.ID] = state.ScoutPaths[swarm.ID][:0] // home again: new walk
		}
	}
	path := append(state.ScoutPaths[swarm.ID], entities.RoutePoint{X: sx, Y: sy})
	if len(path) > entities.MaxRouteLen {
		path = path[len(path)-entities.MaxRouteLen:] // fray the HOME end, keep the working tip
	}
	state.ScoutPaths[swarm.ID] = path
}

// registerCarrionSite records/refreshes a food site in a colony's memory, attaching the
// registering scout's walked route. Same-cell hits refresh strength and keep the
// SHORTER route (trails straighten over generations — the ACO nod). Weakest site
// evicted past the cap (lowest strength, lowest cell-key tiebreak).
func registerCarrionSite(state *WorldState, nestKey string, gx, gy int, add float32, route []entities.RoutePoint) bool {
	if nestKey == "" {
		return false
	}
	if state.ColonyMemory == nil { // defend test/deserialization construction paths
		state.ColonyMemory = make(map[string]*entities.ColonyMemory)
	}
	mem := state.ColonyMemory[nestKey]
	if mem == nil {
		mem = &entities.ColonyMemory{}
		state.ColonyMemory[nestKey] = mem
	}
	for _, s := range mem.Sites {
		// COALESCENCE (v8 finding): a carrion PILE registered as 15+ one-cell sites
		// that churned the 8-slot memory, split reinforcement, and soaked recruits
		// on neighbor cells. Anything within the merge radius IS the same site.
		dx, dy := s.GridX-gx, s.GridY-gy
		if dx*dx+dy*dy <= entities.SiteMergeRadius*entities.SiteMergeRadius {
			s.Strength += add
			if s.Strength > entities.SiteStrengthCap {
				s.Strength = entities.SiteStrengthCap
			}
			if len(route) > 0 && (len(s.Route) == 0 || len(route) < len(s.Route)) {
				s.Route = append([]entities.RoutePoint(nil), route...)
			}
			return false
		}
	}
	site := &entities.CarrionSite{GridX: gx, GridY: gy, Strength: add,
		Route: append([]entities.RoutePoint(nil), route...)}
	mem.Sites = append(mem.Sites, site)
	isNew := true
	if len(mem.Sites) > entities.MaxColonySites {
		weakest := 0
		for i, s := range mem.Sites {
			w := mem.Sites[weakest]
			if s.Strength < w.Strength ||
				(s.Strength == w.Strength && siteKeyLess(s, w)) {
				weakest = i
			}
		}
		mem.Sites = append(mem.Sites[:weakest], mem.Sites[weakest+1:]...)
	}
	return isNew
}

// anyMarcherFor reports whether any live swarm is currently committed to the site —
// the "is this trail lit?" check for relight-recruitment. O(marchers), tiny.
func anyMarcherFor(state *WorldState, siteKey string) bool {
	for _, k := range sortedStringKeys(state.MarchTargets) {
		if state.MarchTargets[k] == siteKey && state.Swarms[k] != nil {
			return true
		}
	}
	return false
}

// recruitWorkers is the scout's RECRUITMENT (v7 finding: without it, a first march
// depended on a worker happening to think hungry+empty-eyed while a far site was
// alive — ~3 commits in 34 days). A FRESH site immediately commits up to `count`
// of the colony's workers (sorted swarm ids — deterministic), who march on their
// next think; their arrivals light the traffic-reinforcement loop. Real ants do
// exactly this (tandem running / recruitment pheromone).
func recruitWorkers(state *WorldState, nestKey string, gx, gy int, count int) int {
	if state.MarchTargets == nil {
		state.MarchTargets = make(map[string]string)
	}
	siteKey := nestKeyFor(gx, gy)
	recruited := 0
	for _, id := range sortedStringKeys(state.Swarms) {
		if recruited >= count {
			break
		}
		sw := state.Swarms[id]
		sp := state.Species[sw.SpeciesID]
		if sp == nil || !sp.CarrionForager || sp.ColonyScout {
			continue
		}
		if sw.Satiation >= 90 { // full loads are homing — don't divert them
			continue
		}
		if state.MarchTargets[id] != "" {
			continue // already on a trail
		}
		state.MarchTargets[id] = siteKey
		recruited++
	}
	return recruited
}

func siteKeyLess(a, b *entities.CarrionSite) bool {
	if a.GridX != b.GridX {
		return a.GridX < b.GridX
	}
	return a.GridY < b.GridY
}

// bestKnownSite picks the trail a worker should walk: argmax Strength/(1+dist) from the
// worker's position; ties break on the lowest cell key. Pure arithmetic — no RNG.
func bestKnownSite(mem *entities.ColonyMemory, fromX, fromY float32) *entities.CarrionSite {
	if mem == nil || len(mem.Sites) == 0 {
		return nil
	}
	sites := append([]*entities.CarrionSite(nil), mem.Sites...)
	sort.Slice(sites, func(i, j int) bool { return siteKeyLess(sites[i], sites[j]) })
	var best *entities.CarrionSite
	var bestScore float32
	for _, s := range sites {
		dx, dy := float32(s.GridX)+0.5-fromX, float32(s.GridY)+0.5-fromY
		dist := float32(math.Sqrt(float64(dx*dx + dy*dy))) // server-only state: the codebase idiom
		score := s.Strength / (1 + dist)
		if best == nil || score > bestScore {
			best, bestScore = s, score
		}
	}
	return best
}

// nextTrailPoint is the STATELESS traversal rule: nearest route point, then two points
// ahead — BUT a waypoint only counts if it makes SPATIAL PROGRESS toward the site
// (v10 finding: scout routes in open terrain are wander TANGLES — index-space
// skip-ahead sent marchers orbiting mid-map; one lucky arrival per run). A useless
// waypoint falls back to the DIRECT line: in the open, direct legs converge into the
// literal file; coherent tunnel routes (scouts that walked home→site corridors) still
// get followed point by point.
func nextTrailPoint(site *entities.CarrionSite, fromX, fromY float32) (float32, float32) {
	sx, sy := float32(site.GridX)+0.5, float32(site.GridY)+0.5
	if len(site.Route) == 0 {
		return sx, sy
	}
	nearest, nearestSq := 0, float32(0)
	for i, p := range site.Route {
		dx, dy := p.X-fromX, p.Y-fromY
		dsq := dx*dx + dy*dy
		if i == 0 || dsq < nearestSq {
			nearest, nearestSq = i, dsq
		}
	}
	target := nearest + 2
	if target >= len(site.Route) {
		return sx, sy
	}
	wp := site.Route[target]
	mySiteSq := (sx-fromX)*(sx-fromX) + (sy-fromY)*(sy-fromY)
	wpSiteSq := (sx-wp.X)*(sx-wp.X) + (sy-wp.Y)*(sy-wp.Y)
	if wpSiteSq >= mySiteSq { // the waypoint would take us BACKWARD — go direct
		return sx, sy
	}
	return wp.X, wp.Y
}

// processColonyMemory decays every site each nest pass (30 ticks) and drops dead
// entries — the age-out that keeps trails honest and memory bounded. Also prunes walk
// buffers of scouts that no longer exist.
func (m *Match) processColonyMemory(state *WorldState) {
	for _, key := range sortedStringKeys(state.ColonyMemory) {
		mem := state.ColonyMemory[key]
		if state.NestStates[key] == nil { // nest gone → its memory dies with it
			delete(state.ColonyMemory, key)
			continue
		}
		kept := mem.Sites[:0]
		for _, s := range mem.Sites {
			s.Strength -= entities.SiteDecayPerPass
			if s.Strength > 0 {
				kept = append(kept, s)
			}
		}
		mem.Sites = kept
		if len(mem.Sites) == 0 {
			delete(state.ColonyMemory, key)
		}
	}
	for _, id := range sortedStringKeys(state.ScoutPaths) {
		if state.Swarms[id] == nil {
			delete(state.ScoutPaths, id)
		}
	}
	for _, id := range sortedStringKeys(state.MarchTargets) {
		if state.Swarms[id] == nil {
			delete(state.MarchTargets, id)
		}
	}
}

