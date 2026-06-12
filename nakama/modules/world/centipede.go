package world

import (
	"fmt"
	"math"
	"math/rand"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// The centipede (architecture_swarm_sync.md §14): an "individual"-category swarm
// that reuses combat/catch/caps/sync wholesale. "Individual" means GROUND CRAWLER
// WITH AN ACTION-STATE MACHINE — swarm sizes are data (max_swarm_size, now 1-3: a
// small KNOT of centipedes shares one center and lunges together; merge/split stay
// disabled for the category, so a full knot's litter mints a new swarm instead —
// see reproduceSwarm). The ActionState machine (windup → surge → recover, plus gnaw)
// runs PER TICK before the think gate — surges are 25 ticks vs 8-30-tick thinks —
// and owns the swarm while active. All outputs are ordinary legs + the existing
// damage/break paths.
//
// Doc rule: Phase = what it WANTS (the standard feeding/reproducing lifecycle — it
// parks at carrion and breeds there); ActionState = what it's forcibly DOING.

const (
	centWindupTicks    = 8   // 0.8s telegraph freeze
	centSurgeMaxTicks  = 25  // surge flight cap
	centRecoverTicks   = 20  // post-lunge backoff
	centSurgeCooldown  = 50  // 5s between lunges
	centSurgeSpeedMult = 4.8 // 1.6 base × 4.8 = 7.7 u/s lunge (player walks 5 — the
	// review's intended flight speed; ×3.5 was computed off the WASP's 2.2 base and
	// left the lunge barely faster than a walking player)
	centSurgeLead      = 0.8 // half-lead: aim = pos + velocity × flight × this
	centBiteRange      = 1.6 // absorbs the velocity-sample error
	centTriggerRange   = 5.0 // player this close → windup
	centDeAggroRange   = 12.0
	centGnawInterval   = 80  // ticks between gnaw damage (fence_wood HP 2 → 16s)
	centGnawCooldown   = 600 // armed on ABANDONED gnaws only
	centGnawTimeout    = 900 // safety: a 90s gnaw that went nowhere abandons
	centWanderTurnMax  = 60.0 * math.Pi / 180.0
	centWanderDistMin  = 4.0
	centWanderDistMax  = 7.0
	centEscapeStreak   = 3 // fully-clamped legs before a free 360° re-roll
)

// processActionState drives windup/surge/recover/gnaw per tick. Returns true while an
// action owns the swarm (the think gate is skipped). When idle (""), it also checks
// the surge TRIGGER (per-tick — a player can cross 5.0 between thinks).
func (m *Match) processActionState(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
	deltaTime float32,
) bool {
	switch swarm.ActionState {
	case "windup":
		if state.TickCount >= swarm.ActionUntilTick {
			m.launchSurge(state, swarm, species, chunkSize, deltaTime)
		}
		return true

	case "surge":
		// Per-tick bite check during flight: range AND line-of-sight (a clamped surge
		// ends ≤1.5 from a player hugging the far side of a fence — a through-fence
		// bite would silently void "stone is the answer").
		sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
		for userID, player := range state.Players {
			px, py := player.WorldX(chunkSize), player.WorldY(chunkSize)
			dx, dy := px-sx, py-sy
			if dx*dx+dy*dy > centBiteRange*centBiteRange {
				continue
			}
			_, _, _, _, blocked := entities.RaycastClampWithBlock(sx, sy, px, py, func(x, y float32) bool {
				return state.IsBlockedForSpecies(x, y, species)
			})
			if blocked {
				continue // a wall between us: no bite through it
			}
			if m.applyBugAttackToPlayer(logger, dispatcher, state, swarm, species, userID, player, species.AttackDamage) {
				m.startRecover(state, swarm, species, px, py, chunkSize, deltaTime)
				return true
			}
		}
		// Flight over (arrived or capped): recover away from the windup target.
		if state.TickCount >= swarm.ActionUntilTick || !swarm.HasTarget {
			tx, ty := swarm.WindupStartX, swarm.WindupStartY
			if p, ok := state.Players[swarm.WindupTargetID]; ok {
				tx, ty = p.WorldX(chunkSize), p.WorldY(chunkSize)
			}
			m.startRecover(state, swarm, species, tx, ty, chunkSize, deltaTime)
		}
		return true

	case "recover":
		if state.TickCount >= swarm.ActionUntilTick {
			swarm.ActionState = ""
			swarm.SurgeCooldownUntil = state.TickCount + centSurgeCooldown
			swarm.NextThinkTick = state.TickCount // re-decide immediately
		}
		return true

	case "gnaw":
		return m.processGnaw(logger, dispatcher, state, swarm, species, chunkSize)
	}

	// IDLE: the surge trigger (per-tick).
	if species.AttackDamage > 0 && state.TickCount >= swarm.SurgeCooldownUntil {
		sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
		if pid, px, py, found := m.nearestPlayer(state, sx, sy, centTriggerRange); found {
			swarm.ActionState = "windup"
			swarm.ActionUntilTick = state.TickCount + centWindupTicks
			swarm.WindupTargetID = pid
			swarm.WindupStartX, swarm.WindupStartY = px, py
			// Freeze: a zero-length leg (origin == target) — deterministic on both
			// sides (server Move no-ops at dist<0.5; client returns target at dist≤0).
			m.emitLeg(state, swarm, species, sx, sy, 1.0, chunkSize, deltaTime)
			m.broadcastBugTelegraph(dispatcher, state, swarm, "windup", chunkSize)
			return true
		}
	}
	return false
}

// launchSurge aims at the target's position AT LAUNCH plus a half-lead from their
// velocity over the windup window (player walk 5 u/s vs windup-start aim = a
// guaranteed miss; the lead clips straight-liners while direction-changers dodge —
// the intended skill check). The leg is CLAMPED (ground-bound) and rides ×3.5.
func (m *Match) launchSurge(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
	deltaTime float32,
) {
	player, ok := state.Players[swarm.WindupTargetID]
	if !ok {
		swarm.ActionState = ""
		swarm.SurgeCooldownUntil = state.TickCount + centSurgeCooldown
		return
	}

	px, py := player.WorldX(chunkSize), player.WorldY(chunkSize)
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)

	// Velocity over the windup (u/s) → lead by flight time × 0.8
	vx := (px - swarm.WindupStartX) / (float32(centWindupTicks) * 0.1)
	vy := (py - swarm.WindupStartY) / (float32(centWindupTicks) * 0.1)
	ddx, ddy := px-sx, py-sy
	dist := float32(math.Sqrt(float64(ddx*ddx + ddy*ddy)))
	surgeSpeed := species.BaseSpeed * centSurgeSpeedMult
	flight := dist / surgeSpeed
	tx := px + vx*flight*centSurgeLead
	ty := py + vy*flight*centSurgeLead

	// Ground-bound: the surge clamps at fences/water like every centipede leg.
	cx, cy := entities.RaycastClamp(sx, sy, tx, ty, func(x, y float32) bool {
		return state.IsBlockedForSpecies(x, y, species)
	})

	swarm.ActionState = "surge"
	swarm.ActionUntilTick = state.TickCount + centSurgeMaxTicks
	m.emitLeg(state, swarm, species, cx, cy, centSurgeSpeedMult, chunkSize, deltaTime)
}

