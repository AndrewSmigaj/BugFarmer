using System;
using System.Collections.Generic;
using TMPro;
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
            new WorldChoice { label = "Normal",         zoneId = "village_21" },
            new WorldChoice { label = "Village B",      zoneId = "village_21_B" },
            new WorldChoice { label = "Test",           zoneId = "sim_test" },
            new WorldChoice { label = "Collision Test", zoneId = "collision_test" },
            new WorldChoice { label = "Split Test",     zoneId = "split_test2" },
            new WorldChoice { label = "Merge Test",     zoneId = "merge_test2" },
            new WorldChoice { label = "Fly Farm Test",  zoneId = "repro_test" },
        };

        [Tooltip("Fired whenever the status changes; bind a Text/TMP_Text setter here.")]
        public StatusEvent onStatus;

        [Tooltip("Optional: assign your world Dropdown. If set, it is auto-populated from `worlds` at runtime " +
                 "and its onValueChanged is wired to SetChoice, so the picker always matches this list — no " +
                 "need to hand-edit the dropdown's options when zones are added/removed in code.")]
        public TMP_Dropdown worldDropdown;

        private int _choice;
        private bool _busy;

        private void Awake()
        {
            // A serialized `worlds` array baked into an existing scene/prefab overrides the code default, so
            // it can lag behind. Make sure the built-in zones are always present even if the Inspector value
            // is stale (this is why a newly-added zone may not "show up" after only editing the code default).
            EnsureWorld("Normal", "village_21");
            EnsureWorld("Test", "sim_test");
            EnsureWorld("Collision Test", "collision_test");
            EnsureWorld("Split Test", "split_test2");
            EnsureWorld("Merge Test", "merge_test2");
            EnsureWorld("Fly Farm Test", "repro_test");
        }

        private void Start()
        {
            if (worldDropdown == null) return;
            worldDropdown.ClearOptions();
            worldDropdown.AddOptions(new List<string>(Labels));
            worldDropdown.onValueChanged.RemoveListener(SetChoice);
            worldDropdown.onValueChanged.AddListener(SetChoice);
            SetChoice(worldDropdown.value);
        }

        private void EnsureWorld(string label, string zoneId)
        {
            if (worlds != null)
                foreach (var w in worlds)
                    if (w != null && w.zoneId == zoneId) return;
            var list = new List<WorldChoice>(worlds ?? Array.Empty<WorldChoice>());
            list.Add(new WorldChoice { label = label, zoneId = zoneId });
            worlds = list.ToArray();
        }

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
