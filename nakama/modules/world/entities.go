package world

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"bugfarmer/entities"
)

// EntityDef is the unified definition for all game entities.
// Three types:
// - items (inventory-only): resources, tools, consumables - World is nil
// - occupants (world-only): trees, rocks, natural objects - only World populated
// - placeables (both): blocks, furniture, structures - both inventory props and World
type EntityDef struct {
	ID       string `json:"-"` // Set from map key
	Name     string `json:"name"`
	Category string `json:"category"`

	// Inventory properties (items and placeables only)
	Stackable bool `json:"stackable,omitempty"`
	MaxStack  int  `json:"max_stack,omitempty"`
	SellPrice int  `json:"sell_price,omitempty"`
	BuyPrice  int  `json:"buy_price,omitempty"`

	// Tool properties (category = "tool")
	ToolType         string         `json:"tool_type,omitempty"`
	ToolTier         int            `json:"tool_tier,omitempty"`
	Reach            float32        `json:"reach,omitempty"`
	MiningSpeed      float32        `json:"mining_speed,omitempty"`
	Durability       int            `json:"durability,omitempty"`
	CooldownTicks    int            `json:"cooldown_ticks,omitempty"`    // Ticks between uses (tools incl. weapons)
	MetadataDefaults map[string]int `json:"metadata_defaults,omitempty"` // Initial metadata (watering can capacity)

	// NET sweep properties (top-level — nets have exactly one move with their own cap
	// semantics and rate-limit slot; they migrate to Moves only if they grow a secondary).
	// The catch AREA is a swept sector (arc_degrees x reach) detected client-side; the
	// server validates alive bug IDs + player->click reach + caps only.
	ArcDegrees float32 `json:"arc_degrees,omitempty"` // Total swept arc
	SwingTime  float32 `json:"swing_time,omitempty"`  // Seconds (animation + client feel)
	CatchCap   int     `json:"catch_cap,omitempty"`   // Per-swing catch cap (nets)

	// WEAPON movesets (swords, spears, axes' combat swing; future whips): per-MOVE combat
	// stats keyed by the input slot ("primary" = left click, "secondary" = right click).
	// The move's kind maps to a client animation profile + hit geometry; the server
	// validates only move-existence + reach + caps (it holds no positions/shapes), so new
	// kinds are data + client code only.
	Moves map[string]*MoveDef `json:"moves,omitempty"`

	// Seed properties
	PlacesCrop string `json:"places_crop,omitempty"` // Crop type this seed plants

	// Armor properties (category = "armor"): which equipment slot the piece
	// occupies (head/body/arms/legs/feet/accessory). Cosmetic-only for now —
	// defense math is a planned follow-up.
	ArmorSlot string `json:"armor_slot,omitempty"`

	// StingImmune (the bee suit): worn in the BODY slot, fully negates sting-class bug
	// attacks (species with attack_is_sting). The first armor damage knob; bites ignore it.
	StingImmune bool `json:"sting_immune,omitempty"`

	// Backpack properties (category = "backpack", armor_slot = "backpack"): how many extra
	// item-inventory slots wearing it unlocks.
	SlotBonus int `json:"slot_bonus,omitempty"`

	// Bug-food value when this item lies on the ground (carrion: bug_parts etc.).
	// > 0 makes a ground drop EDIBLE: it registers in the deterministic food registry
	// (ITEM_ROTTED at spawn, FOOD_CONSUMED(0) at expiry — both hash-bearing).
	FoodValue int `json:"food_value,omitempty"`

	// Consumable/subdual-tool properties (§C): Effect names the condition_tools key it applies
	// ("calm"; later "chill"/"stun"); EffectPower scales the species fill (the tool-tier knob —
	// absent/0 reads as 1.0).
	Effect      string  `json:"effect,omitempty"`
	EffectPower float32 `json:"effect_power,omitempty"`

	// Item classes/tags: "clothing", "food", "material", "metal", "tool", "seed", "book",
	// "drink"… A filtered container only accepts items carrying its tag; tags also seed future
	// inventory sort/filter. Pure data — no behavior beyond the filter check.
	Tags []string `json:"tags,omitempty"`

	// World data (nil for inventory-only items)
	World *WorldData `json:"world,omitempty"`

	// Entity type set during loading: "item", "occupant", or "placeable"
	EntityType string `json:"-"`
}

