package world

// The save queue (save_writer.go, D73), run one job at a time against the faithful storage stand-in.

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"testing"
	"time"
)

func testWriter(nk *memStorage) *saveWriter {
	w := newSaveWriter(nk, nopRuntimeLogger())
	w.retryMin, w.retryMax = time.Millisecond, 4*time.Millisecond
	return w
}

// testBatch is a minimal batch: a world document at this tick plus characters given as "user/char=coins".
func testBatch(zone string, tick int64, reason string, chars ...string) *saveBatch {
	b := &saveBatch{zoneID: zone, matchID: "m-" + zone, reason: reason, tick: tick, done: make(chan struct{}),
		world: fmt.Sprintf(`{"version":1,"zone_id":%q,"tick":%d}`, zone, tick)}
	for _, c := range chars {
		who, coinsText, _ := strings.Cut(c, "=")
		user, char, _ := strings.Cut(who, "/")
		coins, _ := strconv.ParseInt(coinsText, 10, 64)
		value, _ := json.Marshal(CharacterSave{Version: characterSaveVersion, CharID: char, Coins: coins})
		b.chars = append(b.chars, charSave{charKey{user, char}, string(value)})
	}
	return b
}

func storedTick(t *testing.T, nk *memStorage, zone string) int64 {
	t.Helper()
	nk.mu.Lock()
	defer nk.mu.Unlock()
	v, ok := nk.objs[memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey(zone, "")))]
	if !ok {
		return -1
	}
	var ws WorldSave
	if err := json.Unmarshal([]byte(v), &ws); err != nil {
		t.Fatal(err)
	}
	return ws.Tick
}

func storedCoins(t *testing.T, nk *memStorage, user, char string) int64 {
	t.Helper()
	nk.mu.Lock()
	defer nk.mu.Unlock()
	v, ok := nk.objs[memKey(CharacterCollection, user, char)]
	if !ok {
		return -1
	}
	var c CharacterSave
	if err := json.Unmarshal([]byte(v), &c); err != nil {
		t.Fatal(err)
	}
	return c.Coins
}

func runAll(w *saveWriter) {
	for w.step(context.Background(), false) {
	}
}

func TestSaveQueueWritesEachBatchTogetherAndInOrder(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	b1 := testBatch("z1", 10, "autosave", "u1/c1=5")
	b2 := testBatch("z2", 20, "autosave", "u2/c2=7")
	b3 := testBatch("z1", 11, "leave", "u1/c1=6")
	for _, b := range []*saveBatch{b1, b2, b3} {
		if !w.enqueueBatch(b) {
			t.Fatal("a batch was refused")
		}
	}
	if !w.step(context.Background(), false) {
		t.Fatal("first job didn't run")
	}
	if storedTick(t, nk, "z1") != 10 || storedCoins(t, nk, "u1", "c1") != 5 || storedTick(t, nk, "z2") != -1 {
		t.Fatalf("after one step only the first batch is written — world and character together")
	}
	select {
	case <-b1.done:
	default:
		t.Fatal("a written batch's done must close")
	}
	runAll(w)
	if storedTick(t, nk, "z1") != 11 || storedCoins(t, nk, "u1", "c1") != 6 || storedTick(t, nk, "z2") != 20 {
		t.Fatalf("later batches must land in queue order")
	}
	if nk.writeCalls != 3 {
		t.Errorf("each batch is ONE storage write: %d writes for 3 batches", nk.writeCalls)
	}
}

func TestSaveQueueWritesAgainstTheStoredVersion(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	w.zoneLoaded("z", "") // the zone started with no save: its first write may only create one
	w.enqueueBatch(testBatch("z", 1, "autosave"))
	runAll(w)
	if storedTick(t, nk, "z") != 1 || w.Halted() != "" {
		t.Fatalf("the first save must create the document")
	}
	w.enqueueBatch(testBatch("z", 2, "autosave"))
	runAll(w)
	if storedTick(t, nk, "z") != 2 || w.Halted() != "" {
		t.Fatalf("later saves are written against the version the queue last wrote")
	}

	// Something else replaces the document: the next write is refused, saving stops, and nothing more is written.
	nk.mu.Lock()
	nk.objs[memKey(ZoneStateCollection, "", worldSaveKey(ZoneStateKey("z", "")))] = `{"version":1,"zone_id":"z","tick":999}`
	nk.mu.Unlock()
	blocked := testBatch("z", 3, "autosave", "u1/c1=1")
	w.enqueueBatch(blocked)
	behind := testBatch("other", 4, "leave", "u9/c9=9")
	w.enqueueBatch(behind)
	runAll(w)
	if w.Halted() == "" {
		t.Fatal("a refused version must stop saving")
	}
	if storedTick(t, nk, "z") != 999 || storedCoins(t, nk, "u1", "c1") != -1 || storedTick(t, nk, "other") != -1 {
		t.Errorf("after a refused version nothing more may be written (not that batch, not the ones behind it)")
	}
	select {
	case <-blocked.done:
		t.Error("an unwritten batch must not report done")
	default:
	}
}

