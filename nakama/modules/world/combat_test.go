package world

// Unit tests for combat v1: data-driven catch (large_net fix + same-tick burst), the
// sparse per-bug HP map (DamageBug, RemoveBugs cleanup, split/merge transfer along the
// deterministic id mappings), and handleMeleeAttack (cooldown gate, swing-total cap,
// two-attackers-one-bug, kill -> BUG_REMOVED ledger + cleanup).
//
// Run inside the builder image:  go test ./modules/world/ -run 'TestCatch|TestMelee|TestBugHP' -v

import (
	"testing"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// nopDispatcher satisfies runtime.MatchDispatcher for handler tests.
type nopDispatcher struct{}

func (nopDispatcher) BroadcastMessage(int64, []byte, []runtime.Presence, runtime.Presence, bool) error {
	return nil
}
func (nopDispatcher) BroadcastMessageDeferred(int64, []byte, []runtime.Presence, runtime.Presence, bool) error {
	return nil
}
func (nopDispatcher) MatchKick([]runtime.Presence) error { return nil }
func (nopDispatcher) MatchLabelUpdate(string) error      { return nil }

// combatTestState extends newTestState with the maps/data the catch+melee handlers touch.
func combatTestState() *WorldState {
	state := newTestState(50)
	state.Players = map[string]*PlayerState{}
	state.Presences = map[string]runtime.Presence{}
	state.ChunkSubs = map[string]map[string]bool{}
	state.Entities = map[string]*EntityDef{
		// Nets stay TOP-LEVEL (one move, own cap semantics + own rate-limit slot)
		"small_net": {ToolType: "net", Reach: 2.5, CatchCap: 10, CooldownTicks: 3},
		"large_net": {ToolType: "net", Reach: 3.5, CatchCap: 20, CooldownTicks: 3},
		// Weapons: combat stats live in MOVES (mirrors prod items.json)
		"sword_wood": {ToolType: "sword", Moves: map[string]*MoveDef{
			"primary":   {Kind: "swing", Damage: 1, ArcDegrees: 100, Reach: 2.5, MaxTargets: 6, CooldownTicks: 4},
			"secondary": {Kind: "stab", Damage: 2, ArcDegrees: 20, Reach: 3.5, MaxTargets: 2, CooldownTicks: 5},
		}},
		"spear_wood": {ToolType: "spear", Moves: map[string]*MoveDef{
			"primary":   {Kind: "stab", Damage: 1, ArcDegrees: 20, Reach: 4.0, MaxTargets: 3, CooldownTicks: 5},
			"secondary": {Kind: "sweep", Damage: 1, ArcDegrees: 140, Reach: 2.0, MaxTargets: 5, CooldownTicks: 6},
		}},
		// Axes alt-attack via a secondary JAB only (left-click stays breaking)
		"axe_wood": {ToolType: "axe", Reach: 3.5, Moves: map[string]*MoveDef{
			"secondary": {Kind: "stab", Damage: 1, ArcDegrees: 20, Reach: 3.0, MaxTargets: 2, CooldownTicks: 5},
		}},
	}
	return state
}

func testPlayer(x, y float32, tool string) *PlayerState {
	p := &PlayerState{UserID: "p1", EquippedTool: tool}
	p.Position = entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: x, LocalY: y}
	return p
}

func idRange(n int) []int {
	ids := make([]int, n)
	for i := range ids {
		ids[i] = i
	}
	return ids
}

// --- Catch: data-driven reach/cap + same-tick burst ---

func TestCatchLargeNetUsesItsData(t *testing.T) {
	state := combatTestState()
	player := testPlayer(10, 10, "large_net")
	state.Players["p1"] = player
	swarm := newTestSwarm("s1", 30, 13, 10) // 3.0 away: inside large_net 3.5, outside hand 2.0
	state.Swarms["s1"] = swarm

	msg := CatchBugMessage{ClickX: 13, ClickY: 10, SwarmID: "s1", BugIDs: idRange(25)}
	(&Match{}).handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	// large_net cap is 20 (the old code treated it as a bare hand: reach 2.0, cap 5)
	if got := 30 - swarm.Count; got != 20 {
		t.Fatalf("large_net removed %d bugs, want 20 (catch_cap)", got)
	}
}

