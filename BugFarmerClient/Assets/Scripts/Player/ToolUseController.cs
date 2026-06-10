using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles farming tool use (hoe, watering can).
    /// Uses OpCode 7 (ToolUse) - separate from breaking/mining.
    /// </summary>
    public class ToolUseController : MonoBehaviour
    {
        [Header("Settings")]
        [Tooltip("Time between tool use messages (cooldown)")]
        [SerializeField] private float toolUseCooldown = 0.3f;

        [Tooltip("Maximum distance from player to use tool")]
        [SerializeField] private float maxToolDistance = 4f;

        private float _lastUseTime;
        private Camera _mainCamera;

        private void Start()
        {
            _mainCamera = Camera.main;
        }

        private void Update()
        {
            // Left-click when holding a farming tool
            if (Input.GetMouseButtonDown(0))
            {
                TryUseTool();
            }
        }

        private void TryUseTool()
        {
            // Check cooldown
            if (Time.time - _lastUseTime < toolUseCooldown)
                return;

            // Check if we have a farming tool equipped
            string toolId = InventoryManager.Instance?.GetEquippedToolId();
            if (string.IsNullOrEmpty(toolId))
            {
                Debug.Log("[ToolUseController] No tool equipped");
                return;
            }

            // Get tool definition to check if it's a farming tool
            var toolDef = EntityDatabase.Get(toolId);
            if (toolDef == null)
            {
                Debug.LogWarning($"[ToolUseController] Tool definition not found for: {toolId}");
                return;
            }

            string toolType = toolDef.ToolType;
            Debug.Log($"[ToolUseController] Tool {toolId} has type: {toolType}");

            // Only handle farming tools - other tools use BreakingController
            if (toolType != "hoe" && toolType != "watering_can" && toolType != "scythe")
            {
                Debug.Log($"[ToolUseController] Tool type {toolType} not handled (use BreakingController)");
                return;
            }

            if (_mainCamera == null)
                return;

            // Get world position under mouse
            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;

            // Convert to cell coordinates
            if (TilemapManager.Instance == null)
                return;

            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);

            // Check distance
            Vector3 cellWorld = TilemapManager.Instance.CellToWorld(cellPos);
            if (Vector3.Distance(transform.position, cellWorld) > maxToolDistance)
                return;

            // Send tool use message
            SendToolUse(cellPos);
            _lastUseTime = Time.time;
        }

        private void SendToolUse(Vector2Int cellPos)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || !socket.IsConnected || match == null)
            {
                Debug.LogWarning("[ToolUseController] Socket not connected, cannot send ToolUse");
                return;
            }

            var msg = new ToolUseMessage
            {
                grid_x = cellPos.x,
                grid_y = cellPos.y
            };

            string json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.ToolUse, json);

            Debug.Log($"[ToolUseController] Sent ToolUse at ({cellPos.x}, {cellPos.y})");
        }
    }
}
