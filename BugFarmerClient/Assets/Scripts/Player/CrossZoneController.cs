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

        /// <summary>
        /// Cross into a zone now, as walking off an edge does — for the headless crossing test (HeadlessSyncTest
        /// -crosstest), whose small test zones are narrower than the 256-cell edges this controller watches.
        /// </summary>
        public Task CrossTo(string neighborZone, float ex, float ey) => _swapping ? Task.CompletedTask : Swap(neighborZone, ex, ey);

        private async Task Swap(string neighborZone, float ex, float ey)
        {
            _swapping = true;
            PlayerController.InputLocked = true;
            Debug.Log($"[CrossZone] swapping to {neighborZone} at entry ({ex:F0},{ey:F0})");
            // Where we came from: if the neighbour can't be entered, we go back here rather than strand the player —
            // pulled back out of the edge band, so they don't walk straight into the failed crossing again.
            string sourceZone = WorldManager.Instance.CurrentZoneId;
            float sx = transform.position.x, sy = transform.position.y;
            float backX = sx <= Trigger ? Lo : sx >= ZoneMax - Trigger ? Hi : sx;
            float backY = sy <= Trigger ? Lo : sy >= ZoneMax - Trigger ? Hi : sy;
            bool sentBack = false;
            try
            {
                // Mirror the server's clamp so client + server agree on the exact entry cell.
                ex = Mathf.Clamp(ex, 0f, ZoneMax);
                ey = Mathf.Clamp(ey, 0f, ZoneMax);

                await ScreenFade.Instance.FadeOut();
                WorldManager.Instance.ResetForZoneSwap();
                await WorldManager.Instance.LeaveWorld();
                try
                {
                    // D73: the server waits until zone A has saved the character before letting it into zone B;
                    // a "busy" answer is retried behind the fade for up to 15 s.
                    await WorldManager.Instance.EnterWorldWithRetry(neighborZone, CharacterSession.SelectedCharID, ex, ey);
                }
                catch (System.Exception enterFailed) when (WorldManager.Instance.CurrentMatch == null)
                {
                    // Not in any zone now (a join that went through and failed afterwards is NOT this case: the player
                    // is in the neighbour, and the outer handler keeps them there).
                    Debug.LogWarning($"[CrossZone] couldn't enter {neighborZone} ({enterFailed.Message}) — going back to {sourceZone}");
                    WorldManager.Instance.ResetForZoneSwap();
                    await WorldManager.Instance.EnterWorldWithRetry(sourceZone, CharacterSession.SelectedCharID, backX, backY);
                    ex = backX;
                    ey = backY;
                    sentBack = true;
                }

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
                if (sentBack)
                    WorldToast.Instance?.Show("Couldn't cross into the next area just now — try again in a moment.");
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
