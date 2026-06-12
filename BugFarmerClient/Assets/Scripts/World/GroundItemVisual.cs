using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Visual component for dropped items in the world.
    /// Handles bob animation and highlight feedback.
    /// Managed by GroundItemManager for pooling.
    /// </summary>
    public class GroundItemVisual : MonoBehaviour
    {
        [Header("Bob Animation")]
        [SerializeField] private float bobAmplitude = 0.08f;
        [SerializeField] private float bobFrequency = 2f;

        [Header("Highlight")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color highlightColor = new Color(1.2f, 1.2f, 1f, 1f);

        // Public properties for manager access
        public string ItemId { get; private set; }
        public string ItemType { get; private set; }
        public int Count { get; private set; }

        private SpriteRenderer spriteRenderer;
        private Vector3 basePosition;
        private float bobOffset;

        /// <summary>True while the despawn tween runs (suppresses the bob; pickup queries skip it).</summary>
        public bool Despawning { get; private set; }

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer == null)
            {
                spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
            }

            // Match occupant sorting layer
            spriteRenderer.sortingLayerName = "Occupants";
            LitMaterials.Apply(spriteRenderer); // receive day/night lighting
        }

        /// <summary>
        /// Initialize the ground item visual.
        /// </summary>
        public void Initialize(string id, string itemType, int count, Sprite sprite, Vector3 worldPosition)
        {
            ItemId = id;
            ItemType = itemType;
            Count = count;

            basePosition = worldPosition;
            transform.position = worldPosition;

            // Ensure we have a sprite renderer
            if (spriteRenderer == null)
            {
                spriteRenderer = GetComponent<SpriteRenderer>();
                if (spriteRenderer == null)
                {
                    spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
                }
            }

            spriteRenderer.sprite = sprite;
            spriteRenderer.color = normalColor;
            spriteRenderer.sortingLayerName = "Occupants";
            spriteRenderer.sortingOrder = -Mathf.RoundToInt(worldPosition.y);

            // Fit-box: drops are scaled-down ORIGINAL sprites (often full world art now, e.g.
            // a 16x24 plant), so uniformly fit within 0.9 cell preserving aspect — clearly a
            // pickup, never rivaling placed occupants. SMALL sprites get upscaled to a
            // 0.6-cell floor (2026-06: tiny drops were too hard to see).
            const float maxCells = 0.9f;
            const float minCells = 0.6f;
            float scale = 1f;
            if (sprite != null)
            {
                // World size in cells at the sprite's own PPU (icons & objects are PPU 16 = 1 cell).
                float w = sprite.rect.width / sprite.pixelsPerUnit;
                float h = sprite.rect.height / sprite.pixelsPerUnit;
                float big = Mathf.Max(w, h);
                scale = big > maxCells ? maxCells / big
                      : big < minCells ? minCells / big : 1f;
            }
            transform.localScale = new Vector3(scale, scale, 1f);

            // Randomize bob phase so items don't sync
            bobOffset = Random.Range(0f, Mathf.PI * 2f);

            gameObject.SetActive(true);
        }

        /// <summary>
        /// Reset for object pooling. MUST restore everything the despawn tween touches
        /// (scale, alpha, the flag, running coroutines) — the rot transition is a real
        /// same-id REMOVE+SPAWN pair, so a pooled visual can be re-issued immediately and
        /// must not respawn shrunken/transparent.
        /// </summary>
        public void ResetVisual()
        {
            StopAllCoroutines();
            Despawning = false;
            ItemId = null;
            ItemType = null;
            Count = 0;
            spriteRenderer.sprite = null;
            spriteRenderer.color = normalColor;
            transform.localScale = Vector3.one;
            gameObject.SetActive(false);
        }

        /// <summary>
        /// Play the despawn tween, then hand the visual back via onDone (the manager pools
        /// it). magnetTarget != null = picked up by the local player: fly into them while
        /// shrinking (the E-pickup magnet). null = a plain remove: quick shrink-fade.
        /// </summary>
        public void Despawn(Vector3? magnetTarget, System.Action onDone)
        {
            if (Despawning) { onDone?.Invoke(); return; }
            if (!gameObject.activeInHierarchy) { onDone?.Invoke(); return; }
            Despawning = true;
            StartCoroutine(DespawnRoutine(magnetTarget, onDone));
        }

        private System.Collections.IEnumerator DespawnRoutine(Vector3? magnetTarget, System.Action onDone)
        {
            float duration = magnetTarget.HasValue ? 0.15f : 0.1f;
            Vector3 startPos = transform.position;
            Vector3 startScale = transform.localScale;
            Color startColor = spriteRenderer.color;

            for (float t = 0f; t < duration; t += Time.deltaTime)
            {
                float k = t / duration;
                if (magnetTarget.HasValue)
                {
                    // Ease-in toward the player: slow start, fast arrival (magnet feel)
                    transform.position = Vector3.Lerp(startPos, magnetTarget.Value, k * k);
                }
                else
                {
                    var c = startColor;
                    c.a = 1f - k;
                    spriteRenderer.color = c;
                }
                transform.localScale = startScale * (1f - 0.8f * k);
                yield return null;
            }

            onDone?.Invoke(); // ResetVisual restores scale/alpha/flag before pooling
        }

        /// <summary>
        /// Set highlight state for hover/proximity feedback.
        /// </summary>
        public void SetHighlight(bool highlighted)
        {
            spriteRenderer.color = highlighted ? highlightColor : normalColor;
        }

        private void Update()
        {
            if (Despawning) return; // the despawn tween owns the transform

            // Sinusoidal bob animation
            float bob = Mathf.Sin((Time.time * bobFrequency) + bobOffset) * bobAmplitude;
            transform.position = basePosition + new Vector3(0f, bob, 0f);
        }
    }
}
