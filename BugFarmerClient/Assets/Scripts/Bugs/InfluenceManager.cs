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

        // Event type constants (must match server)
        public const string EventPlayerCellEnter = "PLAYER_CELL_ENTER";
        public const string EventPlayerCellLeave = "PLAYER_CELL_LEAVE";
        public const string EventSwarmSetTarget = "SWARM_SET_TARGET";
        public const string EventBugRemoved = "BUG_REMOVED";
        public const string EventBugSpawned = "BUG_SPAWNED";
        public const string EventSwarmSplit = "SWARM_SPLIT";
        public const string EventSwarmMerge = "SWARM_MERGE";
        public const string EventSwarmReproduced = "SWARM_REPRODUCED";
        public const string EventItemRotted = "ITEM_ROTTED";
        public const string EventFoodConsumed = "FOOD_CONSUMED";

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

        /// <summary>Clear the registry (late-join resync re-bootstraps it).</summary>
        public void ClearFood() => _food.Clear();

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