// MoveDef is one weapon move (an input slot's attack): stats the server validates with
// plus the animation kind the client renders with.
type MoveDef struct {
	Kind          string  `json:"kind"`           // "swing" | "stab" | "sweep" (client anim + geometry)
	Damage        int     `json:"damage"`         // HP per hit (vs species max_hp); <=0 -> 1
	ArcDegrees    float32 `json:"arc_degrees"`    // Client hit geometry only (server has no positions)
	Reach         float32 `json:"reach"`          // Server-validated: player->click <= reach+0.5
	SwingTime     float32 `json:"swing_time"`     // Seconds (animation + client feel)
	MaxTargets    int     `json:"max_targets"`    // Per-SWING hit cap; <=0 -> 1
	CooldownTicks int     `json:"cooldown_ticks"` // Vs the shared LastToolTick; <=0 -> 3
}

// GetMove resolves a weapon move by input-slot name. NIL-RECEIVER-SAFE by design: the
// melee gate is exactly `weapon.GetMove(name) != nil`, and `weapon` is nil for a bare
// hand ("") or any id absent from Entities (EquipTool relays arbitrary client strings).
func (e *EntityDef) GetMove(name string) *MoveDef {
	if e == nil || e.Moves == nil {
		return nil
	}
	return e.Moves[name]
}

// WorldData describes how an entity appears/behaves in the world.
type WorldData struct {
	Footprint     []int  `json:"footprint"` // [width, height] in grid cells
	Pivot         string `json:"pivot"`     // "bc" (bottom-center), "c" (center)
	BlocksPlayers bool   `json:"blocks_players,omitempty"`
	BlocksBugs    bool   `json:"blocks_bugs,omitempty"`
	Gnawable      bool   `json:"gnawable,omitempty"` // centipedes chew through it (wood fences/gates)

	// Rotation
	Rotatable  bool `json:"rotatable,omitempty"`
	Directions int  `json:"directions,omitempty"` // 2 or 4

	// Interaction
	Interactable    bool   `json:"interactable,omitempty"`
	InteractionType string `json:"interaction_type,omitempty"` // "craft", "storage", "door", "sleep", "sign", "well", "beehive", "shop"

	// Breaking (nil = unbreakable)
	Breakable *BreakableData `json:"breakable,omitempty"`

	// Fruit tree properties
	FruitType      string `json:"fruit_type,omitempty"`       // "apple", "orange"
	MaxFruit       int    `json:"max_fruit,omitempty"`        // Maximum fruit capacity
	FruitGrowTicks int    `json:"fruit_grow_ticks,omitempty"` // Ticks per fruit growth
	FruitDropTicks int    `json:"fruit_drop_ticks,omitempty"` // Ticks until fruit drops
	FruitRotTicks  int    `json:"fruit_rot_ticks,omitempty"`  // Ticks for dropped fruit to rot (default 16800 = 2 game-days)

	// Host-plant breeding (milkweed): butterflies lay eggs here, depleting per breed (it regrows). A
	// HostPlantState tracks capacity per cell; FindNearbyFood treats it as a depletable breeding source
	// while capacity > 0 (and skips it when grazed out). Flowers are NOT host plants — just nectar.
	HostPlant bool `json:"host_plant,omitempty"`

	// Nectar (flowers): a depletable FEEDING pool. Bugs that feed here drain it; it regrows slowly and is
	// skipped when grazed out — so an over-large population exhausts its food and starves back (boom-bust).
	// A ForagePoolState tracks nectar per cell. The feeding analogue of host_plant.
	Nectar bool `json:"nectar,omitempty"`

	// Hive properties (bee nests: the wild hive + the placeable hive-box tiers; nil = not a
	// hive). honey_cap = combs the hive stores; honey_mult scales accrual per brood deposit
	// (deluxe boxes make honey faster). Display/inventory yield knobs — never sim inputs.
	Hive *HiveData `json:"hive,omitempty"`

	// Station properties (player-fillable material processors — compost bin first; nil = not a station)
	Station *StationData `json:"station,omitempty"`

	// Container properties (item storage — chests, dressers, racks; nil = not a container).
	// Craft stations are NOT declared here — they're detected by being a key in
	// RecipesByStation, and their output-grid size is a code constant (§ craft station).
	// craft_slots is their ONE data knob: how many recipes the station runs AT ONCE
	// (parallel processors; absent/0 = 1). Slow processors (furnace/forge/sawmill…)
	// get >1; manual benches stay at 1.
	CraftSlots int            `json:"craft_slots,omitempty"`
	Container  *ContainerData `json:"container,omitempty"`

	// Shop properties (NPC vendor; nil = not a vendor). interaction_type:"shop" opens its panel.
	Shop *ShopData `json:"shop,omitempty"`
}

