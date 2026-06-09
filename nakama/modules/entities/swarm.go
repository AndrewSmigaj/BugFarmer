package entities

import (
	"math"
	"math/rand"
)

// SwarmState tracks a group of bugs moving together.
// Server manages position/count, client renders individual flies with deterministic simulation.
type SwarmState struct {
	ID        string
	SpeciesID string
	Position  EntityPosition
	Radius    float32   // Visual spread radius in blocks
	Count     int       // Number of alive bugs in swarm
	Facing    Direction // Movement direction hint for client
	Velocity  Vec2      // Current movement
	HomePos   EntityPosition
	WanderRad float32 // Max distance from home

	ReproduceCooldown float32 // Seconds until can reproduce

	// Condition meter (for subduing mechanics, 0-100 range)
	ConditionValue float32
	CurrentHP      int

	// Lifecycle (server-owned)
	Phase             string  // "feeding", "reproducing", "idle"
	Satiation         float32 // 0-100, increases when bugs feed
	ReproductionMeter float32 // 0-100, increases when bugs visit breeding sites

	// Movement target (pre-validated path)
	TargetX   float32 // Destination X (validated to be reachable)
	TargetY   float32 // Destination Y
	HasTarget bool    // Whether we have an active target

	// Think timer - swarms make decisions every few seconds, not every tick
	NextThinkTick int64 // Tick when swarm next evaluates targets

	// Cached food target (set at Think time; lets the per-tick at-food check be O(1) —
	// distance to this point + a registry validity lookup — instead of a chunk scan).
	TargetFoodID         string  // Ground-item id or station cell-key; "" = none
	TargetFoodX          float32 // World position of the food source
	TargetFoodY          float32
	TargetFoodDepletable bool // True for ground items/stations (required for BREEDING)

	// Forage duty cycle: the forage/wander MODE persists ~30-50s (10x the think cadence) so
	// behavior doesn't flicker leg-to-leg; movement legs within a mode stay short (3-5s).
	ForageMode    bool  // Current mode: seek food vs pure wander
	ModeUntilTick int64 // Tick when the mode rerolls

	// Bug ID tracking for deterministic catching
	RemovedBugIDs map[int]bool // Set of removed bug IDs (not serialized)
	NextBugID     int          // Next ID to assign for new bugs (reproduction)
}

// ClearFoodTarget drops the cached food target (depleted / phase change) and forces an
// immediate re-Think so the swarm retargets without the 3-5s think lag.
func (s *SwarmState) ClearFoodTarget(currentTick int64) {
	s.TargetFoodID = ""
	s.TargetFoodDepletable = false
	s.NextThinkTick = currentTick
}

// CanReproduce returns true if reproduction cooldown has elapsed
func (s *SwarmState) CanReproduce() bool {
	return s.ReproduceCooldown <= 0
}

// InitializeBugIDs sets up bug ID tracking for deterministic catching.
// Optional - RemoveBugs will lazy-initialize if needed.
func (s *SwarmState) InitializeBugIDs() {
	s.RemovedBugIDs = make(map[int]bool)
	s.NextBugID = s.Count // Bugs start with IDs 0 to Count-1
}

// IsBugAlive returns true if the bug ID is valid and has not been removed.
func (s *SwarmState) IsBugAlive(bugID int) bool {
	if bugID < 0 || bugID >= s.NextBugID {
		return false
	}
	// Safe to read from nil map - returns false (zero value)
	return !s.RemovedBugIDs[bugID]
}

// RemoveBugs marks the given bug IDs as removed and returns which were actually removed.
// Invalid or already-removed IDs are silently ignored.
func (s *SwarmState) RemoveBugs(bugIDs []int) []int {
	// Lazy initialization - safe even if InitializeBugIDs wasn't called
	if s.RemovedBugIDs == nil {
		s.RemovedBugIDs = make(map[int]bool)
		if s.NextBugID == 0 {
			s.NextBugID = s.Count
		}
	}

	var removed []int
	for _, id := range bugIDs {
		if s.IsBugAlive(id) {
			s.RemovedBugIDs[id] = true
			removed = append(removed, id)
		}
	}
	s.Count -= len(removed)
	return removed
}

// GetRemovedIDs returns a slice of all removed bug IDs (for late joiner sync).
func (s *SwarmState) GetRemovedIDs() []int {
	if len(s.RemovedBugIDs) == 0 {
		return nil
	}
	ids := make([]int, 0, len(s.RemovedBugIDs))
	for id := range s.RemovedBugIDs {
		ids = append(ids, id)
	}
	return ids
}

// GetID implements Entity interface
func (s *SwarmState) GetID() string {
	return s.ID
}

// GetPosition implements Entity interface
func (s *SwarmState) GetPosition() EntityPosition {
	return s.Position
}

// GetType implements Entity interface
func (s *SwarmState) GetType() string {
	return "swarm"
}

// WorldX returns the absolute world X coordinate
func (s *SwarmState) WorldX(chunkSize int) float32 {
	return float32(s.Position.ChunkX*chunkSize) + s.Position.LocalX
}

// WorldY returns the absolute world Y coordinate
func (s *SwarmState) WorldY(chunkSize int) float32 {
	return float32(s.Position.ChunkY*chunkSize) + s.Position.LocalY
}

