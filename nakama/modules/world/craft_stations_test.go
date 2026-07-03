package world

// Per-station craft-slots: N parallel CraftProcessor lanes per station (world.craft_slots,
// default 1) sharing ONE output grid. These pin the load-bearing behaviors: the legacy-save
// migration (flat Recipe/Queue/Progress → Procs[0]), parallel processing, stall isolation
// (a full output stalls one lane, not its siblings), proc targeting + the legacy default
// proc 0, and craft_slots seeding/top-up.
// Run:  go test ./world/ -run TestCraft -v

import (
	"encoding/json"
	"testing"

	"bugfarmer/entities"
)

// craftTestState: a 2-slot furnace anchored at (10,10) with a fast + a slow recipe, a 1-slot
// workbench at (20,20), and a player holding inputs for both furnace recipes.
func craftTestState() (*WorldState, *PlayerState, *Match) {
	state := newTestState(20)
	state.Players = map[string]*PlayerState{}
	state.CraftStations = map[string]*CraftStationState{} // newTestState doesn't init this map
	state.Entities["furnace"] = &EntityDef{World: &WorldData{CraftSlots: 2}}
	state.Entities["workbench"] = &EntityDef{World: &WorldData{}}

	fast := &entities.RecipeDef{ID: "bar_fast", Station: "furnace",
		Inputs: []entities.RecipeIO{{Item: "ore_a", Count: 1}},
		Output: entities.RecipeIO{Item: "bar_a", Count: 1}, ProcessTicks: 3}
	slow := &entities.RecipeDef{ID: "bar_slow", Station: "furnace",
		Inputs: []entities.RecipeIO{{Item: "ore_b", Count: 1}},
		Output: entities.RecipeIO{Item: "bar_b", Count: 1}, ProcessTicks: 5}
	bench := &entities.RecipeDef{ID: "plank", Station: "workbench",
		Inputs: []entities.RecipeIO{{Item: "wood", Count: 1}},
		Output: entities.RecipeIO{Item: "plank", Count: 1}, ProcessTicks: 1}
	state.Recipes = map[string]*entities.RecipeDef{"bar_fast": fast, "bar_slow": slow, "plank": bench}
	state.RecipesByStation = map[string][]*entities.RecipeDef{
		"furnace": {fast, slow}, "workbench": {bench},
	}

	state.Chunks[ChunkKey(0, 0)] = NewEmptyChunk(0, 0, "grass")
	state.Chunks[ChunkKey(0, 0)].SetOccupant(10, 10, &PlacedOccupant{ID: "furnace", Anchor: true})
	state.Chunks[ChunkKey(0, 0)].SetOccupant(20, 20, &PlacedOccupant{ID: "workbench", Anchor: true})

	p := testPlayer(10, 10, "")
	p.ItemSlots[0] = InventorySlot{ItemID: "ore_a", Count: 5}
	p.ItemSlots[1] = InventorySlot{ItemID: "ore_b", Count: 5}
	state.Players["p1"] = p
	return state, p, &Match{}
}

// 1. Legacy-save migration: a pre-craft-slots CraftStationState (flat Recipe/Queue/Progress,
// Go-default field names — the struct never had json tags) folds into Procs[0]; the re-marshal
// emits the Procs shape and round-trips.
func TestCraftLegacySaveMigratesToProcs(t *testing.T) {
	legacy := []byte(`{"Key":"craft_5_5","EntityID":"furnace","GridX":5,"GridY":5,
		"Output":[{"item_id":"bar_a","count":3}],"Recipe":"bar_fast","Queue":2,"Progress":5}`)
	var s CraftStationState
	if err := json.Unmarshal(legacy, &s); err != nil {
		t.Fatalf("legacy unmarshal: %v", err)
	}
	if len(s.Procs) != 1 || s.Procs[0].Recipe != "bar_fast" || s.Procs[0].Queue != 2 || s.Procs[0].Progress != 5 {
		t.Fatalf("legacy fields did not fold into Procs[0]: %+v", s.Procs)
	}
	if len(s.Output) != 1 || s.Output[0].ItemID != "bar_a" {
		t.Fatalf("output grid lost in migration: %+v", s.Output)
	}

	// Round-trip: the new shape survives its own marshal/unmarshal unchanged.
	out, err := json.Marshal(&s)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var s2 CraftStationState
	if err := json.Unmarshal(out, &s2); err != nil {
		t.Fatalf("re-unmarshal: %v", err)
	}
	if len(s2.Procs) != 1 || s2.Procs[0] != s.Procs[0] {
		t.Fatalf("Procs did not round-trip: %+v vs %+v", s2.Procs, s.Procs)
	}
}

