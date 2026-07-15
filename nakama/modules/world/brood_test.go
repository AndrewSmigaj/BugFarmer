package world

// Visible breeding broods: flies/butterflies lay eggs into a BroodState at the source; processBroods
// matures eggs -> maggots and hatches them into the camped swarm via SWARM_REPRODUCED. Broods are
// soft state (never hashed) — these tests pin the server economy; the headless bug_lab harness covers
// the end-to-end loop + determinism.

import (
	"testing"

	"bugfarmer/entities"
)

// Lay -> mature -> hatch: eggs laid in a brood eventually grow the camped swarm (deferred, not instant).
func TestBroodLifecycleLayMatureHatch(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 6, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}

	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "ground_pile", "food1", 12)
	if got := m.layEggs(nil, state, b, 2); got != 2 {
		t.Fatalf("expected 2 eggs laid, got %d", got)
	}
	// food must exist so the source-gone sweep doesn't fire first
	state.GroundItems["food1"] = &entities.GroundItem{ID: "food1", FoodValue: 100,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10}}

	start := swarm.Count
	// Loop bound scales with the maturation clock so slowing BroodEggMatureTicks doesn't break the test
	// (processBroods advances StageProgress by its 30-tick interval each call).
	maxIters := int(entities.BroodEggMatureTicks/30) + 20
	for i := 0; i < maxIters && swarm.Count == start; i++ {
		m.processBroods(state, nil, nopRuntimeLogger())
	}
	if swarm.Count <= start {
		t.Fatalf("brood never hatched into the swarm: count=%d", swarm.Count)
	}
	if len(eventsOfType(state, InfluenceSwarmReproduced)) == 0 {
		t.Fatal("a hatch into the camped swarm must emit SWARM_REPRODUCED")
	}
}

// Hatch respects the population cap (the nest's at-cap banking): hold maggots until room frees up.
func TestBroodHatchHoldsAtCap(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 10, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {Max: 10, MaxPopulation: 10}, // exactly at cap
	}}
	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "station", "station_10_10", 12)
	b.Maggots = 4

	if got := m.hatchFromBrood(state, b); got != 0 {
		t.Fatalf("hatch at the population cap must HOLD, got %d", got)
	}
	if b.Maggots != 4 || swarm.Count != 10 {
		t.Fatalf("nothing should hatch at cap: maggots=%d count=%d", b.Maggots, swarm.Count)
	}

	state.CurrentZone.BugSpawning.SpeciesCaps["fly_common"] = SpeciesCap{Max: 10, MaxPopulation: 13}
	if got := m.hatchFromBrood(state, b); got != 2 {
		t.Fatalf("with room for 3, a hatch of BroodHatchCount=2 should fire, got %d", got)
	}
	if swarm.Count != 12 || b.Maggots != 2 {
		t.Fatalf("hatch should grow the swarm by 2: count=%d maggots=%d", swarm.Count, b.Maggots)
	}
}

// A maggot pile vanishes when its food is gone: the sweep hatches the remaining maggots, then clears it.
func TestBroodGroundPileSweepHatchesAndClears(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 6, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "ground_pile", "food1", 12)
	b.Maggots = 2
	// GroundItems has no "food1" → the food has been consumed away.

	m.processBroods(state, nil, nopRuntimeLogger())

	if state.BroodStates["10,10"] != nil {
		t.Fatal("a pile must clear once its food is gone")
	}
	if swarm.Count != 8 {
		t.Fatalf("the sweep should hatch the 2 remaining maggots: count=%d", swarm.Count)
	}
}

// The nursery has a capacity (food-scaled for a pile): laying beyond it is clamped, a full brood rejects.
func TestBroodEggCapClamps(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	b := m.getOrCreateBrood(state, 5, 5, "fly_common", "ground_pile", "food1", 3) // cap 3
	if got := m.layEggs(nil, state, b, 5); got != 3 {
		t.Fatalf("lay must clamp to capacity: accepted %d, want 3", got)
	}
	if got := m.layEggs(nil, state, b, 2); got != 0 {
		t.Fatalf("a full nursery must accept 0, got %d", got)
	}
	if b.Eggs != 3 {
		t.Fatalf("eggs=%d, want 3", b.Eggs)
	}
}
