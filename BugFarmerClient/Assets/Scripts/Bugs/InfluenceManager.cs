using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.Entities;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Manages player cell positions from server-authored influence events.
    /// CRITICAL: Bug AI reads from this manager, NOT from player transforms.
    /// This ensures all clients process the same ordered event stream for deterministic behavior.
    ///
    /// Rules:
    /// - PLAYER_CELL_ENTER overwrites cell position
    /// - PLAYER_CELL_LEAVE does nothing (keeps last known position)
    /// - This guarantees single cell per player, no transient states
    /// </summary>
    public class InfluenceManager : MonoBehaviour
    {
        public static InfluenceManager Instance { get; private set; }

        // Player cell positions from server events only
        // Key: player_id, Value: (cellX, cellY)
        private readonly Dictionary<string, (int cellX, int cellY)> _playerCells = new();

        // Re-anchoring movement legs for swarm centers from SWARM_SET_TARGET events.
        // Each leg fully describes a movement segment; the center is derived deterministically
        // via a closed-form march (see TryComputeSwarmCenter). No per-frame mutation.
        // Key: swarm_id
        private readonly Dictionary<string, SwarmLeg> _swarmLegs = new();

        private struct SwarmLeg
        {
            public FixedPoint2 Origin;
            public FixedPoint2 Target;
            public FixedPoint Speed;   // Distance per tick (fixed-point)
            public long StartTick;     // Tick the leg began
        }

        // Phase 2 individual-fly predation: which prey a predator swarm is hunting + its strike params,
        // read from the hunt SWARM_SET_TARGET fields. The AUTHORITY uses this to pick the nearest
        // individual fly to strike. Populated only while a predator is actively hunting; cleared otherwise.
        // Key: predator swarm_id.
        private readonly Dictionary<string, SwarmStrike> _swarmStrikes = new();

        public struct SwarmStrike
        {
            public string TargetPreyId;
            public int StrikeRadiusFixed; // ×1000 (compare via FixedPoint multiply, NOT raw int²)
            public int KillsPerStrike;
            public int StrikeCooldownTicks;
        }

        // Event type constants (must match server)
        public const string EventPlayerCellEnter = "PLAYER_CELL_ENTER";
        public const string EventPlayerCellLeave = "PLAYER_CELL_LEAVE";
        public const string EventSwarmSetTarget = "SWARM_SET_TARGET";
        public const string EventBugRemoved = "BUG_REMOVED";
        public const string EventBugSpawned = "BUG_SPAWNED";
        public const string EventSwarmSplit = "SWARM_SPLIT";
        public const string EventSwarmMerge = "SWARM_MERGE";
        public const string EventSwarmReproduced = "SWARM_REPRODUCED";
        public const string EventSwarmSpawned = "SWARM_SPAWNED";
        public const string EventItemRotted = "ITEM_ROTTED";
        public const string EventFoodConsumed = "FOOD_CONSUMED";
        public const string EventOccupantBlocksBugs = "OCCUPANT_BLOCKS_BUGS"; // Phase 1b: fence/wall placed (level=1) or removed (0)
        public const string EventTreeFruitGrow = "TREE_FRUIT_GROW"; // server-only ledger; fruit shown via OpCode 93
        public const string EventTreeFruitDrop = "TREE_FRUIT_DROP"; // server-only ledger; fruit shown via OpCode 93

        // === Deterministic FOOD REGISTRY ===
        // food_id -> (world position, remaining level). Maintained ONLY from tick+seq events
        // (ITEM_ROTTED registers; FOOD_CONSUMED sets the level, 0 removes) plus one documented
        // exception: on-receipt HYDRATION of already-rotten ground items re-sent on chunk
        // subscribe (join-time bootstrap, same approximate-until-resync class as snapshots).
        // Bug landing visuals read this; it must never be mutated from OpCode-47/48 directly.
        private readonly Dictionary<string, (FixedPoint2 pos, int level)> _food = new();

        /// <summary>Join-time bootstrap for an already-rotten ground item (see note above).</summary>
        public void HydrateFood(string foodId, Vector2 worldPos, int level)
        {
            if (level <= 0 || _food.ContainsKey(foodId)) return;
            _food[foodId] = (FixedPoint2.FromVector2(worldPos), level);
        }

        /// <summary>
        /// Deterministic nearest food source within maxDist of a point (the swarm centre).
        /// Ties broken by food id. Returns false if none in range.
        /// </summary>
        public bool TryGetNearestFood(FixedPoint2 from, float maxDist, out FixedPoint2 pos)
        {
            pos = default;
            int bestSqr = int.MaxValue;
            string bestId = null;
            var maxFixed = FixedPoint.FromFloat(maxDist);
            int maxSqr = (maxFixed * maxFixed).Value;
            foreach (var kv in _food)
            {
                int sqr = kv.Value.pos.SqrDistanceTo(from).Value;
                if (sqr > maxSqr) continue;
                if (sqr < bestSqr || (sqr == bestSqr && string.CompareOrdinal(kv.Key, bestId) < 0))
                {
                    bestSqr = sqr;
                    bestId = kv.Key;
                    pos = kv.Value.pos;
                }
            }
            return bestId != null;
        }

        /// <summary>Like TryGetNearestFood but ALSO returns the food id — an individual predator needs the id to
        /// report a corpse-consume. Deterministic (same _food + ascending-id tie-break on every client).</summary>
        public bool TryGetNearestFoodId(FixedPoint2 from, float maxDist, out string foodId, out FixedPoint2 pos)
        {
            pos = default; foodId = null;
            int bestSqr = int.MaxValue;
            var maxFixed = FixedPoint.FromFloat(maxDist);
            int maxSqr = (maxFixed * maxFixed).Value;
            foreach (var kv in _food)
            {
                int sqr = kv.Value.pos.SqrDistanceTo(from).Value;
                if (sqr > maxSqr) continue;
                if (sqr < bestSqr || (sqr == bestSqr && string.CompareOrdinal(kv.Key, foodId) < 0))
                { bestSqr = sqr; foodId = kv.Key; pos = kv.Value.pos; }
            }
            return foodId != null;
        }

        /// <summary>Resolve a specific food source's current position by id (a bug feeding at ONE corpse); false if
        /// it's gone (consumed / rotted).</summary>
        public bool TryGetFoodPos(string foodId, out FixedPoint2 pos)
        {
            if (foodId != null && _food.TryGetValue(foodId, out var v)) { pos = v.pos; return true; }
            pos = default; return false;
        }

        /// <summary>Clear the registry (late-join resync re-bootstraps it).</summary>
        public void ClearFood() => _food.Clear();

        /// <summary>
        /// Export the full food registry so the AUTHORITY can embed it in its ZoneSnapshot. The registry is
        /// event-sourced and pruned, so (like swarm legs) the live registry is the reliable late-join source.
        /// Raw FixedPoint.Value coords — bit-exact hydration, no float round-trip.
        /// </summary>
        public IEnumerable<(string id, int x, int y, int level)> ExportFood()
        {
            foreach (var kv in _food)
                yield return (kv.Key, kv.Value.pos.X.Value, kv.Value.pos.Y.Value, kv.Value.level);
        }

        /// <summary>
        /// Hydrate one food entry from a snapshot (late-join), using raw FixedPoint.Value coords for bit-exact
        /// determinism. Overwrites unconditionally (authoritative); subsequent replay events converge it.
        /// </summary>
        public void HydrateFoodExact(string foodId, int x, int y, int level)
        {
            if (string.IsNullOrEmpty(foodId) || level <= 0) return;
            _food[foodId] = (new FixedPoint2(
                new FixedPoint { Value = x }, new FixedPoint { Value = y }), level);
        }

        // ── Hunt assignments (_swarmStrikes) snapshot, mirroring the food registry ──────────────────────────
        // _swarmStrikes is per-swarm predator→prey state set ONLY from live/replayed SWARM_SET_TARGET events, so
        // a late-joiner whose predator's hunt leg predates the replay window would have no prey list and wander
        // while the authority hunts → per-bug desync. Snapshot it exactly like _food: authority ExportSwarmStrikes
        // → relay → joiner ClearSwarmStrikes + HydrateSwarmStrike (before replay). Replay-window events converge
        // it on top. Same clear-then-hydrate discipline as ClearFood/HydrateFoodExact.

        /// <summary>Clear the hunt assignments (late-join/resync re-hydrates from the snapshot).</summary>
        public void ClearSwarmStrikes() => _swarmStrikes.Clear();

        /// <summary>Export the full hunt-assignment dict so the AUTHORITY can embed it in its ZoneSnapshot.</summary>
        public IEnumerable<(string predatorId, SwarmStrike strike)> ExportSwarmStrikes()
        {
            foreach (var kv in _swarmStrikes)
                yield return (kv.Key, kv.Value);
        }

        /// <summary>Hydrate one hunt assignment from a snapshot (late-join). Overwrites authoritatively; replay
        /// events converge it. An empty target_prey_id means "not hunting" — skip (leaves no entry).</summary>
        public void HydrateSwarmStrike(string predatorId, string targetPreyId, int strikeRadius, int kills, int cooldown)
        {
            if (string.IsNullOrEmpty(predatorId) || string.IsNullOrEmpty(targetPreyId)) return;
            _swarmStrikes[predatorId] = new SwarmStrike
            {
                TargetPreyId = targetPreyId,
                StrikeRadiusFixed = strikeRadius,
                KillsPerStrike = kills,
                StrikeCooldownTicks = cooldown,
            };
        }

        private void Awake()
        {
            Instance = this;
        }

        // NOTE: OpCode 71 (InfluenceBroadcast) is handled by SwarmManager,
        // which controls event buffering during REPLAY state and calls
        // ProcessInfluenceEvent() directly for deterministic event ordering.

        /// <summary>
        /// Process a single influence event.
        /// Called from match data handler or during late join replay.
        /// </summary>
        public void ProcessInfluenceEvent(InfluenceEvent evt)
        {
            switch (evt.type)
            {
                case EventPlayerCellEnter:
                    // Overwrite cell position - player is now in this cell
                    _playerCells[evt.player_id] = (evt.cell_x, evt.cell_y);
                    break;

                case EventPlayerCellLeave:
                    // DO NOTHING - keep last known position
                    // ENTER will overwrite when player enters new cell
                    // This guarantees single cell per player, no transient states
                    break;

                case EventSwarmSetTarget:
                    // Re-anchor this swarm's center to a new movement leg.
                    // origin/target/speed are fixed-point (value/1000 = actual).
                    _swarmLegs[evt.swarm_id] = new SwarmLeg
                    {
                        Origin = new FixedPoint2(
                            new FixedPoint { Value = evt.origin_x },
                            new FixedPoint { Value = evt.origin_y }),
                        Target = new FixedPoint2(
                            new FixedPoint { Value = evt.target_x },
                            new FixedPoint { Value = evt.target_y }),
                        Speed = new FixedPoint { Value = evt.speed },
                        StartTick = evt.tick
                    };
                    // Phase 2: a HUNT leg carries the prey + strike params (empty on every other leg) —
                    // store for the authority's strike pass; clear when this predator stops hunting.
                    if (!string.IsNullOrEmpty(evt.target_prey_id))
                    {
                        _swarmStrikes[evt.swarm_id] = new SwarmStrike
                        {
                            TargetPreyId = evt.target_prey_id,
                            StrikeRadiusFixed = evt.strike_radius,
                            KillsPerStrike = evt.kills_per_strike,
                            StrikeCooldownTicks = evt.strike_cooldown_ticks,
                        };
                    }
                    else
                    {
                        _swarmStrikes.Remove(evt.swarm_id);
                    }
                    break;

                case EventBugRemoved:
                    // Remove bug from swarm (for late joiner replay)
                    SwarmManager.Instance?.GetSwarm(evt.swarm_id)?.RemoveBugsById(new[] { evt.bug_id });
                    break;

                case EventBugSpawned:
                    // Future: handle bug spawning for reproduction
                    break;

                case EventSwarmSplit:
                    // Over-limit swarm sheds its highest bug-ids into a new child swarm.
                    // Applied at the event tick on every client; bugs MOVE (positions preserved).
                    SwarmManager.Instance?.HandleSwarmSplit(evt);
                    break;

                case EventSwarmMerge:
                    // Overlapping swarm absorbed into a survivor; its bugs MOVE across.
                    SwarmManager.Instance?.HandleSwarmMerge(evt);
                    break;

                case EventSwarmReproduced:
                    // Sated swarm bred at a food source: spawn the new bugs at the centre.
                    SwarmManager.Instance?.HandleSwarmReproduced(evt);
                    break;

                case EventSwarmSpawned:
                    // A new swarm minted at runtime: create it + seed its bugs from the spawn seed at
                    // THIS event tick (idempotent). Replaces SwarmUpdate-create so live followers and
                    // late-join replay all create it at the same tick → identical wander-step count.
                    SwarmManager.Instance?.HandleSwarmSpawned(evt);
                    break;

                case EventItemRotted:
                    // A ground item became bug food: register it (world cell centre).
                    if (!string.IsNullOrEmpty(evt.food_id) && evt.level > 0)
                        _food[evt.food_id] = (FixedPoint2.FromVector2(
                            new Vector2(evt.cell_x + 0.5f, evt.cell_y + 0.5f)), evt.level);
                    break;

                case EventFoodConsumed:
                    // Level semantics: set FoodID -> level (deposits raise it, feeding lowers
                    // it); 0 removes the source from the registry.
                    if (!string.IsNullOrEmpty(evt.food_id))
                    {
                        if (evt.level <= 0)
                            _food.Remove(evt.food_id);
                        else
                            _food[evt.food_id] = (FixedPoint2.FromVector2(
                                new Vector2(evt.cell_x + 0.5f, evt.cell_y + 0.5f)), evt.level);
                    }
                    break;

                case EventOccupantBlocksBugs:
                    // Phase 1b: a blocks_bugs occupant (fence/wall) was placed (level=1) or removed (0) at a
                    // cell. Update the ZONE-WIDE bug-collision set so every client (incl. far ones the
                    // chunk-scoped WorldUpdate never reaches) toggles this cell at the SAME tick → the bug sim
                    // collides identically. Idempotent (HashSet add/remove).
                    BugFarmer.World.TilemapManager.Instance?.SetBlocksBugs(
                        new Vector2Int(evt.cell_x, evt.cell_y), evt.level > 0);
                    break;

                case EventTreeFruitGrow:
                case EventTreeFruitDrop:
                    // Server-only ledger events (replay/determinism). The client renders fruit on
                    // trees via the separate OpCode 93 (TilemapManager.HandleTreeFruitUpdate), so
                    // there's nothing to do here — just don't warn as "unknown".
                    break;

                default:
                    Debug.LogWarning($"[InfluenceManager] Unknown event type: {evt.type}");
                    break;
            }
        }

        /// <summary>
        /// Get all player cells for bug AI.
        /// Returns cell coordinates only - deterministic for all clients.
        /// </summary>
        public IEnumerable<(string playerId, int cellX, int cellY)> GetPlayerCells()
        {
            foreach (var kvp in _playerCells)
            {
                yield return (kvp.Key, kvp.Value.cellX, kvp.Value.cellY);
            }
        }

        /// <summary>
        /// Get player count for debugging/validation.
        /// </summary>
        public int PlayerCellCount => _playerCells.Count;

        /// <summary>
        /// Phase 2: the predator swarms currently hunting (predator swarm_id → strike params), for the
        /// authority's per-tick strike pass. Caller iterates in a deterministic order (sort by key).
        /// </summary>
        public IEnumerable<KeyValuePair<string, SwarmStrike>> GetHuntingSwarms() => _swarmStrikes;

        /// <summary>
        /// Compute a swarm's center deterministically for a given tick via closed-form march
        /// along its current leg. Stateless: same (swarmId, tick) always yields the same center
        /// on every client, in both live and replay. Returns false if no leg has been seen yet
        /// (caller should fall back to the swarm's initial/metadata center).
        ///
        /// Mirrors swarm.go Move: marches origin -> target at Speed/tick, clamped at target.
        /// </summary>
        public bool TryComputeSwarmCenter(string swarmId, long tick, out FixedPoint2 center)
        {
            center = FixedPoint2.Zero;
            if (!_swarmLegs.TryGetValue(swarmId, out var leg))
                return false;

            long elapsed = tick - leg.StartTick;
            if (elapsed < 0) elapsed = 0;

            var delta = leg.Target - leg.Origin;
            var dist = FixedPointMath.Sqrt(delta.SqrMagnitude());
            if (dist.Value <= 0)
            {
                center = leg.Target;
                return true;
            }

            // traveled = speed * elapsed (long to avoid overflow on long legs); clamp at target.
            long traveledVal = (long)leg.Speed.Value * elapsed;
            if (traveledVal >= dist.Value)
            {
                center = leg.Target;
                return true;
            }

            var dir = FixedPointMath.Normalize(delta);
            center = leg.Origin + dir * new FixedPoint { Value = (int)traveledVal };
            return true;
        }

        /// <summary>
        /// Directly set a swarm's movement leg during snapshot hydration.
        /// This is for initial state, NOT for event processing.
        /// </summary>
        public void SetSwarmLeg(string swarmId, FixedPoint2 origin, FixedPoint2 target, FixedPoint speed, long startTick)
        {
            _swarmLegs[swarmId] = new SwarmLeg { Origin = origin, Target = target, Speed = speed, StartTick = startTick };
        }

        /// <summary>
        /// Read a swarm's current movement leg (fixed-point Values) so the authority can embed it in its
        /// ZoneSnapshot. This is the AUTHORITATIVE source for late-join leg hydration — the InfluenceLog is
        /// pruned each tick, so a slow swarm's last SWARM_SET_TARGET may be gone; the live leg never is.
        /// Returns false if the swarm has not yet received a leg (caller leaves has_target=false).
        /// </summary>
        public bool TryGetSwarmLeg(string swarmId, out int originX, out int originY,
                                   out int targetX, out int targetY, out int speed, out long startTick)
        {
            if (_swarmLegs.TryGetValue(swarmId, out var leg))
            {
                originX = leg.Origin.X.Value; originY = leg.Origin.Y.Value;
                targetX = leg.Target.X.Value; targetY = leg.Target.Y.Value;
                speed = leg.Speed.Value; startTick = leg.StartTick;
                return true;
            }
            originX = originY = targetX = targetY = speed = 0; startTick = 0;
            return false;
        }

        /// <summary>
        /// Clear all swarm legs. Called during late join initialization (mirrors ClearPlayerCells).
        /// </summary>
        public void ClearSwarmLegs()
        {
            _swarmLegs.Clear();
        }

        /// <summary>
        /// Clear all player cells.
        /// Called when leaving match or during late join initialization.
        /// </summary>
        public void ClearPlayerCells()
        {
            _playerCells.Clear();
        }

        /// <summary>
        /// Directly set a player's cell position during snapshot hydration.
        /// This is for initial state, NOT for event processing.
        /// IMPORTANT: Only call during late join snapshot application.
        /// </summary>
        public void SetPlayerCell(string playerId, int cellX, int cellY)
        {
            _playerCells[playerId] = (cellX, cellY);
        }

        /// <summary>
        /// Remove a specific player's cell.
        /// Called when player leaves.
        /// </summary>
        public void RemovePlayerCell(string playerId)
        {
            _playerCells.Remove(playerId);
        }
    }
}
