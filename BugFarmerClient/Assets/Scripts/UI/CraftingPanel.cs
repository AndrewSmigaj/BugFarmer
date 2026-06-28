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
        private bool _openedInventory; // true when opening this container also opened the inventory

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
        private const int MaxInputs = 4;   // recipes have <=3 inputs + an optional catalyst
        private TMP_Text _qtyText;
        private TMP_Text _recipeName;
        private Button _craftButton;
        private Image _progressFill;
        private TMP_Text _queueText;
        // INPUT item-square row (icons + have/need labels) → arrow → output preview (replaces the old text)
        private readonly List<InventorySlotUI> _inputSlots = new List<InventorySlotUI>();
        private readonly List<TMP_Text> _inputLabels = new List<TMP_Text>();
        private InventorySlotUI _outputPreview;
        private TMP_Text _arrow;
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
            ConfigureDock(_isCraft);
            // Storage opens your inventory too (so you can drag items into the chest), and the
            // container docks top-center between the bug + gear docks. If the inventory wasn't
            // already open, WE opened it → close it when the container closes.
            if (!_isCraft && InventoryPanel.Instance != null && !InventoryPanel.IsOpen)
            {
                _openedInventory = true;
                InventoryPanel.Instance.SetOpen(true);
            }
            BuildContent();
            SetOpen(true);
            Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "open" });
        }

        // Craft stations get the big center panel; storage containers get a compact top-center dock
        // (the real inventory shows your side).
        private void ConfigureDock(bool craft)
        {
            // Both dock at the TOP so the screen center stays open for the player. Craft stations
            // need the wider panel (recipes + I/O); containers are a compact grid.
            _dock.anchorMin = _dock.anchorMax = new Vector2(0.5f, 1f);
            _dock.pivot = new Vector2(0.5f, 1f);
            _dock.sizeDelta = craft ? new Vector2(600, 320) : new Vector2(312, 220);
            _dock.anchoredPosition = new Vector2(0, -8);
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

            if (!open && _openedInventory)
            {
                _openedInventory = false;
                InventoryPanel.Instance?.SetOpen(false);
            }
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
            _inputSlots.Clear();
            _inputLabels.Clear();
            _containerSlots.Clear();
            _playerSlots.Clear();
            _qtyText = _recipeName = _queueText = _arrow = null;
            _outputPreview = null;
            _craftButton = null;
            _progressFill = null;

            if (_isCraft) BuildCraftContent();
            else BuildStorageContent();
        }

        private void BuildCraftContent()
        {
            var recipes = RecipeDatabase.ForStation(_occupantId);
            // Hide gated recipes the player hasn't learned. Basic recipes (unlock "" / "default")
            // are always craftable; "shop:<npc>"/"find" recipes appear only once in KnownRecipes.
            var known = InventoryManager.Instance != null ? InventoryManager.Instance.KnownRecipes : null;
            recipes = recipes.FindAll(r =>
                string.IsNullOrEmpty(r.unlock) || r.unlock == "default" ||
                (known != null && known.Contains(r.id)));

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

            // INPUT squares (icon + have/need under each) → arrow → the recipe's OUTPUT preview.
            var needHead = UIFactory.MakeText(_content, "NeedHead", UIFactory.CountSize,
                                              UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(needHead.rectTransform, 160, -22, 230, 14);
            needHead.text = "NEEDS";
            for (int i = 0; i < MaxInputs; i++)
            {
                var s = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)s.transform, 160 + i * 42, -40, UIFactory.Slot, UIFactory.Slot);
                _inputSlots.Add(s);
                var lbl = UIFactory.MakeText(_content, $"In{i}Lbl", UIFactory.CountSize,
                                             UIFactory.TextColor, TextAlignmentOptions.Center);
                Place(lbl.rectTransform, 160 + i * 42, -82, UIFactory.Slot, 14);
                _inputLabels.Add(lbl);
            }
            _arrow = UIFactory.MakeText(_content, "Arrow", UIFactory.HeaderSize + 4f,
                                        UIFactory.HeaderColor, TextAlignmentOptions.Center);
            Place(_arrow.rectTransform, 160, -52, 24, 20);
            _outputPreview = UIFactory.MakeSlot(_content, "slot_frame");
            Place((RectTransform)_outputPreview.transform, 188, -40, UIFactory.Slot, UIFactory.Slot);

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
            // Only the CONTAINER grid here — your inventory (the real left/right docks) is the
            // player side. Move items by double-/shift-click (quick) or by drag (pick a stack up
            // in your inventory → click a container cell to deposit it).
            var def = EntityDatabase.Get(_occupantId);
            var head = UIFactory.MakeText(_content, "ChestHeader", UIFactory.CountSize + 1f,
                                          UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(head.rectTransform, 0, 0, 300, 14);
            head.text = "Double-/shift-click or drag a stack to move it";

            int slotCount = _last?.slots?.Length ?? (def?.World?.ContainerSlots ?? 12);
            var cGrid = UIFactory.MakeGrid(_content, "ContainerGrid", 6, UIFactory.Slot);
            Place((RectTransform)cGrid.transform, 0, -18, 6 * 44, 5 * 44);
            for (int i = 0; i < slotCount; i++)
            {
                var s = UIFactory.MakeSlot(cGrid.transform, "slot_frame");
                int idx = i;
                s.OnSlotClicked += (slot, ev) => OnContainerSlotClicked(idx, ev);
                _containerSlots.Add(s);
            }
            RefreshStorageSlots();
        }

        // Container cell click: a held cursor (a stack picked up from your inventory) DEPOSITS into
        // this cell; otherwise a double-/shift-click quick-moves the cell's stack to your bag.
        private void OnContainerSlotClicked(int idx, PointerEventData ev)
        {
            var drag = DragDropController.Instance;
            if (drag != null && drag.HasCursorItem && drag.CursorSourceType == SlotType.Item)
            {
                Send(new ContainerActionMessage
                {
                    gx = _cell.x, gy = _cell.y, op = "move",
                    zone = "player", slot = drag.CursorSourceIndex,
                    to_zone = "container", to_slot = idx, count = drag.CursorCount
                });
                drag.ForceClearCursor(); // the container handler's full inv-sync reconciles the bag
                return;
            }
            if (IsQuickClick(ev))
                Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "quick", zone = "container", slot = idx });
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

        private static readonly Color ShortColor = new Color32(0xE0, 0x66, 0x66, 0xFF);

        private void RefreshSelected()
        {
            if (_qtyText != null) _qtyText.text = _qty.ToString();
            if (_selected == null)
            {
                if (_recipeName != null) _recipeName.text = "(select a recipe)";
                for (int i = 0; i < _inputSlots.Count; i++) { _inputSlots[i].Clear(); _inputLabels[i].text = ""; }
                _outputPreview?.Clear();
                if (_arrow != null) _arrow.text = "";
                if (_craftButton != null) _craftButton.interactable = false;
                return;
            }
            if (_recipeName != null)
            {
                var od = EntityDatabase.Get(_selected.output.item);
                _recipeName.text = $"{(od?.Name ?? _selected.output.item)} x{_selected.output.count}";
            }

            // Fill the input squares (icon + need badge) with a have/need label coloured red when short.
            bool affordable = true;
            int n = 0;
            foreach (var io in EnumInputs(_selected))
            {
                if (n >= MaxInputs) break;
                int have = CountItem(io.item);
                int need = io.count * Mathf.Max(1, _qty);
                bool ok = have >= need;
                if (!ok) affordable = false;
                _inputSlots[n].SetSlot(new InventorySlot { item_id = io.item, count = need });
                _inputLabels[n].text = $"{have}/{need}";
                _inputLabels[n].color = ok ? UIFactory.TextColor : ShortColor;
                n++;
            }
            for (int i = n; i < _inputSlots.Count; i++) { _inputSlots[i].Clear(); _inputLabels[i].text = ""; }

            // arrow after the last input → the output preview
            if (_arrow != null)
            {
                _arrow.text = "→";
                Place(_arrow.rectTransform, 160 + n * 42, -52, 24, 20);
            }
            if (_outputPreview != null)
            {
                Place((RectTransform)_outputPreview.transform, 160 + n * 42 + 24, -40, UIFactory.Slot, UIFactory.Slot);
                _outputPreview.SetSlot(new InventorySlot { item_id = _selected.output.item, count = _selected.output.count });
            }
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
            float remainingSec = 0f;
            if (queue > 0 && total > 0f)
            {
                float baseProg = _last.progress;
                float prog = Mathf.Min(total, baseProg + (Time.time - _lastStamp) * TickRate);
                t = Mathf.Clamp01(prog / total);
                remainingSec = Mathf.Max(0f, (total - prog) / TickRate);   // ticks → seconds (10 Hz)
            }
            var rt = _progressFill.rectTransform;
            rt.sizeDelta = new Vector2(226f * t, rt.sizeDelta.y);
            if (_queueText != null)
                _queueText.text = queue > 0
                    ? $"Crafting…  {Mathf.CeilToInt(remainingSec)}s left" + (queue > 1 ? $"   ·   x{queue} queued" : "")
                    : "Idle";
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
