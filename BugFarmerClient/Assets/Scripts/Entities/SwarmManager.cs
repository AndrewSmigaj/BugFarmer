using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Nakama;
using UnityEngine;
using BugFarmer.Bugs;
using BugFarmer.Networking;
using BugFarmer.Util;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Result of detecting bugs at a position from a single swarm.
    /// Contains bug IDs for deterministic removal across all clients.
    /// </summary>
    public struct CatchResult
    {
        public string swarmId;
        public int[] bugIds;
    }

    /// <summary>
    /// Cached snapshot waiting for swarm creation.
    /// Includes tick for catch-up calculation.
    /// </summary>
    public struct PendingSnapshot
    {
        public BugSampleData[] Bugs;
        public long SnapshotTick;
    }

    /// <summary>
    /// Manages swarm visuals based on server updates.
    /// Singleton that subscribes to WorldManager.OnMatchData for OpCode 20.
    /// IMPORTANT: Waits for WorldSeed before spawning swarms to ensure determinism.
    /// </summary>
    public class SwarmManager : MonoBehaviour
    {
        public static SwarmManager Instance { get; private set; }

        private readonly Dictionary<string, SwarmVisual> _swarms = new();

        // Pending swarm data waiting for WorldSeed initialization
        private SwarmUpdateMessage _pendingUpdate;
        private bool _hasPendingUpdate;

        // Pending snapshots waiting for swarm creation (race condition fix)
        private readonly Dictionary<string, PendingSnapshot> _pendingSnapshots = new();

        // ==========================================================================
        // TICK FRONTIER ARCHITECTURE
        // ==========================================================================
        // "Clients simulate continuously, but never invent inputs.
        //  All non-determinism is resolved by the server before simulation occurs."
        //
        // The ledger is authoritative decisions (events), not bug positions.
        // Bug positions are derived: state(t+1) = F(state(t), authoritative_inputs(t))
        // ==========================================================================

        /// <summary>
        /// SwarmManager owns THE ONE simulation tick. SwarmVisual never advances time.
        /// Meaning: "I have simulated through this tick already"
        /// </summary>
        private long _simulationTick;

        /// <summary>
        /// Server's authoritative tick frontier.
        /// Meaning: "All authoritative inputs/events for ticks <= this are finalized and broadcast."
        /// Client may ONLY simulate while SimulationTick < AuthoritativeTick.
        /// </summary>
        private long _authoritativeTick;

        /// <summary>
        /// State machine: JOINING → REPLAYING → HANDSHAKE_WAIT → LIVE
        /// </summary>
        private enum SyncState { Joining, Replaying, HandshakeWait, Live }
        private SyncState _syncState = SyncState.Joining;

        // Time accumulator for LIVE mode ticking
        private const float TickRate = 10f;
        private const float SecondsPerTick = 1f / TickRate;
        private float _tickAccumulator;

        // === Event Inbox (FIX #1: No SortedSet - it silently drops duplicates!) ===
        // Use Dictionary for dedup + List for ordered processing
        private readonly Dictionary<long, InfluenceEvent> _inboxBySeq = new();  // seq → event (dedup)
        private readonly List<InfluenceEvent> _pendingEvents = new();            // sorted by (tick, seq)
        private bool _pendingEventsDirty = false;

        /// <summary>
        /// Track last applied seq for monotonicity validation + bounded memory (FIX #6).
        /// </summary>
        private long _lastAppliedSeq = -1;

        /// <summary>
        /// Track last received seq for watermark check (FIX #7).
        /// </summary>
        private long _lastReceivedSeq = -1;

        /// <summary>
        /// Watermark from frontier - all events with seq <= this are finalized (FIX #7).
        /// </summary>
        private long _frontierWatermark = -1;

        // Authority state
        private bool _isAuthority;
        private string _currentZoneId;
        private Coroutine _snapshotCoroutine;
        private const float SnapshotInterval = 10f;

        private void Awake()
        {
            Instance = this;

            // Initialize file logger
            DebugFileLogger.Initialize();
            DebugFileLogger.Log("[SwarmManager] Awake - debug logging started");

            // Ensure InfluenceManager exists (required for tick frontier architecture)
            if (InfluenceManager.Instance == null)
            {
                var go = new GameObject("InfluenceManager");
                go.AddComponent<InfluenceManager>();
                Debug.Log("[SwarmManager] Auto-created InfluenceManager");
            }
        }

        private void Start()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData += HandleMatchData;
                Debug.Log("[SwarmManager] Subscribed to WorldManager.OnMatchData");
            }
            else
            {
                Debug.LogError("[SwarmManager] WorldManager.Instance is null! Cannot subscribe to match data.");
            }
        }

        // Debug: track last logged state to avoid spam
        private SyncState _lastLoggedState = SyncState.Joining;
        private long _lastLoggedTick = -1;
        private bool _loggedInitialState = false;

        private void Update()
        {
            // Debug: one-time log of initial state
            if (!_loggedInitialState)
            {
                Debug.Log($"[SwarmManager] Initial state: syncState={_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}");
                _loggedInitialState = true;
            }

            // Handle pending swarm data (existing logic)
            if (_hasPendingUpdate && WorldSeedProvider.Instance?.IsInitialized == true)
            {
                Debug.Log($"[SwarmManager] WorldSeed ready ({WorldSeedProvider.Instance.WorldSeed}), spawning {_pendingUpdate.swarms.Length} pending swarms");
                ProcessSwarmUpdate(_pendingUpdate);
                _hasPendingUpdate = false;
                _pendingUpdate = null;
            }

            // Debug: log state changes
            if (_syncState != _lastLoggedState)
            {
                Debug.Log($"[SwarmManager] State change: {_lastLoggedState} -> {_syncState}");
                _lastLoggedState = _syncState;
            }

            // Only advance ticks in LIVE state
            // NOTE: HANDSHAKE_WAIT is a LOGIC gate, not a NETWORK gate.
            // Messages still arrive and update frontier/watermark/inbox during wait.
            if (_syncState != SyncState.Live)
                return;

            // CRITICAL: Tick Frontier Gate with Watermark Check (FIX #7)
            // Client may ONLY advance when:
            // 1. SimulationTick < AuthoritativeTick  (frontier check)
            // 2. _lastReceivedSeq >= _frontierWatermark  (watermark check - all events received)
            _tickAccumulator += Time.deltaTime;
            bool canAdvance = _simulationTick < _authoritativeTick
                           && _lastReceivedSeq >= _frontierWatermark;

            // Debug: log gate conditions (also to file for debugging)
            if (_simulationTick != _lastLoggedTick || Time.frameCount % 300 == 0)
            {
                var gateMsg = $"[SwarmManager] Tick gate: state={_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}, lastSeq={_lastReceivedSeq}, watermark={_frontierWatermark}, canAdvance={canAdvance}";
                Debug.Log(gateMsg);
                DebugFileLogger.Log(gateMsg);
                _lastLoggedTick = _simulationTick;
            }

            while (_tickAccumulator >= SecondsPerTick && canAdvance)
            {
                AdvanceOneTick();
                _tickAccumulator -= SecondsPerTick;
                // Re-check after each tick
                canAdvance = _simulationTick < _authoritativeTick
                          && _lastReceivedSeq >= _frontierWatermark;
            }

            // Cap accumulator if we're gated (don't let it grow unbounded)
            if (!canAdvance)
            {
                _tickAccumulator = Mathf.Min(_tickAccumulator, SecondsPerTick);
            }

            // Visual interpolation (read-only) - always runs in LIVE
            float t = _tickAccumulator / SecondsPerTick;
            InterpolateAllSwarms(t);
        }

        // ==========================================================================
        // EVENT INBOX METHODS
        // ==========================================================================

        /// <summary>
        /// Add event to inbox with duplicate detection.
        /// FIX #3: Explicit duplicate handling rules.
        /// </summary>
        private void EnqueueEvent(InfluenceEvent evt)
        {
            // Check if already applied (duplicate-after-apply)
            if (evt.seq <= _lastAppliedSeq)
            {
                Debug.LogWarning($"[SwarmManager] Duplicate event after apply: seq={evt.seq} (lastApplied={_lastAppliedSeq})");
                return; // OK to ignore, but log warning
            }

            // Check if already in inbox (duplicate-before-apply)
            if (_inboxBySeq.ContainsKey(evt.seq))
            {
                Debug.LogError($"[SwarmManager] DUPLICATE EVENT BEFORE APPLY: seq={evt.seq} - protocol bug!");
                return; // ERROR condition - should not happen with reliable transport
            }

            // Add to inbox
            _inboxBySeq[evt.seq] = evt;
            _pendingEvents.Add(evt);
            _pendingEventsDirty = true;

            // Track last received seq for watermark check (FIX #7)
            if (evt.seq > _lastReceivedSeq)
            {
                _lastReceivedSeq = evt.seq;
            }
        }

        /// <summary>
        /// Get sorted pending events for processing.
        /// </summary>
        private IEnumerable<InfluenceEvent> GetSortedPendingEvents()
        {
            if (_pendingEventsDirty)
            {
                _pendingEvents.Sort((a, b) => {
                    int tickCmp = a.tick.CompareTo(b.tick);
                    if (tickCmp != 0) return tickCmp;
                    return a.seq.CompareTo(b.seq);
                });
                _pendingEventsDirty = false;
            }
            return _pendingEvents;
        }

        // ==========================================================================
        // TICK ADVANCEMENT METHODS
        // ==========================================================================

        /// <summary>
        /// Advance simulation by one tick.
        /// INVARIANT: Must only be called when SimulationTick < AuthoritativeTick
        /// FIX #2: Uses deterministic iteration order everywhere.
        /// </summary>
        private void AdvanceOneTick()
        {
            // 1. Process events for the tick we're LEAVING (end-of-tick semantics)
            // Events stamped tick=T are applied AFTER simulating T, BEFORE simulating T+1
            // This ensures effects are visible starting at tick T+1
            ProcessEventsForTick(_simulationTick);

            // 2. Increment tick - now entering the new tick
            _simulationTick++;

            // 3. Get player targets from InfluenceManager (deterministic, sorted by playerId)
            // CRITICAL: Bug AI reads from InfluenceManager, NEVER from transforms!
            // NOTE: This now reflects events we just applied in step 1
            var players = GetDeterministicPlayerTargets();

            // Debug: log tick advancement with total bug count (only every 50 ticks to reduce spam)
            if (_simulationTick % 50 == 0)
            {
                int totalBugs = 0;
                foreach (var swarm in _swarms.Values)
                    totalBugs += swarm.Count;
                var msg = $"[SwarmManager] Tick {_simulationTick}: {_swarms.Count} swarms, {totalBugs} total bugs, {players.Count} players";
                Debug.Log(msg);
                DebugFileLogger.Log(msg);
            }

            // 4. Simulate all bugs for the NEW tick
            // FIX #2: MUST iterate in deterministic order (sorted by swarmId)
            foreach (var swarmId in _swarms.Keys.OrderBy(id => id))
            {
                _swarms[swarmId].SimulateTick(_simulationTick, players);
            }
        }

        /// <summary>
        /// Process all events from inbox that have tick == targetTick.
        /// Events are processed in seq order.
        /// FIX #4: Old event not applied triggers resync (not just log).
        /// </summary>
        private void ProcessEventsForTick(long targetTick)
        {
            var toRemove = new List<long>();

            foreach (var evt in GetSortedPendingEvents())
            {
                if (evt.tick > targetTick)
                    break; // No more events for this tick

                if (evt.tick < targetTick)
                {
                    // FIX #4: Old event that should have been applied - PROTOCOL VIOLATION
                    Debug.LogError($"[SwarmManager] PROTOCOL VIOLATION: Old event not applied! tick={evt.tick}, seq={evt.seq}, type={evt.type}");
                    Debug.LogError($"[SwarmManager] Current SimulationTick={_simulationTick}, targetTick={targetTick}");
                    RequestResync();
                    return;
                }

                // Apply event
                ApplyInfluenceEvent(evt);
                _lastAppliedSeq = evt.seq;
                toRemove.Add(evt.seq);
            }

            // Remove processed events from inbox
            foreach (var seq in toRemove)
            {
                _inboxBySeq.Remove(seq);
                _pendingEvents.RemoveAll(e => e.seq == seq);
            }
        }

        private void ApplyInfluenceEvent(InfluenceEvent evt)
        {
            InfluenceManager.Instance?.ProcessInfluenceEvent(evt);
        }

        /// <summary>
        /// FIX #2: Returns player targets in deterministic order (sorted by playerId).
        /// CRITICAL: Reads from InfluenceManager (server events), NOT from transforms!
        /// </summary>
        private List<PlayerTarget> GetDeterministicPlayerTargets()
        {
            var targets = new List<PlayerTarget>();

            if (InfluenceManager.Instance != null)
            {
                foreach (var (playerId, cellX, cellY) in InfluenceManager.Instance.GetPlayerCells()
                    .OrderBy(p => p.playerId))
                {
                    targets.Add(new PlayerTarget
                    {
                        PlayerId = playerId,
                        Position = new FixedPoint2(
                            new FixedPoint { Value = cellX * FixedPoint.Scale },
                            new FixedPoint { Value = cellY * FixedPoint.Scale }
                        )
                    });
                }
            }

            return targets;
        }

        /// <summary>
        /// Interpolate all swarms for visual smoothing.
        /// INVARIANT: Visual code MUST NOT mutate simulation state.
        /// </summary>
        private void InterpolateAllSwarms(float t)
        {
            foreach (var swarmId in _swarms.Keys.OrderBy(id => id))
            {
                _swarms[swarmId].Interpolate(t);
            }
        }

        /// <summary>
        /// FIX #4: Request resync when protocol violation detected.
        /// </summary>
        private void RequestResync()
        {
            Debug.LogError($"[SwarmManager] Requesting resync due to protocol violation");
            _syncState = SyncState.Joining;
            _inboxBySeq.Clear();
            _pendingEvents.Clear();
            _lastAppliedSeq = -1;
            _lastReceivedSeq = -1;
            _frontierWatermark = -1;

            // Request late join snapshot from server
            RequestFullSnapshot(0, 0); // TODO: Track current chunk
        }

        /// <summary>
        /// Replay from current SimulationTick to targetTick.
        /// Uses same AdvanceOneTick() as LIVE mode - unified code path.
        /// </summary>
        private void ReplayToTick(long targetTick)
        {
            Debug.Log($"[SwarmManager] Replaying from tick {_simulationTick} to {targetTick}");

            while (_simulationTick < targetTick)
            {
                AdvanceOneTick();
            }

            Debug.Log($"[SwarmManager] Replay complete at tick {_simulationTick}");
        }

        // ==========================================================================
        // MESSAGE HANDLERS
        // ==========================================================================

        private void HandleMatchData(IMatchState state)
        {
            // Debug: log zone-related opcodes
            if (state.OpCode == OpCodes.ZoneAuthority ||
                state.OpCode == OpCodes.ZoneTickBroadcast ||
                state.OpCode == OpCodes.ZoneHandoff ||
                state.OpCode == OpCodes.LateJoinSnapshot ||
                state.OpCode == OpCodes.InfluenceBroadcast)
            {
                Debug.Log($"[SwarmManager] Received OpCode {state.OpCode}");
            }

            switch (state.OpCode)
            {
                case OpCodes.SwarmUpdate:
                    HandleSwarmUpdate(state);
                    break;
                case OpCodes.BugCaught:
                    HandleBugCaught(state);
                    break;
                // Bug sync (late joiner + drift detection)
                case OpCodes.RequestSample:
                    HandleSampleRequest(state);
                    break;
                case OpCodes.SampleBroadcast:
                    HandleSampleBroadcast(state);
                    break;
                case OpCodes.FullSnapshot:
                    HandleFullSnapshot(state);
                    break;
                // Zone authority + late join
                case OpCodes.InfluenceBroadcast:
                    HandleInfluenceBroadcast(state);
                    break;
                case OpCodes.LateJoinSnapshot:
                    HandleLateJoinSnapshot(state);
                    break;
                case OpCodes.ZoneHandoff:
                    HandleZoneHandoff(state);
                    break;
                case OpCodes.ZoneAuthority:
                    HandleZoneAuthority(state);
                    break;
                case OpCodes.ZoneTickBroadcast:
                    HandleZoneTickBroadcast(state);
                    break;
                // Inventory messages (26, 37, 38) handled by InventoryManager
            }
        }

        private void HandleSwarmUpdate(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var update = JsonUtility.FromJson<SwarmUpdateMessage>(json);

            if (update?.swarms == null)
            {
                return;
            }

            // If WorldSeed not ready yet, cache this update and wait
            if (WorldSeedProvider.Instance?.IsInitialized != true)
            {
                Debug.Log($"[SwarmManager] WorldSeed not ready, caching {update.swarms.Length} swarms");
                _pendingUpdate = update;
                _hasPendingUpdate = true;
                return;
            }

            ProcessSwarmUpdate(update);
        }

        private void ProcessSwarmUpdate(SwarmUpdateMessage update)
        {
            // Track which swarms we received this tick
            var receivedIds = new HashSet<string>();

            foreach (var data in update.swarms)
            {
                receivedIds.Add(data.id);

                if (_swarms.TryGetValue(data.id, out var existing))
                {
                    // Update existing swarm
                    existing.UpdateFromServer(data);
                }
                else
                {
                    // Spawn new swarm visual
                    SpawnSwarm(data, update.tick);
                }
            }

            // Remove swarms not in this update (merged/despawned)
            var toRemove = _swarms.Keys.Where(id => !receivedIds.Contains(id)).ToList();
            foreach (var id in toRemove)
            {
                if (_swarms.TryGetValue(id, out var swarm))
                {
                    swarm.Cleanup();
                    Destroy(swarm.gameObject);
                }
                _swarms.Remove(id);
            }
        }

        private void HandleBugCaught(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<BugCaughtMessage>(json);

            if (msg == null) return;

            // Skip own catch - already removed bugs optimistically
            var localUserId = WorldManager.Instance?.Self?.UserId;
            if (!string.IsNullOrEmpty(localUserId) && msg.catcher_id == localUserId)
                return;

            // Other players: remove by ID (deterministic - all clients see same bugs disappear)
            var swarm = GetSwarm(msg.swarm_id);
            if (swarm != null)
            {
                swarm.RemoveBugsById(msg.bug_ids);
                swarm.ShowCatchAnimation(new Vector2(msg.x, msg.y), msg.catcher_id);
            }
        }

        // === Bug Sync Handlers (Late Joiner + Drift Detection) ===

        /// <summary>
        /// Handle server request for bug positions (OpCode 61).
        /// Respond with positions for the requested bugs.
        /// </summary>
        private void HandleSampleRequest(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<SampleRequestMessage>(json);
            if (msg?.samples == null) return;

            // Gather positions for all requested bugs
            var samples = new List<BugSampleData>();
            foreach (var query in msg.samples)
            {
                var swarm = GetSwarm(query.swarm_id);
                if (swarm != null)
                {
                    var positions = swarm.GetBugPositions(new[] { query.bug_id });
                    samples.AddRange(positions);
                }
            }

            // Send response back to server
            var response = new SampleResponseMessage
            {
                chunk_x = msg.chunk_x,
                chunk_y = msg.chunk_y,
                tick = msg.tick,
                samples = samples.ToArray()
            };
            SendToServer(OpCodes.SampleResponse, response);
        }

        /// <summary>
        /// Handle server broadcast of sample positions (OpCode 63).
        /// Compare local positions and request snapshot if drift exceeds threshold.
        /// </summary>
        private void HandleSampleBroadcast(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<SampleResponseMessage>(json);
            if (msg?.samples == null) return;

            float maxDrift = 0f;
            foreach (var sample in msg.samples)
            {
                var swarm = GetSwarm(sample.swarm_id);
                if (swarm != null)
                {
                    var localPositions = swarm.GetBugPositions(new[] { sample.bug_id });
                    if (localPositions.Length > 0)
                    {
                        // Calculate drift in world units (fixed-point / 1000)
                        float dx = (localPositions[0].x - sample.x) / 1000f;
                        float dy = (localPositions[0].y - sample.y) / 1000f;
                        float drift = Mathf.Sqrt(dx * dx + dy * dy);
                        maxDrift = Mathf.Max(maxDrift, drift);
                    }
                }
            }

            // If drift exceeds 0.5 blocks, request full snapshot
            if (maxDrift >= 0.5f)
            {
                Debug.Log($"[SwarmManager] Drift detected ({maxDrift:F2} blocks), requesting snapshot for chunk {msg.chunk_x},{msg.chunk_y}");
                RequestFullSnapshot(msg.chunk_x, msg.chunk_y);
            }
        }

        /// <summary>
        /// Handle full snapshot from server (OpCode 67).
        /// Apply positions to sync bugs with authoritative state.
        /// Includes catch-up simulation to reach current tick.
        /// Caches snapshots for swarms that don't exist yet (race condition).
        /// </summary>
        private void HandleFullSnapshot(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<FullSnapshotMessage>(json);
            if (msg?.swarms == null) return;

            Debug.Log($"[SwarmManager] Received snapshot for chunk {msg.chunk_x},{msg.chunk_y} with {msg.swarms.Length} swarms at tick {msg.tick}");

            foreach (var swarmData in msg.swarms)
            {
                if (swarmData.bugs == null) continue;

                var swarm = GetSwarm(swarmData.swarm_id);
                if (swarm != null)
                {
                    swarm.ApplySnapshot(swarmData.bugs);
                    // TODO: Drift correction catch-up needs redesign for tick frontier architecture
                    // The old CatchUpTicks was removed. Drift correction should:
                    // 1. Set _simulationTick = msg.tick
                    // 2. Replay to _authoritativeTick using AdvanceOneTick()
                    // For now, just apply snapshot and let normal tick advancement continue
                }
                else
                {
                    // Swarm doesn't exist yet - cache for when it's created
                    Debug.Log($"[SwarmManager] Caching snapshot for swarm {swarmData.swarm_id} ({swarmData.bugs.Length} bugs)");
                    _pendingSnapshots[swarmData.swarm_id] = new PendingSnapshot
                    {
                        Bugs = swarmData.bugs,
                        SnapshotTick = msg.tick
                    };
                }
            }
        }

        // NOTE: GetCurrentPlayerTargets() REMOVED - use GetDeterministicPlayerTargets() instead
        // which reads from InfluenceManager (server-authored) for deterministic simulation.

        /// <summary>
        /// Request full snapshot when drift detected or as late joiner.
        /// </summary>
        private void RequestFullSnapshot(int chunkX, int chunkY)
        {
            var request = new SnapshotRequestMessage
            {
                chunk_x = chunkX,
                chunk_y = chunkY
            };
            SendToServer(OpCodes.RequestSnapshot, request);
        }

        /// <summary>
        /// Send a message to the server via the match socket.
        /// </summary>
        private void SendToServer(int opCode, object message)
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return;

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return;

            var json = JsonUtility.ToJson(message);
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, opCode, json);
        }

        private void SpawnSwarm(SwarmData data, long serverTick)
        {
            var obj = new GameObject($"Swarm_{data.id}");
            var visual = obj.AddComponent<SwarmVisual>();
            visual.Initialize(data, serverTick);
            _swarms[data.id] = visual;

            // Check for pending snapshot (late joiner race condition fix)
            if (_pendingSnapshots.TryGetValue(data.id, out var pending))
            {
                Debug.Log($"[SwarmManager] Applying cached snapshot to swarm {data.id} ({pending.Bugs.Length} bugs)");

                visual.ApplySnapshot(pending.Bugs);
                // NOTE: Catch-up is handled by SwarmManager's tick advancement loop
                // The swarm will naturally catch up as AdvanceOneTick() processes ticks

                _pendingSnapshots.Remove(data.id);
            }
        }

        // ==========================================================================
        // ZONE AUTHORITY + LATE JOIN HANDLERS
        // ==========================================================================

        /// <summary>
        /// Handle influence events from server (OpCode 71).
        /// Events go to inbox, processed at end-of-tick.
        /// NOTE: Runs in ALL states (not just LIVE) - this is intentional.
        /// </summary>
        private void HandleInfluenceBroadcast(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<InfluenceBroadcastMessage>(json);
            if (msg?.events == null) return;

            foreach (var evt in msg.events)
            {
                EnqueueEvent(evt);
            }
        }

        /// <summary>
        /// Handle late join snapshot (OpCode 72).
        /// Contains snapshot + influence_log for deterministic replay.
        /// </summary>
        private void HandleLateJoinSnapshot(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<LateJoinSnapshotMessage>(json);
            if (msg == null) return;

            Debug.Log($"[SwarmManager] LateJoinSnapshot: zone={msg.zone_id}, tick range {msg.snapshot_tick} to {msg.end_tick}");

            // Enter REPLAYING state
            _syncState = SyncState.Replaying;
            _inboxBySeq.Clear();
            _pendingEvents.Clear();
            _pendingEventsDirty = false;
            _currentZoneId = msg.zone_id;

            // Initialize seed and ticks
            WorldSeedProvider.Instance?.Initialize(msg.world_seed, msg.snapshot_tick);
            _simulationTick = msg.snapshot_tick;
            _authoritativeTick = msg.end_tick;  // During replay, frontier is end_tick

            var localUserId = WorldManager.Instance?.Self?.UserId;
            _isAuthority = (msg.authority_id == localUserId);

            // Clear player cells for fresh replay
            InfluenceManager.Instance?.ClearPlayerCells();

            // Apply bug snapshots
            if (msg.swarms != null)
            {
                foreach (var swarmData in msg.swarms)
                {
                    if (swarmData.bugs == null) continue;
                    var swarm = GetSwarm(swarmData.swarm_id);
                    if (swarm != null)
                    {
                        swarm.ApplySnapshot(swarmData.bugs);
                    }
                    else
                    {
                        _pendingSnapshots[swarmData.swarm_id] = new PendingSnapshot
                        {
                            Bugs = swarmData.bugs,
                            SnapshotTick = msg.snapshot_tick
                        };
                    }
                }
            }

            // Reset seq tracking for replay
            _lastAppliedSeq = -1;
            _lastReceivedSeq = -1;
            _frontierWatermark = -1;  // Replay bypasses frontier gating

            // Add influence log events to inbox
            if (msg.influence_log != null)
            {
                foreach (var evt in msg.influence_log)
                {
                    EnqueueEvent(evt);
                }
            }

            // Replay to end_tick
            ReplayToTick(msg.end_tick);

            // Snap visuals after replay
            foreach (var swarm in _swarms.Values)
            {
                swarm.SyncAllBugPositions();
            }

            // Enter HANDSHAKE_WAIT
            _syncState = SyncState.HandshakeWait;
            Debug.Log($"[SwarmManager] Replay complete at tick {_simulationTick}, waiting for handshake");
        }

        /// <summary>
        /// Handle zone handoff (OpCode 73).
        /// Sent after LateJoinSnapshot to confirm transition to LIVE.
        /// </summary>
        private void HandleZoneHandoff(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ZoneHandoffMessage>(json);
            if (msg == null) return;

            Debug.Log($"[SwarmManager] ZoneHandoff received: live from tick {msg.live_start_tick}");

            if (_syncState == SyncState.HandshakeWait)
            {
                _authoritativeTick = msg.live_start_tick;
                TransitionToLive();
            }
        }

        /// <summary>
        /// Handle zone authority assignment (OpCode 76).
        /// First client goes directly to LIVE; includes bootstrap tick.
        /// NOTE: Runs in ALL states - this is intentional.
        /// </summary>
        private void HandleZoneAuthority(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ZoneAuthorityMessage>(json);
            if (msg == null)
            {
                Debug.LogWarning("[SwarmManager] ZoneAuthority: failed to parse message");
                return;
            }

            var localUserId = WorldManager.Instance?.Self?.UserId;
            bool wasAuthority = _isAuthority;
            _isAuthority = (msg.authority_id == localUserId);
            _currentZoneId = msg.zone_id;

            Debug.Log($"[SwarmManager] ZoneAuthority: authority={msg.authority_id}, tick={msg.authoritative_tick}, seq={msg.last_event_seq}, localUser={localUserId}, isLocalAuthority={_isAuthority}, currentState={_syncState}");

            // First client joins - go directly to LIVE
            if (_syncState == SyncState.Joining)
            {
                _authoritativeTick = msg.authoritative_tick;
                _simulationTick = msg.authoritative_tick;  // "I have simulated through this tick"
                _frontierWatermark = msg.last_event_seq;   // FIX #7: Initial watermark
                _lastReceivedSeq = msg.last_event_seq;     // FIX #7: Assume all prior events received
                TransitionToLive();
            }

            // Handle authority handoff
            if (_isAuthority && !wasAuthority)
            {
                StartAuthoritySnapshots();
            }
            else if (!_isAuthority && wasAuthority)
            {
                StopAuthoritySnapshots();
            }
        }

        /// <summary>
        /// Handle tick frontier broadcast (OpCode 78).
        /// Server publishes this EVERY tick AFTER all events for that tick.
        /// NOTE: Runs in ALL states - this is intentional (updates frontier during HANDSHAKE_WAIT).
        /// </summary>
        private void HandleZoneTickBroadcast(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ZoneTickBroadcastMessage>(json);
            if (msg == null)
            {
                Debug.LogWarning("[SwarmManager] ZoneTickBroadcast: failed to parse message");
                return;
            }

            // Update frontier AND watermark (FIX #7)
            if (msg.authoritative_tick > _authoritativeTick)
            {
                Debug.Log($"[SwarmManager] ZoneTickBroadcast: frontier {_authoritativeTick} -> {msg.authoritative_tick}, watermark={msg.last_event_seq}");
                _authoritativeTick = msg.authoritative_tick;
                _frontierWatermark = msg.last_event_seq;
            }
        }

        /// <summary>
        /// Transition to LIVE state.
        /// </summary>
        private void TransitionToLive()
        {
            _syncState = SyncState.Live;
            _tickAccumulator = 0f;

            Debug.Log($"[SwarmManager] Entered LIVE at tick {_simulationTick}, frontier at {_authoritativeTick}");

            if (_isAuthority)
            {
                StartAuthoritySnapshots();
            }
        }

        /// <summary>
        /// Start periodic snapshot sending (authority duty).
        /// </summary>
        private void StartAuthoritySnapshots()
        {
            if (_snapshotCoroutine != null)
            {
                StopCoroutine(_snapshotCoroutine);
            }
            _snapshotCoroutine = StartCoroutine(AuthoritySnapshotLoop());
            Debug.Log($"[SwarmManager] Started authority snapshots for zone {_currentZoneId}");
        }

        /// <summary>
        /// Stop periodic snapshot sending.
        /// </summary>
        private void StopAuthoritySnapshots()
        {
            if (_snapshotCoroutine != null)
            {
                StopCoroutine(_snapshotCoroutine);
                _snapshotCoroutine = null;
            }
            Debug.Log($"[SwarmManager] Stopped authority snapshots");
        }

        /// <summary>
        /// Authority sends periodic snapshots for late joiners.
        /// </summary>
        private IEnumerator AuthoritySnapshotLoop()
        {
            while (_isAuthority)
            {
                yield return new WaitForSeconds(SnapshotInterval);

                if (!_isAuthority) break;

                // Build and send snapshot
                var swarmSnapshots = new List<SwarmSnapshotData>();
                foreach (var kvp in _swarms)
                {
                    var bugData = kvp.Value.GetBugPositions(null); // Get all bugs
                    if (bugData.Length > 0)
                    {
                        swarmSnapshots.Add(new SwarmSnapshotData
                        {
                            swarm_id = kvp.Key,
                            bugs = bugData
                        });
                    }
                }

                var snapshot = new ZoneSnapshotMessage
                {
                    zone_id = _currentZoneId,
                    snapshot_tick = _simulationTick,
                    swarms = swarmSnapshots.ToArray(),
                    state_hash = "" // TODO: Implement state hash
                };

                SendToServer(OpCodes.ZoneSnapshot, snapshot);
                Debug.Log($"[SwarmManager] Sent authority snapshot at tick {_simulationTick}");
            }
        }

        /// <summary>
        /// Get a swarm visual by ID.
        /// </summary>
        public SwarmVisual GetSwarm(string swarmId)
        {
            _swarms.TryGetValue(swarmId, out var swarm);
            return swarm;
        }

        /// <summary>
        /// Get all current swarms.
        /// </summary>
        public IEnumerable<SwarmVisual> GetAllSwarms()
        {
            return _swarms.Values;
        }

        /// <summary>
        /// Get bug IDs at position across all swarms (does NOT remove them).
        /// Used by CatchingController to detect which bugs were clicked.
        /// </summary>
        public List<CatchResult> GetBugsAtPosition(Vector2 worldPosition, float catchRadius)
        {
            var results = new List<CatchResult>();

            foreach (var kvp in _swarms)
            {
                int[] bugIds = kvp.Value.GetBugsInRadius(worldPosition, catchRadius);
                if (bugIds.Length > 0)
                {
                    results.Add(new CatchResult { swarmId = kvp.Key, bugIds = bugIds });
                }
            }

            return results;
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
            }

            // Clean up all swarms
            foreach (var swarm in _swarms.Values)
            {
                swarm.Cleanup();
            }
            _swarms.Clear();
            _pendingSnapshots.Clear();
        }
    }
}
