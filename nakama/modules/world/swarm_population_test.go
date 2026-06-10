package world

// Unit tests for the deterministic swarm population pass: size-SPLIT (Count > MaxSwarmSize
// sheds the highest alive bug-ids into a child) and proximity-MERGE (overlapping centers,
// combined <= MaxSwarmSize). Both must travel ONLY as SWARM_SPLIT/SWARM_MERGE influence
// events (no SwarmsDirty) with exact bookkeeping, so clients can apply them by MOVING bugs.
//
// Run inside the builder image:  go test ./modules/world/ -run TestSwarm -v

import (
	"testing"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// nopLogger satisfies runtime.Logger for tests.
type nopLogger struct{}

func (nopLogger) Debug(string, ...interface{})                          {}
func (nopLogger) Info(string, ...interface{})                           {}
func (nopLogger) Warn(string, ...interface{})                           {}
func (nopLogger) Error(string, ...interface{})                          {}
func (l nopLogger) WithField(string, interface{}) runtime.Logger        { return l }
func (l nopLogger) WithFields(map[string]interface{}) runtime.Logger    { return l }
func (nopLogger) Fields() map[string]interface{}                        { return nil }

func nopRuntimeLogger() runtime.Logger { return nopLogger{} }

func newTestState(maxSwarm int) *WorldState {
	return &WorldState{
		Config:          WorldConfig{ChunkSize: 32, TickRate: 10},
		TickCount:       1000,
		Swarms:          map[string]*entities.SwarmState{},
		SwarmsBySpecies: map[string][]string{},
		Species: map[string]*entities.BugSpecies{
			"fly_common": {
				MinSwarmSize: 5,
				MaxSwarmSize: maxSwarm,
				MergeRadius:  2.5,
			},
		},
		ZoneStates:  map[string]*ZoneState{},
		CurrentZone: &ZoneConfig{ZoneID: "testzone"},
		// Ecology maps (consumption/reproduction/station tests)
		GroundItems: map[string]*entities.GroundItem{},
		Stations:    map[string]*entities.StationState{},
		Entities:    map[string]*EntityDef{},
		// Farming maps (tree water-gating tests)
		FruitTreeStates: map[string]*entities.FruitTreeState{},
		Chunks:          map[string]*ChunkData{},
	}
}

func newTestSwarm(id string, count int, x, y float32) *entities.SwarmState {
	s := &entities.SwarmState{
		ID:        id,
		SpeciesID: "fly_common",
		Position:  entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: x, LocalY: y},
		Radius:    4.0,
		Count:     count,
	}
	s.InitializeBugIDs() // ids 0..count-1 alive
	return s
}

func eventsOfType(state *WorldState, t string) []InfluenceEvent {
	var out []InfluenceEvent
	for _, e := range state.PendingInfluence {
		if e.Type == t {
			out = append(out, e)
		}
	}
	return out
}

func TestSwarmSizeSplit(t *testing.T) {
	state := newTestState(20)
	parent := newTestSwarm("parent", 21, 10, 10) // over the limit of 20
	state.Swarms["parent"] = parent
	state.SwarmsBySpecies["fly_common"] = []string{"parent"}

	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())

	// Parent keeps 11, child gets 10 (21/2 = 10 shed)
	if parent.Count != 11 {
		t.Fatalf("parent.Count = %d, want 11", parent.Count)
	}
	if len(state.Swarms) != 2 {
		t.Fatalf("len(Swarms) = %d, want 2", len(state.Swarms))
	}
	// Shed ids must be the HIGHEST: 11..20 dead on the parent, 0..10 alive
	for id := 0; id <= 10; id++ {
		if !parent.IsBugAlive(id) {
			t.Fatalf("parent bug %d should be alive", id)
		}
	}
	for id := 11; id <= 20; id++ {
		if parent.IsBugAlive(id) {
			t.Fatalf("parent bug %d should be shed", id)
		}
	}
	// The child: count 10, ids 0..9 alive, registered in SwarmsBySpecies
	var child *entities.SwarmState
	for id, s := range state.Swarms {
		if id != "parent" {
			child = s
		}
	}
	if child == nil || child.Count != 10 {
		t.Fatalf("child missing or wrong count: %+v", child)
	}
	if !child.IsBugAlive(0) || !child.IsBugAlive(9) || child.IsBugAlive(10) {
		t.Fatalf("child id space wrong: NextBugID=%d", child.NextBugID)
	}
	if len(state.SwarmsBySpecies["fly_common"]) != 2 {
		t.Fatalf("SwarmsBySpecies not updated: %v", state.SwarmsBySpecies["fly_common"])
	}
	// Exactly one SWARM_SPLIT event with exact bookkeeping; NO SwarmsDirty
	evs := eventsOfType(state, InfluenceSwarmSplit)
	if len(evs) != 1 {
		t.Fatalf("SWARM_SPLIT events = %d, want 1", len(evs))
	}
	e := evs[0]
	if e.SwarmID != "parent" || e.NewSwarmID != child.ID || e.SplitCount != 10 || e.ParentCount != 11 {
		t.Fatalf("split event fields wrong: %+v", e)
	}
	if state.SwarmsDirty {
		t.Fatal("SwarmsDirty must NOT be set by a split (lifecycle travels via the event)")
	}
	// Total bugs conserved
	if parent.Count+child.Count != 21 {
		t.Fatalf("bugs not conserved: %d + %d != 21", parent.Count, child.Count)
	}
}

