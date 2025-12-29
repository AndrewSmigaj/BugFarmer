package entities

// EggClusterState tracks eggs laid by swarms.
// Server manages hatching timers, client renders egg sprites.
type EggClusterState struct {
	ID          string
	SpeciesID   string         // What species will hatch
	Position    EntityPosition // Where eggs were laid
	Count       int            // Number of eggs
	HatchTimer  float32        // Countdown until hatch
	ParentSwarm string         // Original swarm ID (for merging back)
}

// GetID implements Entity interface
func (e *EggClusterState) GetID() string {
	return e.ID
}

// GetPosition implements Entity interface
func (e *EggClusterState) GetPosition() EntityPosition {
	return e.Position
}

// GetType implements Entity interface
func (e *EggClusterState) GetType() string {
	return "eggs"
}

// HatchProgress returns 0.0-1.0 progress toward hatching.
// Requires species to know total hatch time.
func (e *EggClusterState) HatchProgress(species *BugSpecies) float32 {
	if species == nil || species.HatchTime <= 0 {
		return 1.0
	}
	progress := 1.0 - (e.HatchTimer / species.HatchTime)
	if progress < 0 {
		return 0
	}
	if progress > 1 {
		return 1
	}
	return progress
}
