namespace BugFarmer.Bugs
{
    /// <summary>
    /// Smooth, graceful movement for butterflies and similar insects.
    /// Bugs pick a distant intent point and glide toward it in arcs.
    /// Low changeRate means long sweeping paths; turnRate controls arc smoothness.
    /// </summary>
    public class GlidingMovement : IBugMovement
    {
        private readonly FixedPoint _speed;
        private readonly FixedPoint _intentRange;
        private readonly int _changeIntervalBase;
        private readonly FixedPoint _turnRate;

        // Per-bug state
        private FixedPoint2 _intentTarget;
        private FixedPoint2 _currentDirection;
        private int _ticksUntilChange;

        // Constants
        private static readonly FixedPoint PullStrength = FixedPoint.FromFloat(0.2f);
        private static readonly FixedPoint SlowFactor = FixedPoint.FromFloat(0.4f);
        private static readonly FixedPoint FleeMultiplier = FixedPoint.FromFloat(1.3f);

        public GlidingMovement(float speed, float intentRange, float changeRate, float turnRate)
        {
            _speed = FixedPoint.FromFloat(speed);
            _intentRange = FixedPoint.FromFloat(intentRange);
            _changeIntervalBase = changeRate > 0 ? (int)(10 / changeRate) : 100;
            if (_changeIntervalBase < 10) _changeIntervalBase = 10;
            _turnRate = FixedPoint.FromFloat(turnRate);

            _intentTarget = FixedPoint2.Zero;
            _currentDirection = FixedPointMath.DirectionFromIndex(0);
            _ticksUntilChange = 0;
        }

        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            _ticksUntilChange--;
            if (_ticksUntilChange <= 0)
            {
                PickNewIntent(bug, swarmCenter);
            }

            // Gradually turn toward intent target
            var toIntent = _intentTarget - bug.Position;
            var desiredDir = FixedPointMath.Normalize(toIntent);

            _currentDirection = BlendDirections(_currentDirection, desiredDir, _turnRate);

            var velocity = new FixedPoint2(_currentDirection.X * _speed, _currentDirection.Y * _speed);

            // Gentle pull toward swarm center if too far
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
            var desiredDir = FixedPointMath.Normalize(toTarget);

            _currentDirection = BlendDirections(_currentDirection, desiredDir, _turnRate);

            bug.Velocity = new FixedPoint2(_currentDirection.X * _speed, _currentDirection.Y * _speed);
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
            var desiredDir = FixedPointMath.Normalize(awayFrom);

            _currentDirection = BlendDirections(_currentDirection, desiredDir, _turnRate);

            var fleeSpeed = _speed * FleeMultiplier;
            bug.Velocity = new FixedPoint2(_currentDirection.X * fleeSpeed, _currentDirection.Y * fleeSpeed);
        }

        private void PickNewIntent(BugAgent bug, FixedPoint2 swarmCenter)
        {
            // Counter-based RNG via bug helper
            int dirIndex = bug.RandomInt(RngPurpose.Direction, 0, FixedPointMath.TableSize);
            var dir = FixedPointMath.DirectionFromIndex(dirIndex);

            int distValue = bug.RandomInt(RngPurpose.SpawnDistance, _intentRange.Value / 2, _intentRange.Value + 1);
            var dist = new FixedPoint { Value = distValue };

            _intentTarget = new FixedPoint2(
                bug.Position.X + dir.X * dist,
                bug.Position.Y + dir.Y * dist
            );

            _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, _changeIntervalBase / 2, _changeIntervalBase + 1);
        }

        private static FixedPoint2 BlendDirections(FixedPoint2 current, FixedPoint2 target, FixedPoint rate)
        {
            var oneMinusRate = FixedPoint.One - rate;

            var blended = new FixedPoint2(
                current.X * oneMinusRate + target.X * rate,
                current.Y * oneMinusRate + target.Y * rate
            );

            var result = FixedPointMath.Normalize(blended);

            // Fallback if blend produced zero (opposite directions edge case)
            if (result.X.Value == 0 && result.Y.Value == 0)
                return current;

            return result;
        }

        public MovementState GetState()
        {
            return new MovementState
            {
                TicksUntilChange = _ticksUntilChange,
                // IntentDir unused by Gliding
                IntentTargetX = _intentTarget.X.Value,
                IntentTargetY = _intentTarget.Y.Value,
                CurrentDirX = _currentDirection.X.Value,
                CurrentDirY = _currentDirection.Y.Value
            };
        }

        public void SetState(MovementState state)
        {
            _ticksUntilChange = state.TicksUntilChange;
            _intentTarget = new FixedPoint2
            {
                X = new FixedPoint { Value = state.IntentTargetX },
                Y = new FixedPoint { Value = state.IntentTargetY }
            };
            _currentDirection = new FixedPoint2
            {
                X = new FixedPoint { Value = state.CurrentDirX },
                Y = new FixedPoint { Value = state.CurrentDirY }
            };
        }
    }
}
