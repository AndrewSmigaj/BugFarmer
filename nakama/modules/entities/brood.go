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
	Maggots       int // matured, awaiting a hatch slot (held here when at the population cap)
	StageProgress int // ticks accumulated toward maturing the next egg -> maggot

	SourceKind string // "station" | "host_plant" | "ground_pile" — drives the source-gone sweep + client visual
	SourceID   string // station key / "" for host_plant (cell-keyed) / ground-item id for a pile
	CapEggs    int    // max Eggs+Maggots held (food-scaled for a ground pile, default for compost/milkweed)
}

// Brood tuning — a slow, visible nursery. These reshape the population CURVE (not the totals); tune
// against the repro_test population graph so steady-state fly numbers match the pre-brood behaviour.
const (
	BroodEggMatureTicks = 100 // ticks to mature one egg -> maggot (~10s at 10Hz)
	BroodHatchCount     = 2   // bugs hatched per hatch event
	BroodDefaultCapEggs = 12  // nursery capacity for compost/milkweed (a ground pile scales by food)
)
