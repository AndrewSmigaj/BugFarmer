package world

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"runtime/debug"
	"sort"
	"strconv"
	"strings"
	"time"

	"bugfarmer/entities"

	"github.com/gofrs/uuid"
	"github.com/heroiclabs/nakama-common/runtime"
)

// Match implements runtime.Match for world simulation
type Match struct{}

// Ecology tunables (per-second rates at 10Hz). First-pass values — tune via the repro_test
// population graph. Species-specific rates (feed/breed/decay) live in species.json.
const (
	feedRadius             = 2.0  // swarm centre within this distance of food = "at" it
	consumePerBugPerSecond = 0.5  // food drained per bug per second while at a depletable source
	reproduceFoodCost      = 40.0 // food consumed by one reproduction event
	// HUNGER OVERRIDE: the forage/wander duty cycle (forage_chance) is for WELL-FED bugs — it makes
	// them wander idly so they look alive. A bug that isn't nearly full must always seek food, or it
	// STALLS BELOW THE BREED POINT: satiation 100 is what flips a bug to "reproducing", but under the
	// plain duty cycle a forager (esp. flies — small vision 8, low forage_chance) plateaus right at
	// this threshold (nibble up, wander, decay back) and NEVER reaches 100 → never breeds. So the
	// threshold must sit just under 100: a bug force-forages until nearly sated, reliably tips into
	// reproducing, breeds, resets to 0, and repeats — the livestock loop. Only the last sliver
	// (90-100) and the sated/reproducing bugs follow the idle duty cycle.
	hungerForageThreshold = 90.0
	// The one-apple budget (architecture_swarm_sync.md §13): a rotten apple = 100 food.
	// At fly consume_rate 0.2, a 10-fly swarm drains 2/s: feeding 0->100 sat (20s) = 40,
	// breeding 0->100 meter (10s) = 20, event cost = 40 -> exactly one breed event per
	// apple, growing 1-2 flies. Cost-per-fly RISES with population (bigger swarms drain
	// faster per capita) — growth is self-braking even before the hard caps.
)

// DayLengthTicks: one in-game day = 8400 ticks = 14 minutes at 10Hz (architecture_farming.md).
// The authoritative tick IS the shared clock — clients derive time-of-day from it directly
// (tick % DayLengthTicks), so the day/night cycle needs no extra netcode. Time pauses with
// the tick when a zone empties and restarts with the match (persistence later).
const DayLengthTicks = 8400

// SimRate is the CANONICAL ticks-per-sim-second: it defines sim-TIME and drives deltaTime + every
// seconds↔ticks conversion (feeding/breeding rates, lifespan, spawn intervals). It NEVER changes —
// all balance is anchored to it. The value returned to Nakama (Config.TickRate = the "call rate", how
// often MatchLoop actually runs in wall-clock) is SEPARATE: a test zone can raise it (≤60, Nakama's
// cap) to run the SAME sim faster in real time, byte-identical (same tick sequence). Decoupling them is
// what lets us watch many game-days of the food-bounded ecology settle in minutes, with zero balance
// change. Everything else in the sim is already counted in raw ticks and scales uniformly.
const SimRate = 10

// reproduceSwarm adds 1-2 bugs (randomized — NOT doubling: gentle, sub-exponential
// growth) to a sated swarm at a breeding source: new ids from NextBugID, a
// SWARM_REPRODUCED ledger event (clients spawn them at the centre at the event tick —
// idempotent, same pattern as split/merge; the count rides the event, so server rand is
// replay-safe), a chunk of food consumed, meters reset (hungry again →
// CheckPhaseTransition falls back to feeding).
//
// HARD population cap (species_caps.max_population, 0 = uncapped): at the cap the event
// is SKIPPED — meters reset AND the cooldown is armed (without it the meter refills in
// ~30s and the skip fires per swarm per cycle), but the 40-food event cost is NOT charged:
// the continuous feeding drain is the honest cost of a capped population camping a source.
func (m *Match) reproduceSwarm(state *WorldState, dispatcher runtime.MatchDispatcher,
	swarm *entities.SwarmState, species *entities.BugSpecies, logger runtime.Logger) {

	count := 1 + state.Rng.Intn(2) // 1-2 offspring

	// VISIBLE BROOD path (flies/butterflies): a non-predator swarm LAYS eggs into the nursery at its
	// breeding source instead of growing instantly. processBroods matures + hatches them, and the
	// population/swarm caps apply at HATCH time (eggs are not bugs). Predators (wasp nest, centipede)
	// and individuals fall through to the instant-growth path below, unchanged.
	// GATED on an egg sprite: only species with a nursery (EggSpriteID) brood. Swarm-category
	// DETRITIVORES (millipede/beetle — no egg art, and they breed on forage pools / carrion that
	// layIntoBrood can't resolve) fall through to instant-growth + merge, which is the food-bounded
	// "fewer fat swarms" behavior we want for them without a fake egg nursery.
	if species.Predation == nil && species.Category == "swarm" && species.EggSpriteID != "" {
		laid := m.layIntoBrood(state, dispatcher, swarm, count)
		swarm.ReproductionMeter = 0
		swarm.Satiation = 0
		swarm.ReproduceCooldown = species.ReproduceCooldown
		if laid {
			m.consumeFood(state, dispatcher, swarm.TargetFoodID, reproduceFoodCost)
		}
		return
	}

	if maxPop := state.SpeciesMaxPopulation(swarm.SpeciesID); maxPop > 0 {
		room := maxPop - state.SpeciesPopulation(swarm.SpeciesID)
		if room < count {
			count = room // partial litter rather than all-or-nothing at the boundary
		}
		if count <= 0 {
			swarm.ReproductionMeter = 0
			swarm.Satiation = 0
			swarm.ReproduceCooldown = species.ReproduceCooldown
			logger.Debug("Swarm %s at the %s population cap (%d): reproduction skipped",
				swarm.ID, swarm.SpeciesID, maxPop)
			return
		}
	}

	// Individuals (ground crawlers, §14.3): merge/split are disabled for the
	// category, so a full swarm can never shed members — growth past MaxSwarmSize
	// would overcap the knot forever. At the swarm-size cap the litter becomes a
	// NEW swarm beside the parent instead, subject to the zone's swarm-count cap
	// (the same arm-the-cooldown skip as the population cap when no room).
	if species.Category == "individual" && species.MaxSwarmSize > 0 &&
		swarm.Count >= species.MaxSwarmSize {
		atSwarmCap := false
		if state.CurrentZone != nil && state.CurrentZone.BugSpawning != nil {
			if zcap, ok := state.CurrentZone.BugSpawning.SpeciesCaps[swarm.SpeciesID]; ok &&
				zcap.Max > 0 && state.AliveSwarmCount(swarm.SpeciesID) >= zcap.Max {
				atSwarmCap = true
			}
		}
		if atSwarmCap {
			swarm.ReproductionMeter = 0
			swarm.Satiation = 0
			swarm.ReproduceCooldown = species.ReproduceCooldown
			logger.Debug("Swarm %s at the %s swarm-count cap: reproduction skipped",
				swarm.ID, swarm.SpeciesID)
			return
		}
		chunkSize := state.Config.ChunkSize
		child := m.spawnSwarmAt(state, swarm.SpeciesID, count,
			swarm.Position.WorldX(chunkSize)+1.5, swarm.Position.WorldY(chunkSize),
			chunkSize)
		if child == nil {
			return
		}
		state.Stats.recordBirth(swarm.SpeciesID, BirthReproduce, count)
		swarm.ReproductionMeter = 0
		swarm.Satiation = 0
		swarm.ReproduceCooldown = species.ReproduceCooldown
		m.consumeFood(state, dispatcher, swarm.TargetFoodID, reproduceFoodCost)
		logger.Info("Swarm %s reproduced at %s: minted new swarm %s (+%d, parent full at %d)",
			swarm.ID, swarm.TargetFoodID, child.ID, count, swarm.Count)
		return
	}

	m.growSwarm(state, swarm, count) // the shared id-math + SWARM_REPRODUCED event
	state.Stats.recordBirth(swarm.SpeciesID, BirthReproduce, count)
	swarm.ReproductionMeter = 0
	swarm.Satiation = 0
	swarm.ReproduceCooldown = species.ReproduceCooldown
	m.consumeFood(state, dispatcher, swarm.TargetFoodID, reproduceFoodCost)
	logger.Info("Swarm %s reproduced at %s: +%d -> %d bugs", swarm.ID, swarm.TargetFoodID, count, swarm.Count)
}

// MatchLabel is the JSON structure for match listing
type MatchLabel struct {
	WorldID      string `json:"world_id"`
	Name         string `json:"name"`
	PlayerCount  int    `json:"player_count"`
	MaxPlayers   int    `json:"max_players"`
	AccessPolicy string `json:"access_policy"`
}

// NewMatch is the constructor registered with Nakama
func NewMatch(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule) (runtime.Match, error) {
	return &Match{}, nil
}

// MatchInit initializes the match state
func (m *Match) MatchInit(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, params map[string]interface{}) (interface{}, int, string) {
	// Extract params
	worldID, ok := params["world_id"].(string)
	if !ok || worldID == "" {
		logger.Error("MatchInit: missing world_id")
		return nil, 0, ""
	}

	ownerID, ok := params["owner_id"].(string)
	if !ok || ownerID == "" {
		logger.Error("MatchInit: missing owner_id")
		return nil, 0, ""
	}

	name, ok := params["name"].(string)
	if !ok || name == "" {
		name = "Unnamed World"
	}

	accessPolicy, ok := params["access_policy"].(string)
	if !ok || (accessPolicy != "public" && accessPolicy != "private") {
		accessPolicy = "public"
	}

	// Extract zone_id param (default to village_21)
	zoneID, ok := params["zone_id"].(string)
	if !ok || zoneID == "" {
		zoneID = "village_21"
	}

	// Create world state
	state := NewWorldState(worldID, ownerID, name, accessPolicy)
	state.ZoneID = zoneID

	// Load species from the canonical config
	species, err := entities.LoadSpecies("data/species.json")
	if err != nil {
		logger.Warn("Failed to load species config: %v - using defaults", err)
		state.Species = defaultFlySpecies()
	} else {
		state.Species = species
	}
	logger.Info("Loaded %d species", len(state.Species))

	// Load zone data (Phase 4)
	zonePath := fmt.Sprintf("data/zones/%s", zoneID)
	zoneConfig, err := LoadZoneConfig(zonePath)
	if err != nil {
		logger.Warn("Failed to load zone config: %v - using default", err)
		zoneConfig = &ZoneConfig{ZoneID: "village_21", BiomeType: "village"}
	}
	state.CurrentZone = zoneConfig

	// Test-zone sim speedup: a zone may raise the Nakama CALL rate (≤60) to run the SAME sim faster in
	// wall-clock. sim-TIME stays anchored to SimRate, so this is balance-neutral (see SimRate). Clamp to
	// Nakama's 1..60 match-tick-rate range; 0/absent leaves the default 10.
	if zoneConfig.CallRate > 0 {
		callRate := zoneConfig.CallRate
		if callRate > 60 {
			callRate = 60
		}
		state.Config.TickRate = callRate
		logger.Info("Zone %s runs at CallRate=%d (sim-time fixed at SimRate=%d → %d× wall-clock)",
			zoneConfig.ZoneID, callRate, SimRate, callRate/SimRate)
	}

	// Sim-batch (TEST zones only): advance N sim-ticks per Nakama call. call_rate caps at 60, so this is
	// the only way past 6× — a 15-game-day tuning run finishes in minutes. Default/clamped to 1 = no
	// batching = byte-identical to one tick per call (production zones omit sim_batch).
	state.Config.SimBatch = 1
	if zoneConfig.SimBatch > 1 {
		state.Config.SimBatch = zoneConfig.SimBatch
		if state.Config.SimBatch > 64 {
			state.Config.SimBatch = 64
		}
		logger.Info("Zone %s runs SimBatch=%d sim-ticks/call (test-zone headless speedup; %d× on top of call_rate)",
			zoneConfig.ZoneID, state.Config.SimBatch, state.Config.SimBatch)
	}

	// Static-sim zones (test/deterministic) disable continuous spawn, merge, and split.
	if zoneConfig.BugSpawning != nil {
		state.StaticSim = zoneConfig.BugSpawning.Static
	}

	// World seed: fixed from zone config for deterministic runs, else random.
	if zoneConfig.Seed != 0 {
		state.WorldSeed = zoneConfig.Seed
	} else {
		state.WorldSeed = rand.Int63()
	}
	// Seed the per-match RNG from WorldSeed so the whole sim is a pure function of (seed, ticks): a fixed
	// seed reproduces the run exactly (the tuning harness relies on this). All server rand.* below now go
	// through state.Rng — NOT the unseeded global math/rand, which Go auto-seeds randomly per process.
	state.Rng = rand.New(rand.NewSource(state.WorldSeed))
	logger.Info("Loaded zone: %s (static=%v, seed=%d)", zoneConfig.ZoneID, state.StaticSim, state.WorldSeed)

	// Load tile definitions (Phase 4)
	state.TileDefs, err = LoadTileDefinitions("data/tiles.json")
	if err != nil {
		logger.Warn("Failed to load tile definitions: %v", err)
	} else {
		logger.Info("Loaded %d tile definitions", len(state.TileDefs))
	}

	// Load entity definitions from unified entity system
	var warnings []string
	state.Tuning = LoadTuning("data/ecology_tuning.json", logger)
	state.Stats = NewEcologyStats()             // interaction-log telemetry (soft state, flushed per game-day)
	state.Perf = NewPerfStats(zoneConfig.Profile) // cost profiler (soft, never hashed; no-op unless profile=true)

	state.Entities, warnings, err = LoadAllEntities("data")
	if err != nil {
		logger.Warn("Failed to load entity definitions: %v", err)
	} else {
		logger.Info("Loaded %d entity definitions", len(state.Entities))
		for _, w := range warnings {
			logger.Warn("Entity loading: %s", w)
		}
	}

	// Load crop definitions
	state.CropDefs, err = LoadCropDefs("data")
	if err != nil {
		logger.Warn("Failed to load crop definitions: %v", err)
	} else {
		logger.Info("Loaded %d crop definitions", len(state.CropDefs))
	}

	// Load crafting recipes
	state.Recipes, state.RecipesByStation, err = LoadRecipes("data")
	if err != nil {
		logger.Warn("Failed to load crafting recipes: %v", err)
	} else {
		logger.Info("Loaded %d crafting recipes across %d stations", len(state.Recipes), len(state.RecipesByStation))
	}

	// ZONE PERSISTENCE: prefetch this zone's saved farm delta (consumed lazily per chunk in
	// handleChunkSubscribe). Must run after CurrentZone is set; before the swarm restore below.
	m.prefetchZoneState(ctx, nk, state, logger)

	// Restore the saved bug population if this zone was persisted; else spawn fresh initial swarms.
	// Restored swarms are CLEAN (IDs 0..Count-1) and enter before any client joins — determinism-safe.
	if !m.restoreSwarms(ctx, nk, state, logger) {
		m.spawnInitialSwarms(state, logger)
		m.seedInitialCarrion(state, logger)
	}

	// Create label for match listing
	label := MatchLabel{
		WorldID:      worldID,
		Name:         name,
		PlayerCount:  0,
		MaxPlayers:   state.Config.MaxPlayers,
		AccessPolicy: accessPolicy,
	}
	labelJSON, err := json.Marshal(label)
	if err != nil {
		logger.Error("MatchInit: failed to marshal label: %v", err)
		return nil, 0, ""
	}

	logger.Info("World match initialized: %s (%s)", name, worldID)

	return state, state.Config.TickRate, string(labelJSON)
}

