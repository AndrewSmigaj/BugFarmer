package world

// Unit tests for the fruit-tree state machine (tank model):
//
//	DORMANT -(3 waterings, 1 manual/day; rain free)-> full tank
//	  -> BATCH only when EMPTY (tank consumed, Pending = MaxFruit, countdown)
//	  -> GROWING one fruit per fruit_grow_ticks (DropTimer resets ONLY on 0->1)
//	  -> ripe fruit falls STAGGERED in the evening window, >= 500 ticks apart.
//
// Run inside the builder image:  go test ./modules/world/ -run TestTree -v

import (
	"testing"

	"bugfarmer/entities"
)

// treeTestState builds a world with one fast fruit tree at (5,5) and returns both.
func treeTestState(maxFruit, growTicks, dropTicks int) (*WorldState, *entities.FruitTreeState) {
	state := newTestState(20)
	state.Entities["tree_test"] = &EntityDef{World: &WorldData{
		FruitType: "apple", MaxFruit: maxFruit,
		FruitGrowTicks: growTicks, FruitDropTicks: dropTicks,
	}}
	chunk := NewEmptyChunk(0, 0, "grass")
	chunk.SetOccupant(5, 5, &PlacedOccupant{ID: "tree_test", Anchor: true})
	state.Chunks[ChunkKey(0, 0)] = chunk
	tree := &entities.FruitTreeState{
		TreeID: "tree_5_5", EntityID: "tree_test", GridX: 5, GridY: 5,
		MaxFruit: maxFruit, LastWaterDay: -1,
	}
	state.FruitTreeStates["5,5"] = tree
	return state, tree
}

// tickTrees advances the world clock AND the tree pass together (falls depend on both
// the apparent time of day and raw-tick spacing).
func tickTrees(m *Match, state *WorldState, n int) {
	for i := 0; i < n; i++ {
		state.TickCount++
		m.processFruitTrees(state, nil, nopRuntimeLogger())
	}
}

// Manual watering: once per apparent day, tank capped at 3; a BACKWARD day jump (debug
// set-time) must not wedge watering (the gate is ==, not >=); day 0 must accept the
// first watering (LastWaterDay starts -1, not 0).
func TestTreeWateringDailyCap(t *testing.T) {
	state, tree := treeTestState(4, 840, 4200)

	// Day 0 (fresh state, tick small): the -1 sentinel must allow watering.
	state.TickCount = 100
	if ok, _ := waterTree(state, tree, true); !ok {
		t.Fatal("fresh tree on day 0 refused its first watering (the zero-value trap)")
	}
	if tree.WaterLevel != 1 {
		t.Fatalf("level=%d, want 1", tree.WaterLevel)
	}

	// Same day: blocked.
	if ok, msg := waterTree(state, tree, true); ok || msg == "" {
		t.Fatal("second manual watering the same day must be refused with a message")
	}

	// Next day: allowed.
	state.TickCount += DayLengthTicks
	if ok, _ := waterTree(state, tree, true); !ok {
		t.Fatal("next-day watering refused")
	}

	// BACKWARD day jump (set-time): the apparent day index drops below LastWaterDay —
	// equality-gate means watering still works on this (different) day.
	state.DayOffsetTicks = 0
	state.TickCount = 200 // back to day 0; LastWaterDay is now 1
	if ok, _ := waterTree(state, tree, true); !ok {
		t.Fatal("backward day jump wedged tree watering (>= gate instead of ==?)")
	}
	if tree.WaterLevel != treeTankCap {
		t.Fatalf("level=%d, want cap %d", tree.WaterLevel, treeTankCap)
	}

	// Tank full: refused even on a fresh day.
	state.TickCount += DayLengthTicks
	if ok, _ := waterTree(state, tree, true); ok {
		t.Fatal("full tank accepted a watering")
	}
}

// The batch triggers ONLY when the tree is empty: a fruited tree BANKS the full tank
// (no consumption, no partial batch); the moment the canopy empties, one clean trigger
// buys a FULL batch.
func TestBatchOnlyWhenEmpty(t *testing.T) {
	state, tree := treeTestState(4, 2, 4200)
	m := &Match{}

	// Fruited tree with a full tank: nothing may fire.
	tree.FruitCount = 2
	tree.WaterLevel = treeTankCap
	tickTrees(m, state, 10)
	if tree.WaterLevel != treeTankCap || tree.PendingGrowth != 0 {
		t.Fatalf("fruited tree consumed its tank: level=%d pending=%d", tree.WaterLevel, tree.PendingGrowth)
	}

	// Canopy empties (picked/knocked): ONE trigger, full batch.
	tree.FruitCount = 0
	tickTrees(m, state, 1)
	if tree.WaterLevel != 0 || tree.PendingGrowth != tree.MaxFruit {
		t.Fatalf("empty tree should trigger a full batch: level=%d pending=%d", tree.WaterLevel, tree.PendingGrowth)
	}
}

