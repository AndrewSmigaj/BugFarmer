package world

// Each character is live in one zone at a time (D73; docs/product/architecture/architecture_persistence.md →
// "One zone at a time").
//
// A character is loaded from storage when it enters a zone and saved with that zone; if it entered the next zone
// before the last one's save of it was written, the next zone would load an older copy — the zone-crossing
// duplication. So a character is FREE to enter a zone only once its departure is written:
//
//   free --world_enter--> reserved (an entry pass for one match) --MatchJoinAttempt--> joining (that session)
//        --MatchJoin--> active --MatchLeave--> releasing (its departure batch is queued) --written--> free
//
//   - world_enter waits (on its own RPC goroutine, within the zone request's budget) until the character is free.
//     If it is active in the SAME zone under another session (a second copy of the game, or the same account with
//     another character), that session is kicked through the match (MatchSignal "kick") and its departure written
//     first. If its zone's match is gone, that match is retired and its queued saves awaited.
//   - The entry pass is checked by MatchJoinAttempt, which re-checks as its LAST step that the pass is at most
//     passMaxAge old. The pass is issued before the client starts joining, and Nakama gives a join 10 s before
//     telling the client "rejected" — while still running the join later if the zone gets to it. Refusing anything
//     older than 8 s means the client always gets the answer, so no ghost join can hold a character.
//   - MatchJoin activates only the session the attempt accepted; a late MatchJoin after the pass ran out is kicked.

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"sync"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

const (
	// passMaxAge: an entry pass older than this is refused by MatchJoinAttempt (Nakama's join timeout is 10 s).
	passMaxAge = 8 * time.Second
	// joiningMaxAge: a joining character whose MatchJoin never came counts as free after this.
	joiningMaxAge = 15 * time.Second
	// kickTimeout bounds the "kick" signal to a zone (Nakama's own signal wait is 10 s).
	kickTimeout = 2 * time.Second
	// recheckEvery: a waiting world_enter looks again this often even if no entry changed.
	recheckEvery = 250 * time.Millisecond
)

var (
	// ErrCharacterBusy: the character is in play elsewhere and didn't come free within the request's budget.
	ErrCharacterBusy = errors.New("character in use")
	// ErrCharacterInPlay: a character can't be deleted while it is in a zone.
	ErrCharacterInPlay = errors.New("character in play")
	errPassRefused     = errors.New("entry pass not valid for this zone")
	errPassExpired     = errors.New("entry pass expired")
)

type charState int

const (
	charReserved charState = iota + 1
	charJoining
	charActive
	charReleasing
	charDeleting
)

type charEntry struct {
	state   charState
	matchID string
	zoneID  string
	session string    // joining / active: the presence's session
	pass    string    // reserved / joining: the entry pass
	at      time.Time // reserved: when the pass was issued; joining: when the attempt accepted it
}

type charRegistry struct {
	mu      sync.Mutex
	entries map[charKey]*charEntry
	changed chan struct{} // closed and replaced whenever any entry changes: wakes the waiting world_enters
	now     func() time.Time
}

func newCharRegistry() *charRegistry {
	return &charRegistry{entries: map[charKey]*charEntry{}, changed: make(chan struct{}), now: time.Now}
}

// notifyLocked wakes every waiter. Callers hold r.mu.
func (r *charRegistry) notifyLocked() {
	close(r.changed)
	r.changed = make(chan struct{})
}

// freeLocked: does the entry no longer hold the character (none, or a pass / join that ran out)?
func (r *charRegistry) freeLocked(e *charEntry) bool {
	if e == nil {
		return true
	}
	switch e.state {
	case charReserved:
		return r.now().Sub(e.at) > passMaxAge
	case charJoining:
		return r.now().Sub(e.at) > joiningMaxAge
	}
	return false
}

func newPass() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