// MatchJoinAttempt validates if a player can join
func (m *Match) MatchJoinAttempt(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presence runtime.Presence, metadata map[string]string) (interface{}, bool, string) {
	logger.Info(">>> MatchJoinAttempt called for %s at tick %d", presence.GetUserId(), tick)
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchJoinAttempt: invalid state type")
		return state, false, "internal error"
	}

	// Check max players
	if len(worldState.Players) >= worldState.Config.MaxPlayers {
		logger.Warn("World %s is full, rejecting %s", worldState.WorldID, presence.GetUserId())
		return state, false, "world is full"
	}

	// Check access policy
	if worldState.AccessPolicy == "private" {
		// For now, only owner can join private worlds
		// TODO: Add invite list
		if presence.GetUserId() != worldState.OwnerID {
			logger.Warn("Private world %s, rejecting non-owner %s", worldState.WorldID, presence.GetUserId())
			return state, false, "private world"
		}
	}

	// Character bridge: if the client passed a char_id in the join metadata, verify it belongs to
	// this account and STASH it for MatchJoin to consume (the two callbacks are decoupled — MatchJoin
	// gets no metadata). Match callbacks run serially on one goroutine per match, so PendingCharacters
	// needs no lock. Absent char_id = ephemeral default join (sync-harness / debug) — still accepted.
	if charID := metadata["char_id"]; charID != "" {
		save, err := LoadCharacterSave(ctx, nk, presence.GetUserId(), charID)
		if err != nil {
			logger.Error("MatchJoinAttempt: character load failed for %s/%s: %v", presence.GetUserId(), charID, err)
			return state, false, "character load failed"
		}
		if save == nil {
			logger.Warn("MatchJoinAttempt: %s requested unknown character %s", presence.GetUserId(), charID)
			return state, false, "character not found"
		}
		worldState.PendingCharacters[presence.GetUserId()] = charID
	}

	// Cross-zone entry: if the client passed entry_x/entry_y (walking off an adjacent zone's edge),
	// stash a validated, edge-anchored entry position for MatchJoin to use INSTEAD of the save's spawn.
	// Clamp to the zone + require a near-edge cell so it can't be a forged teleport into the interior.
	if exs, eys := metadata["entry_x"], metadata["entry_y"]; exs != "" && eys != "" {
		ex, errX := strconv.ParseFloat(exs, 32)
		ey, errY := strconv.ParseFloat(eys, 32)
		if errX == nil && errY == nil {
			w, h := 256.0, 256.0
			if worldState.CurrentZone != nil {
				if worldState.CurrentZone.Width > 0 {
					w = float64(worldState.CurrentZone.Width)
				}
				if worldState.CurrentZone.Height > 0 {
					h = float64(worldState.CurrentZone.Height)
				}
			}
			cl := func(v, max float64) float32 {
				if v < 0 {
					return 0
				}
				if v > max-1 {
					return float32(max - 1)
				}
				return float32(v)
			}
			cx, cy := cl(ex, w), cl(ey, h)
			const edge = 4.0 // must be within 4 cells of some edge (anti-forge)
			nearEdge := float64(cx) <= edge || float64(cx) >= w-1-edge ||
				float64(cy) <= edge || float64(cy) >= h-1-edge
			if nearEdge {
				worldState.PendingEntryPositions[presence.GetUserId()] = [2]float32{cx, cy}
			} else {
				logger.Warn("MatchJoinAttempt: rejecting non-edge entry pos (%.1f,%.1f) from %s", cx, cy, presence.GetUserId())
			}
		}
	}

	logger.Info("Player %s approved to join world %s", presence.GetUserId(), worldState.WorldID)
	return state, true, ""
}

// MatchJoin is called when player(s) successfully join
func (m *Match) MatchJoin(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presences []runtime.Presence) interface{} {
	logger.Info(">>> MatchJoin called with %d presences at tick %d", len(presences), tick)
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchJoin: invalid state type")
		return state
	}

	for _, presence := range presences {
		userID := presence.GetUserId()

		// RECONNECTION DETECTION: If this user already has a presence (old session),
		// log it. The old session's MatchLeave will fire later but will be ignored
		// by the stale session guard (session ID mismatch).
		if oldPresence, exists := worldState.Presences[userID]; exists {
			logger.Info("Player %s reconnecting: replacing session %s with %s",
				userID, oldPresence.GetSessionId(), presence.GetSessionId())
		}

		worldState.AddPlayer(userID, presence.GetUsername(), presence)
		player := worldState.Players[userID]

		// Zone id for cell events + per-character spawn placement.
		zoneID := ""
		if worldState.CurrentZone != nil {
			zoneID = worldState.CurrentZone.ZoneID
		}

		// CHARACTER LOAD (Part C): if a character was staged in MatchJoinAttempt, overlay its
		// persisted inventory/equipment/coins/appearance/home onto AddPlayer's fresh defaults and
		// choose the spawn. Character data is NOT in the bug-sim hash, and we set the spawn cell
		// BEFORE the PLAYER_CELL event below — so this is invisible to the deterministic tick.
		if charID, staged := worldState.PendingCharacters[userID]; staged {
			delete(worldState.PendingCharacters, userID)
			if save, err := LoadCharacterSave(ctx, nk, userID, charID); err != nil {
				logger.Error("MatchJoin: character load failed for %s/%s: %v", userID, charID, err)
			} else if save != nil {
				applyCharacterSave(player, save)
				if !save.IntroSeen {
					// First login: keep AddPlayer's spawn_point (the central square) + flag the
					// intro to ride this join's FullInventorySync (guaranteed-delivered; no race).
					player.IntroSeen = true
					player.PendingIntro = true
				} else if save.HomeZone == zoneID {
					// Returning with a bed home in this zone → wake at the bed (Minecraft-style
					// save point: "wherever you last saved, via a bed").
					player.SetWorldPosition(save.HomeX, save.HomeY, worldState.Config.ChunkSize)
				} else if save.LastZone == zoneID {
					// No bed home here yet → drop back where they logged out.
					player.SetWorldPosition(save.LastX, save.LastY, worldState.Config.ChunkSize)
				}
				// A different zone (or first login) keeps AddPlayer's zone spawn_point.
				logger.Info("Loaded character %q (%s) for %s in zone %s", save.Name, charID, userID, zoneID)
			}
		}

		// CROSS-ZONE ENTRY (top priority): if the player walked off an adjacent zone's edge, place them
		// at the matching edge of THIS zone — overrides the character save's spawn decision above (it's
		// the last SetWorldPosition, so it wins). Still inventory-loaded from the char save. Set BEFORE
		// the PLAYER_CELL event below, so the deterministic bug sim sees only the final entry cell.
		if entry, staged := worldState.PendingEntryPositions[userID]; staged {
			delete(worldState.PendingEntryPositions, userID)
			player.SetWorldPosition(entry[0], entry[1], worldState.Config.ChunkSize)
			logger.Info("Player %s cross-zone entered %s at edge (%.1f,%.1f)", userID, zoneID, entry[0], entry[1])
		}

		logger.Info("Player %s joined world %s", presence.GetUsername(), worldState.WorldID)

		// Send WorldInit for deterministic bug simulation
		worldInit := WorldInitMessage{
			WorldSeed: worldState.WorldSeed,
			Tick:      worldState.TickCount,
		}
		initData, _ := json.Marshal(worldInit)
		dispatcher.BroadcastMessage(OpCodeWorldInit, initData, []runtime.Presence{presence}, nil, true)

		// World environment (time-of-day offset + weather) — display state the joiner
		// can't derive from the tick alone
		m.sendWorldEnv(dispatcher, worldState, presence)

		// Seed the hearts UI (damage-0 echo; presence-targeted)
		// Send full inventory sync to the joining player (carries the restored character inventory)
		if err := m.sendInventorySync(logger, dispatcher, player, presence); err != nil {
			logger.Warn("Failed to send inventory sync to %s: %v", userID, err)
		}

		// Seed the hearts UI (damage-0 echo; presence-targeted)
		m.sendPlayerDamage(dispatcher, worldState, userID, PlayerDamageMessage{
			HP: player.HP, MaxHP: player.MaxHP, Damage: 0,
		})

		// Emit initial cell event for spawn position (deterministic bug AI)
		spawnX := player.WorldX(worldState.Config.ChunkSize)
		spawnY := player.WorldY(worldState.Config.ChunkSize)
		worldState.CheckPlayerCellChange(userID, spawnX, spawnY, zoneID)

		// Authoritatively place the local player on the client at the position decided above (last
		// logout / bed home / zone spawn). The passive entity-update snap is racy (client movement
		// can clobber the server position first) AND one-shot across a reconnect — this is reliable.
		if spawnData, sErr := json.Marshal(PlayerSpawnMessage{X: spawnX, Y: spawnY}); sErr == nil {
			dispatcher.BroadcastMessage(OpCodePlayerSpawn, spawnData, []runtime.Presence{presence}, nil, true)
		}

		// PLAYER INFO (appearance + name; static per session, so sent once on join, not per tick):
		//   1) roster of everyone already here → the joiner, so it can render the existing players.
		//   2) the joiner's own entry → everyone, so existing clients learn the newcomer.
		// Display-only (never in the sim hash). A reconnect re-runs this, so it self-corrects.
		roster := make([]PlayerInfoEntry, 0, len(worldState.Players))
		for uid, p := range worldState.Players {
			roster = append(roster, playerInfoEntry(uid, p))
		}
		if rData, rErr := json.Marshal(PlayerInfoMessage{Players: roster}); rErr == nil {
			dispatcher.BroadcastMessage(OpCodePlayerInfo, rData, []runtime.Presence{presence}, nil, true)
		}
		if jData, jErr := json.Marshal(PlayerInfoMessage{Players: []PlayerInfoEntry{playerInfoEntry(userID, player)}}); jErr == nil {
			dispatcher.BroadcastMessage(OpCodePlayerInfo, jData, nil, nil, true)
		}

		// === ZONE AUTHORITY ASSIGNMENT ===
		// First player in zone becomes authority, late joiners get snapshot
		if worldState.CurrentZone != nil {
			zone := worldState.GetOrCreateZone(zoneID)
			zone.Members[userID] = true

			if zone.AuthorityUserID == "" || zone.AuthorityUserID == userID {
				// First player OR authority reconnecting - assign/confirm as authority
				zone.AuthorityUserID = userID
				logger.Info("Assigned %s as authority for zone %s (reconnect=%v)", userID, zoneID, zone.AuthorityUserID == userID)

				// Send ZoneAuthority with bootstrap tick
				// Bootstrap Rule: LastEventSeq = -1 for first client
				// This indicates no prior influence events exist or are required.
				// The cell event just created will be broadcast in next MatchLoop tick,
				// and the first ZoneTickBroadcast will carry the real watermark.
				authMsg := ZoneAuthorityMessage{
					ZoneID:            zoneID,
					AuthorityID:       userID,
					AuthoritativeTick: worldState.TickCount,
					LastEventSeq:      -1, // FIRST CLIENT BOOTSTRAP - no prior events
					// Seed-baseline so the first joiner (or a reconnecting authority) CREATES the current
					// swarms itself — SwarmUpdate no longer creates. Bugs seed from (worldSeed,swarmId,bugId)
					// at the centre; this client is the origin of truth, so seed-from-centre is exact.
					Swarms: m.buildSwarmSeedBaseline(worldState, zone, worldState.Config.ChunkSize),
				}
				authData, _ := json.Marshal(authMsg)
				dispatcher.BroadcastMessage(OpCodeZoneAuthority, authData, []runtime.Presence{presence}, nil, true)
			} else {
				// Late joiner - needs snapshot from authority
				logger.Info("Late joiner %s in zone %s, authority is %s", userID, zoneID, zone.AuthorityUserID)
				m.sendLateJoinSnapshot(logger, dispatcher, worldState, userID, presence)
			}
		}
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	// SwarmUpdate is event-driven, so bootstrap a joiner's swarm set on the next tick.
	// (Late joiners also receive swarm_metadata in the snapshot; this re-broadcast is a
	// harmless reconcile and is the ONLY swarm set the first/authority client receives.)
	worldState.SwarmsDirty = true

	return worldState
}

// playerInfoEntry builds the cosmetic identity (appearance + name) broadcast for a player. Reads the
// already-loaded character state; empty for a no-character join (the client then defaults to merchant).
func playerInfoEntry(userID string, p *PlayerState) PlayerInfoEntry {
	return PlayerInfoEntry{
		UserID:    userID,
		Name:      p.Username,
		CharClass: p.Appearance.Class,
		CharHair:  p.Appearance.Hair,
		CharSkin:  p.Appearance.Skin,
	}
}

// sendInventorySync sends the player's full inventory state
func (m *Match) sendInventorySync(logger runtime.Logger, dispatcher runtime.MatchDispatcher, player *PlayerState, presence runtime.Presence) error {
	// Convert fixed arrays to slices for JSON
	bugSlots := make([]InventorySlot, len(player.BugSlots))
	copy(bugSlots, player.BugSlots[:])

	itemSlots := make([]InventorySlot, len(player.ItemSlots))
	copy(itemSlots, player.ItemSlots[:])

	unlocked := player.ItemSlotsUnlocked
	if unlocked <= 0 {
		unlocked = baseUnlockedItemSlots
	}
	msg := FullInventorySyncMessage{
		BugSlots:          bugSlots,
		ItemSlots:         itemSlots,
		Coins:             player.Coins,
		ItemSlotsUnlocked: unlocked,
		Intro:             player.PendingIntro,
	}
	player.PendingIntro = false // one-shot

	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	dispatcher.BroadcastMessage(OpCodeFullInventorySync, data, []runtime.Presence{presence}, nil, true)

	// Worn armor (cosmetic equipment) rides its own message so the client's
	// EquipmentState initializes alongside the inventory.
	eqMsg := EquipmentUpdateMessage{Equipment: player.Equipment[:]}
	if eqData, eqErr := json.Marshal(eqMsg); eqErr == nil {
		dispatcher.BroadcastMessage(OpCodeEquipmentUpdate, eqData, []runtime.Presence{presence}, nil, true)
	}

	logger.Info("Sent inventory sync to %s: %d bug slots, %d item slots, %d coins",
		presence.GetUserId(), len(bugSlots), len(itemSlots), player.Coins)
	return nil
}

// MatchLeave is called when player(s) leave
func (m *Match) MatchLeave(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, presences []runtime.Presence) interface{} {
	logger.Info(">>> MatchLeave called with %d presences at tick %d", len(presences), tick)
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLeave: invalid state type")
		return state
	}

	for _, presence := range presences {
		userID := presence.GetUserId()

		// STALE SESSION GUARD: If a newer session has already replaced this one
		// (reconnection), skip the leave cleanup entirely. The new session is still
		// active and should not be wiped out by the old session disconnecting.
		if currentPresence, exists := worldState.Presences[userID]; exists {
			if currentPresence.GetSessionId() != presence.GetSessionId() {
				logger.Info("Ignoring stale MatchLeave for %s: leaving session %s != current session %s",
					userID, presence.GetSessionId(), currentPresence.GetSessionId())
				continue
			}
		}

		// CHARACTER SAVE (Part C): persist this character before removing it. Build the snapshot
		// synchronously here (race-free — the match goroutine is single-threaded, and player is
		// freed by RemovePlayer just below), then write to storage in a detached goroutine so the
		// leave path doesn't block on I/O. The stale-session guard above already prevents a
		// reconnect's leave from clobbering the live session.
		if player, ok := worldState.Players[userID]; ok && player.CharacterID != "" {
			zoneID := ""
			if worldState.CurrentZone != nil {
				zoneID = worldState.CurrentZone.ZoneID
			}
			save := buildCharacterSave(player, zoneID, worldState.Config.ChunkSize, time.Now().Unix())
			go func() {
				if err := WriteCharacterSave(context.Background(), nk, userID, save); err != nil {
					logger.Error("MatchLeave: character save failed for %s/%s: %v", userID, save.CharID, err)
				}
			}()
		}

		worldState.RemovePlayer(userID)

		// Emit PLAYER_CELL_LEAVE influence event before deleting cell state
		// This ensures other clients' InfluenceManager removes the phantom player cell
		if cell, exists := worldState.PlayerCells[userID]; exists {
			zoneID := ""
			if worldState.CurrentZone != nil {
				zoneID = worldState.CurrentZone.ZoneID
			}
			worldState.AddInfluenceEvent(zoneID, InfluencePlayerCellLeave, userID, cell.CellX, cell.CellY, "", 0)
		}

		// Clean up player cell state
		delete(worldState.PlayerCells, userID)

		// Clean up chunk subscriptions
		for _, subs := range worldState.ChunkSubs {
			delete(subs, userID)
		}

		// === ZONE AUTHORITY REASSIGNMENT ===
		// If leaving player was authority, reassign to another member
		if worldState.CurrentZone != nil {
			zoneID := worldState.CurrentZone.ZoneID
			zone := worldState.GetZone(zoneID)
			if zone != nil {
				delete(zone.Members, userID)

				// Check if zone is now completely empty - reset ALL sync state
				// This prevents watermark mismatch when next player joins
				if len(zone.Members) == 0 {
					zone.NextSeq = 0
					zone.InfluenceLog = nil
					zone.LatestSnapshot = nil
					zone.LatestSnapshotTick = 0
					zone.LatestSnapshotHash = ""
					zone.AuthorityUserID = ""
					// Drop any event still queued for broadcast. Otherwise an event from the last
					// tick before everyone left can survive the reset + pause-when-empty and be
					// delivered to the next (reconnecting) client mixed with the fresh seq-0 stream,
					// leaving a seq gap the client's HasAllEventsUpTo can never close (it stalls).
					worldState.ClearPendingInfluence()
					logger.Info("Zone %s is now empty - reset all sync state (NextSeq, InfluenceLog, Snapshot, Authority, PendingInfluence)", zoneID)

					// ZONE PERSISTENCE: the zone just went quiet — snapshot its farm (+ bug population)
					// and write it async. The live paused match stays the source of truth until terminate,
					// so this is a restart backup. Snapshot is built synchronously on the match goroutine.
					if recs := m.snapshotZoneState(worldState); len(recs) > 0 {
						go writeZoneRecords(context.Background(), nk, logger, recs)
					}
				} else if zone.AuthorityUserID == userID {
					// Authority is leaving but zone still has members - reassign
					zone.AuthorityUserID = ""
					var newAuthority string
					for memberID := range zone.Members {
						if _, connected := worldState.Presences[memberID]; connected {
							newAuthority = memberID
							break
						}
					}

					if newAuthority != "" {
						zone.AuthorityUserID = newAuthority
						logger.Info("Reassigned authority for zone %s to %s", zoneID, newAuthority)

						// Broadcast new authority to all remaining players
						// Note: This is NOT a bootstrap, so use current watermark
						authMsg := ZoneAuthorityMessage{
							ZoneID:            zoneID,
							AuthorityID:       newAuthority,
							AuthoritativeTick: worldState.TickCount,
							LastEventSeq:      zone.NextSeq - 1,
						}
						authData, _ := json.Marshal(authMsg)
						dispatcher.BroadcastMessage(OpCodeZoneAuthority, authData, nil, nil, true)
					} else {
						// Members exist but none are connected - this is a transient state
						// Zone will be reset when the last member actually leaves
						logger.Info("No connected players in zone %s, authority cleared (waiting for full empty)", zoneID)
					}
				}
			}
		}

		logger.Info("Player %s left world %s", presence.GetUsername(), worldState.WorldID)
	}

	// Update label with new player count
	m.updateLabel(dispatcher, worldState)

	// Return state to keep match alive (persistent world)
	return worldState
}

