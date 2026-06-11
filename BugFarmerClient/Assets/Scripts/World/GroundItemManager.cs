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
        private Transform _player; // magnet-tween target (cached lazily)

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

            // Join-time food-registry HYDRATION: chunk-subscribe re-sends existing ground
            // items; ones that are ALREADY rotten are bug food a joiner would otherwise miss
            // (their ITEM_ROTTED events may be pruned). Live mutations stay event-driven —
            // HydrateFood is a no-op for ids already registered.
            if (msg.item_type.StartsWith("rotten_"))
                Bugs.InfluenceManager.Instance?.HydrateFood(msg.id, new Vector2(msg.x, msg.y), 100);
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
                _items.Remove(msg.id);

                // OUR pending pickup (TTL-marked by PickupController)? Magnet the item
                // into the player. Anything else (another player's grab, rot's same-id
                // remove+respawn) gets a quick shrink-fade. Either way the visual pools
                // only AFTER the tween — and ResetVisual restores scale/alpha first.
                Vector3? magnetTarget = null;
                if (Player.PickupController.ConsumeMark(msg.id))
                {
                    if (_player == null)
                        _player = FindObjectOfType<Player.PlayerController>()?.transform;
                    if (_player != null)
                        magnetTarget = _player.position;
                }
                visual.Despawn(magnetTarget, () => ReturnToPool(visual));
            }
        }

        /// <summary>
        /// Find the closest ground item within radius of a world position.
        /// </summary>
        public GroundItemVisual GetItemAtPosition(Vector3 worldPosition, float radius)
        {
            return GetClosestItem(worldPosition, radius, includeBugFood: true);
        }

        /// <summary>
        /// True for items the walk-over magnet must NOT collect — only the deliberate
        /// E key takes them. Two sources: registered BUG FOOD (rotten fruit — "what the
        /// bugs eat belongs to the bugs"), and items flagged no_auto_pickup in items.json
        /// (fresh fruit: tree fruit is farmed deliberately, not hoovered in passing —
        /// the 'it auto-picks my apples' fix).
        /// </summary>
        public static bool IsAutoPickupExcluded(string itemType)
        {
            if (string.IsNullOrEmpty(itemType)) return false;
            if (itemType.StartsWith("rotten_")) return true;
            var def = EntityDatabase.Get(itemType);
            return def != null && def.NoAutoPickup;
        }

        /// <summary>
        /// Closest ground item within radius, optionally skipping auto-pickup-excluded
        /// items (the walk-over magnet path).
        /// </summary>
        public GroundItemVisual GetClosestItem(Vector3 worldPosition, float radius, bool includeBugFood)
        {
            GroundItemVisual closest = null;
            float closestDist = radius;

            foreach (var item in _items.Values)
            {
                if (item.Despawning)
                    continue;
                if (!includeBugFood && IsAutoPickupExcluded(item.ItemType))
                    continue;
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
