package world

// Restoring a backup (restore.go, D73), on the faithful storage stand-in and a real folder.

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"
)

// backupOf writes a backup of the stand-in's storage now (in dir, as the rolling backups do) and returns its path.
func backupOf(t *testing.T, nk *memStorage, dir string, at time.Time) string {
	t.Helper()
	zones, chars, err := listBackupContent(context.Background(), nk)
	if err != nil {
		t.Fatal(err)
	}
	f, err := newBackupFile("rolling", at, zones, chars)
	if err != nil {
		t.Fatal(err)
	}
	path, err := writeBackupFile(dir, nextBackupName(dir, at), f, readBackupFile)
	if err != nil {
		t.Fatal(err)
	}
	return path
}

// placeForRestore copies a backup into restore/, as the tool does (a fresh copy: a new modification time).
func placeForRestore(t *testing.T, dir, path string) string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	inbox := filepath.Join(dir, "restore")
	if err := os.MkdirAll(inbox, 0o755); err != nil {
		t.Fatal(err)
	}
	placed := filepath.Join(inbox, filepath.Base(path))
	if err := os.WriteFile(placed, data, 0o644); err != nil {
		t.Fatal(err)
	}
	return placed
}

func testRestorer(nk *memStorage, dir string) *restorer {
	return &restorer{nk: nk, logger: nopRuntimeLogger(), dir: dir, now: func() time.Time {
		return time.Date(2026, 10, 1, 9, 0, 0, 0, time.UTC)
	}}
}

func snapshot(nk *memStorage) map[string]string {
	nk.mu.Lock()
	defer nk.mu.Unlock()
	return nk.copyObjs()
}

func filesIn(t *testing.T, dir string) []string {
	t.Helper()
	des, err := os.ReadDir(dir)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		t.Fatal(err)
	}
	var out []string
	for _, de := range des {
		if !de.IsDir() {
			out = append(out, de.Name())
		}
	}
	return out
}

func set(nk *memStorage, collection, user, key, value string) {
	nk.objs[memKey(collection, user, key)] = value
}

func TestRestorePutsTheBackupBackAndRemovesWhatCameAfter(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
	set(nk, ZoneStateCollection, "", "old:meta", `{"version":1,"modified_chunks":["0_0"]}`) // an old-format zone
	set(nk, ZoneStateCollection, "", "old:0_0", `{"cells":[]}`)
	set(nk, ZoneStateCollection, "", "z:world:v7", `{"copy":"before"}`) // a pre-upgrade copy: never touched
	set(nk, CharacterCollection, "u1", "c1", `{"version":1,"char_id":"c1","coins":5}`)
	backup := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))

	// Play after the backup: the zone moves on, a zone and a character are made, the old-format records are cleaned
	// up, a pre-upgrade copy and a character's backup copy appear.
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":9}`)
	set(nk, ZoneStateCollection, "", "y:world", `{"version":1,"zone_id":"y","tick":3}`)
	delete(nk.objs, memKey(ZoneStateCollection, "", "old:0_0"))
	set(nk, ZoneStateCollection, "", "z:world:v7", `{"copy":"after"}`)
	set(nk, CharacterCollection, "u1", "c1", `{"version":1,"char_id":"c1","coins":50}`)
	set(nk, CharacterCollection, "u1", "c2", `{"version":1,"char_id":"c2","coins":1}`)
	set(nk, CharacterBackupCollection, "u1", "c1:v0", `{"char_id":"c1"}`)
	set(nk, worldListCollection, "", "default_z", `{"world_id":"default_z"}`)
	after := snapshot(nk)

	placed := placeForRestore(t, dir, backup)
	res, err := testRestorer(nk, dir).run(context.Background())
	if err != nil {
		t.Fatalf("restore failed: %v", err)
	}
	if nk.multiCalls != 1 {
		t.Errorf("a restore is ONE transaction: %d MultiUpdate calls", nk.multiCalls)
	}
	if storedTick(t, nk, "z") != 1 || storedCoins(t, nk, "u1", "c1") != 5 {
		t.Errorf("the zone and the character must be as in the backup: tick %d, coins %d", storedTick(t, nk, "z"), storedCoins(t, nk, "u1", "c1"))
	}
	for _, k := range []string{memKey(ZoneStateCollection, "", "y:world"), memKey(CharacterCollection, "u1", "c2")} {
		if _, there := nk.objs[k]; there {
			t.Errorf("%s was made after the backup and must be removed", k)
		}
	}
	if nk.objs[memKey(ZoneStateCollection, "", "old:0_0")] != `{"cells":[]}` {
		t.Errorf("the old-format zone's records must come back")
	}
	for _, k := range []string{memKey(ZoneStateCollection, "", "z:world:v7"), memKey(CharacterBackupCollection, "u1", "c1:v0"),
		memKey(worldListCollection, "", "default_z")} {
		if nk.objs[k] != after[k] {
			t.Errorf("%s is not part of a backup and must be left as it is: %q", k, nk.objs[k])
		}
	}
	if res.zones != 3 || res.chars != 1 || res.removedZones != 1 || res.removedChars != 1 {
		t.Errorf("result: %+v", res)
	}
	// The state before is kept, and the file is done.
	pre := readBackup(t, filepath.Join(dir, "pre-restore", res.preRestore))
	if backupTick(t, pre, "z:world") != 9 || backupCoins(t, pre, "u1", "c2") != 1 || pre.Kind != "pre-restore" {
		t.Errorf("the pre-restore backup must hold the state before the restore")
	}
	if _, err := os.Stat(placed); !errors.Is(err, os.ErrNotExist) || len(filesIn(t, filepath.Join(dir, "restore", "done"))) != 1 {
		t.Errorf("an applied file moves to restore/done/")
	}

	// And a restore can be undone: putting back the pre-restore copy brings the later state back.
	placeForRestore(t, dir, filepath.Join(dir, "pre-restore", res.preRestore))
	r2 := testRestorer(nk, dir)
	r2.now = func() time.Time { return time.Date(2026, 10, 1, 9, 5, 0, 0, time.UTC) }
	if _, err := r2.run(context.Background()); err != nil {
		t.Fatal(err)
	}
	if storedTick(t, nk, "z") != 9 || storedCoins(t, nk, "u1", "c2") != 1 || storedCoins(t, nk, "u1", "c1") != 50 {
		t.Errorf("restoring the pre-restore copy must undo the restore")
	}
}