func TestCatchHandReachRejectsFarClick(t *testing.T) {
	state := combatTestState()
	state.Players["p1"] = testPlayer(10, 10, "") // bare hand
	swarm := newTestSwarm("s1", 10, 13.5, 10)    // 3.5 away > hand 2.0+0.5
	state.Swarms["s1"] = swarm

	msg := CatchBugMessage{ClickX: 13.5, ClickY: 10, SwarmID: "s1", BugIDs: idRange(3)}
	(&Match{}).handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	if swarm.Count != 10 {
		t.Fatalf("hand catch at 3.5 units removed %d bugs, want 0 (out of reach)", 10-swarm.Count)
	}
}

func TestCatchSameTickBurstHitsBothSwarms(t *testing.T) {
	state := combatTestState()
	state.Players["p1"] = testPlayer(10, 10, "small_net")
	s1 := newTestSwarm("s1", 10, 11, 10)
	s2 := newTestSwarm("s2", 10, 11, 11)
	state.Swarms["s1"], state.Swarms["s2"] = s1, s2

	// One swing, two swarms -> two messages in the same tick: BOTH must land
	// (the old per-message stamp dropped the second -> client-side ghost bugs).
	m := &Match{}
	m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state,
		CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: "s1", BugIDs: idRange(4)}, "p1", 32)
	m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state,
		CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: "s2", BugIDs: idRange(4)}, "p1", 32)

	if s1.Count != 6 || s2.Count != 6 {
		t.Fatalf("same-tick burst: s1=%d s2=%d, want 6/6", s1.Count, s2.Count)
	}

	// A NEW swing on the very next tick is inside the 3-tick cooldown -> rejected.
	state.TickCount++
	m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state,
		CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: "s1", BugIDs: idRange(4)}, "p1", 32)
	if s1.Count != 6 {
		t.Fatalf("cooldown: next-tick swing removed bugs (s1=%d), want rejected", s1.Count)
	}
}

func TestCatchCleansBugHP(t *testing.T) {
	state := combatTestState()
	state.Players["p1"] = testPlayer(10, 10, "small_net")
	swarm := newTestSwarm("s1", 10, 11, 10)
	state.Swarms["s1"] = swarm
	swarm.DamageBug(2, 1, 3) // bug 2 damaged to hp 2

	msg := CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: "s1", BugIDs: []int{2}}
	(&Match{}).handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	if _, leaked := swarm.BugHP[2]; leaked {
		t.Fatal("catching a damaged bug leaked its BugHP entry")
	}
}

// --- BugHP core ---

func TestBugHPDamageThenKill(t *testing.T) {
	swarm := newTestSwarm("s1", 5, 0, 0)

	hp, survived := swarm.DamageBug(1, 1, 2)
	if !survived || hp != 1 {
		t.Fatalf("first hit: hp=%d survived=%v, want 1/true", hp, survived)
	}
	if swarm.BugHP[1] != 1 {
		t.Fatalf("BugHP[1]=%d, want 1", swarm.BugHP[1])
	}

	hp, survived = swarm.DamageBug(1, 1, 2)
	if survived || hp != 0 {
		t.Fatalf("second hit: hp=%d survived=%v, want 0/false (kill)", hp, survived)
	}
	removed := swarm.RemoveBugs([]int{1})
	if len(removed) != 1 {
		t.Fatalf("kill removal removed %d, want 1", len(removed))
	}
	if _, leaked := swarm.BugHP[1]; leaked {
		t.Fatal("RemoveBugs left a stale BugHP entry")
	}
	// Double-kill: second removal returns empty (no double drop upstream)
	if again := swarm.RemoveBugs([]int{1}); len(again) != 0 {
		t.Fatalf("double-kill removed %d, want 0", len(again))
	}
}

