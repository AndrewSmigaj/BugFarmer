using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Bug system OpCodes (extends OpCodes partial class).
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Bug System - Server -> Client
        public const int SwarmUpdate = 20;

        // Bug Catching (Phase 2a)
        public const int CatchBug = 24;           // C->S: Click to catch
        public const int BugCaught = 25;          // S->C: Broadcast catch event
        // OpCode 26 (BugSlotUpdate) moved to InventoryMessages.cs
        public const int EquipTool = 27;          // C->S: Equip/unequip tool

        // Bug Simulation (Phase 6 - Deterministic Per-Bug)
        public const int WorldInit = 68;          // S->C: WorldSeed on join (sent once)

        // Bug Sync OpCodes (Late Joiner + Drift Detection)
        public const int RequestSample = 61;      // S->C: Request positions for specific bug IDs
        public const int SampleResponse = 62;     // C->S: Positions for requested bugs
        public const int SampleBroadcast = 63;    // S->C: Sample for local comparison
        public const int RequestSnapshot = 66;    // C->S: Client requests full snapshot (drift)
        public const int FullSnapshot = 67;       // S->C: Full bug positions for resync

        // Stations (player-fillable processors: compost bin etc.)
        public const int StationDeposit = 85;     // C->S: Deposit an inventory item into a station
        public const int StationUpdate = 86;      // S->C: Station fill changed (UI meter)

        // Dev tuning (debug): live-override ecology parameters on the server
        public const int EcologyTuning = 87;      // C->S: EcologyTuningMessage

        // Combat (melee weapons: sword/spear). ONE message per swing — a swing may hit
        // multiple swarms, carried as entries of one payload.
        public const int MeleeAttack = 88;        // C->S: swing with detected (swarm, ids) hits
        public const int MeleeResult = 89;        // S->C: validated damage/kills — the SOLE
                                                  // per-bug HP display channel + cosmetics
                                                  // (kills ALSO arrive as BUG_REMOVED ledger events)

        // Influence Event OpCodes (Server-Authored Bug Sync)
        public const int InfluenceBroadcast = 71; // S->C: Player cell change events
        public const int LateJoinSnapshot = 72;   // S->C: Full state for late joiner
        public const int ZoneHandoff = 73;        // S->C: Handoff watermark after late join
        public const int ZoneSnapshot = 75;       // C->S: Authority sends periodic snapshot
        public const int ZoneAuthority = 76;      // S->C: Authority assigned/changed
        public const int ZoneHash = 77;           // C->S: Client sends state hash
        public const int ZoneTickBroadcast = 78;  // S->C: Tick frontier update (10Hz)
    }

    /// <summary>
    /// World initialization message from server (OpCode 68).
    /// Sent once on join with seed for deterministic simulation.
    /// </summary>
    [Serializable]
    public class WorldInitMessage
    {
        public long world_seed;
        public long tick;
    }

    /// <summary>
    /// Single swarm data within SwarmUpdateMessage.
    /// Matches server SwarmData struct.
    /// </summary>
    [Serializable]
    public class SwarmData
    {
        public string id;
        public string species_id;
        public string sprite_id;
        public float x;
        public float y;
        public float radius;
        public int count;
        public int facing;
        public string phase;           // "feeding", "reproducing", "idle"
        public int next_bug_id;        // Total bugs ever spawned (for late joiners)
        public int[] removed_ids;      // Bug IDs to skip when spawning (for late joiners)
        public BugHPEntry[] bug_hp;    // Damaged bugs' remaining HP (display seed; populated
                                       // ONLY by the late-join snapshot, else null)

        // In-flight movement leg active at snapshot_tick (late-join hydration only).
        // Fixed-point (value/1000 = actual), identical to the originating SWARM_SET_TARGET
        // event so the hydrated leg reproduces the live center march bit-for-bit.
        public bool has_target;
        public int leg_origin_x;
        public int leg_origin_y;
        public int leg_target_x;
        public int leg_target_y;
        public int leg_speed;
        public long leg_start_tick;
    }

    /// <summary>
    /// Swarm update message from server (OpCode 20).
    /// Contains all swarm positions for the tick.
    /// </summary>
    [Serializable]
    public class SwarmUpdateMessage
    {
        public long tick;           // Server tick for sync (matches server messages.go)
        public SwarmData[] swarms;
    }

    // === Bug Catching Messages (Phase 2a) ===

    /// <summary>
    /// Catch attempt sent to server (OpCode 24).
    /// Client detects bugs by ID and sends the list for validation.
    /// </summary>
    [Serializable]
    public class CatchBugMessage
    {
        public float click_x;
        public float click_y;
        public string swarm_id;
        public int[] bug_ids;      // IDs of bugs client detected in radius
    }

    /// <summary>
    /// Catch event broadcast to all clients (OpCode 25).
    /// All clients use validated bug IDs for deterministic removal.
    /// </summary>
    [Serializable]
    public class BugCaughtMessage
    {
        public string swarm_id;
        public string catcher_id;
        public int[] bug_ids;      // Server-validated bug IDs to remove
        public int new_total;
        public float x;
        public float y;
    }

    /// <summary>
    /// Melee swing sent to server (OpCode 88): ONE message per swing; hits lists every
    /// swarm the swept sector intercepted with the client-detected bug IDs.
    /// </summary>
    [Serializable]
    public class MeleeAttackMessage
    {
        public float click_x;
        public float click_y;
        public string move;        // input slot ("primary"/"secondary"); empty = primary
        public MeleeSwarmHits[] hits;
    }

    [Serializable]
    public class MeleeSwarmHits
    {
        public string swarm_id;
        public int[] bug_ids;
    }

    /// <summary>
    /// Melee result broadcast to all clients (OpCode 89): the SOLE channel for per-bug HP
    /// display (DisplayHP on BugVisual — HP never rides the deterministic ledger) plus all
    /// combat cosmetics. hp values are ABSOLUTE (last-writer-wins converges when two
    /// players hit the same bug). Kills land authoritatively via BUG_REMOVED ledger events
    /// in the same network flush; killed[] here is only the cosmetic pop + attribution.
    /// </summary>
    [Serializable]
    public class MeleeResultMessage
    {
        public string attacker_id;
        public float click_x;
        public float click_y;
        public string weapon;      // attacker's weapon id — self-describing remote replay
        public string move;        // RESOLVED move name (server normalizes ""->"primary")
        public MeleeSwarmResult[] results;
    }

    [Serializable]
    public class MeleeSwarmResult
    {
        public string swarm_id;
        public BugHPEntry[] damaged;   // survivors: absolute hp_left
        public int[] killed;           // removed ids (cosmetic; removal = ledger)
    }

    /// <summary>(bug id, remaining hp) pair — an array entry because JsonUtility cannot
    /// deserialize dictionaries (same reason removed_ids is int[]).</summary>
    [Serializable]
    public class BugHPEntry
    {
        public int bug_id;
        public int hp;
    }

    // BugInventoryUpdateMessage removed - replaced by SlotUpdateMessage in InventoryMessages.cs

    /// <summary>
    /// Tool equip message sent to server (OpCode 27).
    /// Syncs equipped tool state for reach validation.
    /// </summary>
    [Serializable]
    public class EquipToolMessage
    {
        public string tool_id; // "" for hand, "small_net" for small net, etc.
    }

    // === Bug Sync Messages (Late Joiner + Drift Detection) ===

    /// <summary>
    /// Query for a single bug's position.
    /// </summary>
    [Serializable]
    public class BugSampleQuery
    {
        public string swarm_id;
        public int bug_id;
    }

    /// <summary>
    /// Full state data for a single bug using fixed-point (value/1000 = actual).
    /// Includes all state needed for deterministic sync.
    /// </summary>
    [Serializable]
    public class BugSampleData
    {
        // Core state
        public string swarm_id;
        public int bug_id;
        public int x;   // FixedPoint.Value: actual = x / 1000f
        public int y;   // FixedPoint.Value: actual = y / 1000f
        public int vx;  // Velocity X (fixed-point)
        public int vy;  // Velocity Y (fixed-point)
        public uint rng_state;  // RNG state for deterministic sync

        // Behavior state
        public string behavior;      // "wander", "flee", "attack", "curious"
        public string target_id;     // Player ID bug is reacting to (empty if none)
        public bool is_alerted;
        public int alert_cooldown;

        // Movement state
        public int ticks_until_change;
        public int intent_dir_x, intent_dir_y;       // Brownian: intent direction
        public int intent_target_x, intent_target_y; // Gliding: intent target
        public int current_dir_x, current_dir_y;     // Gliding: current direction

        // DIAGNOSTIC ONLY (re-root investigation; never hashed): provenance of this bug on this client.
        public long spawn_tick = -1;
        public string spawn_source = "?";
    }

    /// <summary>
    /// Server requests our state hash at a settled tick (OpCode 61).
    /// </summary>
    [Serializable]
    public class SampleRequestMessage
    {
        public int chunk_x;
        public int chunk_y;
        public long tick;   // Settled tick to hash (behind the frontier)
    }

    /// <summary>
    /// Client responds with its ComputeStateHash() at the requested tick (OpCode 62).
    /// has_hash=false means the tick is no longer buffered (abstain from comparison).
    /// </summary>
    [Serializable]
    public class SampleResponseMessage
    {
        public int chunk_x;
        public int chunk_y;
        public long tick;
        public long hash;
        public bool has_hash;
    }

    /// <summary>
    /// Client requests full snapshot when drift detected (OpCode 66).
    /// </summary>
    [Serializable]
    public class SnapshotRequestMessage
    {
        public int chunk_x;
        public int chunk_y;
    }

    /// <summary>
    /// All bug positions for a single swarm.
    /// </summary>
    [Serializable]
    public class SwarmSnapshotData
    {
        public string swarm_id;
        public BugSampleData[] bugs;

        // Current movement leg AT the snapshot tick (authoritative). Lets late-join hydrate the swarm
        // center coherently — the server's InfluenceLog is pruned, so a slow swarm's last SWARM_SET_TARGET
        // may be gone. has_leg=false means the swarm has no leg yet (use the fallback center).
        public bool has_leg;
        public int leg_origin_x, leg_origin_y;
        public int leg_target_x, leg_target_y;
        public int leg_speed;
        public long leg_start_tick;
    }

    /// <summary>
    /// Full snapshot for late joiners or drift correction (OpCode 67).
    /// </summary>
    [Serializable]
    public class FullSnapshotMessage
    {
        public int chunk_x;
        public int chunk_y;
        public long tick;
        public SwarmSnapshotData[] swarms;
    }

    // === Influence Event Messages (Server-Authored Bug Sync) ===

    /// <summary>
    /// Single influence event from server.
    /// Server-authored, ensures all clients process same ordered event stream.
    /// </summary>
    [Serializable]
    public class InfluenceEvent
    {
        public long tick;                  // Simulation tick when event occurs
        public long seq;                   // Strictly increasing sequence number (zone-local)
        public string type;                // "PLAYER_CELL_ENTER", "PLAYER_CELL_LEAVE", etc.
        public string zone_id;             // Zone this event belongs to
        public string player_id;           // For PLAYER_CELL_* events
        public int cell_x;                 // Cell coordinates
        public int cell_y;
        public string swarm_id;            // For BUG_* and SWARM_* events
        public int bug_id;                 // For BUG_* events

        // For SWARM_SET_TARGET: re-anchoring movement leg (fixed-point, value/1000 = actual)
        public int origin_x;               // Center position at start of leg
        public int origin_y;
        public int target_x;               // Center destination
        public int target_y;
        public int speed;                  // Distance per tick (fixed-point)

        // For SWARM_SPLIT / SWARM_MERGE (position-preserving bug MOVES between swarms).
        //   SWARM_SPLIT: swarm_id=parent, new_swarm_id=child, split_count=bugs moved
        //     (parent's highest alive ids -> child ids 0..split_count-1), center_x/y=child seed.
        //   SWARM_MERGE: swarm_id=survivor, new_swarm_id=absorbed, split_count=bugs moved,
        //     new_bug_id_base=survivor ids the moved bugs become.
        public string new_swarm_id;
        public int split_count;
        public int center_x;               // fixed-point ×1000
        public int center_y;
        public int new_bug_id_base;
        public int parent_count;           // SWARM_SPLIT: parent's POST-split count (idempotent apply)

        // FOOD events (ITEM_ROTTED / FOOD_CONSUMED): the deterministic food registry.
        // cell_x/cell_y are WORLD cells; level = remaining food value (0 = gone).
        public string food_id;
        public int level;
    }

    /// <summary>
    /// Influence event broadcast from server (OpCode 71).
    /// </summary>
    [Serializable]
    public class InfluenceBroadcastMessage
    {
        public InfluenceEvent[] events;
    }

    /// <summary>
    /// Deposit one item into a station (OpCode 85, C->S). Server validates acceptance,
    /// capacity, range, and inventory, then raises the fill meter.
    /// </summary>
    [Serializable]
    public class StationDepositMessage
    {
        public int gx;
        public int gy;
        public string item_id;
    }

    /// <summary>
    /// A station's fill meter changed (OpCode 86, S->C). Display-only — bug AI reads the
    /// deterministic FOOD_CONSUMED ledger instead.
    /// </summary>
    [Serializable]
    public class StationUpdateMessage
    {
        public int gx;
        public int gy;
        public int input;    // raw deposits awaiting processing
        public int fill;     // processed compost (the food provider)
        public int capacity;
    }

    /// <summary>
    /// DEV TOOL (OpCode 87, C->S): live-override a species' ecology parameters on the server
    /// (foraging duty cycle, feed/breed rates, consumption) — tuned from the F6 debug panel.
    /// </summary>
    [Serializable]
    public class EcologyTuningMessage
    {
        public string species_id;
        public float forage_chance;
        public int forage_mode_min_ticks;
        public int forage_mode_max_ticks;
        public float feed_amount;
        public float breed_amount;
        public float satiation_decay;
        public float consume_rate;
        public float reproduce_cooldown;
    }

    /// <summary>
    /// Zone authority message from server (OpCode 76).
    /// Includes bootstrap tick + watermark for first client.
    /// </summary>
    [Serializable]
    public class ZoneAuthorityMessage
    {
        public string zone_id;
        public string authority_id;
        public long authoritative_tick;  // Bootstrap tick for first client
        public long last_event_seq;      // FIX #7: Initial watermark for bootstrap
    }

    /// <summary>
    /// Tick frontier broadcast from server (OpCode 78).
    /// Server publishes this EVERY tick (10Hz) AFTER broadcasting all events.
    /// CRITICAL: Server must broadcast events BEFORE frontier to ensure safety.
    /// </summary>
    [Serializable]
    public class ZoneTickBroadcastMessage
    {
        public string zone_id;
        public long authoritative_tick;  // Client may simulate up to (but not beyond) this
        public long last_event_seq;      // FIX #7: Watermark - all events with seq <= this are finalized
        public string authority_id;      // Current zone authority (for late authority setup)
    }

    /// <summary>
    /// Zone handoff watermark from server (OpCode 73).
    /// Sent after LateJoinSnapshot to confirm "no undisclosed events <= EndTick".
    /// Client can go LIVE immediately after receiving this.
    /// </summary>
    [Serializable]
    public class ZoneHandoffMessage
    {
        public string zone_id;
        public long live_start_tick;  // T_end + 1: first tick client is live
        public long last_event_seq;   // Watermark at handoff time
    }

    /// <summary>
    /// Zone snapshot from authority client (OpCode 75).
    /// </summary>
    [Serializable]
    public class ZoneSnapshotMessage
    {
        public string zone_id;
        public long snapshot_tick;
        public long snapshot_last_event_seq; // Last applied seq included in snapshot state
        public SwarmSnapshotData[] swarms;
        public string state_hash;
    }

    /// <summary>
    /// Zone hash from client for validation (OpCode 77).
    /// </summary>
    [Serializable]
    public class ZoneHashMessage
    {
        public string zone_id;
        public long tick;
        public string state_hash;
    }

    /// <summary>
    /// Player cell position data for late join sync.
    /// This is snapshot STATE, not an event.
    /// </summary>
    [Serializable]
    public class PlayerCellData
    {
        public string player_id;
        public int cell_x;
        public int cell_y;
    }

    /// <summary>
    /// Late join snapshot from server (OpCode 72).
    /// Contains fixed tick range for deterministic replay.
    /// </summary>
    [Serializable]
    public class LateJoinSnapshotMessage
    {
        public string zone_id;
        public long world_seed;
        public long snapshot_tick;             // T_snapshot (fixed)
        public long end_tick;                  // T_end (fixed)
        public long snapshot_last_event_seq;   // Last seq baked into snapshot state
        public long end_last_event_seq;        // Current watermark at end_tick
        public SwarmSnapshotData[] swarms;     // Bug state from authority
        public SwarmData[] swarm_metadata;     // Swarm metadata for creating visuals before replay
        public InfluenceEvent[] influence_log; // Events in (snapshot_last_seq, end_last_seq]
        public string authority_id;
        public PlayerCellData[] player_cells;  // Current player positions (state, not events)
    }
}
