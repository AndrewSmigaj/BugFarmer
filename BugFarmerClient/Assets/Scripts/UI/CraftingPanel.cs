using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.Player;
using BugFarmer.World;

namespace BugFarmer.UI
{
    /// <summary>
    /// ONE panel for both craft stations (workbench/furnace/anvil/…) and storage containers
    /// (chests/dressers/racks) — right-click the occupant to open. The server is authoritative:
    /// every action is an OpCode-98 message, and the panel renders from the OpCode-99 echo +
    /// RecipeDatabase. There is no quick/slow split — a station just processes at its recipe's
    /// process_ticks (the bar fills near-instantly for a workbench, slowly for a furnace).
    ///
    /// Craft: pick a recipe → set qty → Craft (inputs leave your bag, output piles into the output
    /// grid over time) → "Get all" or double-click a cell to collect (overflow stays).
    /// Storage: double-/shift-click a stack to move the WHOLE thing to the other side.
    /// </summary>
    public class CraftingPanel : MonoBehaviour
    {
        public static CraftingPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 2.5f;
        private const float TickRate = 10f; // server tick Hz — used to interpolate the progress bar

        private bool _isOpen;
        private Vector2Int _cell;
        private string _occupantId = "";
        private bool _isCraft;

        // UI frame
        private CanvasGroup _group;
        private RectTransform _dock;
        private RectTransform _content; // rebuilt per open
        private TMP_Text _title;

        // Craft-mode widgets (recreated per open / per refresh)
        private readonly List<(InventorySlotUI slot, RecipeDatabase.Recipe recipe)> _recipeSlots =
            new List<(InventorySlotUI, RecipeDatabase.Recipe)>();
        private RecipeDatabase.Recipe _selected;
        private int _qty = 1;
        private TMP_Text _qtyText;
        private TMP_Text _inputsText;
        private TMP_Text _recipeName;
        private Button _craftButton;
        private Image _progressFill;
        private TMP_Text _queueText;
        private readonly List<InventorySlotUI> _outputSlots = new List<InventorySlotUI>();

        // Storage-mode widgets
        private readonly List<InventorySlotUI> _containerSlots = new List<InventorySlotUI>();
        private readonly List<InventorySlotUI> _playerSlots = new List<InventorySlotUI>();

        // Last server echo (drives slots + the interpolated progress bar)
        private ContainerUpdateMessage _last;
        private float _lastStamp;

        // ---------------------------------------------------------------- lifecycle

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);

