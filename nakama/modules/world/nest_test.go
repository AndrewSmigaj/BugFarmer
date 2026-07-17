package world

// Tests for the wasp-nest brood economy + the wasp phase machine (homing/defending).
//
// Run inside the builder image:  go test ./modules/world/ -run TestNest -v

import (
	"fmt"
	"testing"

	"bugfarmer/entities"
)

// nestTestState: a wasp_nest occupant at (10,10) + the wasp species, chunks open.
func nestTestState() *WorldState {
	state := predationTestState()
	state.Entities["wasp_nest"] = &EntityDef{
		Category: "nature",
		World:    &WorldData{Breakable: &BreakableData{HP: 4, RequiredToolType: "axe", RequiredToolTier: 1}},
	}
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.SetOccupant(10, 10, &PlacedOccupant{ID: "wasp_nest", Anchor: true})
	state.SwarmsBySpecies["wasp_common"] = []string{}
	return state
}

func initTestNest(m *Match, state *WorldState) (*entities.NestState, *entities.SwarmState) {
	m.initNestsInChunk(state, state.Chunks[ChunkKey(0, 0)], 0, 0, nopRuntimeLogger())
	nest := state.NestStates["10,10"]
	if nest == nil {
		return nil, nil
	}
	resident := state.Swarms[nest.ResidentSwarmID]
	return nest, resident
}

// Founding: the chunk scan registers the nest and spawns a cap-aware resident with
// NestKey + HomePos at the nest.
func TestNestFoundsResident(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	if nest == nil || resident == nil {
		t.Fatal("nest/resident not founded")
	}
	if resident.Count != entities.NestFoundingSize || resident.NestKey != "10,10" {
		t.Fatalf("resident count=%d nestKey=%q", resident.Count, resident.NestKey)
	}
	if resident.SpeciesID != "wasp_common" {
		t.Fatalf("resident species=%q", resident.SpeciesID)
	}
}

// The full trip: sated → homing → arrival deposit (+brood, satiation→80, feeding) —
// and hunting resumes only below the hunt threshold (the 125s rest window:
// (80-30)/0.4 per the species numbers).
func TestNestHomingDepositCycle(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	species := state.Species["wasp_common"]

	// Sated far from home → homing legs toward the nest.
	resident.Position = entities.EntityPosition{LocalX: 25, LocalY: 10}
	resident.Satiation = 100
	state.TickCount = resident.NextThinkTick + 1
	if !m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger()) {
		t.Fatal("homing think must own the leg")
	}
	if resident.Phase != "homing" || !resident.CarryingBrood {
		t.Fatalf("phase=%q carrying=%v, want homing/true", resident.Phase, resident.CarryingBrood)
	}
	if resident.TargetX > 25 {
		t.Fatalf("homing leg target x=%.1f, want toward the nest at 10.5", resident.TargetX)
	}

	// Walk it home (drive think+move).
	for i := 0; i < 600 && resident.Phase == "homing"; i++ {
		state.TickCount++
		if state.TickCount >= resident.NextThinkTick {
			m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
		}
		resident.Move(0.1, species, 32)
	}
	if resident.Phase != "feeding" || resident.CarryingBrood {
		t.Fatalf("after arrival: phase=%q carrying=%v", resident.Phase, resident.CarryingBrood)
	}
	if got := m.nestBroodCount(state, nest); got != 1 {
		t.Fatalf("nest brood=%d, want 1 egg laid on the homing deposit", got)
	}
	if resident.Satiation != 80 {
		t.Fatalf("post-deposit satiation=%.0f, want deposit_satiation 80", resident.Satiation)
	}

	// After depositing, satiation drops to deposit_satiation (80) — still BELOW the full-load ceiling
	// (predatorFullSatiation=90), so the forager loop immediately RESUMES hunting (the old rest-at-
	// HuntSatiationThreshold dead zone was deliberately removed; see predation.go). Re-acquires the prey.
	fly := newTestSwarm("b_fly", 10, 14, 12)
	state.Swarms[fly.ID] = fly
	// The wasp ENTERS THE NEST for a dwell (tending the brood) before resuming — advance past the dwell,
	// then (satiation 80 < the 90 ceiling) it re-acquires the prey.
	state.TickCount = resident.FeedUntilTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.TargetPreyID != fly.ID {
		t.Fatalf("post-dwell wasp (satiation 80 < ceiling 90) should resume hunting, got prey=%q", resident.TargetPreyID)
	}
}

