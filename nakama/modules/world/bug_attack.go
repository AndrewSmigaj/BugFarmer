package world

import (
	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// bug_attack.go — the bug→player ATTACK subsystem (the "dealing damage" side). ONE place that turns an
// authority-reported strike into player damage for EVERY attack style, through EVERY gate, so a new bug
// (of 50) can't skip a gate. The player-HP funnel (applyBugAttackToPlayer) + regen/dodge live in
// handlers_player.go (the "receiving damage" side). All behaviour comes from the per-species attack{}
// profile (entities.AttackConfig) — no per-species code here.

// attackSanityMargin: how far beyond the cloud a "strike" report is still accepted (cells). The AUTHORITY
// did the precise per-individual + LoS check against the player's exact position; this is only an anti-cheat
// backstop, so it's deliberately generous.
const attackSanityMargin = 1.0

// bugAttackAllowed is the shared authoritative gate every attack style passes through: defend-only (bees/ants),
// nocturnal-by-day, and subdued. (Per-swarm cooldown + shared invuln + dodge i-frames + sting-immunity live in
// applyBugAttackToPlayer, so they gate every path too.)
// peacefulZone reports whether the current zone is a peaceful OBSERVATION zone (bugs ignore the player).
// Read at all three combat gates so no attack style — sting, contact, lunge, or nest-defend — fires.
func peacefulZone(state *WorldState) bool {
	return state.CurrentZone != nil && state.CurrentZone.Peaceful
}

func (m *Match) bugAttackAllowed(state *WorldState, swarm *entities.SwarmState, species *entities.BugSpecies, atk *entities.AttackConfig) bool {
	if peacefulZone(state) {
		return false
	}
	if atk.OnlyDefending && swarm.Phase != "defending" {
		return false
	}
	if species.Nocturnal && !isNightForHunting(state) {
		return false
	}
	if swarmSubdued(swarm, species) {
		return false
	}
	return true
}

// handleBugPlayerStrike applies (or telegraphs) an attack the AUTHORITY client detected per-individual. The
// server holds only swarm CENTRES, so the authority — which has the per-bug positions AND the player's exact
// position — owns the timing + range; the server re-gates + applies. Two-beat via msg.Phase:
//   "windup" → flash the telegraph only (no damage);
//   "strike"/"" → the wind-up elapsed AND a bug is STILL in range → apply now (the funnel caps to ≤1 hit/window).
// This replaces the old server-scheduled centre-fire (the phantom). Mirrors handlePredationStrike.
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
	if zone := state.GetOrCreateZone(state.CurrentZone.ZoneID); zone.AuthorityUserID != senderID {
		return // AUTHORITY ONLY (anti-cheat + de-dupe)
	}
	swarm, ok := state.Swarms[msg.SwarmID]
	if !ok || swarm.Count <= 0 {
		return
	}
	species := state.Species[swarm.SpeciesID]
	if species == nil {
		return
	}
	atk := species.AttackProfile()
	if atk == nil {
		return
	}
	player, ok := state.Players[msg.PlayerID]
	if !ok || player == nil {
		return
	}
	if !m.bugAttackAllowed(state, swarm, species, atk) {
		return
	}
	// Loose anti-cheat centre sanity with the server's FINE player pos (the authority did the precise check).
	cs := state.Config.ChunkSize
	dx := player.WorldX(cs) - swarm.WorldX(cs)
	dy := player.WorldY(cs) - swarm.WorldY(cs)
	maxR := atk.Range + swarm.Radius + attackSanityMargin
	if dx*dx+dy*dy > maxR*maxR {
		return
	}

	// Telegraphs play AT the player so a SINGLE member peels off / darts in (not the whole cloud): the
	// "swoop in and attack" read. The client resolves the nearest member to that point.
	px, py := player.WorldX(cs), player.WorldY(cs)
	if msg.Phase == "windup" {
		m.broadcastBugTelegraphAt(dispatcher, state, swarm, "windup", px, py)
		return
	}
	for _, id := range msg.BugIDs {
		if !swarm.IsBugAlive(id) {
			continue
		}
		if m.applyBugAttackToPlayer(logger, dispatcher, state, swarm, species, msg.PlayerID, player, atk.Damage) {
			// Connected: the member DARTS in as it strikes (contact = a big cosmetic dart, lunge =
			// just the flash — the surge already carried the body). Display-only; damage already applied.
			m.broadcastBugTelegraphAt(dispatcher, state, swarm, "dive", px, py)
			return
		}
	}
}
