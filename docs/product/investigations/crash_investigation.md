# Client crash/freeze investigation — findings

**Date:** 2026-06-13 (investigation of the 2026-06-12 session)
**Scope:** read-only investigation per plan `i-want-to-try-humming-comet.md`. Deliverable: this
report + a proposed (separate) fix plan.

> **STATUS 2026-06-13 — cause fix LANDED, verify pending.** The logging storm (root cause C4)
> has been fixed client-side: `SetStackTraceLogType(Log/Warning,None)` in `UIBootstrap`; a
> default-off `DebugConfig.Verbose` gating the hot `Debug.Log` sites and `DebugFileLogger`
> internally; the defeated tick-gate throttle removed; plus the `HotbarUI.cs:53` NRE guard.
> **C3 (no reconnect) is intentionally NOT yet fixed** — deferred to the "client reconnect /
> self-heal" backlog item. Confirm with the in-Editor soak in the Verification section below.

## TL;DR — root cause CONFIRMED with evidence

The client freeze is a **client-side synchronous-logging storm** that stalls the Unity main
thread, which makes the client unable to drain its WebSocket. Nakama then closes the session
server-side with **`session outgoing queue full`**, and the client has **no reconnect path**, so
it sits frozen with no ticks while the server keeps running. This matches every reported symptom
(client dies / server lives / "relatively quickly" / triggered by normal play with more systems /
"sign back on and it's fine").

Andrew's hypothesis was right about the *mechanism* (server closed the socket, client left stuck)
— but the **cause is client-side**, not a server bug.

### The chain (each link evidenced)
1. **Per-tick + per-message logging, never gated.** Each `Debug.Log` in the Editor forces a
   synchronous `StackTraceUtility:ExtractStackTrace()`, **and** each call also hits
   `DebugFileLogger.Log` → `File.AppendAllText` (open→append→close a file handle *per line*, on
   the main thread; under WSL the path is on the Windows fs where open/close is slow).
2. → The Unity **main thread spends its time logging instead of draining the socket**; the Editor
   Console also retains every entry (memory growth).
3. → Nakama's per-session **outgoing queue fills** → server closes the socket:
   `[NetworkManager] Socket closed: session outgoing queue full` (**10 occurrences** in the log).
4. → `Socket.Closed` fires `OnDisconnected`, whose **only subscriber is `DebugPanel`** (a label
   update). **No reconnect.** Client frozen, no ticks. Server unaffected (other sessions fine).
5. → Relaunch re-auths via `RestoreOrAuthenticateSession()` → "fine again."

## Evidence base

- **Unity Editor log** (Andrew played in-Editor, not a Player build):
  `/mnt/c/Users/emily/AppData/Local/Unity/Editor/Editor.log` — **2.4 GB / 31,749,473 lines**,
  last written 2026-06-12 21:40. The sheer size *is* a finding.
- The stale `Player.log` (Jun 2) is a clean shutdown — used only as a healthy-cadence baseline.
- Server docker logs from the session are **gone** (container was restarted; `Up 28s`), but the
  client log captured the server's close reason, so they were not needed.

### Volume (sample of 200k mid-log lines)
| Message | count / 200k lines |
|---|---|
| `[SwarmManager] Tick gate:` | 3,202 |
| `[SwarmManager] ZoneTickBroadcast:` | 1,600 |
| ≈ ticks in the window | ~1,600 |

→ **~125 log lines per server tick**, each line a `Debug.Log` (stack-trace extraction) **plus** a
`DebugFileLogger` file append.

### The defeated throttle (a real logic bug)
`SwarmManager.cs:306-313` intends to log the tick gate "every 50 ticks **OR** when `canAdvance`
changes." But during normal `Live` play `canAdvance` **alternates True/False every single tick**
(visible throughout the log and in the healthy `Player.log` baseline), so the transition clause
`canAdvance != _lastLoggedCanAdvance` fires **every tick**. The throttle is a no-op → ~2 tick-gate
logs/tick.

Ungated per-message logs:
- `WorldManager.cs:199` — logs every opcode except EntityUpdate/SwarmUpdate (so 71/78/11/… every receipt).
- `SwarmManager.cs:631` — logs ZoneAuthority/ZoneTickBroadcast/ZoneHandoff/LateJoinSnapshot/InfluenceBroadcast every receipt (ZoneTickBroadcast = every tick).

