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
	stingTelegraphTicks = 12 // 1.2s wind-up between the telegraph flash and the sting — the fairness window
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
	// Per-swarm cooldown (attack_cooldown is in SECONDS; 10Hz)
	cooldownTicks := int64(species.AttackCooldown * 10)
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
	if species.AttackIsSting && len(player.Equipment) > 1 {
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

// handleBugPlayerStrike applies a PER-INDIVIDUAL sting the AUTHORITY detected. The server holds only swarm
// CENTRES, so it can't tell which individual is actually next to the player — the old center-based
// checkBugAttacks stung anyone near the CENTROID (the "phantom" hit). The authority (which has per-bug
// positions) reports the attacker(s); the server re-gates through the funnel so damage stays authoritative.
// Mirrors handlePredationStrike.
func (m *Match) handleBugPlayerStrike(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	senderID string,
	msg BugPlayerStrikeMessage,
) {
	if state.CurrentZone == nil {
		return
	}
	zone := state.GetOrCreateZone(state.CurrentZone.ZoneID)
	if zone.AuthorityUserID != senderID {
		return // AUTHORITY ONLY (anti-cheat + de-dupe)
	}
	swarm, ok := state.Swarms[msg.SwarmID]
	if !ok || swarm.Count <= 0 {
		return
	}
	species := state.Species[swarm.SpeciesID]
	if species == nil || species.AttackDamage <= 0 {
		return
	}
	player, ok := state.Players[msg.PlayerID]
	if !ok || player == nil {
		return
	}
	// Full authoritative gates the authority skipped (it reports loosely): defend-only (bees), subdued,
	// and nocturnal (any night-active attacker can't sting by day).
	if species.StingsOnlyDefending && swarm.Phase != "defending" {
		return
	}
	if species.Nocturnal && !isNightForHunting(state) {
		return
	}
	if swarmSubdued(swarm, species) {
		return
	}
	// Loose centre-range sanity with the server's FINE player pos (mirrors handlePredationStrike) — rejects
	// obviously-bogus reports without needing the per-bug positions the server lacks.
	cs := state.Config.ChunkSize
	dx := player.WorldX(cs) - swarm.WorldX(cs)
	dy := player.WorldY(cs) - swarm.WorldY(cs)
	maxR := stingRange + swarm.Radius
	if dx*dx+dy*dy > maxR*maxR {
		return
	}
	// Two-beat telegraph: don't sting on contact — ARM a telegraphed sting. Flash the wind-up NOW and schedule
	// the hit for stingTelegraphTicks later (processPendingStings), so the player can dodge (i-frames) or step
	// out before it lands. A pending sting OR the post-sting cooldown blocks re-arming, so it can't be spammed.
	if swarm.PendingStingTick > 0 {
		return // already wound up against someone
	}
	cooldownTicks := int64(species.AttackCooldown * 10)
	if cooldownTicks <= 0 {
		cooldownTicks = 20
	}
	if state.TickCount-swarm.LastAttackTick < cooldownTicks {
		return // still on cooldown from the last sting
	}
	// At least one reported attacker must still be alive (guards a stale report before we commit a wind-up).
	alive := false
	for _, id := range msg.BugIDs {
		if swarm.IsBugAlive(id) {
			alive = true
			break
		}
	}
	if !alive {
		return
	}
	swarm.PendingStingPlayer = msg.PlayerID
	swarm.PendingStingTick = state.TickCount + stingTelegraphTicks
	m.broadcastBugTelegraph(dispatcher, state, swarm, "windup", state.Config.ChunkSize)
}

// processPendingStings fires telegraphed stings whose wind-up has elapsed (the SECOND beat). At fire time it
// re-gates: the target must still exist and the swarm centre must still be within loose sting range (step-out
// counterplay), then applyBugAttackToPlayer applies the FINAL gates (dodge i-frames, shared invuln, per-swarm
// cooldown, subdued, sting-immunity) + damage. Runs every tick; sorted iteration keeps this sim-inert pass
// reproducible.
func (m *Match) processPendingStings(logger runtime.Logger, dispatcher runtime.MatchDispatcher, state *WorldState) {
	cs := state.Config.ChunkSize
	for _, swarmID := range sortedStringKeys(state.Swarms) {
		swarm := state.Swarms[swarmID]
		if swarm == nil || swarm.PendingStingTick == 0 || state.TickCount < swarm.PendingStingTick {
			continue
		}
		playerID := swarm.PendingStingPlayer
		swarm.PendingStingTick = 0
		swarm.PendingStingPlayer = ""

		if swarm.Count <= 0 {
			continue
		}
		species := state.Species[swarm.SpeciesID]
		if species == nil || species.AttackDamage <= 0 {
			continue
		}
		player, ok := state.Players[playerID]
		if !ok || player == nil {
			continue
		}
		// Step-out counterplay: if the swarm centre has drifted out of loose sting range, the sting whiffs.
		dx := player.WorldX(cs) - swarm.WorldX(cs)
		dy := player.WorldY(cs) - swarm.WorldY(cs)
		maxR := stingRange + swarm.Radius
		if dx*dx+dy*dy > maxR*maxR {
			continue
		}
		m.applyBugAttackToPlayer(logger, dispatcher, state, swarm, species, playerID, player, species.AttackDamage)
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

