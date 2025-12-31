package world

import (
	"encoding/json"
	"fmt"
	"os"
)

// TileDefinition describes a floor/ground tile's properties.
// These are flat terrain tiles that players walk on.
type TileDefinition struct {
	ID string `json:"id"`

	// Movement
	MovementMult  float32 `json:"movement_mult"`  // Speed: 1.0=normal, 0.5=slow(mud), 1.1=fast(path)
	BlocksPlayers bool    `json:"blocks_players"` // Impassable (deep water)
	BlocksBugs    bool    `json:"blocks_bugs"`    // Bugs can't cross

	// What can be placed on this floor tile?
	AcceptsPlant     bool `json:"accepts_plant"`     // Seeds can be planted (garden_plot)
	AcceptsFurniture bool `json:"accepts_furniture"` // Furniture, crafting stations
	AcceptsStructure bool `json:"accepts_structure"` // Walls, fences, doors

	// Tool actions (convert this tile to another)
	// Example: {"hoe": "garden_plot"} - using hoe on grass makes garden plot
	ToolActions map[string]string `json:"tool_actions,omitempty"`
}

// LoadTileDefinitions reads floor tile definitions from JSON.
// Format: {"grass": {...}, "garden_plot": {...}, ...}
func LoadTileDefinitions(path string) (map[string]*TileDefinition, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read tile config: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse tile config: %w", err)
	}

	tiles := make(map[string]*TileDefinition)
	for id, tileData := range raw {
		var tile TileDefinition
		if err := json.Unmarshal(tileData, &tile); err != nil {
			return nil, fmt.Errorf("failed to parse tile %s: %w", id, err)
		}
		tile.ID = id

		// Default walkable tiles to normal speed
		if tile.MovementMult == 0 && !tile.BlocksPlayers {
			tile.MovementMult = 1.0
		}

		tiles[id] = &tile
	}

	return tiles, nil
}

// GetToolActionResult returns the resulting tile when using a tool.
func (t *TileDefinition) GetToolActionResult(toolType string) string {
	if t.ToolActions == nil {
		return ""
	}
	return t.ToolActions[toolType]
}

// IsWalkable returns true if players can walk on this tile.
func (t *TileDefinition) IsWalkable() bool {
	return !t.BlocksPlayers
}

// CanPlaceOccupant checks if an occupant category can be placed here.
func (t *TileDefinition) CanPlaceOccupant(category string) bool {
	if t.BlocksPlayers {
		return false
	}
	switch category {
	case "plant":
		return t.AcceptsPlant
	case "furniture", "crafting", "storage", "lighting", "beekeeping":
		return t.AcceptsFurniture
	case "structure", "fence", "wall", "door", "natural":
		return t.AcceptsStructure
	default:
		return t.AcceptsFurniture
	}
}
