namespace BugFarmer.Bugs
{
    /// <summary>
    /// Movement state for synchronization between clients.
    /// Captures all state needed to reproduce deterministic behavior.
    /// </summary>
    public struct MovementState
    {
        public int TicksUntilChange;
        public int IntentDirX, IntentDirY;       // Brownian: intent direction (FixedPoint.Value)
        public int IntentTargetX, IntentTargetY; // Gliding: intent target position (FixedPoint.Value)
        public int CurrentDirX, CurrentDirY;     // Gliding: current direction (FixedPoint.Value)
    }

    /// <summary>
    /// Strategy interface for bug movement behaviors.
    /// Each bug gets its own instance (not shared) because behaviors can have per-bug state.
    /// </summary>
    public interface IBugMovement
    {
        /// <summary>
        /// Update the bug's velocity for wander behavior. Called each tick.
        /// </summary>
        /// <param name="bug">The bug agent to update</param>
        /// <param name="swarmCenter">Current swarm center position</param>
        /// <param name="wanderRadiusSqr">Squared wander radius (for distance checks)</param>
        void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr);

        /// <summary>
        /// Move toward a target at full speed (for chase/attack behavior).
        /// </summary>
        void MoveToward(BugAgent bug, FixedPoint2 target);

        /// <summary>
        /// Move toward a target slowly (for curious behavior - gentle drift).
        /// </summary>
        void MoveTowardSlow(BugAgent bug, FixedPoint2 target);

        /// <summary>
        /// Move away from a target (for flee behavior).
        /// </summary>
        void MoveAwayFrom(BugAgent bug, FixedPoint2 target);

        /// <summary>
        /// Get current movement state for snapshot sync.
        /// </summary>
        MovementState GetState();

        /// <summary>
        /// Set movement state from snapshot sync.
        /// </summary>
        void SetState(MovementState state);
    }
}