            _dock = UIFactory.MakeDock(transform, "CraftDock", new Vector2(0.5f, 0.5f),
                                       new Vector2(0.5f, 0.5f), new Vector2(600, 440), Vector2.zero);
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            _title = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 2f,
                                        UIFactory.HeaderColor, TextAlignmentOptions.Center);
            Place(_title.rectTransform, 0, -8, 600, 20, new Vector2(0.5f, 1f), new Vector2(0.5f, 1f));

            _content = UIFactory.MakeRect(_dock, "Content");
            UIFactory.Stretch(_content, 12);
            ((RectTransform)_content).offsetMax = new Vector2(-12, -34); // leave room for the title

            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState += OnMatchState;
            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged += OnInventoryChanged;

            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState -= OnMatchState;
            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged -= OnInventoryChanged;
        }

        private void Update()
        {
            if (!_isOpen) return;
            if (Input.GetKeyDown(KeyCode.Escape)) { SetOpen(false); return; }
            if (_isCraft) AnimateProgress();
        }

        // ---------------------------------------------------------------- open / route

        /// <summary>
        /// Routed right-click (PlayerInputRouter). Opens the craft/storage panel for a station or
        /// chest; closes an open panel when the click lands elsewhere. Returns TRUE on any state
        /// transition (so the click is consumed and never also jabs/places).
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            var hit = Physics2D.OverlapPoint(mouseWorld);
            var target = hit != null ? hit.GetComponent<OccupantClickTarget>() : null;
            if (target == null)
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }

            var def = EntityDatabase.Get(target.OccupantId);
            string it = def?.World?.InteractionType;
            bool craft = it == "craft";
            bool storage = it == "storage";
            if (!craft && !storage)
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }

            // Range check (server re-validates; out-of-range falls through unhandled)
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > MaxInteractDistance * MaxInteractDistance)
                    return false;
            }

            // Toggle if re-clicking the same open station; otherwise (re)open for this cell.
            if (_isOpen && _cell == target.AnchorCell) { SetOpen(false); return true; }

            _cell = target.AnchorCell;
            _occupantId = target.OccupantId;
            _isCraft = craft;
            _selected = null;
            _qty = 1;
            _last = null;
            Open();
            return true;
        }

        private void Open()
        {
            _title.text = (EntityDatabase.Get(_occupantId)?.Name) ?? _occupantId;
            BuildContent();
            SetOpen(true);
            Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "open" });
        }

        private void SetOpen(bool open)
        {
            _isOpen = open;
            if (_group != null)
            {
                _group.alpha = open ? 1f : 0f;
                _group.blocksRaycasts = open;
                _group.interactable = open;
            }
            _dock.gameObject.SetActive(open);
        }

        // ---------------------------------------------------------------- build content

        private void BuildContent()
        {
            // Clear previous content + cached widget refs (Immediate so stale slots don't linger
            // under the grids for a frame)
            for (int i = _content.childCount - 1; i >= 0; i--)
                DestroyImmediate(_content.GetChild(i).gameObject);
            _recipeSlots.Clear();
            _outputSlots.Clear();
            _containerSlots.Clear();
            _playerSlots.Clear();
            _qtyText = _inputsText = _recipeName = _queueText = null;
            _craftButton = null;
            _progressFill = null;

            if (_isCraft) BuildCraftContent();
            else BuildStorageContent();
        }

        private void BuildCraftContent()
        {
            var recipes = RecipeDatabase.ForStation(_occupantId);

            // --- LEFT: recipe list ---
            var listHead = UIFactory.MakeText(_content, "RecipesHeader", UIFactory.HeaderSize,
                                              UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(listHead.rectTransform, 0, 0, 150, 16);
            listHead.text = "RECIPES";

            var grid = UIFactory.MakeGrid(_content, "RecipeGrid", 3, UIFactory.Slot);
            Place((RectTransform)grid.transform, 0, -20, 3 * 44, 4 * 44);
            foreach (var r in recipes)
            {
                var s = UIFactory.MakeSlot(grid.transform, "slot_frame");
                s.SetSlot(new InventorySlot { item_id = r.output.item, count = r.output.count });
                var captured = r;
                s.OnSlotClicked += (slot, ev) => SelectRecipe(captured);
                _recipeSlots.Add((s, r));
            }

            // --- MIDDLE: selected recipe details ---
            _recipeName = UIFactory.MakeText(_content, "RecipeName", UIFactory.HeaderSize,
                                             UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_recipeName.rectTransform, 160, 0, 230, 18);

            _inputsText = UIFactory.MakeText(_content, "Inputs", UIFactory.CountSize + 1f,
                                             UIFactory.TextColor, TextAlignmentOptions.TopLeft);
            _inputsText.enableWordWrapping = true;
            Place(_inputsText.rectTransform, 160, -22, 230, 90);

            // qty stepper
            MakeButton(_content, "Minus", "-", 160, -116, 28, 24, () => { _qty = Mathf.Max(1, _qty - 1); RefreshSelected(); });
            _qtyText = UIFactory.MakeText(_content, "Qty", UIFactory.HeaderSize, UIFactory.TextColor, TextAlignmentOptions.Center);
            Place(_qtyText.rectTransform, 192, -116, 40, 24);
            MakeButton(_content, "Plus", "+", 236, -116, 28, 24, () => { _qty = Mathf.Min(99, _qty + 1); RefreshSelected(); });

            _craftButton = MakeButton(_content, "Craft", "Craft", 272, -116, 100, 24, DoCraft);

            // progress bar + queue
            var barBg = UIFactory.MakeImage(_content, "BarBg", "slot_frame", true);
            barBg.color = new Color(0f, 0f, 0f, 0.4f);
            Place(barBg.rectTransform, 160, -150, 230, 14);
            _progressFill = UIFactory.MakeImage(_content, "BarFill", null);
            _progressFill.color = new Color(0.95f, 0.7f, 0.25f, 1f);
            Place(_progressFill.rectTransform, 162, -152, 0, 10);
            _queueText = UIFactory.MakeText(_content, "Queue", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_queueText.rectTransform, 160, -168, 230, 16);

            // --- RIGHT: output grid + Get all ---
            var outHead = UIFactory.MakeText(_content, "OutputHeader", UIFactory.HeaderSize,
                                             UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(outHead.rectTransform, 410, 0, 120, 16);
            outHead.text = "OUTPUT";
            var outGrid = UIFactory.MakeGrid(_content, "OutputGrid", 2, UIFactory.Slot);
            Place((RectTransform)outGrid.transform, 410, -20, 2 * 44, 4 * 44);
            for (int i = 0; i < 8; i++)
            {
                var s = UIFactory.MakeSlot(outGrid.transform, "slot_frame");
                int idx = i;
                s.OnSlotClicked += (slot, ev) =>
                {
                    if (IsQuickClick(ev))
                        Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "collect", slot = idx });
                };
                _outputSlots.Add(s);
            }
            MakeButton(_content, "GetAll", "Get all", 410, -206, 88, 24,
                       () => Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "get_all" }));

            if (recipes.Count > 0) SelectRecipe(recipes[0]);
            else RefreshSelected();
        }

        private void BuildStorageContent()
        {
            var def = EntityDatabase.Get(_occupantId);

            var head = UIFactory.MakeText(_content, "ChestHeader", UIFactory.HeaderSize,
                                          UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(head.rectTransform, 0, 0, 400, 16);
            head.text = "STORAGE — double-click to move a stack";

            // container grid (size from the last echo if we have it, else a reasonable default)
            int slotCount = _last?.slots?.Length ?? (def?.World?.ContainerSlots ?? 12);
            var cGrid = UIFactory.MakeGrid(_content, "ContainerGrid", 6, UIFactory.Slot);
            Place((RectTransform)cGrid.transform, 0, -20, 6 * 44, 4 * 44);
            for (int i = 0; i < slotCount; i++)
            {
                var s = UIFactory.MakeSlot(cGrid.transform, "slot_frame");
                int idx = i;
                s.OnSlotClicked += (slot, ev) =>
                {
                    if (IsQuickClick(ev))
                        Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "quick", zone = "container", slot = idx });
                };
                _containerSlots.Add(s);
            }

            // your items
            var yh = UIFactory.MakeText(_content, "YourHeader", UIFactory.HeaderSize,
                                        UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(yh.rectTransform, 0, -210, 200, 16);
            yh.text = "YOUR ITEMS";
            var pGrid = UIFactory.MakeGrid(_content, "PlayerGrid", 10, UIFactory.Slot);
            Place((RectTransform)pGrid.transform, 0, -230, 10 * 44, 2 * 44);
            int playerCount = InventoryManager.Instance?.ItemSlots?.Length ?? 20;
            for (int i = 0; i < playerCount; i++)
            {
                var s = UIFactory.MakeSlot(pGrid.transform, "slot_frame");
                int idx = i;
                s.OnSlotClicked += (slot, ev) =>
                {
                    if (IsQuickClick(ev))
                        Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "quick", zone = "player", slot = idx });
                };
                _playerSlots.Add(s);
            }

            RefreshStorageSlots();
        }

        // ---------------------------------------------------------------- craft refresh

        private void SelectRecipe(RecipeDatabase.Recipe r)
        {
            // Local view only — the "craft" action carries the recipe id, so browsing recipes never
            // touches the server (no spurious "finish the current batch" while a queue runs).
            _selected = r;
            for (int i = 0; i < _recipeSlots.Count; i++)
                _recipeSlots[i].slot.SetSelected(_recipeSlots[i].recipe == r);
            RefreshSelected();
        }

        private void RefreshSelected()
        {
            if (_qtyText != null) _qtyText.text = _qty.ToString();
            if (_selected == null)
            {
                if (_recipeName != null) _recipeName.text = "(select a recipe)";
                if (_inputsText != null) _inputsText.text = "";
                if (_craftButton != null) _craftButton.interactable = false;
                return;
            }
            if (_recipeName != null)
            {
                var od = EntityDatabase.Get(_selected.output.item);
                _recipeName.text = $"{(od?.Name ?? _selected.output.item)} x{_selected.output.count}";
            }

            bool affordable = true;
            var sb = new System.Text.StringBuilder();
            foreach (var io in EnumInputs(_selected))
            {
                int have = CountItem(io.item);
                int need = io.count * Mathf.Max(1, _qty);
                bool ok = have >= need;
                if (!ok) affordable = false;
                var nd = EntityDatabase.Get(io.item);
                string name = nd?.Name ?? io.item;
                string line = $"{name}  {have}/{need}";
                sb.AppendLine(ok ? line : $"<color=#E06666>{line}</color>");
            }
            if (_inputsText != null) _inputsText.text = sb.ToString();
            if (_craftButton != null) _craftButton.interactable = affordable;
        }

        private void DoCraft()
        {
            if (_selected == null) return;
            Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "craft", recipe = _selected.id, qty = _qty });
        }

        private void AnimateProgress()
        {
            if (_progressFill == null) return;
            float total = _last != null ? _last.total : 0;
            int queue = _last != null ? _last.queue : 0;
            float t = 0f;
            if (queue > 0 && total > 0f)
            {
                float baseProg = _last.progress;
                float prog = Mathf.Min(total, baseProg + (Time.time - _lastStamp) * TickRate);
                t = Mathf.Clamp01(prog / total);
            }
            var rt = _progressFill.rectTransform;
            rt.sizeDelta = new Vector2(226f * t, rt.sizeDelta.y);
            if (_queueText != null)
                _queueText.text = queue > 0 ? $"Crafting… {queue} queued" : "Idle";
        }

        // ---------------------------------------------------------------- echoes / refresh

        private void OnMatchState(Nakama.IMatchState state)
        {
            if (state.OpCode != OpCodes.ContainerUpdate) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ContainerUpdateMessage>(json);
            if (msg == null || msg.gx != _cell.x || msg.gy != _cell.y || !_isOpen) return;
            _last = msg;
            _lastStamp = Time.time;

            if (_isCraft) RefreshOutput();
            else RefreshStorageSlots();
        }

        private void RefreshOutput()
        {
            if (_last?.slots == null) return;
            for (int i = 0; i < _outputSlots.Count; i++)
            {
                if (i < _last.slots.Length) _outputSlots[i].SetSlot(_last.slots[i]);
                else _outputSlots[i].Clear();
            }
        }

        private void RefreshStorageSlots()
        {
            if (_last?.slots != null)
            {
                for (int i = 0; i < _containerSlots.Count; i++)
                {
                    if (i < _last.slots.Length) _containerSlots[i].SetSlot(_last.slots[i]);
                    else _containerSlots[i].Clear();
                }
            }
            var inv = InventoryManager.Instance;
            if (inv?.ItemSlots != null)
                for (int i = 0; i < _playerSlots.Count && i < inv.ItemSlots.Length; i++)
                    _playerSlots[i].SetSlot(inv.ItemSlots[i]);
        }

        private void OnInventoryChanged()
        {
            if (!_isOpen) return;
            if (_isCraft) RefreshSelected();
            else RefreshStorageSlots();
        }

        // ---------------------------------------------------------------- helpers

        private static IEnumerable<RecipeDatabase.RecipeIO> EnumInputs(RecipeDatabase.Recipe r)
        {
            foreach (var io in r.inputs) yield return io;
            if (r.catalyst != null) yield return r.catalyst;
        }

        private static int CountItem(string itemId)
        {
            var inv = InventoryManager.Instance;
            if (inv?.ItemSlots == null) return 0;
            int n = 0;
            foreach (var s in inv.ItemSlots)
                if (s != null && s.item_id == itemId) n += s.count;
            return n;
        }

        private static bool CanAfford(RecipeDatabase.Recipe r, int qty)
        {
            foreach (var io in EnumInputs(r))
                if (CountItem(io.item) < io.count * Mathf.Max(1, qty)) return false;
            return true;
        }

        private static bool IsQuickClick(PointerEventData ev)
        {
            return ev.clickCount >= 2 || Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
        }

        private Button MakeButton(Transform parent, string name, string label,
                                  float x, float y, float w, float h, UnityEngine.Events.UnityAction onClick)
        {
            var rt = UIFactory.MakeRect(parent, name);
            Place(rt, x, y, w, h);
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = UIFactory.UISprite("slot_frame");
            img.type = Image.Type.Sliced;
            img.raycastTarget = true;
            var btn = rt.gameObject.AddComponent<Button>();
            var txt = UIFactory.MakeText(rt, "Label", UIFactory.HeaderSize, UIFactory.TextColor, TextAlignmentOptions.Center);
            UIFactory.Stretch(txt.rectTransform, 0);
            txt.text = label;
            if (onClick != null) btn.onClick.AddListener(onClick);
            return btn;
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f); // top-left of content
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h, Vector2 anchor, Vector2 pivot)
        {
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = pivot;
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private void Send(ContainerActionMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.Container, JsonUtility.ToJson(msg));
        }
    }
}
