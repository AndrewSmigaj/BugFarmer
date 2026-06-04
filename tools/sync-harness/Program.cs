using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Nakama;

// Headless Bug Farmer sync harness.
//
// A PROTOCOL OBSERVER (not a reimplementation of the client sync state machine): it joins a
// world via the real Nakama .NET SDK, then records every incoming match message and watches for
// a reception gap. Its question is narrow and decisive: "does the server keep delivering ticks to
// a present client?" Running headless (no Unity main-thread pump) localizes the freeze:
//   - reproduces the reception stop  -> server/protocol side
//   - stays clean while Unity freezes -> Unity main-thread side
//
// Usage: dotnet run -- [--host 127.0.0.1] [--port 7350] [--key defaultkey]
//                      [--zone sim_test] [--duration 150] [--tag p1]
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

        private static async Task<int> Main(string[] args)
        {
            var o = Args.Parse(args);
            Log($"connecting to {o.Host}:{o.Port} key={o.Key} zone={o.Zone} duration={o.Duration}s");

            var client = new Client("http", o.Host, o.Port, o.Key) { Timeout = 10 };
            var deviceId = $"sim-{o.Tag}-{Guid.NewGuid():N}".Substring(0, 24);
            var session = await client.AuthenticateDeviceAsync(deviceId);
            Log($"authenticated user={session.UserId}");

            var sw = Stopwatch.StartNew();
            double lastRecvMs = 0;
            long recvCount = 0, authTick = -1, lastSeq = -1, maxAuthTick = -1;
            string authorityId = null, myUserId = session.UserId;
            bool isAuthority = false, gapOpen = false;
            int gapCount = 0;
            var opCounts = new Dictionary<long, long>();

            var socket = Socket.From(client);
            socket.Closed += () => Log("!! socket CLOSED");
            socket.ReceivedError += e => Log($"!! socket ERROR: {e.Message}");
            socket.ReceivedMatchState += st =>
            {
                recvCount++;
                lastRecvMs = sw.Elapsed.TotalMilliseconds;
                if (gapOpen) { Log($"reception RESUMED after gap (authTick={authTick})"); gapOpen = false; }
                opCounts.TryGetValue(st.OpCode, out var c);
                opCounts[st.OpCode] = c + 1;

                if (st.OpCode == OpZoneTickBroadcast || st.OpCode == OpZoneAuthority)
                {
                    try
                    {
                        using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(st.State));
                        var root = doc.RootElement;
                        if (root.TryGetProperty("authoritative_tick", out var at)) { authTick = at.GetInt64(); if (authTick > maxAuthTick) maxAuthTick = authTick; }
                        if (root.TryGetProperty("last_event_seq", out var ls)) lastSeq = ls.GetInt64();
                        if (st.OpCode == OpZoneAuthority && root.TryGetProperty("authority_id", out var aid))
                        {
                            authorityId = aid.GetString();
                            isAuthority = authorityId == myUserId;
                            Log($"ZoneAuthority authority={authorityId} isAuthority={isAuthority}");
                        }
                    }
                    catch (Exception ex) { Log($"parse err op{st.OpCode}: {ex.Message}"); }
                }
                else if (st.OpCode == OpLateJoinSnapshot || st.OpCode == OpZoneHandoff)
                {
                    Log($"received op{st.OpCode} ({(st.OpCode == OpLateJoinSnapshot ? "LateJoinSnapshot" : "ZoneHandoff")})");
                }
            };

            await socket.ConnectAsync(session);
            Log("socket connected");

            // Enter the canonical world for the zone (find-or-create singleton, server-side).
            var enterPayload = JsonSerializer.Serialize(new Dictionary<string, object> { ["zone_id"] = o.Zone });
            var rpc = await client.RpcAsync(session, "world_enter", enterPayload);
            string matchId;
            using (var rdoc = JsonDocument.Parse(rpc.Payload))
                matchId = rdoc.RootElement.GetProperty("match_id").GetString();
            Log($"world_enter {o.Zone} -> match={matchId}");

            var match = await socket.JoinMatchAsync(matchId);
            myUserId = match.Self.UserId;
            int presences = 0; foreach (var _ in match.Presences) presences++;
            Log($"joined match={match.Id} self={myUserId} presences={presences}");

            // One movement to establish a player cell (mirror the real client / repro).
            var mv = JsonSerializer.Serialize(new Dictionary<string, object> { ["x"] = 48.0, ["y"] = 48.0, ["facing"] = 0 });
            await socket.SendMatchStateAsync(matchId, OpMovement, mv);
            Log("sent initial movement (cell 48,48)");

            // Observe: report progress every ~5s; flag a >2s reception gap (the freeze signature).
            double endAt = sw.Elapsed.TotalSeconds + o.Duration;
            double nextReport = 5;
            while (sw.Elapsed.TotalSeconds < endAt)
            {
                await Task.Delay(250);
                double now = sw.Elapsed.TotalSeconds;
                double gap = (sw.Elapsed.TotalMilliseconds - lastRecvMs) / 1000.0;
                if (recvCount > 0 && gap > 2.0 && !gapOpen)
                {
                    gapOpen = true; gapCount++;
                    Log($"RECEPTION GAP gap={gap:F1}s lastAuthTick={authTick} recvCount={recvCount} connected={socket.IsConnected}");
                }
                if (now >= nextReport)
                {
                    nextReport += 5;
                    Log($"t={now,4:F0}s authTick={authTick} lastSeq={lastSeq} recv={recvCount} authority={isAuthority}");
                }
            }

            Log("=== SUMMARY ===");
            Log($"maxAuthTick={maxAuthTick} recvCount={recvCount} gaps={gapCount} isAuthority={isAuthority} connected={socket.IsConnected}");
            var ops = new List<string>(); foreach (var kv in opCounts) ops.Add($"op{kv.Key}={kv.Value}");
            ops.Sort(); Log("opcodes: " + string.Join(" ", ops));
            bool advanced = maxAuthTick >= 50;
            Log(gapCount == 0 && advanced
                ? "RESULT: PASS (ticks advanced, no reception gap)"
                : $"RESULT: {(advanced ? "GAP DETECTED" : "NO ADVANCE")} (gaps={gapCount}, maxAuthTick={maxAuthTick})");

            await socket.CloseAsync();
            return gapCount == 0 && advanced ? 0 : 1;
        }

        private static void Log(string m) => Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss.fff}] {m}");

        private sealed class Args
        {
            public string Host = "127.0.0.1", Key = "defaultkey", Zone = "sim_test", Tag = "p1";
            public int Port = 7350, Duration = 150;
            public static Args Parse(string[] a)
            {
                var o = new Args();
                for (int i = 0; i + 1 < a.Length; i += 2)
                {
                    var v = a[i + 1];
                    switch (a[i])
                    {
                        case "--host": o.Host = v; break;
                        case "--port": o.Port = int.Parse(v); break;
                        case "--key": o.Key = v; break;
                        case "--zone": o.Zone = v; break;
                        case "--duration": o.Duration = int.Parse(v); break;
                        case "--tag": o.Tag = v; break;
                    }
                }
                return o;
            }
        }
    }
}
