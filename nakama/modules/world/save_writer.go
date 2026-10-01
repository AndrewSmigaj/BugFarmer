package world

// The save queue (D73): ONE goroutine writes every save job in the order the jobs were queued.
//
//   - A batch (save_batch.go) is one zone and everyone in it, written in ONE StorageWrite — Nakama runs it as one
//     transaction, so all of it lands or none of it does. The zone's document is written with the version this queue
//     last saw (`*` before the zone's first save), the characters with "" (each character is live in one zone only).
//   - A database error never skips a batch: the same batch is retried, with growing pauses, until it lands (a
//     warning every 30 s). Skipping one would break the rule everything rests on — stored data is always the first N
//     jobs of the queue.
//   - A refused version means something other than this queue changed the zone's stored save. Writing on would mix
//     two histories, so saving STOPS: nothing more is written, an error is logged every 30 s, and storage keeps its
//     last consistent state for the next start.
//   - Characters whose account has been deleted are left out (storage refuses rows for a missing account).
//   - Barriers and tasks run in queue order too: a barrier tells its caller every job queued before it is written; a
//     task runs inside the queue (backups list storage there, so they always see a consistent moment).
//   - Autosave and sleep saves are coalesced: while one waits for a zone, another is skipped (the next carries
//     everything). Departures and final saves always queue.

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

type jobKind int

const (
	jobBatch jobKind = iota
	jobBarrier
	jobTask
)

type saveJob struct {
	kind  jobKind
	batch *saveBatch
	task  func(ctx context.Context) error
	err   error         // a task's result, set before done is closed
	done  chan struct{} // closed once the job has run
}

// longQueue is how many waiting jobs are worth a warning (the database is slow or down).
const longQueue = 100

type saveWriter struct {
	nk     runtime.NakamaModule
	logger runtime.Logger

	mu            sync.Mutex
	queue         []*saveJob
	wake          chan struct{}
	halted        string            // why saving stopped ("" = it hasn't)
	versions      map[string]string // zone -> the version of its stored world document, as far as this queue knows ("*" = none)
	waiting       map[string]int    // zone -> coalescable batches still queued
	legacyDone    map[string]bool   // zones whose old-format records were cleaned up this run
	onWritten     func(*saveBatch)  // after a batch lands — frees its departing characters
	lastLongQueue time.Time
	changes       atomic.Int64 // storage changes made (batches written, characters deleted) — backups wait for one

	retryMin, retryMax, warnEvery, writeTimeout time.Duration
}

func newSaveWriter(nk runtime.NakamaModule, logger runtime.Logger) *saveWriter {
	return &saveWriter{
		nk: nk, logger: logger, wake: make(chan struct{}, 1),
		versions: map[string]string{}, waiting: map[string]int{}, legacyDone: map[string]bool{},
		retryMin: 100 * time.Millisecond, retryMax: 5 * time.Second, warnEvery: 30 * time.Second, writeTimeout: 10 * time.Second,
	}
}

func (w *saveWriter) pushLocked(job *saveJob) {
	w.queue = append(w.queue, job)
	if len(w.queue) > longQueue && time.Since(w.lastLongQueue) > time.Minute {
		w.lastLongQueue = time.Now()
		w.logger.Warn("Save queue: %d jobs waiting — the database may be slow or down", len(w.queue))
	}
	select {
	case w.wake <- struct{}{}:
	default:
	}
}

// enqueueBatch queues a zone's save. false = skipped: it is coalescable and one is already waiting for the zone.
func (w *saveWriter) enqueueBatch(b *saveBatch) bool {
	w.mu.Lock()
	defer w.mu.Unlock()
	if b.coalesce {
		if w.waiting[b.zoneID] > 0 {
			return false
		}
		w.waiting[b.zoneID]++
	}
	w.pushLocked(&saveJob{kind: jobBatch, batch: b, done: b.done})
	return true
}

