using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// Full inventory panel. Toggle with I. EDGE DOCKS, the screen center stays open world (you watch
    /// your REAL player change as you equip). Left dock: BUGS. Right: ITEMS (a grid that grows DOWN as
    /// a backpack unlocks slots) with the EQUIPMENT MANNEQUIN to its right (head/chest, arms + feet
    /// shown on BOTH sides but ONE logical item each, legs, accessories, backpack).
    /// </summary>
    public class InventoryPanel : MonoBehaviour
    {
        public static InventoryPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private CanvasGroup canvasGroup;
        private GameObject panelRoot;
        private TMP_Text coinsText;

        // Bug side (left dock) — unchanged; BugInfoCard swaps into BugGridRoot.
        private InventorySlotUI[] bugSlots;
        private GameObject _bugGridRoot;
        private RectTransform _bugDock;
        public GameObject BugGridRoot => _bugGridRoot;
        public RectTransform BugDock => _bugDock;

        // Equipment mannequin: DISPLAY cells (arms/feet appear twice), each carrying its LOGICAL
        // equip index in SlotIndex so a click/repaint hits the one underlying slot.
        private readonly List<InventorySlotUI> _equipCells = new List<InventorySlotUI>();
        public IReadOnlyList<InventorySlotUI> EquipSlots => _equipCells;

        // Item panel: a dynamic grid of slots 10..(ItemSlotsUnlocked-1), rebuilt when capacity changes.
        // Sits ABOVE the hotbar (bottom-center) and grows UP as a backpack adds rows.
        private RectTransform _itemsDock;
        private Transform _itemGridRoot;
        private readonly List<InventorySlotUI> _itemCells = new List<InventorySlotUI>();

        private bool _isOpen;
        private const int PanelStart = 10;     // panel shows item slots 10+
        private const int PanelCols = 10;      // match the hotbar width — the panel extends it
        private const int CellPx = 44;         // 40 slot + 4 gap

        // Mannequin layout: (logicalSlotIndex, ghostSprite, x, y) in the EquipDock (top-left origin).
        private struct Cell { public int slot; public string ghost; public float x, y; }
        private static readonly Cell[] Mannequin =
        {
            new Cell { slot = 0, ghost = "ghost_head",      x = 64,  y = -24 },   // head
            new Cell { slot = 2, ghost = "ghost_arms",      x = 16,  y = -72 },   // arm L
            new Cell { slot = 1, ghost = "ghost_body",      x = 64,  y = -72 },   // chest
            new Cell { slot = 2, ghost = "ghost_arms",      x = 112, y = -72 },   // arm R (same slot)
            new Cell { slot = 3, ghost = "ghost_legs",      x = 64,  y = -120 },  // legs
            new Cell { slot = 4, ghost = "ghost_feet",      x = 40,  y = -168 },  // foot L
            new Cell { slot = 4, ghost = "ghost_feet",      x = 88,  y = -168 },  // foot R (same slot)
            new Cell { slot = 5, ghost = "ghost_accessory", x = 16,  y = -220 },  // acc 1
            new Cell { slot = 6, ghost = "ghost_accessory", x = 64,  y = -220 },  // acc 2
            new Cell { slot = 7, ghost = null,              x = 112, y = -220 },  // backpack (ghost art: Part 5)
        };

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void BuildIfEmpty()
        {
            if (panelRoot != null) return;

            UIFactory.Stretch((RectTransform)transform, 0);
            var root = UIFactory.MakeRect(transform, "Docks");
            UIFactory.Stretch(root, 0);
            canvasGroup = root.gameObject.AddComponent<CanvasGroup>();
            panelRoot = root.gameObject;

            // ---- LEFT DOCK: bugs (the info card swaps with the grid) ----
            _bugDock = UIFactory.MakeDock(root, "BugDock", new Vector2(0f, 0.5f),
                                          new Vector2(0f, 0.5f), new Vector2(196, 300), new Vector2(6, 0));
            var bugsRoot = UIFactory.MakeRect(_bugDock, "BugGridRoot");
            UIFactory.Stretch(bugsRoot, 0);
            _bugGridRoot = bugsRoot.gameObject;
            var bugsHead = UIFactory.MakeText(bugsRoot, "BugsHeader", UIFactory.HeaderSize,
                                              UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(bugsHead.rectTransform, 12, -8, 80, 16);
            bugsHead.text = "BUGS";
            var bugGrid = UIFactory.MakeGrid(bugsRoot, "BugGrid", 4, UIFactory.Slot);
            Place((RectTransform)bugGrid.transform, 12, -26, 4 * CellPx, 5 * CellPx);
            bugSlots = new InventorySlotUI[20];
            for (int i = 0; i < 20; i++)
                bugSlots[i] = UIFactory.MakeSlot(bugGrid.transform, "slot_frame_bug");

            // ---- RIGHT DOCK: equipment mannequin (rightmost) ----
            var equipDock = UIFactory.MakeDock(root, "EquipDock", new Vector2(1f, 0.5f),
                                               new Vector2(1f, 0.5f), new Vector2(168, 320), new Vector2(-6, 0));
            var equipHead = UIFactory.MakeText(equipDock, "EquipHeader", UIFactory.HeaderSize,
                                               UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(equipHead.rectTransform, 12, -6, 80, 16);
            equipHead.text = "EQUIP";
            foreach (var c in Mannequin)
            {
                var cell = UIFactory.MakeSlot(equipDock, "slot_frame_equip", c.ghost);
                Place((RectTransform)cell.transform, c.x, c.y, 40, 40);
                cell.Initialize(SlotType.Equipment, c.slot);
                cell.OnSlotClicked += OnSlotClicked;
                _equipCells.Add(cell);
            }

            // ---- ITEMS DOCK: bottom-center, just ABOVE the hotbar; rows grow UP (it "extends"
            // the hotbar). Center stays open so you watch your real player. ----
            _itemsDock = UIFactory.MakeDock(root, "ItemsDock", new Vector2(0.5f, 0f),
                                            new Vector2(0.5f, 0f), new Vector2(PanelCols * CellPx + 8, 60),
                                            new Vector2(0, 66)); // clears the ~62px hotbar
            var grid = UIFactory.MakeGrid(_itemsDock, "ItemGrid", PanelCols, UIFactory.Slot);
            grid.startCorner = GridLayoutGroup.Corner.LowerLeft; // slots 10-19 are the row ABOVE the hotbar
            var grt = (RectTransform)grid.transform;
            grt.anchorMin = grt.anchorMax = new Vector2(0.5f, 0f);
            grt.pivot = new Vector2(0.5f, 0f);
            grt.anchoredPosition = new Vector2(0, 4);
            _itemGridRoot = grid.transform;

            // coins: small, screen bottom-left corner
            var coinIcon = UIFactory.MakeImage(root, "CoinIcon", "icon_coin");
            PlaceCorner(coinIcon.rectTransform, 8, 8, 18, 18);
            coinsText = UIFactory.MakeText(root, "Coins", 12f, UIFactory.TextColor, TextAlignmentOptions.Left);
            PlaceCorner(coinsText.rectTransform, 30, 9, 100, 16);

            BuildItemGrid();
        }

        /// <summary>(Re)build the panel item cells for the current unlocked capacity (10..Unlocked-1).</summary>
        private void BuildItemGrid()
        {
            if (_itemGridRoot == null) return;
            for (int i = _itemGridRoot.childCount - 1; i >= 0; i--)
                DestroyImmediate(_itemGridRoot.GetChild(i).gameObject);
            _itemCells.Clear();

            int unlocked = InventoryManager.Instance?.ItemSlotsUnlocked ?? 30;
            int panelCount = Mathf.Max(0, unlocked - PanelStart);
            int rows = Mathf.CeilToInt(panelCount / (float)PanelCols);

            // Size grid + dock to the row count (dock is bottom-anchored, so it grows UPward).
            ((RectTransform)_itemGridRoot).sizeDelta = new Vector2(PanelCols * CellPx, rows * CellPx);
            if (_itemsDock != null)
                _itemsDock.sizeDelta = new Vector2(PanelCols * CellPx + 8, rows * CellPx + 10);

            for (int i = 0; i < panelCount; i++)
            {
                var cell = UIFactory.MakeSlot(_itemGridRoot, "slot_frame");
                cell.Initialize(SlotType.Item, PanelStart + i);
                cell.OnSlotClicked += OnSlotClicked;
                _itemCells.Add(cell);
            }
        }

        private static void PlaceCorner(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 0f); // screen bottom-left
            rt.pivot = new Vector2(0f, 0f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f); // top-left
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private void Start()
        {
            BuildIfEmpty();

            for (int i = 0; i < bugSlots.Length && i < InventoryManager.BugSlotCount; i++)
            {
                bugSlots[i].Initialize(SlotType.Bug, i);
                bugSlots[i].OnSlotClicked += OnSlotClicked;
            }

            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnInventoryChanged += RefreshAllSlots;
                InventoryManager.Instance.OnItemSlotChanged += OnItemSlotChanged;
                InventoryManager.Instance.OnBugSlotChanged += OnBugSlotChanged;
                InventoryManager.Instance.OnCoinsChanged += OnCoinsChanged;
                InventoryManager.Instance.OnEquipmentChanged += RefreshEquipment;
                InventoryManager.Instance.OnCapacityChanged += OnCapacityChanged;
            }

            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnInventoryChanged -= RefreshAllSlots;
                InventoryManager.Instance.OnItemSlotChanged -= OnItemSlotChanged;
                InventoryManager.Instance.OnBugSlotChanged -= OnBugSlotChanged;
                InventoryManager.Instance.OnCoinsChanged -= OnCoinsChanged;
                InventoryManager.Instance.OnEquipmentChanged -= RefreshEquipment;
                InventoryManager.Instance.OnCapacityChanged -= OnCapacityChanged;
            }
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.I)) Toggle();

            if (_isOpen && Input.GetKeyDown(KeyCode.Escape))
            {
                if (BugInfoCard.Instance != null && BugInfoCard.Instance.IsShowing)
                    BugInfoCard.Instance.Hide();
                else
                    SetOpen(false);
            }
        }

        public void Toggle() => SetOpen(!_isOpen);

        public void SetOpen(bool open)
        {
            _isOpen = open;
            if (canvasGroup != null)
            {
                canvasGroup.alpha = open ? 1f : 0f;
                canvasGroup.blocksRaycasts = open;
                canvasGroup.interactable = open;
            }
            if (panelRoot != null) panelRoot.SetActive(open);

            if (open)
            {
                RefreshAllSlots();
                RefreshEquipment();
            }
            else
            {
                BugInfoCard.Instance?.Hide();
            }
        }

        private void OnCapacityChanged()
        {
            BuildItemGrid();
            if (_isOpen) RefreshAllSlots();
        }

        private void OnItemSlotChanged(int index)
        {
            if (!_isOpen) return;
            int panelIndex = index - PanelStart;
            if (panelIndex >= 0 && panelIndex < _itemCells.Count)
                RefreshItemCell(panelIndex);
        }

        private void OnBugSlotChanged(int index)
        {
            if (_isOpen && index >= 0 && index < bugSlots.Length)
                RefreshBugSlot(index);
        }

        private void OnCoinsChanged(long coins)
        {
            if (_isOpen) RefreshCoins();
        }

        private void RefreshItemCell(int panelIndex)
        {
            var inv = InventoryManager.Instance;
            int invIndex = panelIndex + PanelStart;
            if (inv != null && invIndex < inv.ItemSlots.Length)
                _itemCells[panelIndex].SetSlot(inv.ItemSlots[invIndex]);
        }

        private void RefreshBugSlot(int index)
        {
            var inv = InventoryManager.Instance;
            if (inv != null && index < inv.BugSlots.Length)
                bugSlots[index].SetSlot(inv.BugSlots[index]);
        }

        private void RefreshAllSlots()
        {
            if (!_isOpen) return;
            var inv = InventoryManager.Instance;
            if (inv == null) return;

            for (int i = 0; i < _itemCells.Count; i++)
            {
                int invIndex = i + PanelStart;
                if (invIndex < inv.ItemSlots.Length)
                    _itemCells[i].SetSlot(inv.ItemSlots[invIndex]);
            }
            for (int i = 0; i < bugSlots.Length && i < inv.BugSlots.Length; i++)
                bugSlots[i].SetSlot(inv.BugSlots[i]);

            RefreshCoins();
            RefreshEquipment();
        }

        private void RefreshCoins()
        {
            if (coinsText != null && InventoryManager.Instance != null)
                coinsText.text = $"{InventoryManager.Instance.Coins:N0}";
        }

        /// <summary>Paint each mannequin cell from its LOGICAL slot (arms/feet cells mirror).</summary>
        private void RefreshEquipment()
        {
            var inv = InventoryManager.Instance;
            if (inv?.Equipment == null) return;
            foreach (var cell in _equipCells)
            {
                int li = cell.SlotIndex;
                if (li < inv.Equipment.Length && !string.IsNullOrEmpty(inv.Equipment[li]))
                    cell.SetSlot(new InventorySlot { item_id = inv.Equipment[li], count = 1 });
                else
                    cell.Clear();
            }
        }

        private void OnSlotClicked(InventorySlotUI slot, PointerEventData eventData)
        {
            DragDropController.Instance?.OnSlotClicked(slot, eventData);
        }
    }
}
