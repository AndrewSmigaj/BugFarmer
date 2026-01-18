package world

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"bugfarmer/entities"
)

// EntityDef is the unified definition for all game entities.
// Three types:
// - items (inventory-only): resources, tools, consumables - World is nil
// - occupants (world-only): trees, rocks, natural objects - only World populated
// - placeables (both): blocks, furniture, structures - both inventory props and World
type EntityDef struct {
	ID       string `json:"-"` // Set from map key
	Name     string `json:"name"`
	Category string `json:"category"`

	// Inventory properties (items and placeables only)
	Stackable bool `json:"stackable,omitempty"`
	MaxStack  int  `json:"max_stack,omitempty"`
	SellPrice int  `json:"sell_price,omitempty"`
	BuyPrice  int  `json:"buy_price,omitempty"`

	// Tool properties (category = "tool")
	ToolType         string         `json:"tool_type,omitempty"`
	ToolTier         int            `json:"tool_tier,omitempty"`
	Reach            float32        `json:"reach,omitempty"`
	MiningSpeed      float32        `json:"mining_speed,omitempty"`
	Durability       int            `json:"durability,omitempty"`
	CatchRadius      float32        `json:"catch_radius,omitempty"`      // For nets
	CooldownTicks    int            `json:"cooldown_ticks,omitempty"`    // Ticks between uses (farming tools)
	MetadataDefaults map[string]int `json:"metadata_defaults,omitempty"` // Initial metadata (watering can capacity)

	// Seed properties
	PlacesCrop string `json:"places_crop,omitempty"` // Crop type this seed plants

	// Consumable properties
	Effect string `json:"effect,omitempty"`

	// World data (nil for inventory-only items)
	World *WorldData `json:"world,omitempty"`

	// Entity type set during loading: "item", "occupant", or "placeable"
	EntityType string `json:"-"`
}

// WorldData describes how an entity appears/behaves in the world.
type WorldData struct {
	Footprint     []int  `json:"footprint"` // [width, height] in grid cells
	Pivot         string `json:"pivot"`     // "bc" (bottom-center), "c" (center)
	BlocksPlayers bool   `json:"blocks_players,omitempty"`
	BlocksBugs    bool   `json:"blocks_bugs,omitempty"`

	// Rotation
	Rotatable  bool `json:"rotatable,omitempty"`
	Directions int  `json:"directions,omitempty"` // 2 or 4

	// Interaction
	Interactable    bool   `json:"interactable,omitempty"`
	InteractionType string `json:"interaction_type,omitempty"` // "craft", "storage", "door", "sleep", "sign", "well", "beehive"

	// Breaking (nil = unbreakable)
	Breakable *BreakableData `json:"breakable,omitempty"`

	// Fruit tree properties
	FruitType      string `json:"fruit_type,omitempty"`       // "apple", "orange"
	MaxFruit       int    `json:"max_fruit,omitempty"`        // Maximum fruit capacity
	FruitGrowTicks int    `json:"fruit_grow_ticks,omitempty"` // Ticks per fruit growth
	FruitDropTicks int    `json:"fruit_drop_ticks,omitempty"` // Ticks until fruit drops
}

// BreakableData describes how something can be broken/harvested.
type BreakableData struct {
	HP               int         `json:"hp"`
	RequiredToolType string      `json:"required_tool_type,omitempty"`
	RequiredToolTier int         `json:"required_tool_tier,omitempty"`
	Drops            []DropEntry `json:"drops,omitempty"`
}

// DropEntry describes a single drop from breaking something.
type DropEntry struct {
	ItemID string  `json:"item_id"`
	Count  int     `json:"count"`
	Chance float32 `json:"chance"` // 0.0 to 1.0
}

// GetFootprint returns (width, height) for the given direction.
// Dir 0 (down) and 3 (up): use W x H as defined
// Dir 1 (left) and 2 (right): swap to H x W
func (w *WorldData) GetFootprint(dir int) (int, int) {
	if w == nil || len(w.Footprint) < 2 {
		return 1, 1
	}
	width, height := w.Footprint[0], w.Footprint[1]
	if width == 0 {
		width = 1
	}
	if height == 0 {
		height = 1
	}
	if dir == 1 || dir == 2 {
		return height, width
	}
	return width, height
}

// CanBreakWith checks if this can be broken with the given tool.
func (b *BreakableData) CanBreakWith(toolType string, toolTier int) bool {
	if b == nil {
		return false
	}
	if b.RequiredToolType != "" && b.RequiredToolType != toolType {
		return false
	}
	return toolTier >= b.RequiredToolTier
}

// IsPlaceable returns true if this entity can be placed by players.
func (e *EntityDef) IsPlaceable() bool {
	return e.EntityType == "placeable"
}

// IsItem returns true if this entity can exist in inventory.
func (e *EntityDef) IsItem() bool {
	return e.EntityType == "item" || e.EntityType == "placeable"
}

// HasWorldPresence returns true if this entity can exist in the world.
func (e *EntityDef) HasWorldPresence() bool {
	return e.World != nil
}

// GetFootprint is a convenience method on EntityDef.
func (e *EntityDef) GetFootprint(dir int) (int, int) {
	if e.World == nil {
		return 1, 1
	}
	return e.World.GetFootprint(dir)
}

