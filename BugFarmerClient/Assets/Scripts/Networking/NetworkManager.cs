using System;
using System.Threading.Tasks;
using BugFarmer.Util;
using Nakama;
using UnityEngine;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Thread-safe singleton for Nakama connection.
    /// Handles authentication, session management, and socket connection.
    /// Pattern validated against official Nakama Unity SDK snippets.
    /// </summary>
    public class NetworkManager : MonoBehaviour
    {
        private const string SingletonName = "/[NetworkManager]";
        private const string SessionPrefName = "nakama.session";
        private const string DeviceIdPrefName = "nakama.deviceid";

        private static readonly object Lock = new object();
        private static NetworkManager _instance;

        public static NetworkManager Instance
        {
            get
            {
                lock (Lock)
                {
                    if (_instance != null) return _instance;

                    var go = GameObject.Find(SingletonName);
                    if (go == null)
                    {
                        go = new GameObject(SingletonName);
                    }

                    if (go.GetComponent<NetworkManager>() == null)
                    {
                        go.AddComponent<NetworkManager>();
                    }

                    DontDestroyOnLoad(go);
                    _instance = go.GetComponent<NetworkManager>();
                    return _instance;
                }
            }
        }

        public IClient Client { get; private set; }
        public ISocket Socket { get; private set; }
        public Task<ISession> Session { get; private set; }

        public event Action OnConnected;
        public event Action<string> OnDisconnected;
        public event Action<Exception> OnError;

        private void Awake()
        {
            // Initialize Client and Socket here (not in constructor)
            // because NewSocket creates a GameObject internally
            Client = new Client("http", "127.0.0.1", 7350, "defaultkey");
#if UNITY_EDITOR
            // Nakama's SDK logger logs EVERY socket message with its full JSON
            // payload via Debug.LogFormat — on the main thread. At the per-tick
            // EntityUpdate/SwarmUpdate rate that both spams the console AND slows
            // the client enough to fill the server's outgoing queue (the
            // "session outgoing queue full" disconnect). Off by default; flip
            // DebugConfig.Verbose to bring it back for debugging.
            if (DebugConfig.Verbose)
                Client.Logger = new UnityLogger();
#endif
            // Late-join/snapshot messages can be large in dense zones: village_21_B's LateJoinSnapshot is
            // ~230KB raw → ~305KB base64 on the wire (Nakama frames match-state data as base64 in a JSON
            // envelope). The Nakama client's default MaxMessageReadSize is 256KB; an over-cap frame is
            // silently truncated → the websocket framing desyncs → the late joiner stops receiving ALL
            // zone-sync messages (snapshot + tick broadcasts) → 0 swarms (every 2nd player into a populated
            // zone sees no bugs). Raise the client read cap to the server's max_message_size_bytes (8MB) so
            // the client accepts anything the server is allowed to send.
            Socket = Client.NewSocket(useMainThread: true,
                defaultAdapter: new Nakama.WebSocketStdlibAdapter(maxMessageReadSize: 8 * 1024 * 1024));
            Socket.Connected += () =>
            {
                Debug.Log("[NetworkManager] Socket connected");
                DebugFileLogger.Log("[NetworkManager] Socket connected");
                OnConnected?.Invoke();
            };

            Socket.Closed += (reason) =>
            {
                Debug.Log($"[NetworkManager] Socket closed: {reason}");
                DebugFileLogger.Log($"[NetworkManager] Socket closed: {reason}");
                OnDisconnected?.Invoke(reason);
            };

            Socket.ReceivedError += e =>
            {
                Debug.LogError($"[NetworkManager] Socket error: {e.Message}");
                DebugFileLogger.Log($"[NetworkManager] Socket error: {e.Message}");
                OnError?.Invoke(e);
            };

            RestoreOrAuthenticateSession();
        }

        // SYNC-TEST hook: the -clientid <id> command-line flag (set by tools/run_sync_test.sh) makes each
        // headless instance a DISTINCT account with its own stable device id. Two instances of one BUILD
        // share PlayerPrefs, so without this they'd auth as the same device/account and the server would
        // treat them as one player. Returns null in normal runs (no flag) -> unchanged behavior.
        private static string SyncTestClientId()
        {
            var args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (args[i] == "-clientid") return args[i + 1];
            return null;
        }

        private void RestoreOrAuthenticateSession()
        {
            // Sync-test instances must NOT restore the shared PlayerPrefs session — force a fresh device auth.
            if (!string.IsNullOrEmpty(SyncTestClientId()))
            {
                Session = AuthenticateAsync();
                return;
            }

            var authToken = PlayerPrefs.GetString(SessionPrefName, string.Empty);
            ISession session = null;

            if (!string.IsNullOrEmpty(authToken))
            {
                session = Nakama.Session.Restore(authToken);
            }

            var expireCheck = DateTime.UtcNow.AddDays(1);

            if (session == null || session.HasExpired(expireCheck))
            {
                Debug.Log("[NetworkManager] Authenticating new session...");
                Session = AuthenticateAsync();
                Session.ContinueWith(t =>
                {
                    if (t.IsCompleted && !t.IsFaulted)
                    {
                        Debug.Log($"[NetworkManager] Authenticated as {t.Result.Username}");
                        PlayerPrefs.SetString(SessionPrefName, t.Result.AuthToken);
                        PlayerPrefs.Save();
                    }
                    else if (t.IsFaulted)
                    {
                        Debug.LogError($"[NetworkManager] Authentication failed: {t.Exception?.InnerException?.Message}");
                    }
                }, TaskScheduler.FromCurrentSynchronizationContext());
            }
            else
            {
                Debug.Log($"[NetworkManager] Restored session for {session.Username}");
                Session = Task.FromResult(session);
            }
        }

        private Task<ISession> AuthenticateAsync()
        {
            // Sync-test: distinct, stable device id per -clientid (no PlayerPrefs — two build instances share it).
            var syncId = SyncTestClientId();
            if (!string.IsNullOrEmpty(syncId))
            {
                var dev = "synctest_" + syncId;
                Debug.Log($"[NetworkManager] SYNC-TEST device id: {dev}");
                return Client.AuthenticateDeviceAsync(dev);
            }

            // Use different device ID for build vs editor to allow local multiplayer testing
            var prefKey = DeviceIdPrefName;
#if !UNITY_EDITOR
            prefKey += "_build";
#endif
            var deviceId = PlayerPrefs.GetString(prefKey, "");
            if (string.IsNullOrEmpty(deviceId))
            {
                deviceId = SystemInfo.deviceUniqueIdentifier + "_" + System.Guid.NewGuid().ToString("N")[..8];
                PlayerPrefs.SetString(prefKey, deviceId);
                PlayerPrefs.Save();
            }
            Debug.Log($"[NetworkManager] Using device ID: {deviceId}");
            return Client.AuthenticateDeviceAsync(deviceId);
        }

        public async Task ConnectSocketAsync()
        {
            var session = await Session;
            if (!Socket.IsConnected)
            {
                Debug.Log("[NetworkManager] Connecting socket...");
                await Socket.ConnectAsync(session);
            }
        }

        public async Task DisconnectSocketAsync()
        {
            if (Socket.IsConnected)
            {
                await Socket.CloseAsync();
            }
        }

        private void OnApplicationQuit()
        {
            Socket?.CloseAsync();
        }
    }
}
