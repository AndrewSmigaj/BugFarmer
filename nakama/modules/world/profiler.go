package world

import (
	"sort"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"
)

// PerfStats — the COST telemetry: per-species server-CPU time by sub-phase, per-species call/leg counts,
// global per-tick-pass timings, and broadcast byte/message totals, accumulated each tick and flushed once
// per game-day as PERFSTATS (one line per species) + PERFSYS (one global line). It answers "where does the
// server spend time, and which species/subsystem drives network traffic" so we optimize from data, not
// guesses (see docs/product/BACKLOG.md #88). Parsed by tools/plot_perf.py.
//
// Gated by `enabled` (the zone's `profile` flag). When OFF, every method is a cheap nil/flag check — Start()
// returns the zero Time so the matching Stop is a no-op — so PRODUCTION pays nothing and stays byte-identical.
//
// SOFT STATE, NEVER HASHED. Timing/byte values never feed back into the sim (no RNG, no control flow); the
// Start/Stop calls wrap existing work as pure observation, so even a profiled run reproduces byte-for-byte.
// Mirrors EcologyStats (ecology_stats.go). All methods are nil-safe (test states don't construct Perf).
type PerfStats struct {
	enabled bool

	cpu    map[string]map[string]int64 // species -> phase ("food"/"pred"/"action") -> nanos this day
	counts map[string]map[string]int64 // species -> counter ("food_calls"/"pred_thinks"/"legs") -> n this day
	sys    map[string]int64            // global pass ("merge"/"decay"/"forage"/"nests") -> nanos this day

	influenceBytes, influenceMsgs int64 // SWARM leg broadcast (OpCode 71) wire totals
	rosterBytes, rosterMsgs       int64 // SwarmUpdate roster broadcast (OpCode 20) wire totals
}

// Fixed column order so every PERFSTATS/PERFSYS line has identical fields (0 when absent) — trivial for
// tools/plot_perf.py to regex into a CSV.
var perfCPUPhases = []string{"food", "pred", "action"}
var perfCounters = []string{"food_calls", "pred_thinks", "legs"}
var perfSysPhases = []string{"merge", "decay", "forage", "nests"}

// NewPerfStats returns an accumulator. enabled=false makes every method a no-op (production default).
func NewPerfStats(enabled bool) *PerfStats {
	return &PerfStats{
		enabled: enabled,
		cpu:     map[string]map[string]int64{},
		counts:  map[string]map[string]int64{},
		sys:     map[string]int64{},
	}
}

// Start returns a timestamp for the matching Stop, or the zero Time when profiling is off (Stop no-ops on it).
func (p *PerfStats) Start() time.Time {
	if p == nil || !p.enabled {
		return time.Time{}
	}
	return time.Now()
}

// StopSpecies attributes the elapsed time since t to (species, phase).
func (p *PerfStats) StopSpecies(species, phase string, t time.Time) {
	if p == nil || !p.enabled || t.IsZero() {
		return
	}
	m := p.cpu[species]
	if m == nil {
		m = map[string]int64{}
		p.cpu[species] = m
	}
	m[phase] += time.Since(t).Nanoseconds()
}

// StopSys attributes the elapsed time since t to a global (not per-species) pass.
func (p *PerfStats) StopSys(phase string, t time.Time) {
	if p == nil || !p.enabled || t.IsZero() {
		return
	}
	p.sys[phase] += time.Since(t).Nanoseconds()
}

// Count bumps a per-species counter ("food_calls", "pred_thinks", "legs").
func (p *PerfStats) Count(species, counter string) {
	if p == nil || !p.enabled {
		return
	}
	m := p.counts[species]
	if m == nil {
		m = map[string]int64{}
		p.counts[species] = m
	}
	m[counter]++
}

// AddInfluenceBytes / AddRosterBytes record exact marshaled wire size of a bug broadcast.
func (p *PerfStats) AddInfluenceBytes(n int) {
	if p == nil || !p.enabled {
		return
	}
	p.influenceBytes += int64(n)
	p.influenceMsgs++
}
func (p *PerfStats) AddRosterBytes(n int) {
	if p == nil || !p.enabled {
		return
	}
	p.rosterBytes += int64(n)
	p.rosterMsgs++
}

func (p *PerfStats) reset() {
	if p == nil {
		return
	}
	p.cpu = map[string]map[string]int64{}
	p.counts = map[string]map[string]int64{}
	p.sys = map[string]int64{}
	p.influenceBytes, p.influenceMsgs = 0, 0
	p.rosterBytes, p.rosterMsgs = 0, 0
}

// emitPerfStats logs one PERFSTATS line per species (live swarms/bugs + CPU-by-subphase in µs + call/leg
// counts) and one global PERFSYS line (per-pass µs + broadcast byte/msg totals), then resets. Species set =
// live swarms ∪ anything timed/counted this day, sorted for stable output. Flat key=val. Soft, never hashed.
func (m *Match) emitPerfStats(state *WorldState, day int64, logger runtime.Logger) {
	p := state.Perf
	if p == nil || !p.enabled {
		return
	}

	type agg struct{ swarms, bugs int }
	live := map[string]*agg{}
	for _, sw := range state.Swarms {
		a := live[sw.SpeciesID]
		if a == nil {
			a = &agg{}
			live[sw.SpeciesID] = a
		}
		a.swarms++
		a.bugs += sw.Count
	}

	set := map[string]struct{}{}
	for sp := range live {
		set[sp] = struct{}{}
	}
	for sp := range p.cpu {
		set[sp] = struct{}{}
	}
	for sp := range p.counts {
		set[sp] = struct{}{}
	}
	species := make([]string, 0, len(set))
	for sp := range set {
		species = append(species, sp)
	}
	sort.Strings(species)

	for _, sp := range species {
		swarms, bugs := 0, 0
		if a := live[sp]; a != nil {
			swarms, bugs = a.swarms, a.bugs
		}
		line := "PERFSTATS day=" + itoa(day) + " sp=" + sp +
			" swarms=" + itoa(int64(swarms)) + " bugs=" + itoa(int64(bugs))
		c := p.cpu[sp] // nil map reads as 0 — safe
		for _, ph := range perfCPUPhases {
			line += " cpu_" + ph + "_us=" + itoa(c[ph]/1000) // ns -> µs
		}
		cnt := p.counts[sp]
		for _, k := range perfCounters {
			line += " " + k + "=" + itoa(cnt[k])
		}
		logger.Info(line)
	}

	sysLine := "PERFSYS day=" + itoa(day)
	for _, ph := range perfSysPhases {
		sysLine += " sys_" + ph + "_us=" + itoa(p.sys[ph]/1000)
	}
	sysLine += " influence_bytes=" + itoa(p.influenceBytes) + " influence_msgs=" + itoa(p.influenceMsgs) +
		" roster_bytes=" + itoa(p.rosterBytes) + " roster_msgs=" + itoa(p.rosterMsgs)
	logger.Info(sysLine)

	p.reset()
}
