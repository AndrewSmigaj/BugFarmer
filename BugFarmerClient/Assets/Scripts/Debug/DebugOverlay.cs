using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Bugs;
using BugFarmer.Entities;

namespace BugFarmer.Tracing
{
    /// <summary>
    /// In-game debug overlay with hotkeys for trace recording.
    /// Attach to a GameObject in the scene.
    /// </summary>
    public class DebugOverlay : MonoBehaviour
    {
        private string _clientId;
        private TickTraceBuffer _traceBuffer;
        private bool _isRecording = false;

        // F4: per-swarm overlay (world-space centre markers + counts). F5: population graph.
        // F6: live ecology tuning (sends overrides to the server — the server is the decider).
        private bool _showSwarms = false;
        private bool _showGraph = false;
        private bool _showTuning = false;
        private bool _showWorld = false;   // F8: world debug (time / weather / spawn)
        private string _wStatus = "";

        // Ecology tuning state (initialized to the species.json fly defaults)
        private float _tForage = 0.25f;       // chance a behavior chunk is FORAGE
        private float _tModeSecs = 40f;       // behavior-chunk length (seconds; ±25% jitter)
        private float _tFeed = 5f;            // satiation/s at food
        private float _tBreed = 10f;          // breed meter/s at source
        private float _tDecay = 0.5f;         // satiation/s away from food
        private float _tConsume = 0.5f;       // food/bug/s
        private float _tCooldown = 30f;       // s between reproductions
        private string _tStatus = "";
        private readonly List<int> _popSamples = new();   // total bug count, sampled every 10 ticks
        private long _lastSampleTick = -1;
        private Texture2D _px;                            // 1x1 white for graph drawing
        private const int MaxSamples = 600;               // 10 minutes at 1 sample/second

        void Start()
        {
            _traceBuffer = new TickTraceBuffer();
            _clientId = Application.isEditor ? "Editor" : "Build";
            _px = new Texture2D(1, 1);
            _px.SetPixel(0, 0, Color.white);
            _px.Apply();
        }

        void Update()
        {
            if (Input.GetKeyDown(KeyCode.F1)) ToggleRecording();
            if (Input.GetKeyDown(KeyCode.F2)) DumpTrace();
            if (Input.GetKeyDown(KeyCode.F3)) LogCurrentState();
            if (Input.GetKeyDown(KeyCode.F4)) _showSwarms = !_showSwarms;
            if (Input.GetKeyDown(KeyCode.F5)) _showGraph = !_showGraph;
            if (Input.GetKeyDown(KeyCode.F6)) _showTuning = !_showTuning;
            if (Input.GetKeyDown(KeyCode.F8)) _showWorld = !_showWorld;

            // Population time-series: one sample per second (10 ticks)
            var sm = SwarmManager.Instance;
            if (sm != null && sm.SimulationTick >= _lastSampleTick + 10)
            {
                _lastSampleTick = sm.SimulationTick;
                _popSamples.Add(sm.TotalBugCount);
                if (_popSamples.Count > MaxSamples)
                    _popSamples.RemoveAt(0);
            }
        }

        void ToggleRecording()
        {
            _isRecording = !_isRecording;
            if (SwarmManager.Instance != null)
            {
                SwarmManager.Instance.SetTraceCallback(_isRecording ? RecordTick : null);
            }
            UnityEngine.Debug.Log($"[DebugOverlay] Recording: {_isRecording}");
        }

        void RecordTick(long tick, long hash, List<BugTrace> bugs, List<PlayerTarget> players)
        {
            _traceBuffer.RecordTick(tick, hash, bugs, players);
        }

        void DumpTrace()
        {
            _traceBuffer.DumpToFile(_clientId);
        }

        void LogCurrentState()
        {
            var sm = SwarmManager.Instance;
            if (sm == null)
            {
                UnityEngine.Debug.Log("[DebugOverlay] SwarmManager not available");
                return;
            }
            UnityEngine.Debug.Log($"[DebugOverlay] Tick={sm.SimulationTick}, Hash={sm.ComputeStateHash():X16}, Swarms={sm.SwarmCount}, Bugs={sm.TotalBugCount}");
        }

