using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// STATIONS — player-fillable material processors (compost bin first; feed troughs etc.
    /// later). Right-click a station occupant to open a small menu: a fill meter + your item
    /// slots as deposit buttons. Deposits are server-validated (accepted item, capacity,
    /// range); the meter updates from StationUpdate (OpCode 86, display-only — bug AI reads
    /// the deterministic FOOD_CONSUMED ledger instead).
    /// </summary>
    public class StationController : MonoBehaviour
    {
        [SerializeField] private float maxInteractDistance = 2.5f;


        // Open panel state
        private bool _open;
        private Vector2Int _cell;
        private string _stationName = "Station";
        private string[] _accepts;      // Item types this station takes (menu filter)
        private int _capacity = 10;

        // Last-known meters per station cell (from OpCode 86)
        private readonly Dictionary<Vector2Int, (int input, int fill, int capacity)> _meters = new();

        private void Start()
        {
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState += OnMatchState;
        }

        private void OnDestroy()
        {
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState -= OnMatchState;
        }

        private void OnMatchState(Nakama.IMatchState state)
        {
            if (state.OpCode != OpCodes.StationUpdate) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<StationUpdateMessage>(json);
            if (msg == null) return;
            _meters[new Vector2Int(msg.gx, msg.gy)] = (msg.input, msg.fill, msg.capacity);
        }

        /// <summary>
        /// Handle a routed right-click (PlayerInputRouter owns right-click; this controller
        /// no longer polls Input). Returns TRUE on any menu STATE TRANSITION — opening,
        /// toggling, OR closing because the click landed elsewhere — so the click is
        /// CONSUMED and never also jabs/places ("closed a menu and accidentally placed a
        /// chest" is the bug class this prevents). Returns false only when there was
        /// nothing to interact with and nothing to close.
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            // Front-most interactable occupant (shared resolver; not a bare OverlapPoint that an
            // overlapping occupant could steal).
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null)
            {
                if (_open) { _open = false; return true; } // closing consumes the click
                return false;
            }

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "station")
            {
                if (_open) { _open = false; return true; }
                return false;
            }

            // Range check (client-side convenience; server re-validates). An out-of-range
            // station click falls through (router footnote: may jab/place) — accepted.
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > maxInteractDistance * maxInteractDistance)
                    return false;
            }

            _cell = target.AnchorCell;
            _stationName = def.Name ?? target.OccupantId;
            _accepts = def.World.StationAccepts;
            _capacity = def.World.StationCapacity;
            _open = !_open;
            return true;
        }

        private bool IsAccepted(string itemId)
        {
            if (_accepts == null) return false;
            foreach (var a in _accepts)
                if (a == itemId) return true;
            return false;
        }

        private void OnGUI()
        {
            if (!_open) return;

            const int W = 260;
            GUILayout.BeginArea(new Rect(Screen.width / 2f - W / 2f, 80, W, 360), GUI.skin.box);
            GUILayout.Label($"=== {_stationName} ===");

            int input = 0, fill = 0, cap = _capacity;
            if (_meters.TryGetValue(_cell, out var mtr)) { input = mtr.input; fill = mtr.fill; cap = mtr.capacity; }

            // INPUT hopper meter (raw deposits being composted)
            GUILayout.Label($"Input: {input}/{cap}");
            DrawMeter(W, input, cap, new Color(0.8f, 0.65f, 0.3f));

            // OUTPUT meter (compost — what the flies feed/breed on)
            GUILayout.Label($"Compost: {fill}/{cap}");
            DrawMeter(W, fill, cap, new Color(0.45f, 0.8f, 0.3f));

            GUILayout.Space(6);
            GUILayout.Label("Deposit (compostables):");

            // Icon grid of ACCEPTED inventory items only — click an icon to deposit one.
            var inv = InventoryManager.Instance;
            bool any = false;
            if (inv?.ItemSlots != null)
            {
                GUILayout.BeginHorizontal();
                int col = 0;
                foreach (var slot in inv.ItemSlots)
                {
                    if (slot == null || slot.IsEmpty || !IsAccepted(slot.item_id)) continue;
                    any = true;

                    var icon = EntityDatabase.GetItemSprite(slot.item_id);
                    var content = icon != null
                        ? new GUIContent(icon.texture, $"{slot.item_id} x{slot.count}")
                        : new GUIContent($"{slot.item_id}\nx{slot.count}");
                    if (GUILayout.Button(content, GUILayout.Width(52), GUILayout.Height(52)))
                        SendDeposit(slot.item_id);
                    GUILayout.Label($"x{slot.count}", GUILayout.Width(28));

                    if (++col % 3 == 0) { GUILayout.EndHorizontal(); GUILayout.BeginHorizontal(); }
                }
                GUILayout.EndHorizontal();
            }
            if (!any) GUILayout.Label("(nothing compostable — fruit goes in here)");

            GUILayout.Space(6);
            if (GUILayout.Button("Close")) _open = false;
            GUILayout.EndArea();
        }

        private void DrawMeter(int panelW, int value, int max, Color color)
        {
            var r = GUILayoutUtility.GetRect(panelW - 16, 12);
            GUI.Box(r, GUIContent.none);
            if (max > 0 && value > 0)
            {
                var fr = new Rect(r.x + 1, r.y + 1, (r.width - 2) * Mathf.Clamp01((float)value / max), r.height - 2);
                GUI.color = color;
                GUI.DrawTexture(fr, Texture2D.whiteTexture);
                GUI.color = Color.white;
            }
        }

        private void SendDeposit(string itemId)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;

            var msg = new StationDepositMessage { gx = _cell.x, gy = _cell.y, item_id = itemId };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.StationDeposit, JsonUtility.ToJson(msg));
        }
    }
}
