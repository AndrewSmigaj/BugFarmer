package world

// Unit tests for handleReleaseBugs (OpCode 29): releasing caught bugs at a clicked point
// either JOINS a nearby same-species swarm (SWARM_REPRODUCED ledger event, meters untouched)
// or creates a NEW swarm (SwarmsDirty broadcast path). Snap radius is
// max(species.MergeRadius, swarm.Radius) — the design-review catch: fly merge_radius (2.5)
// is smaller than the VISIBLE swarm_radius (4.0), so clicking fringe bugs must still join.
//
// Run inside the builder image:  go test ./modules/world/ -run TestRelease -v

import (
	"encoding/json"
	"testing"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// releaseTestState: combatTestState + species swarm fields + open chunks around the
// play area (IsBlocked treats MISSING chunks as blocked, which would wall-clamp every
// new swarm to the player's feet).
func releaseTestState() *WorldState {
	state := combatTestState()
	sp := state.Species["fly_common"]
	sp.MergeRadius = 2.5
	sp.SwarmRadius = 4.0
	sp.WanderRadius = 10.0
	for cx := 0; cx <= 1; cx++ {
		for cy := 0; cy <= 1; cy++ {
			state.Chunks[ChunkKey(cx, cy)] = openChunk(cx, cy)
		}
	}
	return state
}

func openChunk(cx, cy int) *ChunkData {
	g := make([][]string, ChunkSize)
	o := make([][]json.RawMessage, ChunkSize)
	for i := range g {
		g[i] = make([]string, ChunkSize)
		o[i] = make([]json.RawMessage, ChunkSize)
	}
	return &ChunkData{ChunkX: cx, ChunkY: cy, Ground: g, Occupants: o}
}

func releasePlayer(state *WorldState, x, y float32, species string, bugs int) *PlayerState {
	p := testPlayer(x, y, "")
	p.BugSlots[0] = InventorySlot{ItemID: species, Count: bugs}
	state.Players["p1"] = p
	return p
}

func releaseMsg(slot, count int, x, y float32) ReleaseBugsMessage {
	return ReleaseBugsMessage{SlotIndex: slot, Count: count, X: x, Y: y}
}

func TestReleaseCreatesNewSwarm(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 8)

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 5, 13, 10), "p1", 32)

	if p.BugSlots[0].Count != 3 {
		t.Fatalf("slot count = %d, want 3", p.BugSlots[0].Count)
	}
	if len(state.Swarms) != 1 {
		t.Fatalf("swarms = %d, want 1", len(state.Swarms))
	}
	var swarm *entities.SwarmState
	for _, s := range state.Swarms {
		swarm = s
	}
	if swarm.Count != 5 || swarm.NextBugID != 5 {
		t.Fatalf("Count/NextBugID = %d/%d, want 5/5", swarm.Count, swarm.NextBugID)
	}
	if swarm.Radius != 4.0 || swarm.WanderRad != 10.0 {
		t.Fatalf("Radius/WanderRad = %v/%v, want species values 4/10", swarm.Radius, swarm.WanderRad)
	}
	wx, wy := swarm.WorldX(32), swarm.WorldY(32)
	if wx < 12 || wx > 14 || wy < 9 || wy > 11 {
		t.Fatalf("swarm at (%.1f, %.1f), want ≈ the click (13, 10)", wx, wy)
	}
	if swarm.HomePos != swarm.Position {
		t.Fatal("HomePos should equal Position (spawn template parity)")
	}
	if !state.SwarmsDirty {
		t.Fatal("new swarm must set SwarmsDirty (the SwarmUpdate creation path)")
	}
	if got := len(eventsOfType(state, InfluenceSwarmReproduced)); got != 0 {
		t.Fatalf("new-swarm release emitted %d SWARM_REPRODUCED events, want 0", got)
	}
	if ids := state.SwarmsBySpecies["fly_common"]; len(ids) != 1 || ids[0] != swarm.ID {
		t.Fatal("SwarmsBySpecies bookkeeping missing")
	}
}

