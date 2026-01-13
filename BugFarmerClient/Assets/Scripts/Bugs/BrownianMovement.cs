namespace BugFarmer.Bugs
{
    /// <summary>
    /// Erratic, buzzing movement for flies and similar insects.
    /// Bugs pick a short intent direction and change frequently.
    /// All math is deterministic fixed-point.
    /// </summary>
    public class BrownianMovement : IBugMovement
    {
        private readonly FixedPoint _speed;
        private readonly int _changeIntervalBase;

        // Per-bug state (each bug gets own instance)
        private FixedPoint2 _intentDirection;
        private int _ticksUntilChange;

        // Constants
        private static readonly FixedPoint PullStrength = FixedPoint.FromFloat(0.3f);
        private static readonly FixedPoint SlowFactor = FixedPoint.FromFloat(0.3f);
        private static readonly FixedPoint FleeMultiplier = FixedPoint.FromFloat(1.5f);

        public BrownianMovement(float speed, float changeRate)
        {
            _speed = FixedPoint.FromFloat(speed);
            _changeIntervalBase = changeRate > 0 ? (int)(10 / changeRate) : 10;
            if (_changeIntervalBase < 3) _changeIntervalBase = 3;

            _intentDirection = FixedPoint2.Zero;
            _ticksUntilChange = 0;
        }

        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            _ticksUntilChange--;
            if (_ticksUntilChange <= 0)
            {
                PickNewIntent(bug);
            }

            var velocity = new FixedPoint2(_intentDirection.X * _speed, _intentDirection.Y * _speed);

            // Pull back toward swarm center if too far
            var toCenter = swarmCenter - bug.Position;
            var distSqr = toCenter.SqrMagnitude();

            if (distSqr > wanderRadiusSqr)
            {
                var norm = FixedPointMath.Normalize(toCenter);
                velocity.X = velocity.X + norm.X * _speed * PullStrength;
                velocity.Y = velocity.Y + norm.Y * _speed * PullStrength;
            }

            bug.Velocity = velocity;
        }

        public void MoveToward(BugAgent bug, FixedPoint2 target)
        {
            var toTarget = target - bug.Position;
            var dir = FixedPointMath.Normalize(toTarget);

            // Random offset for zig-zag pursuit (+/- 45 degrees)
            // Counter-based RNG via bug helper
            int offsetSteps = bug.RandomInt(RngPurpose.TargetOffset, -32, 33);
            var rotated = RotateDirection(dir, offsetSteps);

            bug.Velocity = new FixedPoint2(rotated.X * _speed, rotated.Y * _speed);
        }

        public void MoveTowardSlow(BugAgent bug, FixedPoint2 target)
        {
            MoveToward(bug, target);
            bug.Velocity = new FixedPoint2(
                bug.Velocity.X * SlowFactor,
                bug.Velocity.Y * SlowFactor
            );
        }

        public void MoveAwayFrom(BugAgent bug, FixedPoint2 target)
        {
            var awayFrom = bug.Position - target;
            var dir = FixedPointMath.Normalize(awayFrom);

            // Wider offset for unpredictable scatter (+/- 63 degrees)
            // Counter-based RNG via bug helper
            int offsetSteps = bug.RandomInt(RngPurpose.TargetOffset, -45, 46);
            var rotated = RotateDirection(dir, offsetSteps);

            var fleeSpeed = _speed * FleeMultiplier;
            bug.Velocity = new FixedPoint2(rotated.X * fleeSpeed, rotated.Y * fleeSpeed);
        }

        private void PickNewIntent(BugAgent bug)
        {
            // Counter-based RNG via bug helper
            int dirIndex = bug.RandomInt(RngPurpose.Direction, 0, FixedPointMath.TableSize);
            _intentDirection = FixedPointMath.DirectionFromIndex(dirIndex);
            _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, _changeIntervalBase / 2, _changeIntervalBase + 1);
        }

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

        public MovementState GetState()
        {
            return new MovementState
            {
                TicksUntilChange = _ticksUntilChange,
                IntentDirX = _intentDirection.X.Value,
                IntentDirY = _intentDirection.Y.Value,
                // IntentTarget and CurrentDir unused by Brownian
            };
        }

        public void SetState(MovementState state)
        {
            _ticksUntilChange = state.TicksUntilChange;
            _intentDirection = new FixedPoint2
            {
                X = new FixedPoint { Value = state.IntentDirX },
                Y = new FixedPoint { Value = state.IntentDirY }
            };
        }
    }
}