// ShopData makes an occupant an NPC vendor. Kind "items" trades ItemSlots; kind "bugs" trades live
// bugs (BugSlots, priced by species.sell_price) plus dead-bug items. Sells = what the NPC offers, each
// with its asking Price (coins the player pays). Buys = item ids/tags the NPC purchases at the item's
// sell_price; the bug dealer additionally buys ANY live species and any dead_<bug> item. Purely
// per-player transaction state — never in the deterministic sim hash.
type ShopData struct {
	Kind    string      `json:"kind"`              // "items" | "bugs"
	Sells   []ShopEntry `json:"sells,omitempty"`   // finished goods the NPC sells (player buys)
	Buys    []string    `json:"buys,omitempty"`    // item ids/tags the NPC buys (price = entity sell_price)
	Recipes []ShopEntry `json:"recipes,omitempty"` // individual recipe ids the NPC teaches (id = recipe id)
	Books   []ShopEntry `json:"books,omitempty"`   // recipe-book entries (id = a recipe `collection`; learns the whole set)
}

// ShopEntry is one offered good: an item or species id and the coins to buy it.
type ShopEntry struct {
	ID    string `json:"id"`
	Price int64  `json:"price"`
}

// ContainerData makes a placeable an item store: Slots cells, optionally restricted to items
// carrying Filter (a tag). interaction_type:"storage" opens its panel. Non-deterministic
// display/inventory state — never in the sim hash.
type ContainerData struct {
	Slots  int    `json:"slots"`            // number of storage cells
	Filter string `json:"filter,omitempty"` // tag a deposited item must carry; "" = accept anything
}

// StationData describes a player-fillable station: deposit accepted items via a menu, the fill
// meter rises, and the contents act as a provider other systems consume (e.g. flies feed/breed
// from a compost bin, draining its fill).
type StationData struct {
	Accepts     []string `json:"accepts"`                 // Item types depositable here
	Capacity    int      `json:"capacity"`                // Max units of fill
	FoodPerUnit int      `json:"food_per_unit,omitempty"` // Food value each unit provides to bugs
	Providers   []string `json:"providers,omitempty"`     // "food", "breeding"
	ProcessTicks int     `json:"process_ticks,omitempty"` // Reserved: fresh->processed conversion time
}

// HiveData is a bee nest's honey-yield tuning (world.hive on the wild hive + hive boxes).
type HiveData struct {
	HoneyCap  float32 `json:"honey_cap"`            // combs the hive holds (harvest yield cap)
	HoneyMult float32 `json:"honey_mult,omitempty"` // accrual multiplier per brood deposit (0 = 1.0)
}

