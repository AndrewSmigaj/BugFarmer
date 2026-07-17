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
        // Panel mode = the occupant's interaction_type ("craft" | "storage" | "station"). ONE panel serves
        // every processing station; the mode selects which regions BuildContent composes. _isCraft/_isStation
        // are read-only views so the existing craft/storage code is untouched.
        private string _mode = "";
        private bool _isCraft => _mode == "craft";
        private bool _isStation => _mode == "station";
        private bool _isNursery => _mode == "nursery";
        private bool _isBeehive => _mode == "beehive";
        private bool _openedInventory; // true when opening this container also opened the inventory

        // Station-mode caches (compost bin): the material-processor meters + its fly brood, keyed by cell and
        // updated whenever an echo arrives (even while closed) so opening a station shows its state immediately.
        private readonly Dictionary<Vector2Int, StationUpdateMessage> _stationEchoes =
            new Dictionary<Vector2Int, StationUpdateMessage>();
        private readonly Dictionary<Vector2Int, BroodUpdateMessage> _broodEchoes =
            new Dictionary<Vector2Int, BroodUpdateMessage>();
        // Station-mode widgets: the compost deposit grid + its two fill meters (rebuilt per open).
        private readonly List<InventorySlotUI> _depositSlots = new List<InventorySlotUI>();
        private Image _stInputFill, _stCompostFill;
        private TMP_Text _stInputLbl, _stCompostLbl;
        // Shared BROOD region — a compost's fly brood AND a wasp/bee/milkweed nursery all render it: egg/larva/
        // pupa stage slots + count labels + a maturation bar + the resident-adult slot. Click a stage to TAKE
        // its units; click while holding a brood item to PLACE-BACK (deposit). Fed by _broodEchoes[_cell].
        private readonly List<InventorySlotUI> _broodSlots = new List<InventorySlotUI>();
        private readonly List<TMP_Text> _broodCountLbls = new List<TMP_Text>();
        private InventorySlotUI _residentSlot;
        private TMP_Text _residentLbl, _broodEmptyLbl, _broodHead;
        private Image _broodBar;
        private float _broodBarShown, _broodBarTarget;
        private bool _hasBrood; // this open renders a brood region (compost / nursery / beehive)

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
        // PROCESSOR LANES (world.craft_slots, default 1): one row each — recipe icon +
        // interpolated progress bar + queue label. All fed by the per-proc echo (procs[]).
        private readonly List<InventorySlotUI> _procIcons = new List<InventorySlotUI>();
        private readonly List<Image> _procFills = new List<Image>();
        private readonly List<TMP_Text> _procLabels = new List<TMP_Text>();
        private readonly Dictionary<string, string> _recipeOutputById = new Dictionary<string, string>();
        private int _lanesOverride; // echo said more lanes than the def (stale data) → rebuild with this
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
            if (_hasBrood && _broodBar != null)
            {
                _broodBarShown = Mathf.MoveTowards(_broodBarShown, _broodBarTarget, Time.deltaTime * 2f);
                SetBar(_broodBar, _broodBarShown);
            }
        }

        // ---------------------------------------------------------------- open / route

        /// <summary>
        /// Routed right-click (PlayerInputRouter). Opens the craft/storage panel for a station or
        /// chest; closes an open panel when the click lands elsewhere. Returns TRUE on any state
        /// transition (so the click is consumed and never also jabs/places).
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            // Front-most interactable occupant (shared resolver; not a bare OverlapPoint that an
            // overlapping occupant could steal).
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null)
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }

            var def = EntityDatabase.Get(target.OccupantId);
            string it = def?.World?.InteractionType;
            if (it != "craft" && it != "storage" && it != "station" && it != "nursery" && it != "beehive")
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
            _mode = it;
            _selected = null;
            _qty = 1;
            _last = null;
            _lanesOverride = 0;
            Open();
            return true;
        }

        private void Open()
        {
            _title.text = (EntityDatabase.Get(_occupantId)?.Name) ?? _occupantId;
            ConfigureDock();
            // Storage opens your inventory too (drag items into the chest). Craft + station have their own I/O
            // (a station shows its own accepted-item deposit grid), so they don't open the inventory panel.
            if (_mode == "storage" && InventoryPanel.Instance != null && !InventoryPanel.IsOpen)
            {
                _openedInventory = true;
                InventoryPanel.Instance.SetOpen(true);
            }
            BuildContent();
            SetOpen(true);
            // Craft/storage fetch their state via the container "open"; a station is fed by pushed
            // StationUpdate/BroodUpdate echoes (cached by cell), so no open request.
            if (!_isStation)
                Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "open" });
        }

        // Craft stations get the big center panel; storage containers get a compact top-center dock
        // (the real inventory shows your side).
        private void ConfigureDock()
        {
            // Both dock at the TOP so the screen center stays open for the player. Craft stations need the
            // wider panel (recipes + I/O); a station (compost) is a tall column (deposit + meters + brood);
            // containers are a compact grid.
            _dock.anchorMin = _dock.anchorMax = new Vector2(0.5f, 1f);
            _dock.pivot = new Vector2(0.5f, 1f);
            _dock.sizeDelta = _isCraft ? new Vector2(600, 320)
                            : _isStation ? new Vector2(320, 300)
                            : (_isNursery || _isBeehive) ? new Vector2(320, 210)
                            : new Vector2(312, 220);
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
            _procIcons.Clear();
            _procFills.Clear();
            _procLabels.Clear();
            _depositSlots.Clear();
            _broodSlots.Clear();
            _broodCountLbls.Clear();
            _qtyText = _recipeName = _arrow = null;
            _outputPreview = null;
            _craftButton = null;
            _stInputFill = _stCompostFill = null;
            _stInputLbl = _stCompostLbl = null;
            _residentSlot = null;
            _residentLbl = _broodEmptyLbl = null;
            _broodBar = null;
            _hasBrood = false;

            if (_isCraft) BuildCraftContent();
            else if (_isStation) BuildStationContent();
            else if (_isNursery) BuildNurseryContent();
            else if (_isBeehive) BuildBeehiveContent();
            else BuildStorageContent();
        }

        // A pure nursery (wasp nest / milkweed) is just the shared brood region.
        private void BuildNurseryContent()
        {
            BuildBroodRegion(0);
            RefreshBrood();
        }

        // A beehive is a station: bees in (auto), honeycomb out. Shows the resident bees (the shared brood
        // region — bee_honey has no stage sprites, so the stage slots hide) + a honeycomb-harvest control.
        private void BuildBeehiveContent()
        {
            BuildBroodRegion(0);
            MakeButton(_content, "Harvest", "Harvest honeycomb", 0, -152, 170, 26, HarvestHoney);
            RefreshBrood();
        }

        private void HarvestHoney() => SendHive(new HiveHarvestMessage { gx = _cell.x, gy = _cell.y });

        private void SendHive(HiveHarvestMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.HiveHarvest, JsonUtility.ToJson(msg));
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

            // PROCESSOR LANE rows (one per craft_slot): what each lane is making, its progress,
            // and its queue. The recipe-id → output-item map feeds the lane icons.
            _recipeOutputById.Clear();
            foreach (var r in RecipeDatabase.ForStation(_occupantId))
                _recipeOutputById[r.id] = r.output.item;
            int lanes = Mathf.Max(1, Mathf.Max(_lanesOverride,
                EntityDatabase.Get(_occupantId)?.World?.CraftSlots ?? 0));
            for (int i = 0; i < lanes; i++)
            {
                float y = -146 - i * 28;
                var icon = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)icon.transform, 160, y, 24, 24);
                _procIcons.Add(icon);
                var barBg = UIFactory.MakeImage(_content, $"BarBg{i}", "slot_frame", true);
                barBg.color = new Color(0f, 0f, 0f, 0.4f);
                Place(barBg.rectTransform, 190, y - 5, 160, 14);
                var fill = UIFactory.MakeImage(_content, $"BarFill{i}", null);
                fill.color = new Color(0.95f, 0.7f, 0.25f, 1f);
                Place(fill.rectTransform, 192, y - 7, 0, 10);
                _procFills.Add(fill);
                var lbl = UIFactory.MakeText(_content, $"ProcQ{i}", UIFactory.CountSize,
                                             UIFactory.TextColor, TextAlignmentOptions.Left);
                Place(lbl.rectTransform, 356, y - 5, 48, 14);
                _procLabels.Add(lbl);
            }
            RefreshProcs();

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

        // ---------------------------------------------------------------- station (compost) mode
        // A compost bin is a two-aspect station: a material PROCESSOR (deposit compostables → fill meters that
        // bugs feed on) AND a fly NURSERY (its brood, via the SHARED brood region below). Functional
        // placeholder — the owner's mockup drives visual polish.
        private void BuildStationContent()
        {
            var head = UIFactory.MakeText(_content, "DepHead", UIFactory.HeaderSize, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(head.rectTransform, 0, 0, 320, 16);
            head.text = "COMPOST — click an item to deposit";

            var grid = UIFactory.MakeGrid(_content, "DepositGrid", 6, UIFactory.Slot);
            Place((RectTransform)grid.transform, 0, -20, 6 * 44, 2 * 44);
            for (int i = 0; i < 12; i++)
            {
                var s = UIFactory.MakeSlot(grid.transform, "slot_frame");
                int idx = i;
                s.OnSlotClicked += (slot, ev) => DepositAccepted(idx);
                _depositSlots.Add(s);
            }

            _stInputLbl = UIFactory.MakeText(_content, "InLbl", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_stInputLbl.rectTransform, 0, -112, 200, 14);
            var inBg = UIFactory.MakeImage(_content, "InBg", "slot_frame", true); inBg.color = new Color(0f, 0f, 0f, 0.4f);
            Place(inBg.rectTransform, 0, -128, 184, 12);
            _stInputFill = UIFactory.MakeImage(_content, "InFill", null); _stInputFill.color = new Color(0.8f, 0.65f, 0.3f, 1f);
            Place(_stInputFill.rectTransform, 2, -130, 0, 8);

            _stCompostLbl = UIFactory.MakeText(_content, "CoLbl", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_stCompostLbl.rectTransform, 0, -144, 200, 14);
            var coBg = UIFactory.MakeImage(_content, "CoBg", "slot_frame", true); coBg.color = new Color(0f, 0f, 0f, 0.4f);
            Place(coBg.rectTransform, 0, -160, 184, 12);
            _stCompostFill = UIFactory.MakeImage(_content, "CoFill", null); _stCompostFill.color = new Color(0.45f, 0.8f, 0.3f, 1f);
            Place(_stCompostFill.rectTransform, 2, -162, 0, 8);

            BuildBroodRegion(-182); // the compost's fly-brood aspect (shared with the nursery/beehive modes)
            RefreshStation();
        }

        private void RefreshStation()
        {
            var def = EntityDatabase.Get(_occupantId);

            // deposit grid = the accepted items currently in your bag
            var accepts = def?.World?.StationAccepts;
            var inv = InventoryManager.Instance;
            int n = 0;
            if (inv?.ItemSlots != null && accepts != null)
            {
                foreach (var slot in inv.ItemSlots)
                {
                    if (n >= _depositSlots.Count) break;
                    if (slot == null || slot.IsEmpty) continue;
                    bool ok = false;
                    foreach (var a in accepts) if (a == slot.item_id) { ok = true; break; }
                    if (!ok) continue;
                    _depositSlots[n].SetSlot(new InventorySlot(slot.item_id, slot.count));
                    n++;
                }
            }
            for (int i = n; i < _depositSlots.Count; i++) _depositSlots[i].Clear();

            // fill meters
            int input = 0, fill = 0, cap = def?.World?.StationCapacity ?? 10;
            if (_stationEchoes.TryGetValue(_cell, out var st)) { input = st.input; fill = st.fill; cap = st.capacity; }
            if (_stInputLbl != null) _stInputLbl.text = $"Input {input}/{cap}";
            if (_stCompostLbl != null) _stCompostLbl.text = $"Compost {fill}/{cap}";
            SetBar(_stInputFill, cap > 0 ? (float)input / cap : 0f);
            SetBar(_stCompostFill, cap > 0 ? (float)fill / cap : 0f);

            RefreshBrood(); // the compost's fly-brood aspect
        }

        private static void SetBar(Image fill, float frac)
        {
            if (fill == null) return;
            var rt = fill.rectTransform;
            rt.sizeDelta = new Vector2(180f * Mathf.Clamp01(frac), rt.sizeDelta.y);
        }

        private void DepositAccepted(int idx)
        {
            if (idx < 0 || idx >= _depositSlots.Count) return;
            var itemId = _depositSlots[idx].CurrentItemId;
            if (string.IsNullOrEmpty(itemId)) return;
            SendStation(new StationDepositMessage { gx = _cell.x, gy = _cell.y, item_id = itemId });
        }

        // ---------------------------------------------------------------- shared BROOD region (nursery aspect)
        // Every breeding station renders this — a compost's fly brood, a wasp/bee/milkweed nursery: egg/larva/
        // pupa stage slots + count labels + a maturation bar + the resident-adult slot. `y` = the region's top
        // (compost places it below its meters; a pure nursery at the top). Click a stage to TAKE its units;
        // click while holding a brood item to PLACE-BACK (deposit).
        private void BuildBroodRegion(float y)
        {
            _hasBrood = true;

            _broodHead = UIFactory.MakeText(_content, "BrHead", UIFactory.HeaderSize, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(_broodHead.rectTransform, 0, y, 132, 16);
            _broodHead.text = "NURSERY"; // replaced per-species in RefreshBrood (MAGGOTS / BROOD / CATERPILLARS / GRUBS …)
            var hint = UIFactory.MakeText(_content, "BrHint", UIFactory.CountSize - 1f, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(hint.rectTransform, 134, y + 1, 182, 14);
            hint.text = "click to collect · drop to deposit";

            for (int i = 0; i < 3; i++)
            {
                var s = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)s.transform, i * 52, y - 20, UIFactory.Slot, UIFactory.Slot);
                int stage = i;
                s.OnSlotClicked += (slot, ev) => OnBroodStageClicked(stage, ev);
                _broodSlots.Add(s);
                var lbl = UIFactory.MakeText(_content, $"BrC{i}", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Center);
                Place(lbl.rectTransform, i * 52 - 6, y - 62, UIFactory.Slot + 12, 14);
                _broodCountLbls.Add(lbl);
            }

            var barBg = UIFactory.MakeImage(_content, "BrBarBg", "slot_frame", true); barBg.color = new Color(0f, 0f, 0f, 0.4f);
            Place(barBg.rectTransform, 0, y - 80, 184, 12);
            _broodBar = UIFactory.MakeImage(_content, "BrBar", null); _broodBar.color = new Color(0.30f, 0.72f, 0.82f, 1f); // teal — distinct from the green compost fill bar
            Place(_broodBar.rectTransform, 2, y - 82, 0, 8);

            var resHead = UIFactory.MakeText(_content, "ResHead", UIFactory.CountSize, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(resHead.rectTransform, 0, y - 96, 200, 14);
            resHead.text = "INSIDE";
            _residentSlot = UIFactory.MakeSlot(_content, "slot_frame");
            Place((RectTransform)_residentSlot.transform, 0, y - 112, UIFactory.Slot, UIFactory.Slot);
            _residentLbl = UIFactory.MakeText(_content, "ResLbl", UIFactory.CountSize + 1f, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_residentLbl.rectTransform, 46, y - 124, 240, 16);

            _broodEmptyLbl = UIFactory.MakeText(_content, "BrEmpty", UIFactory.CountSize + 1f, UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_broodEmptyLbl.rectTransform, 0, y - 20, 300, 16);
            _broodEmptyLbl.text = "Nothing developing here yet.";
            _broodEmptyLbl.enabled = false;
        }

        private void RefreshBrood()
        {
            if (!_hasBrood) return;
            _broodEchoes.TryGetValue(_cell, out var b);
            bool has = b != null;
            if (_broodEmptyLbl != null) _broodEmptyLbl.enabled = !has;

            var sp = has ? EntityDatabase.GetSpecies(b.species) : null;
            string[] ids = { sp?.EggSpriteId ?? "", sp?.LarvaSpriteId ?? "", sp?.PupaSpriteId ?? "" };
            int[] counts = has ? new[] { b.eggs, b.maggots, b.pupae } : new[] { 0, 0, 0 };
            // Species-appropriate stage words (fly=maggots, wasp/beetle=grubs, butterfly=caterpillars/
            // chrysalises, centi/millipede=young); "brood" only where BroodLabel says a true nest/hive.
            // Fall back to the generic terms when a species omits them.
            string[] names = { "eggs", sp?.LarvaName ?? "larvae", sp?.PupaName ?? "pupae" };
            if (_broodHead != null)
            {
                string label = has ? sp?.BroodLabel : null;
                _broodHead.text = string.IsNullOrEmpty(label) ? "NURSERY" : label.ToUpperInvariant();
            }
            for (int i = 0; i < _broodSlots.Count; i++)
            {
                bool show = has && !string.IsNullOrEmpty(ids[i]);
                _broodSlots[i].gameObject.SetActive(show);
                _broodCountLbls[i].enabled = show;
                if (!show) continue;
                if (counts[i] > 0) _broodSlots[i].SetSlot(new InventorySlot(ids[i], counts[i]));
                else _broodSlots[i].Clear();
                _broodCountLbls[i].text = $"{names[i]}: {counts[i]}";
            }

            _broodBarTarget = has ? Mathf.Clamp01(b.progress) : 0f;

            int residents = has ? b.residents : 0;
            bool showRes = residents > 0;
            if (_residentSlot != null) _residentSlot.gameObject.SetActive(showRes);
            if (_residentLbl != null) _residentLbl.enabled = showRes;
            if (showRes)
            {
                _residentSlot.SetSlot(new InventorySlot(b.species, residents));
                _residentLbl.text = $"× {residents} {(string.IsNullOrEmpty(sp?.Name) ? b.species : sp.Name)}";
            }
        }

        // Click a stage: hold a brood item on the cursor → DEPOSIT it here (place-back, species-validated
        // server-side); otherwise COLLECT this stage's units.
        private void OnBroodStageClicked(int stage, PointerEventData ev)
        {
            if (!_isOpen) return;
            var drag = DragDropController.Instance;
            if (drag != null && drag.HasCursorItem && drag.CursorSourceType == SlotType.Item)
            {
                SendNursery(new NurseryDepositMessage { gx = _cell.x, gy = _cell.y, slot = drag.CursorSourceIndex, count = drag.CursorCount });
                drag.ForceClearCursor();
                return;
            }
            SendNursery(new NurseryTakeMessage { gx = _cell.x, gy = _cell.y, stage = stage, count = 0 });
        }

        private void SendStation(StationDepositMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.StationDeposit, JsonUtility.ToJson(msg));
        }

        private void SendNursery(NurseryTakeMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.NurseryTake, JsonUtility.ToJson(msg));
        }

        private void SendNursery(NurseryDepositMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.NurseryDeposit, JsonUtility.ToJson(msg));
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

            // A recipe is craftable only if some lane can take it (running it already, or idle).
            bool laneFree = PickLane(_selected.id) >= 0;
            if (!laneFree && _recipeName != null) _recipeName.text += "   (all lanes busy)";
            affordable = affordable && laneFree;

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
            int proc = PickLane(_selected.id);
            if (proc < 0) return; // every lane busy with another recipe (button is disabled then)
            Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "craft", recipe = _selected.id, qty = _qty, proc = proc });
        }

        /// <summary>The lane a craft of recipeId should target: a lane already running it (top up
        /// its queue) → the first idle lane → -1 (all lanes busy with other recipes).</summary>
        private int PickLane(string recipeId)
        {
            var procs = _last?.procs;
            if (procs == null || procs.Length == 0) return 0; // pre-echo: lane 0 (server validates)
            for (int i = 0; i < procs.Length; i++)
                if (procs[i].queue > 0 && procs[i].recipe == recipeId) return i;
            for (int i = 0; i < procs.Length; i++)
                if (procs[i].queue <= 0) return i;
            return -1;
        }

        /// <summary>Lane icons from the echo: the recipe's output item while the lane runs.</summary>
        private void RefreshProcs()
        {
            for (int i = 0; i < _procIcons.Count; i++)
            {
                var p = (_last?.procs != null && i < _last.procs.Length) ? _last.procs[i] : null;
                if (p != null && p.queue > 0 && !string.IsNullOrEmpty(p.recipe) &&
                    _recipeOutputById.TryGetValue(p.recipe, out var outItem))
                    _procIcons[i].SetSlot(new InventorySlot(outItem, 1));
                else
                    _procIcons[i].Clear();
            }
        }

        private void AnimateProgress()
        {
            for (int i = 0; i < _procFills.Count; i++)
            {
                var p = (_last?.procs != null && i < _last.procs.Length) ? _last.procs[i] : null;
                int queue = p != null ? p.queue : 0;
                float t = 0f;
                float remainingSec = 0f;
                if (p != null && queue > 0 && p.total > 0)
                {
                    float prog = Mathf.Min(p.total, p.progress + (Time.time - _lastStamp) * TickRate);
                    t = Mathf.Clamp01(prog / p.total);
                    remainingSec = Mathf.Max(0f, (p.total - prog) / TickRate); // ticks → seconds (10 Hz)
                }
                var rt = _procFills[i].rectTransform;
                rt.sizeDelta = new Vector2(156f * t, rt.sizeDelta.y);
                if (i < _procLabels.Count)
                    _procLabels[i].text = queue > 0 ? $"{Mathf.CeilToInt(remainingSec)}s ×{queue}" : "idle";
            }
        }

        // ---------------------------------------------------------------- echoes / refresh

        private void OnMatchState(Nakama.IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            switch (state.OpCode)
            {
                // Station (compost) echoes — cached by cell ALWAYS (even while closed) so opening shows current
                // state; a station's fill meter + its fly brood arrive on these two separate opcodes.
                case OpCodes.StationUpdate:
                {
                    var m = JsonUtility.FromJson<StationUpdateMessage>(json);
                    if (m == null) return;
                    _stationEchoes[new Vector2Int(m.gx, m.gy)] = m;
                    if (_isStation && _isOpen && m.gx == _cell.x && m.gy == _cell.y) RefreshStation();
                    return;
                }
                case OpCodes.BroodUpdate:
                {
                    var m = JsonUtility.FromJson<BroodUpdateMessage>(json);
                    if (m == null) return;
                    var c = new Vector2Int(m.gx, m.gy);
                    if (m.removed || (m.eggs + m.maggots + m.pupae + m.residents) <= 0) _broodEchoes.Remove(c);
                    else _broodEchoes[c] = m;
                    if ((_isStation || _isNursery || _isBeehive) && _isOpen && c == _cell) RefreshBrood();
                    return;
                }
                case OpCodes.ContainerUpdate:
                {
                    var msg = JsonUtility.FromJson<ContainerUpdateMessage>(json);
                    if (msg == null || msg.gx != _cell.x || msg.gy != _cell.y || !_isOpen) return;
                    _last = msg;
                    _lastStamp = Time.time;
                    if (_isCraft)
                    {
                        // Server truth wins on the lane count (stale/missing client craft_slots):
                        // rebuild the rows once, then refresh as normal.
                        if (msg.procs != null && msg.procs.Length > 0 && msg.procs.Length != _procIcons.Count)
                        {
                            _lanesOverride = msg.procs.Length;
                            BuildContent();
                        }
                        RefreshOutput();
                        RefreshProcs();
                        RefreshSelected(); // a lane freeing/filling can flip the Craft button
                    }
                    else RefreshStorageSlots();
                    return;
                }
            }
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
            else if (_isStation) RefreshStation();
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
