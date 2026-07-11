package world

// Tests for the PER-INDIVIDUAL bug→player sting (handleBugPlayerStrike): the authority-detect→relay path that
// replaces the old center-based checkBugAttacks (the "phantom hit" the playtest reported). The server holds only
// swarm CENTRES, so the authority reports which individual bug(s) are actually in range; the server re-gates
// through applyBugAttackToPlayer. These tests pin the server-side gates the authority relies on.
//
// Run inside the builder image:  go test ./modules/world/ -run TestBugPlayerStrike -v

import (
	"testing"
)

// Happy path: the zone authority reports an in-range attacker → the funnel applies one hit.
func TestBugPlayerStrikeApplies(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10) // centre 0.5 from the player at (10,10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2),
	})
	if p.HP != 9 {
		t.Fatalf("HP=%d, want 9 after one relayed sting", p.HP)
	}
}

// Anti-cheat: a report from anyone who is NOT the zone authority is ignored.
func TestBugPlayerStrikeAuthorityOnly(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, "not_the_authority", BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2),
	})
	if p.HP != 10 {
		t.Fatalf("HP=%d — a non-authority report must be ignored", p.HP)
	}
}

// Centre-range sanity: even a well-formed authority report is rejected if the swarm centre is nowhere near the
// player (guards against a bogus/stale report). maxR = stingRange(1.5) + swarm.Radius(4) = 5.5.
func TestBugPlayerStrikeCenterSanity(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 16.5, 10) // centre 6.5 from the player > maxR 5.5
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2),
	})
	if p.HP != 10 {
		t.Fatalf("HP=%d — a report far outside centre range must be rejected", p.HP)
	}
}

// Dodge i-frames: a well-timed roll (DodgeInvulnUntilTick in the future) negates the relayed sting.
func TestBugPlayerStrikeDodgeNegates(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000
	p.DodgeInvulnUntilTick = 1005 // rolled at t=1000, i-frames through 1004

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2),
	})
	if p.HP != 10 {
		t.Fatalf("HP=%d — a dodge i-frame must negate the sting", p.HP)
	}

	// After the window closes, the next sting lands.
	state.TickCount = 1005
	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2),
	})
	if p.HP != 9 {
		t.Fatalf("HP=%d — sting must land once the i-frame window closes", p.HP)
	}
}

// Stale ids: a reported bug that is no longer alive is skipped (no phantom damage from a dead attacker).
func TestBugPlayerStrikeDeadBugFiltered(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: []int{999}, // no such bug
	})
	if p.HP != 10 {
		t.Fatalf("HP=%d — a report naming only non-alive bugs must not damage", p.HP)
	}
}
