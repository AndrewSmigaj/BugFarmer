package entities

// NestState tracks one wasp-nest occupant's brood economy (the fruit-tree pattern:
// in-memory, scanned from chunk occupants at chunk load, no persistence — a destroyed
// nest resurrects on server restart like every broken occupant; documented in §14).
//
// Brood economics (the spec line that bounds three exploits at once): deposits bank
// brood (clamped); hatches consume 3 for +2 wasps into the resident; a dead resident
// RE-HATCHES after a delay at a size equal to the brood consumed — so ~3 consecutive
// culls exhaust a nest into readable dormancy, culling is bounded attrition (not a
// treadmill), and catch-farming a nest can't money-pump.
type NestState struct {
	GridX, GridY    int
	EntityID        string // occupant type ("wasp_nest") — generic for future hives
	SpeciesID       string // the species this nest spawns ("wasp_common")
	Brood           int    // banked deposits, clamped at BroodCap
	ResidentSwarmID string // the patrol this nest owns ("" = none)
	RehatchAtTick   int64  // armed when the resident dies with brood banked (0 = unarmed)
}

// Nest tuning (architecture_swarm_sync.md §14).
const (
	NestBroodCap      = 6    // two banked hatch events — no chain-hatching after a cull
	NestHatchCost     = 3    // brood consumed per hatch
	NestHatchCount    = 2    // wasps added per hatch (+2 flat: countable growth)
	NestRehatchDelay  = 1200 // 2 min from resident death to re-hatch
	NestFoundingSize  = 4    // the initial resident patrol
	NestDefendRadius  = 5.0  // players this close to the nest aggro the resident
	NestDefendRelease = 10.0 // hysteresis: defending ends beyond this
	NestDefendTicks   = 300  // or after 30s
	NestDepositRange  = 2.0  // arrival distance for a brood deposit
	NestHomingTimeout = 600  // a homing trip that takes >60s drops the brood
)
