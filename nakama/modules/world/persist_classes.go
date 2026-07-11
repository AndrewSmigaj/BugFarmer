package world

// THE PERSISTENCE CLASSIFICATION TABLE — every WorldState field, classified exactly once.
//
// This table is the contract that keeps "forgot to persist X" from ever happening silently:
// TestPersistClassificationComplete walks WorldState by reflection and FAILS naming any field
// missing here (and any stale entry for a field that no longer exists). Adding a WorldState
// field forces you to decide — and record — what a server restart does to it.
//
// The three classes (see world_save.go):
//   WORLD-STATE — anything players or the ecology changed. Persists byte-faithfully in the
//                 WorldSave document; the note says which field carries it.
//   PER-RUN     — session/sync/derived state that must NOT survive a restart (presences, the
//                 influence ledger, RNG, caches, telemetry). The note says why.
//   CONFIG      — loaded from data files / match-creation parameters at every MatchInit.
//
// DEAD marks fields written nowhere (flagged for a separate deletion commit) — kept distinct so
// the table never quietly launders a dead field as "per-run".

type persistClass string

const (
	classWorldState persistClass = "WORLD-STATE"
	classPerRun     persistClass = "PER-RUN"
	classConfig     persistClass = "CONFIG"
	classDead       persistClass = "DEAD"
)

type persistEntry struct {
	Class persistClass
	Note  string
}

