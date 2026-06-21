using BugFarmer.Networking;

namespace BugFarmer.Tracing
{
    /// <summary>
    /// Simplified bug trace struct for CSV output.
    /// Uses FixedPoint.Value (int) - no floats for determinism.
    /// </summary>
    [System.Serializable]
    public struct BugTrace
    {
        public long tick;
        public string swarmId;
        public int bugId;
        public int x;           // FixedPoint.Value (no floats!)
        public int y;
        public int vx;
        public int vy;
        public string behavior; // "wander", "flee", etc.
        public int alertCooldown;
        public uint rngState;
        public int ticksUntilChange; // Brownian wander-cycle phase (key desync signal)
        public int intentDirX;
        public int intentDirY;
        public long spawnTick;     // DIAGNOSTIC (re-root investigation): when this client created the bug
        public string spawnSource; // DIAGNOSTIC: via which path (metadataPrespawn/liveSwarmUpdate/reproduce/...)

        public string ToCsv() =>
            $"{tick},{swarmId},{bugId},{x},{y},{vx},{vy},{behavior},{alertCooldown},{rngState},{ticksUntilChange},{intentDirX},{intentDirY},{spawnTick},{spawnSource}";

        public static string CsvHeader => "tick,swarmId,bugId,x,y,vx,vy,behavior,alertCooldown,rngState,ticksUntilChange,intentDirX,intentDirY,spawnTick,spawnSource";

        /// <summary>
        /// Create from existing BugSampleData.
        /// </summary>
        public static BugTrace FromSampleData(long tick, BugSampleData data)
        {
            return new BugTrace
            {
                tick = tick,
                swarmId = data.swarm_id,
                bugId = data.bug_id,
                x = data.x,
                y = data.y,
                vx = data.vx,
                vy = data.vy,
                behavior = data.behavior,
                alertCooldown = data.alert_cooldown,
                rngState = data.rng_state,
                ticksUntilChange = data.ticks_until_change,
                intentDirX = data.intent_dir_x,
                intentDirY = data.intent_dir_y,
                spawnTick = data.spawn_tick,
                spawnSource = data.spawn_source
            };
        }
    }

    /// <summary>
    /// DIAGNOSTIC (leg/center late-join divergence): per-swarm movement-leg + derived center, captured each
    /// traced tick. Comparing this A-vs-B at common ticks pins whether the residual is leg-CONTENT divergence
    /// (origin/target/speed/startTick differ) or a no-leg fallback-center mismatch (hasLeg differs / fallback
    /// differs). All ints are FixedPoint.Value (no floats — determinism). See architecture_swarm_sync.md.
    /// </summary>
    [System.Serializable]
    public struct SwarmLegTrace
    {
        public long tick;
        public string swarmId;
        public bool hasLeg;        // did InfluenceManager hold a leg (vs falling back to metadata center)?
        public int originX, originY;
        public int targetX, targetY;
        public int speed;
        public long startTick;     // leg start tick (closed-form march reference)
        public int centerX, centerY;     // the center bug AI actually used this tick (_simCenter)
        public int fallbackX, fallbackY; // metadata/initial center (used when hasLeg == false)
        public bool foodNear;            // is a food source within feed range of the center? (food-registry coherence)

        public string ToCsv() =>
            $"{tick},{swarmId},{(hasLeg ? 1 : 0)},{originX},{originY},{targetX},{targetY},{speed},{startTick},{centerX},{centerY},{fallbackX},{fallbackY},{(foodNear ? 1 : 0)}";

        public static string CsvHeader =>
            "tick,swarmId,hasLeg,originX,originY,targetX,targetY,speed,startTick,centerX,centerY,fallbackX,fallbackY,foodNear";
    }
}
