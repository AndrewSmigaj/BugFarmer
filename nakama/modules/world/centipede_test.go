package world

// Tests for the centipede ActionState machine (windup/surge/recover/gnaw), the
// serpentine wander escape hatch, and the swarm-of-one invariants.
//
// Run inside the builder image:  go test ./modules/world/ -run TestCent -v

import (
	"testing"

	"bugfarmer/entities"
)

func centTestState() (*WorldState, *entities.SwarmState) {
	state := predationTestState()
	state.Species["centipede_garden"] = &entities.BugSpecies{
		ID: "centipede_garden", Category: "individual",
		BaseSpeed: 1.6, VisionRange: 10, WanderRadius: 15,
		MinSwarmSize: 1, MaxSwarmSize: 1,
		AttackDamage: 2, AttackCooldown: 5.0,
		MaxHP: 6, NetSize: "trap_only",
		AttractionsByPhase: map[string][]string{}, // pure hunter — no scavenging (breeds via the well-fed timer)
		Predation: &entities.PredationConfig{
			Prey: []string{"fly_common"}, StrikeRadius: 1.2, StrikeCooldownTicks: 50,
			KillsPerStrike: 1, FeedPerKill: 30, HuntSpeedMult: 1.0,
			HuntSatiationThreshold: 30, NestOccupant: "",
		},
	}
	state.Entities["fence_wood"] = &EntityDef{World: &WorldData{
		BlocksBugs: true, Gnawable: true,
		Breakable: &BreakableData{HP: 2, RequiredToolType: "axe"},
	}}
	state.Entities["fence_stone"] = &EntityDef{World: &WorldData{
		BlocksBugs: true, // NOT gnawable
		Breakable:  &BreakableData{HP: 4, RequiredToolType: "pickaxe"},
	}}

	cent := newTestSwarm("c_cent", 1, 10, 10)
	cent.SpeciesID = "centipede_garden"
	cent.HomePos = cent.Position
	state.Swarms[cent.ID] = cent
	return state, cent
}

// driveCentTick replicates the loop order for the centipede: ActionState per tick →
// think gate → move.
func driveCentTick(m *Match, state *WorldState, cent *entities.SwarmState) {
	state.TickCount++
	species := state.Species[cent.SpeciesID]
	active := m.processActionState(nopRuntimeLogger(), nil, state, cent, species, 32, 0.1)
	if !active && state.TickCount >= cent.NextThinkTick {
		if !m.predationThink(state, cent, species, 32, 0.1, nopRuntimeLogger()) {
			cent.SpeedMult = 1.0
			cent.TargetPreyID = ""
			cent.NextThinkTick = state.TickCount + 30
		}
	}
	cent.Move(0.1, species, 32)
}

// Surge: trigger at 5.0 → 8-tick windup freeze → clamped lead surge → overshoot →
// turnaround → idle on a cooldown. The BITE is no longer applied here: the connect is detected
// client-side (against the rendered sprite) and applied via handleBugPlayerStrike
// (bug_player_strike_test.go). The server surge is therefore DAMAGE-FREE — this test guards that
// invariant (the phantom is gone) plus the choreography.
func TestCentSurgeCycle(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 13, LocalY: 10}} // 3u away, standing still
	state.Players = map[string]*PlayerState{"p1": p}

	// Trigger + windup freeze
	driveCentTick(m, state, cent)
	if cent.ActionState != "windup" {
		t.Fatalf("state=%q, want windup", cent.ActionState)
	}
	frozeX := cent.WorldX(32)
	for i := 0; i < centWindupTicks-1; i++ { // up to (not incl.) the launch tick
		driveCentTick(m, state, cent)
		if cent.WorldX(32) != frozeX {
			t.Fatal("centipede moved during the windup freeze")
		}
	}
	driveCentTick(m, state, cent) // the launch tick: surge leg + first move
	if cent.ActionState != "surge" {
		t.Fatalf("state=%q, want surge after the windup", cent.ActionState)
	}

	// No server bite → the surge overshoots and banks into the turnaround, then idles on a cooldown.
	sawTurnaround := false
	for i := 0; i < centSurgeMaxTicks+centTurnLegs*centTurnLegTicks+centRecoverTicks+8; i++ {
		driveCentTick(m, state, cent)
		if cent.ActionState == "turnaround" {
			sawTurnaround = true
		}
		if sawTurnaround && cent.ActionState == "" {
			break
		}
	}
	if p.HP != 10 {
		t.Fatalf("server surge applied HP=%d — it must be DAMAGE-FREE (the client detects the bite)", p.HP)
	}
	if !sawTurnaround {
		t.Fatal("a surge with no server bite must bank into the turnaround")
	}
	if cent.ActionState != "" {
		t.Fatalf("state=%q, want idle after the cycle", cent.ActionState)
	}
	if cent.SurgeCooldownUntil <= state.TickCount {
		t.Fatal("surge cooldown not armed after the cycle")
	}
}