// Breeding-unify: a deposit lays a VISIBLE egg into the nest brood — no instant pop — and processBroods
// matures + hatches it INTO THE RESIDENT over time (hatchFromBrood's "nest" case + SWARM_REPRODUCED).
func TestNestBroodDevelopsAndHatches(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)

	before := resident.Count
	for i := 0; i < 3; i++ {
		m.depositBrood(state, resident, nest, nopRuntimeLogger())
	}
	if resident.Count != before {
		t.Fatalf("deposits must NOT instant-hatch: count=%d, want %d", resident.Count, before)
	}
	if got := m.nestBroodCount(state, nest); got != 3 {
		t.Fatalf("3 deposits should bank 3 eggs in the nest brood, got %d", got)
	}
	// Advance the slow nursery clock until it hatches into the resident.
	maxIters := int(entities.BroodEggMatureTicks/30)*3 + 30
	for i := 0; i < maxIters && resident.Count == before; i++ {
		m.processBroods(state, nil, nopRuntimeLogger())
	}
	if resident.Count <= before {
		t.Fatalf("nest brood never hatched into the resident: count=%d", resident.Count)
	}
	evs := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evs) == 0 || evs[0].SwarmID != resident.ID {
		t.Fatalf("a nest hatch must emit SWARM_REPRODUCED into the resident: %+v", evs)
	}
}

// Deposits bank into the nest brood and CLAMP at NestBroodCap (no unbounded banking).
func TestNestBroodClampAtCap(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)

	for i := 0; i < 20; i++ {
		m.depositBrood(state, resident, nest, nopRuntimeLogger())
	}
	if got := m.nestBroodCount(state, nest); got != entities.NestBroodCap {
		t.Fatalf("nest brood must clamp at NestBroodCap=%d, got %d", entities.NestBroodCap, got)
	}
}

// Brood-drain re-hatch: a dead resident re-staffs after the delay at brood-consumed
// size; ~3 culls exhaust the nest into dormancy.
func TestNestBroodDrainRehatch(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	// Bank 6 ready maggots (two hatch-cost worth) in the nest BroodState.
	b := m.getOrCreateBrood(state, nest.GridX, nest.GridY, nest.SpeciesID, "nest", "", entities.NestBroodCap)
	b.Maggots = 6

	// Cull #1: the player catches/kills the whole patrol.
	delete(state.Swarms, resident.ID)
	m.processNests(state, nil, nopRuntimeLogger()) // arms the timer
	if nest.RehatchAtTick == 0 {
		t.Fatal("re-hatch timer not armed")
	}
	state.TickCount = nest.RehatchAtTick
	m.processNests(state, nil, nopRuntimeLogger()) // re-hatches
	r2 := state.Swarms[nest.ResidentSwarmID]
	if r2 == nil || r2.Count != entities.NestHatchCost {
		t.Fatalf("re-hatch #1: resident=%v count=%v, want size = brood consumed (%d)",
			r2 != nil, rcount(r2), entities.NestHatchCost)
	}
	if got := m.nestBroodCount(state, nest); got != 3 {
		t.Fatalf("brood after re-hatch #1 = %d, want 3", got)
	}

	// Cull #2: drains the rest.
	delete(state.Swarms, r2.ID)
	m.processNests(state, nil, nopRuntimeLogger())
	state.TickCount = nest.RehatchAtTick
	m.processNests(state, nil, nopRuntimeLogger())
	r3 := state.Swarms[nest.ResidentSwarmID]
	if r3 == nil || m.nestBroodCount(state, nest) != 0 {
		t.Fatalf("re-hatch #2: resident=%v brood=%d", r3 != nil, m.nestBroodCount(state, nest))
	}

	// Cull #3: nothing left — DORMANT (the readable axe-at-leisure state).
	delete(state.Swarms, r3.ID)
	m.processNests(state, nil, nopRuntimeLogger())
	if nest.RehatchAtTick != 0 {
		t.Fatal("dormant nest must not arm a re-hatch")
	}
	state.TickCount += entities.NestRehatchDelay + 10
	m.processNests(state, nil, nopRuntimeLogger())
	if _, alive := state.Swarms[nest.ResidentSwarmID]; alive && nest.ResidentSwarmID != "" {
		t.Fatal("dormant nest re-staffed from nothing")
	}
}

