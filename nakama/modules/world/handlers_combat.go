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

// Chance that a killed bug drops bug_parts (v1: one hardcoded drop for all species;
// per-species kill_drops waits for real loot-table design — see BACKLOG).
const killDropChance = 0.5
const killDropItem = "bug_parts"

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

	// Equipped weapon gates the action; all stats are data (items.json).
	weapon := state.Entities[player.EquippedTool]
	if weapon == nil || (weapon.ToolType != "sword" && weapon.ToolType != "spear") {
		return
	}

	// Per-weapon cooldown — shared LastToolTick also closes the weapon-swap bypass.
	if !m.validateToolCooldown(state, player, state.TickCount) {
		return
	}

	// Reach: player → click distance (+slack for swing geometry/latency).
	dx := msg.ClickX - player.WorldX(chunkSize)
	dy := msg.ClickY - player.WorldY(chunkSize)
	reach := weapon.Reach + 0.5
	if dx*dx+dy*dy > reach*reach {
		return
	}

	maxTargets := weapon.MaxTargets
	if maxTargets <= 0 {
		maxTargets = 1
	}
	damage := weapon.Damage
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

			// Kill: removal flows through the SAME path as catching — RemoveBugs
			// (which also cleans the BugHP entry) + a BUG_REMOVED ledger event for
			// deterministic application and late-joiner replay.
			removed := swarm.RemoveBugs([]int{bugID})
			if len(removed) == 0 {
				continue
			}
			result.Killed = append(result.Killed, bugID)
			if state.CurrentZone != nil {
				state.AddInfluenceEvent(state.CurrentZone.ZoneID, InfluenceBugRemoved,
					"", 0, 0, swarm.ID, bugID)
			}
			m.spawnKillDrop(logger, dispatcher, state, msg.ClickX, msg.ClickY, chunkSize)
		}

		if len(result.Damaged) > 0 || len(result.Killed) > 0 {
			results = append(results, result)
		}

		// Empty swarm despawns exactly like the catch path.
		if swarm.Count <= 0 {
			delete(state.Swarms, swarm.ID)
			state.SwarmsDirty = true
		}
	}

	if len(results) == 0 {
		return // full whiff — nothing to broadcast
	}

	resultMsg := MeleeResultMessage{
		AttackerID: playerID,
		ClickX:     msg.ClickX,
		ClickY:     msg.ClickY,
		Results:    results,
	}
	data, _ := json.Marshal(resultMsg)
	dispatcher.BroadcastMessage(OpCodeMeleeResult, data, nil, nil, true)

	logger.Debug("Player %s melee: %d struck across %d swarms", playerID, struck, len(results))
}

// spawnKillDrop chance-rolls a bug_parts ground item at the strike position (+jitter) —
// the break-drop spawn pattern. No DecaysTo and FoodValue stays 0, so kill drops are
// never bug food (bug-food gates on FoodValue > 0).
func (m *Match) spawnKillDrop(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	clickX, clickY float32,
	chunkSize int,
) {
	if rand.Float32() > killDropChance {
		return
	}

	cs := float32(chunkSize)
	worldX := clickX + (rand.Float32()-0.5)*0.6
	worldY := clickY + (rand.Float32()-0.5)*0.6
	cx := int(worldX / cs)
	cy := int(worldY / cs)

	itemID := fmt.Sprintf("item_kill_%d", time.Now().UnixNano())
	groundItem := &entities.GroundItem{
		ID:       itemID,
		ItemType: killDropItem,
		Count:    1,
		Position: entities.EntityPosition{
			ChunkX: cx,
			ChunkY: cy,
			LocalX: worldX - float32(cx)*cs,
			LocalY: worldY - float32(cy)*cs,
		},
		Lifetime: 60.0,
	}
	state.GroundItems[itemID] = groundItem

	spawnMsg := GroundItemSpawnMessage{
		ID:       itemID,
		ItemType: killDropItem,
		Count:    1,
		X:        worldX,
		Y:        worldY,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)

	logger.Debug("Kill drop %s at %.1f,%.1f", killDropItem, worldX, worldY)
}
