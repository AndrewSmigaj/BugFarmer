namespace BugFarmer.Bugs
{
    /// <summary>
    /// Per-bug movement for centipede PACK members (movement_style "centipede"). Unlike CrawlingMovement
    /// (the offset-follow model where a whole knot rides one server-clamped center), each member is an
    /// INDEPENDENT agent: it serpentine-wanders around the pack center on its own heading, and MoveToward
    /// REALLY steers toward a target (CrawlingMovement.MoveToward was a no-op — the reason centipedes could
    /// not hunt). Per-bug collision (SkipCollision=false), so members chase individual prey + collide with
    /// walls. Deterministic: counter-RNG only, fixed-point; heading + retarget timer round-trip MovementState
    /// (snapshot-only — movement ints are not hashed). The segmented body lives in the VISUAL layer
    /// (CentipedeTrail), which just follows the head sprite, so it is agnostic to this movement.
    /// </summary>
    public class CentipedeMovement : IBugMovement
    {
        // Blocks/tick. Wander is a slow creep; the chase MUST out-run a fleeing fly (0.2 wander × 1.5 flee =
        // 0.3/tick) or the pack never catches prey — matched to the wasp's DartingMovement dash (0.35).
        private static readonly FixedPoint CrawlSpeed = FixedPoint.FromFloat(0.14f);
        private static readonly FixedPoint ChaseSpeed = FixedPoint.FromFloat(0.35f);
        private static readonly FixedPoint SlowSpeed = FixedPoint.FromFloat(0.11f);
        private static readonly FixedPoint PullStrength = FixedPoint.FromFloat(0.3f);

        // Serpentine: ±~60° per retarget (43/256 of a turn ≈ 60°); retarget every 0.8-1.6s → a squirming crawl.
        private const int TurnMaxSteps = 43;
        private const int RetargetMin = 8;
        private const int RetargetMax = 16;

        private FixedPoint2 _heading;     // unit vector; (0,0) = unseeded (first tick / a never-moved snapshot bug)
        private int _ticksUntilChange;

        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            _ticksUntilChange--;
            if (_ticksUntilChange <= 0)
            {
                if (_heading.X.Value == 0 && _heading.Y.Value == 0)
                {
                    // Seed an ABSOLUTE heading (no prior heading to turn from).
                    int idx = bug.RandomInt(RngPurpose.Direction, 0, FixedPointMath.TableSize);
                    _heading = FixedPointMath.DirectionFromIndex(idx);
                }
                else
                {
                    // Serpentine: turn the current heading by a small ± amount (relative → a squirming path).
                    int turn = bug.RandomInt(RngPurpose.Direction, -TurnMaxSteps, TurnMaxSteps + 1);
                    _heading = RotateDirection(_heading, turn);
                }
                _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, RetargetMin, RetargetMax);
            }

            var velocity = new FixedPoint2(_heading.X * CrawlSpeed, _heading.Y * CrawlSpeed);

            // Stay near the pack center — a member drifting on its own heading would leave the pack.
            var toCenter = swarmCenter - bug.Position;
            if (toCenter.SqrMagnitude() > wanderRadiusSqr)
            {
                var norm = FixedPointMath.Normalize(toCenter);
                velocity.X = velocity.X + norm.X * CrawlSpeed * PullStrength;
                velocity.Y = velocity.Y + norm.Y * CrawlSpeed * PullStrength;
            }

            bug.Velocity = velocity;
        }

        // Real steering toward a target (the hunt/approach) — this is what makes centipedes chase prey.
        public void MoveToward(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(target - bug.Position);
            bug.Velocity = new FixedPoint2(dir.X * ChaseSpeed, dir.Y * ChaseSpeed);
        }

        public void MoveTowardSlow(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(target - bug.Position);
            bug.Velocity = new FixedPoint2(dir.X * SlowSpeed, dir.Y * SlowSpeed);
        }

        public void MoveAwayFrom(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(bug.Position - target);
            bug.Velocity = new FixedPoint2(dir.X * ChaseSpeed, dir.Y * ChaseSpeed);
        }

        // Rotate a unit vector by offsetSteps table-indices (deterministic; same shape as BrownianMovement's
        // private helper, duplicated here rather than exposing it).
        private static FixedPoint2 RotateDirection(FixedPoint2 dir, int offsetSteps)
        {
            if (offsetSteps == 0) return dir;
            int angleValue = offsetSteps * FixedPointMath.TwoPiScaled / FixedPointMath.TableSize;
            var angle = new FixedPoint { Value = angleValue };
            var cos = FixedPointMath.Cos(angle);
            var sin = FixedPointMath.Sin(angle);
            return new FixedPoint2(
                dir.X * cos - dir.Y * sin,
                dir.X * sin + dir.Y * cos
            );
        }

        public MovementState GetState() => new MovementState
        {
            TicksUntilChange = _ticksUntilChange,
            IntentDirX = _heading.X.Value,
            IntentDirY = _heading.Y.Value,
        };

        public void SetState(MovementState state)
        {
            _ticksUntilChange = state.TicksUntilChange;
            _heading = new FixedPoint2(
                new FixedPoint { Value = state.IntentDirX },
                new FixedPoint { Value = state.IntentDirY });
        }
    }
}