// MatchLoop is called every tick
func (m *Match) MatchLoop(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, messages []runtime.MatchData) (result interface{}) {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchLoop: invalid state type")
		return nil // End match on invalid state
	}

	// PANIC RECOVERY: Catch any hidden panics and log them
	// IMPORTANT: We set result = worldState so if panic occurs, match continues
	defer func() {
		if r := recover(); r != nil {
			logger.Error("PANIC in MatchLoop: %v", r)
			logger.Error("Stack trace:\n%s", debug.Stack())
			result = worldState // Keep match alive after panic
		}
	}()

	// Pause when no one is connected. A world must not "run" (advance ticks, simulate bugs,
	// merge/split, broadcast) with zero players — that both wastes work and was crashing
	// long-idle matches in merge/split. Returning state keeps the match alive but fully idle;
	// TickCount freezes, so every tick-delta pauses cleanly and resumes when a player joins.
	if len(worldState.Players) == 0 && len(worldState.Presences) == 0 {
		// Defense in depth: the pause skips the normal per-tick broadcast+clear, so make sure no
		// event lingers in the queue across an empty period (it would leak to the next client).
		if len(worldState.PendingInfluence) > 0 {
			worldState.ClearPendingInfluence()
		}
		return worldState
	}

	// SIM BATCH (test zones only; SimBatch=1 in production = ONE iteration = byte-identical behavior):
	// advance N full sim-ticks per Nakama call so a headless tuning run covers many game-days fast. Each
	// iteration is a complete, unchanged tick (TickCount++, sim, per-tick broadcast); the messages slice
	// re-processes each sub-tick (harmless for the observer/test use — don't send mutating messages to a
	// batched zone). VERIFIED: no early `return` between here and the loop close, so the wrap is safe.
	for simStep := 0; simStep < worldState.Config.SimBatch; simStep++ {
		worldState.TickCount++
		chunkSize := worldState.Config.ChunkSize

		// ZONE PERSISTENCE: periodic autosave while occupied (crash safety between the on-empty/terminate
		// saves). Snapshot synchronously on the match goroutine, write async. Only fires past the pause
		// guard, so it never runs on an empty zone.
		if worldState.TickCount-worldState.LastZoneSaveTick >= zoneAutosaveTicks {
			worldState.LastZoneSaveTick = worldState.TickCount
			if recs := m.snapshotZoneState(worldState); len(recs) > 0 {
				go writeZoneRecords(context.Background(), nk, logger, recs)
			}
		}

		// Process incoming messages
		for _, msg := range messages {
			if simStep > 0 {
				break // process player input only ONCE per call (re-processing each sub-tick re-floods
				// chunk-subscribes etc.); sub-ticks 1..N are pure simulation
			}
			userID := msg.GetUserId()
			player, exists := worldState.Players[userID]
			if !exists {
				continue
			}

			opCode := msg.GetOpCode()
			// Don't log high-frequency messages
			if opCode != OpCodeMovement && opCode != OpCodeChunkSubscribe && opCode != OpCodeChunkUnsub {
				logger.Info("Received OpCode %d from %s", opCode, userID)
			}

			switch opCode {
			case OpCodeMovement:
				var movement MovementMessage
				if err := json.Unmarshal(msg.GetData(), &movement); err != nil {
					logger.Warn("Invalid movement message from %s: %v", userID, err)
					continue
				}
				// Authoritative collision: reject moves into cells that block players. The client position is
				// the CENTRE of the 16x32 (1x2-cell) centre-pivoted sprite, so the feet (ground contact) are
				// one cell below: (X, Y-1). The client predicts this too; this is the server backstop. Facing
				// still updates so turning in place against a wall works.
				if worldState.IsBlockedForPlayers(movement.X, movement.Y-1.0) {
					player.Facing = entities.Direction(movement.Facing)
					continue
				}
				// Update player state
				player.SetWorldPosition(movement.X, movement.Y, chunkSize)
				player.Facing = entities.Direction(movement.Facing)

				// Track cell changes for deterministic bug AI
				zoneID := ""
				if worldState.CurrentZone != nil {
					zoneID = worldState.CurrentZone.ZoneID
				}
				worldState.CheckPlayerCellChange(userID, movement.X, movement.Y, zoneID)

			case OpCodeCatchBug:
				var catchMsg CatchBugMessage
				if err := json.Unmarshal(msg.GetData(), &catchMsg); err != nil {
					logger.Warn("Invalid catch message from %s: %v", userID, err)
					continue
				}
				m.handleCatchBug(logger, dispatcher, worldState, catchMsg, userID, chunkSize)

			case OpCodeMeleeAttack:
				var meleeMsg MeleeAttackMessage
				if err := json.Unmarshal(msg.GetData(), &meleeMsg); err != nil {
					logger.Warn("Invalid melee message from %s: %v", userID, err)
					continue
				}
				m.handleMeleeAttack(logger, dispatcher, worldState, meleeMsg, userID, chunkSize)

			case OpCodeReleaseBugs:
				var releaseMsg ReleaseBugsMessage
				if err := json.Unmarshal(msg.GetData(), &releaseMsg); err != nil {
					logger.Warn("Invalid release message from %s: %v", userID, err)
					continue
				}
				m.handleReleaseBugs(logger, dispatcher, worldState, releaseMsg, userID, chunkSize)

			case OpCodeEquipArmor:
				var armorMsg EquipArmorMessage
				if err := json.Unmarshal(msg.GetData(), &armorMsg); err != nil {
					logger.Warn("Invalid equip-armor message from %s: %v", userID, err)
					continue
				}
				m.handleEquipArmor(logger, dispatcher, worldState, userID, armorMsg)

			case OpCodeEquipTool:
				var equipMsg EquipToolMessage
				if err := json.Unmarshal(msg.GetData(), &equipMsg); err != nil {
					logger.Warn("Invalid equip message from %s: %v", userID, err)
					continue
				}
				player.EquippedTool = equipMsg.ToolID
				logger.Info("Player %s equipped tool: %q", userID, equipMsg.ToolID)

			case OpCodeMoveSlot:
				var moveMsg MoveSlotMessage
				if err := json.Unmarshal(msg.GetData(), &moveMsg); err != nil {
					logger.Warn("Invalid move slot message from %s: %v", userID, err)
					continue
				}
				m.handleMoveSlot(logger, dispatcher, worldState, moveMsg, userID)

			// World Building (Phase 4)
			case OpCodeChunkSubscribe:
				var subMsg ChunkSubscribeMessage
				if err := json.Unmarshal(msg.GetData(), &subMsg); err != nil {
					logger.Warn("Invalid chunk subscribe from %s: %v", userID, err)
					continue
				}
				m.handleChunkSubscribe(logger, dispatcher, worldState, userID, subMsg.ChunkX, subMsg.ChunkY)

			case OpCodeChunkUnsub:
				var subMsg ChunkSubscribeMessage
				if err := json.Unmarshal(msg.GetData(), &subMsg); err != nil {
					continue
				}
				m.handleChunkUnsub(worldState, userID, subMsg.ChunkX, subMsg.ChunkY)

			case OpCodeTilePlace:
				var placeMsg TilePlaceMessage
				if err := json.Unmarshal(msg.GetData(), &placeMsg); err != nil {
					logger.Warn("Invalid tile place from %s: %v", userID, err)
					continue
				}
				m.handleTilePlace(logger, dispatcher, worldState, userID, placeMsg)

			case OpCodeTileBreak:
				var breakMsg TileBreakMessage
				if err := json.Unmarshal(msg.GetData(), &breakMsg); err != nil {
					logger.Warn("Invalid tile break from %s: %v", userID, err)
					continue
				}
				m.handleTileBreak(logger, dispatcher, worldState, userID, breakMsg, worldState.TickCount)

			case OpCodeToolUse:
				var toolMsg ToolUseMessage
				if err := json.Unmarshal(msg.GetData(), &toolMsg); err != nil {
					logger.Warn("Invalid tool use from %s: %v", userID, err)
					continue
				}
				m.handleToolUse(logger, dispatcher, worldState, userID, toolMsg, worldState.TickCount)

			case OpCodePlantInteract:
				var plantMsg PlantInteractMessage
				if err := json.Unmarshal(msg.GetData(), &plantMsg); err != nil {
					logger.Warn("Invalid plant interact from %s: %v", userID, err)
					continue
				}
				m.handlePlantInteract(logger, dispatcher, worldState, userID, plantMsg, worldState.TickCount)

			case OpCodePickupItem:
				var pickupMsg PickupItemMessage
				if err := json.Unmarshal(msg.GetData(), &pickupMsg); err != nil {
					continue
				}
				m.handlePickupItem(logger, dispatcher, worldState, userID, pickupMsg)

			case OpCodeTreeHarvest:
				var harvestMsg TreeHarvestMessage
				if err := json.Unmarshal(msg.GetData(), &harvestMsg); err != nil {
					logger.Warn("Invalid tree harvest from %s: %v", userID, err)
					continue
				}
				m.handleTreeHarvest(logger, dispatcher, worldState, userID, harvestMsg)

			// NOTE: OpCodeInteractionReport (70) RETIRED — no client ever sent it, and the
			// lifecycle meters it fed are now SERVER-authoritative (advanced in the swarm loop
			// from center-at-food checks; effects ride the influence ledger).

			case OpCodeStationDeposit:
				var depositMsg StationDepositMessage
				if err := json.Unmarshal(msg.GetData(), &depositMsg); err != nil {
					logger.Warn("Invalid station deposit from %s: %v", userID, err)
					continue
				}
				m.handleStationDeposit(logger, dispatcher, worldState, userID, depositMsg)

			case OpCodeContainer:
				var caMsg ContainerActionMessage
				if err := json.Unmarshal(msg.GetData(), &caMsg); err != nil {
					logger.Warn("Invalid container action from %s: %v", userID, err)
					continue
				}
				m.handleContainerAction(logger, dispatcher, worldState, userID, caMsg)

			case OpCodeSetHome:
				var shMsg SetHomeMessage
				if err := json.Unmarshal(msg.GetData(), &shMsg); err != nil {
					logger.Warn("Invalid set-home from %s: %v", userID, err)
					continue
				}
				m.handleSetHome(logger, dispatcher, nk, worldState, userID, shMsg)

			case OpCodeEcologyTuning:
				// DEV TOOL: live-override a species' ecology parameters from the Unity debug
				// panel (server-decided values; determinism-safe).
				var tuneMsg EcologyTuningMessage
				if err := json.Unmarshal(msg.GetData(), &tuneMsg); err != nil {
					logger.Warn("Invalid ecology tuning from %s: %v", userID, err)
					continue
				}
				if sp := worldState.Species[tuneMsg.SpeciesID]; sp != nil {
					sp.ForageChance = tuneMsg.ForageChance
					if tuneMsg.ForageModeMinTicks > 0 {
						sp.ForageModeMinTicks = tuneMsg.ForageModeMinTicks
					}
					if tuneMsg.ForageModeMaxTicks > 0 {
						sp.ForageModeMaxTicks = tuneMsg.ForageModeMaxTicks
					}
					if tuneMsg.FeedAmount > 0 {
						sp.FeedAmount = tuneMsg.FeedAmount
					}
					if tuneMsg.BreedAmount > 0 {
						sp.BreedAmount = tuneMsg.BreedAmount
					}
					if tuneMsg.SatiationDecay > 0 {
						sp.SatiationDecayRate = tuneMsg.SatiationDecay
					}
					if tuneMsg.ConsumeRate > 0 {
						sp.ConsumeRate = tuneMsg.ConsumeRate
					}
					if tuneMsg.ReproduceCooldown > 0 {
						sp.ReproduceCooldown = tuneMsg.ReproduceCooldown
					}
					logger.Info("ECOLOGY TUNED %s by %s: forage=%.2f mode=%d-%dt feed=%.1f breed=%.1f decay=%.2f consume=%.2f cd=%.0fs",
						tuneMsg.SpeciesID, userID, sp.ForageChance, sp.ForageModeMinTicks, sp.ForageModeMaxTicks,
						sp.FeedAmount, sp.BreedAmount, sp.SatiationDecayRate, sp.ConsumeRate, sp.ReproduceCooldown)
				}

			case OpCodeDebugWorld:
				// DEV TOOL (the EcologyTuning convention: ungated, loudly logged).
				var dwMsg DebugWorldMessage
				if err := json.Unmarshal(msg.GetData(), &dwMsg); err != nil {
					logger.Warn("Invalid debug-world from %s: %v", userID, err)
					continue
				}
				m.handleDebugWorld(logger, dispatcher, worldState, dwMsg, userID, chunkSize)

			// Bug Sync (Late Joiner + Drift Detection)
			case OpCodeSampleResponse:
				var respMsg SampleResponseMessage
				if err := json.Unmarshal(msg.GetData(), &respMsg); err != nil {
					logger.Warn("Invalid sample response from %s: %v", userID, err)
					continue
				}
				m.handleSampleResponse(logger, dispatcher, worldState, userID, respMsg)

			case OpCodeRequestSnapshot:
				var reqMsg SnapshotRequestMessage
				if err := json.Unmarshal(msg.GetData(), &reqMsg); err != nil {
					logger.Warn("Invalid snapshot request from %s: %v", userID, err)
					continue
				}
				m.handleSnapshotRequest(logger, dispatcher, worldState, userID, reqMsg)

			case OpCodeZoneSnapshot:
				// Authority client sends periodic snapshots (OpCode 75)
				var snapMsg ZoneSnapshotMessage
				if err := json.Unmarshal(msg.GetData(), &snapMsg); err != nil {
					logger.Warn("Invalid zone snapshot from %s: %v", userID, err)
					continue
				}
				m.handleZoneSnapshot(logger, worldState, userID, snapMsg)
			}
		}

		// Broadcast entity updates to all clients
		if len(worldState.Players) > 0 {
			entityData := make([]EntityData, 0, len(worldState.Players))
			for userID, player := range worldState.Players {
				eqa := ""
				for _, piece := range player.Equipment {
					if piece != "" {
						eqa = strings.Join(player.Equipment[:], ",")
						break
					}
				}
				entityData = append(entityData, EntityData{
					ID:       "player_" + userID,
					Type:     "player",
					X:        player.WorldX(chunkSize),
					Y:        player.WorldY(chunkSize),
					Facing:   int(player.Facing),
					Equipped: player.EquippedTool,
					Eqa:      eqa,
				})
			}

			update := EntityUpdateMessage{Entities: entityData}
			data, err := json.Marshal(update)
			if err != nil {
				logger.Error("Failed to marshal entity update: %v", err)
			} else {
				dispatcher.BroadcastMessage(OpCodeEntityUpdate, data, nil, nil, true)
			}
		}

		// === Crop Growth ===
		cropCount := len(worldState.CropStates)
		if cropCount > 0 && worldState.TickCount%100 == 0 {
			logger.Debug("DEBUG: processCropGrowth starting with %d crops at tick %d", cropCount, worldState.TickCount)
		}
		m.processCropGrowth(worldState, dispatcher)

		// === Fruit Trees & Ground Item Decay ===
		m.processFruitTrees(worldState, dispatcher, logger)
		m.processHostPlants(worldState) // milkweed breeding capacity regrows
		fgt := worldState.Perf.Start()
		m.processForagePools(worldState) // flower nectar regrows (the boom-bust food)
		worldState.Perf.StopSys("forage", fgt)
		if worldState.TickCount%30 == 0 {
			nst := worldState.Perf.Start()
			m.processNests(worldState, logger)                        // occupant-gone sweep + brood-drain re-hatch
			m.processNestFounding(worldState, dispatcher, logger)     // a thriving colony splits off a daughter hive
			m.processPredatorBreeding(worldState, dispatcher, logger) // nestless carnivores breed when well-fed
			m.processBroods(worldState, dispatcher, logger)           // visible nurseries: mature eggs -> maggots -> hatch
			worldState.Perf.StopSys("nests", nst)
		}
		dct := worldState.Perf.Start()
		m.processGroundItemDecay(worldState, dispatcher)
		worldState.Perf.StopSys("decay", dct)
		m.processStations(worldState, dispatcher)      // material processors: input -> compost
		m.processCraftStations(worldState, dispatcher) // recipe processors: queued batches -> output grid

		// === Swarm Simulation ===
		deltaTime := 1.0 / float32(SimRate) // sim-seconds per tick — fixed, NOT 1/CallRate (see SimRate)

		// Blocked checker for collision detection
		isBlocked := func(x, y float32) bool {
			return worldState.IsBlocked(x, y)
		}

		// Simulate swarms — sorted-ID order (not raw map range) so rand draws, shared-food grabs, and the
		// IDs minted by breeding are a pure function of which swarms exist, not Go's randomized map order.
		// Snapshotting the IDs first also fixes the unspecified behavior of adding to a map mid-range:
		// swarms born from breeding THIS tick aren't processed until next tick (deterministic).
		for _, swarmID := range sortedStringKeys(worldState.Swarms) {
			swarm := worldState.Swarms[swarmID]
			if swarm == nil {
				continue // removed earlier this tick (predation/merge)
			}
			species := worldState.Species[swarm.SpeciesID]
			if species == nil {
				continue
			}

			// THINK: Every few seconds, pick new target (expensive). Food/breeding sources come
			// from the unified query (rotten ground fruit + filled stations + flora occupants);
			// the chosen source is CACHED on the swarm so the per-tick meter check is O(1).
			// V1 RULE: a REPRODUCING swarm only targets DEPLETABLE sources (items/stations) —
			// flora is infinite, so breeding on it would mean unbounded growth.
			// ActionState machine (centipede windup/surge/recover/gnaw): PER TICK, BEFORE
			// the think gate — surges are 25 ticks vs 8-30-tick thinks, and the bite check
			// must run every tick of flight. Owns the swarm while active.
			actionActive := false
			if species.Predation != nil && species.Category == "individual" {
				pt := worldState.Perf.Start()
				actionActive = m.processActionState(logger, dispatcher, worldState, swarm, species, chunkSize, deltaTime)
				worldState.Perf.StopSpecies(swarm.SpeciesID, "action", pt)
			}

			// Predation branches (prey FLEE / predator hunt+wander) REPLACE the shared
			// forage block when they fire — they emit their own leg, write their own
			// SpeedMult, and own NextThinkTick (hunt/flee re-aim every 10-15 ticks).
			if !actionActive && worldState.TickCount >= swarm.NextThinkTick &&
				!m.predationThink(worldState, swarm, species, chunkSize, deltaTime, logger) {
				var resourceX, resourceY float32 = float32(math.NaN()), float32(math.NaN())
				swarm.TargetFoodID = ""
				swarm.TargetFoodDepletable = false
				// The shared path resets the per-leg speed (sync contract: EVERY leg-emitting
				// path writes SpeedMult — without this a swarm that fled keeps the flee speed
				// forever, consistently on both sides and invisible to every harness) and the
				// hunt cache (exclusivity: dining and hunting never coexist).
				swarm.SpeedMult = 1.0
				swarm.TargetPreyID = ""

				// FORAGE DUTY CYCLE: the forage/wander MODE persists 30-50s (10x the leg cadence)
				// so behavior doesn't flicker leg-to-leg — rolled by forage_chance (~25% for
				// flies). Satiation/breeding fill across several feeding sessions with hunger
				// decaying in between. OVERRIDE: once sated (reproducing phase) the swarm always
				// seeks the breeding source and PARKS there until the reproduction fires.
				if worldState.TickCount >= swarm.ModeUntilTick {
					swarm.ForageMode = species.ForageChance <= 0 || worldState.Rng.Float32() < species.ForageChance
					modeMin, modeMax := int64(species.ForageModeMinTicks), int64(species.ForageModeMaxTicks)
					if modeMin <= 0 {
						modeMin = 300 // default 30s
					}
					if modeMax <= modeMin {
						modeMax = modeMin + 200
					}
					swarm.ModeUntilTick = worldState.TickCount + modeMin + worldState.Rng.Int63n(modeMax-modeMin+1)
				}
				// Hungry OR breeding bugs always forage; only comfortably-fed ones follow the idle
				// wander duty cycle. (Predators take the predationThink path above, not this one.)
				forage := swarm.ForageMode || swarm.Phase == "reproducing" || swarm.Satiation < hungerForageThreshold
				attractions := swarm.GetCurrentAttractions(species)
				if forage && len(attractions) > 0 {
					ft := worldState.Perf.Start()
					hits := FindNearbyFood(worldState, swarm.Position, species.VisionRange, attractions)
					worldState.Perf.StopSpecies(swarm.SpeciesID, "food", ft)
					worldState.Perf.Count(swarm.SpeciesID, "food_calls")
					if swarm.Phase == "reproducing" {
						kept := hits[:0]
						for _, h := range hits {
							if h.Depletable {
								kept = append(kept, h)
							}
						}
						hits = kept
					}
					if len(hits) > 0 {
						resourceX, resourceY = hits[0].X, hits[0].Y
						swarm.TargetFoodID = hits[0].ID
						swarm.TargetFoodX, swarm.TargetFoodY = hits[0].X, hits[0].Y
						swarm.TargetFoodDepletable = hits[0].Depletable
					}
				}

				// Origin = center BEFORE this leg starts (pre-Move). Emit a sparse,
				// self-describing leg event so clients re-anchor + move deterministically.
				originX := swarm.WorldX(chunkSize)
				originY := swarm.WorldY(chunkSize)

				swarm.Think(species, chunkSize, resourceX, resourceY, isBlocked, worldState.Rng)

				if worldState.CurrentZone != nil {
					worldState.AddSwarmTargetEvent(
						worldState.CurrentZone.ZoneID, swarm.ID,
						toFixed(originX), toFixed(originY),
						toFixed(swarm.TargetX), toFixed(swarm.TargetY),
						// SpeedMult is 1.0 on this path (reset above); carried explicitly
						// so the event ALWAYS equals the speed Move will use (§14).
						toFixed(species.BaseSpeed*swarm.EffectiveSpeedMult()*deltaTime),
					)
				}

				// Schedule next think: 30-50 ticks (3-5 seconds at 10 ticks/sec)
				swarm.NextThinkTick = worldState.TickCount + 30 + worldState.Rng.Int63n(21)
			}

			// MOVE: Every tick, move toward target (cheap)
			swarm.Move(deltaTime, species, chunkSize)

			// Predation strike: PER-TICK (centers can cross between the 10-15-tick re-aims).
			// O(1): cached TargetPreyID validity + one distance + the cooldown.
			if species.Predation != nil {
				m.checkPredationStrike(logger, dispatcher, worldState, swarm, species, chunkSize)
			}

			// Bug-vs-player attacks (stings/bites): contact range, cooldown + invuln gated
			if species.AttackDamage > 0 {
				m.checkBugAttacks(logger, dispatcher, worldState, swarm, species, chunkSize)
			}

			// === Lifecycle meters (server-authoritative; all effects ride the ledger) ===
			swarm.ReproduceCooldown -= deltaTime // was never decremented before this system
			swarm.CompostCooldown -= deltaTime   // detritivore compost-deposit pacing

			atFood := false
			if swarm.TargetFoodID != "" {
				if swarm.TargetFoodDepletable && !m.foodSourceAlive(worldState, swarm.TargetFoodID, swarm.TargetFoodX, swarm.TargetFoodY) {
					// Source depleted/picked up: drop it and re-Think immediately.
					swarm.ClearFoodTarget(worldState.TickCount)
				} else {
					dx := swarm.WorldX(chunkSize) - swarm.TargetFoodX
					dy := swarm.WorldY(chunkSize) - swarm.TargetFoodY
					atFood = dx*dx+dy*dy <= feedRadius*feedRadius
				}
			}

			if atFood {
				consumeRate := species.ConsumeRate
				if consumeRate <= 0 {
					consumeRate = consumePerBugPerSecond
				}
				switch swarm.Phase {
				case "feeding":
					// Species rates are per-second (FeedAmount 5 => sated in 20s).
					swarm.Satiation += species.FeedAmount * deltaTime
					if swarm.Satiation > 100 {
						swarm.Satiation = 100
					}
					if swarm.TargetFoodDepletable {
						// More flies = faster consumption (architecture_farming.md).
						drain := consumeRate * float32(swarm.Count) * deltaTime
						m.consumeFood(worldState, dispatcher, swarm.TargetFoodID, drain) // ground items / stations
						// Flower nectar (occupant-backed depletable feeding pool, keyed by cell, like the
						// milkweed-capacity drain): a big swarm exhausts it → the flower is skipped → starve.
						if fp := worldState.ForagePools[fmt.Sprintf("%d,%d", int(swarm.TargetFoodX), int(swarm.TargetFoodY))]; fp != nil {
							fp.Nectar -= drain
							if fp.Nectar < 0 {
								fp.Nectar = 0
							}
						}
					}
				case "reproducing":
					if swarm.TargetFoodDepletable { // v1: breeding requires a depletable source
						swarm.ReproductionMeter += species.BreedAmount * deltaTime
						m.consumeFood(worldState, dispatcher, swarm.TargetFoodID,
							consumeRate*float32(swarm.Count)*deltaTime)
						if swarm.ReproductionMeter >= 100 && swarm.CanReproduce() && swarm.Count > 0 {
							m.reproduceSwarm(worldState, dispatcher, swarm, species, logger)
							// Host-plant breeding (butterfly on milkweed) drains the milkweed's capacity;
							// grazed-out milkweed stops being a breeding source until it regrows.
							if hp := worldState.HostPlantStates[fmt.Sprintf("%d,%d", int(swarm.TargetFoodX), int(swarm.TargetFoodY))]; hp != nil {
								hp.Capacity -= worldState.Tuning.HostBreedCost
								if hp.Capacity < 0 {
									hp.Capacity = 0
								}
							}
							// Detritus breeding (millipede on leaf litter) drains the litter pool, the same way
							// host-plant breeding drains milkweed — so a breeding boom eats out the forest floor
							// and the millipede bust follows (the food-bound oscillation). Litter pools only.
							if fp := worldState.ForagePools[fmt.Sprintf("%d,%d", int(swarm.TargetFoodX), int(swarm.TargetFoodY))]; fp != nil && fp.EntityID == litterOccupantID {
								fp.Nectar -= worldState.Tuning.HostBreedCost
								if fp.Nectar < 0 {
									fp.Nectar = 0
								}
							}
						}
					}
				}
				// Detritivore: eating a carcass (in ANY phase — they sate fast and dine in 'reproducing')
				// produces compost: periodically drop a compost INPUT into the nearest bin; the station
				// pipeline turns it into fly food.
				if species.ProducesCompost && swarm.CompostCooldown <= 0 {
					if it, ok := worldState.GroundItems[swarm.TargetFoodID]; ok && it.IsCarrion {
						if m.depositCompostNear(worldState, dispatcher, swarm.WorldX(chunkSize), swarm.WorldY(chunkSize)) {
							swarm.CompostCooldown = 10.0 // ~1 compost input / 10s while at carrion
						}
					}
				}
			} else {
				// Hunger: satiation drains when not feeding (wired for the first time —
				// satiation_decay_rate existed in species.json but was never applied).
				swarm.Satiation -= species.SatiationDecayRate * deltaTime
				if swarm.Satiation < 0 {
					swarm.Satiation = 0
				}
			}

			// STARVATION: a swarm pinned at 0 satiation can't find food; processStarvation culls it once
			// the timer passes the threshold. Any satiation (recently fed) resets it. This turns
			// "over-large population exhausts its food" into a real BUST (vs a slow old-age drift).
			if swarm.Satiation <= 0 {
				swarm.StarveTimer += deltaTime
			} else {
				swarm.StarveTimer = 0
			}

			// Phase transitions. NO SwarmsDirty here (clients never read phase; the old dirty
			// flag only generated spurious full-set SwarmUpdate broadcasts). On a change the
			// attractions differ, so retarget immediately instead of waiting out the think timer.
			//
			// NEST predators (Predation.NestOccupant != "") skip this: their lifecycle is the
			// custom feeding/homing/defending machine — the standard sated→"reproducing" flip
			// would strand them (no breeding attractions; brood goes to the nest instead).
			// NESTLESS predators (centipede) KEEP the standard lifecycle — it's exactly what
			// makes them park at carrion and reproduce there.
			if species.Predation == nil || species.Predation.NestOccupant == "" {
				prevPhase := swarm.Phase
				swarm.CheckPhaseTransition(species)
				if swarm.Phase != prevPhase {
					swarm.ClearFoodTarget(worldState.TickCount)
				}
			}
		}

		// Check merge/split every 50 ticks (5 seconds)
		// Population pass once a minute (600 ticks at 10Hz): proximity-merge + size-split.
		// Both travel as tick+seq SWARM_MERGE/SWARM_SPLIT influence events (deterministic).
		if worldState.TickCount-worldState.LastMergeCheck >= 600 {
			mgt := worldState.Perf.Start()
			m.checkSwarmMerging(worldState, chunkSize, logger) // the O(S²) all-pairs the audit flagged
			m.checkSwarmSplitting(worldState, chunkSize, logger)
			worldState.Perf.StopSys("merge", mgt)
			worldState.LastMergeCheck = worldState.TickCount
		}

		// Check continuous spawning every 100 ticks (10 seconds)
		if worldState.TickCount%worldState.Tuning.DirectorIntervalTicks == 0 {
			m.processEcologyDirector(logger, dispatcher, worldState, chunkSize) // bands: re-seed low / cull high
		}
		if worldState.TickCount%100 == 0 {
			m.checkContinuousSpawning(worldState, worldState.TickCount, logger)
		}

		// Natural death (per-bug aging) every 100 ticks (10s): cull bugs past their DeathTick.
		if worldState.TickCount%100 == 0 {
			m.processNaturalDeath(logger, dispatcher, worldState, chunkSize)
			m.processStarvation(logger, dispatcher, worldState, chunkSize)
		}

		// === Day rollover (one day = DayLengthTicks = 14 min) ===
		// Resets every crop's daily watering count — the max_daily_waterings cap existed but
		// nothing ever reset it (documented gap, architecture_farming.md). Clients derive the
		// same day boundary from (tick + DayOffsetTicks) for their lighting cycle.
		//
		// Epoch compare (AdvanceDayIfNeeded), not modulo — a debug set-time crossing the
		// boundary must not skip/double the daily reset.
		if currentDay, rolled := worldState.AdvanceDayIfNeeded(); rolled {
			for _, crop := range worldState.CropStates {
				crop.WateringsToday = 0
			}
			m.scheduleDailyRain(worldState, logger)
			m.emitEcologyStats(worldState, currentDay, logger)  // flush the day's interaction log, then reset
			m.emitResourceStats(worldState, currentDay, logger) // + the depletable food-stock totals (supply side)
			m.emitSwarmSnapshot(worldState, currentDay, logger) // + per-swarm positions for the daily bug-map
			m.emitPerfStats(worldState, currentDay, logger)     // + the cost profiler (no-op unless profile=true)
			logger.Info("DAY %d begins (tick %d): daily watering counts reset for %d crops",
				currentDay+1, worldState.TickCount, len(worldState.CropStates))
		}

		// Weather: start the scheduled shower / end an expired one (display + one-shot
		// watering; frontier-neutral)
		m.processWeather(worldState, dispatcher, logger)

		// Player HP regen: +1 per 30s, gated on damage recency (echoed to the owner)
		m.processPlayerRegen(dispatcher, worldState)

		// Broadcast swarm SET/metadata only when it changes (NOT per tick). Positions are
		// derived deterministically on clients from SWARM_SET_TARGET events, so this carries
		// lifecycle/metadata + the current leg for clients creating a swarm's visual.
		if worldState.SwarmsDirty {
			swarmData := make([]SwarmData, 0, len(worldState.Swarms))
			for _, swarm := range worldState.Swarms {
				spriteID := swarm.SpeciesID // fallback
				if species, ok := worldState.Species[swarm.SpeciesID]; ok {
					spriteID = species.SpriteID
				}
				swarmData = append(swarmData, SwarmData{
					ID:         swarm.ID,
					SpeciesID:  swarm.SpeciesID,
					SpriteID:   spriteID,
					X:          swarm.WorldX(chunkSize),
					Y:          swarm.WorldY(chunkSize),
					Radius:     swarm.Radius,
					Count:      swarm.Count,
					Facing:     int(swarm.Facing),
					Phase:      swarm.Phase,
					NextBugID:  swarm.NextBugID,
					RemovedIDs: swarm.GetRemovedIDs(),
				})
			}

			swarmUpdate := SwarmUpdateMessage{Tick: worldState.TickCount, Swarms: swarmData}
			data, err := json.Marshal(swarmUpdate)
			if err != nil {
				logger.Error("Failed to marshal swarm update: %v", err)
			} else {
				dispatcher.BroadcastMessage(OpCodeSwarmUpdate, data, nil, nil, true)
				worldState.Perf.AddRosterBytes(len(data)) // cost profiler: roster wire size
			}
			worldState.SwarmsDirty = false
		}

		// NOTE: ground-item lifetimes are processed ONLY by processGroundItemDecay (farming pass,
		// line ~628). The old updateGroundItemLifetimes here DOUBLE-decremented Lifetime and raced
		// the rot transition (deleting fruit before it could rot) — removed.

		// Bug sync: periodic drift sampling every 300 ticks (30 seconds at 10Hz)
		if worldState.TickCount%300 == 0 {
			m.checkDriftSampling(logger, dispatcher, worldState)
		}

		// Broadcast pending influence events (server-authored bug sync)
		if len(worldState.PendingInfluence) > 0 {
			influenceMsg := InfluenceBroadcastMessage{Events: worldState.PendingInfluence}
			data, err := json.Marshal(influenceMsg)
			if err != nil {
				logger.Error("Failed to marshal influence broadcast: %v", err)
			} else {
				dispatcher.BroadcastMessage(OpCodeInfluenceBroadcast, data, nil, nil, true)
				worldState.Perf.AddInfluenceBytes(len(data)) // cost profiler: leg-batch wire size
			}
			worldState.ClearPendingInfluence()
		}

		// === TICK FRONTIER BROADCAST (OpCode 78) ===
		// CRITICAL: Must be broadcast EVERY tick, AFTER influence events
		// This is the safety mechanism for frontier-gated simulation:
		// Server guarantees all events for tick t are broadcast BEFORE frontier t
		// DEBUG: Log when broadcast is skipped
		if worldState.CurrentZone == nil {
			if worldState.TickCount%100 == 0 {
				logger.Warn("ZoneTickBroadcast SKIPPED: CurrentZone is nil at tick %d", worldState.TickCount)
			}
		} else if len(worldState.Players) == 0 && len(worldState.Presences) == 0 {
			if worldState.TickCount%100 == 0 {
				logger.Warn("ZoneTickBroadcast SKIPPED: No players/presences at tick %d", worldState.TickCount)
			}
		}
		if worldState.CurrentZone != nil && (len(worldState.Players) > 0 || len(worldState.Presences) > 0) {
			zone := worldState.GetOrCreateZone(worldState.CurrentZone.ZoneID)
			tickMsg := ZoneTickBroadcastMessage{
				ZoneID:            worldState.CurrentZone.ZoneID,
				AuthoritativeTick: worldState.TickCount,
				LastEventSeq:      zone.NextSeq - 1, // Last assigned seq (NextSeq is next to assign)
				AuthorityID:       zone.AuthorityUserID,
			}
			tickData, err := json.Marshal(tickMsg)
			if err != nil {
				logger.Error("Failed to marshal tick broadcast: %v", err)
			} else {
				dispatcher.BroadcastMessage(OpCodeZoneTickBroadcast, tickData, nil, nil, true)
			}
		}

		// Prune influence log periodically (every 100 ticks)
		if worldState.TickCount%100 == 0 && worldState.CurrentZone != nil {
			worldState.PruneInfluenceLog(worldState.CurrentZone.ZoneID, worldState.TickCount)
		}
	} // end SIM BATCH loop

	// Return state to continue (never nil for persistent world)
	return worldState
}

