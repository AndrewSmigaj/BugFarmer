package entities

import (
	"math"
	"math/rand"
)

// SwarmState tracks a group of bugs moving together.
// Server manages position/count, client renders individual flies with Brownian motion.
type SwarmState struct {
	ID        string
	SpeciesID string
	Position  EntityPosition
	Radius    float32   // Visual spread radius in blocks
	Count     int       // Number of bugs in swarm
	Facing    Direction // Movement direction hint for client
	Velocity  Vec2      // Current movement
	HomePos   EntityPosition
	WanderRad float32 // Max distance from home

	ReproduceCooldown float32 // Seconds until can reproduce

	// Condition meter (for subduing mechanics, 0-100 range)
	ConditionValue float32
	CurrentHP      int
}

// CanReproduce returns true if reproduction cooldown has elapsed
func (s *SwarmState) CanReproduce() bool {
	return s.ReproduceCooldown <= 0
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

// UpdateWander applies Brownian motion movement to the swarm
func (s *SwarmState) UpdateWander(deltaTime float32, species *BugSpecies, chunkSize int) {
	// 30% chance per tick to change direction (Brownian motion)
	if rand.Float32() < 0.3 {
		angle := rand.Float32() * 2 * math.Pi
		s.Velocity = Vec2{
			X: float32(math.Cos(float64(angle))) * species.BaseSpeed,
			Y: float32(math.Sin(float64(angle))) * species.BaseSpeed,
		}
	}

	// Apply velocity
	s.Position.LocalX += s.Velocity.X * deltaTime
	s.Position.LocalY += s.Velocity.Y * deltaTime
	s.Position.Normalize(chunkSize)

	// Check distance from home, bias back if too far
	homeWorldX := float32(s.HomePos.ChunkX*chunkSize) + s.HomePos.LocalX
	homeWorldY := float32(s.HomePos.ChunkY*chunkSize) + s.HomePos.LocalY
	currWorldX := s.WorldX(chunkSize)
	currWorldY := s.WorldY(chunkSize)

	dx, dy := currWorldX-homeWorldX, currWorldY-homeWorldY
	dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

	if dist > s.WanderRad {
		s.Velocity = Vec2{X: -dx / dist * species.BaseSpeed, Y: -dy / dist * species.BaseSpeed}
	}

	s.Facing = VelocityToDirection(s.Velocity)
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