// BlockedChecker is a function that checks if a world position blocks swarm movement
type BlockedChecker func(worldX, worldY float32) bool

// Think is called every few seconds (not every tick) to pick a new target.
// resourceX/resourceY are the closest resource, or NaN if none visible.
func (s *SwarmState) Think(species *BugSpecies, chunkSize int,
	resourceX, resourceY float32, isBlocked BlockedChecker) {

	currX := s.WorldX(chunkSize)
	currY := s.WorldY(chunkSize)

	var rawTargetX, rawTargetY float32
	if !math.IsNaN(float64(resourceX)) {
		// Go toward resource
		rawTargetX, rawTargetY = resourceX, resourceY
	} else {
		// Random direction within vision range
		angle := rand.Float32() * 2 * math.Pi
		dist := rand.Float32() * species.VisionRange
		rawTargetX = currX + float32(math.Cos(float64(angle)))*dist
		rawTargetY = currY + float32(math.Sin(float64(angle)))*dist
	}

	s.TargetX, s.TargetY = raycastToBlock(currX, currY, rawTargetX, rawTargetY, isBlocked)
	s.HasTarget = true
}

// Move is called every tick to move toward current target.
// This is cheap - just applies velocity, no decision making.
func (s *SwarmState) Move(deltaTime float32, species *BugSpecies, chunkSize int) {
	if !s.HasTarget {
		s.Velocity = Vec2{X: 0, Y: 0}
		s.Facing = VelocityToDirection(s.Velocity)
		return
	}

	currX := s.WorldX(chunkSize)
	currY := s.WorldY(chunkSize)

	dx, dy := s.TargetX-currX, s.TargetY-currY
	dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

	if dist < 0.5 {
		// Arrived at target - stop, wait for next Think
		s.HasTarget = false
		s.Velocity = Vec2{X: 0, Y: 0}
	} else {
		// Move toward target
		s.Velocity = Vec2{
			X: dx / dist * species.BaseSpeed,
			Y: dy / dist * species.BaseSpeed,
		}
		s.Position.LocalX += s.Velocity.X * deltaTime
		s.Position.LocalY += s.Velocity.Y * deltaTime
		s.Position.Normalize(chunkSize)
	}

	s.Facing = VelocityToDirection(s.Velocity)
}

// RaycastClamp exposes raycastToBlock for callers outside this package (e.g. placing a
// split-child swarm centre so it can't land through a fence/wall — penned swarms split INSIDE).
func RaycastClamp(startX, startY, endX, endY float32, isBlocked BlockedChecker) (float32, float32) {
	return raycastToBlock(startX, startY, endX, endY, isBlocked)
}

// raycastToBlock walks from start toward end, returning position just before first blocked cell.
// If path is clear, returns the end position. If isBlocked is nil, returns end directly.
func raycastToBlock(startX, startY, endX, endY float32, isBlocked BlockedChecker) (float32, float32) {
	if isBlocked == nil {
		return endX, endY
	}

	dx := endX - startX
	dy := endY - startY
	dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

	if dist < 0.5 {
		return endX, endY
	}

	// Normalize direction
	dirX := dx / dist
	dirY := dy / dist

	// Step through in 0.5-block increments (small enough to catch 1x1 cells)
	const stepSize float32 = 0.5
	steps := int(dist / stepSize)

	prevX, prevY := startX, startY
	for i := 1; i <= steps; i++ {
		checkX := startX + dirX*stepSize*float32(i)
		checkY := startY + dirY*stepSize*float32(i)

		if isBlocked(checkX, checkY) {
			// Return position just before the blocked cell
			return prevX, prevY
		}
		prevX, prevY = checkX, checkY
	}

	// Check final position
	if isBlocked(endX, endY) {
		return prevX, prevY
	}

	return endX, endY
}

// CheckPhaseTransition checks if swarm should transition to a new lifecycle phase
func (s *SwarmState) CheckPhaseTransition(species *BugSpecies) {
	switch s.Phase {
	case "feeding":
		if s.Satiation >= 100 {
			s.Phase = "reproducing"
		}
	case "reproducing":
		// The reproduction itself happens in the match loop (it needs food-source access:
		// meter fills only AT a depletable source, then Count doubles + SWARM_REPRODUCED is
		// emitted and meters reset). Here we only handle STARVATION: if satiation decayed
		// away while hunting for a breeding source, fall back to feeding.
		if s.Satiation <= 0 {
			s.Phase = "feeding"
			s.ReproductionMeter = 0
		}
	case "", "idle":
		s.Phase = "feeding" // Default to feeding
	}
}

// GetCurrentAttractions returns the resource IDs this swarm is attracted to based on current phase
func (s *SwarmState) GetCurrentAttractions(species *BugSpecies) []string {
	if species.AttractionsByPhase == nil {
		return nil
	}
	if attractions, ok := species.AttractionsByPhase[s.Phase]; ok {
		return attractions
	}
	return nil
}

// VelocityToDirection converts a velocity vector to the nearest cardinal direction
func VelocityToDirection(v Vec2) Direction {
	if v.X == 0 && v.Y == 0 {
		return DirDown
	}
	if math.Abs(float64(v.X)) > math.Abs(float64(v.Y)) {
		if v.X > 0 {
			return DirRight
		}
		return DirLeft
	}
	if v.Y > 0 {
		return DirUp
	}
	return DirDown
}
