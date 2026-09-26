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
	EntityID        string // occupant type ("wasp_nest"/"bee_hive_wild"/hive boxes) — generic
	SpeciesID       string // the species this nest spawns ("wasp_common", "bee_honey")
	Brood           int    // banked deposits, clamped at BroodCap
	ResidentSwarmID string // the patrol this nest owns ("" = none)
	RehatchAtTick   int64  // armed when the resident dies with brood banked (0 = unarmed)

	// Bees (the yield the nest doc anticipated): each brood deposit also makes honey, up to
	// the hive occupant's world.hive.honey_cap. Harvested by hand (HiveHarvest) as honeycomb.
	// Display/inventory yield — never a bug-sim input, never hashed.
	Honey float32

	// Smoker suppression: while TickCount < SmokedUntilTick, BOTH defend entries (the passive
	// player-near-nest aggro and recallNestDefenders) are no-ops — the calm harvest window.
	// Server-only; the ABSENCE of defend legs replays identically on every client.
	SmokedUntilTick int64

	// Founded flips true the first time a resident is minted here. The RECOVERY path only
	// revives nests that once held a colony — a freshly-placed dormant hive box can be claimed
	// ONLY by a daughter-founding (bees must actually arrive; no colonies from nowhere).
	Founded bool
}

// Nest tuning (architecture_swarm_sync.md §14).
const (
	NestBroodCap      = 9    // banked hatch events (raised so a thriving colony grows faster)
	NestHatchCost     = 3    // brood consumed per hatch
	NestHatchCount    = 3    // wasps added per hatch (+3: more wasps per cycle — the "more wasps" tuning)
	NestRehatchDelay  = 1200 // 2 min from resident death to re-hatch
	NestRecoveryDelay = 3000 // 5 min: a brood-exhausted colony re-founds a fresh patrol IF prey is near
	NestFoundingSize  = 4    // the initial resident patrol
	NestDefendRadius  = 5.0  // players this close to the nest aggro the resident
	NestDefendRelease = 10.0 // hysteresis: defending ends beyond this
	NestDefendTicks   = 300  // or after 30s
	NestDepositRange  = 2.0  // arrival distance for a brood deposit
	NestHomingTimeout = 600  // a homing trip that takes >60s drops the brood
)
