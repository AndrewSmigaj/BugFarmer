namespace BugFarmer.Networking
{
    public static partial class OpCodes
    {
        public const int HiveHarvest = 107;    // C->S: hand-harvest the hive at {gx,gy}
        public const int HiveHarvestAck = 108; // S->C (harvester only): result toast {ok,count,message}
    }

    /// <summary>Hand-harvest request: pull every whole honeycomb from the hive at (gx,gy).
    /// The server recalls the colony's defenders unless the hive was freshly smoked.</summary>
    [System.Serializable]
    public class HiveHarvestMessage
    {
        public int gx;
        public int gy;
    }

    /// <summary>Harvest result (presence-targeted). message carries the flavor line
    /// ("The hive SEETHES!" / "The smoke keeps them calm.").</summary>
    [System.Serializable]
    public class HiveHarvestAckMessage
    {
        public bool ok;
        public int count;
        public string message;
    }
}
