package entities

// HostPlantState tracks a breeding host plant (milkweed) at a cell. Butterflies lay eggs on it,
// depleting Capacity per breed event; it regrows over time. Capacity 0 = grazed out (not a breeding
// source until it regrows). Server-only soft state (NOT hashed; resets on restart, like nests) — the
// butterfly's targeting is server-driven (SWARM_SET_TARGET legs) and births ride SWARM_REPRODUCED.
type HostPlantState struct {
	EntityID     string
	GridX, GridY int
	Capacity     float32 // 0..max; breeding drains it, regen refills it
}
