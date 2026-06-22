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
	if nest.Brood != 1 {
		t.Fatalf("brood=%d, want 1", nest.Brood)
	}
	if resident.Satiation != 80 {
		t.Fatalf("post-deposit satiation=%.0f, want deposit_satiation 80", resident.Satiation)
	}

	// After depositing, satiation drops to deposit_satiation (80) — still BELOW the full-load ceiling
	// (predatorFullSatiation=90), so the forager loop immediately RESUMES hunting (the old rest-at-
	// HuntSatiationThreshold dead zone was deliberately removed; see predation.go). Re-acquires the prey.
	fly := newTestSwarm("b_fly", 10, 14, 12)
	state.Swarms[fly.ID] = fly
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if resident.TargetPreyID != fly.ID {
		t.Fatalf("post-deposit wasp (satiation 80 < ceiling 90) should resume hunting, got prey=%q", resident.TargetPreyID)
	}
}

// Hatch at brood 3: +2 flat into the resident via the shared growSwarm (ids + event).
func TestNestHatchAtThreeBrood(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)

	nest.Brood = 2
	before := resident.Count
	m.depositBrood(state, resident, nest, nopRuntimeLogger()) // -> 3 -> hatch
	if resident.Count != before+entities.NestHatchCount {
		t.Fatalf("count=%d, want +%d", resident.Count, entities.NestHatchCount)
	}
	if nest.Brood != 0 {
		t.Fatalf("brood=%d, want 0 (3 consumed)", nest.Brood)
	}
	evs := eventsOfType(state, InfluenceSwarmReproduced)
	if len(evs) != 1 || evs[0].SwarmID != resident.ID || evs[0].SplitCount != entities.NestHatchCount {
		t.Fatalf("hatch event wrong: %+v", evs)
	}
}

// Brood clamps at NestBroodCap — no banked chain-hatching after a cull.
func TestNestBroodClamp(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)

	// Saturate the population cap so hatches skip and deposits only bank.
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"wasp_common": {Max: 5, MaxPopulation: resident.Count}, // exactly at cap
	}}
	for i := 0; i < 12; i++ {
		m.depositBrood(state, resident, nest, nopRuntimeLogger())
	}
	if nest.Brood != entities.NestBroodCap {
		t.Fatalf("brood=%d, want the clamp %d", nest.Brood, entities.NestBroodCap)
	}
	if resident.Count > 4 {
		t.Fatalf("hatched past the population cap: %d", resident.Count)
	}
}

// Brood-drain re-hatch: a dead resident re-staffs after the delay at brood-consumed
// size; ~3 culls exhaust the nest into dormancy.
func TestNestBroodDrainRehatch(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	nest, resident := initTestNest(m, state)
	nest.Brood = 6 // two banked hatches

	// Cull #1: the player catches/kills the whole patrol.
	delete(state.Swarms, resident.ID)
	m.processNests(state, nopRuntimeLogger()) // arms the timer
	if nest.RehatchAtTick == 0 {
		t.Fatal("re-hatch timer not armed")
	}
	state.TickCount = nest.RehatchAtTick
	m.processNests(state, nopRuntimeLogger()) // re-hatches
	r2 := state.Swarms[nest.ResidentSwarmID]
	if r2 == nil || r2.Count != entities.NestHatchCost {
		t.Fatalf("re-hatch #1: resident=%v count=%v, want size = brood consumed (%d)",
			r2 != nil, rcount(r2), entities.NestHatchCost)
	}
	if nest.Brood != 3 {
		t.Fatalf("brood after re-hatch #1 = %d, want 3", nest.Brood)
	}

	// Cull #2: drains the rest.
	delete(state.Swarms, r2.ID)
	m.processNests(state, nopRuntimeLogger())
	state.TickCount = nest.RehatchAtTick
	m.processNests(state, nopRuntimeLogger())
	r3 := state.Swarms[nest.ResidentSwarmID]
	if r3 == nil || nest.Brood != 0 {
		t.Fatalf("re-hatch #2: resident=%v brood=%d", r3 != nil, nest.Brood)
	}

	// Cull #3: nothing left — DORMANT (the readable axe-at-leisure state).
	delete(state.Swarms, r3.ID)
	m.processNests(state, nopRuntimeLogger())
	if nest.RehatchAtTick != 0 {
		t.Fatal("dormant nest must not arm a re-hatch")
	}
	state.TickCount += entities.NestRehatchDelay + 10
	m.processNests(state, nopRuntimeLogger())
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

// The occupant-gone SWEEP (any removal path) also cleans + orphans.
func TestNestSweepOnOccupantGone(t *testing.T) {
	state := nestTestState()
	m := &Match{}
	_, resident := initTestNest(m, state)

	// Remove the occupant directly (not via breakOccupantAt).
	chunk := state.Chunks[ChunkKey(0, 0)]
	chunk.ClearOccupant(10, 10)
	m.processNests(state, nopRuntimeLogger())

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
	nest.Brood = entities.NestBroodCap - 1
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 1 {
		t.Fatalf("a non-thriving colony must not found (nests=%d)", len(state.NestStates))
	}

	// Thriving: saturated patrol + full brood → founds exactly one daughter, draining the parent brood.
	nest.Brood = entities.NestBroodCap
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 2 {
		t.Fatalf("a thriving colony under MaxNests must found one daughter hive, got %d nests", len(state.NestStates))
	}
	if nest.Brood != 0 {
		t.Fatalf("founding must drain the parent brood (cooldown), got %d", nest.Brood)
	}

	// At the cap (2 nests): re-arm the parent, still no further founding.
	nest.Brood = entities.NestBroodCap
	resident.Count = species.MaxSwarmSize
	m.processNestFounding(state, nil, nopRuntimeLogger())
	if len(state.NestStates) != 2 {
		t.Fatalf("at MaxNests no more hives may be founded, got %d", len(state.NestStates))
	}
}
