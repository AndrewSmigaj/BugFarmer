package world

// Forage pools (flower nectar) + starvation: the boom-bust engine. A depletable flower feeds bugs until
// grazed out, then is skipped (so an over-large population can't feed) → it starves back via
// processStarvation. The full oscillation is tuned on the bug_lab population graph; these pin the parts.

import (
	"testing"

	"bugfarmer/entities"
)

// A flower with nectar is a DEPLETABLE feeding hit; grazed-out it's skipped; unregistered it's plain
// (non-depletable) — mirrors the milkweed depletable test.
func TestFindNearbyFoodFlowerNectarDepletable(t *testing.T) {
	state := newTestState(20)
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	state.Chunks[ChunkKey(0, 0)].SetOccupant(10, 10, &PlacedOccupant{ID: "flower_wild", Anchor: true})
	pos := entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 12, LocalY: 10}

	state.ForagePools["10,10"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 10, GridY: 10, Nectar: 50}
	hits := FindNearbyFood(state, pos, 24, []string{"flower_wild"})
	if len(hits) != 1 || hits[0].ID != "flower_wild" || !hits[0].Depletable {
		t.Fatalf("flower with nectar must be a depletable feeding hit, got %+v", hits)
	}

	state.ForagePools["10,10"].Nectar = 0
	if hits := FindNearbyFood(state, pos, 24, []string{"flower_wild"}); len(hits) != 0 {
		t.Fatalf("grazed-out flower must be skipped (starve the over-large pop), got %+v", hits)
	}

	delete(state.ForagePools, "10,10")
	hits = FindNearbyFood(state, pos, 24, []string{"flower_wild"})
	if len(hits) != 1 || hits[0].Depletable {
		t.Fatalf("unregistered flower must be a plain non-depletable occupant, got %+v", hits)
	}
}

func TestForagePoolRegrows(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.ForagePools["5,5"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 5, GridY: 5, Nectar: 10}
	m.processForagePools(state)
	if state.ForagePools["5,5"].Nectar <= 10 {
		t.Fatalf("nectar did not regrow: %f", state.ForagePools["5,5"].Nectar)
	}
	state.ForagePools["5,5"].Nectar = maxNectar
	m.processForagePools(state)
	if state.ForagePools["5,5"].Nectar != maxNectar {
		t.Fatalf("nectar exceeded max: %f", state.ForagePools["5,5"].Nectar)
	}
}

func TestFoodSourceAliveForagePool(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.ForagePools["5,5"] = &entities.ForagePoolState{GridX: 5, GridY: 5, Nectar: 100}
	if !m.foodSourceAlive(state, "flower_wild", 5, 5) {
		t.Fatal("flower with nectar must be alive (else its target clears every tick)")
	}
	state.ForagePools["5,5"].Nectar = 0
	if m.foodSourceAlive(state, "flower_wild", 5, 5) {
		t.Fatal("grazed-out flower must be dead so a starving bug re-thinks")
	}
}

// A swarm starving past the threshold loses a fraction of its bugs (the bust); a fed swarm is untouched.
func TestProcessStarvationCulls(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 20, 10, 10)
	swarm.StarveTimer = starvationDeathSecs + 1 // starving past the threshold
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}

	m.processStarvation(nopRuntimeLogger(), nil, state, 32)
	if swarm.Count != 18 { // 10% of 20 = 2 culled
		t.Fatalf("starving swarm should lose 10%% (20 -> 18), got %d", swarm.Count)
	}
	if swarm.StarveTimer != starvationDeathSecs-starvationCullPause {
		t.Fatalf("timer should re-arm to %f for the next cull, got %f", starvationDeathSecs-starvationCullPause, swarm.StarveTimer)
	}

	swarm.StarveTimer = 0 // recently fed → not starving
	m.processStarvation(nopRuntimeLogger(), nil, state, 32)
	if swarm.Count != 18 {
		t.Fatalf("a fed swarm must not be culled, got %d", swarm.Count)
	}
}
