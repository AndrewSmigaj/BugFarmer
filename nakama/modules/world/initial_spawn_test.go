package world

import (
	"os"
	"testing"

	"bugfarmer/entities"
)

// TestInitialSpawnPlacesBugsWithEmptyChunkCache is the regression guard for the initial-spawn fix.
//
// At MatchInit the chunk cache (state.Chunks) is EMPTY — chunks load lazily on player subscribe. So the
// spawn walkability check must consult the AUTHORED map on disk (IsBlockedForSpawn -> chunkForCollision),
// or every cell reads "blocked" and spawnInitialSwarms places ZERO bugs ("Seeded world with 0 swarms").
// This runs the real spawn against the real crawler_lab zone files with an EMPTY cache and asserts the
// configured bugs actually land. Pre-fix this would have produced 0 swarms.
func TestInitialSpawnPlacesBugsWithEmptyChunkCache(t *testing.T) {
	// LoadChunk resolves "data/zones/..." relative to CWD; hop to the nakama dir (two up from world/).
	cwd, _ := os.Getwd()
	if err := os.Chdir("../.."); err != nil {
		t.Fatalf("chdir: %v", err)
	}
	defer os.Chdir(cwd)
	if _, err := os.Stat("data/zones/crawler_lab/zone.json"); err != nil {
		t.Skipf("crawler_lab zone files not reachable from here: %v", err)
	}

	state := newTestState(40)
	state.SpeciesNextSpawn = map[string]float64{} // spawnInitialSwarms writes this; newTestState omits it
	state.StaticSim = false
	state.CurrentZone = &ZoneConfig{ZoneID: "crawler_lab", Width: 96, Height: 96}
	state.Species["fly_common"] = &entities.BugSpecies{
		Category: "swarm", MinSwarmSize: 5, MaxSwarmSize: 40, SwarmRadius: 4,
	}
	state.CurrentZone.BugSpawning = &BugSpawnConfig{
		SpeciesCaps: map[string]SpeciesCap{
			"fly_common": {Initial: 6, Max: 40, SwarmSize: 1},
		},
		SpawnAreas: []SpawnArea{
			// A circle inside the crawler_lab pen (open grass) — same shape the real zone uses.
			{ID: "pen", Species: []string{"fly_common"}, Type: "circle", CX: 19, CY: 36, Radius: 8},
		},
	}
	// state.Chunks intentionally EMPTY — the exact MatchInit condition the fix targets.

	(&Match{}).spawnInitialSwarms(state, nopRuntimeLogger())

	if len(state.Swarms) == 0 {
		t.Fatalf("initial spawn placed ZERO swarms with an empty chunk cache — the authored-map walkability fix is broken")
	}
	if len(state.Swarms) != 6 {
		t.Fatalf("expected all 6 initial swarms placed in the open pen, got %d", len(state.Swarms))
	}
	t.Logf("OK: placed %d swarm(s) from an empty chunk cache (fix working)", len(state.Swarms))
}