// BreakableData describes how something can be broken/harvested.
type BreakableData struct {
	HP               int         `json:"hp"`
	RequiredToolType string      `json:"required_tool_type,omitempty"`
	RequiredToolTier int         `json:"required_tool_tier,omitempty"`
	Drops            []DropEntry `json:"drops,omitempty"`
}

// DropEntry describes a single drop from breaking something. Count is a fixed amount; CountMin/CountMax give
// a random RANGE (rolled on the server via state.Rng, so all clients agree) — mirrors HarvestCountMin/Max.
// When the range is unset it defaults to the fixed Count (see load-defaults), so old data keeps working.
type DropEntry struct {
	ItemID   string  `json:"item_id"`
	Count    int     `json:"count"`
	CountMin int     `json:"count_min,omitempty"`
	CountMax int     `json:"count_max,omitempty"`
	Chance   float32 `json:"chance"` // 0.0 to 1.0
}

// GetFootprint returns (width, height) for the given direction.
// Dir 0 (down) and 3 (up): use W x H as defined
// Dir 1 (left) and 2 (right): swap to H x W
func (w *WorldData) GetFootprint(dir int) (int, int) {
	if w == nil || len(w.Footprint) < 2 {
		return 1, 1
	}
	width, height := w.Footprint[0], w.Footprint[1]
	if width == 0 {
		width = 1
	}
	if height == 0 {
		height = 1
	}
	if dir == 1 || dir == 2 {
		return height, width
	}
	return width, height
}

// CanBreakWith checks if this can be broken with the given tool.
func (b *BreakableData) CanBreakWith(toolType string, toolTier int) bool {
	if b == nil {
		return false
	}
	if b.RequiredToolType != "" && b.RequiredToolType != toolType {
		return false
	}
	return toolTier >= b.RequiredToolTier
}

// IsPlaceable returns true if this entity can be placed by players.
func (e *EntityDef) IsPlaceable() bool {
	return e.EntityType == "placeable"
}

// IsItem returns true if this entity can exist in inventory.
func (e *EntityDef) IsItem() bool {
	return e.EntityType == "item" || e.EntityType == "placeable"
}

// HasTag reports whether this entity carries the given item class/tag (container filtering).
func (e *EntityDef) HasTag(tag string) bool {
	if e == nil {
		return false
	}
	for _, t := range e.Tags {
		if t == tag {
			return true
		}
	}
	return false
}

// HasWorldPresence returns true if this entity can exist in the world.
func (e *EntityDef) HasWorldPresence() bool {
	return e.World != nil
}

// GetFootprint is a convenience method on EntityDef.
func (e *EntityDef) GetFootprint(dir int) (int, int) {
	if e.World == nil {
		return 1, 1
	}
	return e.World.GetFootprint(dir)
}

// CanBreakWith is a convenience method on EntityDef.
func (e *EntityDef) CanBreakWith(toolType string, toolTier int) bool {
	if e.World == nil || e.World.Breakable == nil {
		return false
	}
	return e.World.Breakable.CanBreakWith(toolType, toolTier)
}

// IsBreakable returns true if this entity can be broken.
func (e *EntityDef) IsBreakable() bool {
	return e.World != nil && e.World.Breakable != nil
}

// GetHP returns the HP for breakable entities, 0 otherwise.
func (e *EntityDef) GetHP() int {
	if e.World == nil || e.World.Breakable == nil {
		return 0
	}
	return e.World.Breakable.HP
}

// GetDrops returns the drop list for breakable entities, nil otherwise.
func (e *EntityDef) GetDrops() []DropEntry {
	if e.World == nil || e.World.Breakable == nil {
		return nil
	}
	return e.World.Breakable.Drops
}

