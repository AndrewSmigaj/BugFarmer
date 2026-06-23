package world

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
	"testing"

	"bugfarmer/entities"
)

// These tests pin the ground-item chunk index (item_index.go) that FindNearbyFood scans instead of the
// whole GroundItems map. The contract is EXACTNESS: the indexed scan must return the byte-identical set a
// full scan would. bruteForceGroundFood replicates the OLD full-scan backing #1 as the reference oracle.

func bruteForceGroundFood(state *WorldState, pos entities.EntityPosition, vision float32, targets []string) []FoodHit {
	targetSet := make(map[string]bool, len(targets))
	for _, id := range targets {
		targetSet[id] = true
	}
	cs := state.Config.ChunkSize
	worldX := float32(pos.ChunkX*cs) + pos.LocalX
	worldY := float32(pos.ChunkY*cs) + pos.LocalY
	wantRotten := targetSet["rotten_fruit"]
	var hits []FoodHit
	for id, item := range state.GroundItems { // full scan — the thing the index replaces
		if item.FoodValue <= 0 {
			continue
		}
		if !targetSet[item.ItemType] && (!wantRotten || item.IsCarrion) {
			continue
		}
		ix := float32(item.Position.ChunkX*cs) + item.Position.LocalX
		iy := float32(item.Position.ChunkY*cs) + item.Position.LocalY
		dx, dy := ix-worldX, iy-worldY
		dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
		if dist <= vision {
			hits = append(hits, FoodHit{ID: id, Kind: "item", X: ix, Y: iy, Dist: dist, Depletable: true})
		}
	}
	sort.Slice(hits, func(i, j int) bool {
		if hits[i].Dist != hits[j].Dist {
			return hits[i].Dist < hits[j].Dist
		}
		return hits[i].ID < hits[j].ID
	})
	return hits
}

// indexOnlyState is a minimal WorldState with ONLY ground items (no stations, no occupants) so
// FindNearbyFood's result is exactly its ground-item backing — isolating the index under test.
func indexOnlyState() *WorldState {
	return &WorldState{
		Config:          WorldConfig{ChunkSize: 32},
		GroundItems:     map[string]*entities.GroundItem{},
		ItemsByChunk:    map[string]map[string]*entities.GroundItem{},
		Stations:        map[string]*entities.StationState{},
		Chunks:          map[string]*ChunkData{},
		HostPlantStates: map[string]*entities.HostPlantState{},
		ForagePools:     map[string]*entities.ForagePoolState{},
	}
}

func TestFindNearbyFoodIndexEqualsBruteForce(t *testing.T) {
	rng := rand.New(rand.NewSource(0xBEEF))
	itemTypes := []string{"rotten_apple", "rotten_orange", "dead_fly", "acorn"}
	targetSets := [][]string{
		{"rotten_fruit"},
		{"dead_fly"},
		{"rotten_fruit", "dead_fly"},
		{"acorn"},
		{"rotten_apple"},
	}

	for trial := 0; trial < 500; trial++ {
		state := indexOnlyState()
		n := rng.Intn(40)
		for i := 0; i < n; i++ {
			// Mix normalized and UN-normalized local coords (incl. negatives / >= ChunkSize) to prove the
			// world-coord floor bucketing is robust regardless of how a creation site stores Position.
			pos := entities.EntityPosition{
				ChunkX: rng.Intn(5),
				ChunkY: rng.Intn(5),
				LocalX: float32(rng.Intn(42)) - 5, // [-5, 37)
				LocalY: float32(rng.Intn(42)) - 5,
			}
			fv := 0
			if rng.Intn(4) != 0 { // ~75% edible
				fv = 1 + rng.Intn(100)
			}
			it := itemTypes[rng.Intn(len(itemTypes))]
			state.putGroundItem(&entities.GroundItem{
				ID:        fmt.Sprintf("it_%d", i),
				ItemType:  it,
				Count:     1,
				Position:  pos,
				FoodValue: fv,
				IsCarrion: it == "dead_fly",
			})
		}

		qpos := entities.EntityPosition{
			ChunkX: rng.Intn(5),
			ChunkY: rng.Intn(5),
			LocalX: float32(rng.Intn(32)),
			LocalY: float32(rng.Intn(32)),
		}
		vision := 1 + rng.Float32()*40
		targets := targetSets[rng.Intn(len(targetSets))]

		got := FindNearbyFood(state, qpos, vision, targets)
		want := bruteForceGroundFood(state, qpos, vision, targets)

		if !sameHits(got, want) {
			t.Fatalf("trial %d: index != brute-force\n  items=%d vision=%.2f targets=%v\n  got =%v\n  want=%v",
				trial, n, vision, targets, got, want)
		}
		if err := state.AssertItemIndexConsistent(); err != nil {
			t.Fatalf("trial %d: index inconsistent after build: %v", trial, err)
		}
	}
}

func sameHits(a, b []FoodHit) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i].ID != b[i].ID || a[i].Kind != b[i].Kind || a[i].Dist != b[i].Dist ||
			a[i].X != b[i].X || a[i].Y != b[i].Y || a[i].Depletable != b[i].Depletable {
			return false
		}
	}
	return true
}

// The funnel-completeness backstop: random add/overwrite/delete churn must always leave ItemsByChunk an
// exact mirror of GroundItems (this is what proves no production mutation site can quietly desync them).
func TestItemIndexConsistencyUnderChurn(t *testing.T) {
	rng := rand.New(rand.NewSource(0x1234))
	state := indexOnlyState()
	for step := 0; step < 4000; step++ {
		id := fmt.Sprintf("it_%d", rng.Intn(60)) // small id space → frequent overwrite + delete-existing
		switch rng.Intn(3) {
		case 0, 1: // put (new or overwrite at a possibly-different position)
			state.putGroundItem(&entities.GroundItem{
				ID:       id,
				ItemType: "rotten_apple",
				Position: entities.EntityPosition{
					ChunkX: rng.Intn(6), ChunkY: rng.Intn(6),
					LocalX: float32(rng.Intn(42)) - 5, LocalY: float32(rng.Intn(42)) - 5,
				},
				FoodValue: 100,
			})
		case 2: // delete (sometimes a no-op on an absent id)
			state.deleteGroundItem(id)
		}
		if err := state.AssertItemIndexConsistent(); err != nil {
			t.Fatalf("step %d: %v", step, err)
		}
	}
	// And a full rebuild must agree with the incrementally-maintained index.
	maintained := state.ItemsByChunk
	state.ItemsByChunk = nil
	state.RebuildItemIndex()
	if len(maintained) != len(state.ItemsByChunk) {
		t.Fatalf("rebuilt bucket count %d != maintained %d", len(state.ItemsByChunk), len(maintained))
	}
	if err := state.AssertItemIndexConsistent(); err != nil {
		t.Fatalf("post-rebuild inconsistent: %v", err)
	}
}
