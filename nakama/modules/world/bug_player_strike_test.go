package world

// Tests for the bug→player attack subsystem (bug_attack.go). The AUTHORITY client owns the two-beat timing +
// the precise per-individual range check; the server (handleBugPlayerStrike) re-gates and applies. A "strike"
// applies immediately (no server-scheduled centre-fire → no phantom); a "windup" only flashes the telegraph.
// HP is server-authoritative + sim-inert, so these are the real correctness gate.
//
// Run inside the builder image:  go test ./modules/world/ -run 'TestBugPlayerStrike|TestAggro' -v

import (
	"testing"
)

func strike(m *Match, state *WorldState, sender, swarmID, playerID string, ids []int) {
	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, sender, BugPlayerStrikeMessage{
		SwarmID: swarmID, PlayerID: playerID, BugIDs: ids, Phase: "strike",
	})
}

// Happy path: an in-range strike from the authority applies one hit immediately.
func TestBugPlayerStrikeApplies(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10) // centre 0.5 from the player at (10,10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 9 {
		t.Fatalf("HP=%d, want 9 after one strike", p.HP)
	}
}

// A "windup" flashes the telegraph only — no damage.
func TestBugPlayerStrikeWindupNoDamage(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2), Phase: "windup",
	})
	if p.HP != 10 {
		t.Fatalf("HP=%d — a windup must not deal damage", p.HP)
	}
}

// Anti-cheat: a strike from anyone who is NOT the zone authority is ignored.
func TestBugPlayerStrikeAuthorityOnly(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	strike(m, state, "not_the_authority", w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 10 {
		t.Fatalf("HP=%d — a non-authority strike must be ignored", p.HP)
	}
}

// Centre-range sanity: a strike whose swarm centre is nowhere near the player is rejected (anti-cheat).
// maxR = range(1.5) + radius(4) + margin(1) = 6.5.
func TestBugPlayerStrikeCenterSanity(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 20, 10) // centre 10 from the player > maxR 6.5
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 10 {
		t.Fatalf("HP=%d — a strike far outside centre range must be rejected", p.HP)
	}
}

// Dodge i-frames negate the strike; once the window lapses the next one lands.
func TestBugPlayerStrikeDodgeNegates(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000
	p.DodgeInvulnUntilTick = 1005

	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 10 {
		t.Fatalf("HP=%d — a dodge i-frame must negate the strike", p.HP)
	}
	state.TickCount = 1005 // window lapsed
	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 9 {
		t.Fatalf("HP=%d — the strike must land once the i-frame window closes", p.HP)
	}
}

// Nocturnal: no strike by day; lands at night. Gate lives in the shared bugAttackAllowed (applies to BOTH styles).
func TestBugPlayerStrikeNocturnalGate(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	state.Species["wasp_common"].Nocturnal = true
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.DayOffsetTicks = 0

	state.TickCount = int64(0.5 * DayLengthTicks) // day
	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 10 {
		t.Fatalf("HP=%d — a nocturnal species must not strike by day", p.HP)
	}
	state.TickCount = int64(0.70 * DayLengthTicks) // night (F8 "Night" button value)
	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 9 {
		t.Fatalf("HP=%d — a nocturnal strike must land at night", p.HP)
	}
}

// Stale ids: a strike naming only non-alive bugs deals no damage.
func TestBugPlayerStrikeDeadBugFiltered(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	strike(m, state, testAuthority, w.ID, "p1", []int{999}) // no such bug
	if p.HP != 10 {
		t.Fatalf("HP=%d — a strike naming only non-alive bugs must not damage", p.HP)
	}
}

// Aggro hysteresis: acquire within ENTER (8), stay sticky out to EXIT (12), release beyond it.
func TestAggroHysteresis(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 0, 0)
	state.Swarms[w.ID] = w
	state.TickCount = 1000
	sp := state.Species["wasp_common"]

	p.Position.LocalX, p.Position.LocalY = 10, 0 // > enter 8
	if m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "" {
		t.Fatalf("must not aggro beyond enter range (10 > 8)")
	}
	p.Position.LocalX, p.Position.LocalY = 6, 0 // < enter 8
	if !m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "p1" {
		t.Fatalf("must aggro within enter range (6 < 8)")
	}
	p.Position.LocalX, p.Position.LocalY = 10, 0 // between enter 8 and exit 12: sticky
	if !m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "p1" {
		t.Fatalf("hysteresis: must keep chasing between enter and exit (10 < 12)")
	}
	p.Position.LocalX, p.Position.LocalY = 13, 0 // > exit 12: release
	if m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "" {
		t.Fatalf("must release past exit range (13 > 12)")
	}
}
