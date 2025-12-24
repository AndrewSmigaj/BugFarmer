using System;
using System.Linq;
using Nakama;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using BugFarmer.Networking;
using BugFarmer.Entities;

namespace BugFarmer.UI
{
    /// <summary>
    /// Debug UI panel for testing Nakama connection and world operations.
    /// </summary>
    public class DebugPanel : MonoBehaviour
    {
        [SerializeField] private Button connectButton;
        [SerializeField] private Button createWorldButton;
        [SerializeField] private Button listWorldsButton;
        [SerializeField] private Button joinWorldButton;
        [SerializeField] private TMP_Text statusText;
        [SerializeField] private TMP_InputField worldNameInput;

        private string _lastWorldId;

        private void Start()
        {
            if (connectButton != null) connectButton.onClick.AddListener(OnConnect);
            if (createWorldButton != null) createWorldButton.onClick.AddListener(OnCreateWorld);
            if (listWorldsButton != null) listWorldsButton.onClick.AddListener(OnListWorlds);
            if (joinWorldButton != null) joinWorldButton.onClick.AddListener(OnJoinWorld);

            NetworkManager.Instance.OnConnected += OnSocketConnected;
            NetworkManager.Instance.OnDisconnected += OnSocketDisconnected;
            NetworkManager.Instance.OnError += OnSocketError;

            WorldManager.Instance.OnPlayerJoined += OnPlayerJoined;
            WorldManager.Instance.OnPlayerLeft += OnPlayerLeft;

            Log("DebugPanel initialized. Click Connect to start.");
        }

        private void OnDestroy()
        {
            if (connectButton != null) connectButton.onClick.RemoveListener(OnConnect);
            if (createWorldButton != null) createWorldButton.onClick.RemoveListener(OnCreateWorld);
            if (listWorldsButton != null) listWorldsButton.onClick.RemoveListener(OnListWorlds);
            if (joinWorldButton != null) joinWorldButton.onClick.RemoveListener(OnJoinWorld);

            if (NetworkManager.Instance != null)
            {
                NetworkManager.Instance.OnConnected -= OnSocketConnected;
                NetworkManager.Instance.OnDisconnected -= OnSocketDisconnected;
                NetworkManager.Instance.OnError -= OnSocketError;
            }

            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnPlayerJoined -= OnPlayerJoined;
                WorldManager.Instance.OnPlayerLeft -= OnPlayerLeft;
            }
        }

        private void OnSocketConnected() => Log("Socket connected!");
        private void OnSocketDisconnected(string reason) => Log($"Socket disconnected: {reason}");
        private void OnSocketError(Exception e) => Log($"Error: {e.Message}");
        private void OnPlayerJoined(IUserPresence p) => Log($"Player joined: {p.Username}");
        private void OnPlayerLeft(IUserPresence p) => Log($"Player left: {p.Username}");

        private async void OnConnect()
        {
            Log("Connecting socket...");
            try
            {
                await NetworkManager.Instance.ConnectSocketAsync();
            }
            catch (Exception ex)
            {
                Log($"Connection failed: {ex.Message}");
            }
        }

        private async void OnCreateWorld()
        {
            var name = string.IsNullOrEmpty(worldNameInput?.text) ? "Test World" : worldNameInput.text;
            Log($"Creating world '{name}'...");
            try
            {
                var response = await WorldManager.Instance.CreateWorld(name);
                _lastWorldId = response.world_id;
                Log($"Created world: {response.world_id}");
            }
            catch (Exception ex)
            {
                Log($"Create failed: {ex.Message}");
            }
        }

        private async void OnListWorlds()
        {
            Log("Listing worlds...");
            try
            {
                var worlds = await WorldManager.Instance.ListWorlds();
                foreach (var w in worlds)
                {
                    Log($"  - {w.name} ({w.world_id})");
                    _lastWorldId = w.world_id; // Remember last one for quick join
                }
                Log($"Found {worlds.Length} world(s)");
            }
            catch (Exception ex)
            {
                Log($"List failed: {ex.Message}");
            }
        }

        private async void OnJoinWorld()
        {
            if (string.IsNullOrEmpty(_lastWorldId))
            {
                Log("No world to join. Create or list first.");
                return;
            }
            Log($"Joining world {_lastWorldId}...");
            try
            {
                var match = await WorldManager.Instance.JoinWorld(_lastWorldId);
                Log($"Joined match: {match.Id} with {match.Presences.Count()} player(s)");

                // Tell EntityManager to skip local player in entity updates
                if (EntityManager.Instance != null && WorldManager.Instance.Self != null)
                {
                    EntityManager.Instance.SetLocalPlayerId(WorldManager.Instance.Self.UserId);
                }
            }
            catch (Exception ex)
            {
                Log($"Join failed: {ex.Message}");
            }
        }

        private void Log(string msg)
        {
            Debug.Log($"[DebugPanel] {msg}");
            if (statusText != null)
            {
                statusText.text = msg + "\n" + statusText.text;
                if (statusText.text.Length > 2000)
                    statusText.text = statusText.text[..2000];
            }
        }
    }
}
