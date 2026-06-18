package world

import (
	"math"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Predation (architecture_swarm_sync.md §14): predators hunt prey SWARMS; prey flee
// predators. ALL of it is server-side state machinery whose outputs ride the EXISTING
// event vocabulary — hunt/flee legs are ordinary SWARM_SET_TARGET events, kills are
// BUG_REMOVED (the melee path verbatim via killBugsInSwarm), carrion is ITEM_ROTTED.
// Clients replay outputs, never decisions, so server-side rand here is replay-safe
// (the established Think-time convention).
//
// Pacing layers (why wasps can't annihilate a zone): satiation budgets the trip
// (hunt only below hunt_satiation_threshold, ~3 kills to sated), the strike cooldown
// (the anti-snowball knob — don't lower it), the hunt timeout, the home-range tether,
// and §13's hard population caps.

const (
	huntReaimMinTicks  = 10  // hunt/flee legs re-aim fast (floor — also the leg-spam floor)
	huntReaimJitter    = 6   // +rand(6)
	huntTimeoutTicks   = 300 // a hunt with no kill for 30s gives up
	wanderThinkMin     = 30  // the existing wander cadence
	wanderThinkJitter  = 21
	predWanderDistance = 6.0 // predator wander leg length
)

// predationThink runs the species-specific Think branches that REPLACE the shared
// forage/wander block. Returns true when it owned this think (emitted a leg + scheduled
// NextThinkTick). Order of ownership:
//  1. PREY flee (a predator is near) — any species with predator_flee_radius
//  2. PREDATOR behavior (species.Predation != nil): hunt / wander-in-home-range
//
// Every path through here writes SpeedMult before emitting (the sync contract).
func (m *Match) predationThink(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
	deltaTime float32,
	logger runtime.Logger,
) bool {
	// --- 1. PREY FLEE -------------------------------------------------------------
	if species.PredatorFleeRadius > 0 {
		if px, py, found := m.nearestPredatorPos(state, swarm, species, species.PredatorFleeRadius); found {
			// Directly away from the predator, RaycastClamped — penned prey corner
			// against their own fence (intended: penned flies are MORE vulnerable).
			sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
			dx, dy := sx-px, sy-py
			dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
			if dist < 0.01 {
				dx, dy, dist = 1, 0, 1 // predator exactly on us: pick a direction
			}
			const fleeDistance = 8.0
			tx := sx + dx/dist*fleeDistance
			ty := sy + dy/dist*fleeDistance
			cx, cy := entities.RaycastClamp(sx, sy, tx, ty, func(x, y float32) bool {
				return state.IsBlockedForSpecies(x, y, species)
			})

			mult := species.PredatorFleeSpeedMult
			if mult <= 0 {
				mult = 1.5
			}
			swarm.TargetFoodID = "" // fleeing abandons the meal (meters pause)
			swarm.TargetPreyID = ""
			m.emitLeg(state, swarm, species, cx, cy, mult, chunkSize, deltaTime)
			swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
			return true
		}
		// No predator near: fall through (prey species may also be predators in
		// principle, but normally this returns to the shared forage path).
	}

	// --- 2. PREDATOR --------------------------------------------------------------
	p := species.Predation
	if p == nil {
		return false
	}

	homeX, homeY := swarm.HomePos.WorldX(chunkSize), swarm.HomePos.WorldY(chunkSize)

	// NEST predators run the custom lifecycle tree: defending > homing > hunt > rest.
	if p.NestOccupant != "" {
		// DEFENDING — entry: recalled by nest damage (recallNestDefenders) OR a player
		// loitering within NestDefendRadius of the nest. Exit: hysteresis distance or
		// the timer. Defenders chase at hunt speed (scary NEAR the nest only).
		nest := state.NestStates[swarm.NestKey]
		if swarm.Phase != "defending" && nest != nil {
			if pid, px, py, found := m.nearestPlayer(state, float32(nest.GridX)+0.5, float32(nest.GridY)+0.5, entities.NestDefendRadius); found {
				_ = px
				_ = py
				swarm.Phase = "defending"
				swarm.DefendTargetID = pid
				swarm.DefendUntilTick = state.TickCount + entities.NestDefendTicks
			}
		}
		if swarm.Phase == "defending" {
			exit := state.TickCount >= swarm.DefendUntilTick || nest == nil
			var tx, ty float32
			if !exit {
				if target, ok := state.Players[swarm.DefendTargetID]; ok {
					tx, ty = target.WorldX(chunkSize), target.WorldY(chunkSize)
					ndx, ndy := tx-(float32(nest.GridX)+0.5), ty-(float32(nest.GridY)+0.5)
					if ndx*ndx+ndy*ndy > entities.NestDefendRelease*entities.NestDefendRelease {
						exit = true // the threat left the nest area
					}
				} else {
					exit = true // attacker gone
				}
			}
			if exit {
				swarm.Phase = "feeding"
				swarm.DefendTargetID = ""
			} else {
				mult := p.HuntSpeedMult
				if mult <= 0 {
					mult = 1.0
				}
				swarm.TargetPreyID = ""
				m.emitLeg(state, swarm, species, tx, ty, mult, chunkSize, deltaTime)
				swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
				return true
			}
		}

		// HOMING — entry: sated with a live nest. Carry one brood home; deposit on
		// arrival (satiation drops to deposit_satiation: the readable rest window);
		// a trip over the timeout drops the brood (a bool-carry can't deadlock).
		if swarm.Phase != "homing" && swarm.Satiation >= 100 && swarm.NestKey != "" && nest != nil {
			swarm.Phase = "homing"
			swarm.CarryingBrood = true
			swarm.HomingStartTick = state.TickCount
			swarm.TargetPreyID = ""
		}
		if swarm.Phase == "homing" {
			if nest == nil || state.TickCount-swarm.HomingStartTick > entities.NestHomingTimeout {
				swarm.Phase = "feeding" // brood dropped / nest gone
				swarm.CarryingBrood = false
			} else {
				nx, ny := float32(nest.GridX)+0.5, float32(nest.GridY)+0.5
				sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
				ddx, ddy := nx-sx, ny-sy
				if ddx*ddx+ddy*ddy <= entities.NestDepositRange*entities.NestDepositRange {
					// Arrived: deposit + hatch check, then rest (hunt resumes only when
					// satiation decays below the hunt threshold — the trip pacing knob)
					if swarm.CarryingBrood {
						m.depositBrood(state, swarm, nest, logger)
					}
					swarm.CarryingBrood = false
					swarm.Phase = "feeding"
					swarm.Satiation = p.DepositSatiation
				} else {
					m.emitLeg(state, swarm, species, nx, ny, 1.0, chunkSize, deltaTime)
					swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
					return true
				}
			}
		}
	}

	// INDIVIDUAL ground predators (centipede): CARRION-FIRST — if food is visible,
	// decline ownership so the SHARED forage block dines/breeds normally (it clears
	// TargetPreyID + resets SpeedMult on entry). Hunting is the fallback for a hungry
	// centipede with nothing to scavenge.
	isIndividual := species.Category == "individual"
	if isIndividual && swarm.TargetPreyID == "" {
		// A fresh swarm's Phase is "" until the first CheckPhaseTransition — default
		// to "feeding" for the attraction lookup (the transition's own default).
		phase := swarm.Phase
		if phase == "" || phase == "idle" {
			phase = "feeding"
		}
		if attractions := species.AttractionsByPhase[phase]; len(attractions) > 0 {
			if hits := FindNearbyFood(state, swarm.Position, species.VisionRange, attractions); len(hits) > 0 {
				return false
			}
		}
	}

	// Continue or acquire a hunt. Hunting persists once started (re-aim each think)
	// until: sated, prey gone/out-of-range, or timeout without a kill.
	hunting := swarm.TargetPreyID != ""
	if !hunting && swarm.Satiation < p.HuntSatiationThreshold {
		if preyID, found := m.nearestPreySwarm(state, swarm, p, chunkSize); found {
			swarm.TargetPreyID = preyID
			swarm.TargetFoodID = "" // exclusivity: never hunt and dine at once
			swarm.HuntStartTick = state.TickCount
			hunting = true
		}
	}

	if hunting {
		prey, ok := state.Swarms[swarm.TargetPreyID]
		preyX, preyY := float32(0), float32(0)
		inRange := false
		if ok && prey.Count > 0 {
			preyX, preyY = prey.WorldX(chunkSize), prey.WorldY(chunkSize)
			hdx, hdy := preyX-homeX, preyY-homeY
			inRange = p.HomeRange <= 0 || hdx*hdx+hdy*hdy <= p.HomeRange*p.HomeRange
		}
		lastProgress := swarm.HuntStartTick
		if swarm.LastStrikeTick > lastProgress {
			lastProgress = swarm.LastStrikeTick
		}
		timedOut := state.TickCount-lastProgress > huntTimeoutTicks
		sated := swarm.Satiation >= 100

		if !ok || !inRange || timedOut || sated {
			swarm.TargetPreyID = "" // hunt over; wander below
		} else {
			// Re-aim at the prey's CURRENT center. Fliers go straight; grounded clamp —
			// and a GNAWABLE blocker turns a clamped individual's hunt into a gnaw
			// (penned prey is acquired through the fence; the break-in motive).
			mult := p.HuntSpeedMult
			if mult <= 0 {
				mult = 1.0
			}
			tx, ty := preyX, preyY
			if !species.FliesOverFences {
				sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
				cxp, cyp, bx, by, blocked := entities.RaycastClampWithBlock(sx, sy, tx, ty, func(x, y float32) bool {
					return state.IsBlockedForSpecies(x, y, species)
				})
				if blocked && isIndividual && m.tryStartGnaw(state, swarm, species, bx, by, chunkSize, deltaTime) {
					return true
				}
				tx, ty = cxp, cyp
			}
			m.emitLeg(state, swarm, species, tx, ty, mult, chunkSize, deltaTime)
			swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
			return true
		}
	}

	// Idle: individuals wander SERPENTINE (heading-constrained short legs + the
	// dead-end escape hatch); swarm predators rest-wander in their home range.
	if isIndividual {
		m.centipedeWander(state, swarm, species, chunkSize, deltaTime)
		return true
	}

	// Wander within the home range (rest between trips; the readable loiter).
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	angle := state.Rng.Float64() * 2 * math.Pi
	tx := sx + float32(math.Cos(angle))*predWanderDistance
	ty := sy + float32(math.Sin(angle))*predWanderDistance
	if p.HomeRange > 0 {
		// Clamp the wander target back inside the home circle
		hdx, hdy := tx-homeX, ty-homeY
		if d := float32(math.Sqrt(float64(hdx*hdx + hdy*hdy))); d > p.HomeRange {
			tx = homeX + hdx/d*p.HomeRange
			ty = homeY + hdy/d*p.HomeRange
		}
	}
	cxp, cyp := entities.RaycastClamp(sx, sy, tx, ty, func(x, y float32) bool {
		return state.IsBlockedForSpecies(x, y, species)
	})
	m.emitLeg(state, swarm, species, cxp, cyp, 1.0, chunkSize, deltaTime)
	swarm.NextThinkTick = state.TickCount + wanderThinkMin + state.Rng.Int63n(wanderThinkJitter)
	return true
}

// checkPredationStrike is the PER-TICK kill check (re-aims happen at think cadence, but
// centers can cross between thinks): cached prey within strike_radius + cooldown →
// kill the LOWEST ascending alive ids via the shared melee kill path, spawn carrion at
// the PREDATOR's center (the strike point — falls back to the victim's center if
// blocked), feed the predator.
func (m *Match) checkPredationStrike(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
) {
	p := species.Predation
	if p == nil || swarm.TargetPreyID == "" {
		return
	}
	if state.TickCount-swarm.LastStrikeTick < p.StrikeCooldownTicks {
		return
	}
	prey, ok := state.Swarms[swarm.TargetPreyID]
	if !ok || prey.Count <= 0 {
		swarm.TargetPreyID = ""
		return
	}

	dx := swarm.WorldX(chunkSize) - prey.WorldX(chunkSize)
	dy := swarm.WorldY(chunkSize) - prey.WorldY(chunkSize)
	if dx*dx+dy*dy > p.StrikeRadius*p.StrikeRadius {
		return
	}

	kills := p.KillsPerStrike
	if kills <= 0 {
		kills = 1
	}
	preySpecies := state.Species[prey.SpeciesID]
	ids := prey.FirstAliveBugIDs(kills)
	removed := m.killBugsInSwarm(logger, dispatcher, state, prey, preySpecies, ids,
		swarm.WorldX(chunkSize), swarm.WorldY(chunkSize), chunkSize)
	if len(removed) == 0 {
		return
	}
	state.Stats.recordDeath(prey.SpeciesID, DeathPredation, len(removed))
	state.Stats.recordPredation(swarm.SpeciesID, prey.SpeciesID, len(removed))

	swarm.LastStrikeTick = state.TickCount
	swarm.HuntStartTick = state.TickCount // a kill is progress: the timeout re-arms
	swarm.Satiation += p.FeedPerKill * float32(len(removed))
	if swarm.Satiation > 100 {
		swarm.Satiation = 100
	}

	// Strike telegraph (display-only): the snatch flash + THWACK at the PREDATOR —
	// the eye goes to the attacker; the victim shrink-fades unnoticed.
	m.broadcastBugTelegraph(dispatcher, state, swarm, "strike", chunkSize)

	logger.Debug("Predation: %s struck %s (-%d, satiation %.0f)",
		swarm.ID, prey.ID, len(removed), swarm.Satiation)
}

// nearestPreySwarm finds the closest living prey swarm within vision AND home range.
// Deterministic: distance with ascending-swarm-id tiebreak (the FindNearbyFood rule).
func (m *Match) nearestPreySwarm(
	state *WorldState,
	hunter *entities.SwarmState,
	p *entities.PredationConfig,
	chunkSize int,
) (string, bool) {
	species := state.Species[hunter.SpeciesID]
	hx, hy := hunter.WorldX(chunkSize), hunter.WorldY(chunkSize)
	homeX, homeY := hunter.HomePos.WorldX(chunkSize), hunter.HomePos.WorldY(chunkSize)
	vision := species.VisionRange

	bestID := ""
	bestDistSq := float32(math.MaxFloat32)
	for id, s := range state.Swarms {
		if s.Count <= 0 || !containsString(p.Prey, s.SpeciesID) {
			continue
		}
		sx, sy := s.WorldX(chunkSize), s.WorldY(chunkSize)
		dx, dy := sx-hx, sy-hy
		distSq := dx*dx + dy*dy
		if distSq > vision*vision {
			continue
		}
		if p.HomeRange > 0 {
			hdx, hdy := sx-homeX, sy-homeY
			if hdx*hdx+hdy*hdy > p.HomeRange*p.HomeRange {
				continue
			}
		}
		if distSq < bestDistSq || (distSq == bestDistSq && id < bestID) {
			bestID = id
			bestDistSq = distSq
		}
	}
	return bestID, bestID != ""
}

// nearestPredatorPos finds the closest predator swarm that hunts THIS species, within
// radius. Used by the prey flee branch (think-cadence cost, tiny swarm counts).
func (m *Match) nearestPredatorPos(
	state *WorldState,
	prey *entities.SwarmState,
	preySpecies *entities.BugSpecies,
	radius float32,
) (float32, float32, bool) {
	chunkSize := state.Config.ChunkSize
	px, py := prey.WorldX(chunkSize), prey.WorldY(chunkSize)

	bestID := ""
	bestX, bestY := float32(0), float32(0)
	bestDistSq := radius * radius
	for id, s := range state.Swarms {
		if s.Count <= 0 || s.ID == prey.ID {
			continue
		}
		sp := state.Species[s.SpeciesID]
		// Match on the SWARM's species id string (struct .ID can be unset for
		// in-memory-constructed species), not the species struct field.
		if sp == nil || sp.Predation == nil || !containsString(sp.Predation.Prey, prey.SpeciesID) {
			continue
		}
		sx, sy := s.WorldX(chunkSize), s.WorldY(chunkSize)
		dx, dy := sx-px, sy-py
		distSq := dx*dx + dy*dy
		if distSq < bestDistSq || (distSq == bestDistSq && bestID != "" && id < bestID) {
			bestID = id
			bestX, bestY = sx, sy
			bestDistSq = distSq
		}
	}
	return bestX, bestY, bestID != ""
}

// emitLeg sets the swarm's movement target + per-leg SpeedMult and emits the
// SWARM_SET_TARGET event carrying the SAME speed the server will move at — the §14
// sync contract in one place.
func (m *Match) emitLeg(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	targetX, targetY, mult float32,
	chunkSize int,
	deltaTime float32,
) {
	originX := swarm.WorldX(chunkSize)
	originY := swarm.WorldY(chunkSize)

	swarm.SpeedMult = mult
	swarm.TargetX, swarm.TargetY = targetX, targetY
	swarm.HasTarget = true

	if state.CurrentZone != nil {
		state.AddSwarmTargetEvent(
			state.CurrentZone.ZoneID, swarm.ID,
			toFixed(originX), toFixed(originY),
			toFixed(targetX), toFixed(targetY),
			toFixed(species.BaseSpeed*swarm.EffectiveSpeedMult()*deltaTime),
		)
	}
}

// broadcastBugTelegraph sends the display-only OpCode 95 (windup flash, strike snatch).
func (m *Match) broadcastBugTelegraph(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	kind string,
	chunkSize int,
) {
	cx := swarm.Position.ChunkX
	cy := swarm.Position.ChunkY
	msg := BugTelegraphMessage{SwarmID: swarm.ID, Kind: kind}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBugTelegraph, msg)
}

