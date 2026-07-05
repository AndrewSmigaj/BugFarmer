package world

// Tests for the bee server core (A2): the prey-less nest-forager branch (decline-ownership →
// the shared forage block), honey accrual on brood deposits, hand-harvest with the anger/smoke
// loop, dormant player-placed hive boxes + colonization, the sting-immune suit hook, and the
// nectar-gated recovery/founding checks.
//
// Run inside the builder image:  go test ./modules/world/ -run 'Bee|Hive|Suit' -v

import (
	"testing"

	"bugfarmer/entities"
)

func beeTestState() (*WorldState, *entities.BugSpecies) {
	state := predationTestState()
	bee := &entities.BugSpecies{
		ID: "bee_honey", Category: "swarm",
		BaseSpeed: 1.8, VisionRange: 14, WanderRadius: 12,
		MinSwarmSize: 3, MaxSwarmSize: 12,
		AttackDamage: 1, AttackCooldown: 2.0,
		StingsOnlyDefending: true, AttackIsSting: true,
		FliesOverFences: true,
		CatchCondition:  "calm", ConditionThreshold: 40,
		ConditionTools:  map[string]float32{"calm": 95},
		AttractionsByPhase: map[string][]string{"feeding": {"flower_wild"}},
		Predation: &entities.PredationConfig{
			Prey: []string{}, HomeRange: 40,
			DepositSatiation: 80, HuntSatiationThreshold: 45,
			NestOccupant:       "bee_hive_wild",
			NestOccupantsExtra: []string{"beehive_basic"},
		},
	}
	state.Species["bee_honey"] = bee
	state.SwarmsBySpecies["bee_honey"] = []string{}
	state.Entities["bee_hive_wild"] = &EntityDef{World: &WorldData{
		Hive:      &HiveData{HoneyCap: 3},
		Breakable: &BreakableData{HP: 4, RequiredToolType: "axe"},
	}}
	state.Entities["beehive_basic"] = &EntityDef{World: &WorldData{
		Hive: &HiveData{HoneyCap: 4},
	}}
	return state, bee
}

// The ONE new sim shape: a hungry prey-less nest species DECLINES predation ownership (the
// centipede carrion-first pattern) so the SHARED forage block dines on nectar; a full load
// (>= 90) preempts into homing and the arrival deposit banks brood AND makes honey.
func TestBeeForageTripLoop(t *testing.T) {
	state, bee := beeTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "bee_hive_wild", "bee_honey", bee, false, nopRuntimeLogger())
	resident := state.Swarms[nest.ResidentSwarmID]
	if resident == nil {
		t.Fatal("wild hive must auto-found a resident")
	}

	// HUNGRY: predationThink must DECLINE (return false) → the shared forage block owns the
	// beat and dines on flowers. A wasp (prey-bearing) in the same state would return true.
	resident.Satiation = 50
	state.TickCount = resident.NextThinkTick + 1
	if m.predationThink(state, resident, bee, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("a hungry prey-less bee must decline ownership (forage on nectar instead)")
	}

	// FULL and FAR from the hive: homing owns the beat (emits the flight leg home).
	resident.Satiation = 92
	resident.Position = entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 25, LocalY: 10}
	state.TickCount = resident.NextThinkTick + 1
	if !m.predationThink(state, resident, bee, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("a full bee far from home must own the beat (homing flight)")
	}
	if resident.Phase != "homing" || !resident.CarryingBrood {
		t.Fatalf("phase=%q carrying=%v, want homing/true", resident.Phase, resident.CarryingBrood)
	}

	// ARRIVED: the deposit beat banks brood +1, makes honey, drops satiation to
	// deposit_satiation — and FALLS THROUGH (returns false) so the same beat resumes
	// foraging. That fall-through IS the trip loop closing.
	resident.Position = entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 10.5, LocalY: 11.5}
	state.TickCount = resident.NextThinkTick + 1
	if m.predationThink(state, resident, bee, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("the deposit beat must fall through to the shared forage block")
	}
	if nest.Brood != 1 {
		t.Fatalf("deposit must bank brood: %d, want 1", nest.Brood)
	}
	if nest.Honey != honeyPerDeposit {
		t.Fatalf("deposit must make honey: %v, want %v", nest.Honey, honeyPerDeposit)
	}
	if resident.Satiation != bee.Predation.DepositSatiation {
		t.Fatalf("post-deposit satiation=%v, want %v", resident.Satiation, bee.Predation.DepositSatiation)
	}
	if resident.Phase != "feeding" || resident.CarryingBrood {
		t.Fatalf("post-deposit phase=%q carrying=%v, want feeding/false", resident.Phase, resident.CarryingBrood)
	}
}

