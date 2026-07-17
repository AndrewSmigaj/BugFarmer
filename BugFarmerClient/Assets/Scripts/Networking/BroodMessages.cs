using System;

namespace BugFarmer.Networking
{
    public static partial class OpCodes
    {
        // Life-stage nursery (display-only; mirrors server nakama/modules/world/messages.go)
        public const int BroodUpdate = 104; // S->C: a brood's egg/larva/pupa counts changed (display-only nursery)
        public const int NurseryTake = 113; // C->S: take brood units from a nursery station into the bag
        public const int NurseryDeposit = 114; // C->S: place brood units from a bag slot INTO a compatible nursery
    }

    /// <summary>
    /// Take brood units OUT of a nursery station into the bag (OpCode 113). A plain station transfer —
    /// stage 0=egg, 1=larva, 2=pupa; count<=0 = take all of that stage. Field names match the server
    /// NurseryTakeMessage json tags exactly (JsonUtility binds by name).
    /// </summary>
    [Serializable]
    public class NurseryTakeMessage
    {
        public int gx;
        public int gy;
        public int stage;
        public int count;
    }

    /// <summary>
    /// Place brood units FROM a bag slot INTO a compatible nursery (OpCode 114) — the reciprocal of take.
    /// slot = the player inventory slot holding the brood item; count<=0 = the whole slot. The server
    /// resolves the item's species+stage and rejects a cross-species deposit. Field names match the server
    /// NurseryDepositMessage json tags (JsonUtility binds by name).
    /// </summary>
    [Serializable]
    public class NurseryDepositMessage
    {
        public int gx;
        public int gy;
        public int slot;
        public int count;
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