// CanBreakWith is a convenience method on EntityDef.
func (e *EntityDef) CanBreakWith(toolType string, toolTier int) bool {
	if e.World == nil || e.World.Breakable == nil {
		return false
	}
	return e.World.Breakable.CanBreakWith(toolType, toolTier)
}

// IsBreakable returns true if this entity can be broken.
func (e *EntityDef) IsBreakable() bool {
	return e.World != nil && e.World.Breakable != nil
}

// GetHP returns the HP for breakable entities, 0 otherwise.
func (e *EntityDef) GetHP() int {
	if e.World == nil || e.World.Breakable == nil {
		return 0
	}
	return e.World.Breakable.HP
}

// GetDrops returns the drop list for breakable entities, nil otherwise.
func (e *EntityDef) GetDrops() []DropEntry {
	if e.World == nil || e.World.Breakable == nil {
		return nil
	}
	return e.World.Breakable.Drops
}

// LoadAllEntities loads entities from all three JSON files into a single map.
// Returns the entity map and a list of any warnings encountered.
func LoadAllEntities(dataPath string) (map[string]*EntityDef, []string, error) {
	entities := make(map[string]*EntityDef)
	var warnings []string

	// Load items (inventory-only)
	itemsPath := filepath.Join(dataPath, "entities", "items.json")
	if w, err := loadEntityFile(itemsPath, "item", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load items: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	// Load occupants (world-only)
	occupantsPath := filepath.Join(dataPath, "entities", "occupants.json")
	if w, err := loadEntityFile(occupantsPath, "occupant", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load occupants: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	// Load placeables (both inventory and world)
	placeablesPath := filepath.Join(dataPath, "entities", "placeables.json")
	if w, err := loadEntityFile(placeablesPath, "placeable", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load placeables: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	return entities, warnings, nil
}

// loadEntityFile loads a single JSON file and adds entities to the map.
// Returns warnings for duplicate IDs.
func loadEntityFile(path, entityType string, entities map[string]*EntityDef) ([]string, error) {
	var warnings []string

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read %s: %w", path, err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse %s: %w", path, err)
	}

	for id, entData := range raw {
		// Skip comment fields
		if id == "_comment" {
			continue
		}

		// Check for duplicate IDs
		if existing, exists := entities[id]; exists {
			warnings = append(warnings, fmt.Sprintf(
				"duplicate entity ID '%s': %s overwrites %s",
				id, entityType, existing.EntityType,
			))
		}

		var ent EntityDef
		if err := json.Unmarshal(entData, &ent); err != nil {
			return warnings, fmt.Errorf("failed to parse entity %s: %w", id, err)
		}

		ent.ID = id
		ent.EntityType = entityType

		// Apply defaults
		applyDefaults(&ent)

		entities[id] = &ent
	}

	return warnings, nil
}

// applyDefaults sets sensible defaults for missing values.
func applyDefaults(e *EntityDef) {
	// Default stack size for stackables
	if e.Stackable && e.MaxStack == 0 {
		e.MaxStack = 99
	}

	// World data defaults
	if e.World != nil {
		// Ensure footprint has at least 2 elements
		if len(e.World.Footprint) < 2 {
			e.World.Footprint = []int{1, 1}
		}
		if e.World.Footprint[0] == 0 {
			e.World.Footprint[0] = 1
		}
		if e.World.Footprint[1] == 0 {
			e.World.Footprint[1] = 1
		}
		if e.World.Pivot == "" {
			e.World.Pivot = "bc"
		}
		if e.World.Rotatable && e.World.Directions == 0 {
			e.World.Directions = 4
		}

		// Breakable defaults
		if e.World.Breakable != nil {
			for i := range e.World.Breakable.Drops {
				if e.World.Breakable.Drops[i].Count == 0 {
					e.World.Breakable.Drops[i].Count = 1
				}
				if e.World.Breakable.Drops[i].Chance == 0 {
					e.World.Breakable.Drops[i].Chance = 1.0
				}
			}
		}
	}
}

// LoadCropDefs loads crop definitions from crops.json
func LoadCropDefs(basePath string) (map[string]*entities.CropDef, error) {
	crops := make(map[string]*entities.CropDef)

	path := filepath.Join(basePath, "entities", "crops.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read crops.json: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse crops.json: %w", err)
	}

	for id, cropData := range raw {
		if id == "_comment" {
			continue
		}

		var def entities.CropDef
		if err := json.Unmarshal(cropData, &def); err != nil {
			return nil, fmt.Errorf("failed to parse crop %s: %w", id, err)
		}

		// Apply defaults
		if def.GrowthStages == 0 {
			def.GrowthStages = 4
		}
		if def.WateringsPerStage == 0 {
			def.WateringsPerStage = 3
		}
		if def.MaxDailyWaterings == 0 {
			def.MaxDailyWaterings = 2
		}
		if def.HarvestCountMin == 0 {
			def.HarvestCountMin = 1
		}
		if def.HarvestCountMax == 0 {
			def.HarvestCountMax = def.HarvestCountMin
		}

		crops[id] = &def
	}

	return crops, nil
}