// barrier queues a marker; the channel closes once every job queued before it has run.
func (w *saveWriter) barrier() chan struct{} {
	job := &saveJob{kind: jobBarrier, done: make(chan struct{})}
	w.mu.Lock()
	w.pushLocked(job)
	w.mu.Unlock()
	return job.done
}

// runTask queues fn to run inside the queue, after every job queued before it.
func (w *saveWriter) runTask(fn func(ctx context.Context) error) *saveJob {
	job := &saveJob{kind: jobTask, task: fn, done: make(chan struct{})}
	w.mu.Lock()
	w.pushLocked(job)
	w.mu.Unlock()
	return job
}

// zoneLoaded records the version of the zone's stored world document as MatchInit found it ("" = none yet).
func (w *saveWriter) zoneLoaded(zoneID, version string) {
	if version == "" {
		version = "*"
	}
	w.mu.Lock()
	w.versions[zoneID] = version
	w.mu.Unlock()
}

// Halted says why saving stopped ("" = it hasn't).
func (w *saveWriter) Halted() string {
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.halted
}

func (w *saveWriter) halt(reason string) {
	w.mu.Lock()
	if w.halted == "" {
		w.halted = reason
	}
	w.mu.Unlock()
	w.logger.Error("SAVING HAS STOPPED: %s. Nothing more will be written; storage keeps its last consistent state, "+
		"which the next start of the server loads.", reason)
}

// run writes jobs until ctx ends — the one queue goroutine (StartSaveSystem).
func (w *saveWriter) run(ctx context.Context) {
	for w.step(ctx, true) {
	}
}

// step runs the job at the head of the queue and reports whether to carry on. With wait, it waits for a job (and,
// once saving has halted, logs every 30 s until ctx ends); without, it returns false at once — tests use that to
// run jobs one at a time.
func (w *saveWriter) step(ctx context.Context, wait bool) bool {
	w.mu.Lock()
	for len(w.queue) == 0 || w.halted != "" {
		halted := w.halted
		w.mu.Unlock()
		if !wait {
			return false
		}
		if halted != "" {
			select {
			case <-ctx.Done():
				return false
			case <-time.After(w.warnEvery):
				w.logger.Error("SAVING HAS STOPPED: %s. Restart the server once the cause is fixed.", halted)
			}
		} else {
			select {
			case <-ctx.Done():
				return false
			case <-w.wake:
			}
		}
		w.mu.Lock()
	}
	job := w.queue[0]
	w.mu.Unlock()

	switch job.kind {
	case jobBarrier:
	case jobTask:
		job.err = job.task(ctx)
	case jobBatch:
		if !w.writeBatch(ctx, job.batch) {
			return ctx.Err() == nil // halted: carry on into the halted wait; ctx ended: stop
		}
	}
	w.mu.Lock()
	w.queue = w.queue[1:]
	if job.kind == jobBatch && job.batch.coalesce {
		w.waiting[job.batch.zoneID]--
	}
	w.mu.Unlock()
	close(job.done)
	return true
}

// writeBatch writes one batch, retrying a database error until it works. false = not written: saving halted (a
// refused version) or ctx ended.
func (w *saveWriter) writeBatch(ctx context.Context, b *saveBatch) bool {
	if b.holdBack > 0 { // test zones only: make a race happen every time (debug_leave_delay_ms)
		select {
		case <-ctx.Done():
			return false
		case <-time.After(b.holdBack):
		}
	}
	delay := w.retryMin
	var lastWarn time.Time
	for {
		err := w.tryWrite(ctx, b)
		if err == nil {
			return true
		}
		if errors.Is(err, runtime.ErrStorageRejectedVersion) {
			w.halt(fmt.Sprintf("zone %s's stored save was changed by something other than this server — its %s save "+
				"at tick %d was refused", b.zoneID, b.reason, b.tick))
			return false
		}
		if time.Since(lastWarn) >= w.warnEvery {
			lastWarn = time.Now()
			w.logger.Warn("Save queue: zone %s's %s save (tick %d) failed — retrying until it lands: %v", b.zoneID, b.reason, b.tick, err)
		}
		select {
		case <-ctx.Done():
			return false
		case <-time.After(delay):
		}
		if delay *= 2; delay > w.retryMax {
			delay = w.retryMax
		}
	}
}

