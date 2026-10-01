package world

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/heroiclabs/nakama-common/runtime"
)

// memStorage (storage_fake_test.go) is the faithful stand-in for Nakama storage these tests use.

func TestUpgradeSaveJSON(t *testing.T) {
	steps := map[int]saveStep{
		1: func(doc map[string]json.RawMessage) error { // v1 -> v2: field "a" renamed "b"
			doc["b"] = doc["a"]
			delete(doc, "a")
			return nil
		},
		2: func(doc map[string]json.RawMessage) error { // v2 -> v3: "b" doubled
			var n int
			if err := json.Unmarshal(doc["b"], &n); err != nil {
				return err
			}
			doc["b"], _ = json.Marshal(n * 2)
			return nil
		},
	}

	raw := []byte(`{"version":3,"b":4}`)
	out, stored, err := upgradeSaveJSON(raw, 3, steps)
	if err != nil || stored != 3 || string(out) != string(raw) {
		t.Fatalf("a current-format save must come back byte-identical: %s, stored %d, err %v", out, stored, err)
	}

	out, stored, err = upgradeSaveJSON([]byte(`{"version":1,"a":2,"keep":"x"}`), 3, steps)
	if err != nil || stored != 1 {
		t.Fatalf("upgrading 1 -> 3: stored %d, err %v", stored, err)
	}
	var got map[string]interface{}
	if err := json.Unmarshal(out, &got); err != nil {
		t.Fatal(err)
	}
	if got["version"] != 3.0 || got["b"] != 4.0 || got["keep"] != "x" || got["a"] != nil {
		t.Errorf("every step must run once, in order, leaving other fields alone: got %v", got)
	}

	if _, stored, err := upgradeSaveJSON([]byte(`{"version":4}`), 3, steps); !errors.Is(err, errSaveFromNewerBuild) || stored != 4 {
		t.Errorf("a save from a newer build must be refused: stored %d, err %v", stored, err)
	}
	if _, _, err := upgradeSaveJSON([]byte(`{"version":1,"a":2}`), 3, map[int]saveStep{1: steps[1]}); !errors.Is(err, errSaveNoUpgradeStep) {
		t.Errorf("a gap in the upgrade chain must be refused, never guessed: %v", err)
	}
	for _, bad := range []string{`not json`, `{"tick":5}`, `{"version":0}`} {
		if _, _, err := upgradeSaveJSON([]byte(bad), 3, steps); !errors.Is(err, errSaveUnreadable) {
			t.Errorf("%s must be unreadable, got %v", bad, err)
		}
	}
	if _, _, err := upgradeSaveJSON([]byte(`{"version":2,"b":"not a number"}`), 3, steps); err == nil || !strings.Contains(err.Error(), "2 -> 3") {
		t.Errorf("a failing step must say which step failed: %v", err)
	}
}

const saveTestZone = "savetest" // no data/zones/savetest in the test's working dir → a placeholder zone

func startZone(nk runtime.NakamaModule) interface{} {
	state, _, _ := (&Match{}).MatchInit(context.Background(), nopRuntimeLogger(), nil, nk, map[string]interface{}{
		"world_id": "w", "owner_id": "o", "zone_id": saveTestZone,
	})
	return state
}

// A zone must never start over a save it can't use: the old code started it empty and the next autosave
// wrote over the player's world.
func TestMatchInitNeverStartsOverAnUnusableSave(t *testing.T) {
	key := memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(saveTestZone, "")))
	for name, doc := range map[string]string{
		"written by a newer build": `{"version":99,"zone_id":"savetest","tick":500}`,
		"unreadable":               `{"version":1,"zone_id":"savetest","tick":"five hundred"}`,
	} {
		nk := newMemStorage()
		nk.objs[key] = doc
		if state := startZone(nk); state != nil {
			t.Errorf("%s: the zone started over a save it can't use", name)
		}
		if nk.objs[key] != doc || len(nk.objs) != 1 {
			t.Errorf("%s: storage was changed: %v", name, nk.objs)
		}
	}
}

