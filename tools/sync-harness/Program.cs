using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Nakama;

// Headless Bug Farmer sync harness.
//
// A PROTOCOL OBSERVER (not a reimplementation of the client sync state machine): it joins a world
// via the real Nakama .NET SDK and records the tick frontier + the seq of every influence event.
// Running headless (no Unity main-thread pump) localizes sync bugs to client vs server.
//
// --reconnect drives the reconnect/re-enter case: enter -> observe -> leave -> wait -> re-enter,
// logging the seqs the server delivers AFTER re-entry. Decisive for the seq-desync bug: if the
// re-entered session receives stale high seqs while the watermark is low, the SERVER is leaking
// pre-reset events; if it only sees fresh low seqs, the desync is client-side.
//
// Usage: dotnet run -- [--host 127.0.0.1] [--port 7350] [--key defaultkey]
//                      [--zone village_21] [--duration 15] [--tag p1] [--reconnect]
namespace BugFarmer.SyncHarness
{
    internal static class Program
    {
        // Opcodes (verified against nakama/modules/world/messages.go)
        private const long OpMovement = 1;
        private const long OpChunkSubscribe = 3;
        private const long OpSwarmUpdate = 20;
        private const long OpInfluenceBroadcast = 71;
        private const long OpLateJoinSnapshot = 72;
        private const long OpZoneHandoff = 73;
        private const long OpZoneAuthority = 76;
        private const long OpZoneTickBroadcast = 78;

        // Shared observer state (closed over by the message handler).
        private static readonly Stopwatch Sw = Stopwatch.StartNew();
        private static long _recvCount, _authTick = -1, _lastSeq = -1, _maxAuthTick = -1;
        private static long _maxInflSeq = -1, _minInflSeqPhase = long.MaxValue, _maxInflSeqPhase = -1;
        private static string _myUserId, _phase = "P1";
        public static string MyUserId => _myUserId; // WorldModel matches the local player entity
        private static bool _isAuthority, _loggedFirstInflThisPhase, _loggedStaleHigh;

        // Phase-1 collision-test observation
        private static int _chunks = 8;                                         // --chunks: subscribe to NxN chunks
        private static (double x0, double y0, double x1, double y1)? _walk;      // --walk path to drive the player
        private static long _playerCellX = long.MinValue, _playerCellY = long.MinValue;
        private static long _playerMaxCellY = long.MinValue, _playerMinCellY = long.MaxValue;
        private static double _confirmedY = double.NaN;                         // server-confirmed centre Y (from cell events)
        private static readonly Dictionary<string, (double x, double y, int count)> _swarmSpawn = new();    // id -> spawn centre+count (OpCode 20)
        private static readonly Dictionary<string, (double minx, double miny, double maxx, double maxy)> _swarmTgt = new(); // id -> SWARM_SET_TARGET bounds
        private static readonly List<string> _populationEvents = new();         // SWARM_SPLIT / SWARM_MERGE observed
        private static readonly List<(long tick, int total)> _popSeries = new(); // population time-series (1 sample/sec)
        private static long _lastPopSampleTick = -1;

        private static async Task<int> Main(string[] args)
        {
            var o = Args.Parse(args);
            _chunks = o.Chunks;
            if (!string.IsNullOrEmpty(o.Walk))
            {
                var p = o.Walk.Split(',');
                if (p.Length == 4)
                    _walk = (double.Parse(p[0]), double.Parse(p[1]), double.Parse(p[2]), double.Parse(p[3]));
            }
            Log($"connect {o.Host}:{o.Port} zone={o.Zone} duration={o.Duration}s reconnect={o.Reconnect} walk={o.Walk}");

            var client = new Client("http", o.Host, o.Port, o.Key) { Timeout = 10 };
            var deviceId = $"sim-{o.Tag}-{Guid.NewGuid():N}".Substring(0, 24);
            var session = await client.AuthenticateDeviceAsync(deviceId);
            _myUserId = session.UserId;
            Log($"authenticated user={session.UserId}");

            var socket = Socket.From(client);
            socket.Closed += () => Log("!! socket CLOSED");
            socket.ReceivedError += e => Log($"!! socket ERROR: {e.Message}");
            socket.ReceivedMatchState += OnMatchState;
            await socket.ConnectAsync(session);
            Log("socket connected");

            // Phase 1
            var matchId = await Enter(client, socket, session, o.Zone);

            // Scripted scenario mode: run actions + asserts, then exit with WorldModel.ExitCode.
            if (!string.IsNullOrEmpty(o.Scenario))
            {
                var scn = Scenarios.Get(o.Scenario);
                if (scn == null) { Log($"unknown scenario '{o.Scenario}'"); await socket.CloseAsync(); return 2; }
                Log($"=== SCENARIO {o.Scenario} ===");
                await scn.RunAsync(socket, matchId);
                Summary();
                await socket.CloseAsync();
                Log($"=== scenario '{o.Scenario}' exit={WorldModel.ExitCode} ===");
                return WorldModel.ExitCode;
            }

            if (_walk != null) _ = DriveWalk(socket, matchId, _walk.Value); // fire-and-forget path drive
            await Observe(socket, o.Duration);

            if (o.Reconnect)
            {
                Log("=== RECONNECT: leaving match ===");
                await socket.LeaveMatchAsync(matchId);
                await Task.Delay(3000); // let the zone empty-reset + pause settle (mirror the real gap)

                BeginPhase("P2-reconnect");
                matchId = await Enter(client, socket, session, o.Zone);
                await Observe(socket, o.Duration + 10); // a bit longer to catch the post-reconnect stall window
            }

            Summary();
            await socket.CloseAsync();
            return 0;
        }

