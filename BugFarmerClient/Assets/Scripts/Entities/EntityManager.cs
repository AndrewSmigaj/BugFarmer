using System.Collections.Generic;
using UnityEngine;
using Nakama;
using BugFarmer.Networking;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Manages spawning, updating, and destroying networked entities.
    /// Listens to WorldManager.OnEntityUpdate for server broadcasts.
    /// </summary>
    public class EntityManager : MonoBehaviour
    {
        public static EntityManager Instance { get; private set; }

        [SerializeField] private GameObject playerPrefab;
        [SerializeField] private GameObject bugPrefab;

        private readonly Dictionary<string, RemoteEntity> _entities = new();
        private readonly Dictionary<string, RemoteEntity> _players = new(); // O(1) player access for bug targeting
        // Per-player appearance + name (PlayerInfo snapshot, OpCode 103). Keyed by "player_"+userId.
        // The source of truth for remote look/name: applied to a live entity, or on spawn if it arrives first.
        private readonly Dictionary<string, PlayerInfoEntry> _playerInfo = new();
        private string _localPlayerId;
        private bool _localPlayerInitialized;

        private void Awake()
        {
            Instance = this;
        }

        private void Start()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnEntityUpdate += HandleEntityUpdate;
                WorldManager.Instance.OnPlayerLeft += HandlePlayerLeft;
            }
            else
            {
                Debug.LogError("[EntityManager] WorldManager not found!");
            }
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnEntityUpdate -= HandleEntityUpdate;
                WorldManager.Instance.OnPlayerLeft -= HandlePlayerLeft;
            }
        }

        /// <summary>
        /// Set the local player's entity ID to skip in updates.
        /// Call after joining a match.
        /// </summary>
        public void SetLocalPlayerId(string userId)
        {
            _localPlayerId = "player_" + userId;
            Debug.Log($"[EntityManager] Local player ID set to: {_localPlayerId}");
        }

        private void HandleEntityUpdate(EntityData[] entities)
        {
            foreach (var data in entities)
            {
                // Handle local player spawn position
                if (data.id == _localPlayerId)
                {
                    if (!_localPlayerInitialized)
                    {
                        // Apply initial spawn position from server
                        var player = FindObjectOfType<Player.PlayerController>();
                        if (player != null)
                        {
                            player.transform.position = new Vector3(data.x, data.y, 0);
                            _localPlayerInitialized = true;
                            Debug.Log($"[EntityManager] Local player spawned at ({data.x}, {data.y})");
                        }
                    }
                    continue; // Skip further processing - movement handled by PlayerController
                }

                if (_entities.TryGetValue(data.id, out var entity))
                {
                    // Update existing entity
                    entity.SetTargetState(data.x, data.y, data.facing);
                    if (data.type == "player")
                        entity.SetEquipped(data.eq); // held-at-rest display (change-checked)
                    entity.SetArmor(data.eqa);   // worn-armor outfit (change-checked)
                }
                else
                {
                    // Spawn new entity
                    var prefab = GetPrefab(data.type);
                    if (prefab != null)
                    {
                        var go = Instantiate(prefab, new Vector3(data.x, data.y, 0), Quaternion.identity);
                        var remote = go.GetComponent<RemoteEntity>();
                        if (remote != null)
                        {
                            remote.EntityId = data.id;
                            remote.SetTargetState(data.x, data.y, data.facing);
                            _entities[data.id] = remote;

                            // Track players separately for O(1) access
                            if (data.type == "player")
                            {
                                _players[data.id] = remote;
                                remote.SetEquipped(data.eq); // joiner bootstrap: equips ride op11
                                remote.SetArmor(data.eqa);
                                // Apply the appearance/name if its PlayerInfo snapshot already arrived
                                // (handles "info before entity" — the other order is handled in ApplyPlayerInfo).
                                if (_playerInfo.TryGetValue(data.id, out var info))
                                {
                                    remote.SetAppearance(info.char_class, info.char_hair, info.char_skin);
                                    remote.SetName(info.name);
                                }
                                Debug.Log($"[EntityManager] Spawned REMOTE PLAYER: {data.id} at ({data.x}, {data.y})");
                            }
                        }
                    }
                    else if (data.type == "player")
                    {
                        Debug.LogError($"[EntityManager] playerPrefab is null! Cannot spawn remote player: {data.id}");
                    }
                }
            }
        }

        private GameObject GetPrefab(string type) => type switch
        {
            "player" => playerPrefab,
            "bug" => bugPrefab,
            _ => null
        };

        private void HandlePlayerLeft(IUserPresence presence)
        {
            var id = "player_" + presence.UserId;
            if (_entities.TryGetValue(id, out var entity))
            {
                Destroy(entity.gameObject); // also destroys the nameplate child
                _entities.Remove(id);
                _players.Remove(id);
            }
            _playerInfo.Remove(id);
        }

        /// <summary>
        /// Apply the per-player appearance + name snapshot (OpCode 103). Stores each entry as the
        /// source of truth and applies it to any already-spawned remote entity; entries for
        /// not-yet-spawned players are picked up by the SPAWN branch. (Runs on the Unity main thread —
        /// the socket uses useMainThread:true.)
        /// </summary>
        public void ApplyPlayerInfo(PlayerInfoEntry[] entries)
        {
            foreach (var e in entries)
            {
                if (e == null || string.IsNullOrEmpty(e.user_id)) continue;
                var id = "player_" + e.user_id;
                if (id == _localPlayerId) continue; // the local player renders from CharacterSession
                _playerInfo[id] = e;
                if (_entities.TryGetValue(id, out var remote) && remote != null)
                {
                    remote.SetAppearance(e.char_class, e.char_hair, e.char_skin);
                    remote.SetName(e.name);
                }
            }
        }

        /// <summary>
        /// Get all remote players for bug behavior targeting.
        /// Returns dictionary for O(1) access. Keys are "player_userId".
        /// </summary>
        public IReadOnlyDictionary<string, RemoteEntity> GetRemotePlayers() => _players;

        /// <summary>
        /// Destroy all tracked entities. Call when leaving a match.
        /// </summary>
        /// <summary>
        /// Authoritatively place the local player (OpCode 102, sent once per join/reconnect). This is
        /// the reliable spawn signal — it pre-empts the passive entity-update snap (which races with
        /// client movement and only fires while _localPlayerInitialized is false, a flag that survives
        /// a reconnect). Marks initialized so the entity-update path won't fight it.
        /// </summary>
        public void SetLocalPlayerSpawn(float x, float y)
        {
            var player = FindObjectOfType<Player.PlayerController>();
            if (player != null)
                player.transform.position = new Vector3(x, y, 0);
            _localPlayerInitialized = true;
            Debug.Log($"[EntityManager] Local player spawn set to ({x}, {y})");
        }

        public void ClearAllEntities()
        {
            foreach (var entity in _entities.Values)
            {
                if (entity != null)
                    Destroy(entity.gameObject);
            }
            _entities.Clear();
            _players.Clear();
            _playerInfo.Clear();
            _localPlayerInitialized = false; // Reset for next match join
        }
    }
}
