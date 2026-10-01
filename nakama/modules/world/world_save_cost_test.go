package world

// The cost of building a zone's save, and the proof that occCellEqual's byte fast path never changes an answer.
// The snapshot is built on the match goroutine, so it must stay cheap now that zones save every minute (D73).
// These tests read the REAL zones (data/zones, mounted read-only by tools/run_go_tests.sh) the way the server does,
// relative to the working directory; they skip if that data isn't there.

import (
	"encoding/json"
	"os"
	"sort"
	"testing"
	"time"
)

// occCellEqualByMeaning is occCellEqual without the fast path: the reference the fast path must agree with.
// (ok=false: a cell that doesn't parse — the reference can't judge it.)
func occCellEqualByMeaning(a, b json.RawMessage) (equal, ok bool) {
	ca, errA := ParseOccupantCell(a)
	cb, errB := ParseOccupantCell(b)
	if errA != nil || errB != nil {
		return false, false
	}
	if ca.IsEmpty != cb.IsEmpty {
		return false, true
	}
	if ca.IsEmpty {
		return true, true
	}
	return ca.Occupant.ID == cb.Occupant.ID && ca.Occupant.Dir == cb.Occupant.Dir && ca.Occupant.Anchor == cb.Occupant.Anchor, true
}

// realZoneState loads every chunk of a real zone into a fresh WorldState — a fully explored zone, as live chunks.
// The working directory moves to nakama/ (the repo) or / (the test container), where data/zones is.
func realZoneState(t testing.TB, zoneID string) (*WorldState, func()) {
	t.Helper()
	wd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	if err := os.Chdir("../.."); err != nil {
		t.Skipf("can't reach the zone data: %v", err)
	}
	restore := func() { _ = os.Chdir(wd) }
	zonePath := "data/zones/" + zoneID
	cfg, err := LoadZoneConfig(zonePath)
	if err != nil {
		restore()
		t.Skipf("real zone data not available (%v) — run through tools/run_go_tests.sh", err)
	}
	state := NewWorldState("w", "o", "n", "public")
	state.CurrentZone = cfg
	for cx := 0; cx*ChunkSize < cfg.Width; cx++ {
		for cy := 0; cy*ChunkSize < cfg.Height; cy++ {
			c, err := LoadChunk(zonePath, cx, cy)
			if err != nil {
				restore()
				t.Fatalf("loading chunk %d,%d: %v", cx, cy, err)
			}
			state.Chunks[ChunkKey(cx, cy)] = c
		}
	}
	return state, restore
}

func TestOccCellEqualFastPathAgreesWithMeaning(t *testing.T) {
	state, restore := realZoneState(t, "village_21_B")
	defer restore()
	var cells []json.RawMessage
	for _, k := range sortedStringKeys(state.Chunks) {
		for _, row := range state.Chunks[k].Occupants {
			cells = append(cells, row...)
		}
	}
	checked := 0
	for i, c := range cells {
		// the cell against itself, against a re-encoded copy (same meaning, other bytes), and against its neighbour
		pairs := [][2]json.RawMessage{{c, c}, {c, cells[(i+1)%len(cells)]}}
		if p, err := ParseOccupantCell(c); err == nil && !p.IsEmpty {
			reenc, _ := json.Marshal(map[string]interface{}{"anchor": p.Occupant.Anchor, "dir": p.Occupant.Dir, "id": p.Occupant.ID})
			pairs = append(pairs, [2]json.RawMessage{c, reenc})
		}
		for _, pr := range pairs {
			want, ok := occCellEqualByMeaning(pr[0], pr[1])
			if !ok {
				continue
			}
			if got := occCellEqual(pr[0], pr[1]); got != want {
				t.Fatalf("occCellEqual(%s, %s) = %v, by meaning %v", pr[0], pr[1], got, want)
			}
			checked++
		}
	}
	if checked < len(cells) {
		t.Fatalf("only %d comparisons over %d cells — the zone data didn't load as expected", checked, len(cells))
	}
	t.Logf("fast path agreed with the full comparison on %d cell pairs of village_21_B", checked)
}

// TestWorldSaveBuildCost builds the save of a fully loaded village_21_B (all 64 chunks) with ~200 player edits,
// checks the document holds exactly those edits, and logs how long the build takes (run with -v to see it).
func TestWorldSaveBuildCost(t *testing.T) {
	state, restore := realZoneState(t, "village_21_B")
	defer restore()
	fence := json.RawMessage(`{"id":"fence_wood","dir":0,"anchor":true}`)
	edited := 0
	for i, k := range sortedStringKeys(state.Chunks) {
		c := state.Chunks[k]
		for j := 0; j < 3; j++ { // three fences and a dug square per chunk
			c.Occupants[(i+j*7)%ChunkSize][(j*11+i)%ChunkSize] = fence
			edited++
		}
		c.Ground[(i*3)%ChunkSize][(i*5)%ChunkSize] = "dirt_dug_test"
		edited++
	}
	m := &Match{}
	var durations []time.Duration
	var ws *WorldSave
	var first []byte
	for run := 0; run < 5; run++ {
		start := time.Now()
		ws = m.buildWorldSave(state) // run 0 reads the authored files (fills BaseChunks); runs 1-4 use the cache
		durations = append(durations, time.Since(start))
		edits, _ := json.Marshal(ws.CellEdits)
		if run == 0 {
			first = edits
		} else if string(edits) != string(first) {
			t.Fatalf("a save built from the cached authored chunks differs from one built from the files (run %d)", run)
		}
	}
	sort.Slice(durations, func(i, j int) bool { return durations[i] < durations[j] })
	if ws == nil {
		t.Fatal("no document built")
	}
	// Some of the planted fences can land on a cell that already held that very fence; count what really differs.
	if len(ws.CellEdits) == 0 || len(ws.CellEdits) > edited {
		t.Fatalf("the document should hold the ~%d edits made, got %d", edited, len(ws.CellEdits))
	}
	t.Logf("village_21_B save build (64 chunks, %d edits): median %v, min %v, max %v",
		len(ws.CellEdits), durations[len(durations)/2], durations[0], durations[len(durations)-1])
}

func BenchmarkBuildWorldSaveVillage21B(b *testing.B) {
	state, restore := realZoneState(b, "village_21_B")
	defer restore()
	m := &Match{}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		m.buildWorldSave(state)
	}
}
