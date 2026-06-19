package world

import (
	"sort"
	"strconv"

	"github.com/heroiclabs/nakama-common/runtime"
)

// EcologyStats — the interaction log: per-game-day births-by-source, deaths-by-cause, and the
// predator→prey kill matrix, accumulated as bugs are minted/removed and flushed once per game-day at
// the day rollover (one ECOSTATS line per species + one PREDLOG line per predator-prey pair). This is
// the "why" telemetry for tuning: it tells us a population is below target because births are
// food-limited (low brood/reproduce) vs. dying to predation/starvation, and — the key self-maintenance
// metric — what fraction of births come from the Director's reseed safety net (drive that to ~0).
//
// SOFT STATE, NEVER HASHED. It only counts events the sim already produced; it never feeds back into
// bug positions (the only hashed state). All record* methods are nil-safe so the test states (which
// don't construct Stats) are unaffected. See docs/product/ecology_parameters.md.
type EcologyStats struct {
	Births    map[string]map[BirthSource]int // species -> source -> bugs born this day
	Deaths    map[string]map[DeathCause]int  // species -> cause -> bugs lost this day
	Predation map[string]map[string]int      // predator species -> prey species -> kills this day
}

// BirthSource attributes a minted bug to the mechanic that produced it (recorded at the semantic call
// site, not the shared growSwarm/spawnSwarmAt primitives, so the source is unambiguous).
type BirthSource string

const (
	BirthBrood     BirthSource = "brood"     // visible-brood hatch (fly/butterfly nursery)
	BirthNest      BirthSource = "nest"      // wasp nest hatch / resident respawn
	BirthReproduce BirthSource = "reproduce" // instant-grow / split (predators, individuals, well-fed timer)
	BirthReseed    BirthSource = "reseed"    // Director injection (min-population safety net + cull-with pulse)
	BirthSpawn     BirthSource = "spawn"     // zone spawner (initial seed + continuous spawn_interval)
)

// DeathCause attributes a removed bug to how it died (recorded at the kill call site).
type DeathCause string

const (
	DeathOldAge    DeathCause = "oldage"    // natural lifespan (processNaturalDeath)
	DeathStarve    DeathCause = "starve"    // starvation cull (processStarvation)
	DeathPredation DeathCause = "predation" // eaten by a predator (checkPredationStrike)
	DeathCull      DeathCause = "cull"      // Director hard-cull (directorCull)
)

// allBirthSources / allDeathCauses fix the column order so every ECOSTATS line has the same fields
// (0 when nothing happened) — trivial for tools/plot_interactions.py to parse into a CSV.
var allBirthSources = []BirthSource{BirthBrood, BirthNest, BirthReproduce, BirthReseed, BirthSpawn}
var allDeathCauses = []DeathCause{DeathOldAge, DeathStarve, DeathPredation, DeathCull}

// NewEcologyStats returns an empty accumulator (maps ready).
func NewEcologyStats() *EcologyStats {
	return &EcologyStats{
		Births:    map[string]map[BirthSource]int{},
		Deaths:    map[string]map[DeathCause]int{},
		Predation: map[string]map[string]int{},
	}
}

func (s *EcologyStats) recordBirth(species string, src BirthSource, n int) {
	if s == nil || n <= 0 {
		return
	}
	if s.Births[species] == nil {
		s.Births[species] = map[BirthSource]int{}
	}
	s.Births[species][src] += n
}

func (s *EcologyStats) recordDeath(species string, cause DeathCause, n int) {
	if s == nil || n <= 0 {
		return
	}
	if s.Deaths[species] == nil {
		s.Deaths[species] = map[DeathCause]int{}
	}
	s.Deaths[species][cause] += n
}

func (s *EcologyStats) recordPredation(predator, prey string, n int) {
	if s == nil || n <= 0 {
		return
	}
	if s.Predation[predator] == nil {
		s.Predation[predator] = map[string]int{}
	}
	s.Predation[predator][prey] += n
}

// reset clears the accumulator for the next game-day.
func (s *EcologyStats) reset() {
	if s == nil {
		return
	}
	s.Births = map[string]map[BirthSource]int{}
	s.Deaths = map[string]map[DeathCause]int{}
	s.Predation = map[string]map[string]int{}
}

