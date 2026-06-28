using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// NPC VENDORS — right-click a "shop" occupant to talk. A Baldur's-Gate-style DIALOGUE opens first
    /// (the NPC's greeting + [Trade] / [Goodbye]); [Trade] opens the Buy/Sell panel. Buy items from the
    /// NPC's stock, LEARN recipes (already-known greyed), buy recipe-BOOKS (a collection teaches its whole
    /// set), and sell your items (+ live bugs/carcasses at the bug dealer), for coins. The server is
    /// authoritative for every price + check; the panel reads live from InventoryManager, which the
    /// FullInventorySync echo refreshes after each trade (coins + slots + known_recipes), so no
    /// client-side optimistic bookkeeping. Mirrors StationController.
    /// </summary>
    public class ShopController : MonoBehaviour
    {
        [SerializeField] private float maxInteractDistance = 2.5f;

        private enum Mode { Dialogue, Trade }   // BG-style: greet first, Trade opens the buy/sell panel
        private bool _open;
        private Mode _mode = Mode.Dialogue;
        private Vector2Int _cell;
        private string _title = "Shop";
        private string _kind = "items";
        private string _greeting = "";
        private EntityDatabase.ShopOffer[] _sells;
        private EntityDatabase.ShopOffer[] _recipes;   // D26: learnable recipes
        private EntityDatabase.ShopOffer[] _books;     // D26: recipe-book collections
        private Vector2 _scroll;

        /// <summary>Routed right-click (PlayerInputRouter owns it). Returns true on any open/close/toggle
        /// state change so the click is consumed (never also jabs/places).</summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            var hit = Physics2D.OverlapPoint(mouseWorld);
            var target = hit != null ? hit.GetComponent<OccupantClickTarget>() : null;
            if (target == null)
            {
                if (_open) { _open = false; return true; }
                return false;
            }

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "shop")
            {
                if (_open) { _open = false; return true; }
                return false;
            }

            // Range check (client convenience; server re-validates).
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > maxInteractDistance * maxInteractDistance)
                    return false;
            }

            if (_open && _cell == target.AnchorCell) { _open = false; return true; } // re-click closes
            _cell = target.AnchorCell;
            _title = def.Name ?? target.OccupantId;
            _kind = def.World.ShopKind ?? "items";
            _sells = def.World.ShopSells;
            _recipes = def.World.ShopRecipes;
            _books = def.World.ShopBooks;
            _greeting = string.IsNullOrEmpty(def.World.Greeting)
                ? "Welcome, traveler. Care to trade?" : def.World.Greeting;
            _mode = Mode.Dialogue;   // greet first; [Trade] opens the panel
            _open = true;
            return true;
        }

        private void OnGUI()
        {
            if (!_open) return;
            var inv = InventoryManager.Instance;
            const int W = 340;
            GUILayout.BeginArea(new Rect(Screen.width / 2f - W / 2f, 60, W, 470), GUI.skin.box);
            GUILayout.Label($"=== {_title} ===    Coins: {(inv != null ? inv.Coins : 0)}");
            if (_mode == Mode.Dialogue) DrawDialogue();
            else DrawTrade(inv);
            GUILayout.EndArea();
        }

        // Baldur's-Gate-style greeting: a line + Trade / Goodbye.
        private void DrawDialogue()
        {
            GUILayout.Space(8);
            GUILayout.Label(_greeting);
            GUILayout.Space(14);
            if (GUILayout.Button("Trade")) _mode = Mode.Trade;
            if (GUILayout.Button("Goodbye")) _open = false;
        }

        private void DrawTrade(InventoryManager inv)
        {
            _scroll = GUILayout.BeginScrollView(_scroll);

            // --- BUY (the NPC's stock) ---
            GUILayout.Label("Buy:");
            if (_sells != null)
            {
                foreach (var offer in _sells)
                {
                    if (offer == null || string.IsNullOrEmpty(offer.Id)) continue;
                    if (GUILayout.Button($"{NameOf(offer.Id)}  —  {offer.Price}c"))
                        Send("buy", offer.Id, "", 0);
                }
            }

            // --- LEARN (recipes the NPC teaches; already-known are greyed) ---
            var known = inv != null ? inv.KnownRecipes : null;
            if (_recipes != null)
            {
                GUILayout.Space(6);
                GUILayout.Label("Learn:");
                foreach (var r in _recipes)
                {
                    if (r == null || string.IsNullOrEmpty(r.Id)) continue;
                    bool have = known != null && known.Contains(r.Id);
                    GUI.enabled = !have;
                    if (GUILayout.Button(have ? $"{NameOf(r.Id)}  —  (known)"
                                              : $"{NameOf(r.Id)}  —  {r.Price}c"))
                        Send("buy", r.Id, "recipe", 0);
                    GUI.enabled = true;
                }
            }

            // --- RECIPE BOOKS (a collection teaches its whole set) ---
            if (_books != null)
            {
                GUILayout.Space(6);
                GUILayout.Label("Recipe books:");
                foreach (var bk in _books)
                {
                    if (bk == null || string.IsNullOrEmpty(bk.Id)) continue;
                    if (GUILayout.Button($"{Prettify(bk.Id)} (book)  —  {bk.Price}c"))
                        Send("buy", bk.Id, "book", 0);
                }
            }

            // --- SELL (your inventory the NPC will take) ---
            GUILayout.Space(8);
            GUILayout.Label("Sell:");
            if (inv != null)
            {
                if (_kind == "bugs")
                {
                    for (int i = 0; i < inv.BugSlots.Length; i++)
                    {
                        var s = inv.BugSlots[i];
                        if (s == null || s.IsEmpty) continue;
                        int price = EntityDatabase.GetSpecies(s.item_id)?.SellPrice ?? 0;
                        if (GUILayout.Button($"{NameOf(s.item_id)} x{s.count}  →  {price}c ea"))
                            Send("sell", s.item_id, "bug", i);
                    }
                    for (int i = 0; i < inv.ItemSlots.Length; i++)
                    {
                        var s = inv.ItemSlots[i];
                        if (s == null || s.IsEmpty || !s.item_id.StartsWith("dead_")) continue;
                        int price = EntityDatabase.Get(s.item_id)?.SellPrice ?? 0;
                        if (GUILayout.Button($"{NameOf(s.item_id)} x{s.count}  →  {price}c ea"))
                            Send("sell", s.item_id, "item", i);
                    }
                }
                else
                {
                    for (int i = 0; i < inv.ItemSlots.Length; i++)
                    {
                        var s = inv.ItemSlots[i];
                        if (s == null || s.IsEmpty) continue;
                        int price = EntityDatabase.Get(s.item_id)?.SellPrice ?? 0;
                        if (price <= 0) continue; // can't be sold anywhere
                        if (GUILayout.Button($"{NameOf(s.item_id)} x{s.count}  →  {price}c ea"))
                            Send("sell", s.item_id, "item", i);
                    }
                }
            }

            GUILayout.EndScrollView();
            GUILayout.Space(6);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("← Back")) _mode = Mode.Dialogue;
            if (GUILayout.Button("Close")) _open = false;
            GUILayout.EndHorizontal();
        }

        /// <summary>Title-case a snake_case id for display (recipe-book collection ids aren't entities).</summary>
        private static string Prettify(string id)
        {
            if (string.IsNullOrEmpty(id)) return id;
            var parts = id.Split('_');
            for (int i = 0; i < parts.Length; i++)
                if (parts[i].Length > 0)
                    parts[i] = char.ToUpper(parts[i][0]) + parts[i].Substring(1);
            return string.Join(" ", parts);
        }

        private static string NameOf(string id)
        {
            var def = EntityDatabase.Get(id);
            if (def != null && !string.IsNullOrEmpty(def.Name)) return def.Name;
            var sp = EntityDatabase.GetSpecies(id);
            return sp != null && !string.IsNullOrEmpty(sp.Name) ? sp.Name : id;
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
