using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;
using BugFarmer.Bugs;
using BugFarmer.Entities;
using BugFarmer.Player;
using BugFarmer.Util;

namespace BugFarmer.Testing
{
    // The headless test runner's measuring and checking rig (docs/plans/village-slice.md, Stage 1.0b). Everything here
    // is switched on only by HeadlessSyncTest's command-line flags; the game never creates any of it.

    /// <summary>
    /// What the bugs are doing, per species, from their own state after each tick: bug-ticks in total and while
    /// hunting, landed at food, eating a corpse, fleeing a player, attacking, curious, winding up a lunge and lunging;
    /// plus the reports made (predation strikes, prey claimed, corpses eaten); plus how many times a bug STARTED each of
    /// those states (the <c>*_starts</c> columns), because a few bugs holding a state for a long time make many
    /// bug-ticks but few separate occurrences. Read-only over the bugs. Compared before and after a change by
    /// tools/ecology/behaviour_check.py.
    /// </summary>
    public static class BehaviourTally
    {
        public static readonly string[] Columns =
            { "bug_ticks", "hunting", "landed", "eating", "flee", "attack", "curious", "windup", "lunge" };
        public const string Header =
            "real_s,tick,species,bug_ticks,hunting,landed,eating,flee,attack,curious,windup,lunge,strikes,prey_claimed,corpses,"
            + "hunting_starts,landed_starts,eating_starts,flee_starts,attack_starts,curious_starts,windup_starts,lunge_starts";
        const int States = 8; // Columns[1..8]; their starts are counted after them, at Columns.Length + state

        static readonly Dictionary<string, long[]> _bySpecies = new Dictionary<string, long[]>();
        static readonly List<BugAgent> _agents = new List<BugAgent>();
        // Each bug's states on the previous tick (bit i = Columns[1 + i]); swapped every tick, so bugs gone are dropped.
        // A bug first seen in a state counts as starting it.
        static Dictionary<BugAgent, int> _prev = new Dictionary<BugAgent, int>();
        static Dictionary<BugAgent, int> _cur = new Dictionary<BugAgent, int>();

        public static void Start()
        {
            ReportLog.Active = true;
            SwarmManager.TestTickObserver = Observe;
        }

        static void Observe(long tick)
        {
            var sm = SwarmManager.Instance;
            if (sm == null) return;
            foreach (var swarm in sm.GetAllSwarms())
            {
                string sp = swarm.SpeciesId ?? "?";
                if (!_bySpecies.TryGetValue(sp, out var c)) _bySpecies[sp] = c = new long[Columns.Length + States];
                _agents.Clear();
                swarm.AppendAgents(_agents);
                foreach (var a in _agents)
                {
                    int s = 0;
                    if (a.HuntTargetBugId >= 0) s |= 1;
                    if (a.LandTicks > 0) s |= 2;
                    if (a.FeedUntilTick > tick) s |= 4;
                    switch (a.CurrentBehavior)
                    {
                        case "flee": s |= 8; break;
                        case "attack": s |= 16; break;
                        case "curious": s |= 32; break;
                    }
                    if (a.SurgePhase == 1) s |= 64;
                    else if (a.SurgePhase == 2) s |= 128;

                    c[0]++;
                    _prev.TryGetValue(a, out int was);
                    int started = s & ~was;
                    for (int i = 0; i < States; i++)
                    {
                        if ((s & (1 << i)) != 0) c[1 + i]++;
                        if ((started & (1 << i)) != 0) c[Columns.Length + i]++;
                    }
                    _cur[a] = s;
                }
            }
            var t = _prev; _prev = _cur; _cur = t;
            _cur.Clear();
        }

        /// <summary>Appends this window's rows (one per species, ordinal order) and clears the window.</summary>
        public static void FlushWindow(StringBuilder into, double realS, long tick)
        {
            var reports = ReportLog.TakeCounts();
            var species = new List<string>(_bySpecies.Keys);
            foreach (var sp in reports.Keys) if (!_bySpecies.ContainsKey(sp)) species.Add(sp);
            species.Sort(string.CompareOrdinal);
            foreach (var sp in species)
            {
                into.Append(realS.ToString("F1", CultureInfo.InvariantCulture)).Append(',')
                    .Append(tick.ToString(CultureInfo.InvariantCulture)).Append(',').Append(sp);
                _bySpecies.TryGetValue(sp, out var c);
                for (int i = 0; i < Columns.Length; i++)
                    into.Append(',').Append((c != null ? c[i] : 0).ToString(CultureInfo.InvariantCulture));
                reports.TryGetValue(sp, out var r);
                for (int i = 0; i < 3; i++)
                    into.Append(',').Append((r != null ? r[i] : 0).ToString(CultureInfo.InvariantCulture));
                for (int i = 0; i < States; i++)
                    into.Append(',').Append((c != null ? c[Columns.Length + i] : 0).ToString(CultureInfo.InvariantCulture));
                into.Append('\n');
            }
            _bySpecies.Clear();
        }
    }

    /// <summary>Records each frame for the cost probe, after every other script (so the frame's drawing is in).</summary>
    [DefaultExecutionOrder(32000)]
    public class CostProbeFrame : MonoBehaviour
    {
        private void LateUpdate()
        {
            if (CostProbe.Enabled) CostProbe.FrameEnd(Time.unscaledDeltaTime);
        }
    }