func TestSplitTransfersBugHP(t *testing.T) {
	state := newTestState(20)
	parent := newTestSwarm("parent", 21, 10, 10) // splits: sheds highest 10 ids (11..20)
	state.Swarms["parent"] = parent
	state.SwarmsBySpecies["fly_common"] = []string{"parent"}
	parent.DamageBug(15, 1, 3) // hp 2; shed asc 11..20 -> child ids 0..9, so 15 -> child 4
	parent.DamageBug(3, 1, 3)  // stays in the parent

	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())

	var child *entities.SwarmState
	for id, s := range state.Swarms {
		if id != "parent" {
			child = s
		}
	}
	if child == nil {
		t.Fatal("no child swarm created")
	}
	if child.BugHP[4] != 2 {
		t.Fatalf("child.BugHP[4]=%d, want 2 (parent id 15 -> child id 4)", child.BugHP[4])
	}
	if len(child.BugHP) != 1 {
		t.Fatalf("child.BugHP has %d entries, want 1", len(child.BugHP))
	}
	if parent.BugHP[3] != 2 {
		t.Fatalf("parent.BugHP[3]=%d, want 2 (undamaged by the split)", parent.BugHP[3])
	}
	if _, leaked := parent.BugHP[15]; leaked {
		t.Fatal("parent kept the shed bug's BugHP entry")
	}
}

func TestMergeTransfersBugHP(t *testing.T) {
	state := newTestState(50)
	s1 := newTestSwarm("s1", 5, 10, 10)
	s2 := newTestSwarm("s2", 5, 11, 10) // within MergeRadius 2.5
	state.Swarms["s1"], state.Swarms["s2"] = s1, s2
	state.SwarmsBySpecies["fly_common"] = []string{"s1", "s2"}
	s2.DamageBug(2, 1, 3) // hp 2; absorbed asc ids 0..4 -> survivor base+k, so 2 -> base+2

	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())

	if len(state.Swarms) != 1 {
		t.Fatalf("swarms after merge = %d, want 1", len(state.Swarms))
	}
	survivor := state.Swarms["s1"]
	if survivor == nil {
		t.Fatal("survivor s1 missing")
	}
	// newBugIDBase = s1.NextBugID before merge = 5; absorbed id 2 -> survivor id 7
	if survivor.BugHP[7] != 2 {
		t.Fatalf("survivor.BugHP[7]=%d, want 2 (absorbed id 2 -> 5+2)", survivor.BugHP[7])
	}
}

// --- Melee handler ---

func meleeState(maxHP int) (*WorldState, *entities.SwarmState) {
	state := combatTestState()
	state.Species["fly_common"].MaxHP = maxHP
	state.Players["p1"] = testPlayer(10, 10, "sword_wood")
	swarm := newTestSwarm("s1", 10, 11, 10) // 1.0 away, inside sword reach 2.5
	state.Swarms["s1"] = swarm
	return state, swarm
}

func TestMeleeDamageThenKillSecondSwing(t *testing.T) {
	state, swarm := meleeState(2)
	m := &Match{}

	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0, 1, 2}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	if swarm.Count != 10 {
		t.Fatalf("first swing on 2-HP bugs killed %d, want 0", 10-swarm.Count)
	}
	for _, id := range []int{0, 1, 2} {
		if swarm.BugHP[id] != 1 {
			t.Fatalf("BugHP[%d]=%d, want 1", id, swarm.BugHP[id])
		}
	}

	// Second swing past the cooldown finishes them
	state.TickCount += 10
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 7 {
		t.Fatalf("second swing killed %d, want 3", 10-swarm.Count)
	}
	removedEvents := eventsOfType(state, InfluenceBugRemoved)
	if len(removedEvents) != 3 {
		t.Fatalf("BUG_REMOVED events = %d, want 3 (kills ride the ledger)", len(removedEvents))
	}
	for _, id := range []int{0, 1, 2} {
		if _, leaked := swarm.BugHP[id]; leaked {
			t.Fatalf("killed bug %d leaked a BugHP entry", id)
		}
	}
}

