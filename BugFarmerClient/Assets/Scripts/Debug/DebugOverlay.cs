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

        void Start()
        {
            _traceBuffer = new TickTraceBuffer();
            _clientId = Application.isEditor ? "Editor" : "Build";
        }

        void Update()
        {
            if (Input.GetKeyDown(KeyCode.F1)) ToggleRecording();
            if (Input.GetKeyDown(KeyCode.F2)) DumpTrace();
            if (Input.GetKeyDown(KeyCode.F3)) LogCurrentState();
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
            GUILayout.BeginArea(new Rect(10, 10, 300, 150));
            GUILayout.Label($"Client: {_clientId}");
            GUILayout.Label($"Recording: {_isRecording} (Buffer: {_traceBuffer?.Count ?? 0})");
            GUILayout.Label($"Tick: {SwarmManager.Instance?.SimulationTick ?? 0}");
            GUILayout.Label($"Bugs: {SwarmManager.Instance?.TotalBugCount ?? 0}");
            GUILayout.Label("F1=Toggle Record, F2=Dump, F3=Log State");
            GUILayout.EndArea();
        }
    }
}
