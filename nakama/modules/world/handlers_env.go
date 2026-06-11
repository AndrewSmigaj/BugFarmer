package world

import (
	"encoding/json"
	"math/rand"

	"github.com/heroiclabs/nakama-common/runtime"
)

// Rain v1 tuning (a shower is a one-shot watering event + visuals; per-cell deterministic
// rain is the designed-later v2, see architecture_weather.md)
const (
	rainDailyChance = 0.30 // chance each apparent day gets one shower
	rainMinTicks    = 1500 // 2.5 min
	rainMaxTicks    = 3000 // 5 min
)

// World environment: the apparent time of day (debug offset) and weather.
//
// FRONTIER-NEUTRAL BY CONSTRUCTION: nothing here feeds the deterministic bug sim.
// The server's only time consumer is the day rollover (epoch compare in match.go);
// rain lands through the existing server-side watering paths; clients use the offset
// purely for lighting. Time of day on BOTH sides:
//
//	t = ((tick + DayOffsetTicks) % DayLengthTicks) / DayLengthTicks
//
// The raw tick NEVER jumps — a debug set-time only shifts the apparent time.

// sendWorldEnv sends the WorldEnv display state (OpCode 91). presence != nil targets one
// joiner; nil broadcasts the change to everyone.
func (m *Match) sendWorldEnv(dispatcher runtime.MatchDispatcher, state *WorldState, presence runtime.Presence) {
	if dispatcher == nil {
		return // unit tests drive the state machines without a dispatcher
	}
	msg := WorldEnvMessage{
		DayOffsetTicks:   state.DayOffsetTicks,
		Weather:          state.WeatherKind,
		WeatherUntilTick: state.WeatherUntilTick,
	}
	data, _ := json.Marshal(msg)
	var targets []runtime.Presence
	if presence != nil {
		targets = []runtime.Presence{presence}
	}
	dispatcher.BroadcastMessage(OpCodeWorldEnv, data, targets, nil, true)
}

// AdvanceDayIfNeeded fires the day rollover when the APPARENT day index changes.
// Epoch compare, not modulo: a forward set-time can move the apparent day past the
// `% DayLengthTicks == 0` boundary without landing on it — modulo would silently skip
// that day's reset (and the rain roll). Day-index comparison fires exactly once per
// apparent-day change, in both jump directions (a backward jump re-fires; the resets
// it guards are all idempotent-safe).
func (s *WorldState) AdvanceDayIfNeeded() (int64, bool) {
	currentDay := (s.TickCount + s.DayOffsetTicks) / DayLengthTicks
	if s.TickCount > 0 && currentDay != s.LastRolloverDay {
		s.LastRolloverDay = currentDay
		return currentDay, true
	}
	return currentDay, false
}

// setTimeOfDay shifts DayOffsetTicks so the apparent position within the day becomes
// targetTicks (0..DayLengthTicks-1). Mod-positive so the offset is always >= 0.
func setTimeOfDay(state *WorldState, targetTicks int64) {
	cur := state.TickCount % DayLengthTicks
	state.DayOffsetTicks = ((targetTicks-cur)%DayLengthTicks + DayLengthTicks) % DayLengthTicks
}

// handleDebugWorld (OpCode 90) — DEV TOOL, the EcologyTuning convention: ungated in this
// trusted dev environment, every use loudly logged.
func (m *Match) handleDebugWorld(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg DebugWorldMessage,
	userID string,
	chunkSize int,
) {
	changed := false

	// Set apparent time of day (-1 = leave alone)
	if msg.SetTimeTicks >= 0 && int64(msg.SetTimeTicks) < DayLengthTicks {
		setTimeOfDay(state, int64(msg.SetTimeTicks))
		apparent := (state.TickCount + state.DayOffsetTicks) % DayLengthTicks
		logger.Info("DEBUG WORLD: %s set time-of-day to %d/%d (offset %d)",
			userID, apparent, DayLengthTicks, state.DayOffsetTicks)
		changed = true
	}

	// Force weather ("" = leave alone) — wired in with the rain scheduler (W2)
	if msg.Weather != "" {
		if m.forceWeather(logger, dispatcher, state, msg.Weather, userID) {
			changed = true
		}
	}

	// Spawn a swarm ("" = no spawn) — wired in with the cap-aware spawn path (W5)
	if msg.SpawnSpecies != "" {
		m.debugSpawnSwarm(logger, state, msg, userID)
	}

	if changed {
		m.sendWorldEnv(dispatcher, state, nil)
	}
}

// scheduleDailyRain rolls the day's weather at the rollover: 30% chance of ONE shower at
// a random raw tick within the next day-length. The scheduled tick is RAW (monotonic) —
// a debug set-time shifts only the apparent time, so the shower never skips; it may just
// land at an odd apparent hour (and a backward jump's rollover re-fire may re-roll —
// accepted dev behavior, logged).
func (m *Match) scheduleDailyRain(state *WorldState, logger runtime.Logger) {
	if rand.Float64() >= rainDailyChance {
		state.ScheduledRainTick = 0
		return
	}
	state.ScheduledRainTick = state.TickCount + 1 + rand.Int63n(DayLengthTicks)
	logger.Info("WEATHER: rain scheduled for tick %d (now %d)", state.ScheduledRainTick, state.TickCount)
}

