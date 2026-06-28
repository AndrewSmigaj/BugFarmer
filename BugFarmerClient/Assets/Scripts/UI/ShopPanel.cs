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
    /// NPC VENDORS as a Canvas panel (replaces the old OnGUI ShopController) — right-click a "shop"
    /// occupant to TALK. A Baldur's-Gate-style DIALOGUE opens first (portrait + greeting + Trade/Goodbye);
    /// [Trade] opens the buy/sell board: BUY items, LEARN recipes (already-known greyed), buy recipe
    /// BOOKS (a collection teaches its whole set), and SELL your items (+ live bugs/carcasses at the bug
    /// dealer). Server-authoritative: every action is an OpCode-Action ShopActionMessage; the panel reads
    /// live from InventoryManager (coins + known_recipes), which the FullInventorySync echo refreshes via
    /// OnInventoryChanged. Mirrors CraftingPanel (UIFactory Canvas UI), with a green vendor accent.
    /// </summary>
    public class ShopPanel : MonoBehaviour
    {
        public static ShopPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 2.5f;
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
        private EntityDatabase.ShopOffer[] _sells, _recipes, _books;

        private CanvasGroup _group;
        private RectTransform _dock, _content;
        private TMP_Text _titleText, _coinText;

        // ------------------------------------------------------------------ lifecycle
        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            _dock = UIFactory.MakeDock(transform, "ShopDock", new Vector2(0.5f, 1f),
                                       new Vector2(0.5f, 1f), new Vector2(560, 440), new Vector2(0, -8));
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            // accent header strip + title
            var head = UIFactory.MakeImage(_dock, "Header", "panel_wood", true);
            head.color = Accent;
            Place(head.rectTransform, 8, -8, 544, 26);
            _titleText = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 1f,
                                            new Color32(238, 228, 204, 255), TextAlignmentOptions.Left);
            Place(_titleText.rectTransform, 18, -12, 380, 18);
            _coinText = UIFactory.MakeText(_dock, "Coins", UIFactory.HeaderSize,
                                           UIFactory.HeaderColor, TextAlignmentOptions.Right);
            Place(_coinText.rectTransform, 420, -12, 122, 18);

            _content = UIFactory.MakeRect(_dock, "Content");
            UIFactory.Stretch(_content, 12);
            ((RectTransform)_content).offsetMax = new Vector2(-12, -38);

            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged += OnInventoryChanged;
            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged -= OnInventoryChanged;
        }

        private void Update()
        {
            if (_isOpen && Input.GetKeyDown(KeyCode.Escape)) SetOpen(false);
        }

        // ------------------------------------------------------------------ open / route
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
            BuildContent();
            SetOpen(true);
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

        // ------------------------------------------------------------------ build
        private void BuildContent()
        {
            for (int i = _content.childCount - 1; i >= 0; i--)
                DestroyImmediate(_content.GetChild(i).gameObject);
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

        private void BuildTrade()
        {
            var known = InventoryManager.Instance != null ? InventoryManager.Instance.KnownRecipes : null;
            float y = 0;

            // BUY
            Header("Buy", 0, y); y -= 18;
            if (_sells != null) RowOfOffers(_sells, y, null);
            y -= 70;

            // LEARN (recipes)
            if (_recipes != null && _recipes.Length > 0)
            {
                Header("Learn", 0, y); y -= 18;
                RowOfOffers(_recipes, y, known);
                y -= 70;
            }

            // RECIPE BOOKS (vertical list)
            if (_books != null && _books.Length > 0)
            {
                Header("Recipe books", 0, y); y -= 20;
                foreach (var bk in _books)
                {
                    if (bk == null || string.IsNullOrEmpty(bk.Id)) continue;
                    var s = UIFactory.MakeSlot(_content, "slot_frame");
                    Place((RectTransform)s.transform, 0, y, UIFactory.Slot, UIFactory.Slot);
                    s.SetSlot(new InventorySlot { item_id = "bookshelf", count = 1 });
                    var captured = bk.Id;
                    s.OnSlotClicked += (slot, ev) => Send("buy", captured, "book", 0);
                    var t = UIFactory.MakeText(_content, "BkName", UIFactory.HeaderSize, UIFactory.TextColor, TextAlignmentOptions.TopLeft);
                    Place(t.rectTransform, 50, y - 2, 320, 16); t.text = Prettify(bk.Id);
                    var p = UIFactory.MakeText(_content, "BkPrice", UIFactory.CountSize, UIFactory.HeaderColor, TextAlignmentOptions.TopLeft);
                    Place(p.rectTransform, 50, y - 22, 320, 14); p.text = $"{bk.Price}c  —  teaches the whole set";
                    y -= 50;
                }
            }

            // SELL (your inventory) — right column
            Header("Sell", 360, 0);
            BuildSell(360, -18);

            // footer
            MakeButton(_content, "Back", "← Back", 360, -240, 80, 24, () => { _mode = Mode.Dialogue; BuildContent(); });
            MakeButton(_content, "Close", "Close", 446, -240, 80, 24, () => SetOpen(false));
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

        private void BuildSell(float bx, float by)
        {
            var inv = InventoryManager.Instance;
            if (inv == null) return;
            int col = 0;
            void Add(string id, int count, string slotType, int slotIdx)
            {
                int price = slotType == "bug"
                    ? (EntityDatabase.GetSpecies(id)?.SellPrice ?? 0)
                    : (EntityDatabase.Get(id)?.SellPrice ?? 0);
                if (price <= 0) return;
                float x = bx + (col % 3) * 52, y = by - (col / 3) * 62;
                var s = UIFactory.MakeSlot(_content, "slot_frame");
                Place((RectTransform)s.transform, x, y, UIFactory.Slot, UIFactory.Slot);
                s.SetSlot(new InventorySlot { item_id = id, count = count });
                string cid = id; int ci = slotIdx; string ct = slotType;
                s.OnSlotClicked += (slot, ev) => Send("sell", cid, ct, ci);
                var lbl = UIFactory.MakeText(_content, "Sp", UIFactory.CountSize, UIFactory.HeaderColor, TextAlignmentOptions.Center);
                Place(lbl.rectTransform, x, y - 42, UIFactory.Slot, 14); lbl.text = $"{price}c";
                col++;
            }
            if (_kind == "bugs")
            {
                for (int i = 0; i < inv.BugSlots.Length; i++)
                {
                    var s = inv.BugSlots[i];
                    if (s != null && !s.IsEmpty) Add(s.item_id, s.count, "bug", i);
                }
                for (int i = 0; i < inv.ItemSlots.Length; i++)
                {
                    var s = inv.ItemSlots[i];
                    if (s != null && !s.IsEmpty && s.item_id.StartsWith("dead_")) Add(s.item_id, s.count, "item", i);
                }
            }
            else
            {
                for (int i = 0; i < inv.ItemSlots.Length; i++)
                {
                    var s = inv.ItemSlots[i];
                    if (s != null && !s.IsEmpty) Add(s.item_id, s.count, "item", i);
                }
            }
        }

        // ------------------------------------------------------------------ refresh
        private void OnInventoryChanged()
        {
            if (!_isOpen) return;
            RefreshCoins();
            if (_mode == Mode.Trade) BuildContent(); // re-grey learned recipes + refresh sell + coins
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
