package world

// Tests for the ANT server core (underground-arc P3.1): the CARRION-FORAGER food shape.
// Ants are empty-prey nest species (the bee's verbatim trip loop) whose diet is
// attraction-scoped ground food + fungus pools instead of flower nectar. The gates
// under test are exactly the ones the plan's certainty table flagged:
//   - the trip loop (decline → forage → homing → deposit) reused unchanged, no honey
//   - nestCanFeedNearby SCOPING: a flower field must NOT feed an ant colony
//   - the mixed-source gate: carrion items AND fungus pools both count
//   - findNestSiteWithCarrion: daughters found beside the species' OWN food, in-band
//
// Run inside the builder image:  go test ./modules/world/ -run 'Ant' -v

import (
	"testing"

	"bugfarmer/entities"
)

func antTestState() (*WorldState, *entities.BugSpecies) {
	state := predationTestState()
	ant := &entities.BugSpecies{
		ID: "ant_worker", Category: "swarm",
		BaseSpeed: 1.2, VisionRange: 10, WanderRadius: 8,
		MinSwarmSize: 2, MaxSwarmSize: 5,
		AttackDamage: 1, AttackCooldown: 2.0,
		StingsOnlyDefending: true,
		CarrionForager:      true,
		AttractionsByPhase: map[string][]string{
			"feeding": {"dead_fly", "rotten_fruit", "mushroom_cluster"},
		},
		Predation: &entities.PredationConfig{
			Prey: []string{}, HomeRange: 40,
			DepositSatiation: 80, HuntSatiationThreshold: 45,
			NestOccupant: "ant_brood",
		},
	}
	state.Species["ant_worker"] = ant
	state.SwarmsBySpecies["ant_worker"] = []string{}
	state.Entities["ant_brood"] = &EntityDef{World: &WorldData{
		Breakable: &BreakableData{HP: 2, RequiredToolType: "shovel"},
	}}
	state.Entities["mushroom_cluster"] = &EntityDef{World: &WorldData{Nectar: true}}
	return state, ant
}

// The bee trip loop, reused verbatim by the ant shape: hungry → DECLINE ownership
// (phase-normalized, attractions resolvable — the starve-sawtooth guard), full →
// homing, arrival → deposit banks brood, and NO honey (ant_brood carries no Hive data).
func TestAntForageTripLoop(t *testing.T) {
	state, ant := antTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "ant_brood", "ant_worker", ant, false, nopRuntimeLogger())
	resident := state.Swarms[nest.ResidentSwarmID]
	if resident == nil {
		t.Fatal("an ant_brood pile must auto-found a resident patrol")
	}

	resident.Satiation = 50
	resident.Phase = ""
	state.TickCount = resident.NextThinkTick + 1
	if m.predationThink(state, resident, ant, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("a hungry prey-less ant must decline ownership (forage on carrion/fungus)")
	}
	if resident.Phase != "feeding" {
		t.Fatalf("decline must normalize Phase: got %q, want feeding", resident.Phase)
	}
	if attractions := resident.GetCurrentAttractions(ant); len(attractions) == 0 {
		t.Fatal("post-decline the ant must resolve its feeding attractions")
	}

	resident.Satiation = 92
	resident.Position = entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 25, LocalY: 10}
	state.TickCount = resident.NextThinkTick + 1
	if !m.predationThink(state, resident, ant, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("a full ant far from the brood must own the beat (homing)")
	}
	if resident.Phase != "homing" || !resident.CarryingBrood {
		t.Fatalf("phase=%q carrying=%v, want homing/true", resident.Phase, resident.CarryingBrood)
	}

	resident.Position = entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 10.5, LocalY: 11.5}
	state.TickCount = resident.NextThinkTick + 1
	if m.predationThink(state, resident, ant, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("the deposit beat must fall through to the shared forage block")
	}
	if nest.Brood != 1 {
		t.Fatalf("deposit must bank brood: %d, want 1", nest.Brood)
	}
	if nest.Honey != 0 {
		t.Fatalf("an ant brood pile must make NO honey: got %v", nest.Honey)
	}
	if resident.Satiation != ant.Predation.DepositSatiation {
		t.Fatalf("post-deposit satiation=%v, want %v", resident.Satiation, ant.Predation.DepositSatiation)
	}
}

