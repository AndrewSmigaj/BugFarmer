package world

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// Zone / farm persistence. A zone is a shared canonical world; everything a player builds (placed/
// broken occupants, tilled/watered soil, crops, fruit trees, chest contents, compost/craft stations,
// ground items) plus the live bug population lives only in the in-memory WorldState today and is lost
// on a server restart / MatchTerminate. This module persists it to Nakama storage as a DELTA on top of
// the authored zone files and re-applies it on match (re)create.
//
// Determinism: farm state is NOT in the bug-sim hash, and restore happens only at load boundaries
// (MatchInit meta/swarms; handleChunkSubscribe per-chunk) before any tick advances. Saves are read-only
// snapshots written on a detached goroutine that never mutates WorldState. See the plan + character_persist.go
// (the pattern this mirrors).

const (
	ZoneStateCollection = "zone_state"
	zoneStateVersion    = 1
)

// ZoneStateKey builds the per-zone key prefix. "" instanceID = the shared zone (today); a non-empty
// instanceID (<zoneID>:<instanceID>) reserves the scheme for future per-player private plots — no
// migration needed. Per-record keys append ":meta", ":swarms", or ":<cx>_<cy>".
func ZoneStateKey(zoneID, instanceID string) string {
	if instanceID == "" {
		return zoneID
	}
	return zoneID + ":" + instanceID
}

func zoneMetaKey(zoneKey string) string              { return zoneKey + ":meta" }
func zoneSwarmKey(zoneKey string) string             { return zoneKey + ":swarms" }
func zoneChunkKey(zoneKey string, cx, cy int) string { return fmt.Sprintf("%s:%d_%d", zoneKey, cx, cy) }

// CellEdit is one cell that differs from the authored base. OccSet distinguishes "occupant unchanged
// (field omitted)" from "occupant explicitly cleared" (a broken authored occupant: OccSet=true, Occ nil).
type CellEdit struct {
	LX     int             `json:"lx"`
	LY     int             `json:"ly"`
	Ground *string         `json:"ground,omitempty"` // non-nil = ground tile differs from base
	Occ    json.RawMessage `json:"occ,omitempty"`    // marshaled PlacedOccupant; nil+OccSet = cleared
	OccSet bool            `json:"occ_set,omitempty"`
}

// ChunkSave is the persisted delta + the sidecar runtime state whose anchor cell lives in this chunk.
// The *State pointers are flat value structs (no pointers/maps/unexported) and JSON round-trip as-is.
type ChunkSave struct {
	Version       int                          `json:"version"`
	ZoneID        string                       `json:"zone_id"`
	ChunkX        int                          `json:"cx"`
	ChunkY        int                          `json:"cy"`
	Cells         []CellEdit                   `json:"cells,omitempty"`
	Crops         []*entities.CropState        `json:"crops,omitempty"`
	Trees         []*entities.FruitTreeState   `json:"trees,omitempty"`
	Stations      []*entities.StationState     `json:"stations,omitempty"`
	Containers    []*ContainerState            `json:"containers,omitempty"`
	CraftStations []*CraftStationState         `json:"craft_stations,omitempty"`
	GroundItems   []*entities.GroundItem       `json:"ground_items,omitempty"`
}

func (c *ChunkSave) isEmpty() bool {
	return len(c.Cells) == 0 && len(c.Crops) == 0 && len(c.Trees) == 0 && len(c.Stations) == 0 &&
		len(c.Containers) == 0 && len(c.CraftStations) == 0 && len(c.GroundItems) == 0
}

// SwarmSave is a MINIMAL bug-population descriptor — what population exists, where, and how far along
// its breeding is. We deliberately drop transient combat/think/action state + bug-id tracking: restore
// rebuilds CLEAN swarms (IDs 0..Count-1, fresh stamps) via spawnSwarmAt, which is determinism-safe at the
// cold-start boundary and sidesteps the TickCount-reset + not-serialized-RemovedBugIDs landmines.
type SwarmSave struct {
	SpeciesID string  `json:"species"`
	WorldX    float32 `json:"x"`
	WorldY    float32 `json:"y"`
	Count     int     `json:"count"`
	Phase     string  `json:"phase,omitempty"`
	Satiation float32 `json:"sat,omitempty"`
	Repro     float32 `json:"repro,omitempty"`
}

