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
