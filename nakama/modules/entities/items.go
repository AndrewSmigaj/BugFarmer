package entities

// GroundItem represents a dropped item in the world (seeds, etc.)
type GroundItem struct {
	ID        string
	ItemType  string         // "acorn", "flower_seed", etc.
	Count     int            // Stack count (default 1)
	Position  EntityPosition
	Lifetime  float32        // Seconds until despawn (60.0 default)
	DecaysTo  string         // Item type this decays into ("apple" -> "rotten_apple")
	FoodValue int            // Food value for bugs (100 for rotten fruit, consumed by flies)
	FoodFrac  float32        // Fractional food drained (consumption accumulator)
	IsCarrion bool           // A bug carcass: detritivore food only — excluded from the "rotten_fruit" wildcard
}

// GetID implements Entity interface
func (g *GroundItem) GetID() string {
	return g.ID
}

// GetPosition implements Entity interface
func (g *GroundItem) GetPosition() EntityPosition {
	return g.Position
}

// GetType implements Entity interface
func (g *GroundItem) GetType() string {
	return "item"
}