func (w *saveWriter) tryWrite(ctx context.Context, b *saveBatch) error {
	wctx, cancel := context.WithTimeout(ctx, w.writeTimeout)
	defer cancel()
	chars, err := w.withoutDeletedAccounts(wctx, b)
	if err != nil {
		return err
	}
	version, err := w.worldVersion(wctx, b.zoneID)
	if err != nil {
		return err
	}
	world := worldSaveWrite(b.zoneID, b.world)
	world.Version = version
	writes := append(make([]*runtime.StorageWrite, 0, 1+len(chars)), world)
	for _, c := range chars {
		writes = append(writes, characterStorageWrite(c.userID, c.charID, c.value))
	}
	acks, err := w.nk.StorageWrite(wctx, writes)
	if err != nil {
		return err
	}
	w.changes.Add(1)
	w.mu.Lock()
	if len(acks) > 0 && acks[0] != nil && acks[0].Version != "" { // acks come back in the order of the writes
		w.versions[b.zoneID] = acks[0].Version
	} else {
		delete(w.versions, b.zoneID) // unknown: read it before the next write
	}
	cleaned := w.legacyDone[b.zoneID]
	w.legacyDone[b.zoneID] = true
	w.mu.Unlock()
	if !cleaned {
		deleteLegacyZoneRecords(wctx, w.nk, w.logger, ZoneStateKey(b.zoneID, ""), b.zoneID)
	}
	if w.onWritten != nil {
		w.onWritten(b)
	}
	return nil
}

// worldVersion is the version the zone's stored world document should have now: what this queue last wrote or
// MatchInit last loaded, else (unknown) read from storage — `*` when there is none.
func (w *saveWriter) worldVersion(ctx context.Context, zoneID string) (string, error) {
	w.mu.Lock()
	v, known := w.versions[zoneID]
	w.mu.Unlock()
	if known {
		return v, nil
	}
	objs, err := w.nk.StorageRead(ctx, []*runtime.StorageRead{{
		Collection: ZoneStateCollection, Key: worldSaveKey(ZoneStateKey(zoneID, "")), UserID: "",
	}})
	if err != nil {
		return "", err
	}
	v = "*"
	if len(objs) > 0 {
		v = objs[0].Version
	}
	w.mu.Lock()
	w.versions[zoneID] = v
	w.mu.Unlock()
	return v, nil
}

// withoutDeletedAccounts leaves out the characters whose account no longer exists: storage refuses rows for a
// missing account, and one such row would fail the whole batch forever.
func (w *saveWriter) withoutDeletedAccounts(ctx context.Context, b *saveBatch) ([]charSave, error) {
	if len(b.chars) == 0 {
		return nil, nil
	}
	ids := make([]string, 0, len(b.chars))
	seen := map[string]bool{}
	for _, c := range b.chars {
		if !seen[c.userID] {
			seen[c.userID] = true
			ids = append(ids, c.userID)
		}
	}
	users, err := w.nk.UsersGetId(ctx, ids, nil)
	if err != nil {
		return nil, err
	}
	exists := make(map[string]bool, len(users))
	for _, u := range users {
		exists[u.Id] = true
	}
	kept := b.chars[:0:0]
	for _, c := range b.chars {
		if exists[c.userID] {
			kept = append(kept, c)
		} else {
			w.logger.Warn("Save queue: character %s/%s left out of zone %s's save — its account no longer exists", c.userID, c.charID, b.zoneID)
		}
	}
	return kept, nil
}
