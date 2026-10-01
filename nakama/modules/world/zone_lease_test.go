package world

// One live copy per zone (zone_lease.go, D73): each row of the lease table, on the faithful storage stand-in, with
// real MatchInit calls standing in for Nakama's MatchCreate.

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

// leaseRig is a save system plus a stand-in for nk.MatchCreate that runs the real MatchInit for the test zone.
type leaseRig struct {
	t       *testing.T
	nk      *memStorage
	sys     *saveSystem
	created atomic.Int32
	states  sync.Map // match id -> *WorldState
}

func newLeaseRig(t *testing.T) *leaseRig {
	nk := newMemStorage()
	nk.matches = map[string]bool{}
	return &leaseRig{t: t, nk: nk, sys: newSaveSystem(nk, nopRuntimeLogger())}
}

// create is what the world RPCs pass to ZoneMatch: start a match (MatchInit binds the zone) and mark it live.
func (r *leaseRig) create(extra map[string]interface{}) (string, error) {
	n := r.created.Add(1)
	id := fmt.Sprintf("match-%d.node", n)
	params := map[string]interface{}{"world_id": "w", "owner_id": "o", "zone_id": saveTestZone}
	for k, v := range extra {
		params[k] = v
	}
	ctx := context.WithValue(context.Background(), runtime.RUNTIME_CTX_MATCH_ID, id)
	state, _, _ := (&Match{sys: r.sys}).MatchInit(ctx, nopRuntimeLogger(), nil, r.nk, params)
	if state == nil {
		return "", errors.New("MatchInit refused to start")
	}
	r.nk.mu.Lock()
	r.nk.matches[id] = true
	r.nk.mu.Unlock()
	r.states.Store(id, state)
	return id, nil
}

func (r *leaseRig) enter(ctx context.Context) (string, bool, error) {
	return r.sys.zoneMatch(ctx, saveTestZone, r.create)
}

func (r *leaseRig) kill(matchID string) { // Nakama stops the match without MatchTerminate
	r.nk.mu.Lock()
	delete(r.nk.matches, matchID)
	r.nk.mu.Unlock()
}

func TestZoneMatchStartsOneCopyThenReusesIt(t *testing.T) {
	r := newLeaseRig(t)
	id1, live1, err := r.enter(context.Background())
	if err != nil || live1 {
		t.Fatalf("the first request must start the zone: %v live=%v", err, live1)
	}
	id2, live2, err := r.enter(context.Background())
	if err != nil || !live2 || id2 != id1 || r.created.Load() != 1 {
		t.Fatalf("the next request must reuse the live copy: id %s vs %s, live=%v, created %d", id2, id1, live2, r.created.Load())
	}
}

func TestZoneMatchConcurrentRequestsStartOneCopy(t *testing.T) {
	r := newLeaseRig(t)
	ids := make(chan string, 10)
	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			id, _, err := r.enter(context.Background())
			if err != nil {
				t.Errorf("request failed: %v", err)
			}
			ids <- id
		}()
	}
	wg.Wait()
	close(ids)
	first := ""
	for id := range ids {
		if first == "" {
			first = id
		}
		if id != first {
			t.Errorf("two copies of one zone: %s and %s", first, id)
		}
	}
	if r.created.Load() != 1 {
		t.Errorf("ten requests at once started %d copies (the roadmap's fault 2)", r.created.Load())
	}
}

func TestZoneMatchRetiresADeadCopyBeforeANewOneLoads(t *testing.T) {
	r := newLeaseRig(t)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	idA, _, _ := r.enter(context.Background())
	stA, _ := r.states.Load(idA)
	a := stA.(*WorldState)
	a.TickCount = 77
	mA := &Match{sys: r.sys}
	queued, err := mA.buildSaveBatch(a, nil, "autosave", false)
	if err != nil || !r.sys.queueSave(queued) {
		t.Fatalf("copy A's save must be admitted while it is the live copy: %v", err)
	}
	// A dies with that save still queued (the queue isn't running yet); a new request arrives.
	r.kill(idA)
	go r.sys.writer.run(ctx)
	idB, live, err := r.enter(context.Background())
	if err != nil || live || idB == idA {
		t.Fatalf("a dead copy must be replaced: %v live=%v", err, live)
	}
	stB, _ := r.states.Load(idB)
	if b := stB.(*WorldState); b.TickCount != 77 {
		t.Errorf("the new copy must load the old copy's last queued save (tick 77), got tick %d", b.TickCount)
	}
	// A callback A was still running finishes and tries to save: refused at the door, never written.
	a.TickCount = 99
	late, _ := mA.buildSaveBatch(a, nil, "autosave", false)
	if r.sys.queueSave(late) {
		t.Fatal("a retired copy's save must be refused")
	}
	if storedTick(t, r.nk, saveTestZone) != 77 {
		t.Errorf("the retired copy wrote over the zone")
	}
}

func TestZoneMatchReportsALiveCopyForCreate(t *testing.T) {
	r := newLeaseRig(t)
	r.enter(context.Background())
	created := r.created.Load()
	_, live, err := r.sys.zoneMatch(context.Background(), saveTestZone, func(map[string]interface{}) (string, error) {
		t.Fatal("create must not be called while a live copy exists")
		return "", nil
	})
	if err != nil || !live || r.created.Load() != created {
		t.Fatalf("a request for a running zone must see the live copy (world_create then refuses): %v live=%v", err, live)
	}
}

func TestStaleZoneStartIsRefused(t *testing.T) {
	r := newLeaseRig(t)
	epoch := r.sys.leases.begin(saveTestZone)
	if _, err := r.create(map[string]interface{}{"zone_epoch": epoch + 1}); err == nil {
		t.Fatal("a MatchInit for an epoch the zone is not starting must refuse")
	}
	r.sys.leases.abort(saveTestZone, epoch)
	if holder := r.sys.leases.holderOf(saveTestZone); holder != "" {
		t.Errorf("a refused start must not hold the zone: %q", holder)
	}
}

func TestFailedZoneStartLeavesTheZoneFree(t *testing.T) {
	r := newLeaseRig(t)
	_, _, err := r.sys.zoneMatch(context.Background(), saveTestZone, func(map[string]interface{}) (string, error) {
		return "", errors.New("MatchCreate failed")
	})
	if err == nil {
		t.Fatal("a failed creation must be reported")
	}
	if _, _, err := r.enter(context.Background()); err != nil {
		t.Fatalf("after a failed start the zone must be free to start: %v", err)
	}
}

func TestZoneMatchRefusedWhileStopping(t *testing.T) {
	r := newLeaseRig(t)
	r.sys.stopping.Store(true)
	if _, _, err := r.enter(context.Background()); !errors.Is(err, ErrServerStopping) {
		t.Fatalf("no zone starts while the server stops: %v", err)
	}
}

func TestZoneMatchGivesUpWithinItsBudget(t *testing.T) {
	r := newLeaseRig(t)
	unlock, err := r.sys.leases.lockZone(context.Background(), saveTestZone) // another request holds the zone
	if err != nil {
		t.Fatal(err)
	}
	defer unlock()
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()
	if _, _, err := r.enter(ctx); !errors.Is(err, ErrZoneBusy) {
		t.Fatalf("a request must give up with 'busy' when its budget runs out: %v", err)
	}
}
