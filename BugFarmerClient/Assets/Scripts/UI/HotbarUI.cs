using UnityEngine;
using UnityEngine.EventSystems;

namespace BugFarmer.UI
{
    /// <summary>
    /// Hotbar UI controller. Displays ItemSlots[0..9] at bottom of screen.
    /// Handles keyboard (1-9, 0), scroll wheel, and click selection.
    /// </summary>
    public class HotbarUI : MonoBehaviour
    {
        [SerializeField] private InventorySlotUI[] slots;

        private int _selectedSlot;

        /// <summary>
        /// Programmatic construction: a wood strip bottom-center holding the
        /// 10 hotbar slots (scene-built arrays win if present).
        /// </summary>
        private void BuildIfEmpty()
        {
            // A leftover scene HotbarUI can carry a length-10 slots array whose
            // elements were never assigned (the half-deleted prefab instances);
            // BuildIfEmpty must rebuild in that case or Start() NREs on slots[i].
            if (slots != null && slots.Length > 0 && System.Array.TrueForAll(slots, s => s != null)) return;

            var rt = (RectTransform)transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0f);
            rt.pivot = new Vector2(0.5f, 0f);
            rt.anchoredPosition = new Vector2(0, 6);
            rt.sizeDelta = new Vector2(10 * 44 + 2 * UIFactory.Pad - 4, 56);
            var bg = gameObject.AddComponent<UnityEngine.UI.Image>();
            bg.sprite = UIFactory.UISprite("panel_wood");
            bg.type = UnityEngine.UI.Image.Type.Sliced;
            bg.raycastTarget = true;

            var grid = UIFactory.MakeGrid(transform, "HotbarGrid", 10, UIFactory.Slot);
            var grt = (RectTransform)grid.transform;
            grt.anchorMin = grt.anchorMax = new Vector2(0.5f, 0.5f);
            grt.pivot = new Vector2(0.5f, 0.5f);
            grt.anchoredPosition = Vector2.zero;
            grt.sizeDelta = new Vector2(10 * 44 - 4, UIFactory.Slot);

            slots = new InventorySlotUI[10];
            for (int i = 0; i < 10; i++)
                slots[i] = UIFactory.MakeSlot(grid.transform, "slot_frame");
        }

        private void Start()
        {
            BuildIfEmpty();

            // Initialize slots with type and index
            for (int i = 0; i < slots.Length && i < InventoryManager.ItemSlotCount; i++)
            {
                slots[i].Initialize(SlotType.Item, i);
                int index = i; // Capture for closure
                slots[i].OnSlotClicked += (slot, eventData) => OnSlotClicked(index, eventData);
            }

            // Subscribe to inventory events
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnItemSlotChanged += OnItemSlotChanged;
                InventoryManager.Instance.OnSelectedSlotChanged += OnSelectedSlotChanged;
                InventoryManager.Instance.OnInventoryChanged += RefreshAllSlots;

                // Initial state
                _selectedSlot = InventoryManager.Instance.SelectedSlot;
                RefreshAllSlots();
                UpdateSelectionVisual();
                Debug.Log($"[HotbarUI] Initialized, selected slot: {_selectedSlot}");
            }
            else
            {
                Debug.LogWarning("[HotbarUI] InventoryManager.Instance is NULL - hotbar won't work!");
            }
        }

        private void OnDestroy()
        {
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnItemSlotChanged -= OnItemSlotChanged;
                InventoryManager.Instance.OnSelectedSlotChanged -= OnSelectedSlotChanged;
                InventoryManager.Instance.OnInventoryChanged -= RefreshAllSlots;
            }
        }

        private void Update()
        {
            HandleKeyboardInput();
            HandleScrollWheel();
        }

        private void HandleKeyboardInput()
        {
            if (Input.GetKeyDown(KeyCode.Alpha1)) SelectSlot(0);
            else if (Input.GetKeyDown(KeyCode.Alpha2)) SelectSlot(1);
            else if (Input.GetKeyDown(KeyCode.Alpha3)) SelectSlot(2);
            else if (Input.GetKeyDown(KeyCode.Alpha4)) SelectSlot(3);
            else if (Input.GetKeyDown(KeyCode.Alpha5)) SelectSlot(4);
            else if (Input.GetKeyDown(KeyCode.Alpha6)) SelectSlot(5);
            else if (Input.GetKeyDown(KeyCode.Alpha7)) SelectSlot(6);
            else if (Input.GetKeyDown(KeyCode.Alpha8)) SelectSlot(7);
            else if (Input.GetKeyDown(KeyCode.Alpha9)) SelectSlot(8);
            else if (Input.GetKeyDown(KeyCode.Alpha0)) SelectSlot(9);
        }

        private void HandleScrollWheel()
        {
            // Disable scroll when inventory panel is open
            if (InventoryPanel.IsOpen)
                return;

            // The shaped-ground builder owns the wheel while a shovel is equipped (cycles the shape it places).
            var equipped = InventoryManager.Instance?.GetEquippedToolId();
            if (!string.IsNullOrEmpty(equipped) &&
                BugFarmer.Data.EntityDatabase.Get(equipped)?.ToolType == "shovel")
                return;

            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (scroll > 0.01f)
            {
                SelectSlot((_selectedSlot - 1 + 10) % 10);
            }
            else if (scroll < -0.01f)
            {
                SelectSlot((_selectedSlot + 1) % 10);
            }
        }

        private void OnSlotClicked(int index, PointerEventData eventData)
        {
            Debug.Log($"[HotbarUI] Slot {index} clicked, button={eventData.button}");

            // Two-mode button (Terraria convention): while the inventory panel is open,
            // hotbar clicks are ITEM OPERATIONS (drag/drop pick/place/swap — this is what
            // makes moving items in/out of the hotbar possible); selection while open is
            // number-keys only. Panel closed = click selects, as always.
            if (InventoryPanel.IsOpen && DragDropController.Instance != null)
            {
                DragDropController.Instance.OnSlotClicked(slots[index], eventData);
                return;
            }

            if (eventData.button == PointerEventData.InputButton.Left)
            {
                SelectSlot(index);
            }
        }

        private void SelectSlot(int index)
        {
            if (index < 0 || index >= InventoryManager.ItemSlotCount)
                return;

            Debug.Log($"[HotbarUI] Selecting slot {index}");
            InventoryManager.Instance?.SelectSlot(index);
        }

        private void OnItemSlotChanged(int slotIndex)
        {
            if (slotIndex >= 0 && slotIndex < slots.Length)
            {
                RefreshSlot(slotIndex);
            }
        }

        private void OnSelectedSlotChanged(int slotIndex)
        {
            _selectedSlot = slotIndex;
            UpdateSelectionVisual();
        }

        private void RefreshSlot(int index)
        {
            if (index < 0 || index >= slots.Length)
                return;

            var inventory = InventoryManager.Instance;
            if (inventory != null && index < inventory.ItemSlots.Length)
            {
                // ForRender = the shop barter-basket overlay: a staged hotbar stack renders
                // reduced/empty while the shop is open (data untouched; no-op otherwise).
                slots[index].SetSlot(ShopPanel.ForRender(SlotType.Item, index, inventory.ItemSlots[index]));
            }
        }

        private void RefreshAllSlots()
        {
            for (int i = 0; i < slots.Length; i++)
            {
                RefreshSlot(i);
            }
        }

        private void UpdateSelectionVisual()
        {
            for (int i = 0; i < slots.Length; i++)
            {
                slots[i].SetSelected(i == _selectedSlot);
            }
        }
    }
}
