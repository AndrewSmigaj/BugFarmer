package world

import (
	"encoding/json"

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

// SpeciesPopulation counts living bugs of a species across all swarms. O(#swarms) —
// call at event rate (reproduce/release/spawn), never per-tick-per-swarm.
func (s *WorldState) SpeciesPopulation(speciesID string) int {
	total := 0
	for _, id := range s.SwarmsBySpecies[speciesID] {
		if sw, ok := s.Swarms[id]; ok {
			total += sw.Count
		}
	}
	return total
}

// SpeciesMaxPopulation returns the zone's HARD population cap for a species
// (species_caps.max_population). 0 = uncapped — test zones depend on the zero value.
func (s *WorldState) SpeciesMaxPopulation(speciesID string) int {
	if s.CurrentZone == nil || s.CurrentZone.BugSpawning == nil {
		return 0
	}
	return s.CurrentZone.BugSpawning.SpeciesCaps[speciesID].MaxPopulation
}

// AliveSwarmCount counts a species' swarms that still exist (SwarmsBySpecies may hold
// stale ids of caught/dead swarms).
func (s *WorldState) AliveSwarmCount(speciesID string) int {
	n := 0
	for _, id := range s.SwarmsBySpecies[speciesID] {
		if _, ok := s.Swarms[id]; ok {
			n++
		}
	}
	return n
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

	// Spawn a swarm ("" = no spawn) — cap-aware (defense in depth: the dev tool obeys
	// the same ceilings the game does)
	if msg.SpawnSpecies != "" {
		m.debugSpawnSwarm(logger, state, msg, userID, chunkSize)
	}

	// Give items ("" = no-op): "kit" = the crafting starter bundle, else one item id.
	if msg.GiveItem != "" {
		m.debugGiveItem(logger, dispatcher, state, userID, msg.GiveItem, msg.GiveCount)
	}

	if changed {
		m.sendWorldEnv(dispatcher, state, nil)
	}
}

// debugGiveItem (DEV TOOL) drops items straight into the player's inventory and re-syncs it.
// "kit" hands over a crafting starter bundle (the Stage-1 recipe materials + a couple of items
// for the filtered-container tests); any other id gives `count` of that item.
func (m *Match) debugGiveItem(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	item string,
	count int,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}
	if count <= 0 {
		count = 1
	}

	give := map[string]int{}
	if item == "kit" {
		give = map[string]int{
			"wood": 99, "coal": 50, "iron_ore": 40, "copper_ore": 40,
			"stone_block": 40, "iron_bar": 20, "fiber": 30,
			"straw_hat": 1, "leather_cap": 1, "apple": 20, // filtered-container (clothing/food) tests
			"backpack": 1, // equip → +10 panel slots
		}
	} else if item == "crafting" {
		// FULL crafting-test loadout: every input to exercise the whole chain end to end —
		// mining refine (ore→crusher→sluice→smelter), bars→tools/weapons, gems→cutter, dead bugs→extractor.
		give = map[string]int{"wood": 99, "coal": 99, "sand": 40, "fiber": 40,
			"iron_ore": 30, "copper_ore": 30, "tin_ore": 30, "silver_ore": 30, "gold_ore": 30, "platinum_ore": 30,
			"iron_bar": 20, "copper_bar": 20, "bronze_bar": 10, "steel_bar": 10, "silver_bar": 10, "gold_bar": 10, "platinum_bar": 10,
			"diamond": 5, "quartz": 5, "ruby": 5, "sapphire": 5, "emerald": 5,
			"dead_beetle": 8, "dead_centipede": 8, "dead_millipede": 8, "dead_wasp": 8, "dead_fly": 8, "dead_butterfly": 8,
			"backpack": 1}
	} else if item == "buglab" {
		// Bug Lab loadout: 100 fruit to feed the pens + 10 of each catchable species to release.
		give = map[string]int{"apple": 100}
		for _, sp := range []string{"fly_common", "butterfly_meadow", "wasp_common", "centipede_garden"} {
			player.AddBugs(sp, 10)
		}
	} else {
		give[item] = count
	}

	for id, n := range give {
		player.AddItem(id, n)
	}
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		_ = m.sendInventorySync(logger, dispatcher, player, presence)
	}
	logger.Info("DEBUG WORLD: %s gave items %v", userID, give)
}

// scheduleDailyRain rolls the day's weather at the rollover: 30% chance of ONE shower at
// a random raw tick within the next day-length. The scheduled tick is RAW (monotonic) —
// a debug set-time shifts only the apparent time, so the shower never skips; it may just
// land at an odd apparent hour (and a backward jump's rollover re-fire may re-roll —
// accepted dev behavior, logged).
func (m *Match) scheduleDailyRain(state *WorldState, logger runtime.Logger) {
	if state.TickCount < state.DroughtUntilTick {
		// A Director drought suppresses the daily roll: untended trees stop refilling, so fruit/nectar
		// thin out and the over-large population that triggered the drought eases off naturally.
		state.ScheduledRainTick = 0
		return
	}
	if state.Rng.Float64() >= rainDailyChance {
		state.ScheduledRainTick = 0
		return
	}
	state.ScheduledRainTick = state.TickCount + 1 + state.Rng.Int63n(DayLengthTicks)
	logger.Info("WEATHER: rain scheduled for tick %d (now %d)", state.ScheduledRainTick, state.TickCount)
}

