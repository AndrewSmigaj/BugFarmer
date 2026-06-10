using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using Nakama;
using BugFarmer.Networking;
using BugFarmer.Entities;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles catching bugs. Two modes:
    /// - Hand catch (no net): Click near swarm, catch exactly 1
    /// - Net swing (net equipped): arc swing, AoE catch multiple
    /// Input arrives via PlayerInputRouter (which owns tool routing + the UI guard);
    /// the swing visual is PlayerToolAnimator (sorting owned in code — the old SmallNet
    /// prefab rendered invisibly on the Default sorting layer).
    /// </summary>
    public class CatchingController : MonoBehaviour
    {
        [Header("Catch Settings")]
        [SerializeField] private float catchCooldown = 0.2f;
        [SerializeField] private float handReach = 2.0f;
        [SerializeField] private float netReach = 4.5f;

        [Header("Catch Indicator")]
        [SerializeField] private float netCatchRadius = 1.5f;
        [SerializeField] private float handCatchRadius = 0.5f;
        [SerializeField] private Color catchIndicatorColor = new Color(1f, 1f, 0f, 0.3f); // Yellow, 30% opacity
        [SerializeField] private float indicatorDuration = 0.2f;

        private float _lastCatchTime;
        private LineRenderer _catchIndicator;
        private Camera _mainCamera;
        private PlayerToolAnimator _animator;

        private void Start()
        {
            _mainCamera = Camera.main;
            _animator = GetComponent<PlayerToolAnimator>();

            // Create catch radius indicator (circle using LineRenderer)
            CreateCatchIndicator();
        }

        private void CreateCatchIndicator()
        {
            var indicatorObj = new GameObject("CatchIndicator");
            indicatorObj.transform.SetParent(null); // World space, not child of player

            _catchIndicator = indicatorObj.AddComponent<LineRenderer>();
            _catchIndicator.useWorldSpace = true;
            _catchIndicator.loop = true;
            _catchIndicator.startWidth = 0.05f;
            _catchIndicator.endWidth = 0.05f;
            _catchIndicator.sortingOrder = 5;

            // Create a simple unlit material
            _catchIndicator.material = new Material(Shader.Find("Sprites/Default"));
            _catchIndicator.startColor = catchIndicatorColor;
            _catchIndicator.endColor = catchIndicatorColor;

            // Generate circle points
            int segments = 32;
            _catchIndicator.positionCount = segments;

            _catchIndicator.enabled = false;
        }

        private void UpdateCirclePositions(Vector2 center, float radius)
        {
            int segments = _catchIndicator.positionCount;
            for (int i = 0; i < segments; i++)
            {
                float angle = (float)i / segments * Mathf.PI * 2f;
                float x = center.x + Mathf.Cos(angle) * radius;
                float y = center.y + Mathf.Sin(angle) * radius;
                _catchIndicator.SetPosition(i, new Vector3(x, y, 0));
            }
        }

        private IEnumerator ShowCatchIndicator(Vector2 position, float radius)
        {
            if (_catchIndicator == null) yield break;

            UpdateCirclePositions(position, radius);
            _catchIndicator.enabled = true;

            yield return new WaitForSeconds(indicatorDuration);

            _catchIndicator.enabled = false;
        }

        /// <summary>
        /// Handle a routed left-click. netMode is resolved by PlayerInputRouter from the
        /// equipped tool's type. Returns true if any bugs were caught — the router uses
        /// this for the bare-hand fallthrough (no bug under cursor → the click breaks).
        /// </summary>
        public bool TryHandleClick(bool netMode)
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null)
            {
                Debug.Log("[Catch] No match - connect to world first");
                return false;
            }

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected)
            {
                Debug.Log("[Catch] Socket not connected");
                return false;
            }

            if (!CanCatch())
                return false;

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return false;
            }

            Vector2 clickPos = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            Vector2 playerPos = transform.position;
            float dist = (clickPos - playerPos).magnitude;

            // Check reach based on mode
            float maxReach = netMode ? netReach : handReach;
            if (dist > maxReach)
            {
                Debug.Log($"[Catch] Too far! dist={dist:F2} > maxReach={maxReach}");
                return false;
            }

            float catchRadius = netMode ? netCatchRadius : handCatchRadius;

            // CLIENT-SIDE: Detect bugs at click position (returns IDs)
            var swarmManager = SwarmManager.Instance;
            List<CatchResult> catches = null;
            if (swarmManager != null)
            {
                catches = swarmManager.GetBugsAtPosition(clickPos, catchRadius);

                // Optimistic removal - remove bugs immediately for instant feedback
                foreach (var result in catches)
                {
                    var swarm = swarmManager.GetSwarm(result.swarmId);
                    swarm?.RemoveBugsById(result.bugIds);
                }
            }

            // Play animation (even on miss) — the net icon swept in-hand by the animator
            if (netMode)
            {
                Vector2 direction = (clickPos - playerPos).normalized;
                string toolId = UI.InventoryManager.Instance?.GetEquippedToolId();
                _animator?.Play("net", Data.EntityDatabase.GetItemSprite(toolId), direction);
                StartCoroutine(ShowCatchIndicator(clickPos, catchRadius));
            }

            // Send bug IDs to server for validation
            bool caughtAny = false;
            if (catches != null)
            {
                foreach (var result in catches)
                {
                    caughtAny = true;
                    var msg = new CatchBugMessage
                    {
                        click_x = clickPos.x,
                        click_y = clickPos.y,
                        swarm_id = result.swarmId,
                        bug_ids = result.bugIds
                    };
                    Debug.Log($"[Catch] Sent: swarm={result.swarmId}, bugIds={result.bugIds.Length}");
                    SendCatchRequest(msg, world.CurrentMatch.Id, socket);
                }
            }

            _lastCatchTime = Time.time;
            return caughtAny;
        }

        private bool CanCatch()
        {
            return Time.time - _lastCatchTime >= catchCooldown;
        }

        private void SendCatchRequest(CatchBugMessage msg, string matchId, ISocket socket)
        {
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(matchId, OpCodes.CatchBug, json);
        }

        private void OnDestroy()
        {
            if (_catchIndicator != null)
            {
                Destroy(_catchIndicator.gameObject);
            }
        }
    }
}
