package world

// BEHAVSTATS — the server half of the behaviour check (docs/plans/village-slice.md, Stage 1.0a): what each species
// did today, counted where the server applies each event, flushed once per game-day beside ECOSTATS. Soft state,
// never hashed. (The feeding and breeding counters live inside MatchLoop's per-swarm pass and are checked in the
// headless runs.)
//
// Run inside the builder image:  go test ./world/ -run TestBehav -v

import (
	"fmt"
	"strings"
	"testing"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// lineLogger records Info lines so a test can read the emitted stats.
type lineLogger struct {
	nopLogger
	lines *[]string
}

func (l lineLogger) Info(format string, args ...interface{}) {
	*l.lines = append(*l.lines, fmt.Sprintf(format, args...))
}
func (l lineLogger) WithField(string, interface{}) runtime.Logger     { return l }
func (l lineLogger) WithFields(map[string]interface{}) runtime.Logger { return l }

func behaviourOf(state *WorldState, species string, ev BehaviourEvent) int {
	return state.Stats.Behaviour[species][ev]
}

// The line: one per species, fixed columns in a fixed order (0 when nothing happened), and the day resets after.
func TestBehavStatsLineFormatAndReset(t *testing.T) {
	state := newTestState(50)
	state.Stats = NewEcologyStats()
	state.Stats.recordBehaviour("fly_common", BehEggs, 3)
	state.Stats.recordBehaviour("fly_common", BehSplit, 1)

	var lines []string
	(&Match{}).emitEcologyStats(state, 7, lineLogger{lines: &lines})

	want := "BEHAVSTATS day=7 sp=fly_common feed=0 breed=0 eggs=3 trip_home=0 trip_abandon=0 nest_defend=0 merge=0 split=1 player_hit=0"
	found := false
	for _, l := range lines {
		if strings.HasPrefix(l, "BEHAVSTATS") {
			if l != want {
				t.Fatalf("BEHAVSTATS line:\n got %q\nwant %q", l, want)
			}
			found = true
		}
	}
	if !found {
		t.Fatalf("no BEHAVSTATS line among %v", lines)
	}
	if len(state.Stats.Behaviour) != 0 {
		t.Fatal("the behaviour counts must reset after the day's lines")
	}
}

// Eggs: a brood clutch counts the eggs accepted (not the eggs offered); a nest deposit counts one.
func TestBehavStatsEggs(t *testing.T) {
	state := newTestState(50)
	state.Stats = NewEcologyStats()
	m := &Match{}
	b := m.getOrCreateBrood(state, 10, 10, "fly_common", "ground_pile", "food1", 4)
	m.layEggs(nil, state, b, 3)
	m.layEggs(nil, state, b, 3) // only 1 more fits (cap 4)
	if got := behaviourOf(state, "fly_common", BehEggs); got != 4 {
		t.Fatalf("eggs=%d, want 4 (3 + the 1 that fit)", got)
	}

	ns := nestTestState()
	ns.Stats = NewEcologyStats()
	nest, _ := initTestNest(m, ns)
	m.depositNestEgg(ns, nest, entities.NestBroodCap)
	if got := behaviourOf(ns, "wasp_common", BehEggs); got != 1 {
		t.Fatalf("nest eggs=%d, want 1", got)
	}
}

// Merges and splits count once each, for their species.
func TestBehavStatsMergeSplit(t *testing.T) {
	state := newTestState(20)
	state.Stats = NewEcologyStats()
	parent := newTestSwarm("parent", 21, 10, 10)
	state.Swarms["parent"] = parent
	state.SwarmsBySpecies["fly_common"] = []string{"parent"}
	(&Match{}).checkSwarmSplitting(state, state.Config.ChunkSize, nopRuntimeLogger())
	if got := behaviourOf(state, "fly_common", BehSplit); got != 1 {
		t.Fatalf("splits=%d, want 1", got)
	}

	state = newTestState(20)
	state.Stats = NewEcologyStats()
	a, b := newTestSwarm("a", 8, 10, 10), newTestSwarm("b", 8, 11, 10)
	state.Swarms["a"], state.Swarms["b"] = a, b
	state.SwarmsBySpecies["fly_common"] = []string{"a", "b"}
	(&Match{}).checkSwarmMerging(state, state.Config.ChunkSize, nopRuntimeLogger())
	if got := behaviourOf(state, "fly_common", BehMerge); got != 1 {
		t.Fatalf("merges=%d, want 1", got)
	}
}

// Nest defence counts the change into "defending" once — a recall of a resident already defending doesn't add one.
func TestBehavStatsNestDefend(t *testing.T) {
	state := nestTestState()
	state.Stats = NewEcologyStats()
	m := &Match{}
	_, resident := initTestNest(m, state)
	resident.Phase = "feeding"
	m.recallNestDefenders(state, 10, 10, "p1")
	m.recallNestDefenders(state, 10, 10, "p1") // already defending: no second count
	if got := behaviourOf(state, "wasp_common", BehNestDefend); got != 1 {
		t.Fatalf("nest defences=%d, want 1", got)
	}
}

// A trip home that reaches the nest counts once; one that times out counts as abandoned.
func TestBehavStatsTripHome(t *testing.T) {
	state := nestTestState()
	state.Stats = NewEcologyStats()
	m := &Match{}
	_, resident := initTestNest(m, state)
	species := state.Species["wasp_common"]

	resident.Position = entities.EntityPosition{LocalX: 25, LocalY: 10}
	resident.Satiation = 100
	state.TickCount = resident.NextThinkTick + 1
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	for i := 0; i < 600 && resident.Phase == "homing"; i++ {
		state.TickCount++
		if state.TickCount >= resident.NextThinkTick {
			m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
		}
		resident.Move(0.1, species, 32)
	}
	if got := behaviourOf(state, "wasp_common", BehTripHome); got != 1 {
		t.Fatalf("trips home=%d, want 1", got)
	}

	// A second trip that never arrives: past the homing timeout it is abandoned.
	resident.Position = entities.EntityPosition{LocalX: 25, LocalY: 10}
	resident.Phase = "homing"
	resident.CarryingBrood = true
	resident.HomingStartTick = state.TickCount
	state.TickCount += entities.NestHomingTimeout + 1
	resident.NextThinkTick = state.TickCount
	m.predationThink(state, resident, species, 32, 0.1, nopRuntimeLogger())
	if got := behaviourOf(state, "wasp_common", BehTripAbandon); got != 1 {
		t.Fatalf("abandoned trips=%d, want 1", got)
	}
}

// A strike that damages a player counts as a hit for the attacking species; a windup (no damage) doesn't.
func TestBehavStatsPlayerHit(t *testing.T) {
	state, p := hpTestState()
	state.Stats = NewEcologyStats()
	m := &Match{}
	w := newWaspSwarm("a_w", 6, 10.5, 10)
	state.Swarms[w.ID] = w
	state.TickCount = 1000

	m.handleBugPlayerStrike(nopRuntimeLogger(), nil, state, testAuthority, BugPlayerStrikeMessage{
		SwarmID: w.ID, PlayerID: "p1", BugIDs: w.FirstAliveBugIDs(2), Phase: "windup",
	})
	strike(m, state, testAuthority, w.ID, "p1", w.FirstAliveBugIDs(2))
	if p.HP != 9 {
		t.Fatalf("HP=%d, want 9 (the strike must land for this test to mean anything)", p.HP)
	}
	if got := behaviourOf(state, w.SpeciesID, BehPlayerHit); got != 1 {
		t.Fatalf("player hits=%d, want 1", got)
	}
}
