using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Containers &amp; crafting OpCodes (extends OpCodes partial class).
    /// Must match server nakama/modules/world/messages.go (OpCodeContainer / OpCodeContainerUpdate).
    /// </summary>
    public static partial class OpCodes
    {
        public const int Container = 98;       // C->S: a container / craft-station action (Op switches behavior)
        public const int ContainerUpdate = 99; // S->C: a container / craft-station's contents + craft progress
        public const int SetHome = 100;        // C->S: sleep in a bed → set this character's home {gx,gy}
        public const int SetHomeAck = 101;     // S->C: home-set confirmation {ok,message,home_x,home_y}
        public const int PlayerSpawn = 102;    // S->C: authoritative local-player spawn on join {x,y}
        public const int PlayerInfo = 103;     // S->C: per-player appearance + name (static; on join)
    }

    /// <summary>
    /// OpCode 98 (C->S): one action on the container / craft-station at (gx,gy). Op selects which
    /// fields matter — see ContainerActionMessage on the server:
    ///   "open"       — just request the current contents
    ///   "quick"      {zone, slot}                      — move a WHOLE stack to the opposite side
    ///   "move"       {zone, slot, to_zone, to_slot, count} — precise drag-drop (-1 = all)
    ///   "set_recipe" {recipe, proc}                    — craft station: pick a lane's active recipe
    ///   "craft"      {recipe, qty, proc}               — craft station: queue qty batches on a lane
    ///   "collect"    {slot}                            — craft station: take ONE output cell (shared grid)
    ///   "get_all"                                      — craft station: sweep the output grid
    /// zone / to_zone are "player" | "container". proc = the processor lane (craft_slots of them;
    /// 0 default) — distinct from slot, which is collect's output-cell index.
    /// </summary>
    [Serializable]
    public class ContainerActionMessage
    {
        public int gx;
        public int gy;
        public string op;
        public string zone;
        public int slot;
        public string to_zone;
        public int to_slot;
        public int count;
        public string recipe;
        public int qty;
        public int proc;
    }

    /// <summary>
    /// OpCode 99 (S->C): a container / craft-station's full contents after any change (plus
    /// per-processor craft progress when is_craft). Display/inventory state only.
    /// (InventorySlot.metadata is ignored by JsonUtility — fine: Stage-1 container/output
    /// contents are stackable materials.)
    /// </summary>
    [Serializable]
    public class ContainerUpdateMessage
    {
        public int gx;
        public int gy;
        public InventorySlot[] slots;  // chest contents OR the craft station's SHARED output grid
        public string filter;          // tag filter (chests); "" = none

        // Craft-station fields (default/absent for plain chests): one entry per processor lane.
        public bool is_craft;
        public CraftProcInfo[] procs;
    }

    /// <summary>One processor lane's display state (mirrors the Go CraftProcInfo).</summary>
    [Serializable]
    public class CraftProcInfo
    {
        public string recipe;          // the lane's active recipe id
        public int progress;           // ticks into the current batch
        public int total;              // process_ticks of the current batch
        public int queue;              // batches remaining (incl current)
    }
}