func rcount(s *entities.SwarmState) int {
	if s == nil {
		return -1
	}
	return s.Count
}

// setNestBrood seeds a nest's banked brood (now the nest BroodState) to n ready maggots — the test-side
// stand-in for the old nest.Brood counter.
func setNestBrood(m *Match, state *WorldState, nest *entities.NestState, n int) {
	b := m.getOrCreateBrood(state, nest.GridX, nest.GridY, nest.SpeciesID, "nest", "", entities.NestBroodCap)
	b.Eggs, b.Maggots = 0, n
}

// Nest destruction (breakOccupantAt) clears the state and ORPHANS the resident:
// no more breeding (deposits no-op), tether stays, hunting continues.
func TestNestBreakOrphansResident(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	_ = nest

	m.breakOccupantAt(nopRuntimeLogger(), nil, state, 10, 10, false)

	if state.NestStates["10,10"] != nil {
		t.Fatal("nest state survived the break")
	}
	if resident.NestKey != "" {
		t.Fatal("resident not orphaned")
	}
	// Orphan sated → NO homing (it has nowhere to go).
	resident.Satiation = 100
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, state.Species["wasp_common"], 32, 0.1, nopRuntimeLogger())
	if resident.Phase == "homing" {
		t.Fatal("orphan entered homing")
	}
}

// Break-teardown: kicking a nursery open PERISHES its developing brood — no bugs are minted from it (a torn
// brood is dead brood; harvest it first to keep it) — and orphans the resident (still alive; being adjacent
// to the breaker its proximity aggro turns it onto them). Only living adults survive a teardown.
func TestNestBreakPerishesBrood(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	setNestBrood(m, state, nest, 5) // 5 developing brood inside
	before := len(state.Swarms)     // includes the already-live resident patrol

	m.breakOccupantAt(nopRuntimeLogger(), nil, state, 10, 10, false)

	if state.NestStates["10,10"] != nil {
		t.Fatal("nest survived the break")
	}
	if got := m.nestBroodCount(state, nest); got != 0 {
		t.Fatalf("brood not cleared on teardown: %d", got)
	}
	// The brood PERISHES — no new swarm is minted from it; only the already-live resident remains.
	if len(state.Swarms) != before {
		t.Fatalf("teardown must NOT mint a swarm from the perished brood: swarms %d -> %d", before, len(state.Swarms))
	}
	if resident.NestKey != "" {
		t.Fatal("resident not orphaned")
	}
	if _, alive := state.Swarms[resident.ID]; !alive {
		t.Fatal("the live resident adults must survive the teardown")
	}
}

// The occupant-gone SWEEP (any removal path) also cleans + orphans.
func TestNestSweepOnOccupantGone(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	_, resident := initTestNest(m, state)

	// Remove the occupant directly (not via breakOccupantAt).
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.ClearOccupant(10, 10)
	m.processNests(state, nil, nopRuntimeLogger())

	if state.NestStates["10,10"] != nil {
		t.Fatal("sweep missed the gone occupant")
	}
	if resident.NestKey != "" {
		t.Fatal("sweep did not orphan the resident")
	}
}