// reserve waits until the character is free and reserves it for matchID, returning the entry pass the join must
// carry. Called by world_enter, on its RPC goroutine — never a match goroutine. Gives up with ErrCharacterBusy when
// ctx (the request's budget) runs out.
func (sys *saveSystem) reserve(ctx context.Context, key charKey, matchID, zoneID string) (string, error) {
	r := sys.chars
	kicked := map[string]bool{} // sessions already asked to leave this request
	for {
		r.mu.Lock()
		e := r.entries[key]
		// One character per account per zone: another character of this account in the zone leaves first.
		other, otherEntry := r.otherCharacterInLocked(key, matchID)
		if other == (charKey{}) && r.freeLocked(e) {
			pass := newPass()
			r.entries[key] = &charEntry{state: charReserved, matchID: matchID, zoneID: zoneID, pass: pass, at: r.now()}
			r.notifyLocked()
			r.mu.Unlock()
			return pass, nil
		}
		var owner, ownerZone, ownerSession string
		var ownerState charState
		if e != nil && !r.freeLocked(e) {
			owner, ownerZone, ownerState, ownerSession = e.matchID, e.zoneID, e.state, e.session
		}
		wait := r.changed
		r.mu.Unlock()

		switch {
		case ownerState == charDeleting:
			return "", ErrCharacterBusy
		case owner != "" && sys.matchGone(ctx, owner):
			// Its zone's match is gone: retire that match (nothing more from it is accepted), wait for everything it
			// queued, then the character is free — its last written save is the one the next zone loads.
			sys.logger.Warn("Character %s/%s: its zone's match %s is gone — retiring it", key.userID, key.charID, owner)
			select {
			case <-sys.retire(ownerZone, owner):
			case <-ctx.Done():
				return "", ErrCharacterBusy
			}
			r.mu.Lock()
			if cur := r.entries[key]; cur != nil && cur.matchID == owner {
				delete(r.entries, key)
				r.notifyLocked()
			}
			r.mu.Unlock()
			continue
		case ownerState == charActive && owner == matchID && !kicked[ownerSession]:
			// Active in this very zone under another session: the newer one takes over — kick the old session; its
			// normal leave writes the character, then it is free.
			kicked[ownerSession] = true
			sys.kick(ctx, matchID, key.userID, ownerSession)
		case other != (charKey{}) && !kicked[otherEntry.session]:
			kicked[otherEntry.session] = true
			sys.kick(ctx, matchID, other.userID, otherEntry.session)
		}
		select {
		case <-wait:
		case <-time.After(recheckEvery): // some changes don't touch an entry: a match dying, a pass running out
		case <-ctx.Done():
			return "", ErrCharacterBusy
		}
	}
}

// otherCharacterInLocked finds another character of the same account active (or joining) in the match.
func (r *charRegistry) otherCharacterInLocked(key charKey, matchID string) (charKey, charEntry) {
	for k, e := range r.entries {
		if k.userID == key.userID && k.charID != key.charID && e.matchID == matchID &&
			(e.state == charActive || e.state == charJoining) {
			return k, *e
		}
	}
	return charKey{}, charEntry{}
}

func (sys *saveSystem) matchGone(ctx context.Context, matchID string) bool {
	m, err := sys.nk.MatchGet(ctx, matchID)
	return err == nil && m == nil
}

// kick asks the match to remove one session (MatchSignal "kick" → dispatcher.MatchKick → an ordinary MatchLeave,
// which saves the character).
func (sys *saveSystem) kick(ctx context.Context, matchID, userID, session string) {
	kctx, cancel := context.WithTimeout(ctx, kickTimeout)
	defer cancel()
	data, _ := json.Marshal(map[string]string{"action": "kick", "user_id": userID, "session_id": session})
	if _, err := sys.nk.MatchSignal(kctx, matchID, string(data)); err != nil {
		sys.logger.Warn("Kick of %s (session %s) from match %s failed: %v", userID, session, matchID, err)
	}
}

// attempt checks an entry pass (MatchJoinAttempt, before the character is loaded).
func (r *charRegistry) attempt(key charKey, matchID, pass string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	e := r.entries[key]
	if e == nil || e.state != charReserved || e.matchID != matchID || e.pass != pass {
		return errPassRefused
	}
	if r.now().Sub(e.at) > passMaxAge {
		return errPassExpired
	}
	return nil
}

