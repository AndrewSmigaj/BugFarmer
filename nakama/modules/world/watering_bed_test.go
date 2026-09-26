package world

// #15 (can't water an empty bed): handleWatering used to reject bare tilled soil with "No crop here".
// Now watering a bare garden_plot flips it to garden_plot_wet + consumes a use; already-wet soil is a
// silent no-op. Revert the bare-soil block in handleWatering and this test fails.
// Run:  go test ./world/ -run TestWaterBareBed -v

import (
	"testing"
)

func TestWaterBareBedWetsTilledSoil(t *testing.T) {
	state := newTestState(20)
	state.Players = map[string]*PlayerState{}
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.Ground[10][10] = "garden_plot" // tilled but unplanted

	p := testPlayer(10, 10, "watering_can")
	p.ItemSlots[0] = InventorySlot{ItemID: "watering_can", Metadata: map[string]int{"uses": 5}}
	state.Players["p1"] = p

	m := &Match{}
	m.handleWatering(nopRuntimeLogger(), nopDispatcher{}, state, "p1", 10, 10, 500)

	if got := chunk.GetGroundTile(10, 10); got != "garden_plot_wet" {
		t.Fatalf("bare bed tile = %q after watering, want garden_plot_wet (the #15 fix)", got)
	}
	if uses := p.ItemSlots[0].Metadata["uses"]; uses != 4 {
		t.Fatalf("watering can uses = %d, want 4 (one consumed)", uses)
	}

	// Watering already-wet soil is a silent no-op — accepted, but no wasted use.
	m.handleWatering(nopRuntimeLogger(), nopDispatcher{}, state, "p1", 10, 10, 600)
	if uses := p.ItemSlots[0].Metadata["uses"]; uses != 4 {
		t.Fatalf("watering already-wet soil consumed a use (uses=%d), want it left at 4", uses)
	}
}
