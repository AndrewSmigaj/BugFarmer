package world

// THE CONDITION/SUBDUAL SYSTEM (§C) — the GENERAL calming mechanic of GDD §7.2/§7.3, implemented
// on the schema that was waiting for it: species catch_condition / condition_threshold /
// condition_decay / condition_tools + SwarmState.ConditionValue (0-100).
//
// The meter: ConditionValue rises when a subdual effect (smoke, calm spray; later chill/stun)
// is applied, and decays back to 0. ONE threshold — species.condition_threshold — means
// "subdued at/above this" for BOTH behavior (aggression goes quiet) AND catching; a bug is never
// placid-but-"too agitated to catch".
//
// Calm covers ALL THREE aggression funnels:
//   1. checkBugAttacks — the ambient contact sting (wasps) skips a subdued swarm.
//   2. The centipede ActionState — no windup START while subdued; a mid-windup/surge ABORTS to
//      recover; tryStartGnaw refuses; an already-gnawing centipede stops (damage kept, no
//      cooldown). The GDD's "smoke it to walk past it" play, complete.
//   3. Nest defense — THE PRECEDENCE RULE, stated once, applied at all three entries (the passive
//      proximity entry, recallNestDefenders, the exit hysteresis):
//          defense is suppressed while (the resident is SUBDUED) or (the nest is SMOKED).
//      Two fields, two honest meanings: the meter is the swarm's own state; NestState.
//      SmokedUntilTick is smoke lingering at the hive entrance while residents forage afield.
//   Belt-and-braces: applyBugAttackToPlayer (the single damage funnel) also refuses while subdued.
//
// Determinism: ConditionValue is SERVER-ONLY soft state (persisted via §P, never hashed). Its
// outputs — the ABSENCE of stings, surges, and defend legs — ride the existing event vocabulary
// identically on every client. Zero ledger surface.

import "bugfarmer/entities"

const (
	// conditionDefaultThreshold: subdued at/above this when the species doesn't set
	// condition_threshold. Sized with the default decay for playable windows: fill 95 (bee)
	// ≈ 27s, 90 (centipede) ≈ 25s, 85 (wasp) ≈ 22s, 80 (harmless) ≈ 20s.
	conditionDefaultThreshold = 40.0
	// conditionDefaultDecay: points/sec when the species doesn't set condition_decay.
	conditionDefaultDecay = 2.0
)

func conditionThreshold(species *entities.BugSpecies) float32 {
	if species != nil && species.ConditionThreshold > 0 {
		return species.ConditionThreshold
	}
	return conditionDefaultThreshold
}

func conditionDecayRate(species *entities.BugSpecies) float32 {
	if species != nil && species.ConditionDecay > 0 {
		return species.ConditionDecay
	}
	return conditionDefaultDecay
}

// swarmSubdued is THE one meaning of "subdued" — behavior checks and the catch gate both call
// this and nothing else.
func swarmSubdued(swarm *entities.SwarmState, species *entities.BugSpecies) bool {
	return swarm.ConditionValue >= conditionThreshold(species)
}

// applyConditionEffect applies one subdual effect to one swarm:
//
//	ConditionValue = max(current, condition_tools[effect] × power)
//
// Re-applying refreshes to the strongest tool's level — never spam-stacks past it. NO code
// default fill: a species without the effect key in condition_tools is IMMUNE to that effect
// (the map keeps its opt-in meaning; every calmable species carries an explicit entry in data).
// power <= 0 reads as 1.0 (effect_power is the tool-tier knob). Returns whether the effect did
// anything at all (for "nothing nearby to calm" feedback).
func applyConditionEffect(swarm *entities.SwarmState, species *entities.BugSpecies, effect string, power float32) bool {
	if swarm == nil || species == nil || swarm.Count <= 0 {
		return false
	}
	base, ok := species.ConditionTools[effect]
	if !ok || base <= 0 {
		return false // no key = this effect does nothing to this species
	}
	if power <= 0 {
		power = 1.0
	}
	fill := base * power
	if fill > 100 {
		fill = 100
	}
	if fill > swarm.ConditionValue {
		swarm.ConditionValue = fill
	}
	return true
}

// decayCondition runs in the per-tick lifecycle-meter block (with ReproduceCooldown et al).
func decayCondition(swarm *entities.SwarmState, species *entities.BugSpecies, deltaTime float32) {
	if swarm.ConditionValue <= 0 {
		return
	}
	swarm.ConditionValue -= conditionDecayRate(species) * deltaTime
	if swarm.ConditionValue < 0 {
		swarm.ConditionValue = 0
	}
}

// applyAreaCondition applies an effect to every swarm within reach of a cell (sorted iteration —
// the nests.go discipline; this path draws no RNG but stays ordered anyway). Returns how many
// swarms the effect actually touched.
func (m *Match) applyAreaCondition(state *WorldState, gx, gy int, reach float32, effect string, power float32) int {
	cs := state.Config.ChunkSize
	cx, cy := float32(gx)+0.5, float32(gy)+0.5
	reachSq := reach * reach
	touched := 0
	for _, id := range sortedStringKeys(state.Swarms) {
		swarm := state.Swarms[id]
		if swarm == nil || swarm.Count <= 0 {
			continue
		}
		dx, dy := swarm.WorldX(cs)-cx, swarm.WorldY(cs)-cy
		if dx*dx+dy*dy > reachSq {
			continue
		}
		if applyConditionEffect(swarm, state.Species[swarm.SpeciesID], effect, power) {
			touched++
		}
	}
	return touched
}

// nestDefenseSuppressed is the §C precedence rule as one reusable predicate:
// defense is suppressed while (the resident is subdued) OR (the nest is smoked).
func nestDefenseSuppressed(state *WorldState, nest *entities.NestState, resident *entities.SwarmState) bool {
	if nest != nil && nest.SmokedUntilTick > state.TickCount {
		return true
	}
	if resident != nil && swarmSubdued(resident, state.Species[resident.SpeciesID]) {
		return true
	}
	return false
}