// Defend: proximity entry + hysteresis exit + the AGGRO-ON-DAMAGE recall from any
// distance (axing while the patrol hunts = a head start, not immunity).
func TestNestDefendTriggerAndRecall(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	_, resident := initTestNest(m, state)
	species := state.Species["wasp_common"]

	state.Players = map[string]*PlayerState{
		"p1": {UserID: "p1", Position: entities.EntityPosition{LocalX: 12, LocalY: 10}}, // 1.5 from the nest
	}

	// Proximity entry at think time.
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.Phase != "defending" || resident.DefendTargetID != "p1" {
		t.Fatalf("phase=%q target=%q, want defending/p1", resident.Phase, resident.DefendTargetID)
	}

	// Hysteresis exit: the player flees past the release radius.
	state.Players["p1"].Position = entities.EntityPosition{LocalX: 25, LocalY: 10}
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.Phase == "defending" {
		t.Fatal("defending did not release past the hysteresis radius")
	}

	// AGGRO-ON-DAMAGE: the resident is far away hunting; a nest hit recalls it NOW.
	resident.Position = entities.EntityPosition{LocalX: 30, LocalY: 30}
	resident.Phase = "feeding"
	m.recallNestDefenders(state, 10, 10, "p1")
	if resident.Phase != "defending" || resident.DefendTargetID != "p1" {
		t.Fatalf("recall failed: phase=%q target=%q", resident.Phase, resident.DefendTargetID)
	}
	if resident.NextThinkTick != state.TickCount {
		t.Fatal("recall must trigger an immediate think")
	}
}

// growSwarm parity across all three callers: same id math, same event shape.
func TestGrowSwarmParity(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	s := newTestSwarm(fmt.Sprintf("s_%d", 1), 5, 10, 10)
	state.Swarms[s.ID] = s

	base := m.growSwarm(state, s, 3)
	if base != 5 || s.Count != 8 || s.NextBugID != 8 {
		t.Fatalf("growSwarm: base=%d count=%d next=%d, want 5/8/8", base, s.Count, s.NextBugID)
	}
	if !s.IsBugAlive(5) || !s.IsBugAlive(7) {
		t.Fatal("grown bugs must be alive")
	}
	evs := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evs) != 1 || evs[0].SplitCount != 3 || evs[0].NewBugIDBase != 5 {
		t.Fatalf("event wrong: %+v", evs)
	}
}

// Phase 3: a THRIVING colony (saturated patrol + full brood bank) splits off a daughter hive — up to
// the per-zone MaxNests — and draining the parent's brood arms a founding cooldown.
func TestNestFoundingSplitsDaughterHive(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	if nest == nil || resident == nil {
		t.Fatal("parent nest/resident not founded")
	}
	species := state.Species["wasp_common"]

	// Allow up to 2 hives, ample population headroom.
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"wasp_common": {MaxNests: 2, MaxPopulation: 100},
	}}

	// A daughter now founds NEXT TO A PREY CLUSTER an adequate distance from the parent (nest at 10,10).
	// Drop a fly swarm at world (55,10) ≈ 44 cells away — inside the 40..120 band + the loaded chunks.
	prey := &entities.SwarmState{ID: "prey_fly", SpeciesID: "fly_common", Count: 6,
		Position: entities.EntityPosition{ChunkX: 1, ChunkY: 0, LocalX: 23, LocalY: 10}}
	prey.InitializeBugIDs()
	state.Swarms["prey_fly"] = prey

	// Not yet thriving (brood not full) → no founding.
	resident.Count = species.MaxSwarmSize
	setNestBrood(m, state, nest, entities.NestBroodCap-1)
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 1 {
		t.Fatalf("a non-thriving colony must not found (nests=%d)", len(state.NestStates))
	}

	// Thriving: saturated patrol + full brood → founds exactly one daughter, draining the parent brood.
	setNestBrood(m, state, nest, entities.NestBroodCap)
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 2 {
		t.Fatalf("a thriving colony under MaxNests must found one daughter hive, got %d nests", len(state.NestStates))
	}
	if got := m.nestBroodCount(state, nest); got != 0 {
		t.Fatalf("founding must drain the parent brood (cooldown), got %d", got)
	}

	// At the cap (2 nests): re-arm the parent, still no further founding.
	setNestBrood(m, state, nest, entities.NestBroodCap)
	resident.Count = species.MaxSwarmSize
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 2 {
		t.Fatalf("at MaxNests no more hives may be founded, got %d", len(state.NestStates))
	}
}

