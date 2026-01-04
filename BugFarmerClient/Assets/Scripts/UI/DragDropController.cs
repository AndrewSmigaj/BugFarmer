using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// Manages cursor item for Terraria-style drag/drop inventory operations.
    /// Handles left-click (full stack), right-click (half/drop 1), and cancellation.
    /// </summary>
    public class DragDropController : MonoBehaviour
    {
        public static DragDropController Instance { get; private set; }

        [Header("Cursor Display")]
        [SerializeField] private GameObject cursorRoot;
        [SerializeField] private Image cursorIcon;
        [SerializeField] private TMP_Text cursorCountText;

        private string _cursorItemId = "";
        private int _cursorCount;
        private SlotType _sourceType;
        private int _sourceIndex;

        public bool HasCursorItem => !string.IsNullOrEmpty(_cursorItemId) && _cursorCount > 0;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Start()
        {
            // Ensure cursor elements don't block raycasts to slots below
            if (cursorRoot != null)
            {
                // Disable raycasts on all graphics in cursor hierarchy
                foreach (var graphic in cursorRoot.GetComponentsInChildren<UnityEngine.UI.Graphic>(true))
                {
                    graphic.raycastTarget = false;
                }
            }

            UpdateCursorDisplay();
        }

        private void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        private void Update()
        {
            if (HasCursorItem && cursorRoot != null)
            {
                cursorRoot.transform.position = Input.mousePosition;
            }

            if (HasCursorItem && Input.GetKeyDown(KeyCode.Escape))
            {
                CancelDrag();
            }

            if (HasCursorItem && !InventoryPanel.IsOpen)
            {
                CancelDrag();
            }
        }

        /// <summary>
        /// Handle slot click. Called by InventorySlotUI via subscription.
        /// </summary>
        public void OnSlotClicked(InventorySlotUI slot, PointerEventData eventData)
        {
            Debug.Log($"[DragDrop] OnSlotClicked: {slot.SlotType}[{slot.SlotIndex}], button={eventData.button}, hasCursor={HasCursorItem}");

            if (eventData.button == PointerEventData.InputButton.Left)
            {
                HandleLeftClick(slot);
            }
            else if (eventData.button == PointerEventData.InputButton.Right)
            {
                HandleRightClick(slot);
            }
        }

        private void HandleLeftClick(InventorySlotUI slot)
        {
            var inventory = InventoryManager.Instance;
            if (inventory == null)
            {
                Debug.LogWarning("[DragDrop] HandleLeftClick: InventoryManager.Instance is null");
                return;
            }

            var targetSlot = GetSlotData(slot.SlotType, slot.SlotIndex);
            bool targetEmpty = targetSlot == null || targetSlot.IsEmpty;

            Debug.Log($"[DragDrop] HandleLeftClick: targetEmpty={targetEmpty}, targetSlot={targetSlot?.item_id ?? "null"}");

            if (!HasCursorItem)
            {
                // Picking up from slot
                if (!targetEmpty)
                {
                    _cursorItemId = targetSlot.item_id;
                    _cursorCount = targetSlot.count;
                    _sourceType = slot.SlotType;
                    _sourceIndex = slot.SlotIndex;

                    Debug.Log($"[DragDrop] Picked up: {_cursorItemId} x{_cursorCount} from {_sourceType}[{_sourceIndex}]");

                    ClearSlot(slot.SlotType, slot.SlotIndex);
                    UpdateCursorDisplay();
                }
            }
            else
            {
                // Placing into slot
                Debug.Log($"[DragDrop] Attempting to place {_cursorItemId} into {slot.SlotType}[{slot.SlotIndex}], canPlace={CanPlaceInSlot(slot.SlotType)}");

                if (targetEmpty)
                {
                    if (CanPlaceInSlot(slot.SlotType))
                    {
                        SetSlotData(slot.SlotType, slot.SlotIndex, _cursorItemId, _cursorCount);
                        SendMoveSlot(_sourceType, _sourceIndex, slot.SlotType, slot.SlotIndex, -1);
                        Debug.Log($"[DragDrop] Placed into empty slot");
                        ClearCursor();
                    }
                    else
                    {
                        Debug.Log($"[DragDrop] Cannot place {_sourceType} item into {slot.SlotType} slot");
                    }
                }
                else if (targetSlot.item_id == _cursorItemId)
                {
                    int newCount = targetSlot.count + _cursorCount;
                    SetSlotData(slot.SlotType, slot.SlotIndex, _cursorItemId, newCount);
                    SendMoveSlot(_sourceType, _sourceIndex, slot.SlotType, slot.SlotIndex, -1);
                    ClearCursor();
                }
                else
                {
                    if (CanPlaceInSlot(slot.SlotType))
                    {
                        string targetId = targetSlot.item_id;
                        int targetCount = targetSlot.count;

                        SetSlotData(slot.SlotType, slot.SlotIndex, _cursorItemId, _cursorCount);
                        SendMoveSlot(_sourceType, _sourceIndex, slot.SlotType, slot.SlotIndex, -1);

                        _cursorItemId = targetId;
                        _cursorCount = targetCount;
                        _sourceType = slot.SlotType;
                        _sourceIndex = slot.SlotIndex;

                        UpdateCursorDisplay();
                    }
                }
            }
        }

        private void HandleRightClick(InventorySlotUI slot)
        {
            var inventory = InventoryManager.Instance;
            if (inventory == null) return;

            var targetSlot = GetSlotData(slot.SlotType, slot.SlotIndex);
            bool targetEmpty = targetSlot == null || targetSlot.IsEmpty;

            if (!HasCursorItem)
            {
                if (!targetEmpty)
                {
                    int half = (targetSlot.count + 1) / 2;
                    int remaining = targetSlot.count - half;

                    _cursorItemId = targetSlot.item_id;
                    _cursorCount = half;
                    _sourceType = slot.SlotType;
                    _sourceIndex = slot.SlotIndex;

                    if (remaining > 0)
                    {
                        SetSlotData(slot.SlotType, slot.SlotIndex, targetSlot.item_id, remaining);
                    }
                    else
                    {
                        ClearSlot(slot.SlotType, slot.SlotIndex);
                    }

                    UpdateCursorDisplay();
                }
            }
            else
            {
                if (CanPlaceInSlot(slot.SlotType))
                {
                    if (targetEmpty)
                    {
                        SetSlotData(slot.SlotType, slot.SlotIndex, _cursorItemId, 1);
                        _cursorCount--;

                        if (_cursorCount <= 0)
                        {
                            ClearCursor();
                        }
                        else
                        {
                            UpdateCursorDisplay();
                        }

                        SendMoveSlot(_sourceType, _sourceIndex, slot.SlotType, slot.SlotIndex, 1);
                    }
                    else if (targetSlot.item_id == _cursorItemId)
                    {
                        SetSlotData(slot.SlotType, slot.SlotIndex, _cursorItemId, targetSlot.count + 1);
                        _cursorCount--;

                        if (_cursorCount <= 0)
                        {
                            ClearCursor();
                        }
                        else
                        {
                            UpdateCursorDisplay();
                        }

                        SendMoveSlot(_sourceType, _sourceIndex, slot.SlotType, slot.SlotIndex, 1);
                    }
                }
            }
        }

        private bool CanPlaceInSlot(SlotType targetType)
        {
            return _sourceType == targetType;
        }

        private InventorySlot GetSlotData(SlotType type, int index)
        {
            var inventory = InventoryManager.Instance;
            if (inventory == null) return null;

            if (type == SlotType.Bug && index < inventory.BugSlots.Length)
                return inventory.BugSlots[index];
            if (type == SlotType.Item && index < inventory.ItemSlots.Length)
                return inventory.ItemSlots[index];

            return null;
        }

        private void SetSlotData(SlotType type, int index, string itemId, int count)
        {
            var inventory = InventoryManager.Instance;
            if (inventory == null) return;

            InventorySlot slot = null;
            if (type == SlotType.Bug && index < inventory.BugSlots.Length)
                slot = inventory.BugSlots[index];
            else if (type == SlotType.Item && index < inventory.ItemSlots.Length)
                slot = inventory.ItemSlots[index];

            if (slot != null)
            {
                slot.item_id = itemId;
                slot.count = count;
            }
        }

        private void ClearSlot(SlotType type, int index)
        {
            SetSlotData(type, index, "", 0);
        }

        private void ClearCursor()
        {
            _cursorItemId = "";
            _cursorCount = 0;
            UpdateCursorDisplay();
        }

        private void CancelDrag()
        {
            if (!HasCursorItem) return;

            var sourceSlot = GetSlotData(_sourceType, _sourceIndex);
            if (sourceSlot != null && sourceSlot.IsEmpty)
            {
                SetSlotData(_sourceType, _sourceIndex, _cursorItemId, _cursorCount);
            }
            else if (sourceSlot != null && sourceSlot.item_id == _cursorItemId)
            {
                SetSlotData(_sourceType, _sourceIndex, _cursorItemId, sourceSlot.count + _cursorCount);
            }
            else
            {
                var inventory = InventoryManager.Instance;
                if (inventory != null)
                {
                    var slots = _sourceType == SlotType.Bug ? inventory.BugSlots : inventory.ItemSlots;
                    for (int i = 0; i < slots.Length; i++)
                    {
                        if (slots[i].IsEmpty)
                        {
                            SetSlotData(_sourceType, i, _cursorItemId, _cursorCount);
                            break;
                        }
                    }
                }
            }

            ClearCursor();
        }

        private void UpdateCursorDisplay()
        {
            if (cursorRoot != null)
            {
                cursorRoot.SetActive(HasCursorItem);
            }

            if (cursorIcon != null)
            {
                if (HasCursorItem)
                {
                    cursorIcon.sprite = EntityDatabase.GetItemSprite(_cursorItemId);
                    cursorIcon.enabled = cursorIcon.sprite != null;
                }
                else
                {
                    cursorIcon.enabled = false;
                }
            }

            if (cursorCountText != null)
            {
                if (HasCursorItem && _cursorCount > 1)
                {
                    cursorCountText.text = _cursorCount.ToString();
                    cursorCountText.enabled = true;
                }
                else
                {
                    cursorCountText.enabled = false;
                }
            }
        }

        private void SendMoveSlot(SlotType srcType, int srcIdx, SlotType dstType, int dstIdx, int count)
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return;

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return;

            var msg = new MoveSlotMessage
            {
                source_type = srcType == SlotType.Bug ? "bug" : "item",
                source_index = srcIdx,
                dest_type = dstType == SlotType.Bug ? "bug" : "item",
                dest_index = dstIdx,
                count = count
            };

            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.MoveSlot, json);
        }
    }
}