// MatchTerminate is called when match is ending
func (m *Match) MatchTerminate(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, graceSeconds int) interface{} {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchTerminate: invalid state type")
		return state
	}

	logger.Info("World %s terminating, grace period %d seconds", worldState.WorldID, graceSeconds)

	// ZONE PERSISTENCE: the authoritative save for a clean restart. SYNCHRONOUS — a detached
	// goroutine could be killed during teardown; graceSeconds gives the window to finish the write.
	if recs := m.snapshotZoneState(worldState); len(recs) > 0 {
		writeZoneRecords(ctx, nk, logger, recs)
		logger.Info("Zone %s: persisted %d record(s) on terminate", worldState.ZoneID, len(recs))
	}

	return worldState
}

// MatchSignal handles external commands (e.g., from RPC)
func (m *Match) MatchSignal(ctx context.Context, logger runtime.Logger, db *sql.DB, nk runtime.NakamaModule, dispatcher runtime.MatchDispatcher, tick int64, state interface{}, data string) (interface{}, string) {
	worldState, ok := state.(*WorldState)
	if !ok {
		logger.Error("MatchSignal: invalid state type")
		return state, `{"error": "internal error"}`
	}

	// Parse signal command
	var cmd map[string]interface{}
	if err := json.Unmarshal([]byte(data), &cmd); err != nil {
		return worldState, `{"error": "invalid signal format"}`
	}

	action, _ := cmd["action"].(string)

	switch action {
	case "get_info":
		info := map[string]interface{}{
			"world_id":     worldState.WorldID,
			"name":         worldState.Name,
			"player_count": len(worldState.Players),
			"tick_count":   worldState.TickCount,
		}
		response, _ := json.Marshal(info)
		return worldState, string(response)

	default:
		return worldState, fmt.Sprintf(`{"error": "unknown action: %s"}`, action)
	}
}

