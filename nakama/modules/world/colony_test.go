package world

// Tests for ANT COLONY MEMORY + trails (underground-arc P3.2): bounded register/refresh/
// evict/decay, deterministic best-site pick, breadcrumb reset-at-home, the worker's
// trail-follow think, and the age-out contract (memory NEVER rides a world save).
//
// Run inside the builder image:  go test ./modules/world/ -run 'Colony|Trail' -v

import (
	"testing"

	"bugfarmer/entities"
)

func TestColonyMemoryRegisterRefreshEvictDecay(t *testing.T) {
	state, _ := antTestState()
	key := nestKeyFor(10, 10)
	state.NestStates[key] = &entities.NestState{GridX: 10, GridY: 10, EntityID: "ant_brood"}

	// Register + refresh: same cell accumulates (clamped), keeps the SHORTER route.
	long := []entities.RoutePoint{{X: 1, Y: 1}, {X: 2, Y: 2}, {X: 3, Y: 3}}
	short := []entities.RoutePoint{{X: 1, Y: 1}, {X: 3, Y: 3}}
	registerCarrionSite(state, key, 20, 10, 12, long)
	registerCarrionSite(state, key, 20, 10, 12, short)
	mem := state.ColonyMemory[key]
	if len(mem.Sites) != 1 || mem.Sites[0].Strength != 24 {
		t.Fatalf("refresh must accumulate on one site: %+v", mem.Sites)
	}
	if len(mem.Sites[0].Route) != 2 {
		t.Fatalf("refresh must keep the SHORTER route (trails straighten): %d points", len(mem.Sites[0].Route))
	}

	// Eviction: past the cap the WEAKEST site dies.
	for i := 0; i < entities.MaxColonySites; i++ {
		registerCarrionSite(state, key, 30+i, 10, float32(20+i), nil)
	}
	if len(mem.Sites) != entities.MaxColonySites {
		t.Fatalf("memory must cap at %d sites: %d", entities.MaxColonySites, len(mem.Sites))
	}
	for _, s := range mem.Sites {
		if s.GridX == 30 && s.GridY == 10 {
			t.Fatal("the weakest site (strength 20) must have been evicted")
		}
	}

	// Decay: strengths drain each pass; dead sites and empty memories vanish.
	m := &Match{}
	for i := 0; i < 100; i++ {
		m.processColonyMemory(state)
	}
	if state.ColonyMemory[key] != nil {
		t.Fatal("decay must age the whole memory out")
	}

	// A memory whose NEST is gone dies immediately.
	registerCarrionSite(state, key, 20, 10, 50, nil)
	delete(state.NestStates, key)
	m.processColonyMemory(state)
	if state.ColonyMemory[key] != nil {
		t.Fatal("a dead nest's memory must die with it")
	}
}

func TestColonyBestSiteDeterministic(t *testing.T) {
	mem := &entities.ColonyMemory{Sites: []*entities.CarrionSite{
		{GridX: 40, GridY: 10, Strength: 30},
		{GridX: 20, GridY: 10, Strength: 30}, // same strength, NEARER from (10,10)
	}}
	for i := 0; i < 5; i++ {
		s := bestKnownSite(mem, 10.5, 10.5)
		if s == nil || s.GridX != 20 {
			t.Fatalf("run %d: pick must be Strength/(1+dist) argmax → (20,10), got %+v", i, s)
		}
	}
	// Exact tie (same score by symmetry) breaks on the lowest cell key.
	mem = &entities.ColonyMemory{Sites: []*entities.CarrionSite{
		{GridX: 30, GridY: 20, Strength: 30},
		{GridX: 30, GridY: 0, Strength: 30},
	}}
	s := bestKnownSite(mem, 30.5, 10.5)
	if s == nil || s.GridY != 0 {
		t.Fatalf("tie must break on lowest key: got %+v", s)
	}
}

func TestScoutBreadcrumbResetAtHomeAndCap(t *testing.T) {
	state, ant := antTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "ant_brood", "ant_worker", ant, false, nopRuntimeLogger())
	scout := newTestSwarm("s1", 1, 30, 10)
	state.Swarms[scout.ID] = scout

	// Crumbs accumulate on the walk...
	for i := 0; i < entities.MaxRouteLen+10; i++ {
		scout.Position = entities.EntityPosition{LocalX: float32(30 + i), LocalY: 10}
		m.scoutBreadcrumb(state, scout, nest, 32)
	}
	if got := len(state.ScoutPaths[scout.ID]); got != entities.MaxRouteLen {
		t.Fatalf("walk buffer must cap at %d: %d", entities.MaxRouteLen, got)
	}
	// ...and RESET when the scout passes home (the stored route runs HOME → SITE).
	scout.Position = entities.EntityPosition{LocalX: 10.5, LocalY: 10.5}
	m.scoutBreadcrumb(state, scout, nest, 32)
	if got := len(state.ScoutPaths[scout.ID]); got != 1 {
		t.Fatalf("passing home must reset the walk buffer: %d", got)
	}
}