// A nursery is a modified station: taking a stage pulls its units into the bag as the per-species stage item
// — a plain transfer (take-all by default), nothing perishes, other stages untouched. Partial + range enforced.
func TestNurseryTakeStation(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	sp := state.Species["wasp_common"]
	sp.EggSpriteID = "wasp_eggs"
	sp.LarvaSpriteID = "wasp_grubs"
	sp.PupaSpriteID = "wasp_pupa"
	sp.LarvaItemID = "wasp_larvae" // larva TAKE item = the designed material; the sprite stays wasp_grubs

	state.BroodStates[broodKey(10, 10)] = &entities.BroodState{
		GridX: 10, GridY: 10, SpeciesID: "wasp_common", SourceKind: "nest",
		Eggs: 5, Maggots: 3, Pupae: 2,
	}
	player := &PlayerState{UserID: "p1", Position: entities.EntityPosition{LocalX: 11, LocalY: 10}}
	state.Players = map[string]*PlayerState{"p1": player}

	// take-all of the larva stage (stage 1)
	m.handleNurseryTake(nopRuntimeLogger(), nopDispatcher{}, state, "p1", NurseryTakeMessage{GX: 10, GY: 10, Stage: 1})
	b := state.BroodStates[broodKey(10, 10)]
	if b.Maggots != 0 {
		t.Fatalf("take-all must empty the larva stage, got %d", b.Maggots)
	}
	if b.Eggs != 5 || b.Pupae != 2 {
		t.Fatalf("other stages must be untouched: eggs=%d pupae=%d", b.Eggs, b.Pupae)
	}
	if slot := player.FindItem("wasp_larvae"); slot < 0 || player.ItemSlots[slot].Count != 3 {
		t.Fatalf("larva take must grant 3 wasp_larvae (the designed item), slot=%d", slot)
	}

	// partial take: 2 of the 5 eggs (stage 0, count 2) — no egg_item_id, so it falls back to the egg SPRITE
	// id (wasp_eggs); nothing perishes, the other 3 stay
	m.handleNurseryTake(nopRuntimeLogger(), nopDispatcher{}, state, "p1", NurseryTakeMessage{GX: 10, GY: 10, Stage: 0, Count: 2})
	if b.Eggs != 3 {
		t.Fatalf("partial take must leave 3 eggs (no perish), got %d", b.Eggs)
	}
	if slot := player.FindItem("wasp_eggs"); slot < 0 || player.ItemSlots[slot].Count != 2 {
		t.Fatalf("must grant 2 wasp_eggs items")
	}

	// out of range: nothing happens
	player.Position = entities.EntityPosition{LocalX: 40, LocalY: 40}
	m.handleNurseryTake(nopRuntimeLogger(), nopDispatcher{}, state, "p1", NurseryTakeMessage{GX: 10, GY: 10, Stage: 2})
	if b.Pupae != 2 {
		t.Fatalf("out-of-range take must do nothing, pupae=%d", b.Pupae)
	}
}