// emitEcologyStats logs one structured ECOSTATS line per species (current pop + avg satiation from the
// live swarms + the day's births/deaths) and one PREDLOG line per predator→prey pair, then resets. The
// species set is the union of everything seen this day (births/deaths/predation) ∪ live swarms, sorted
// for stable output. Flat key=val so a grep+regex in tools/plot_interactions.py parses it directly.
func (m *Match) emitEcologyStats(state *WorldState, day int64, logger runtime.Logger) {
	if state.Stats == nil {
		return
	}

	// Live aggregates per species (population + mean satiation) from the current swarms.
	type agg struct {
		count  int
		satSum float32
		swarms int
	}
	live := map[string]*agg{}
	for _, sw := range state.Swarms {
		a := live[sw.SpeciesID]
		if a == nil {
			a = &agg{}
			live[sw.SpeciesID] = a
		}
		a.count += sw.Count
		a.satSum += sw.Satiation
		a.swarms++
	}

	// Union of species with any activity this day.
	speciesSet := map[string]struct{}{}
	for sp := range live {
		speciesSet[sp] = struct{}{}
	}
	for sp := range state.Stats.Births {
		speciesSet[sp] = struct{}{}
	}
	for sp := range state.Stats.Deaths {
		speciesSet[sp] = struct{}{}
	}
	species := make([]string, 0, len(speciesSet))
	for sp := range speciesSet {
		species = append(species, sp)
	}
	sort.Strings(species)

	for _, sp := range species {
		pop, avgSat := 0, float32(0)
		if a := live[sp]; a != nil {
			pop = a.count
			if a.swarms > 0 {
				avgSat = a.satSum / float32(a.swarms)
			}
		}
		b, d := state.Stats.Births[sp], state.Stats.Deaths[sp]
		// Fixed-column births/deaths (0 when absent) for stable parsing.
		line := "ECOSTATS day=" + itoa(day) + " sp=" + sp + " pop=" + itoa(int64(pop))
		for _, src := range allBirthSources {
			line += " b_" + string(src) + "=" + itoa(int64(b[src]))
		}
		for _, cause := range allDeathCauses {
			line += " d_" + string(cause) + "=" + itoa(int64(d[cause]))
		}
		line += " avg_sat=" + ftoa(avgSat)
		logger.Info(line)
	}

	// Predation matrix: one line per predator→prey pair (sorted).
	preds := make([]string, 0, len(state.Stats.Predation))
	for p := range state.Stats.Predation {
		preds = append(preds, p)
	}
	sort.Strings(preds)
	for _, pred := range preds {
		preyMap := state.Stats.Predation[pred]
		preys := make([]string, 0, len(preyMap))
		for q := range preyMap {
			preys = append(preys, q)
		}
		sort.Strings(preys)
		for _, prey := range preys {
			logger.Info("PREDLOG day=" + itoa(day) + " pred=" + pred + " prey=" + prey + " kills=" + itoa(int64(preyMap[prey])))
		}
	}

	state.Stats.reset()
}

// emitResourceStats logs one RESSTATS line per game-day with the totals of every DEPLETABLE food STOCK
// — the supply side of the food-competition bound. These are what bug breeding actually competes for, so
// reading them next to ECOSTATS tells us whether a population is breeding-substrate-STARVED (e.g. flies
// well-fed but b_brood low because `rotten` is tiny) vs. genuinely food-bounded. SOFT STATE, never hashed
// (it only sums existing soft stocks — ground items / forage pools / host plants). Paired with
// tools/plot_phase.py to plot population-vs-its-food (closed loop = alive cycle).
//
// Fields: rotten = ready fly/detritivore substrate (rotted ground food, FoodValue>0, NOT carrion);
// unripe = the rot-pipeline backlog (dropped fruit not yet rotted); carrion = bug carcasses (beetle/
// millipede food); nectar = butterfly FEEDING stock (sum ForagePools); milkweed = butterfly BREEDING
// stock (sum HostPlantStates capacity) with msites = host plants still breedable (capacity>0).
func (m *Match) emitResourceStats(state *WorldState, day int64, logger runtime.Logger) {
	var rotten, unripe, carrion int
	var rottenFood int64
	for _, it := range state.GroundItems {
		switch {
		case it.IsCarrion:
			carrion++
		case it.FoodValue > 0:
			rotten++
			rottenFood += int64(it.FoodValue)
		default:
			unripe++ // dropped fruit still ripening into rotten substrate
		}
	}
	var nectar float32
	for _, fp := range state.ForagePools {
		nectar += fp.Nectar
	}
	var milkweed float32
	msites := 0
	for _, hp := range state.HostPlantStates {
		milkweed += hp.Capacity
		if hp.Capacity > 0 {
			msites++
		}
	}
	logger.Info("RESSTATS day=" + itoa(day) +
		" rotten=" + itoa(int64(rotten)) + " rotten_food=" + itoa(rottenFood) +
		" unripe=" + itoa(int64(unripe)) + " carrion=" + itoa(int64(carrion)) +
		" nectar=" + ftoa(nectar) + " milkweed=" + ftoa(milkweed) + " msites=" + itoa(int64(msites)))
}

// emitSwarmSnapshot logs one SWARMSNAP line per live swarm once per game-day — species + world position +
// size — so tools/plot_bugmap.py can render a top-down bug-distribution map per day (WHERE the bugs are,
// not just the per-species totals). Sorted by id for stable output. SOFT STATE, never hashed.
func (m *Match) emitSwarmSnapshot(state *WorldState, day int64, logger runtime.Logger) {
	cs := state.Config.ChunkSize
	for _, id := range sortedStringKeys(state.Swarms) {
		sw := state.Swarms[id]
		if sw.Count <= 0 {
			continue
		}
		logger.Info("SWARMSNAP day=" + itoa(day) + " sp=" + sw.SpeciesID +
			" x=" + ftoa(sw.WorldX(cs)) + " y=" + ftoa(sw.WorldY(cs)) + " count=" + itoa(int64(sw.Count)))
	}
}

// itoa / ftoa — local formatters for the flat key=val log line (one decimal place for satiation).
func itoa(n int64) string { return strconv.FormatInt(n, 10) }
func ftoa(f float32) string {
	return strconv.FormatFloat(float64(f), 'f', 1, 64)
}