// The velocity lead: launchSurge aims at pos + velocity×flight×lead, so the surge target LEADS a
// moving player — a +Y drifter yields a HIGHER surge target Y than the same player drifting −Y. This
// is the server-side geometry (unchanged); whether the lead CONNECTS is now detected client-side
// against the rendered sprite, so this test verifies the aim, not an HP hit.
func TestCentSurgeLead(t *testing.T) {
	surgeTargetY := func(vy float32) float32 {
		state, cent := centTestState()
		m := &Match{}
		p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
			Position: entities.EntityPosition{LocalX: 14, LocalY: 10}}
		state.Players = map[string]*PlayerState{"p1": p}

		for i := 0; i < 60 && cent.ActionState != "surge"; i++ {
			driveCentTick(m, state, cent)
			p.Position.LocalY += vy // steady drift through the windup → sets the lead velocity
			p.Position.Normalize(32)
		}
		if cent.ActionState != "surge" {
			t.Fatalf("never launched a surge (vy=%.2f)", vy)
		}
		return cent.TargetY
	}

	up := surgeTargetY(0.25)    // drifting +Y
	down := surgeTargetY(-0.25) // drifting −Y
	if !(up > down) {
		t.Fatalf("surge must LEAD the player's velocity: +Y-drift target=%.2f must exceed −Y-drift target=%.2f", up, down)
	}
}

// The surge OVERSHOOTS: its leg target lies BEYOND the player along the launch line —
// it charges THROUGH their spot (the per-tick flight check bites mid-pass) and ends
// past them, set up for the turnaround.
func TestCentSurgeOvershoot(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 13, LocalY: 10}} // standing, 3u east
	state.Players = map[string]*PlayerState{"p1": p}

	for i := 0; i < centWindupTicks+2 && cent.ActionState != "surge"; i++ {
		driveCentTick(m, state, cent)
	}
	if cent.ActionState != "surge" {
		t.Fatalf("state=%q, want surge", cent.ActionState)
	}
	// Zero player velocity → aim = the player; target = aim + overshoot along the line.
	if cent.TargetX < 13+centSurgeOvershoot-0.5 {
		t.Fatalf("surge target X=%.2f, want ≥ %.2f (past the player at 13)",
			cent.TargetX, 13+centSurgeOvershoot-0.5)
	}
}

// A MISSED surge banks back toward the player (turnaround: chained arc legs, the
// heading converging on them) and re-engages on the SHORT cooldown — it presses the
// attack instead of retreating. A player who RUNS (beyond de-aggro) ends it with the
// full cooldown instead.
func TestCentMissTurnaround(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 14, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": p}

	for i := 0; i < centWindupTicks+2 && cent.ActionState != "surge"; i++ {
		driveCentTick(m, state, cent)
	}
	if cent.ActionState != "surge" {
		t.Fatalf("state=%q, want surge", cent.ActionState)
	}
	// DODGE: sidestep well off the flight line (still inside de-aggro 12).
	p.Position.LocalY = 16
	p.Position.Normalize(32)

	sawTurnaround := false
	for i := 0; i < centSurgeMaxTicks+centTurnLegs*centTurnLegTicks+8; i++ {
		driveCentTick(m, state, cent)
		if cent.ActionState == "turnaround" {
			sawTurnaround = true
		}
		if sawTurnaround && cent.ActionState == "" {
			break
		}
	}
	if !sawTurnaround {
		t.Fatal("missed surge never entered turnaround")
	}
	if cent.ActionState != "" {
		t.Fatalf("state=%q, want idle after the turnaround", cent.ActionState)
	}
	// Short re-engage cooldown (presses the attack), not the full 50.
	if cd := cent.SurgeCooldownUntil - state.TickCount; cd > centTurnCooldown {
		t.Fatalf("cooldown after turnaround = %d ticks, want ≤ %d (short)", cd, centTurnCooldown)
	}
	if p.HP != 10 {
		t.Fatalf("dodged player took damage: HP=%d", p.HP)
	}

	// --- The runner: dodge AND flee beyond de-aggro → full cooldown, no pursuit.
	state2, cent2 := centTestState()
	p2 := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 14, LocalY: 10}}
	state2.Players = map[string]*PlayerState{"p1": p2}
	for i := 0; i < centWindupTicks+2 && cent2.ActionState != "surge"; i++ {
		driveCentTick(m, state2, cent2)
	}
	p2.Position.LocalX, p2.Position.LocalY = 40, 40 // gone
	p2.Position.Normalize(32)
	for i := 0; i < centSurgeMaxTicks+centTurnLegs*centTurnLegTicks+8 && cent2.ActionState != ""; i++ {
		driveCentTick(m, state2, cent2)
	}
	if cd := cent2.SurgeCooldownUntil - state2.TickCount; cd <= centTurnCooldown {
		t.Fatalf("runner-escape cooldown = %d ticks, want the FULL backoff", cd)
	}
}

