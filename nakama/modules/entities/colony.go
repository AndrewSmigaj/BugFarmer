package entities

// colony.go — ANT COLONY MEMORY (underground-arc P3.2).
//
// FRONTIER-SYNC CLASSIFICATION (the load-bearing contract): colony memory is
// SERVER-ONLY CENTER-AI SOFT STATE, exactly the NestState.Brood class. It is
//   - NEVER hashed (no ComputeStateHash field),
//   - NEVER snapshotted (LateJoinSnapshot carries Swarms/Metadata/Log/Players/Food only),
//   - NEVER saved (buildWorldSave must not serialize it — the Unbounded-Growth lens
//     demands trails AGE OUT; a restart forgets them and scouts re-learn).
// Its only observable output is which SWARM_SET_TARGET legs the server emits — which
// every client already replays identically. Zero new ledger events.
//
// BOUNDS: ≤ MaxColonySites sites per nest (weakest evicted), ≤ MaxRouteLen breadcrumbs
// per site → standing memory ≤ nests × 8 × 24 points. Strength decays every nest pass.

// RoutePoint is one scout breadcrumb (world coords, cell-ish resolution).
type RoutePoint struct {
	X float32
	Y float32
}

// CarrionSite is one remembered food site plus the scout's WALKED route to it.
// The route is the trail: workers replay it hop-by-hop, so files share one literal
// polyline that bends with the terrain (an LOS-safe chain by construction — the scout
// actually walked it). Route order is HOME → SITE.
type CarrionSite struct {
	GridX    int
	GridY    int
	Strength float32
	Route    []RoutePoint
}

// ColonyMemory is one nest's remembered world. A slice, not a map: bounded, ordered,
// and iterated deterministically by construction.
type ColonyMemory struct {
	Sites []*CarrionSite
}

const (
	// MaxColonySites bounds each nest's memory (Unbounded-Growth lens).
	MaxColonySites = 8
	// MaxRouteLen bounds one trail's breadcrumbs. A scout walk longer than this since
	// leaving home frays at the HOME end (oldest dropped) — v1 accepts that; colonies
	// forage within home range, where walks stay short.
	MaxRouteLen = 24
	// SiteStrengthCap clamps refreshes so one bonanza can't dominate forever.
	SiteStrengthCap = 100.0
	// SiteMergeRadius: registrations within this radius merge into ONE site — a food
	// PILE is one destination, not a memory-churning constellation of cells (v8).
	SiteMergeRadius = 4
	// SiteDecayPerPass drains strength every nest pass (30 ticks) — the age-out.
	// 0.75 (was 1.5): one scout sighting must live long enough (~50s) for the first
	// workers to reach a FAR site and light the traffic-reinforcement loop (v6: at
	// 1.5, sparse-scout memories evaporated before anyone marched).
	SiteDecayPerPass = 0.75
)