// ZoneSwarmSave is the zone-wide bug population. Its presence (even empty) means "this zone was saved" →
// restore the EXACT population (incl. "none", if the player caught them all) instead of fresh spawns.
type ZoneSwarmSave struct {
	Version int         `json:"version"`
	ZoneID  string      `json:"zone_id"`
	Swarms  []SwarmSave `json:"swarms"`
}

// buildSwarmSave snapshots the live (server-authoritative) swarm population to minimal descriptors.
func (m *Match) buildSwarmSave(state *WorldState) []SwarmSave {
	cs := state.Config.ChunkSize
	out := make([]SwarmSave, 0, len(state.Swarms))
	for _, sw := range state.Swarms {
		if sw == nil || sw.Count <= 0 {
			continue
		}
		out = append(out, SwarmSave{
			SpeciesID: sw.SpeciesID,
			WorldX:    float32(sw.Position.ChunkX*cs) + sw.Position.LocalX,
			WorldY:    float32(sw.Position.ChunkY*cs) + sw.Position.LocalY,
			Count:     sw.Count, Phase: sw.Phase, Satiation: sw.Satiation, Repro: sw.ReproductionMeter,
		})
	}
	return out
}

// restoreSwarms loads the saved population and recreates CLEAN swarms (mirrors spawnInitialSwarms but
// seeded from the save). Returns true if a swarm record existed (→ caller skips spawnInitialSwarms);
// false = never saved (pristine zone → fresh spawns). Determinism-safe: clean swarms enter at MatchInit
// before any client joins, identical to fresh spawns; the first joiner bootstraps as authority off them.
func (m *Match) restoreSwarms(ctx context.Context, nk runtime.NakamaModule, state *WorldState, logger runtime.Logger) bool {
	if state.CurrentZone == nil {
		return false
	}
	if state.CurrentZone.EphemeralSwarms {
		// Test zone: always start fresh (caller spawns the `initial` population). Keeps tuning runs
		// reproducible — no carry-over of the prior run's saved populations.
		return false
	}
	zoneKey := ZoneStateKey(state.CurrentZone.ZoneID, "")
	objs, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: ZoneStateCollection, Key: zoneSwarmKey(zoneKey), UserID: "",
	}})
	if err != nil || len(objs) == 0 {
		return false
	}
	var zss ZoneSwarmSave
	if json.Unmarshal([]byte(objs[0].Value), &zss) != nil || zss.Version != zoneStateVersion ||
		zss.ZoneID != state.CurrentZone.ZoneID {
		return false
	}
	cs := state.Config.ChunkSize
	restored := 0
	for _, s := range zss.Swarms {
		sw := m.spawnSwarmAt(state, s.SpeciesID, s.Count, s.WorldX, s.WorldY, cs)
		if sw == nil {
			continue // unknown species / bad count
		}
		if s.Phase != "" {
			sw.Phase = s.Phase
		}
		sw.Satiation = s.Satiation
		sw.ReproductionMeter = s.Repro
		restored++
	}
	logger.Info("Zone %s: restored %d swarm(s) from save (skipping initial spawn)", state.CurrentZone.ZoneID, restored)
	return true
}

// ZoneMeta is the small zone-wide record. ModifiedChunks is the index MatchInit uses to batch-read
// exactly this zone's chunk records (StorageList can't filter by key prefix).
type ZoneMeta struct {
	Version         int      `json:"version"`
	ZoneID          string   `json:"zone_id"`
	LastRolloverDay int64    `json:"last_rollover_day"`
	ModifiedChunks  []string `json:"modified_chunks"` // "cx_cy" suffixes
	SavedAt         int64    `json:"saved_at"`
}

// ---- storage helpers (system-owned, server-only write — mirrors character_persist.go) ----

func writeZoneRecord(ctx context.Context, nk runtime.NakamaModule, key string, v interface{}) error {
	data, err := json.Marshal(v)
	if err != nil {
		return err
	}
	_, err = nk.StorageWrite(ctx, []*runtime.StorageWrite{{
		Collection:      ZoneStateCollection,
		Key:             key,
		UserID:          "", // system-owned (shared zone)
		Value:           string(data),
		PermissionRead:  2, // public read (a shared zone)
		PermissionWrite: 0, // server-only
	}})
	return err
}

func deleteZoneRecord(ctx context.Context, nk runtime.NakamaModule, key string) error {
	return nk.StorageDelete(ctx, []*runtime.StorageDelete{{
		Collection: ZoneStateCollection, Key: key, UserID: "",
	}})
}

