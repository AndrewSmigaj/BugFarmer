package world

// Tests for THE CONDITION/SUBDUAL SYSTEM (§C — condition.go + the three aggression funnels +
// the catch gate + the smoker/consumable delivery paths).
//
// Run inside the builder image:  go test ./modules/world/ -run 'Condition|Calm|Smoker|Consumable' -v

import (
	"testing"

	"bugfarmer/entities"
)

// --- the meter itself ---

func TestConditionApplyMaxAndImmunity(t *testing.T) {
	sp := &entities.BugSpecies{ID: "wasp_common", ConditionTools: map[string]float32{"calm": 85}}
	sw := newTestSwarm("s1", 5, 10, 10)

	// Apply = max(current, fill): fills to 85, re-applying does NOT stack past it.
	if !applyConditionEffect(sw, sp, "calm", 1.0) || sw.ConditionValue != 85 {
		t.Fatalf("fill: got %v, want 85", sw.ConditionValue)
	}
	applyConditionEffect(sw, sp, "calm", 1.0)
	if sw.ConditionValue != 85 {
		t.Fatalf("re-apply stacked: %v", sw.ConditionValue)
	}
	// A weaker application never LOWERS the meter.
	sw2 := newTestSwarm("s2", 5, 10, 10)
	sw2.ConditionValue = 95
	applyConditionEffect(sw2, sp, "calm", 1.0)
	if sw2.ConditionValue != 95 {
		t.Fatalf("weaker apply lowered the meter: %v", sw2.ConditionValue)
	}
	// effect_power scales the fill, capped at 100.
	sw3 := newTestSwarm("s3", 5, 10, 10)
	applyConditionEffect(sw3, sp, "calm", 1.5)
	if sw3.ConditionValue != 100 {
		t.Fatalf("power-scaled fill: got %v, want capped 100", sw3.ConditionValue)
	}
	// NO key = IMMUNE (the map keeps its opt-in meaning — no code default).
	immune := &entities.BugSpecies{ID: "stoic_bug", ConditionTools: map[string]float32{}}
	sw4 := newTestSwarm("s4", 5, 10, 10)
	if applyConditionEffect(sw4, immune, "calm", 1.0) || sw4.ConditionValue != 0 {
		t.Fatalf("no-key species must be unaffected: %v", sw4.ConditionValue)
	}
	// Unknown effect on a calm-only species: nothing.
	if applyConditionEffect(sw, sp, "chill", 1.0) {
		t.Fatal("unknown effect must do nothing")
	}
}

func TestConditionDecayExpiry(t *testing.T) {
	sp := &entities.BugSpecies{ID: "wasp_common", ConditionTools: map[string]float32{"calm": 85}}
	sw := newTestSwarm("s1", 5, 10, 10)
	applyConditionEffect(sw, sp, "calm", 1.0)

	// Default decay 2/s, default threshold 40: subdued for (85-40)/2 = 22.5s.
	ticksSubdued := 0
	for i := 0; i < 300; i++ { // 30s of 0.1s ticks
		if swarmSubdued(sw, sp) {
			ticksSubdued++
		}
		decayCondition(sw, sp, 0.1)
	}
	if ticksSubdued < 220 || ticksSubdued > 230 {
		t.Fatalf("subdued for %d ticks, want ~225 (22.5s at 10Hz)", ticksSubdued)
	}
	if sw.ConditionValue != 0 {
		// 30s × 2/s = 60 drained from 85 → 25 left. Drain the rest and check the floor.
		for i := 0; i < 200; i++ {
			decayCondition(sw, sp, 0.1)
		}
		if sw.ConditionValue != 0 {
			t.Fatalf("meter must floor at 0, got %v", sw.ConditionValue)
		}
	}
}

// --- funnel 1: the ambient contact sting ---

