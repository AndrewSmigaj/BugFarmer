package world

import (
	"os"
	"testing"

	"bugfarmer/entities"
)

// Stage 1.3 (docs/plans/village-slice.md): the whole zone on the server.

// chdirNakama moves to the nakama directory (two up from world/), where "data/zones/..." resolves, for one test.
func chdirNakama(t *testing.T) {
	t.Helper()
	cwd, _ := os.Getwd()
	if err := os.Chdir("../.."); err != nil {
		t.Fatalf("chdir: %v", err)
	}
	t.Cleanup(func() { _ = os.Chdir(cwd) })
	if _, err := os.Stat("data/zones/crawler_lab/zone.json"); err != nil {
		t.Skipf("crawler_lab zone files not reachable from here: %v", err)
	}
}

// Every chunk of the zone's grid is loaded once; a chunk already loaded (the restore's edited chunks) is kept as it is;
// a chunk file outside the grid is not loaded; a second run changes nothing.
func TestLoadWholeZoneLoadsEveryChunkOnce(t *testing.T) {
	chdirNakama(t)
	state := newTestState(40)
	state.CurrentZone = &ZoneConfig{ZoneID: "crawler_lab", Width: 96, Height: 96} // 3 x 3 chunks
	edited := NewEmptyChunk(1, 1, "dirt")
	state.Chunks[ChunkKey(1, 1)] = edited

	m := &Match{}
	m.loadWholeZone(state, nopRuntimeLogger())
	if len(state.Chunks) != 9 {
		t.Fatalf("want the 9 chunks of a 3 x 3 zone, got %d", len(state.Chunks))
	}
	if state.Chunks[ChunkKey(1, 1)] != edited {
		t.Fatal("a chunk already loaded (the restore's edits) must be kept, not reloaded from its file")
	}
	if _, ok := state.Chunks[ChunkKey(3, 0)]; ok {
		t.Fatal("crawler_lab has a chunk file at 3,0, outside its 96 x 96 grid: it must not be loaded")
	}
	trees, nests := len(state.FruitTreeStates), len(state.NestStates)
	m.loadWholeZone(state, nopRuntimeLogger())
	if len(state.Chunks) != 9 || len(state.FruitTreeStates) != trees || len(state.NestStates) != nests {
		t.Fatal("a second run must change nothing")
	}
}

// Outside the zone's chunk grid every cell is a wall, for players and for every bug (fliers too); inside, the usual
// rules hold.
func TestCellsOutsideTheZoneAreWalls(t *testing.T) {
	chdirNakama(t)
	state := newTestState(40)
	state.CurrentZone = &ZoneConfig{ZoneID: "crawler_lab", Width: 96, Height: 96}
	(&Match{}).loadWholeZone(state, nopRuntimeLogger())
	// A walkable "phantom" chunk just outside, as a chunk request there made before Stage 1.3: still a wall.
	state.Chunks[ChunkKey(3, 0)] = NewEmptyChunk(3, 0, "grass")
	flier := &entities.BugSpecies{FliesOverFences: true}
	for _, p := range [][2]float32{{-0.5, 10}, {10, -0.5}, {96.5, 10}, {10, 96.5}, {200, 200}} {
		if !state.IsBlockedForPlayers(p[0], p[1]) {
			t.Fatalf("players: %v is outside the zone and must be a wall", p)
		}
		if !state.IsBlockedForSpecies(p[0], p[1], flier) {
			t.Fatalf("fliers: %v is outside the zone and must be a wall", p)
		}
	}
	// The open grass inside the centipede pen (the spawn circle the initial-spawn test uses).
	if state.IsBlockedForPlayers(19.5, 36.5) || state.IsBlockedForSpecies(19.5, 36.5, flier) {
		t.Fatal("an open cell inside the zone must stay open")
	}
	if state.ChunkInZone(-1, 0) || state.ChunkInZone(3, 0) || !state.ChunkInZone(2, 2) {
		t.Fatal("ChunkInZone must cover exactly the 3 x 3 grid")
	}
}

