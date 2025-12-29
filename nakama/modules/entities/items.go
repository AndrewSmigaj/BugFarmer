package entities

// GroundItem represents a dropped item in the world (seeds, etc.)
type GroundItem struct {
	ID       string
	ItemType string         // "acorn", "flower_seed", etc.
	Position EntityPosition
	Lifetime float32        // Seconds until despawn (60.0 default)
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
