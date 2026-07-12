package world

// Tests for the PER-INDIVIDUAL bug→player sting: the authority-detect→relay path (handleBugPlayerStrike) that
// replaces the old center-based checkBugAttacks (the "phantom hit" the playtest reported), plus the two-beat
// TELEGRAPH — handleBugPlayerStrike ARMS a wind-up and processPendingStings fires it stingTelegraphTicks later,
// re-gated so a dodge / step-out during the wind-up negates the hit. HP is server-authoritative + sim-inert, so
// these tests are the real correctness gate (the sting won't show in the client sync hash).
//
// Run inside the builder image:  go test ./modules/world/ -run TestBugPlayerStrike -v

import (
	"testing"
)

// report arms a telegraphed sting (the first beat). fireStings advances past the wind-up and runs the fire pass.
func report(m *Match, state *WorldState, sender, swarmID, playerID string, ids []int) {
	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, sender, BugPlayerStrikeMessage{
		SwarmID: swarmID, PlayerID: playerID, BugIDs: ids,
	})
}

func fireStings(m *Match, state *WorldState) {
	state.TickCount += stingTelegraphTicks
	m.processPendingStings(nopRuntimeLogger(), nil, state)
}

// Happy path: an in-range report arms a wind-up; nothing lands until it fires; then the funnel applies one hit.
func TestBugPlayerStrikeApplies(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10) // centre 0.5 from the player at (10,10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 10 {
		t.Fatalf("HP=%d — the sting must WIND UP, not land on contact", p.HP)
	}
	if w.PendingStingTick != 1000+stingTelegraphTicks {
		t.Fatalf("PendingStingTick=%d, want %d", w.PendingStingTick, 1000+stingTelegraphTicks)
	}

	fireStings(m, state)
	if p.HP != 9 {
		t.Fatalf("HP=%d, want 9 after the telegraphed sting lands", p.HP)
	}
	if w.PendingStingTick != 0 {
		t.Fatalf("PendingStingTick=%d — must clear after firing", w.PendingStingTick)
	}
}

// Anti-cheat: a report from anyone who is NOT the zone authority arms nothing.
func TestBugPlayerStrikeAuthorityOnly(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, "not_the_authority", w.ID, "p1", w.FirstAliveBugIDs(2))
	if w.PendingStingTick != 0 {
		t.Fatalf("a non-authority report must not arm a sting (PendingStingTick=%d)", w.PendingStingTick)
	}
	fireStings(m, state)
	if p.HP != 10 {
		t.Fatalf("HP=%d — a non-authority report must never damage", p.HP)
	}
}

// Centre-range sanity: a report whose swarm centre is nowhere near the player is rejected at arm time.
// maxR = stingRange(1.5) + swarm.Radius(4) = 5.5.
func TestBugPlayerStrikeCenterSanity(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 16.5, 10) // centre 6.5 from the player > maxR 5.5
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	fireStings(m, state)
	if p.HP != 10 {
		t.Fatalf("HP=%d — a report far outside centre range must be rejected", p.HP)
	}
}

// Dodge i-frames: a roll active AT fire time negates the telegraphed sting; once it lapses the next one lands.
func TestBugPlayerStrikeDodgeNegates(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	// Dodge through the fire tick (1000 + 12 = 1012).
	p.DodgeInvulnUntilTick = 1013
	fireStings(m, state)
	if p.HP != 10 {
		t.Fatalf("HP=%d — a dodge i-frame active at fire time must negate the sting", p.HP)
	}

	// Next cycle, no dodge: it lands. (The whiffed sting never armed LastAttackTick, so re-arming is allowed.)
	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	fireStings(m, state)
	if p.HP != 9 {
		t.Fatalf("HP=%d — the sting must land once the i-frame window lapses", p.HP)
	}
}

// Step-out: if the player leaves loose sting range during the wind-up, the sting whiffs at fire time.
func TestBugPlayerStrikeStepOutWhiffs(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	p.Position.LocalX, p.Position.LocalY = 40, 40 // sprint away before the wind-up completes
	fireStings(m, state)
	if p.HP != 10 {
		t.Fatalf("HP=%d — stepping out of range during the wind-up must whiff the sting", p.HP)
	}
}

