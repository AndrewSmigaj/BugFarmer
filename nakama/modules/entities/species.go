package entities

import (
	"encoding/json"
	"fmt"
	"os"
)

// BugSpecies defines all properties for a bug type.
// SpriteID is a lookup key - client loads sprite sheets with all directions/animations.
type BugSpecies struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Category    string `json:"category"` // "swarm", "individual", "boss"

	// Movement
	BaseSpeed        float32 `json:"base_speed"`
	WanderRadius     float32 `json:"wander_radius"`
	WanderChangeRate float32 `json:"wander_change_rate"` // Chance per tick to change direction (0.0-1.0)

	// Vision-based resource seeking (server-side swarm AI)
	VisionRange        float32             `json:"vision_range"`
	AttractionsByPhase map[string][]string `json:"attractions_by_phase"` // phase → resource IDs
	AttractionStrength float32             `json:"attraction_strength"`
	ForageChance       float32             `json:"forage_chance"`         // Chance a behavior chunk is FORAGE vs wander (0 = always forage)
	ForageModeMinTicks int                 `json:"forage_mode_min_ticks"` // Behavior-chunk duration range (default 300-500 = 30-50s)
	ForageModeMaxTicks int                 `json:"forage_mode_max_ticks"`
	ConsumeRate        float32             `json:"consume_rate"` // Food drained per bug per second at a source (default 0.5)

	// Lifecycle parameters
	FeedAmount         float32 `json:"feed_amount"`          // Satiation per feeding event
	BreedAmount        float32 `json:"breed_amount"`         // Reproduction progress per breeding event
	SatiationDecayRate float32 `json:"satiation_decay_rate"` // Per second in idle

	// Swarm-specific (category=swarm only)
	MinSwarmSize   int     `json:"min_swarm_size"`
	MaxSwarmSize   int     `json:"max_swarm_size"`
	SwarmRadius    float32 `json:"swarm_radius"`
	MergeRadius    float32 `json:"merge_radius"`
	SplitThreshold int     `json:"split_threshold"`
	SplitChance    float32 `json:"split_chance"`

	// Player Reaction AI
	PlayerReaction string  `json:"player_reaction"` // "ignore", "flee", "attack", "curious"
	ReactionRadius float32 `json:"reaction_radius"`
	FleeSpeedMult  float32 `json:"flee_speed_mult"`
	AttackDamage   int     `json:"attack_damage"`
	AttackCooldown float32 `json:"attack_cooldown"`

	// Catching Requirements
	NetSize            string             `json:"net_size"` // "small", "medium", "large", "trap_only"
	CatchCondition     string             `json:"catch_condition"`
	ConditionThreshold float32            `json:"condition_threshold"`
	ConditionDecay     float32            `json:"condition_decay"`
	ConditionTools     map[string]float32 `json:"condition_tools"`

	// Combat: per-bug max HP (weapons subtract their damage; 0/absent = 1).
	MaxHP       int            `json:"max_hp"`
	DamageTools map[string]int `json:"damage_tools"`

	// Economy
	SellPrice int `json:"sell_price"`

	// Reproduction
	BreedingPlants    []string `json:"breeding_plants"`
	EggCountMin       int      `json:"egg_count_min"`
	EggCountMax       int      `json:"egg_count_max"`
	HatchTime         float32  `json:"hatch_time"`
	ReproduceCooldown float32  `json:"reproduce_cooldown"`

	// Natural death (per-bug aging). LifespanSecs <= 0 = immortal. At birth each bug gets a
	// DeathTick = now + lifespan ± LifespanSpreadSecs (so a cohort doesn't all die at once). On
	// death it drops CarcassItem (a dead_<species> food item — detritivore food, not loot).
	LifespanSecs       float32 `json:"lifespan_secs"`
	LifespanSpreadSecs float32 `json:"lifespan_spread_secs"`
	CarcassItem        string  `json:"carcass_item"`

	// Detritivore: while feeding on a carcass, periodically deposit compost INPUT into the nearest
	// compost bin (the existing station pipeline converts input→compost→fly food). Closes the
	// death→carcass→compost→fly loop. millipede=true; others false.
	ProducesCompost bool `json:"produces_compost"`

	// Sprites - lookup keys for client to load sprite sheets
	SpriteID    string `json:"sprite_id"`
	EggSpriteID string `json:"egg_sprite_id"`

	// Kill drops: per-species loot table (replaces the old hardcoded bug_parts).
	// Empty = drops nothing.
	KillDrops []KillDrop `json:"kill_drops"`

	// Prey-side predation fields (set on species that GET hunted)
	PredatorFleeRadius    float32 `json:"predator_flee_radius"`     // flee when a predator swarm is this close
	PredatorFleeSpeedMult float32 `json:"predator_flee_speed_mult"` // flee-from-predator speed (decoupled from the player flee mult)
	// RELOCATE: instead of the short directly-away flee, a swarm has RelocateChance (per flee think) to make a
	// long BREAK-CONTACT jump of RelocateDistance (away from predator + a random angle), to actually escape a
	// hunter's vision rather than be out-chased. NOT all swarms do it (chance) — some stay and get eaten (the
	// crash). RelocateCooldownTicks gates re-jumping. 0/absent = off (plain flee). Determinism-safe (state.Rng).
	RelocateChance        float32 `json:"relocate_chance"`
	RelocateDistance      float32 `json:"relocate_distance"`
	RelocateCooldownTicks int64   `json:"relocate_cooldown_ticks"`

	// Movement trait: this species' swarm centers AND client bug visuals skip the
	// OCCUPANT collision branch only (fences, walls, houses — there are no roofs yet).
	// The zone edge still blocks; ground never blocks bugs (water stops people only).
	// Named so nobody "fixes" flies, which also fly but must respect pens. Applies
	// identically at BOTH collision sites (server leg clamp + client per-bug
	// collision) — per-bug positions are hash state.
	FliesOverFences bool `json:"flies_over_fences"`

	// Client movement class key ("brownian", "gliding", "darting", "crawling").
	// Hash-bearing same-build data (the client reads the published species.json).
	MovementStyle string `json:"movement_style"`

	// Gentle-until-provoked (bees): with this set, checkBugAttacks stings ONLY while the
	// swarm is in the "defending" phase (nest recalled / player loitering at the hive).
	// Without it, any attack_damage>0 species stings anyone in contact range (wasps).
	StingsOnlyDefending bool `json:"stings_only_defending"`

	// AttackIsSting classifies the attack for gear: a sting_immune body piece (the bee suit)
	// fully negates STINGS (bees, wasps) but not bites (centipedes chew through cloth).
	AttackIsSting bool `json:"attack_is_sting"`

	// Predator configuration. The NIL POINTER is the predator gate — non-predators
	// never enter the predation branch.
	Predation *PredationConfig `json:"predation"`
}

