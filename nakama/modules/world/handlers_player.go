package world

import (
	"encoding/json"
	"math"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Player HP v1 (architecture_swarm_sync.md §14): sim-inert display state. Bug AI reads
// player CELLS (already on the ledger); HP rides the presence-TARGETED PlayerDamage
// message (94) — an unfiltered broadcast would knock back every client in the zone.

const (
	playerInvulnTicks   = 10 // 1s shared across ALL attackers
	dodgeInvulnTicks    = 5  // 0.5s i-frame window a dodge-roll grants
	regenDelayTicks   = 100 // regen starts 10s after the last damage
	regenIntervalTick = 300 // +1 HP per 30s
	stingRange        = 1.5 // "standing in them" — ambient wasps only sting at contact
)

// applyBugAttackToPlayer lands one bug attack: per-swarm attack cooldown + the shared
// 1s invuln gate, HP decrement, the targeted damage message with a knockback vector,
// and the faint (HP refill + teleport to spawn — the client snaps itself on receipt).
func (m *Match) applyBugAttackToPlayer(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	userID string,
	player *PlayerState,
	damage int,
) bool {
	// Per-species attack profile (cooldown, sting-class). AttackProfile is never nil for a caller that got
	// here (they hold an atk), but guard defensively.
	atk := species.AttackProfile()
	cd := float32(2.0)
	if atk != nil && atk.CooldownSecs > 0 {
		cd = atk.CooldownSecs
	}
	// Per-swarm cooldown (cooldown_secs → ticks; 10Hz)
	cooldownTicks := int64(cd * 10)
	if cooldownTicks <= 0 {
		cooldownTicks = 20
	}
	if state.TickCount-swarm.LastAttackTick < cooldownTicks {
		return false
	}
	// Shared invuln window (across all attackers)
	if state.TickCount-player.LastDamageTick < playerInvulnTicks {
		return false
	}
	// Dodge i-frames — a well-timed roll negates the sting (separate window; doesn't gate regen).
	if state.TickCount < player.DodgeInvulnUntilTick {
		return false
	}

	// SUBDUED (§C belt-and-braces): every bug attack funnels through here (checkBugAttacks +
	// the centipede bite are the only callers), so a calmed swarm cannot land damage even if
	// an upstream entry check is missed later.
	if swarmSubdued(swarm, species) {
		return false
	}

	// STING IMMUNITY (the bee suit — the first armor damage hook): a sting_immune BODY piece
	// fully negates sting-class attacks (bees, wasps); bites (centipedes) still land. No HP
	// change, no knockback, no invuln burn — the cloud rages, the keeper works.
	if atk != nil && atk.IsSting && len(player.Equipment) > 1 {
		if def := state.Entities[player.Equipment[1]]; def != nil && def.StingImmune {
			return false
		}
	}

	swarm.LastAttackTick = state.TickCount
	player.LastDamageTick = state.TickCount
	player.HP -= damage
	if player.MaxHP <= 0 {
		player.MaxHP = 10 // pre-HP players (joined before this slice) heal up lazily
	}

	chunkSize := state.Config.ChunkSize
	dx := player.WorldX(chunkSize) - swarm.WorldX(chunkSize)
	dy := player.WorldY(chunkSize) - swarm.WorldY(chunkSize)
	distSq := dx*dx + dy*dy
	if distSq > 0.0001 {
		l := float32(1.0 / math.Sqrt(float64(distSq)))
		dx, dy = dx*l, dy*l
	} else {
		dx, dy = 0, 1
	}

	msg := PlayerDamageMessage{
		HP: player.HP, MaxHP: player.MaxHP, Damage: damage,
		SourceSpecies: swarm.SpeciesID,
		KnockDX:       dx, KnockDY: dy,
	}

	if player.HP <= 0 {
		// FAINT: refill + respawn, no item loss (v1). Default = the zone spawn; if this character
		// has slept in a bed IN THIS zone, wake at that home instead (Minecraft-style).
		spawnX, spawnY := float32(256), float32(256)
		zoneID := ""
		if state.CurrentZone != nil {
			spawnX = float32(state.CurrentZone.SpawnPoint[0])
			spawnY = float32(state.CurrentZone.SpawnPoint[1])
			zoneID = state.CurrentZone.ZoneID
		}
		if player.HomeZone != "" && player.HomeZone == zoneID {
			spawnX, spawnY = player.HomeX, player.HomeY
		}
		player.HP = player.MaxHP
		player.SetWorldPosition(spawnX, spawnY, chunkSize)
		msg.Faint = true
		msg.HP = player.HP
		msg.RespawnX, msg.RespawnY = spawnX, spawnY
		logger.Info("Player %s fainted (stung by %s) — respawned", userID, swarm.SpeciesID)
	}

	m.sendPlayerDamage(dispatcher, state, userID, msg)
	return true
}

// checkBugAttacks runs per tick for attack-capable species (attack_damage > 0): any
// player within sting range of the swarm center takes the hit. Ambient swarms only
// sting players standing IN them; chasing happens via the defending/surge legs.
func (m *Match) checkBugAttacks(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	chunkSize int,
) {
	if species.AttackDamage <= 0 || swarm.Count <= 0 {
		return
	}
	// Gentle-until-provoked (bees): only a DEFENDING colony stings. Wasps (flag unset) keep
	// their ambient contact sting.
	if species.StingsOnlyDefending && swarm.Phase != "defending" {
		return
	}
	// FUNNEL 1 (§C): a subdued swarm doesn't ambient-sting — walk through the calm cloud.
	if swarmSubdued(swarm, species) {
		return
	}
	sx, sy := swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)
	for userID, player := range state.Players {
		dx := player.WorldX(chunkSize) - sx
		dy := player.WorldY(chunkSize) - sy
		if dx*dx+dy*dy > stingRange*stingRange {
			continue
		}
		if m.applyBugAttackToPlayer(logger, dispatcher, state, swarm, species, userID, player, species.AttackDamage) {
			return // one victim per swarm per tick (the cooldown re-arms anyway)
		}
	}
}