func TestCalmSuppressesAmbientSting(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := state.Species["wasp_common"]
	wasp.AttackDamage = 1
	wasp.AttackCooldown = 0.1
	wasp.ConditionTools = map[string]float32{"calm": 85}

	sw := newTestSwarm("w1", 5, 10, 10)
	sw.SpeciesID = "wasp_common"
	state.Swarms[sw.ID] = sw
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 10.5, LocalY: 10}} // inside stingRange
	state.Players = map[string]*PlayerState{"p1": p}
	state.TickCount = 1000

	// Subdued: standing IN the swarm draws no sting.
	applyConditionEffect(sw, wasp, "calm", 1.0)
	m.checkBugAttacks(nopRuntimeLogger(), nopDispatcher{}, state, sw, wasp, 32)
	if p.HP != 10 {
		t.Fatalf("subdued wasp stung: HP=%d", p.HP)
	}
	// Meter drained below threshold: the sting is back.
	sw.ConditionValue = conditionDefaultThreshold - 1
	state.TickCount += 100 // clear cooldown/invuln windows
	m.checkBugAttacks(nopRuntimeLogger(), nopDispatcher{}, state, sw, wasp, 32)
	if p.HP != 9 {
		t.Fatalf("agitated wasp must sting: HP=%d", p.HP)
	}
}

// A peaceful OBSERVATION zone (the peace toggle) suppresses ALL bug→player attacks: a wasp standing
// on the player draws no sting; flipping peaceful off, the sting is back. (bugAttackAllowed gate.)
func TestPeacefulZoneSuppressesSting(t *testing.T) {
	state := predationTestState()
	state.CurrentZone = &ZoneConfig{ZoneID: "arena", Peaceful: true}
	m := &Match{}
	wasp := state.Species["wasp_common"]
	wasp.AttackDamage = 1
	wasp.AttackCooldown = 0.1

	sw := newTestSwarm("w1", 5, 10, 10)
	sw.SpeciesID = "wasp_common"
	state.Swarms[sw.ID] = sw
	p := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 10.5, LocalY: 10}} // inside stingRange
	state.Players = map[string]*PlayerState{"p1": p}
	state.TickCount = 1000

	// Peaceful: standing IN the swarm draws no sting.
	m.checkBugAttacks(nopRuntimeLogger(), nopDispatcher{}, state, sw, wasp, 32)
	if p.HP != 10 {
		t.Fatalf("peaceful-zone wasp stung: HP=%d", p.HP)
	}
	// Peace off: the sting returns.
	state.CurrentZone.Peaceful = false
	state.TickCount += 100 // clear cooldown/invuln windows
	m.checkBugAttacks(nopRuntimeLogger(), nopDispatcher{}, state, sw, wasp, 32)
	if p.HP != 9 {
		t.Fatalf("non-peaceful wasp must sting: HP=%d", p.HP)
	}
}

// --- funnel 2: the centipede action machine ---

func TestCalmCentipedeNoWindupStart(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	species := state.Species["centipede_garden"]
	species.ConditionTools = map[string]float32{"calm": 90}
	state.Players = map[string]*PlayerState{
		"p1": {UserID: "p1", HP: 10, MaxHP: 10, Position: entities.EntityPosition{LocalX: 13, LocalY: 10}},
	}
	applyConditionEffect(cent, species, "calm", 1.0)

	driveCentTick(m, state, cent)
	if cent.ActionState == "windup" {
		t.Fatal("a subdued centipede must not START a windup — the walk-past play")
	}
}

func TestCalmCentipedeAbortsWindupAndSurge(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	species := state.Species["centipede_garden"]
	species.ConditionTools = map[string]float32{"calm": 90}
	state.Players = map[string]*PlayerState{
		"p1": {UserID: "p1", HP: 10, MaxHP: 10, Position: entities.EntityPosition{LocalX: 13, LocalY: 10}},
	}

	// Enter windup agitated…
	driveCentTick(m, state, cent)
	if cent.ActionState != "windup" {
		t.Fatalf("setup: state=%q, want windup", cent.ActionState)
	}
	// …then the smoke lands mid-windup: the lunge dissolves into recover.
	applyConditionEffect(cent, species, "calm", 1.0)
	driveCentTick(m, state, cent)
	if cent.ActionState != "recover" || cent.WindupTargetID != "" {
		t.Fatalf("windup abort: state=%q target=%q, want recover/\"\"", cent.ActionState, cent.WindupTargetID)
	}

	// Same for a surge in flight.
	cent2 := newTestSwarm("c_cent2", 1, 20, 20)
	cent2.SpeciesID = "centipede_garden"
	state.Swarms[cent2.ID] = cent2
	cent2.ActionState = "surge"
	cent2.ActionUntilTick = state.TickCount + 100
	applyConditionEffect(cent2, species, "calm", 1.0)
	m.processActionState(nopRuntimeLogger(), nil, state, cent2, species, 32, 0.1)
	if cent2.ActionState != "recover" {
		t.Fatalf("surge abort: state=%q, want recover", cent2.ActionState)
	}
}

