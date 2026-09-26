package world

import (
	"encoding/json"
	"os"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Tuning — the ecology balance dials, loaded from data/ecology_tuning.json at MatchInit so a config sweep
// (tools/bug_lab_configs) can override them WITHOUT recompiling. Soft state, NEVER hashed. An absent file
// (or a missing key) keeps the DefaultTuning() value, which equals the current code constant — so a
// no-override run is byte-identical to the compiled defaults. See docs/product/ecology/ecology_parameters.md.
type Tuning struct {
	// Plant food governors (handlers_farming.go)
	NectarRegenPerTick   float32 `json:"nectar_regen_per_tick"`
	MaxNectar            float32 `json:"max_nectar"`
	HostRegenPerTick     float32 `json:"host_regen_per_tick"`
	HostBreedCost        float32 `json:"host_breed_cost"`
	MaxHostCapacity      float32 `json:"max_host_capacity"`
	DroughtFoodRegenMult float32 `json:"drought_food_regen_mult"`

	// Leaf-litter forage pool — the millipede's DEPLETABLE detritus food (the forest-floor analogue of
	// flower nectar). Scarcer + slower-regrowing than nectar by design, so millipede is genuinely
	// food-bounded and OSCILLATES instead of pinning flat on infinite litter.
	MaxLitter          float32 `json:"max_litter"`
	LitterRegenPerTick float32 `json:"litter_regen_per_tick"`

	// Lifecycle / Director (match.go, predation.go, ecology_director.go)
	SpawnSatiation         float32 `json:"spawn_satiation"`
	StarvationDeathSecs    float32 `json:"starvation_death_secs"`
	StarvationCullFrac     float32 `json:"starvation_cull_frac"`
	PredatorBreedSatiation float32 `json:"predator_breed_satiation"`
	DirectorIntervalTicks  int64   `json:"director_interval_ticks"`
	DroughtDays            int64   `json:"drought_days"`

	// Nest economy + the daughter-nest founding distance (the predator-clustering dial)
	NestHatchCount   int `json:"nest_hatch_count"`
	NestBroodCap     int `json:"nest_brood_cap"`
	NestHatchCost    int `json:"nest_hatch_cost"`
	NestFoundingSize int `json:"nest_founding_size"`
	NestFoundDistMin int `json:"nest_found_dist_min"`
	NestFoundDistMax int `json:"nest_found_dist_max"`
}

// DefaultTuning returns the compiled-in values. The const literals (with their explanatory comments) stay
// the single source of truth; this just exposes them as overridable data. Keep this in sync with the consts.
func DefaultTuning() *Tuning {
	return &Tuning{
		NectarRegenPerTick:   nectarRegenPerTick,
		MaxNectar:            maxNectar,
		HostRegenPerTick:     hostRegenPerTick,
		HostBreedCost:        hostBreedCost,
		MaxHostCapacity:      maxHostCapacity,
		DroughtFoodRegenMult: droughtFoodRegenMult,

		MaxLitter:          maxLitter,
		LitterRegenPerTick: litterRegenPerTick,

		SpawnSatiation:         spawnSatiation,
		StarvationDeathSecs:    starvationDeathSecs,
		StarvationCullFrac:     starvationCullFrac,
		PredatorBreedSatiation: predatorBreedSatiation,
		DirectorIntervalTicks:  directorIntervalTicks,
		DroughtDays:            droughtDays,

		NestHatchCount:   entities.NestHatchCount,
		NestBroodCap:     entities.NestBroodCap,
		NestHatchCost:    entities.NestHatchCost,
		NestFoundingSize: entities.NestFoundingSize,
		NestFoundDistMin: nestFoundDistMin,
		NestFoundDistMax: nestFoundDistMax,
	}
}

// LoadTuning reads data/ecology_tuning.json over the defaults (absent file → pure defaults; missing keys
// keep their default). A parse error logs + falls back to clean defaults.
func LoadTuning(path string, logger runtime.Logger) *Tuning {
	t := DefaultTuning()
	data, err := os.ReadFile(path)
	if err != nil {
		return t // absent → defaults (the byte-identical baseline)
	}
	if err := json.Unmarshal(data, t); err != nil {
		logger.Warn("ecology_tuning.json parse error (using defaults): %v", err)
		return DefaultTuning()
	}
	logger.Info("Loaded ecology tuning overrides from %s", path)
	return t
}
