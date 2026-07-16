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

	// The pile isn't "source-gone" (piles detach from their food); its remaining maggots develop to adults
	// on the brood clock and hatch, then the empty pile retires. (Source broods now dwell per stage, so the
	// hatch takes the clock rather than a single instant call.) Ground piles live under the "g:" key namespace.
	pileKey := "g:10,10"
	maxIters := int(entities.BroodEggMatureTicks/30) + 20
	for i := 0; i < maxIters && state.BroodStates[pileKey] != nil; i++ {
		m.processBroods(state, nil, nopRuntimeLogger())
	}

	if state.BroodStates[pileKey] != nil {
		t.Fatal("a pile must clear once its maggots have hatched out")
	}
	if swarm.Count != 8 {
		t.Fatalf("the pile should hatch its 2 remaining maggots: count=%d", swarm.Count)
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

// Pupating SOURCE brood: egg -> larva -> PUPA -> adult. The pupa stage is reached before hatching, and the
// split timing keeps total dev time within the old egg->maggot budget (no ecology re-tune).
func TestBroodSourcePupatesFullCycle(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	state.Species["fly_common"].PupaSpriteID = "fly_pupa" // data-driven: a pupa sprite => this species pupates
	swarm := newTestSwarm("s", 6, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}

	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "ground_pile", "food1", 12)
	if got := m.layEggs(nil, state, b, 2); got != 2 {
		t.Fatalf("expected 2 eggs laid, got %d", got)
	}
	state.GroundItems["food1"] = &entities.GroundItem{ID: "food1", FoodValue: 100,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10}}

	start := swarm.Count
	sawPupa := false
	maxIters := int(entities.BroodEggMatureTicks/30) + 20 // same budget as the non-pupating model
	for i := 0; i < maxIters && swarm.Count == start; i++ {
		m.processBroods(state, nil, nopRuntimeLogger())
		if b.Pupae > 0 {
			sawPupa = true
		}
	}
	if !sawPupa {
		t.Fatal("a pupating source brood must pass through the PUPA stage (Pupae>0) before hatching")
	}
	if swarm.Count <= start {
		t.Fatalf("pupating brood never hatched within the preserved tick budget: count=%d", swarm.Count)
	}
	if len(eventsOfType(state, InfluenceSwarmReproduced)) == 0 {
		t.Fatal("a hatch must emit SWARM_REPRODUCED")
	}
}

// Nests pupate too (wasps/bees are holometabolous): a nest brood of a pupating species runs the full
// egg->larva->pupa->adult ladder and hatches from Pupae, and nestBroodCount counts pupae so the nest economy
// (founding/recovery) still sees the whole brood. Only a species with NO pupa sprite stays egg->larva->adult.
func TestBroodNestPupates(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	state.Species["fly_common"].PupaSpriteID = "fly_pupa" // a pupating species...

	nestB := &entities.BroodState{SpeciesID: "fly_common", SourceKind: "nest", Eggs: 2, Maggots: 1, Pupae: 3}
	if !m.broodPupates(state, nestB) {
		t.Fatal("a nest brood of a pupating species must pupate")
	}
	if got := m.broodReadyToHatch(state, nestB); got != 3 {
		t.Fatalf("a pupating nest brood hatches from Pupae: readyToHatch=%d want 3", got)
	}
	// nestBroodCount must include pupae so founding/recovery see the full brood.
	nest := &entities.NestState{GridX: 5, GridY: 6, SpeciesID: "fly_common"}
	nestB.SourceID = ""
	state.BroodStates[broodKey(5, 6)] = nestB
	if got := m.nestBroodCount(state, nest); got != 2+1+3 {
		t.Fatalf("nestBroodCount must count eggs+maggots+pupae: got %d want 6", got)
	}

	// A species with NO pupa sprite stays egg->larva->adult (hatches from Maggots).
	state.Species["millipede"] = &entities.BugSpecies{Category: "swarm"}
	noPupaB := &entities.BroodState{SpeciesID: "millipede", SourceKind: "ground_pile", Maggots: 2}
	if m.broodPupates(state, noPupaB) {
		t.Fatal("a species with no pupa sprite must NOT pupate")
	}
	if got := m.broodReadyToHatch(state, noPupaB); got != 2 {
		t.Fatalf("a non-pupating brood hatches from Maggots: readyToHatch=%d want 2", got)
	}
}

// Regression (the maturation-order bug): a CONTINUOUSLY-laid pupating brood must still hatch. If maturation
// advanced egg->larva first, incoming eggs would starve pupation and larvae would pile up forever (a
// population crash). Later-stage-first keeps larvae flowing to pupae->adults even while eggs keep arriving.
func TestBroodPupatingKeepsHatchingUnderContinuousLay(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	state.Species["fly_common"].PupaSpriteID = "fly_pupa"
	swarm := newTestSwarm("s", 6, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}

	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "ground_pile", "food1", 30)
	state.GroundItems["food1"] = &entities.GroundItem{ID: "food1", FoodValue: 100,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10}}

	start := swarm.Count
	for i := 0; i < 120; i++ {
		if i%5 == 0 {
			m.layEggs(nil, state, b, 1) // a fly keeps breeding at the pile — Eggs is rarely 0
		}
		m.processBroods(state, nil, nopRuntimeLogger())
	}
	if swarm.Count <= start {
		t.Fatalf("continuously-laid pupating brood never hatched (larvae starved pupation?): count=%d larvae=%d pupae=%d",
			swarm.Count, b.Maggots, b.Pupae)
	}
}
