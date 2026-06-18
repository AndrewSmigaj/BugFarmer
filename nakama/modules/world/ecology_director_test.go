package world

// The Ecology Director's three-tier ladder: re-seed (extreme low) / extra-rain (moderate low) / nothing
// (natural band) / drought (moderate high) / hard cull (extreme high), with relief-over-suppression on
// the shared global weather. The predator-release + re-seed spawn paths are exercised in the headless
// bug_lab run (they need spawn areas); here we cover the cull + the weather tiers.

import (
	"testing"

	"bugfarmer/entities"
)

func TestDirectorCullsOverBand(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 60, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	state.StaticSim = false
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {CullAt: 50}, // 60 > 50, no CullWith → overcrowding cull
	}}

	m.processEcologyDirector(nopRuntimeLogger(), nil, state, 32)
	if swarm.Count != 50 { // culled down to the band (cull_at 50)
		t.Fatalf("director should cull an over-band species 60 -> 50 (to cull_at), got %d", swarm.Count)
	}
}

func TestDirectorNoOpInBand(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 40, 10, 10)
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	state.StaticSim = false
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {MinPopulation: 10, CullAt: 60}, // 40 is between min and cull_at → no action
	}}

	m.processEcologyDirector(nopRuntimeLogger(), nil, state, 32)
	if swarm.Count != 40 {
		t.Fatalf("in-band population must be untouched, got %d", swarm.Count)
	}
	if state.WeatherKind == "rain" || state.DroughtUntilTick > state.TickCount {
		t.Fatalf("a population inside [event_low,event_high] must trigger no weather event")
	}
}

// Below EventLow (but above the re-seed floor) → an extra-rain relief event (more fruit/nectar → food up).
func TestDirectorExtraRainBelowEventLow(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 12, 10, 10) // 12 < event_low 25
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	state.StaticSim = false
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {EventLow: 25, EventHigh: 90, CullAt: 120},
	}}

	m.processEcologyDirector(nopRuntimeLogger(), nil, state, 32)
	if state.WeatherKind != "rain" {
		t.Fatalf("a species below event_low must trigger extra rain, got weather %q", state.WeatherKind)
	}
}

// Above EventHigh (but below the hard cull) → a drought (rain suppressed); no bug is touched.
func TestDirectorDroughtAboveEventHigh(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	swarm := newTestSwarm("s", 95, 10, 10) // event_high 90 < 95 < cull_at 120
	state.Swarms["s"] = swarm
	state.SwarmsBySpecies["fly_common"] = []string{"s"}
	state.StaticSim = false
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common": {EventLow: 25, EventHigh: 90, CullAt: 120},
	}}

	m.processEcologyDirector(nopRuntimeLogger(), nil, state, 32)
	if state.DroughtUntilTick <= state.TickCount {
		t.Fatalf("a species above event_high must arm a drought, got DroughtUntilTick %d (now %d)", state.DroughtUntilTick, state.TickCount)
	}
	if state.WeatherKind == "rain" {
		t.Fatalf("no species is low — no relief rain should fire")
	}
	if swarm.Count != 95 {
		t.Fatalf("the moderate-high (drought) tier must NOT cull bugs, got %d", swarm.Count)
	}
}

// Shared global weather: one species low (wants rain) + another high (wants drought) → rain wins.
func TestDirectorReliefBeatsSuppression(t *testing.T) {
	state := newTestState(50)
	m := &Match{}
	fly := newTestSwarm("fly", 12, 10, 10) // low → wants rain
	state.Swarms["fly"] = fly
	state.SwarmsBySpecies["fly_common"] = []string{"fly"}

	state.Species["butterfly_meadow"] = &entities.BugSpecies{Category: "swarm", MinSwarmSize: 5, MaxSwarmSize: 50}
	bf := &entities.SwarmState{ID: "bf", SpeciesID: "butterfly_meadow",
		Position: entities.EntityPosition{LocalX: 20, LocalY: 20}, Count: 80} // high → wants drought
	bf.InitializeBugIDs()
	state.Swarms["bf"] = bf
	state.SwarmsBySpecies["butterfly_meadow"] = []string{"bf"}

	state.StaticSim = false
	state.CurrentZone.BugSpawning = &BugSpawnConfig{SpeciesCaps: map[string]SpeciesCap{
		"fly_common":       {EventLow: 25, EventHigh: 90, CullAt: 120},
		"butterfly_meadow": {EventLow: 30, EventHigh: 70, CullAt: 95},
	}}

	m.processEcologyDirector(nopRuntimeLogger(), nil, state, 32)
	if state.WeatherKind != "rain" {
		t.Fatalf("relief (fly low) must beat suppression (butterfly high): expected rain, got %q", state.WeatherKind)
	}
	if state.DroughtUntilTick > state.TickCount {
		t.Fatalf("no drought may be armed when relief rain wins, got DroughtUntilTick %d", state.DroughtUntilTick)
	}
}
