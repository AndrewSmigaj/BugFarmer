package entities

// ForagePoolState is a depletable FEEDING food pool on a plant occupant (flower nectar). Bugs that feed
// here drain its Nectar; it regenerates slowly toward the cap. When grazed to 0 it stops being a food
// source (FindNearbyFood skips it) until it regrows — so an over-large population exhausts its food and
// STARVES back (the boom-bust). This is the FEEDING analogue of HostPlantState (which is BREEDING
// capacity on milkweed); a plant can have either or both.
//
// Server-only soft state: never hashed, never in the late-join snapshot, resets on restart — the same
// contract as HostPlantState/StationState. Keyed by "gx,gy" in WorldState.ForagePools. The regen rate
// is the master dial for oscillation amplitude/period (slow regen = bigger, slower boom-bust).
type ForagePoolState struct {
	EntityID     string
	GridX, GridY int
	Nectar       float32 // 0..cap; feeding drains it, regen refills it
}
