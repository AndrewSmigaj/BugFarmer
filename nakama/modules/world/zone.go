package world

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// ChunkSize is cells per chunk dimension (32x32 cells = 512x512 pixels).
const ChunkSize = 32

// BugSpawnConfig holds zone-level bug spawning configuration.
// Species caps are zone-wide (not per-area). Spawn areas define WHERE bugs appear.
type BugSpawnConfig struct {
	SpeciesCaps    map[string]SpeciesCap `json:"species_caps"`              // species_id → cap config
	SpawnAreas     []SpawnArea           `json:"spawn_areas"`               // WHERE species can spawn
	Static         bool                  `json:"static"`                    // If true: no continuous spawn, merge, or split (test/deterministic zones)
	InitialCarrion []CarrionSeed         `json:"initial_carrion,omitempty"` // authored carrion ground items seeded at match start (e.g. dead millipedes in the woods)
}

// CarrionSeed places authored carrion ground items at match start — a breeding/feeding substrate that
// would otherwise only appear once bugs start dying (the day-1 bootstrap, e.g. dead millipedes so the
// woods' flies/beetles have food from tick 0). Seeded deterministically before any client joins.
type CarrionSeed struct {
	Item  string `json:"item"`            // ground-item id (e.g. "dead_millipede")
	X     int    `json:"x"`               // world cell X
	Y     int    `json:"y"`               // world cell Y
	Count int    `json:"count,omitempty"` // how many to drop near (x,y); default 1
}

// SpeciesCap defines spawn limits for one species in a zone.
//
// Two distinct ceilings (architecture_swarm_sync.md §13):
//   - Max counts SWARMS and is spawn BACK-PRESSURE, not an invariant: continuous
//     spawning skips at/above it, but forced release-joins + the split pass can
//     overshoot it temporarily (bounded; decays via catches; never refilled).
//   - MaxPopulation counts BUGS and is the HARD guard: reproduction and releases are
//     gated against it before any mutation. 0 = uncapped (test zones rely on this).
type SpeciesCap struct {
	Initial       int     `json:"initial"`        // Swarms to spawn on match init
	Max           int     `json:"max"`            // Zone-wide max SWARM COUNT (spawn back-pressure)
	MaxPopulation int     `json:"max_population"` // Zone-wide max BUGS (hard cap; 0 = uncapped)
	SpawnInterval float32 `json:"spawn_interval"` // Seconds between continuous spawn attempts
	SwarmSize     int     `json:"swarm_size"`     // Fixed bugs per swarm (0 = use species Min/Max range)

	// Ecology Director bands — a per-species THREE-TIER control ladder (ecology_director.go). Natural
	// dynamics (food/predation/starvation) own the middle band [EventLow..EventHigh] and the Director does
	// NOTHING there; it only acts at the edges, gentlest-first:
	//   pop < MinPopulation (extreme low)  -> RE-SEED the species          (last-resort anti-extinction floor)
	//   pop < EventLow      (moderate low) -> EXTRA-RAIN event             (environmental: more fruit/nectar -> food up)
	//   pop > EventHigh     (moderate high)-> DROUGHT event                (environmental: suppress rain -> food tightens)
	//   pop > CullAt        (extreme high) -> HARD CULL (predator/direct)  (last resort, well above EventHigh)
	// Ordering invariant (validated at load): MinPopulation < EventLow < EventHigh < CullAt < MaxPopulation.
	// Any unset (0) tier is simply skipped. CullWith = a predator to release at the prey; "" = direct cull.
	MinPopulation int    `json:"min_population,omitempty"`
	EventLow      int    `json:"event_low,omitempty"`
	EventHigh     int    `json:"event_high,omitempty"`
	CullAt        int    `json:"cull_at,omitempty"`
	CullWith      string `json:"cull_with,omitempty"`

	// MaxNests caps how many hives of a nest-based predator (wasp) the zone may hold. A thriving colony
	// FOUNDS a daughter hive (processNestFounding) up to this many — how the predator population GROWS and
	// SPREADS. 0 = no dynamic founding (only the hand-placed nest occupants exist).
	MaxNests int `json:"max_nests,omitempty"`
}

// SpawnArea defines where a species can spawn.
// Type "zone" = anywhere in zone, Type "circle" = within radius of cx,cy.
type SpawnArea struct {
	ID      string   `json:"id"`
	Species []string `json:"species"` // Which species can spawn here
	Type    string   `json:"type"`    // "zone" or "circle"
	// Relative selection weight when a species has multiple areas (default 1.0 when absent/<=0).
	// Habitat circles get a high weight, the zone-wide wild-card a low one — e.g. habitat circles
	// summing to ~3 + a zone area at ~1 → ~3:1 habitat-vs-anywhere. See spawnSwarmForSpecies.
	Weight float64 `json:"weight,omitempty"`
	// Circle fields (only used if Type == "circle")
	CX     int `json:"cx,omitempty"`
	CY     int `json:"cy,omitempty"`
	Radius int `json:"radius,omitempty"`
}

