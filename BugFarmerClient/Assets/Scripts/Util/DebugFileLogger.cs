using System;
using System.IO;
using UnityEngine;

namespace BugFarmer.Util
{
    /// <summary>
    /// Simple file logger for debugging. Writes to BugFarmer_debug.log in persistent data path.
    /// </summary>
    public static class DebugFileLogger
    {
        private static string _logPath;
        private static bool _initialized;

        public static void Initialize()
        {
            if (_initialized) return;

            var pid = System.Diagnostics.Process.GetCurrentProcess().Id;
            _logPath = Path.Combine(Application.persistentDataPath, $"BugFarmer_debug_{pid}.log");

            // Clear old log
            try
            {
                File.WriteAllText(_logPath, $"=== BugFarmer Debug Log Started {DateTime.Now} ===\n");
                Debug.Log($"[DebugFileLogger] Logging to: {_logPath}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[DebugFileLogger] Failed to initialize: {e.Message}");
            }

            _initialized = true;
        }

        public static void Log(string message)
        {
            // Off by default: this does synchronous per-call file I/O on the
            // calling (main) thread. Gated here so all callers go quiet at once.
            if (!DebugConfig.Verbose) return;

            if (!_initialized) Initialize();

            try
            {
                File.AppendAllText(_logPath, $"[{DateTime.Now:HH:mm:ss.fff}] {message}\n");
            }
            catch
            {
                // Silently fail to avoid spam
            }
        }

        public static string GetLogPath()
        {
            if (!_initialized) Initialize();
            return _logPath;
        }
    }
}
