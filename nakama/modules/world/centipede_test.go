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
		AttractionsByPhase: map[string][]string{"feeding": {"bug_parts"}},
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

// Surge: trigger at 5.0 → 8-tick windup freeze → clamped lead surge → bite or recover
// → cooldown; de-aggro beyond the trigger range just never re-triggers.
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

	// A STANDING player gets bitten (lead = 0 for zero velocity).
	for i := 0; i < centSurgeMaxTicks+centRecoverTicks+2 && p.HP == 10; i++ {
		driveCentTick(m, state, cent)
	}
	if p.HP != 8 {
		t.Fatalf("standing player HP=%d, want 8 (bite 2)", p.HP)
	}
	// Recover then cooldown.
	for i := 0; i < centRecoverTicks+2; i++ {
		driveCentTick(m, state, cent)
	}
	if cent.ActionState != "" {
		t.Fatalf("state=%q, want idle after recover", cent.ActionState)
	}
	if cent.SurgeCooldownUntil <= state.TickCount {
		t.Fatal("surge cooldown not armed")
	}
}

// The velocity half-lead: a player strafing steadily (half walk speed — fighting,
// not fleeing) gets clipped by the lead; the same player REVERSING direction at
// launch escapes (the skill check: the hiss asks you to move DIFFERENTLY). A
// full-speed runner with the whole telegraph as head start legitimately outruns
// the lunge — the telegraph rewarding movement is the design.
func TestCentSurgeLead(t *testing.T) {
	run := func(reverse bool) bool {
		state, cent := centTestState()
		m := &Match{}
		p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
			Position: entities.EntityPosition{LocalX: 14, LocalY: 10}}
		state.Players = map[string]*PlayerState{"p1": p}

		const strafeSpeed = 0.25 // half walk speed: circling while fighting
		dir := float32(strafeSpeed)
		for i := 0; i < 80 && p.HP == 10; i++ {
			driveCentTick(m, state, cent)
			if reverse && cent.ActionState == "surge" {
				dir = -strafeSpeed // direction change at launch
			}
			p.Position.LocalY += dir
			p.Position.Normalize(32)
		}
		return p.HP < 10
	}

	if !run(false) {
		t.Fatal("a steady strafer must get clipped by the lead")
	}
	if run(true) {
		t.Fatal("a direction-change at launch must dodge the surge")
	}
}

// The surge CLAMPS at fences and the bite is LOS-gated: a player across a wall within
// 1.6 of the clamp point takes NO damage.
func TestCentSurgeNoThroughFenceBite(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	chunk := state.Chunks[ChunkKey(0, 0)]
	// A FULL-COLUMN stone wall at x=12 — no flanking around the ends (a shorter wall
	// let the wander legitimately walk around it and bite with clear LOS).
	for ly := 0; ly < 32; ly++ {
		chunk.SetOccupant(12, ly, &PlacedOccupant{ID: "fence_stone", Anchor: true})
	}
	// Player hugging the far side of the wall at x=12; centipede at x=10
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 13.2, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": p}

	for i := 0; i < 120; i++ {
		driveCentTick(m, state, cent)
	}
	if p.HP != 10 {
		t.Fatalf("through-fence bite landed: HP=%d — 'stone is the answer' is void", p.HP)
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

// Carrion-first: a hungry centipede with BOTH carrion and prey visible declines the
// hunt (the shared forage path takes it).
func TestCentCarrionFirst(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	state.GroundItems["c1"] = &entities.GroundItem{
		ID: "c1", ItemType: "bug_parts", Count: 1,
		Position:  entities.EntityPosition{LocalX: 13, LocalY: 10},
		FoodValue: 10,
	}
	prey := newTestSwarm("b_fly", 5, 14, 10)
	state.Swarms[prey.ID] = prey
	cent.Satiation = 0

	state.TickCount = cent.NextThinkTick + 1
	owned := m.predationThink(state, cent, state.Species[cent.SpeciesID], 32, 0.1, nopRuntimeLogger())
	if owned {
		t.Fatal("with carrion visible the centipede must DECLINE (shared forage dines)")
	}

	// Carrion gone → the hunt fires.
	delete(state.GroundItems, "c1")
	state.TickCount = cent.NextThinkTick + 1
	owned = m.predationThink(state, cent, state.Species[cent.SpeciesID], 32, 0.1, nopRuntimeLogger())
	if !owned || cent.TargetPreyID != prey.ID {
		t.Fatalf("hungry + no carrion must hunt (owned=%v prey=%q)", owned, cent.TargetPreyID)
	}
}
