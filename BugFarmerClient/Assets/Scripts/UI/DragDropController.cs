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

        /// <summary>
        /// Programmatic construction of the drag cursor (icon + count that
        /// follow the mouse); scene-built refs win if present.
        /// </summary>
        private void BuildIfEmpty()
        {
            if (cursorRoot != null) return;

            var rt = UIFactory.MakeRect(transform, "CursorRoot");
            rt.sizeDelta = new Vector2(UIFactory.Slot, UIFactory.Slot);
            cursorRoot = rt.gameObject;
            cursorIcon = UIFactory.MakeImage(rt, "Icon", null);
            UIFactory.Stretch(cursorIcon.rectTransform, 2);
            cursorIcon.preserveAspect = true;
            cursorCountText = UIFactory.MakeText(rt, "Count", UIFactory.CountSize,
                                                 UIFactory.CountColor,
                                                 TMPro.TextAlignmentOptions.BottomRight);
            UIFactory.Stretch(cursorCountText.rectTransform, 1);
            cursorCountText.fontStyle = TMPro.FontStyles.Bold;
        }

        private void Start()
        {
            BuildIfEmpty();

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

            // Equipment slots route through the armor equip flow (wired in the
            // armor pass); inert until then.
            if (slot.SlotType == SlotType.Equipment)
            {
                EquipmentController.Instance?.OnEquipSlotClicked(slot, eventData, this);
                return;
            }

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

                        // SWAP: the server deposits the taken item into the ORIGINAL SOURCE
                        // slot (MoveSlot case 3 swaps in place) — so the cursor's new item
                        // lives server-side at _sourceIndex, NOT at the clicked slot. Do NOT
                        // re-point the source here (doing so corrupted every continuation
                        // after a swap: duplicates + items landing in the wrong slots).
                        _cursorItemId = targetId;
                        _cursorCount = targetCount;

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

            // Bug slot, empty cursor: right-click opens the INFO CARD (species
            // knowledge; the half-stack pickup stays on item slots).
            if (!HasCursorItem && !targetEmpty && slot.SlotType == SlotType.Bug)
            {
                var card = BugInfoCard.Ensure();
                if (card != null)
                {
                    card.Show(slot.CurrentItemId, slot.CurrentCount);
                    return;
                }
            }

            // Armor in an item slot: right-click = QUICK-EQUIP (armor is
            // unstackable, so the half-pickup this replaces was equivalent to a
            // full pickup anyway).
            if (!HasCursorItem && !targetEmpty && slot.SlotType == SlotType.Item &&
                EquipmentController.Instance != null &&
                EquipmentController.Instance.TryQuickEquip(slot))
            {
                return;
            }

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

                // Local mutation (no server echo will repaint this) — every cursor
                // operation funnels through here: pickup, place, swap, half, drop-one,
                // cancel. Fires the slot events + keeps the server's equipped tool fresh.
                inventory.NotifyLocalSlotMutation(type, index);
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

        // === Cursor-place support (PlacementController + InventoryManager) ===

        /// <summary>Item id on the drag cursor ("" when empty).</summary>
        public string CursorItemId => _cursorItemId;
        /// <summary>The cursor stack's count (release-all sends THIS, never -1).</summary>
        public int CursorCount => _cursorCount;
        /// <summary>The cursor stack's server-side home slot.</summary>
        public int CursorSourceIndex => _sourceIndex;
        public SlotType CursorSourceType => _sourceType;

        /// <summary>
        /// Server-echo interception for the cursor's SOURCE slot — called by
        /// InventoryManager.HandleItemSlotUpdate AND HandleBugSlotUpdate INLINE, before
        /// writing the slot / firing events (deterministic ordering — never an event
        /// subscription). While the cursor holds a stack picked from slot S, the server
        /// still has that stack IN S; any server-side write of S (cursor-place consume,
        /// walk-over pickup stacking, a caught bug merging in, watering use) is therefore
        /// "the stack the cursor is holding" and its count must flow ONTO the cursor.
        ///
        /// Invariant: server S = local S remainder (half-pickups) + cursor count.
        /// Returns true = caller leaves the slot value UNTOUCHED (events still fire);
        /// false = caller writes the echo normally.
        /// </summary>
        public bool TryInterceptSlotEcho(SlotType slotType, int index, string itemId, int count)
        {
            // Slot TYPE must match too — bug and item indexes overlap 0-19.
            if (!HasCursorItem || slotType != _sourceType || index != _sourceIndex)
                return false;

            if (count == 0)
            {
                // Last-item case (e.g. cursor-placed the final block): server truth wins.
                ClearCursor();
                return false;
            }

            if (itemId != _cursorItemId)
            {
                // Defensive (unreachable under ordered delivery): a different item landed
                // in our source slot — surrender to server truth rather than corrupt.
                Debug.LogWarning($"[DragDrop] Source-slot echo item mismatch ({itemId} != {_cursorItemId}) — cancelling cursor");
                ClearCursor();
                return false;
            }

            // Remainder-preserving: the local slot may hold a half-pickup remainder that
            // stays IN the slot; only the cursor's share of the echoed count updates.
            var localSlot = GetSlotData(slotType, index);
            int remainder = (localSlot != null && !localSlot.IsEmpty) ? localSlot.count : 0;
            int newCursor = count - remainder;
            if (newCursor <= 0)
            {
                ClearCursor();
                return false; // server truth wins; echo writes normally
            }

            _cursorCount = newCursor;
            UpdateCursorDisplay();
            return true;
        }

        /// <summary>
        /// Drop the cursor WITHOUT restoring to a slot — used when a FullInventorySync
        /// repaints everything from server truth (reconnect); restoring locally on top of
        /// that would duplicate the stack.
        /// </summary>
        public void ForceClearCursor()
        {
            if (HasCursorItem)
                ClearCursor();
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
                    // World-art display sprites have arbitrary aspect ratios — letterbox.
                    cursorIcon.preserveAspect = true;
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
