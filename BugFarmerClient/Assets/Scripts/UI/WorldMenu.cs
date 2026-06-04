using System;
using UnityEngine;
using UnityEngine.Events;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// UI-agnostic world-select logic for the login screen. Build whatever UI you like (dropdown,
    /// buttons, third-party assets) and wire it to these hooks:
    ///   - your selector's onValueChanged(int)  -> SetChoice
    ///   - your Play/Connect button's onClick    -> Play
    ///   - bind onStatus(string)                 -> your status Text/TMP_Text setter
    ///
    /// No world creation happens client-side; the server ensures the world via the world_enter
    /// RPC (find-or-create singleton per zone). Use `Labels` to populate a dropdown at runtime,
    /// or just set your dropdown's options to match the `worlds` order in the Inspector.
    /// </summary>
    public class WorldMenu : MonoBehaviour
    {
        [Serializable]
        public class WorldChoice
        {
            public string label;   // shown in your UI (e.g. "Normal")
            public string zoneId;  // server zone id (e.g. "village_21")
        }

        // Subclassed so Unity can serialize/expose the UnityEvent<string> in the Inspector.
        [Serializable]
        public class StatusEvent : UnityEvent<string> { }

        [Tooltip("World options. Order must match your dropdown's option order.")]
        public WorldChoice[] worlds =
        {
            new WorldChoice { label = "Normal", zoneId = "village_21" },
            new WorldChoice { label = "Test",   zoneId = "sim_test" },
        };

        [Tooltip("Fired whenever the status changes; bind a Text/TMP_Text setter here.")]
        public StatusEvent onStatus;

        private int _choice;
        private bool _busy;

        /// <summary>Current status string (also pushed via onStatus).</summary>
        public string Status { get; private set; } = "";

        /// <summary>Option labels in order — handy for populating a dropdown at runtime.</summary>
        public string[] Labels
        {
            get
            {
                var labels = new string[worlds.Length];
                for (int i = 0; i < worlds.Length; i++) labels[i] = worlds[i].label;
                return labels;
            }
        }

        /// <summary>Hook your selector's onValueChanged(int) here.</summary>
        public void SetChoice(int index)
        {
            if (index >= 0 && index < worlds.Length) _choice = index;
        }

        /// <summary>Hook your Play button's onClick here. Connects the socket, then enters the chosen world.</summary>
        public async void Play()
        {
            if (_busy) return;
            if (worlds == null || worlds.Length == 0) { SetStatus("No worlds configured."); return; }

            _busy = true;
            var choice = worlds[Mathf.Clamp(_choice, 0, worlds.Length - 1)];
            try
            {
                SetStatus("Connecting...");
                await NetworkManager.Instance.ConnectSocketAsync();
                SetStatus($"Entering {choice.label}...");
                await WorldManager.Instance.EnterWorld(choice.zoneId);
                SetStatus($"In world: {choice.label}");
            }
            catch (Exception ex)
            {
                SetStatus($"Failed: {ex.Message}");
                Debug.LogError($"[WorldMenu] Play failed: {ex}");
            }
            finally
            {
                _busy = false;
            }
        }

        private void SetStatus(string msg)
        {
            Status = msg;
            Debug.Log($"[WorldMenu] {msg}");
            onStatus?.Invoke(msg);
        }
    }
}
