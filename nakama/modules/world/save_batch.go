package world

// A save batch (D73): one zone and everyone in it, captured at one tick on the zone's match goroutine, as bytes —
// later changes to the live state can't leak into it, and the queue can write it on another goroutine. The world
// document plus the character of every player in the zone (and of the players leaving with this batch) go to
// storage in one all-or-nothing write (saveWriter).

import (
	"fmt"
	"time"
)

// charKey names one character: the account it belongs to and its id.
type charKey struct{ userID, charID string }

// stagedCharacter is a character MatchJoinAttempt accepted and loaded, waiting for its MatchJoin.
type stagedCharacter struct {
	key  charKey
	save *CharacterSave
}

// charSave is one character's stored document, as bytes.
type charSave struct {
	charKey
	value string
}

type saveBatch struct {
	zoneID  string
	matchID string // the match that built it — only the zone's current live copy may write (zoneLeases)
	reason  string // autosave | leave | sleep | terminate — for the logs
	tick    int64
	world   string     // the zone's WorldSave document
	chars   []charSave // every character in the zone at that tick, and the departing ones
	departs []charKey  // characters leaving the zone with this batch: free to enter another zone once it's written
	// coalesce: an autosave or a sleep save, which can be skipped while another such batch for the zone still waits —
	// the next one carries everything. Departures and the final save are never skipped.
	coalesce bool
	built    time.Duration // how long building it took on the match goroutine
	holdBack time.Duration // test zones only (debug_leave_delay_ms): the queue waits this long before writing it
	done     chan struct{} // closed once the batch is written
}

// slowBatchBuild is when building a batch on the match goroutine is worth a warning (a save of a fully loaded
// 64-chunk zone costs ~1 ms; world_save_cost_test.go).
const slowBatchBuild = 20 * time.Millisecond

// buildSaveBatch captures the zone and everyone in it, plus the departing characters already captured by the
// caller (their players have left the zone's state by now). A panic while building is turned into an error: a
// failed build is logged and saves nothing, rather than stopping the match.
func (m *Match) buildSaveBatch(state *WorldState, departing []charSave, reason string, coalesce bool) (b *saveBatch, err error) {
	defer func() {
		if r := recover(); r != nil {
			b, err = nil, fmt.Errorf("building the %s save panicked: %v", reason, r)
		}
	}()
	if state.CurrentZone == nil {
		return nil, fmt.Errorf("no zone")
	}
	start := time.Now()
	zoneID := state.CurrentZone.ZoneID
	doc, tick := m.snapshotWorldSaveBytes(state)
	if doc == "" {
		return nil, fmt.Errorf("zone %s: the world document could not be built", zoneID)
	}
	b = &saveBatch{zoneID: zoneID, matchID: state.MatchID, reason: reason, tick: tick, world: doc,
		coalesce: coalesce, done: make(chan struct{})}
	now := time.Now().Unix()
	for _, userID := range sortedStringKeys(state.Players) {
		p := state.Players[userID]
		if p == nil || p.CharacterID == "" {
			continue // a join without a character (test harness, debug) has nothing to keep
		}
		value, err := marshalCharacterSave(buildCharacterSave(p, zoneID, state.Config.ChunkSize, now))
		if err != nil {
			return nil, fmt.Errorf("zone %s: character %s/%s can't be encoded: %w", zoneID, userID, p.CharacterID, err)
		}
		b.chars = append(b.chars, charSave{charKey{userID, p.CharacterID}, value})
	}
	for _, d := range departing {
		b.chars = append(b.chars, d)
		b.departs = append(b.departs, d.charKey)
	}
	b.built = time.Since(start)
	return b, nil
}

// departingCharacter captures a leaving player's character, as bytes, before the player is removed from the zone.
// ok=false: the player has no character (a test-harness or debug join) — nothing to save.
func departingCharacter(state *WorldState, userID string) (charSave, bool, error) {
	p := state.Players[userID]
	if p == nil || p.CharacterID == "" {
		return charSave{}, false, nil
	}
	zoneID := ""
	if state.CurrentZone != nil {
		zoneID = state.CurrentZone.ZoneID
	}
	value, err := marshalCharacterSave(buildCharacterSave(p, zoneID, state.Config.ChunkSize, time.Now().Unix()))
	if err != nil {
		return charSave{}, false, fmt.Errorf("character %s/%s can't be encoded: %w", userID, p.CharacterID, err)
	}
	return charSave{charKey{userID, p.CharacterID}, value}, true, nil
}