func TestSwarmNoSplitAtLimit(t *testing.T) {
	state := newTestState(20)
	state.Swarms["a"] = newTestSwarm("a", 20, 10, 10) // exactly at the limit
	state.SwarmsBySpecies["fly_common"] = []string{"a"}

	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())

	if len(state.Swarms) != 1 || len(state.PendingInfluence) != 0 {
		t.Fatalf("at-limit swarm must not split: swarms=%d events=%d", len(state.Swarms), len(state.PendingInfluence))
	}
}

func TestSwarmProximityMerge(t *testing.T) {
	state := newTestState(20)
	a := newTestSwarm("a", 8, 10, 10)
	b := newTestSwarm("b", 9, 11, 10) // 1.0 apart < merge_radius 2.5; combined 17 <= 20
	state.Swarms["a"], state.Swarms["b"] = a, b
	state.SwarmsBySpecies["fly_common"] = []string{"a", "b"}

	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())

	if len(state.Swarms) != 1 {
		t.Fatalf("len(Swarms) = %d, want 1 after merge", len(state.Swarms))
	}
	evs := eventsOfType(state, InfluenceSwarmMerge)
	if len(evs) != 1 {
		t.Fatalf("SWARM_MERGE events = %d, want 1", len(evs))
	}
	e := evs[0]
	survivor, ok := state.Swarms[e.SwarmID]
	if !ok {
		t.Fatalf("event survivor %s not in Swarms", e.SwarmID)
	}
	if survivor.Count != 17 {
		t.Fatalf("survivor.Count = %d, want 17 (conserved)", survivor.Count)
	}
	// The moved bugs become real, catchable survivor ids: base..base+count-1 < NextBugID
	if e.NewBugIDBase+e.SplitCount != survivor.NextBugID {
		t.Fatalf("id bookkeeping wrong: base %d + count %d != NextBugID %d", e.NewBugIDBase, e.SplitCount, survivor.NextBugID)
	}
	if !survivor.IsBugAlive(e.NewBugIDBase) || !survivor.IsBugAlive(e.NewBugIDBase+e.SplitCount-1) {
		t.Fatal("moved bugs must be alive (catchable) on the survivor")
	}
	if len(state.SwarmsBySpecies["fly_common"]) != 1 {
		t.Fatalf("SwarmsBySpecies not updated: %v", state.SwarmsBySpecies["fly_common"])
	}
	if state.SwarmsDirty {
		t.Fatal("SwarmsDirty must NOT be set by a merge")
	}
}

func TestSwarmNoMergeOverCap(t *testing.T) {
	state := newTestState(20)
	state.Swarms["a"] = newTestSwarm("a", 15, 10, 10)
	state.Swarms["b"] = newTestSwarm("b", 10, 11, 10) // combined 25 > 20
	state.SwarmsBySpecies["fly_common"] = []string{"a", "b"}

	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())

	if len(state.Swarms) != 2 || len(state.PendingInfluence) != 0 {
		t.Fatalf("over-cap swarms must not merge: swarms=%d events=%d", len(state.Swarms), len(state.PendingInfluence))
	}
}

// === Fly lifecycle: consumption + reproduction bookkeeping ===

func TestConsumeFoodThresholdsAndDepletion(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	item := &entities.GroundItem{
		ID:        "food1",
		ItemType:  "rotten_apple",
		Count:     1,
		Position:  entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 10, LocalY: 10},
		FoodValue: 100,
	}
	state.GroundItems["food1"] = item

	// Drain 30 -> level 70 (crosses 75): one FOOD_CONSUMED event
	m.consumeFood(state, nil, "food1", 30)
	if item.FoodValue != 70 {
		t.Fatalf("FoodValue = %d, want 70", item.FoodValue)
	}
	evs := eventsOfType(state, InfluenceFoodConsumed)
	if len(evs) != 1 || evs[0].Level != 70 || evs[0].FoodID != "food1" {
		t.Fatalf("threshold event wrong: %+v", evs)
	}

	// Drain the rest -> 0: item removed from the world + a depleted event
	m.consumeFood(state, nil, "food1", 80)
	if _, exists := state.GroundItems["food1"]; exists {
		t.Fatal("depleted item must be removed")
	}
	evs = eventsOfType(state, InfluenceFoodConsumed)
	if len(evs) < 2 || evs[len(evs)-1].Level != 0 {
		t.Fatalf("depletion event wrong: %+v", evs)
	}
}

