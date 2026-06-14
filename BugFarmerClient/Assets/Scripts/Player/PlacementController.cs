using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles player placement of objects from inventory into the world.
    /// Shows ghost preview when holding a placeable item.
    /// Right-click to place, R to rotate.
    /// </summary>
    public class PlacementController : MonoBehaviour
    {
        [Header("Ghost Preview")]
        [SerializeField] private SpriteRenderer ghostPreview;
        [SerializeField] private Color validColor = new Color(0f, 1f, 0f, 0.5f);
        [SerializeField] private Color invalidColor = new Color(1f, 0f, 0f, 0.5f);

        [Header("Settings")]
        [SerializeField] private float maxPlaceDistance = 4f;

        private string _currentPlaceableId;
        private int _placementDirection;
        private bool _isPlacing;
        private bool _cursorMode;       // placing FROM the drag cursor (panel item)
        private int _cursorSourceSlot;  // the cursor stack's server-side home slot
        private Camera _mainCamera;

        private void Start()
        {
            _mainCamera = Camera.main;

            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnSelectedSlotChanged += OnSlotChanged;
                InventoryManager.Instance.OnInventoryChanged += OnInventoryChanged;
            }

            if (ghostPreview != null)
                ghostPreview.gameObject.SetActive(false);
        }

        private void OnDestroy()
        {
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnSelectedSlotChanged -= OnSlotChanged;
                InventoryManager.Instance.OnInventoryChanged -= OnInventoryChanged;
            }
        }

        private void Update()
        {
            UpdatePlacementMode();

            if (_isPlacing)
            {
                UpdateGhostPreview();

                // R to rotate (right-click placement arrives via PlayerInputRouter)
                if (Input.GetKeyDown(KeyCode.R))
                {
                    _placementDirection = (_placementDirection + 1) % 4;
                }
            }
        }

        /// <summary>
        /// Handle a routed right-click (PlayerInputRouter owns right-click). MODE-BASED, not
        /// success-based: returns true whenever placing mode is active — even when the spot
        /// is invalid (red ghost) — because a misclicked placement must NEVER fall through
        /// to a weapon jab. Returns false only when not in placing mode at all.
        /// </summary>
        public bool TryHandleRightClick()
        {
            if (!_isPlacing) return false;
            TryPlace();
            return true;
        }

        private void OnSlotChanged(int slot) => UpdatePlacementMode();
        private void OnInventoryChanged() => UpdatePlacementMode();

        private void UpdatePlacementMode()
        {
            // CURSOR-EXCLUSIVE resolution: while the drag cursor holds anything, the
            // equipped-item fallback is disabled (dragging a sword while dirt is hotbar-
            // selected must not leave an equipped-mode ghost that right-click places).
            // Cursor item placeable -> cursor-place mode; cursor non-placeable -> no ghost.
            string itemId;
            var drag = DragDropController.Instance;
            if (drag != null && drag.HasCursorItem)
            {
                bool cursorPlaceable = drag.CursorSourceType == SlotType.Item &&
                                       EntityDatabase.IsPlaceable(drag.CursorItemId);
                itemId = cursorPlaceable ? drag.CursorItemId : "";
                _cursorMode = cursorPlaceable;
                _cursorSourceSlot = drag.CursorSourceIndex;
            }
            else
            {
                itemId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
                _cursorMode = false;
            }
            // "placer" tools (torch) place on LEFT-click with no ghost (PlayerInputRouter ->
            // PlaceEquippedNow); keep them OUT of the generic ghost/right-click placing mode.
            bool isPlaceable = !string.IsNullOrEmpty(itemId) && EntityDatabase.IsPlaceable(itemId)
                               && EntityDatabase.Get(itemId)?.ToolType != "placer";

            if (isPlaceable && itemId != _currentPlaceableId)
            {
                _currentPlaceableId = itemId;
                _isPlacing = true;
                _placementDirection = 0;

                if (ghostPreview != null)
                {
                    // For seeds, show the plant sprite instead of seed sprite
                    string spriteId = itemId;
                    var def = EntityDatabase.Get(itemId);
                    if (def != null && !string.IsNullOrEmpty(def.PlacesCrop))
                    {
                        spriteId = "plant_" + def.PlacesCrop;
                    }

                    ghostPreview.sprite = EntityDatabase.GetWorldSprite(spriteId);

                    // Scale ghost to match target size
                    var targetSize = EntityDatabase.GetSpriteSize(spriteId);
                    var sprite = ghostPreview.sprite;
                    if (sprite != null)
                    {
                        float scaleX = targetSize.x / sprite.rect.width;
                        float scaleY = targetSize.y / sprite.rect.height;
                        ghostPreview.transform.localScale = new Vector3(scaleX, scaleY, 1f);
                    }

                    ghostPreview.gameObject.SetActive(true);
                }
            }
            else if (!isPlaceable && _isPlacing)
            {
                _currentPlaceableId = null;
                _isPlacing = false;
                if (ghostPreview != null)
                    ghostPreview.gameObject.SetActive(false);
            }
        }

        private void UpdateGhostPreview()
        {
            if (ghostPreview == null || TilemapManager.Instance == null || _mainCamera == null)
                return;

            // Cursor mode: the ghost lives over the WORLD only — over UI the drag-cursor
            // icon is the feedback (a ghost under the inventory panel just reads as noise).
            if (_cursorMode)
            {
                bool overUI = UnityEngine.EventSystems.EventSystem.current != null &&
                              UnityEngine.EventSystems.EventSystem.current.IsPointerOverGameObject();
                ghostPreview.enabled = !overUI;
                if (overUI) return;
            }
            else if (!ghostPreview.enabled)
            {
                ghostPreview.enabled = true; // don't inherit a cursor-mode over-UI hide
            }

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;
            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);
            ghostPreview.transform.position = TilemapManager.Instance.CellToWorld(cellPos);
            ghostPreview.color = CanPlaceAt(cellPos) ? validColor : invalidColor;
        }

        private bool CanPlaceAt(Vector2Int cellPos) =>
            CanPlaceAt(_currentPlaceableId, _placementDirection, cellPos);

        private bool CanPlaceAt(string placeableId, int direction, Vector2Int cellPos)
        {
            if (TilemapManager.Instance == null)
                return false;

            Vector3 cellWorld = TilemapManager.Instance.CellToWorld(cellPos);
            if (Vector3.Distance(transform.position, cellWorld) > maxPlaceDistance)
                return false;

            // Seeds can only be placed on garden_plot tiles
            var def = EntityDatabase.Get(placeableId);
            if (def != null && !string.IsNullOrEmpty(def.PlacesCrop))
            {
                string groundTile = TilemapManager.Instance.GetGroundAt(cellPos);
                if (groundTile != "garden_plot" && groundTile != "garden_plot_wet")
                    return false;
            }

            Vector2Int size = EntityDatabase.GetFootprint(placeableId, direction);
            for (int dy = 0; dy < size.y; dy++)
            {
                for (int dx = 0; dx < size.x; dx++)
                {
                    if (TilemapManager.Instance.IsCellOccupied(new Vector2Int(cellPos.x + dx, cellPos.y + dy)))
                        return false;
                }
            }
            return true;
        }

        private void TryPlace()
        {
            if (TilemapManager.Instance == null || _mainCamera == null)
                return;

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;
            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);

            if (!CanPlaceAt(cellPos))
                return;

            SendPlace(_currentPlaceableId, cellPos, _placementDirection, _cursorMode, _cursorSourceSlot);
        }

        /// <summary>
        /// Left-click placement for "placer" tools (e.g. torch): place the EQUIPPED occupant at the
        /// mouse cell immediately — no ghost, no placing-mode. Called by PlayerInputRouter on a
        /// left-click when the equipped tool_type is "placer".
        /// </summary>
        public void PlaceEquippedNow()
        {
            if (TilemapManager.Instance == null || _mainCamera == null)
                return;
            string itemId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            if (string.IsNullOrEmpty(itemId) || !EntityDatabase.IsPlaceable(itemId))
                return;

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;
            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);
            if (!CanPlaceAt(itemId, 0, cellPos))
                return;

            SendPlace(itemId, cellPos, 0, cursorMode: false, sourceSlot: 0);
        }

        /// <summary>The single send path: TilePlace (or TilePlaceFromSlot in cursor mode).</summary>
        private void SendPlace(string occupantId, Vector2Int cellPos, int direction,
                               bool cursorMode, int sourceSlot)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || !socket.IsConnected || match == null)
            {
                Debug.LogWarning("[PlacementController] Socket not connected, cannot place");
                return;
            }

            // Send the item ID as-is - server handles seed->plant conversion.
            // Cursor mode names its source slot (separate message class: the field must
            // only exist on the wire when it means something — server-side it's a *int).
            string json;
            if (cursorMode)
            {
                json = JsonUtility.ToJson(new TilePlaceFromSlotMessage
                {
                    grid_x = cellPos.x,
                    grid_y = cellPos.y,
                    occupant_id = occupantId,
                    direction = direction,
                    source_slot = sourceSlot
                });
            }
            else
            {
                json = JsonUtility.ToJson(new TilePlaceMessage
                {
                    grid_x = cellPos.x,
                    grid_y = cellPos.y,
                    occupant_id = occupantId,
                    direction = direction
                });
            }
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.TilePlace, json);
            Debug.Log($"[PlacementController] Placing {occupantId} at ({cellPos.x}, {cellPos.y}) cursorMode={cursorMode}");
        }

        public bool IsPlacing => _isPlacing;
    }
}
