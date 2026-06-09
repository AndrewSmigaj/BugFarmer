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

// FoodHit is a food/breeding source within vision range. Unifies three backings:
//   - "item":     a ground item with FoodValue > 0 (rotten fruit) — DEPLETABLE
//   - "station":  a player-filled station with Fill > 0 (compost bin) — DEPLETABLE
//   - "occupant": a flora occupant (flowers, milkweed) — NON-depletable (feeding flavor only;
//     v1 rule: REPRODUCTION requires a depletable source, else growth would be unbounded)
type FoodHit struct {
	ID         string  // Ground-item id / StationKey / occupant id
	Kind       string  // "item" | "station" | "occupant"
	X, Y       float32 // World position
	Dist       float32
	Depletable bool
}

// FindNearbyFood searches for food/breeding sources within visionRange matching the species'
// interest list (attractions_by_phase entries). Matching rules:
//   - "rotten_fruit" is a WILDCARD: any ground item that has finished rotting (FoodValue > 0)
//   - a station entity id (e.g. "compost_bin") matches stations of that type with Fill > 0
//   - any other id matches occupants (flowers, milkweed) — the existing behavior
// Deterministic order: sorted by distance, ties broken by ID.
func FindNearbyFood(state *WorldState, pos entities.EntityPosition, visionRange float32, targetIDs []string) []FoodHit {
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

	var hits []FoodHit

	// 1) Ground items (rotten fruit): the "rotten_fruit" wildcard or an exact item type.
	wantRotten := targetSet["rotten_fruit"]
	for id, item := range state.GroundItems {
		if item.FoodValue <= 0 {
			continue
		}
		if !wantRotten && !targetSet[item.ItemType] {
			continue
		}
		ix := float32(item.Position.ChunkX*chunkSize) + item.Position.LocalX
		iy := float32(item.Position.ChunkY*chunkSize) + item.Position.LocalY
		dx, dy := ix-worldX, iy-worldY
		dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
		if dist <= visionRange {
			hits = append(hits, FoodHit{ID: id, Kind: "item", X: ix, Y: iy, Dist: dist, Depletable: true})
		}
	}

	// 2) Stations with fill (compost bin etc.)
	for key, st := range state.Stations {
		if st.Fill <= 0 || !targetSet[st.EntityID] {
			continue
		}
		sx := float32(st.GridX) + 0.5
		sy := float32(st.GridY) + 0.5
		dx, dy := sx-worldX, sy-worldY
		dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
		if dist <= visionRange {
			hits = append(hits, FoodHit{ID: key, Kind: "station", X: sx, Y: sy, Dist: dist, Depletable: true})
		}
	}

	// 3) Flora occupants (existing attraction behavior) — non-depletable.
	for _, r := range FindNearbyResources(state, pos, visionRange, targetIDs) {
		hits = append(hits, FoodHit{ID: r.ID, Kind: "occupant", X: r.X, Y: r.Y, Dist: r.Dist, Depletable: false})
	}

	sort.Slice(hits, func(i, j int) bool {
		if hits[i].Dist != hits[j].Dist {
			return hits[i].Dist < hits[j].Dist
		}
		return hits[i].ID < hits[j].ID
	})
	return hits
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
