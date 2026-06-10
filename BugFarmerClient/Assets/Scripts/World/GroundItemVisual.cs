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
            // a 16x24 plant), so uniformly fit within 0.75 cell preserving aspect — clearly a
            // pickup, never rivaling placed occupants. Never upscale small icons above 1x.
            const float maxCells = 0.75f;
            float scale = 1f;
            if (sprite != null)
            {
                // World size in cells at the sprite's own PPU (icons & objects are PPU 16 = 1 cell).
                float w = sprite.rect.width / sprite.pixelsPerUnit;
                float h = sprite.rect.height / sprite.pixelsPerUnit;
                scale = Mathf.Min(1f, maxCells / Mathf.Max(w, h));
            }
            transform.localScale = new Vector3(scale, scale, 1f);

            // Randomize bob phase so items don't sync
            bobOffset = Random.Range(0f, Mathf.PI * 2f);

            gameObject.SetActive(true);
        }

        /// <summary>
        /// Reset for object pooling.
        /// </summary>
        public void ResetVisual()
        {
            ItemId = null;
            ItemType = null;
            Count = 0;
            spriteRenderer.sprite = null;
            spriteRenderer.color = normalColor;
            gameObject.SetActive(false);
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
            // Sinusoidal bob animation
            float bob = Mathf.Sin((Time.time * bobFrequency) + bobOffset) * bobAmplitude;
            transform.position = basePosition + new Vector3(0f, bob, 0f);
        }
    }
}
