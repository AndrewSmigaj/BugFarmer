using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// Full inventory panel. Toggle with I key.
    /// Shows tools grid (2x5) and bugs grid (4x5).
    /// </summary>
    public class InventoryPanel : MonoBehaviour
    {
        public static InventoryPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        [Header("Panels")]
        [SerializeField] private CanvasGroup canvasGroup;
        [SerializeField] private GameObject panelRoot;

        [Header("Slots")]
        [SerializeField] private InventorySlotUI[] itemSlots;  // 10 tool slots (2x5)
        [SerializeField] private InventorySlotUI[] bugSlots;   // 20 bug slots (4x5)

        [Header("Display")]
        [SerializeField] private TMP_Text coinsText;

        private bool _isOpen;

        // Code-built parts (UIFactory path): the 7 equipment slots (order:
        // head, body, arms, legs, feet, acc1, acc2 — wired up in the armor
        // pass) and the right-dock content root the bug info card swaps with.
        private InventorySlotUI[] _equipSlots;
        private GameObject _bugGridRoot;
        private RectTransform _bugDock;
        public InventorySlotUI[] EquipSlots => _equipSlots;
        public GameObject BugGridRoot => _bugGridRoot;
        public RectTransform BugDock => _bugDock;

        /// <summary>
        /// Programmatic construction (2026-06): EDGE DOCKS, the screen center
        /// stays open world — the game never pauses and the camera keeps the
        /// REAL player centered; you watch your actual character change as
        /// you equip. Left dock: equipment strip + item storage + coins.
        /// Right dock: the bug grid (the info card swaps in here).
        /// </summary>
        private void BuildIfEmpty()
        {
            if (itemSlots != null && itemSlots.Length > 0) return; // scene-built

            var root = UIFactory.MakeRect(transform, "Docks");
            UIFactory.Stretch(root, 0);
            canvasGroup = root.gameObject.AddComponent<CanvasGroup>();
            panelRoot = root.gameObject;

            // ---- RIGHT DOCK: equipment + items + coins (Andrew: items right) ----
            var left = UIFactory.MakeDock(root, "GearDock", new Vector2(1f, 0.5f),
                                          new Vector2(1f, 0.5f), new Vector2(168, 392),
                                          new Vector2(-8, 0));
            var equipHead = UIFactory.MakeText(left, "EquipHeader", UIFactory.HeaderSize,
                                               UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(equipHead.rectTransform, 12, -8, 60, 16);
            equipHead.text = "EQUIP";

            string[] ghosts = { "ghost_head", "ghost_body", "ghost_arms",
                                "ghost_legs", "ghost_feet" };
            _equipSlots = new InventorySlotUI[7];
            var equipGrid = UIFactory.MakeGrid(left, "EquipGrid", 1, UIFactory.EquipSlot);
            Place((RectTransform)equipGrid.transform, 10, -26, UIFactory.EquipSlot, 5 * 52);
            for (int i = 0; i < 5; i++)
                _equipSlots[i] = UIFactory.MakeSlot(equipGrid.transform,
                                                    "slot_frame_equip", ghosts[i]);
            var accGrid = UIFactory.MakeGrid(left, "AccessoryGrid", 2, UIFactory.EquipSlot);
            Place((RectTransform)accGrid.transform, 10, -26 - 5 * 52 - 4,
                  2 * 52, UIFactory.EquipSlot);
            for (int i = 5; i < 7; i++)
                _equipSlots[i] = UIFactory.MakeSlot(accGrid.transform,
                                                    "slot_frame_equip", "ghost_accessory");

            var itemsHead = UIFactory.MakeText(left, "ItemsHeader", UIFactory.HeaderSize,
                                               UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(itemsHead.rectTransform, 70, -8, 60, 16);
            itemsHead.text = "ITEMS";
            var itemGrid = UIFactory.MakeGrid(left, "ItemGrid", 2, UIFactory.Slot);
            Place((RectTransform)itemGrid.transform, 70, -26, 2 * 44, 5 * 44);
            itemSlots = new InventorySlotUI[10];
            for (int i = 0; i < 10; i++)
                itemSlots[i] = UIFactory.MakeSlot(itemGrid.transform, "slot_frame");

            var coinIcon = UIFactory.MakeImage(left, "CoinIcon", "icon_coin");
            Place(coinIcon.rectTransform, 12, -358, 22, 22);
            coinsText = UIFactory.MakeText(left, "Coins", 12f, UIFactory.TextColor,
                                           TextAlignmentOptions.Left);
            Place(coinsText.rectTransform, 38, -360, 110, 18);

            // ---- LEFT DOCK: bugs (the info card swaps with the grid; Andrew:
            // bugs left — hearts sit top-LEFT corner, this dock is middle-left) ----
            _bugDock = UIFactory.MakeDock(root, "BugDock", new Vector2(0f, 0.5f),
                                            new Vector2(0f, 0.5f), new Vector2(208, 280),
                                            new Vector2(8, 0));
            var bugsRoot = UIFactory.MakeRect(_bugDock, "BugGridRoot");
            UIFactory.Stretch(bugsRoot, 0);
            _bugGridRoot = bugsRoot.gameObject;
            var bugsHead = UIFactory.MakeText(bugsRoot, "BugsHeader", UIFactory.HeaderSize,
                                              UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(bugsHead.rectTransform, 12, -8, 60, 16);
            bugsHead.text = "BUGS";
            var bugGrid = UIFactory.MakeGrid(bugsRoot, "BugGrid", 4, UIFactory.Slot);
            Place((RectTransform)bugGrid.transform, 12, -26, 4 * 44, 5 * 44);
            bugSlots = new InventorySlotUI[20];
            for (int i = 0; i < 20; i++)
                bugSlots[i] = UIFactory.MakeSlot(bugGrid.transform, "slot_frame_bug");
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f); // top-left
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

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
            BuildIfEmpty();

            // Initialize item slots (10-19, the non-hotbar storage)
            // Hotbar handles slots 0-9, inventory panel handles 10-19
            const int itemSlotOffset = 10;
            for (int i = 0; i < itemSlots.Length && (i + itemSlotOffset) < InventoryManager.ItemSlotCount; i++)
            {
                itemSlots[i].Initialize(SlotType.Item, i + itemSlotOffset);
                itemSlots[i].OnSlotClicked += OnSlotClicked;
            }

            // Initialize bug slots and subscribe to drag/drop
            for (int i = 0; i < bugSlots.Length && i < InventoryManager.BugSlotCount; i++)
            {
                bugSlots[i].Initialize(SlotType.Bug, i);
                bugSlots[i].OnSlotClicked += OnSlotClicked;
            }

            // Equipment slots (code-built only; indices 0-6 = head, body,
            // arms, legs, feet, acc1, acc2)
            if (_equipSlots != null)
            {
                for (int i = 0; i < _equipSlots.Length; i++)
                {
                    _equipSlots[i].Initialize(SlotType.Equipment, i);
                    _equipSlots[i].OnSlotClicked += OnSlotClicked;
                }
            }

            // Subscribe to inventory events
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnInventoryChanged += RefreshAllSlots;
                InventoryManager.Instance.OnItemSlotChanged += OnItemSlotChanged;
                InventoryManager.Instance.OnBugSlotChanged += OnBugSlotChanged;
                InventoryManager.Instance.OnCoinsChanged += OnCoinsChanged;
                InventoryManager.Instance.OnEquipmentChanged += RefreshEquipment;
            }

            // Start closed
            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this)
                Instance = null;

            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnInventoryChanged -= RefreshAllSlots;
                InventoryManager.Instance.OnItemSlotChanged -= OnItemSlotChanged;
                InventoryManager.Instance.OnBugSlotChanged -= OnBugSlotChanged;
                InventoryManager.Instance.OnCoinsChanged -= OnCoinsChanged;
                InventoryManager.Instance.OnEquipmentChanged -= RefreshEquipment;
            }
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.I))
            {
                Toggle();
            }

            if (_isOpen && Input.GetKeyDown(KeyCode.Escape))
            {
                // layered close: the bug info card first, then the panel
                if (BugInfoCard.Instance != null && BugInfoCard.Instance.IsShowing)
                    BugInfoCard.Instance.Hide();
                else
                    SetOpen(false);
            }
        }

        public void Toggle()
        {
            SetOpen(!_isOpen);
        }

        public void SetOpen(bool open)
        {
            _isOpen = open;

            if (canvasGroup != null)
            {
                canvasGroup.alpha = open ? 1f : 0f;
                canvasGroup.blocksRaycasts = open;
                canvasGroup.interactable = open;
            }

            if (panelRoot != null)
            {
                panelRoot.SetActive(open);
            }

            if (open)
            {
                RefreshAllSlots();
                RefreshCoins();
                RefreshEquipment();
            }
            else
            {
                BugInfoCard.Instance?.Hide();
            }
        }

        private void OnItemSlotChanged(int index)
        {
            if (!_isOpen) return;
            // Convert inventory index to panel index (subtract offset)
            int panelIndex = index - 10;
            if (panelIndex >= 0 && panelIndex < itemSlots.Length)
            {
                RefreshItemSlot(panelIndex);
            }
        }

        private void OnBugSlotChanged(int index)
        {
            if (!_isOpen) return;
            if (index >= 0 && index < bugSlots.Length)
            {
                RefreshBugSlot(index);
            }
        }

        private void OnCoinsChanged(long coins)
        {
            if (_isOpen)
            {
                RefreshCoins();
            }
        }

        private void RefreshItemSlot(int panelIndex)
        {
            var inventory = InventoryManager.Instance;
            int inventoryIndex = panelIndex + 10; // Panel slot 0 = inventory slot 10
            if (inventory != null && inventoryIndex < inventory.ItemSlots.Length)
            {
                itemSlots[panelIndex].SetSlot(inventory.ItemSlots[inventoryIndex]);
            }
        }

        private void RefreshBugSlot(int index)
        {
            var inventory = InventoryManager.Instance;
            if (inventory != null && index < inventory.BugSlots.Length)
            {
                bugSlots[index].SetSlot(inventory.BugSlots[index]);
            }
        }

        private void RefreshAllSlots()
        {
            if (!_isOpen) return;

            var inventory = InventoryManager.Instance;
            if (inventory == null) return;

            // Item slots show inventory slots 10-19
            for (int i = 0; i < itemSlots.Length; i++)
            {
                int inventoryIndex = i + 10;
                if (inventoryIndex < inventory.ItemSlots.Length)
                {
                    itemSlots[i].SetSlot(inventory.ItemSlots[inventoryIndex]);
                }
            }

            for (int i = 0; i < bugSlots.Length && i < inventory.BugSlots.Length; i++)
            {
                bugSlots[i].SetSlot(inventory.BugSlots[i]);
            }

            RefreshCoins();
        }

        private void RefreshCoins()
        {
            if (coinsText != null && InventoryManager.Instance != null)
            {
                coinsText.text = $"Coins: {InventoryManager.Instance.Coins:N0}";
            }
        }

        /// <summary>Repaint the 7 equipment slots from InventoryManager.Equipment
        /// (worn pieces render as 1-count slots; empties show their ghost).</summary>
        private void RefreshEquipment()
        {
            var inv = InventoryManager.Instance;
            if (_equipSlots == null || inv?.Equipment == null) return;
            for (int i = 0; i < _equipSlots.Length && i < inv.Equipment.Length; i++)
            {
                var id = inv.Equipment[i];
                if (string.IsNullOrEmpty(id))
                    _equipSlots[i].Clear();
                else
                    _equipSlots[i].SetSlot(new InventorySlot { item_id = id, count = 1 });
            }
        }

        private void OnSlotClicked(InventorySlotUI slot, PointerEventData eventData)
        {
            DragDropController.Instance?.OnSlotClicked(slot, eventData);
        }
    }
}
