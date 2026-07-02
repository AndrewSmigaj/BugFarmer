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
    /// NPC VENDORS as a Canvas panel — right-click a "shop" occupant to TALK. A Baldur's-Gate-style
    /// DIALOGUE opens first (portrait + greeting + Trade/Goodbye); [Trade] opens the buy/sell board:
    /// BUY items, LEARN recipes (already-known greyed), buy recipe BOOKS, and the Apico-style BARTER
    /// SELL — your REAL inventory opens with the shop and you stage stacks into a "to sell" BASKET
    /// (right-click / double-click a slot = whole stack; drag = via the cursor; right-click a basket
    /// cell with a held cursor = one at a time), then ONE "Sell for Xc" sells the whole batch
    /// atomically (server `sell_batch`). Staging is a client-side OVERLAY (StagedQty) the inventory
    /// render consults — inventory DATA is never mutated, so the FullInventorySync repaint (e.g. a
    /// buy mid-shop) can't resurrect a staged slot. Server-authoritative: every action is an
    /// OpCode-Action ShopActionMessage; the panel reads live from InventoryManager, which the
    /// FullInventorySync echo refreshes via OnInventoryChanged. Mirrors CraftingPanel (UIFactory
    /// Canvas UI), with a green vendor accent.
    /// </summary>
    public class ShopPanel : MonoBehaviour
    {
        public static ShopPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 2.5f;
        private const int BasketCells = 8;         // staged-line cap (4 × 2 grid)
        private const float SellReplyTimeout = 3f; // re-enable Sell if no echo (disconnect safety)
        private static readonly Color Accent = new Color32(120, 156, 86, 235);   // vendor green-gold
        private static readonly Color Dim = new Color32(150, 140, 126, 255);

        private enum Mode { Dialogue, Trade }
        private bool _isOpen;
        private Mode _mode = Mode.Dialogue;
        private Vector2Int _cell;
        private string _occId = "";
        private string _title = "Shop";
        private string _kind = "items";
        private string _greeting = "";
        private string[] _buys;
        private EntityDatabase.ShopOffer[] _sells, _recipes, _books;

        // The barter basket: one staged line per source slot. DATA only — the basket grid and the
        // inventory-render overlay both draw from this list, so it survives every BuildContent
        // rebuild and every server repaint.
        private class StagedLine { public SlotType slotType; public int slotIndex; public string id; public int qty; }
        private readonly List<StagedLine> _staged = new List<StagedLine>();
        private bool _openedInventory; // we opened the InventoryPanel with the shop → close it with the shop
        private string _status = "";   // status line under the Sell button (refusals / skips / sold-for)
        private bool _sellPending;     // a sell_batch is in flight; Sell disabled until the echo
        private long _coinsBeforeSell;
        private float _sellSentAt;

        private CanvasGroup _group;
        private RectTransform _dock, _content;
        private TMP_Text _titleText, _coinText, _statusText;
        private Image _headImg;
        private Button _backBtn, _closeBtn;

        // ------------------------------------------------------------------ lifecycle
        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            // The dock stays SHORT (ConfigureDock): the UI canvas is 800×600-reference width-matched,
            // so a 16:9 window is only ~450 canvas-units tall — a tall dock would cover the
            // bottom-docked InventoryPanel the barter board trades out of.
            _dock = UIFactory.MakeDock(transform, "ShopDock", new Vector2(0.5f, 1f),
                                       new Vector2(0.5f, 1f), new Vector2(560, 200), new Vector2(0, -8));
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            // accent header strip + title + coins + Back/Close (sized per-mode in ConfigureDock)
            _headImg = UIFactory.MakeImage(_dock, "Header", "panel_wood", true);
            _headImg.color = Accent;
            _titleText = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 1f,
                                            new Color32(238, 228, 204, 255), TextAlignmentOptions.Left);
            _coinText = UIFactory.MakeText(_dock, "Coins", UIFactory.HeaderSize,
                                           UIFactory.HeaderColor, TextAlignmentOptions.Right);
            _backBtn = MakeButton(_dock, "Back", "← Back", 0, 0, 62, 20,
                                  () => { _mode = Mode.Dialogue; BuildContent(); });
            _closeBtn = MakeButton(_dock, "Close", "X", 0, 0, 30, 20, () => SetOpen(false));

            _content = UIFactory.MakeRect(_dock, "Content");
            UIFactory.Stretch(_content, 12);
            ((RectTransform)_content).offsetMax = new Vector2(-12, -38);

            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged += OnInventoryChanged;
            // Server refusals ride OpCode 40 (ErrorMessage) — surface them in the shop status line
            // (mirrors CraftingPanel's direct socket subscription for its opcode-99 echo).
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState += OnMatchState;
            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged -= OnInventoryChanged;
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState -= OnMatchState;
        }

        private void Update()
        {
            if (!_isOpen) return;
            if (Input.GetKeyDown(KeyCode.Escape)) { SetOpen(false); return; }
            // Disconnect safety: a sell_batch whose echo never arrives must not wedge the button.
            if (_sellPending && Time.time - _sellSentAt > SellReplyTimeout)
            {
                _sellPending = false;
                SetStatus("No reply — try again");
                if (_mode == Mode.Trade) BuildContent();
            }
        }

        // ------------------------------------------------------------------ open / route
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
            if (def?.World == null || def.World.InteractionType != "shop")
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > MaxInteractDistance * MaxInteractDistance) return false;
            }
            if (_isOpen && _cell == target.AnchorCell) { SetOpen(false); return true; }

            _cell = target.AnchorCell;
            _occId = target.OccupantId;
            _title = def.Name ?? target.OccupantId;
            _kind = def.World.ShopKind ?? "items";
            _buys = def.World.ShopBuys;
            _sells = def.World.ShopSells;
            _recipes = def.World.ShopRecipes;
            _books = def.World.ShopBooks;
            _greeting = string.IsNullOrEmpty(def.World.Greeting)
                ? "Welcome, traveler. Care to trade?" : def.World.Greeting;
            _mode = Mode.Dialogue;
            Open();
            return true;
        }

        private void Open()
        {
            _titleText.text = _title;
            ClearBasketAndRepaint(); // switching vendors while open must un-hide the old staging
            _sellPending = false;
            // A held drag cursor is returned to its slot so every mid-shop pickup starts clean —
            // this keeps the cursor/staging bookkeeping's "server slot = local slot + cursor"
            // invariant trivially true (see DragDropController.TryTakeCursorForStaging).
            DragDropController.Instance?.CancelToSource();
            // The barter board trades out of your REAL inventory — open it with the shop
            // (mirrors the CraftingPanel storage precedent; close it with the shop if WE opened it).
            if (InventoryPanel.Instance != null && !InventoryPanel.IsOpen)
            {
                _openedInventory = true;
                InventoryPanel.Instance.SetOpen(true);
            }
            BuildContent();
            SetOpen(true);
        }

        private void SetOpen(bool open)
        {
            bool wasOpen = _isOpen;
            _isOpen = open;
            if (_group != null)
            {
                _group.alpha = open ? 1f : 0f;
                _group.blocksRaycasts = open;
                _group.interactable = open;
            }
            _dock.gameObject.SetActive(open);

            if (!open && wasOpen)
            {
                // Cancel = clear the overlay; nothing to restore (data was never mutated).
                ClearBasketAndRepaint();
                _sellPending = false;
                if (_openedInventory)
                {
                    _openedInventory = false;
                    InventoryPanel.Instance?.SetOpen(false);
                }
            }
        }

        /// <summary>Empty the basket and repaint the slots that were rendering reduced — the
        /// overlay is view-only, so "restore" is just a repaint.</summary>
        private void ClearBasketAndRepaint()
        {
            var toRepaint = new List<StagedLine>(_staged);
            _staged.Clear();
            _status = "";
            foreach (var ln in toRepaint)
                InventoryManager.Instance?.NotifyLocalSlotMutation(ln.slotType, ln.slotIndex);
        }

        // ------------------------------------------------------------------ staging (the overlay)

        /// <summary>How many of slot (type,index) are staged in the basket. The inventory render
        /// (InventoryPanel + HotbarUI) subtracts this so staged stacks visibly leave the bag —
        /// without ever touching InventoryManager data (repaint-immune by construction).</summary>
        public static int StagedQty(SlotType type, int index)
        {
            var inst = Instance;
            if (inst == null || !inst._isOpen) return 0;
            foreach (var ln in inst._staged)
                if (ln.slotType == type && ln.slotIndex == index) return ln.qty;
            return 0;
        }

        /// <summary>The slot as the inventory should DRAW it: the real slot minus any staged share
        /// (null = draw empty). Pure view transform — never mutates the slot.</summary>
        public static InventorySlot ForRender(SlotType type, int index, InventorySlot slot)
        {
            int staged = StagedQty(type, index);
            if (staged <= 0 || slot == null || slot.IsEmpty) return slot;
            int remaining = slot.count - staged;
            return remaining > 0 ? new InventorySlot(slot.item_id, remaining) : null;
        }

        /// <summary>Right-click stage verb (DragDropController routes here while a shop is open):
        /// stage the slot's whole remaining stack. Returns FALSE when this vendor won't buy the
        /// item so the click falls through to its normal verb (bug info card, quick-equip, …).</summary>
        public static bool TryStageSlot(InventorySlotUI slot)
        {
            var inst = Instance;
            var inv = InventoryManager.Instance;
            if (inst == null || !inst._isOpen || slot == null || inv == null) return false;
            if (slot.SlotType == SlotType.Equipment) return false;

            var data = slot.SlotType == SlotType.Bug
                ? (slot.SlotIndex < inv.BugSlots.Length ? inv.BugSlots[slot.SlotIndex] : null)
                : (slot.SlotIndex < inv.ItemSlots.Length ? inv.ItemSlots[slot.SlotIndex] : null);
            if (data == null || data.IsEmpty) return false;

            if (!inst.CanStageId(slot.SlotType, data.item_id, out string reason))
                return false; // not sellable here → the click keeps its normal meaning

            int avail = data.count - StagedQty(slot.SlotType, slot.SlotIndex);
            if (avail <= 0) return true; // already fully staged — consume the click
            inst.Stage(slot.SlotType, slot.SlotIndex, data.item_id, avail);
            return true;
        }

        /// <summary>Double-click stage verb: the 1st click of the double-click picked the stack
        /// onto the drag cursor; this stages the CURSOR (whole stack). Returns false (fall through
        /// to the normal put-back) when the vendor won't buy it.</summary>
        public static bool TryStageCursor()
        {
            var inst = Instance;
            var drag = DragDropController.Instance;
            if (inst == null || !inst._isOpen || drag == null || !drag.HasCursorItem) return false;
            if (!inst.CanStageId(drag.CursorSourceType, drag.CursorItemId, out string reason))
            {
                inst.SetStatus(reason);
                return false;
            }
            if (drag.TryTakeCursorForStaging(drag.CursorCount, out var t, out var idx, out var id, out var taken) && taken > 0)
                inst.Stage(t, idx, id, taken);
            return true; // the cursor was consumed (or safely returned) — never fall through
        }

        /// <summary>Mirrors the server filter `shopBuysItem`: a bug dealer takes live bugs + any
        /// dead_* carcass; an item vendor takes ids/tags in its buys list. Also requires a positive
        /// payout (selling for 0 is a trap, and matches the old sell list's price filter).</summary>
        private bool CanStageId(SlotType type, string id, out string reason)
        {
            if (_kind == "bugs")
            {
                if (type == SlotType.Bug)
                {
                    if ((EntityDatabase.GetSpecies(id)?.SellPrice ?? 0) > 0) { reason = null; return true; }
                    reason = "They won't pay for that bug";
                    return false;
                }
                if (id.StartsWith("dead_") && (EntityDatabase.Get(id)?.SellPrice ?? 0) > 0)
                {
                    reason = null;
                    return true;
                }
                reason = "They only buy bugs and carcasses";
                return false;
            }

            if (type == SlotType.Bug) { reason = "They don't buy live bugs"; return false; }
            var def = EntityDatabase.Get(id);
            if (def == null || def.SellPrice <= 0) { reason = "That's worthless to them"; return false; }
            if (_buys != null)
            {
                foreach (var b in _buys)
                {
                    if (b == id) { reason = null; return true; }
                    if (def.Tags != null)
                        foreach (var t in def.Tags)
                            if (t == b) { reason = null; return true; }
                }
            }
            reason = "They don't buy that";
            return false;
        }

        private int UnitPrice(SlotType type, string id) => type == SlotType.Bug
            ? (EntityDatabase.GetSpecies(id)?.SellPrice ?? 0)
            : (EntityDatabase.Get(id)?.SellPrice ?? 0);

        private void Stage(SlotType type, int index, string id, int qty)
        {
            if (qty <= 0) return;
            foreach (var ln in _staged)
            {
                if (ln.slotType == type && ln.slotIndex == index)
                {
                    ln.qty += qty;
                    InventoryManager.Instance?.NotifyLocalSlotMutation(type, index);
                    return;
                }
            }
            if (_staged.Count >= BasketCells) { SetStatus("The basket is full"); return; }
            _staged.Add(new StagedLine { slotType = type, slotIndex = index, id = id, qty = qty });
            InventoryManager.Instance?.NotifyLocalSlotMutation(type, index);
        }

        private void Unstage(int lineIdx, int qty)
        {
            if (lineIdx < 0 || lineIdx >= _staged.Count) return;
            var ln = _staged[lineIdx];
            ln.qty -= qty;
            if (ln.qty <= 0) _staged.RemoveAt(lineIdx);
            InventoryManager.Instance?.NotifyLocalSlotMutation(ln.slotType, ln.slotIndex);
        }

        /// <summary>Drop lines whose slot no longer backs them (sold, consumed, or changed) and
        /// clamp any line the server shrank — runs on every inventory echo.</summary>
        private void RevalidateStaged()
        {
            var inv = InventoryManager.Instance;
            if (inv == null) return;
            for (int i = _staged.Count - 1; i >= 0; i--)
            {
                var ln = _staged[i];
                var slot = ln.slotType == SlotType.Bug
                    ? (ln.slotIndex < inv.BugSlots.Length ? inv.BugSlots[ln.slotIndex] : null)
                    : (ln.slotIndex < inv.ItemSlots.Length ? inv.ItemSlots[ln.slotIndex] : null);
                if (slot == null || slot.IsEmpty || slot.item_id != ln.id) { _staged.RemoveAt(i); continue; }
                if (ln.qty > slot.count) ln.qty = slot.count;
            }
        }

        private void DoSellBatch()
        {
            if (_staged.Count == 0 || _sellPending) return;
            var lines = new ShopSellLine[_staged.Count];
            for (int i = 0; i < _staged.Count; i++)
            {
                lines[i] = new ShopSellLine
                {
                    slot_type = _staged[i].slotType == SlotType.Bug ? "bug" : "item",
                    slot = _staged[i].slotIndex,
                    id = _staged[i].id,
                    qty = _staged[i].qty,
                };
            }
            _coinsBeforeSell = InventoryManager.Instance?.Coins ?? 0;
            _sellPending = true;
            _sellSentAt = Time.time;
            _status = "Selling…";

            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
            {
                _sellPending = false;
                SetStatus("Not connected");
                return;
            }
            var msg = new ShopActionMessage { gx = _cell.x, gy = _cell.y, op = "sell_batch", lines = lines };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.Action, JsonUtility.ToJson(msg));
            BuildContent(); // re-render with Sell disabled
        }

        private void SetStatus(string text)
        {
            _status = text ?? "";
            if (_statusText != null) _statusText.text = _status;
        }

        // ------------------------------------------------------------------ build

        // Per-mode dock geometry. Trade is WIDE + SHORT (780×226): on a 16:9 window the width-matched
        // 800-reference canvas is ~450 units tall and the InventoryPanel's item rows top out at
        // 164-208 from the bottom — a 226-tall top dock leaves the whole bag visible below it.
        private void ConfigureDock()
        {
            float w = _mode == Mode.Trade ? 780f : 560f;
            float h = _mode == Mode.Trade ? 226f : 200f;
            _dock.sizeDelta = new Vector2(w, h);
            Place(_headImg.rectTransform, 8, -8, w - 16, 26);
            Place(_titleText.rectTransform, 18, -12, w - 326, 18); // ends where the coins begin
            Place(_coinText.rectTransform, w - 300, -12, 140, 18);
            Place((RectTransform)_backBtn.transform, w - 150, -11, 62, 20);
            Place((RectTransform)_closeBtn.transform, w - 82, -11, 30, 20);
            _backBtn.gameObject.SetActive(_mode == Mode.Trade);
        }

        private void BuildContent()
        {
            ConfigureDock();
            for (int i = _content.childCount - 1; i >= 0; i--)
                DestroyImmediate(_content.GetChild(i).gameObject);
            _statusText = null;
            RefreshCoins();
            _titleText.text = _mode == Mode.Trade ? $"{_title}   ·   Trade" : _title;
            if (_mode == Mode.Dialogue) BuildDialogue();
            else BuildTrade();
        }

        private void BuildDialogue()
        {
            // portrait
            var frame = UIFactory.MakeImage(_content, "PortFrame", "slot_frame");
            Place(frame.rectTransform, 4, -8, 96, 96);
            var port = UIFactory.MakeImage(_content, "Portrait", null);
            Place(port.rectTransform, 12, -16, 80, 80);
            var sp = EntityDatabase.GetWorldSprite(_occId);
            if (sp != null) { port.sprite = sp; port.preserveAspect = true; }
            else port.enabled = false;

            var line = UIFactory.MakeText(_content, "Greeting", UIFactory.HeaderSize,
                                          UIFactory.TextColor, TextAlignmentOptions.TopLeft);
            line.enableWordWrapping = true;
            Place(line.rectTransform, 116, -16, 410, 80);
            line.text = $"“{_greeting}”";

            MakeButton(_content, "Trade", "Trade", 116, -110, 150, 32, () => { _mode = Mode.Trade; BuildContent(); }, primary: true);
            MakeButton(_content, "Goodbye", "Goodbye", 276, -110, 150, 32, () => SetOpen(false));
        }

        // Compact three-column trade board (fits the 226-tall dock): Buy+Learn rows on the left,
        // a slim Books column in the middle, the sell basket on the right. Back/Close live in the
        // header strip (ConfigureDock), not a footer — vertical space is the scarce axis.
        private void BuildTrade()
        {
            var known = InventoryManager.Instance != null ? InventoryManager.Instance.KnownRecipes : null;
            float w = _dock.sizeDelta.x - 24f; // content width (12 inset each side)

            // BUY (left column)
            Header("Buy", 0, 0);
            if (_sells != null) RowOfOffers(_sells, -18, null);

            // LEARN (recipes)
            if (_recipes != null && _recipes.Length > 0)
            {
                Header("Learn", 0, -84);
                RowOfOffers(_recipes, -102, known);
            }

            // RECIPE BOOKS (slim middle column, up to 3)
            if (_books != null && _books.Length > 0)
            {
                Header("Books", 370, 0);
                float yB = -18;
                int shown = 0;
                foreach (var bk in _books)
                {
                    if (bk == null || string.IsNullOrEmpty(bk.Id) || shown >= 3) continue;
                    var s = UIFactory.MakeSlot(_content, "slot_frame");
                    Place((RectTransform)s.transform, 370, yB, UIFactory.Slot, UIFactory.Slot);
                    s.SetSlot(new InventorySlot { item_id = "bookshelf", count = 1 });
                    var captured = bk.Id;
                    s.OnSlotClicked += (slot, ev) => Send("buy", captured, "book", 0);
                    var t = UIFactory.MakeText(_content, "BkName", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.TopLeft);
                    t.enableWordWrapping = true;
                    Place(t.rectTransform, 414, yB - 2, 116, 44);
                    t.text = $"{Prettify(bk.Id)}\n{bk.Price}c — whole set";
                    yB -= 48;
                    shown++;
                }
            }

            // SELL — the barter basket (right column). Your REAL inventory is the item source:
            // right-click / double-click a bag or hotbar stack to stage it here.
            BuildBasket(w - 220f);
        }

        // A horizontal row of up to 8 offer slots (price label under each; greyed if known).
        private void RowOfOffers(EntityDatabase.ShopOffer[] offers, float y, HashSet<string> known)
        {
            int col = 0;
            foreach (var off in offers)
            {
                if (off == null || string.IsNullOrEmpty(off.Id) || col >= 6) continue;
                float x = col * 52;
                var s = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)s.transform, x, y, UIFactory.Slot, UIFactory.Slot);
                s.SetSlot(new InventorySlot { item_id = off.Id, count = 1 });
                bool isRecipe = known != null;
                bool have = isRecipe && known.Contains(off.Id);
                s.SetDimmed(have);
                var captured = off.Id;
                if (!have)
                    s.OnSlotClicked += (slot, ev) => Send("buy", captured, isRecipe ? "recipe" : "", 0);
                var lbl = UIFactory.MakeText(_content, "Price", UIFactory.CountSize,
                                             have ? Dim : UIFactory.HeaderColor, TextAlignmentOptions.Center);
                Place(lbl.rectTransform, x, y - 42, UIFactory.Slot, 14);
                lbl.text = have ? "known" : $"{off.Price}c";
                col++;
            }
        }

        private void BuildBasket(float bx)
        {
            Header("Sell", bx, 0);

            // What this vendor buys, inline after the header (the honest filter — mirrors the
            // server's shopBuysItem).
            var buysLbl = UIFactory.MakeText(_content, "Buys", UIFactory.CountSize,
                                             Dim, TextAlignmentOptions.TopLeft);
            buysLbl.enableWordWrapping = false;
            Place(buysLbl.rectTransform, bx + 40, -2, 180, 14);
            if (_kind == "bugs")
                buysLbl.text = "buys: live bugs, carcasses";
            else if (_buys != null && _buys.Length > 0)
                buysLbl.text = "buys: " + string.Join(", ", _buys);
            else
                buysLbl.text = "buys: nothing";

            // Basket grid (4 × 2): staged stacks render as slots; empty cells accept a held cursor.
            long total = 0;
            for (int i = 0; i < BasketCells; i++)
            {
                float x = bx + (i % 4) * 44, y = -18 - (i / 4) * 44;
                var cell = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)cell.transform, x, y, UIFactory.Slot, UIFactory.Slot);
                if (i < _staged.Count)
                {
                    cell.SetSlot(new InventorySlot(_staged[i].id, _staged[i].qty));
                    total += (long)UnitPrice(_staged[i].slotType, _staged[i].id) * _staged[i].qty;
                }
                int captured = i;
                cell.OnSlotClicked += (slot, ev) => OnBasketCellClicked(captured, ev);
            }

            // "Sell for Xc" — greyed when the basket is empty or a sale is in flight.
            var sellBtn = MakeButton(_content, "SellAll", total > 0 ? $"Sell for {total}c" : "Sell",
                                     bx, -108, 176, 24, DoSellBatch, primary: total > 0 && !_sellPending);
            sellBtn.interactable = _staged.Count > 0 && !_sellPending;

            _statusText = UIFactory.MakeText(_content, "SellStatus", UIFactory.CountSize,
                                             UIFactory.TextColor, TextAlignmentOptions.TopLeft);
            _statusText.enableWordWrapping = true;
            Place(_statusText.rectTransform, bx, -136, 216, 40);
            _statusText.text = _status;
        }

        // Basket cell click: a held cursor DEPOSITS into the basket (left = all, right = ONE — the
        // existing drop-one convention); otherwise clicking a staged line returns it to the bag
        // (left = whole line, right = one).
        private void OnBasketCellClicked(int cellIdx, PointerEventData ev)
        {
            var drag = DragDropController.Instance;
            if (drag != null && drag.HasCursorItem)
            {
                if (!CanStageId(drag.CursorSourceType, drag.CursorItemId, out string reason))
                {
                    SetStatus(reason);
                    return;
                }
                int want = ev.button == PointerEventData.InputButton.Right ? 1 : drag.CursorCount;
                if (drag.TryTakeCursorForStaging(want, out var t, out var idx, out var id, out var taken) && taken > 0)
                    Stage(t, idx, id, taken);
                return;
            }
            if (cellIdx >= _staged.Count) return;
            Unstage(cellIdx, ev.button == PointerEventData.InputButton.Right ? 1 : int.MaxValue);
        }

        // ------------------------------------------------------------------ refresh
        private void OnInventoryChanged()
        {
            if (!_isOpen) return;
            if (_sellPending)
            {
                // The sell_batch echo landed: report the payout from the coin delta; skipped lines
                // stay staged (their slots are unchanged) with the server's opcode-40 text below.
                _sellPending = false;
                long delta = (InventoryManager.Instance?.Coins ?? 0) - _coinsBeforeSell;
                if (delta > 0)
                    _status = _status.StartsWith("Didn't sell") ? $"Sold for {delta}c — {_status}" : $"Sold for {delta}c";
            }
            RevalidateStaged();
            RefreshCoins();
            if (_mode == Mode.Trade) BuildContent(); // re-grey learned recipes + refresh basket + coins
        }

        private void OnMatchState(Nakama.IMatchState state)
        {
            if (state.OpCode != OpCodes.ErrorMessage || !_isOpen) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ErrorMessage>(json);
            if (msg == null || string.IsNullOrEmpty(msg.error)) return;
            SetStatus(msg.error);
            // An all-lines-refused batch sends the error WITHOUT an inventory echo — unwedge Sell.
            if (_sellPending)
            {
                _sellPending = false;
                if (_mode == Mode.Trade) BuildContent();
            }
        }

        private void RefreshCoins()
        {
            if (_coinText != null)
                _coinText.text = $"{(InventoryManager.Instance != null ? InventoryManager.Instance.Coins : 0)}c";
        }

        // ------------------------------------------------------------------ helpers
        private void Header(string s, float x, float y)
        {
            var t = UIFactory.MakeText(_content, "H", UIFactory.HeaderSize, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(t.rectTransform, x, y, 200, 16); t.text = s;
        }

        private static string Prettify(string id)
        {
            if (string.IsNullOrEmpty(id)) return id;
            var parts = id.Split('_');
            for (int i = 0; i < parts.Length; i++)
                if (parts[i].Length > 0) parts[i] = char.ToUpper(parts[i][0]) + parts[i].Substring(1);
            return string.Join(" ", parts);
        }

        private Button MakeButton(Transform parent, string name, string label,
                                  float x, float y, float w, float h, UnityEngine.Events.UnityAction onClick, bool primary = false)
        {
            var rt = UIFactory.MakeRect(parent, name);
            Place(rt, x, y, w, h);
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = UIFactory.UISprite("slot_frame");
            img.type = Image.Type.Sliced;
            if (primary) img.color = new Color32(214, 170, 58, 255);
            img.raycastTarget = true;
            var btn = rt.gameObject.AddComponent<Button>();
            var txt = UIFactory.MakeText(rt, "Label", UIFactory.HeaderSize,
                                         primary ? new Color32(36, 28, 18, 255) : UIFactory.TextColor, TextAlignmentOptions.Center);
            UIFactory.Stretch(txt.rectTransform, 0);
            txt.text = label;
            if (onClick != null) btn.onClick.AddListener(onClick);
            return btn;
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private void Send(string op, string id, string slotType, int slot)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            var msg = new ShopActionMessage
            {
                gx = _cell.x, gy = _cell.y, op = op, id = id, qty = 1, slot = slot, slot_type = slotType,
            };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.Action, JsonUtility.ToJson(msg));
        }
    }
}
