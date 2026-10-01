package world

// The clean-stop save (MatchTerminate → finalSave, D73): the zone's world document and the character of everyone
// still in it go to the save queue as ONE batch, and MatchTerminate waits for it to be written before returning nil.

import (
	"context"
	"encoding/json"
	"strings"
	"testing"
	"time"
)

// runningSaves is a save system whose queue runs (as on the server) until the test ends.
func runningSaves(t *testing.T, nk *memStorage) *saveSystem {
	t.Helper()
	sys := newSaveSystem(nk, nopRuntimeLogger())
	ctx, cancel := context.WithCancel(context.Background())
	t.Cleanup(cancel)
	go sys.writer.run(ctx)
	return sys
}

func terminateZone(t *testing.T, m *Match, nk *memStorage, ws *WorldState, grace int) {
	t.Helper()
	if got := m.MatchTerminate(context.Background(), nopRuntimeLogger(), nil, nk, nopDispatcher{}, 0, ws, grace); got != nil {
		t.Fatalf("MatchTerminate must return nil (stop at once) — a live state keeps the match running unsaved through the grace period")
	}
}

func TestFinalSaveWritesWorldAndCharactersTogether(t *testing.T) {
	nk := newMemStorage()
	m := &Match{sys: runningSaves(t, nk)}
	ws, ok := startZoneWith(m, nk).(*WorldState)
	if !ok {
		t.Fatal("zone didn't start")
	}
	ws.TickCount = 4321
	ws.Players["u1"] = &PlayerState{UserID: "u1", CharacterID: "c1", Coins: 42}
	ws.Players["u2"] = &PlayerState{UserID: "u2"} // joined without a character: nothing to keep
	nk.mu.Lock()
	nk.writeCalls = 0
	nk.mu.Unlock()

	terminateZone(t, m, nk, ws, 15) // returns only once the final save is written

	nk.mu.Lock()
	defer nk.mu.Unlock()
	if nk.writeCalls != 1 {
		t.Fatalf("the world and the characters must be written in ONE storage write, got %d writes", nk.writeCalls)
	}
	var world WorldSave
	if err := json.Unmarshal([]byte(nk.objs[memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(saveTestZone, "")))]), &world); err != nil || world.Tick != 4321 {
		t.Fatalf("the world document wasn't saved at the zone's tick: tick %d, err %v", world.Tick, err)
	}
	var char CharacterSave
	if err := json.Unmarshal([]byte(nk.objs[memKey(CharacterCollection, "u1", "c1")]), &char); err != nil || char.Coins != 42 || char.LastZone != saveTestZone {
		t.Fatalf("the present character wasn't saved with the world: %+v, err %v", char, err)
	}
	for k := range nk.objs {
		if strings.HasPrefix(k, CharacterCollection+"|u2|") {
			t.Errorf("a player without a character must not be written: %s", k)
		}
	}
}

func TestFinalSaveNeverWritesOverAChangedSave(t *testing.T) {
	nk := newMemStorage()
	sys := runningSaves(t, nk)
	m := &Match{sys: sys}
	ws, ok := startZoneWith(m, nk).(*WorldState)
	if !ok {
		t.Fatal("zone didn't start")
	}
	ws.Players["u1"] = &PlayerState{UserID: "u1", CharacterID: "c1", Coins: 42}
	// Something other than this server wrote the zone's save while it ran (the zone started with none): writing on
	// would mix two histories, so the queue must refuse and stop saving — and write nothing.
	key := memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(saveTestZone, "")))
	nk.mu.Lock()
	nk.objs[key] = `{"version":1,"zone_id":"savetest","tick":500}`
	nk.mu.Unlock()

	start := time.Now()
	terminateZone(t, m, nk, ws, 2) // gives up after the grace period less a second
	if time.Since(start) > 3*time.Second {
		t.Errorf("MatchTerminate must give up within the grace period")
	}
	if sys.writer.Halted() == "" {
		t.Errorf("a save changed by something else must stop saving")
	}
	nk.mu.Lock()
	defer nk.mu.Unlock()
	if nk.objs[key] != `{"version":1,"zone_id":"savetest","tick":500}` {
		t.Errorf("the changed save was written over")
	}
	if _, wrote := nk.objs[memKey(CharacterCollection, "u1", "c1")]; wrote {
		t.Errorf("the character was written without its world")
	}
}

func TestTerminateSaveTimeoutLeavesAMargin(t *testing.T) {
	for grace, want := range map[int]int{0: 1, 1: 1, 2: 1, 15: 14} {
		if got := terminateSaveTimeout(grace); int(got.Seconds()) != want {
			t.Errorf("grace %ds: save timeout %v, want %ds", grace, got, want)
		}
	}
}
