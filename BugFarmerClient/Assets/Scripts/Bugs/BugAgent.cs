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

        // Alert chance per check (3/10 = 30%). Integer ratio to keep the roll float-free.
        private const int AlertChanceNumerator = 3;
        private const int AlertChanceDenominator = 10;

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

        // === Feed-at-food visual (deterministic) ===
        private int _landTicks; // >0 = landed (paused) on a food source

        private const float FeedVisualRadius = 2.5f; // centre within this of food => bugs engage
        private static readonly int LandDistSqr =
            (FixedPoint.FromFloat(0.35f) * FixedPoint.FromFloat(0.35f)).Value;

        // Per-bug feeding participation re-rolls every 8s window, so bugs drift in and out of
        // feeding INDIVIDUALLY — the swarm never flips between modes as one block.
        private const long ParticipationWindowTicks = 80;
        private static readonly FixedPoint ApproachRadiusSqr =
            FixedPoint.FromFloat(0.4f * 0.4f);
        // Non-landing bugs HOVER in a tight halo around the food (instead of the ±8-cell
        // swarm wander) — this is what makes "buzzing around the fruit/bin" visible.
        private static readonly FixedPoint HoverRadiusSqr =
            FixedPoint.FromFloat(1.2f * 1.2f);

        /// <summary>
        /// If the swarm centre is at a food source (deterministic event-driven registry),
        /// SOME bugs (per-bug per-window roll) approach it with their normal buzzy Brownian
        /// motion pulled toward a personal landing point, land for a few ticks, and resume;
        /// the rest keep wandering. Returns true when feeding owns this tick's movement.
        /// </summary>
        private bool TryFeedAtFood(FixedPoint2 swarmCenter)
        {
            var im = InfluenceManager.Instance;
            if (im == null) return false;

            if (!im.TryGetNearestFood(swarmCenter, FeedVisualRadius, out var foodPos))
            {
                _landTicks = 0;
                return false;
            }

            // INDIVIDUAL participation: each bug rolls per 8s window (counter-RNG on the
            // window index — deterministic on every client). ~60% LAND in any window; the
            // others don't land but HOVER in a tight halo around the food — the whole swarm
            // visibly condenses onto the fruit/bin ("buzzing"), staggered and alive.
            long window = _currentTick / ParticipationWindowTicks;
            bool joining = CounterRng.Chance(_worldSeed, SwarmId, BugId, window, RngPurpose.Participate, 3, 5);
            if (!joining)
            {
                _landTicks = 0;
                Movement.UpdateMovement(this, foodPos, HoverRadiusSqr);
                return true;
            }

            if (_landTicks > 0)
            {
                _landTicks--;
                Velocity = default; // landed: hold position
                return true;
            }

            // Per-bug landing point: a stable ring offset derived from BugId (no RNG burn) —
            // bugs encircle the fruit/bin instead of stacking on one pixel.
            var dir = FixedPointMath.DirectionFromIndex((BugId * 37) & (FixedPointMath.TableSize - 1));
            var ring = FixedPoint.FromFloat(0.3f);
            var target = new FixedPoint2(foodPos.X + dir.X * ring, foodPos.Y + dir.Y * ring);

            if (Position.SqrDistanceTo(target).Value <= LandDistSqr)
            {
                _landTicks = RandomInt(RngPurpose.Land, 10, 31); // land 1-3 seconds
                Velocity = default;
            }
            else
            {
                // BUZZY approach: the bug's normal Brownian movement with its "home" set to
                // the landing point and a tiny radius — identical visual character to regular
                // wandering (random jinks + gentle pull), just drifting onto the fruit,
                // instead of a robotic straight-line glide.
                Movement.UpdateMovement(this, target, ApproachRadiusSqr);
            }
            return true;
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
                    // FEEDING VISUAL: when the swarm centre is at a registered food source,
                    // bugs approach it, LAND (pause), then resume — driven purely by
                    // deterministic inputs (event-driven food registry + derived centre +
                    // counter-RNG + a per-bug-id ring offset), so all clients stay identical.
                    // Crawling individuals skip the fly hover-land feed dance — the
                    // centipede head must ride the center verbatim (it still EATS via
                    // the server meters; this is display only).
                    if (_behavior.SkipCollision || !TryFeedAtFood(swarmCenter))
                        Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    break;
            }

            // 3. Apply velocity, resolving collision against blocks_bugs cells so individual bugs can't
            //    pass through walls/fences. Deterministic: integer cell lookups + slide X-then-Y.
            //    All clients run this identically, so the per-tick state-hash stays in agreement.
            //    SPECIES-AWARE (§14, both collision sites): flies_over_fences skips the
            //    occupant branch only (water still blocks); crawling individuals skip
            //    Resolve entirely (the head rides the server-clamped center verbatim).
            var proposed = new FixedPoint2(
                Position.X + Velocity.X,
                Position.Y + Velocity.Y
            );
            Position = _behavior.SkipCollision
                ? proposed
                : BugCollision.Resolve(Position, proposed, _behavior.FliesOverFences);
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

                // Integer counter-based roll for alert - ALWAYS compute, use conditionally.
                // This prevents desync: same hash regardless of whether we're in the "if (!_isAlerted)"
                // branch, and the integer comparison is bit-identical across platforms.
                bool alertNotice = CounterRng.Chance(_worldSeed, SwarmId, BugId, _currentTick,
                    RngPurpose.Alert, AlertChanceNumerator, AlertChanceDenominator);

                if (nearestId != null)
                {
                    // Player in range - roll chance to notice
                    if (!_isAlerted)
                    {
                        if (alertNotice)
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