func TestRestoreLeavesOutDeletedAccounts(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, CharacterCollection, "u1", "c1", `{"version":1,"char_id":"c1","coins":5}`)
	set(nk, CharacterCollection, "gone", "c9", `{"version":1,"char_id":"c9","coins":9}`)
	backup := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
	nk.users = map[string]bool{"u1": true} // the account "gone" was deleted since (its characters with it)
	delete(nk.objs, memKey(CharacterCollection, "gone", "c9"))
	set(nk, CharacterCollection, "u1", "c1", `{"version":1,"char_id":"c1","coins":7}`)
	placeForRestore(t, dir, backup)
	res, err := testRestorer(nk, dir).run(context.Background())
	if err != nil {
		t.Fatalf("a deleted account must not stop the restore: %v", err)
	}
	if res.leftOut != 1 || storedCoins(t, nk, "u1", "c1") != 5 || storedCoins(t, nk, "gone", "c9") != -1 {
		t.Errorf("the deleted account's character is left out, the rest restored: %+v", res)
	}
}

func TestRestoreIsAllOrNothing(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
	backup := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":2}`)
	set(nk, ZoneStateCollection, "", "y:world", `{"version":1,"zone_id":"y","tick":2}`)
	before := snapshot(nk)
	placeForRestore(t, dir, backup)
	nk.failOnce("multi", errors.New("database went away"))
	if _, err := testRestorer(nk, dir).run(context.Background()); err == nil {
		t.Fatal("a failed write must fail the restore")
	}
	if !reflect.DeepEqual(snapshot(nk), before) {
		t.Errorf("a failed restore must change nothing")
	}
	if len(filesIn(t, filepath.Join(dir, "restore", "failed"))) != 1 || len(filesIn(t, filepath.Join(dir, "restore"))) != 0 {
		t.Errorf("a failed restore's file moves to restore/failed/, so it isn't tried at every start")
	}
}

