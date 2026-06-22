using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;

namespace BugFarmer.Player
{
    /// <summary>
    /// BEDS — right-click a bed (occupant interaction_type "sleep") to set this character's HOME:
    /// the point you wake at on death, and (server-side) where you log in. Minecraft-style. The
    /// server validates (a real bed, in range) + persists the home in the character save and replies
    /// with a SetHomeAck (OpCode 101) that we surface as a brief on-screen confirmation.
    ///
    /// Routed by PlayerInputRouter's right-click chain (after stations, before placement — interact
    /// beats place). Returns TRUE only when the click landed on a bed, so non-bed clicks fall through.
    /// </summary>
    public class SleepController : MonoBehaviour
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
            if (state.OpCode != OpCodes.SetHomeAck) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<SetHomeAckMessage>(json);
            if (msg == null) return;
            ShowToast(string.IsNullOrEmpty(msg.message) ? (msg.ok ? "Home set." : "Couldn't set home.") : msg.message);
        }

        /// <summary>
        /// Right-click handler (PlayerInputRouter owns the button). Sends a set-home for the bed under
        /// the cursor and returns true (consumed). Returns false when there's no bed there, so the
        /// click falls through to placement/attack. Range + bed validity are RE-checked server-side.
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            var hit = Physics2D.OverlapPoint(mouseWorld);
            var target = hit != null ? hit.GetComponent<OccupantClickTarget>() : null;
            if (target == null) return false;

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "sleep")
                return false;

            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
                return true; // it WAS a bed click — consume it even if we can't send right now

            var msg = new SetHomeMessage { gx = target.AnchorCell.x, gy = target.AnchorCell.y };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.SetHome, JsonUtility.ToJson(msg));
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
            const float w = 320f, h = 34f;
            GUI.Box(new Rect(Screen.width / 2f - w / 2f, 110f, w, h), _toast, style);
        }
    }
}
