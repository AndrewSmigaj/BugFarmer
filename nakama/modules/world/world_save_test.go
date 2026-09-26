package world

// Tests for THE PERSISTENCE SYSTEM (world_save.go + persist_classes.go + the legacy importer).
// The definitional gates for §P:
//   - classification completeness (reflection vs the persist_classes.go table)
//   - full round-trip deep-equality on the WORLD-STATE subset
//   - the clock resumes (and LastZoneSaveTick anchors to it)
//   - GroundItemSeq survives (no id re-mint collision)
//   - legacy decode + importer clamps (the OLD compensations live ONLY in the importer)
//   - the generation guard (newer save wins)
//
// Run inside the builder image:  go test ./modules/world/ -run 'WorldSave|Persist|Legacy' -v

import (
	"encoding/json"
	"math/rand"
	"reflect"
	"testing"

	"bugfarmer/entities"
)

// newPersistTestState builds a WorldState with every registry the save system touches.
func newPersistTestState() *WorldState {
	return &WorldState{
		Config:          WorldConfig{ChunkSize: 32, TickRate: 10},
		Tuning:          DefaultTuning(),
		Rng:             rand.New(rand.NewSource(1)),
		CurrentZone:     &ZoneConfig{ZoneID: "testzone"},
		Chunks:          map[string]*ChunkData{},
		Swarms:          map[string]*entities.SwarmState{},
		SwarmsBySpecies: map[string][]string{},
		Species: map[string]*entities.BugSpecies{
			"wasp_common": {Category: "swarm", SwarmRadius: 2.5, WanderRadius: 12},
		},
		ZoneStates:      map[string]*ZoneState{},
		GroundItems:     map[string]*entities.GroundItem{},
		Stations:        map[string]*entities.StationState{},
		Entities:        map[string]*EntityDef{},
		CropStates:      map[string]*entities.CropState{},
		FruitTreeStates: map[string]*entities.FruitTreeState{},
		NestStates:      map[string]*entities.NestState{},
		HostPlantStates: map[string]*entities.HostPlantState{},
		BroodStates:     map[string]*entities.BroodState{},
		ForagePools:     map[string]*entities.ForagePoolState{},
		GnawDamage:      map[string]int{},
		Containers:      map[string]*ContainerState{},
		CraftStations:   map[string]*CraftStationState{},
	}
}

// TestPersistClassificationComplete is THE enforcement: every WorldState field must be classified
// in persist_classes.go, and every table entry must name a real field. A new field without a
// classification fails here BY NAME — "forgot to persist X" can't happen silently.
func TestPersistClassificationComplete(t *testing.T) {
	typ := reflect.TypeOf(WorldState{})
	structFields := map[string]bool{}
	for i := 0; i < typ.NumField(); i++ {
		name := typ.Field(i).Name
		structFields[name] = true
		if _, ok := persistClasses[name]; !ok {
			t.Errorf("WorldState.%s has NO persistence classification — add it to persist_classes.go "+
				"(WORLD-STATE with its WorldSave field, PER-RUN with why, or CONFIG with its source)", name)
		}
	}
	for name := range persistClasses {
		if !structFields[name] {
			t.Errorf("persist_classes.go classifies %q but WorldState has no such field — remove the stale entry", name)
		}
	}
	// Every WORLD-STATE class must round-trip: sanity-pin the count so a reclassification is a
	// conscious edit here too.
	worldStateFields := 0
	for _, e := range persistClasses {
		if e.Class == classWorldState {
			worldStateFields++
		}
	}
	if worldStateFields != 21 {
		t.Errorf("WORLD-STATE field count = %d, want 21 (clock+rollover, 6 sky/offset fields, GroundItemSeq, "+
			"Swarms, GroundItems, Chunks, GnawDamage, and the 9 sidecar registries) — update this pin when §P grows", worldStateFields)
	}
}