func TestHoneyAccrualCapAndMult(t *testing.T) {
	state, _ := beeTestState()
	m := &Match{}
	sw := newTestSwarm("b1", 5, 10, 10)
	sw.SpeciesID = "bee_honey"
	state.Swarms[sw.ID] = sw

	// Wild hive (cap 3): 0.5/deposit, capped.
	nest := &entities.NestState{GridX: 10, GridY: 10, EntityID: "bee_hive_wild", SpeciesID: "bee_honey"}
	for i := 0; i < 10; i++ {
		m.depositBrood(state, sw, nest, nopRuntimeLogger())
	}
	if nest.Honey != 3 {
		t.Fatalf("honey must cap at the hive's honey_cap: %v, want 3", nest.Honey)
	}

	// Deluxe-style mult: 1.5 × 0.5 = 0.75 per deposit.
	state.Entities["beehive_deluxe"] = &EntityDef{World: &WorldData{Hive: &HiveData{HoneyCap: 10, HoneyMult: 1.5}}}
	deluxe := &entities.NestState{GridX: 20, GridY: 20, EntityID: "beehive_deluxe", SpeciesID: "bee_honey"}
	m.depositBrood(state, sw, deluxe, nopRuntimeLogger())
	if deluxe.Honey != 0.75 {
		t.Fatalf("honey_mult must scale accrual: %v, want 0.75", deluxe.Honey)
	}

	// A wasp nest (no world.hive) makes NO honey.
	state.Entities["wasp_nest_x"] = &EntityDef{World: &WorldData{}}
	waspNest := &entities.NestState{GridX: 30, GridY: 30, EntityID: "wasp_nest_x", SpeciesID: "wasp_common"}
	m.depositBrood(state, sw, waspNest, nopRuntimeLogger())
	if waspNest.Honey != 0 {
		t.Fatalf("a hive-less nest must not accrue honey: %v", waspNest.Honey)
	}
}