// Pending is a countdown, never recomputed: harvesting mid-growth doesn't change how
// many fruits the batch still grows — the player loses nothing.
func TestPendingCountdownSurvivesHarvest(t *testing.T) {
	state, tree := treeTestState(4, 2, 99999)
	m := &Match{}

	tree.WaterLevel = treeTankCap
	tickTrees(m, state, 1) // trigger: pending 4
	tickTrees(m, state, 4) // grow 2
	if tree.FruitCount != 2 || tree.PendingGrowth != 2 {
		t.Fatalf("setup: fruit=%d pending=%d, want 2/2", tree.FruitCount, tree.PendingGrowth)
	}

	tree.FruitCount-- // player picks one mid-batch

	tickTrees(m, state, 4) // the remaining 2 still grow
	if tree.FruitCount != 3 || tree.PendingGrowth != 0 {
		t.Fatalf("after harvest mid-batch: fruit=%d pending=%d, want 3/0 (batch total unchanged)", tree.FruitCount, tree.PendingGrowth)
	}
}

// DropTimer resets ONLY on the FruitCount 0->1 growth transition: later grows must not
// restart the ripeness clock (old bug: old fruit never ripened while anything grew).
func TestDropTimerResetsOnlyOnFirstFruit(t *testing.T) {
	state, tree := treeTestState(4, 2, 99999)
	m := &Match{}

	tree.WaterLevel = treeTankCap
	tickTrees(m, state, 1) // trigger
	tickTrees(m, state, 2) // first fruit: 0->1 resets DropTimer
	if tree.FruitCount != 1 {
		t.Fatalf("setup: fruit=%d, want 1", tree.FruitCount)
	}
	timerAfterFirst := tree.DropTimer

	tickTrees(m, state, 2) // second fruit: must NOT reset
	if tree.FruitCount != 2 {
		t.Fatalf("second fruit didn't grow: fruit=%d", tree.FruitCount)
	}
	if tree.DropTimer <= timerAfterFirst {
		t.Fatalf("DropTimer reset on a later grow: %d (was %d after first)", tree.DropTimer, timerAfterFirst)
	}
}

// Ripe fruit falls only inside the evening window, one at a time, >= spacing apart —
// and a fresh batch gets its FULL shelf life (no inherited ripeness).
func TestEveningStaggeredFalls(t *testing.T) {
	state, tree := treeTestState(4, 2, 50)
	m := &Match{}

	// Park the clock at EVENING (t ≈ 0.41) with everything ripe.
	state.TickCount = DayLengthTicks + int64(float64(DayLengthTicks)*0.41)
	tree.FruitCount = 3
	tree.DropTimer = 100 // > FruitDropTicks(50): ripe

	var fallTicks []int64
	last := 3
	for i := 0; i < int(treeFallSpacingTicks)*3+10; i++ {
		tickTrees(m, state, 1)
		if tree.FruitCount < last {
			fallTicks = append(fallTicks, state.TickCount)
			last = tree.FruitCount
		}
	}
	if len(fallTicks) != 3 {
		t.Fatalf("expected 3 staggered falls, got %d", len(fallTicks))
	}
	for i := 1; i < len(fallTicks); i++ {
		if gap := fallTicks[i] - fallTicks[i-1]; gap < treeFallSpacingTicks {
			t.Fatalf("falls %d ticks apart, want >= %d", gap, treeFallSpacingTicks)
		}
	}
	if len(state.GroundItems) != 3 {
		t.Fatalf("fallen fruit should be ground items: %d", len(state.GroundItems))
	}

	// Fresh batch after the shed: full shelf life — the first new fruit resets the
	// ripeness clock, so nothing falls before FruitDropTicks elapse.
	tree.WaterLevel = treeTankCap
	tickTrees(m, state, 1) // trigger
	tickTrees(m, state, 2) // first fruit of the new batch (DropTimer -> 0 at growth)
	if tree.FruitCount != 1 {
		t.Fatalf("new batch first fruit missing: %d", tree.FruitCount)
	}
	items := len(state.GroundItems)
	tickTrees(m, state, 30) // still inside evening, but DropTimer < 50
	if len(state.GroundItems) != items {
		t.Fatal("fresh batch shed with zero shelf life (DropTimer inherited)")
	}
}