func (m *Match) startRecover(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	awayFromX, awayFromY float32,
	chunkSize int,
	deltaTime float32,
) {
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	dx, dy := sx-awayFromX, sy-awayFromY
	dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
	if dist < 0.01 {
		dx, dy, dist = 1, 0, 1
	}
	const back = 4.0
	tx, ty := sx+dx/dist*back, sy+dy/dist*back
	cx, cy := entities.RaycastClamp(sx, sy, tx, ty, func(x, y float32) bool {
		return state.IsBlockedForSpecies(x, y, species)
	})
	swarm.ActionState = "recover"
	swarm.ActionUntilTick = state.TickCount + centRecoverTicks
	m.emitLeg(state, swarm, species, cx, cy, 1.0, chunkSize, deltaTime)
}

// tryStartGnaw is called from the THINK path when a seek/hunt leg was clamped: if the
// blocking cell is gnawable and the cooldown is clear, park and start chewing.
func (m *Match) tryStartGnaw(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	blockX, blockY int,
	chunkSize int,
	deltaTime float32,
) bool {
	if state.TickCount < swarm.GnawCooldownUntil {
		return false
	}
	def := m.occupantDefAt(state, blockX, blockY)
	if def == nil || def.World == nil || !def.World.Gnawable {
		return false
	}

	swarm.ActionState = "gnaw"
	swarm.GnawKey = fmt.Sprintf("%d,%d", blockX, blockY)
	swarm.GnawNextTick = state.TickCount + centGnawInterval
	swarm.ActionUntilTick = state.TickCount + centGnawTimeout // safety abandon
	// Park: zero-length leg at the clamp point (we're already there post-clamp)
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	m.emitLeg(state, swarm, species, sx, sy, 1.0, chunkSize, deltaTime)
	return true
}

