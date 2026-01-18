package entities

// CropState tracks a planted crop's current state
type CropState struct {
	PlantID           string
	PlantType         string // "tomato", "corn", "wheat"
	GridX, GridY      int
	Stage             int   // 0=seed, 1=sprout, 2=young, 3=mature
	HP                int   // 100 max, damaged by pests
	Water             int   // Cumulative hydration score (drives growth)
	WateringsToday    int   // Reset each day (for max_daily_waterings cap)
	Flags             uint8 // fertilized, etc.
	HarvestsRemaining int   // Multi-harvest crops
	PlantedTick       int64
}

// CropDef defines a crop type's growth and harvest properties
type CropDef struct {
	CropType          string  `json:"crop_type"`
	GrowthStages      int     `json:"growth_stages"`
	WateringsPerStage int     `json:"waterings_per_stage"`
	MaxDailyWaterings int     `json:"max_daily_waterings"`
	HarvestItem       string  `json:"harvest_item"`
	HarvestCountMin   int     `json:"harvest_count_min"`
	HarvestCountMax   int     `json:"harvest_count_max"`
	SeedDropChance    float32 `json:"seed_drop_chance"`
	MultiHarvest      bool    `json:"multi_harvest"`
	MaxHarvests       int     `json:"max_harvests"`
	RegrowTicks       int     `json:"regrow_ticks"`
}