// LoadZoneMeta reads the zone meta record. (nil, nil) when absent.
func LoadZoneMeta(ctx context.Context, nk runtime.NakamaModule, zoneKey string) (*ZoneMeta, error) {
	objs, err := nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: ZoneStateCollection, Key: zoneMetaKey(zoneKey), UserID: "",
	}})
	if err != nil || len(objs) == 0 {
		return nil, err
	}
	var meta ZoneMeta
	if err := json.Unmarshal([]byte(objs[0].Value), &meta); err != nil {
		return nil, err
	}
	return &meta, nil
}

// LoadChunkSaves batch-reads the named chunk records (from meta.ModifiedChunks) and returns a cache
// keyed by the in-memory ChunkKey (cx,cy). Corrupt/version/zone-mismatch records are skipped.
func LoadChunkSaves(ctx context.Context, nk runtime.NakamaModule, zoneKey, zoneID string, chunkSuffixes []string) (map[string]*ChunkSave, error) {
	cache := make(map[string]*ChunkSave)
	if len(chunkSuffixes) == 0 {
		return cache, nil
	}
	reads := make([]*runtime.StorageRead, 0, len(chunkSuffixes))
	for _, suf := range chunkSuffixes {
		reads = append(reads, &runtime.StorageRead{
			Collection: ZoneStateCollection, Key: zoneKey + ":" + suf, UserID: "",
		})
	}
	objs, err := nk.StorageRead(ctx, reads)
	if err != nil {
		return cache, err
	}
	for _, o := range objs {
		var cs ChunkSave
		if json.Unmarshal([]byte(o.Value), &cs) != nil {
			continue
		}
		if cs.Version != zoneStateVersion || cs.ZoneID != zoneID {
			continue
		}
		cache[ChunkKey(cs.ChunkX, cs.ChunkY)] = &cs
	}
	return cache, nil
}

// zoneAutosaveTicks gates the periodic autosave (~10 min at 10 Hz) — only fires while occupied (the
// MatchLoop pause guard returns before this), exactly when crash-safety matters.
const zoneAutosaveTicks = 6000

// prefetchZoneState loads this zone's saved farm delta at MatchInit into ZoneChunkCache, so the lazy
// handleChunkSubscribe (which has no ctx/nk) can apply per-chunk. Absent meta → pristine zone (no-op).
// (Apparent day/weather are intentionally NOT restored in v1 — they restart fresh, which is safe; only
// the farm + bug population carry over.)
func (m *Match) prefetchZoneState(ctx context.Context, nk runtime.NakamaModule, state *WorldState, logger runtime.Logger) {
	if state.CurrentZone == nil {
		return
	}
	zoneKey := ZoneStateKey(state.CurrentZone.ZoneID, "")
	meta, err := LoadZoneMeta(ctx, nk, zoneKey)
	if err != nil {
		logger.Error("zone prefetch: meta read failed for %s: %v", zoneKey, err)
		return
	}
	if meta == nil {
		return // never saved → pristine authored zone
	}
	cache, err := LoadChunkSaves(ctx, nk, zoneKey, state.CurrentZone.ZoneID, meta.ModifiedChunks)
	if err != nil {
		logger.Error("zone prefetch: chunk read failed for %s: %v", zoneKey, err)
	}
	state.ZoneChunkCache = cache
	logger.Info("Zone %s: prefetched %d modified chunk(s) from save", state.CurrentZone.ZoneID, len(cache))
}

// ---- build (snapshot) ----

// occCellEqual semantically compares two occupant cells (parsed {ID,Dir,Anchor}), NOT raw bytes —
// SetOccupant marshals canonically but authored JSON may be formatted differently.
func occCellEqual(a, b json.RawMessage) bool {
	ca, _ := ParseOccupantCell(a)
	cb, _ := ParseOccupantCell(b)
	if ca.IsEmpty != cb.IsEmpty {
		return false
	}
	if ca.IsEmpty {
		return true
	}
	return ca.Occupant.ID == cb.Occupant.ID && ca.Occupant.Dir == cb.Occupant.Dir &&
		ca.Occupant.Anchor == cb.Occupant.Anchor
}

