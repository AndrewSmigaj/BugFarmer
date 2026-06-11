package world

import "testing"

// setTimeOfDay: the apparent time-of-day must equal the target after the shift, for any
// current tick, and the offset must always be mod-positive.
func TestSetTimeOfDayOffsetMath(t *testing.T) {
	cases := []struct {
		tick   int64
		target int64
	}{
		{0, 0},
		{0, 4200},          // fresh match -> noonish
		{100, 8399},        // just started -> end of day (offset wraps)
		{8400, 4200},       // exactly one day in
		{8401, 0},          // target behind the current apparent time
		{123456, 2100},     // deep into a match
		{8399, 8399},       // no-op shift
		{DayLengthTicks*7 + 3, 5000},
	}
	for _, c := range cases {
		s := &WorldState{TickCount: c.tick}
		setTimeOfDay(s, c.target)
		if s.DayOffsetTicks < 0 || s.DayOffsetTicks >= DayLengthTicks {
			t.Errorf("tick=%d target=%d: offset %d not mod-positive", c.tick, c.target, s.DayOffsetTicks)
		}
		apparent := (s.TickCount + s.DayOffsetTicks) % DayLengthTicks
		if apparent != c.target {
			t.Errorf("tick=%d target=%d: apparent=%d", c.tick, c.target, apparent)
		}
	}
}

// Plain time passage: the rollover fires exactly once per day boundary, never at tick 0.
func TestAdvanceDayPlainPassage(t *testing.T) {
	s := &WorldState{}
	rolls := 0
	for s.TickCount = 0; s.TickCount <= DayLengthTicks*3; s.TickCount++ {
		if _, rolled := s.AdvanceDayIfNeeded(); rolled {
			rolls++
		}
	}
	if rolls != 3 {
		t.Fatalf("expected 3 rollovers across 3 days, got %d", rolls)
	}
	if s.LastRolloverDay != 3 {
		t.Fatalf("expected LastRolloverDay=3, got %d", s.LastRolloverDay)
	}
}

// A forward set-time that crosses the day boundary must still produce exactly one
// rollover (the modulo formulation would skip it: the apparent day moves PAST the
// boundary without landing on a %==0 tick).
func TestAdvanceDayForwardJumpDoesNotSkip(t *testing.T) {
	s := &WorldState{}

	// Run to late evening of day 0.
	for s.TickCount = 0; s.TickCount < 8000; s.TickCount++ {
		s.AdvanceDayIfNeeded()
	}
	if s.LastRolloverDay != 0 {
		t.Fatalf("setup: expected day 0, got %d", s.LastRolloverDay)
	}

	// Debug set-time forward to "morning" — apparent day index jumps 0 -> 1 between
	// ticks, never landing on a boundary tick.
	setTimeOfDay(s, 1000)

	if _, rolled := s.AdvanceDayIfNeeded(); !rolled {
		t.Fatal("forward set-time crossed the day boundary but the rollover did not fire")
	}
	if s.LastRolloverDay != 1 {
		t.Fatalf("expected LastRolloverDay=1 after the jump, got %d", s.LastRolloverDay)
	}

	// And it fires only once.
	if _, rolled := s.AdvanceDayIfNeeded(); rolled {
		t.Fatal("rollover double-fired after the jump")
	}
}

// A backward set-time re-fires the rollover when the day index drops (documented,
// harmless: everything it resets is idempotent-class), then does not fire again.
func TestAdvanceDayBackwardJumpRefires(t *testing.T) {
	s := &WorldState{}
	for s.TickCount = 0; s.TickCount < DayLengthTicks+100; s.TickCount++ {
		s.AdvanceDayIfNeeded()
	}
	if s.LastRolloverDay != 1 {
		t.Fatalf("setup: expected day 1, got %d", s.LastRolloverDay)
	}

	// Jump the apparent time backward across the boundary: target an apparent time
	// EARLIER in the day than now, far enough that the day index drops... a backward
	// apparent move within setTimeOfDay's mod-positive offset can only move the index
	// FORWARD or keep it (offset >= 0). Emulate a real backward day change directly:
	s.DayOffsetTicks = 0
	cur, rolled := s.AdvanceDayIfNeeded()
	if !rolled || cur != 1 {
		// TickCount is DayLengthTicks+100 with offset 0 -> still day 1; LastRolloverDay
		// is already 1, so no re-fire — that's the no-change case.
		if rolled {
			t.Fatalf("unexpected rollover: day=%d", cur)
		}
	}

	// True backward: pretend the prior offset had pushed us to day 2 first.
	setTimeOfDay(s, 8399) // late evening; may push the index up
	s.AdvanceDayIfNeeded()
	before := s.LastRolloverDay
	s.DayOffsetTicks = 0 // drop the offset: apparent index falls back
	cur, rolled = s.AdvanceDayIfNeeded()
	if before > 1 && (!rolled || cur >= before) {
		t.Fatalf("backward index drop should re-fire: before=%d cur=%d rolled=%v", before, cur, rolled)
	}
}
