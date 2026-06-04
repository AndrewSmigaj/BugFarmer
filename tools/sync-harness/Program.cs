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
        private static bool _isAuthority, _loggedFirstInflThisPhase, _loggedStaleHigh;

        private static async Task<int> Main(string[] args)
        {
            var o = Args.Parse(args);
            Log($"connect {o.Host}:{o.Port} zone={o.Zone} duration={o.Duration}s reconnect={o.Reconnect}");

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

            var mv = JsonSerializer.Serialize(new Dictionary<string, object> { ["x"] = 48.0, ["y"] = 48.0, ["facing"] = 0 });
            await socket.SendMatchStateAsync(matchId, OpMovement, mv);
            Log($"[{_phase}] sent initial movement (cell 48,48)");
            return matchId;
        }

        private static void OnMatchState(IMatchState st)
        {
            _recvCount++;
            try
            {
                if (st.OpCode == OpZoneTickBroadcast || st.OpCode == OpZoneAuthority)
                {
                    using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(st.State));
                    var root = doc.RootElement;
                    if (root.TryGetProperty("authoritative_tick", out var at)) { _authTick = at.GetInt64(); if (_authTick > _maxAuthTick) _maxAuthTick = _authTick; }
                    if (root.TryGetProperty("last_event_seq", out var ls)) _lastSeq = ls.GetInt64();
                    if (st.OpCode == OpZoneAuthority && root.TryGetProperty("authority_id", out var aid))
                    {
                        var authorityId = aid.GetString();
                        _isAuthority = authorityId == _myUserId;
                        Log($"[{_phase}] ZoneAuthority authority={authorityId} isAuthority={_isAuthority} tick={_authTick} seq={_lastSeq}");
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
        }

        private static void Log(string m) => Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss.fff}] {m}");

        private sealed class Args
        {
            public string Host = "127.0.0.1", Key = "defaultkey", Zone = "village_21", Tag = "p1";
            public int Port = 7350, Duration = 15;
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
                        case "--reconnect": o.Reconnect = true; break;
                    }
                }
                return o;
            }
        }
    }
}