func TestReleaseJoinsNearbySwarm(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 6)
	swarm := newTestSwarm("s1", 10, 12, 10)
	swarm.Radius = 4.0
	swarm.Satiation = 33
	swarm.ReproductionMeter = 44
	state.Swarms["s1"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}

	// Click 2.0 from the swarm center (inside merge radius 2.5)
	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 6, 14, 10), "p1", 32)

	if swarm.Count != 16 || swarm.NextBugID != 16 {
		t.Fatalf("Count/NextBugID = %d/%d, want 16/16", swarm.Count, swarm.NextBugID)
	}
	if len(state.Swarms) != 1 || state.SwarmsDirty {
		t.Fatal("join must not create a swarm or set SwarmsDirty")
	}
	evts := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evts) != 1 || evts[0].SplitCount != 6 || evts[0].NewBugIDBase != 10 {
		t.Fatalf("SWARM_REPRODUCED = %+v, want count 6 base 10", evts)
	}
	if swarm.Satiation != 33 || swarm.ReproductionMeter != 44 {
		t.Fatal("release must NOT touch reproduction meters")
	}
	if p.BugSlots[0].Count != 0 || p.BugSlots[0].ItemID != "" {
		t.Fatal("releasing the whole slot should empty it")
	}
}

func TestReleaseSnapUsesSwarmVisualRadius(t *testing.T) {
	// THE design-review case: click at 3.5 from the center — inside the swarm's VISIBLE
	// radius (4.0) but outside merge_radius (2.5). Must JOIN, not duplicate.
	state := releaseTestState()
	releasePlayer(state, 10, 10, "fly_common", 4)
	swarm := newTestSwarm("s1", 10, 10, 10)
	swarm.Radius = 4.0
	state.Swarms["s1"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 4, 13.5, 10), "p1", 32)

	if len(state.Swarms) != 1 {
		t.Fatal("click inside the visual radius spawned a duplicate swarm")
	}
	if swarm.Count != 14 {
		t.Fatalf("swarm.Count = %d, want 14 (joined)", swarm.Count)
	}
}

func TestReleasePicksNearestOfTwo(t *testing.T) {
	state := releaseTestState()
	releasePlayer(state, 10, 10, "fly_common", 3)
	near := newTestSwarm("near", 10, 11.5, 10)
	far := newTestSwarm("far", 10, 13.5, 10)
	near.Radius, far.Radius = 4.0, 4.0
	state.Swarms["near"], state.Swarms["far"] = near, far
	state.SwarmsBySpecies["fly_common"] = []string{"far", "near"} // order must not matter

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 3, 12, 10), "p1", 32)

	if near.Count != 13 || far.Count != 10 {
		t.Fatalf("near/far = %d/%d, want 13/10 (nearest wins)", near.Count, far.Count)
	}
}

func TestReleaseDifferentSpeciesIgnored(t *testing.T) {
	state := releaseTestState()
	state.Species["butterfly_meadow"] = &entities.BugSpecies{
		MinSwarmSize: 2, MaxSwarmSize: 15, MergeRadius: 6.0, SwarmRadius: 5.0, WanderRadius: 12,
	}
	releasePlayer(state, 10, 10, "butterfly_meadow", 2)
	fly := newTestSwarm("flies", 10, 12, 10) // fly swarm at the click
	state.Swarms["flies"] = fly
	state.SwarmsBySpecies["fly_common"] = []string{"flies"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 2, 12, 10), "p1", 32)

	if fly.Count != 10 {
		t.Fatal("released butterflies joined a FLY swarm")
	}
	if len(state.Swarms) != 2 {
		t.Fatalf("swarms = %d, want 2 (new butterfly swarm)", len(state.Swarms))
	}
}

// Joining over MaxSwarmSize is allowed: the population pass (600-tick cadence) splits
// the overgrown swarm. NB: releaseTestState has NO zone caps — MaxPopulation zero-value
// = uncapped is pinned behavior (test zones depend on it).
func TestReleaseOverCapStillJoins(t *testing.T) {
	state := releaseTestState()
	releasePlayer(state, 10, 10, "fly_common", 10)
	swarm := newTestSwarm("s1", 50, 11, 10) // at MaxSwarmSize (test cap 50)
	swarm.Radius = 4.0
	state.Swarms["s1"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 10, 11, 10), "p1", 32)

	if swarm.Count != 60 {
		t.Fatalf("swarm.Count = %d, want 60 (over-cap adds; split pass rebalances)", swarm.Count)
	}
}

