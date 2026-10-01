package world

// Each character live in one zone at a time (char_registry.go, D73): the registry's rows, then the zone crossing
// and the same-zone takeover through the real match callbacks, on the faithful storage stand-in.

import (
	"context"
	"errors"
	"sync"
	"testing"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

type sessPresence struct{ user, session string }

func (p sessPresence) GetUserId() string                 { return p.user }
func (p sessPresence) GetSessionId() string              { return p.session }
func (p sessPresence) GetNodeId() string                 { return "node" }
func (p sessPresence) GetHidden() bool                   { return false }
func (p sessPresence) GetPersistence() bool              { return false }
func (p sessPresence) GetUsername() string               { return p.user }
func (p sessPresence) GetStatus() string                 { return "" }
func (p sessPresence) GetReason() runtime.PresenceReason { return runtime.PresenceReasonUnknown }

// kickRecorder is a dispatcher that records MatchKick (Nakama would turn each into a MatchLeave).
type kickRecorder struct {
	nopDispatcher
	mu     sync.Mutex
	kicked []runtime.Presence
}

func (k *kickRecorder) MatchKick(p []runtime.Presence) error {
	k.mu.Lock()
	defer k.mu.Unlock()
	k.kicked = append(k.kicked, p...)
	return nil
}

func (k *kickRecorder) take() []runtime.Presence {
	k.mu.Lock()
	defer k.mu.Unlock()
	out := k.kicked
	k.kicked = nil
	return out
}

// regRig: a save system, zones started through zoneMatch with the real MatchInit, characters in storage.
type regRig struct {
	t     *testing.T
	nk    *memStorage
	sys   *saveSystem
	disp  *kickRecorder
	zones map[string]*rigZone // match id -> its zone
	clock time.Time
	stop  context.CancelFunc
}

// rigZone is one running zone. Nakama runs all of a match's callbacks on ONE goroutine, one at a time; the rig's
// callbacks come from several test goroutines, so mu makes them take turns the same way.
type rigZone struct {
	mu    sync.Mutex
	id    string
	m     *Match
	state *WorldState
}

func newRegRig(t *testing.T) *regRig {
	nk := newMemStorage()
	nk.matches = map[string]bool{}
	r := &regRig{t: t, nk: nk, sys: newSaveSystem(nk, nopRuntimeLogger()), disp: &kickRecorder{},
		zones: map[string]*rigZone{}, clock: time.Now()}
	r.sys.chars.now = func() time.Time { return r.clock }
	// Nakama's MatchSignal runs the match's own MatchSignal (the "kick" action) on its goroutine.
	nk.signal = func(id, data string) (string, error) {
		z := r.zones[id]
		if z == nil {
			return "", errors.New("match not found")
		}
		z.mu.Lock()
		defer z.mu.Unlock()
		_, res := z.m.MatchSignal(context.Background(), nopRuntimeLogger(), nil, nk, r.disp, 0, z.state, data)
		return res, nil
	}
	return r
}

func (r *regRig) runQueue() {
	ctx, cancel := context.WithCancel(context.Background())
	r.stop = cancel
	r.t.Cleanup(cancel)
	go r.sys.writer.run(ctx)
}

func (r *regRig) startZone(zoneID string) *rigZone {
	r.t.Helper()
	id, _, err := r.sys.zoneMatch(context.Background(), zoneID, func(extra map[string]interface{}) (string, error) {
		id := zoneID + "-match.node"
		params := map[string]interface{}{"world_id": "w", "owner_id": "o", "zone_id": zoneID}
		for k, v := range extra {
			params[k] = v
		}
		m := &Match{sys: r.sys}
		ctx := context.WithValue(context.Background(), runtime.RUNTIME_CTX_MATCH_ID, id)
		st, _, _ := m.MatchInit(ctx, nopRuntimeLogger(), nil, r.nk, params)
		if st == nil {
			return "", errors.New("MatchInit refused")
		}
		r.nk.mu.Lock()
		r.nk.matches[id] = true
		r.nk.mu.Unlock()
		r.zones[id] = &rigZone{id: id, m: m, state: st.(*WorldState)}
		return id, nil
	})
	if err != nil {
		r.t.Fatalf("starting zone %s: %v", zoneID, err)
	}
	return r.zones[id]
}

// storeCharacter puts a new character (the starting kit: 50 fences) in storage.
func (r *regRig) storeCharacter(user, char string) {
	save := DefaultCharacterSave(char, char, Appearance{}, time.Now().Unix())
	value, _ := marshalCharacterSave(save)
	r.nk.mu.Lock()
	r.nk.objs[memKey(CharacterCollection, user, char)] = value
	r.nk.mu.Unlock()
}

// join runs the real join callbacks with the given pass. ok = the attempt accepted it.
func (r *regRig) join(z *rigZone, p sessPresence, char, pass string) bool {
	z.mu.Lock()
	_, ok, _ := z.m.MatchJoinAttempt(context.Background(), nopRuntimeLogger(), nil, r.nk, r.disp, 0, z.state, p,
		map[string]string{"char_id": char, "pass": pass})
	z.mu.Unlock()
	if ok {
		z.mu.Lock()
		z.m.MatchJoin(context.Background(), nopRuntimeLogger(), nil, r.nk, r.disp, 0, z.state, []runtime.Presence{p})
		z.mu.Unlock()
	}
	return ok
}

func (r *regRig) leave(z *rigZone, p runtime.Presence) {
	z.mu.Lock()
	defer z.mu.Unlock()
	z.m.MatchLeave(context.Background(), nopRuntimeLogger(), nil, r.nk, r.disp, 0, z.state, []runtime.Presence{p})
}

// enter is world_enter + the join: reserve (waiting, within budget), then join with the pass.
func (r *regRig) enter(z *rigZone, p sessPresence, char string, budget time.Duration) error {
	ctx, cancel := context.WithTimeout(context.Background(), budget)
	defer cancel()
	pass, err := r.sys.reserve(ctx, charKey{p.user, char}, z.id, z.state.CurrentZone.ZoneID)
	if err != nil {
		return err
	}
	if !r.join(z, p, char, pass) {
		return errors.New("join refused")
	}
	return nil
}

func fences(p *PlayerState) int {
	n := 0
	for _, s := range p.ItemSlots {
		if s.ItemID == "fence_wood" {
			n += s.Count
		}
	}
	return n
}

func dropFences(p *PlayerState, n int) {
	for i := range p.ItemSlots {
		if p.ItemSlots[i].ItemID == "fence_wood" {
			p.ItemSlots[i].Count -= n
			return
		}
	}
}

func TestCrossingWaitsForTheDepartureAndLoadsTheNewestCharacter(t *testing.T) {
	r := newRegRig(t)
	r.storeCharacter("u1", "c1")
	a, b := r.startZone(saveTestZone), r.startZone("savetest_b")
	p := sessPresence{"u1", "s1"}
	if err := r.enter(a, p, "c1", time.Second); err != nil {
		t.Fatal(err)
	}
	dropFences(a.state.Players["u1"], 5) // the player puts 5 fences down in zone A
	if got := fences(a.state.Players["u1"]); got != 45 {
		t.Fatalf("setup: bag %d", got)
	}
	r.leave(a, p) // the departure batch is queued — the queue is NOT running yet: its write is held back

	entered := make(chan error, 1)
	go func() { entered <- r.enter(b, p, "c1", 3*time.Second) }()
	select {
	case err := <-entered:
		t.Fatalf("entering zone B must wait until zone A's save of the character is written (got %v)", err)
	case <-time.After(300 * time.Millisecond):
	}
	r.runQueue()
	if err := <-entered; err != nil {
		t.Fatalf("once A's departure is written, B can be entered: %v", err)
	}
	if got := fences(b.state.Players["u1"]); got != 45 {
		t.Fatalf("the character arrived in B with %d fences — it must be the bag that left A (45), never an older copy", got)
	}
}

func TestSameZoneNewerCopyTakesOver(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	z := r.startZone(saveTestZone)
	old := sessPresence{"u1", "old"}
	if err := r.enter(z, old, "c1", time.Second); err != nil {
		t.Fatal(err)
	}
	dropFences(z.state.Players["u1"], 2) // live bag 48; storage still holds 50

	newer := sessPresence{"u1", "new"}
	entered := make(chan error, 1)
	go func() { entered <- r.enter(z, newer, "c1", 3*time.Second) }()
	// The reserve kicks the old session through the match; Nakama turns the kick into a MatchLeave.
	deadline := time.Now().Add(2 * time.Second)
	var kicked []runtime.Presence
	for len(kicked) == 0 && time.Now().Before(deadline) {
		time.Sleep(10 * time.Millisecond)
		kicked = r.disp.take()
	}
	if len(kicked) != 1 || kicked[0].GetSessionId() != "old" {
		t.Fatalf("the old session must be kicked: %v", kicked)
	}
	r.leave(z, kicked[0])
	if err := <-entered; err != nil {
		t.Fatalf("the newer copy must get in once the old one's leave is written: %v", err)
	}
	if got := fences(z.state.Players["u1"]); got != 48 {
		t.Fatalf("the newer copy must see the live bag (48), not the stored 50: got %d", got)
	}
}

func TestDeadZoneIsRetiredBeforeItsCharacterMoves(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	a, b := r.startZone(saveTestZone), r.startZone("savetest_b")
	p := sessPresence{"u1", "s1"}
	if err := r.enter(a, p, "c1", time.Second); err != nil {
		t.Fatal(err)
	}
	r.nk.mu.Lock()
	delete(r.nk.matches, a.id) // zone A's match is stopped without MatchTerminate: no leave ever comes
	r.nk.mu.Unlock()
	if err := r.enter(b, p, "c1", 2*time.Second); err != nil {
		t.Fatalf("a character whose zone died must be able to enter another: %v", err)
	}
	late, _ := a.m.buildSaveBatch(a.state, nil, "autosave", false)
	if r.sys.queueSave(late) {
		t.Fatal("the dead zone's late save must be refused once it is retired")
	}
}

func TestAnotherCharacterOfTheAccountLeavesTheZoneFirst(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	r.storeCharacter("u1", "c2")
	z := r.startZone(saveTestZone)
	if err := r.enter(z, sessPresence{"u1", "s1"}, "c2", time.Second); err != nil {
		t.Fatal(err)
	}
	entered := make(chan error, 1)
	go func() { entered <- r.enter(z, sessPresence{"u1", "s2"}, "c1", 3*time.Second) }()
	deadline := time.Now().Add(2 * time.Second)
	var kicked []runtime.Presence
	for len(kicked) == 0 && time.Now().Before(deadline) {
		time.Sleep(10 * time.Millisecond)
		kicked = r.disp.take()
	}
	if len(kicked) != 1 || kicked[0].GetSessionId() != "s1" {
		t.Fatalf("the account's other character must be sent out of the zone first: %v", kicked)
	}
	r.leave(z, kicked[0])
	if err := <-entered; err != nil {
		t.Fatalf("then the new character enters: %v", err)
	}
	if p := z.state.Players["u1"]; p == nil || p.CharacterID != "c1" {
		t.Fatalf("the zone must hold the new character")
	}
}

func TestEntryPassRules(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	z := r.startZone(saveTestZone)
	p := sessPresence{"u1", "s1"}
	if r.join(z, p, "c1", "no-pass") {
		t.Fatal("a join without the pass world_enter issued must be refused")
	}
	pass, err := r.sys.reserve(context.Background(), charKey{"u1", "c1"}, z.id, saveTestZone)
	if err != nil {
		t.Fatal(err)
	}
	r.clock = r.clock.Add(passMaxAge + time.Second)
	if r.join(z, p, "c1", pass) {
		t.Fatal("a pass older than 8 s must be refused: the client's 10 s join may already have given up")
	}
	// The ran-out pass no longer holds the character: a new world_enter gets one at once.
	ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel()
	pass2, err := r.sys.reserve(ctx, charKey{"u1", "c1"}, z.id, saveTestZone)
	if err != nil || !r.join(z, p, "c1", pass2) {
		t.Fatalf("a fresh pass must work: %v", err)
	}
}

func TestLateJoinAfterThePassRanOutIsKicked(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	z := r.startZone(saveTestZone)
	p := sessPresence{"u1", "s1"}
	key := charKey{"u1", "c1"}
	pass, _ := r.sys.reserve(context.Background(), key, z.id, saveTestZone)
	if _, ok, _ := z.m.MatchJoinAttempt(context.Background(), nopRuntimeLogger(), nil, r.nk, r.disp, 0, z.state, p,
		map[string]string{"char_id": "c1", "pass": pass}); !ok {
		t.Fatal("the attempt must accept a fresh pass")
	}
	// Nakama's join comes much later (its queue was stalled); meanwhile the joining state ran out and another
	// request took the character.
	r.clock = r.clock.Add(joiningMaxAge + time.Second)
	if _, err := r.sys.reserve(context.Background(), key, "elsewhere.node", "savetest_b"); err != nil {
		t.Fatal(err)
	}
	z.m.MatchJoin(context.Background(), nopRuntimeLogger(), nil, r.nk, r.disp, 0, z.state, []runtime.Presence{p})
	if _, present := z.state.Players["u1"]; present {
		t.Fatal("a join whose pass ran out must not put the character in the zone")
	}
	if kicked := r.disp.take(); len(kicked) != 1 {
		t.Fatalf("its session must be removed: %v", kicked)
	}
}

func TestBusyCharacterGivesUpWithinTheBudget(t *testing.T) {
	r := newRegRig(t)
	r.runQueue()
	r.storeCharacter("u1", "c1")
	a, b := r.startZone(saveTestZone), r.startZone("savetest_b")
	if err := r.enter(a, sessPresence{"u1", "s1"}, "c1", time.Second); err != nil {
		t.Fatal(err)
	}
	// A second copy of the game, still playing in zone A, tries zone B: refused ("character in use").
	if err := r.enter(b, sessPresence{"u1", "s2"}, "c1", 200*time.Millisecond); !errors.Is(err, ErrCharacterBusy) {
		t.Fatalf("a character in play in another zone must be refused within the budget: %v", err)
	}
}

func TestDeleteRefusedWhileInPlayAndQueuedAfterSaves(t *testing.T) {
	r := newRegRig(t)
	r.storeCharacter("u1", "c1")
	z := r.startZone(saveTestZone)
	p := sessPresence{"u1", "s1"}
	r.runQueue()
	if err := r.enter(z, p, "c1", time.Second); err != nil {
		t.Fatal(err)
	}
	savesMu.Lock()
	saves = r.sys // DeleteCharacter uses the server's save system
	savesMu.Unlock()
	defer func() { savesMu.Lock(); saves = nil; savesMu.Unlock() }()
	if err := DeleteCharacter(context.Background(), r.nk, "u1", "c1"); !errors.Is(err, ErrCharacterInPlay) {
		t.Fatalf("a character in a zone must not be deleted: %v", err)
	}
	r.leave(z, p)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	for {
		err := DeleteCharacter(ctx, r.nk, "u1", "c1")
		if err == nil {
			break
		}
		if !errors.Is(err, ErrCharacterInPlay) || ctx.Err() != nil {
			t.Fatalf("once its departure is written the character can be deleted: %v", err)
		}
		time.Sleep(20 * time.Millisecond)
	}
	r.nk.mu.Lock()
	_, still := r.nk.objs[memKey(CharacterCollection, "u1", "c1")]
	r.nk.mu.Unlock()
	if still {
		t.Fatal("the character must be deleted")
	}
}
