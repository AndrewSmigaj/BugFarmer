package world

// One live copy per zone (D73; docs/product/architecture/architecture_persistence.md → "One live copy per zone").
//
// A zone's save is per zone, not per world, so two matches running the same zone would load and write the same save
// (the roadmap's known fault 2: two players arriving at once could start two copies; the debug panel's world_create
// could start a second copy of a running zone under a new world id). So:
//
//   - every request that starts a zone's match goes through zoneMatch, under that zone's lock: a live copy is reused;
//     only when there is none is a new one created;
//   - a copy whose match is gone (Nakama can stop a match without MatchTerminate — a full call queue, a nil return)
//     is RETIRED first — from then on nothing it queues is accepted — and only then does the new copy wait for the
//     save queue to write everything the old copy queued before, and load: so it loads the old copy's last save, and
//     a callback the old copy was still running can't write over the new copy later;
//   - MatchInit binds its match id to the epoch the request reserved (a stale or unknown request is refused);
//   - the save queue admits a zone's batch only from the zone's bound, unretired match ("fencing at the door").

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"
)

var (
	// ErrZoneRunning: a request asked for a NEW copy of a zone that already has a live one (the debug world_create).
	ErrZoneRunning = errors.New("zone already running")
	// ErrServerStopping: the server is shutting down — no zone starts and no one enters.
	ErrServerStopping = errors.New("server stopping")
	// ErrZoneBusy: the zone's lock or the old copy's saves didn't come free in time — try again.
	ErrZoneBusy = errors.New("zone busy, try again")
)

type zoneLease struct {
	holder string // the zone's live match ("" = none bound)
	epoch  int64  // bumped for every new copy; MatchInit binds to it
	// starting: a request holds the zone's lock and is creating a match for `epoch`
	starting bool
}

type zoneLeases struct {
	mu      sync.Mutex
	zones   map[string]*zoneLease
	retired map[string]bool          // match ids that may never queue a save again
	locks   map[string]chan struct{} // one per zone: held across a match's creation (a 1-slot channel, so a wait can time out)
}

func newZoneLeases() *zoneLeases {
	return &zoneLeases{zones: map[string]*zoneLease{}, retired: map[string]bool{}, locks: map[string]chan struct{}{}}
}

func (l *zoneLeases) zone(zoneID string) *zoneLease {
	z := l.zones[zoneID]
	if z == nil {
		z = &zoneLease{}
		l.zones[zoneID] = z
	}
	return z
}

// lockZone takes the zone's lock, waiting no longer than ctx allows.
func (l *zoneLeases) lockZone(ctx context.Context, zoneID string) (func(), error) {
	l.mu.Lock()
	lk := l.locks[zoneID]
	if lk == nil {
		lk = make(chan struct{}, 1)
		l.locks[zoneID] = lk
	}
	l.mu.Unlock()
	select {
	case lk <- struct{}{}:
		return func() { <-lk }, nil
	case <-ctx.Done():
		return nil, ErrZoneBusy
	}
}

func (l *zoneLeases) holderOf(zoneID string) string {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.zone(zoneID).holder
}

// begin reserves the next epoch for a new copy of the zone.
func (l *zoneLeases) begin(zoneID string) int64 {
	l.mu.Lock()
	defer l.mu.Unlock()
	z := l.zone(zoneID)
	z.epoch++
	z.starting = true
	return z.epoch
}

// abort undoes begin when the match could not be created.
func (l *zoneLeases) abort(zoneID string, epoch int64) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if z := l.zone(zoneID); z.epoch == epoch {
		z.starting = false
	}
}

// bind makes matchID the zone's live copy (MatchInit). epoch 0 = a match created outside zoneMatch (unit tests): it
// takes the zone only if no live copy holds it.
func (l *zoneLeases) bind(zoneID string, epoch int64, matchID string) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	z := l.zone(zoneID)
	switch {
	case epoch == 0 && z.holder == "" && !z.starting:
		z.epoch++
	case epoch == 0:
		return fmt.Errorf("zone %s already has a live copy (%s)", zoneID, z.holder)
	case epoch != z.epoch || !z.starting:
		return fmt.Errorf("zone %s: this start (epoch %d) is stale — the zone is at epoch %d", zoneID, epoch, z.epoch)
	}
	z.holder, z.starting = matchID, false
	return nil
}

