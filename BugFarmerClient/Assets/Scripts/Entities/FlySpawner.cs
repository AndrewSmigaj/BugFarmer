using UnityEngine;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Spawns flies in a circular area around this object.
    /// </summary>
    public class FlySpawner : MonoBehaviour
    {
        [SerializeField] private GameObject flyPrefab;
        [SerializeField] private int spawnCount = 10;
        [SerializeField] private float spawnRadius = 5f;

        private void Start()
        {
            SpawnFlies();
        }

        [ContextMenu("Spawn Flies")]
        public void SpawnFlies()
        {
            if (flyPrefab == null)
            {
                Debug.LogError("[FlySpawner] No fly prefab assigned!");
                return;
            }

            for (int i = 0; i < spawnCount; i++)
            {
                // Random position within spawn radius
                Vector2 offset = Random.insideUnitCircle * spawnRadius;
                Vector3 spawnPos = transform.position + new Vector3(offset.x, offset.y, 0);

                GameObject fly = Instantiate(flyPrefab, spawnPos, Quaternion.identity, transform);

                // Set the home position for wandering
                var behavior = fly.GetComponent<FlyBehavior>();
                if (behavior != null)
                {
                    behavior.SetHomePosition(spawnPos);
                }
            }

            Debug.Log($"[FlySpawner] Spawned {spawnCount} flies");
        }

        private void OnDrawGizmosSelected()
        {
            // Show spawn area in editor
            Gizmos.color = new Color(1f, 1f, 0f, 0.3f);
            Gizmos.DrawWireSphere(transform.position, spawnRadius);
        }
    }
}
