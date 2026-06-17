package world

// Host plants (milkweed): butterfly breeding capacity regrows over time and caps at max.
// The depletable-flag + breeding integration is covered by the headless bug_lab harness run.
// Run:  go test ./world/ -run TestProcessHostPlants -v

import (
	"testing"

	"bugfarmer/entities"
)

// The crux of butterfly breeding: a milkweed occupant must surface from FindNearbyFood as a
// DEPLETABLE hit while it has capacity (so the reproducing-phase filter, which keeps only
// depletable sources, lets a butterfly breed there) — and must be SKIPPED ENTIRELY once grazed
// out, so breeding halts until it regrows. This is the mechanism the headless lab exercises end
// to end; here we prove it deterministically without waiting on the slow feed→sate→breed timing.
func TestFindNearbyFoodMilkweedDepletable(t *testing.T) {
	state := newTestState(20)
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	state.Chunks[ChunkKey(0, 0)].SetOccupant(10, 10, &PlacedOccupant{ID: "milkweed", Anchor: true})

	// A butterfly standing two cells away, reproducing-phase interest = ["milkweed"].
	pos := entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 12, LocalY: 10}

	// 1) With capacity, milkweed is a depletable breeding source.
	state.HostPlantStates["10,10"] = &entities.HostPlantState{EntityID: "milkweed", GridX: 10, GridY: 10, Capacity: 50}
	hits := FindNearbyFood(state, pos, 24, []string{"milkweed"})
	if len(hits) != 1 {
		t.Fatalf("expected 1 milkweed hit, got %d: %+v", len(hits), hits)
	}
	if hits[0].ID != "milkweed" || !hits[0].Depletable {
		t.Fatalf("milkweed with capacity must be a DEPLETABLE hit, got %+v", hits[0])
	}

	// 2) Grazed out (capacity 0): skipped entirely — a reproducing butterfly finds nothing here.
	state.HostPlantStates["10,10"].Capacity = 0
	if hits := FindNearbyFood(state, pos, 24, []string{"milkweed"}); len(hits) != 0 {
		t.Fatalf("grazed-out milkweed must be skipped, got %+v", hits)
	}

	// 3) A milkweed with NO host-plant state registered (e.g. outside a loaded chunk's init) is a
	//    non-depletable occupant — feeding flavor only, never a breeding source.
	delete(state.HostPlantStates, "10,10")
	hits = FindNearbyFood(state, pos, 24, []string{"milkweed"})
	if len(hits) != 1 || hits[0].Depletable {
		t.Fatalf("unregistered milkweed must be a NON-depletable occupant, got %+v", hits)
	}
}

// Regression: a milkweed target is DEPLETABLE, so it runs the per-tick "is my food source still
// alive?" clear-check. foodSourceAlive must recognise a host-plant occupant (keyed by position) —
// otherwise the milkweed target is cleared every tick and a reproducing butterfly can never park on
// it to breed (the bug that made butterflies reach 'reproducing' but stay target="").
func TestFoodSourceAliveHostPlant(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.HostPlantStates["58,18"] = &entities.HostPlantState{EntityID: "milkweed", GridX: 58, GridY: 18, Capacity: 100}

	if !m.foodSourceAlive(state, "milkweed", 58, 18) {
		t.Fatal("milkweed with capacity must be alive (else its target is cleared every tick)")
	}
	state.HostPlantStates["58,18"].Capacity = 0
	if m.foodSourceAlive(state, "milkweed", 58, 18) {
		t.Fatal("grazed-out milkweed must be dead so the target clears and breeding stops")
	}
	// No host-plant registered at that cell → not alive (nothing to breed on).
	if m.foodSourceAlive(state, "milkweed", 99, 99) {
		t.Fatal("unregistered cell must not be a live food source")
	}
}

func TestProcessHostPlantsRegrows(t *testing.T) {
	state := newTestState(20)
	state.HostPlantStates["10,10"] = &entities.HostPlantState{EntityID: "milkweed", GridX: 10, GridY: 10, Capacity: 50}
	m := &Match{}

	m.processHostPlants(state)
	if got := state.HostPlantStates["10,10"].Capacity; got <= 50 {
		t.Fatalf("capacity did not regrow: %f", got)
	}

	// regrowth caps at max
	state.HostPlantStates["10,10"].Capacity = maxHostCapacity
	m.processHostPlants(state)
	if got := state.HostPlantStates["10,10"].Capacity; got != maxHostCapacity {
		t.Fatalf("capacity exceeded max: %f", got)
	}
}