// ZoneConfig describes a zone's metadata and spawn settings.
// Zones are 16x16 chunks (512x512 cells at 16px per cell = 8192x8192 pixels).
type ZoneConfig struct {
	ZoneID      string          `json:"zone_id"`
	Name        string          `json:"name"`
	Row         int             `json:"row"`            // Zone grid row
	Col         int             `json:"col"`            // Zone grid column
	Width       int             `json:"width"`          // Width in cells (default 512)
	Height      int             `json:"height"`         // Height in cells (default 512)
	SpawnPoint  [2]int          `json:"spawn_point"`    // Default spawn (cell coords)
	BiomeType   string          `json:"biome_type"`     // "meadow", "forest", "cave", etc.
	Seed        int64           `json:"seed,omitempty"` // Fixed world seed for deterministic runs (0 = random)
	BugSpawning *BugSpawnConfig `json:"bug_spawning"`   // Zone-level bug spawn config (optional)

	// CallRate: Nakama match tick rate (calls/sec) for THIS zone, 1..60. 0/absent = default 10.
	// TEST ZONES ONLY raise it (e.g. 60) to run the SAME sim ~6× faster in wall-clock — sim-TIME is
	// fixed by SimRate, so balance is unchanged (byte-identical tick sequence). Production zones omit it.
	CallRate int `json:"call_rate,omitempty"`

	// EphemeralSwarms: TEST ZONES ONLY — skip restoring the saved bug population at MatchInit so the zone
	// always starts from its `initial` spawns. Tuning runs are then reproducible + comparable (without it,
	// a restart reloads the PRIOR run's populations, e.g. butterflies reload pinned at their cap).
	EphemeralSwarms bool `json:"ephemeral_swarms,omitempty"`

	// SimBatch: TEST ZONES ONLY — advance N sim-ticks per Nakama call (1..64). call_rate is capped at
	// Nakama's 60Hz, so this is how a headless tuning run covers many game-days fast (e.g. 8 → 48× with
	// call_rate 60). Production zones omit it → 1 → no batching → byte-identical to a single tick/call.
	SimBatch int `json:"sim_batch,omitempty"`

	// Profile: TEST/TUNING ZONES ONLY — enable the PERFSTATS cost profiler (per-species server-CPU by
	// sub-phase + per-species leg counts + global pass timings + broadcast byte totals, flushed per game-day).
	// Pure observation, never hashed; production omits it → zero overhead (see profiler.go).
	Profile bool `json:"profile,omitempty"`

	// Cross-zone adjacency: edge direction ("north"/"south"/"east"/"west") -> neighbor zoneID.
	// Walking off an edge with a neighbor hidden-swaps into it (see CrossZoneController). Absent/""
	// = a hard edge (no crossing). +Y = north, so south edge = y0, north edge = y255.
	Neighbors map[string]string `json:"neighbors,omitempty"`
}

// ChunkData stores the two-layer tile data for a 32x32 cell chunk.
// Ground layer: floor tiles (grass, dirt, stone_path, etc.)
// Occupants layer: things on top (blocks, furniture, plants, trees, structures)
//
// Occupants use json.RawMessage for polymorphic storage:
//   - null: empty cell
//   - {"id":"...", "dir":0, "anchor":true}: anchor cell with occupant data
//   - {"id":"...", "dir":0}: footprint cell (anchor omitted = false)
type ChunkData struct {
	ChunkX    int                 `json:"chunk_x"`
	ChunkY    int                 `json:"chunk_y"`
	Ground    [][]string          `json:"ground"`    // 32x32 tile IDs (ChunkSize per side)
	Occupants [][]json.RawMessage `json:"occupants"` // 32x32 polymorphic
}

// OccupantCell represents parsed occupant layer data.
type OccupantCell struct {
	IsEmpty  bool            // null in JSON
	Occupant *PlacedOccupant // Occupant data (has Anchor=true for anchor cell)
}

// ParseOccupantCell interprets a json.RawMessage from the occupants layer.
func ParseOccupantCell(raw json.RawMessage) (*OccupantCell, error) {
	if raw == nil || string(raw) == "null" {
		return &OccupantCell{IsEmpty: true}, nil
	}

	// Parse occupant object {id, dir, anchor}
	var occ PlacedOccupant
	if err := json.Unmarshal(raw, &occ); err != nil {
		return nil, fmt.Errorf("invalid occupant cell: %w", err)
	}
	return &OccupantCell{Occupant: &occ}, nil
}