// nearestPlayer finds the closest player to a world point within radius (ascending
// user-id tiebreak for determinism in logs/tests; the value is server-only).
func (m *Match) nearestPlayer(state *WorldState, x, y, radius float32) (string, float32, float32, bool) {
	chunkSize := state.Config.ChunkSize
	bestID := ""
	var bestX, bestY float32
	bestDistSq := radius * radius
	for id, p := range state.Players {
		px, py := p.WorldX(chunkSize), p.WorldY(chunkSize)
		dx, dy := px-x, py-y
		distSq := dx*dx + dy*dy
		if distSq < bestDistSq || (distSq == bestDistSq && bestID != "" && id < bestID) {
			bestID = id
			bestX, bestY = px, py
			bestDistSq = distSq
		}
	}
	return bestID, bestX, bestY, bestID != ""
}

// netTierTrapOnly: the "no net works" sentinel tier.
const netTierTrapOnly = 99

// netSizeTier maps species net_size to the tool_tier ordering: hands ≡ small_net = 1,
// (no medium net exists yet) large_net = 3, trap_only = never nettable.
func netSizeTier(netSize string) int {
	switch netSize {
	case "", "small":
		return 1
	case "medium":
		return 2
	case "large":
		return 3
	case "trap_only":
		return netTierTrapOnly
	default:
		return 1
	}
}