// Continuous spawning respects the population cap: a saturated zone stops being
// refilled by natural spawns (back-pressure half of the §13 design); the same setup
// under the cap DOES spawn (the gate, not the harness, is what blocks).
func TestContinuousSpawnRespectsPopulationCap(t *testing.T) {
	mkState := func(maxPop int) *WorldState {
		state := releaseTestState()
		state.SpeciesNextSpawn = map[string]float64{}
		state.CurrentZone.Width = 32
		state.CurrentZone.Height = 32
		state.CurrentZone.BugSpawning = &BugSpawnConfig{
			SpeciesCaps: map[string]SpeciesCap{
				"fly_common": {Max: 10, MaxPopulation: maxPop, SpawnInterval: 1, SwarmSize: 5},
			},
			SpawnAreas: []SpawnArea{{Type: "zone", Species: []string{"fly_common"}}},
		}
		s := newTestSwarm("s1", 20, 10, 10)
		state.Swarms["s1"] = s
		state.SwarmsBySpecies["fly_common"] = []string{"s1"}
		return state
	}
	m := &Match{}

	// At the cap (pop 20 >= 20): no spawn.
	capped := mkState(20)
	m.checkContinuousSpawning(capped, capped.TickCount, nopRuntimeLogger())
	if len(capped.Swarms) != 1 {
		t.Fatalf("continuous spawn leaked past the population cap: %d swarms", len(capped.Swarms))
	}

	// Under the cap: the identical harness spawns (proves the gate is what blocked).
	open := mkState(100)
	m.checkContinuousSpawning(open, open.TickCount, nopRuntimeLogger())
	if len(open.Swarms) != 2 {
		t.Fatalf("control failed — harness can't spawn at all: %d swarms", len(open.Swarms))
	}
}

// The F8 debug spawn obeys both ceilings (defense in depth).
func TestDebugSpawnRespectsCaps(t *testing.T) {
	state := releaseTestState()
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {Max: 1, MaxPopulation: 25},
	}}
	s := newTestSwarm("s1", 20, 10, 10)
	state.Swarms["s1"] = s
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}
	m := &Match{}

	// Population cap: 20 + 8 > 25 — blocked.
	m.debugSpawnSwarm(nopRuntimeLogger(), state,
		DebugWorldMessage{SpawnSpecies: "fly_common", SpawnCount: 8, SpawnX: 12, SpawnY: 12}, "dev", 32)
	if len(state.Swarms) != 1 {
		t.Fatalf("debug spawn leaked past the population cap: %d", len(state.Swarms))
	}

	// Swarm-count cap (room in population, none in count): still blocked.
	m.debugSpawnSwarm(nopRuntimeLogger(), state,
		DebugWorldMessage{SpawnSpecies: "fly_common", SpawnCount: 2, SpawnX: 12, SpawnY: 12}, "dev", 32)
	if len(state.Swarms) != 1 {
		t.Fatalf("debug spawn leaked past the swarm-count cap: %d", len(state.Swarms))
	}

	// Raise both: it spawns.
	state.CurrentZone.BugSpawning.SpeciesCaps["fly_common"] = SpeciesCap{Max: 5, MaxPopulation: 100}
	m.debugSpawnSwarm(nopRuntimeLogger(), state,
		DebugWorldMessage{SpawnSpecies: "fly_common", SpawnCount: 8, SpawnX: 12, SpawnY: 12}, "dev", 32)
	if len(state.Swarms) != 2 {
		t.Fatalf("debug spawn control failed: %d swarms", len(state.Swarms))
	}
}

