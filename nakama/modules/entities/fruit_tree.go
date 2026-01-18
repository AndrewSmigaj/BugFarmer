package entities

// FruitTreeState tracks a fruit tree's current state
type FruitTreeState struct {
	TreeID          string
	GridX, GridY    int
	FruitCount      int   // Current fruit on tree
	MaxFruit        int   // Maximum fruit capacity
	GrowthProgress  int   // Ticks since last fruit grew
	DropTimer       int   // Ticks since fruit ripened (drops if too long)
	LastHarvestTick int64 // Last time player harvested
}
