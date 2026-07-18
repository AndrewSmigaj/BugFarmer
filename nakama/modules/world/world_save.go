package world

// THE PERSISTENCE SYSTEM (§P of the plan; docs/product/architecture — persistence section).
//
// Principle: THE WORLD SAVES AS-IS AND TIME CONTINUES.
//
//   - Every WorldState field is classified exactly once in persist_classes.go
//     (WORLD-STATE = saved here | PER-RUN = never saved | CONFIG = reloaded from data files).
//     A reflection test fails the build if a new field is left unclassified.
//   - The whole zone persists as ONE document (WorldSave): marshal the structs as they are,
//     unmarshal them back, resume the clock. No lossy rebuilds, no tick-stamp clamps, no
//     reference relinking — those were all compensations for resetting the clock and reminting
//     swarm identities, and both roots are gone.
//   - WorldSave.Tick doubles as the GENERATION STAMP: a writer refuses to replace a document
//     carrying a higher tick, so a slow async save can never roll the zone back over a newer one
//     (the empty-transition save racing the terminate save).
//   - Old multi-record saves (meta + per-chunk + swarms) are imported ONCE by the legacy importer
//     in zone_persist.go and deleted after the first successful document write.

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

const worldSaveVersion = 1

// GlobalCellEdit is one player-made map change, as a semantic diff against the AUTHORED zone
// (global coordinates). Ground nil = unchanged; OccSet with Occ nil = an authored occupant was
// removed. The diff (not a full map copy) is what keeps authored-zone updates compatible with
// old saves and the document small.
type GlobalCellEdit struct {
	GX     int             `json:"gx"`
	GY     int             `json:"gy"`
	Ground *string         `json:"ground,omitempty"`
	Occ    json.RawMessage `json:"occ,omitempty"`
	OccSet bool            `json:"occ_set,omitempty"`
}

// WorldSave is the one persistence document for a zone: every WORLD-STATE field of WorldState,
// saved byte-faithfully. See persist_classes.go for the field-by-field ledger.
type WorldSave struct {
	Version int    `json:"version"`
	ZoneID  string `json:"zone_id"`
	SavedAt int64  `json:"saved_at"`

	// The world clock — restored FIRST; every persisted tick-stamp below is valid against it.
	// Also the generation stamp (see writeWorldSave).
	Tick            int64 `json:"tick"`
	LastRolloverDay int64 `json:"last_rollover_day"`

	// Sky state: you log back into the same evening and the same rainstorm.
	DayOffsetTicks    int64  `json:"day_offset_ticks,omitempty"`
	WeatherKind       string `json:"weather,omitempty"`
	WeatherUntilTick  int64  `json:"weather_until,omitempty"`
	ScheduledRainTick int64  `json:"rain_at,omitempty"`
	DroughtUntilTick  int64  `json:"drought_until,omitempty"`

	// The ground-item id counter — persisted so a new drop can never re-mint a restored item's id
	// (which silently overwrote the item and skewed the FindNearbyFood tiebreak).
	GroundItemSeq int64 `json:"ground_item_seq,omitempty"`

	CellEdits []GlobalCellEdit `json:"cell_edits,omitempty"`
	Gnaw      map[string]int   `json:"gnaw,omitempty"` // half-chewed fences stay half-chewed

	Swarms        []*entities.SwarmState      `json:"swarms"`
	Crops         []*entities.CropState       `json:"crops,omitempty"`
	Trees         []*entities.FruitTreeState  `json:"trees,omitempty"`
	Stations      []*entities.StationState    `json:"stations,omitempty"`
	Containers    []*ContainerState           `json:"containers,omitempty"`
	CraftStations []*CraftStationState        `json:"craft_stations,omitempty"`
	Nests         []*entities.NestState       `json:"nests,omitempty"`
	ForagePools   []*entities.ForagePoolState `json:"forage_pools,omitempty"`
	HostPlants    []*entities.HostPlantState  `json:"host_plants,omitempty"`
	Broods        []*entities.BroodState      `json:"broods,omitempty"`
	GroundItems   []*entities.GroundItem      `json:"ground_items,omitempty"`
}

func worldSaveKey(zoneKey string) string { return zoneKey + ":world" }

// ---- build (snapshot, synchronous on the match goroutine) ----