// Hand-harvest: whole combs into the bag; poking the hive RECALLS the colony onto you unless
// smoked (the suit stops stings, NOT the anger — that's applyBugAttackToPlayer's job).
func TestHiveHarvestRecallAndSmoke(t *testing.T) {
	state, bee := beeTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "bee_hive_wild", "bee_honey", bee, false, nopRuntimeLogger())
	resident := state.Swarms[nest.ResidentSwarmID]
	nest.Honey = 2.6
	state.TickCount = 1000

	player := &PlayerState{UserID: "p1", Position: entities.EntityPosition{LocalX: 11, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": player}

	m.handleHiveHarvest(nopRuntimeLogger(), nopDispatcher{}, state, "p1", HiveHarvestMessage{GX: 10, GY: 10})

	slot := player.FindItem("honeycomb")
	if slot < 0 || player.ItemSlots[slot].Count != 2 {
		t.Fatalf("harvest must pop floor(2.6)=2 combs, got slot=%d", slot)
	}
	if nest.Honey < 0.59 || nest.Honey > 0.61 {
		t.Fatalf("fractional honey must remain: %v, want 0.6", nest.Honey)
	}
	if resident.Phase != "defending" || resident.DefendTargetID != "p1" {
		t.Fatalf("unsmoked harvest must enrage the colony: phase=%q", resident.Phase)
	}

	// Smoked: the same poke draws nothing.
	resident.Phase = "feeding"
	resident.DefendTargetID = ""
	nest.Honey = 1.0
	nest.SmokedUntilTick = state.TickCount + smokerCalmTicks
	m.handleHiveHarvest(nopRuntimeLogger(), nopDispatcher{}, state, "p1", HiveHarvestMessage{GX: 10, GY: 10})
	if resident.Phase == "defending" {
		t.Fatal("a smoked hive must not recall defenders — the calm harvest window")
	}
	if slot := player.FindItem("honeycomb"); player.ItemSlots[slot].Count != 3 {
		t.Fatalf("smoked harvest still yields: count=%d, want 3", player.ItemSlots[slot].Count)
	}
}

// A player placing a hive box mints NO free bees (dormant registration); a thriving colony
// CLAIMS the box (findClaimableBox → nestSpawnResident) and only then it is Founded.
func TestPlacedBoxDormantThenClaimed(t *testing.T) {
	state, bee := beeTestState()
	m := &Match{}

	box := m.registerNestAt(state, 18, 10, "beehive_basic", "bee_honey", bee, true, nopRuntimeLogger())
	if box.ResidentSwarmID != "" || box.Founded {
		t.Fatalf("a placed box must register DORMANT: resident=%q founded=%v", box.ResidentSwarmID, box.Founded)
	}
	if len(state.Swarms) != 0 {
		t.Fatal("placing a box must not mint bees")
	}

	// A mother colony 8 cells away (inside the 4..NestFoundDistMax claim band) finds the box.
	parent := m.registerNestAt(state, 10, 10, "bee_hive_wild", "bee_honey", bee, false, nopRuntimeLogger())
	key, ok := m.findClaimableBox(state, parent, bee)
	if !ok || key != "18,10" {
		t.Fatalf("claimable box not found: key=%q ok=%v", key, ok)
	}

	// The claim founds it: resident minted at the box, Founded set.
	m.nestSpawnResident(state, box, bee, state.Tuning.NestFoundingSize, nopRuntimeLogger())
	if box.ResidentSwarmID == "" || !box.Founded {
		t.Fatalf("claimed box must be founded: resident=%q founded=%v", box.ResidentSwarmID, box.Founded)
	}
	if sw := state.Swarms[box.ResidentSwarmID]; sw == nil || sw.NestKey != "18,10" {
		t.Fatal("claimed box's resident must be tethered to the box")
	}
}

// The suit: sting-class attacks (bee, wasp with attack_is_sting) are zeroed by a sting_immune
// BODY piece; a centipede BITE (attack_is_sting false) lands regardless.
func TestSuitZeroesStingButNotBite(t *testing.T) {
	state, bee := beeTestState()
	m := &Match{}
	state.Entities["bee_suit"] = &EntityDef{Category: "armor", ArmorSlot: "body", StingImmune: true}

	player := &PlayerState{UserID: "p1", HP: 10, MaxHP: 10,
		Position: entities.EntityPosition{LocalX: 10, LocalY: 10}}
	player.Equipment[1] = "bee_suit" // body slot
	state.Players = map[string]*PlayerState{"p1": player}
	state.TickCount = 1000

	sting := newTestSwarm("b1", 5, 10, 10)
	sting.SpeciesID = "bee_honey"
	state.Swarms[sting.ID] = sting
	if m.applyBugAttackToPlayer(nopRuntimeLogger(), nopDispatcher{}, state, sting, bee, "p1", player, 1) {
		t.Fatal("suited player must shrug off a sting")
	}
	if player.HP != 10 {
		t.Fatalf("sting damage leaked through the suit: HP=%d", player.HP)
	}

	// Centipede bite: NOT a sting — the suit does nothing.
	centSpecies := &entities.BugSpecies{ID: "centipede_garden", AttackDamage: 2, AttackCooldown: 0.1, AttackIsSting: false}
	bite := newTestSwarm("c1", 1, 10, 10)
	bite.SpeciesID = "centipede_garden"
	state.Swarms[bite.ID] = bite
	state.TickCount += 100
	if !m.applyBugAttackToPlayer(nopRuntimeLogger(), nopDispatcher{}, state, bite, centSpecies, "p1", player, 2) {
		t.Fatal("a bite must land through the bee suit")
	}
	if player.HP != 8 {
		t.Fatalf("bite damage wrong: HP=%d, want 8", player.HP)
	}
}

// Recovery/founding food gates are species-shape-aware: a prey-less forager needs LIVE NECTAR
// in home range (a grazed-out field doesn't count); a hunter needs live prey (unchanged).
func TestBeeNestNectarGate(t *testing.T) {
	state, bee := beeTestState()
	m := &Match{}
	nest := &entities.NestState{GridX: 10, GridY: 10, EntityID: "bee_hive_wild", SpeciesID: "bee_honey"}

	if m.nestCanFeedNearby(state, nest, bee) {
		t.Fatal("no flowers → a bee nest cannot feed")
	}
	state.ForagePools["14,10"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 14, GridY: 10, Nectar: 50}
	if !m.nestCanFeedNearby(state, nest, bee) {
		t.Fatal("live nectar in home range → the nest can feed")
	}
	state.ForagePools["14,10"].Nectar = 5 // below the graze floor
	if m.nestCanFeedNearby(state, nest, bee) {
		t.Fatal("a grazed-out field must not count as feedable")
	}

	// findNestSiteWithNectar picks beside the RICHEST field in the band; none → WAIT.
	if _, _, ok := m.findNestSiteWithNectar(state, 10, 10, bee, 4, 30); ok {
		t.Fatal("no adequate field → founding must WAIT")
	}
	state.ForagePools["22,10"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 22, GridY: 10, Nectar: 80}
	gx, gy, ok := m.findNestSiteWithNectar(state, 10, 10, bee, 4, 30)
	if !ok {
		t.Fatal("a rich field in the band must yield a founding site")
	}
	dx, dy := gx-22, gy-10
	if dx*dx+dy*dy > 8*8 {
		t.Fatalf("site (%d,%d) must be beside the rich field (22,10)", gx, gy)
	}
}
