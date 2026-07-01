package world

// #10 (moved compost can't accept deposits): resolveStation lazily creates a StationState for a station
// occupant that has none yet — the moved/runtime-placed case, since initStationsInChunk only scans at
// chunk-load. Revert resolveStation (back to a bare state.Stations[key] lookup) and this test fails.
// Run:  go test ./world/ -run TestResolveStation -v

import (
	"testing"

	"bugfarmer/entities"
)

func TestResolveStationLazyCreatesForPlacedBin(t *testing.T) {
	state := newTestState(20)
	state.Entities["compost_bin"] = &EntityDef{World: &WorldData{Station: &StationData{Capacity: 10, FoodPerUnit: 100}}}
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	state.Chunks[ChunkKey(0, 0)].SetOccupant(10, 10, &PlacedOccupant{ID: "compost_bin", Anchor: true})
	m := &Match{}

	// Precondition: a bin placed into an already-loaded chunk has NO StationState.
	if state.Stations[entities.StationKey(10, 10)] != nil {
		t.Fatal("precondition: expected no pre-existing station state")
	}

	st := m.resolveStation(state, 10, 10)
	if st == nil {
		t.Fatal("resolveStation returned nil for an anchored compost occupant (the #10 bug)")
	}
	if state.Stations[entities.StationKey(10, 10)] != st {
		t.Fatal("resolveStation did not store the created state in state.Stations")
	}
	if st.EntityID != "compost_bin" || st.GridX != 10 || st.GridY != 10 || st.InputCount != 0 {
		t.Fatalf("created station has wrong fields: %+v", st)
	}

	// Idempotent: a second resolve returns the SAME state (no duplicate creation).
	if m.resolveStation(state, 10, 10) != st {
		t.Fatal("resolveStation is not idempotent — created a duplicate")
	}

	// No occupant there -> nil (never conjure a phantom station).
	if m.resolveStation(state, 20, 20) != nil {
		t.Fatal("resolveStation created a station where no occupant is anchored")
	}

	// A non-station occupant -> nil (only world.station occupants become stations).
	state.Entities["tree_oak"] = &EntityDef{World: &WorldData{}}
	state.Chunks[ChunkKey(0, 0)].SetOccupant(12, 12, &PlacedOccupant{ID: "tree_oak", Anchor: true})
	if m.resolveStation(state, 12, 12) != nil {
		t.Fatal("resolveStation created a station for a non-station occupant")
	}
}