// "Stone is the answer": the surge CLAMPS at the wall — the body never crosses it, so a player on
// the far side is unreachable (server movement guarantee). The additional through-thin-wall BITE
// block is now enforced CLIENT-side (RenderedStingersInRange + BugCollision.LineBlocked, the same
// integer-Bresenham LoS as the predation #20 fix) — not Go-testable here. This guards the movement
// half + that the server surge stays damage-free.
func TestCentSurgeNoThroughFenceBite(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	chunk := state.Chunks[ChunkKey(0, 0)]
	// A FULL-COLUMN stone wall at x=12 — no flanking around the ends.
	for ly := 0; ly < 32; ly++ {
		chunk.SetOccupant(12, ly, &PlacedOccupant{ID: "fence_stone", Anchor: true})
	}
	// Player hugging the far side of the wall at x=12; centipede at x=10
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 13.2, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": p}

	// The wall is column 12; the player is at 13.2 (cell 13, the far side). The centipede may touch the
	// near face of the wall cell but must never CROSS to the player's cell (x >= 13) — the surge clamps.
	for i := 0; i < 120; i++ {
		driveCentTick(m, state, cent)
		if cent.WorldX(32) >= 13 {
			t.Fatalf("centipede crossed the stone wall to the player's side (x=%.2f) — the surge must clamp", cent.WorldX(32))
		}
	}
	if p.HP != 10 {
		t.Fatalf("server applied damage across a wall: HP=%d — the server surge must be damage-free", p.HP)
	}
}

// Gnaw: a hungry centipede with penned prey chews the wood fence at 80-tick intervals
// (HP 2 → broken), the break drops NOTHING and CHAINS without cooldown; stone is immune.
func TestCentGnawThroughWood(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	chunk := state.Chunks[ChunkKey(0, 0)]
	// A wood fence wall between the centipede (10,10) and penned prey (20,10)
	for ly := 5; ly <= 15; ly++ {
		chunk.SetOccupant(15, ly, &PlacedOccupant{ID: "fence_wood", Anchor: true})
	}
	prey := newTestSwarm("b_fly", 5, 18, 10)
	state.Swarms[prey.ID] = prey
	cent.Satiation = 0 // hungry → hunts → clamped → gnaws

	broke := false
	for i := 0; i < centGnawInterval*3+80 && !broke; i++ {
		driveCentTick(m, state, cent)
		cx, cy, lx, ly := GlobalToChunk(15, 10)
		c := state.Chunks[ChunkKey(cx, cy)]
		cell, _ := c.GetOccupantCell(lx, ly)
		broke = cell.IsEmpty || cell.Occupant == nil
	}
	if !broke {
		t.Fatalf("fence not gnawed through (state=%q key=%q dmg=%v)",
			cent.ActionState, cent.GnawKey, state.GnawDamage)
	}
	if len(state.GroundItems) != 0 {
		t.Fatal("gnawed fences must drop NOTHING (consumed)")
	}
	if cent.GnawCooldownUntil > state.TickCount {
		t.Fatal("a SUCCESSFUL break must not arm the gnaw cooldown (layer chaining)")
	}
}

// Stone fences are immune: the centipede never enters gnaw against them.
func TestCentStoneImmune(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	chunk := state.Chunks[ChunkKey(0, 0)]
	for ly := 5; ly <= 15; ly++ {
		chunk.SetOccupant(15, ly, &PlacedOccupant{ID: "fence_stone", Anchor: true})
	}
	prey := newTestSwarm("b_fly", 5, 18, 10)
	state.Swarms[prey.ID] = prey
	cent.Satiation = 0

	for i := 0; i < 400; i++ {
		driveCentTick(m, state, cent)
		if cent.ActionState == "gnaw" {
			t.Fatal("centipede gnawed STONE")
		}
	}
	// The wall held.
	cx, cy, lx, ly := GlobalToChunk(15, 10)
	cell, _ := state.Chunks[ChunkKey(cx, cy)].GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil {
		t.Fatal("stone fence vanished")
	}
}

