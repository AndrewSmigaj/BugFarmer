using System.Threading.Tasks;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.Entities;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Hidden cross-zone swap: when the local player walks to a zone edge that has a neighbor (from the
    /// world_enter response), fade to black → tear down zone A → join the neighbor at its matching edge →
    /// snap camera → fade back. Reads the player's own world position (1 unit = 1 cell; +Y = north).
    /// Edges WITHOUT a neighbor act as a soft wall (clamp). Attached to the local player by PlayerController.
    /// </summary>
    public class CrossZoneController : MonoBehaviour
    {
        private const float ZoneMax = 255f;  // 256x256 zone, cells 0..255
        private const float Trigger = 2f;    // cross when within this many cells of an edge
        // Arrival insets land the player CLEAR of the opposite edge's trigger band (so you don't
        // immediately re-cross) while staying inside the server's anti-forge window (entry must be
        // within 4 cells of an edge: cy<=4 / cy>=251) and on walkable ground (the mine's grass strip
        // y=250..255; the village south-edge grass). Lo=4 (off the y<=2 trigger), Hi=251 (off y>=253).
        private const float Lo = 4f;         // arrive just inside the near (0) edge
        private const float Hi = 251f;       // arrive just inside the far (255) edge

        private bool _swapping;
        private float _debounceUntil;
        private float _nextDiag;

        private void Update()
        {
            if (_swapping || Time.time < _debounceUntil) return;
            var wm = WorldManager.Instance;
            if (wm == null || wm.CurrentMatch == null) return;
            var n = wm.CurrentNeighbors;

            float px = transform.position.x, py = transform.position.y;

            // DIAGNOSTIC (throttled): see how close to the edge the player gets + the neighbor state.
            if ((px < 8f || px > ZoneMax - 8f || py < 8f || py > ZoneMax - 8f) && Time.time >= _nextDiag)
            {
                _nextDiag = Time.time + 1f;
                Debug.Log($"[CrossZone] near edge pos=({px:F1},{py:F1}) neighbors S={n?.south} N={n?.north} E={n?.east} W={n?.west}");
            }

            if (n != null && py <= Trigger && !string.IsNullOrEmpty(n.south)) { _ = Swap(n.south, px, Hi); return; }
            if (n != null && py >= ZoneMax - Trigger && !string.IsNullOrEmpty(n.north)) { _ = Swap(n.north, px, Lo); return; }
            if (n != null && px <= Trigger && !string.IsNullOrEmpty(n.west)) { _ = Swap(n.west, Hi, py); return; }
            if (n != null && px >= ZoneMax - Trigger && !string.IsNullOrEmpty(n.east)) { _ = Swap(n.east, Lo, py); return; }

            // No-neighbor edge: soft wall so the player can't walk into the void. No-op when in-bounds.
            float cx = Mathf.Clamp(px, 0.5f, ZoneMax - 0.5f);
            float cy = Mathf.Clamp(py, 0.5f, ZoneMax - 0.5f);
            if (cx != px || cy != py)
                transform.position = new Vector3(cx, cy, transform.position.z);
        }

        private async Task Swap(string neighborZone, float ex, float ey)
        {
            _swapping = true;
            PlayerController.InputLocked = true;
            Debug.Log($"[CrossZone] swapping to {neighborZone} at entry ({ex:F0},{ey:F0})");
            try
            {
                // Mirror the server's clamp so client + server agree on the exact entry cell.
                ex = Mathf.Clamp(ex, 0f, ZoneMax);
                ey = Mathf.Clamp(ey, 0f, ZoneMax);

                await ScreenFade.Instance.FadeOut();
                WorldManager.Instance.ResetForZoneSwap();
                await WorldManager.Instance.LeaveWorld();
                await WorldManager.Instance.EnterWorld(neighborZone, CharacterSession.SelectedCharID, ex, ey);

                // AUTHORITATIVELY place the local player at the known entry. Position is client-
                // authoritative (PlayerController.SendMovement pushes transform.position), so the swap
                // must own placement rather than wait for the server's PlayerSpawn (102) — that join-
                // time broadcast races with the JoinMatchAsync CurrentMatch assignment and can be
                // dropped, while a stale old-zone EntityUpdate can win the passive snap and strand us.
                // This sets transform.position + _localPlayerInitialized so no stale snap can stomp it;
                // the server's entry-override places us at the same cell, so the next send re-affirms it.
                EntityManager.Instance?.SetLocalPlayerSpawn(ex, ey);

                // Brief settle behind the cover so the neighbor's edge chunks stream in.
                await WaitSeconds(0.4f);

                var cam = Camera.main != null ? Camera.main.GetComponent<CameraFollow>() : null;
                cam?.SnapToTarget();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[CrossZone] swap to {neighborZone} failed: {e.Message}");
            }
            finally
            {
                await ScreenFade.Instance.FadeIn();
                PlayerController.InputLocked = false;
                _debounceUntil = Time.time + 1.5f; // don't immediately re-trigger at the arrival edge
                _swapping = false;
            }
        }

        private static async Task WaitSeconds(float s)
        {
            float t = 0f;
            while (t < s) { await Task.Yield(); t += Time.unscaledDeltaTime; }
        }
    }
}
