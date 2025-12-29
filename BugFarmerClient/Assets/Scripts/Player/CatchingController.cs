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
    /// - Net swing (net equipped): Terraria-style arc swing, AoE catch multiple
    /// </summary>
    public class CatchingController : MonoBehaviour
    {
        [Header("Catch Settings")]
        [SerializeField] private float catchCooldown = 0.2f;
        [SerializeField] private float handReach = 2.0f;
        [SerializeField] private float netReach = 4.5f;

        [Header("Net Animation")]
        [SerializeField] private GameObject netSwingPrefab;
        [SerializeField] private float swingDuration = 0.15f;
        [SerializeField] private float swingArc = 90f; // Total arc in degrees
        [SerializeField] private float netOffset = 0.5f; // Distance from player center

        [Header("Catch Indicator")]
        [SerializeField] private float netCatchRadius = 1.5f;
        [SerializeField] private float handCatchRadius = 0.5f;
        [SerializeField] private Color catchIndicatorColor = new Color(1f, 1f, 0f, 0.3f); // Yellow, 30% opacity
        [SerializeField] private float indicatorDuration = 0.2f;

        private float _lastCatchTime;
        private Transform _netTransform;
        private SpriteRenderer _netVisual;
        private bool _isSwinging;
        private LineRenderer _catchIndicator;

        /// <summary>
        /// Check if a net is equipped via hotbar selection.
        /// </summary>
        private bool HasNetEquipped
        {
            get
            {
                var inventory = UI.InventoryManager.Instance;
                if (inventory == null) return false;
                var toolId = inventory.GetEquippedToolId();
                return toolId == "small_net" || toolId == "large_net";
            }
        }

        private void Start()
        {
            // Create net swing visual as child (disabled initially)
            if (netSwingPrefab != null)
            {
                var netObj = Instantiate(netSwingPrefab, transform);
                _netTransform = netObj.transform;
                _netTransform.localPosition = Vector3.zero;
                _netVisual = netObj.GetComponent<SpriteRenderer>();
                if (_netVisual != null)
                {
                    _netVisual.enabled = false;
                    Debug.Log($"[Catch] Net visual created: {_netVisual.sprite?.name ?? "NO SPRITE"}");
                }
                else
                {
                    Debug.LogWarning("[Catch] Net prefab has no SpriteRenderer!");
                }
            }
            else
            {
                Debug.LogWarning("[Catch] No net prefab assigned!");
            }

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

        private void Update()
        {
            if (_isSwinging) return;

            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null)
            {
                if (Input.GetMouseButtonDown(0))
                    Debug.Log("[Catch] No match - connect to world first");
                return;
            }

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected)
            {
                if (Input.GetMouseButtonDown(0))
                    Debug.Log("[Catch] Socket not connected");
                return;
            }

            if (Input.GetMouseButtonDown(0) && CanCatch())
            {
                Vector2 clickPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
                Vector2 playerPos = transform.position;
                float dist = (clickPos - playerPos).magnitude;

                Debug.Log($"[Catch] Click at {clickPos}, player at {playerPos}, dist={dist:F2}, netEquipped={HasNetEquipped}");

                // Check reach based on mode
                float maxReach = HasNetEquipped ? netReach : handReach;
                if (dist > maxReach)
                {
                    Debug.Log($"[Catch] Too far! dist={dist:F2} > maxReach={maxReach}");
                    return;
                }

                float catchRadius = HasNetEquipped ? netCatchRadius : handCatchRadius;

                // CLIENT-SIDE: Detect and remove flies immediately
                var swarmManager = SwarmManager.Instance;
                List<CatchResult> catches = null;
                if (swarmManager != null)
                {
                    catches = swarmManager.CatchAtPosition(clickPos, catchRadius);
                }

                // Play animation (even on miss)
                if (HasNetEquipped)
                {
                    Debug.Log("[Catch] Playing net swing animation");
                    Vector2 direction = (clickPos - playerPos).normalized;
                    StartCoroutine(NetSwingRoutine(direction));
                    StartCoroutine(ShowCatchIndicator(clickPos, catchRadius));
                }

                // Send to server for each affected swarm
                if (catches != null)
                {
                    foreach (var result in catches)
                    {
                        var msg = new CatchBugMessage
                        {
                            click_x = clickPos.x,
                            click_y = clickPos.y,
                            swarm_id = result.swarmId,
                            caught_count = result.caughtCount
                        };
                        Debug.Log($"[Catch] Sent: swarm={result.swarmId}, count={result.caughtCount}");
                        SendCatchRequest(msg, world.CurrentMatch.Id, socket);
                    }
                }

                _lastCatchTime = Time.time;
            }
        }

        private bool CanCatch()
        {
            return Time.time - _lastCatchTime >= catchCooldown;
        }

        private IEnumerator NetSwingRoutine(Vector2 swingDirection)
        {
            if (_netVisual == null || _netTransform == null) yield break;

            _isSwinging = true;
            _netVisual.enabled = true;

            // Calculate base angle from direction
            float baseAngle = Mathf.Atan2(swingDirection.y, swingDirection.x) * Mathf.Rad2Deg;
            float halfArc = swingArc / 2f;

            float elapsed = 0f;

            while (elapsed < swingDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / swingDuration;

                // Swing from start of arc to end of arc
                float currentAngle = Mathf.Lerp(baseAngle + halfArc, baseAngle - halfArc, t);

                // Position net at offset from player in current direction
                float radAngle = currentAngle * Mathf.Deg2Rad;
                Vector2 offset = new Vector2(Mathf.Cos(radAngle), Mathf.Sin(radAngle)) * netOffset;
                _netTransform.localPosition = offset;

                // Rotate net to point outward
                _netTransform.localRotation = Quaternion.Euler(0, 0, currentAngle - 90f);

                yield return null;
            }

            _netVisual.enabled = false;
            _netTransform.localPosition = Vector3.zero;
            _netTransform.localRotation = Quaternion.identity;
            _isSwinging = false;
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
