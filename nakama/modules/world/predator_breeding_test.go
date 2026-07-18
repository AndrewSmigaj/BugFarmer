package world

// The carnivore "well-fed timer" breeding (processPredatorBreeding): a NESTLESS predator that's well-fed
// reproduces on its cooldown. Pure hunters can't breed through the standard sated→reproducing→dine path
// (a kill tops satiation to ~95, the flip needs 100, and they have no carrion attraction), so without this
// they die as a same-age re-seeded cohort.
//
// Run inside the builder image:  go test ./modules/world/ -run TestPredatorBreed -v

import "testing"

func TestPredatorBreedsWhenWellFed(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	species := state.Species[cent.SpeciesID]
	species.MaxSwarmSize = 5    // headroom to grow in place
	species.ReproduceCooldown = 300 // re-armed after a breed
	cent.Count = 2
	cent.Satiation = predatorBreedSatiation + 5
	cent.ReproduceCooldown = 0 // CanReproduce() true
	state.Swarms[cent.ID] = cent
	state.SwarmsBySpecies[cent.SpeciesID] = []string{cent.ID}

	broodsBefore := len(state.BroodStates)
	m.processPredatorBreeding(state, nil, nopRuntimeLogger())

	// A nestless predator breeds by laying a VISIBLE brood (an egg clutch that develops + hatches
	// into pack members later), NOT an instant pop-out — the breeding-unify model. Centipedes joined
	// this path when they became category:"swarm" packs (they have egg/larva art).
	if len(state.BroodStates) <= broodsBefore {
		t.Fatalf("a well-fed nestless predator must lay a brood: broods %d -> %d", broodsBefore, len(state.BroodStates))
	}
	if cent.ReproduceCooldown <= 0 {
		t.Fatal("breeding must re-arm the reproduce cooldown (forces a re-hunt before the next breed)")
	}
}

func TestPredatorNoBreedWhenHungry(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	cent.Count = 2
	cent.Satiation = predatorBreedSatiation - 20 // not well-fed
	cent.ReproduceCooldown = 0
	state.Swarms[cent.ID] = cent
	state.SwarmsBySpecies[cent.SpeciesID] = []string{cent.ID}

	before := state.SpeciesPopulation(cent.SpeciesID)
	m.processPredatorBreeding(state, nil, nopRuntimeLogger())

	if state.SpeciesPopulation(cent.SpeciesID) != before {
		t.Fatalf("a hungry predator must NOT reproduce, pop changed %d -> %d", before, state.SpeciesPopulation(cent.SpeciesID))
	}
}