func TestMeleeCooldownGate(t *testing.T) {
	state, swarm := meleeState(1)
	m := &Match{}
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}

	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 9 {
		t.Fatalf("first swing killed %d, want 1", 10-swarm.Count)
	}

	// Same tick AND next tick are both inside the 4-tick cooldown -> rejected.
	msg.Hits[0].BugIDs = []int{1}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	state.TickCount++
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 9 {
		t.Fatalf("cooldown: extra swings killed %d more, want 0", 9-swarm.Count)
	}
}

func TestMeleeSwingTotalCapAcrossSwarms(t *testing.T) {
	state, _ := meleeState(1)
	s2 := newTestSwarm("s2", 10, 11, 11)
	state.Swarms["s2"] = s2
	m := &Match{}

	// 5 + 5 claimed hits, sword max_targets 6 -> total struck must be 6, not 10.
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10, Hits: []MeleeSwarmHits{
		{SwarmID: "s1", BugIDs: idRange(5)},
		{SwarmID: "s2", BugIDs: idRange(5)},
	}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	totalKilled := (10 - state.Swarms["s1"].Count) + (10 - s2.Count)
	if totalKilled != 6 {
		t.Fatalf("swing-total cap: struck %d across swarms, want 6 (max_targets)", totalKilled)
	}
}

func TestMeleeTwoAttackersOneBug(t *testing.T) {
	state, swarm := meleeState(1)
	p2 := testPlayer(10, 10, "sword_wood")
	p2.UserID = "p2"
	state.Players["p2"] = p2
	m := &Match{}

	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p2", 32)

	if swarm.Count != 9 {
		t.Fatalf("two attackers on one bug killed %d, want 1 (second whiffs)", 10-swarm.Count)
	}
	if got := len(eventsOfType(state, InfluenceBugRemoved)); got != 1 {
		t.Fatalf("BUG_REMOVED events = %d, want 1 (no double kill/drop)", got)
	}
}

func TestMeleeRejectsNonWeaponTool(t *testing.T) {
	// The gate is move-existence: a net has NO moves map, so any melee attempt is
	// rejected (it used to be a tool_type check; same outcome, new reason).
	state, swarm := meleeState(1)
	state.Players["p1"].EquippedTool = "small_net"
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 10 {
		t.Fatal("a net performed a melee attack — tool gate failed")
	}
}

// --- Movesets ---

func TestMeleeSecondaryUsesItsMoveStats(t *testing.T) {
	// Sword secondary: reach 3.5 (primary 2.5 would reject the 3.3 click), damage 2.
	state := combatTestState()
	state.Species["fly_common"].MaxHP = 3
	state.Players["p1"] = testPlayer(10, 10, "sword_wood")
	swarm := newTestSwarm("s1", 5, 13.3, 10) // 3.3 away
	state.Swarms["s1"] = swarm

	msg := MeleeAttackMessage{ClickX: 13.3, ClickY: 10, Move: "secondary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	if swarm.BugHP[0] != 1 {
		t.Fatalf("BugHP[0]=%d, want 1 (3 maxHP − 2 jab damage)", swarm.BugHP[0])
	}
}

