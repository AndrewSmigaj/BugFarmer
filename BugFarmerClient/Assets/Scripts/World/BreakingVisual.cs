using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Visual feedback for breaking/mining progress.
    /// Displays crack overlay sprites as HP decreases.
    /// Requires break stage sprites to be assigned in TileDatabase or prefab.
    /// </summary>
    public class BreakingVisual : MonoBehaviour
    {
        private static Sprite[] _breakStages;
        private SpriteRenderer _renderer;
        private float _progress = 1f;

        /// <summary>
        /// Set the shared break stage sprites for all BreakingVisual instances.
        /// Call this once during initialization with sprites loaded from Resources.
        /// </summary>
        public static void SetBreakStages(Sprite[] sprites)
        {
            _breakStages = sprites;
        }

        private void Awake()
        {
            _renderer = GetComponent<SpriteRenderer>();
            if (_renderer == null)
            {
                _renderer = gameObject.AddComponent<SpriteRenderer>();
            }
            // Render above occupants - must be on same sorting layer
            _renderer.sortingLayerName = "Occupants";
            _renderer.sortingOrder = 1000; // High value to render on top of all occupants
            // Semi-transparent overlay
            _renderer.color = new Color(1f, 1f, 1f, 0.9f);
        }

        /// <summary>
        /// Set the breaking progress (0 = fully broken, 1 = full HP).
        /// </summary>
        public void SetProgress(float progress)
        {
            _progress = Mathf.Clamp01(progress);

            if (_breakStages == null || _breakStages.Length == 0)
            {
                Debug.LogWarning("[BreakingVisual] No break stage sprites set. Call SetBreakStages() first.");
                return;
            }

            // Calculate damage percentage (inverse of progress)
            float damagePercent = 1f - _progress;

            // Select stage: 0% damage = stage 0, ~100% damage = last stage
            int stageIndex = Mathf.FloorToInt(damagePercent * _breakStages.Length);
            stageIndex = Mathf.Clamp(stageIndex, 0, _breakStages.Length - 1);

            var sprite = _breakStages[stageIndex];
            if (sprite == null)
            {
                Debug.LogWarning($"[BreakingVisual] Break stage sprite {stageIndex} is null!");
                return;
            }

            _renderer.sprite = sprite;
            _renderer.enabled = true;
            Debug.Log($"[BreakingVisual] Set stage {stageIndex} (damage {damagePercent:P0}), sprite: {sprite.name}");
        }

        /// <summary>
        /// Get the current progress value.
        /// </summary>
        public float Progress => _progress;
    }
}
