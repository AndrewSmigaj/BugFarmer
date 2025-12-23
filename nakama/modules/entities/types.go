package entities

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

// TileX returns the integer tile X coordinate within the chunk.
func (p *EntityPosition) TileX() int {
	return int(p.LocalX)
}

// TileY returns the integer tile Y coordinate within the chunk.
func (p *EntityPosition) TileY() int {
	return int(p.LocalY)
}
