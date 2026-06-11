namespace BugFarmer.Bugs
{
    /// <summary>
    /// Movement for INDIVIDUAL ground bugs (centipede): the single bug's position hard-
    /// tracks the swarm center VERBATIM — zero jitter, no per-bug collision (legality is
    /// the server leg clamp's job; skipping BugCollision.Resolve also sidesteps the
    /// raycast's diagonal-corner permeability). Effectively stateless → trivially
    /// snapshot-safe (GetState/SetState are no-ops). Render smoothing and the segment
    /// trail live in the VISUAL layer (CentipedeTrail), never here — Position is hash
    /// state. Reaction display is off for individuals (BugAgent gates on behavior
    /// "ignore" via the species row).
    /// </summary>
    public class CrawlingMovement : IBugMovement
    {
        public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr)
        {
            // Velocity = exactly the delta to the center: position lands ON it this tick.
            bug.Velocity = new FixedPoint2(
                swarmCenter.X - bug.Position.X,
                swarmCenter.Y - bug.Position.Y
            );
        }

        // Individuals never run the reaction-display branches (species reaction is
        // "ignore"); these exist to satisfy the interface and behave sanely if reached.
        public void MoveToward(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public void MoveTowardSlow(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public void MoveAwayFrom(BugAgent bug, FixedPoint2 target) =>
            bug.Velocity = FixedPoint2.Zero;

        public MovementState GetState() => new MovementState();

        public void SetState(MovementState state) { }
    }
}