// HARD population cap: a release that would push the species over is rejected before
// ANY mutation — slot intact, no swarm growth, no new swarm — on BOTH branches.
func TestReleaseRejectedAtPopulationCap(t *testing.T) {
	state := releaseTestState()
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {Max: 10, MaxPopulation: 55},
	}}

	// JOIN branch: a swarm of 50 at the click; releasing 10 would hit 60 > 55.
	p := releasePlayer(state, 10, 10, "fly_common", 10)
	swarm := newTestSwarm("s1", 50, 11, 10)
	swarm.Radius = 4.0
	state.Swarms["s1"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 10, 11, 10), "p1", 32)

	if p.BugSlots[0].Count != 10 {
		t.Fatalf("rejected release mutated the slot: %d", p.BugSlots[0].Count)
	}
	if swarm.Count != 50 || len(state.Swarms) != 1 {
		t.Fatalf("rejected release mutated swarms: count=%d swarms=%d", swarm.Count, len(state.Swarms))
	}

	// NEW-SWARM branch: same cap, click far from the swarm — still rejected.
	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 10, 7, 10), "p1", 32)
	if p.BugSlots[0].Count != 10 || len(state.Swarms) != 1 {
		t.Fatalf("new-swarm branch leaked past the population cap: slot=%d swarms=%d",
			p.BugSlots[0].Count, len(state.Swarms))
	}

	// Under the cap: the same release works (the gate is the SUM, not the state).
	state.CurrentZone.BugSpawning.SpeciesCaps["fly_common"] = SpeciesCap{Max: 10, MaxPopulation: 100}
	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 10, 11, 10), "p1", 32)
	if p.BugSlots[0].Count != 0 || swarm.Count != 60 {
		t.Fatalf("under-cap release should join: slot=%d count=%d", p.BugSlots[0].Count, swarm.Count)
	}
}

// Swarm-COUNT cap: at the cap a release can't mint a new swarm — it force-joins the
// NEAREST same-species swarm at ANY distance (the player keeps their bugs; §12.2).
func TestReleaseForceJoinsAtSwarmCountCap(t *testing.T) {
	state := releaseTestState()
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {Max: 2}, // count cap only; population uncapped
	}}
	p := releasePlayer(state, 10, 10, "fly_common", 5)
	near := newTestSwarm("near", 10, 13, 13) // ~4.6 from the click — outside snap
	far := newTestSwarm("far", 10, 30, 30)
	near.Radius, far.Radius = 1.0, 1.0 // tiny visual radii: nothing snaps at the click
	state.Swarms["near"], state.Swarms["far"] = near, far
	state.SwarmsBySpecies["fly_common"] = []string{"near", "far"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 5, 10, 10), "p1", 32)

	if len(state.Swarms) != 2 {
		t.Fatalf("at the swarm-count cap a new swarm was minted: %d", len(state.Swarms))
	}
	if near.Count != 15 {
		t.Fatalf("force-join must pick the NEAREST swarm: near=%d far=%d", near.Count, far.Count)
	}
	if p.BugSlots[0].Count != 0 {
		t.Fatalf("force-join must keep the player's bugs (slot=%d released)", p.BugSlots[0].Count)
	}
	// And it rides the ledger like any join.
	evs := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evs) != 1 || evs[0].SwarmID != "near" || evs[0].SplitCount != 5 {
		t.Fatalf("force-join event wrong: %+v", evs)
	}
}

func TestReleaseLazyNextBugIDGuard(t *testing.T) {
	state := releaseTestState()
	releasePlayer(state, 10, 10, "fly_common", 2)
	swarm := newTestSwarm("s1", 7, 11, 10)
	swarm.Radius = 4.0
	swarm.NextBugID = 0 // uninitialized — guard must set it to Count first
	state.Swarms["s1"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s1"}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 2, 11, 10), "p1", 32)

	evts := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evts) != 1 || evts[0].NewBugIDBase != 7 {
		t.Fatalf("base = %+v, want 7 (reproduceSwarm lazy-guard parity)", evts)
	}
	if swarm.NextBugID != 9 {
		t.Fatalf("NextBugID = %d, want 9", swarm.NextBugID)
	}
}

func TestReleaseReachRejected(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 5)

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 5, 20, 10), "p1", 32) // 10 units away >> 4.5

	if p.BugSlots[0].Count != 5 || len(state.Swarms) != 0 || len(state.PendingInfluence) != 0 {
		t.Fatal("out-of-reach release must be a complete no-op")
	}
}

func TestReleaseCountSemantics(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 5)
	m := &Match{}

	// count > slot clamps to slot
	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 99, 11, 10), "p1", 32)
	if p.BugSlots[0].Count != 0 {
		t.Fatalf("clamp: slot = %d, want 0", p.BugSlots[0].Count)
	}

	// count 0 rejects
	p.BugSlots[0] = InventorySlot{ItemID: "fly_common", Count: 3}
	before := len(state.PendingInfluence)
	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 0, 11, 10), "p1", 32)
	if p.BugSlots[0].Count != 3 || len(state.PendingInfluence) != before {
		t.Fatal("count 0 must be a no-op")
	}

	// -1 = all
	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, -1, 11, 10), "p1", 32)
	if p.BugSlots[0].Count != 0 || p.BugSlots[0].ItemID != "" {
		t.Fatal("-1 must release the whole slot (and clear it)")
	}
}

