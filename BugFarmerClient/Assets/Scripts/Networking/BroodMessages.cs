using System;

namespace BugFarmer.Networking
{
    public static partial class OpCodes
    {
        // Life-stage nursery (display-only; mirrors server nakama/modules/world/messages.go)
        public const int BroodUpdate = 104; // S->C: a brood's egg/larva/pupa counts changed (display-only nursery)
    }

    /// <summary>
    /// A visible nursery's stage counts changed (OpCode 104). DISPLAY-ONLY — the actual births ride the
    /// deterministic SWARM_REPRODUCED ledger, so a dropped/late BroodUpdate only delays the on-screen stage
    /// sprite, never the bug positions. Field names match the server BroodUpdateMessage json tags exactly
    /// (JsonUtility binds by name).
    /// </summary>
    [Serializable]
    public class BroodUpdateMessage
    {
        public int gx;
        public int gy;
        public string species;
        public int eggs;
        public int maggots;   // LARVA stage
        public int pupae;     // PUPA stage (any pupating species — fly/butterfly/beetle/wasp; 0 for non-pupating)
        public float progress; // current stage's fraction toward the next transition (0..1) — the panel's conversion bar
        public int residents; // resident adults living IN the station (nests today; 0 otherwise) — the panel's adult slots
        public string kind;   // "station" | "host_plant" | "ground_pile" | "nest"
        public bool removed;
    }
}