// Outside the evening window ripe fruit NEVER falls, no matter how overripe.
func TestNoFallsOutsideEvening(t *testing.T) {
	state, tree := treeTestState(4, 2, 50)
	m := &Match{}

	state.TickCount = DayLengthTicks + 100 // morning (t ≈ 0.01)
	tree.FruitCount = 3
	tree.DropTimer = 10000

	tickTrees(m, state, 2000) // runs to t ≈ 0.25 — still before the window
	if tree.FruitCount != 3 || len(state.GroundItems) != 0 {
		t.Fatalf("fruit fell outside the evening window: fruit=%d items=%d", tree.FruitCount, len(state.GroundItems))
	}
}

// Wild trees init pre-fruited (2-3) but all UNRIPE, with an empty tank and the -1
// watering sentinel — forage exists, but re-fruiting needs rain or a player.
func TestWildInitUnripe(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.Entities["tree_apple"] = &EntityDef{World: &WorldData{
		FruitType: "apple", MaxFruit: 4, FruitGrowTicks: 840, FruitDropTicks: 4200,
	}}
	chunk := NewEmptyChunk(0, 0, "grass")
	for i := 0; i < 8; i++ {
		chunk.SetOccupant(i*3, 5, &PlacedOccupant{ID: "tree_apple", Anchor: true})
	}
	state.Chunks[ChunkKey(0, 0)] = chunk

	m.initFruitTreesInChunk(state, chunk, 0, 0, nopRuntimeLogger())

	if len(state.FruitTreeStates) != 8 {
		t.Fatalf("expected 8 trees, got %d", len(state.FruitTreeStates))
	}
	for key, tree := range state.FruitTreeStates {
		if tree.FruitCount < 2 || tree.FruitCount > 3 {
			t.Errorf("%s: wild FruitCount=%d, want 2-3", key, tree.FruitCount)
		}
		if tree.DropTimer >= 4200 {
			t.Errorf("%s: wild tree inits RIPE (DropTimer=%d)", key, tree.DropTimer)
		}
		if tree.WaterLevel != 0 || tree.PendingGrowth != 0 {
			t.Errorf("%s: wild tank not empty (level=%d pending=%d)", key, tree.WaterLevel, tree.PendingGrowth)
		}
		if tree.LastWaterDay != -1 {
			t.Errorf("%s: LastWaterDay=%d, want -1 (zero-value would block day-0 watering)", key, tree.LastWaterDay)
		}
	}
}

// Hands-pick (OpCode 92): one fruit per harvest into the inventory; rejects keep both
// the tree and the inventory intact (range, empty tree, full inventory).
func TestTreeHarvest(t *testing.T) {
	state, tree := treeTestState(4, 2, 4200)
	m := &Match{}
	tree.FruitCount = 2

	player := &PlayerState{
		UserID:   "p1",
		Position: entities.EntityPosition{LocalX: 6.0, LocalY: 5.5}, // ~1.1 from tree center (5.5,5.5)
	}
	state.Players = map[string]*PlayerState{"p1": player}

	// Pick one: fruit moves tree -> inventory.
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	if tree.FruitCount != 1 {
		t.Fatalf("tree fruit=%d, want 1", tree.FruitCount)
	}
	if player.ItemSlots[0].ItemID != "apple" || player.ItemSlots[0].Count != 1 {
		t.Fatalf("inventory got %q x%d, want apple x1", player.ItemSlots[0].ItemID, player.ItemSlots[0].Count)
	}

	// Out of range: no change.
	player.Position.LocalX = 20
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	if tree.FruitCount != 1 || player.ItemSlots[0].Count != 1 {
		t.Fatal("out-of-range harvest mutated state")
	}
	player.Position.LocalX = 6.0

	// Empty the tree: harvest refuses.
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	if tree.FruitCount != 0 {
		t.Fatalf("tree fruit=%d, want 0", tree.FruitCount)
	}
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	if player.ItemSlots[0].Count != 2 {
		t.Fatalf("empty-tree harvest changed inventory: count=%d, want 2", player.ItemSlots[0].Count)
	}

	// Full inventory: fruit STAYS on the tree.
	tree.FruitCount = 1
	for i := range player.ItemSlots {
		if player.ItemSlots[i].ItemID == "" {
			player.ItemSlots[i] = InventorySlot{ItemID: "stone_block", Count: 1}
		}
	}
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	// apple already stacks in slot 0 — make the stack check honest by using a fruit the
	// player does NOT hold: an orange tree.
	if tree.FruitCount != 0 || player.ItemSlots[0].Count != 3 {
		// apple stacked onto the existing apple slot — allowed; full means "no slot AND
		// no stack". Verify the genuinely-full case below.
		t.Fatalf("stacking pick failed: fruit=%d apples=%d", tree.FruitCount, player.ItemSlots[0].Count)
	}

	state.Entities["tree_test"].World.FruitType = "orange"
	tree.FruitCount = 1
	m.handleTreeHarvest(nopRuntimeLogger(), nil, state, "p1", TreeHarvestMessage{GX: 5, GY: 5})
	if tree.FruitCount != 1 {
		t.Fatalf("full-inventory pick removed fruit from the tree: %d", tree.FruitCount)
	}
}