// 2. Two lanes process DIFFERENT recipes in parallel; each pays out on its own ProcessTicks.
func TestCraftTwoProcsRunInParallel(t *testing.T) {
	state, p, m := craftTestState()
	s := m.resolveCraftStation(state, 10, 10)
	if s == nil || len(s.Procs) != 2 {
		t.Fatalf("expected a 2-proc furnace, got %+v", s)
	}
	if !m.craftQueue(nopDispatcher{}, state, "p1", p, s, 0, "bar_fast", 1) {
		t.Fatal("queue fast on proc 0")
	}
	if !m.craftQueue(nopDispatcher{}, state, "p1", p, s, 1, "bar_slow", 1) {
		t.Fatal("queue slow on proc 1")
	}

	for i := 0; i < 3; i++ {
		m.processCraftStations(state, nopDispatcher{})
	}
	if got := outputCount(s, "bar_a"); got != 1 {
		t.Fatalf("fast lane should have produced after 3 ticks: bar_a=%d", got)
	}
	if got := outputCount(s, "bar_b"); got != 0 {
		t.Fatalf("slow lane must still be processing at tick 3: bar_b=%d", got)
	}
	for i := 0; i < 2; i++ {
		m.processCraftStations(state, nopDispatcher{})
	}
	if got := outputCount(s, "bar_b"); got != 1 {
		t.Fatalf("slow lane should have produced after 5 ticks: bar_b=%d", got)
	}
}

// 3. A full output grid stalls ONLY the lane that can't pay out; a collect unblocks it.
func TestCraftFullOutputStallsOneLaneNotSiblings(t *testing.T) {
	state, p, m := craftTestState()
	s := m.resolveCraftStation(state, 10, 10)
	// Fill the grid: 7 junk stacks + an existing bar_b stack. bar_a (fast lane) has NO room;
	// bar_b (slow lane) merges into its stack.
	for i := 0; i < 7; i++ {
		s.Output[i] = InventorySlot{ItemID: "junk", Count: 1}
	}
	s.Output[7] = InventorySlot{ItemID: "bar_b", Count: 1}

	if !m.craftQueue(nopDispatcher{}, state, "p1", p, s, 0, "bar_fast", 1) ||
		!m.craftQueue(nopDispatcher{}, state, "p1", p, s, 1, "bar_slow", 1) {
		t.Fatal("queueing failed")
	}
	for i := 0; i < 6; i++ {
		m.processCraftStations(state, nopDispatcher{})
	}
	if got := outputCount(s, "bar_b"); got != 2 {
		t.Fatalf("unblocked lane must keep producing: bar_b=%d (want 2)", got)
	}
	if s.Procs[0].Queue != 1 || outputCount(s, "bar_a") != 0 {
		t.Fatalf("full-output lane must STALL, not lose the batch: queue=%d bar_a=%d",
			s.Procs[0].Queue, outputCount(s, "bar_a"))
	}

	// Collect a junk stack → an empty cell opens → the stalled lane pays out next tick.
	if !craftCollectOne(p, s, 0) {
		t.Fatal("collect failed")
	}
	m.processCraftStations(state, nopDispatcher{})
	if outputCount(s, "bar_a") != 1 || s.Procs[0].Queue != 0 {
		t.Fatalf("stalled lane should pay out after room opens: bar_a=%d queue=%d",
			outputCount(s, "bar_a"), s.Procs[0].Queue)
	}
}

