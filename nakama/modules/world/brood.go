package world

import (
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Visible breeding broods. Flies/butterflies LAY eggs into a BroodState at their breeding source
// (compost bin, milkweed, or a transient maggot pile on rotten ground-fruit) instead of growing
// instantly; processBroods matures eggs -> maggots and HATCHES bugs via the proven growSwarm /
// spawnSwarmAt -> SWARM_REPRODUCED paths. Broods are server-only soft state (never hashed, never in the
// late-join snapshot); the BroodUpdate broadcast is display-only. Wasp nests keep their own NestState
// economy (handlers in nests.go) — this file is the non-predator sources only.

const broodHatchJoinRadius = 4.0 // a hatch grows a same-species swarm camped this close, else mints one

// broodKey is the "gx,gy" map key for a brood at a cell.
func broodKey(gx, gy int) string { return fmt.Sprintf("%d,%d", gx, gy) }

// broodAreaSize: ground-pile maggot broods are SHARED across this NxN-cell area (≈ one pile per tree's
// windfall) instead of one-per-apple, so every local fly lays into a single persistent, maturing pile.
const broodAreaSize = 4

// broodAreaKey snaps a cell to its area origin — the shared ground-pile maggot-brood cell for that area.
func broodAreaKey(gx, gy int) (int, int) {
	return (gx / broodAreaSize) * broodAreaSize, (gy / broodAreaSize) * broodAreaSize
}

// getOrCreateBrood returns the brood at (gx,gy), creating it bound to its source if absent.
// Ground-pile (fly) broods get a "g:" key namespace so an area-snapped fly pile can never collide with a
// host-plant (milkweed) or station brood that uses the SAME exact cell — without it, a milkweed sitting on
// an area-origin cell (gx,gy both %4==0) would share a map slot with a fly pile and one species would lay
// into / hatch from the other's brood.
func (m *Match) getOrCreateBrood(state *WorldState, gx, gy int, speciesID, sourceKind, sourceID string, capEggs int) *entities.BroodState {
	key := broodKey(gx, gy)
	if sourceKind == "ground_pile" {
		key = "g:" + key
	}
	b := state.BroodStates[key]
	if b == nil {
		b = &entities.BroodState{
			GridX: gx, GridY: gy, SpeciesID: speciesID,
			SourceKind: sourceKind, SourceID: sourceID, CapEggs: capEggs,
		}
		state.BroodStates[key] = b
	}
	return b
}

// layEggs deposits n eggs into the brood at (gx,gy), clamped at the brood's capacity. Returns how many
// were actually accepted (0 if the nursery is full). Called from the reproduceSwarm redirect.
func (m *Match) layEggs(dispatcher runtime.MatchDispatcher, state *WorldState, b *entities.BroodState, n int) int {
	room := b.CapEggs - (b.Eggs + b.Maggots + b.Pupae)
	if room <= 0 {
		return 0
	}
	if n > room {
		n = room
	}
	b.Eggs += n
	m.broadcastBroodUpdate(dispatcher, state, b, false)
	return n
}

// layIntoBrood resolves the reproducing swarm's breeding source (compost station / milkweed host plant /
// rotten-fruit ground pile) and lays `count` eggs into the brood there. Returns true if any were
// accepted (false: unknown source, or the nursery is full). The pile is sized by the food it sits on.
func (m *Match) layIntoBrood(state *WorldState, dispatcher runtime.MatchDispatcher, swarm *entities.SwarmState, count int) bool {
	gx, gy := int(swarm.TargetFoodX), int(swarm.TargetFoodY)
	capEggs := entities.BroodDefaultCapEggs

	var kind, sourceID string
	if state.Stations[swarm.TargetFoodID] != nil {
		kind, sourceID = "station", swarm.TargetFoodID
	} else if state.HostPlantStates[broodKey(gx, gy)] != nil {
		kind = "host_plant"
	} else if it, ok := state.GroundItems[swarm.TargetFoodID]; ok && it.FoodValue > 0 {
		// SHARED per-AREA maggot pile (≈ one per tree's windfall), NOT bound to this single apple. The
		// apple is eaten within seconds (feeding drain + the breed food-cost), but the maggots laid in it
		// must keep developing (10s+ each to mature). So we snap the brood to a coarse area cell — every
		// local fly lays into the SAME persistent pile — and detach it from the apple's lifetime: the food
		// is already paid at lay time, so broodSourceGone never fires for a ground pile and processBroods
		// retires the pile only once it has fully hatched out. capEggs stays the shared default (set above).
		kind, sourceID = "ground_pile", ""
		gx, gy = broodAreaKey(gx, gy)
		_ = it
	} else {
		// No recognized food-source breeding spot (free-roaming predators like dragonfly/centipede,
		// detritivores that breed on forage pools/carrion). Lay a VISIBLE clutch at the swarm's OWN area
		// cell so the birth still develops + is visible — never an instant pop-out. Reuses the ground-pile
		// behavior (detached lifetime, retires once fully hatched out).
		cs := state.Config.ChunkSize
		kind, sourceID = "ground_pile", ""
		gx, gy = broodAreaKey(int(swarm.WorldX(cs)), int(swarm.WorldY(cs)))
	}

	b := m.getOrCreateBrood(state, gx, gy, swarm.SpeciesID, kind, sourceID, capEggs)
	return m.layEggs(dispatcher, state, b, count) > 0
}

// processBroods (slow clock, beside processNests) climbs each brood one life stage per stageTicks
// (egg->larva->[pupa]->adult; the final step hatches bugs) and sweeps broods whose source is gone.
// Collect-then-delete (no map mutation mid-range).
func (m *Match) processBroods(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	const interval = 30 // call cadence (ticks); matches the processNests slow clock
	var toDelete []string

	for _, key := range sortedStringKeys(state.BroodStates) { // sorted: hatches mint swarm IDs
		b := state.BroodStates[key]
		// 1) Source-gone sweep: hatch whatever fully matured, then clear.
		if m.broodSourceGone(state, b) {
			for m.broodReadyToHatch(state, b) > 0 {
				if hatched := m.hatchFromBrood(state, b); hatched == 0 {
					break // at the population/swarm cap — drop the rest with the vanishing source
				}
			}
			m.broadcastBroodUpdate(dispatcher, state, b, true)
			toDelete = append(toDelete, key)
			continue
		}

		// Climb ONE life stage per stageTicks so EVERY stage DWELLS (is broadcast + rendered):
		// egg->larva->[pupa]->adult; the final transition IS the hatch. BroodEggMatureTicks is split by the
		// transition count so TOTAL egg->adult dev time is unchanged — the pupa just subdivides the same
		// window. Most-advanced-first (advanceBroodStage) so nothing starves. NESTS use the SAME ladder now
		// (they pupate + count pupae via nestBroodCount) — the nest hatch grows the resident (hatchFromBrood).
		transitions := 2
		if m.broodPupates(state, b) {
			transitions = 3
		}
		stageTicks := entities.BroodEggMatureTicks / transitions
		if b.Eggs > 0 || b.Maggots > 0 || b.Pupae > 0 {
			b.StageProgress += interval
			if b.StageProgress >= stageTicks {
				if m.advanceBroodStage(state, b) {
					b.StageProgress -= stageTicks
				} else {
					b.StageProgress = stageTicks // only a cap-held final stage remains — hold, retry next call
				}
			}
		}

		// A ground pile isn't tied to a vanishing apple: retire it once it has fully hatched out (no eggs,
		// larvae, or pupae left) so a tree's between-fruitings don't leave empty piles lingering. Active
		// piles (a fly bred there this cycle) keep ≥1 egg and survive.
		if b.SourceKind == "ground_pile" && b.Eggs == 0 && b.Maggots == 0 && b.Pupae == 0 {
			m.broadcastBroodUpdate(dispatcher, state, b, true)
			toDelete = append(toDelete, key)
			continue
		}

		// Re-broadcast the live brood every slow tick (not only on a stage transition) so an open nursery
		// panel keeps its counts, conversion bar (StageProgress), and resident count fresh. Display-only +
		// chunk-scoped → cheap (a handful of broods per zone).
		m.broadcastBroodUpdate(dispatcher, state, b, false)
	}

	for _, key := range toDelete {
		delete(state.BroodStates, key)
	}
}

// broodSourceGone reports whether the brood's backing source has disappeared.
func (m *Match) broodSourceGone(state *WorldState, b *entities.BroodState) bool {
	switch b.SourceKind {
	case "ground_pile":
		// A laid maggot pile develops on its own (the food was consumed at lay time); it is never
		// "source-gone". processBroods retires it once empty (all eggs matured + hatched out).
		return false
	case "station":
		return state.Stations[b.SourceID] == nil
	case "host_plant":
		return state.HostPlantStates[broodKey(b.GridX, b.GridY)] == nil
	case "nest":
		// The nest occupant is gone (destroyed / swept). On a calm SWEEP its in-progress brood hatches out
		// into the resident (if still alive) then clears — same shape as a vanishing station. The player-BREAK
		// path (onNestOccupantRemoved) instead PERISHES the brood (clearNestBrood) BEFORE deleting the nest,
		// so by the time the sweep sees NestStates==nil the BroodState is already gone (nothing double-hatches).
		return state.NestStates[broodKey(b.GridX, b.GridY)] == nil
	}
	return false
}

// nestBroodCount is the nest's banked brood (eggs + maggots in its visible BroodState) — the economy
// currency processNests/processNestFounding read, replacing the old nest.Brood counter.
func (m *Match) nestBroodCount(state *WorldState, nest *entities.NestState) int {
	if b := state.BroodStates[broodKey(nest.GridX, nest.GridY)]; b != nil {
		return b.Eggs + b.Maggots + b.Pupae
	}
	return 0
}

// depositNestEgg lays ONE egg into the nest's visible BroodState (a homing resident's provisioning
// trip), clamped at the nest brood cap. Dispatcher-free (called from the deposit path inside
// predationThink) so it does NOT broadcast — processBroods/processNests carry the display update.
func (m *Match) depositNestEgg(state *WorldState, nest *entities.NestState, capEggs int) {
	b := m.getOrCreateBrood(state, nest.GridX, nest.GridY, nest.SpeciesID, "nest", "", capEggs)
	if b.Eggs+b.Maggots+b.Pupae < b.CapEggs {
		b.Eggs++
	}
}

// drainNestBrood removes up to n from the nest's BroodState (maggots first, then eggs) and returns how
// many were drained — the recovery re-staff (a dead resident's banked brood becomes a fresh patrol).
// Broadcasts the display update; clears the brood if it empties.
func (m *Match) drainNestBrood(state *WorldState, dispatcher runtime.MatchDispatcher, nest *entities.NestState, n int) int {
	key := broodKey(nest.GridX, nest.GridY)
	b := state.BroodStates[key]
	if b == nil || n <= 0 {
		return 0
	}
	drained := 0
	// Drain most-advanced first: pupae, then maggots, then eggs (re-staff pulls the closest-to-adult brood).
	for _, stage := range []*int{&b.Pupae, &b.Maggots, &b.Eggs} {
		if n <= 0 {
			break
		}
		take := n
		if take > *stage {
			take = *stage
		}
		*stage -= take
		drained += take
		n -= take
	}
	empty := b.Eggs == 0 && b.Maggots == 0 && b.Pupae == 0
	m.broadcastBroodUpdate(dispatcher, state, b, empty)
	if empty {
		delete(state.BroodStates, key)
	}
	return drained
}

// clearNestBrood removes the nest's entire BroodState (founding drains the banked surplus to a cooldown).
func (m *Match) clearNestBrood(state *WorldState, dispatcher runtime.MatchDispatcher, nest *entities.NestState) {
	key := broodKey(nest.GridX, nest.GridY)
	if b := state.BroodStates[key]; b != nil {
		m.broadcastBroodUpdate(dispatcher, state, b, true)
		delete(state.BroodStates, key)
	}
}

// broodPupates reports whether this brood runs the full egg->larva->PUPA->adult ladder: any brood
// (source OR nest) whose species has a pupa sprite. Holometabolous bugs (fly/butterfly/beetle + wasp/bee/ant
// in a nest) pupate; non-pupating species (e.g. millipede) stay egg->larva->adult. The nest economy
// (nestBroodCount / drainNestBrood) counts pupae too, so nests pupate without breaking founding/recovery.
func (m *Match) broodPupates(state *WorldState, b *entities.BroodState) bool {
	sp := state.Species[b.SpeciesID]
	return sp != nil && sp.PupaSpriteID != ""
}

// broodReadyToHatch is the count in the final pre-adult stage — PUPAE for a pupating source brood, else MAGGOTS.
func (m *Match) broodReadyToHatch(state *WorldState, b *entities.BroodState) int {
	if m.broodPupates(state, b) {
		return b.Pupae
	}
	return b.Maggots
}

// advanceBroodStage advances ONE brood item by one stage, MOST-ADVANCED first. The final advance IS the hatch
// (via hatchFromBrood, cap-gated). Most-advanced-first keeps the final stage draining — continuous laying
// still hatches, larvae/pupae never pile up forever — while every stage still dwells one stageTicks (so it is
// broadcast + rendered). Returns false only when nothing could advance (e.g. just a cap-held final stage).
func (m *Match) advanceBroodStage(state *WorldState, b *entities.BroodState) bool {
	pupating := m.broodPupates(state, b)

	// Final stage -> adult (hatch). hatchFromBrood drains the right field (pupae if pupating, else maggots)
	// and returns 0 when held at the population/swarm cap — then we fall through to advance an earlier stage.
	if pupating && b.Pupae > 0 {
		if m.hatchFromBrood(state, b) > 0 {
			return true
		}
	} else if !pupating && b.Maggots > 0 {
		if m.hatchFromBrood(state, b) > 0 {
			return true
		}
	}

	// Larva -> pupa (pupating only; for a non-pupating brood the larva IS the final stage, handled above).
	if pupating && b.Maggots > 0 {
		b.Maggots--
		b.Pupae++
		return true
	}

	// Egg -> larva.
	if b.Eggs > 0 {
		b.Eggs--
		b.Maggots++
		return true
	}

	return false
}

// hatchFromBrood turns up to BroodHatchCount of the final-stage brood into bugs at the brood cell — growing
// the nearest same-species swarm camped there (the breeder) or, failing that, minting a small new swarm.
// Returns the number hatched (0 if held at the population/swarm cap). Mirrors the nest hatch + reproduceSwarm caps.
func (m *Match) hatchFromBrood(state *WorldState, b *entities.BroodState) int {
	species := state.Species[b.SpeciesID]
	// The final pre-adult stage: PUPAE for a pupating source brood, else MAGGOTS (nests + non-pupating).
	ready := &b.Maggots
	if m.broodPupates(state, b) {
		ready = &b.Pupae
	}
	if species == nil || *ready <= 0 {
		return 0
	}
	n := entities.BroodHatchCount
	if n > *ready {
		n = *ready
	}

	// Population cap: hold maggots if there's no room (the nest's at-cap banking).
	if maxPop := state.SpeciesMaxPopulation(b.SpeciesID); maxPop > 0 {
		room := maxPop - state.SpeciesPopulation(b.SpeciesID)
		if room < n {
			n = room
		}
		if n <= 0 {
			return 0
		}
	}

	// NEST brood: emerge into the nest's own RESIDENT patrol (it may be hunting far from the nest, so
	// nearestSwarmNear is wrong here). No live resident → HOLD the maggots (processNests recovery drains
	// them to re-staff); nest gone → HOLD (the source-gone sweep / break-release owns it).
	if b.SourceKind == "nest" {
		nest := state.NestStates[broodKey(b.GridX, b.GridY)]
		if nest == nil {
			return 0
		}
		resident, alive := state.Swarms[nest.ResidentSwarmID]
		if !alive || nest.ResidentSwarmID == "" {
			return 0
		}
		m.growSwarm(state, resident, n)
		state.Stats.recordBirth(b.SpeciesID, BirthBrood, n)
		*ready -= n
		return n
	}

	chunkSize := state.Config.ChunkSize
	cellX := float32(b.GridX) + 0.5
	cellY := float32(b.GridY) + 0.5

	if target := m.nearestSwarmNear(state, b.SpeciesID, cellX, cellY, broodHatchJoinRadius, chunkSize); target != nil {
		m.growSwarm(state, target, n) // SWARM_REPRODUCED into the camped swarm
	} else {
		// No swarm to join: mint one, honoring the zone swarm-count cap (else hold).
		if state.CurrentZone != nil && state.CurrentZone.BugSpawning != nil {
			if zcap, ok := state.CurrentZone.BugSpawning.SpeciesCaps[b.SpeciesID]; ok &&
				zcap.Max > 0 && state.AliveSwarmCount(b.SpeciesID) >= zcap.Max {
				return 0
			}
		}
		if m.spawnSwarmAt(state, b.SpeciesID, n, cellX, cellY, chunkSize) == nil {
			return 0
		}
	}
	state.Stats.recordBirth(b.SpeciesID, BirthBrood, n) // both paths minted n bugs from the brood
	*ready -= n
	return n
}

// nearestSwarmNear returns the closest same-species swarm whose centre is within radius of (x,y), or nil.
func (m *Match) nearestSwarmNear(state *WorldState, speciesID string, x, y, radius float32, chunkSize int) *entities.SwarmState {
	var best *entities.SwarmState
	bestD := radius * radius
	for _, id := range state.SwarmsBySpecies[speciesID] {
		sw, ok := state.Swarms[id]
		if !ok {
			continue
		}
		dx := sw.WorldX(chunkSize) - x
		dy := sw.WorldY(chunkSize) - y
		if d := dx*dx + dy*dy; d <= bestD {
			bestD = d
			best = sw
		}
	}
	return best
}

// onBroodSourceRemoved is the breakOccupantAt hook: a broken compost/milkweed clears its brood at once
// (the slow sweep is only a backstop). Hatch nothing — a destroyed source loses its in-progress brood.
func (m *Match) onBroodSourceRemoved(state *WorldState, dispatcher runtime.MatchDispatcher, gx, gy int) {
	key := broodKey(gx, gy)
	if b := state.BroodStates[key]; b != nil {
		m.broadcastBroodUpdate(dispatcher, state, b, true)
		delete(state.BroodStates, key)
	}
}

// broadcastBroodUpdate sends a display-only nursery update to the brood's chunk subscribers.
// broodUpdateMessage builds the display-only OpCode-104 payload for a brood: stage counts + the
// conversion-bar fraction (how far the current stage has climbed toward the next transition, 0..1) +
// the resident-adult count (nests today; compost later). Shared by the chunk broadcast and the
// join/subscribe hydration so both carry identical fields.
func (m *Match) broodUpdateMessage(state *WorldState, b *entities.BroodState, removed bool) BroodUpdateMessage {
	var progress float32
	if !removed {
		transitions := 2
		if m.broodPupates(state, b) {
			transitions = 3
		}
		if stageTicks := entities.BroodEggMatureTicks / transitions; stageTicks > 0 {
			progress = float32(b.StageProgress) / float32(stageTicks)
			if progress > 1 {
				progress = 1
			}
		}
	}
	residents := 0
	if b.SourceKind == "nest" {
		if nest := state.NestStates[broodKey(b.GridX, b.GridY)]; nest != nil {
			if sw, ok := state.Swarms[nest.ResidentSwarmID]; ok && sw != nil {
				residents = sw.Count
			}
		}
	}
	return BroodUpdateMessage{
		GX: b.GridX, GY: b.GridY, Species: b.SpeciesID,
		Eggs: b.Eggs, Maggots: b.Maggots, Pupae: b.Pupae,
		Progress: progress, Residents: residents,
		Kind: b.SourceKind, Removed: removed,
	}
}

func (m *Match) broadcastBroodUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, b *entities.BroodState, removed bool) {
	chunkSize := state.Config.ChunkSize
	cx, cy := b.GridX/chunkSize, b.GridY/chunkSize
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBroodUpdate, m.broodUpdateMessage(state, b, removed))
}
