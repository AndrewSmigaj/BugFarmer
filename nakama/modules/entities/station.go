package entities

import "fmt"

// StationState is a player-fillable material processor (compost bin is the first instance;
// feed troughs / bait baskets later). The player deposits accepted items via a small menu;
// Fill rises (visible meter); the contents act as a PROVIDER other systems consume — e.g.
// flies feed/breed at a non-empty compost bin, draining its fill through the same
// consumption path as rotten fruit. Defined per-entity in world.station (data-driven).
type StationState struct {
	Key      string // "station_<gx>_<gy>" — stable cell key (also the FoodID in events)
	EntityID string // Entity type id ("compost_bin") for def lookups
	GridX    int
	GridY    int

	// MATERIAL PROCESSOR: deposits land in the INPUT hopper; every process_ticks one input
	// unit converts into one unit of OUTPUT (Fill — the compost, which is what bugs feed and
	// breed on, and what fertilizer will draw from later).
	InputCount      int // Raw deposited items awaiting processing
	ProcessProgress int // Ticks into converting the current input unit

	Fill     int     // PROCESSED units (compost) 0..capacity — the food provider
	FoodFrac float32 // Fractional food drained from the current unit (consumption accumulator)
}

// StationKey builds the stable cell key for a station at a global grid cell.
func StationKey(gx, gy int) string {
	return fmt.Sprintf("station_%d_%d", gx, gy)
}