func TestSaveQueueRetriesADatabaseErrorUntilItLands(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	nk.failOnce("write", errors.New("connection refused"))
	b1 := testBatch("z", 1, "leave", "u1/c1=3")
	b2 := testBatch("z", 2, "autosave", "u1/c1=4")
	w.enqueueBatch(b1)
	w.enqueueBatch(b2)
	if !w.step(context.Background(), false) {
		t.Fatal("the job didn't run")
	}
	if storedTick(t, nk, "z") != 1 || storedCoins(t, nk, "u1", "c1") != 3 {
		t.Fatalf("the batch that hit a database error must be retried and land — not be skipped")
	}
	runAll(w)
	if storedTick(t, nk, "z") != 2 || w.Halted() != "" {
		t.Fatalf("the queue carries on after a retried batch")
	}
}

func TestSaveQueueLeavesOutDeletedAccounts(t *testing.T) {
	nk := newMemStorage()
	nk.users = map[string]bool{"u1": true}
	w := testWriter(nk)
	w.enqueueBatch(testBatch("z", 1, "autosave", "u1/c1=5", "gone/c2=9"))
	runAll(w)
	if w.Halted() != "" || storedTick(t, nk, "z") != 1 || storedCoins(t, nk, "u1", "c1") != 5 {
		t.Fatalf("a deleted account must not stop the batch: halted %q", w.Halted())
	}
	if storedCoins(t, nk, "gone", "c2") != -1 {
		t.Errorf("a deleted account's character must be left out")
	}
}

func TestSaveQueueCoalescesAutosavesButNeverDepartures(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	a1, a2 := testBatch("z", 1, "autosave"), testBatch("z", 2, "autosave")
	a1.coalesce, a2.coalesce = true, true
	if !w.enqueueBatch(a1) || w.enqueueBatch(a2) {
		t.Fatalf("while an autosave waits for a zone, the next one is skipped")
	}
	if !w.enqueueBatch(testBatch("z", 3, "leave")) {
		t.Fatalf("a departure always queues")
	}
	other := testBatch("y", 1, "autosave")
	other.coalesce = true
	if !w.enqueueBatch(other) {
		t.Fatalf("another zone's autosave is independent")
	}
	runAll(w)
	a3 := testBatch("z", 4, "autosave")
	a3.coalesce = true
	if !w.enqueueBatch(a3) {
		t.Fatalf("once the waiting autosave is written, the next one queues")
	}
}

func TestSaveQueueBarrierAndTaskRunInOrder(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	w.enqueueBatch(testBatch("z", 1, "leave"))
	barrier := w.barrier()
	var sawTick int64 = -2
	task := w.runTask(func(ctx context.Context) error { sawTick = storedTick(t, nk, "z"); return nil })
	select {
	case <-barrier:
		t.Fatal("a barrier must wait for the jobs queued before it")
	default:
	}
	runAll(w)
	<-barrier
	<-task.done
	if sawTick != 1 {
		t.Errorf("a task runs after the jobs queued before it: it saw tick %d", sawTick)
	}
}

func TestSaveQueueReportsDeparturesOnlyOnceWritten(t *testing.T) {
	nk := newMemStorage()
	w := testWriter(nk)
	var freed []charKey
	w.onWritten = func(b *saveBatch) { freed = append(freed, b.departs...) }
	b := testBatch("z", 1, "leave")
	dep := charSave{charKey{"u1", "c1"}, `{"version":1,"char_id":"c1"}`}
	b.chars = append(b.chars, dep)
	b.departs = append(b.departs, dep.charKey)
	nk.failOnce("write", errors.New("timeout"))
	w.enqueueBatch(b)
	runAll(w)
	if len(freed) != 1 || freed[0] != dep.charKey {
		t.Fatalf("a departing character is freed once its batch is written: %v", freed)
	}
}

func TestSaveQueueCleansUpOldFormatRecordsOnce(t *testing.T) {
	nk := newMemStorage()
	zoneKey := ZoneStateKey("z", "")
	nk.objs[memKey(ZoneStateCollection, "", zoneMetaKey(zoneKey))] = `{"version":1,"modified_chunks":["0_0"]}`
	nk.objs[memKey(ZoneStateCollection, "", zoneKey+":0_0")] = `{}`
	nk.objs[memKey(ZoneStateCollection, "", zoneSwarmKey(zoneKey))] = `[]`
	w := testWriter(nk)
	w.enqueueBatch(testBatch("z", 1, "autosave"))
	runAll(w)
	nk.mu.Lock()
	defer nk.mu.Unlock()
	for _, k := range []string{zoneMetaKey(zoneKey), zoneKey + ":0_0", zoneSwarmKey(zoneKey)} {
		if _, left := nk.objs[memKey(ZoneStateCollection, "", k)]; left {
			t.Errorf("old-format record %s must be deleted after the zone's first new save", k)
		}
	}
}

func TestZoneStartSetsSaveClock(t *testing.T) {
	nk := newMemStorage()
	sys := newSaveSystem(nk, nopRuntimeLogger())
	before := time.Now()
	ws, ok := startZoneWith(&Match{sys: sys}, nk).(*WorldState)
	if !ok {
		t.Fatal("zone didn't start")
	}
	if ws.LastSaveAt.Before(before) {
		t.Errorf("zone start-up must set LastSaveAt, so the first autosave comes an interval later, not at once")
	}
	if v, err := sys.writer.worldVersion(context.Background(), saveTestZone); err != nil || v != "*" {
		t.Errorf("a zone that started with no save must make its first write create one: version %q, err %v", v, err)
	}
}
