package world

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// ChunkSize is cells per chunk dimension (32x32 cells = 512x512 pixels).
const ChunkSize = 32

// ZoneConfig describes a zone's metadata and spawn settings.
// Zones are 16x16 chunks (512x512 cells at 16px per cell = 8192x8192 pixels).
type ZoneConfig struct {
	ZoneID     string `json:"zone_id"`
	Name       string `json:"name"`
	Row        int    `json:"row"`         // Zone grid row
	Col        int    `json:"col"`         // Zone grid column
	Width      int    `json:"width"`       // Width in cells (default 512)
	Height     int    `json:"height"`      // Height in cells (default 512)
	SpawnPoint [2]int `json:"spawn_point"` // Default spawn (cell coords)
	BiomeType  string `json:"biome_type"`  // "meadow", "forest", "cave", etc.
}

// ChunkData stores the two-layer tile data for a 32x32 cell chunk.
// Ground layer: floor tiles (grass, dirt, stone_path, etc.)
// Occupants layer: things on top (blocks, furniture, plants, trees, structures)
//
// Occupants use json.RawMessage for polymorphic storage:
//   - null: empty cell
//   - "@": blocked by multi-cell occupant (anchor is in adjacent cell)
//   - {"id":"...", "dir":0}: anchor cell with occupant data
type ChunkData struct {
	ChunkX    int                 `json:"chunk_x"`
	ChunkY    int                 `json:"chunk_y"`
	Ground    [][]string          `json:"ground"`    // 16x16 tile IDs
	Occupants [][]json.RawMessage `json:"occupants"` // 16x16 polymorphic
}

// OccupantCell represents parsed occupant layer data.
type OccupantCell struct {
	IsEmpty   bool            // null in JSON
	IsBlocked bool            // "@" marker - blocked by adjacent multi-cell occupant
	Occupant  *PlacedOccupant // Anchor cell with occupant data
}

// ParseOccupantCell interprets a json.RawMessage from the occupants layer.
func ParseOccupantCell(raw json.RawMessage) (*OccupantCell, error) {
	if raw == nil || string(raw) == "null" {
		return &OccupantCell{IsEmpty: true}, nil
	}

	// Check for "@" blocked marker
	var str string
	if err := json.Unmarshal(raw, &str); err == nil {
		if str == "@" {
			return &OccupantCell{IsBlocked: true}, nil
		}
		return nil, fmt.Errorf("invalid occupant string: %q (expected \"@\")", str)
	}

	// Full occupant object {id, dir}
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
		zone.Width = ChunkSize * 16 // 512 cells (16 chunks × 32 cells)
	}
	if zone.Height == 0 {
		zone.Height = ChunkSize * 16 // 512 cells (16 chunks × 32 cells)
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
func (c *ChunkData) SetOccupant(lx, ly int, occ *PlacedOccupant) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}

	if occ == nil {
		c.Occupants[ly][lx] = nil
		return true
	}

	data, err := json.Marshal(occ)
	if err != nil {
		return false
	}
	c.Occupants[ly][lx] = data
	return true
}

// SetBlockedMarker marks a cell as blocked by a multi-cell occupant.
// Used for non-anchor cells of multi-cell occupants.
func (c *ChunkData) SetBlockedMarker(lx, ly int) bool {
	if lx < 0 || lx >= ChunkSize || ly < 0 || ly >= ChunkSize {
		return false
	}
	data, _ := json.Marshal("@")
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
