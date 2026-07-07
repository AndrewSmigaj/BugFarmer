package world

import (
	"math"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Predation (architecture_swarm_sync.md §14): predators hunt prey SWARMS; prey flee predators. The hunt
// ECONOMY is server-side state machinery whose outputs ride the EXISTING event vocabulary — hunt/flee legs
// are ordinary SWARM_SET_TARGET events (now also carrying target_prey_id + strike params on a hunt leg),
// kills are BUG_REMOVED (the melee path verbatim via killBugsInSwarm), carrion is ITEM_ROTTED. Server-side
// rand here is replay-safe (clients replay outputs, never decisions — the Think-time convention).
//
// Phase 2 EXCEPTION — the STRIKE SELECTION (which individual flies die) is computed by the AUTHORITY
// CLIENT, which has bit-identical per-bug positions; it reports victims via OpCodePredationStrike →
// handlePredationStrike → applyPredationStrike (the server has only centres). The kill still rides
// BUG_REMOVED so followers/late-joiners stay in sync.
//
// Pacing layers (why wasps can't annihilate a zone): satiation budgets the trip
// (hunt only below hunt_satiation_threshold, ~3 kills to sated), the strike cooldown
// (the anti-snowball knob — don't lower it), the hunt timeout, the home-range tether,
// and §13's hard population caps.

const (
	huntReaimMinTicks  = 10  // hunt/flee legs re-aim fast (floor — also the leg-spam floor)
	huntReaimJitter    = 6   // +rand(6)
	huntTimeoutTicks   = 300 // a hunt with no kill for 30s: re-target a fresh prey (nest predators) / give up (others)
	wanderThinkMin     = 30  // the existing wander cadence
	wanderThinkJitter  = 21
	predWanderDistance = 6.0 // predator wander leg length
	// predatorFullSatiation: a nest predator's "caught a full load" point. It is BOTH the homing trigger
	// (carry the load home, deposit brood) AND the forage ceiling (keep hunting until you reach it). Tying
	// the two together is the whole 2-state forager loop — FORAGE while < full, PROVISION at full — with no
	// dead zone between "too fed to start a hunt" and "full enough to go home", and no idling while hungry.
	// It MUST sit below the 100 satiation cap: a kill clamps satiation AT 100, so a trigger of 100 is never
	// observed at a think (satiation decays a hair below 100 in the 1-3s between the kill and the next
	// think) and the wasp forages forever without ever heading home. 90 leaves the post-kill overshoot
	// comfortably above it (decay-per-think ≈ 0.3), so the provision reliably fires.
	predatorFullSatiation = 90.0
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
	// Cost profiler: time the whole predationThink (flee scan + hunt) per species. The flee branch's
	// nearestPredatorPos is the O(S²) the audit flagged — this quantifies it. Nil/disabled = no-op.
	pt := state.Perf.Start()
	state.Perf.Count(species.ID, "pred_thinks")
	defer state.Perf.StopSpecies(species.ID, "pred", pt)

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
			// Default: the short directly-away flee (out-chased by a faster hunter). But with RelocateChance
			// (and off cooldown) a swarm instead makes a long BREAK-CONTACT jump — RelocateDistance away, with
			// a random angle so relocating swarms scatter to DIFFERENT spots — to clear the hunter's vision and
			// actually escape. Not all roll it → some stay and get eaten (the crash). Determinism-safe: state.Rng.
			fleeDistance := float32(8.0)
			if species.RelocateChance > 0 && state.TickCount >= swarm.RelocateReadyTick &&
				state.Rng.Float32() < species.RelocateChance {
				fleeDistance = species.RelocateDistance
				if fleeDistance <= 0 {
					fleeDistance = 22.0
				}
				ang := (state.Rng.Float32()*2 - 1) // ±~57° jitter on the away direction (rotation preserves length)
				ca, sa := float32(math.Cos(float64(ang))), float32(math.Sin(float64(ang)))
				dx, dy = dx*ca-dy*sa, dx*sa+dy*ca
				swarm.RelocateReadyTick = state.TickCount + species.RelocateCooldownTicks
			}
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
		// §C precedence rule (all three defend entries apply it): defense is suppressed
		// while (the resident is SUBDUED) or (the nest is SMOKED).
		nest := state.NestStates[swarm.NestKey]
		if swarm.Phase != "defending" && nest != nil && !nestDefenseSuppressed(state, nest, swarm) {
			if pid, px, py, found := m.nearestPlayer(state, float32(nest.GridX)+0.5, float32(nest.GridY)+0.5, entities.NestDefendRadius); found {
				_ = px
				_ = py
				swarm.Phase = "defending"
				swarm.DefendTargetID = pid
				swarm.DefendUntilTick = state.TickCount + entities.NestDefendTicks
			}
		}
		if swarm.Phase == "defending" {
			// Exit hysteresis — the same §C precedence rule ends an anger already in flight.
			exit := state.TickCount >= swarm.DefendUntilTick || nest == nil ||
				nestDefenseSuppressed(state, nest, swarm)
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

		// PROVISION — entry: a full load with a live nest. Carry the brood home; deposit on
		// arrival (satiation drops to deposit_satiation, the post-provision level); a trip over
		// the timeout drops the brood (a bool-carry can't deadlock). FULL is the same threshold the
		// forage block hunts toward, so there is no gap between stopping the hunt and heading home.
		if swarm.Phase != "homing" && swarm.Satiation >= predatorFullSatiation && swarm.NestKey != "" && nest != nil {
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

	// FEED-PAUSE (#20): a predator PARKS on its kill for the feeding dwell. Slotted AFTER the nest
	// defending/homing block (a nest attack still preempts the meal) and BEFORE the individual/hunt
	// blocks. Re-emits a zero-length hold-leg at the jittered re-aim cadence (so the swarm re-checks
	// defend/home each think — responsive) — the swarm freezes IN SYNC (clients mirror the march;
	// origin==target → both arrival-clamps hold it). Determinism: FeedUntilTick is a deterministic
	// tick stamp set by the ledgered strike, so every client/handoff-authority holds-or-thinks alike.
	if swarm.FeedUntilTick > state.TickCount {
		cx, cy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
		m.emitLeg(state, swarm, species, cx, cy, 1.0, chunkSize, deltaTime)
		swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
		return true
	}

	// ANT COLONY BEHAVIOR (P3.2): scouts breadcrumb their walk and REGISTER anything
	// edible into the colony memory; hungry workers with nothing in VISION walk the
	// best-known trail hop-by-hop (the scout's stored route — files share one literal
	// polyline). Everything else falls through to the bee decline below, so dining,
	// provisioning and homing stay the verbatim shared machinery. Server-only reads;
	// the only outputs are ordinary legs.
	if species.CarrionForager {
		// Phase normalization FIRST (the bee_arena starve-sawtooth lesson): attractions
		// resolve BY PHASE and a fresh swarm is born at Phase "" — an un-normalized
		// worker would see "no food in vision" while standing on a feast.
		if swarm.Phase == "" || swarm.Phase == "idle" {
			swarm.Phase = "feeding"
		}
		nestKey, colonyNest := m.nearestColonyNest(state, swarm, species, chunkSize)
		if species.ColonyScout {
			// THE SENSOR (owner ruling: scouts are pure sensors): crumb the walk,
			// register nearby food, then decline below — the shared blocks feed and
			// wander it. Spawned scouts carry no NestKey → PROVISION never fires.
			m.scoutBreadcrumb(state, swarm, colonyNest, chunkSize)
			if nestKey != "" && colonyNest != nil {
				nx2 := float32(colonyNest.GridX) + 0.5
				ny2 := float32(colonyNest.GridY) + 0.5
				for _, h := range FindNearbyFood(state, swarm.Position, species.VisionRange,
					swarm.GetCurrentAttractions(species)) {
					// TRAILS ARE FOR FAR FOOD (the v3 lab finding): scouts constantly
					// re-registered the colony's own fungus garden, and Strength/(1+dist)
					// let the 5-cell mushrooms out-score the 48-cell bonanza 10:1 — every
					// "march" was a 3-cell hop inside the garden. Food within vision of
					// the NEST needs no trail by definition (workers at home already see
					// it); only beyond-garden finds enter colony memory.
					hdx, hdy := h.X-nx2, h.Y-ny2
					if hdx*hdx+hdy*hdy <= species.VisionRange*species.VisionRange {
						continue
					}
					isNew := registerCarrionSite(state, nestKey, int(h.X), int(h.Y),
						scoutRegisterStrength, state.ScoutPaths[swarm.ID])
					// Recruit on a FRESH site — or RELIGHT a known one whose trail
					// has lapsed (v9: coalescence keeps sites alive, so fresh-only
					// recruitment fired 4 times in 34 days).
					if isNew || !anyMarcherFor(state, nestKeyFor(int(h.X), int(h.Y))) {
						n := recruitWorkers(state, nestKey, int(h.X), int(h.Y), 5)
						if n > 0 {
							logger.Info("ANTLOG recruit nest=%s site=%d,%d workers=%d",
								nestKey, int(h.X), int(h.Y), n)
						}
					}
					logger.Info("ANTLOG register nest=%s site=%d,%d kind=%s routeLen=%d",
						nestKey, int(h.X), int(h.Y), h.Kind, len(state.ScoutPaths[swarm.ID]))
				}
			}
			// The sensor contract: scouts ALWAYS decline ownership — the shared forage/
			// wander blocks feed and move them. (With nest_occupant now link-only, the
			// bee decline below no longer catches them.)
			return false
		} else if swarm.Satiation < predatorFullSatiation && nestKey != "" {
			// THE WORKER'S MARCH, WITH COMMITMENT. The v2 lab exposed the oscillation
			// trap: pool trickle-regen re-captured every marcher at the garden's edge
			// (a 1-nectar blip in vision cancelled the trip, the blip drained, repeat)
			// — so no trail could ever cross the map. A worker now COMMITS to a site
			// (MarchTargets, server-only) and holds the trail until the site dies, it
			// ARRIVES (the site's own food enters vision → dining takes over), or a
			// full load sends it home; after the deposit it re-commits — that cycle IS
			// the visible trail.
			committed := ""
			if state.MarchTargets != nil {
				committed = state.MarchTargets[swarm.ID]
			}
			mem := state.ColonyMemory[nestKey]
			var site *entities.CarrionSite
			if committed != "" {
				if mem != nil {
					for _, s2 := range mem.Sites {
						if nestKeyFor(s2.GridX, s2.GridY) == committed {
							site = s2
							break
						}
					}
				}
				if site == nil {
					delete(state.MarchTargets, swarm.ID) // the site died — release
				}
			}
			visionHits := FindNearbyFood(state, swarm.Position, species.VisionRange,
				swarm.GetCurrentAttractions(species))
			if site == nil && len(visionHits) == 0 {
				if site = bestKnownSite(mem, swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)); site != nil {
					if state.MarchTargets == nil {
						state.MarchTargets = make(map[string]string)
					}
					state.MarchTargets[swarm.ID] = nestKeyFor(site.GridX, site.GridY)
					logger.Info("ANTLOG commit swarm=%s site=%d,%d", swarm.ID, site.GridX, site.GridY)
				}
			}
			if site != nil {
				sx2, sy2 := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
				ddx, ddy := float32(site.GridX)+0.5-sx2, float32(site.GridY)+0.5-sy2
				if ddx*ddx+ddy*ddy <= species.VisionRange*species.VisionRange && len(visionHits) > 0 {
					// TRAFFIC REINFORCEMENT (the ACO other-half, v6 finding): an
					// arrival re-vouches for the site, so a trail SUSTAINS ITSELF
					// while the food lasts — scouts only have to LIGHT it. When the
					// food is gone arrivals stop and decay retires the trail (the
					// designed migrate-on-depletion dynamic).
					registerCarrionSite(state, nestKey, site.GridX, site.GridY,
						workerReinforceStrength, nil)
					delete(state.MarchTargets, swarm.ID) // arrived: dine (decline below)
					logger.Info("ANTLOG arrive swarm=%s site=%d,%d", swarm.ID, site.GridX, site.GridY)
				} else {
					tx, ty := nextTrailPoint(site, sx2, sy2)
					swarm.TargetPreyID = ""
					m.emitLeg(state, swarm, species, tx, ty, 1.0, chunkSize, deltaTime)
					swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
					return true
				}
			}
		}
	}

	// NECTAR FORAGERS (bees): a NEST species with an EMPTY prey list never hunts — while
	// below the full-load point it declines ownership (the centipede carrion-first pattern)
	// so the SHARED forage block dines on flower nectar; satiation then climbs to
	// predatorFullSatiation and the PROVISION block above carries the load home (brood +
	// honey). Defend/homing/feed-pause above still preempt. At/above full with no live nest
	// (orphan), it falls through to the home-range rest-wander below, like orphan wasps.
	if p.NestOccupant != "" && len(p.Prey) == 0 && swarm.Satiation < predatorFullSatiation {
		// PHASE NORMALIZATION AT THE HANDOFF (the bee_arena starve-sawtooth root cause): the
		// shared forage block reads attractions BY PHASE, and nest species skip the standard
		// phase machine (match.go — the sated→"reproducing" flip would strand them). A fresh
		// resident is born at Phase "" and would look up attractions for "" forever — starving
		// beside a full flower field. Default to "feeding" here, exactly like the centipede
		// think's own "" → feeding default; deposits already set "feeding" on arrival.
		if swarm.Phase == "" || swarm.Phase == "idle" {
			swarm.Phase = "feeding"
		}
		return false
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
	//
	// FORAGE ceiling: a NEST predator hunts until it has a full load (predatorFullSatiation) — the SAME
	// point that sends it home to provision — so whenever it isn't full it re-acquires the nearest prey
	// (a lost/elusive prey just means "pick the next one"), and it never sits idle while still hungry. That
	// closes the old dead zone (too fed to start a hunt at 45, not full enough to home at 100). Free-roaming
	// individuals (centipede) keep their own hunt_satiation_threshold so they still get rest-wander beats.
	huntCeiling := p.HuntSatiationThreshold
	if p.NestOccupant != "" {
		huntCeiling = predatorFullSatiation
	}
	hunting := swarm.TargetPreyID != ""
	if !hunting && swarm.Satiation < huntCeiling {
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

// (The legacy autonomous centre-distance strike `checkPredationStrike` was removed in Phase 2 — the
// authority CLIENT now selects which individual flies are struck, using real per-bug positions, and reports
// them via handlePredationStrike → applyPredationStrike. The server has only swarm centres, so it can no
// longer choose individual victims.)

// applyPredationStrike APPLIES a chosen set of victim ids (the caller owns SELECTION): kill via the
// shared melee path, record stats, advance the predator's cooldown/hunt-progress + satiation, telegraph.
// Shared by the legacy autonomous centre-strike (checkPredationStrike) and the Phase-2 client-reported
// PredationStrike handler. victimX/victimY (optional) are the per-victim world positions for the
// display-only snatch — nil falls back to the predator-centre flash. Returns the number actually removed.
func (m *Match) applyPredationStrike(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	predator *entities.SwarmState,
	predatorSpecies *entities.BugSpecies,
	prey *entities.SwarmState,
	ids []int,
	victimX, victimY []float32,
	chunkSize int,
) int {
	p := predatorSpecies.Predation
	if p == nil {
		return 0
	}
	preySpecies := state.Species[prey.SpeciesID]
	removed := m.killBugsInSwarm(logger, dispatcher, state, prey, preySpecies, ids,
		predator.WorldX(chunkSize), predator.WorldY(chunkSize), chunkSize)
	if len(removed) == 0 {
		return 0
	}
	state.Stats.recordDeath(prey.SpeciesID, DeathPredation, len(removed))
	state.Stats.recordPredation(predator.SpeciesID, prey.SpeciesID, len(removed))

	predator.LastStrikeTick = state.TickCount
	predator.HuntStartTick = state.TickCount // a kill is progress: the timeout re-arms
	predator.Satiation += p.FeedPerKill * float32(len(removed))
	if predator.Satiation > 100 {
		predator.Satiation = 100
	}

	// FEED-PAUSE (#20): park on the kill for the dwell. NextThinkTick=now forces a prompt re-think so the
	// park begins AT the kill (a tight, readable beat) instead of ~1s later along the stale hunt-leg.
	// Per-species; 0 = off. (A load-filling kill that flips a nest predator to "homing" skips the park —
	// the home trip is its own pause — but the corpse telegraph below still fires on every kill.)
	if p.FeedPauseTicks > 0 {
		predator.FeedUntilTick = state.TickCount + p.FeedPauseTicks
		predator.NextThinkTick = state.TickCount
	}

	// Strike telegraph (display-only): the snatch flash + THWACK. Phase 2 carries the victim positions
	// so the snatch plays AT each eaten fly (individual strike reads on screen); nil = predator-centre.
	// #20: carry the prey's carcass + the feeding-dwell seconds so the client shows + fades a corpse.
	tickRate := state.Config.TickRate
	if tickRate <= 0 {
		tickRate = 10
	}
	carcass := ""
	if preySpecies != nil {
		carcass = preySpecies.CarcassItem
	}
	feedPauseSecs := float32(p.FeedPauseTicks) / float32(tickRate)
	m.broadcastBugStrikeTelegraph(dispatcher, state, predator, victimX, victimY, carcass, feedPauseSecs, chunkSize)

	logger.Info("Predation: %s struck %s (-%d, satiation %.0f)",
		predator.ID, prey.ID, len(removed), predator.Satiation)
	return len(removed)
}

// handlePredationStrike validates + applies an AUTHORITY-reported individual-fly strike (OpCode 105).
// The authority client did the SELECTION (it has per-bug positions; the server has only centres); the
// server is the gate and applies the kill via the shared path so followers/late-joiners sync through the
// relayed BUG_REMOVED. Idempotent-ish: the server cooldown throttles the authority's per-tick re-sends.
func (m *Match) handlePredationStrike(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	senderID string,
	msg PredationStrikeMessage,
) {
	if state.CurrentZone == nil {
		return
	}
	zone := state.GetOrCreateZone(state.CurrentZone.ZoneID)
	// AUTHORITY ONLY — the authority drives strikes; ignore everyone else (anti-cheat + de-dupe).
	if zone.AuthorityUserID != senderID {
		logger.Warn("Ignoring predation strike from non-authority %s (authority is %s)", senderID, zone.AuthorityUserID)
		return
	}
	chunkSize := state.Config.ChunkSize

	predator, ok := state.Swarms[msg.PredatorSwarmID]
	if !ok || predator.Count <= 0 {
		return
	}
	prey, ok := state.Swarms[msg.PreySwarmID]
	if !ok || prey.Count <= 0 {
		return
	}
	predSpecies := state.Species[predator.SpeciesID]
	if predSpecies == nil || predSpecies.Predation == nil {
		return
	}
	p := predSpecies.Predation
	if !containsString(p.Prey, prey.SpeciesID) { // predator must actually hunt this prey species
		return
	}
	if state.TickCount-predator.LastStrikeTick < p.StrikeCooldownTicks { // server cooldown is authoritative
		return
	}
	if predator.FeedUntilTick > state.TickCount { // #20: mid-feed — the predator is parked, ignore strike re-sends
		return
	}
	// Loose centre-range sanity (the server has only centres): a legitimate individual strike has the two
	// centres within StrikeRadius + both cloud radii. Rejects obviously-bogus reports, not real ones.
	dx := predator.WorldX(chunkSize) - prey.WorldX(chunkSize)
	dy := predator.WorldY(chunkSize) - prey.WorldY(chunkSize)
	maxR := p.StrikeRadius + predator.Radius + prey.Radius
	if dx*dx+dy*dy > maxR*maxR {
		return
	}

	kills := p.KillsPerStrike
	if kills <= 0 {
		kills = 1
	}
	// Keep only ids ALIVE in the prey swarm (a victim may have died between the authority's select and
	// now — e.g. natural death), clamp to KillsPerStrike. Victim positions ride along for the snatch.
	hasPos := len(msg.BugX) == len(msg.BugIDs) && len(msg.BugY) == len(msg.BugIDs)
	ids := make([]int, 0, len(msg.BugIDs))
	var vx, vy []float32
	if hasPos {
		vx = make([]float32, 0, len(msg.BugIDs))
		vy = make([]float32, 0, len(msg.BugIDs))
	}
	for i, id := range msg.BugIDs {
		if len(ids) >= kills {
			break
		}
		if !prey.IsBugAlive(id) {
			continue
		}
		ids = append(ids, id)
		if hasPos {
			vx = append(vx, msg.BugX[i])
			vy = append(vy, msg.BugY[i])
		}
	}
	if len(ids) == 0 {
		return
	}
	m.applyPredationStrike(logger, dispatcher, state, predator, predSpecies, prey, ids, vx, vy, chunkSize)
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

	// Phase 2: tag a HUNT leg with the prey + strike params so the authority client can run the
	// individual-fly strike selection. swarm.TargetPreyID is set only while actively hunting (incl. a
	// centipede gnaw); cleared on flee/home/wander/hunt-end — so every non-hunt leg sends empty/0.
	targetPreyID := ""
	strikeRadius, killsPerStrike, strikeCooldownTicks := 0, 0, 0
	if swarm.TargetPreyID != "" && species.Predation != nil {
		targetPreyID = swarm.TargetPreyID
		strikeRadius = toFixed(species.Predation.StrikeRadius)
		killsPerStrike = species.Predation.KillsPerStrike
		strikeCooldownTicks = int(species.Predation.StrikeCooldownTicks)
	}

	if state.CurrentZone != nil {
		state.AddSwarmTargetEvent(
			state.CurrentZone.ZoneID, swarm.ID,
			toFixed(originX), toFixed(originY),
			toFixed(targetX), toFixed(targetY),
			toFixed(species.BaseSpeed*swarm.EffectiveSpeedMult()*deltaTime),
			targetPreyID, strikeRadius, killsPerStrike, strikeCooldownTicks,
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

// broadcastBugStrikeTelegraph is the predation-strike telegraph (display-only): the snatch/THWACK plays
// AT each victim position (victimX/victimY) so an individual-fly strike reads on screen; nil victims fall
// back to the predator-centre flash. Chunk-scoped on the predator's chunk like the other telegraphs.
func (m *Match) broadcastBugStrikeTelegraph(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	predator *entities.SwarmState,
	victimX, victimY []float32,
	carcassItem string, // #20: the dead_<prey> the client shows at each victim (display-only)
	feedPauseSecs float32, // #20: how long the corpse holds before fading (the feeding dwell)
	chunkSize int,
) {
	msg := BugTelegraphMessage{SwarmID: predator.ID, Kind: "strike", VictimX: victimX, VictimY: victimY,
		CarcassItem: carcassItem, FeedPauseSecs: feedPauseSecs}
	m.broadcastToChunk(dispatcher, state, predator.Position.ChunkX, predator.Position.ChunkY, OpCodeBugTelegraph, msg)
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