// handlePlayerDodge grants a brief server-authoritative i-frame window so a well-timed dodge-roll negates an
// incoming sting. Movement itself stays client-predicted + reconciled.
func (m *Match) handlePlayerDodge(state *WorldState, senderID string) {
	if player, ok := state.Players[senderID]; ok && player != nil {
		player.DodgeInvulnUntilTick = state.TickCount + dodgeInvulnTicks
	}
}

// processPlayerRegen: +1 HP per 30s, starting 10s after the last damage. The damage-0
// echo keeps the victim's hearts UI in step.
func (m *Match) processPlayerRegen(dispatcher runtime.MatchDispatcher, state *WorldState) {
	if state.TickCount%regenIntervalTick != 0 {
		return
	}
	for userID, player := range state.Players {
		if player.MaxHP <= 0 {
			player.MaxHP, player.HP = 10, 10 // lazy init for pre-slice players
			continue
		}
		if player.HP >= player.MaxHP {
			continue
		}
		if state.TickCount-player.LastDamageTick < regenDelayTicks {
			continue
		}
		player.HP++
		m.sendPlayerDamage(dispatcher, state, userID, PlayerDamageMessage{
			HP: player.HP, MaxHP: player.MaxHP, Damage: 0,
		})
	}
}

// sendPlayerDamage targets the victim's presence ONLY (HP is private state; knockback
// on every client would shove the whole zone). The sendWorldError pattern.
func (m *Match) sendPlayerDamage(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg PlayerDamageMessage,
) {
	if dispatcher == nil {
		return // unit tests drive the state machine without a dispatcher
	}
	presence, ok := state.Presences[userID]
	if !ok || presence == nil {
		return
	}
	data, _ := json.Marshal(msg)
	dispatcher.BroadcastMessage(OpCodePlayerDamage, data, []runtime.Presence{presence}, nil, true)
}

