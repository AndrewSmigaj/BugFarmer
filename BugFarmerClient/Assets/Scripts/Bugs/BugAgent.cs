using System.Collections.Generic;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Player position data for deterministic targeting.
    /// </summary>
    public struct PlayerTarget
    {
        public string PlayerId;
        public FixedPoint2 Position;
    }

    /// <summary>
    /// Per-bug agent with deterministic simulation.
    /// Each bug has its own RNG, position, velocity, and movement behavior.
    /// Velocity is in units per tick (fixed timestep).
    ///
    /// RNG RULES:
    /// - Spawn-time initialization uses stateful Rng (runs once, no branching issues)
    /// - Simulation logic uses counter-based RNG via RandomInt/RandomFloat helpers
    /// - Counter-based RNG prevents desync from conditional RNG consumption
    /// </summary>
    public class BugAgent
    {
        public int BugId;
        public string SwarmId;
        public string SpeciesId;

        // Spawn-time RNG (stateful, OK because runs once per bug)
        public DeterministicRandom Rng;

        // Counter-based RNG context (set each tick)
        private long _worldSeed;
        private long _currentTick;

        public FixedPoint2 Position;
        public FixedPoint2 Velocity;
        public IBugMovement Movement;

        // Behavior state
        public string CurrentBehavior; // "wander", "flee", "attack", "curious"
        public string TargetPlayerId;

        // Alert state (stochastic reaction)
        private bool _isAlerted;
        private int _alertCheckCooldown;

        // Public accessors for sync
        public bool IsAlerted { get => _isAlerted; set => _isAlerted = value; }
        public int AlertCheckCooldown { get => _alertCheckCooldown; set => _alertCheckCooldown = value; }

        // Cached species behavior
        private SpeciesBehavior _behavior;
        private FixedPoint _reactionRadiusSqr;
        private FixedPoint _wanderRadiusSqr;

        // Alert chance per check (30%)
        private const float AlertChance = 0.3f;

        public BugAgent(long worldSeed, string swarmId, string speciesId, int bugId, FixedPoint2 startPosition)
        {
            BugId = bugId;
            SwarmId = swarmId;
            SpeciesId = speciesId;

            // Store world seed for counter-based RNG during simulation
            _worldSeed = worldSeed;
            _currentTick = 0;

            // Stateful RNG for spawn-time initialization only
            Rng = DeterministicRandom.ForBug(worldSeed, swarmId, bugId);
            Position = startPosition;
            Velocity = FixedPoint2.Zero;
            Movement = MovementFactory.CreateMovement(speciesId);

            CurrentBehavior = "wander";
            TargetPlayerId = null;

            _isAlerted = false;
            _alertCheckCooldown = Rng.RangeInt(1, 10); // Stagger initial checks (spawn-time, stateful OK)

            _behavior = MovementFactory.GetBehavior(speciesId);
            _reactionRadiusSqr = FixedPoint.FromFloat(_behavior.ReactionRadius * _behavior.ReactionRadius);
            _wanderRadiusSqr = FixedPoint.FromFloat(_behavior.WanderRadius * _behavior.WanderRadius);
        }

        /// <summary>
        /// Counter-based random int for simulation logic.
        /// Same inputs always produce same output - prevents desync from conditional branches.
        /// </summary>
        public int RandomInt(int purposeId, int min, int max)
        {
            return CounterRng.RangeInt(_worldSeed, SwarmId, BugId, _currentTick, purposeId, min, max);
        }

        /// <summary>
        /// Counter-based random float [0,1) for simulation logic.
        /// Same inputs always produce same output - prevents desync from conditional branches.
        /// </summary>
        public float RandomFloat(int purposeId)
        {
            return CounterRng.Float(_worldSeed, SwarmId, BugId, _currentTick, purposeId);
        }

        /// <summary>
        /// Simulate one tick of bug behavior and movement.
        /// </summary>
        /// <param name="swarmCenter">Current swarm center position</param>
        /// <param name="players">Player positions (from InfluenceManager)</param>
        /// <param name="currentTick">Current simulation tick for counter-based RNG</param>
        public void SimulateTick(FixedPoint2 swarmCenter, List<PlayerTarget> players, long currentTick)
        {
            // Store tick for counter-based RNG calls
            _currentTick = currentTick;

            // 1. Update behavior based on nearby players (stochastic alert)
            UpdateBehavior(players);

            // 2. Apply movement based on current behavior
            switch (CurrentBehavior)
            {
                case "attack":
                    if (TargetPlayerId != null)
                    {
                        var targetPos = GetPlayerPosition(players, TargetPlayerId);
                        if (targetPos.HasValue)
                            Movement.MoveToward(this, targetPos.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                case "flee":
                    if (TargetPlayerId != null)
                    {
                        var fleeFrom = GetPlayerPosition(players, TargetPlayerId);
                        if (fleeFrom.HasValue)
                            Movement.MoveAwayFrom(this, fleeFrom.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                case "curious":
                    if (TargetPlayerId != null)
                    {
                        var curiousPos = GetPlayerPosition(players, TargetPlayerId);
                        if (curiousPos.HasValue)
                            Movement.MoveTowardSlow(this, curiousPos.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                default: // "wander" or "ignore"
                    Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    break;
            }

            // 3. Apply velocity to position (velocity = units per tick)
            Position = new FixedPoint2(
                Position.X + Velocity.X,
                Position.Y + Velocity.Y
            );

            // 4. Collision resolved by BugAgentManager after this
        }

        /// <summary>
        /// Update behavior with stochastic alert system.
        /// Bugs don't all react instantly - they notice players over time.
        /// </summary>
        private void UpdateBehavior(List<PlayerTarget> players)
        {
            if (_behavior.PlayerReaction == "ignore" || _behavior.ReactionRadius <= 0)
            {
                CurrentBehavior = "wander";
                TargetPlayerId = null;
                return;
            }

            _alertCheckCooldown--;

            // If alerted and not time to re-check, keep current behavior
            if (_alertCheckCooldown > 0 && _isAlerted && TargetPlayerId != null)
            {
                // Verify target still in range
                var targetPos = GetPlayerPosition(players, TargetPlayerId);
                if (targetPos.HasValue)
                {
                    var distSqr = Position.SqrDistanceTo(targetPos.Value);
                    if (distSqr <= _reactionRadiusSqr)
                        return; // Still tracking target
                }
                // Target left range - become un-alerted
                _isAlerted = false;
                TargetPlayerId = null;
                CurrentBehavior = "wander";
                return;
            }

            // Time to check for players
            if (_alertCheckCooldown <= 0)
            {
                // Counter-based RNG for cooldown - always evaluates regardless of branch
                _alertCheckCooldown = RandomInt(RngPurpose.Cooldown, 5, 15);

                // Find nearest player in range
                string nearestId = null;
                FixedPoint nearestDistSqr = _reactionRadiusSqr;

                foreach (var player in players)
                {
                    var distSqr = Position.SqrDistanceTo(player.Position);
                    if (distSqr < nearestDistSqr)
                    {
                        nearestDistSqr = distSqr;
                        nearestId = player.PlayerId;
                    }
                    else if (distSqr == nearestDistSqr && nearestId != null)
                    {
                        // Tie-breaker: lexicographically smaller ID
                        if (string.CompareOrdinal(player.PlayerId, nearestId) < 0)
                            nearestId = player.PlayerId;
                    }
                }

                // Counter-based RNG for alert - ALWAYS compute, use conditionally
                // This prevents desync: same hash regardless of whether we're in "if (!_isAlerted)" branch
                float alertRoll = RandomFloat(RngPurpose.Alert);

                if (nearestId != null)
                {
                    // Player in range - roll chance to notice
                    if (!_isAlerted)
                    {
                        if (alertRoll < AlertChance)
                        {
                            _isAlerted = true;
                            TargetPlayerId = nearestId;
                            CurrentBehavior = _behavior.PlayerReaction;
                        }
                        // else: didn't notice yet, keep wandering
                    }
                    else
                    {
                        // Already alerted - update target to nearest
                        TargetPlayerId = nearestId;
                        CurrentBehavior = _behavior.PlayerReaction;
                    }
                }
                else
                {
                    // No player in range - become un-alerted
                    _isAlerted = false;
                    TargetPlayerId = null;
                    CurrentBehavior = "wander";
                }
            }
        }

        private static FixedPoint2? GetPlayerPosition(List<PlayerTarget> players, string playerId)
        {
            foreach (var player in players)
            {
                if (player.PlayerId == playerId)
                    return player.Position;
            }
            return null;
        }

        /// <summary>
        /// Get world position as Vector2 for rendering.
        /// </summary>
        public UnityEngine.Vector2 WorldPosition => Position.ToVector2();
    }
}
