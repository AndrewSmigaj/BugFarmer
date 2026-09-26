package world

import (
	"fmt"
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

	// 1) Ground items (rotten fruit / carrion): scan only the chunk buckets that can hold an item
	//    within visionRange, via the ItemsByChunk index (see item_index.go) — NOT the whole item map.
	//    Result is IDENTICAL to a full scan: the inner dist filter is unchanged, and the scanned chunk
	//    box [worldX±vision, worldY±vision] (PLUS a 1-chunk pad as float-rounding insurance) is a
	//    superset of every chunk a within-vision item can fall in.
	wantRotten := targetSet["rotten_fruit"]
	minCX := floorDivF(worldX-visionRange, chunkSize) - 1
	maxCX := floorDivF(worldX+visionRange, chunkSize) + 1
	minCY := floorDivF(worldY-visionRange, chunkSize) - 1
	maxCY := floorDivF(worldY+visionRange, chunkSize) + 1
	for cy := minCY; cy <= maxCY; cy++ {
		for cx := minCX; cx <= maxCX; cx++ {
			bucket := state.ItemsByChunk[ChunkKey(cx, cy)]
			if bucket == nil {
				continue
			}
			for id, item := range bucket {
				if item.FoodValue <= 0 {
					continue
				}
				// The "rotten_fruit" wildcard matches any rotted food EXCEPT bug carcasses (carrion is
				// detritivore food — flies don't breed on their own dead). Carrion matches only a species
				// that lists the exact dead_<species> id (e.g. the millipede).
				if !targetSet[item.ItemType] && (!wantRotten || item.IsCarrion) {
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

	// 3) Flora occupants. Most are infinite nectar (non-depletable). HOST PLANTS (milkweed) are a
	//    DEPLETABLE breeding source while they have capacity — and are SKIPPED when grazed out, so a
	//    reproducing butterfly stops breeding there until it regrows.
	for _, r := range FindNearbyResources(state, pos, visionRange, targetIDs) {
		cellKey := fmt.Sprintf("%d,%d", int(r.X), int(r.Y))
		depletable := false
		if hp := state.HostPlantStates[cellKey]; hp != nil { // milkweed breeding capacity
			if hp.Capacity <= 0 {
				continue
			}
			depletable = true
		} else if fp := state.ForagePools[cellKey]; fp != nil { // flower nectar (feeding) — depletes + regrows
			if fp.Nectar <= 0 {
				continue // grazed out: not a food source until it regrows → over-large pop starves
			}
			depletable = true
		}
		hits = append(hits, FoodHit{ID: r.ID, Kind: "occupant", X: r.X, Y: r.Y, Dist: r.Dist, Depletable: depletable})
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

			// Iterate the chunk's cached ANCHOR index instead of all 32x32 cells (each of which would be a
			// json.Unmarshal). Same (ly,lx) order + same dist test as the old cell scan → identical result,
			// and species whose targets are never occupants (carrion/rotten-fruit eaters) just skip-filter
			// a handful of anchors instead of parsing 1024 cells.
			chunk.ensureAnchors()
			for _, a := range chunk.anchors {
				if !targetSet[a.id] {
					continue
				}
				occX := float32(cx*chunkSize + a.lx)
				occY := float32(cy*chunkSize + a.ly)
				dx, dy := occX-worldX, occY-worldY
				dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

				if dist <= visionRange {
					hits = append(hits, ResourceHit{ID: a.id, X: occX, Y: occY, Dist: dist})
				}
			}
		}
	}

	// Sort by distance (closest first)
	sort.Slice(hits, func(i, j int) bool { return hits[i].Dist < hits[j].Dist })
	return hits
}
