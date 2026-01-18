using UnityEngine;
using BugFarmer.Data;
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

        [Tooltip("Maximum distance from player to break an object (Terraria-style reach)")]
        [SerializeField] private float maxBreakDistance = 8f;

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
            if (_mainCamera == null)
                return;

            // Skip if equipped tool is a farming tool (handled by ToolUseController)
            string toolId = InventoryManager.Instance?.GetEquippedToolId();
            if (!string.IsNullOrEmpty(toolId))
            {
                var toolDef = EntityDatabase.Get(toolId);
                if (toolDef != null && (toolDef.ToolType == "hoe" || toolDef.ToolType == "watering_can"))
                {
                    StopBreaking();
                    return;
                }
            }

            // Get world position under mouse
            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;

            // Find occupant collider at mouse position
            Collider2D hitCollider = Physics2D.OverlapPoint(mouseWorld);
            if (hitCollider == null)
            {
                // Debug: show what's under cursor when clicking on empty space
                if (Input.GetMouseButtonDown(0))
                {
                    Debug.Log($"[BreakingController] No collider at {mouseWorld}");
                }
                StopBreaking();
                return;
            }

            // Get click target component for occupant metadata
            var clickTarget = hitCollider.GetComponent<OccupantClickTarget>();
            if (clickTarget == null || !clickTarget.IsBreakable)
            {
                if (Input.GetMouseButtonDown(0))
                {
                    Debug.Log($"[BreakingController] Hit {hitCollider.name} but no OccupantClickTarget or not breakable");
                }
                StopBreaking();
                return;
            }

            // Use anchor cell from click target (bottom-left of footprint)
            Vector2Int anchorCell = clickTarget.AnchorCell;

            // Check distance from player to anchor cell
            if (TilemapManager.Instance != null)
            {
                Vector3 cellWorld = TilemapManager.Instance.CellToWorld(anchorCell);
                if (Vector3.Distance(transform.position, cellWorld) > maxBreakDistance)
                {
                    StopBreaking();
                    return;
                }
            }

            // Check if we have a tool equipped (not a placeable item)
            // Server will validate tool requirements - wrong tool = no action
            string equippedItem = InventoryManager.Instance?.GetEquippedToolId() ?? "";

            // Skip if holding a placeable item (placement uses different input)
            if (!string.IsNullOrEmpty(equippedItem) && EntityDatabase.IsPlaceable(equippedItem))
            {
                StopBreaking();
                return;
            }

            // Check if target changed
            if (_breakingCell != anchorCell)
            {
                _breakingCell = anchorCell;
                _lastBreakTime = 0; // Reset timer for new target
            }

            _isBreaking = true;

            // Send break message at interval
            if (Time.time - _lastBreakTime >= breakClickInterval)
            {
                SendBreakRequest(anchorCell);
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
