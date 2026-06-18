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
	CompostCooldown   float32 // Detritivores: seconds until the next compost-input deposit (server-only)
	StarveTimer       float32 // Seconds the swarm has been at 0 satiation; past a threshold it starves (server-only)
	// Per-bug natural-death schedule: bugID -> absolute tick the bug dies of old age. Set at birth,
	// carried through merge/split like BugHP, cleaned in RemoveBugs. Server-only, NOT in the state hash
	// (clients learn of deaths only via BUG_REMOVED events). Absent / lifespan<=0 = the bug is immortal.
	DeathTick map[int]int64

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

	// Per-leg speed multiplier (hunt ×1.5, prey-flee ×1.8, surge ×3.5...). SYNC CONTRACT
	// (architecture_swarm_sync.md §14): Move multiplies by it AND the leg-event emission
	// carries BaseSpeed*SpeedMult — server position and client leg interpolation must
	// agree. It is written ONLY in code paths that immediately emit a leg (never
	// mid-leg: clients capture speed per-leg), and EVERY leg-emitting path writes it
	// (the shared forage path writes 1.0 — otherwise a swarm that fled keeps the flee
	// speed forever, consistently on both sides and invisible to every harness).
	// 0 means "unset" and reads as 1.0.
	SpeedMult float32

	// Predation (server-only; outputs ride the existing event vocabulary).
	// TargetPreyID is the Think-cached hunt target (the TargetFoodID pattern: the
	// per-tick strike check is O(1)). MUTUALLY EXCLUSIVE with TargetFoodID — setting
	// one clears the other, else a strike could fire while parked on carrion.
	TargetPreyID   string // prey swarm id; "" = not hunting
	HuntStartTick  int64  // when the current hunt began (timeout)
	LastStrikeTick int64  // strike cooldown anchor
	LastAttackTick int64  // player-sting/bite cooldown anchor

	// Nest membership (wasps). Phase strings for nest predators: "feeding" (hunt),
	// "homing" (carry brood back), "defending" (chase a nest threat). An ORPHAN
	// (NestKey == "") never breeds, tethers to its last HomePos, still hunts/stings.
	NestKey         string // "gx,gy" of the home nest; "" = orphan
	CarryingBrood   bool   // sated trip in progress (a bool-carry, not a meter)
	HomingStartTick int64  // homing timeout anchor (600 ticks drops the brood)
	DefendUntilTick int64  // defending exits at this tick (or by distance hysteresis)
	DefendTargetID  string // player being chased while defending

	// ActionState (centipede): what the bug is FORCIBLY DOING right now — orthogonal
	// to the lifecycle Phase (what it WANTS). "" | "windup" | "surge" | "recover" |
	// "turnaround" | "gnaw". Runs per-tick BEFORE the think gate and owns the swarm
	// while active.
	ActionState       string
	ActionUntilTick   int64   // current action ends/advances at this tick
	SurgeCooldownUntil int64  // no new windup before this
	WindupTargetID    string  // the player being lunged at
	WindupStartX      float32 // their position at windup START (the velocity sample)
	WindupStartY      float32
	WanderHeading     float32 // serpentine wander heading (radians)
	ClampedLegStreak  int     // dead-end escape hatch: 3 fully-clamped legs => free roll
	TurnLegsLeft      int     // turnaround arc legs remaining after a missed surge
	GnawKey           string  // "gx,gy" of the fence being chewed
	GnawNextTick      int64   // next gnaw damage tick
	GnawCooldownUntil int64   // armed on ABANDONED gnaws only (successful breaks chain)

	// Bug ID tracking for deterministic catching
	RemovedBugIDs map[int]bool // Set of removed bug IDs (not serialized)
	NextBugID     int          // Next ID to assign for new bugs (reproduction)

	// Combat: sparse per-bug HP — stores ONLY damaged bugs (absent = full species MaxHP).
	// Server-authoritative; clients hold a display-only copy fed by MeleeResultMessage.
	// Cleaned inside RemoveBugs; transferred along the deterministic id mappings at
	// split/merge (see checkSwarmSplitting/checkSwarmMerging).
	BugHP map[int]int
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
			// Centralized BugHP cleanup: a removed bug (caught, killed, split-shed)
			// never leaks a stale damaged-HP entry.
			delete(s.BugHP, id)
			delete(s.DeathTick, id) // same: no stale natural-death schedule for a gone bug

		}
	}
	s.Count -= len(removed)
	return removed
}

