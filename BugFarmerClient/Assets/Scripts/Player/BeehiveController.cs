using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;

namespace BugFarmer.Player
{
    /// <summary>
    /// BEEHIVES — right-click a hive (occupant interaction_type "beehive": the wild tree hive or
    /// any placed beehive_* box) to hand-harvest its whole honeycombs (OpCode 107, the tree-pick
    /// pattern — no panel). The SERVER decides everything: range, comb count, and whether the
    /// colony boils out at you (it does, unless the hive was freshly smoked — the bee suit stops
    /// the stings, not the anger). The ack (OpCode 108) is surfaced as a toast; the combs arrive
    /// via the ordinary inventory sync.
    ///
    /// Routed by PlayerInputRouter's right-click chain (with the other interactables, before
    /// placement). Returns TRUE only when the click landed on a beehive occupant.
    /// </summary>
    public class BeehiveController : MonoBehaviour
    {
        private string _toast = "";
        private float _toastUntil;

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
            if (state.OpCode != OpCodes.HiveHarvestAck) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<HiveHarvestAckMessage>(json);
            if (msg == null) return;
            ShowToast(string.IsNullOrEmpty(msg.message)
                ? (msg.ok ? $"+{msg.count} honeycomb" : "Nothing to harvest.")
                : msg.message);
        }

        /// <summary>
        /// Right-click handler (PlayerInputRouter owns the button). Sends the harvest for the hive
        /// under the cursor and returns true (consumed). False when there's no beehive there, so
        /// the click falls through to placement/attack. Range is RE-checked server-side.
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null) return false;

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "beehive")
                return false;

            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
                return true; // it WAS a hive click — consume it even if we can't send right now

            var msg = new HiveHarvestMessage { gx = target.AnchorCell.x, gy = target.AnchorCell.y };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.HiveHarvest, JsonUtility.ToJson(msg));
            return true;
        }

        private void ShowToast(string text)
        {
            _toast = text;
            _toastUntil = Time.time + 2.5f;
        }

        private void OnGUI()
        {
            if (Time.time > _toastUntil || string.IsNullOrEmpty(_toast)) return;
            var style = new GUIStyle(GUI.skin.box) { fontSize = 16, alignment = TextAnchor.MiddleCenter };
            const float w = 360f, h = 34f;
            GUI.Box(new Rect(Screen.width / 2f - w / 2f, 110f, w, h), _toast, style);
        }
    }
}
