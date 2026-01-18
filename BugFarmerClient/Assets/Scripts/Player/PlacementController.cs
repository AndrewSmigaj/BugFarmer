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

                // Right-click to place
                if (Input.GetMouseButtonDown(1))
                {
                    TryPlace();
                }

                // R to rotate
                if (Input.GetKeyDown(KeyCode.R))
                {
                    _placementDirection = (_placementDirection + 1) % 4;
                }
            }
        }

        private void OnSlotChanged(int slot) => UpdatePlacementMode();
        private void OnInventoryChanged() => UpdatePlacementMode();

        private void UpdatePlacementMode()
        {
            string itemId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            bool isPlaceable = !string.IsNullOrEmpty(itemId) && EntityDatabase.IsPlaceable(itemId);

            if (isPlaceable && itemId != _currentPlaceableId)
            {
                _currentPlaceableId = itemId;
                _isPlacing = true;
                _placementDirection = 0;

                if (ghostPreview != null)
                {
                    ghostPreview.sprite = EntityDatabase.GetWorldSprite(itemId);

                    // Scale ghost to match target size
                    var targetSize = EntityDatabase.GetSpriteSize(itemId);
                    var sprite = ghostPreview.sprite;
                    float scaleX = targetSize.x / sprite.rect.width;
                    float scaleY = targetSize.y / sprite.rect.height;
                    ghostPreview.transform.localScale = new Vector3(scaleX, scaleY, 1f);

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

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;
            Vector2Int cellPos = TilemapManager.Instance.WorldToCell(mouseWorld);
            ghostPreview.transform.position = TilemapManager.Instance.CellToWorld(cellPos);
            ghostPreview.color = CanPlaceAt(cellPos) ? validColor : invalidColor;
        }

        private bool CanPlaceAt(Vector2Int cellPos)
        {
            if (TilemapManager.Instance == null)
                return false;

            Vector3 cellWorld = TilemapManager.Instance.CellToWorld(cellPos);
            if (Vector3.Distance(transform.position, cellWorld) > maxPlaceDistance)
                return false;

            Vector2Int size = EntityDatabase.GetFootprint(_currentPlaceableId, _placementDirection);
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

            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || match == null)
                return;

            var msg = new TilePlaceMessage
            {
                grid_x = cellPos.x,
                grid_y = cellPos.y,
                occupant_id = _currentPlaceableId,
                direction = _placementDirection
            };
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.TilePlace, JsonUtility.ToJson(msg));
        }

        public bool IsPlacing => _isPlacing;
    }
}
