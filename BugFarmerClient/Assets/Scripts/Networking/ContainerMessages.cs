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
    }

    /// <summary>
    /// OpCode 98 (C->S): one action on the container / craft-station at (gx,gy). Op selects which
    /// fields matter — see ContainerActionMessage on the server:
    ///   "open"       — just request the current contents
    ///   "quick"      {zone, slot}                      — move a WHOLE stack to the opposite side
    ///   "move"       {zone, slot, to_zone, to_slot, count} — precise drag-drop (-1 = all)
    ///   "set_recipe" {recipe}                          — craft station: pick the active recipe
    ///   "craft"      {recipe, qty}                     — craft station: queue qty batches
    ///   "collect"    {slot}                            — craft station: take ONE output cell
    ///   "get_all"                                      — craft station: sweep the output grid
    /// zone / to_zone are "player" | "container".
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
    }

    /// <summary>
    /// OpCode 99 (S->C): a container / craft-station's full contents after any change (plus craft
    /// progress when is_craft). Display/inventory state only. (InventorySlot.metadata is ignored by
    /// JsonUtility — fine: Stage-1 container/output contents are stackable materials.)
    /// </summary>
    [Serializable]
    public class ContainerUpdateMessage
    {
        public int gx;
        public int gy;
        public InventorySlot[] slots;  // chest contents OR craft output grid
        public string filter;          // tag filter (chests); "" = none

        // Craft-station fields (default/absent for plain chests)
        public bool is_craft;
        public string recipe;          // active recipe id
        public int progress;           // ticks into the current batch
        public int total;              // process_ticks of the current batch
        public int queue;              // batches remaining (incl current)
    }
}
