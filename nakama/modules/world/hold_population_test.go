package world

// The test-zone HoldPopulation switch (docs/plans/village-slice.md, Stage 1.0a): cost measurements need a steady bug
// count, so nothing is born after the start and nothing dies of age or hunger — while the rest of the ecology runs
// as normal (breeding still resets its meters and eats its food, merges and splits and predation still happen, nests
// still staff when their chunk loads). Each test pairs the held case with the normal case so it can't pass by doing
// nothing.
//
// Run inside the builder image:  go test ./world/ -run TestHoldPopulation -v

import (
	"testing"

	"bugfarmer/entities"
)

func holdOn(state *WorldState) *WorldState {
	state.CurrentZone.HoldPopulation = true
	return state
}

// Hatching: a brood with ready maggots grows the swarm normally, and hatches nothing when held.
func TestHoldPopulationNoHatch(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := newTestState(50)
		if held {
			holdOn(state)
		}
		m := &Match{}
		swarm := newTestSwarm("s", 10, 10, 10)
		state.Swarms["s"] = swarm
		state.SwarmsBySpecies["fly_common"] = []string{"s"}
		b := m.getOrCreateBrood(state, 10, 10, "fly_common", "station", "station_10_10", 12)
		b.Maggots = 4

		got := m.hatchFromBrood(state, b)
		if held && (got != 0 || swarm.Count != 10 || b.Maggots != 4) {
			t.Fatalf("held: hatched=%d count=%d maggots=%d, want nothing hatched", got, swarm.Count, b.Maggots)
		}
		if !held && (got == 0 || swarm.Count == 10) {
			t.Fatalf("control: the brood must hatch (hatched=%d count=%d)", got, swarm.Count)
		}
	}
}

// Breeding: reproduceSwarm lays a clutch normally; held, it lays nothing but still resets the meter, satiation and
// cooldown (otherwise the swarm would sit "reproducing" and drain its plant every tick).
func TestHoldPopulationReproduceResetsWithoutClutch(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := newTestState(50)
		if held {
			holdOn(state)
		}
		m := &Match{}
		species := state.Species["fly_common"]
		species.ReproduceCooldown = 30
		swarm := newTestSwarm("s", 10, 10, 10)
		swarm.ReproductionMeter, swarm.Satiation = 100, 80
		state.Swarms["s"] = swarm
		state.SwarmsBySpecies["fly_common"] = []string{"s"}

		m.reproduceSwarm(state, nil, swarm, species, nopRuntimeLogger())

		if swarm.ReproductionMeter != 0 || swarm.Satiation != 0 || swarm.ReproduceCooldown != 30 {
			t.Fatalf("held=%v: meter=%.0f satiation=%.0f cooldown=%v, want the resets applied", held,
				swarm.ReproductionMeter, swarm.Satiation, swarm.ReproduceCooldown)
		}
		if held && len(state.BroodStates) != 0 {
			t.Fatalf("held: %d broods laid, want none", len(state.BroodStates))
		}
		if !held && len(state.BroodStates) == 0 {
			t.Fatal("control: a clutch must be laid")
		}
	}
}

// Nest species grow in place (growSwarm) normally; held, they don't, and the resets still apply.
func TestHoldPopulationNestSpeciesReproduceNoGrowth(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := nestTestState()
		if held {
			holdOn(state)
		}
		m := &Match{}
		_, resident := initTestNest(m, state)
		species := state.Species["wasp_common"]
		before := resident.Count
		resident.ReproductionMeter, resident.Satiation = 100, 80

		m.reproduceSwarm(state, nil, resident, species, nopRuntimeLogger())

		if held && resident.Count != before {
			t.Fatalf("held: count %d -> %d, want unchanged", before, resident.Count)
		}
		if !held && resident.Count <= before {
			t.Fatalf("control: the resident must grow (count %d -> %d)", before, resident.Count)
		}
		if resident.ReproductionMeter != 0 || resident.Satiation != 0 {
			t.Fatalf("held=%v: meter=%.0f satiation=%.0f, want reset", held, resident.ReproductionMeter, resident.Satiation)
		}
	}
}

// Nest eggs from a trip home: laid normally, none when held.
func TestHoldPopulationNoNestEggs(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := nestTestState()
		if held {
			holdOn(state)
		}
		m := &Match{}
		nest, _ := initTestNest(m, state)
		m.depositNestEgg(state, nest, entities.NestBroodCap)
		got := m.nestBroodCount(state, nest)
		if held && got != 0 {
			t.Fatalf("held: nest brood=%d, want 0", got)
		}
		if !held && got != 1 {
			t.Fatalf("control: nest brood=%d, want 1", got)
		}
	}
}