// buildWorldSave snapshots the zone's entire WORLD-STATE into one document. Registries are
// walked in sorted key order so the marshaled document is stable (diff-able, test-friendly).
func (m *Match) buildWorldSave(state *WorldState) *WorldSave {
	if state.CurrentZone == nil {
		return nil
	}
	ws := &WorldSave{
		Version: worldSaveVersion,
		ZoneID:  state.CurrentZone.ZoneID,
		SavedAt: time.Now().Unix(),

		Tick:            state.TickCount,
		LastRolloverDay: state.LastRolloverDay,

		DayOffsetTicks:    state.DayOffsetTicks,
		WeatherKind:       state.WeatherKind,
		WeatherUntilTick:  state.WeatherUntilTick,
		ScheduledRainTick: state.ScheduledRainTick,
		DroughtUntilTick:  state.DroughtUntilTick,

		GroundItemSeq: state.GroundItemSeq,
	}

	// Cell edits: the semantic diff of every LOADED chunk vs its authored base. Chunks that were
	// never loaded cannot have been edited.
	zonePath := "data/zones/" + state.CurrentZone.ZoneID
	for _, chunkKey := range sortedStringKeys(state.Chunks) {
		live := state.Chunks[chunkKey]
		if live == nil {
			continue
		}
		cx, cy := live.ChunkX, live.ChunkY
		base, err := LoadChunk(zonePath, cx, cy)
		if err != nil {
			base = NewEmptyChunk(cx, cy, "grass") // same fallback the subscribe path uses
		}
		for ly := 0; ly < ChunkSize; ly++ {
			for lx := 0; lx < ChunkSize; lx++ {
				edit := GlobalCellEdit{GX: cx*ChunkSize + lx, GY: cy*ChunkSize + ly}
				changed := false
				if liveG, baseG := groundAt(live, lx, ly), groundAt(base, lx, ly); liveG != baseG {
					g := liveG
					edit.Ground = &g
					changed = true
				}
				liveO, baseO := occAt(live, lx, ly), occAt(base, lx, ly)
				if !occCellEqual(liveO, baseO) {
					edit.Occ = liveO
					edit.OccSet = true
					changed = true
				}
				if changed {
					ws.CellEdits = append(ws.CellEdits, edit)
				}
			}
		}
	}

	if len(state.GnawDamage) > 0 {
		ws.Gnaw = make(map[string]int, len(state.GnawDamage))
		for k, v := range state.GnawDamage {
			ws.Gnaw[k] = v
		}
	}

	// Registries, whole structs, sorted for stable output. Swarms/GroundItems are skipped on
	// EphemeralSwarms test zones (fresh-start tuning runs must not inherit populations/piles).
	ephemeral := state.CurrentZone.EphemeralSwarms
	if !ephemeral {
		ws.Swarms = make([]*entities.SwarmState, 0, len(state.Swarms))
		for _, id := range sortedStringKeys(state.Swarms) {
			if sw := state.Swarms[id]; sw != nil && sw.Count > 0 {
				ws.Swarms = append(ws.Swarms, sw)
			}
		}
		for _, id := range sortedStringKeys(state.GroundItems) {
			ws.GroundItems = append(ws.GroundItems, state.GroundItems[id])
		}
	} else {
		ws.Swarms = []*entities.SwarmState{}
	}
	for _, k := range sortedStringKeys(state.CropStates) {
		ws.Crops = append(ws.Crops, state.CropStates[k])
	}
	for _, k := range sortedStringKeys(state.FruitTreeStates) {
		ws.Trees = append(ws.Trees, state.FruitTreeStates[k])
	}
	for _, k := range sortedStringKeys(state.Stations) {
		ws.Stations = append(ws.Stations, state.Stations[k])
	}
	for _, k := range sortedStringKeys(state.Containers) {
		ws.Containers = append(ws.Containers, state.Containers[k])
	}
	for _, k := range sortedStringKeys(state.CraftStations) {
		ws.CraftStations = append(ws.CraftStations, state.CraftStations[k])
	}
	for _, k := range sortedStringKeys(state.NestStates) {
		ws.Nests = append(ws.Nests, state.NestStates[k])
	}
	for _, k := range sortedStringKeys(state.ForagePools) {
		ws.ForagePools = append(ws.ForagePools, state.ForagePools[k])
	}
	for _, k := range sortedStringKeys(state.HostPlantStates) {
		ws.HostPlants = append(ws.HostPlants, state.HostPlantStates[k])
	}
	for _, k := range sortedStringKeys(state.BroodStates) {
		ws.Broods = append(ws.Broods, state.BroodStates[k])
	}
	return ws
}