// updateLabel updates the match label with current player count
func (m *Match) updateLabel(dispatcher runtime.MatchDispatcher, state *WorldState) {
	label := MatchLabel{
		WorldID:      state.WorldID,
		Name:         state.Name,
		PlayerCount:  len(state.Players),
		MaxPlayers:   state.Config.MaxPlayers,
		AccessPolicy: state.AccessPolicy,
	}
	labelJSON, _ := json.Marshal(label)
	dispatcher.MatchLabelUpdate(string(labelJSON))
}

// defaultFlySpecies returns a fallback species map if config fails to load
func defaultFlySpecies() map[string]*entities.BugSpecies {
	return map[string]*entities.BugSpecies{
		"fly": {
			ID:             "fly",
			Name:           "Common Fly",
			Category:       "swarm",
			BaseSpeed:      1.5,
			WanderRadius:   8.0,
			MinSwarmSize:   5,
			MaxSwarmSize:   50,
			SwarmRadius:    4.0,
			MergeRadius:    4.0,
			SplitThreshold: 40,
			SplitChance:    0.01,
		},
	}
}

// spawnInitialSwarms seeds the world with swarms using zone-level species caps.
// Initial seeding spawns cap.Initial swarms per species immediately on match init.
func (m *Match) spawnInitialSwarms(state *WorldState, logger runtime.Logger) {
	cfg := state.CurrentZone.BugSpawning
	if cfg == nil {
		logger.Info("No bug spawning config for zone")
		return
	}

	totalSpawned := 0

	// Initialize species tracking and spawn initial swarms
	for _, speciesID := range sortedStringKeys(cfg.SpeciesCaps) { // sorted: initial spawn mints IDs in order
		cap := cfg.SpeciesCaps[speciesID]
		state.SwarmsBySpecies[speciesID] = []string{}

		// Schedule first continuous spawn check
		state.SpeciesNextSpawn[speciesID] = float64(cap.SpawnInterval)

		// NEST species (wasp): population comes ONLY from the placed nest occupants — their founding
		// residents are staffed at chunk-load by registerNestAt, and dead colonies recover via the
		// prey-gated nest path (processNests). NEVER a free swarm. Skipping them here removes the
		// "nestless wasp" reseeds at the root (the bug we traced: fat-but-sterile free-spawned wasps).
		if cap.MaxNests > 0 {
			continue
		}

		// SPREAD START (2026-06): distribute the Initial swarms round-robin across ALL of the species'
		// habitat circles, so the populated start is spatially spread — every grove/meadow/patch gets
		// seeded — instead of piled into one weighted-random spot. Falls back to the weighted pick for a
		// species with no circle habitat (only a zone-wide area).
		circles := m.habitatCirclesForSpecies(cfg, speciesID)
		species := state.Species[speciesID]
		for i := 0; i < cap.Initial; i++ {
			var swarm *entities.SwarmState
			if len(circles) > 0 && species != nil {
				swarm = m.spawnSwarmInArea(state, speciesID, species, cap, circles[i%len(circles)], logger)
			} else {
				swarm = m.spawnSwarmForSpecies(state, speciesID, logger)
			}
			if swarm != nil {
				totalSpawned++
				state.Stats.recordBirth(speciesID, BirthSpawn, swarm.Count)
			}
		}

		logger.Debug("Species %s: seeded %d swarms across %d habitat circles", speciesID, cap.Initial, len(circles))
	}

	logger.Info("Seeded world with %d swarms across %d species",
		totalSpawned, len(cfg.SpeciesCaps))
}

// seedInitialCarrion drops the zone's authored carrion ground items (BugSpawnConfig.InitialCarrion) at
// match start — the day-1 food bootstrap (e.g. dead millipedes in the woods so the local flies breed and
// the beetles feed from tick 0, instead of waiting for the first natural deaths). Created directly into
// state.GroundItems (no dispatcher: this runs at MatchInit before any client joins, like restoreSwarms);
// clients receive them on chunk subscribe. Deterministic: fixed positions + the GroundItemSeq counter.
func (m *Match) seedInitialCarrion(state *WorldState, logger runtime.Logger) {
	cfg := state.CurrentZone.BugSpawning
	if cfg == nil || len(cfg.InitialCarrion) == 0 {
		return
	}
	chunkSize := state.Config.ChunkSize
	seeded := 0
	for _, seed := range cfg.InitialCarrion {
		if seed.Item == "" {
			continue
		}
		n := seed.Count
		if n <= 0 {
			n = 1
		}
		foodValue := 0
		if def := state.Entities[seed.Item]; def != nil {
			foodValue = def.FoodValue
		}
		for i := 0; i < n; i++ {
			// Fan multiples out along X so they don't stack on one cell (deterministic offset).
			pos := entities.EntityPosition{LocalX: float32(seed.X + i), LocalY: float32(seed.Y)}
			pos.Normalize(chunkSize)
			itemID := state.nextItemID("item_carcass")
			state.GroundItems[itemID] = &entities.GroundItem{
				ID:        itemID,
				ItemType:  seed.Item,
				Count:     1,
				Position:  pos,
				Lifetime:  killDropLifetime,
				FoodValue: foodValue,
				IsCarrion: true,
			}
			if foodValue > 0 && state.CurrentZone != nil {
				state.AddFoodEvent(state.CurrentZone.ZoneID, InfluenceItemRotted, itemID,
					seed.X+i, seed.Y, foodValue)
			}
			seeded++
		}
	}
	logger.Info("Seeded %d authored carrion ground items", seeded)
}

// habitatCirclesForSpecies returns the species' circle-type spawn areas (its named habitats), in authored
// order — the targets for spread-on-spawn seeding. Zone-wide (wild-card) areas are excluded so the spread
// hits actual habitats, not random map cells.
func (m *Match) habitatCirclesForSpecies(cfg *BugSpawnConfig, speciesID string) []SpawnArea {
	var out []SpawnArea
	for _, area := range cfg.SpawnAreas {
		if area.Type != "circle" {
			continue
		}
		for _, s := range area.Species {
			if s == speciesID {
				out = append(out, area)
				break
			}
		}
	}
	return out
}

// spawnSwarmForSpecies creates a new swarm for the given species in a valid spawn area.
// Returns nil if species is at zone cap or has no valid spawn areas.
func (m *Match) spawnSwarmForSpecies(state *WorldState, speciesID string, logger runtime.Logger) *entities.SwarmState {
	cfg := state.CurrentZone.BugSpawning
	cap := cfg.SpeciesCaps[speciesID]

	// Check zone-level cap for this species
	aliveCount := 0
	for _, swarmID := range state.SwarmsBySpecies[speciesID] {
		if _, exists := state.Swarms[swarmID]; exists {
			aliveCount++
		}
	}
	if aliveCount >= cap.Max {
		return nil
	}

	// Get species definition
	species := state.Species[speciesID]
	if species == nil {
		logger.Warn("Unknown species %s", speciesID)
		return nil
	}

	// Find spawn areas that include this species
	var validAreas []SpawnArea
	for _, area := range cfg.SpawnAreas {
		for _, s := range area.Species {
			if s == speciesID {
				validAreas = append(validAreas, area)
				break
			}
		}
	}
	if len(validAreas) == 0 {
		logger.Warn("No spawn areas defined for species %s", speciesID)
		return nil
	}

	// WEIGHTED area pick: a species' habitat circles carry a high weight, the zone-wide wild-card a low
	// one (SpawnArea.Weight, default 1.0) — so most spawns land in-habitat and a minority wander in
	// anywhere (the ~3:1 model). Used by the Director re-seed; the initial/continuous paths spread across
	// all circles instead (spawnSwarmInArea).
	totalW := 0.0
	for _, a := range validAreas {
		w := a.Weight
		if w <= 0 {
			w = 1.0
		}
		totalW += w
	}
	area := validAreas[len(validAreas)-1] // fallback for float rounding
	roll := state.Rng.Float64() * totalW
	for _, a := range validAreas {
		w := a.Weight
		if w <= 0 {
			w = 1.0
		}
		if roll < w {
			area = a
			break
		}
		roll -= w
	}

	return m.spawnSwarmInArea(state, speciesID, species, cap, area, logger)
}