func containsString(list []string, s string) bool {
	for _, v := range list {
		if v == s {
			return true
		}
	}
	return false
}

// predatorBreedSatiation — a NESTLESS predator this well-fed reproduces (the carnivore "well-fed timer").
const predatorBreedSatiation = 70.0

// processPredatorBreeding lets nestless predators (centipede, future carnivores) reproduce when well-fed.
// A pure HUNTER never breeds through the standard sated→reproducing→dine path: a kill tops satiation to
// only ~95 (the flip needs 100), and it has no carrion attraction to dine at — so it would die as a
// same-age re-seeded cohort. Instead a well-fed hunter breeds on its reproduce cooldown via the EXISTING
// reproduceSwarm (grows the swarm below MaxSwarmSize, splits a child at it). reproduceSwarm resets
// satiation→0 + the cooldown, so it must re-hunt to breed again (natural pacing) and is cap-aware;
// consumeFood with an empty TargetFoodID is a no-op. NEST predators (wasps) breed at the nest, skipped.
// Collect-then-act: reproduceSwarm can mint a new swarm (mutates state.Swarms) mid-range.
func (m *Match) processPredatorBreeding(state *WorldState, dispatcher runtime.MatchDispatcher, logger runtime.Logger) {
	if state.StaticSim {
		return
	}
	var breeders []*entities.SwarmState
	for _, id := range sortedStringKeys(state.Swarms) { // sorted: reproduceSwarm draws rand per breeder
		swarm := state.Swarms[id]
		species := state.Species[swarm.SpeciesID]
		if species == nil || species.Predation == nil || species.Predation.NestOccupant != "" {
			continue
		}
		if swarm.Count > 0 && swarm.Satiation >= state.Tuning.PredatorBreedSatiation && swarm.CanReproduce() {
			breeders = append(breeders, swarm)
		}
	}
	for _, swarm := range breeders {
		m.reproduceSwarm(state, dispatcher, swarm, state.Species[swarm.SpeciesID], logger)
	}
}