// LoadAllEntities loads entities from all three JSON files into a single map.
// Returns the entity map and a list of any warnings encountered.
func LoadAllEntities(dataPath string) (map[string]*EntityDef, []string, error) {
	entities := make(map[string]*EntityDef)
	var warnings []string

	// Load items (inventory-only)
	itemsPath := filepath.Join(dataPath, "entities", "items.json")
	if w, err := loadEntityFile(itemsPath, "item", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load items: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	// Load occupants (world-only)
	occupantsPath := filepath.Join(dataPath, "entities", "occupants.json")
	if w, err := loadEntityFile(occupantsPath, "occupant", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load occupants: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	// Load placeables (both inventory and world)
	placeablesPath := filepath.Join(dataPath, "entities", "placeables.json")
	if w, err := loadEntityFile(placeablesPath, "placeable", entities); err != nil {
		return nil, nil, fmt.Errorf("failed to load placeables: %w", err)
	} else {
		warnings = append(warnings, w...)
	}

	return entities, warnings, nil
}

// loadEntityFile loads a single JSON file and adds entities to the map.
// Returns warnings for duplicate IDs.
func loadEntityFile(path, entityType string, entities map[string]*EntityDef) ([]string, error) {
	var warnings []string

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read %s: %w", path, err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse %s: %w", path, err)
	}

	for id, entData := range raw {
		// Skip comment fields
		if id == "_comment" {
			continue
		}

		// Check for duplicate IDs
		if existing, exists := entities[id]; exists {
			warnings = append(warnings, fmt.Sprintf(
				"duplicate entity ID '%s': %s overwrites %s",
				id, entityType, existing.EntityType,
			))
		}

		var ent EntityDef
		if err := json.Unmarshal(entData, &ent); err != nil {
			return warnings, fmt.Errorf("failed to parse entity %s: %w", id, err)
		}

		ent.ID = id
		ent.EntityType = entityType

		// Apply defaults
		applyDefaults(&ent)

		entities[id] = &ent
	}

	return warnings, nil
}

// applyDefaults sets sensible defaults for missing values.
func applyDefaults(e *EntityDef) {
	// Default stack size for stackables
	if e.Stackable && e.MaxStack == 0 {
		e.MaxStack = 99
	}

	// World data defaults
	if e.World != nil {
		// Ensure footprint has at least 2 elements
		if len(e.World.Footprint) < 2 {
			e.World.Footprint = []int{1, 1}
		}
		if e.World.Footprint[0] == 0 {
			e.World.Footprint[0] = 1
		}
		if e.World.Footprint[1] == 0 {
			e.World.Footprint[1] = 1
		}
		if e.World.Pivot == "" {
			e.World.Pivot = "bc"
		}
		if e.World.Rotatable && e.World.Directions == 0 {
			e.World.Directions = 4
		}

		// Breakable defaults
		if e.World.Breakable != nil {
			for i := range e.World.Breakable.Drops {
				d := &e.World.Breakable.Drops[i]
				if d.Count == 0 {
					d.Count = 1
				}
				if d.Chance == 0 {
					d.Chance = 1.0
				}
				// Count range defaults to the fixed Count (mirrors HarvestCountMin/Max at :480).
				if d.CountMin == 0 {
					d.CountMin = d.Count
				}
				if d.CountMax == 0 {
					d.CountMax = d.CountMin
				}
			}
		}
	}
}

// LoadCropDefs loads crop definitions from crops.json
func LoadCropDefs(basePath string) (map[string]*entities.CropDef, error) {
	crops := make(map[string]*entities.CropDef)

	path := filepath.Join(basePath, "entities", "crops.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read crops.json: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse crops.json: %w", err)
	}

	for id, cropData := range raw {
		if id == "_comment" {
			continue
		}

		var def entities.CropDef
		if err := json.Unmarshal(cropData, &def); err != nil {
			return nil, fmt.Errorf("failed to parse crop %s: %w", id, err)
		}

		// Apply defaults
		if def.GrowthStages == 0 {
			def.GrowthStages = 4
		}
		if def.WateringsPerStage == 0 {
			def.WateringsPerStage = 3
		}
		if def.MaxDailyWaterings == 0 {
			def.MaxDailyWaterings = 2
		}
		if def.HarvestCountMin == 0 {
			def.HarvestCountMin = 1
		}
		if def.HarvestCountMax == 0 {
			def.HarvestCountMax = def.HarvestCountMin
		}

		crops[id] = &def
	}

	return crops, nil
}

