package world

import (
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// The centipede's per-bug brain — serpentine wander, telegraphed lunge at the player,
// prey hunt — now runs on the CLIENT, one brain per pack member (movement_style
// "centipede"; architecture_swarm_sync.md §14). The ONLY centipede behavior left on the
// server is the GNAW: chewing through a blocking gnawable fence to reach penned prey. It
// stays here because it MUTATES the world (it needs the occupant/Gnawable data and owns
// the break), so it must be authority-driven + ledgered like every other world mutation.
//
// The gnaw is a per-swarm ActionState ("gnaw") started from the THINK path when a hunt
// leg is clamped by a gnawable blocker (predation.go). While chewing, the swarm owns the
// tick (dispatched in match.go before the think gate); processGnaw damages the fence
// every centGnawInterval ticks through its own GnawDamage pool and finishes with the
// shared breakOccupantAt. Being SUBDUED (smoke) stops a gnaw (§C funnel).

const (
	centGnawInterval = 80  // ticks between gnaw damage (fence_wood HP 2 → 16s)
	centGnawCooldown = 600 // armed on ABANDONED gnaws only
	centGnawTimeout  = 900 // safety: a 90s gnaw that went nowhere abandons
)

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
	// §C: the single choke point for STARTING a gnaw — a subdued centipede doesn't chew.
	if swarmSubdued(swarm, species) {
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

	// §C (the mid-gnaw case): smoke lands while it's ALREADY chewing → it stops. Damage
	// dealt so far stays in the gnaw pool; no cooldown (being calmed is not an abandon).
	if swarmSubdued(swarm, species) {
		m.endGnaw(state, swarm, false)
		return false
	}

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
