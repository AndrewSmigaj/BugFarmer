namespace BugFarmer.Bugs
{
    /// <summary>
    /// Species behavior configuration. Values match server species.json.
    /// </summary>
    public struct SpeciesBehavior
    {
        public string PlayerReaction;  // "ignore", "flee", "attack", "curious"
        public float ReactionRadius;   // Distance at which bug reacts to players
        public float WanderRadius;     // How far bugs wander from swarm center
    }

    /// <summary>
    /// Factory for creating movement behaviors and getting species config.
    /// Hardcoded for Phase 1 - could later load from species.json.
    /// </summary>
    public static class MovementFactory
    {
        /// <summary>
        /// Create a movement behavior instance for the given species.
        /// Each bug should get its own instance (movement has per-bug state).
        /// Speed values are in blocks/tick (at 10Hz, multiply by 10 to get blocks/sec).
        /// </summary>
        public static IBugMovement CreateMovement(string speciesId)
        {
            return speciesId switch
            {
                "fly_common" => new BrownianMovement(
                    speed: 0.2f,       // ~2 blocks/sec - erratic buzzing
                    changeRate: 0.3f
                ),
                "butterfly_meadow" => new GlidingMovement(
                    speed: 0.15f,      // ~1.5 blocks/sec - slower, graceful
                    intentRange: 10f,
                    changeRate: 0.05f,
                    turnRate: 0.1f
                ),
                "bee" => new BrownianMovement(
                    speed: 0.25f,      // ~2.5 blocks/sec - faster than flies
                    changeRate: 0.25f
                ),
                "moth" => new GlidingMovement(
                    speed: 0.1f,       // ~1 block/sec - slow, gentle
                    intentRange: 6f,
                    changeRate: 0.08f,
                    turnRate: 0.15f
                ),
                _ => new BrownianMovement(
                    speed: 0.15f,      // ~1.5 blocks/sec default
                    changeRate: 0.3f
                )
            };
        }

        /// <summary>
        /// Get behavior configuration for the given species.
        /// </summary>
        public static SpeciesBehavior GetBehavior(string speciesId)
        {
            return speciesId switch
            {
                "fly_common" => new SpeciesBehavior
                {
                    PlayerReaction = "flee",
                    ReactionRadius = 6.0f,
                    WanderRadius = 4.0f
                },
                "butterfly_meadow" => new SpeciesBehavior
                {
                    PlayerReaction = "curious",
                    ReactionRadius = 8.0f,
                    WanderRadius = 5.0f
                },
                "bee" => new SpeciesBehavior
                {
                    PlayerReaction = "attack",
                    ReactionRadius = 5.0f,
                    WanderRadius = 3.0f
                },
                "moth" => new SpeciesBehavior
                {
                    PlayerReaction = "curious",
                    ReactionRadius = 4.0f,
                    WanderRadius = 4.0f
                },
                _ => new SpeciesBehavior
                {
                    PlayerReaction = "ignore",
                    ReactionRadius = 0f,
                    WanderRadius = 4.0f
                }
            };
        }
    }
}