// LoadZoneConfig reads zone metadata from zone.json.
func LoadZoneConfig(zonePath string) (*ZoneConfig, error) {
	data, err := os.ReadFile(filepath.Join(zonePath, "zone.json"))
	if err != nil {
		return nil, fmt.Errorf("failed to read zone config: %w", err)
	}

	var zone ZoneConfig
	if err := json.Unmarshal(data, &zone); err != nil {
		return nil, fmt.Errorf("failed to parse zone config: %w", err)
	}

	// Defaults
	if zone.Width == 0 {
		zone.Width = ChunkSize * 8 // 256 cells (8 chunks × 32 cells)
	}
	if zone.Height == 0 {
		zone.Height = ChunkSize * 8 // 256 cells (8 chunks × 32 cells)
	}

	return &zone, nil
}

// LoadChunk reads chunk data from chunk_X_Y.json.
func LoadChunk(zonePath string, cx, cy int) (*ChunkData, error) {
	filename := fmt.Sprintf("chunk_%d_%d.json", cx, cy)
	data, err := os.ReadFile(filepath.Join(zonePath, filename))
	if err != nil {
		return nil, fmt.Errorf("failed to read chunk %d,%d: %w", cx, cy, err)
	}

	var chunk ChunkData
	if err := json.Unmarshal(data, &chunk); err != nil {
		return nil, fmt.Errorf("failed to parse chunk %d,%d: %w", cx, cy, err)
	}

	chunk.ChunkX = cx
	chunk.ChunkY = cy
	return &chunk, nil
}

// NewEmptyChunk creates a chunk filled with the given ground tile.
func NewEmptyChunk(cx, cy int, defaultTile string) *ChunkData {
	ground := make([][]string, ChunkSize)
	occupants := make([][]json.RawMessage, ChunkSize)

	for y := 0; y < ChunkSize; y++ {
		ground[y] = make([]string, ChunkSize)
		occupants[y] = make([]json.RawMessage, ChunkSize)
		for x := 0; x < ChunkSize; x++ {
			ground[y][x] = defaultTile
			occupants[y][x] = nil // Empty
		}
	}

	return &ChunkData{
		ChunkX:    cx,
		ChunkY:    cy,
		Ground:    ground,
		Occupants: occupants,
	}
}

// GetGroundTile returns the floor tile ID at local chunk coordinates.
func (c *ChunkData) GetGroundTile(lx, ly int) string {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return ""
	}
	return c.Ground[ly][lx]
}

// SetGroundTile sets the floor tile at local chunk coordinates.
func (c *ChunkData) SetGroundTile(lx, ly int, tileID string) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}
	c.Ground[ly][lx] = tileID
	return true
}

// GetOccupantCell returns the parsed occupant cell at local coordinates.
func (c *ChunkData) GetOccupantCell(lx, ly int) (*OccupantCell, error) {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return &OccupantCell{IsEmpty: true}, nil
	}
	return ParseOccupantCell(c.Occupants[ly][lx])
}

// SetOccupant places an occupant at local coordinates (anchor cell).
// Sets Anchor=true on the occupant before storing.
func (c *ChunkData) SetOccupant(lx, ly int, occ *PlacedOccupant) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}

	if occ == nil {
		c.Occupants[ly][lx] = nil
		return true
	}

	// Mark as anchor cell
	occ.Anchor = true
	data, err := json.Marshal(occ)
	if err != nil {
		return false
	}
	c.Occupants[ly][lx] = data
	return true
}

// SetFootprintCell marks a cell as part of a multi-cell occupant's footprint.
// Stores the occupant ID and direction but with Anchor=false (omitted in JSON).
func (c *ChunkData) SetFootprintCell(lx, ly int, occupantID string, dir int) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}
	occ := &PlacedOccupant{ID: occupantID, Dir: dir, Anchor: false}
	data, _ := json.Marshal(occ)
	c.Occupants[ly][lx] = data
	return true
}

// ClearOccupant removes an occupant from local coordinates.
func (c *ChunkData) ClearOccupant(lx, ly int) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}
	c.Occupants[ly][lx] = nil
	return true
}

// GlobalToChunk converts global cell coordinates to chunk + local coordinates.
func GlobalToChunk(gx, gy int) (chunkX, chunkY, localX, localY int) {
	chunkX = gx / ChunkSize
	chunkY = gy / ChunkSize
	localX = gx % ChunkSize
	localY = gy % ChunkSize

	// Handle negative coordinates correctly
	if gx < 0 && localX != 0 {
		chunkX--
		localX += ChunkSize
	}
	if gy < 0 && localY != 0 {
		chunkY--
		localY += ChunkSize
	}
	return
}

// ChunkToGlobal converts chunk + local coordinates to global cell coordinates.
func ChunkToGlobal(chunkX, chunkY, localX, localY int) (gx, gy int) {
	gx = chunkX*ChunkSize + localX
	gy = chunkY*ChunkSize + localY
	return
}

// ChunkKey generates a map key string for chunk coordinates.
func ChunkKey(cx, cy int) string {
	return fmt.Sprintf("%d,%d", cx, cy)
}
