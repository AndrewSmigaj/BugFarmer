using UnityEngine;
using BugFarmer.Networking;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Base component for networked entities (players, bugs, etc.).
    /// Handles position interpolation and sprite direction updates.
    /// </summary>
    public class RemoteEntity : MonoBehaviour
    {
        [SerializeField] private Sprite[] directionSprites; // 0=Down, 1=Left, 2=Right, 3=Up

        private const float InterpDuration = 0.15f; // 150ms
        private SpriteRenderer _spriteRenderer;
        private Vector2 _startPos;
        private Vector2 _targetPos;
        private float _interpProgress = 1f; // Start complete (no interpolation until first update)

        public string EntityId { get; set; }
        public Direction Facing { get; private set; } = Direction.Down;

        private void Awake()
        {
            _spriteRenderer = GetComponent<SpriteRenderer>();

            // Set sorting layer for proper rendering with Y-sorting
            if (_spriteRenderer != null)
            {
                _spriteRenderer.sortingLayerName = "Occupants";
            }

            // Load sprites from Resources if not assigned in prefab
            if (directionSprites == null || directionSprites.Length == 0)
            {
                directionSprites = new Sprite[4];
                directionSprites[0] = Resources.Load<Sprite>("Player/farmer_down");
                directionSprites[1] = Resources.Load<Sprite>("Player/farmer_left");
                directionSprites[2] = Resources.Load<Sprite>("Player/farmer_right");
                directionSprites[3] = Resources.Load<Sprite>("Player/farmer_up");

                if (directionSprites[0] != null)
                {
                    Debug.Log("[RemoteEntity] Loaded farmer sprites from Resources/Player/");
                }
                else
                {
                    Debug.LogWarning("[RemoteEntity] No farmer sprites found in Resources/Player/");
                }
            }
        }

        private void Update()
        {
            if (_interpProgress < 1f)
            {
                _interpProgress = Mathf.Min(_interpProgress + Time.deltaTime / InterpDuration, 1f);
                Vector2 newPos = Vector2.Lerp(_startPos, _targetPos, _interpProgress);
                transform.position = new Vector3(newPos.x, newPos.y, transform.position.z);

                // Y-sort by the FEET, not the sprite centre. The character sprite is centre-pivoted
                // (16x32 = 1x2 cells), so the feet are a cell below transform.position; bounds.min.y is
                // the rendered sprite's bottom in world space (matches occupants' -cellPos.y = their feet).
                if (_spriteRenderer != null && _spriteRenderer.sprite != null)
                {
                    _spriteRenderer.sortingOrder = -Mathf.FloorToInt(_spriteRenderer.bounds.min.y);
                }
            }
        }

        /// <summary>
        /// Called by EntityManager when new state arrives from server.
        /// </summary>
        public void SetTargetState(float x, float y, int facing)
        {
            // Restart interpolation from current position
            _startPos = transform.position;
            _targetPos = new Vector2(x, y);
            _interpProgress = 0f;

            // Update facing and sprite
            Facing = (Direction)facing;
            UpdateSprite();
        }

        private void UpdateSprite()
        {
            if (_spriteRenderer != null && directionSprites != null &&
                (int)Facing < directionSprites.Length && directionSprites[(int)Facing] != null)
            {
                _spriteRenderer.sprite = directionSprites[(int)Facing];
            }
        }
    }
}
