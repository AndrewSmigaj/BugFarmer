using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// NPC VENDORS — right-click a "shop" occupant (general store / bug dealer) to open a Buy/Sell
    /// panel. Buy from the NPC's stock (server-priced); sell your items, and at the bug dealer your
    /// live bugs + dead-bug carcasses, for coins. The server is authoritative for every price + check;
    /// the panel reads live from InventoryManager, which the FullInventorySync echo refreshes after each
    /// trade (coins + slots), so no client-side optimistic bookkeeping. Mirrors StationController.
    /// </summary>
    public class ShopController : MonoBehaviour
    {
        [SerializeField] private float maxInteractDistance = 2.5f;

        private bool _open;
        private Vector2Int _cell;
        private string _title = "Shop";
        private string _kind = "items";
        private EntityDatabase.ShopOffer[] _sells;
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
            _open = true;
            return true;
        }

        private void OnGUI()
        {
            if (!_open) return;
            var inv = InventoryManager.Instance;
            const int W = 320;
            GUILayout.BeginArea(new Rect(Screen.width / 2f - W / 2f, 60, W, 470), GUI.skin.box);
            GUILayout.Label($"=== {_title} ===    Coins: {(inv != null ? inv.Coins : 0)}");
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
            if (GUILayout.Button("Close")) _open = false;
            GUILayout.EndArea();
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