        void OnGUI()
        {
            var sm = SwarmManager.Instance;

            GUILayout.BeginArea(new Rect(10, 10, 320, 200));
            GUILayout.Label($"Client: {_clientId}");
            GUILayout.Label($"Recording: {_isRecording} (Buffer: {_traceBuffer?.Count ?? 0})");
            GUILayout.Label($"Tick: {sm?.SimulationTick ?? 0}");
            GUILayout.Label($"Swarms: {sm?.SwarmCount ?? 0}   Bugs: {sm?.TotalBugCount ?? 0}");
            GUILayout.Label("F1=Record F2=Dump F3=Log F4=Swarms F5=Graph F6=Tuning F8=World");
            GUILayout.EndArea();

            if (_showSwarms && sm != null)
                DrawSwarmOverlay(sm);
            if (_showGraph)
                DrawPopulationGraph();
            if (_showTuning)
                DrawEcologyTuning();
            if (_showWorld)
                DrawWorldDebug();
        }

        /// <summary>
        /// F8: world debug (OpCode 90 — server-decided, loudly logged, the F6 convention).
        /// Set the apparent time of day, force weather, spawn a fly swarm at the player.
        /// </summary>
        void DrawWorldDebug()
        {
            const int W = 340;
            GUILayout.BeginArea(new Rect(Screen.width - W - 12, 500, W, 190), GUI.skin.box);
            GUILayout.Label("=== WORLD DEBUG — F8 ===");

            // Time of day: tick positions within the 8400-tick day (0 = morning).
            // Evening (4200) lands at the top of the fruit-fall window t∈[0.40,0.62).
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Morning")) SendWorldDebug(t => t.set_time_ticks = 0);
            if (GUILayout.Button("Noon")) SendWorldDebug(t => t.set_time_ticks = 2100);
            if (GUILayout.Button("Evening")) SendWorldDebug(t => t.set_time_ticks = 4200);
            if (GUILayout.Button("Night")) SendWorldDebug(t => t.set_time_ticks = 5880);
            GUILayout.EndHorizontal();

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Rain")) SendWorldDebug(t => t.weather = "rain");
            if (GUILayout.Button("Stop weather")) SendWorldDebug(t => t.weather = "stop");
            GUILayout.EndHorizontal();

            if (GUILayout.Button("Spawn fly swarm at player"))
                SendWorldDebug(t =>
                {
                    var player = FindObjectOfType<BugFarmer.Player.PlayerController>();
                    t.spawn_species = "fly_common";
                    t.spawn_count = 8;
                    if (player != null)
                    {
                        t.spawn_x = player.transform.position.x;
                        t.spawn_y = player.transform.position.y;
                    }
                });

            GUILayout.Label($"time now: {BugFarmer.World.DayNightController.TimeOfDay:F2}  " +
                            $"weather: {BugFarmer.World.DayNightController.Weather}");
            if (!string.IsNullOrEmpty(_wStatus))
                GUILayout.Label(_wStatus);
            GUILayout.EndArea();
        }

        void SendWorldDebug(System.Action<BugFarmer.Networking.DebugWorldMessage> fill)
        {
            var world = BugFarmer.Networking.WorldManager.Instance;
            var socket = BugFarmer.Networking.NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
            {
                _wStatus = "not connected";
                return;
            }
            var msg = new BugFarmer.Networking.DebugWorldMessage();
            fill(msg);
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id,
                BugFarmer.Networking.OpCodes.DebugWorld, JsonUtility.ToJson(msg));
            _wStatus = $"sent @ {System.DateTime.Now:HH:mm:ss}";
        }

        /// <summary>
        /// F6: live ecology tuning. Sliders for the fly duty-cycle and rates; Apply sends the
        /// overrides to the SERVER (OpCode 87), which owns all these decisions — takes effect
        /// immediately, no rebuild. Values reset to species.json defaults on server restart.
        /// </summary>
        void DrawEcologyTuning()
        {
            const int W = 340;
            GUILayout.BeginArea(new Rect(Screen.width - W - 12, 160, W, 330), GUI.skin.box);
            GUILayout.Label("=== ECOLOGY TUNING (fly_common) — F6 ===");

            _tForage = Slider("Forage chance", _tForage, 0f, 1f, "P0");
            _tModeSecs = Slider("Behavior chunk (s)", _tModeSecs, 5f, 120f, "F0");
            _tFeed = Slider("Feed rate (sat/s)", _tFeed, 1f, 25f, "F1");
            _tBreed = Slider("Breed rate (/s)", _tBreed, 1f, 25f, "F1");
            _tDecay = Slider("Hunger decay (/s)", _tDecay, 0.05f, 5f, "F2");
            _tConsume = Slider("Consume (food/bug/s)", _tConsume, 0.05f, 3f, "F2");
            _tCooldown = Slider("Reproduce cooldown (s)", _tCooldown, 5f, 180f, "F0");

            GUILayout.Space(4);
            if (GUILayout.Button("APPLY TO SERVER"))
                SendTuning();
            if (!string.IsNullOrEmpty(_tStatus))
                GUILayout.Label(_tStatus);
            GUILayout.EndArea();
        }

