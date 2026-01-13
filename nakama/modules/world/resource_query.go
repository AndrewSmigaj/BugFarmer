package world

import (
	"math"
	"sort"

	"bugfarmer/entities"
)

// ResourceHit represents a found resource within vision range
type ResourceHit struct {
	ID   string  // Occupant ID (e.g., "flower_wild", "compost_pile")
	X    float32 // World X coordinate
	Y    float32 // World Y coordinate
	Dist float32 // Distance from query position
}

// FindNearbyResources searches for occupants matching targetIDs within visionRange of the given position.
// Returns hits sorted by distance (closest first).
func FindNearbyResources(state *WorldState, pos entities.EntityPosition, visionRange float32, targetIDs []string) []ResourceHit {
	if len(targetIDs) == 0 {
		return nil
	}

	targetSet := make(map[string]bool, len(targetIDs))
	for _, id := range targetIDs {
		targetSet[id] = true
	}

	chunkSize := state.Config.ChunkSize
	worldX := float32(pos.ChunkX*chunkSize) + pos.LocalX
	worldY := float32(pos.ChunkY*chunkSize) + pos.LocalY

	chunksToSearch := int(math.Ceil(float64(visionRange) / float64(chunkSize)))

	var hits []ResourceHit

	for cy := pos.ChunkY - chunksToSearch; cy <= pos.ChunkY+chunksToSearch; cy++ {
		for cx := pos.ChunkX - chunksToSearch; cx <= pos.ChunkX+chunksToSearch; cx++ {
			chunk := state.Chunks[ChunkKey(cx, cy)]
			if chunk == nil {
				continue
			}

			for ly := 0; ly < ChunkSize; ly++ {
				for lx := 0; lx < ChunkSize; lx++ {
					cell, err := chunk.GetOccupantCell(lx, ly)
					if err != nil || cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
						continue
					}

					if !targetSet[cell.Occupant.ID] {
						continue
					}

					occX := float32(cx*chunkSize + lx)
					occY := float32(cy*chunkSize + ly)
					dx, dy := occX-worldX, occY-worldY
					dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

					if dist <= visionRange {
						hits = append(hits, ResourceHit{ID: cell.Occupant.ID, X: occX, Y: occY, Dist: dist})
					}
				}
			}
		}
	}

	// Sort by distance (closest first)
	sort.Slice(hits, func(i, j int) bool { return hits[i].Dist < hits[j].Dist })
	return hits
}