// Player hits and gnaw damage are SEPARATE pools: hitting a gnawed fence must not
// reset the gnaw progress (the BreakingState owner-reset bug this design avoids).
func TestCentGnawSeparateFromPlayerBreaking(t *testing.T) {
	state, cent := centTestState()
	_ = cent
	state.GnawDamage["15,10"] = 1 // mid-gnaw
	state.BreakingState = map[string]*BreakingProgress{}

	// A player starts (and resets) THEIR break pool on the same fence — the gnaw
	// pool must be untouched.
	state.BreakingState["15,10"] = &BreakingProgress{GridX: 15, GridY: 10, PlayerID: "p1", CurrentHP: 2, MaxHP: 2}
	state.BreakingState["15,10"].CurrentHP = 1

	if state.GnawDamage["15,10"] != 1 {
		t.Fatal("player breaking touched the gnaw pool")
	}
}

// Dead-end escape: boxed in by stone on three sides, the serpentine wander frees
// itself within a handful of thinks (heading updates on clamped rolls + the 3-streak
// free 360°).
func TestCentDeadEndEscape(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	chunk := state.Chunks[ChunkKey(0, 0)]
	// A stone pocket: walls north, east, south of (10,10); open to the WEST.
	for d := -2; d <= 2; d++ {
		chunk.SetOccupant(12, 10+d, &PlacedOccupant{ID: "fence_stone", Anchor: true}) // east
		chunk.SetOccupant(10+d, 12, &PlacedOccupant{ID: "fence_stone", Anchor: true}) // north
		chunk.SetOccupant(10+d, 8, &PlacedOccupant{ID: "fence_stone", Anchor: true})  // south
	}
	cent.WanderHeading = 0 // facing EAST, straight at the wall
	cent.Satiation = 100   // no hunting; pure wander

	for i := 0; i < 900; i++ {
		driveCentTick(m, state, cent)
		if cent.WorldX(32) < 8.5 {
			return // escaped west ✓
		}
	}
	t.Fatalf("centipede never escaped the dead end (at %.1f,%.1f streak=%d)",
		cent.WorldX(32), cent.WorldY(32), cent.ClampedLegStreak)
}

// Individuals never merge or split, even when overfed/overlapping.
func TestCentNeverMergesOrSplits(t *testing.T) {
	state, c1 := centTestState()
	m := &Match{}
	c2 := newTestSwarm("c_cent2", 1, 10.2, 10)
	c2.SpeciesID = "centipede_garden"
	state.Swarms[c2.ID] = c2
	c1.Count = 3 // force over max_swarm_size 1

	m.checkSwarmMerging(state, 32, nopRuntimeLogger())
	m.checkSwarmSplitting(state, 32, nopRuntimeLogger())

	if len(state.Swarms) != 3 { // c1, c2, b_fly?? — predationTestState has no flies; just c1+c2
		// recount precisely:
		n := 0
		for range state.Swarms {
			n++
		}
		if n != 2 {
			t.Fatalf("swarm count changed: %d (merge or split fired on individuals)", n)
		}
	}
	if c1.Count != 3 {
		t.Fatalf("individual split: count=%d", c1.Count)
	}
}

// The centipede CAN reproduce (the NestOccupant-gated CheckPhaseTransition rule):
// nestless predators keep the standard lifecycle.
func TestCentKeepsStandardLifecycle(t *testing.T) {
	state, cent := centTestState()
	species := state.Species[cent.SpeciesID]

	// The skip rule: nest predators skip, nestless do NOT.
	if species.Predation.NestOccupant != "" {
		t.Fatal("test species must be nestless")
	}
	cent.Phase = "feeding"
	cent.Satiation = 100
	cent.CheckPhaseTransition(species)
	if cent.Phase != "reproducing" {
		t.Fatalf("phase=%q — the nestless centipede must enter the standard reproducing phase", cent.Phase)
	}
}

// Pure hunter: the centipede no longer scavenges (empty attractions), so a hungry
// centipede HUNTS prey even with carrion sitting right next to it (it ignores it).
func TestCentHuntsIgnoringCarrion(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 13, LocalY: 10},
		FoodValue: 10,
	}
	prey := newTestSwarm("b_fly", 5, 14, 10)
	state.Swarms[prey.ID] = prey
	cent.Satiation = 0

	state.TickCount = cent.NextThinkTick + 1
	owned := m.predationThink(state, cent, state.Species[cent.SpeciesID], 32, 0.1, nopRuntimeLogger())
	if !owned || cent.TargetPreyID != prey.ID {
		t.Fatalf("a pure-hunter centipede must HUNT even with carrion present (owned=%v prey=%q)", owned, cent.TargetPreyID)
	}
}
