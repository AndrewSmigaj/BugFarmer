package world

// Rolling backups (backup.go, D73), on the faithful storage stand-in and a real folder.

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
	"time"
)

func testBackups(t *testing.T, nk *memStorage) (*backups, string) {
	t.Helper()
	dir := t.TempDir()
	b := newBackups(newSaveSystem(nk, nopRuntimeLogger()), dir, time.Hour)
	return b, dir
}

// backupNow lists and writes a backup with the queue run by hand.
func backupNow(t *testing.T, b *backups) string {
	t.Helper()
	l := b.queueListing()
	runAll(b.sys.writer)
	path, err := b.finish(context.Background(), l, "test")
	if err != nil {
		t.Fatalf("backup failed: %v", err)
	}
	return path
}

func backupTick(t *testing.T, f *backupFile, key string) int64 {
	t.Helper()
	for _, o := range f.ZoneState {
		if o.Key == key {
			var ws WorldSave
			if err := json.Unmarshal(o.Value, &ws); err != nil {
				t.Fatal(err)
			}
			return ws.Tick
		}
	}
	return -1
}

func backupCoins(t *testing.T, f *backupFile, user, char string) int64 {
	t.Helper()
	for _, o := range f.Characters {
		if o.UserID == user && o.Key == char {
			var c CharacterSave
			if err := json.Unmarshal(o.Value, &c); err != nil {
				t.Fatal(err)
			}
			return c.Coins
		}
	}
	return -1
}

func readBackup(t *testing.T, path string) *backupFile {
	t.Helper()
	f, err := readBackupFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return f
}

func TestBackupIsOneMomentOfTheSaveQueue(t *testing.T) {
	nk := newMemStorage()
	b, _ := testBackups(t, nk)
	w := b.sys.writer
	w.enqueueBatch(testBatch("z", 1, "autosave", "u1/c1=5"))
	l := b.queueListing()
	w.enqueueBatch(testBatch("z", 2, "leave", "u1/c1=6")) // queued after the backup: written after its listing
	runAll(w)
	path, err := b.finish(context.Background(), l, "test")
	if err != nil {
		t.Fatal(err)
	}
	f := readBackup(t, path)
	if backupTick(t, f, "z:world") != 1 || backupCoins(t, f, "u1", "c1") != 5 {
		t.Errorf("the backup must hold exactly what the jobs before it wrote: tick %d, coins %d",
			backupTick(t, f, "z:world"), backupCoins(t, f, "u1", "c1"))
	}
	if storedTick(t, nk, "z") != 2 || storedCoins(t, nk, "u1", "c1") != 6 {
		t.Errorf("the batch queued after the backup must still be written")
	}
}

func TestBackupStartUpListingRunsBeforeAnySave(t *testing.T) {
	nk := newMemStorage()
	nk.objs[memKey(ZoneStateCollection, "", "z:world")] = `{"version":1,"zone_id":"z","tick":7}`
	b, dir := testBackups(t, nk)
	ctx, cancel := context.WithCancel(context.Background())
	t.Cleanup(func() { cancel(); <-b.stopped })              // before the folder is removed
	b.start(ctx)                                             // queues the listing at once; the queue isn't running yet
	b.sys.writer.enqueueBatch(testBatch("z", 8, "autosave")) // a zone saving right after start-up
	go b.sys.writer.run(ctx)
	entries := waitForBackups(t, dir, 1)
	if got := backupTick(t, readBackup(t, filepath.Join(dir, entries[0].name)), "z:world"); got != 7 {
		t.Errorf("the start-up backup must hold the state from before this run saved anything: tick %d", got)
	}
}

