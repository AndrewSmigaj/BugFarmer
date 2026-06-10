using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.Player
{
    /// <summary>
    /// Animates the equipped tool sprite in the player's hand — one animator, profile-driven
    /// (no per-tool prefabs). The tool sprite IS the item's display sprite (the icon), drawn
    /// diagonally (grip bottom-left, head top-right) so it reads correctly when rotated.
    ///
    /// Owns its child hierarchy and ALL sorting in code (the old SmallNet prefab sat on the
    /// Default sorting layer and rendered invisibly behind the ground — never again):
    ///   ToolPivot (player center, rotates) -> HeldTool (SpriteRenderer, offset = grip distance)
    ///                                          -> TrailAnchor (TrailRenderer at the head, sweeps)
    /// Added via AddComponent from PlayerController; siblings grab it with GetComponent in Start.
    /// </summary>
    public class PlayerToolAnimator : MonoBehaviour
    {
        public enum AnimKind { Swing, Sweep, Stab, Pour }

        public class Profile
        {
            public AnimKind Kind;
            public float Duration;    // seconds
            public float ArcDegrees;  // Swing/Sweep total arc
            public float Offset;      // sprite distance from player center (world units)
            public float StabReach;   // Stab: how far the sprite lunges
        }

        // Defaults per tool_type; combat callers can override arc/duration from item data.
        private static readonly Dictionary<string, Profile> Profiles = new Dictionary<string, Profile>
        {
            ["axe"]          = new Profile { Kind = AnimKind.Swing, Duration = 0.18f, ArcDegrees = 100f, Offset = 0.55f },
            ["pickaxe"]      = new Profile { Kind = AnimKind.Swing, Duration = 0.18f, ArcDegrees = 100f, Offset = 0.55f },
            ["shovel"]       = new Profile { Kind = AnimKind.Swing, Duration = 0.20f, ArcDegrees = 90f,  Offset = 0.55f },
            ["hoe"]          = new Profile { Kind = AnimKind.Swing, Duration = 0.20f, ArcDegrees = 90f,  Offset = 0.55f },
            ["sword"]        = new Profile { Kind = AnimKind.Swing, Duration = 0.20f, ArcDegrees = 100f, Offset = 0.6f  },
            ["net"]          = new Profile { Kind = AnimKind.Sweep, Duration = 0.25f, ArcDegrees = 90f,  Offset = 0.6f  },
            ["scythe"]       = new Profile { Kind = AnimKind.Sweep, Duration = 0.25f, ArcDegrees = 120f, Offset = 0.6f  },
            ["spear"]        = new Profile { Kind = AnimKind.Stab,  Duration = 0.22f, Offset = 0.45f, StabReach = 1.1f },
            ["watering_can"] = new Profile { Kind = AnimKind.Pour,  Duration = 0.30f, Offset = 0.5f  },
        };

        // The diagonal art convention points the head at +45° in sprite space; this offset
        // makes the head point outward along the pivot's swing direction.
        private const float SpriteArtAngle = 45f;
        private const float MaxSpriteCells = 1.0f; // fit-box cap for the held sprite

        public bool IsPlaying { get; private set; }

        private Transform _pivot;
        private SpriteRenderer _held;
        private TrailRenderer _trail;
        private SpriteRenderer _playerRenderer;
        private bool _behindPlayer; // aiming up -> tool renders behind the head
        private Coroutine _routine;

        private void Awake()
        {
            _playerRenderer = GetComponent<SpriteRenderer>();

            var pivotObj = new GameObject("ToolPivot");
            pivotObj.transform.SetParent(transform, false);
            _pivot = pivotObj.transform;

            var heldObj = new GameObject("HeldTool");
            heldObj.transform.SetParent(_pivot, false);
            _held = heldObj.AddComponent<SpriteRenderer>();
            _held.sortingLayerName = "Occupants";
            _held.enabled = false;

            // Trail rides the tool head (a bit past the sprite center, along the swing radius).
            var trailObj = new GameObject("TrailAnchor");
            trailObj.transform.SetParent(heldObj.transform, false);
            trailObj.transform.localPosition = new Vector3(0.25f, 0.25f, 0f); // toward the head
            _trail = trailObj.AddComponent<TrailRenderer>();
            _trail.material = new Material(Shader.Find("Sprites/Default"));
            _trail.startWidth = 0.15f;
            _trail.endWidth = 0.02f;
            _trail.time = 0.2f;
            _trail.minVertexDistance = 0.05f;
            _trail.startColor = new Color(1f, 1f, 1f, 0.6f);
            _trail.endColor = new Color(1f, 1f, 1f, 0f);
            _trail.sortingLayerName = "Occupants";
            _trail.emitting = false;
        }

        private void LateUpdate()
        {
            // The player rewrites its Y-sorted order every FixedUpdate — track it.
            if (_playerRenderer != null)
            {
                int order = _playerRenderer.sortingOrder + (_behindPlayer ? -1 : 1);
                _held.sortingOrder = order;
                _trail.sortingOrder = order;
            }
        }

        /// <summary>
        /// Play the tool animation for the equipped tool toward aimDir. Plays even on a miss.
        /// arcDegrees/duration of 0 use the tool_type profile defaults (combat passes item data).
        /// </summary>
        public void Play(string toolType, Sprite toolSprite, Vector2 aimDir,
                         float arcDegrees = 0f, float duration = 0f)
        {
            if (toolSprite == null || string.IsNullOrEmpty(toolType)) return;
            if (!Profiles.TryGetValue(toolType, out var profile)) return;

            if (_routine != null) StopCoroutine(_routine);

            float arc = arcDegrees > 0f ? arcDegrees : profile.ArcDegrees;
            float dur = duration > 0f ? duration : profile.Duration;
            if (aimDir.sqrMagnitude < 0.0001f) aimDir = Vector2.right;

            _behindPlayer = Mathf.Abs(aimDir.y) > Mathf.Abs(aimDir.x) && aimDir.y > 0f;

            _held.sprite = toolSprite;
            FitSprite(toolSprite);

            _routine = StartCoroutine(AnimateRoutine(profile, arc, dur, aimDir.normalized));
        }

        private void FitSprite(Sprite sprite)
        {
            float w = sprite.rect.width / sprite.pixelsPerUnit;
            float h = sprite.rect.height / sprite.pixelsPerUnit;
            float scale = Mathf.Min(1f, MaxSpriteCells / Mathf.Max(w, h));
            _held.transform.localScale = new Vector3(scale, scale, 1f);
        }

        private IEnumerator AnimateRoutine(Profile profile, float arc, float duration, Vector2 aim)
        {
            IsPlaying = true;
            _held.enabled = true;

            float aimAngle = Mathf.Atan2(aim.y, aim.x) * Mathf.Rad2Deg;
            _held.transform.localPosition = new Vector3(profile.Offset, 0f, 0f);
            _held.transform.localRotation = Quaternion.Euler(0f, 0f, -SpriteArtAngle);

            switch (profile.Kind)
            {
                case AnimKind.Swing:
                case AnimKind.Sweep:
                {
                    bool sweep = profile.Kind == AnimKind.Sweep;
                    float half = arc / 2f;
                    _pivot.localRotation = Quaternion.Euler(0f, 0f, aimAngle + half);
                    if (sweep)
                    {
                        _trail.Clear(); // AFTER repositioning, or it streaks from the old spot
                        _trail.time = duration;
                        _trail.emitting = true;
                    }

                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float eased = 1f - (1f - t) * (1f - t); // ease-out: fast start
                        float angle = Mathf.Lerp(aimAngle + half, aimAngle - half, eased);
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
                        yield return null;
                    }
                    if (sweep) _trail.emitting = false;
                    break;
                }
                case AnimKind.Stab:
                {
                    _pivot.localRotation = Quaternion.Euler(0f, 0f, aimAngle);
                    float outTime = duration * 0.4f;
                    float backTime = duration - outTime;
                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float x = elapsed < outTime
                            ? Mathf.Lerp(profile.Offset, profile.StabReach, elapsed / outTime)
                            : Mathf.Lerp(profile.StabReach, profile.Offset,
                                         (elapsed - outTime) / backTime);
                        _held.transform.localPosition = new Vector3(x, 0f, 0f);
                        yield return null;
                    }
                    break;
                }
                case AnimKind.Pour:
                {
                    _pivot.localRotation = Quaternion.Euler(0f, 0f, aimAngle);
                    // Tip the can over the target; WaterDroplet provides the splash feedback.
                    _held.transform.localRotation = Quaternion.Euler(0f, 0f, -SpriteArtAngle - 40f);
                    yield return new WaitForSeconds(duration);
                    break;
                }
            }

            _held.enabled = false;
            IsPlaying = false;
            _routine = null;
        }
    }
}
