package world

// THE SAVE SYSTEM (D73; docs/product/architecture/architecture_persistence.md → "One save queue").
//
// Every save of a zone, and of the characters in it, goes through ONE ordered queue (saveWriter, save_writer.go)
// as a batch built at one tick on the zone's match goroutine (save_batch.go): the zone's world document plus the
// character of every player in the zone, written in one all-or-nothing storage write. So stored data is always the
// result of writing, in order, the first N jobs of the queue — a crash, a restart or a backup always finds each zone
// and the characters in it from the same moment. Two more rules keep that true across zones: at most one live
// copy of each zone (zoneLeases, zone_lease.go) and each character live in one zone at a time (charRegistry).

import (
	"context"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

// defaultAutosaveInterval is how often an occupied zone saves itself and everyone in it (D73: every minute — a
// save costs ~1 ms, world_save_cost_test.go). runtime.env BF_AUTOSAVE_SECONDS overrides it for the whole server;
// a test zone's autosave_seconds overrides it for that zone.
const defaultAutosaveInterval = 60 * time.Second

// saveSystem is the server's one save system: made once per process by StartSaveSystem (InitModule).
type saveSystem struct {
	nk       runtime.NakamaModule
	logger   runtime.Logger
	writer   *saveWriter
	leases   *zoneLeases   // one live copy per zone (zone_lease.go)
	chars    *charRegistry // each character live in one zone at a time (char_registry.go)
	stopping atomic.Bool   // the server is shutting down: no new zone entries, joins or backups
	autosave time.Duration // the default autosave interval
}

var (
	savesMu sync.RWMutex
	saves   *saveSystem
)

// newSaveSystem makes a save system whose queue is not running yet (tests step it by hand).
func newSaveSystem(nk runtime.NakamaModule, logger runtime.Logger) *saveSystem {
	sys := &saveSystem{nk: nk, logger: logger, writer: newSaveWriter(nk, logger), leases: newZoneLeases(),
		chars: newCharRegistry(), autosave: defaultAutosaveInterval}
	sys.writer.onWritten = sys.chars.written // a departing character is free once its batch is written
	return sys
}

// StartSaveSystem makes the server's save system, starts its queue, and makes it the one every match and RPC uses.
// InitModule calls it once, before anything can save. env is the runtime environment (local.yml runtime.env).
func StartSaveSystem(nk runtime.NakamaModule, logger runtime.Logger, env map[string]string) *saveSystem {
	sys := newSaveSystem(nk, logger)
	if v, err := strconv.Atoi(env["BF_AUTOSAVE_SECONDS"]); err == nil && v > 0 {
		sys.autosave = time.Duration(v) * time.Second
	}
	go sys.writer.run(context.Background())
	// Rolling backups (backup.go): the start-up backup's listing is queued now, before any zone can save.
	if dir := env["BF_BACKUP_DIR"]; dir != "" {
		every := defaultBackupInterval
		if v, err := strconv.Atoi(env["BF_BACKUP_MINUTES"]); err == nil && v > 0 {
			every = time.Duration(v) * time.Minute
		}
		newBackups(sys, dir, every).start(context.Background())
		logger.Info("Backups: at start-up, then every %v if anything was saved, in %s", every, dir)
	} else {
		logger.Warn("Backups are OFF: runtime.env has no BF_BACKUP_DIR")
	}
	savesMu.Lock()
	saves = sys
	savesMu.Unlock()
	logger.Info("Save system started: zones autosave every %v", sys.autosave)
	return sys
}

// currentSaves is the server's save system (nil before InitModule — and in unit tests that don't set one up).
func currentSaves() *saveSystem {
	savesMu.RLock()
	defer savesMu.RUnlock()
	return saves
}

// saveSys is the save system this match uses: its own (tests) or the server's.
func (m *Match) saveSys() *saveSystem {
	if m.sys != nil {
		return m.sys
	}
	return currentSaves()
}

// autosaveInterval is how often this zone autosaves: its own autosave_seconds (test zones), else the server's.
func (sys *saveSystem) autosaveInterval(zone *ZoneConfig) time.Duration {
	if zone != nil && zone.AutosaveSeconds > 0 {
		return time.Duration(zone.AutosaveSeconds) * time.Second
	}
	return sys.autosave
}

// sleepSaveGap is the least time between two saves a sleeping player asks for (a bed can be clicked repeatedly).
const sleepSaveGap = 5 * time.Second

// queueSave puts a zone's batch on the save queue — only if its match is still the zone's live copy (fencing at the
// door: a retired copy's save is refused here, never dropped from inside the queue). false = not queued: refused,
// or a coalescable save for the zone already waits (it carries a recent state).
func (sys *saveSystem) queueSave(b *saveBatch) bool {
	sys.leases.mu.Lock()
	defer sys.leases.mu.Unlock()
	if !sys.leases.admitLocked(b.zoneID, b.matchID) {
		sys.logger.Error("Zone %s: a %s save from match %s was refused — that match is no longer the zone's live copy",
			b.zoneID, b.reason, b.matchID)
		return false
	}
	return sys.writer.enqueueBatch(b)
}

// saveIfDue queues the zone's save when one is due — an autosave interval after the last save, or soon after a
// player slept (SaveRequested, at most one per sleepSaveGap). MatchLoop calls it while the zone is occupied.
func (m *Match) saveIfDue(logger runtime.Logger, state *WorldState) {
	sys := m.saveSys()
	if sys == nil || state.CurrentZone == nil {
		return
	}
	now := time.Now()
	since := now.Sub(state.LastSaveAt)
	reason := ""
	switch {
	case since >= sys.autosaveInterval(state.CurrentZone):
		reason = "autosave"
	case state.SaveRequested && since >= sleepSaveGap:
		reason = "sleep"
	default:
		return
	}
	state.LastSaveAt = now // also after a failed build: try again an interval later, not every tick
	b, err := m.buildSaveBatch(state, nil, reason, true)
	if err != nil {
		logger.Error("Zone %s: %s save not queued: %v", state.CurrentZone.ZoneID, reason, err)
		return
	}
	state.SaveRequested = false
	if b.built > slowBatchBuild {
		logger.Warn("Zone %s: building the %s save took %v on the match goroutine", state.CurrentZone.ZoneID, reason, b.built)
	}
	sys.queueSave(b)
}

// queueLeaveSave queues the batch a MatchLeave makes: the departing characters plus the zone and everyone still in
// it. Never skipped. A test zone's debug_leave_delay_ms holds its write back (the crash test's crossing race).
func (m *Match) queueLeaveSave(logger runtime.Logger, state *WorldState, departing []charSave) {
	sys := m.saveSys()
	if sys == nil || state.CurrentZone == nil {
		return
	}
	b, err := m.buildSaveBatch(state, departing, "leave", false)
	if err != nil {
		logger.Error("Zone %s: the leave save was NOT queued (%d departing character(s) stay unsaved): %v",
			state.CurrentZone.ZoneID, len(departing), err)
		return
	}
	if d := state.CurrentZone.DebugLeaveDelayMs; d > 0 {
		b.holdBack = time.Duration(d) * time.Millisecond
	}
	state.LastSaveAt = time.Now()
	sys.queueSave(b)
}

// finalSave queues the zone's last save (MatchTerminate) and waits up to timeout for it to be written.
func (m *Match) finalSave(logger runtime.Logger, state *WorldState, timeout time.Duration) {
	sys := m.saveSys()
	if sys == nil || state.CurrentZone == nil {
		return
	}
	zoneID := state.CurrentZone.ZoneID
	b, err := m.buildSaveBatch(state, nil, "terminate", false)
	if err != nil {
		logger.Error("Zone %s: the final save could not be built: %v", zoneID, err)
		return
	}
	if !sys.queueSave(b) {
		logger.Error("Zone %s: the final save was refused", zoneID)
		return
	}
	select {
	case <-b.done:
		logger.Info("Zone %s: final save on shutdown — world (tick %d) and %d character(s) in one write", zoneID, b.tick, len(b.chars))
	case <-time.After(timeout):
		logger.Error("Zone %s: the final save was NOT written within %v (is the database down?)", zoneID, timeout)
	}
}

// Shutdown is the server's shutdown hook (RegisterShutdown): no new zone entries, joins or backups from now on, then
// wait — within Nakama's grace period (ctx) — until every save queued so far is written. Nakama runs it alongside
// the zones' MatchTerminate (each waits for its own final save) and waits for both.
func (sys *saveSystem) Shutdown(ctx context.Context) {
	sys.stopping.Store(true)
	select {
	case <-sys.writer.barrier():
		sys.logger.Info("Save queue drained for shutdown")
	case <-ctx.Done():
		sys.logger.Error("Shutdown: the save queue did not drain within the grace period (halted: %q)", sys.writer.Halted())
	}
}