func TestReleaseInvalidInputs(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 5)
	m := &Match{}

	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(99, 1, 11, 10), "p1", 32) // slot OOB
	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(1, 1, 11, 10), "p1", 32) // empty slot
	p.BugSlots[2] = InventorySlot{ItemID: "unknown_species", Count: 3}
	m.handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(2, 1, 11, 10), "p1", 32) // species not in state.Species

	if p.BugSlots[0].Count != 5 || p.BugSlots[2].Count != 3 ||
		len(state.Swarms) != 0 || len(state.PendingInfluence) != 0 {
		t.Fatal("invalid inputs must all be no-ops")
	}
}

func TestReleaseWallClamped(t *testing.T) {
	state := releaseTestState()
	releasePlayer(state, 10, 10, "fly_common", 4)

	// A bug-blocking occupant wall at x=12 between player (10) and click (14)
	state.Entities["wall_test"] = &EntityDef{
		Name: "Wall", Category: "structure",
		World: &WorldData{Footprint: []int{1, 1}, BlocksBugs: true},
	}
	for y := 8; y <= 12; y++ {
		state.Chunks[ChunkKey(0, 0)].SetOccupant(12, y, &PlacedOccupant{ID: "wall_test"})
	}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), nopDispatcher{}, state,
		releaseMsg(0, 4, 14, 10), "p1", 32)

	if len(state.Swarms) != 1 {
		t.Fatalf("swarms = %d, want 1", len(state.Swarms))
	}
	for _, s := range state.Swarms {
		if wx := s.WorldX(32); wx >= 12 {
			t.Fatalf("swarm at x=%.1f, want clamped before the wall at 12", wx)
		}
	}
}

// recordingDispatcher captures broadcasts for echo assertions.
type recordingDispatcher struct {
	ops       []int64
	presences [][]runtime.Presence
}

func (r *recordingDispatcher) BroadcastMessage(op int64, data []byte, p []runtime.Presence, s runtime.Presence, rel bool) error {
	r.ops = append(r.ops, op)
	r.presences = append(r.presences, p)
	return nil
}
func (r *recordingDispatcher) BroadcastMessageDeferred(op int64, data []byte, p []runtime.Presence, s runtime.Presence, rel bool) error {
	return r.BroadcastMessage(op, data, p, s, rel)
}
func (r *recordingDispatcher) MatchKick([]runtime.Presence) error { return nil }
func (r *recordingDispatcher) MatchLabelUpdate(string) error      { return nil }

type stubPresence struct{ id string }

func (s stubPresence) GetUserId() string    { return s.id }
func (s stubPresence) GetSessionId() string { return "sess_" + s.id }
func (s stubPresence) GetNodeId() string    { return "node" }
func (s stubPresence) GetHidden() bool      { return false }
func (s stubPresence) GetPersistence() bool { return false }
func (s stubPresence) GetUsername() string  { return s.id }
func (s stubPresence) GetStatus() string    { return "" }
func (s stubPresence) GetReason() runtime.PresenceReason {
	return runtime.PresenceReasonUnknown
}

func TestReleaseEchoesSlotToReleaserOnly(t *testing.T) {
	state := releaseTestState()
	p := releasePlayer(state, 10, 10, "fly_common", 5)
	state.Presences["p1"] = stubPresence{id: "p1"}
	rec := &recordingDispatcher{}

	(&Match{}).handleReleaseBugs(nopRuntimeLogger(), rec, state,
		releaseMsg(0, 2, 11, 10), "p1", 32)

	if p.BugSlots[0].Count != 3 {
		t.Fatalf("slot = %d, want 3", p.BugSlots[0].Count)
	}
	echoes := 0
	for i, op := range rec.ops {
		if op == OpCodeBugSlotUpdate {
			echoes++
			if len(rec.presences[i]) != 1 {
				t.Fatal("slot echo must target the releaser only")
			}
		}
	}
	if echoes != 1 {
		t.Fatalf("BugSlotUpdate echoes = %d, want 1", echoes)
	}
}