    /// <summary>
    /// Walks the local player along a route (cell waypoints, one "x,y" per line, '#' comments), through the game's own
    /// movement: <see cref="PlayerController.ScriptedMove"/> stands in for the keyboard. A waypoint it can't reach in 10
    /// game-seconds is skipped; after a faint (the player jumps back to spawn) it heads for the nearest unvisited one.
    /// Loops the route until the run ends. Headless it is the wanderer; windowed, the camera follows, so it's the tour.
    /// </summary>
    public class RouteFollower : MonoBehaviour
    {
        private readonly List<Vector2> _points = new List<Vector2>();
        private readonly HashSet<int> _visitedThisLap = new HashSet<int>();
        private int _next;
        private PlayerController _player;
        private Vector2 _lastPos;
        private float _bestDist = float.MaxValue, _progressAt;
        public int Reached { get; private set; }
        public int Skipped { get; private set; }
        public int Laps { get; private set; }

        public bool Load(string path)
        {
            if (!File.Exists(path)) return false;
            foreach (var raw in File.ReadAllLines(path))
            {
                var line = raw.Trim();
                if (line.Length == 0 || line[0] == '#') continue;
                var p = line.Split(',');
                if (p.Length >= 2 && float.TryParse(p[0], NumberStyles.Float, CultureInfo.InvariantCulture, out float x)
                    && float.TryParse(p[1], NumberStyles.Float, CultureInfo.InvariantCulture, out float y))
                    _points.Add(new Vector2(x + 0.5f, y + 0.5f));
            }
            return _points.Count > 0;
        }

        private void Update()
        {
            if (_points.Count == 0) return;
            if (_player == null)
            {
                _player = FindFirstObjectByType<PlayerController>();
                if (_player == null) return;
                _lastPos = _player.transform.position;
                _progressAt = Time.time;
            }
            Vector2 pos = _player.transform.position;

            // A faint sends the player back to spawn: head for the nearest waypoint not yet reached this lap.
            if ((pos - _lastPos).sqrMagnitude > 64f)
            {
                _next = Nearest(pos);
                ResetProgress();
            }
            _lastPos = pos;

            Vector2 target = _points[_next];
            Vector2 to = target - pos;
            float dist = to.magnitude;
            if (dist < 0.75f)
            {
                Reached++;
                Advance(skipped: false);
                return;
            }
            if (dist < _bestDist - 0.5f) { _bestDist = dist; _progressAt = Time.time; }
            else if (Time.time - _progressAt > 10f) { Skipped++; Advance(skipped: true); return; }
            PlayerController.ScriptedMove = to / dist;
        }

        private void Advance(bool skipped)
        {
            _visitedThisLap.Add(_next);
            _next++;
            if (_next >= _points.Count) { _next = 0; Laps++; _visitedThisLap.Clear(); }
            ResetProgress();
        }

        private void ResetProgress()
        {
            _bestDist = float.MaxValue;
            _progressAt = Time.time;
        }

        private int Nearest(Vector2 pos)
        {
            int best = _next; float bestD = float.MaxValue;
            for (int i = 0; i < _points.Count; i++)
            {
                if (_visitedThisLap.Contains(i)) continue;
                float d = (_points[i] - pos).sqrMagnitude;
                if (d < bestD) { bestD = d; best = i; }
            }
            return best;
        }

        private void OnDestroy() => PlayerController.ScriptedMove = null;
    }

    /// <summary>
    /// Writes the probes' per-window files every 5 real seconds whatever the test mode, and the summaries at the end.
    /// Files go to persistentDataPath with the client id in the name, so several test players don't collide.
    /// </summary>
    public class ProbeWriter : MonoBehaviour
    {
        public static ProbeWriter Instance { get; private set; }
        private string _dir, _id, _perfMode;
        private StringBuilder _cost, _behaviour;
        private float _t0, _windowStart;
        private RouteFollower _route;

        public void Begin(string dir, string clientId, string perfMode, bool cost, bool behaviour, RouteFollower route)
        {
            Instance = this;
            _dir = dir; _id = clientId; _perfMode = perfMode ?? "";
            _route = route;
            if (cost) _cost = new StringBuilder(CostProbe.WindowHeader + "\n");
            if (behaviour) _behaviour = new StringBuilder(BehaviourTally.Header + "\n");
            _t0 = _windowStart = Time.realtimeSinceStartup;
        }

        private void Update()
        {
            if (Time.realtimeSinceStartup - _windowStart < 5f) return;
            _windowStart = Time.realtimeSinceStartup;
            WindowNow();
        }

        private void WindowNow()
        {
            var sm = SwarmManager.Instance;
            double real = Time.realtimeSinceStartup - _t0;
            long tick = sm != null ? sm.SimulationTick : 0;
            if (_cost != null && CostProbe.Enabled)
                _cost.Append(CostProbe.WindowRow(real, tick, sm != null ? sm.SwarmCount : 0, sm != null ? sm.TotalBugCount : 0)).Append('\n');
            if (_behaviour != null) BehaviourTally.FlushWindow(_behaviour, real, tick);
        }

        // A clean exit of any kind (the runner's own Quit, a window closed, a polite stop) writes the files.
        private void OnApplicationQuit() => Finish();

        /// <summary>Flushes the last window, writes every file and closes the logs. Safe to call twice.</summary>
        public void Finish()
        {
            if (_dir == null) return;
            WindowNow();
            if (_cost != null)
            {
                File.WriteAllText(Path.Combine(_dir, $"client_cost_{_id}.csv"), _cost.ToString());
                File.WriteAllText(Path.Combine(_dir, $"client_cost_summary_{_id}.json"), CostProbe.SummaryJson(_perfMode));
            }
            if (_behaviour != null)
                File.WriteAllText(Path.Combine(_dir, $"client_behaviour_{_id}.csv"), _behaviour.ToString());
            if (_route != null)
                Debug.Log($"[HeadlessSyncTest] route: reached={_route.Reached} skipped={_route.Skipped} laps={_route.Laps}");
            HashLog.Close();
            ReportLog.Close();
            CostProbe.Stop();
            _dir = null;
        }
    }
}