// LoadGroundRecipes loads shovel tile-placement recipes (placed material id -> ingredients) from
// ground_recipes.json. A COMPOSITE tile costs BOTH its materials' recipes (unioned in handleShovel);
// digging a tile drops the same ingredients. Pure data, zero code per recipe.
func LoadGroundRecipes(basePath string) (map[string][]entities.RecipeIO, error) {
	path := filepath.Join(basePath, "entities", "ground_recipes.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read ground_recipes.json: %w", err)
	}
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("failed to parse ground_recipes.json: %w", err)
	}
	out := make(map[string][]entities.RecipeIO)
	for id, v := range raw {
		if id == "_comment" {
			continue
		}
		var ings []entities.RecipeIO
		if err := json.Unmarshal(v, &ings); err != nil {
			return nil, fmt.Errorf("failed to parse ground recipe %s: %w", id, err)
		}
		out[id] = ings
	}
	return out, nil
}

// groundRecipeIngredients returns the merged ingredient list for placing/digging a ground id: the UNION
// (summed by item) of every material's recipe. A composite costs/drops BOTH materials; a solid, just one.
func (w *WorldState) groundRecipeIngredients(id string) []entities.RecipeIO {
	merged := map[string]int{}
	order := []string{}
	for _, mat := range CompositeMaterials(id) {
		for _, ing := range w.GroundRecipes[mat] {
			if _, seen := merged[ing.Item]; !seen {
				order = append(order, ing.Item)
			}
			merged[ing.Item] += ing.Count
		}
	}
	out := make([]entities.RecipeIO, 0, len(order))
	for _, it := range order {
		out = append(out, entities.RecipeIO{Item: it, Count: merged[it]})
	}
	return out
}

// groundShortfall returns "Need 2 stone, 1 plank" listing only the ingredients the player LACKS, or ""
// if they can afford all of them (so the shovel can surface a clear reason via the world-error toast).
func groundShortfall(player *PlayerState, ings []entities.RecipeIO) string {
	parts := []string{}
	for _, ing := range ings {
		if have := playerCount(player, ing.Item); have < ing.Count {
			parts = append(parts, fmt.Sprintf("%d %s", ing.Count-have, ing.Item))
		}
	}
	if len(parts) == 0 {
		return ""
	}
	return "Need " + strings.Join(parts, ", ")
}

// LoadRecipes loads crafting recipes from recipes.json into a by-id map AND a by-station index
// (the panel needs "every recipe craftable at station X"). Mirrors LoadCropDefs. The recipe table
// is pure data — zero code per recipe; publish_entities.py ships recipes.json by glob.
func LoadRecipes(basePath string) (map[string]*entities.RecipeDef, map[string][]*entities.RecipeDef, error) {
	recipes := make(map[string]*entities.RecipeDef)
	byStation := make(map[string][]*entities.RecipeDef)

	path := filepath.Join(basePath, "entities", "recipes.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to read recipes.json: %w", err)
	}

	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, nil, fmt.Errorf("failed to parse recipes.json: %w", err)
	}

	for id, recipeData := range raw {
		if id == "_comment" {
			continue
		}

		var def entities.RecipeDef
		if err := json.Unmarshal(recipeData, &def); err != nil {
			return nil, nil, fmt.Errorf("failed to parse recipe %s: %w", id, err)
		}
		def.ID = id

		// Defaults
		if def.Output.Count == 0 {
			def.Output.Count = 1
		}
		if def.ProcessTicks < 0 {
			def.ProcessTicks = 0
		}

		recipes[id] = &def
		byStation[def.Station] = append(byStation[def.Station], &def)
	}

	return recipes, byStation, nil
}