// A save holding an edit outside the zone (possible from a "phantom" chunk before Stage 1.3) restores without stopping
// the zone: the edit is left out, the others are applied. Before, the negative coordinate indexed a chunk with a
// negative number (a panic in MatchInit).
func TestRestoreLeavesOutEditsOutsideTheZone(t *testing.T) {
	m := &Match{}
	save := m.buildWorldSave(newTestState(40))
	dirt := "dirt"
	save.CellEdits = append(save.CellEdits,
		GlobalCellEdit{GX: -5, GY: 3, Ground: &dirt},
		GlobalCellEdit{GX: 10, GY: 10, Ground: &dirt},
		GlobalCellEdit{GX: 300, GY: 3, Ground: &dirt})
	fresh := newTestState(40)
	m.restoreWorldSave(fresh, save, nopRuntimeLogger())
	chunk := fresh.Chunks[ChunkKey(0, 0)]
	if chunk == nil || chunk.Ground[10][10] != "dirt" {
		t.Fatal("the edit inside the zone must be applied")
	}
	if len(fresh.Chunks) != 1 {
		t.Fatalf("only the edited chunk inside the zone may be loaded, got %d chunks", len(fresh.Chunks))
	}
}

// Nothing is saved for a chunk outside the zone.
func TestSaveLeavesOutChunksOutsideTheZone(t *testing.T) {
	state := newTestState(40)
	phantom := NewEmptyChunk(-1, 0, "dirt") // differs from the (missing → grass) base on every cell
	state.Chunks[ChunkKey(-1, 0)] = phantom
	save := (&Match{}).buildWorldSave(state)
	for _, e := range save.CellEdits {
		if e.GX < 0 {
			t.Fatalf("an edit outside the zone was saved: %+v", e)
		}
	}
}

// The starting spawn keeps the groups already listed for a species (nest groups founded while a test zone's restore
// set up its edited chunks); before, it emptied the list and those groups were never counted again.
func TestSpawnInitialSwarmsKeepsGroupsAlreadyListed(t *testing.T) {
	chdirNakama(t)
	state := newTestState(40)
	state.SpeciesNextSpawn = map[string]float64{}
	state.StaticSim = false
	state.CurrentZone = &ZoneConfig{ZoneID: "crawler_lab", Width: 96, Height: 96}
	state.Species["fly_common"] = &entities.BugSpecies{Category: "swarm", MinSwarmSize: 5, MaxSwarmSize: 40, SwarmRadius: 4}
	state.CurrentZone.BugSpawning = &BugSpawnConfig{
		SpeciesCaps: map[string]SpeciesCap{"fly_common": {Initial: 2, Max: 40, SwarmSize: 1}},
		SpawnAreas:  []SpawnArea{{ID: "pen", Species: []string{"fly_common"}, Type: "circle", CX: 19, CY: 36, Radius: 8}},
	}
	state.SwarmsBySpecies["fly_common"] = []string{"swarm_founded_earlier"}

	(&Match{}).spawnInitialSwarms(state, nopRuntimeLogger())
	list := state.SwarmsBySpecies["fly_common"]
	if len(list) != 3 || list[0] != "swarm_founded_earlier" {
		t.Fatalf("want the earlier group kept plus 2 new ones, got %v", list)
	}
}

// A zone starts with no events: its start-up (the starting groups, every chunk's fruit trees and nests) logs events while
// nobody is connected, and the first player is told there are none before it — so MatchInit empties the zone's sync
// state. Non-vacuous: crawler_lab's start-up spawns its centipedes (each a SWARM_SPAWNED event).
func TestMatchInitStartsTheZoneWithNoEvents(t *testing.T) {
	chdirNakama(t)
	r := newRegRig(t)
	z := r.startZone("crawler_lab")
	st := z.state
	if len(st.Swarms) == 0 {
		t.Fatal("crawler_lab's start-up must spawn groups (else this test proves nothing)")
	}
	cx, cy := st.zoneChunkGrid()
	if len(st.Chunks) != cx*cy {
		t.Fatalf("the whole zone must be loaded at start: want %d chunks, got %d", cx*cy, len(st.Chunks))
	}
	zone := st.GetZone("crawler_lab")
	if zone == nil {
		t.Fatal("the start-up spawn logs its events on the zone, so the zone must exist")
	}
	if zone.NextSeq != 0 || len(zone.InfluenceLog) != 0 || len(st.PendingInfluence) != 0 {
		t.Fatalf("the zone must start with no events: NextSeq %d, log %d, queued %d",
			zone.NextSeq, len(zone.InfluenceLog), len(st.PendingInfluence))
	}
}
