package world

// The clean-stop save (MatchTerminate → writeFinalSave): the zone's world document and the character of everyone
// still in it go to storage in ONE write, so a restart brings them back from the same moment.

import (
	"context"
	"encoding/json"
	"strings"
	"testing"
)

func terminateZone(t *testing.T, nk *memStorage, ws *WorldState) {
	t.Helper()
	if got := (&Match{}).MatchTerminate(context.Background(), nopRuntimeLogger(), nil, nk, nopDispatcher{}, 0, ws, 15); got != nil {
		t.Fatalf("MatchTerminate must return nil (stop at once) — a live state keeps the match running unsaved through the grace period")
	}
}

func TestFinalSaveWritesWorldAndCharactersTogether(t *testing.T) {
	nk := newMemStorage()
	ws, ok := startZone(nk).(*WorldState)
	if !ok {
		t.Fatal("zone didn't start")
	}
	ws.TickCount = 4321
	ws.Players["u1"] = &PlayerState{UserID: "u1", CharacterID: "c1", Coins: 42}
	ws.Players["u2"] = &PlayerState{UserID: "u2"} // joined without a character: nothing to keep
	nk.writeCalls = 0

	terminateZone(t, nk, ws)

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

func TestFinalSaveWritesNothingOverAnUnusableSave(t *testing.T) {
	nk := newMemStorage()
	ws, ok := startZone(nk).(*WorldState)
	if !ok {
		t.Fatal("zone didn't start")
	}
	ws.Players["u1"] = &PlayerState{UserID: "u1", CharacterID: "c1", Coins: 42}
	// Something wrote a save this build can't use while the zone ran: the final save must leave storage as it is —
	// writing the character alone would split it from the world it was played in.
	key := memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(saveTestZone, "")))
	nk.objs[key] = `{"version":99,"zone_id":"savetest","tick":500}`
	nk.writeCalls = 0

	terminateZone(t, nk, ws)

	if nk.writeCalls != 0 {
		t.Errorf("nothing may be written over an unusable save, got %d writes", nk.writeCalls)
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