// admitLocked: may this match queue a save for the zone? Only the zone's bound, unretired copy. Callers hold l.mu.
func (l *zoneLeases) admitLocked(zoneID, matchID string) bool {
	return !l.retired[matchID] && l.zone(zoneID).holder == matchID
}

// retireLocked stops a match from ever queueing a save again and frees its zone. Callers hold l.mu.
func (l *zoneLeases) retireLocked(zoneID, matchID string) {
	l.retired[matchID] = true
	if z := l.zone(zoneID); z.holder == matchID {
		z.holder = ""
	}
}

// retire retires a dead match and queues a barrier IN THE SAME CRITICAL SECTION as the door check: every save the
// old copy got admitted is in the queue before the barrier; anything it tries after is refused. The returned channel
// closes once all of the old copy's saves are written.
func (sys *saveSystem) retire(zoneID, matchID string) chan struct{} {
	sys.leases.mu.Lock()
	defer sys.leases.mu.Unlock()
	sys.leases.retireLocked(zoneID, matchID)
	return sys.writer.barrier()
}

// zoneMatch returns the zone's live match, creating one with create only when there is none. live: an existing copy
// was found (create was not called). Every request that starts a zone's match goes through here.
func (sys *saveSystem) zoneMatch(ctx context.Context, zoneID string,
	create func(params map[string]interface{}) (string, error)) (matchID string, live bool, err error) {
	if sys.stopping.Load() {
		return "", false, ErrServerStopping
	}
	unlock, err := sys.leases.lockZone(ctx, zoneID)
	if err != nil {
		return "", false, err
	}
	defer unlock()

	if holder := sys.leases.holderOf(zoneID); holder != "" {
		if m, _ := sys.nk.MatchGet(ctx, holder); m != nil {
			return holder, true, nil
		}
		// The live copy's match is gone (stopped without MatchTerminate): retire it, then wait until everything it
		// queued is written, so the new copy loads its last save.
		sys.logger.Warn("Zone %s: its match %s is gone — retiring it before a new copy starts", zoneID, holder)
		select {
		case <-sys.retire(zoneID, holder):
		case <-ctx.Done():
			return "", false, ErrZoneBusy
		}
	}
	if sys.stopping.Load() {
		return "", false, ErrServerStopping
	}
	epoch := sys.leases.begin(zoneID)
	id, err := create(map[string]interface{}{"zone_epoch": epoch})
	if err != nil {
		sys.leases.abort(zoneID, epoch)
		return "", false, err
	}
	if bound := sys.leases.holderOf(zoneID); bound != id {
		sys.leases.abort(zoneID, epoch)
		return "", false, fmt.Errorf("zone %s: the new match %s did not take the zone (bound: %q)", zoneID, id, bound)
	}
	return id, false, nil
}

// ZoneMatch is zoneMatch on the server's save system — for the world RPCs (world_enter, world_create, world_join).
// create starts the match with nk.MatchCreate, adding the given params (the reserved zone epoch) to its own.
func ZoneMatch(ctx context.Context, zoneID string, create func(params map[string]interface{}) (string, error)) (string, bool, error) {
	sys := currentSaves()
	if sys == nil {
		id, err := create(nil)
		return id, false, err
	}
	return sys.zoneMatch(ctx, zoneID, create)
}

// zoneEpochParam reads the epoch zoneMatch put in the match's params (0 = none: a match started some other way).
func zoneEpochParam(params map[string]interface{}) int64 {
	switch v := params["zone_epoch"].(type) {
	case int64:
		return v
	case int:
		return int64(v)
	case float64:
		return int64(v)
	}
	return 0
}

// localMatchID names a match whose context carries no id (unit tests calling MatchInit directly).
func localMatchID(zoneID string) string {
	return fmt.Sprintf("local-%s-%d", zoneID, time.Now().UnixNano())
}

// DescribeZoneError is a short, plain reason for a player when a zone can't be entered.
func DescribeZoneError(err error) (message, code string) {
	switch {
	case errors.Is(err, ErrServerStopping):
		return "the server is shutting down", "SERVER_STOPPING"
	case errors.Is(err, ErrZoneBusy):
		return "the zone is busy — try again", "ZONE_BUSY"
	case errors.Is(err, ErrZoneRunning):
		return "that zone is already running in another world", "ZONE_RUNNING"
	}
	return "failed to enter world", "MATCH_CREATE_FAILED"
}
