using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles player breaking/mining of world objects.
    /// Right-click on a breakable occupant to mine it.
    /// Server validates tool requirements and tracks breaking progress.
    /// </summary>
    public class BreakingController : MonoBehaviour
    {
        [Header("Settings")]
        [Tooltip("Time between break messages sent to server")]
        [SerializeField] private float breakClickInterval = 0.25f;

        [Tooltip("Maximum distance from player to break an object")]
        [SerializeField] private float maxBreakDistance = 4f;

        private Vector2Int? _breakingCell;
        private float _lastBreakTime;
        private bool _isBreaking;
        private Camera _mainCamera;

        private void Start()
        {
            _mainCamera = Camera.main;
        }

        private void Update()
        {
            // Left-click to break/mine when holding a tool
            if (Input.GetMouseButton(0))
            {
                TryBreak();
            }
            else if (_isBreaking)
            {
                StopBreaking();
            }
        }

        private void TryBreak()
        {
            if (TilemapManager.Instance == null || _mainCamera == null)
                return;

            // Get cell under mouse
            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;
            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);

            // Check distance from player
            Vector3 cellWorld = TilemapManager.Instance.CellToWorld(cellPos);
            if (Vector3.Distance(transform.position, cellWorld) > maxBreakDistance)
            {
                StopBreaking();
                return;
            }

            // Check if there's something to break at this cell
            if (!TilemapManager.Instance.IsCellOccupied(cellPos))
            {
                StopBreaking();
                return;
            }

            // Check if we have a tool equipped (not a placeable item)
            // Server will validate tool requirements - wrong tool = no action
            string equippedItem = InventoryManager.Instance?.GetEquippedToolId() ?? "";

            // Skip if holding a placeable item (placement uses different input)
            if (!string.IsNullOrEmpty(equippedItem) && TileDatabase.Instance?.IsPlaceable(equippedItem) == true)
            {
                StopBreaking();
                return;
            }

            // Check if target changed
            if (_breakingCell != cellPos)
            {
                _breakingCell = cellPos;
                _lastBreakTime = 0; // Reset timer for new target
            }

            _isBreaking = true;

            // Send break message at interval
            if (Time.time - _lastBreakTime >= breakClickInterval)
            {
                SendBreakRequest(cellPos);
                _lastBreakTime = Time.time;
            }
        }

        private void StopBreaking()
        {
            _isBreaking = false;
            _breakingCell = null;
        }

        private void SendBreakRequest(Vector2Int cellPos)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || match == null)
                return;

            var msg = new TileBreakMessage
            {
                grid_x = cellPos.x,
                grid_y = cellPos.y
            };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.TileBreak, json);
        }

        /// <summary>
        /// Check if currently breaking something.
        /// </summary>
        public bool IsBreaking => _isBreaking;

        /// <summary>
        /// Get the cell currently being broken, or null if not breaking.
        /// </summary>
        public Vector2Int? BreakingCell => _breakingCell;
    }
}
