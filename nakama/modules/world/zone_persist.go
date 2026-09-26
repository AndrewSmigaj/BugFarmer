package world

import (
	"context"
	"encoding/json"
	"strconv"
	"strings"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// LEGACY zone-save importer. The live persistence system is world_save.go (ONE WorldSave document
// per zone; the clock resumes; full-fidelity swarms — see §P / persist_classes.go). This file only
// DECODES the old multi-record format (":meta" + ":<cx>_<cy>" chunk deltas + ":swarms") so nothing
// anyone built before the migration is lost:
//
//   - importLegacySave runs at MatchInit ONLY when no WorldSave document exists. It applies the old
//     records eagerly with the OLD system's compensations kept intact (tick-stamp clamps, lossy
//     clean-swarm rebuild) — legacy stamps were written against a clock that reset to 0, so they are
//     meaningless under the resumed clock and must be clamped HERE, in the importer, nowhere else.
//   - The first successful WorldSave write DELETES the legacy records (deleteLegacyZoneRecords) —
//     new-doc-wins forever after; no resurrection, no storage garbage.
//   - This whole file dies a release later.

const (
	ZoneStateCollection = "zone_state"
	zoneStateVersion    = 1
)

// ZoneStateKey builds the per-zone key prefix. "" instanceID = the shared zone (today); a non-empty
// instanceID (<zoneID>:<instanceID>) reserves the scheme for future per-player private plots — no
// migration needed. The live document appends ":world"; legacy records appended ":meta", ":swarms",
// or ":<cx>_<cy>".
func ZoneStateKey(zoneID, instanceID string) string {
	if instanceID == "" {
		return zoneID
	}
	return zoneID + ":" + instanceID
}

func zoneMetaKey(zoneKey string) string  { return zoneKey + ":meta" }
func zoneSwarmKey(zoneKey string) string { return zoneKey + ":swarms" }

// CellEdit is one cell that differs from the authored base (legacy: chunk-local coordinates).
type CellEdit struct {
	LX     int             `json:"lx"`
	LY     int             `json:"ly"`
	Ground *string         `json:"ground,omitempty"` // non-nil = ground tile differs from base
	Occ    json.RawMessage `json:"occ,omitempty"`    // marshaled PlacedOccupant; nil+OccSet = cleared
	OccSet bool            `json:"occ_set,omitempty"`
}

// ChunkSave is the legacy per-chunk record: the cell delta + the sidecar state anchored in the chunk.
type ChunkSave struct {
	Version       int                        `json:"version"`
	ZoneID        string                     `json:"zone_id"`
	ChunkX        int                        `json:"cx"`
	ChunkY        int                        `json:"cy"`
	Cells         []CellEdit                 `json:"cells,omitempty"`
	Crops         []*entities.CropState      `json:"crops,omitempty"`
	Trees         []*entities.FruitTreeState `json:"trees,omitempty"`
	Stations      []*entities.StationState   `json:"stations,omitempty"`
	Containers    []*ContainerState          `json:"containers,omitempty"`
	CraftStations []*CraftStationState       `json:"craft_stations,omitempty"`
	GroundItems   []*entities.GroundItem     `json:"ground_items,omitempty"`
	Nests         []*entities.NestState      `json:"nests,omitempty"`
	ForagePools   []*entities.ForagePoolState `json:"forage_pools,omitempty"`
	HostPlants    []*entities.HostPlantState  `json:"host_plants,omitempty"`
	Broods        []*entities.BroodState      `json:"broods,omitempty"`
}

// SwarmSave is the legacy MINIMAL bug-population descriptor (the lossy pre-§P format).
type SwarmSave struct {
	SpeciesID string  `json:"species"`
	WorldX    float32 `json:"x"`
	WorldY    float32 `json:"y"`
	Count     int     `json:"count"`
	Phase     string  `json:"phase,omitempty"`
	Satiation float32 `json:"sat,omitempty"`
	Repro     float32 `json:"repro,omitempty"`
}

// ZoneSwarmSave is the legacy zone-wide bug population record.
type ZoneSwarmSave struct {
	Version int         `json:"version"`
	ZoneID  string      `json:"zone_id"`
	Swarms  []SwarmSave `json:"swarms"`
}

// ZoneMeta is the legacy zone-wide record; ModifiedChunks indexes the chunk records.
type ZoneMeta struct {
	Version         int      `json:"version"`
	ZoneID          string   `json:"zone_id"`
	LastRolloverDay int64    `json:"last_rollover_day"`
	ModifiedChunks  []string `json:"modified_chunks"` // "cx_cy" suffixes
	SavedAt         int64    `json:"saved_at"`
}

// zoneAutosaveTicks gates the periodic autosave (~10 min at 10 Hz) — only fires while occupied (the
// MatchLoop pause guard returns before this), exactly when crash-safety matters.
const zoneAutosaveTicks = 6000

// ---- legacy storage reads ----

// LoadZoneMeta reads the legacy zone meta record. (nil, nil) when absent.
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

// LoadChunkSaves batch-reads the named legacy chunk records (from meta.ModifiedChunks), keyed by the
// in-memory ChunkKey (cx,cy). Corrupt/version/zone-mismatch records are skipped.
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

// ---- the one-time import (MatchInit, only when no WorldSave document exists) ----

// importLegacySave eagerly applies a legacy multi-record save: every modified chunk is loaded from
// the authored zone, overlaid, sidecar-hydrated (with the OLD clamps), and init-scanned — before any
// client joins. Returns whether the legacy SWARM population was restored (false → the caller spawns
// fresh initial swarms; farm/sidecar state may still have been imported).
func (m *Match) importLegacySave(ctx context.Context, nk runtime.NakamaModule, state *WorldState, logger runtime.Logger) bool {
	if state.CurrentZone == nil {
		return false
	}
	zoneKey := ZoneStateKey(state.CurrentZone.ZoneID, "")
	meta, err := LoadZoneMeta(ctx, nk, zoneKey)
	if err != nil {
		logger.Error("legacy import: meta read failed for %s: %v", zoneKey, err)
		return false
	}
	if meta == nil {
		return false // never saved → pristine authored zone
	}
	cache, err := LoadChunkSaves(ctx, nk, zoneKey, state.CurrentZone.ZoneID, meta.ModifiedChunks)
	if err != nil {
		logger.Error("legacy import: chunk read failed for %s: %v", zoneKey, err)
	}
	state.LastRolloverDay = meta.LastRolloverDay

	zonePath := "data/zones/" + state.CurrentZone.ZoneID
	for _, chunkKey := range sortedStringKeys(cache) {
		cs := cache[chunkKey]
		if _, exists := state.Chunks[chunkKey]; exists {
			continue
		}
		chunk, err := LoadChunk(zonePath, cs.ChunkX, cs.ChunkY)
		if err != nil {
			chunk = NewEmptyChunk(cs.ChunkX, cs.ChunkY, "grass")
		}
		state.Chunks[chunkKey] = chunk
		m.applyLegacyChunkSave(state, chunk, cs)
		m.initFruitTreesInChunk(state, chunk, cs.ChunkX, cs.ChunkY, logger)
		m.initNestsInChunk(state, chunk, cs.ChunkX, cs.ChunkY, logger)
		m.initHostPlantsInChunk(state, chunk, cs.ChunkX, cs.ChunkY, logger)
		m.initForagePoolsInChunk(state, chunk, cs.ChunkX, cs.ChunkY, logger)
		m.initStationsInChunk(state, chunk, cs.ChunkX, cs.ChunkY, logger)
	}

	// The legacy latent GroundItemSeq bug, fixed at import: restored item ids carry "<prefix>_<n>"
	// suffixes while the seq would restart at 0 — bump it past the highest imported suffix so a new
	// drop can never re-mint (and silently overwrite) a restored item's id.
	for _, id := range sortedStringKeys(state.GroundItems) {
		if i := strings.LastIndex(id, "_"); i >= 0 {
			if n, err := strconv.ParseInt(id[i+1:], 10, 64); err == nil && n > state.GroundItemSeq {
				state.GroundItemSeq = n
			}
		}
	}

	logger.Info("Zone %s: imported legacy save (%d chunk record(s))", state.CurrentZone.ZoneID, len(cache))
	return m.importLegacySwarms(ctx, nk, state, logger)
}

// applyLegacyChunkSave overlays one legacy chunk record onto a freshly-loaded chunk and hydrates the
// sidecar maps. Runs BEFORE the init scans (their skip-if-present guards then keep restored state).
// The OLD clamps live here on purpose: legacy tick-stamps were written against a clock that reset to
// 0 every boot, so under the resumed clock they are garbage and get zeroed. The live system
// (world_save.go) has NO clamps — its stamps are valid because the clock persists.
func (m *Match) applyLegacyChunkSave(state *WorldState, chunk *ChunkData, cs *ChunkSave) {
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
		state.CropStates[gridKey(c.GridX, c.GridY)] = c
	}
	for _, t := range cs.Trees {
		t.LastFallTick = 0 // legacy stamps are against a reset clock — clamp (importer-only)
		t.LastHarvestTick = 0
		state.FruitTreeStates[gridKey(t.GridX, t.GridY)] = t
	}
	for _, st := range cs.Stations {
		state.Stations[entities.StationKey(st.GridX, st.GridY)] = st
	}
	for _, ct := range cs.Containers {
		state.Containers[ContainerKey(ct.GridX, ct.GridY)] = ct
	}
	for _, cf := range cs.CraftStations {
		// Legacy pre-craft-slots saves fold Recipe/Queue/Progress into Procs[0] at unmarshal
		// (CraftStationState.UnmarshalJSON); top the lanes up to the def's craft_slots here.
		ensureProcs(state, cf)
		state.CraftStations[CraftStationKey(cf.GridX, cf.GridY)] = cf
	}
	for _, n := range cs.Nests {
		n.RehatchAtTick = 0 // importer-only clamps, as above
		n.SmokedUntilTick = 0
		n.ResidentSwarmID = "" // legacy swarms re-mint ids; nest recovery self-heals the resident
		state.NestStates[gridKey(n.GridX, n.GridY)] = n
	}
	for _, fp := range cs.ForagePools {
		state.ForagePools[gridKey(fp.GridX, fp.GridY)] = fp
	}
	for _, hp := range cs.HostPlants {
		state.HostPlantStates[gridKey(hp.GridX, hp.GridY)] = hp
	}
	for _, br := range cs.Broods {
		key := broodKey(br.GridX, br.GridY)
		if br.SourceKind == "ground_pile" {
			key = "g:" + key
		}
		state.BroodStates[key] = br
	}
	if state.CurrentZone == nil || !state.CurrentZone.EphemeralSwarms {
		for _, gi := range cs.GroundItems {
			state.putGroundItem(gi)
		}
	}
}

