package world

import (
	"encoding/json"
	"fmt"
	"os"
)

// OccupantDefinition describes an object placed on floor tiles.
// Includes blocks, furniture, plants, trees, walls, fences, doors, etc.
type OccupantDefinition struct {
	ID       string `json:"id"`
	Category string `json:"category"` // "block", "natural", "furniture", "crafting", "structure", etc.

	// Footprint (grid cells occupied, for default direction 0=down)
	// When rotated 90/270 degrees, W and H swap.
	FootprintW int `json:"footprint_w"` // Width in cells (default dir)
	FootprintH int `json:"footprint_h"` // Height in cells (default dir)

	// Movement blocking
	BlocksPlayers bool `json:"blocks_players"` // Solid - can't walk through
	BlocksBugs    bool `json:"blocks_bugs"`    // Bugs can't pass

	// Breaking/harvesting
	IsBreakable      bool   `json:"is_breakable"`
	RequiredToolType string `json:"required_tool_type"` // "pickaxe", "axe", "shovel", ""
	RequiredToolTier int    `json:"required_tool_tier"` // 1=wood...9=diamond
	HP               int    `json:"hp"`                 // Hits to break
	DropItemID       string `json:"drop_item_id"`       // Item dropped
	DropCount        int    `json:"drop_count"`         // Quantity (default 1)

	// For blocks only: floor tile revealed when block removed
	RevealsFloorTile string `json:"reveals_floor_tile"`

	// Rotation
	Rotatable  bool `json:"rotatable"`   // Can player rotate when placing?
	Directions int  `json:"directions"`  // 0=fixed, 2=H/V only, 4=all directions

	// Interaction
	Interactable    bool   `json:"interactable"`
	InteractionType string `json:"interaction_type"` // "craft", "storage", "door", etc.

	// Placement
	PlaceableByPlayer bool   `json:"placeable_by_player"`
	RequiresFloorTile string `json:"requires_floor_tile"` // e.g., "garden_plot" for plants
}

// PlacedOccupant is stored in chunk data at anchor cell.
// Blocked cells store "@" marker string.
type PlacedOccupant struct {
	ID  string `json:"id"`
	Dir int    `json:"dir,omitempty"` // 0=down, 1=left, 2=right, 3=up
}

// LoadOccupantDefinitions reads definitions from JSON.
func LoadOccupantDefinitions(path string) (map[string]*OccupantDefinition, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read occupant config: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse occupant config: %w", err)
	}

	occupants := make(map[string]*OccupantDefinition)
	for id, occData := range raw {
		var occ OccupantDefinition
		if err := json.Unmarshal(occData, &occ); err != nil {
			return nil, fmt.Errorf("failed to parse occupant %s: %w", id, err)
		}
		occ.ID = id

		// Defaults
		if occ.FootprintW == 0 {
			occ.FootprintW = 1
		}
		if occ.FootprintH == 0 {
			occ.FootprintH = 1
		}
		if occ.DropCount == 0 && occ.DropItemID != "" {
			occ.DropCount = 1
		}
		if occ.Directions == 0 && occ.Rotatable {
			occ.Directions = 4
		}

		occupants[id] = &occ
	}

	return occupants, nil
}

// GetFootprint returns (width, height) for the given direction.
// Dir 0 (down) and 3 (up): use W x H as defined
// Dir 1 (left) and 2 (right): swap to H x W
func (o *OccupantDefinition) GetFootprint(dir int) (int, int) {
	if dir == 1 || dir == 2 { // Left or Right - rotated 90 degrees
		return o.FootprintH, o.FootprintW
	}
	return o.FootprintW, o.FootprintH
}

// GetBlockedCells returns all grid positions occupied by this occupant
// when anchor is at (ax, ay) with given direction.
// Anchor is always bottom-left of the rotated footprint.
func (o *OccupantDefinition) GetBlockedCells(ax, ay, dir int) [][2]int {
	w, h := o.GetFootprint(dir)
	cells := make([][2]int, 0, w*h)

	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			cells = append(cells, [2]int{ax + dx, ay + dy})
		}
	}

	return cells
}

// CanBreakWith checks if this can be broken with the given tool.
func (o *OccupantDefinition) CanBreakWith(toolType string, toolTier int) bool {
	if !o.IsBreakable {
		return false
	}
	if o.RequiredToolType != "" && o.RequiredToolType != toolType {
		return false
	}
	return toolTier >= o.RequiredToolTier
}
