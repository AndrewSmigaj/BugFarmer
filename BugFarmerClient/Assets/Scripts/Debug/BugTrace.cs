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

        public string ToCsv() =>
            $"{tick},{swarmId},{bugId},{x},{y},{vx},{vy},{behavior},{alertCooldown},{rngState},{ticksUntilChange},{intentDirX},{intentDirY}";

        public static string CsvHeader => "tick,swarmId,bugId,x,y,vx,vy,behavior,alertCooldown,rngState,ticksUntilChange,intentDirX,intentDirY";

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
                intentDirY = data.intent_dir_y
            };
        }
    }
}