// Tool hits knock one fruit to the GROUND per hit (never into the inventory), ignoring
// the evening window; an empty tree just takes break damage.
func TestKnockdownOnToolHit(t *testing.T) {
	state, tree := treeTestState(4, 2, 4200)
	m := &Match{}
	tree.FruitCount = 2

	// Make the tree breakable by hand so handleTileBreak engages.
	state.Entities["tree_test"].World.Breakable = &BreakableData{HP: 10}
	state.BreakingState = map[string]*BreakingProgress{}
	player := &PlayerState{
		UserID:   "p1",
		Position: entities.EntityPosition{LocalX: 6.0, LocalY: 5.5},
	}
	state.Players = map[string]*PlayerState{"p1": player}

	// Morning (outside the evening fall window): hits still knock fruit down.
	m.handleTileBreak(nopRuntimeLogger(), nil, state, "p1", TileBreakMessage{GridX: 5, GridY: 5}, state.TickCount)
	if tree.FruitCount != 1 {
		t.Fatalf("first hit should knock one fruit: %d", tree.FruitCount)
	}
	if len(state.GroundItems) != 1 {
		t.Fatalf("knocked fruit should hit the ground: %d items", len(state.GroundItems))
	}
	m.handleTileBreak(nopRuntimeLogger(), nil, state, "p1", TileBreakMessage{GridX: 5, GridY: 5}, state.TickCount)
	if tree.FruitCount != 0 || len(state.GroundItems) != 2 {
		t.Fatalf("second hit: fruit=%d items=%d", tree.FruitCount, len(state.GroundItems))
	}

	// Empty tree: more hits, no underflow, no items.
	m.handleTileBreak(nopRuntimeLogger(), nil, state, "p1", TileBreakMessage{GridX: 5, GridY: 5}, state.TickCount)
	if tree.FruitCount != 0 || len(state.GroundItems) != 2 {
		t.Fatalf("empty-tree hit mutated fruit: fruit=%d items=%d", tree.FruitCount, len(state.GroundItems))
	}
}

// Rain filling the tank DURING a growing batch banks it — exactly one new batch fires,
// and only after the canopy fully empties.
func TestRainBanksDuringGrowthSingleTrigger(t *testing.T) {
	state, tree := treeTestState(2, 2, 99999)
	m := &Match{}

	tree.WaterLevel = treeTankCap
	tickTrees(m, state, 1) // trigger batch #1
	tickTrees(m, state, 2) // first fruit growing

	// Rain tops the tank back up mid-batch (waterTree clamps at cap, no daily stamp).
	for i := 0; i < 5; i++ {
		waterTree(state, tree, false)
	}
	if tree.WaterLevel != treeTankCap {
		t.Fatalf("rain should bank a full tank: level=%d", tree.WaterLevel)
	}

	// Finish the batch: pending hits 0 but the canopy holds fruit — NO trigger.
	tickTrees(m, state, 4)
	if tree.FruitCount != 2 || tree.PendingGrowth != 0 {
		t.Fatalf("batch #1 should complete: fruit=%d pending=%d", tree.FruitCount, tree.PendingGrowth)
	}
	tickTrees(m, state, 10)
	if tree.WaterLevel != treeTankCap {
		t.Fatalf("banked tank consumed while canopy full: level=%d", tree.WaterLevel)
	}

	// Empty the canopy: exactly one trigger.
	tree.FruitCount = 0
	tickTrees(m, state, 1)
	if tree.WaterLevel != 0 || tree.PendingGrowth != tree.MaxFruit {
		t.Fatalf("banked tank should buy exactly one batch: level=%d pending=%d", tree.WaterLevel, tree.PendingGrowth)
	}
}