// The worker's march: with a known site and NOTHING in vision, the think OWNS the beat
// and emits a leg toward the trail (skip-ahead waypoint); with food in vision it
// declines so the shared forage block dines as always.
func TestTrailFollowThink(t *testing.T) {
	state, ant := antTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "ant_brood", "ant_worker", ant, false, nopRuntimeLogger())
	worker := state.Swarms[nest.ResidentSwarmID]
	worker.Satiation = 50
	worker.Phase = "feeding"

	// A remembered site far east, with the scout's walked route.
	route := []entities.RoutePoint{{X: 12, Y: 10}, {X: 16, Y: 10}, {X: 20, Y: 10},
		{X: 24, Y: 10}, {X: 28, Y: 10}}
	registerCarrionSite(state, nestKeyFor(10, 10), 30, 10, 40, route)

	state.TickCount = worker.NextThinkTick + 1
	if !m.predationThink(state, worker, ant, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("a hungry worker with a known trail and empty vision must MARCH (own the beat)")
	}
	if worker.TargetX <= worker.WorldX(32) {
		t.Fatalf("the march leg must head toward the site (east): targetX=%v fromX=%v",
			worker.TargetX, worker.WorldX(32))
	}

	// Food IN VISION preempts the trail: decline → the shared forage block dines.
	state.putGroundItem(&entities.GroundItem{
		ID: "snack", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: worker.WorldX(32) + 3, LocalY: 10},
		FoodValue: 10,
	})
	state.TickCount = worker.NextThinkTick + 1
	if m.predationThink(state, worker, ant, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("food in vision must preempt the trail (decline to the shared forage block)")
	}
}

// The scout think registers what it passes — and the registration lands in the NEAREST
// colony of its occupant family (spawned scouts adopt the closest brood).
func TestScoutRegistersIntoNearestColony(t *testing.T) {
	state, ant := antTestState()
	scoutSpec := &entities.BugSpecies{
		ID: "ant_scout", Category: "swarm",
		BaseSpeed: 1.2, VisionRange: 12, WanderRadius: 22,
		MinSwarmSize: 1, MaxSwarmSize: 2,
		CarrionForager: true, ColonyScout: true,
		AttractionsByPhase: map[string][]string{"feeding": {"dead_fly"}},
		Predation: &entities.PredationConfig{
			Prey: []string{}, HomeRange: 110,
			DepositSatiation: 80, HuntSatiationThreshold: 45,
			NestOccupant: "ant_brood",
		},
	}
	state.Species["ant_scout"] = scoutSpec
	state.SwarmsBySpecies["ant_scout"] = []string{}
	m := &Match{}
	m.registerNestAt(state, 10, 10, "ant_brood", "ant_worker", ant, false, nopRuntimeLogger())

	scout := newTestSwarm("scout1", 1, 25, 10)
	scout.SpeciesID = "ant_scout"
	state.Swarms[scout.ID] = scout
	state.putGroundItem(&entities.GroundItem{
		ID: "find", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 27, LocalY: 10},
		FoodValue: 10,
	})
	scout.Satiation = 50
	state.TickCount = scout.NextThinkTick + 1
	m.predationThink(state, scout, scoutSpec, 32, 0.1, nopRuntimeLogger())

	mem := state.ColonyMemory[nestKeyFor(10, 10)]
	if mem == nil || len(mem.Sites) == 0 {
		t.Fatal("the scout must register the carrion into the nearest colony's memory")
	}
	if mem.Sites[0].GridX != 27 || mem.Sites[0].GridY != 10 {
		t.Fatalf("registered site must be the item cell: %+v", mem.Sites[0])
	}
}

// THE AGE-OUT CONTRACT: colony memory must never ride a world save — a restart forgets
// trails and the scouts re-learn them (Unbounded-Growth lens; server-only soft state).
func TestColonyMemoryNeverSaved(t *testing.T) {
	state, _ := antTestState()
	key := nestKeyFor(10, 10)
	state.NestStates[key] = &entities.NestState{GridX: 10, GridY: 10, EntityID: "ant_brood"}
	registerCarrionSite(state, key, 20, 10, 50, []entities.RoutePoint{{X: 1, Y: 1}})
	if state.ScoutPaths == nil {
		state.ScoutPaths = make(map[string][]entities.RoutePoint)
	}
	state.ScoutPaths["s1"] = []entities.RoutePoint{{X: 2, Y: 2}}

	m := &Match{}
	save := m.buildWorldSave(state)
	fresh, _ := antTestState()
	m.restoreWorldSave(fresh, save, nopRuntimeLogger())
	if len(fresh.ColonyMemory) != 0 || len(fresh.ScoutPaths) != 0 {
		t.Fatalf("colony memory/scout paths must NOT survive a save round-trip: mem=%d paths=%d",
			len(fresh.ColonyMemory), len(fresh.ScoutPaths))
	}
}