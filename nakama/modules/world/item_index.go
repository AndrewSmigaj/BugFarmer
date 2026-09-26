package world

import (
	"fmt"
	"math"

	"bugfarmer/entities"
)

// item_index.go — a chunk-bucketed index OVER state.GroundItems so FindNearbyFood can scan only the
// chunks near a swarm instead of the whole zone's item map (the old O(items) per-think scan).
//
// ItemsByChunk is a PURE DERIVED VIEW of GroundItems: chunkKey -> itemID -> *GroundItem. It is
// maintained INCREMENTALLY (not rebuilt per tick) because feeding deletes items and deaths spawn
// carcasses MID swarm-loop — i.e. GroundItems mutates between two swarms' food queries within one
// tick — so a once-per-tick snapshot would go stale and the result would NOT match the live scan.
// Every ground-item add MUST go through putGroundItem and every delete through deleteGroundItem, or
// the index drifts. AssertItemIndexConsistent (exercised by the determinism harness / tests) is the
// backstop that proves no mutation site was missed.

// floorDivF returns floor(v / cs) as an int for a FLOAT world coordinate — the chunk index it falls in.
// Used by BOTH the bucket key (itemChunkKey) and the FindNearbyFood scan so the two agree exactly,
// including for negative coordinates (math.Floor, not integer truncation). (Distinct from the integer
// floorDiv in state.go.)
func floorDivF(v float32, cs int) int {
	return int(math.Floor(float64(v) / float64(cs)))
}

// itemChunkKey is the bucket key for a ground item, computed from its WORLD position with the same
// floorDiv used by the scan — so an item is always found in the chunk the scan looks for it in, even
// if LocalX/Y are not normalized into [0, ChunkSize).
func (s *WorldState) itemChunkKey(item *entities.GroundItem) string {
	cs := s.Config.ChunkSize
	ix := float32(item.Position.ChunkX*cs) + item.Position.LocalX
	iy := float32(item.Position.ChunkY*cs) + item.Position.LocalY
	return ChunkKey(floorDivF(ix, cs), floorDivF(iy, cs))
}

// putGroundItem inserts/updates a ground item in BOTH the flat map and the chunk index. Overwrite-safe
// (re-adding an existing id first unindexes the old entry). ALL ground-item adds must call this.
func (s *WorldState) putGroundItem(item *entities.GroundItem) {
	if s.ItemsByChunk == nil { // defend any construction/deserialization path that didn't init it
		s.ItemsByChunk = make(map[string]map[string]*entities.GroundItem)
	}
	if old, ok := s.GroundItems[item.ID]; ok {
		s.unindexGroundItem(old)
	}
	s.GroundItems[item.ID] = item
	k := s.itemChunkKey(item)
	bucket := s.ItemsByChunk[k]
	if bucket == nil {
		bucket = make(map[string]*entities.GroundItem)
		s.ItemsByChunk[k] = bucket
	}
	bucket[item.ID] = item
}

// deleteGroundItem removes a ground item from BOTH the flat map and the chunk index. ALL ground-item
// deletes must call this. No-op if the id is absent.
func (s *WorldState) deleteGroundItem(id string) {
	if old, ok := s.GroundItems[id]; ok {
		s.unindexGroundItem(old)
		delete(s.GroundItems, id)
	}
}

// unindexGroundItem removes an item from its chunk bucket (Position is immutable after creation, so the
// key matches the one used when it was added). Drops empty buckets to keep the index compact.
func (s *WorldState) unindexGroundItem(item *entities.GroundItem) {
	k := s.itemChunkKey(item)
	if bucket := s.ItemsByChunk[k]; bucket != nil {
		delete(bucket, item.ID)
		if len(bucket) == 0 {
			delete(s.ItemsByChunk, k)
		}
	}
}

// RebuildItemIndex reconstructs ItemsByChunk from GroundItems. Safe to call any time; used as the
// reference inside AssertItemIndexConsistent and available for any future bulk-load path.
func (s *WorldState) RebuildItemIndex() {
	s.ItemsByChunk = make(map[string]map[string]*entities.GroundItem)
	for _, item := range s.GroundItems {
		k := s.itemChunkKey(item)
		bucket := s.ItemsByChunk[k]
		if bucket == nil {
			bucket = make(map[string]*entities.GroundItem)
			s.ItemsByChunk[k] = bucket
		}
		bucket[item.ID] = item
	}
}

// AssertItemIndexConsistent returns an error unless ItemsByChunk EXACTLY mirrors GroundItems — every
// item present in its correct bucket and no stale/extra entries. The funnel-completeness backstop:
// call it after ticks in tests/harness; a missed mutation site makes it fail loudly.
func (s *WorldState) AssertItemIndexConsistent() error {
	for id, item := range s.GroundItems {
		k := s.itemChunkKey(item)
		bucket := s.ItemsByChunk[k]
		if bucket == nil || bucket[id] != item {
			return fmt.Errorf("ground item %s (bucket %s) missing/mismatched in ItemsByChunk", id, k)
		}
	}
	indexed := 0
	for k, bucket := range s.ItemsByChunk {
		for id, item := range bucket {
			if s.GroundItems[id] != item {
				return fmt.Errorf("stale/extra index entry %s in bucket %s", id, k)
			}
			indexed++
		}
	}
	if indexed != len(s.GroundItems) {
		return fmt.Errorf("index entry count %d != GroundItems count %d", indexed, len(s.GroundItems))
	}
	return nil
}