// snapshotWorldSaveBytes marshals the document synchronously on the match goroutine — the bytes
// are a frozen snapshot, immune to later WorldState mutation, safe to write async.
func (m *Match) snapshotWorldSaveBytes(state *WorldState) (string, int64) {
	ws := m.buildWorldSave(state)
	if ws == nil {
		return "", 0
	}
	data, err := json.Marshal(ws)
	if err != nil {
		return "", 0
	}
	return string(data), ws.Tick
}

// ---- write (with the generation guard) ----

// worldSaveSuperseded is the generation guard's decision: a stored document STRICTLY ahead of the
// snapshot wins (equal ticks are the same generation — overwriting is fine). This is what stops a
// slow async empty-transition write from rolling the zone back over a newer terminate save.
func worldSaveSuperseded(storedTick, snapshotTick int64) bool {
	return storedTick > snapshotTick
}

// writeWorldSave stores the document — unless storage already holds one with a HIGHER tick
// (a newer save from a racing writer: e.g. the async empty-transition save finishing after the
// synchronous terminate save). On the first successful write it deletes the legacy multi-record
// save, completing the one-time migration.
func writeWorldSave(ctx context.Context, nk runtime.NakamaModule, logger runtime.Logger, zoneID, value string, tick int64) {
	zoneKey := ZoneStateKey(zoneID, "")
	key := worldSaveKey(zoneKey)

	if existing, err := loadWorldSave(ctx, nk, zoneKey); err == nil && existing != nil && worldSaveSuperseded(existing.Tick, tick) {
		logger.Info("Zone %s: skipped world-save write (stored tick %d > snapshot tick %d — newer save wins)",
			zoneID, existing.Tick, tick)
		return
	}

	_, err := nk.StorageWrite(ctx, []*runtime.StorageWrite{{
		Collection:      ZoneStateCollection,
		Key:             key,
		UserID:          "", // system-owned (shared zone)
		Value:           value,
		PermissionRead:  2,
		PermissionWrite: 0,
	}})
	if err != nil {
		logger.Error("Zone %s: world-save write failed: %v", zoneID, err)
		return
	}
	deleteLegacyZoneRecords(ctx, nk, logger, zoneKey, zoneID)
}

// loadWorldSave reads the zone's document. (nil, nil) when absent.
func loadWorldSave(ctx context.Context, nk runtime.NakamaModule, zoneKey string) (*WorldSave, error) {
	objs, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: ZoneStateCollection, Key: worldSaveKey(zoneKey), UserID: "",
	}})
	if err != nil || len(objs) == 0 {
		return nil, err
	}
	var ws WorldSave
	if err := json.Unmarshal([]byte(objs[0].Value), &ws); err != nil {
		return nil, err
	}
	if ws.Version != worldSaveVersion {
		return nil, nil // future-versioned doc: treat as absent rather than misread
	}
	return &ws, nil
}

// ---- restore (eager, at MatchInit, before any client joins) ----