// processWeather runs every tick: starts the scheduled shower, ends an expired one.
// `>=` comparisons everywhere — never `==` (a missed exact tick must not wedge a state).
func (m *Match) processWeather(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	if state.ScheduledRainTick > 0 && state.TickCount >= state.ScheduledRainTick && state.WeatherKind == "" {
		state.ScheduledRainTick = 0
		m.startRain(state, dispatcher, logger, rainMinTicks+rand.Int63n(rainMaxTicks-rainMinTicks+1))
	}
	if state.WeatherKind != "" && state.TickCount >= state.WeatherUntilTick {
		m.stopWeather(state, dispatcher, logger)
	}
}

// startRain begins a shower: ONE-SHOT watering of every crop (daily cap respected) and
// every fruit tree (the wild-tree restock path), through the same state the watering-can
// path uses — rain is ordinary watering as far as the sim is concerned (frontier-neutral).
// Broadcasts WorldEnv so clients start the visuals.
func (m *Match) startRain(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger, durationTicks int64) {
	state.WeatherKind = "rain"
	state.WeatherUntilTick = state.TickCount + durationTicks
	watered := m.rainWaterAll(state, dispatcher)
	m.sendWorldEnv(dispatcher, state, nil)
	logger.Info("RAIN starts at tick %d for %d ticks (watered %d crops/trees)",
		state.TickCount, durationTicks, watered)
}

// stopWeather clears the current weather and tells clients.
func (m *Match) stopWeather(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	state.WeatherKind = ""
	state.WeatherUntilTick = 0
	m.sendWorldEnv(dispatcher, state, nil)
	logger.Info("RAIN ends at tick %d", state.TickCount)
}

// rainWaterAll applies the one-shot shower watering. Crops: +1 water within the daily
// cap, with the wet-tile visual and crop broadcast (the handleWatering pattern). Trees:
// +1 can's worth of charges (capped) — the droplet indicator clears via the existing
// tree-water broadcast. Returns how many things drank.
func (m *Match) rainWaterAll(state *WorldState, dispatcher runtime.MatchDispatcher) int {
	watered := 0

	for _, crop := range state.CropStates {
		cropDef := state.CropDefs[crop.PlantType]
		if cropDef == nil || crop.WateringsToday >= cropDef.MaxDailyWaterings {
			continue
		}
		crop.Water++
		crop.WateringsToday++
		watered++

		cx, cy, lx, ly := GlobalToChunk(crop.GridX, crop.GridY)
		if chunk := state.Chunks[ChunkKey(cx, cy)]; chunk != nil {
			if chunk.Ground[ly][lx] == "garden_plot" {
				chunk.Ground[ly][lx] = "garden_plot_wet"
				m.broadcastWorldUpdate(dispatcher, state, cx, cy, crop.GridX, crop.GridY,
					"garden_plot_wet", nil, false)
			}
		}
		m.broadcastCropUpdate(dispatcher, state, crop.GridX, crop.GridY, crop)
	}

	// Trees: rain pours one FREE watering into the tank (no daily stamp, silent clamp)
	// — the wild-tree restock path: untended trees re-fruit only through showers.
	for _, tree := range state.FruitTreeStates {
		if ok, _ := waterTree(state, tree, false); ok {
			watered++
			m.broadcastTreeWaterUpdate(dispatcher, state, tree)
		}
	}

	return watered
}

// forceWeather handles the F8 weather buttons. Broadcasts internally (start/stop both
// send WorldEnv), so it returns false to avoid a duplicate 91 from the caller.
func (m *Match) forceWeather(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	kind string,
	userID string,
) bool {
	switch kind {
	case "rain":
		logger.Info("DEBUG WORLD: %s forces rain", userID)
		m.startRain(state, dispatcher, logger, rainMinTicks+rand.Int63n(rainMaxTicks-rainMinTicks+1))
	case "stop":
		logger.Info("DEBUG WORLD: %s stops weather", userID)
		if state.WeatherKind != "" {
			m.stopWeather(state, dispatcher, logger)
		}
	default:
		logger.Warn("DEBUG WORLD: %s sent unknown weather %q", userID, kind)
	}
	return false
}

// debugSpawnSwarm handles the F8 spawn button. Stub until the cap-aware spawn extraction
// lands (W5): logs and ignores.
func (m *Match) debugSpawnSwarm(
	logger runtime.Logger,
	state *WorldState,
	msg DebugWorldMessage,
	userID string,
) {
	logger.Info("DEBUG WORLD: %s requested spawn %dx %s — cap-aware spawn not built yet (W5)",
		userID, msg.SpawnCount, msg.SpawnSpecies)
}