// buildChunkSave diffs a LOADED chunk vs its authored base and gathers the sidecar state anchored in
// it. Returns nil when the chunk is pristine (no record needed). Read-only over WorldState.
func (m *Match) buildChunkSave(state *WorldState, cx, cy int) *ChunkSave {
	chunkKey := ChunkKey(cx, cy)
	live := state.Chunks[chunkKey]
	if live == nil {
		return nil
	}
	zonePath := "data/zones/" + state.CurrentZone.ZoneID
	base, err := LoadChunk(zonePath, cx, cy)
	if err != nil {
		base = NewEmptyChunk(cx, cy, "grass") // same fallback handleChunkSubscribe uses
	}

	cs := &ChunkSave{Version: zoneStateVersion, ZoneID: state.CurrentZone.ZoneID, ChunkX: cx, ChunkY: cy}

	for ly := 0; ly < ChunkSize; ly++ {
		for lx := 0; lx < ChunkSize; lx++ {
			edit := CellEdit{LX: lx, LY: ly}
			changed := false
			if liveG, baseG := groundAt(live, lx, ly), groundAt(base, lx, ly); liveG != baseG {
				g := liveG
				edit.Ground = &g
				changed = true
			}
			liveO, baseO := occAt(live, lx, ly), occAt(base, lx, ly)
			if !occCellEqual(liveO, baseO) {
				edit.Occ = liveO // nil when the authored occupant was broken (cleared)
				edit.OccSet = true
				changed = true
			}
			if changed {
				cs.Cells = append(cs.Cells, edit)
			}
		}
	}

	csz := state.Config.ChunkSize
	inChunk := func(gx, gy int) bool { return gx/csz == cx && gy/csz == cy }
	for _, c := range state.CropStates {
		if inChunk(c.GridX, c.GridY) {
			cs.Crops = append(cs.Crops, c)
		}
	}
	for _, t := range state.FruitTreeStates {
		if inChunk(t.GridX, t.GridY) {
			cs.Trees = append(cs.Trees, t)
		}
	}
	for _, st := range state.Stations {
		if inChunk(st.GridX, st.GridY) {
			cs.Stations = append(cs.Stations, st)
		}
	}
	for _, ct := range state.Containers {
		if inChunk(ct.GridX, ct.GridY) {
			cs.Containers = append(cs.Containers, ct)
		}
	}
	for _, cf := range state.CraftStations {
		if inChunk(cf.GridX, cf.GridY) {
			cs.CraftStations = append(cs.CraftStations, cf)
		}
	}
	for _, gi := range state.GroundItems {
		if gi.Position.ChunkX == cx && gi.Position.ChunkY == cy {
			cs.GroundItems = append(cs.GroundItems, gi)
		}
	}

	if cs.isEmpty() {
		return nil
	}
	return cs
}

// zoneRecord is a marshaled record ready to write (bytes captured synchronously so the async write
// is immune to later WorldState mutation).
type zoneRecord struct {
	key   string
	value string
}

// snapshotZoneState builds the full set of records to persist for the zone, SYNCHRONOUSLY on the match
// goroutine (reads + marshals WorldState now; the returned bytes are a frozen snapshot). The caller then
// writes them (sync on terminate, async elsewhere). The meta's ModifiedChunks MERGES chunks modified
// this session with prior-modified chunks that weren't revisited (whose storage records are untouched) —
// so a farm in a chunk you didn't walk through this session is preserved, not dropped.
func (m *Match) snapshotZoneState(state *WorldState) []zoneRecord {
	if state.CurrentZone == nil {
		return nil
	}
	zoneKey := ZoneStateKey(state.CurrentZone.ZoneID, "")
	var recs []zoneRecord
	modified := make(map[string]bool)

	for _, chunk := range state.Chunks {
		cs := m.buildChunkSave(state, chunk.ChunkX, chunk.ChunkY)
		if cs == nil {
			continue // pristine (or reverted) — no record; drops out of the index
		}
		data, err := json.Marshal(cs)
		if err != nil {
			continue
		}
		suffix := fmt.Sprintf("%d_%d", chunk.ChunkX, chunk.ChunkY)
		recs = append(recs, zoneRecord{key: zoneKey + ":" + suffix, value: string(data)})
		modified[suffix] = true
	}

	// Preserve prior-modified chunks that weren't loaded this session (their records stay as-is).
	loaded := func(cx, cy int) bool { _, ok := state.Chunks[ChunkKey(cx, cy)]; return ok }
	for _, cs := range state.ZoneChunkCache {
		if !loaded(cs.ChunkX, cs.ChunkY) {
			modified[fmt.Sprintf("%d_%d", cs.ChunkX, cs.ChunkY)] = true
		}
	}

	chunkList := make([]string, 0, len(modified))
	for s := range modified {
		chunkList = append(chunkList, s)
	}
	meta := &ZoneMeta{
		Version: zoneStateVersion, ZoneID: state.CurrentZone.ZoneID,
		LastRolloverDay: state.LastRolloverDay, ModifiedChunks: chunkList, SavedAt: time.Now().Unix(),
	}
	if metaData, err := json.Marshal(meta); err == nil {
		recs = append(recs, zoneRecord{key: zoneMetaKey(zoneKey), value: string(metaData)})
	}

	// Bug population (its presence means "saved" → restore exact population, even if empty).
	zss := &ZoneSwarmSave{Version: zoneStateVersion, ZoneID: state.CurrentZone.ZoneID, Swarms: m.buildSwarmSave(state)}
	if swData, err := json.Marshal(zss); err == nil {
		recs = append(recs, zoneRecord{key: zoneSwarmKey(zoneKey), value: string(swData)})
	}
	return recs
}