func TestRestoreRefusesWhatThisBuildCantLoad(t *testing.T) {
	// Each case makes the file to restore (good is a sound backup of the zone at tick 1).
	for name, makeFile := range map[string]func(t *testing.T, good string) string{
		"a zone save from a newer build": func(t *testing.T, _ string) string {
			nk := newMemStorage()
			set(nk, ZoneStateCollection, "", "z:world", `{"version":99,"zone_id":"z","tick":1}`)
			return backupOf(t, nk, t.TempDir(), time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
		},
		"a character from a newer build": func(t *testing.T, _ string) string {
			nk := newMemStorage()
			set(nk, CharacterCollection, "u1", "c1", `{"version":99,"char_id":"c1"}`)
			return backupOf(t, nk, t.TempDir(), time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
		},
		"a damaged file": func(t *testing.T, good string) string {
			data, err := os.ReadFile(good)
			if err != nil {
				t.Fatal(err)
			}
			bad := filepath.Join(t.TempDir(), "world-20260930T200000Z.json")
			if err := os.WriteFile(bad, []byte(strings.Replace(string(data), `"tick":1`, `"tick":2`, 1)), 0o644); err != nil {
				t.Fatal(err)
			}
			return bad
		},
	} {
		t.Run(name, func(t *testing.T) {
			nk := newMemStorage()
			dir := t.TempDir()
			set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
			good := backupOf(t, nk, dir, time.Date(2026, 9, 30, 19, 0, 0, 0, time.UTC))
			set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":5}`)
			before := snapshot(nk)
			placeForRestore(t, dir, makeFile(t, good))
			if _, err := testRestorer(nk, dir).run(context.Background()); err == nil {
				t.Fatal("must be refused")
			}
			if !reflect.DeepEqual(snapshot(nk), before) || nk.multiCalls != 0 {
				t.Errorf("a refused restore writes nothing")
			}
			if len(filesIn(t, filepath.Join(dir, "pre-restore"))) != 0 {
				t.Errorf("it is refused before anything else happens, even the pre-restore backup")
			}
		})
	}
}

func TestRestoreIsNotAppliedTwiceFromAStuckFile(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
	backup := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":2}`)
	placed := placeForRestore(t, dir, backup)
	info, _ := os.Stat(placed)
	if _, err := testRestorer(nk, dir).run(context.Background()); err != nil || storedTick(t, nk, "z") != 1 {
		t.Fatalf("first restore: %v, tick %d", err, storedTick(t, nk, "z"))
	}
	// The game is played on (tick 3); the same placement of the file is found again (it couldn't be moved away).
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":3}`)
	stuck := placeForRestore(t, dir, backup)
	if err := os.Chtimes(stuck, info.ModTime(), info.ModTime()); err != nil {
		t.Fatal(err)
	}
	res, err := testRestorer(nk, dir).run(context.Background())
	if err != nil || !res.alreadyApplied || storedTick(t, nk, "z") != 3 {
		t.Errorf("an applied file found again must not roll the game back: %v, %+v, tick %d", err, res, storedTick(t, nk, "z"))
	}
	// Put in place again on purpose (a new copy): that is a new request, and it is applied.
	again := placeForRestore(t, dir, backup)
	_ = os.Chtimes(again, info.ModTime().Add(time.Minute), info.ModTime().Add(time.Minute))
	if _, err := testRestorer(nk, dir).run(context.Background()); err != nil || storedTick(t, nk, "z") != 1 {
		t.Errorf("restoring the same backup again later must work: %v, tick %d", err, storedTick(t, nk, "z"))
	}
}

func TestRestoreNeedsExactlyOneFile(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
	if res, err := testRestorer(nk, dir).run(context.Background()); err != nil || !res.nothingToDo {
		t.Fatalf("no file: nothing to do (%v)", err)
	}
	a := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
	b := backupOf(t, nk, dir, time.Date(2026, 9, 30, 21, 0, 0, 0, time.UTC))
	placeForRestore(t, dir, a)
	placeForRestore(t, dir, b)
	before := snapshot(nk)
	if _, err := testRestorer(nk, dir).run(context.Background()); err == nil {
		t.Fatal("two files: which one? Refused")
	}
	if !reflect.DeepEqual(snapshot(nk), before) || len(filesIn(t, filepath.Join(dir, "restore", "failed"))) != 2 {
		t.Errorf("both refused files move to restore/failed/, and nothing changes")
	}
}

func TestRestoreNeedsTheSafetyCopyFirst(t *testing.T) {
	nk := newMemStorage()
	dir := t.TempDir()
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":1}`)
	backup := backupOf(t, nk, dir, time.Date(2026, 9, 30, 20, 0, 0, 0, time.UTC))
	set(nk, ZoneStateCollection, "", "z:world", `{"version":1,"zone_id":"z","tick":2}`)
	// pre-restore/ can't be made (a file is in the way): the current state can't be backed up.
	if err := os.WriteFile(filepath.Join(dir, "pre-restore"), []byte("in the way"), 0o644); err != nil {
		t.Fatal(err)
	}
	placeForRestore(t, dir, backup)
	if _, err := testRestorer(nk, dir).run(context.Background()); err == nil || storedTick(t, nk, "z") != 2 || nk.multiCalls != 0 {
		t.Errorf("without its safety copy, nothing is restored: %v, tick %d", err, storedTick(t, nk, "z"))
	}
}