// spawnSwarmInArea mints ONE swarm of the species inside a specific spawn area — the shared core of the
// weighted single-pick (spawnSwarmForSpecies) and the spread-across-all-habitats seeding. Honors the
// per-species swarm-count cap and retries for a walkable cell. Returns nil at cap or if no walkable cell is
// found. Does NOT record a birth — the caller attributes the source (BirthSpawn vs BirthReseed).
// Determinism: draws state.Rng in a fixed order (count, then position retries).
func (m *Match) spawnSwarmInArea(state *WorldState, speciesID string, species *entities.BugSpecies, cap SpeciesCap, area SpawnArea, logger runtime.Logger) *entities.SwarmState {
	// Per-species swarm-count cap (spawn back-pressure).
	aliveCount := 0
	for _, swarmID := range state.SwarmsBySpecies[speciesID] {
		if _, exists := state.Swarms[swarmID]; exists {
			aliveCount++
		}
	}
	if aliveCount >= cap.Max {
		return nil
	}

	// Generate a position, RETRYING for a walkable cell so a zone-wide (or water-overlapping circle)
	// spawn never lands in the lake / a wall — natural death still handles merely-suboptimal spots.
	var worldX, worldY float32
	placed := false
	for attempt := 0; attempt < 12; attempt++ {
		if area.Type == "zone" {
			worldX = float32(state.Rng.Intn(state.CurrentZone.Width))
			worldY = float32(state.Rng.Intn(state.CurrentZone.Height))
		} else {
			angle := state.Rng.Float64() * 2 * math.Pi
			r := float64(area.Radius) * math.Sqrt(state.Rng.Float64()) // sqrt for uniform distribution
			worldX = float32(area.CX) + float32(r*math.Cos(angle))
			worldY = float32(area.CY) + float32(r*math.Sin(angle))
		}
		if !state.IsBlocked(worldX, worldY) {
			placed = true
			break
		}
	}
	if !placed {
		return nil // no walkable cell found (rare) — skip this spawn rather than drop a bug in terrain
	}

	// Convert to chunk position
	chunkSize := state.Config.ChunkSize
	pos := entities.EntityPosition{
		ChunkX: int(worldX) / chunkSize,
		ChunkY: int(worldY) / chunkSize,
		LocalX: worldX - float32(int(worldX)/chunkSize*chunkSize),
		LocalY: worldY - float32(int(worldY)/chunkSize*chunkSize),
	}

	// Determine bug count: fixed swarm_size if set (deterministic test zones),
	// else species MinSwarmSize plus a random amount in the lower-middle range.
	countRange := species.MaxSwarmSize / 2
	if countRange < 1 {
		countRange = 1
	}
	count := species.MinSwarmSize + state.Rng.Intn(countRange)
	if cap.SwarmSize > 0 {
		count = cap.SwarmSize
	}
	id, _ := uuid.NewV4()
	swarm := &entities.SwarmState{
		ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
		SpeciesID: speciesID,
		Position:  pos,
		Radius:    species.SwarmRadius,
		Count:     count,
		WanderRad: species.WanderRadius,
		HomePos:   pos,
		Satiation: state.Tuning.SpawnSatiation, // born half-fed (see const) — natural-spawn + Director re-seed path
	}
	swarm.InitializeBugIDs()
	assignDeathTicks(swarm, species, 0, count, state.TickCount, SimRate)

	state.Swarms[swarm.ID] = swarm
	state.SwarmsBySpecies[speciesID] = append(state.SwarmsBySpecies[speciesID], swarm.ID)
	state.SwarmsDirty = true
	// Deterministic spawn via the ledger (see AddSwarmSpawnedEvent) — all clients create at the same tick.
	if state.CurrentZone != nil {
		state.AddSwarmSpawnedEvent(state.CurrentZone.ZoneID, swarm.ID, speciesID, count,
			toFixed(swarm.WorldX(chunkSize)), toFixed(swarm.WorldY(chunkSize)))
	}

	logger.Debug("Spawned swarm %s (%s) in %s at (%.0f, %.0f)",
		swarm.ID, speciesID, area.ID, worldX, worldY)

	return swarm
}

// checkContinuousSpawning spawns new swarms over time until species caps are reached.
// Should be called periodically from the tick loop.
func (m *Match) checkContinuousSpawning(state *WorldState, tick int64, logger runtime.Logger) {
	if state.StaticSim {
		return // Skip continuous spawning in debug mode
	}

	cfg := state.CurrentZone.BugSpawning
	if cfg == nil {
		return
	}

	currentTime := float64(tick) / float64(SimRate) // sim-seconds (spawn-interval clock) — fixed

	for _, speciesID := range sortedStringKeys(cfg.SpeciesCaps) { // sorted: continuous spawn mints IDs in order
		cap := cfg.SpeciesCaps[speciesID]
		// Check if it's time to try spawning
		if currentTime < state.SpeciesNextSpawn[speciesID] {
			continue
		}
		// Schedule next attempt up front (so the nest-species `continue` below doesn't skip the clock).
		nextAt := currentTime + float64(cap.SpawnInterval)

		// NEST species (wasp): no free immigration — nests + recovery own the population.
		if cap.MaxNests > 0 {
			state.SpeciesNextSpawn[speciesID] = nextAt
			continue
		}

		// Clean up dead/caught swarms from species tracking
		var aliveSwarms []string
		for _, swarmID := range state.SwarmsBySpecies[speciesID] {
			if _, exists := state.Swarms[swarmID]; exists {
				aliveSwarms = append(aliveSwarms, swarmID)
			}
		}
		state.SwarmsBySpecies[speciesID] = aliveSwarms

		// Spawn one new swarm if below the swarm-count cap AND the population cap
		// (defense in depth — natural spawns stop refilling a saturated zone). SPREAD: the immigration
		// trickle rotates through the species' habitat circles round-robin (a per-species cursor), so over
		// time fresh bugs reach EVERY grove/patch — keeping each predator region's prey topped up — rather
		// than always landing in the weighted-random favourite. Same gentle volume (one swarm per interval).
		atPopCap := cap.MaxPopulation > 0 && state.SpeciesPopulation(speciesID) >= cap.MaxPopulation
		if len(aliveSwarms) < cap.Max && !atPopCap {
			circles := m.habitatCirclesForSpecies(cfg, speciesID)
			species := state.Species[speciesID]
			var swarm *entities.SwarmState
			if len(circles) > 0 && species != nil {
				idx := state.SpeciesSpawnCursor[speciesID] % len(circles)
				state.SpeciesSpawnCursor[speciesID] = idx + 1
				swarm = m.spawnSwarmInArea(state, speciesID, species, cap, circles[idx], logger)
			} else {
				swarm = m.spawnSwarmForSpecies(state, speciesID, logger)
			}
			if swarm != nil {
				state.Stats.recordBirth(speciesID, BirthSpawn, swarm.Count)
				logger.Debug("Continuous spawn: %s (%s) [%d/%d]",
					swarm.ID, speciesID, len(aliveSwarms)+1, cap.Max)
			}
		}

		// Schedule next spawn attempt
		state.SpeciesNextSpawn[speciesID] = nextAt
	}
}

// checkSwarmMerging merges nearby swarms of the same species
// depositCompostNear bumps the INPUT of the nearest food-producing station (compost bin) within
// range of (x,y) by one — the existing processStations pipeline converts input→compost→fly food (a
// deterministic food-level event). Detritivores call this while eating carrion. Returns true if a
// deposit happened. Server-authoritative; InputCount is display state, the food rise rides the ledger.
func (m *Match) depositCompostNear(state *WorldState, dispatcher runtime.MatchDispatcher, x, y float32) bool {
	const compostRadius2 = 12.0 * 12.0
	var best *entities.StationState
	var bestCap int
	bestD := float32(compostRadius2)
	for _, st := range state.Stations {
		def := state.Entities[st.EntityID]
		if def == nil || def.World == nil || def.World.Station == nil || def.World.Station.FoodPerUnit <= 0 {
			continue // only food-producing stations (compost bins)
		}
		capacity := def.World.Station.Capacity
		if capacity <= 0 {
			capacity = 10
		}
		if st.InputCount >= capacity {
			continue // input backlog full
		}
		sx := float32(st.GridX) + 0.5
		sy := float32(st.GridY) + 0.5
		dx, dy := sx-x, sy-y
		if d := dx*dx + dy*dy; d < bestD {
			bestD, best, bestCap = d, st, capacity
		}
	}
	if best == nil {
		return false
	}
	best.InputCount++
	m.broadcastStationUpdate(dispatcher, best, bestCap)
	return true
}

// processNaturalDeath culls bugs that have reached their scheduled DeathTick (set at birth from the
// species lifespan). Server-authoritative: emits BUG_REMOVED per culled bug (clients replay) + drops
// a species carcass. Collects culls first, then acts (so it never mutates state.Swarms mid-range —
// matches the merge/split style). Removal order is irrelevant: BUG_REMOVED events commute.
func (m *Match) processNaturalDeath(logger runtime.Logger, dispatcher runtime.MatchDispatcher, state *WorldState, chunkSize int) {
	now := state.TickCount
	type cull struct {
		swarm *entities.SwarmState
		ids   []int
	}
	var culls []cull
	for _, swID := range sortedStringKeys(state.Swarms) { // sorted: carcass spawns consume deterministic item IDs
		swarm := state.Swarms[swID]
		if len(swarm.DeathTick) == 0 || swarm.Count <= 0 {
			continue
		}
		var dead []int
		for id, dt := range swarm.DeathTick {
			if dt <= now && swarm.IsBugAlive(id) {
				dead = append(dead, id)
			}
		}
		if len(dead) > 0 {
			culls = append(culls, cull{swarm, dead})
		}
	}
	for _, c := range culls {
		state.Stats.recordDeath(c.swarm.SpeciesID, DeathOldAge, len(c.ids))
		m.killBugsNaturally(logger, dispatcher, state, c.swarm, state.Species[c.swarm.SpeciesID], c.ids, chunkSize)
	}
}

// Starvation tuning — a swarm that can't find food (StarveTimer accumulating at 0 satiation) dies back.
// This is what turns an over-large population into a real BUST (the down-swing of the boom-bust). The
// cull fraction + pause set how sharp the bust is (tuned on the population graph). Deaths drop carcasses
// (killBugsNaturally) so the recycle loop still runs.
const (
	starvationDeathSecs = 60.0 // sim-seconds at 0 satiation before a swarm starts to starve to death
	starvationCullFrac  = 0.10 // fraction of the swarm culled per starvation event (min 1 bug)
	starvationCullPause = 10.0 // sim-seconds between successive culls while still starving

	// A newly spawned swarm starts half-fed — a bug entering the world has eaten recently. Without this,
	// every swarm is born at Satiation 0 and its StarveTimer accrues immediately; a PREDATOR (no food
	// at its feet, must hunt) is then culled ~starvationDeathSecs after spawn before it can reach prey.
	// At a wasp's 0.4/s decay, 50 satiation = ~125 sim-s of runway to find a meal. The StarveTimer
	// self-resets the moment satiation rises (match.go:1294), so this is the only guard newborns need.
	spawnSatiation = 50.0
)

// processStarvation culls a fraction of any swarm that has been starving past the threshold, then
// re-arms its timer so it keeps dying back (gradually) until it finds food again. Collect-then-act
// (no map mutation mid-range), mirroring processNaturalDeath.
func (m *Match) processStarvation(logger runtime.Logger, dispatcher runtime.MatchDispatcher, state *WorldState, chunkSize int) {
	type cull struct {
		swarm *entities.SwarmState
		ids   []int
	}
	var culls []cull
	for _, swID := range sortedStringKeys(state.Swarms) { // sorted: starvation carcasses consume deterministic item IDs
		swarm := state.Swarms[swID]
		if swarm.Count <= 0 || swarm.StarveTimer < state.Tuning.StarvationDeathSecs {
			continue
		}
		n := int(float32(swarm.Count) * state.Tuning.StarvationCullFrac)
		if n < 1 {
			n = 1
		}
		if ids := swarm.FirstAliveBugIDs(n); len(ids) > 0 {
			culls = append(culls, cull{swarm, ids})
		}
		swarm.StarveTimer = starvationDeathSecs - starvationCullPause // re-arm: cull again after the pause if still starving
	}
	for _, c := range culls {
		state.Stats.recordDeath(c.swarm.SpeciesID, DeathStarve, len(c.ids))
		m.killBugsNaturally(logger, dispatcher, state, c.swarm, state.Species[c.swarm.SpeciesID], c.ids, chunkSize)
	}
}

func (m *Match) checkSwarmMerging(state *WorldState, chunkSize int, logger runtime.Logger) {
	if state.StaticSim {
		return // Skip merging in debug mode
	}

	merged := make(map[string]bool)
	toDelete := []string{}

	// Deterministic order: the lower-id swarm is always the survivor (id1). Map iteration order is
	// randomized, so without this the merge survivor — and thus the id remapping — would vary run to
	// run (non-reproducible; flaked the transfer tests). Server-authoritative either way; pinning it
	// keeps merges reproducible.
	mergeIDs := make([]string, 0, len(state.Swarms))
	for id := range state.Swarms {
		mergeIDs = append(mergeIDs, id)
	}
	sort.Strings(mergeIDs)

	for _, id1 := range mergeIDs {
		swarm1 := state.Swarms[id1]
		if swarm1 == nil || merged[id1] {
			continue
		}
		species1 := state.Species[swarm1.SpeciesID]
		if species1 == nil || species1.Category == "individual" {
			continue // individuals (centipede) never merge
		}

		for _, id2 := range mergeIDs {
			swarm2 := state.Swarms[id2]
			if swarm2 == nil || id1 == id2 || merged[id2] {
				continue
			}
			if swarm1.SpeciesID != swarm2.SpeciesID {
				continue
			}

			// Calculate distance between swarm centers
			dist := distBetweenSwarms(swarm1, swarm2, chunkSize)

			// Merge if within merge radius (centers mostly overlapping)
			if dist <= species1.MergeRadius {
				combined := swarm1.Count + swarm2.Count
				// Only merge if combined doesn't exceed max
				if combined <= species1.MaxSwarmSize {
					// The absorbed swarm's bugs become NEW survivor ids starting at the
					// survivor's pre-merge NextBugID — they stay alive + catchable
					// (IsBugAlive requires id < NextBugID). Lazy-init guard first.
					if swarm1.NextBugID == 0 {
						swarm1.NextBugID = swarm1.Count
					}
					newBugIDBase := swarm1.NextBugID
					swarm1.NextBugID += swarm2.Count
					swarm1.Count = combined
					merged[id2] = true
					toDelete = append(toDelete, id2)

					// Transfer damaged HP + natural-death schedule along the exact mapping the
					// client applies: absorbed alive ids ASCENDING -> survivor ids newBugIDBase+k.
					if len(swarm2.BugHP) > 0 || len(swarm2.DeathTick) > 0 {
						if swarm2.NextBugID == 0 {
							swarm2.NextBugID = swarm2.Count
						}
						k := 0
						for aid := 0; aid < swarm2.NextBugID; aid++ {
							if !swarm2.IsBugAlive(aid) {
								continue
							}
							newID := newBugIDBase + k
							if hp, ok := swarm2.BugHP[aid]; ok {
								if swarm1.BugHP == nil {
									swarm1.BugHP = make(map[int]int)
								}
								swarm1.BugHP[newID] = hp
							}
							if dt, ok := swarm2.DeathTick[aid]; ok {
								if swarm1.DeathTick == nil {
									swarm1.DeathTick = make(map[int]int64)
								}
								swarm1.DeathTick[newID] = dt
							}
							k++
						}
					}

					// Tick+seq event: clients MOVE the absorbed bugs into the survivor at
					// the event tick (positions preserved). NO SwarmsDirty — the lifecycle
					// change travels only through the deterministic ledger.
					if state.CurrentZone != nil {
						state.AddSwarmMergeEvent(state.CurrentZone.ZoneID, id1, id2, swarm2.Count, newBugIDBase)
					}
				}
			}
		}
	}

	// Delete merged swarms after iteration (and keep SwarmsBySpecies consistent)
	for _, id := range toDelete {
		if sw, ok := state.Swarms[id]; ok {
			ids := state.SwarmsBySpecies[sw.SpeciesID]
			for i, sid := range ids {
				if sid == id {
					state.SwarmsBySpecies[sw.SpeciesID] = append(ids[:i], ids[i+1:]...)
					break
				}
			}
		}
		delete(state.Swarms, id)
	}

	if len(toDelete) > 0 {
		logger.Info("Merged %d swarms (via SWARM_MERGE events)", len(toDelete))
	}
}

