package world

// Natural death (per-bug aging): DeathTick is scheduled at birth, carried through split/merge exactly
// like BugHP, cleaned on removal, and the death pass culls bugs past their DeathTick.
// Run:  go test ./world/ -run 'TestDeath|TestAssignDeathTicks|TestProcessNaturalDeath' -v

import (
	"testing"

	"bugfarmer/entities"
)

func TestAssignDeathTicksSchedulesFromLifespan(t *testing.T) {
	sw := newTestSwarm("s", 3, 10, 10) // ids 0..2, bornTick below
	sp := &entities.BugSpecies{LifespanSecs: 10, LifespanSpreadSecs: 0}
	assignDeathTicks(sw, sp, 0, 3, 1000, 10) // tickRate 10 → lifespan 100 ticks, no spread
	for id := 0; id < 3; id++ {
		if sw.DeathTick[id] != 1100 {
			t.Fatalf("DeathTick[%d]=%d, want 1100 (born 1000 + 10s*10)", id, sw.DeathTick[id])
		}
	}
	// Spread stays within [-spread, +spread] of the mean.
	sw2 := newTestSwarm("s2", 4, 10, 10)
	spS := &entities.BugSpecies{LifespanSecs: 10, LifespanSpreadSecs: 2} // ±20 ticks
	assignDeathTicks(sw2, spS, 0, 4, 1000, 10)
	for id := 0; id < 4; id++ {
		if sw2.DeathTick[id] < 1080 || sw2.DeathTick[id] > 1120 {
			t.Fatalf("DeathTick[%d]=%d out of [1080,1120]", id, sw2.DeathTick[id])
		}
	}
	// Immortal species (lifespan<=0) schedules nothing.
	sw3 := newTestSwarm("s3", 2, 10, 10)
	assignDeathTicks(sw3, &entities.BugSpecies{LifespanSecs: 0}, 0, 2, 1000, 10)
	if len(sw3.DeathTick) != 0 {
		t.Fatalf("immortal species scheduled %d deaths, want 0", len(sw3.DeathTick))
	}
}

func TestRemoveBugsCleansDeathTick(t *testing.T) {
	sw := newTestSwarm("s", 3, 10, 10)
	sw.DeathTick = map[int]int64{0: 1100, 1: 1200, 2: 1300}
	sw.RemoveBugs([]int{1})
	if _, leaked := sw.DeathTick[1]; leaked {
		t.Fatal("RemoveBugs left a stale DeathTick entry")
	}
	if sw.DeathTick[0] != 1100 || sw.DeathTick[2] != 1300 {
		t.Fatal("RemoveBugs disturbed surviving DeathTick entries")
	}
}

func TestSplitTransfersDeathTick(t *testing.T) {
	state := newTestState(20)
	parent := newTestSwarm("parent", 21, 10, 10) // sheds highest 10 ids (11..20) -> child 0..9
	state.Swarms["parent"] = parent
	state.SwarmsBySpecies["fly_common"] = []string{"parent"}
	parent.DeathTick = map[int]int64{15: 5000, 3: 6000} // 15 sheds (asc 11..20 -> child, 15 -> child 4); 3 stays

	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())

	var child *entities.SwarmState
	for id, s := range state.Swarms {
		if id != "parent" {
			child = s
		}
	}
	if child == nil {
		t.Fatal("no child swarm created")
	}
	if child.DeathTick[4] != 5000 {
		t.Fatalf("child.DeathTick[4]=%d, want 5000 (parent id 15 -> child id 4)", child.DeathTick[4])
	}
	if len(child.DeathTick) != 1 {
		t.Fatalf("child.DeathTick has %d entries, want 1", len(child.DeathTick))
	}
	if parent.DeathTick[3] != 6000 {
		t.Fatalf("parent.DeathTick[3]=%d, want 6000 (kept)", parent.DeathTick[3])
	}
	if _, leaked := parent.DeathTick[15]; leaked {
		t.Fatal("parent kept the shed bug's DeathTick entry")
	}
}

func TestMergeTransfersDeathTick(t *testing.T) {
	state := newTestState(50)
	s1 := newTestSwarm("s1", 5, 10, 10)
	s2 := newTestSwarm("s2", 5, 11, 10) // within MergeRadius 2.5
	state.Swarms["s1"], state.Swarms["s2"] = s1, s2
	state.SwarmsBySpecies["fly_common"] = []string{"s1", "s2"}
	s2.DeathTick = map[int]int64{2: 7000} // absorbed asc ids 0..4 -> survivor base+k; base=5 so 2 -> 7

	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())

	survivor := state.Swarms["s1"]
	if survivor == nil {
		t.Fatal("survivor s1 missing")
	}
	if survivor.DeathTick[7] != 7000 {
		t.Fatalf("survivor.DeathTick[7]=%d, want 7000 (absorbed id 2 -> 5+2)", survivor.DeathTick[7])
	}
}

func TestProcessNaturalDeathCullsAgedBugs(t *testing.T) {
	state := newTestState(20) // TickCount = 1000
	state.Species["fly_common"].CarcassItem = "dead_fly"
	sw := newTestSwarm("s", 5, 10, 10) // ids 0..4 alive
	// 0,1 past their death tick; 2 in the future; 3,4 have no schedule (immortal-ish) → survive.
	sw.DeathTick = map[int]int64{0: 900, 1: 950, 2: 2000}
	state.Swarms["s"] = sw

	(&Match{}).processNaturalDeath(nopRuntimeLogger(), nopDispatcher{}, state, 32)

	if sw.IsBugAlive(0) || sw.IsBugAlive(1) {
		t.Fatal("aged bugs 0/1 were not culled")
	}
	if !sw.IsBugAlive(2) || !sw.IsBugAlive(3) || !sw.IsBugAlive(4) {
		t.Fatal("non-aged bugs 2/3/4 were wrongly culled")
	}
	if sw.Count != 3 {
		t.Fatalf("Count=%d after culling 2 of 5, want 3", sw.Count)
	}
}
