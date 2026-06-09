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

	// HP (for "weakened" condition)
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

	// Sprites - lookup keys for client to load sprite sheets
	SpriteID    string `json:"sprite_id"`
	EggSpriteID string `json:"egg_sprite_id"`
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
