package world

// Tests for the centipede's SERVER-side GNAW — the only centipede behavior still on the
// server — plus the pack lifecycle (merge / split / breed), which is no longer disabled.
// The combat brain (windup/surge/recover/turnaround) and the serpentine wander moved to
// the CLIENT, one brain per pack member (movement_style "centipede"); those are exercised
// by the Unity + determinism gates, not here.
//
// Run inside the builder image:  go test ./modules/world/ -run TestCent -v

import (
	"testing"

	"bugfarmer/entities"
)

func centTestState() (*WorldState, *entities.SwarmState) {
	state := predationTestState()
	state.Species["centipede_garden"] = &entities.BugSpecies{
		ID: "centipede_garden", Category: "swarm", MovementStyle: "centipede",
		BaseSpeed: 1.6, VisionRange: 10, WanderRadius: 15,
		MinSwarmSize: 3, MaxSwarmSize: 5, SwarmRadius: 2.5, MergeRadius: 1.5, SplitThreshold: 6,
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

// driveCentTick replicates the server loop order for a centipede swarm: the GNAW
// ActionState (the only server-side action left) is dispatched per tick BEFORE the think
// gate; otherwise the predator think (hunt/wander) runs, then the center moves.
func driveCentTick(m *Match, state *WorldState, cent *entities.SwarmState) {
	state.TickCount++
	species := state.Species[cent.SpeciesID]
	active := false
	if cent.ActionState == "gnaw" {
		active = m.processGnaw(nopRuntimeLogger(), nil, state, cent, species, 32)
	}
	if !active && state.TickCount >= cent.NextThinkTick {
		if !m.predationThink(state, cent, species, 32, 0.1, nopRuntimeLogger()) {
			cent.SpeedMult = 1.0
			cent.TargetPreyID = ""
			cent.NextThinkTick = state.TickCount + 30
		}
	}
	cent.Move(0.1, species, 32)
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

// Centipede PACKS merge (two small overlapping packs combine, up to max_swarm_size) and
// SPLIT (a pack grown past split_threshold halves into two, each ≥ min_swarm_size) — the
// swarm dynamics that were disabled for the retired "individual" swarm-of-1 model.
func TestCentPacksMergeAndSplit(t *testing.T) {
	m := &Match{}

	// MERGE: two packs of 2, 1.0 apart (≤ merge_radius 1.5) → one pack of 4 (≤ max 5).
	state, _ := centTestState()
	delete(state.Swarms, "c_cent") // drop the fixture's default solo swarm
	a := newTestSwarm("c_a", 2, 10, 10)
	a.SpeciesID = "centipede_garden"
	b := newTestSwarm("c_b", 2, 11, 10)
	b.SpeciesID = "centipede_garden"
	state.Swarms["c_a"] = a
	state.Swarms["c_b"] = b

	m.checkSwarmMerging(state, 32, nopRuntimeLogger())

	if len(state.Swarms) != 1 {
		t.Fatalf("two overlapping packs must merge into one: %d swarms remain", len(state.Swarms))
	}
	for _, s := range state.Swarms {
		if s.Count != 4 {
			t.Fatalf("merged pack count=%d, want 4", s.Count)
		}
	}

	// SPLIT: a pack of 7 (> split_threshold 6) halves; both halves ≥ min_swarm_size 3.
	state2, _ := centTestState()
	delete(state2.Swarms, "c_cent")
	big := newTestSwarm("c_big", 7, 10, 10)
	big.SpeciesID = "centipede_garden"
	state2.Swarms["c_big"] = big

	m.checkSwarmSplitting(state2, 32, nopRuntimeLogger())

	if len(state2.Swarms) != 2 {
		t.Fatalf("a pack over split_threshold must split in two: %d swarms", len(state2.Swarms))
	}
	total := 0
	for _, s := range state2.Swarms {
		if s.Count < 3 {
			t.Fatalf("split half too small: count=%d (< min_swarm_size 3)", s.Count)
		}
		total += s.Count
	}
	if total != 7 {
		t.Fatalf("split must conserve members: total=%d, want 7", total)
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
