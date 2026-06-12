using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Base component for networked entities (players, bugs, etc.).
    /// Handles position interpolation, sprite direction updates, and the equipped-tool
    /// display (held at rest + swing replays via the attached PlayerToolAnimator).
    /// </summary>
    public class RemoteEntity : MonoBehaviour
    {
        [SerializeField] private Sprite[] directionSprites; // 0=Down, 1=Left, 2=Right, 3=Up

        private const float InterpDuration = 0.15f; // 150ms
        private const float WalkFps = 7f;
        private SpriteRenderer _spriteRenderer;
        private Vector2 _startPos;
        private Vector2 _targetPos;
        private float _interpProgress = 1f; // Start complete (no interpolation until first update)
        private Player.PlayerToolAnimator _toolAnimator;
        private string _equipped;

        // Walk frames [dir][contact, idle, contact, idle] (baked farmer set);
        // falls back to the static directionSprites when frames are missing.
        private Sprite[][] _frames;
        private float _walkClock;
        private int _frameIndex = 1;

        public string EntityId { get; set; }
        public Direction Facing { get; private set; } = Direction.Down;
        /// <summary>Last-known equipped item id (from EntityData.eq); "" = bare hand.</summary>
        public string Equipped => _equipped ?? "";
        /// <summary>The remote player's tool animator (swing replays).</summary>
        public Player.PlayerToolAnimator ToolAnimator => _toolAnimator;

        private void Awake()
        {
            _spriteRenderer = GetComponent<SpriteRenderer>();

            // Held-at-rest display + swing replays (the animator depends only on this
            // sibling SpriteRenderer; sorting is owned in its code).
            _toolAnimator = GetComponent<Player.PlayerToolAnimator>();
            if (_toolAnimator == null)
                _toolAnimator = gameObject.AddComponent<Player.PlayerToolAnimator>();

            // Set sorting layer for proper rendering with Y-sorting
            if (_spriteRenderer != null)
            {
                _spriteRenderer.sortingLayerName = "Occupants";
                World.LitMaterials.Apply(_spriteRenderer); // receive day/night lighting
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

            // Walk frames (idle + _w1/_w3); remote players animate while lerping.
            _frames = Player.CharacterComposer.LoadBaked("farmer");
        }

        private void Update()
        {
            // Walking = interpolation in progress over a non-trivial distance.
            bool walking = _interpProgress < 1f &&
                           (_targetPos - _startPos).sqrMagnitude > 0.0004f;
            int frame = 1;
            if (walking)
            {
                _walkClock += Time.deltaTime * WalkFps;
                frame = (int)_walkClock % 4;
            }
            else
            {
                _walkClock = 0f;
            }
            if (frame != _frameIndex)
            {
                _frameIndex = frame;
                UpdateSprite();
            }

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
            if (_spriteRenderer == null) return;
            var s = _frames != null ? _frames[(int)Facing][_frameIndex] : null;
            if (s == null && directionSprites != null &&
                (int)Facing < directionSprites.Length)
                s = directionSprites[(int)Facing];
            if (s != null)
                _spriteRenderer.sprite = s;
        }

        private string _armor;

        /// <summary>
        /// Set the remote player's WORN ARMOR (EntityData.eqa: 7 comma-joined
        /// slot ids, "" = naked). Change-checked; re-composes the paper-doll
        /// outfit (baked farmer fallback when layers are unavailable).
        /// </summary>
        public void SetArmor(string eqa)
        {
            eqa ??= "";
            if (eqa == _armor) return;
            _armor = eqa;

            if (!Player.CharacterComposer.ComposedOutfitsEnabled)
                return; // trial: stay on the baked vector-Scout frames

            Sprite[][] composed = null;
            if (eqa.Length > 0)
            {
                var outfit = Player.CharacterComposer.OutfitFromEquipment(eqa.Split(','));
                composed = Player.CharacterComposer.Compose(outfit);
            }
            _frames = composed ?? Player.CharacterComposer.LoadBaked("farmer");
            UpdateSprite();
        }

        /// <summary>
        /// Set the remote player's equipped item (arrives every tick via EntityData.eq —
        /// null when absent/bare-handed). Change-checked: no per-tick sprite lookups.
        /// Unknown ids show nothing (EquipTool relays arbitrary client strings).
        /// </summary>
        public void SetEquipped(string itemId)
        {
            itemId ??= ""; // omitempty + JsonUtility => null, not ""
            if (itemId == _equipped) return;
            _equipped = itemId;

            if (_toolAnimator == null) return;
            var def = EntityDatabase.Get(itemId);
            if (def?.ToolType != null && def.ToolType != "hands")
                _toolAnimator.SetIdleItem(def.ToolType, EntityDatabase.GetItemSprite(itemId));
            else
                _toolAnimator.SetIdleItem(null, null); // bare hand / hands tool / non-tool
        }
    }
}
