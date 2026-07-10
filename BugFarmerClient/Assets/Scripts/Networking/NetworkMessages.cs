using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// OpCodes for match state messages.
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Client -> Server
        public const int Movement = 1;
        public const int Action = 2;
        public const int ChunkSubscribe = 3;
        public const int ChunkUnsub = 4;
        public const int TilePlace = 5;
        public const int TileBreak = 6;
        public const int ToolUse = 7;

        // Server -> Client
        public const int StateUpdate = 10;
        public const int EntityUpdate = 11;
        public const int Chat = 12;

        // Farming - Server -> Client
        public const int CropUpdate = 50;
        public const int TreeWaterUpdate = 51; // tree water charges (droplet indicator)

        // Farming - Client -> Server
        public const int PlantInteract = 55;

        // World environment (dev tool + display) - must match server messages.go
        public const int DebugWorld = 90;       // C->S: set time / force weather / spawn swarm
        public const int WorldEnv = 91;         // S->C: day offset + weather (on change + join)
        public const int TreeHarvest = 92;      // C->S: hands-pick one fruit
        public const int TreeFruitUpdate = 93;  // S->C: a tree's fruit count (canopy overlay)

        // Predators
        public const int PlayerDamage = 94;     // S->C (victim only): bug attack / regen echo
        public const int BugTelegraph = 95;     // S->C: display-only attack telegraph
        public const int EquipArmor = 96;       // C->S: {equip_slot, inv_slot} equip/unequip/swap
        public const int EquipmentUpdate = 97;  // S->C: the 7 worn-armor slots (echo + join)
        public const int PredationStrike = 105; // C->S (authority only): individual flies a predator struck
        public const int ZoneCollisionMap = 106; // S->C (join + resync): zone-complete blocks_bugs cell set
        public const int ZoneRoofMap = 109;      // S->C (join + resync): zone-complete authored roof cell set (cosmetic — underground lighting)
    }

    /// <summary>
    /// Direction enum matching server entities.Direction.
    /// Down=0, Left=1, Right=2, Up=3
    /// </summary>
    public enum Direction
    {
        Down = 0,
        Left = 1,
        Right = 2,
        Up = 3
    }

    // === Client -> Server Messages ===

    /// <summary>
    /// Movement message sent to server (OpCode 1).
    /// Contains world coordinates and facing direction.
    /// </summary>
    [Serializable]
    public class MovementMessage
    {
        public float x;
        public float y;
        public int facing;
    }

    // === Server -> Client Messages ===

    /// <summary>
    /// Single entity data within EntityUpdateMessage.
    /// </summary>
    [Serializable]
    public class EntityData
    {
        public string id;
        public string type;
        public float x;
        public float y;
        public int facing;
        public string eq;   // equipped item id; NULL when absent (omitempty + JsonUtility),
        public string eqa;    // worn armor: 7 comma-joined ids (head,body,arms,legs,feet,acc1,acc2)
                            // not "" — consumers must null-coalesce
    }

    /// <summary>
    /// Entity update message from server (OpCode 11).
    /// Contains all entity positions for the tick.
    /// </summary>
    [Serializable]
    public class EntityUpdateMessage
    {
        public EntityData[] entities;
    }

    // === Farming Messages ===

    /// <summary>
    /// Tool use message sent to server (OpCode 7).
    /// Server looks up player.EquippedTool to determine action (hoe, watering can).
    /// </summary>
    [Serializable]
    public class ToolUseMessage
    {
        public int grid_x;  // Target cell X
        public int grid_y;  // Target cell Y
        // Player-chosen ground id for the SHOVEL (shaped-ground builder), e.g. "grass~dirt~diagNE".
        // Left empty for every other tool (server computes their result). Validated server-side.
        public string ground_id;
        // SHOVEL only: true = DIG (revert cell to dirt, gain the material block); false = PLACE.
        public bool dig;
    }

    /// <summary>
    /// Plant interact message sent to server (OpCode 55).
    /// Used for harvesting or destroying crops.
    /// </summary>
    [Serializable]
    public class PlantInteractMessage
    {
        public int grid_x;
        public int grid_y;
        public bool destroy_intent;  // true = destroy, false = harvest
    }

    /// <summary>
    /// Crop update message from server (OpCode 50).
    /// Sent when crop state changes (growth, watering).
    /// </summary>
    [Serializable]
    public class CropUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int stage;
        public int hp;
        public int water;
        public int flags;  // fertilized, etc.
    }

    /// <summary>
    /// Tree water/tank state (OpCode 51, display-only). Droplet rule, computed client-side:
    /// show iff water_level &lt; 3 &amp;&amp; last_water_day != currentDay — so the droplet
    /// reappears at the day rollover without a new message.
    /// </summary>
    [Serializable]
    public class TreeWaterUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int water_level;      // 0..3 tank
        public int pending_growth;   // fruits left to grow in the current batch
        public long last_water_day;  // day index of the last MANUAL watering (-1 = never)
    }

    /// <summary>
    /// World environment display state (OpCode 91): sent on change and to each joiner.
    /// Time of day on both sides: ((tick + day_offset_ticks) % 8400) / 8400.
    /// weather_until_tick shares the SimulationTick domain — the missed-stop fallback;
    /// the weather field applies ON RECEIPT ("" = stop now).
    /// </summary>
    [Serializable]
    public class WorldEnvMessage
    {
        public long day_offset_ticks;
        public string weather;            // "" or "rain"
        public long weather_until_tick;
    }

    /// <summary>
    /// Debug world controls (OpCode 90, dev tool — the F8 panel). Sentinels for "leave
    /// alone": set_time_ticks -1, weather "", spawn_species "".
    /// </summary>
    [Serializable]
    public class DebugWorldMessage
    {
        public int set_time_ticks = -1;   // -1 or 0..8399
        public string weather = "";       // "" | "rain" | "stop"
        public string spawn_species = "";
        public int spawn_count;
        public float spawn_x;
        public float spawn_y;
        public string give_item = "";     // "" no-op | "kit" (crafting bundle) | an item id
        public int give_count;            // count for a single item id (kit ignores it)
    }

    /// <summary>
    /// A tree's fruit count changed (OpCode 93, display-only): drives the canopy fruit
    /// overlay. Broadcast on change + re-sent per chunk-subscribe for fruited trees.
    /// </summary>
    [Serializable]
    public class TreeFruitUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int fruit_count;
        public string fruit_type;         // item id for the overlay sprite ("apple")
    }

    /// <summary>Hands-pick one fruit from the tree at (gx, gy) (OpCode 92).</summary>
    [Serializable]
    public class TreeHarvestMessage
    {
        public int gx;
        public int gy;
    }

    /// <summary>
    /// A bug attack landed on the LOCAL player (OpCode 94 — the server targets the
    /// victim's presence only). damage 0 = a regen/join echo for the hearts UI.
    /// </summary>
    [Serializable]
    public class PlayerDamageMessage
    {
        public int hp;
        public int max_hp;
        public int damage;
        public string source_species;
        public float knock_dx;
        public float knock_dy;
        public bool faint;
        public float respawn_x;
        public float respawn_y;
    }

    /// <summary>Display-only attack telegraph (OpCode 95): "strike" or "windup".</summary>
    [Serializable]
    public class BugTelegraphMessage
    {
        public string swarm_id;
        public string kind;
        // Phase 2: per-victim world points so the strike snatch plays AT each eaten fly. Display-only.
        public float[] victim_x;
        public float[] victim_y;
        // #20: the dead_<prey> sprite shown at each victim + how long it holds before fading (the
        // predator's feeding dwell). Both display-only; absent on older servers (JsonUtility leaves them 0/null).
        public string carcass_item;
        public float feed_pause_secs;
    }

    /// <summary>
    /// PredationStrike (OpCode 105, C→S, AUTHORITY ONLY): the authority client picked the individual flies a
    /// predator struck (it has per-bug positions; the server does not) and reports them. The server
    /// validates + applies the kill via the existing path, so followers/late-joiners sync via BUG_REMOVED.
    /// bug_x/bug_y are the victims' positions for the display-only snatch.
    /// </summary>
    [Serializable]
    public class PredationStrikeMessage
    {
        public string predator_swarm_id;
        public string prey_swarm_id;
        public int[] bug_ids;
        public float[] bug_x;
        public float[] bug_y;
        public long tick;
    }

    /// <summary>
    /// ZoneCollisionMap (OpCode 106, S→C, sent to one joiner on join + resync): the COMPLETE set of cells in
    /// the zone whose occupant blocks bugs. The client hydrates TilemapManager._blocksBugsZoneWide so its bug
    /// sim collides zone-wide + identically to every other client (Phase 1b). cx[i],cy[i] = one global cell.
    /// </summary>
    [Serializable]
    public class ZoneCollisionMapMessage
    {
        public int[] cx;
        public int[] cy;
    }

    /// <summary>
    /// ZoneRoofMap (OpCode 109, S→C, on join + resync): the COMPLETE set of authored "roofed"
    /// (underground / no-sun) cells. COSMETIC — the client darkens these for the underground lighting; never
    /// a sim input. cx[i],cy[i] = one global roofed cell.
    /// </summary>
    [Serializable]
    public class ZoneRoofMapMessage
    {
        public int[] cx;
        public int[] cy;
    }

    /// <summary>Sleep in a bed → set this character's home (OpCode 100, C→S): the bed's anchor cell.</summary>
    [Serializable]
    public class SetHomeMessage
    {
        public int gx;
        public int gy;
    }

    /// <summary>Buy/sell at an NPC vendor (OpCode 2 / Action, C→S). The server is authoritative for
    /// price + validation; the reply is the existing FullInventorySync echo (coins+items+bugs).
    /// op "sell_batch" carries the barter basket in `lines` (each line validated server-side).</summary>
    [Serializable]
    public class ShopActionMessage
    {
        public int gx;
        public int gy;
        public string op;          // "buy" | "sell" | "sell_batch"
        public string id;          // item or species id
        public int qty;            // default 1
        public int slot;           // sell: which player slot
        public string slot_type;   // "item" | "bug" (sell)
        public ShopSellLine[] lines; // sell_batch: the staged basket
    }

    /// <summary>One staged basket line of a sell_batch (mirrors the Go ShopSellLine).</summary>
    [Serializable]
    public class ShopSellLine
    {
        public string slot_type;   // "item" | "bug"
        public int slot;           // the player's slot index
        public string id;          // what the slot is expected to hold
        public int qty;            // how many to sell
    }

    /// <summary>Home-set confirmation (OpCode 101, S→C): shown as a brief toast.</summary>
    [Serializable]
    public class SetHomeAckMessage
    {
        public bool ok;
        public string message;
        public float home_x;
        public float home_y;
    }

    /// <summary>Authoritative local-player spawn on join (OpCode 102, S→C).</summary>
    [Serializable]
    public class PlayerSpawnMessage
    {
        public float x;
        public float y;
    }

    /// <summary>One remote player's cosmetic identity — drives the paper-doll + nameplate (OpCode 103).</summary>
    [Serializable]
    public class PlayerInfoEntry
    {
        public string user_id;
        public string name;
        public string char_class;
        public string char_hair;
        public string char_skin;
    }

    /// <summary>Per-player appearance + name, sent once on join (roster, or a single newcomer). OpCode 103.</summary>
    [Serializable]
    public class PlayerInfoMessage
    {
        public PlayerInfoEntry[] players;
    }

    // === Character RPCs (per-account roster; see nakama/modules/rpc/character.go) ===

    /// <summary>Server RPC error envelope ({"error","code"}, returned with HTTP 200).</summary>
    [Serializable]
    public class ErrorResponse
    {
        public string error;
        public string code;
    }

    /// <summary>Cosmetic identity for the paper-doll composer (server: world.Appearance).</summary>
    [Serializable]
    public class CharacterAppearance
    {
        public string @class;  // "class" is a C# keyword — JsonUtility maps the field name verbatim
        public string hair;
        public string skin;
    }

    /// <summary>Lightweight character view for the select screen (server: world.CharacterSummary).</summary>
    [Serializable]
    public class CharacterSummary
    {
        public string char_id;
        public string name;
        public CharacterAppearance appearance;
        public string last_zone;
        public long last_played_at;
    }

    /// <summary>Response of character_list (wrapper — JsonUtility can't parse a top-level array).</summary>
    [Serializable]
    public class CharacterListResponse
    {
        public CharacterSummary[] characters;
    }

    /// <summary>Request of character_create.</summary>
    [Serializable]
    public class CharacterCreateRequest
    {
        public string name;
        public string @class;
        public string hair;
        public string skin;
    }

    /// <summary>Response of character_create.</summary>
    [Serializable]
    public class CharacterCreateResponse
    {
        public CharacterSummary character;
    }

    /// <summary>Request of character_delete.</summary>
    [Serializable]
    public class CharacterDeleteRequest
    {
        public string char_id;
    }

    /// <summary>Response of character_delete.</summary>
    [Serializable]
    public class CharacterDeleteResponse
    {
        public string deleted;
    }

    /// <summary>
    /// The character chosen on the select screen, for this session. Read by WorldManager.EnterWorld
    /// (join metadata) and the WorldMenu gate. Appearance is authoritative from the server on join
    /// (FullInventorySync), so this only needs to carry the id + a label for the menu.
    /// </summary>
    public static class CharacterSession
    {
        public static string SelectedCharID;
        public static string SelectedCharName;

        // Chosen appearance (the LOCAL player renders this immediately — the client picked it).
        // Defaults match the baked merchant body so a no-selection join still looks right.
        public static string Class = "merchant";
        public static string Hair = "blonde";
        public static string Skin = "default";

        public static bool HasSelection => !string.IsNullOrEmpty(SelectedCharID);

        public static void SetAppearance(CharacterAppearance app)
        {
            Class = !string.IsNullOrEmpty(app?.@class) ? app.@class : "merchant";
            Hair = !string.IsNullOrEmpty(app?.hair) ? app.hair : "blonde";
            Skin = !string.IsNullOrEmpty(app?.skin) ? app.skin : "default";
        }
    }
}
