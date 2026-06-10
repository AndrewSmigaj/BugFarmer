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
        /// arcDegrees/duration of 0 use the tool_type profile defaults (combat passes item
        /// data). kindOverride lets a MOVE pick its animation independent of the tool_type
        /// profile (a sword jab plays Stab on a "sword"): "swing" | "stab" | "sweep".
        /// </summary>
        public void Play(string toolType, Sprite toolSprite, Vector2 aimDir,
                         float arcDegrees = 0f, float duration = 0f, string kindOverride = null)
        {
            if (toolSprite == null || string.IsNullOrEmpty(toolType)) return;
            if (!Profiles.TryGetValue(toolType, out var profile)) return;

            if (!string.IsNullOrEmpty(kindOverride))
            {
                AnimKind? kind = kindOverride switch
                {
                    "swing" => AnimKind.Swing,
                    "stab" => AnimKind.Stab,
                    "sweep" => AnimKind.Sweep,
                    _ => null
                };
                if (kind == null)
                {
                    // Typo'd data must be VISIBLE, not silently the profile default
                    Debug.LogWarning($"[ToolAnimator] Unknown move kind '{kindOverride}' for {toolType}");
                }
                else if (kind != profile.Kind)
                {
                    // Shallow per-call profile with the overridden kind. Stab on a
                    // non-spear profile (sword jab) has no authored StabReach — derive one.
                    profile = new Profile
                    {
                        Kind = kind.Value,
                        Duration = profile.Duration,
                        ArcDegrees = profile.ArcDegrees,
                        Offset = profile.Offset,
                        StabReach = profile.StabReach > 0f ? profile.StabReach : profile.Offset + 0.65f
                    };
                }
            }

            if (_routine != null)
            {
                // Interrupt contract: a mid-flight sweep leaves the trail EMITTING (the
                // routine's own cleanup never runs) — kill it here; the new routine
                // re-enables it if it's a sweep.
                StopCoroutine(_routine);
                _trail.emitting = false;
            }

            float arc = arcDegrees > 0f ? arcDegrees : profile.ArcDegrees;
            float dur = duration > 0f ? duration : profile.Duration;
            if (aimDir.sqrMagnitude < 0.0001f) aimDir = Vector2.right;

            _behindPlayer = Mathf.Abs(aimDir.y) > Mathf.Abs(aimDir.x) && aimDir.y > 0f;

            _held.sprite = toolSprite;
            FitSprite(toolSprite, 1f);

            _routine = StartCoroutine(AnimateRoutine(profile, arc, dur, aimDir.normalized));
        }

        // === Idle held-at-rest display ===
        // _idleToolType/_idleSprite are the SINGLE source of idle truth: SetIdleItem only
        // writes them (+ applies immediately when not animating); every animation end and
        // interrupt path converges on RestoreIdle().

        private string _idleToolType;
        private Sprite _idleSprite;
        private const float IdleScale = 0.75f;     // smaller at rest than mid-swing
        private const float IdleAngle = -35f;      // down-forward at the player's side
        private const float IdleOffset = 0.4f;

        /// <summary>
        /// Set (or clear, with nulls) the equipped item shown in-hand at rest. Gating is
        /// the CALLER's job (v1: tools only — ToolType != null). Applies immediately when
        /// idle; mid-swing it takes effect when the animation restores.
        /// </summary>
        public void SetIdleItem(string toolType, Sprite sprite)
        {
            _idleToolType = toolType;
            _idleSprite = (toolType != null) ? sprite : null;
            if (!IsPlaying)
                RestoreIdle();
        }

        /// <summary>
        /// THE single restore path (routine end + every interrupt): trail off, then the
        /// idle pose or hidden.
        /// </summary>
        private void RestoreIdle()
        {
            _trail.emitting = false;

            if (_idleSprite == null)
            {
                _held.enabled = false;
                return;
            }

            _behindPlayer = false;
            _held.sprite = _idleSprite;
            FitSprite(_idleSprite, IdleScale);
            _pivot.localRotation = Quaternion.Euler(0f, 0f, IdleAngle);
            _held.transform.localPosition = new Vector3(IdleOffset, 0f, 0f);
            _held.transform.localRotation = Quaternion.Euler(0f, 0f, -SpriteArtAngle);
            _held.enabled = true;
        }

        private void FitSprite(Sprite sprite, float multiplier)
        {
            float w = sprite.rect.width / sprite.pixelsPerUnit;
            float h = sprite.rect.height / sprite.pixelsPerUnit;
            float scale = Mathf.Min(1f, MaxSpriteCells / Mathf.Max(w, h)) * multiplier;
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

            IsPlaying = false;
            _routine = null;
            RestoreIdle(); // back to the held-at-rest pose (or hidden when nothing equipped)
        }
    }
}
