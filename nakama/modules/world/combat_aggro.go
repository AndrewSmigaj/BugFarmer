package world

import "bugfarmer/entities"

// combat_aggro.go — proximity pursuit. The "how an attack-capable bug decides to come at you" layer, separate
// from predator hunting (predation.go) and from the damage subsystem (bug_attack.go). Ranges are per-species
// (attack.aggro_enter / aggro_exit); the surge-lunge trigger + choreography live in centipede.go.

// aggroPlayerThink is the proximity-aggro chase. Called EVERY tick for a non-actionState attack-capable swarm
// (so it notices a player promptly — not gated behind a 3-5 s wander leg). It keeps a STICKY target with
// hysteresis (attack.aggro_enter → aggro_exit) and emits a chase leg only on target-acquire or on the re-aim
// cadence (so no per-tick leg spam). Centipedes use this too: it closes the gap to attack.lunge.trigger_range,
// then the per-tick surge trigger takes over (it runs first, sets actionActive, and this isn't called during a
// surge). Defenders (aggro_enter == 0, e.g. bees/ants) don't proximity-chase — nest defence handles them.
// Per-species ranges from the attack{} profile; server-authoritative leg → deterministic. Returns true when it
// OWNS the think (has a target).
func (m *Match) aggroPlayerThink(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
	deltaTime float32,
) bool {
	atk := species.AttackProfile()
	if atk == nil || atk.AggroEnter <= 0 || swarm.Count <= 0 ||
		(species.Nocturnal && !isNightForHunting(state)) || swarmSubdued(swarm, species) {
		swarm.AggroTargetID = ""
		return false
	}
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)

	// Keep the current target while it stays inside EXIT; otherwise try to acquire the nearest within ENTER.
	var tx, ty float32
	acquired := false
	if swarm.AggroTargetID != "" {
		if p, ok := state.Players[swarm.AggroTargetID]; ok && p != nil {
			px, py := p.WorldX(chunkSize), p.WorldY(chunkSize)
			if dx, dy := px-sx, py-sy; dx*dx+dy*dy <= atk.AggroExit*atk.AggroExit {
				tx, ty = px, py
			} else {
				swarm.AggroTargetID = "" // left the exit radius
			}
		} else {
			swarm.AggroTargetID = "" // gone
		}
	}
	if swarm.AggroTargetID == "" {
		enter := atk.AggroEnter
		if species.VisionRange > 0 && species.VisionRange < enter {
			enter = species.VisionRange // a short-sighted crawler only notices you up close
		}
		if pid, px, py, found := m.nearestPlayer(state, sx, sy, enter); found {
			swarm.AggroTargetID = pid
			tx, ty = px, py
			acquired = true
		}
	}
	if swarm.AggroTargetID == "" {
		return false // nobody to chase → fall through to normal think
	}

	// Emit a chase leg on ACQUIRE (prompt) or on the re-aim cadence; otherwise ride the current leg.
	if acquired || state.TickCount >= swarm.NextThinkTick {
		// HOW FAST the cloud closes/hovers: attack.aggro_speed_mult is the explicit knob (base_speed × this
		// must beat the player's walk or the swarm trails and bumbles). Falls back to the predator hunt speed,
		// then 1.4, for un-migrated species. Same deterministic leg either way — only the speed differs.
		mult := float32(1.4)
		if species.Predation != nil && species.Predation.HuntSpeedMult > 0 {
			mult = species.Predation.HuntSpeedMult
		}
		if atk.AggroSpeedMult > 0 {
			mult = atk.AggroSpeedMult
		}
		// Grounded attackers clamp the chase to a reachable point (path around walls, not through them);
		// fliers (FliesOverFences) aim straight.
		if !species.FliesOverFences {
			tx, ty, _, _, _ = entities.RaycastClampWithBlock(sx, sy, tx, ty, func(x, y float32) bool {
				return state.IsBlockedForSpecies(x, y, species)
			})
		}
		swarm.TargetPreyID = ""
		m.emitLeg(state, swarm, species, tx, ty, mult, chunkSize, deltaTime)
		swarm.NextThinkTick = state.TickCount + huntReaimMinTicks + state.Rng.Int63n(huntReaimJitter)
	}
	return true
}
