using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Nakama;
using UnityEngine;

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

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_join", payload);
                var response = JsonUtility.FromJson<WorldJoinResponse>(result.Payload);

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

                Debug.Log($"[WorldManager] Joined match: {CurrentMatch.Id} with {Players.Count} player(s)");
                return CurrentMatch;
            }
            catch (ApiResponseException ex)
            {
                Debug.LogError($"[WorldManager] JoinWorld failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Enter the canonical world for a zone (Normal=village_21, Test=sim_test) via the
        /// world_enter RPC, which finds-or-creates a singleton world server-side. No world
        /// creation happens client-side. Mirrors JoinWorld once it has the match id.
        /// </summary>
        public async Task<IMatch> EnterWorld(string zoneId)
        {
            var session = await NetworkManager.Instance.Session;
            var socket = NetworkManager.Instance.Socket;

            var request = new WorldEnterRequest { zone_id = zoneId };
            var payload = JsonUtility.ToJson(request);

            try
            {
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "world_enter", payload);
                var response = JsonUtility.FromJson<WorldJoinResponse>(result.Payload);

                CurrentMatch = await socket.JoinMatchAsync(response.match_id);
                Self = CurrentMatch.Self;
                Players.Clear();
                Players.AddRange(CurrentMatch.Presences);

                if (Entities.EntityManager.Instance != null)
                {
                    Entities.EntityManager.Instance.SetLocalPlayerId(Self.UserId);
                }

                Debug.Log($"[WorldManager] Entered zone '{zoneId}': match {CurrentMatch.Id} with {Players.Count} player(s)");
                return CurrentMatch;
            }
            catch (ApiResponseException ex)
            {
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
            }
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
            // Debug: log all incoming opcodes except frequent ones
            if (state.OpCode != OpCodes.EntityUpdate && state.OpCode != 20) // 20 = SwarmUpdate
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

                default:
                    OnMatchData?.Invoke(state);
                    break;
            }
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