// 4. Proc targeting through the full handler: out-of-range refused; a legacy message (no proc
// field → 0) works; a busy lane refuses a DIFFERENT recipe but accepts more of the same.
func TestCraftHandlerProcTargeting(t *testing.T) {
	state, p, m := craftTestState()
	base := ContainerActionMessage{GX: 10, GY: 10, Op: "craft", Qty: 1}

	bad := base
	bad.Recipe, bad.Proc = "bar_fast", 5
	m.handleCraftStationAction(nil, nopDispatcher{}, state, "p1", p, bad)
	s := state.CraftStations[CraftStationKey(10, 10)]
	if s != nil && (s.Procs[0].Queue != 0 || s.Procs[1].Queue != 0) {
		t.Fatal("out-of-range proc must be refused")
	}

	legacy := base // Proc zero-value = 0, the legacy-client shape
	legacy.Recipe = "bar_fast"
	m.handleCraftStationAction(nil, nopDispatcher{}, state, "p1", p, legacy)
	s = state.CraftStations[CraftStationKey(10, 10)]
	if s == nil || s.Procs[0].Queue != 1 || s.Procs[0].Recipe != "bar_fast" {
		t.Fatalf("legacy no-proc message must target lane 0: %+v", s.Procs)
	}

	diff := base
	diff.Recipe = "bar_slow" // different recipe on the busy lane 0
	m.handleCraftStationAction(nil, nopDispatcher{}, state, "p1", p, diff)
	if s.Procs[0].Queue != 1 || s.Procs[0].Recipe != "bar_fast" {
		t.Fatalf("busy lane must refuse a different recipe: %+v", s.Procs[0])
	}

	same := base
	same.Recipe = "bar_fast"
	m.handleCraftStationAction(nil, nopDispatcher{}, state, "p1", p, same)
	if s.Procs[0].Queue != 2 {
		t.Fatalf("same recipe must add to the busy lane's queue: %+v", s.Procs[0])
	}
}

// 5. craft_slots seeding: the furnace def (2) seeds 2 lanes; the workbench (unset) defaults to 1;
// a restored 1-lane legacy state tops up to the def without touching lane 0's contents.
func TestCraftSlotsSeedingAndTopUp(t *testing.T) {
	state, _, m := craftTestState()
	if s := m.resolveCraftStation(state, 10, 10); len(s.Procs) != 2 {
		t.Fatalf("furnace craft_slots=2 must seed 2 lanes, got %d", len(s.Procs))
	}
	if s := m.resolveCraftStation(state, 20, 20); len(s.Procs) != 1 {
		t.Fatalf("workbench without craft_slots must default to 1 lane, got %d", len(s.Procs))
	}

	// A restored legacy furnace (1 migrated lane, mid-batch) tops up to 2 on resolve.
	key := CraftStationKey(12, 12)
	state.Chunks[ChunkKey(0, 0)].SetOccupant(12, 12, &PlacedOccupant{ID: "furnace", Anchor: true})
	state.CraftStations[key] = &CraftStationState{
		Key: key, EntityID: "furnace", GridX: 12, GridY: 12,
		Output: make([]InventorySlot, craftOutputSlots),
		Procs:  []CraftProcessor{{Recipe: "bar_fast", Queue: 2, Progress: 5}},
	}
	s := m.resolveCraftStation(state, 12, 12)
	if len(s.Procs) != 2 {
		t.Fatalf("restored station must top up to craft_slots lanes, got %d", len(s.Procs))
	}
	if s.Procs[0].Recipe != "bar_fast" || s.Procs[0].Queue != 2 || s.Procs[0].Progress != 5 {
		t.Fatalf("top-up must not touch lane 0's in-flight batch: %+v", s.Procs[0])
	}
}

// outputCount sums every output-grid stack of item.
func outputCount(s *CraftStationState, item string) int {
	n := 0
	for i := range s.Output {
		if s.Output[i].ItemID == item {
			n += s.Output[i].Count
		}
	}
	return n
}