func TestCalmCentipedeGnawChokeAndMidGnawStop(t *testing.T) {
	state, cent := centTestState()
	m := &Match{}
	species := state.Species["centipede_garden"]
	species.ConditionTools = map[string]float32{"calm": 90}
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.SetOccupant(15, 10, &PlacedOccupant{ID: "fence_wood", Anchor: true})

	// Choke: a subdued centipede refuses to START a gnaw.
	applyConditionEffect(cent, species, "calm", 1.0)
	if m.tryStartGnaw(state, cent, species, 15, 10, 32, 0.1) {
		t.Fatal("subdued centipede must not start a gnaw")
	}

	// Mid-gnaw: start agitated, smoke lands, the chewing STOPS — damage kept, NO cooldown.
	cent.ConditionValue = 0
	if !m.tryStartGnaw(state, cent, species, 15, 10, 32, 0.1) {
		t.Fatal("setup: gnaw must start while agitated")
	}
	state.GnawDamage["15,10"] = 1 // half-chewed
	applyConditionEffect(cent, species, "calm", 1.0)
	m.processGnaw(nopRuntimeLogger(), nil, state, cent, species, 32)
	if cent.ActionState == "gnaw" {
		t.Fatal("smoke must stop an in-progress gnaw")
	}
	if state.GnawDamage["15,10"] != 1 {
		t.Fatal("gnaw damage must be KEPT (calming is not a repair)")
	}
	if cent.GnawCooldownUntil > state.TickCount {
		t.Fatal("calming is not an abandon — no gnaw cooldown")
	}
}

// --- funnel 3: nest defense (the precedence rule at all three entries) ---

func TestCalmNestDefensePrecedence(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	_, resident := initTestNest(m, state)
	species := state.Species["wasp_common"]
	species.ConditionTools = map[string]float32{"calm": 85}
	nest := state.NestStates["10,10"]

	state.Players = map[string]*PlayerState{
		"p1": {UserID: "p1", Position: entities.EntityPosition{LocalX: 12, LocalY: 10}},
	}

	// Entry 1 — recall: a SUBDUED resident ignores a nest hit.
	applyConditionEffect(resident, species, "calm", 1.0)
	m.recallNestDefenders(state, 10, 10, "p1")
	if resident.Phase == "defending" {
		t.Fatal("recall must be suppressed while the resident is subdued")
	}

	// Entry 2 — passive proximity: a player loitering at the nest draws nothing while subdued.
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.Phase == "defending" {
		t.Fatal("passive defend entry must be suppressed while the resident is subdued")
	}

	// Entry 3 — exit hysteresis: an anger already in flight ENDS when the calm lands.
	resident.ConditionValue = 0
	m.recallNestDefenders(state, 10, 10, "p1")
	if resident.Phase != "defending" {
		t.Fatal("setup: agitated recall must work")
	}
	applyConditionEffect(resident, species, "calm", 1.0)
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.Phase == "defending" {
		t.Fatal("in-flight defense must exit when the resident is calmed")
	}

	// The OTHER half of the rule: nest SMOKED suppresses even an agitated resident.
	resident.ConditionValue = 0
	resident.Phase = "feeding"
	nest.SmokedUntilTick = state.TickCount + 300
	m.recallNestDefenders(state, 10, 10, "p1")
	if resident.Phase == "defending" {
		t.Fatal("recall must be suppressed while the nest is smoked")
	}
}

// --- the catch gate (§7.3) ---

