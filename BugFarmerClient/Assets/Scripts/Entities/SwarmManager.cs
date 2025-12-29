using System.Collections.Generic;
using System.Linq;
using Nakama;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.UI;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Result of catching flies from a single swarm.
    /// </summary>
    public struct CatchResult
    {
        public string swarmId;
        public int caughtCount;
    }

    /// <summary>
    /// Manages swarm visuals based on server updates.
    /// Singleton that subscribes to WorldManager.OnMatchData for OpCode 20.
    /// </summary>
    public class SwarmManager : MonoBehaviour
    {
        public static SwarmManager Instance { get; private set; }

        [SerializeField] private GameObject swarmVisualPrefab;
        [SerializeField] private GameObject flyPrefab;

        private readonly Dictionary<string, SwarmVisual> _swarms = new();

        private void Awake()
        {
            Instance = this;
        }

        private void Start()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData += HandleMatchData;
            }
        }

        private void HandleMatchData(IMatchState state)
        {
            switch (state.OpCode)
            {
                case OpCodes.SwarmUpdate:
                    HandleSwarmUpdate(state);
                    break;
                case OpCodes.BugCaught:
                    HandleBugCaught(state);
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
                    SpawnSwarm(data);
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

            // Skip own catch - already removed flies locally
            var localUserId = WorldManager.Instance?.Self?.UserId;
            if (!string.IsNullOrEmpty(localUserId) && msg.catcher_id == localUserId)
                return;

            // Other players: use random removal
            var swarm = GetSwarm(msg.swarm_id);
            if (swarm != null)
            {
                swarm.RemoveRandomFlies(msg.count);
                swarm.ShowCatchAnimation(new Vector2(msg.x, msg.y), msg.catcher_id);
            }
        }

        private void SpawnSwarm(SwarmData data)
        {
            GameObject obj;

            if (swarmVisualPrefab != null)
            {
                obj = Instantiate(swarmVisualPrefab);
            }
            else
            {
                // Fallback: create empty GameObject with SwarmVisual
                obj = new GameObject($"Swarm_{data.id}");
                obj.AddComponent<SwarmVisual>();
            }

            var visual = obj.GetComponent<SwarmVisual>();
            visual.Initialize(data, flyPrefab);
            _swarms[data.id] = visual;
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
        /// Catch flies at position across all swarms.
        /// Removes flies within radius and returns results per swarm.
        /// </summary>
        public List<CatchResult> CatchAtPosition(Vector2 worldPosition, float catchRadius)
        {
            var results = new List<CatchResult>();

            foreach (var kvp in _swarms)
            {
                int caught = kvp.Value.RemoveFliesInRadius(worldPosition, catchRadius);
                if (caught > 0)
                {
                    results.Add(new CatchResult { swarmId = kvp.Key, caughtCount = caught });
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
        }
    }
}
