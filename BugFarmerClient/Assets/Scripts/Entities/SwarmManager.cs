using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Nakama;
using UnityEngine;
using BugFarmer.Bugs;
using BugFarmer.Networking;
using BugFarmer.Util;
using BugFarmer.Tracing;

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
        private const double TickRate = 10.0;
        private const double SecondsPerTick = 1.0 / TickRate;
        private double _tickAccumulator;

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

        // Pending authority check (for race condition where ZoneAuthority arrives before Self is known)
        private string _pendingAuthorityId;
        private long _pendingAuthorityTick;
        private long _pendingAuthoritySeq;

        // Safety net timeouts
        private float _frontierStallTimer;
        private const float FrontierStallTimeout = 5.0f; // Request resync after 5s stuck
        private float _handshakeWaitTimer;
        private const float HandshakeWaitTimeout = 10.0f; // Request resync after 10s in HandshakeWait
        private int _resyncAttempts;
        private const int MaxResyncAttempts = 3;

        // Reception watchdog (observability only): detect when match messages stop arriving while
        // Update() keeps running — the freeze signature. Set in HandleMatchData, checked in Update().
        private float _lastMatchMsgTime = -1f;
        private bool _receptionGapLogged;

        // Trace callback - only invoked when debug overlay is recording
        private Action<long, long, List<BugTrace>, List<PlayerTarget>> _traceCallback;

        // Always-on ring buffer of tick -> ComputeStateHash() for tick-aligned drift checks.
        // The server samples a settled tick (behind the frontier) from every client and compares
        // equal-tick hashes; comparing the SAME tick is what makes the check honest (the old
        // position-sampling scheme compared across mismatched ticks and false-positived).
        private const int HashRingSize = 120; // ~12s at 10Hz - covers drift margin + RTT
        private readonly Queue<long> _hashRingOrder = new();
        private readonly Dictionary<long, long> _hashRing = new();

        private void RecordTickHash(long tick, long hash)
        {
            if (_hashRing.ContainsKey(tick))
            {
                _hashRing[tick] = hash;
                return;
            }
            _hashRing[tick] = hash;
            _hashRingOrder.Enqueue(tick);
            if (_hashRingOrder.Count > HashRingSize)
                _hashRing.Remove(_hashRingOrder.Dequeue());
        }

        /// <summary>Current simulation tick (read-only for external code).</summary>
        public long SimulationTick => _simulationTick;

        /// <summary>Number of active swarms.</summary>
        public int SwarmCount => _swarms.Count;

        /// <summary>Total bugs across all swarms.</summary>
        public int TotalBugCount
        {
            get
            {
                int count = 0;
                foreach (var swarm in _swarms.Values)
                    count += swarm.Count;
                return count;
            }
        }

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
                WorldManager.Instance.OnPlayerLeft += HandlePlayerLeft;
                Debug.Log("[SwarmManager] Subscribed to WorldManager.OnMatchData + OnPlayerLeft");
            }
            else
            {
                Debug.LogError("[SwarmManager] WorldManager.Instance is null! Cannot subscribe to match data.");
            }
        }

        /// <summary>
        /// Clean up InfluenceManager when a player leaves (presence-based safety net).
        /// Server also emits PLAYER_CELL_LEAVE, but this handles the case where the event is lost.
        /// </summary>
        private void HandlePlayerLeft(Nakama.IUserPresence presence)
        {
            InfluenceManager.Instance?.RemovePlayerCell(presence.UserId);
            Debug.Log($"[SwarmManager] Player left: {presence.UserId}, removed from InfluenceManager");
        }

        // Debug: track last logged state to avoid spam
        private SyncState _lastLoggedState = SyncState.Joining;
        private long _lastLoggedTick = -1;
        private bool _lastLoggedCanAdvance = true;
        private bool _loggedInitialState = false;

        private void Update()
        {
            // Debug: one-time log of initial state
            if (!_loggedInitialState)
            {
                Debug.Log($"[SwarmManager] Initial state: syncState={_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}");
                _loggedInitialState = true;
            }

            // Reception watchdog: if match messages stop arriving while Update keeps running, log the
            // gap once at its onset (the freeze signature). Observability only — no behavior change.
            if (_lastMatchMsgTime >= 0f && Time.time - _lastMatchMsgTime > 2f && !_receptionGapLogged)
            {
                _receptionGapLogged = true;
                DebugFileLogger.Log($"[SwarmManager] RECEPTION GAP: no match msg for {Time.time - _lastMatchMsgTime:F1}s, state={_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}, lastSeq={_lastReceivedSeq}");
            }

            // RACE CONDITION FIX: Process pending ZoneAuthority when localUserId becomes available
            // This handles the case where ZoneAuthority arrived before JoinMatchAsync completed
            if (!string.IsNullOrEmpty(_pendingAuthorityId))
            {
                var localUserId = WorldManager.Instance?.Self?.UserId;
                if (!string.IsNullOrEmpty(localUserId))
                {
                    Debug.Log($"[SwarmManager] Processing DEFERRED ZoneAuthority now that localUserId={localUserId} is known");
                    DebugFileLogger.Log($"[SwarmManager] Processing DEFERRED ZoneAuthority: authority={_pendingAuthorityId}, localUserId={localUserId}");
                    ProcessZoneAuthority(_pendingAuthorityId, _pendingAuthorityTick, _pendingAuthoritySeq, _currentZoneId, localUserId);
                    _pendingAuthorityId = null;  // Clear pending - processed
                }
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
            {
                // Safety net: a client stuck in HandshakeWait (handoff lost) auto-resyncs.
                if (_syncState == SyncState.HandshakeWait)
                {
                    _handshakeWaitTimer += Time.deltaTime;
                    if (_handshakeWaitTimer >= HandshakeWaitTimeout && _resyncAttempts < MaxResyncAttempts)
                    {
                        Debug.LogWarning($"[SwarmManager] HandshakeWait exceeded {HandshakeWaitTimeout}s - resyncing (attempt {_resyncAttempts + 1}/{MaxResyncAttempts})");
                        _resyncAttempts++;
                        _handshakeWaitTimer = 0f;
                        RequestResync();
                    }
                }
                else
                {
                    _handshakeWaitTimer = 0f;
                }
                return;
            }

            // Entered LIVE: handshake timer no longer relevant.
            _handshakeWaitTimer = 0f;

            // CRITICAL: Tick Frontier Gate with Watermark Check (FIX #7)
            // Client may ONLY advance when:
            // 1. SimulationTick < AuthoritativeTick  (frontier check)
            // 2. _lastReceivedSeq >= _frontierWatermark  (watermark check - all events received)
            _tickAccumulator += Time.deltaTime;
            bool canAdvance = _simulationTick < _authoritativeTick
                           && HasAllEventsUpTo(_frontierWatermark);

            // Debug: log gate conditions only when important changes occur
            // - Every 50 ticks (~5 sec) for periodic status
            // - When canAdvance changes (stuck/unstuck transition)
            bool shouldLog = (_simulationTick % 50 == 0 && _simulationTick != _lastLoggedTick)
                          || (canAdvance != _lastLoggedCanAdvance);
            if (shouldLog)
            {
                var gateMsg = $"[SwarmManager] Tick gate: state={_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}, lastSeq={_lastReceivedSeq}, watermark={_frontierWatermark}, canAdvance={canAdvance}";
                Debug.Log(gateMsg);
                DebugFileLogger.Log(gateMsg);
                _lastLoggedTick = _simulationTick;
                _lastLoggedCanAdvance = canAdvance;
            }

            while (_tickAccumulator >= SecondsPerTick && canAdvance)
            {
                AdvanceOneTick();
                _tickAccumulator -= SecondsPerTick;
                // Re-check after each tick
                canAdvance = _simulationTick < _authoritativeTick
                          && HasAllEventsUpTo(_frontierWatermark);
            }

            // Cap accumulator if we're gated (don't let it grow unbounded)
            if (!canAdvance)
            {
                _tickAccumulator = System.Math.Min(_tickAccumulator, SecondsPerTick);

                // Safety net: if we stay gated too long (lost event or stalled frontier),
                // auto-resync via the late-join path. Bounded by MaxResyncAttempts.
                _frontierStallTimer += Time.deltaTime;
                if (_frontierStallTimer >= FrontierStallTimeout && _resyncAttempts < MaxResyncAttempts)
                {
                    Debug.LogWarning($"[SwarmManager] Frontier stalled {FrontierStallTimeout}s (simTick={_simulationTick}, authTick={_authoritativeTick}, lastSeq={_lastReceivedSeq}, watermark={_frontierWatermark}) - resyncing (attempt {_resyncAttempts + 1}/{MaxResyncAttempts})");
                    DebugFileLogger.Log($"[SwarmManager] Frontier STALLED {FrontierStallTimeout}s simTick={_simulationTick} authTick={_authoritativeTick} lastSeq={_lastReceivedSeq} watermark={_frontierWatermark} - resync {_resyncAttempts + 1}/{MaxResyncAttempts}");
                    _resyncAttempts++;
                    _frontierStallTimer = 0f;
                    RequestResync();
                    return;
                }
            }
            else
            {
                // Made progress - clear the stall timer.
                _frontierStallTimer = 0f;
            }

            // Visual interpolation (read-only) - always runs in LIVE
            float t = (float)(_tickAccumulator / SecondsPerTick);
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

        /// <summary>
        /// Check if all events from lastApplied+1 through watermark are in inbox.
        /// Prevents race condition when ZoneTickBroadcast arrives before InfluenceBroadcast.
        /// </summary>
        private bool HasAllEventsUpTo(long watermark)
        {
            // Bootstrap: no events required
            if (watermark < 0) return true;

            // Check continuous sequence from lastApplied+1 to watermark
            for (long seq = _lastAppliedSeq + 1; seq <= watermark; seq++)
            {
                if (!_inboxBySeq.ContainsKey(seq))
                    return false;
            }
            return true;
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

            // Record this tick's state hash for tick-aligned drift checks (always on, cheap).
            var hash = ComputeStateHash();
            RecordTickHash(_simulationTick, hash);

            // Invoke trace callback if recording
            if (_traceCallback != null)
            {
                var bugs = CollectBugTraces();
                _traceCallback(_simulationTick, hash, bugs, players);
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
        /// Request a full zone resync (recovery). The frontier system is zone-scoped, so recovery
        /// routes through the proven late-join path: the server responds to OpCode 66 with a
        /// LateJoinSnapshot (OpCode 72), which HandleLateJoinSnapshot replays to the frontier and
        /// transitions back to LIVE. Used for protocol violations, frontier stalls, handshake
        /// timeouts, and large drift. Bounded by MaxResyncAttempts in the Update loop.
        /// </summary>
        private void RequestResync()
        {
            Debug.LogWarning($"[SwarmManager] Requesting zone resync (late-join path)");
            DebugFileLogger.Log($"[SwarmManager] RequestResync -> Joining (from {_syncState}, simTick={_simulationTick}, authTick={_authoritativeTick}, lastSeq={_lastReceivedSeq})");
            _syncState = SyncState.Joining;
            _inboxBySeq.Clear();
            _pendingEvents.Clear();
            _pendingEventsDirty = false;
            _lastAppliedSeq = -1;
            _lastReceivedSeq = -1;
            _frontierWatermark = -1;

            // Zone-wide resync request. Chunk fields are unused; the server resyncs the whole zone.
            SendToServer(OpCodes.RequestSnapshot, new SnapshotRequestMessage());
        }

        /// <summary>
        /// Replay from current SimulationTick to targetTick.
        /// Uses same AdvanceOneTick() as LIVE mode - unified code path.
        /// </summary>
        private void ReplayToTick(long targetTick)
        {
            Debug.Log($"[SwarmManager] Replaying from tick {_simulationTick} to {targetTick}");
            DebugFileLogger.Log($"[SwarmManager] ReplayToTick: from {_simulationTick} to {targetTick}");

            while (_simulationTick < targetTick)
            {
                AdvanceOneTick();
            }

            Debug.Log($"[SwarmManager] Replay complete at tick {_simulationTick}");
            DebugFileLogger.Log($"[SwarmManager] ReplayToTick: complete at {_simulationTick}");
        }

        // ==========================================================================
        // MESSAGE HANDLERS
        // ==========================================================================

        private void HandleMatchData(IMatchState state)
        {
            // Reception watchdog bookkeeping (observability).
            _lastMatchMsgTime = Time.time;
            _receptionGapLogged = false;

            // Debug: log zone-related opcodes
            if (state.OpCode == OpCodes.ZoneAuthority ||
                state.OpCode == OpCodes.ZoneTickBroadcast ||
                state.OpCode == OpCodes.ZoneHandoff ||
                state.OpCode == OpCodes.LateJoinSnapshot ||
                state.OpCode == OpCodes.InfluenceBroadcast)
            {
                var logMsg = $"[SwarmManager] Received OpCode {state.OpCode}";
                Debug.Log(logMsg);
                DebugFileLogger.Log(logMsg);
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
        /// Handle server request for our state hash at a settled tick (OpCode 61).
        /// Respond with ComputeStateHash() at msg.tick from the ring buffer. If that tick is no
        /// longer buffered (e.g. we just resynced), respond with has_hash=false to abstain - the
        /// server then excludes us from the comparison instead of treating us as drifted.
        /// </summary>
        private void HandleSampleRequest(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<SampleRequestMessage>(json);
            if (msg == null) return;

            bool hasHash = _hashRing.TryGetValue(msg.tick, out var hash);
            var response = new SampleResponseMessage
            {
                chunk_x = msg.chunk_x,
                chunk_y = msg.chunk_y,
                tick = msg.tick,
                hash = hasHash ? hash : 0,
                has_hash = hasHash
            };
            SendToServer(OpCodes.SampleResponse, response);
        }

        // NOTE: HandleSampleBroadcast (OpCode 63) REMOVED. Drift comparison is now server-side:
        // the server collects each client's equal-tick hash and resyncs only the minority. The
        // old client-side position compare ran across mismatched ticks and false-positived.

        // NOTE: HandleFullSnapshot (OpCode 67) and RequestFullSnapshot REMOVED. Recovery is now
        // zone-wide via the late-join path (RequestResync -> server LateJoinSnapshot). The old
        // chunk-scoped snapshot couldn't safely rewind the zone-wide simulation tick.

        // NOTE: GetCurrentPlayerTargets() REMOVED - use GetDeterministicPlayerTargets() instead
        // which reads from InfluenceManager (server-authored) for deterministic simulation.

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
                Debug.Log($"[SwarmManager] Applying cached snapshot to swarm {data.id} ({pending.Bugs.Length} bugs from tick {pending.SnapshotTick})");
                DebugFileLogger.Log($"[SwarmManager] Applying cached snapshot to swarm {data.id} ({pending.Bugs.Length} bugs from tick {pending.SnapshotTick})");

                visual.ApplySnapshot(pending.Bugs);
                // NOTE: Catch-up is handled by SwarmManager's tick advancement loop
                // The swarm will naturally catch up as AdvanceOneTick() processes ticks

                _pendingSnapshots.Remove(data.id);
            }
            else
            {
                Debug.Log($"[SwarmManager] No cached snapshot for swarm {data.id}, using SwarmUpdate initialization");
                DebugFileLogger.Log($"[SwarmManager] No cached snapshot for swarm {data.id}, using SwarmUpdate initialization");
            }
        }

        /// <summary>
        /// Create a swarm visual from metadata during late join snapshot processing.
        /// Bug positions will be set separately via ApplySnapshot.
        /// </summary>
        private void SpawnSwarmFromMetadata(SwarmData data, long snapshotTick)
        {
            var obj = new GameObject($"Swarm_{data.id}");
            var visual = obj.AddComponent<SwarmVisual>();
            visual.Initialize(data, snapshotTick);
            _swarms[data.id] = visual;
            // Note: Bug positions will be applied via ApplySnapshot after this
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

            var lateJoinLog = $"[SwarmManager] LateJoinSnapshot: zone={msg.zone_id}, tick range {msg.snapshot_tick} to {msg.end_tick}, authority={msg.authority_id}, player_cells={msg.player_cells?.Length ?? 0}";
            Debug.Log(lateJoinLog);
            DebugFileLogger.Log(lateJoinLog);

            // DEBUG: Tick semantics investigation - log BEFORE applying snapshot_tick
            var beforeLog = $"[LateJoin] Before snapshot: simTick={_simulationTick}";
            Debug.Log(beforeLog);
            DebugFileLogger.Log(beforeLog);

            // Enter REPLAYING state
            DebugFileLogger.Log($"[SwarmManager] STATE -> Replaying (late-join snapshot received, from {_syncState})");
            _syncState = SyncState.Replaying;
            _inboxBySeq.Clear();
            _pendingEvents.Clear();
            _pendingEventsDirty = false;
            _currentZoneId = msg.zone_id;

            // Initialize seed and ticks
            WorldSeedProvider.Instance?.Initialize(msg.world_seed, msg.snapshot_tick);
            _simulationTick = msg.snapshot_tick;
            _authoritativeTick = msg.end_tick;  // During replay, frontier is end_tick

            // DEBUG: Tick semantics investigation - log AFTER applying snapshot_tick
            var afterSnapshotLog = $"[LateJoin] After applying snapshot_tick: simTick={_simulationTick}";
            Debug.Log(afterSnapshotLog);
            DebugFileLogger.Log(afterSnapshotLog);

            var localUserId = WorldManager.Instance?.Self?.UserId;
            _isAuthority = (msg.authority_id == localUserId);

            // Late join = full state replacement. Snapshot player_cells is authoritative.
            // Do not merge with existing state; always clear then rehydrate.
            InfluenceManager.Instance?.ClearPlayerCells();

            // Clear swarm movement legs too. Any leg whose Think falls inside the replay window
            // is re-established when the influence_log replays below. Swarms that are mid-leg
            // (Think happened before snapshot_tick) fall back to their metadata center until the
            // next Think - acceptable, sub-cell, and self-correcting.
            InfluenceManager.Instance?.ClearSwarmLegs();

            // Hydrate player cells from snapshot STATE (not events)
            // This restores the point-in-time player positions at snapshot_tick
            if (msg.player_cells != null)
            {
                foreach (var cell in msg.player_cells)
                {
                    InfluenceManager.Instance?.SetPlayerCell(cell.player_id, cell.cell_x, cell.cell_y);
                }
                Debug.Log($"[SwarmManager] Hydrated {msg.player_cells.Length} player cells from snapshot");
                DebugFileLogger.Log($"[SwarmManager] Hydrated {msg.player_cells.Length} player cells from snapshot");
            }

            // Create swarm visuals from metadata BEFORE applying snapshots
            // This ensures swarms exist when we apply bug positions
            int metadataCount = msg.swarm_metadata?.Length ?? 0;
            Debug.Log($"[SwarmManager] LateJoinSnapshot contains {metadataCount} swarm metadata entries");
            DebugFileLogger.Log($"[SwarmManager] LateJoinSnapshot contains {metadataCount} swarm metadata entries");

            if (msg.swarm_metadata != null)
            {
                foreach (var metadata in msg.swarm_metadata)
                {
                    // Re-hydrate the in-flight movement leg BEFORE replay (legs were cleared above).
                    // Must run for existing swarms too (resync path): otherwise the center freezes
                    // at the metadata fallback until the next Think and diverges from live clients.
                    // Legs that started after snapshot_tick arrive via influence_log replay and
                    // overwrite this at their own tick. Origin/target/speed are fixed-point (×1000),
                    // identical to the originating event, so the closed-form march is bit-identical.
                    if (metadata.has_target)
                    {
                        InfluenceManager.Instance?.SetSwarmLeg(
                            metadata.id,
                            new FixedPoint2(
                                new FixedPoint { Value = metadata.leg_origin_x },
                                new FixedPoint { Value = metadata.leg_origin_y }),
                            new FixedPoint2(
                                new FixedPoint { Value = metadata.leg_target_x },
                                new FixedPoint { Value = metadata.leg_target_y }),
                            new FixedPoint { Value = metadata.leg_speed },
                            metadata.leg_start_tick);
                    }

                    if (_swarms.ContainsKey(metadata.id))
                    {
                        Debug.Log($"[SwarmManager] Swarm {metadata.id} already exists, skipping creation");
                        continue;
                    }

                    Debug.Log($"[SwarmManager] Creating swarm {metadata.id} from metadata before replay");
                    DebugFileLogger.Log($"[SwarmManager] Creating swarm {metadata.id} from metadata before replay");

                    // Create swarm visual using the snapshot_tick (they'll be positioned at snapshot state)
                    SpawnSwarmFromMetadata(metadata, msg.snapshot_tick);
                }
            }

            // Apply bug snapshots - swarms should now exist from metadata above
            int swarmCount = msg.swarms?.Length ?? 0;
            Debug.Log($"[SwarmManager] Applying bug positions for {swarmCount} swarms");
            DebugFileLogger.Log($"[SwarmManager] Applying bug positions for {swarmCount} swarms");

            if (swarmCount == 0)
            {
                Debug.Log("[SwarmManager] Bootstrap snapshot (no swarms yet), will receive via SwarmUpdate");
                DebugFileLogger.Log("[SwarmManager] Bootstrap snapshot (no swarms), bugs will come via SwarmUpdate");
            }
            if (msg.swarms != null)
            {
                foreach (var swarmData in msg.swarms)
                {
                    int bugCount = swarmData.bugs?.Length ?? 0;
                    Debug.Log($"[SwarmManager] Processing swarm {swarmData.swarm_id} with {bugCount} bugs");
                    DebugFileLogger.Log($"[SwarmManager] Processing swarm {swarmData.swarm_id} with {bugCount} bugs");

                    if (swarmData.bugs == null) continue;
                    var swarm = GetSwarm(swarmData.swarm_id);
                    if (swarm != null)
                    {
                        Debug.Log($"[SwarmManager] Swarm {swarmData.swarm_id} exists, applying snapshot directly");
                        DebugFileLogger.Log($"[SwarmManager] Swarm {swarmData.swarm_id} exists, applying snapshot directly");
                        swarm.ApplySnapshot(swarmData.bugs);
                    }
                    else
                    {
                        // This shouldn't happen now that we create from metadata, but keep as fallback
                        Debug.LogWarning($"[SwarmManager] Swarm {swarmData.swarm_id} NOT found (no metadata?), caching {bugCount} bugs for later");
                        DebugFileLogger.Log($"[SwarmManager] Swarm {swarmData.swarm_id} NOT found, caching {bugCount} bugs for later");
                        _pendingSnapshots[swarmData.swarm_id] = new PendingSnapshot
                        {
                            Bugs = swarmData.bugs,
                            SnapshotTick = msg.snapshot_tick
                        };
                    }
                }
            }

            // Set seq baselines from snapshot (spec §4.2: _lastAppliedSeq = snapshot_last_event_seq)
            // THIS IS THE PRIMARY FREEZE FIX: without this, _lastAppliedSeq stays -1 and
            // HasAllEventsUpTo(watermark) looks for events baked into the snapshot that never arrive.
            _lastAppliedSeq = msg.snapshot_last_event_seq;
            _lastReceivedSeq = msg.snapshot_last_event_seq;
            _frontierWatermark = msg.end_last_event_seq;  // Know the target from the start

            // Spec §7.3: APPLY_SNAPSHOT checkpoint
            var applyLog = $"APPLY_SNAPSHOT snapshot_tick={msg.snapshot_tick} snapshot_last_seq={msg.snapshot_last_event_seq} end_tick={msg.end_tick} end_last_seq={msg.end_last_event_seq}";
            Debug.Log($"[SwarmManager] {applyLog}");
            DebugFileLogger.Log($"[SwarmManager] {applyLog}");

            // Spec §7.3: BASELINES checkpoint
            var baselineLog = $"BASELINES simTick={_simulationTick} lastAppliedSeq={_lastAppliedSeq}";
            Debug.Log($"[SwarmManager] {baselineLog}");
            DebugFileLogger.Log($"[SwarmManager] {baselineLog}");

            // Add influence log events to inbox
            if (msg.influence_log != null)
            {
                foreach (var evt in msg.influence_log)
                {
                    EnqueueEvent(evt);
                }
            }

            // Spec §7.3: INBOX checkpoint
            long minSeq = -1, maxSeq = -1;
            if (_inboxBySeq.Count > 0)
            {
                minSeq = long.MaxValue;
                foreach (var seq in _inboxBySeq.Keys)
                {
                    if (seq < minSeq) minSeq = seq;
                    if (seq > maxSeq) maxSeq = seq;
                }
            }
            var inboxLog = $"INBOX minSeq={minSeq} maxSeq={maxSeq} count={_inboxBySeq.Count}";
            Debug.Log($"[SwarmManager] {inboxLog}");
            DebugFileLogger.Log($"[SwarmManager] {inboxLog}");

            // Replay to end_tick
            ReplayToTick(msg.end_tick);

            // Spec §7.3: REPLAY_DONE checkpoint
            var replayHash = ComputeStateHash();
            var replayLog = $"REPLAY_DONE simTick={_simulationTick} lastAppliedSeq={_lastAppliedSeq} hash={replayHash}";
            Debug.Log($"[SwarmManager] {replayLog}");
            DebugFileLogger.Log($"[SwarmManager] {replayLog}");

            // Snap visuals after replay
            foreach (var swarm in _swarms.Values)
            {
                swarm.SyncAllBugPositions();
            }

            // Enter HANDSHAKE_WAIT
            _syncState = SyncState.HandshakeWait;
            Debug.Log($"[SwarmManager] Replay complete at tick {_simulationTick}, waiting for handshake");
            DebugFileLogger.Log($"[SwarmManager] STATE -> HandshakeWait at simTick={_simulationTick} (awaiting ZoneHandoff)");
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

            // Spec §7.3: HANDOFF checkpoint
            var handoffLog = $"HANDOFF live_start_tick={msg.live_start_tick} last_event_seq={msg.last_event_seq} simTick={_simulationTick} state={_syncState}";
            Debug.Log($"[SwarmManager] {handoffLog}");
            DebugFileLogger.Log($"[SwarmManager] {handoffLog}");

            if (_syncState == SyncState.HandshakeWait)
            {
                // Use Math.Max to avoid rolling back values that ZoneTickBroadcast already advanced
                // during HandshakeWait (spec §3.6)
                _authoritativeTick = Math.Max(_authoritativeTick, msg.live_start_tick);
                _frontierWatermark = Math.Max(_frontierWatermark, msg.last_event_seq);
                TransitionToLive();
                DebugFileLogger.Log($"[SwarmManager] Transitioned to LIVE at tick {_simulationTick}, authTick={_authoritativeTick}, watermark={_frontierWatermark}");
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

            // RACE CONDITION FIX: ZoneAuthority may arrive before JoinMatchAsync completes
            // and Self.UserId is populated. Cache the info and process in Update() when ready.
            if (string.IsNullOrEmpty(localUserId))
            {
                _pendingAuthorityId = msg.authority_id;
                _pendingAuthorityTick = msg.authoritative_tick;
                _pendingAuthoritySeq = msg.last_event_seq;
                _currentZoneId = msg.zone_id;
                Debug.LogWarning($"[SwarmManager] ZoneAuthority received but localUserId not yet known - caching. authority={msg.authority_id}, tick={msg.authoritative_tick}");
                DebugFileLogger.Log($"[SwarmManager] ZoneAuthority CACHED (localUserId empty): authority={msg.authority_id}, tick={msg.authoritative_tick}");
                return;
            }

            ProcessZoneAuthority(msg.authority_id, msg.authoritative_tick, msg.last_event_seq, msg.zone_id, localUserId);
        }

        /// <summary>
        /// Process zone authority assignment. Called immediately from HandleZoneAuthority
        /// or deferred from Update() when localUserId becomes available.
        /// </summary>
        private void ProcessZoneAuthority(string authorityId, long authoritativeTick, long lastEventSeq, string zoneId, string localUserId)
        {
            bool wasAuthority = _isAuthority;
            _isAuthority = (authorityId == localUserId);
            _currentZoneId = zoneId;

            var authLog = $"[SwarmManager] ZoneAuthority: authority={authorityId}, tick={authoritativeTick}, seq={lastEventSeq}, localUser={localUserId}, isLocalAuthority={_isAuthority}, currentState={_syncState}";
            Debug.Log(authLog);
            DebugFileLogger.Log(authLog);

            // First client joins - go directly to LIVE
            if (_syncState == SyncState.Joining)
            {
                _authoritativeTick = authoritativeTick;
                _simulationTick = authoritativeTick;  // "I have simulated through this tick"
                _frontierWatermark = lastEventSeq;   // FIX #7: Initial watermark
                _lastReceivedSeq = lastEventSeq;     // FIX #7: Assume all prior events received
                TransitionToLive();
                DebugFileLogger.Log($"[SwarmManager] First client -> LIVE at tick {_simulationTick}");
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

            // FIX: Detect authority from tick broadcast if ZoneAuthority was lost
            // This handles the case where ZoneAuthority is sent at MatchJoin before socket is ready
            var localUserId = WorldManager.Instance?.Self?.UserId;
            if (!string.IsNullOrEmpty(msg.authority_id) && msg.authority_id == localUserId && !_isAuthority)
            {
                Debug.Log($"[SwarmManager] ZoneTickBroadcast: Detected self as authority from tick broadcast (ZoneAuthority was likely lost)");
                DebugFileLogger.Log($"[SwarmManager] Late authority setup from tick broadcast: authority_id={msg.authority_id}");

                _isAuthority = true;
                _currentZoneId = msg.zone_id;

                // If still JOINING, go directly to LIVE (same as ZoneAuthority handler)
                if (_syncState == SyncState.Joining)
                {
                    _authoritativeTick = msg.authoritative_tick;
                    _simulationTick = msg.authoritative_tick;
                    _frontierWatermark = msg.last_event_seq;
                    _lastReceivedSeq = msg.last_event_seq;
                    TransitionToLive();
                    DebugFileLogger.Log($"[SwarmManager] Authority (from tick) -> LIVE at tick {_simulationTick}");
                }
                else
                {
                    // Already past JOINING - just start sending snapshots
                    StartAuthoritySnapshots();
                }
            }

            // Update frontier AND watermark (FIX #7)
            if (msg.authoritative_tick > _authoritativeTick)
            {
                Debug.Log($"[SwarmManager] ZoneTickBroadcast: frontier {_authoritativeTick} -> {msg.authoritative_tick}, watermark={msg.last_event_seq}");
                _authoritativeTick = msg.authoritative_tick;
                _frontierWatermark = msg.last_event_seq;
            }
            else
            {
                // Observability: a broadcast that does NOT advance the frontier. Healthy play almost
                // never hits this (each tick's broadcast is newer); a burst of these during a stall
                // means we're draining STALE broadcasts (processing behind the server) — the smoking
                // gun for a client-side message backlog under load.
                DebugFileLogger.Log($"[SwarmManager] ZTB non-advancing: msg.tick={msg.authoritative_tick} authTick={_authoritativeTick} msg.seq={msg.last_event_seq} sim={_simulationTick} state={_syncState}");
            }
        }

        /// <summary>
        /// Transition to LIVE state.
        /// </summary>
        private void TransitionToLive()
        {
            _syncState = SyncState.Live;
            _tickAccumulator = 0.0;

            // Successful (re)sync - clear recovery counters so future stalls get a fresh budget.
            _resyncAttempts = 0;
            _frontierStallTimer = 0f;
            _handshakeWaitTimer = 0f;

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
            // Small delay to ensure swarms are initialized, then send first snapshot
            yield return new WaitForSeconds(0.5f);
            if (!_isAuthority) yield break;

            SendAuthoritySnapshot();

            while (_isAuthority)
            {
                yield return new WaitForSeconds(SnapshotInterval);
                if (!_isAuthority) break;
                SendAuthoritySnapshot();
            }
        }

        /// <summary>
        /// Build and send authority snapshot to server.
        /// </summary>
        private void SendAuthoritySnapshot()
        {
            // Guard: don't send snapshot before any ticks simulated (snapshot_tick would be negative)
            if (_simulationTick <= 0) return;

            var swarmSnapshots = new List<SwarmSnapshotData>();
            foreach (var kvp in _swarms)
            {
                var bugData = kvp.Value.GetAllBugPositions();
                if (bugData.Length > 0)
                {
                    swarmSnapshots.Add(new SwarmSnapshotData
                    {
                        swarm_id = kvp.Key,
                        bugs = bugData
                    });
                }
            }

            // FIX: snapshot_tick must be the tick whose simulation is COMPLETE in this snapshot.
            // _simulationTick is the tick we're ABOUT TO simulate (next tick), so subtract 1.
            // Contract: snapshot_tick = T means "state after SimulateTick(T) with events at T applied"
            var snapshot = new ZoneSnapshotMessage
            {
                zone_id = _currentZoneId,
                snapshot_tick = _simulationTick - 1,
                snapshot_last_event_seq = _lastAppliedSeq, // Last seq whose effects are in this snapshot
                swarms = swarmSnapshots.ToArray(),
                state_hash = "" // TODO: Implement state hash
            };

            SendToServer(OpCodes.ZoneSnapshot, snapshot);
            // DEBUG: Tick semantics - log when snapshot is sent
            var snapLog = $"[Snapshot] Sending zone snapshot: snapshot_tick={snapshot.snapshot_tick}, simTick={_simulationTick}, lastAppliedSeq={_lastAppliedSeq}, swarms={swarmSnapshots.Count}";
            Debug.Log(snapLog);
            DebugFileLogger.Log(snapLog);
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

        // ==========================================================================
        // DEBUG TRACE METHODS
        // ==========================================================================

        public void SetTraceCallback(Action<long, long, List<BugTrace>, List<PlayerTarget>> callback)
        {
            _traceCallback = callback;
        }

        /// <summary>
        /// Collect bug traces from all swarms for the trace buffer.
        /// Uses existing GetAllBugPositions() which returns BugSampleData[].
        /// </summary>
        private List<BugTrace> CollectBugTraces()
        {
            var traces = new List<BugTrace>();
            foreach (var swarmId in _swarms.Keys.OrderBy(id => id))
            {
                var samples = _swarms[swarmId].GetAllBugPositions();
                foreach (var sample in samples)
                {
                    traces.Add(BugTrace.FromSampleData(_simulationTick, sample));
                }
            }
            return traces;
        }

        /// <summary>
        /// Compute deterministic hash of all bug state for divergence detection.
        /// Uses FNV-1a with position and velocity (the core simulation state).
        /// </summary>
        public long ComputeStateHash()
        {
            unchecked
            {
                // FNV-1a 64-bit
                ulong hash = 14695981039346656037UL;
                const ulong prime = 1099511628211UL;

                foreach (var swarmId in _swarms.Keys.OrderBy(id => id))
                {
                    var samples = _swarms[swarmId].GetAllBugPositions();
                    // GetAllBugPositions already returns in consistent order
                    foreach (var bug in samples.OrderBy(b => b.bug_id))
                    {
                        hash ^= (ulong)bug.x;
                        hash *= prime;
                        hash ^= (ulong)bug.y;
                        hash *= prime;
                        hash ^= (ulong)bug.vx;
                        hash *= prime;
                        hash ^= (ulong)bug.vy;
                        hash *= prime;
                    }
                }
                return (long)hash;
            }
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
                WorldManager.Instance.OnPlayerLeft -= HandlePlayerLeft;
            }

            // Clean up all swarms
            foreach (var swarm in _swarms.Values)
            {
                swarm.Cleanup();
            }
            _swarms.Clear();
            _pendingSnapshots.Clear();

            // Clear pending authority state
            _pendingAuthorityId = null;
        }
    }
}