// restoreWorldSave applies the document to a fresh WorldState. Order matters and lives HERE, in
// one function: (1) the clock + scalars, (2) the registries (so the init scans skip-if-present),
// (3) swarms, (4) the edited chunks — each loaded, overlaid, and init-scanned eagerly.
func (m *Match) restoreWorldSave(state *WorldState, ws *WorldSave, logger runtime.Logger) {
	// (1) The clock first — everything else's tick-stamps are relative to it.
	state.TickCount = ws.Tick
	state.LastZoneSaveTick = ws.Tick // else the autosave delta sees "forever ago" and fires at once
	state.LastRolloverDay = ws.LastRolloverDay
	state.DayOffsetTicks = ws.DayOffsetTicks
	state.WeatherKind = ws.WeatherKind
	state.WeatherUntilTick = ws.WeatherUntilTick
	state.ScheduledRainTick = ws.ScheduledRainTick
	state.DroughtUntilTick = ws.DroughtUntilTick
	state.GroundItemSeq = ws.GroundItemSeq

	// (2) Registries — keys re-derived from anchor cells (stable grid coordinates).
	for _, c := range ws.Crops {
		state.CropStates[gridKey(c.GridX, c.GridY)] = c
	}
	for _, t := range ws.Trees {
		state.FruitTreeStates[gridKey(t.GridX, t.GridY)] = t
	}
	for _, st := range ws.Stations {
		state.Stations[entities.StationKey(st.GridX, st.GridY)] = st
	}
	for _, ct := range ws.Containers {
		state.Containers[ContainerKey(ct.GridX, ct.GridY)] = ct
	}
	for _, cf := range ws.CraftStations {
		ensureProcs(state, cf) // craft-slots legacy fold + def top-up (unchanged behavior)
		state.CraftStations[CraftStationKey(cf.GridX, cf.GridY)] = cf
	}
	for _, n := range ws.Nests {
		state.NestStates[gridKey(n.GridX, n.GridY)] = n
	}
	for _, fp := range ws.ForagePools {
		state.ForagePools[gridKey(fp.GridX, fp.GridY)] = fp
	}
	for _, hp := range ws.HostPlants {
		state.HostPlantStates[gridKey(hp.GridX, hp.GridY)] = hp
	}
	for _, br := range ws.Broods {
		key := broodKey(br.GridX, br.GridY)
		if br.SourceKind == "ground_pile" {
			key = "g:" + key
		}
		state.BroodStates[key] = br
	}
	for k, v := range ws.Gnaw {
		state.GnawDamage[k] = v
	}
	ephemeral := state.CurrentZone != nil && state.CurrentZone.EphemeralSwarms
	if !ephemeral {
		for _, gi := range ws.GroundItems {
			state.putGroundItem(gi)
		}
	}

	// (3) Swarms — as they were, identities included. The only fixup is refreshing the
	// CONFIG-DERIVED fields from the live species def (a rebalance must reach saved swarms);
	// the player-ref field DefendTargetID holds a stable userID and self-heals.
	if !ephemeral {
		for _, sw := range ws.Swarms {
			if sw == nil || sw.Count <= 0 {
				continue
			}
			species := state.Species[sw.SpeciesID]
			if species == nil {
				continue // species removed from data — drop its swarms
			}
			sw.Radius = species.SwarmRadius
			sw.WanderRad = species.WanderRadius
			state.Swarms[sw.ID] = sw
			state.SwarmsBySpecies[sw.SpeciesID] = append(state.SwarmsBySpecies[sw.SpeciesID], sw.ID)
		}
	}

	// (4) Edited chunks — loaded and scanned NOW so their occupants exist before any client
	// (and before the zone-wide collision map builds). Untouched chunks keep loading lazily.
	touched := map[string][2]int{}
	for _, e := range ws.CellEdits {
		cx, cy := e.GX/ChunkSize, e.GY/ChunkSize
		touched[ChunkKey(cx, cy)] = [2]int{cx, cy}
	}
	zonePath := "data/zones/" + ws.ZoneID
	for _, chunkKey := range sortedStringKeys(touched) {
		cx, cy := touched[chunkKey][0], touched[chunkKey][1]
		if _, exists := state.Chunks[chunkKey]; exists {
			continue
		}
		chunk, err := LoadChunk(zonePath, cx, cy)
		if err != nil {
			chunk = NewEmptyChunk(cx, cy, "grass")
		}
		for _, e := range ws.CellEdits {
			if e.GX/ChunkSize != cx || e.GY/ChunkSize != cy {
				continue
			}
			lx, ly := e.GX%ChunkSize, e.GY%ChunkSize
			if e.Ground != nil {
				chunk.Ground[ly][lx] = *e.Ground
			}
			if e.OccSet {
				chunk.Occupants[ly][lx] = e.Occ
			}
		}
		state.Chunks[chunkKey] = chunk
		m.initFruitTreesInChunk(state, chunk, cx, cy, logger)
		m.initNestsInChunk(state, chunk, cx, cy, logger)
		m.initHostPlantsInChunk(state, chunk, cx, cy, logger)
		m.initForagePoolsInChunk(state, chunk, cx, cy, logger)
		m.initStationsInChunk(state, chunk, cx, cy, logger)
	}

	logger.Info("Zone %s: restored world save (tick %d, %d swarms, %d edits, %d nests, %d items)",
		ws.ZoneID, ws.Tick, len(ws.Swarms), len(ws.CellEdits), len(ws.Nests), len(ws.GroundItems))
}

// gridKey is the "%d,%d" anchor-cell key every cell-keyed registry uses (crops, trees, nests,
// forage pools, host plants) — one helper instead of five inline Sprintf copies.
func gridKey(gx, gy int) string { return fmt.Sprintf("%d,%d", gx, gy) }
