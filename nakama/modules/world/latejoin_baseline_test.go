package world

// What a late joiner (or a resyncing client) starts from must describe the snapshot's moment, because it replays every
// later event itself (docs/product/investigations/latejoin-rejoin-divergence.md, 2026-10-06):
//   - the collision map: the current blocks_bugs set with every OCCUPANT_BLOCKS_BUGS change after the snapshot undone
//     (cause B: a fence gnawed through between the snapshot and the join was already open in the joiner's replay);
//   - the player cells: the authority's registry at the snapshot, unfiltered (cause A: a same-account rejoin passed a
//     current-members filter with its OLD cell and replayed a phantom of itself).
//
// Run inside the builder image:  go test ./world/ -run 'TestUndoBlocksBugs|TestLateJoinPlayerCells' -v

import (
	"reflect"
	"testing"
)

func blocksEvent(seq int64, x, y int, blocked bool) InfluenceEvent {
	level := 0
	if blocked {
		level = 1
	}
	return InfluenceEvent{Seq: seq, Tick: seq, Type: InfluenceOccupantBlocksBugs, CellX: x, CellY: y, Level: level}
}

func cellSet(cx, cy []int) map[[2]int]bool {
	s := map[[2]int]bool{}
	for i := range cx {
		s[[2]int{cx[i], cy[i]}] = true
	}
	return s
}

func TestUndoBlocksBugsAfterRestoresAFenceRemovedInTheWindow(t *testing.T) {
	// now: the fence at (75,107) is gone (gnawed at seq 12); the snapshot was taken at seq 10
	cx, cy := []int{10, 20}, []int{5, 6}
	log := []InfluenceEvent{blocksEvent(12, 75, 107, false)}
	gx, gy := undoBlocksBugsAfter(cx, cy, log, 10)
	if got := cellSet(gx, gy); !got[[2]int{75, 107}] || len(got) != 3 {
		t.Fatalf("the fence removed after the snapshot must still block in the joiner's base map; got %v", got)
	}
}

func TestUndoBlocksBugsAfterOpensAFencePlacedInTheWindow(t *testing.T) {
	cx, cy := []int{10, 30}, []int{5, 9} // (30,9) placed at seq 15, after the snapshot at seq 14
	log := []InfluenceEvent{blocksEvent(15, 30, 9, true)}
	gx, gy := undoBlocksBugsAfter(cx, cy, log, 14)
	if got := cellSet(gx, gy); got[[2]int{30, 9}] || len(got) != 1 {
		t.Fatalf("a fence placed after the snapshot must be open in the base map; got %v", got)
	}
}

func TestUndoBlocksBugsAfterLeavesChangesBeforeTheSnapshot(t *testing.T) {
	// a removal at seq 8 is already in the snapshot (cut 10): the current map is the answer, unchanged and in order
	cx, cy := []int{3, 1, 2}, []int{1, 1, 1}
	log := []InfluenceEvent{blocksEvent(8, 75, 107, false), {Seq: 11, Type: InfluencePlayerCellEnter, CellX: 3, CellY: 1}}
	gx, gy := undoBlocksBugsAfter(cx, cy, log, 10)
	if !reflect.DeepEqual(gx, cx) || !reflect.DeepEqual(gy, cy) {
		t.Fatalf("no in-window collision change: the map must come back unchanged; got %v %v", gx, gy)
	}
}

func TestUndoBlocksBugsAfterUndoesInReverseOrder(t *testing.T) {
	// in the window: a fence placed at (4,4) (seq 21) then gnawed (seq 23); another removed (seq 22). At the snapshot
	// (cut 20) (4,4) was open and (6,6) blocked; now (4,4) is open again and (6,6) gone.
	cx, cy := []int{1}, []int{1}
	log := []InfluenceEvent{blocksEvent(21, 4, 4, true), blocksEvent(22, 6, 6, false), blocksEvent(23, 4, 4, false)}
	gx, gy := undoBlocksBugsAfter(cx, cy, log, 20)
	want := map[[2]int]bool{{1, 1}: true, {6, 6}: true}
	if got := cellSet(gx, gy); !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v, want %v", got, want)
	}
	// deterministic order: sorted by y, then x
	if !reflect.DeepEqual(gx, []int{1, 6}) || !reflect.DeepEqual(gy, []int{1, 6}) {
		t.Fatalf("cells must come back sorted by y then x; got %v %v", gx, gy)
	}
}

func TestLateJoinPlayerCellsKeepsTheSnapshotRegistryUnfiltered(t *testing.T) {
	// P2 left after the snapshot and has just rejoined (a member again); P3 left after the snapshot and is gone. The
	// joiner starts from the snapshot registry as it was; both departures replay as PLAYER_CELL_LEAVE.
	snapshot := []PlayerCellData{{PlayerID: "p1", CellX: 126, CellY: 118}, {PlayerID: "p2", CellX: 30, CellY: 140},
		{PlayerID: "p3", CellX: 50, CellY: 50}}
	members := map[string]bool{"p1": true, "p2": true}
	current := map[string]*PlayerCellState{"p1": {126, 118}, "p2": {126, 118}}
	if got := lateJoinPlayerCells(snapshot, members, current); !reflect.DeepEqual(got, snapshot) {
		t.Fatalf("the snapshot's cells must pass through unfiltered; got %v", got)
	}
}

func TestLateJoinPlayerCellsBootstrapUsesCurrentMembersInOrder(t *testing.T) {
	members := map[string]bool{"pb": true, "pa": true, "pc": true}
	current := map[string]*PlayerCellState{"pb": {2, 2}, "pa": {1, 1}} // pc has no cell yet
	want := []PlayerCellData{{PlayerID: "pa", CellX: 1, CellY: 1}, {PlayerID: "pb", CellX: 2, CellY: 2}}
	if got := lateJoinPlayerCells(nil, members, current); !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v, want %v", got, want)
	}
}
