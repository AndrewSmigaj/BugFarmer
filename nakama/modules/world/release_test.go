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
