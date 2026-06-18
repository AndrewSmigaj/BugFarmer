package world

// Predator/starvation guard tests (Phase 0 of the living-ecology redesign). The die-off bug was: every
// swarm was constructed at Satiation 0, so its StarveTimer accrued from birth and a PREDATOR (no food
// underfoot — it must hunt) was culled ~starvationDeathSecs after spawn, before it could reach prey.
// The fix gives a newborn `spawnSatiation` of runway; processStarvation still culls a genuinely
// food-starved swarm once its timer passes the threshold.
//
// Run inside the builder image:  go test ./modules/world/ -run 'TestSpawn|TestStarvation' -v

import "testing"

// A freshly spawned swarm must be born fed (so its StarveTimer doesn't accrue from tick 0).
func TestSpawnSwarmAtIsBornFed(t *testing.T) {
	state := newTestState(50)
	m := &Match{}

	sw := m.spawnSwarmAt(state, "fly_common", 10, 16, 16, state.Config.ChunkSize)
	if sw == nil {
		t.Fatal("spawnSwarmAt returned nil")
	}
	if sw.Satiation != spawnSatiation {
		t.Fatalf("a freshly spawned swarm must start fed (%.0f), got Satiation %.1f", spawnSatiation, sw.Satiation)
	}
	if sw.StarveTimer != 0 {
		t.Fatalf("a fresh swarm must have StarveTimer 0, got %.1f", sw.StarveTimer)
	}
}

// A swarm under the starvation threshold is untouched (the runway the spawn satiation buys); one pinned
// past the threshold loses a cull fraction. This is the guard the predator fix relies on.
func TestStarvationCullsOnlyPastThreshold(t *testing.T) {
	state := newTestState(50)
	m := &Match{}

	fresh := newTestSwarm("fresh", 10, 10, 10)
	fresh.StarveTimer = starvationDeathSecs - 1 // not yet starving
	state.Swarms["fresh"] = fresh
	state.SwarmsBySpecies["fly_common"] = []string{"fresh"}

	starved := newTestSwarm("starved", 10, 20, 20)
	starved.StarveTimer = starvationDeathSecs // starving
	state.Swarms["starved"] = starved
	state.SwarmsBySpecies["fly_common"] = append(state.SwarmsBySpecies["fly_common"], "starved")

	m.processStarvation(nopRuntimeLogger(), nil, state, state.Config.ChunkSize)

	if fresh.Count != 10 {
		t.Fatalf("a swarm under the starvation threshold must not be culled, got %d", fresh.Count)
	}
	if starved.Count != 9 { // 10 - 10% (min 1)
		t.Fatalf("a starved swarm must lose ~10%% (1 of 10), got %d", starved.Count)
	}
}