func waitForBackups(t *testing.T, dir string, n int) []backupEntry {
	t.Helper()
	deadline := time.Now().Add(5 * time.Second)
	for {
		entries, err := rollingBackups(dir)
		if err != nil {
			t.Fatal(err)
		}
		if len(entries) >= n {
			return entries
		}
		if time.Now().After(deadline) {
			t.Fatalf("waited for %d backup(s), have %d", n, len(entries))
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func TestBackupTakesZoneSavesAndCharactersButNotPreUpgradeCopies(t *testing.T) {
	nk := newMemStorage()
	for k, v := range map[string]string{
		"z:world":    `{"version":2,"zone_id":"z","tick":3}`,
		"z:world:v1": `{"version":1,"zone_id":"z","tick":2}`,    // the pre-upgrade copy: not part of a backup
		"old:meta":   `{"version":1,"modified_chunks":["0_0"]}`, // a zone still in the old format: part of it
		"old:0_0":    `{"cells":[]}`,
		"old:swarms": `{"swarms":[]}`,
	} {
		nk.objs[memKey(ZoneStateCollection, "", k)] = v
	}
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"version":1,"char_id":"c1","coins":4}`
	nk.objs[memKey(CharacterBackupCollection, "u1", "c1:v0")] = `{"char_id":"c1"}`
	nk.objs[memKey(worldListCollection, "", "default_z")] = `{"world_id":"default_z"}`
	b, _ := testBackups(t, nk)
	f := readBackup(t, backupNow(t, b))
	var keys []string
	for _, o := range f.ZoneState {
		keys = append(keys, o.Key)
	}
	if got, want := strings.Join(keys, " "), "old:0_0 old:meta old:swarms z:world"; got != want {
		t.Errorf("zone records in the backup: %q, want %q (sorted; no pre-upgrade copy)", got, want)
	}
	if len(f.Characters) != 1 || backupCoins(t, f, "u1", "c1") != 4 {
		t.Errorf("the backup must hold every character and nothing else from other collections: %+v", f.Characters)
	}
}

// worldListCollection is rpc.CollectionWorlds (the world list) — rpc imports world, so it can't be used here.
const worldListCollection = "worlds"

func TestBackupListsEveryAccountAcrossPages(t *testing.T) {
	nk := newMemStorage()
	for u := 0; u < 50; u++ {
		for c := 0; c < 5; c++ {
			nk.objs[memKey(CharacterCollection, fmt.Sprintf("u%02d", u), fmt.Sprintf("c%d", c))] = fmt.Sprintf(`{"coins":%d}`, u*10+c)
		}
	}
	b, _ := testBackups(t, nk)
	f := readBackup(t, backupNow(t, b))
	if len(f.Characters) != 250 {
		t.Fatalf("250 characters over 3 pages, got %d", len(f.Characters))
	}
	if !sort.SliceIsSorted(f.Characters, func(i, j int) bool {
		a, c := f.Characters[i], f.Characters[j]
		return a.Key < c.Key || (a.Key == c.Key && a.UserID < c.UserID)
	}) {
		t.Errorf("characters must be sorted by key, then account, so equal storage makes an equal file")
	}
}

func TestBackupServerOwnedRecordsHaveNoAccount(t *testing.T) {
	nk := newMemStorage()
	nk.objs[memKey(ZoneStateCollection, nilUserID, "z:world")] = `{"tick":1}` // how Nakama lists the server's own
	b, _ := testBackups(t, nk)
	f := readBackup(t, backupNow(t, b))
	if len(f.ZoneState) != 1 || f.ZoneState[0].UserID != "" {
		t.Errorf("a server-owned record is kept without an account: %+v", f.ZoneState)
	}
}

func TestBackupFileDetectsDamageAndNewerFormats(t *testing.T) {
	nk := newMemStorage()
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"coins":12345}`
	b, dir := testBackups(t, nk)
	path := backupNow(t, b)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	damaged := filepath.Join(dir, "damaged.json")
	if err := os.WriteFile(damaged, []byte(strings.Replace(string(data), "12345", "99999", 1)), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := readBackupFile(damaged); err == nil || !strings.Contains(err.Error(), "damaged") {
		t.Errorf("a backup whose contents changed must be reported damaged: %v", err)
	}
	newer := filepath.Join(dir, "newer.json")
	if err := os.WriteFile(newer, []byte(strings.Replace(string(data), `"format":1`, `"format":2`, 1)), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := readBackupFile(newer); err == nil || !strings.Contains(err.Error(), "format 2") {
		t.Errorf("a backup from a newer build must be refused: %v", err)
	}
}

func TestBackupSkipsAnUnchangedCopy(t *testing.T) {
	nk := newMemStorage()
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"coins":1}`
	b, dir := testBackups(t, nk)
	tick := time.Date(2026, 9, 30, 12, 0, 0, 0, time.UTC)
	b.now = func() time.Time { tick = tick.Add(time.Minute); return tick }
	backupNow(t, b)
	l := b.queueListing()
	runAll(b.sys.writer)
	if path, err := b.finish(context.Background(), l, "test"); err != nil || path != "" {
		t.Fatalf("nothing changed: no second file (got %q, %v)", path, err)
	}
	// After a restart too: the newest backup's hash is read back from the folder.
	again := newBackups(newSaveSystem(nk, nopRuntimeLogger()), dir, time.Hour)
	again.now = b.now
	again.loadNewest()
	l = again.queueListing()
	runAll(again.sys.writer)
	if path, err := again.finish(context.Background(), l, "start-up"); err != nil || path != "" {
		t.Fatalf("an unchanged start-up must not write a copy (got %q, %v)", path, err)
	}
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"coins":2}`
	backupNow(t, again)
	if entries, _ := rollingBackups(dir); len(entries) != 2 {
		t.Errorf("a change makes a new backup: %d file(s)", len(entries))
	}
}

func TestBackupRetentionKeepsRecentDailyAndWeekly(t *testing.T) {
	// One backup every 6 hours for 60 days, newest first.
	end := time.Date(2026, 9, 30, 18, 0, 0, 0, time.UTC)
	var entries []backupEntry
	for i := 0; i < 240; i++ {
		at := end.Add(-time.Duration(i) * 6 * time.Hour)
		entries = append(entries, backupEntry{name: "world-" + at.Format(backupTimeLayout) + ".json", at: at})
	}
	dropped := map[string]bool{}
	for _, e := range backupsToDrop(entries, defaultBackupRetention) {
		dropped[e.name] = true
	}
	kept := 0
	for i, e := range entries {
		if !dropped[e.name] {
			kept++
		}
		if i < 10 && dropped[e.name] {
			t.Errorf("the 10 newest are kept: %s dropped", e.name)
		}
	}
	// The newest of each of the 7 most recent days, and of each of the 4 most recent weeks.
	newestOf := func(key func(time.Time) string, n int) []string {
		seen := map[string]bool{}
		var out []string
		for _, e := range entries {
			if k := key(e.at); !seen[k] && len(seen) < n {
				seen[k] = true
				out = append(out, e.name)
			}
		}
		return out
	}
	days := newestOf(func(t time.Time) string { return t.Format("2006-01-02") }, 7)
	weeks := newestOf(func(t time.Time) string { y, w := t.ISOWeek(); return fmt.Sprint(y, w) }, 4)
	for _, n := range append(days, weeks...) {
		if dropped[n] {
			t.Errorf("%s is a day's or week's newest and must be kept", n)
		}
	}
	want := map[string]bool{}
	for _, e := range entries[:10] {
		want[e.name] = true
	}
	for _, n := range append(days, weeks...) {
		want[n] = true
	}
	if kept != len(want) || kept > 21 {
		t.Errorf("kept %d backups; exactly the union of the three rules is %d (at most 21)", kept, len(want))
	}
}

func TestBackupRetentionReachesBackPastIdleWeeks(t *testing.T) {
	// A server played on three days months apart keeps those days' newest, not just the last session's.
	var entries []backupEntry
	for _, d := range []string{"20260930T200000Z", "20260930T100000Z", "20260601T120000Z", "20260115T080000Z"} {
		at, _ := time.Parse(backupTimeLayout, d)
		entries = append(entries, backupEntry{name: "world-" + d + ".json", at: at})
	}
	if drop := backupsToDrop(entries, backupRetention{recent: 1, daily: 7, weekly: 4}); len(drop) != 1 ||
		drop[0].name != "world-20260930T100000Z.json" {
		t.Errorf("only the older backup of the last day goes; got %v", drop)
	}
}

func TestBackupPrunesOnlyAfterTheNewOneReadsBack(t *testing.T) {
	nk := newMemStorage()
	b, dir := testBackups(t, nk)
	// 15 older backups, a minute apart and readable — more than the retention keeps.
	for i := 0; i < 15; i++ {
		at := time.Date(2026, 9, 30, 10, i, 0, 0, time.UTC)
		f, err := newBackupFile("rolling", at, []backupObject{}, []backupObject{{UserID: "u1", Key: "c1",
			Value: json.RawMessage(fmt.Sprintf(`{"coins":%d}`, i))}})
		if err != nil {
			t.Fatal(err)
		}
		if _, err := writeBackupFile(dir, nextBackupName(dir, at), f, readBackupFile); err != nil {
			t.Fatal(err)
		}
	}
	before, _ := rollingBackups(dir)
	if len(before) != 15 {
		t.Fatalf("setup: 15 backups, got %d", len(before))
	}
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"coins":100}`
	b.now = func() time.Time { return time.Date(2026, 9, 30, 11, 0, 0, 0, time.UTC) }
	b.readBack = func(string) (*backupFile, error) { return nil, errors.New("disk said no") }
	l := b.queueListing()
	runAll(b.sys.writer)
	if _, err := b.finish(context.Background(), l, "test"); err == nil {
		t.Fatal("a backup that doesn't read back must fail")
	}
	after, _ := rollingBackups(dir)
	if len(after) != len(before) {
		t.Errorf("nothing may be pruned (and the bad file is removed): %d files before, %d after", len(before), len(after))
	}
	b.readBack = readBackupFile
	backupNow(t, b)
	if final, _ := rollingBackups(dir); len(final) != 10 || final[0].at.Hour() != 11 {
		t.Errorf("with a good backup, the folder is pruned to the 10 newest (one day, one week): %d", len(final))
	}
}

func TestBackupLeavesOtherFilesAlone(t *testing.T) {
	nk := newMemStorage()
	b, dir := testBackups(t, nk)
	b.keep = backupRetention{recent: 1}
	others := []string{"db-before-saves.dump", "world-notes.json", "world-20260101T000000Z.json.bak"}
	for _, n := range others {
		if err := os.WriteFile(filepath.Join(dir, n), []byte("x"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.MkdirAll(filepath.Join(dir, "pre-restore"), 0o755); err != nil {
		t.Fatal(err)
	}
	stale := filepath.Join(dir, ".world-20260930T100000Z.json.tmp")
	if err := os.WriteFile(stale, []byte("{"), 0o644); err != nil {
		t.Fatal(err)
	}
	removeStaleTemps(dir)
	for i := 0; i < 3; i++ {
		nk.objs[memKey(CharacterCollection, "u1", "c1")] = fmt.Sprintf(`{"coins":%d}`, i)
		at := time.Date(2026, 9, 30, 12, i, 0, 0, time.UTC)
		b.now = func() time.Time { return at }
		backupNow(t, b)
	}
	for _, n := range append(others, "pre-restore") {
		if _, err := os.Stat(filepath.Join(dir, n)); err != nil {
			t.Errorf("%s is not ours and must be left alone: %v", n, err)
		}
	}
	if _, err := os.Stat(stale); !errors.Is(err, os.ErrNotExist) {
		t.Errorf("a cut-off backup's temporary file is removed")
	}
}

func TestBackupRunsOnlyWhenSomethingWasSaved(t *testing.T) {
	nk := newMemStorage()
	nk.objs[memKey(CharacterCollection, "u1", "c1")] = `{"coins":1}`
	b, dir := testBackups(t, nk)
	b.every = 20 * time.Millisecond
	ctx, cancel := context.WithCancel(context.Background())
	t.Cleanup(func() { cancel(); <-b.stopped }) // before the folder is removed
	go b.sys.writer.run(ctx)
	b.start(ctx)
	waitForBackups(t, dir, 1)
	time.Sleep(150 * time.Millisecond) // several intervals with nothing saved
	if entries, _ := rollingBackups(dir); len(entries) != 1 {
		t.Fatalf("no backup while nothing is saved: %d", len(entries))
	}
	b.sys.writer.enqueueBatch(testBatch("z", 1, "autosave", "u1/c1=2"))
	waitForBackups(t, dir, 2)
	b.sys.stopping.Store(true) // a stopping server takes no new backups: the loop ends
	select {
	case <-b.stopped:
	case <-time.After(5 * time.Second):
		t.Fatal("the backups must stop once the server is stopping")
	}
}
