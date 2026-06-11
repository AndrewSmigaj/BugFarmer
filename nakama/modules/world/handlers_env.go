package world

import (
	"encoding/json"

	"github.com/heroiclabs/nakama-common/runtime"
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

// forceWeather handles the F8 weather buttons. Returns true if the env state changed.
// Stub until the rain scheduler lands (W2): logs and ignores.
func (m *Match) forceWeather(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	kind string,
	userID string,
) bool {
	logger.Info("DEBUG WORLD: %s requested weather %q — scheduler not built yet (W2)", userID, kind)
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