func TestReproduceSwarmDoubles(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	swarm := newTestSwarm("s", 6, 10, 10)
	swarm.TargetFoodID = "food1"
	state.Swarms["s"] = swarm
	state.GroundItems["food1"] = &entities.GroundItem{
		ID: "food1", ItemType: "rotten_apple", Count: 1,
		Position:  entities.EntityPosition{LocalX: 10, LocalY: 10},
		FoodValue: 100,
	}
	species := state.Species["fly_common"]
	species.ReproduceCooldown = 30

	m.reproduceSwarm(state, nil, swarm, species, nopRuntimeLogger())

	// Doubled: 6 -> 12, new ids 6..11 alive + catchable
	if swarm.Count != 12 || swarm.NextBugID != 12 {
		t.Fatalf("count=%d nextBugID=%d, want 12/12", swarm.Count, swarm.NextBugID)
	}
	if !swarm.IsBugAlive(6) || !swarm.IsBugAlive(11) {
		t.Fatal("reproduced bugs must be alive (catchable)")
	}
	// Meters reset + cooldown armed
	if swarm.Satiation != 0 || swarm.ReproductionMeter != 0 || swarm.ReproduceCooldown != 30 {
		t.Fatalf("meters/cooldown wrong: sat=%f meter=%f cd=%f", swarm.Satiation, swarm.ReproductionMeter, swarm.ReproduceCooldown)
	}
	// One SWARM_REPRODUCED event with exact id bookkeeping
	evs := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evs) != 1 || evs[0].SwarmID != "s" || evs[0].SplitCount != 6 || evs[0].NewBugIDBase != 6 {
		t.Fatalf("reproduce event wrong: %+v", evs)
	}
	// Breeding consumed food (reproduceFoodCost = 50)
	if state.GroundItems["food1"].FoodValue != 50 {
		t.Fatalf("food after breed = %d, want 50", state.GroundItems["food1"].FoodValue)
	}
}

// === Water-gated fruit trees ===

func TestTreeWaterGating(t *testing.T) {
	state := newTestState(20)
	m := &Match{}

	// A fast tree at (5,5): grow every 2 ticks, drop every 3 — with ONE water charge.
	// MaxFruit=1 because growing RESETS the drop timer (fruit accumulates to max before
	// any drop — intended behavior); max 1 lets the drop fire promptly in the test.
	state.Entities["tree_test"] = &EntityDef{World: &WorldData{
		FruitType: "apple", MaxFruit: 1, FruitGrowTicks: 2, FruitDropTicks: 3,
	}}
	chunk := NewEmptyChunk(0, 0, "grass")
	chunk.SetOccupant(5, 5, &PlacedOccupant{ID: "tree_test", Anchor: true})
	state.Chunks[ChunkKey(0, 0)] = chunk
	tree := &entities.FruitTreeState{
		TreeID: "tree_5_5", EntityID: "tree_test", GridX: 5, GridY: 5,
		MaxFruit: 1, WaterCharges: 1,
	}
	state.FruitTreeStates["5,5"] = tree

	tick := func(n int) {
		for i := 0; i < n; i++ {
			m.processFruitTrees(state, nil, nopRuntimeLogger())
		}
	}

	// Watered: fruit grows (2 ticks) then drops (3 more) — consuming the only charge.
	tick(2)
	if tree.FruitCount != 1 {
		t.Fatalf("watered tree should grow: FruitCount=%d, want 1", tree.FruitCount)
	}
	tick(3)
	if tree.FruitCount != 0 || tree.WaterCharges != 0 {
		t.Fatalf("drop should fire + consume the charge: fruit=%d charges=%d", tree.FruitCount, tree.WaterCharges)
	}
	if len(state.GroundItems) != 1 {
		t.Fatalf("dropped fruit should be a ground item: %d", len(state.GroundItems))
	}

	// DRY: many more ticks — no new fruit ever grows.
	tick(50)
	if tree.FruitCount != 0 || len(state.GroundItems) != 1 {
		t.Fatalf("dry tree must not produce: fruit=%d items=%d", tree.FruitCount, len(state.GroundItems))
	}

	// Re-watered: production resumes.
	tree.WaterCharges = treeWaterPerCan
	tick(2)
	if tree.FruitCount != 1 {
		t.Fatalf("re-watered tree should grow again: FruitCount=%d", tree.FruitCount)
	}
}

func TestStationConsumption(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.Entities["compost_bin"] = &EntityDef{World: &WorldData{
		Station: &StationData{Accepts: []string{"apple"}, Capacity: 10, FoodPerUnit: 100},
	}}
	st := &entities.StationState{Key: "station_5_5", EntityID: "compost_bin", GridX: 5, GridY: 5, Fill: 2}
	state.Stations[st.Key] = st

	// Drain 150 -> from 200 to 50: fill drops to 1 with 50 drained into the current unit
	m.consumeFood(state, nil, st.Key, 150)
	if st.Fill != 1 {
		t.Fatalf("fill = %d, want 1", st.Fill)
	}
	evs := eventsOfType(state, InfluenceFoodConsumed)
	if len(evs) == 0 || evs[len(evs)-1].Level != 50 {
		t.Fatalf("station level event wrong: %+v", evs)
	}
	if !m.foodSourceAlive(state, st.Key) {
		t.Fatal("station with fill must be alive")
	}
}
