package entities

import "math"

// Vec2 represents a 2D float vector (for velocity, position offsets)
type Vec2 struct {
	X, Y float32
}

// Add returns the sum of two vectors
func (v Vec2) Add(other Vec2) Vec2 {
	return Vec2{v.X + other.X, v.Y + other.Y}
}

// Sub returns the difference of two vectors
func (v Vec2) Sub(other Vec2) Vec2 {
	return Vec2{v.X - other.X, v.Y - other.Y}
}

// Scale returns the vector multiplied by a scalar
func (v Vec2) Scale(s float32) Vec2 {
	return Vec2{v.X * s, v.Y * s}
}

// Magnitude returns the length of the vector
func (v Vec2) Magnitude() float32 {
	return float32(math.Sqrt(float64(v.X*v.X + v.Y*v.Y)))
}

// Normalized returns a unit vector in the same direction
func (v Vec2) Normalized() Vec2 {
	mag := v.Magnitude()
	if mag == 0 {
		return Vec2{0, 0}
	}
	return Vec2{v.X / mag, v.Y / mag}
}

// DistanceTo returns the distance between two vectors
func (v Vec2) DistanceTo(other Vec2) float32 {
	dx, dy := v.X-other.X, v.Y-other.Y
	return float32(math.Sqrt(float64(dx*dx + dy*dy)))
}

// Vec2Int represents a 2D integer vector (for grid cells)
type Vec2Int struct {
	X, Y int
}

// CircleOverlapArea returns the area of intersection between two circles.
// r1, r2 are radii; dist is the distance between circle centers.
func CircleOverlapArea(r1, r2, dist float32) float32 {
	// No overlap
	if dist >= r1+r2 {
		return 0
	}

	// One circle contains the other - intersection is smaller circle
	diff := float32(math.Abs(float64(r1 - r2)))
	if dist <= diff {
		smaller := r1
		if r2 < r1 {
			smaller = r2
		}
		return float32(math.Pi) * smaller * smaller
	}

	// Partial overlap - use lens area formula
	d := float64(dist)
	R := float64(r1)
	r := float64(r2)

	// Lens area calculation (intersection of two circles)
	part1 := r * r * math.Acos((d*d+r*r-R*R)/(2*d*r))
	part2 := R * R * math.Acos((d*d+R*R-r*r)/(2*d*R))
	part3 := 0.5 * math.Sqrt((-d+r+R)*(d+r-R)*(d-r+R)*(d+r+R))
	return float32(part1 + part2 - part3)
}

// SwarmCatchRatio returns the fraction of swarm that overlaps with catch circle.
// catchRadius: radius of the catching tool (net)
// swarmRadius: radius of the swarm
// dist: distance between click position and swarm center
func SwarmCatchRatio(catchRadius, swarmRadius, dist float32) float32 {
	overlapArea := CircleOverlapArea(catchRadius, swarmRadius, dist)
	swarmArea := float32(math.Pi) * swarmRadius * swarmRadius
	if swarmArea == 0 {
		return 0
	}
	ratio := overlapArea / swarmArea
	if ratio > 1 {
		ratio = 1 // Clamp to 1 (shouldn't happen but safety)
	}
	return ratio
}