// Nests still staff when their chunk first loads (part of the starting count), held or not.
func TestHoldPopulationKeepsNestStaffingOnChunkLoad(t *testing.T) {
	state := holdOn(nestTestState())
	nest, resident := initTestNest(&Match{}, state)
	if nest == nil || resident == nil || resident.Count != state.Tuning.NestFoundingSize {
		t.Fatalf("held zone: nest=%v resident=%v, want the founding patrol staffed on chunk load",
			nest != nil, rcount(resident))
	}
}

// A dead resident with banked brood re-hatches normally; held, the nest stays empty however long we wait.
func TestHoldPopulationNoNestRehatch(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := nestTestState()
		if held {
			holdOn(state)
		}
		m := &Match{}
		nest, resident := initTestNest(m, state)
		setNestBrood(m, state, nest, 6)
		delete(state.Swarms, resident.ID)

		for i := 0; i < 3; i++ {
			m.processNests(state, nil, nopRuntimeLogger())
			state.TickCount += entities.NestRehatchDelay + entities.NestRecoveryDelay + 10
		}
		_, alive := state.Swarms[nest.ResidentSwarmID]
		restaffed := alive && nest.ResidentSwarmID != resident.ID
		if held && restaffed {
			t.Fatal("held: the nest re-hatched a resident")
		}
		if !held && !restaffed {
			t.Fatal("control: the nest must re-hatch from its banked brood")
		}
	}
}

// Natural death: aged bugs are culled normally; held, nobody dies of age.
func TestHoldPopulationNoAgeingDeaths(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := newTestState(20)
		if held {
			holdOn(state)
		}
		state.Species["fly_common"].CarcassItem = "dead_fly"
		sw := newTestSwarm("s", 5, 10, 10)
		sw.DeathTick = map[int]int64{0: 900, 1: 950}
		state.Swarms["s"] = sw

		(&Match{}).processNaturalDeath(nopRuntimeLogger(), nopDispatcher{}, state, 32)

		if held && sw.Count != 5 {
			t.Fatalf("held: count=%d, want 5 (no ageing deaths)", sw.Count)
		}
		if !held && sw.Count != 3 {
			t.Fatalf("control: count=%d, want 3", sw.Count)
		}
	}
}

// Starvation: a starving swarm loses bugs normally; held, it doesn't.
func TestHoldPopulationNoStarvationDeaths(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := newTestState(50)
		if held {
			holdOn(state)
		}
		starved := newTestSwarm("starved", 10, 20, 20)
		starved.StarveTimer = starvationDeathSecs
		state.Swarms["starved"] = starved
		state.SwarmsBySpecies["fly_common"] = []string{"starved"}

		(&Match{}).processStarvation(nopRuntimeLogger(), nil, state, state.Config.ChunkSize)

		if held && starved.Count != 10 {
			t.Fatalf("held: count=%d, want 10", starved.Count)
		}
		if !held && starved.Count != 9 {
			t.Fatalf("control: count=%d, want 9", starved.Count)
		}
	}
}

// The director: an over-band species is culled normally; held, the director does nothing.
func TestHoldPopulationNoDirector(t *testing.T) {
	for _, held := range []bool{false, true} {
		state := newTestState(50)
		if held {
			holdOn(state)
		}
		swarm := newTestSwarm("s", 60, 10, 10)
		state.Swarms["s"] = swarm
		state.SwarmsBySpecies["fly_common"] = []string{"s"}
		state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
			"fly_common": {CullAt: 50},
		}}

		(&Match{}).processEcologyDirector(nopRuntimeLogger(), nil, state, 32)

		if held && swarm.Count != 60 {
			t.Fatalf("held: count=%d, want 60 (no director)", swarm.Count)
		}
		if !held && swarm.Count != 50 {
			t.Fatalf("control: count=%d, want 50", swarm.Count)
		}
	}
}

// Merges and splits keep running in a held zone (their cost is part of what's measured), and they conserve bugs.
func TestHoldPopulationKeepsMergeAndSplit(t *testing.T) {
	state := holdOn(newTestState(20))
	parent := newTestSwarm("parent", 21, 10, 10)
	state.Swarms["parent"] = parent
	state.SwarmsBySpecies["fly_common"] = []string{"parent"}
	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())
	if len(state.Swarms) != 2 || parent.Count != 11 {
		t.Fatalf("held: split didn't run (swarms=%d parent=%d)", len(state.Swarms), parent.Count)
	}

	state = holdOn(newTestState(20))
	a, b := newTestSwarm("a", 8, 10, 10), newTestSwarm("b", 8, 11, 10)
	state.Swarms["a"], state.Swarms["b"] = a, b
	state.SwarmsBySpecies["fly_common"] = []string{"a", "b"}
	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())
	if len(state.Swarms) != 1 {
		t.Fatalf("held: merge didn't run (swarms=%d)", len(state.Swarms))
	}
	for _, s := range state.Swarms {
		if s.Count != 16 {
			t.Fatalf("held: merged count=%d, want 16", s.Count)
		}
	}
}
