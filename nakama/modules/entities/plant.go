package entities

import (
	"encoding/json"
	"fmt"
	"os"
)

// PlantState tracks breeding plants in the world.
// Plants are consumed when bugs breed on them.
type PlantState struct {
	ID         string
	PlantType  string         // "rotting_fruit", "flower", etc.
	Position   EntityPosition // Grid origin position
	Health     int            // Consumed when breeding occurs
	GrowthTime float32        // Time since planted (for natural ones)
}

// GetID implements Entity interface
func (p *PlantState) GetID() string {
	return p.ID
}

// GetPosition implements Entity interface
func (p *PlantState) GetPosition() EntityPosition {
	return p.Position
}

// GetType implements Entity interface
func (p *PlantState) GetType() string {
	return "plant"
}

// PlantDef defines a plant type's properties (loaded from config)
type PlantDef struct {
	PlantType   string   `json:"plant_type"`   // "rotting_fruit", "flower", "oak_tree"
	SeedType    string   `json:"seed_type"`    // "fruit_seed", "flower_seed", "acorn"
	Health      int      `json:"health"`       // How many breeding cycles before consumed
	DropsSeed   bool     `json:"drops_seed"`   // Does it drop seed when destroyed?
	SpawnWeight float32  `json:"spawn_weight"` // Relative probability for natural spawning
	BreedTypes  []string `json:"breed_types"`  // Which bug species can breed here
}

// LoadPlantDefs reads plant definitions from JSON config
func LoadPlantDefs(path string) (map[string]*PlantDef, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read plant config: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse plant config: %w", err)
	}

	defs := make(map[string]*PlantDef)
	for plantType, defData := range raw {
		var def PlantDef
		if err := json.Unmarshal(defData, &def); err != nil {
			return nil, fmt.Errorf("failed to parse plant %s: %w", plantType, err)
		}
		def.PlantType = plantType
		defs[plantType] = &def
	}

	return defs, nil
}
