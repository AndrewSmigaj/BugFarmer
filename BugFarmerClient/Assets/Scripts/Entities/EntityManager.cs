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
                        }
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
                Destroy(entity.gameObject);
                _entities.Remove(id);
            }
        }

        /// <summary>
        /// Destroy all tracked entities. Call when leaving a match.
        /// </summary>
        public void ClearAllEntities()
        {
            foreach (var entity in _entities.Values)
            {
                if (entity != null)
                    Destroy(entity.gameObject);
            }
            _entities.Clear();
            _localPlayerInitialized = false; // Reset for next match join
        }
    }
}
