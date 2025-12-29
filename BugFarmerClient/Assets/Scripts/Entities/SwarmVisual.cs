using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Networking;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Visual representation of a swarm. Manages individual fly GameObjects
    /// and interpolates the swarm center position.
    /// </summary>
    public class SwarmVisual : MonoBehaviour
    {
        [SerializeField] private GameObject flyPrefab;

        private readonly List<FlyBehavior> _flies = new();
        private static readonly Stack<FlyBehavior> _flyPool = new();

        private Vector2 _previousPos;
        private Vector2 _targetPos;
        private float _interpProgress = 1f;
        private const float InterpDuration = 0.15f; // 150ms interpolation

        public string SwarmId { get; private set; }
        public string SpeciesId { get; private set; }
        public int Count => _flies.Count;

        /// <summary>
        /// Initialize the swarm visual with server data.
        /// </summary>
        public void Initialize(SwarmData data, GameObject flyPrefabOverride = null)
        {
            if (flyPrefabOverride != null)
            {
                flyPrefab = flyPrefabOverride;
            }

            SwarmId = data.id;
            SpeciesId = data.species_id;

            _previousPos = new Vector2(data.x, data.y);
            _targetPos = _previousPos;
            transform.position = _previousPos;

            AdjustFlyCount(data.count, data.radius);
        }

        /// <summary>
        /// Update from server data - starts interpolation to new position.
        /// </summary>
        public void UpdateFromServer(SwarmData data)
        {
            // Start interpolation from current position to new target
            _previousPos = transform.position;
            _targetPos = new Vector2(data.x, data.y);
            _interpProgress = 0f;

            // Adjust fly count if changed
            if (_flies.Count != data.count)
            {
                AdjustFlyCount(data.count, data.radius);
            }

            // Update fly wander radius if changed
            foreach (var fly in _flies)
            {
                fly.WanderRadius = data.radius;
            }
        }

        private void Update()
        {
            // Interpolate position
            if (_interpProgress < 1f)
            {
                _interpProgress += Time.deltaTime / InterpDuration;
                if (_interpProgress > 1f)
                {
                    _interpProgress = 1f;
                }

                transform.position = Vector2.Lerp(_previousPos, _targetPos, _interpProgress);

                // Update fly home positions to follow swarm center
                Vector2 center = transform.position;
                foreach (var fly in _flies)
                {
                    fly.SetHomePosition(center);
                }
            }
        }

        /// <summary>
        /// Adjust the number of flies to match server count.
        /// </summary>
        private void AdjustFlyCount(int targetCount, float radius)
        {
            // Add flies
            while (_flies.Count < targetCount)
            {
                var fly = GetFlyFromPool();
                if (fly == null && flyPrefab != null)
                {
                    var flyObj = Instantiate(flyPrefab, transform);
                    fly = flyObj.GetComponent<FlyBehavior>();
                }

                if (fly != null)
                {
                    fly.gameObject.SetActive(true);
                    fly.transform.SetParent(transform);

                    // Random position within swarm radius
                    Vector2 offset = Random.insideUnitCircle * radius;
                    fly.transform.position = (Vector2)transform.position + offset;
                    fly.SetHomePosition(transform.position);
                    fly.WanderRadius = radius;

                    _flies.Add(fly);
                }
            }

            // Remove excess flies
            while (_flies.Count > targetCount && _flies.Count > 0)
            {
                var fly = _flies[_flies.Count - 1];
                _flies.RemoveAt(_flies.Count - 1);
                ReturnFlyToPool(fly);
            }
        }

        /// <summary>
        /// Get a fly from the static pool, or null if empty.
        /// </summary>
        private static FlyBehavior GetFlyFromPool()
        {
            if (_flyPool.Count > 0)
            {
                return _flyPool.Pop();
            }
            return null;
        }

        /// <summary>
        /// Return a fly to the static pool.
        /// </summary>
        private static void ReturnFlyToPool(FlyBehavior fly)
        {
            if (fly != null)
            {
                fly.gameObject.SetActive(false);
                fly.transform.SetParent(null);
                _flyPool.Push(fly);
            }
        }

        /// <summary>
        /// Remove random flies immediately (visual feedback for catches).
        /// Different from AdjustFlyCount which removes from end.
        /// </summary>
        public void RemoveRandomFlies(int count)
        {
            for (int i = 0; i < count && _flies.Count > 0; i++)
            {
                int idx = Random.Range(0, _flies.Count);
                var fly = _flies[idx];
                _flies.RemoveAt(idx);
                ReturnFlyToPool(fly);
            }
        }

        /// <summary>
        /// Remove flies within radius of a world position.
        /// Returns count removed for sending to server.
        /// </summary>
        public int RemoveFliesInRadius(Vector2 worldPosition, float radius)
        {
            float radiusSq = radius * radius;
            int removed = 0;

            for (int i = _flies.Count - 1; i >= 0; i--)
            {
                var fly = _flies[i];
                if (fly == null) continue;

                Vector2 flyPos = fly.transform.position;
                if ((flyPos - worldPosition).sqrMagnitude <= radiusSq)
                {
                    _flies.RemoveAt(i);
                    ReturnFlyToPool(fly);
                    removed++;
                }
            }

            return removed;
        }

        /// <summary>
        /// Show catch animation for other players (local player has their own).
        /// </summary>
        public void ShowCatchAnimation(Vector2 catchPos, string catcherID)
        {
            // Skip if catcher is local player
            var localUserId = WorldManager.Instance?.Self?.UserId;
            if (catcherID == localUserId)
            {
                return;
            }

            // For now, just log - visual effect prefab can be added later
            Debug.Log($"[SwarmVisual] Player {catcherID} caught bugs at {catchPos}");
        }

        /// <summary>
        /// Clean up when swarm is destroyed.
        /// </summary>
        public void Cleanup()
        {
            foreach (var fly in _flies)
            {
                ReturnFlyToPool(fly);
            }
            _flies.Clear();
        }

        private void OnDestroy()
        {
            Cleanup();
        }
    }
}