// buildPopulatedState fills a state with one of EVERYTHING the document persists, using values
// that would expose clamping/losses (non-zero tick stamps, live references, both brood key kinds).
func buildPopulatedState(t *testing.T) *WorldState {
	t.Helper()
	s := newPersistTestState()

	// The clock + sky + counters.
	s.TickCount = 5000
	s.LastRolloverDay = 3
	s.DayOffsetTicks = 111
	s.WeatherKind = "rain"
	s.WeatherUntilTick = 5600
	s.ScheduledRainTick = 7000
	s.DroughtUntilTick = 0
	s.GroundItemSeq = 42

	// An edited chunk: one ground change + one player-placed occupant.
	chunk := NewEmptyChunk(0, 0, "grass")
	chunk.Ground[2][3] = "dirt"
	chunk.Occupants[5][6] = json.RawMessage(`{"id":"fence_wood","anchor":true}`)
	s.Chunks[ChunkKey(0, 0)] = chunk

	// A full-fidelity swarm: maps, stamps, nest membership, action state — everything that the
	// legacy lossy save dropped.
	sw := &entities.SwarmState{
		ID:        "swarm-uuid-1",
		SpeciesID: "wasp_common",
		Position:  entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 10.5, LocalY: 11.25},
		Radius:    2.5, // == species SwarmRadius (refresh must be a no-op for DeepEqual)
		Count:     7,
		HomePos:   entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 8.5, LocalY: 8.5},
		WanderRad: 12, // == species WanderRadius
		Phase:     "homing",
		Satiation: 92.5,
		ConditionValue: 55.5,
		NestKey:        "8,8",
		CarryingBrood:  true,
		HomingStartTick: 4900,
		NextThinkTick:   5030,
		DeathTick:       map[int]int64{2: 9000, 5: 12000},
		RemovedBugIDs:   map[int]bool{1: true},
		NextBugID:       8,
		BugHP:           map[int]int{3: 1},
		ActionState:     "gnaw",
		ActionUntilTick: 5020,
		GnawKey:         "30,30",
		DefendTargetID:  "user-abc", // stable userID — persists AS-IS
	}
	s.Swarms[sw.ID] = sw
	s.SwarmsBySpecies[sw.SpeciesID] = []string{sw.ID}

	// Every sidecar registry, tick stamps deliberately NON-zero (they must survive un-clamped).
	s.CropStates["3,2"] = &entities.CropState{PlantID: "p1", PlantType: "tomato", GridX: 3, GridY: 2, Stage: 2, HP: 90, Water: 4, PlantedTick: 4000}
	s.FruitTreeStates["10,10"] = &entities.FruitTreeState{TreeID: "t1", EntityID: "tree_apple", GridX: 10, GridY: 10, FruitCount: 2, MaxFruit: 4, LastFallTick: 4321, LastHarvestTick: 4500, WaterLevel: 2, LastWaterDay: 3}
	s.Stations[entities.StationKey(12, 12)] = &entities.StationState{Key: entities.StationKey(12, 12), EntityID: "compost_bin", GridX: 12, GridY: 12, InputCount: 3, ProcessProgress: 40}
	s.Containers[ContainerKey(14, 14)] = &ContainerState{Key: ContainerKey(14, 14), EntityID: "chest", GridX: 14, GridY: 14, Slots: []InventorySlot{{ItemID: "acorn", Count: 5}}}
	cf := &CraftStationState{Key: CraftStationKey(16, 16), EntityID: "workbench", GridX: 16, GridY: 16, Output: []InventorySlot{{ItemID: "plank", Count: 2}}, Procs: []CraftProcessor{{Recipe: "plank", Queue: 3, Progress: 17}}}
	s.CraftStations[cf.Key] = cf
	s.NestStates["8,8"] = &entities.NestState{GridX: 8, GridY: 8, EntityID: "wasp_nest", SpeciesID: "wasp_common", Brood: 4, ResidentSwarmID: "swarm-uuid-1", RehatchAtTick: 5100, SmokedUntilTick: 5200, Honey: 1.5, Founded: true}
	s.ForagePools["20,20"] = &entities.ForagePoolState{EntityID: "flower_wild", GridX: 20, GridY: 20, Nectar: 33.5}
	s.HostPlantStates["22,22"] = &entities.HostPlantState{EntityID: "milkweed", GridX: 22, GridY: 22, Capacity: 12.5}
	s.BroodStates["24,24"] = &entities.BroodState{GridX: 24, GridY: 24, SpeciesID: "butterfly_meadow", Eggs: 2, Maggots: 1, SourceKind: "host_plant", CapEggs: 12}
	s.BroodStates["g:26,26"] = &entities.BroodState{GridX: 26, GridY: 26, SpeciesID: "fly_common", Eggs: 4, SourceKind: "ground_pile", SourceID: "carrion_7", CapEggs: 8}
	s.GnawDamage["30,30"] = 2 // a half-chewed fence

	s.putGroundItem(&entities.GroundItem{ID: "carrion_7", ItemType: "dead_millipede", Count: 1,
		Position: entities.EntityPosition{ChunkX: 0, ChunkY: 0, LocalX: 26.5, LocalY: 26.5}, FoodValue: 80, IsCarrion: true})
	return s
}