// importLegacySwarms recreates the legacy lossy population as CLEAN swarms (fresh ids/stamps via
// spawnSwarmAt — the old restore semantics, kept verbatim). Returns true if a swarm record existed
// (even an empty one: "the player caught them all" is a real saved population).
func (m *Match) importLegacySwarms(ctx context.Context, nk runtime.NakamaModule, state *WorldState, logger runtime.Logger) bool {
	if state.CurrentZone.EphemeralSwarms {
		return false // test zone: always start fresh
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
	logger.Info("Zone %s: imported %d legacy swarm(s)", state.CurrentZone.ZoneID, restored)
	return true
}

// ---- cleanup (called by the live system after its first successful document write) ----

// deleteLegacyZoneRecords removes the old multi-record save once a WorldSave document exists —
// new-doc-wins from then on. No-op (one cheap read) when no legacy meta remains.
func deleteLegacyZoneRecords(ctx context.Context, nk runtime.NakamaModule, logger runtime.Logger, zoneKey, zoneID string) {
	meta, err := LoadZoneMeta(ctx, nk, zoneKey)
	if err != nil || meta == nil {
		return
	}
	dels := []*runtime.StorageDelete{
		{Collection: ZoneStateCollection, Key: zoneMetaKey(zoneKey), UserID: ""},
		{Collection: ZoneStateCollection, Key: zoneSwarmKey(zoneKey), UserID: ""},
	}
	for _, suf := range meta.ModifiedChunks {
		dels = append(dels, &runtime.StorageDelete{
			Collection: ZoneStateCollection, Key: zoneKey + ":" + suf, UserID: "",
		})
	}
	if err := nk.StorageDelete(ctx, dels); err != nil {
		logger.Error("Zone %s: legacy record cleanup failed: %v", zoneID, err)
		return
	}
	logger.Info("Zone %s: deleted %d legacy record(s) (migration complete)", zoneID, len(dels))
}

// ---- shared cell-diff helpers (used by the live builder in world_save.go too) ----

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