        float Slider(string label, float value, float min, float max, string fmt)
        {
            GUILayout.BeginHorizontal();
            GUILayout.Label($"{label}: {value.ToString(fmt)}", GUILayout.Width(180));
            float v = GUILayout.HorizontalSlider(value, min, max, GUILayout.Width(140));
            GUILayout.EndHorizontal();
            return v;
        }

        void SendTuning()
        {
            var world = BugFarmer.Networking.WorldManager.Instance;
            var socket = BugFarmer.Networking.NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
            {
                _tStatus = "not connected";
                return;
            }

            int modeTicks = Mathf.RoundToInt(_tModeSecs * 10f);
            var msg = new BugFarmer.Networking.EcologyTuningMessage
            {
                species_id = "fly_common",
                forage_chance = _tForage,
                forage_mode_min_ticks = Mathf.Max(10, Mathf.RoundToInt(modeTicks * 0.75f)),
                forage_mode_max_ticks = Mathf.Max(20, Mathf.RoundToInt(modeTicks * 1.25f)),
                feed_amount = _tFeed,
                breed_amount = _tBreed,
                satiation_decay = _tDecay,
                consume_rate = _tConsume,
                reproduce_cooldown = _tCooldown,
            };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id,
                BugFarmer.Networking.OpCodes.EcologyTuning, JsonUtility.ToJson(msg));
            _tStatus = $"applied @ {System.DateTime.Now:HH:mm:ss}";
        }

        /// <summary>
        /// F4: a list panel of every swarm (id, bug count) plus a world-space marker + label at
        /// each swarm's centre — makes merges/splits/reproduction directly visible in-game.
        /// </summary>
        void DrawSwarmOverlay(SwarmManager sm)
        {
            var cam = Camera.main;
            int i = 0;
            GUILayout.BeginArea(new Rect(10, 215, 320, 400));
            GUILayout.Label("=== SWARMS ===");
            foreach (var swarm in sm.GetAllSwarms())
            {
                Vector3 c = swarm.transform.position;
                GUILayout.Label($"{swarm.SwarmId}: {swarm.Count} bugs @ ({c.x:F1},{c.y:F1})");
                i++;
                if (i >= 16) { GUILayout.Label("..."); break; }

                if (cam != null)
                {
                    var sp = cam.WorldToScreenPoint(c);
                    if (sp.z > 0)
                    {
                        float gx = sp.x, gy = Screen.height - sp.y;
                        // crosshair marker + count label at the centre
                        GUI.color = Color.yellow;
                        GUI.DrawTexture(new Rect(gx - 8, gy - 1, 16, 2), _px);
                        GUI.DrawTexture(new Rect(gx - 1, gy - 8, 2, 16), _px);
                        GUI.Label(new Rect(gx + 6, gy - 18, 120, 20), $"{swarm.Count}");
                        GUI.color = Color.white;
                    }
                }
            }
            GUILayout.EndArea();
        }

        /// <summary>
        /// F5: total-bug-population over time (1 sample/second) — the fly-boom graph.
        /// </summary>
        void DrawPopulationGraph()
        {
            const int W = 320, H = 110;
            float x0 = Screen.width - W - 12, y0 = 12;

            GUI.color = new Color(0f, 0f, 0f, 0.55f);
            GUI.DrawTexture(new Rect(x0 - 4, y0 - 4, W + 8, H + 26), _px);
            GUI.color = Color.white;

            int max = 1;
            foreach (var v in _popSamples) if (v > max) max = v;

            GUI.Label(new Rect(x0, y0 + H + 2, W, 18), $"bugs over time (max {max}, {_popSamples.Count}s)");
            GUI.color = Color.green;
            int n = _popSamples.Count;
            for (int s = 0; s < n; s++)
            {
                float px = x0 + (float)s / MaxSamples * W;
                float ph = (float)_popSamples[s] / max * (H - 4);
                GUI.DrawTexture(new Rect(px, y0 + H - ph, 2, 2), _px);
            }
            GUI.color = Color.white;
        }
    }
}
