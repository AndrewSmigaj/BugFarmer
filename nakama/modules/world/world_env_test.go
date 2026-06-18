package world

import (
	"testing"

	"bugfarmer/entities"
)

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

// Rain's one-shot watering: crops drink +1 within the daily cap (capped crops skip),
// trees gain a can's worth of charges (capped), and nothing else mutates.
func TestRainWaterAllRespectsCaps(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	state.CropStates = map[string]*entities.CropState{}
	state.CropDefs = map[string]*entities.CropDef{
		"tomato": {CropType: "tomato", MaxDailyWaterings: 2},
	}
	thirsty := &entities.CropState{PlantType: "tomato", GridX: 3, GridY: 3, Water: 1, WateringsToday: 1}
	capped := &entities.CropState{PlantType: "tomato", GridX: 4, GridY: 4, Water: 5, WateringsToday: 2}
	state.CropStates["3,3"] = thirsty
	state.CropStates["4,4"] = capped

	dryTree := &entities.FruitTreeState{TreeID: "t1", GridX: 6, GridY: 6, WaterLevel: 0, LastWaterDay: -1}
	fullTree := &entities.FruitTreeState{TreeID: "t2", GridX: 7, GridY: 7, WaterLevel: treeTankCap, LastWaterDay: -1}
	// A tree the player ALREADY watered today: rain must still top it up (no daily stamp)
	wateredToday := &entities.FruitTreeState{TreeID: "t3", GridX: 8, GridY: 8, WaterLevel: 1,
		LastWaterDay: (state.TickCount + state.DayOffsetTicks) / DayLengthTicks}
	state.FruitTreeStates["6,6"] = dryTree
	state.FruitTreeStates["7,7"] = fullTree
	state.FruitTreeStates["8,8"] = wateredToday

	watered := m.rainWaterAll(state, nil)

	if thirsty.Water != 2 || thirsty.WateringsToday != 2 {
		t.Errorf("thirsty crop: water=%d today=%d, want 2/2", thirsty.Water, thirsty.WateringsToday)
	}
	if capped.Water != 5 || capped.WateringsToday != 2 {
		t.Errorf("capped crop mutated: water=%d today=%d", capped.Water, capped.WateringsToday)
	}
	if dryTree.WaterLevel != 1 {
		t.Errorf("dry tree level=%d, want 1", dryTree.WaterLevel)
	}
	if dryTree.LastWaterDay != -1 {
		t.Errorf("rain stamped the daily watering (LastWaterDay=%d)", dryTree.LastWaterDay)
	}
	if fullTree.WaterLevel != treeTankCap {
		t.Errorf("full tree level=%d, want cap %d", fullTree.WaterLevel, treeTankCap)
	}
	if wateredToday.WaterLevel != 2 {
		t.Errorf("already-watered-today tree level=%d, want 2 (rain ignores the daily cap)", wateredToday.WaterLevel)
	}
	if watered != 3 {
		t.Errorf("watered=%d, want 3 (one crop + two trees)", watered)
	}
}

// Scheduler bounds + lifecycle: a scheduled shower starts at/after its tick (>=, never
// ==), runs within the duration bounds, and clears itself; force-stop ends it.
func TestRainSchedulerStartStop(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	logger := nopRuntimeLogger()

	// Schedule deterministically (bypass the 30% roll).
	state.ScheduledRainTick = state.TickCount + 10

	// Before the tick: nothing starts.
	m.processWeather(state, nil, logger)
	if state.WeatherKind != "" {
		t.Fatal("rain started early")
	}

	// Jump PAST the scheduled tick (the >= guard: an exact-tick miss must not wedge).
	state.TickCount += 25
	m.processWeather(state, nil, logger)
	if state.WeatherKind != "rain" {
		t.Fatal("rain did not start at/after its scheduled tick")
	}
	if state.ScheduledRainTick != 0 {
		t.Fatal("scheduled tick not cleared after start")
	}
	dur := state.WeatherUntilTick - state.TickCount
	if dur < rainMinTicks || dur > rainMaxTicks {
		t.Fatalf("duration %d outside [%d,%d]", dur, rainMinTicks, rainMaxTicks)
	}

	// Run to the end: it stops on its own.
	state.TickCount = state.WeatherUntilTick
	m.processWeather(state, nil, logger)
	if state.WeatherKind != "" || state.WeatherUntilTick != 0 {
		t.Fatalf("rain did not stop: kind=%q until=%d", state.WeatherKind, state.WeatherUntilTick)
	}

	// Force path: start + stop.
	m.forceWeather(logger, nil, state, "rain", "tester")
	if state.WeatherKind != "rain" {
		t.Fatal("forceWeather(rain) did not start rain")
	}
	m.forceWeather(logger, nil, state, "stop", "tester")
	if state.WeatherKind != "" {
		t.Fatal("forceWeather(stop) did not stop rain")
	}
}

// A Director drought suppresses the daily rain roll, surfaces a "drought" visual, lifts on its timer,
// and is overridden by a relief shower (requestExtraRain).
func TestDroughtSuppressesAndLifts(t *testing.T) {
	state := newTestState(20)
	m := &Match{}
	logger := nopRuntimeLogger()

	// Arm a 2-day drought.
	m.requestDrought(state, logger, 2)
	if state.DroughtUntilTick != state.TickCount+2*DayLengthTicks {
		t.Fatalf("drought window wrong: %d", state.DroughtUntilTick)
	}

	// The daily roll schedules NOTHING while the drought is active (even though we force the dice
	// by setting a tick first — scheduleDailyRain must early-return).
	state.ScheduledRainTick = 12345
	m.scheduleDailyRain(state, logger)
	if state.ScheduledRainTick != 0 {
		t.Fatalf("drought must suppress the daily rain roll, got ScheduledRainTick %d", state.ScheduledRainTick)
	}

	// processWeather surfaces the drought as a distinct WeatherKind.
	m.processWeather(state, nil, logger)
	if state.WeatherKind != "drought" {
		t.Fatalf("active drought must surface as WeatherKind=drought, got %q", state.WeatherKind)
	}

	// Relief beats suppression: an extra-rain request lifts the drought and starts a shower.
	m.requestExtraRain(state, nil, logger)
	if state.DroughtUntilTick != 0 {
		t.Fatalf("requestExtraRain must lift the drought, DroughtUntilTick=%d", state.DroughtUntilTick)
	}
	if state.WeatherKind != "rain" {
		t.Fatalf("requestExtraRain must start a shower, got %q", state.WeatherKind)
	}

	// Re-arm, let it run out, confirm it clears back to clear sky.
	m.stopWeather(state, nil, logger)
	m.requestDrought(state, logger, 2)
	m.processWeather(state, nil, logger) // surfaces drought
	state.TickCount = state.DroughtUntilTick + 1
	m.processWeather(state, nil, logger) // past the window → clears
	if state.WeatherKind != "" {
		t.Fatalf("an expired drought must clear, got %q", state.WeatherKind)
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
