package entities

// BugAIState represents the current AI behavior mode
type BugAIState int

const (
	BugIdle BugAIState = iota
	BugWander
	BugAlert
	BugChase
	BugFlee
)

// IndividualBugState tracks single entity bugs (millipede, beetle).
// These have unique movement patterns (Bezier curves) and individual AI.
type IndividualBugState struct {
	ID        string
	SpeciesID string
	Position  EntityPosition
	Facing    Direction

	// Bezier curve movement (millipedes)
	PathPoints []Vec2  // Control points
	PathT      float32 // Progress along curve [0, 1]
	Speed      float32

	// AI state
	State    BugAIState // idle, wander, alert, chase, flee
	TargetID string     // Player ID if chasing/fleeing

	// Condition meter (for subduing mechanics)
	ConditionValue float32 // Current meter level (0-100)
	CurrentHP      int     // For HP-based creatures (starts at MaxHP, 0 = catchable)
}

// GetID implements Entity interface
func (b *IndividualBugState) GetID() string {
	return b.ID
}

// GetPosition implements Entity interface
func (b *IndividualBugState) GetPosition() EntityPosition {
	return b.Position
}

// GetType implements Entity interface
func (b *IndividualBugState) GetType() string {
	return "bug"
}
