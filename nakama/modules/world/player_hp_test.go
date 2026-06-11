package world

// Tests for player HP v1: bug attacks (invuln + per-swarm cooldown), faint/respawn,
// and the regen pass.
//
// Run inside the builder image:  go test ./modules/world/ -run TestPlayerHP -v

import (
	"testing"

	"bugfarmer/entities"
)

func hpTestState() (*WorldState, *PlayerState) {
	state := predationTestState()
	state.Species["wasp_common"].AttackDamage = 1
	state.Species["wasp_common"].AttackCooldown = 2.0
	state.CurrentZone.SpawnPoint = [2]int{100, 100}
	p := &PlayerState{
		UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10},
	}
	state.Players = map[string]*PlayerState{"p1": p}
	return state, p
}

// Contact sting: damage lands, then the per-swarm cooldown AND the shared invuln both
// gate; a SECOND swarm is blocked by the shared invuln window.
func TestPlayerHPInvulnAcrossAttackers(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	species := state.Species["wasp_common"]
	w1 := newWaspSwarm("a_w1", 6, 10.5, 10)
	w2 := newWaspSwarm("b_w2", 6, 9.5, 10)
	state.Swarms[w1.ID] = w1
	state.Swarms[w2.ID] = w2
	state.TickCount = 1000

	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w1, species, 32)
	if p.HP != 9 {
		t.Fatalf("HP=%d, want 9 after one sting", p.HP)
	}

	// Second swarm, same tick: the SHARED invuln blocks.
	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w2, species, 32)
	if p.HP != 9 {
		t.Fatalf("HP=%d — invuln must gate across attackers", p.HP)
	}

	// Same swarm after invuln but inside ITS cooldown (2s = 20 ticks): still blocked.
	state.TickCount += 15
	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w1, species, 32)
	if p.HP != 9 {
		t.Fatalf("HP=%d — per-swarm cooldown must hold", p.HP)
	}

	// Both gates open: the OTHER swarm stings.
	state.TickCount += 10
	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w2, species, 32)
	if p.HP != 8 {
		t.Fatalf("HP=%d, want 8", p.HP)
	}
}

// Faint at 0: HP refills + the SERVER position snaps to the zone spawn.
func TestPlayerHPFaintRespawn(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	species := state.Species["wasp_common"]
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	p.HP = 1
	state.TickCount = 1000

	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w, species, 32)

	if p.HP != p.MaxHP {
		t.Fatalf("faint must refill: HP=%d", p.HP)
	}
	if p.WorldX(32) != 100 || p.WorldY(32) != 100 {
		t.Fatalf("faint must respawn at the zone spawn: (%.0f, %.0f)", p.WorldX(32), p.WorldY(32))
	}
}

// Regen: +1 only at the interval, only after the damage delay, never past max.
func TestPlayerHPRegen(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	p.HP = 5
	p.LastDamageTick = 1000

	// Too soon after damage (inside the 100-tick delay).
	state.TickCount = 1050
	for state.TickCount%300 != 0 {
		state.TickCount++
	}
	if state.TickCount-p.LastDamageTick < 100 {
		m.processPlayerRegen(nil, state)
		if p.HP != 5 {
			t.Fatalf("regen fired inside the damage delay: HP=%d", p.HP)
		}
	}

	// Past the delay, on the interval: +1.
	state.TickCount = 1500 // 1500%300==0, 500 ticks after damage
	m.processPlayerRegen(nil, state)
	if p.HP != 6 {
		t.Fatalf("HP=%d, want 6", p.HP)
	}

	// Off-interval ticks: nothing.
	state.TickCount = 1501
	m.processPlayerRegen(nil, state)
	if p.HP != 6 {
		t.Fatalf("regen fired off-interval: HP=%d", p.HP)
	}

	// Never past max.
	p.HP = 10
	state.TickCount = 1800
	m.processPlayerRegen(nil, state)
	if p.HP != 10 {
		t.Fatalf("regen overfilled: HP=%d", p.HP)
	}
}

// Out of sting range: nothing happens.
func TestPlayerHPRangeGate(t *testing.T) {
	state, p := hpTestState()
	m := &Match{}
	species := state.Species["wasp_common"]
	w := newWaspSwarm("a_w", 6, 14, 10) // 4 units away > sting range 1.5
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.checkBugAttacks(nopRuntimeLogger(), nil, state, w, species, 32)
	if p.HP != 10 {
		t.Fatalf("HP=%d — out-of-range sting landed", p.HP)
	}
}
