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
        public bool FliesOverFences;   // HASH-BEARING: per-bug collision skips occupants
        public bool SkipCollision;     // crawling individuals: head = center verbatim
        // ATTACK-movement knobs (player_reaction "attack"): the cloud hovers `Standoff` cells off the player and
        // each bug swoops in for `DiveTicks` every `DivePeriodTicks`, staggered per bug-id so ~1-2 dive at once.
        // Hash-bearing (drives Agent.Position), from the attack{} block. 0 = a sensible default (see BugAgent).
        public float Standoff;
        public int DivePeriodTicks;
        public int DiveTicks;
    }

    /// <summary>
    /// Factory for creating movement behaviors and getting species config — DATA-DRIVEN
    /// via the published Data/species.json (movement_style / player_reaction /
    /// flies_over_fences through EntityDatabase): a new species is one data row + a
    /// sprite. The per-STYLE numeric tuning lives here; the old per-species-id switch
    /// remains as the fallback for rows without a movement_style. These values feed the
    /// deterministic per-bug sim — same-build clients parse the same published file
    /// (the established class; publish_entities.py is the drift tripwire).
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
            var info = Data.EntityDatabase.GetSpecies(speciesId);
            switch (info?.MovementStyle)
            {
                case "brownian":
                    return new BrownianMovement(speed: 0.2f, changeRate: 0.3f);
                case "gliding":
                    return new GlidingMovement(speed: 0.15f, intentRange: 10f, changeRate: 0.05f, turnRate: 0.1f);
                case "darting":
                    // dash 0.35 ≥ the ×1.5 hunt-leg center speed (0.33) — visuals never trail
                    return new DartingMovement(dashSpeed: 0.35f, hoverSpeed: 0.06f);
                case "crawling":
                    return new CrawlingMovement();
            }
            // Fallback: the legacy per-species-id switch (rows without movement_style)
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
            // DATA branch: rows with a movement_style carry their full behavior config
            // in the published species.json (player_reaction/reaction_radius/
            // flies_over_fences) — the wasp ships as pure data.
            var info = Data.EntityDatabase.GetSpecies(speciesId);
            if (info != null && !string.IsNullOrEmpty(info.MovementStyle))
            {
                // Per-bug wander leash is DISPLAY tuning, set per style (the previously
                // hardcoded per-species values, preserved):
                float wander = info.MovementStyle switch
                {
                    "gliding" => 5.0f,
                    "darting" => 1.5f, // strike formation: tight
                    "crawling" => 0f,  // the head IS the center
                    _ => 4.0f,         // brownian
                };
                var atk = info.Attack;
                return new SpeciesBehavior
                {
                    PlayerReaction = string.IsNullOrEmpty(info.PlayerReaction) ? "ignore" : info.PlayerReaction,
                    ReactionRadius = info.ReactionRadius,
                    WanderRadius = wander,
                    FliesOverFences = info.FliesOverFences,
                    SkipCollision = info.MovementStyle == "crawling",
                    Standoff = atk != null ? atk.Standoff : 0f,
                    DivePeriodTicks = atk != null && atk.DivePeriodSecs > 0 ? (int)(atk.DivePeriodSecs * 10f) : 0,
                    DiveTicks = atk != null && atk.DiveSecs > 0 ? (int)(atk.DiveSecs * 10f) : 0,
                };
            }

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