// DamageBug applies damage to an alive bug. Returns (hpLeft, true) when the bug survives
// with hpLeft > 0, or (0, false) when the hit kills it (caller removes via RemoveBugs) —
// also (0, false) for dead/invalid ids with killed=false semantics handled by IsBugAlive
// at the call site. maxHP <= 0 is treated as 1.
func (s *SwarmState) DamageBug(bugID, damage, maxHP int) (int, bool) {
	if maxHP <= 0 {
		maxHP = 1
	}
	hp, damaged := 0, false
	if s.BugHP != nil {
		hp, damaged = s.BugHP[bugID]
	}
	if !damaged {
		hp = maxHP
	}
	hp -= damage
	if hp <= 0 {
		return 0, false // kill — caller removes (RemoveBugs deletes the HP entry)
	}
	if s.BugHP == nil {
		s.BugHP = make(map[int]int)
	}
	s.BugHP[bugID] = hp
	return hp, true
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
	resourceX, resourceY float32, isBlocked BlockedChecker, rng *rand.Rand) {

	currX := s.WorldX(chunkSize)
	currY := s.WorldY(chunkSize)

	var rawTargetX, rawTargetY float32
	if !math.IsNaN(float64(resourceX)) {
		// Go toward resource
		rawTargetX, rawTargetY = resourceX, resourceY
	} else {
		// Random direction within vision range
		angle := rng.Float32() * 2 * math.Pi
		dist := rng.Float32() * species.VisionRange
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
		// Move toward target at the LEG's speed (BaseSpeed × the per-leg SpeedMult —
		// the leg event carries the same product, keeping client interpolation in step)
		speed := species.BaseSpeed * s.EffectiveSpeedMult()
		s.Velocity = Vec2{
			X: dx / dist * speed,
			Y: dy / dist * speed,
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

// RaycastClampWithBlock is RaycastClamp that ALSO reports the first blocking cell
// (integer grid coords) when the ray was clamped. hit=false means the path was clear.
// Consumers (the gnaw trigger, the bite LOS gate) need the cell — deriving it outside
// would couple to the internal step size.
func RaycastClampWithBlock(startX, startY, endX, endY float32, isBlocked BlockedChecker) (cx, cy float32, blockX, blockY int, hit bool) {
	if isBlocked == nil {
		return endX, endY, 0, 0, false
	}
	dx := endX - startX
	dy := endY - startY
	dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
	if dist < 0.5 {
		return endX, endY, 0, 0, false
	}
	dirX := dx / dist
	dirY := dy / dist
	const stepSize float32 = 0.5
	steps := int(dist / stepSize)

	prevX, prevY := startX, startY
	for i := 1; i <= steps; i++ {
		checkX := startX + dirX*stepSize*float32(i)
		checkY := startY + dirY*stepSize*float32(i)
		if isBlocked(checkX, checkY) {
			return prevX, prevY, int(math.Floor(float64(checkX))), int(math.Floor(float64(checkY))), true
		}
		prevX, prevY = checkX, checkY
	}
	if isBlocked(endX, endY) {
		return prevX, prevY, int(math.Floor(float64(endX))), int(math.Floor(float64(endY))), true
	}
	return endX, endY, 0, 0, false
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

// EffectiveSpeedMult reads the per-leg speed multiplier (0 = unset = 1.0).
func (s *SwarmState) EffectiveSpeedMult() float32 {
	if s.SpeedMult <= 0 {
		return 1.0
	}
	return s.SpeedMult
}

// FirstAliveBugIDs returns the n lowest alive bug ids (ascending) — the deterministic
// predation-kill pick. Mirrors IsBugAlive's logic with RemoveBugs' lazy-init bound:
// a swarm that never grew/lost bugs has NextBugID 0 and live ids 0..Count-1.
func (s *SwarmState) FirstAliveBugIDs(n int) []int {
	bound := s.NextBugID
	if bound == 0 {
		bound = s.Count
	}
	ids := make([]int, 0, n)
	for id := 0; id < bound && len(ids) < n; id++ {
		if !s.RemovedBugIDs[id] { // nil-map-safe read
			ids = append(ids, id)
		}
	}
	return ids
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