// processGnaw: damage every centGnawInterval ticks through the GNAW pool (its own map
// — never BreakingState, whose owner-reset would let players "repair" by hitting);
// cracks ride the existing BreakProgress broadcast. Break completion = the shared
// breakOccupantAt with NO drops (gnawed fences are consumed) and NO cooldown
// (successful breaks CHAIN through layered walls — only abandons arm the cooldown,
// else wood-doubling substitutes for stone).
func (m *Match) processGnaw(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
) bool {
	var gx, gy int
	fmt.Sscanf(swarm.GnawKey, "%d,%d", &gx, &gy)

	def := m.occupantDefAt(state, gx, gy)
	if def == nil || def.World == nil || !def.World.Gnawable {
		// Target gone (player broke it / changed): back to thinking, no cooldown —
		// the world changed, that's not an abandon.
		m.endGnaw(state, swarm, false)
		return false
	}
	if state.TickCount >= swarm.ActionUntilTick {
		m.endGnaw(state, swarm, true) // a gnaw that went nowhere: abandon + cooldown
		return false
	}
	if state.TickCount < swarm.GnawNextTick {
		return true
	}

	// Chew.
	swarm.GnawNextTick = state.TickCount + centGnawInterval
	state.GnawDamage[swarm.GnawKey]++
	remaining := def.GetHP() - state.GnawDamage[swarm.GnawKey]

	progressMsg := BreakProgressMessage{
		GridX: gx, GridY: gy,
		CurrentHP: remaining, MaxHP: def.GetHP(),
		PlayerID: "swarm:" + swarm.ID, // display-only; the client never reads it
	}
	cx, cy, _, _ := GlobalToChunk(gx, gy)
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBreakProgress, progressMsg)
	m.broadcastBugTelegraph(dispatcher, state, swarm, "gnaw", chunkSize)

	if remaining <= 0 {
		delete(state.GnawDamage, swarm.GnawKey)
		m.breakOccupantAt(logger, dispatcher, state, gx, gy, false) // consumed, no drops
		m.endGnaw(state, swarm, false)                              // success CHAINS (no cooldown)
		logger.Info("Centipede %s gnawed through the fence at %s", swarm.ID, swarm.GnawKey)
		return false
	}
	return true
}

func (m *Match) endGnaw(state *WorldState, swarm *entities.SwarmState, abandoned bool) {
	if abandoned {
		swarm.GnawCooldownUntil = state.TickCount + centGnawCooldown
		delete(state.GnawDamage, swarm.GnawKey)
	}
	swarm.ActionState = ""
	swarm.GnawKey = ""
	swarm.NextThinkTick = state.TickCount // re-decide immediately
}

func (m *Match) occupantDefAt(state *WorldState, gx, gy int) *EntityDef {
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return nil
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil {
		return nil
	}
	return state.Entities[cell.Occupant.ID]
}

// centipedeWander: serpentine heading-constrained short legs (±60° per think,
// 4-7 cells) with the dead-end escape hatch — the heading updates to the ROLLED
// heading even when clamped, and 3 consecutive fully-clamped legs earn a free 360°
// re-roll (a stone dead-end would otherwise pin it facing the wall forever). Gnaw
// triggers ride the clamp result when the blocker is gnawable.
func (m *Match) centipedeWander(
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
	deltaTime float32,
) {
	// Graduated escape: serpentine ±60° in the open; once a leg clamps the turn
	// range widens to ±120°, and 3 clamped legs earn a free 360° roll — a pocketed
	// centipede frees itself in a handful of thinks instead of random-walking its
	// heading 5° at a time while visibly stuck.
	var turn float64
	switch {
	case swarm.ClampedLegStreak >= centEscapeStreak:
		turn = rand.Float64()*2*math.Pi - math.Pi // free 360°
		swarm.ClampedLegStreak = 0
	case swarm.ClampedLegStreak >= 1:
		turn = (rand.Float64()*2 - 1) * centWanderTurnMax * 2 // ±120°
	default:
		turn = (rand.Float64()*2 - 1) * centWanderTurnMax
	}
	heading := float64(swarm.WanderHeading) + turn
	swarm.WanderHeading = float32(heading)

	dist := centWanderDistMin + rand.Float64()*(centWanderDistMax-centWanderDistMin)
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	tx := sx + float32(math.Cos(heading)*dist)
	ty := sy + float32(math.Sin(heading)*dist)

	// Tether to home (wander_radius around HomePos)
	if species.WanderRadius > 0 {
		hx, hy := swarm.HomePos.WorldX(chunkSize), swarm.HomePos.WorldY(chunkSize)
		hdx, hdy := tx-hx, ty-hy
		if d := float32(math.Sqrt(float64(hdx*hdx + hdy*hdy))); d > species.WanderRadius {
			tx = hx + hdx/d*species.WanderRadius
			ty = hy + hdy/d*species.WanderRadius
		}
	}

	cx, cy, blockX, blockY, hit := entities.RaycastClampWithBlock(sx, sy, tx, ty, func(x, y float32) bool {
		return state.IsBlockedForSpecies(x, y, species)
	})

	// Clamped = the leg achieved less than HALF its intended distance (an absolute
	// <0.5 test let corner-jiggling reset the streak forever: partial 0.5-1.5 moves
	// against two walls while the heading random-walked too slowly to escape).
	mdx, mdy := cx-sx, cy-sy
	achieved := float64(mdx*mdx + mdy*mdy)
	intended := dist * dist * 0.25 // (dist/2)^2
	if achieved < intended {
		swarm.ClampedLegStreak++
	} else {
		swarm.ClampedLegStreak = 0
	}

	if hit && m.tryStartGnaw(state, swarm, species, blockX, blockY, chunkSize, deltaTime) {
		return
	}

	m.emitLeg(state, swarm, species, cx, cy, 1.0, chunkSize, deltaTime)
	swarm.NextThinkTick = state.TickCount + 20 + rand.Int63n(11) // short serpentine legs
}