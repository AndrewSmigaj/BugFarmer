using UnityEngine;
using Nakama;
using BugFarmer.Networking;

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

        private Rigidbody2D _rb;
        private SpriteRenderer _spriteRenderer;

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
        }

        private void Update()
        {
            // Read input
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            // Calculate velocity
            Vector2 input = new Vector2(horizontal, vertical);
            if (input.sqrMagnitude > 1f)
                input.Normalize();

            Velocity = input * moveSpeed;

            // Update facing direction based on dominant axis
            UpdateFacing(horizontal, vertical);

            // Send position to server
            TrySendMovement();
        }

        private void FixedUpdate()
        {
            if (_rb != null)
            {
                _rb.linearVelocity = Velocity;
            }
            else
            {
                transform.position += (Vector3)Velocity * Time.fixedDeltaTime;
            }
        }

        private void UpdateFacing(float h, float v)
        {
            // Only update facing if there's input
            if (Mathf.Abs(h) < 0.01f && Mathf.Abs(v) < 0.01f)
                return;

            Direction newFacing;
            // Prioritize horizontal if both pressed equally, else use dominant
            if (Mathf.Abs(h) >= Mathf.Abs(v))
            {
                newFacing = h > 0 ? Direction.Right : Direction.Left;
            }
            else
            {
                newFacing = v > 0 ? Direction.Up : Direction.Down;
            }

            if (newFacing != Facing)
            {
                Facing = newFacing;
                UpdateSprite();
            }
        }

        private void UpdateSprite()
        {
            if (_spriteRenderer != null && directionSprites != null &&
                (int)Facing < directionSprites.Length && directionSprites[(int)Facing] != null)
            {
                _spriteRenderer.sprite = directionSprites[(int)Facing];
            }
        }

        private void TrySendMovement()
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return;

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return;

            bool isMoving = Velocity.sqrMagnitude > 0.01f;
            bool stateChanged = isMoving != _wasMoving || Facing != _lastSentFacing;
            bool intervalElapsed = Time.time - _lastSendTime >= SendInterval;

            // Send on: state change OR interval elapsed while moving
            if (stateChanged || (isMoving && intervalElapsed))
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
