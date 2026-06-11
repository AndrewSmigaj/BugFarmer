package entities

// FruitTreeState tracks a fruit tree's current state.
//
// The lifecycle (architecture_farming.md "Fruit Trees"):
//
//	DORMANT -(3 waterings, max 1/day manual; rain adds 1 free)-> tank full
//	  -> BATCH trigger (only when the tree is EMPTY: tank consumed, Pending = MaxFruit)
//	  -> GROWING (one fruit per fruit_grow_ticks; Pending counts DOWN)
//	  -> FRUITING (fruit sits on the canopy, never rots there; hands-pick or knock down)
//	  -> ripe fruit falls STAGGERED during the evening window, >= 500 ticks apart
//	  -> ground fruit rots in fruit_rot_ticks -> fly food.
type FruitTreeState struct {
	TreeID          string
	EntityID        string // Entity type id ("tree_apple") for def lookups (fruit_rot_ticks etc.)
	GridX, GridY    int
	FruitCount      int   // Current fruit on the canopy
	MaxFruit        int   // Batch size (a full tank buys exactly one full batch)
	GrowthProgress  int   // Ticks toward the next fruit while a batch is growing
	PendingGrowth   int   // Fruits left to grow in the current batch (COUNTDOWN, never recomputed)
	DropTimer       int   // Ripeness clock; resets ONLY on the FruitCount 0->1 growth transition
	LastFallTick    int64 // Raw tick of the last evening fall (stagger spacing)
	LastHarvestTick int64 // Last time a player picked fruit
	WaterLevel      int   // Watering tank 0..3
	LastWaterDay    int64 // Day index of the last MANUAL watering (1/day; -1 = never)
}
