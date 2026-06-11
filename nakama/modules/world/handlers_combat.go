package world

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"sort"
	"time"

	"github.com/heroiclabs/nakama-common/runtime"

	"bugfarmer/entities"
)

// Kill drops are per-species loot tables (species.json kill_drops); carrion lifetime in
// seconds before a ground drop despawns (emitting FOOD_CONSUMED(0) if it was edible).
const killDropLifetime = 60.0

// handleMeleeAttack processes one melee SWING (OpCode 88). Mirrors the catch trust
// model: the client detects bug ids against its deterministic positions; the server
// validates alive-ids + player→click reach + per-swing cap (it holds no per-bug
// positions), applies damage against the sparse SwarmState.BugHP map, removes kills
// through the same RemoveBugs + BUG_REMOVED ledger path as catching, and broadcasts
// a MeleeResultMessage (OpCode 89) — the sole per-bug HP display channel.
func (m *Match) handleMeleeAttack(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg MeleeAttackMessage,
	playerID string,
	chunkSize int,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}

	// MOVE-EXISTENCE is the entire gate: GetMove is nil-receiver-safe, so a bare hand
	// (""), an Entities-absent id (EquipTool relays arbitrary client strings), a tool
	// without moves (hoe, net), and an unknown move name all fall out of one expression.
	// This is also what lets axes alt-attack without being "weapons".
	moveName := msg.Move
	if moveName == "" {
		moveName = "primary"
	}
	weapon := state.Entities[player.EquippedTool]
	move := weapon.GetMove(moveName)
	if move == nil {
		return
	}

	// Reach BEFORE the cooldown stamp — a too-far click must not eat the cooldown.
	dx := msg.ClickX - player.WorldX(chunkSize)
	dy := msg.ClickY - player.WorldY(chunkSize)
	reach := move.Reach + 0.5
	if dx*dx+dy*dy > reach*reach {
		return
	}

	// Per-MOVE cooldown on the shared LastToolTick (sword<->hoe<->jab throttle each
	// other; closes alternating-spam and the weapon-swap bypass).
	if !m.validateCooldownTicks(player, state.TickCount, move.CooldownTicks) {
		return
	}

	maxTargets := move.MaxTargets
	if maxTargets <= 0 {
		maxTargets = 1
	}
	damage := move.Damage
	if damage <= 0 {
		damage = 1
	}

	// Deterministic iteration: entries sorted by swarm id, bug ids sorted within each;
	// the per-swing cap applies to the TOTAL across swarms (not per entry).
	hits := append([]MeleeSwarmHits(nil), msg.Hits...)
	sort.Slice(hits, func(i, j int) bool { return hits[i].SwarmID < hits[j].SwarmID })

	results := []MeleeSwarmResult{}
	struck := 0
	for _, hit := range hits {
		if struck >= maxTargets {
			break
		}
		swarm, ok := state.Swarms[hit.SwarmID]
		if !ok || swarm.Count <= 0 {
			continue // split/merge/despawn race — the swing whiffs on this swarm
		}
		species := state.Species[swarm.SpeciesID]
		maxHP := 1
		if species != nil && species.MaxHP > 0 {
			maxHP = species.MaxHP
		}

		bugIDs := append([]int(nil), hit.BugIDs...)
		sort.Ints(bugIDs)

		result := MeleeSwarmResult{
			SwarmID: swarm.ID,
			Damaged: []BugHPEntry{}, // initialized: nil would marshal as JSON null
			Killed:  []int{},
		}
		for _, bugID := range bugIDs {
			if struck >= maxTargets {
				break
			}
			if !swarm.IsBugAlive(bugID) {
				continue // already caught/killed/shed — whiff, no double anything
			}
			struck++

			if hpLeft, survived := swarm.DamageBug(bugID, damage, maxHP); survived {
				result.Damaged = append(result.Damaged, BugHPEntry{BugID: bugID, HP: hpLeft})
				continue
			}

			// Kill: removal flows through the SHARED kill path (RemoveBugs +
			// BUG_REMOVED + drops + empty-swarm despawn) — the same function
			// predation strikes use.
			removed := m.killBugsInSwarm(logger, dispatcher, state, swarm, species,
				[]int{bugID}, msg.ClickX, msg.ClickY, chunkSize)
			if len(removed) == 0 {
				continue
			}
			result.Killed = append(result.Killed, bugID)
		}

		if len(result.Damaged) > 0 || len(result.Killed) > 0 {
			results = append(results, result)
		}
	}

	if len(results) == 0 {
		return // full whiff — nothing to broadcast
	}

	resultMsg := MeleeResultMessage{
		AttackerID: playerID,
		ClickX:     msg.ClickX,
		ClickY:     msg.ClickY,
		Weapon:     player.EquippedTool, // self-describing: remote replay needs no eq lookup
		Move:       moveName,            // resolved name ("" was normalized to "primary")
		Results:    results,
	}
	data, _ := json.Marshal(resultMsg)
	dispatcher.BroadcastMessage(OpCodeMeleeResult, data, nil, nil, true)

	logger.Debug("Player %s melee: %d struck across %d swarms", playerID, struck, len(results))
}

