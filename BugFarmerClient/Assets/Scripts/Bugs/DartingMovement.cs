namespace BugFarmer.Bugs
{
    /// <summary>
    /// Hover-and-dash movement for wasps: short stationary HOVERS punctuated by quick
    /// DASHES in a new direction — the predatory, twitchy read. Deterministic fixed-point
    /// + counter-based RNG only (the BrownianMovement conventions); per-bug state
    /// round-trips GetState/SetState through the existing MovementState ints
    /// (TicksUntilChange = phase timer; IntentDir = dash direction; CurrentDirX = phase
    /// flag 0/1) so late joiners reconverge bit-exactly (the §14 contract).
    /// Per-bug speed ≥ 0.33 blocks/tick so visuals never trail the ×1.5 hunt legs.
    /// </summary>
    public class DartingMovement : IBugMovement
    {
        private readonly FixedPoint _dashSpeed;
        private readonly FixedPoint _hoverSpeed;

        // Per-bug state
        private FixedPoint2 _dashDirection;
        private int _ticksUntilChange; // counts down the current phase
        private int _dashing;         // 0 = hover, 1 = dash

        private static readonly FixedPoint PullStrength = FixedPoint.FromFloat(0.5f);

        public DartingMovement(float dashSpeed, float hoverSpeed)
        {
            _dashSpeed = FixedPoint.FromFloat(dashSpeed);
            _hoverSpeed = FixedPoint.FromFloat(hoverSpeed);
            _dashDirection = FixedPoint2.Zero;
            _ticksUntilChange = 0;
            _dashing = 0;
        }

        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            _ticksUntilChange--;
            if (_ticksUntilChange <= 0)
            {
                // Flip phase: hover (4-9 ticks, drifting) <-> dash (3-5 ticks, fast)
                if (_dashing == 1)
                {
                    _dashing = 0;
                    _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, 4, 10);
                }
                else
                {
                    _dashing = 1;
                    int dirIndex = bug.RandomInt(RngPurpose.Direction, 0, FixedPointMath.TableSize);
                    _dashDirection = FixedPointMath.DirectionFromIndex(dirIndex);
                    _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, 3, 6);
                }
            }

            var speed = _dashing == 1 ? _dashSpeed : _hoverSpeed;
            var velocity = new FixedPoint2(_dashDirection.X * speed, _dashDirection.Y * speed);

            // Tight-formation pull (wasps fly in strike formation)
            var toCenter = swarmCenter - bug.Position;
            if (toCenter.SqrMagnitude() > wanderRadiusSqr)
            {
                var norm = FixedPointMath.Normalize(toCenter);
                velocity.X = velocity.X + norm.X * _dashSpeed * PullStrength;
                velocity.Y = velocity.Y + norm.Y * _dashSpeed * PullStrength;
            }

            bug.Velocity = velocity;
        }

        public void MoveToward(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(target - bug.Position);
            bug.Velocity = new FixedPoint2(dir.X * _dashSpeed, dir.Y * _dashSpeed);
        }

        public void MoveTowardSlow(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(target - bug.Position);
            bug.Velocity = new FixedPoint2(dir.X * _hoverSpeed, dir.Y * _hoverSpeed);
        }

        public void MoveAwayFrom(BugAgent bug, FixedPoint2 target)
        {
            var dir = FixedPointMath.Normalize(bug.Position - target);
            bug.Velocity = new FixedPoint2(dir.X * _dashSpeed, dir.Y * _dashSpeed);
        }

        public MovementState GetState()
        {
            return new MovementState
            {
                TicksUntilChange = _ticksUntilChange,
                IntentDirX = _dashDirection.X.Value,
                IntentDirY = _dashDirection.Y.Value,
                CurrentDirX = _dashing, // phase flag rides an unused Gliding slot
            };
        }

        public void SetState(MovementState state)
        {
            _ticksUntilChange = state.TicksUntilChange;
            _dashDirection = new FixedPoint2
            {
                X = new FixedPoint { Value = state.IntentDirX },
                Y = new FixedPoint { Value = state.IntentDirY }
            };
            _dashing = state.CurrentDirX;
        }
    }
}
