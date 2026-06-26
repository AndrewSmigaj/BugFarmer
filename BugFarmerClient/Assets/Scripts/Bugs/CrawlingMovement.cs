namespace BugFarmer.Bugs
{
    /// <summary>
    /// Movement for INDIVIDUAL ground bugs (centipede knots, 1-3 per swarm): each bug's
    /// position is the swarm center PLUS a slowly-wandering per-bug OFFSET. The offset
    /// model (not velocity-chase) means every member tracks the center EXACTLY through
    /// 7.7 u/s surges — the whole knot lunges together with zero lag — while the offsets
    /// crawl around between re-targets so a parked knot reads as restless centipedes,
    /// not stacked sprites. No per-bug collision (legality is the server leg clamp's
    /// job; skipping BugCollision.Resolve also sidesteps the raycast's diagonal-corner
    /// permeability). Deterministic: CounterRng only; offset + target + timer round-trip
    /// MovementState (IntentDir = current offset, IntentTarget = offset target) —
    /// Position is hash state. The segment trail lives in the VISUAL layer
    /// (CentipedeTrail), never here. Reaction display is off for individuals (BugAgent
    /// gates on behavior "ignore" via the species row).
    /// </summary>
    public class CrawlingMovement : IBugMovement
    {
        // Members patrol a WIDE territory around the shared center and re-target often, so a parked
        // knot reads as separate centipedes wandering their own patch — not a huddle. (Raised from
        // 2.4 / sped up retarget after playtest: "they all move the same, attack at once, bunched".)
        private static readonly FixedPoint KnotRadius = FixedPoint.FromFloat(4.0f);
        private static readonly FixedPoint OffsetStep = FixedPoint.FromFloat(0.05f);
        private const int RetargetMinTicks = 20;  // 2-5s between repositions (livelier)
        private const int RetargetMaxTicks = 51;

        private FixedPoint2 _offset;
        private FixedPoint2 _offsetTarget;
        private int _ticksUntilChange;

        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            _ticksUntilChange--;
            if (_ticksUntilChange <= 0)
                PickNewOffsetTarget(bug);

            // Creep the offset toward its target (capped step = crawl speed).
            var toTarget = _offsetTarget - _offset;
            var distSqr = toTarget.SqrMagnitude();
            if (distSqr.Value > 0)
            {
                if (distSqr <= OffsetStep * OffsetStep)
                {
                    _offset = _offsetTarget;
                }
                else
                {
                    var dir = FixedPointMath.Normalize(toTarget);
                    _offset = new FixedPoint2(
                        _offset.X + dir.X * OffsetStep,
                        _offset.Y + dir.Y * OffsetStep
                    );
                }
            }

            // Follow (center + offset) by a PER-BUG fraction of the remaining gap each tick — slower
            // members trail when the center surges, faster ones lead, so the knot STRINGS OUT during a
            // lunge and regroups when parked, and members reach prey (and strike) at different times
            // instead of all at once. Exponential follow always converges, so a member never drifts
            // away. Deterministic: fraction is fixed per member (BugId), FixedPoint math, no per-tick RNG.
            int fpct = 30 + (bug.BugId * 37) % 31;          // 30..60% — constant per member
            var frac = FixedPoint.FromFloat(fpct / 100f);
            var gapX = swarmCenter.X + _offset.X - bug.Position.X;
            var gapY = swarmCenter.Y + _offset.Y - bug.Position.Y;
            bug.Velocity = new FixedPoint2(gapX * frac, gapY * frac);
        }

        private void PickNewOffsetTarget(BugAgent bug)
        {
            int dirIndex = bug.RandomInt(RngPurpose.Direction, 0, FixedPointMath.TableSize);
            var dir = FixedPointMath.DirectionFromIndex(dirIndex);
            // Radius fraction in [45%, 100%] of KnotRadius so members spread, not pile
            // (the floor keeps them off the center, where they'd stack).
            int pct = bug.RandomInt(RngPurpose.TargetOffset, 45, 101);
            var r = KnotRadius * FixedPoint.FromFloat(pct / 100f);
            _offsetTarget = new FixedPoint2(dir.X * r, dir.Y * r);
            _ticksUntilChange = bug.RandomInt(RngPurpose.MovementChange, RetargetMinTicks, RetargetMaxTicks);
        }

        // Individuals never run the reaction-display branches (species reaction is
        // "ignore"); these exist to satisfy the interface and behave sanely if reached.
        public void MoveToward(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public void MoveTowardSlow(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public void MoveAwayFrom(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public MovementState GetState() => new MovementState
        {
            TicksUntilChange = _ticksUntilChange,
            IntentDirX = _offset.X.Value,
            IntentDirY = _offset.Y.Value,
            IntentTargetX = _offsetTarget.X.Value,
            IntentTargetY = _offsetTarget.Y.Value,
        };

        public void SetState(MovementState state)
        {
            _ticksUntilChange = state.TicksUntilChange;
            _offset = new FixedPoint2(
                new FixedPoint { Value = state.IntentDirX },
                new FixedPoint { Value = state.IntentDirY });
            _offsetTarget = new FixedPoint2(
                new FixedPoint { Value = state.IntentTargetX },
                new FixedPoint { Value = state.IntentTargetY });
        }
    }
}