// TestWorldSaveRoundTrip: build → marshal → unmarshal → restore into a FRESH state → the entire
// WORLD-STATE subset is deep-equal. No clamps, no losses, no relinking.
func TestWorldSaveRoundTrip(t *testing.T) {
	m := &Match{}
	src := buildPopulatedState(t)

	ws := m.buildWorldSave(src)
	if ws == nil {
		t.Fatal("buildWorldSave returned nil")
	}
	data, err := json.Marshal(ws)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var decoded WorldSave
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}

	dst := newPersistTestState()
	m.restoreWorldSave(dst, &decoded, nopRuntimeLogger())

	// The clock + scalars.
	if dst.TickCount != 5000 || dst.LastRolloverDay != 3 || dst.DayOffsetTicks != 111 {
		t.Fatalf("clock: got tick=%d rollover=%d offset=%d", dst.TickCount, dst.LastRolloverDay, dst.DayOffsetTicks)
	}
	if dst.WeatherKind != "rain" || dst.WeatherUntilTick != 5600 || dst.ScheduledRainTick != 7000 {
		t.Fatalf("weather: got %q until=%d rain_at=%d", dst.WeatherKind, dst.WeatherUntilTick, dst.ScheduledRainTick)
	}
	if dst.GroundItemSeq != 42 {
		t.Fatalf("GroundItemSeq = %d, want 42", dst.GroundItemSeq)
	}

	// The full registries, deep-equal (the definitional §P gate).
	checks := []struct {
		name     string
		got, want interface{}
	}{
		{"Swarms", dst.Swarms, src.Swarms},
		{"CropStates", dst.CropStates, src.CropStates},
		{"FruitTreeStates", dst.FruitTreeStates, src.FruitTreeStates},
		{"Stations", dst.Stations, src.Stations},
		{"Containers", dst.Containers, src.Containers},
		{"CraftStations", dst.CraftStations, src.CraftStations},
		{"NestStates", dst.NestStates, src.NestStates},
		{"ForagePools", dst.ForagePools, src.ForagePools},
		{"HostPlantStates", dst.HostPlantStates, src.HostPlantStates},
		{"BroodStates", dst.BroodStates, src.BroodStates},
		{"GnawDamage", dst.GnawDamage, src.GnawDamage},
		{"GroundItems", dst.GroundItems, src.GroundItems},
	}
	for _, c := range checks {
		if !reflect.DeepEqual(c.got, c.want) {
			t.Errorf("%s did not round-trip:\n got: %+v\nwant: %+v", c.name, c.got, c.want)
		}
	}

	// The tick stamps that the OLD system clamped must survive intact.
	if tr := dst.FruitTreeStates["10,10"]; tr.LastFallTick != 4321 || tr.LastHarvestTick != 4500 {
		t.Errorf("tree stamps clamped: LastFallTick=%d LastHarvestTick=%d (want 4321/4500)", tr.LastFallTick, tr.LastHarvestTick)
	}
	if n := dst.NestStates["8,8"]; n.RehatchAtTick != 5100 || n.SmokedUntilTick != 5200 || n.ResidentSwarmID != "swarm-uuid-1" {
		t.Errorf("nest lost state: rehatch=%d smoked=%d resident=%q", n.RehatchAtTick, n.SmokedUntilTick, n.ResidentSwarmID)
	}

	// The swarm keeps its IDENTITY (the root fix: no fresh minting, references stay valid).
	if _, ok := dst.Swarms["swarm-uuid-1"]; !ok {
		t.Fatal("swarm identity lost — restored under a different id")
	}
	if got := dst.SwarmsBySpecies["wasp_common"]; len(got) != 1 || got[0] != "swarm-uuid-1" {
		t.Errorf("SwarmsBySpecies not rebuilt: %v", got)
	}

	// The edited chunk was EAGER-loaded with its edits applied.
	ch := dst.Chunks[ChunkKey(0, 0)]
	if ch == nil {
		t.Fatal("edited chunk not eager-loaded at restore")
	}
	if got := groundAt(ch, 3, 2); got != "dirt" {
		t.Errorf("ground edit lost: cell(3,2) = %q, want dirt", got)
	}
	if !occCellEqual(occAt(ch, 6, 5), json.RawMessage(`{"id":"fence_wood","anchor":true}`)) {
		t.Errorf("occupant edit lost at cell(6,5): %s", string(occAt(ch, 6, 5)))
	}
}