var persistClasses = map[string]persistEntry{
	// -- identity / config (re-supplied at every MatchInit) --
	"Config":       {classConfig, "match config from creation params"},
	"WorldID":      {classPerRun, "match identity, re-supplied at creation"},
	"OwnerID":      {classPerRun, "match creation param"},
	"Name":         {classPerRun, "match creation param"},
	"AccessPolicy": {classPerRun, "match creation param"},
	"CreatedAt":    {classPerRun, "this run's creation stamp"},
	"ZoneID":       {classConfig, "derived from the zone creation param (logging)"},
	"StaticSim":    {classConfig, "from zone bug_spawning.static"},

	// -- the world clock --
	"TickCount": {classWorldState, "WorldSave.Tick — THE keystone: restored FIRST, so every persisted tick-stamp stays valid; doubles as the save generation stamp"},

	// -- randomness (determinism is within-run only, by design) --
	"WorldSeed": {classPerRun, "per-run seed; cross-restart bit-reproducibility is a non-goal"},
	"Rng":       {classPerRun, "seeded from WorldSeed at init"},

	// -- ids --
	"GroundItemSeq": {classWorldState, "WorldSave.GroundItemSeq — restored items keep ids; a reset counter would re-mint one and silently overwrite (the FindNearbyFood-tiebreak latent bug)"},

	// -- players / presences (the character system persists players separately, user-owned) --
	"Players":               {classPerRun, "live sessions; character_persist.go owns durable player state"},
	"Presences":             {classPerRun, "live sessions"},
	"PendingCharacters":     {classPerRun, "join-attempt handoff"},
	"PendingEntryPositions": {classPerRun, "join-attempt handoff"},

	// -- entities --
	"Swarms":      {classWorldState, "WorldSave.Swarms — FULL FIDELITY, whole structs (see SwarmState's json tags); Radius/WanderRad refreshed from species def at load; player-ref fields self-heal"},
	"GroundItems": {classWorldState, "WorldSave.GroundItems (skipped on EphemeralSwarms test zones)"},
	"ItemsByChunk": {classPerRun, "derived chunk-bucketed index over GroundItems; rebuilt by putGroundItem during restore"},

	// -- config data --
	"Species":          {classConfig, "data/species.json"},
	"Tuning":           {classConfig, "data/ecology_tuning.json"},
	"TileDefs":         {classConfig, "data/tiles.json"},
	"Entities":         {classConfig, "data/entities/*.json"},
	"CropDefs":         {classConfig, "data/crops.json"},
	"Recipes":          {classConfig, "data/recipes.json"},
	"RecipesByStation": {classConfig, "derived from Recipes at load"},
	"GroundRecipes":    {classConfig, "data/entities/ground_recipes.json"},
	"CurrentZone":      {classConfig, "authored zone metadata"},

	// -- timing / telemetry --
	"LastMergeCheck": {classPerRun, "merge/split cadence anchor; re-anchors on the resumed clock"},
	"Stats":          {classPerRun, "per-day tuning telemetry, flushed at rollover"},
	"Perf":           {classPerRun, "profiler observation, nil in production"},

	// -- sky state --
	"DayOffsetTicks":    {classWorldState, "WorldSave.DayOffsetTicks — apparent time-of-day survives"},
	"LastRolloverDay":   {classWorldState, "WorldSave.LastRolloverDay — the daily reset must not double-fire"},
	"WeatherKind":       {classWorldState, "WorldSave.WeatherKind — you log back into the same rainstorm"},
	"WeatherUntilTick":  {classWorldState, "WorldSave.WeatherUntilTick"},
	"ScheduledRainTick": {classWorldState, "WorldSave.ScheduledRainTick"},
	"DroughtUntilTick":  {classWorldState, "WorldSave.DroughtUntilTick"},

	// -- broadcast / sync (per-run BY the sync architecture: ledger/epoch/seq reset with the run) --
	"SwarmsDirty":      {classPerRun, "broadcast dirty flag"},
	"LastSampleTick":   {classPerRun, "drift-check cadence"},
	"DriftChecks":      {classPerRun, "in-flight hash checks"},
	"PlayerCells":      {classPerRun, "live player positions"},
	"ZoneStates":       {classPerRun, "authority + influence ledger (NextSeq/InfluenceLog/snapshots) — per-run by the sync architecture"},
	"PendingInfluence": {classPerRun, "this tick's outgoing events"},

	// -- the map --
	"Chunks":        {classWorldState, "WorldSave.CellEdits — semantic diff of loaded chunks vs the authored zone; edited chunks eager-load at restore"},
	"ChunkSubs":     {classPerRun, "live view subscriptions"},
	"BreakingState": {classPerRun, "an in-progress hand action; abandoned on restart"},

	// -- farm / ecology registries (whole structs into the document) --
	"CropStates":      {classWorldState, "WorldSave.Crops"},
	"FruitTreeStates": {classWorldState, "WorldSave.Trees"},
	"NestStates":      {classWorldState, "WorldSave.Nests — Honey/Brood/SmokedUntilTick/Founded ride along; ResidentSwarmID stays valid (swarm ids persist)"},
	"HostPlantStates": {classWorldState, "WorldSave.HostPlants"},
	"BroodStates":     {classWorldState, "WorldSave.Broods — the ground-pile \"g:\" key namespace is re-derived from SourceKind"},
	"ForagePools":     {classWorldState, "WorldSave.ForagePools — nectar levels ARE the bee economy"},
	"ColonyMemory":    {classPerRun, "ant trails MUST age out, never persist (Unbounded-Growth lens; entities/colony.go) — a restart forgets and scouts re-learn"},
	"ScoutPaths":      {classPerRun, "scout walk buffers feeding ColonyMemory — same age-out contract, pruned when the swarm dies"},
	"MarchTargets":    {classPerRun, "worker march commitments (trail hysteresis) — derived from ColonyMemory, same age-out"},
	"GnawDamage":      {classWorldState, "WorldSave.Gnaw — half-chewed fences stay half-chewed (was silently lost before §P)"},
	"Stations":        {classWorldState, "WorldSave.Stations"},
	"Containers":      {classWorldState, "WorldSave.Containers"},
	"CraftStations":   {classWorldState, "WorldSave.CraftStations — ensureProcs folds legacy shapes + tops up lanes at restore"},

	// -- spawn tracking --
	"SwarmsBySpecies":    {classPerRun, "derived index over Swarms; rebuilt during restore"},
	"SpeciesNextSpawn":   {classPerRun, "seconds derive from the resumed tick; boot behavior unchanged"},
	"SpeciesSpawnCursor": {classPerRun, "round-robin cursor; restarting the rotation is harmless"},

	// -- persistence bookkeeping --
	"LastZoneSaveTick": {classPerRun, "SET to the restored Tick at load (else one spurious autosave fires immediately)"},
}