func TestCatchCalmGate(t *testing.T) {
	state := combatTestState()
	m := &Match{}
	state.Species["bee_test"] = &entities.BugSpecies{
		ID: "bee_test", Category: "swarm", NetSize: "small",
		CatchCondition: "calm", ConditionThreshold: 40,
		ConditionTools: map[string]float32{"calm": 95},
		MinSwarmSize:   1, MaxSwarmSize: 20,
	}
	player := testPlayer(10, 10, "small_net")
	state.Players["p1"] = player
	sw := newTestSwarm("b1", 10, 11, 10)
	sw.SpeciesID = "bee_test"
	state.Swarms["b1"] = sw

	msg := CatchBugMessage{ClickX: 11, ClickY: 10, SwarmID: "b1", BugIDs: idRange(5)}

	// Agitated: rejected, nothing caught.
	state.TickCount = 100
	m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if sw.Count != 10 {
		t.Fatalf("agitated catch must be rejected: count=%d, want 10", sw.Count)
	}

	// Subdued at/above the SAME threshold behavior uses: catch succeeds.
	applyConditionEffect(sw, state.Species["bee_test"], "calm", 1.0)
	state.TickCount = 200 // clear the per-swing rate limit
	m.handleCatchBug(nopRuntimeLogger(), nopDispatcher{}, state, msg, "p1", 32)
	if sw.Count != 5 {
		t.Fatalf("calm catch must succeed: count=%d, want 5", sw.Count)
	}
}

// --- delivery: the generalized smoker + the consumable verb ---

func TestSmokerCalmsSwarmsAndSmokesNests(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	_, resident := initTestNest(m, state)
	species := state.Species["wasp_common"]
	species.ConditionTools = map[string]float32{"calm": 85}
	nest := state.NestStates["10,10"]

	state.Entities["smoker"] = &EntityDef{Category: "tool", ToolType: "smoker", Effect: "calm", EffectPower: 1.0}
	player := &PlayerState{UserID: "p1", EquippedTool: "smoker",
		Position: entities.EntityPosition{LocalX: 11, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": player}
	state.TickCount = 1000
	resident.Position = entities.EntityPosition{LocalX: 12, LocalY: 10} // in the puff

	m.handleSmoker(nopRuntimeLogger(), nopDispatcher{}, state, "p1", 11, 10, state.TickCount)

	if resident.ConditionValue != 85 {
		t.Fatalf("puffed swarm ConditionValue=%v, want 85 (the GENERAL fill, not bee-only)", resident.ConditionValue)
	}
	if nest.SmokedUntilTick != state.TickCount+smokerCalmTicks {
		t.Fatalf("nest not smoke-stamped: %d", nest.SmokedUntilTick)
	}
}

func TestConsumableAppliesAndConsumes(t *testing.T) {
	state := predationTestState()
	m := &Match{}
	wasp := state.Species["wasp_common"]
	wasp.ConditionTools = map[string]float32{"calm": 85}

	sprayDef := &EntityDef{Category: "consumable", Effect: "calm", Reach: 3.0}
	state.Entities["calm_spray"] = sprayDef
	player := &PlayerState{UserID: "p1", EquippedTool: "calm_spray",
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10}}
	slot := player.AddItem("calm_spray", 2)
	state.Players = map[string]*PlayerState{"p1": player}
	state.TickCount = 1000

	sw := newTestSwarm("w1", 5, 11, 10)
	sw.SpeciesID = "wasp_common"
	state.Swarms[sw.ID] = sw

	// Hit: effect applied + ONE consumed.
	m.handleConsumableUse(nopRuntimeLogger(), nopDispatcher{}, state, "p1", "calm_spray", sprayDef, 11, 10, state.TickCount)
	if sw.ConditionValue != 85 {
		t.Fatalf("spray fill: got %v, want 85", sw.ConditionValue)
	}
	if player.ItemSlots[slot].Count != 1 {
		t.Fatalf("spray must consume one: count=%d, want 1", player.ItemSlots[slot].Count)
	}

	// Miss (nothing in radius): NOT consumed.
	sw.Position = entities.EntityPosition{LocalX: 30, LocalY: 30}
	state.TickCount += 100
	m.handleConsumableUse(nopRuntimeLogger(), nopDispatcher{}, state, "p1", "calm_spray", sprayDef, 11, 10, state.TickCount)
	if player.ItemSlots[slot].Count != 1 {
		t.Fatalf("a miss must cost nothing: count=%d, want 1", player.ItemSlots[slot].Count)
	}
}
