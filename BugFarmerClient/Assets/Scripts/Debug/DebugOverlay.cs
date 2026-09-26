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
        private bool _showStats = false;   // F9: the corner stats readout (tick/swarms/bugs) — OFF by default
        private bool _showSwarms = false;
        private bool _showGraph = false;
        private bool _showTuning = false;
        private bool _showWorld = false;   // F8: world debug (time / weather / spawn)
        private bool _showPerf = false;    // F7: client cost profiler (FPS + per-subsystem ms + GC heap)
        private string _wStatus = "";
        // Debug enemy spawner (arena testing): a species picker + count.
        private System.Collections.Generic.List<string> _spawnIds;
        private int _spawnIdx;
        private int _spawnCount = 4;

        // Perf panel state: a smoothed frame-time so the FPS readout doesn't flicker.
        private float _frameMsEMA = 0f;

        // Ecology tuning state (initialized to the species.json fly defaults)
        private float _tForage = 0.25f;       // chance a behavior chunk is FORAGE
        private float _tModeSecs = 40f;       // behavior-chunk length (seconds; ±25% jitter)
        private float _tFeed = 5f;            // satiation/s at food
        private float _tBreed = 10f;          // breed meter/s at source
        private float _tDecay = 0.5f;         // satiation/s away from food
        private float _tConsume = 0.5f;       // food/bug/s
        private float _tCooldown = 30f;       // s between reproductions
        private string _tStatus = "";
        private readonly Dictionary<string, List<int>> _popBySpecies = new();  // species -> samples, every 10 ticks
        private int _popLen = 0;                           // aligned sample length across species
        private long _lastSampleTick = -1;
        // stable per-species line colors
        private static readonly Color[] _palette = {
            Color.green, Color.cyan, Color.yellow, Color.magenta,
            new Color(1f, 0.55f, 0f), Color.red, new Color(0.6f, 0.8f, 1f),
        };
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
            if (Input.GetKeyDown(KeyCode.F7))
            {
                _showPerf = !_showPerf;
                BugFarmer.Util.PerfProfiler.Enabled = _showPerf; // only pay the Stopwatch cost while shown
            }
            if (Input.GetKeyDown(KeyCode.F8)) _showWorld = !_showWorld;
            if (Input.GetKeyDown(KeyCode.F9)) _showStats = !_showStats;

            // Smoothed frame time for the F7 panel (unscaled so a paused timeScale doesn't skew it).
            float frameMs = Time.unscaledDeltaTime * 1000f;
            _frameMsEMA = _frameMsEMA <= 0f ? frameMs : _frameMsEMA * 0.9f + frameMs * 0.1f;

            // Population time-series: one sample per second (10 ticks), per species
            var sm = SwarmManager.Instance;
            if (sm != null && sm.SimulationTick >= _lastSampleTick + 10)
            {
                _lastSampleTick = sm.SimulationTick;
                var counts = sm.BugCountBySpecies();
                foreach (var sp in counts.Keys)              // backfill new species with zeros so series align
                    if (!_popBySpecies.ContainsKey(sp))
                        _popBySpecies[sp] = new List<int>(new int[_popLen]);
                foreach (var kv in _popBySpecies)
                    kv.Value.Add(counts.TryGetValue(kv.Key, out int c) ? c : 0);
                _popLen++;
                if (_popLen > MaxSamples)
                {
                    foreach (var kv in _popBySpecies) kv.Value.RemoveAt(0);
                    _popLen--;
                }
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

            // Corner stats readout — hidden by default; F9 toggles it (no debug text on screen normally).
            if (_showStats)
            {
                GUILayout.BeginArea(new Rect(10, 10, 320, 200));
                GUILayout.Label($"Client: {_clientId}");
                GUILayout.Label($"Recording: {_isRecording} (Buffer: {_traceBuffer?.Count ?? 0})");
                GUILayout.Label($"Tick: {sm?.SimulationTick ?? 0}");
                GUILayout.Label($"Swarms: {sm?.SwarmCount ?? 0}   Bugs: {sm?.TotalBugCount ?? 0}");
                GUILayout.Label("F1=Rec F2=Dump F3=Log F4=Swarms F5=Graph F6=Tuning F7=Perf F8=World F9=Stats");
                GUILayout.EndArea();
            }

            if (_showSwarms && sm != null)
                DrawSwarmOverlay(sm);
            if (_showGraph)
                DrawPopulationGraph();
            if (_showTuning)
                DrawEcologyTuning();
            if (_showWorld)
                DrawWorldDebug();
            if (_showPerf)
                DrawPerf(sm);
        }

        /// <summary>
        /// F7: client cost profiler. FPS + smoothed frame-time, managed-heap size, and the per-subsystem
        /// ms/frame breakdown from <see cref="BugFarmer.Util.PerfProfiler"/> (Net.* / Sim.* / Render.*),
        /// plus live bugs-by-species. For DEEP analysis (per-method CPU + GC alloc) record the Unity
        /// Profiler window in the editor — the same markers feed it. Toggling F7 flips PerfProfiler.Enabled.
        /// </summary>
        void DrawPerf(SwarmManager sm)
        {
            const int W = 330;
            GUILayout.BeginArea(new Rect(Screen.width - W - 12, 12, W, 460), GUI.skin.box);
            GUILayout.Label("=== CLIENT PERF — F7 ===");
            float fps = _frameMsEMA > 0f ? 1000f / _frameMsEMA : 0f;
            GUILayout.Label($"FPS: {fps:F0}    frame: {_frameMsEMA:F2} ms");
            float heapMB = System.GC.GetTotalMemory(false) / (1024f * 1024f);
            GUILayout.Label($"heap: {heapMB:F1} MB    swarms: {sm?.SwarmCount ?? 0}   bugs: {sm?.TotalBugCount ?? 0}");

            GUILayout.Space(4);
            GUILayout.Label("— bug subsystems (ms this frame ×calls) —");
            var disp = BugFarmer.Util.PerfProfiler.Display;
            if (disp.Count == 0)
            {
                GUILayout.Label("  (no samples yet — needs bug activity)");
            }
            else
            {
                double total = 0;
                var keys = new List<string>(disp.Keys);
                keys.Sort();
                foreach (var k in keys)
                {
                    var s = disp[k];
                    total += s.ms;
                    GUILayout.Label($"  {k,-18} {s.ms,6:F2} ms  x{s.calls}");
                }
                GUILayout.Label($"  {"TOTAL",-18} {total,6:F2} ms");
            }

            GUILayout.Space(4);
            GUILayout.Label("— bugs by species —");
            if (sm != null)
                foreach (var kv in sm.BugCountBySpecies())
                    GUILayout.Label($"  {ShortSpecies(kv.Key)}: {kv.Value}");
            GUILayout.EndArea();
        }

        /// <summary>
        /// F8: world debug (OpCode 90 — server-decided, loudly logged, the F6 convention).
        /// Set the apparent time of day, force weather, spawn a fly swarm at the player.
        /// </summary>
        void DrawWorldDebug()
        {
            const int W = 340;
            const int H = 290;
            // Vertically centred on the right edge so the whole panel is visible at any
            // view height (it used to be anchored low and ran off the bottom of the screen).
            float y = Mathf.Max(12f, (Screen.height - H) * 0.5f);
            GUILayout.BeginArea(new Rect(Screen.width - W - 12, y, W, H), GUI.skin.box);
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

            // Night darkness: live, client-only tune of the global night-floor intensity
            // (lower = darker). Set "Night" above to see the effect. Debug-only.
            float ni = BugFarmer.World.DayNightController.DebugNightIntensityOverride ?? 0.20f;
            BugFarmer.World.DayNightController.DebugNightIntensityOverride =
                Slider("Night darkness", ni, 0.02f, 0.6f, "F2");

            // Rain intensity preset (client-side for now) + a manual lightning strike.
            var ri = BugFarmer.World.RainController.Intensity;
            GUILayout.BeginHorizontal();
            GUILayout.Label("Rain:", GUILayout.Width(40));
            if (GUILayout.Button(ri == BugFarmer.World.RainController.RainIntensity.Light ? "[Light]" : "Light"))
                BugFarmer.World.RainController.Intensity = BugFarmer.World.RainController.RainIntensity.Light;
            if (GUILayout.Button(ri == BugFarmer.World.RainController.RainIntensity.Heavy ? "[Heavy]" : "Heavy"))
                BugFarmer.World.RainController.Intensity = BugFarmer.World.RainController.RainIntensity.Heavy;
            if (GUILayout.Button("Strike"))
                BugFarmer.World.RainController.RequestStrike();
            GUILayout.EndHorizontal();

            // Enemy spawner (arena testing): pick ANY species + count, spawn at the player.
            if (_spawnIds == null || _spawnIds.Count == 0)
                _spawnIds = BugFarmer.Data.EntityDatabase.AllSpeciesIds();
            if (_spawnIds != null && _spawnIds.Count > 0)
            {
                if (_spawnIdx >= _spawnIds.Count) _spawnIdx = 0;
                GUILayout.BeginHorizontal();
                if (GUILayout.Button("<", GUILayout.Width(24))) _spawnIdx = (_spawnIdx - 1 + _spawnIds.Count) % _spawnIds.Count;
                GUILayout.Label(_spawnIds[_spawnIdx], GUILayout.Width(140));
                if (GUILayout.Button(">", GUILayout.Width(24))) _spawnIdx = (_spawnIdx + 1) % _spawnIds.Count;
                if (GUILayout.Button("-", GUILayout.Width(24))) _spawnCount = System.Math.Max(1, _spawnCount - 1);
                GUILayout.Label($"x{_spawnCount}", GUILayout.Width(34));
                if (GUILayout.Button("+", GUILayout.Width(24))) _spawnCount = System.Math.Min(40, _spawnCount + 1);
                GUILayout.EndHorizontal();
                if (GUILayout.Button($"Spawn {_spawnIds[_spawnIdx]} x{_spawnCount} at player"))
                {
                    string sp = _spawnIds[_spawnIdx];
                    int n = _spawnCount;
                    SendWorldDebug(t =>
                    {
                        var player = FindObjectOfType<BugFarmer.Player.PlayerController>();
                        t.spawn_species = sp;
                        t.spawn_count = n;
                        if (player != null)
                        {
                            t.spawn_x = player.transform.position.x;
                            t.spawn_y = player.transform.position.y;
                        }
                    });
                }
            }

            // Crafting: stock the player with the Stage-1 recipe materials (+ a couple of items
            // for the filtered-container tests). Use in the "Crafting Test" zone.
            if (GUILayout.Button("Give crafting kit"))
                SendWorldDebug(t => t.give_item = "kit");

            // Bug Lab loadout: 100 fruit + 10 of each catchable species to release into the pens.
            if (GUILayout.Button("Stock Bug Lab"))
                SendWorldDebug(t => t.give_item = "buglab");

            // Ecology-watch kit: spawns a fruit tree + compost bin next to you and gives fruit + a watering
            // can, so a whole food web (fruit→rot→flies→predators) stands up in one click (pairs with a peaceful zone).
            if (GUILayout.Button("Ecology kit"))
                SendWorldDebug(t => t.give_item = "eco");

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
        /// F5: per-species bug population over time (1 sample/second) — one colored line per species
        /// + a legend with live counts. The ecology tuning instrument.
        /// </summary>
        void DrawPopulationGraph()
        {
            const int W = 320, H = 110;
            float x0 = Screen.width - W - 12, y0 = 12;
            int legendRows = Mathf.Max(1, _popBySpecies.Count);

            GUI.color = new Color(0f, 0f, 0f, 0.6f);
            GUI.DrawTexture(new Rect(x0 - 4, y0 - 4, W + 8, H + 26 + legendRows * 16), _px);
            GUI.color = Color.white;

            int max = 1;
            foreach (var kv in _popBySpecies)
                foreach (var v in kv.Value) if (v > max) max = v;

            GUI.Label(new Rect(x0, y0 + H + 2, W, 18), $"bugs/species over time (max {max}, {_popLen}s)");

            foreach (var kv in _popBySpecies)            // one line per species
            {
                GUI.color = SpeciesColor(kv.Key);
                var s = kv.Value;
                for (int i = 0; i < s.Count; i++)
                {
                    float px = x0 + (float)i / MaxSamples * W;
                    float ph = (float)s[i] / max * (H - 4);
                    GUI.DrawTexture(new Rect(px, y0 + H - ph, 2, 2), _px);
                }
            }

            int li = 0;                                   // legend
            foreach (var kv in _popBySpecies)
            {
                GUI.color = SpeciesColor(kv.Key);
                int cur = kv.Value.Count > 0 ? kv.Value[kv.Value.Count - 1] : 0;
                GUI.Label(new Rect(x0, y0 + H + 20 + li * 16, W, 16), $"■ {ShortSpecies(kv.Key)}: {cur}");
                li++;
            }
            GUI.color = Color.white;
        }

        private static Color SpeciesColor(string sp)
        {
            int h = 0;
            foreach (char c in sp) h = h * 31 + c;
            return _palette[Mathf.Abs(h) % _palette.Length];
        }

        private static string ShortSpecies(string sp)
        {
            int i = sp.IndexOf('_');
            return i > 0 ? sp.Substring(0, i) : sp;
        }
    }
}
