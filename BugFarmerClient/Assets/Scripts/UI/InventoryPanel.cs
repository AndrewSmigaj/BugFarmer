using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;

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

            // Subscribe to inventory events
            if (InventoryManager.Instance != null)
            {
                InventoryManager.Instance.OnInventoryChanged += RefreshAllSlots;
                InventoryManager.Instance.OnItemSlotChanged += OnItemSlotChanged;
                InventoryManager.Instance.OnBugSlotChanged += OnBugSlotChanged;
                InventoryManager.Instance.OnCoinsChanged += OnCoinsChanged;
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

        private void OnSlotClicked(InventorySlotUI slot, PointerEventData eventData)
        {
            DragDropController.Instance?.OnSlotClicked(slot, eventData);
        }
    }
}