// No spam: while a sting is already wound up, a second report does not re-arm or reschedule it.
func TestBugPlayerStrikeTelegraphNoSpam(t *testing.T) {
	state, _ := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	armed := w.PendingStingTick
	state.TickCount = 1005
	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if w.PendingStingTick != armed {
		t.Fatalf("PendingStingTick=%d — a second report must not reschedule the wind-up (was %d)", w.PendingStingTick, armed)
	}
}

// Aggro: an attack-capable swarm chases a nearby player, ignores a far one, and won't aggro nocturnal-by-day.
func TestAggroPlayerThinkChasesNearbyPlayer(t *testing.T) {
	state, p := hpTestState() // wasp_common attack_damage=1; player at (10,10)
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 13, 10) // 3 cells away, inside aggro range (8)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	if !m.aggroPlayerThink(state, w, state.Species["wasp_common"], 32, 0.1) {
		t.Fatalf("a wasp should aggro a player 3 cells away")
	}

	// Far player → no aggro.
	p.Position.LocalX, p.Position.LocalY = 80, 80
	if m.aggroPlayerThink(state, w, state.Species["wasp_common"], 32, 0.1) {
		t.Fatalf("a wasp must not aggro a player far outside aggro range")
	}

	// Nocturnal-by-day → no aggro even when adjacent.
	p.Position.LocalX, p.Position.LocalY = 12, 10
	state.Species["wasp_common"].Nocturnal = true
	state.TickCount = int64(0.5 * DayLengthTicks) // day
	if m.aggroPlayerThink(state, w, state.Species["wasp_common"], 32, 0.1) {
		t.Fatalf("a nocturnal species must not aggro by day")
	}
}

// Aggro hysteresis: acquire within ENTER (8), stay sticky out to EXIT (12), release beyond it.
func TestAggroHysteresis(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 0, 0) // swarm at origin
	state.Swarms[w.ID] = w
	state.TickCount = 1000
	sp := state.Species["wasp_common"]

	// 10 cells away (> enter 8): no aggro.
	p.Position.LocalX, p.Position.LocalY = 10, 0
	if m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "" {
		t.Fatalf("must not aggro beyond enter range (10 > 8)")
	}
	// 6 cells (< enter 8): acquire.
	p.Position.LocalX, p.Position.LocalY = 6, 0
	if !m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "p1" {
		t.Fatalf("must aggro within enter range (6 < 8)")
	}
	// Drifts to 10 (between enter 8 and exit 12): STICKY, still engaged.
	p.Position.LocalX, p.Position.LocalY = 10, 0
	if !m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "p1" {
		t.Fatalf("hysteresis: must keep chasing between enter and exit (10 < 12)")
	}
	// Past exit 12: release.
	p.Position.LocalX, p.Position.LocalY = 13, 0
	if m.aggroPlayerThink(state, w, sp, 32, 0.1) || w.AggroTargetID != "" {
		t.Fatalf("must release past exit range (13 > 12)")
	}
}

// Nocturnal: a night hunter can't arm a sting by day; at night it arms + lands.
func TestBugPlayerStrikeNocturnalGate(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	state.Species["wasp_common"].Nocturnal = true
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.DayOffsetTicks = 0

	// DAY (t≈0.5): no wind-up arms.
	state.TickCount = int64(0.5 * DayLengthTicks)
	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if w.PendingStingTick != 0 {
		t.Fatalf("a nocturnal species must not arm a sting by day (PendingStingTick=%d)", w.PendingStingTick)
	}

	// NIGHT (t≈0.70 — the debug "Night" button value): it arms, and the sting lands.
	state.TickCount = int64(0.70 * DayLengthTicks)
	report(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if w.PendingStingTick == 0 {
		t.Fatalf("a nocturnal species must arm a sting at night")
	}
	fireStings(m, state)
	if p.HP != 9 {
		t.Fatalf("HP=%d — a nocturnal sting must land at night", p.HP)
	}
}

// Stale ids: a report naming only non-alive bugs arms nothing (no phantom wind-up from a dead attacker).
func TestBugPlayerStrikeDeadBugFiltered(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	report(m, state, testAuthority, w.ID, "p1", []int{999}) // no such bug
	if w.PendingStingTick != 0 {
		t.Fatalf("a report of only non-alive bugs must not arm a sting (PendingStingTick=%d)", w.PendingStingTick)
	}
	fireStings(m, state)
	if p.HP != 10 {
		t.Fatalf("HP=%d — a report naming only non-alive bugs must not damage", p.HP)
	}
}