func TestMeleePrimaryBeyondItsReachRejectedWithoutStamp(t *testing.T) {
	// The same 3.3-unit click: primary (reach 2.5+0.5) rejects — and must NOT stamp
	// the cooldown (a far click that eats your cooldown is the bug the reorder fixes);
	// secondary (3.5+0.5) immediately lands.
	state := combatTestState()
	state.Species["fly_common"].MaxHP = 1
	state.Players["p1"] = testPlayer(10, 10, "sword_wood")
	swarm := newTestSwarm("s1", 5, 13.3, 10)
	state.Swarms["s1"] = swarm
	m := &Match{}

	primary := MeleeAttackMessage{ClickX: 13.3, ClickY: 10, Move: "primary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, primary, "p1", 32)
	if swarm.Count != 5 {
		t.Fatal("primary landed beyond its reach")
	}
	if state.Players["p1"].LastToolTick == state.TickCount {
		t.Fatal("rejected-by-reach swing stamped the cooldown")
	}

	secondary := MeleeAttackMessage{ClickX: 13.3, ClickY: 10, Move: "secondary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, secondary, "p1", 32)
	if swarm.Count != 4 {
		t.Fatal("secondary at the same distance should land (its reach is 3.5)")
	}
}

func TestMeleeUnknownMoveRejectedWithoutStamp(t *testing.T) {
	state, swarm := meleeState(1)
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "tertiary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 10 {
		t.Fatal("unknown move performed an attack")
	}
	if state.Players["p1"].LastToolTick == state.TickCount {
		t.Fatal("unknown move stamped the cooldown")
	}
}

func TestMeleeEmptyMoveDefaultsToPrimary(t *testing.T) {
	state, swarm := meleeState(1)
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10, // Move omitted
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 9 {
		t.Fatal("empty move did not resolve to primary")
	}
}

func TestMeleeAxeSecondaryOnly(t *testing.T) {
	// Axes have ONLY a secondary combat move (left-click stays breaking).
	state, swarm := meleeState(1)
	state.Players["p1"].EquippedTool = "axe_wood"
	m := &Match{}

	primary := MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "primary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, primary, "p1", 32)
	if swarm.Count != 10 {
		t.Fatal("axe primary melee should be rejected (no such move)")
	}

	secondary := MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "secondary",
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, secondary, "p1", 32)
	if swarm.Count != 9 {
		t.Fatal("axe secondary should damage bugs")
	}
}

func TestMeleeSharedCooldownAcrossMoves(t *testing.T) {
	// primary (cd 4) at tick T, then secondary at T+1: the SHARED LastToolTick gates it
	// (alternating jab/swing spam is closed); secondary at T+5 lands (its cd is 5).
	state, swarm := meleeState(1)
	m := &Match{}

	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state,
		MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "primary",
			Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}, "p1", 32)
	if swarm.Count != 9 {
		t.Fatal("setup: primary should land")
	}

	state.TickCount++
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state,
		MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "secondary",
			Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{1}}}}, "p1", 32)
	if swarm.Count != 9 {
		t.Fatal("secondary inside the shared cooldown should be rejected")
	}

	state.TickCount += 4 // now T+5 since the stamp
	m.handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state,
		MeleeAttackMessage{ClickX: 11, ClickY: 10, Move: "secondary",
			Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{1}}}}, "p1", 32)
	if swarm.Count != 8 {
		t.Fatal("secondary past the cooldown should land")
	}
}

func TestMeleeBareHandRejected(t *testing.T) {
	state, swarm := meleeState(1)
	state.Players["p1"].EquippedTool = ""
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 10 {
		t.Fatal("bare hand performed a melee attack")
	}
}

func TestMeleeUnknownWeaponIdNoPanic(t *testing.T) {
	// EquipTool relays arbitrary client strings; an Entities-absent id must be a clean
	// rejection (nil-receiver-safe GetMove), never a panic in the match loop.
	state, swarm := meleeState(1)
	state.Players["p1"].EquippedTool = "ghost_sword"
	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: []int{0}}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if swarm.Count != 10 {
		t.Fatal("unknown weapon id performed a melee attack")
	}
}

func TestMeleeEmptySwarmDespawns(t *testing.T) {
	state := combatTestState()
	state.Species["fly_common"].MaxHP = 1
	state.Players["p1"] = testPlayer(10, 10, "sword_wood")
	swarm := newTestSwarm("s1", 3, 11, 10)
	state.Swarms["s1"] = swarm

	msg := MeleeAttackMessage{ClickX: 11, ClickY: 10,
		Hits: []MeleeSwarmHits{{SwarmID: "s1", BugIDs: idRange(3)}}}
	(&Match{}).handleMeleeAttack(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)

	if _, alive := state.Swarms["s1"]; alive {
		t.Fatal("emptied swarm not despawned")
	}
	if !state.SwarmsDirty {
		t.Fatal("despawn must set SwarmsDirty (catch-path parity)")
	}
}
