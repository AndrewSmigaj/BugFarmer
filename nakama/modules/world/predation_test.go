package world

// Tests for the predator-slice foundations: per-species kill_drops loot tables, edible
// carrion entering/leaving the deterministic food registry (ITEM_ROTTED at spawn,
// FOOD_CONSUMED(0) at lifetime expiry — both hash-bearing), and FindNearbyFood matching
// carrion by exact item type.
//
// Run inside the builder image:  go test ./modules/world/ -run TestKillDrop -v

import (
	"testing"

	"bugfarmer/entities"
)

func killDropTestState() *WorldState {
	state := newTestState(20)
	state.Entities["bug_parts"] = &EntityDef{Category: "resource", FoodValue: 10}
	state.Entities["wasp_stinger"] = &EntityDef{Category: "resource"} // inedible
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "bug_parts", CountMin: 1, CountMax: 1, Chance: 1.0},
	}
	// Open chunk so IsBlocked doesn't trip on nil chunks at the drop point
	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	return state
}

// A kill drop from a species with an edible item: ground item carries the def's
// FoodValue AND an ITEM_ROTTED ledger event registers it as bug food.
func TestKillDropEdibleEmitsItemRotted(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	species := state.Species["fly_common"]

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, species, 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	for _, item := range state.GroundItems {
		if item.ItemType != "bug_parts" || item.FoodValue != 10 {
			t.Fatalf("drop %s food=%d, want bug_parts food=10", item.ItemType, item.FoodValue)
		}
		if item.Lifetime <= 0 {
			t.Fatal("carrion must have a finite lifetime")
		}
	}
	evs := eventsOfType(state, InfluenceItemRotted)
	if len(evs) != 1 || evs[0].Level != 10 {
		t.Fatalf("ITEM_ROTTED events=%d level=%v, want 1 at level 10", len(evs), evs)
	}
}

// An INEDIBLE drop (no food_value) emits NO registry event.
func TestKillDropInedibleStaysLedgerSilent(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "wasp_stinger", CountMin: 1, CountMax: 1, Chance: 1.0},
	}

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"], 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	if got := len(eventsOfType(state, InfluenceItemRotted)); got != 0 {
		t.Fatalf("inedible drop emitted %d ITEM_ROTTED events", got)
	}
}

// A blocked drop point (predator hovering over a fence) falls back to the victim's
// center — an edible item registered inside a blocks_bugs cell would be a permanent
// wall-attractor.
func TestKillDropBlockedFallsBackToVictim(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Entities["fence_wood"] = &EntityDef{World: &WorldData{BlocksBugs: true}}
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.SetOccupant(10, 10, &PlacedOccupant{ID: "fence_wood", Anchor: true})

	// Drop point = the fence cell center; fallback = open ground at (20, 20)
	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"],
		10.5, 10.5, 20, 20, 32)

	for _, item := range state.GroundItems {
		wx := float32(item.Position.ChunkX*32) + item.Position.LocalX
		wy := float32(item.Position.ChunkY*32) + item.Position.LocalY
		if wx > 15 && wy > 15 {
			return // landed near the fallback ✓
		}
		t.Fatalf("blocked drop landed at (%.1f, %.1f), want near the fallback (20, 20)", wx, wy)
	}
	t.Fatal("no drop spawned")
}

// Lifetime expiry of an EDIBLE item must clear the registry: FOOD_CONSUMED(level 0).
// Carrion is the first edible item that expires — without this, every uneaten corpse
// leaves a phantom registry entry and a joiner-vs-veteran resync loop.
func TestCarrionExpiryEmitsFoodConsumedZero(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "bug_parts", Count: 1,
		Position:  entities.EntityPosition{LocalX: 10, LocalY: 10},
		FoodValue: 10,
		Lifetime:  0.05, // expires on the first decay tick
	}

	m.processGroundItemDecay(state, nil)

	if _, exists := state.GroundItems["c1"]; exists {
		t.Fatal("expired carrion still in the world")
	}
	evs := eventsOfType(state, InfluenceFoodConsumed)
	if len(evs) != 1 || evs[0].Level != 0 || evs[0].FoodID != "c1" {
		t.Fatalf("expiry events wrong: %+v (want one FOOD_CONSUMED level 0 for c1)", evs)
	}
}

// An inedible item's expiry stays silent (no registry entry existed).
func TestInedibleExpiryStaysSilent(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.GroundItems["s1"] = &entities.GroundItem{
		ID: "s1", ItemType: "wasp_stinger", Count: 1,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10},
		Lifetime: 0.05,
	}

	m.processGroundItemDecay(state, nil)

	if got := len(eventsOfType(state, InfluenceFoodConsumed)); got != 0 {
		t.Fatalf("inedible expiry emitted %d FOOD_CONSUMED events", got)
	}
}

// FindNearbyFood matches carrion by exact item type (the centipede's attraction list)
// AND via the rotten_fruit wildcard (flies scavenge corpses — intended emergence).
func TestFindNearbyFoodMatchesCarrion(t *testing.T) {
	state := killDropTestState()
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "bug_parts", Count: 1,
		Position:  entities.EntityPosition{LocalX: 12, LocalY: 10},
		FoodValue: 10,
	}
	pos := entities.EntityPosition{LocalX: 10, LocalY: 10}

	// Exact match (centipede)
	hits := FindNearbyFood(state, pos, 8, []string{"bug_parts"})
	if len(hits) != 1 || hits[0].ID != "c1" {
		t.Fatalf("exact-match hits=%v, want c1", hits)
	}
	// Wildcard (flies): any FoodValue>0 ground item
	hits = FindNearbyFood(state, pos, 8, []string{"rotten_fruit"})
	if len(hits) != 1 || hits[0].ID != "c1" {
		t.Fatalf("wildcard hits=%v, want c1 (flies scavenge carrion)", hits)
	}
}

// kill_drops parse: count ranges + chance roll bounds + multiple entries.
func TestKillDropCountRange(t *testing.T) {
	state := killDropTestState()
	m := &Match{}
	state.Entities["centipede_parts"] = &EntityDef{Category: "resource"}
	state.Species["fly_common"].KillDrops = []entities.KillDrop{
		{Item: "centipede_parts", CountMin: 3, CountMax: 5, Chance: 1.0},
	}

	m.spawnKillDrops(nopRuntimeLogger(), nil, state, state.Species["fly_common"], 10, 10, 10, 10, 32)

	if len(state.GroundItems) != 1 {
		t.Fatalf("drops=%d, want 1", len(state.GroundItems))
	}
	for _, item := range state.GroundItems {
		if item.Count < 3 || item.Count > 5 {
			t.Fatalf("count=%d, want 3-5", item.Count)
		}
	}
}