// TestWorldSaveResumeClock: LastZoneSaveTick anchors to the restored tick so the autosave delta
// doesn't see "forever ago" and fire immediately.
func TestWorldSaveResumeClock(t *testing.T) {
	m := &Match{}
	src := buildPopulatedState(t)
	ws := m.buildWorldSave(src)

	dst := newPersistTestState()
	m.restoreWorldSave(dst, ws, nopRuntimeLogger())
	if dst.LastZoneSaveTick != 5000 {
		t.Fatalf("LastZoneSaveTick = %d, want the restored tick 5000", dst.LastZoneSaveTick)
	}
}

// TestGroundItemSeqNoCollision: after a restore, a newly minted item id must not collide with
// (and silently overwrite) a restored item — the latent pre-§P bug.
func TestGroundItemSeqNoCollision(t *testing.T) {
	m := &Match{}
	src := newPersistTestState()
	src.GroundItemSeq = 7
	src.putGroundItem(&entities.GroundItem{ID: src.nextItemID("drop"), ItemType: "acorn", Count: 1}) // drop_8

	ws := m.buildWorldSave(src)
	dst := newPersistTestState()
	m.restoreWorldSave(dst, ws, nopRuntimeLogger())

	newID := dst.nextItemID("drop")
	if _, exists := dst.GroundItems[newID]; exists {
		t.Fatalf("freshly minted id %q collides with a restored item", newID)
	}
	if newID != "drop_9" {
		t.Fatalf("minted %q, want drop_9 (seq must resume at 8)", newID)
	}
}

// TestWorldSaveEphemeralZoneSkipsPopulation: tuning zones neither save nor restore swarms/items —
// every run starts fresh (the reproducibility guard).
func TestWorldSaveEphemeralZoneSkipsPopulation(t *testing.T) {
	m := &Match{}
	src := buildPopulatedState(t)
	src.CurrentZone.EphemeralSwarms = true

	ws := m.buildWorldSave(src)
	if len(ws.Swarms) != 0 || len(ws.GroundItems) != 0 {
		t.Fatalf("ephemeral zone persisted population: %d swarms, %d items", len(ws.Swarms), len(ws.GroundItems))
	}
	// Farm state still persists (a test zone's placed fences shouldn't vanish).
	if len(ws.Nests) == 0 || len(ws.CellEdits) == 0 {
		t.Fatal("ephemeral zone dropped farm/sidecar state — only the population should be skipped")
	}
}