        private static async Task<string> Enter(IClient client, ISocket socket, ISession session, string zone)
        {
            var enterPayload = JsonSerializer.Serialize(new Dictionary<string, object> { ["zone_id"] = zone });
            var rpc = await client.RpcAsync(session, "world_enter", enterPayload);
            string matchId;
            using (var rdoc = JsonDocument.Parse(rpc.Payload))
                matchId = rdoc.RootElement.GetProperty("match_id").GetString();
            Log($"[{_phase}] world_enter {zone} -> match={matchId}");

            var match = await socket.JoinMatchAsync(matchId);
            _myUserId = match.Self.UserId;
            Log($"[{_phase}] joined match={match.Id} self={_myUserId}");

            // Subscribe to chunks so the SERVER loads them into its collision map (state.Chunks). Without
            // this a passive client never triggers LoadChunk, so every IsBlocked* lookup hits a nil chunk
            // and reads as "blocked" — movement + swarm wander both freeze. A real client subscribes too.
            int subN = 0;
            for (int cx = 0; cx < _chunks; cx++)
                for (int cy = 0; cy < _chunks; cy++)
                {
                    var sub = JsonSerializer.Serialize(new Dictionary<string, object> { ["chunk_x"] = cx, ["chunk_y"] = cy });
                    await socket.SendMatchStateAsync(matchId, OpChunkSubscribe, sub);
                    subN++;
                }
            Log($"[{_phase}] subscribed to {subN} chunks ({_chunks}x{_chunks} grid)");

            double mx = _walk?.x0 ?? 48.0, my = _walk?.y0 ?? 48.0;
            var mv = JsonSerializer.Serialize(new Dictionary<string, object> { ["x"] = mx, ["y"] = my, ["facing"] = 0 });
            await socket.SendMatchStateAsync(matchId, OpMovement, mv);
            Log($"[{_phase}] sent initial movement ({mx:F1},{my:F1})");
            return matchId;
        }

        // Drive the player in a straight line from (x0,y0) to (x1,y1), one ~0.5-cell step per 100ms (~10Hz,
        // matching the server tick). The harness sends RAW positions (no client gate), so this exercises the
        // SERVER's authoritative collision: blocked moves get no PLAYER_CELL_ENTER, so the cell trajectory halts.
        // VERTICAL walk (x held at x0) that steps from the SERVER-CONFIRMED position, so a blocked move
        // actually stops the player instead of tunnelling: we only advance `cur` when the server confirms
        // the previous step (via a PLAYER_CELL_ENTER → _confirmedY), so we never send a position more than
        // one step past the last accepted one. The harness sends RAW positions (no client gate), so this
        // exercises the server-authoritative collision.
        private static async Task DriveWalk(ISocket socket, string matchId, (double x0, double y0, double x1, double y1) w)
        {
            await Task.Delay(1500); // entry + chunk subscriptions settle
            int dir = Math.Sign(w.y1 - w.y0);
            int facing = dir > 0 ? 3 : 0; // up / down
            Log($"[{_phase}] WALK x={w.x0:F1} y {w.y0:F1} -> {w.y1:F1} (stepping from confirmed position)");
            if (double.IsNaN(_confirmedY)) _confirmedY = w.y0;
            double cur = w.y0; int stuck = 0; const double step = 0.34;
            for (int i = 0; i < 600 && Math.Abs(cur - w.y1) > 0.5 && stuck < 12; i++)
            {
                double next = cur + dir * step;
                var mv = JsonSerializer.Serialize(new Dictionary<string, object> { ["x"] = w.x0, ["y"] = next, ["facing"] = facing });
                await socket.SendMatchStateAsync(matchId, OpMovement, mv);
                await Task.Delay(120);
                if (Math.Abs(_confirmedY - next) < 1.2) { cur = next; stuck = 0; } // server accepted
                else stuck++;                                                       // rejected -> blocked
            }
            long fc = double.IsNaN(_confirmedY) ? -1 : (long)Math.Floor(_confirmedY);
            Log($"[{_phase}] WALK ended: confirmed centre cell y={fc} (target y={w.y1:F0}) -> {(stuck >= 12 ? "BLOCKED" : "reached target")}");
        }