// killBugsInSwarm is THE shared kill path (melee + predation strikes): RemoveBugs
// (cleans BugHP), one BUG_REMOVED ledger event per id (deterministic application +
// late-join replay), the victim species' kill drops at (dropX, dropY) with the swarm
// center as the blocked-cell fallback, and the empty-swarm despawn (the catch
// convention: delete + SwarmsDirty; stale SwarmsBySpecies ids are cleaned lazily).
// Returns the ids actually removed.
func (m *Match) killBugsInSwarm(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	swarm *entities.SwarmState,
	species *entities.BugSpecies,
	bugIDs []int,
	dropX, dropY float32,
	chunkSize int,
) []int {
	removed := swarm.RemoveBugs(bugIDs)
	if len(removed) == 0 {
		return removed
	}

	zoneID := ""
	if state.CurrentZone != nil {
		zoneID = state.CurrentZone.ZoneID
	}
	for _, id := range removed {
		if zoneID != "" {
			state.AddInfluenceEvent(zoneID, InfluenceBugRemoved, "", 0, 0, swarm.ID, id)
		}
		m.spawnKillDrops(logger, dispatcher, state, species,
			dropX, dropY,
			swarm.WorldX(chunkSize), swarm.WorldY(chunkSize), chunkSize)
	}

	// Empty swarm despawns exactly like the catch path.
	if swarm.Count <= 0 {
		delete(state.Swarms, swarm.ID)
		state.SwarmsDirty = true
	}
	return removed
}

// spawnKillDrops rolls the VICTIM species' kill_drops loot table at (dropX, dropY)
// (+jitter per item). Player kills pass the strike position; predation kills pass the
// predator's center; the centipede's death scatters along its trail (the caller spreads
// positions). If the drop point is blocked (a flying predator can legally strike while
// hovering OVER a fence cell), fall back to fallbackX/Y — the victim's center, always
// clear ground by construction — because an EDIBLE drop inside a blocks_bugs cell would
// become a permanent wall-attractor for fly visuals and an unreachable gnaw lure.
//
// Edible drops (item def food_value > 0) get a FoodValue and MUST emit ITEM_ROTTED:
// follower clients build the deterministic food registry from the ledger, and fly
// display clustering at food feeds bug positions = the state hash.
func (m *Match) spawnKillDrops(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	species *entities.BugSpecies,
	dropX, dropY, fallbackX, fallbackY float32,
	chunkSize int,
) {
	if species == nil || len(species.KillDrops) == 0 {
		return
	}

	if state.IsBlocked(dropX, dropY) {
		dropX, dropY = fallbackX, fallbackY
	}

	for _, drop := range species.KillDrops {
		if drop.Chance < 1.0 && rand.Float32() > drop.Chance {
			continue
		}
		count := drop.CountMin
		if drop.CountMax > drop.CountMin {
			count += rand.Intn(drop.CountMax - drop.CountMin + 1)
		}
		if count <= 0 {
			continue
		}

		worldX := dropX + (rand.Float32()-0.5)*0.6
		worldY := dropY + (rand.Float32()-0.5)*0.6
		// Normalize like spawnSwarmAt (the old int(x/cs) truncation was wrong for
		// negative coords)
		pos := entities.EntityPosition{LocalX: worldX, LocalY: worldY}
		pos.Normalize(chunkSize)

		foodValue := 0
		if def := state.Entities[drop.Item]; def != nil {
			foodValue = def.FoodValue
		}

		itemID := fmt.Sprintf("item_kill_%d", time.Now().UnixNano())
		groundItem := &entities.GroundItem{
			ID:        itemID,
			ItemType:  drop.Item,
			Count:     count,
			Position:  pos,
			Lifetime:  killDropLifetime,
			FoodValue: foodValue,
		}
		state.GroundItems[itemID] = groundItem

		spawnMsg := GroundItemSpawnMessage{
			ID:       itemID,
			ItemType: drop.Item,
			Count:    count,
			X:        worldX,
			Y:        worldY,
		}
		m.broadcastToChunk(dispatcher, state, pos.ChunkX, pos.ChunkY, OpCodeGroundItemSpawn, spawnMsg)

		// Edible carrion enters the deterministic food registry (hash-bearing)
		if foodValue > 0 && state.CurrentZone != nil {
			state.AddFoodEvent(state.CurrentZone.ZoneID, InfluenceItemRotted, itemID,
				int(worldX), int(worldY), foodValue)
		}

		logger.Debug("Kill drop %s x%d at %.1f,%.1f (food=%d)", drop.Item, count, worldX, worldY, foodValue)
	}
}