// TestWorldSaveGenerationGuard: the pure decision — a stored doc STRICTLY ahead wins; same-tick
// and older docs are overwritten.
func TestWorldSaveGenerationGuard(t *testing.T) {
	if !worldSaveSuperseded(6000, 5000) {
		t.Error("stored 6000 vs snapshot 5000: the newer stored save must win (skip the write)")
	}
	if worldSaveSuperseded(5000, 5000) {
		t.Error("equal ticks are the same generation — the write must proceed")
	}
	if worldSaveSuperseded(4000, 5000) {
		t.Error("stored 4000 vs snapshot 5000: the snapshot is newer — the write must proceed")
	}
}

// TestLegacyChunkImportClamps: the OLD compensations live ONLY in the importer — legacy stamps
// (written against a clock that reset to 0) are clamped, and the dangling resident ref is cleared.
func TestLegacyChunkImportClamps(t *testing.T) {
	m := &Match{}
	s := newPersistTestState()

	legacyJSON := `{
		"version": 1, "zone_id": "testzone", "cx": 0, "cy": 0,
		"cells": [{"lx": 3, "ly": 2, "ground": "dirt"}],
		"trees": [{"TreeID": "t1", "EntityID": "tree_apple", "GridX": 10, "GridY": 10, "FruitCount": 2, "LastFallTick": 4321, "LastHarvestTick": 4500}],
		"nests": [{"GridX": 8, "GridY": 8, "EntityID": "wasp_nest", "SpeciesID": "wasp_common", "Brood": 4, "ResidentSwarmID": "stale-id", "RehatchAtTick": 5100, "SmokedUntilTick": 5200}]
	}`
	var cs ChunkSave
	if err := json.Unmarshal([]byte(legacyJSON), &cs); err != nil {
		t.Fatalf("legacy decode: %v", err)
	}

	chunk := NewEmptyChunk(0, 0, "grass")
	s.Chunks[ChunkKey(0, 0)] = chunk
	m.applyLegacyChunkSave(s, chunk, &cs)

	if got := groundAt(chunk, 3, 2); got != "dirt" {
		t.Errorf("legacy cell edit not applied: %q", got)
	}
	tr := s.FruitTreeStates["10,10"]
	if tr == nil || tr.LastFallTick != 0 || tr.LastHarvestTick != 0 {
		t.Errorf("legacy tree stamps must be CLAMPED by the importer: %+v", tr)
	}
	if tr != nil && tr.FruitCount != 2 {
		t.Errorf("legacy tree payload lost: FruitCount=%d", tr.FruitCount)
	}
	n := s.NestStates["8,8"]
	if n == nil || n.RehatchAtTick != 0 || n.SmokedUntilTick != 0 || n.ResidentSwarmID != "" {
		t.Errorf("legacy nest must be clamped + resident cleared (recovery self-heals): %+v", n)
	}
	if n != nil && n.Brood != 4 {
		t.Errorf("legacy nest payload lost: Brood=%d", n.Brood)
	}
}

// TestSwarmStateJSONTags: the save format is the TAGS, not the Go names — a rename must not be
// able to silently orphan saved data. Spot-check the load-bearing fields.
func TestSwarmStateJSONTags(t *testing.T) {
	sw := &entities.SwarmState{ID: "x", SpeciesID: "wasp_common", Count: 3, NestKey: "1,2",
		DeathTick: map[int]int64{4: 100}, RemovedBugIDs: map[int]bool{0: true}, BugHP: map[int]int{1: 2}}
	data, err := json.Marshal(sw)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		t.Fatalf("unmarshal to map: %v", err)
	}
	for _, key := range []string{"id", "species", "count", "nest_key", "death_tick", "removed_bugs", "bug_hp"} {
		if _, ok := raw[key]; !ok {
			t.Errorf("SwarmState json missing tagged key %q — got keys %v", key, keysOf(raw))
		}
	}
	var back entities.SwarmState
	if err := json.Unmarshal(data, &back); err != nil {
		t.Fatalf("round-trip unmarshal: %v", err)
	}
	if !reflect.DeepEqual(&back, sw) {
		t.Errorf("SwarmState round-trip mismatch:\n got %+v\nwant %+v", &back, sw)
	}
}

func keysOf(m map[string]json.RawMessage) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