// THE SCOPING GATE (the reason nestHasCarrionFoodNearby exists): a rich FLOWER field in
// home range must NOT feed an ant colony — the stock nectar gate counts ALL pools and
// would wrongly qualify it. Then each of the ant's OWN foods flips the gate true:
// a fungus pool (occupant + pool + attraction), and a carrion ground item.
func TestAntNestFoodGateScoping(t *testing.T) {
	state, ant := antTestState()
	m := &Match{}
	nest := m.registerNestAt(state, 10, 10, "ant_brood", "ant_worker", ant, false, nopRuntimeLogger())

	// 1) Nothing edible → false.
	if m.nestCanFeedNearby(state, nest, ant) {
		t.Fatal("an empty larder must not feed the colony")
	}

	// 2) A rich FLOWER pool in range → still false (flower_wild is not in ant attractions).
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.SetOccupant(14, 10, &PlacedOccupant{ID: "flower_wild", Anchor: true})
	state.ForagePools["14,10"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 14, GridY: 10, Nectar: 80}
	if m.nestCanFeedNearby(state, nest, ant) {
		t.Fatal("a FLOWER field must not feed an ant colony (attraction scoping)")
	}

	// 3) A stocked FUNGUS pool (occupant + pool, in attractions) → true.
	chunk.SetOccupant(16, 10, &PlacedOccupant{ID: "mushroom_cluster", Anchor: true})
	state.ForagePools["16,10"] = &entities.ForagePoolState{EntityID: "mushroom_cluster", GridX: 16, GridY: 10, Nectar: 50}
	if !m.nestCanFeedNearby(state, nest, ant) {
		t.Fatal("a stocked fungus pool in home range must feed the colony")
	}

	// 3b) ...and a GRAZED-OUT fungus pool must not (depletion awareness).
	state.ForagePools["16,10"].Nectar = 0
	if m.nestCanFeedNearby(state, nest, ant) {
		t.Fatal("a grazed-out fungus pool must not count as food")
	}

	// 4) A carrion ground item alone → true (the mixed-source half of the gate).
	state.putGroundItem(&entities.GroundItem{
		ID: "c1", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 18, LocalY: 10},
		FoodValue: 10,
	})
	if !m.nestCanFeedNearby(state, nest, ant) {
		t.Fatal("carrion in home range must feed the colony")
	}
}

// Daughter founding: the site lands BESIDE the species' own food, respects the minimum
// spread distance, and WAITS when there is nothing to eat.
func TestAntFoundingSiteBesideFood(t *testing.T) {
	state, ant := antTestState()
	m := &Match{}

	// Nothing anywhere → wait.
	if _, _, ok := m.findNestSiteWithCarrion(state, 10, 10, ant, 5, 40); ok {
		t.Fatal("no food → the colony must WAIT, not found a doomed nest")
	}

	// Carrion too CLOSE (inside minD) → still wait (daughters spread, not stack).
	state.putGroundItem(&entities.GroundItem{
		ID: "near", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 12, LocalY: 10},
		FoodValue: 10,
	})
	if _, _, ok := m.findNestSiteWithCarrion(state, 10, 10, ant, 5, 40); ok {
		t.Fatal("food inside the minimum spread distance must not qualify")
	}

	// Carrion in band → a walkable site beside it.
	state.putGroundItem(&entities.GroundItem{
		ID: "far", ItemType: "dead_fly", Count: 1,
		Position:  entities.EntityPosition{LocalX: 30, LocalY: 10},
		FoodValue: 10,
	})
	gx, gy, ok := m.findNestSiteWithCarrion(state, 10, 10, ant, 5, 40)
	if !ok {
		t.Fatal("in-band carrion must yield a founding site")
	}
	if dx, dy := gx-30, gy-10; dx*dx+dy*dy > 9*9 {
		t.Fatalf("site (%d,%d) must sit beside the food at (30,10)", gx, gy)
	}
}