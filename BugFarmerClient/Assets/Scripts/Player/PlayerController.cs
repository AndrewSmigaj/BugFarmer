using UnityEngine;
using UnityEngine.EventSystems;
using Nakama;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles local player movement and facing direction.
    /// Movement is in world units (1 unit = 1 block = 8 pixels at PPU 8).
    /// Requires Rigidbody2D set to Kinematic for physics-based movement.
    /// Sends position updates to server via NetworkManager.
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [SerializeField] private float moveSpeed = 5f; // Blocks per second
        [SerializeField] private Sprite[] directionSprites; // 0=Down, 1=Left, 2=Right, 3=Up

        public Direction Facing { get; private set; } = Direction.Down;
        public Vector2 Velocity { get; private set; }

        // Walk animation: [dir][frame] with frame order [contact, idle, contact, idle].
        // Composed via CharacterComposer (paper-doll layers) or LoadBaked; falls back
        // to the static directionSprites when neither is available.
        private const float WalkFps = 7f;
        private Sprite[][] _frames;
        private float _walkClock;
        private int _frameIndex = 1;

        private Rigidbody2D _rb;
        private SpriteRenderer _spriteRenderer;
        private Camera _mainCamera;

        // Movement sending state
        private const float SendInterval = 0.1f; // 100ms
        private float _lastSendTime;
        private Direction _lastSentFacing;
        private bool _wasMoving;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            _spriteRenderer = GetComponent<SpriteRenderer>();
            if (_rb == null)
            {
                Debug.LogWarning("[PlayerController] No Rigidbody2D found. Using transform movement.");
            }

            // Set sorting layer for proper rendering with Y-sorting
            if (_spriteRenderer != null)
            {
                _spriteRenderer.sortingLayerName = "Occupants";
            }

            // Code-attached player systems (controllers are split between Player.prefab and
            // scene-added components — attaching these in code sidesteps both):
            // the in-hand tool animator and the single left-click owner.
            if (GetComponent<PlayerToolAnimator>() == null)
                gameObject.AddComponent<PlayerToolAnimator>();
            if (GetComponent<MeleeController>() == null)
                gameObject.AddComponent<MeleeController>();
            if (GetComponent<BugReleaseController>() == null)
                gameObject.AddComponent<BugReleaseController>();
            if (GetComponent<TreeHarvestController>() == null)
                gameObject.AddComponent<TreeHarvestController>();
            if (GetComponent<PlayerHealth>() == null)
                gameObject.AddComponent<PlayerHealth>();
            if (GetComponent<PlayerInputRouter>() == null)
                gameObject.AddComponent<PlayerInputRouter>();
        }

        private PlayerToolAnimator _toolAnimator;

        private void Start()
        {
            // Held-at-rest display: show the equipped tool in-hand whenever it changes.
            _toolAnimator = GetComponent<PlayerToolAnimator>();
            var inv = InventoryManager.Instance;
            if (inv != null)
            {
                inv.OnSelectedSlotChanged += OnEquipMaybeChanged;
                inv.OnItemSlotChanged += OnEquipMaybeChanged;
                inv.OnInventoryChanged += RefreshHeldItem;
                RefreshHeldItem();
            }

            // Walk frames: composed from the worn equipment (server echoes it
            // on join); baked farmer until then / as fallback.
            _frames = CharacterComposer.LoadBaked("farmer");
            UpdateSprite();
            if (inv != null)
                inv.OnEquipmentChanged += RebuildOutfit;
        }

        // ---- worn armor: re-compose the LOCAL player when equipment changes
        // (the open-center inventory layout exists so you SEE this happen).
        private void RebuildOutfit()
        {
            var inv = InventoryManager.Instance;
            var outfit = CharacterComposer.OutfitFromEquipment(inv?.Equipment);
            var composed = CharacterComposer.Compose(outfit);
            if (composed == null)
            {
                Debug.LogWarning("[PlayerController] outfit compose failed (layers missing " +
                                 "or not CPU-readable — run tools/fix_sprite_ppu.py); baked fallback.");
                composed = CharacterComposer.LoadBaked("farmer");
                if (composed == null) return;
            }
            _frames = composed;
            UpdateSprite();
        }

        private void OnDestroy()
        {
            var inv = InventoryManager.Instance;
            if (inv != null)
            {
                inv.OnSelectedSlotChanged -= OnEquipMaybeChanged;
                inv.OnItemSlotChanged -= OnEquipMaybeChanged;
                inv.OnInventoryChanged -= RefreshHeldItem;
                inv.OnEquipmentChanged -= RebuildOutfit;
            }
        }

        private void OnEquipMaybeChanged(int _) => RefreshHeldItem();

        private void RefreshHeldItem()
        {
            if (_toolAnimator == null) return;
            string id = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            var def = EntityDatabase.Get(id);
            // v1 gating: TOOLS only (a held torch already shows via its personal light;
            // placeables show the ghost instead). HANDS show nothing in-hand — the slot
            // icon is the affordance, the hand itself is the tool.
            if (def?.ToolType != null && def.ToolType != "hands")
                _toolAnimator.SetIdleItem(def.ToolType, EntityDatabase.GetItemSprite(id));
            else
                _toolAnimator.SetIdleItem(null, null);
        }

        private void Update()
        {
            // Don't move until we've joined a match
            if (WorldManager.Instance?.CurrentMatch == null)
            {
                Velocity = Vector2.zero;
                return;
            }

            // Skip input when typing in UI
            if (EventSystem.current != null && EventSystem.current.currentSelectedGameObject != null)
            {
                Velocity = Vector2.zero;
                return;
            }

            // Read input
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            // Calculate velocity
            Vector2 input = new Vector2(horizontal, vertical);
            if (input.sqrMagnitude > 1f)
                input.Normalize();

            Velocity = input * moveSpeed;

            // Face the MOUSE, not the movement direction (aim-driven: press A while the
            // mouse points right and you run backwards). Movement never sets facing.
            UpdateFacingFromMouse();

            // Walk-cycle clock: cycle [contact, idle, contact, idle] while moving,
            // rest on the idle frame when still.
            int frame = 1;
            if (Velocity.sqrMagnitude > 0.01f)
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

            // Send position to server
            TrySendMovement();
        }

        private void FixedUpdate()
        {
            // Resolve movement against blocked cells (occupants with blocks_players, water) so solids
            // actually stop the player — slide along walls like the bug collision does.
            Vector3 current = transform.position;
            Vector3 proposed = current + (Vector3)Velocity * Time.fixedDeltaTime;
            Vector3 next = ResolveCollision(current, proposed);

            if (_rb != null)
            {
                _rb.MovePosition(next);
            }
            else
            {
                transform.position = next;
            }

            // Y-sort by the player's FEET (sprite is centre-pivoted, so feet are below transform.position).
            if (_spriteRenderer != null)
            {
                _spriteRenderer.sortingOrder = -Mathf.FloorToInt(FeetWorld(next).y);
            }
        }

        /// <summary>Block the player from entering cells with blocks_players occupants / impassable ground.
        /// Tries the full move, then X-only, then Y-only (wall slide), else stays put.</summary>
        private Vector3 ResolveCollision(Vector3 current, Vector3 proposed)
        {
            var tm = BugFarmer.World.TilemapManager.Instance;
            if (tm == null) return proposed;
            if (!FeetBlocked(tm, proposed)) return proposed;
            var xOnly = new Vector3(proposed.x, current.y, current.z);
            if (!FeetBlocked(tm, xOnly)) return xOnly;
            var yOnly = new Vector3(current.x, proposed.y, current.z);
            if (!FeetBlocked(tm, yOnly)) return yOnly;
            return current;
        }

        private bool FeetBlocked(BugFarmer.World.TilemapManager tm, Vector3 worldPos)
        {
            Vector2 feet = FeetWorld(worldPos);
            return tm.IsCellBlockedForPlayers(tm.WorldToCell(new Vector3(feet.x, feet.y, 0f)));
        }

        // The player's FEET = bottom-centre of the rendered sprite. The sprite is CENTER-pivoted, so the
        // feet sit below transform.position; derive the offset from the sprite bounds (pivot/size-agnostic)
        // so both collision and Y-sort use the true ground-contact point, not the sprite centre.
        private Vector2 FeetWorld(Vector3 pos)
        {
            if (_spriteRenderer == null || _spriteRenderer.sprite == null)
                return new Vector2(pos.x, pos.y);
            Bounds b = _spriteRenderer.bounds;
            float offX = b.center.x - transform.position.x;
            float offY = b.min.y - transform.position.y;
            return new Vector2(pos.x + offX, pos.y + offY);
        }

        private void UpdateFacingFromMouse()
        {
            // Freeze facing while the cursor is over UI — browsing the inventory
            // shouldn't spin the player.
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                return;

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return;
            }

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            float dx = mouseWorld.x - transform.position.x;
            float dy = mouseWorld.y - transform.position.y;

            // Quadrant by dominant axis (4-direction sprites); ties go horizontal.
            Direction newFacing = Mathf.Abs(dx) >= Mathf.Abs(dy)
                ? (dx > 0 ? Direction.Right : Direction.Left)
                : (dy > 0 ? Direction.Up : Direction.Down);

            if (newFacing != Facing)
            {
                Facing = newFacing;
                UpdateSprite();
            }
        }

        private void UpdateSprite()
        {
            if (_spriteRenderer == null) return;
            // Composed/baked frame set first; static directionSprites as the fallback.
            var s = _frames != null ? _frames[(int)Facing][_frameIndex] : null;
            if (s == null && directionSprites != null &&
                (int)Facing < directionSprites.Length)
                s = directionSprites[(int)Facing];
            if (s != null)
                _spriteRenderer.sprite = s;
        }

        private void TrySendMovement()
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return;

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return;

            bool isMoving = Velocity.sqrMagnitude > 0.01f;
            bool intervalElapsed = Time.time - _lastSendTime >= SendInterval;

            // Move-state changes send immediately; facing-only changes are rate-limited to
            // SendInterval (mouse-driven facing flips quadrants constantly while standing
            // still — don't spam a packet per flip).
            bool moveStateChanged = isMoving != _wasMoving;
            bool facingChanged = Facing != _lastSentFacing;

            if (moveStateChanged || (isMoving && intervalElapsed) || (facingChanged && intervalElapsed))
            {
                SendMovement(world.CurrentMatch.Id, socket);
                _wasMoving = isMoving;
            }
        }

        private void SendMovement(string matchId, ISocket socket)
        {
            var pos = (Vector2)transform.position;
            var msg = new MovementMessage { x = pos.x, y = pos.y, facing = (int)Facing };
            var json = JsonUtility.ToJson(msg);

            _ = socket.SendMatchStateAsync(matchId, OpCodes.Movement, json);

            _lastSentFacing = Facing;
            _lastSendTime = Time.time;
        }
    }
}