// confirmAttempt is MatchJoinAttempt's LAST step: the pass is still this one and still young enough that the client
// is waiting for the answer — then the character is joining, for this session.
func (r *charRegistry) confirmAttempt(key charKey, matchID, pass, session string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	e := r.entries[key]
	if e == nil || e.state != charReserved || e.matchID != matchID || e.pass != pass {
		return errPassRefused
	}
	if r.now().Sub(e.at) > passMaxAge {
		return errPassExpired
	}
	e.state, e.session, e.at = charJoining, session, r.now()
	r.notifyLocked()
	return nil
}

// cancel drops a reservation whose join failed after its pass was accepted (the character couldn't be loaded, say),
// so the player's retry needn't wait for the pass to run out.
func (r *charRegistry) cancel(key charKey, matchID, pass string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if e := r.entries[key]; e != nil && e.state == charReserved && e.matchID == matchID && e.pass == pass {
		delete(r.entries, key)
		r.notifyLocked()
	}
}

// joinRefusal is the reason a refused join gives the client (its crossing retries behind the fade).
func joinRefusal(err error) string {
	if errors.Is(err, errPassExpired) {
		return "pass_expired"
	}
	return "pass_refused"
}

// joined makes the character active (MatchJoin) — only for the session the attempt accepted. false: the pass ran
// out and the character went elsewhere; the caller kicks the presence.
func (r *charRegistry) joined(key charKey, matchID, session string) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	e := r.entries[key]
	if e == nil || e.state != charJoining || e.matchID != matchID || e.session != session {
		return false
	}
	e.state = charActive
	r.notifyLocked()
	return true
}

// departing marks the character as leaving (MatchLeave, as its departure is captured for the leave batch).
func (r *charRegistry) departing(key charKey, matchID, session string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if e := r.entries[key]; e != nil && e.state == charActive && e.matchID == matchID && e.session == session {
		e.state = charReleasing
		r.notifyLocked()
	}
}

// written frees the batch's departing characters once the save queue has written it.
func (r *charRegistry) written(b *saveBatch) {
	if len(b.departs) == 0 {
		return
	}
	r.mu.Lock()
	defer r.mu.Unlock()
	for _, k := range b.departs {
		if e := r.entries[k]; e != nil && e.state == charReleasing && e.matchID == b.matchID {
			delete(r.entries, k)
		}
	}
	r.notifyLocked()
}

// beginDelete reserves a free character for deletion; false = it is in play.
func (r *charRegistry) beginDelete(key charKey) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	if !r.freeLocked(r.entries[key]) {
		return false
	}
	r.entries[key] = &charEntry{state: charDeleting}
	return true
}

func (r *charRegistry) endDelete(key charKey) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if e := r.entries[key]; e != nil && e.state == charDeleting {
		delete(r.entries, key)
		r.notifyLocked()
	}
}

// ReserveCharacter is reserve on the server's save system — for world_enter. "" pass and no error: no save system.
func ReserveCharacter(ctx context.Context, userID, charID, matchID, zoneID string) (string, error) {
	sys := currentSaves()
	if sys == nil {
		return "", nil
	}
	if sys.stopping.Load() {
		return "", ErrServerStopping
	}
	return sys.reserve(ctx, charKey{userID, charID}, matchID, zoneID)
}

// DeleteCharacter deletes one of the account's characters — never one in play — as a task on the save queue, so it
// lands after every save already queued (a backup or a crash never sees it deleted and then saved again). The
// character stays "being deleted" until the task has run, even if ctx gives up first.
func DeleteCharacter(ctx context.Context, nk runtime.NakamaModule, userID, charID string) error {
	sys := currentSaves()
	if sys == nil {
		return DeleteCharacterSave(ctx, nk, userID, charID)
	}
	key := charKey{userID, charID}
	if !sys.chars.beginDelete(key) {
		return ErrCharacterInPlay
	}
	job := sys.writer.runTask(func(tctx context.Context) error {
		defer sys.chars.endDelete(key)
		if err := DeleteCharacterSave(tctx, nk, userID, charID); err != nil {
			return err
		}
		sys.writer.changes.Add(1)
		return nil
	})
	select {
	case <-job.done:
		return job.err
	case <-ctx.Done():
		return ErrCharacterBusy
	}
}