// KillDrop is one entry of a species' kill loot table.
type KillDrop struct {
	Item     string  `json:"item"`
	CountMin int     `json:"count_min"`
	CountMax int     `json:"count_max"`
	Chance   float32 `json:"chance"`
}

// PredationConfig holds the predator-only knobs (architecture_swarm_sync.md §14).
// All server-only state machinery; outputs ride the existing event vocabulary.
type PredationConfig struct {
	Prey                   []string `json:"prey"`                     // species ids this predator hunts
	HomeRange              float32  `json:"home_range"`               // hunt/wander tether radius around the nest/HomePos
	StrikeRadius           float32  `json:"strike_radius"`            // center-to-center kill range
	StrikeCooldownTicks    int64    `json:"strike_cooldown_ticks"`    // min ticks between kills (the anti-snowball knob)
	KillsPerStrike         int      `json:"kills_per_strike"`         // prey bugs killed per strike
	FeedPerKill            float32  `json:"feed_per_kill"`            // satiation gained per kill
	FeedPauseTicks         int64    `json:"feed_pause_ticks"`         // ticks the predator PARKS on a kill (the feeding dwell; 0 = off). Keep <= strike_cooldown_ticks to stay rate-neutral.
	HuntSpeedMult          float32  `json:"hunt_speed_mult"`          // leg speed multiplier while hunting
	DepositSatiation       float32  `json:"deposit_satiation"`        // satiation set after a nest deposit (rest pacing)
	HuntSatiationThreshold float32  `json:"hunt_satiation_threshold"` // hunts only below this satiation
	NestOccupant           string   `json:"nest_occupant"`            // occupant id of this species' nest ("" = nestless)
	// Additional occupant ids that also serve as this species' nests — the PLAYER-PLACED hive
	// boxes (bees: beehive_basic..deluxe). Unlike the primary NestOccupant (wild hives, which
	// auto-found a resident when their chunk loads), extras register DORMANT: no free colony —
	// a daughter-founding or recovering colony must CLAIM the box (how a player's apiary
	// comes alive).
	NestOccupantsExtra []string `json:"nest_occupants_extra"`
}

// LoadSpecies reads species definitions from JSON config
func LoadSpecies(path string) (map[string]*BugSpecies, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read species config: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse species config: %w", err)
	}

	species := make(map[string]*BugSpecies)
	for id, specData := range raw {
		var spec BugSpecies
		if err := json.Unmarshal(specData, &spec); err != nil {
			return nil, fmt.Errorf("failed to parse species %s: %w", id, err)
		}
		spec.ID = id
		species[id] = &spec
	}

	return species, nil
}
