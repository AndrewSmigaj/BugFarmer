using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Nakama;
using UnityEngine;
using BugFarmer.Util;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Handles world RPC calls and match state management.
    /// </summary>
    public class WorldManager : MonoBehaviour
    {
        public static WorldManager Instance { get; private set; }

        public IMatch CurrentMatch { get; private set; }
        public IUserPresence Self { get; private set; }
        public List<IUserPresence> Players { get; } = new();

        // Current zone + its edge neighbors (from the world_enter response) — drives CrossZoneController.
        public string CurrentZoneId { get; private set; }
        public ZoneNeighbors CurrentNeighbors { get; private set; }

        // JOIN-HANDSHAKE BUFFER: match-data frames can arrive BEFORE JoinMatchAsync returns and assigns
        // CurrentMatch — Nakama dispatches them through one FIFO together with the join response
        // (Assets/Nakama/Runtime/UnitySocket.cs). The HandleMatchState guard would otherwise DROP them,
        // and the one-shot WorldInit (OpCode 68, the world seed) has no second chance → the authority
        // client never seeds its bug sim and shows 0 swarms. We buffer frames for the match we're joining
        // and replay them once CurrentMatch/Self are set. See docs/product/determinism_audit_2026-06-20.md.
        private string _joiningMatchId;
        private readonly List<IMatchState> _preJoinBuffer = new();
        private const int MaxPreJoinBuffer = 256;

        public event Action<IUserPresence> OnPlayerJoined;
        public event Action<IUserPresence> OnPlayerLeft;
        public event Action<IMatchState> OnMatchData;
        public event Action<EntityData[]> OnEntityUpdate;

        private void Awake()
        {
            Instance = this;
        }

        private async void Start()
        {
            await NetworkManager.Instance.Session; // Wait for auth
            var socket = NetworkManager.Instance.Socket;
            socket.ReceivedMatchPresence += HandlePresence;
            socket.ReceivedMatchState += HandleMatchState;
        }

        public async Task<WorldCreateResponse> CreateWorld(string name, string accessPolicy = "public", string zoneId = "")
        {
            var session = await NetworkManager.Instance.Session;
            var request = new WorldCreateRequest
            {
                name = name,
                access_policy = accessPolicy,
                zone_id = zoneId
            };
            var payload = JsonUtility.ToJson(request);

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_create", payload);
                var response = JsonUtility.FromJson<WorldCreateResponse>(result.Payload);
                Debug.Log($"[WorldManager] Created world: {response.world_id}");
                return response;
            }
            catch (ApiResponseException ex)
            {
                Debug.LogError($"[WorldManager] CreateWorld failed: {ex.Message}");
                throw;
            }
        }

        public async Task<WorldInfo[]> ListWorlds(int limit = 10)
        {
            var session = await NetworkManager.Instance.Session;
            var request = new WorldListRequest { limit = limit };
            var payload = JsonUtility.ToJson(request);

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_list", payload);
                var response = JsonUtility.FromJson<WorldListResponse>(result.Payload);
                Debug.Log($"[WorldManager] Found {response.worlds?.Length ?? 0} world(s)");
                return response.worlds ?? Array.Empty<WorldInfo>();
            }
            catch (ApiResponseException ex)
            {
                Debug.LogError($"[WorldManager] ListWorlds failed: {ex.Message}");
                throw;
            }
        }

        public async Task<IMatch> JoinWorld(string worldId)
        {
            var session = await NetworkManager.Instance.Session;
            var socket = NetworkManager.Instance.Socket;

            var request = new WorldJoinRequest { world_id = worldId };
            var payload = JsonUtility.ToJson(request);

            _joiningMatchId = null;
            _preJoinBuffer.Clear();

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_join", payload);
                var response = JsonUtility.FromJson<WorldJoinResponse>(result.Payload);

                _joiningMatchId = response.match_id;
                CurrentMatch = await socket.JoinMatchAsync(response.match_id);
                Self = CurrentMatch.Self;
                Players.Clear();
                Players.AddRange(CurrentMatch.Presences);

                // CRITICAL: Set local player ID for EntityManager to filter self updates
                if (Entities.EntityManager.Instance != null)
                {
                    Entities.EntityManager.Instance.SetLocalPlayerId(Self.UserId);
                    Debug.Log($"[WorldManager] Set local player ID: {Self.UserId}");
                }
                else
                {
                    Debug.LogError("[WorldManager] EntityManager.Instance is null! Remote players will not be filtered correctly.");
                }

                FlushPreJoinBuffer();
                Debug.Log($"[WorldManager] Joined match: {CurrentMatch.Id} with {Players.Count} player(s)");
                return CurrentMatch;
            }
            catch (ApiResponseException ex)
            {
                _joiningMatchId = null;
                _preJoinBuffer.Clear();
                Debug.LogError($"[WorldManager] JoinWorld failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Enter the canonical world for a zone (Normal=village_21, Test=sim_test) via the
        /// world_enter RPC, which finds-or-creates a singleton world server-side. No world
        /// creation happens client-side. Mirrors JoinWorld once it has the match id.
        /// </summary>
        public async Task<IMatch> EnterWorld(string zoneId, string charId = null,
                                             float? entryX = null, float? entryY = null)
        {
            var session = await NetworkManager.Instance.Session;
            var socket = NetworkManager.Instance.Socket;

            // Start clean: discard any frames buffered for a previous join (e.g. before a zone swap). We
            // only begin buffering once _joiningMatchId is set to THIS match below, right before the join.
            _joiningMatchId = null;
            _preJoinBuffer.Clear();

            var request = new WorldEnterRequest { zone_id = zoneId };
            var payload = JsonUtility.ToJson(request);

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_enter", payload);
                var response = JsonUtility.FromJson<WorldJoinResponse>(result.Payload);

                // JOIN METADATA: char_id (load the save) + optional entry_x/entry_y (cross-zone edge
                // entry — places the player at the matching edge instead of the save's spawn).
                var meta = new Dictionary<string, string>();
                if (!string.IsNullOrEmpty(charId)) meta["char_id"] = charId;
                if (entryX.HasValue && entryY.HasValue)
                {
                    meta["entry_x"] = entryX.Value.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
                    meta["entry_y"] = entryY.Value.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
                }
                // Buffer (don't drop) match-data that arrives for THIS match during the join handshake.
                _joiningMatchId = response.match_id;
                CurrentMatch = meta.Count > 0
                    ? await socket.JoinMatchAsync(response.match_id, meta)
                    : await socket.JoinMatchAsync(response.match_id);

                CurrentZoneId = zoneId;
                CurrentNeighbors = response.neighbors;
                Debug.Log($"[WorldManager] zone '{zoneId}' neighbors: N={CurrentNeighbors?.north} " +
                          $"S={CurrentNeighbors?.south} E={CurrentNeighbors?.east} W={CurrentNeighbors?.west}");
                Self = CurrentMatch.Self;
                Players.Clear();
                Players.AddRange(CurrentMatch.Presences);

                if (Entities.EntityManager.Instance != null)
                {
                    Entities.EntityManager.Instance.SetLocalPlayerId(Self.UserId);
                }

                // Now fully joined (CurrentMatch/Self/local-player set): replay anything that arrived during
                // the handshake — notably the one-shot WorldInit that seeds the bug sim.
                FlushPreJoinBuffer();

                Debug.Log($"[WorldManager] Entered zone '{zoneId}': match {CurrentMatch.Id} with {Players.Count} player(s)");
                return CurrentMatch;
            }
            catch (ApiResponseException ex)
            {
                _joiningMatchId = null;
                _preJoinBuffer.Clear();
                Debug.LogError($"[WorldManager] EnterWorld('{zoneId}') failed: {ex.Message}");
                throw;
            }
        }

        public async Task LeaveWorld()
        {
            if (CurrentMatch != null)
            {
                var matchId = CurrentMatch.Id;
                await NetworkManager.Instance.Socket.LeaveMatchAsync(matchId);
                Debug.Log($"[WorldManager] Left match: {matchId}");
                CurrentMatch = null;
                Self = null;
                Players.Clear();
                _joiningMatchId = null;
                _preJoinBuffer.Clear();
            }
        }

        /// <summary>
        /// Tear down ALL of the current zone's client state before a cross-zone swap. Both zones share
        /// coords 0..255, so without this zone A's remote players, bugs, influence registry, and terrain
        /// ghost into zone B. Call this right before EnterWorld(neighbor). Zone B re-bootstraps from its
        /// own join messages (PlayerSpawn/SwarmUpdate/ChunkData), exactly like a fresh join.
        /// </summary>
        public void ResetForZoneSwap()
        {
            Entities.EntityManager.Instance?.ClearAllEntities();      // remote players/entities + re-arm spawn snap
            Entities.SwarmManager.Instance?.ClearAllSwarms();         // bug visuals + the seq/inbox frontier state
            Bugs.InfluenceManager.Instance?.ClearPlayerCells();       // event-sourced bug-AI context
            Bugs.InfluenceManager.Instance?.ClearSwarmLegs();
            Bugs.InfluenceManager.Instance?.ClearFood();
            World.TilemapManager.Instance?.UnloadAllChunks();         // terrain + occupant pool
            Debug.Log("[WorldManager] ResetForZoneSwap: cleared entities/swarms/influence/tiles");
        }

        private void HandlePresence(IMatchPresenceEvent ev)
        {
            foreach (var leave in ev.Leaves)
            {
                Players.RemoveAll(p => p.SessionId == leave.SessionId);
                Debug.Log($"[WorldManager] Player left: {leave.Username}");
                OnPlayerLeft?.Invoke(leave);
            }

            foreach (var join in ev.Joins)
            {
                if (join.SessionId != Self?.SessionId)
                {
                    Players.Add(join);
                    Debug.Log($"[WorldManager] Player joined: {join.Username}");
                    OnPlayerJoined?.Invoke(join);
                }
            }
        }

        private void HandleMatchState(IMatchState state)
        {
            // JOIN-HANDSHAKE: frames for the match we're currently joining can arrive before
            // JoinMatchAsync returns (CurrentMatch still null). Dropping them loses the one-shot WorldInit
            // (seed) → 0-swarm authority. Buffer them and replay after the join completes (FlushPreJoinBuffer).
            if (CurrentMatch == null)
            {
                if (_joiningMatchId != null && state.MatchId == _joiningMatchId && _preJoinBuffer.Count < MaxPreJoinBuffer)
                {
                    if (DebugConfig.Verbose)
                        Debug.Log($"[WorldManager] Buffering pre-join OpCode {state.OpCode} for match {state.MatchId}");
                    _preJoinBuffer.Add(state);
                }
                return;
            }

            // CROSS-ZONE GUARD: drop messages not for the current match. On a fast zone swap, stale
            // zone-A messages can still be buffered; applied to zone B they ghost entities AND inject
            // A's influence seqs into B's frontier (a sync stall). The match id is the definitive filter.
            if (state.MatchId != CurrentMatch.Id)
                return;

            // Debug: log all incoming opcodes except frequent ones
            if (DebugConfig.Verbose && state.OpCode != OpCodes.EntityUpdate && state.OpCode != 20) // 20 = SwarmUpdate
            {
                Debug.Log($"[WorldManager] Received OpCode {state.OpCode}");
            }

            switch (state.OpCode)
            {
                case OpCodes.EntityUpdate:
                    var json = System.Text.Encoding.UTF8.GetString(state.State);
                    var update = JsonUtility.FromJson<EntityUpdateMessage>(json);
                    if (update?.entities != null)
                    {
                        OnEntityUpdate?.Invoke(update.entities);
                    }
                    break;

                case OpCodes.PlayerSpawn:
                    var spawnJson = System.Text.Encoding.UTF8.GetString(state.State);
                    var spawn = JsonUtility.FromJson<PlayerSpawnMessage>(spawnJson);
                    if (spawn != null)
                        Entities.EntityManager.Instance?.SetLocalPlayerSpawn(spawn.x, spawn.y);
                    break;

                case OpCodes.PlayerInfo:
                    var infoJson = System.Text.Encoding.UTF8.GetString(state.State);
                    var info = JsonUtility.FromJson<PlayerInfoMessage>(infoJson);
                    if (info?.players != null)
                        Entities.EntityManager.Instance?.ApplyPlayerInfo(info.players);
                    break;

                default:
                    OnMatchData?.Invoke(state);
                    break;
            }
        }

        // Replay match-data buffered during the join handshake, now that CurrentMatch/Self/local-player are
        // set so every handler sees a fully-joined client. Order is preserved (WorldInit before ZoneAuthority,
        // etc.). Re-entry is safe: CurrentMatch is non-null now, so these flow through the normal path.
        private void FlushPreJoinBuffer()
        {
            _joiningMatchId = null;
            if (_preJoinBuffer.Count == 0) return;
            var buffered = _preJoinBuffer.ToArray();
            _preJoinBuffer.Clear();
            // Unconditional (low-volume: once per join): names the opcodes recovered. This is the evidence
            // that the one-shot WorldInit (OpCode 68) was arriving during the handshake and would otherwise
            // have been dropped — i.e. the fix is doing real work.
            Debug.Log($"[WorldManager] Flushing {buffered.Length} buffered pre-join message(s); opcodes=[{string.Join(",", buffered.Select(s => s.OpCode))}]");
            foreach (var st in buffered)
                HandleMatchState(st);
        }

        private void OnDestroy()
        {
            var socket = NetworkManager.Instance?.Socket;
            if (socket != null)
            {
                socket.ReceivedMatchPresence -= HandlePresence;
                socket.ReceivedMatchState -= HandleMatchState;
            }
        }
    }

    // Request DTOs - JsonUtility requires concrete [Serializable] classes
    [Serializable]
    public class WorldCreateRequest
    {
        public string name;
        public string access_policy;
        public string zone_id;
    }

    [Serializable]
    public class WorldListRequest
    {
        public int limit;
    }

    [Serializable]
    public class WorldJoinRequest
    {
        public string world_id;
    }

    [Serializable]
    public class WorldEnterRequest
    {
        public string zone_id;
    }

    // Response DTOs
    [Serializable]
    public class WorldCreateResponse
    {
        public string world_id;
        public string match_id;
    }

    [Serializable]
    public class WorldJoinResponse
    {
        public string match_id;
        public ZoneNeighbors neighbors;   // cross-zone adjacency (may be null)
    }

    /// <summary>A zone's edge neighbors (zoneID per direction; "" = a hard edge). Fixed fields so JsonUtility parses it.</summary>
    [Serializable]
    public class ZoneNeighbors
    {
        public string north;
        public string south;
        public string east;
        public string west;
    }

    [Serializable]
    public class WorldListResponse
    {
        public WorldInfo[] worlds;
    }

    [Serializable]
    public class WorldInfo
    {
        public string world_id;
        public string name;
        public string owner_id;
    }
}