// checkSwarmSplitting splits any swarm whose size exceeds the species limit (deterministic
// size rule — no random roll). The parent sheds its HIGHEST splitCount alive bug-ids into a
// new child swarm; clients MOVE those exact bugs at the event tick (positions preserved).
func (m *Match) checkSwarmSplitting(state *WorldState, chunkSize int, logger runtime.Logger) {
	if state.StaticSim {
		return // Skip splitting in debug mode
	}

	newSwarms := []*entities.SwarmState{}

	for _, swarmID := range sortedStringKeys(state.Swarms) { // sorted: child IDs + offsetPosition rand are order-dependent
		swarm := state.Swarms[swarmID]
		if swarm == nil {
			continue
		}
		species := state.Species[swarm.SpeciesID]
		if species == nil || species.Category == "individual" {
			continue // individuals (centipede) never split — belt+braces over the sizes
		}

		// Deterministic size rule: split when over the split limit. SplitThreshold (if set) decouples the
		// split POINT from MaxSwarmSize (the nominal spawn/merge size) — a swarm grows to SplitThreshold
		// before halving into smaller, more-dispersed swarms. Falls back to MaxSwarmSize when 0/unset, so it's
		// a no-op until tuned. (Keep SplitThreshold >= MaxSwarmSize to avoid merge↔split churn.)
		splitLimit := species.MaxSwarmSize
		if species.SplitThreshold > 0 {
			splitLimit = species.SplitThreshold
		}
		if swarm.Count > splitLimit {
			splitCount := swarm.Count / 2
			if splitCount < species.MinSwarmSize || swarm.Count-splitCount < species.MinSwarmSize {
				continue // Either half would be too small
			}

			// Shed the HIGHEST splitCount alive ids (the client mirrors this exact set:
			// it moves its highest alive ids into the child, in sorted order).
			if swarm.NextBugID == 0 {
				swarm.NextBugID = swarm.Count // lazy-init guard (initial swarms are initialized at spawn)
			}
			shed := make([]int, 0, splitCount)
			for id := swarm.NextBugID - 1; id >= 0 && len(shed) < splitCount; id-- {
				if swarm.IsBugAlive(id) {
					shed = append(shed, id)
				}
			}

			// Harvest damaged HP BEFORE RemoveBugs deletes the entries. The client maps
			// the shed ids ASCENDING -> child ids 0..n-1; mirror that mapping exactly
			// (shed was collected descending above).
			var shedHP map[int]int
			var shedDeath map[int]int64
			if len(swarm.BugHP) > 0 || len(swarm.DeathTick) > 0 {
				asc := append([]int(nil), shed...)
				sort.Ints(asc)
				for childID, oldID := range asc {
					if hp, ok := swarm.BugHP[oldID]; ok {
						if shedHP == nil {
							shedHP = make(map[int]int)
						}
						shedHP[childID] = hp
					}
					if dt, ok := swarm.DeathTick[oldID]; ok {
						if shedDeath == nil {
							shedDeath = make(map[int]int64)
						}
						shedDeath[childID] = dt
					}
				}
			}

			swarm.RemoveBugs(shed) // marks RemovedBugIDs + decrements Count (no double-decrement)

			// Create the child offset from the parent; NextThinkTick=0 -> it Thinks (and
			// emits its first SWARM_SET_TARGET leg) on the next tick.
			id, _ := uuid.NewV4()
			newPos := offsetPosition(swarm.Position, 3.0, chunkSize, state.Rng)
			// Clamp the child centre against walls/fences: offsetPosition is collision-blind,
			// and a PENNED swarm that grows past the limit must split INSIDE the pen (else the
			// child centre lands beyond the fence and its bugs strain at the wall forever).
			{
				px := swarm.WorldX(chunkSize)
				py := swarm.WorldY(chunkSize)
				nx := float32(newPos.ChunkX*chunkSize) + newPos.LocalX
				ny := float32(newPos.ChunkY*chunkSize) + newPos.LocalY
				cxw, cyw := entities.RaycastClamp(px, py, nx, ny, func(x, y float32) bool {
					return state.IsBlocked(x, y)
				})
				newPos = entities.EntityPosition{LocalX: cxw, LocalY: cyw}
				newPos.Normalize(chunkSize)
			}

			newSwarm := &entities.SwarmState{
				ID:        fmt.Sprintf("swarm_%s", id.String()[:8]),
				SpeciesID: swarm.SpeciesID,
				Position:  newPos,
				Radius:    swarm.Radius,
				Count:     len(shed),
				HomePos:   newPos,
				WanderRad: swarm.WanderRad,
				Satiation: swarm.Satiation, // a split inherits the parent's fed-ness (they were one swarm)
			}
			newSwarm.InitializeBugIDs()    // child ids 0..count-1
			newSwarm.BugHP = shedHP        // damaged HP follows the moved bugs (nil if none)
			newSwarm.DeathTick = shedDeath // natural-death schedule follows the moved bugs too
			newSwarms = append(newSwarms, newSwarm)

			// Tick+seq event: lifecycle travels ONLY through the deterministic ledger
			// (NO SwarmsDirty — avoids the on-receipt SwarmUpdate creation race).
			if state.CurrentZone != nil {
				state.AddSwarmSplitEvent(state.CurrentZone.ZoneID, swarm.ID, newSwarm.ID,
					len(shed), swarm.Count, // swarm.Count is already POST-shed here
					toFixed(newSwarm.WorldX(chunkSize)), toFixed(newSwarm.WorldY(chunkSize)))
			}
		}
	}

	// Add new swarms after iteration (and keep SwarmsBySpecies consistent — was missing)
	for _, s := range newSwarms {
		state.Swarms[s.ID] = s
		state.SwarmsBySpecies[s.SpeciesID] = append(state.SwarmsBySpecies[s.SpeciesID], s.ID)
	}

	if len(newSwarms) > 0 {
		logger.Info("Split %d over-limit swarms (via SWARM_SPLIT events)", len(newSwarms))
	}
}

// toFixed converts a float32 world coordinate to the client fixed-point scale (×1000).
// Matches FixedPoint.Scale on the client so leg events deserialize without rescaling.
func toFixed(v float32) int {
	return int(math.Round(float64(v) * 1000.0))
}

// distBetweenSwarms calculates world distance between two swarms
func distBetweenSwarms(s1, s2 *entities.SwarmState, chunkSize int) float32 {
	dx := s1.WorldX(chunkSize) - s2.WorldX(chunkSize)
	dy := s1.WorldY(chunkSize) - s2.WorldY(chunkSize)
	return float32(math.Sqrt(float64(dx*dx + dy*dy)))
}

// offsetPosition creates a new position offset by the given distance
func offsetPosition(pos entities.EntityPosition, offset float32, chunkSize int, rng *rand.Rand) entities.EntityPosition {
	angle := rng.Float64() * 2 * math.Pi
	newPos := entities.EntityPosition{
		ChunkX: pos.ChunkX,
		ChunkY: pos.ChunkY,
		LocalX: pos.LocalX + float32(math.Cos(angle))*offset,
		LocalY: pos.LocalY + float32(math.Sin(angle))*offset,
	}
	newPos.Normalize(chunkSize)
	return newPos
}

// handleCatchBug processes a catch attempt from a player (Phase 2a)
// Client-trusted: client detects flies and sends count, server trusts it
func (m *Match) handleCatchBug(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg CatchBugMessage,
	playerID string,
	chunkSize int,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}

	// Tool stats are DATA (items.json), not hardcoded ids — any net works, and new
	// tiers need zero code. Hand defaults when no net is equipped.
	maxReach := float32(2.0)
	maxCatch := 5
	cooldown := int64(2) // hand: 2 ticks = the old 200ms at 10Hz
	if toolDef := state.Entities[player.EquippedTool]; toolDef != nil && toolDef.ToolType == "net" {
		if toolDef.Reach > 0 {
			maxReach = toolDef.Reach
		}
		if toolDef.CatchCap > 0 {
			maxCatch = toolDef.CatchCap
		}
		if toolDef.CooldownTicks > 0 {
			cooldown = int64(toolDef.CooldownTicks)
		}
	}

	// Rate limit per SWING: one swing's messages arrive as a same-tick burst (one per
	// hit swarm) and share the slot — stamping per-message used to silently drop every
	// swarm after the first, ghost-removing those bugs on the catching client.
	tick := state.TickCount
	if tick != player.LastCatchTick {
		if tick-player.LastCatchTick < cooldown {
			return
		}
		player.LastCatchTick = tick
	}

	// Get player world position using existing method
	playerX := player.WorldX(chunkSize)
	playerY := player.WorldY(chunkSize)

	// Validate click is within reach (+slack for swing geometry/latency)
	dx := msg.ClickX - playerX
	dy := msg.ClickY - playerY
	reachSlack := maxReach + 0.5
	if dx*dx+dy*dy > reachSlack*reachSlack {
		return // Too far
	}

	// Look up the specific swarm
	swarm, exists := state.Swarms[msg.SwarmID]
	if !exists || swarm.Count <= 0 {
		return
	}

	// NET-TIER gate (the first enforcement of species net_size): hand ≡ tier 1
	// (small) — hand-catching flies AND butterflies stays core early game; wasps
	// need the large net; trap_only (centipede) rejects EVERYTHING incl. hands.
	if catchSpecies := state.Species[swarm.SpeciesID]; catchSpecies != nil {
		required := netSizeTier(catchSpecies.NetSize)
		netTier := 1 // bare hands / the hands tool
		if toolDef := state.Entities[player.EquippedTool]; toolDef != nil &&
			toolDef.ToolType == "net" && toolDef.ToolTier > 0 {
			netTier = toolDef.ToolTier
		}
		if netTier < required {
			if required >= netTierTrapOnly {
				m.sendWorldError(dispatcher, state, playerID, "Far too big for any net!")
			} else {
				m.sendWorldError(dispatcher, state, playerID, "You need a larger net for that bug!")
			}
			return
		}
	}

	bugIDs := msg.BugIDs
	if len(bugIDs) > maxCatch {
		bugIDs = bugIDs[:maxCatch]
	}

	// Validate and remove bugs - returns only valid, alive IDs
	removed := swarm.RemoveBugs(bugIDs)
	if len(removed) == 0 {
		return
	}

	// Emit BUG_REMOVED influence events for deterministic late joiner replay
	// Each removed bug gets its own event so replay can process them individually
	if state.CurrentZone != nil {
		zoneID := state.CurrentZone.ZoneID
		for _, bugID := range removed {
			state.AddInfluenceEvent(zoneID, InfluenceBugRemoved, "", 0, 0, swarm.ID, bugID)
		}
	}

	// Add to player's bug inventory
	slotIdx := player.AddBugs(swarm.SpeciesID, len(removed))

	// Broadcast catch event to all clients with validated bug IDs
	caughtMsg := BugCaughtMessage{
		SwarmID:   swarm.ID,
		CatcherID: playerID,
		BugIDs:    removed,
		NewTotal:  swarm.Count,
		X:         msg.ClickX,
		Y:         msg.ClickY,
	}
	data, _ := json.Marshal(caughtMsg)
	dispatcher.BroadcastMessage(OpCodeBugCaught, data, nil, nil, true)

	// Send slot update to catcher only (if bugs were added successfully)
	if slotIdx >= 0 {
		slotMsg := SlotUpdateMessage{
			SlotIndex: slotIdx,
			ItemID:    player.BugSlots[slotIdx].ItemID,
			Count:     player.BugSlots[slotIdx].Count,
		}
		slotData, _ := json.Marshal(slotMsg)
		presence := state.Presences[playerID]
		dispatcher.BroadcastMessage(OpCodeBugSlotUpdate, slotData,
			[]runtime.Presence{presence}, nil, true)
	}

	// Remove empty swarm (despawn → re-broadcast set so clients drop the visual)
	if swarm.Count <= 0 {
		delete(state.Swarms, swarm.ID)
		state.SwarmsDirty = true
	}
}

// handleMoveSlot processes inventory slot move/swap operations
func (m *Match) handleMoveSlot(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	msg MoveSlotMessage,
	playerID string,
) {
	player, exists := state.Players[playerID]
	if !exists {
		return
	}

	// Perform the move
	if !player.MoveSlot(msg.SourceType, msg.SourceIndex, msg.DestType, msg.DestIndex, msg.Count) {
		// Move failed - send error to client
		errMsg := ErrorMessage{Error: "Invalid move operation"}
		errData, _ := json.Marshal(errMsg)
		presence := state.Presences[playerID]
		dispatcher.BroadcastMessage(OpCodeErrorMessage, errData,
			[]runtime.Presence{presence}, nil, true)
		return
	}

	// Send slot updates for both affected slots
	presence := state.Presences[playerID]

	// Determine which OpCode to use based on slot type
	opCode := OpCodeBugSlotUpdate
	if msg.SourceType == "item" {
		opCode = OpCodeItemSlotUpdate
	}

	// Source slot update
	var srcSlot InventorySlot
	if msg.SourceType == "bug" {
		srcSlot = player.BugSlots[msg.SourceIndex]
	} else {
		srcSlot = player.ItemSlots[msg.SourceIndex]
	}
	srcMsg := SlotUpdateMessage{
		SlotIndex: msg.SourceIndex,
		ItemID:    srcSlot.ItemID,
		Count:     srcSlot.Count,
		Metadata:  srcSlot.Metadata, // tool state travels with the move (sendSlotUpdate precedent)
	}
	srcData, _ := json.Marshal(srcMsg)
	dispatcher.BroadcastMessage(opCode, srcData, []runtime.Presence{presence}, nil, true)

	// Destination slot update
	var dstSlot InventorySlot
	if msg.DestType == "bug" {
		dstSlot = player.BugSlots[msg.DestIndex]
	} else {
		dstSlot = player.ItemSlots[msg.DestIndex]
	}
	dstMsg := SlotUpdateMessage{
		SlotIndex: msg.DestIndex,
		ItemID:    dstSlot.ItemID,
		Count:     dstSlot.Count,
		Metadata:  dstSlot.Metadata,
	}
	dstData, _ := json.Marshal(dstMsg)
	dispatcher.BroadcastMessage(opCode, dstData, []runtime.Presence{presence}, nil, true)

	logger.Debug("Player %s moved slot %s[%d] -> %s[%d]",
		playerID, msg.SourceType, msg.SourceIndex, msg.DestType, msg.DestIndex)
}

// updateGroundItemLifetimes REMOVED: it duplicated processGroundItemDecay (which handles both
// decay-to-rot and plain expiry), double-decrementing every item's Lifetime and racing the rot
// transition — dropped fruit frequently got deleted before it could become rotten. One processor now.

// handleInteractionReport REMOVED (OpCode 70 retired): no client ever sent it, and the
// lifecycle meters are now SERVER-authoritative — advanced in the swarm simulation loop from
// centre-at-food checks (see the Lifecycle meters block), with all effects on the ledger
// (SWARM_REPRODUCED / FOOD_CONSUMED). This removes the multi-client double-count risk too.

// === Bug Sync (Late Joiner + Drift Detection) ===

// handleSampleResponse processes OpCode 62 - a client's state hash at the settled drift tick.
// It accumulates responses into the chunk's DriftCheck; once every expected (still-connected)
// client has answered, it compares the equal-tick hashes and issues a targeted late-join
// resync to any minority. Hashes are only ever compared at the SAME tick, so this never
// false-positives on legitimate motion (the bug in the old position-sampling scheme).
func (m *Match) handleSampleResponse(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	senderID string,
	msg SampleResponseMessage,
) {
	chunkKey := ChunkKey(msg.ChunkX, msg.ChunkY)
	check := state.DriftChecks[chunkKey]
	if check == nil || msg.Tick != check.SampleTick || !check.Expected[senderID] {
		return // Stale, unsolicited, or not part of this round
	}

	check.Responded[senderID] = true
	if msg.HasHash {
		check.Votes[senderID] = msg.Hash
	}
	// HasHash==false: client lacks that tick (e.g. just resynced) - abstains, no vote.

	// Wait until every still-connected expected client has responded.
	for userID := range check.Expected {
		if _, connected := state.Presences[userID]; !connected {
			continue // Disconnected mid-round - don't wait on it
		}
		if !check.Responded[userID] {
			return // Still waiting
		}
	}

	// Round complete - tally votes.
	delete(state.DriftChecks, chunkKey)
	counts := make(map[int64]int)
	for _, h := range check.Votes {
		counts[h]++
	}
	if len(counts) <= 1 {
		return // Unanimous (or nobody voted) - no drift
	}

	// Pick the majority hash as the reference. On a tie, skip to avoid resync storms.
	var refHash int64
	bestCount, tie := -1, false
	for h, c := range counts {
		if c > bestCount {
			bestCount, refHash, tie = c, h, false
		} else if c == bestCount {
			tie = true
		}
	}
	if tie {
		logger.Warn("Drift check for chunk %d,%d at tick %d: ambiguous hash split %v - skipping resync",
			msg.ChunkX, msg.ChunkY, check.SampleTick, counts)
		return
	}

	// Resync every voter that disagreed with the majority.
	for userID, h := range check.Votes {
		if h == refHash {
			continue
		}
		if p, ok := state.Presences[userID]; ok && p != nil {
			logger.Warn("Drift detected: client %s hash %d != majority %d at tick %d - resyncing",
				userID, h, refHash, check.SampleTick)
			m.sendLateJoinSnapshot(logger, dispatcher, state, userID, p)
		}
	}
}

