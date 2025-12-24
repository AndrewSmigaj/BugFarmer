package entities

// Direction represents the 4 cardinal directions for top-down view.
// Shared by all entities (players, bugs, etc.)
type Direction int

const (
	DirDown  Direction = iota // 0 - default, facing camera
	DirLeft                   // 1
	DirRight                  // 2
	DirUp                     // 3
)

// EntityPosition represents chunk-relative coordinates for entities.
type EntityPosition struct {
	ChunkX int
	ChunkY int
	LocalX float32
	LocalY float32
}

// Entity interface for all game entities.
type Entity interface {
	GetID() string
	GetPosition() EntityPosition
	GetType() string
}

// Normalize adjusts position if outside chunk bounds.
// chunkSize is passed from world config.
func (p *EntityPosition) Normalize(chunkSize int) {
	cs := float32(chunkSize)
	for p.LocalX >= cs {
		p.ChunkX++
		p.LocalX -= cs
	}
	for p.LocalX < 0 {
		p.ChunkX--
		p.LocalX += cs
	}
	for p.LocalY >= cs {
		p.ChunkY++
		p.LocalY -= cs
	}
	for p.LocalY < 0 {
		p.ChunkY--
		p.LocalY += cs
	}
}

// BlockX returns the integer block X coordinate within the chunk.
func (p *EntityPosition) BlockX() int {
	return int(p.LocalX)
}

// BlockY returns the integer block Y coordinate within the chunk.
func (p *EntityPosition) BlockY() int {
	return int(p.LocalY)
}