func TestMatchInitUpgradesAnOlderSaveAndKeepsTheOriginal(t *testing.T) {
	was, wasSteps := worldSaveVersion, worldSaveSteps
	defer func() { worldSaveVersion, worldSaveSteps = was, wasSteps }()
	worldSaveVersion = was + 1
	worldSaveSteps = map[int]saveStep{was: func(doc map[string]json.RawMessage) error {
		doc["ground_item_seq"] = json.RawMessage("777") // the upgrade's visible effect
		return nil
	}}

	nk := newMemStorage()
	zoneKey := ZoneStateKey(saveTestZone, "")
	saveKey := memKey(ZoneStateCollection, "", worldSaveKey(zoneKey))
	backupKey := memKey(ZoneStateCollection, "", worldSaveBackupKey(zoneKey, was))
	original := fmt.Sprintf(`{"version":%d,"zone_id":"savetest","tick":500,"swarms":[]}`, was)
	nk.objs[saveKey] = original

	ws, ok := startZone(nk).(*WorldState)
	if !ok {
		t.Fatal("the zone didn't start from an older save it can upgrade")
	}
	if ws.TickCount != 500 || ws.GroundItemSeq != 777 {
		t.Errorf("the upgraded save wasn't restored: tick %d (want 500), ground_item_seq %d (want 777)", ws.TickCount, ws.GroundItemSeq)
	}
	if nk.objs[backupKey] != original {
		t.Errorf("the original must be kept untouched before the upgrade: backup = %q", nk.objs[backupKey])
	}
	if nk.objs[saveKey] != original {
		t.Errorf("starting the zone must not rewrite the save itself (the autosave does that later)")
	}

	// A second start before the next autosave (e.g. after a crash) keeps the FIRST backup.
	nk.objs[saveKey] = fmt.Sprintf(`{"version":%d,"zone_id":"savetest","tick":600,"swarms":[]}`, was)
	if startZone(nk) == nil {
		t.Fatal("second start failed")
	}
	if nk.objs[backupKey] != original {
		t.Errorf("a later start replaced the original backup")
	}
}

func TestWorldSaveWriteNeverOverwritesAnUnusableSave(t *testing.T) {
	nk := newMemStorage()
	key := memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(saveTestZone, "")))
	newer := `{"version":99,"zone_id":"savetest","tick":500}`
	nk.objs[key] = newer
	writeWorldSave(context.Background(), nk, nopRuntimeLogger(), saveTestZone, `{"version":1,"zone_id":"savetest","tick":900}`, 900)
	if nk.objs[key] != newer {
		t.Errorf("an autosave overwrote a save written by a newer build")
	}

	nk.objs[key] = `{"version":1,"zone_id":"savetest","tick":100}`
	fresh := `{"version":1,"zone_id":"savetest","tick":900}`
	writeWorldSave(context.Background(), nk, nopRuntimeLogger(), saveTestZone, fresh, 900)
	if nk.objs[key] != fresh {
		t.Errorf("a normal autosave over an older tick must still be written")
	}
}

func TestCharacterSaveVersions(t *testing.T) {
	ctx := context.Background()
	nk := newMemStorage()
	current := fmt.Sprintf(`{"version":%d,"char_id":"c1","name":"Ada","coins":5}`, characterSaveVersion)
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = current
	nk.objs[memKey(CharacterCollection, "u1", "c2")] = `{"version":99,"char_id":"c2","name":"Future"}`

	if save, err := LoadCharacterSave(ctx, nk, "u1", "c1"); err != nil || save == nil || save.Name != "Ada" || save.Coins != 5 {
		t.Fatalf("a current character must load as-is: %+v, %v", save, err)
	}
	if save, err := LoadCharacterSave(ctx, nk, "u1", "c2"); !errors.Is(err, errSaveFromNewerBuild) || save != nil {
		t.Errorf("a character from a newer build must be refused (never loaded as empty): %+v, %v", save, err)
	}
	list, err := ListCharacterSummaries(ctx, nk, "u1")
	if err != nil || len(list) != 1 || list[0].CharID != "c1" {
		t.Errorf("the select screen must list only characters this build can use: %+v, %v", list, err)
	}

	was, wasSteps := characterSaveVersion, characterSaveSteps
	defer func() { characterSaveVersion, characterSaveSteps = was, wasSteps }()
	characterSaveVersion = was + 1
	characterSaveSteps = map[int]saveStep{was: func(doc map[string]json.RawMessage) error {
		doc["coins"] = json.RawMessage("50")
		return nil
	}}
	save, err := LoadCharacterSave(ctx, nk, "u1", "c1")
	if err != nil || save == nil || save.Coins != 50 {
		t.Fatalf("an older character must be upgraded: %+v, %v", save, err)
	}
	if got := nk.objs[memKey(CharacterBackupCollection, "u1", fmt.Sprintf("c1:v%d", was))]; got != current {
		t.Errorf("the original character must be kept untouched before the upgrade: %q", got)
	}
	if err := WriteCharacterSave(ctx, nk, "u1", save); err != nil {
		t.Fatal(err)
	}
	var written struct{ Version int }
	_ = json.Unmarshal([]byte(nk.objs[memKey(CharacterCollection, "u1", "c1")]), &written)
	if written.Version != characterSaveVersion {
		t.Errorf("a written character must carry this build's format: %d", written.Version)
	}
}