### The disconnect / no-reconnect (server-side close + frozen client)
- `[NetworkManager] Socket closed: session outgoing queue full` ×10, interleaved with
  `WebSocketException: The remote party closed the WebSocket connection without completing the
  close handshake`.
- `NetworkManager.cs:75-80` `Socket.Closed` → log + `OnDisconnected?.Invoke`. **No reconnect.**
- Only subscriber: `DebugPanel.cs:35` (UI text). Confirms the freeze persists by design.

## The C1–C8 matrix — verdicts

| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| **C1** | Per-frame C# exception | **REFUTED** | Exactly **one** NullReferenceException in 2.4 GB, and it's a one-time **startup** NRE (`HotbarUI.Start`), not per-frame. |
| **C2** | Exception on a specific server message | **REFUTED** | No per-message exceptions found anywhere in the log. |
| **C3** | Disconnect + no/broken reconnect | **CONFIRMED (persistence)** | `Socket.Closed` only updates a DebugPanel; no reconnect path exists. This is *why* the freeze sticks. |
| **C4** | Main-thread stall → server backpressure close | **CONFIRMED (trigger)** | `session outgoing queue full` ×10; logging storm (125 lines/tick, stack-trace + sync file I/O) is the stall. |
| **C5** | Runaway allocation / leak | **SUSPECTED (contributing)** | Editor Console retains 31.7M entries + 2.4 GB log → memory growth/GC thrash compounds the stall. Not separately isolated. |
| **C6** | Server panic → frozen zone | **REFUTED** | No server panic; tick gate healthy to the end (frontier advancing right before the clean editor shutdown). |
| **C7** | Frontier/seq desync deadlock | **REFUTED** | At session end `simTick` advances 15684→15704, frontier advancing, watermark tracks seq, `canAdvance` alternates normally. No stale-high/gate stall. |
| **C8** | Server hang (infinite loop) | **REFUTED** | Frontier kept advancing; the server was producing ticks *faster than the client could consume* (the opposite of a hang). |

## Secondary bug found (independent of the freeze)
`HotbarUI.cs:53` — `slots[i].Initialize(...)` throws NRE when a scene-provided `slots` array has
null elements. `BuildIfEmpty()` only skips rebuild when `slots.Length > 0`, not when every element
is assigned. One-time at startup; breaks hotbar slot init but does not cause the freeze.

## Proposed fix plan (SEPARATE — not applied in this pass)

**Primary (kills the root cause):**
1. Kill the Editor's per-log stack-trace cost: `Application.SetStackTraceLogType(LogType.Log,
   StackTraceLogType.None)` at startup (Log/Warning; keep stacks for Error/Exception).
2. Gate all per-tick/per-message logs behind a verbosity flag **default-off**
   (`WorldManager.cs:199`, `SwarmManager.cs:309`, `:631`, `:1470`).
3. Fix the tick-gate throttle so the `canAdvance`-transition clause doesn't fire every tick
   (it toggles every tick by design) — or drop the per-tick branch entirely.
4. Make `DebugFileLogger` non-blocking: buffer + flush on a background thread (or remove the
   per-tick callers). `File.AppendAllText` per line on the main thread must go.

**Secondary (self-heals transient closes):**
5. Add client reconnect on `Socket.Closed` (re-join match + resync frontier) so a one-off
   backpressure close recovers instead of freezing.

**Tertiary:**
6. Null-guard `HotbarUI.cs:53` (and harden `BuildIfEmpty` against partially-populated arrays).

**Optional server mitigation (not the cause):** larger per-session outgoing queue and/or
unreliable delivery for high-rate broadcasts — defense in depth only; fixing client logging
removes the pressure.

## Verification for the fix pass
After (1)–(4): a long in-Editor soak with active play (sword/hoe/inventory/combat) should produce
a **small** editor log and **zero** `session outgoing queue full` closes. The sync-harness already
shows the server stays healthy with a well-behaved consumer, which corroborates that the consumer
(client) was the bottleneck.