// handleSnapshotRequest processes OpCode 66 - a client's request for a full zone resync.
// The frontier system is zone-scoped, so recovery routes through the same proven late-join
// path (snapshot -> influence-log replay -> handoff -> live) rather than partial chunk
// catch-up, which cannot safely rewind the zone-wide simulation tick. The chunk fields in
// the request are ignored; resync is always zone-wide for the requester.
func (m *Match) handleSnapshotRequest(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	requesterID string,
	msg SnapshotRequestMessage,
) {
	presence, ok := state.Presences[requesterID]
	if !ok || presence == nil {
		logger.Warn("Resync request from %s but no presence found", requesterID)
		return
	}

	logger.Info("Zone resync requested by %s - sending late-join snapshot", requesterID)
	m.sendLateJoinSnapshot(logger, dispatcher, state, requesterID, presence)
}

// handleZoneSnapshot stores a snapshot from the authority client (OpCode 75).
// The server stores (but does not inspect) the snapshot for late joiners.
func (m *Match) handleZoneSnapshot(
	logger runtime.Logger,
	state *WorldState,
	senderID string,
	msg ZoneSnapshotMessage,
) {
	zone := state.GetOrCreateZone(msg.ZoneID)

	// Only accept snapshots from the current authority
	if zone.AuthorityUserID != senderID {
		logger.Warn("Ignoring snapshot from non-authority %s (authority is %s)", senderID, zone.AuthorityUserID)
		return
	}

	// Store the snapshot (opaque to server)
	zone.LatestSnapshot = &ZoneSnapshot{
		ZoneID:               msg.ZoneID,
		SnapshotTick:         msg.SnapshotTick,
		SnapshotLastEventSeq: msg.SnapshotLastEventSeq,
		Swarms:               msg.Swarms,
		Food:                 msg.Food, // relay the authoritative food registry (opaque to server)
		StateHash:            msg.StateHash,
	}
	zone.LatestSnapshotTick = msg.SnapshotTick
	zone.LatestSnapshotHash = msg.StateHash

	logger.Debug("Stored snapshot from authority %s at tick %d, last_event_seq=%d", senderID, msg.SnapshotTick, msg.SnapshotLastEventSeq)
}

// buildSwarmSeedBaseline returns swarm METADATA (no per-bug positions) for every live swarm, so a
// joiner with no per-bug snapshot can CREATE the swarms and seed their bugs deterministically from
// (worldSeed, swarmId, bugId) at the swarm centre. Two callers:
//   - the FIRST joiner (ZoneAuthority): it IS the origin of truth, so seed-from-centre is exactly
//     right (no client has simulated, no per-bug positions exist anywhere yet); and
//   - a late joiner in the rare window before the authority's first snapshot (empty bootstrap): it
//     gets seed-from-centre too — no worse than the pre-existing SwarmUpdate bootstrap, and the
//     drift-resync converges it to the authority's exact state (see task: on-demand snapshot).
// The live leg (last SWARM_SET_TARGET) is hydrated so the centre marches from tick one.
func (m *Match) buildSwarmSeedBaseline(state *WorldState, zone *ZoneState, chunkSize int) []SwarmData {
	ids := make([]string, 0, len(state.Swarms))
	for id := range state.Swarms {
		ids = append(ids, id)
	}
	sort.Strings(ids) // deterministic order (cosmetic; keeps logs/diffs stable)

	baseline := make([]SwarmData, 0, len(ids))
	for _, id := range ids {
		swarm := state.Swarms[id]
		spriteID := swarm.SpeciesID
		if species, ok := state.Species[swarm.SpeciesID]; ok {
			spriteID = species.SpriteID
		}
		meta := SwarmData{
			ID:         swarm.ID,
			SpeciesID:  swarm.SpeciesID,
			SpriteID:   spriteID,
			X:          swarm.WorldX(chunkSize),
			Y:          swarm.WorldY(chunkSize),
			Radius:     swarm.Radius,
			Count:      swarm.Count,
			Facing:     int(swarm.Facing),
			Phase:      swarm.Phase,
			NextBugID:  swarm.NextBugID,
			RemovedIDs: swarm.GetRemovedIDs(),
		}
		// Hydrate the leg active now (latest SWARM_SET_TARGET in the unpruned log) so the closed-form
		// centre march starts correct; swarms with no leg yet get one via their first live event.
		for i := len(zone.InfluenceLog) - 1; i >= 0; i-- {
			evt := zone.InfluenceLog[i]
			if evt.Type == InfluenceSwarmSetTarget && evt.SwarmID == swarm.ID {
				meta.HasTarget = true
				meta.LegOriginX = evt.OriginX
				meta.LegOriginY = evt.OriginY
				meta.LegTargetX = evt.TargetX
				meta.LegTargetY = evt.TargetY
				meta.LegSpeed = evt.Speed
				meta.LegStartTick = evt.Tick
				break
			}
		}
		baseline = append(baseline, meta)
	}
	return baseline
}

// sendLateJoinSnapshot sends a LateJoinSnapshot (OpCode 72) to a joining player.
// This contains the authority's snapshot plus the influence log for replay.
func (m *Match) sendLateJoinSnapshot(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	joinerID string,
	presence runtime.Presence,
) {
	if state.CurrentZone == nil {
		logger.Warn("Cannot send late join snapshot - no current zone")
		return
	}

	zoneID := state.CurrentZone.ZoneID
	zone := state.GetOrCreateZone(zoneID)

	// Check if we have a snapshot from authority.
	// If no snapshot yet (rare ~1-frame window before the authority's first snapshot), bootstrap:
	// the joiner CREATES the current swarms from a seed-baseline (see buildSwarmSeedBaseline) and
	// drift-resync converges it to the authority's exact per-bug state. NOT via SwarmUpdate anymore.
	bootstrap := false
	if zone.LatestSnapshot == nil {
		bootstrap = true
		logger.Info("No authority snapshot yet, creating seed-baseline bootstrap for late joiner %s in zone %s", joinerID, zoneID)
		zone.LatestSnapshot = &ZoneSnapshot{
			ZoneID:               zoneID,
			SnapshotTick:         state.TickCount,
			SnapshotLastEventSeq: zone.NextSeq - 1,      // All events to date are "in" the bootstrap state
			Swarms:               []SwarmSnapshotData{}, // No per-bug data; swarm_metadata carries the seed-baseline
			StateHash:            "",
		}
		zone.LatestSnapshotTick = state.TickCount
	}

	snapshotTick := zone.LatestSnapshotTick
	endTick := state.TickCount
	snapshotLastSeq := zone.LatestSnapshot.SnapshotLastEventSeq
	endLastSeq := zone.NextSeq - 1 // Current watermark

	// Build influence log by seq interval (spec §8.2: "Do not filter by tick alone. Use seq intervals.")
	// Include events where seq ∈ (snapshotLastSeq, endLastSeq]
	var influenceLog []InfluenceEvent
	for _, evt := range zone.InfluenceLog {
		if evt.Seq > snapshotLastSeq && evt.Seq <= endLastSeq {
			influenceLog = append(influenceLog, evt)
		}
	}

	// Server packaging verification (spec §7.5)
	if len(influenceLog) > 0 {
		firstSeq := influenceLog[0].Seq
		lastSeq := influenceLog[len(influenceLog)-1].Seq
		logger.Info("LateJoinSnapshot packaging: seq interval (%d, %d], events=%d, first_seq=%d, last_seq=%d",
			snapshotLastSeq, endLastSeq, len(influenceLog), firstSeq, lastSeq)
	} else {
		logger.Info("LateJoinSnapshot packaging: seq interval (%d, %d], events=0 (empty)",
			snapshotLastSeq, endLastSeq)
	}

	// Late-join coherence summary (one line): how many swarms are leg-less at snapshot (their first leg
	// arrives during replay) and how many food-registry entries ride the snapshot. Both must hydrate
	// coherently or fresh swarms feeding at a food source desync — see architecture_swarm_sync.md.
	noLegCount := 0
	for _, s := range zone.LatestSnapshot.Swarms {
		if !s.HasLeg {
			noLegCount++
		}
	}
	logger.Info("LateJoinSnapshot coherence: swarms=%d (leg-less=%d) food_entries=%d",
		len(zone.LatestSnapshot.Swarms), noLegCount, len(zone.LatestSnapshot.Food))

	// Collect current player cell positions from authoritative state
	// This is snapshot state, NOT event reconstruction
	// Only include players currently in zone.Members (connected, zone-resident)
	var playerCells []PlayerCellData
	for playerID := range zone.Members {
		if cell, ok := state.PlayerCells[playerID]; ok {
			playerCells = append(playerCells, PlayerCellData{
				PlayerID: playerID,
				CellX:    cell.CellX,
				CellY:    cell.CellY,
			})
		}
	}

	// Sanity check: playerCells should match zone.Members count
	// If mismatch, state.PlayerCells wasn't updated correctly on join/leave
	if len(playerCells) != len(zone.Members) {
		logger.Warn("LateJoinSnapshot: playerCells=%d but zone.Members=%d - possible state sync bug",
			len(playerCells), len(zone.Members))
	}

	// Collect swarm metadata for creating swarm visuals on client
	// This allows clients to create swarms BEFORE replay, so snapshot positions can be applied
	chunkSize := state.Config.ChunkSize
	var swarmMetadata []SwarmData
	if bootstrap {
		// No authority snapshot: deliver the seed-baseline (client creates + seeds from centre).
		swarmMetadata = m.buildSwarmSeedBaseline(state, zone, chunkSize)
	}
	for _, swarmSnapshot := range zone.LatestSnapshot.Swarms {
		if swarm, ok := state.Swarms[swarmSnapshot.SwarmID]; ok {
			spriteID := swarm.SpeciesID // fallback
			if species, ok := state.Species[swarm.SpeciesID]; ok {
				spriteID = species.SpriteID
			}
			meta := SwarmData{
				ID:         swarm.ID,
				SpeciesID:  swarm.SpeciesID,
				SpriteID:   spriteID,
				X:          swarm.WorldX(chunkSize),
				Y:          swarm.WorldY(chunkSize),
				Radius:     swarm.Radius,
				Count:      swarm.Count,
				Facing:     int(swarm.Facing),
				Phase:      swarm.Phase,
				NextBugID:  swarm.NextBugID,
				RemovedIDs: swarm.GetRemovedIDs(),
			}

			// Seed the joiner's display-only HP for damaged bugs (server-owned truth,
			// the RemovedIDs precedent). Subsequent MeleeResultMessages converge it.
			if len(swarm.BugHP) > 0 {
				ids := make([]int, 0, len(swarm.BugHP))
				for bugID := range swarm.BugHP {
					ids = append(ids, bugID)
				}
				sort.Ints(ids)
				meta.BugHP = make([]BugHPEntry, 0, len(ids))
				for _, bugID := range ids {
					meta.BugHP = append(meta.BugHP, BugHPEntry{BugID: bugID, HP: swarm.BugHP[bugID]})
				}
			}

			// Hydrate the leg active AT snapshotTick. PREFERRED source: the authority embedded its live
			// leg in the snapshot (swarmSnapshot.HasLeg) — this is reliable even for slow swarms whose last
			// SWARM_SET_TARGET has been pruned from the InfluenceLog. (The old log-scan below missed those,
			// so late-joiners fell back to the metadata center and the swarm center diverged.) Legs started
			// after snapshotTick still replay from influenceLog and overwrite this at their own tick.
			if swarmSnapshot.HasLeg {
				meta.HasTarget = true
				meta.LegOriginX = swarmSnapshot.LegOriginX
				meta.LegOriginY = swarmSnapshot.LegOriginY
				meta.LegTargetX = swarmSnapshot.LegTargetX
				meta.LegTargetY = swarmSnapshot.LegTargetY
				meta.LegSpeed = swarmSnapshot.LegSpeed
				meta.LegStartTick = swarmSnapshot.LegStartTick
			} else {
				// Fallback (pre-leg-embedding snapshots, or bootstrap): scan the pruned InfluenceLog.
				for i := len(zone.InfluenceLog) - 1; i >= 0; i-- {
					evt := zone.InfluenceLog[i]
					if evt.Type == InfluenceSwarmSetTarget && evt.SwarmID == swarm.ID && evt.Tick <= snapshotTick {
						meta.HasTarget = true
						meta.LegOriginX = evt.OriginX
						meta.LegOriginY = evt.OriginY
						meta.LegTargetX = evt.TargetX
						meta.LegTargetY = evt.TargetY
						meta.LegSpeed = evt.Speed
						meta.LegStartTick = evt.Tick
						break
					}
				}
			}

			swarmMetadata = append(swarmMetadata, meta)
		}
	}

	msg := LateJoinSnapshot{
		ZoneID:               zoneID,
		WorldSeed:            state.WorldSeed,
		SnapshotTick:         snapshotTick,
		EndTick:              endTick,
		SnapshotLastEventSeq: snapshotLastSeq,
		EndLastEventSeq:      endLastSeq,
		Swarms:               zone.LatestSnapshot.Swarms,
		SwarmMetadata:        swarmMetadata,
		InfluenceLog:         influenceLog,
		AuthorityID:          zone.AuthorityUserID,
		PlayerCells:          playerCells,
		Food:                 zone.LatestSnapshot.Food, // authoritative food registry for late-join hydration
	}

	data, err := json.Marshal(msg)
	if err != nil {
		logger.Error("Failed to marshal late join snapshot: %v", err)
		return
	}

	dispatcher.BroadcastMessage(OpCodeLateJoinSnapshot, data, []runtime.Presence{presence}, nil, true)
	swarmCount := 0
	if zone.LatestSnapshot != nil && zone.LatestSnapshot.Swarms != nil {
		swarmCount = len(zone.LatestSnapshot.Swarms)
	}
	logger.Info("Sent LateJoinSnapshot to %s: tick range %d to %d, seq range (%d, %d], %d events, %d player_cells, %d swarms, %d swarm_metadata",
		joinerID, snapshotTick, endTick, snapshotLastSeq, endLastSeq, len(influenceLog), len(playerCells), swarmCount, len(swarmMetadata))
	for _, cell := range playerCells {
		logger.Info("  PlayerCell: %s at (%d, %d)", cell.PlayerID, cell.CellX, cell.CellY)
	}

	// Send ZoneHandoff to confirm the tick range
	// This guarantees: "no undisclosed events <= end_tick"
	handoffMsg := ZoneHandoffMessage{
		ZoneID:        zoneID,
		LiveStartTick: endTick + 1,
		LastEventSeq:  endLastSeq, // Watermark at handoff time (spec §3.6)
	}
	handoffData, _ := json.Marshal(handoffMsg)
	dispatcher.BroadcastMessage(OpCodeZoneHandoff, handoffData, []runtime.Presence{presence}, nil, true)
	logger.Info("Sent ZoneHandoff to %s: live_start_tick=%d, last_event_seq=%d", joinerID, endTick+1, endLastSeq)
}

// driftSampleMargin is how far behind the frontier the sampled tick sits, so every client
// has already simulated it (and still has it buffered) by the time the request arrives.
const driftSampleMargin = 20 // ticks (~2s at 10Hz)

// checkDriftSampling performs periodic, tick-aligned drift detection.
// Called every 300 ticks (~30s). For each chunk with ≥2 connected clients it asks ALL of
// them for ComputeStateHash() at the SAME settled tick (TickCount - margin) and records the
// expected responders in a DriftCheck. handleSampleResponse compares the equal-tick hashes and
// resyncs any minority. This replaces position sampling, which compared positions across
// mismatched ticks and produced false-positive resyncs every 30s.
func (m *Match) checkDriftSampling(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
) {
	sampleTick := state.TickCount - driftSampleMargin
	if sampleTick < 0 {
		return // Not enough history yet
	}

	for chunkKey, subs := range state.ChunkSubs {
		// Collect connected clients in this chunk
		var presences []runtime.Presence
		expected := make(map[string]bool)
		for playerID := range subs {
			if p, ok := state.Presences[playerID]; ok && p != nil {
				presences = append(presences, p)
				expected[playerID] = true
			}
		}
		if len(expected) < 2 {
			continue // Need at least 2 clients to compare
		}

		// Parse chunk coordinates
		var cx, cy int
		fmt.Sscanf(chunkKey, "%d,%d", &cx, &cy)

		// Open a fresh drift-check round (overwrites any stale one for this chunk)
		state.DriftChecks[chunkKey] = &DriftCheck{
			SampleTick: sampleTick,
			Expected:   expected,
			Responded:  make(map[string]bool),
			Votes:      make(map[string]int64),
		}

		reqMsg := SampleRequestMessage{ChunkX: cx, ChunkY: cy, Tick: sampleTick}
		data, _ := json.Marshal(reqMsg)
		dispatcher.BroadcastMessage(OpCodeRequestSample, data, presences, nil, true)
		logger.Debug("Drift hash request sent to %d clients for chunk %d,%d at tick %d",
			len(presences), cx, cy, sampleTick)
	}
}
