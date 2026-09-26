package entities

// BroodState is the VISIBLE nursery at one non-predator breeding source — a compost bin, a milkweed,
// or a transient maggot pile on rotten ground-fruit. Flies/butterflies LAY eggs here (the reproduceSwarm
// redirect) instead of growing instantly; the brood MATURES (eggs -> maggots) and HATCHES real bugs on a
// slow clock via growSwarm / spawnSwarmAt -> SWARM_REPRODUCED.
//
// Server-only SOFT STATE: never hashed, never in the late-join snapshot, resets on restart — the exact
// NestState / HostPlantState contract. The population cap applies at HATCH time (eggs are not bugs, so a
// brood at the cap simply HOLDS its maggots, like a nest banks brood). Keyed by "gx,gy" in
// WorldState.BroodStates. Wasp nests keep their own NestState.Brood economy; this is the non-predator
// sources only (fly_common, butterfly_meadow).
type BroodState struct {
	GridX, GridY int
	SpeciesID    string // the species this brood produces ("fly_common", "butterfly_meadow")

	Eggs          int // freshly laid, not yet matured
	Maggots       int // matured to LARVA; awaiting the next stage (pupa) or a hatch slot (held here at the cap)
	Pupae         int // SOURCE broods of a pupating species only (egg->larva->PUPA->adult); nests never populate this
	StageProgress int // ticks accumulated toward maturing the next stage transition

	SourceKind string // "station" | "host_plant" | "ground_pile" — drives the source-gone sweep + client visual
	SourceID   string // station key / "" for host_plant (cell-keyed) / ground-item id for a pile
	CapEggs    int    // max Eggs+Maggots held (food-scaled for a ground pile, default for compost/milkweed)
}

// Brood tuning — a slow, visible nursery. These reshape the population CURVE (not the totals); tune
// against the repro_test population graph so steady-state fly numbers match the pre-brood behaviour.
const (
	// Owner: breeding must be SLOW + visible — "over hours in game or even a day or two", never seconds
	// (seconds = always-empty nests). At 10Hz, DayLengthTicks=8400 (1 game-day), so 1 game-hour = 350 ticks.
	// 350 = ~1 game-hour to mature ONE egg -> maggot; a full clutch (CapEggs) develops over several game-hours
	// to ~a day, and a brood always has developing eggs to look in on. (Was 100 = ~10s, the "hatch instantly"
	// problem.) This reshapes the population CURVE, not the target totals — re-tune the band in Phase 3.
	BroodEggMatureTicks = 350 // TOTAL egg->adult dev budget in ticks (~1 game-hour at 10Hz); processBroods splits it across the stage transitions (2 or 3), so total dev time is stage-count-independent
	BroodHatchCount     = 2   // bugs hatched per hatch event
	BroodDefaultCapEggs = 12  // nursery capacity for compost/milkweed (a ground pile scales by food)
)