        private static void OnMatchState(IMatchState st)
        {
            _recvCount++;
            try
            {
                // Feed the scripted-client world-model (farm/inventory/entity opcodes; ignores the rest).
                WorldModel.Apply(st.OpCode, Encoding.UTF8.GetString(st.State));

                if (st.OpCode == OpZoneTickBroadcast || st.OpCode == OpZoneAuthority)
                {
                    using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(st.State));
                    var root = doc.RootElement;
                    if (root.TryGetProperty("authoritative_tick", out var at)) { _authTick = at.GetInt64(); if (_authTick > _maxAuthTick) _maxAuthTick = _authTick; }
                    // Population time-series: one sample per second (10 ticks)
                    if (_authTick >= _lastPopSampleTick + 10)
                    {
                        _lastPopSampleTick = _authTick;
                        int total = 0;
                        foreach (var kv in _swarmSpawn) total += kv.Value.count;
                        _popSeries.Add((_authTick, total));
                    }
                    if (root.TryGetProperty("last_event_seq", out var ls)) _lastSeq = ls.GetInt64();
                    if (st.OpCode == OpZoneAuthority && root.TryGetProperty("authority_id", out var aid))
                    {
                        var authorityId = aid.GetString();
                        _isAuthority = authorityId == _myUserId;
                        Log($"[{_phase}] ZoneAuthority authority={authorityId} isAuthority={_isAuthority} tick={_authTick} seq={_lastSeq}");
                    }
                }
                else if (st.OpCode == OpSwarmUpdate)
                {
                    using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(st.State));
                    if (doc.RootElement.TryGetProperty("swarms", out var sw) && sw.ValueKind == JsonValueKind.Array)
                        foreach (var s in sw.EnumerateArray())
                        {
                            if (!s.TryGetProperty("id", out var idp)) continue;
                            string id = idp.GetString();
                            double x = s.TryGetProperty("x", out var xp) ? xp.GetDouble() : 0;
                            double y = s.TryGetProperty("y", out var yp) ? yp.GetDouble() : 0;
                            int cnt = s.TryGetProperty("count", out var cp) ? cp.GetInt32() : 0;
                            if (!_swarmSpawn.ContainsKey(id))
                                Log($"[{_phase}] SWARM {id} center=({x:F1},{y:F1}) count={cnt}");
                            _swarmSpawn[id] = (x, y, cnt);
                        }
                }
                else if (st.OpCode == OpInfluenceBroadcast)
                {
                    // Decode events[].seq — the decisive datum for the seq-desync bug.
                    using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(st.State));
                    if (doc.RootElement.TryGetProperty("events", out var evs) && evs.ValueKind == JsonValueKind.Array)
                    {
                        long bMin = long.MaxValue, bMax = -1; int n = 0;
                        foreach (var e in evs.EnumerateArray())
                        {
                            if (!e.TryGetProperty("seq", out var sq)) continue;
                            long s = sq.GetInt64(); n++;
                            if (s < bMin) bMin = s;
                            if (s > bMax) bMax = s;
                            string type = e.TryGetProperty("type", out var tp) ? tp.GetString() : "";
                            if (type == "PLAYER_CELL_ENTER" && e.TryGetProperty("player_id", out var pid) && pid.GetString() == _myUserId
                                && e.TryGetProperty("cell_x", out var ecx) && e.TryGetProperty("cell_y", out var ecy))
                            {
                                _playerCellX = ecx.GetInt64(); _playerCellY = ecy.GetInt64();
                                _confirmedY = _playerCellY + 0.5; // centre of the confirmed cell
                                if (_playerCellY > _playerMaxCellY) _playerMaxCellY = _playerCellY;
                                if (_playerCellY < _playerMinCellY) _playerMinCellY = _playerCellY;
                            }
                            else if (type == "SWARM_SET_TARGET" && e.TryGetProperty("swarm_id", out var swid)
                                && e.TryGetProperty("target_x", out var tx) && e.TryGetProperty("target_y", out var ty))
                            {
                                string id = swid.GetString();
                                double txf = tx.GetInt64() / 1000.0, tyf = ty.GetInt64() / 1000.0;
                                if (_swarmTgt.TryGetValue(id, out var b))
                                    _swarmTgt[id] = (Math.Min(b.minx, txf), Math.Min(b.miny, tyf), Math.Max(b.maxx, txf), Math.Max(b.maxy, tyf));
                                else
                                    _swarmTgt[id] = (txf, tyf, txf, tyf);
                            }
                            else if (type == "SWARM_SPLIT" || type == "SWARM_MERGE" || type == "SWARM_REPRODUCED")
                            {
                                string srcId = e.TryGetProperty("swarm_id", out var p1) ? p1.GetString() : "?";
                                string dstId = e.TryGetProperty("new_swarm_id", out var p2) ? p2.GetString() : "?";
                                long cnt = e.TryGetProperty("split_count", out var p3) ? p3.GetInt64() : -1;
                                long pcnt = e.TryGetProperty("parent_count", out var p4) ? p4.GetInt64() : -1;
                                long bbase = e.TryGetProperty("new_bug_id_base", out var p5) ? p5.GetInt64() : -1;
                                long etick = e.TryGetProperty("tick", out var tt) ? tt.GetInt64() : -1;
                                Log($"[{_phase}] {type}: {srcId} <-> {dstId} count={cnt} parentCount={pcnt} idBase={bbase} (tick={etick} seq={s})");
                                _populationEvents.Add($"{type} {srcId}->{dstId} n={cnt}");

                                // Maintain live per-swarm counts for the population CSV
                                if (type == "SWARM_REPRODUCED" && _swarmSpawn.TryGetValue(srcId, out var rs))
                                    _swarmSpawn[srcId] = (rs.x, rs.y, rs.count + (int)cnt);
                                else if (type == "SWARM_SPLIT")
                                {
                                    if (_swarmSpawn.TryGetValue(srcId, out var ps))
                                        _swarmSpawn[srcId] = (ps.x, ps.y, (int)pcnt);
                                    if (!_swarmSpawn.ContainsKey(dstId))
                                        _swarmSpawn[dstId] = (0, 0, (int)cnt);
                                }
                                else if (type == "SWARM_MERGE")
                                {
                                    if (_swarmSpawn.TryGetValue(srcId, out var ss) && _swarmSpawn.TryGetValue(dstId, out var ab))
                                        _swarmSpawn[srcId] = (ss.x, ss.y, ss.count + ab.count);
                                    _swarmSpawn.Remove(dstId);
                                }
                            }
                            else if (type == "FOOD_CONSUMED" || type == "ITEM_ROTTED")
                            {
                                string fid = e.TryGetProperty("food_id", out var ff) ? ff.GetString() : "?";
                                long lvl = e.TryGetProperty("level", out var lv) ? lv.GetInt64() : -1;
                                Log($"[{_phase}] {type}: {fid} level={lvl} (seq={s})");
                            }
                        }
                        if (n > 0)
                        {
                            if (bMax > _maxInflSeq) _maxInflSeq = bMax;
                            if (bMin < _minInflSeqPhase) _minInflSeqPhase = bMin;
                            if (bMax > _maxInflSeqPhase) _maxInflSeqPhase = bMax;
                            if (!_loggedFirstInflThisPhase)
                            {
                                _loggedFirstInflThisPhase = true;
                                Log($"[{_phase}] FIRST influence after entry: {n} events seq [{bMin}..{bMax}] (watermark={_lastSeq})");
                            }
                            // Flag stale-high seqs (the 7833 signature) against the current watermark.
                            if (!_loggedStaleHigh && _lastSeq >= 0 && bMax > _lastSeq + 100)
                            {
                                _loggedStaleHigh = true;
                                Log($"[{_phase}] STALE-HIGH influence seq={bMax} while watermark={_lastSeq} (gap!)");
                            }
                        }
                    }
                }
                else if (st.OpCode == OpLateJoinSnapshot || st.OpCode == OpZoneHandoff)
                {
                    Log($"[{_phase}] received op{st.OpCode} ({(st.OpCode == OpLateJoinSnapshot ? "LateJoinSnapshot" : "ZoneHandoff")})");
                }
            }
            catch (Exception ex) { Log($"[{_phase}] parse err op{st.OpCode}: {ex.Message}"); }
        }

        private static void BeginPhase(string name)
        {
            _phase = name;
            _loggedFirstInflThisPhase = false;
            _loggedStaleHigh = false;
            _minInflSeqPhase = long.MaxValue;
            _maxInflSeqPhase = -1;
            Log($"=== PHASE {name} ===");
        }

        private static async Task Observe(ISocket socket, int seconds)
        {
            double endAt = Sw.Elapsed.TotalSeconds + seconds;
            double nextReport = Sw.Elapsed.TotalSeconds + 5;
            while (Sw.Elapsed.TotalSeconds < endAt)
            {
                await Task.Delay(250);
                if (Sw.Elapsed.TotalSeconds >= nextReport)
                {
                    nextReport += 5;
                    string inflRange = _maxInflSeqPhase >= 0 ? $"infl[{_minInflSeqPhase}..{_maxInflSeqPhase}]" : "infl[-]";
                    Log($"[{_phase}] t={Sw.Elapsed.TotalSeconds,4:F0}s authTick={_authTick} watermark={_lastSeq} {inflRange} recv={_recvCount} auth={_isAuthority}");
                }
            }
        }

        private static void Summary()
        {
            Log("=== SUMMARY ===");
            Log($"maxAuthTick={_maxAuthTick} maxInfluenceSeq={_maxInflSeq} recvCount={_recvCount} isAuthority={_isAuthority}");
            if (_playerMaxCellY != long.MinValue)
                Log($"PLAYER cells: last=({_playerCellX},{_playerCellY}) y-range [{_playerMinCellY}..{_playerMaxCellY}]");
            foreach (var kv in _swarmSpawn)
            {
                string tgt = _swarmTgt.TryGetValue(kv.Key, out var b)
                    ? $"targets x[{b.minx:F1}..{b.maxx:F1}] y[{b.miny:F1}..{b.maxy:F1}]"
                    : "no SWARM_SET_TARGET seen";
                Log($"SWARM {kv.Key}: spawn=({kv.Value.x:F1},{kv.Value.y:F1}) count={kv.Value.count} {tgt}");
            }
            if (_populationEvents.Count > 0)
            {
                Log($"POPULATION events ({_populationEvents.Count}):");
                foreach (var pe in _populationEvents) Log($"  {pe}");
            }
            if (_popSeries.Count > 0)
            {
                // CSV for tools/plot_fly_counts.py
                var csvPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "fly_counts.csv");
                var sb = new StringBuilder("tick,total_bugs\n");
                foreach (var (tick, total) in _popSeries) sb.Append(tick).Append(',').Append(total).Append('\n');
                System.IO.File.WriteAllText(csvPath, sb.ToString());
                Log($"POPULATION series: {_popSeries.Count} samples -> {csvPath} (plot with tools/plot_fly_counts.py)");
            }
        }

        private static void Log(string m) => Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss.fff}] {m}");

        private sealed class Args
        {
            public string Host = "127.0.0.1", Key = "defaultkey", Zone = "village_21", Tag = "p1", Walk = "", Scenario = "";
            public int Port = 7350, Duration = 15, Chunks = 8;
            public bool Reconnect;
            public static Args Parse(string[] a)
            {
                var o = new Args();
                for (int i = 0; i < a.Length; i++)
                {
                    switch (a[i])
                    {
                        case "--host": o.Host = a[++i]; break;
                        case "--port": o.Port = int.Parse(a[++i]); break;
                        case "--key": o.Key = a[++i]; break;
                        case "--zone": o.Zone = a[++i]; break;
                        case "--duration": o.Duration = int.Parse(a[++i]); break;
                        case "--tag": o.Tag = a[++i]; break;
                        case "--walk": o.Walk = a[++i]; break;
                        case "--chunks": o.Chunks = int.Parse(a[++i]); break;
                        case "--scenario": o.Scenario = a[++i]; break;
                        case "--reconnect": o.Reconnect = true; break;
                    }
                }
                return o;
            }
        }
    }
}