// writeZoneRecords persists the snapshot (batched StorageWrite). Safe to call from a detached goroutine
// (the records are pre-marshaled bytes; nk is concurrency-safe).
func writeZoneRecords(ctx context.Context, nk runtime.NakamaModule, logger runtime.Logger, recs []zoneRecord) {
	if len(recs) == 0 {
		return
	}
	writes := make([]*runtime.StorageWrite, 0, len(recs))
	for _, r := range recs {
		writes = append(writes, &runtime.StorageWrite{
			Collection: ZoneStateCollection, Key: r.key, UserID: "",
			Value: r.value, PermissionRead: 2, PermissionWrite: 0,
		})
	}
	if _, err := nk.StorageWrite(ctx, writes); err != nil {
		logger.Error("zone save: StorageWrite failed: %v", err)
	}
}

func groundAt(c *ChunkData, lx, ly int) string {
	if ly < len(c.Ground) && lx < len(c.Ground[ly]) {
		return c.Ground[ly][lx]
	}
	return ""
}
func occAt(c *ChunkData, lx, ly int) json.RawMessage {
	if ly < len(c.Occupants) && lx < len(c.Occupants[ly]) {
		return c.Occupants[ly][lx]
	}
	return nil
}

// ---- apply (restore) ----

// applyChunkSave overlays a cached ChunkSave onto a freshly-loaded chunk + hydrates the sidecar maps.
// MUST run in handleChunkSubscribe AFTER LoadChunk but BEFORE the init scans (they randomize untracked
// trees/stations; restoring first hits their skip-if-present guard). No-op when no record is cached.
func (m *Match) applyChunkSave(state *WorldState, chunk *ChunkData, cx, cy int) {
	if state.ZoneChunkCache == nil {
		return
	}
	cs := state.ZoneChunkCache[ChunkKey(cx, cy)]
	if cs == nil {
		return
	}

	for _, e := range cs.Cells {
		if e.LY < 0 || e.LY >= ChunkSize || e.LX < 0 || e.LX >= ChunkSize {
			continue
		}
		if e.Ground != nil {
			chunk.Ground[e.LY][e.LX] = *e.Ground
		}
		if e.OccSet {
			chunk.Occupants[e.LY][e.LX] = e.Occ // nil clears (broken authored occupant)
		}
	}

	for _, c := range cs.Crops {
		state.CropStates[fmt.Sprintf("%d,%d", c.GridX, c.GridY)] = c
	}
	for _, t := range cs.Trees {
		t.LastFallTick = 0 // tick stamps are stale after a TickCount reset — clamp the gate anchors
		t.LastHarvestTick = 0
		state.FruitTreeStates[fmt.Sprintf("%d,%d", t.GridX, t.GridY)] = t
	}
	for _, st := range cs.Stations {
		state.Stations[entities.StationKey(st.GridX, st.GridY)] = st
	}
	for _, ct := range cs.Containers {
		state.Containers[ContainerKey(ct.GridX, ct.GridY)] = ct
	}
	for _, cf := range cs.CraftStations {
		state.CraftStations[CraftStationKey(cf.GridX, cf.GridY)] = cf
	}
	for _, gi := range cs.GroundItems {
		state.GroundItems[gi.ID] = gi
	}
}