// requestDrought starts (or extends) a Director drought: the daily rain roll is suppressed for `days`
// game-days. The mechanic is DroughtUntilTick (read by scheduleDailyRain); WeatherKind="drought" is a
// display/chart label that processWeather maintains. No-op if a longer drought is already running.
func (m *Match) requestDrought(state *WorldState, logger runtime.Logger, days int64) {
	until := state.TickCount + days*DayLengthTicks
	if until <= state.DroughtUntilTick {
		return
	}
	state.DroughtUntilTick = until
	logger.Info("Director: DROUGHT until tick %d (%d game-days, now %d)", until, days, state.TickCount)
}

// requestExtraRain forces a relief shower NOW and lifts any active drought (the relief-over-suppression
// rule: a species near collapse outranks an overshoot we can still hard-cull). Reuses startRain.
func (m *Match) requestExtraRain(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	state.DroughtUntilTick = 0
	if state.WeatherKind == "rain" {
		return // already raining
	}
	if state.WeatherKind == "drought" {
		m.stopWeather(state, dispatcher, logger) // drop the drought visual so the shower shows
	}
	m.startRain(state, dispatcher, logger, rainMinTicks+state.Rng.Int63n(rainMaxTicks-rainMinTicks+1))
	logger.Info("Director: EXTRA RAIN (relief, now %d)", state.TickCount)
}

// processWeather runs every tick: starts the scheduled shower, ends an expired one.
// `>=` comparisons everywhere — never `==` (a missed exact tick must not wedge a state).
func (m *Match) processWeather(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	// Start a scheduled shower (only when clear — the daily roll is suppressed during a drought, so
	// ScheduledRainTick is 0 then anyway; this also won't interrupt the "drought" visual).
	if state.ScheduledRainTick > 0 && state.TickCount >= state.ScheduledRainTick && state.WeatherKind == "" {
		state.ScheduledRainTick = 0
		m.startRain(state, dispatcher, logger, rainMinTicks+state.Rng.Int63n(rainMaxTicks-rainMinTicks+1))
	}
	// End the current weather (a shower OR an expired drought visual) when its window closes.
	if state.WeatherKind != "" && state.TickCount >= state.WeatherUntilTick {
		m.stopWeather(state, dispatcher, logger)
	}
	// Surface an active drought as a distinct WeatherKind once the sky is otherwise clear (display + chart
	// only; the actual suppression is DroughtUntilTick in scheduleDailyRain). Re-asserts after a relief
	// shower ends if the drought hasn't lifted.
	if state.WeatherKind == "" && state.DroughtUntilTick > state.TickCount {
		state.WeatherKind = "drought"
		state.WeatherUntilTick = state.DroughtUntilTick
		m.sendWorldEnv(dispatcher, state, nil)
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
		m.startRain(state, dispatcher, logger, rainMinTicks+state.Rng.Int63n(rainMaxTicks-rainMinTicks+1))
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

// debugSpawnSwarm handles the F8 spawn button: a new swarm at (spawn_x, spawn_y),
// respecting BOTH zone ceilings — the population cap blocks outright; the swarm-count
// cap blocks minting (use a release to force-join instead).
func (m *Match) debugSpawnSwarm(
	logger runtime.Logger,
	state *WorldState,
	msg DebugWorldMessage,
	userID string,
	chunkSize int,
) {
	speciesID := msg.SpawnSpecies
	species := state.Species[speciesID]
	if species == nil {
		logger.Warn("DEBUG WORLD: %s requested unknown species %q", userID, speciesID)
		return
	}

	n := msg.SpawnCount
	if n <= 0 {
		n = species.MinSwarmSize
		if n <= 0 {
			n = 8
		}
	}

	if maxPop := state.SpeciesMaxPopulation(speciesID); maxPop > 0 &&
		state.SpeciesPopulation(speciesID)+n > maxPop {
		logger.Info("DEBUG WORLD: spawn blocked — %s at population cap %d", speciesID, maxPop)
		return
	}
	if state.CurrentZone != nil && state.CurrentZone.BugSpawning != nil {
		if cap, ok := state.CurrentZone.BugSpawning.SpeciesCaps[speciesID]; ok && cap.Max > 0 &&
			state.AliveSwarmCount(speciesID) >= cap.Max {
			logger.Info("DEBUG WORLD: spawn blocked — %s at swarm-count cap %d", speciesID, cap.Max)
			return
		}
	}

	if swarm := m.spawnSwarmAt(state, speciesID, n, msg.SpawnX, msg.SpawnY, chunkSize); swarm != nil {
		logger.Info("DEBUG WORLD: %s spawned %d %s as %s at (%.1f, %.1f)",
			userID, n, speciesID, swarm.ID, msg.SpawnX, msg.SpawnY)
	}
}
