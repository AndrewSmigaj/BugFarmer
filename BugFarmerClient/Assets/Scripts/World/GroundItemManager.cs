using System.Collections.Generic;
using Nakama;
using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.UI;

namespace BugFarmer.World
{
    /// <summary>
    /// Manages ground item visuals based on server updates.
    /// Singleton that subscribes to WorldManager.OnMatchData for OpCodes 47/48.
    /// </summary>
    public class GroundItemManager : MonoBehaviour
    {
        public static GroundItemManager Instance { get; private set; }

        private readonly Dictionary<string, GroundItemVisual> _items = new();
        private readonly Queue<GroundItemVisual> _pool = new();

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

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
            }
        }

        private void HandleMatchData(IMatchState state)
        {
            switch (state.OpCode)
            {
                case OpCodes.GroundItemSpawn:
                    HandleItemSpawn(state);
                    break;
                case OpCodes.GroundItemRemove:
                    HandleItemRemove(state);
                    break;
            }
        }

        private void HandleItemSpawn(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<GroundItemSpawnMessage>(json);

            if (msg == null || string.IsNullOrEmpty(msg.id))
                return;

            if (_items.ContainsKey(msg.id))
                return;

            var sprite = EntityDatabase.GetItemSprite(msg.item_type);
            var visual = GetFromPool();
            var worldPos = new Vector3(msg.x, msg.y, 0f);
            visual.Initialize(msg.id, msg.item_type, msg.count, sprite, worldPos);
            _items[msg.id] = visual;
        }

        private void HandleItemRemove(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<GroundItemRemoveMessage>(json);

            if (msg == null || string.IsNullOrEmpty(msg.id))
            {
                return;
            }

            if (_items.TryGetValue(msg.id, out var visual))
            {
                ReturnToPool(visual);
                _items.Remove(msg.id);
            }
        }

        /// <summary>
        /// Find the closest ground item within radius of a world position.
        /// </summary>
        public GroundItemVisual GetItemAtPosition(Vector3 worldPosition, float radius)
        {
            GroundItemVisual closest = null;
            float closestDist = radius;

            foreach (var item in _items.Values)
            {
                float dist = Vector2.Distance(worldPosition, item.transform.position);
                if (dist < closestDist)
                {
                    closestDist = dist;
                    closest = item;
                }
            }

            return closest;
        }

        /// <summary>
        /// Clear all ground items (e.g., on disconnect or chunk unload).
        /// </summary>
        public void ClearAll()
        {
            foreach (var item in _items.Values)
            {
                ReturnToPool(item);
            }
            _items.Clear();
        }

        private GroundItemVisual GetFromPool()
        {
            if (_pool.Count > 0)
            {
                return _pool.Dequeue();
            }

            // Create GameObject programmatically (no prefab needed)
            var go = new GameObject("GroundItem");
            go.transform.SetParent(transform);
            go.AddComponent<SpriteRenderer>();
            var visual = go.AddComponent<GroundItemVisual>();
            go.SetActive(false);
            return visual;
        }

        private void ReturnToPool(GroundItemVisual visual)
        {
            visual.ResetVisual();
            _pool.Enqueue(visual);
        }
    }
}
