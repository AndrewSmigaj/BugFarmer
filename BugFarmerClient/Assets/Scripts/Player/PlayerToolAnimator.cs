using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Networking; // Direction

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
        public enum AnimKind { Swing, Sweep, Stab, Pour, Scoop, Chop, Till }

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
            // Heavy tools (axe/pickaxe) swing SLOWER — a longer, weightier chop (owner: heavy = slower). Their
            // break cadence is widened to match in BreakingController so the long swing isn't interrupted.
            ["axe"]          = new Profile { Kind = AnimKind.Chop,  Duration = 0.34f, ArcDegrees = 110f, Offset = 0.55f },
            ["pickaxe"]      = new Profile { Kind = AnimKind.Chop,  Duration = 0.34f, ArcDegrees = 110f, Offset = 0.55f },
            ["shovel"]       = new Profile { Kind = AnimKind.Scoop, Duration = 0.24f, ArcDegrees = 90f,  Offset = 0.55f },
            ["hoe"]          = new Profile { Kind = AnimKind.Till,  Duration = 0.24f, ArcDegrees = 90f,  Offset = 0.55f },
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
        private const float MaxSwingDuration = 0.45f; // clamp so a swing can't outlast its caller's cadence

        public bool IsPlaying { get; private set; }

        private Transform _pivot;
        private SpriteRenderer _held;
        private TrailRenderer _trail;
        private SpriteRenderer _playerRenderer;
        private bool _behindPlayer; // aiming up -> tool renders behind the head
        private PlayerController _player; // for the idle pose's facing direction
        private Coroutine _routine;

        private void Awake()
        {
            _playerRenderer = GetComponent<SpriteRenderer>();
            _player = GetComponent<PlayerController>();

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
            // Idle tool tracks the (mouse-driven) facing live, not just on equip/swing.
            if (!IsPlaying && _held.enabled && _idleSprite != null)
                OrientIdleByFacing();

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
                         float arcDegrees = 0f, float duration = 0f, string kindOverride = null,
                         System.Action onContact = null)
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
            // Defensive clamp: a swing longer than its caller's cadence would be interrupted before contact.
            // No current tool/weapon violates this (verified vs items.json), so this only guards future data.
            dur = Mathf.Min(dur, MaxSwingDuration);
            if (aimDir.sqrMagnitude < 0.0001f) aimDir = Vector2.right;

            _behindPlayer = Mathf.Abs(aimDir.y) > Mathf.Abs(aimDir.x) && aimDir.y > 0f;

            _held.sprite = toolSprite;
            FitSprite(toolSprite, 1f);

            _routine = StartCoroutine(AnimateRoutine(profile, arc, dur, aimDir.normalized, onContact));
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

            _held.sprite = _idleSprite;
            FitSprite(_idleSprite, IdleScale);
            _held.transform.localPosition = new Vector3(IdleOffset, 0f, 0f);
            _held.transform.localRotation = Quaternion.Euler(0f, 0f, -SpriteArtAngle);
            _held.enabled = true;
            OrientIdleByFacing();
        }

        /// <summary>
        /// Point the at-rest tool by the player's (mouse-driven) facing: down-forward at the side
        /// (Right = base <see cref="IdleAngle"/>), mirrored when facing Left, straight down when
        /// facing Down, and up + behind the head when facing Up. Re-applied every frame in
        /// LateUpdate so the idle pose tracks facing live — not just on equip/swing-restore.
        /// </summary>
        private void OrientIdleByFacing()
        {
            float angle;
            switch (_player != null ? _player.Facing : Direction.Down)
            {
                case Direction.Right: angle = IdleAngle;          _behindPlayer = false; break; // down-right
                case Direction.Left:  angle = -180f - IdleAngle;  _behindPlayer = false; break; // mirror: down-left
                case Direction.Up:    angle = 90f;                _behindPlayer = true;  break; // up, behind head
                default:              angle = -90f;               _behindPlayer = false; break; // Down: straight down
            }
            _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
        }

        private void FitSprite(Sprite sprite, float multiplier)
        {
            float w = sprite.rect.width / sprite.pixelsPerUnit;
            float h = sprite.rect.height / sprite.pixelsPerUnit;
            float scale = Mathf.Min(1f, MaxSpriteCells / Mathf.Max(w, h)) * multiplier;
            _held.transform.localScale = new Vector3(scale, scale, 1f);
        }

        // Easing (pure math, zero-alloc). EaseOut = decelerate (wind-up settle), EaseIn = accelerate into
        // contact (peak velocity at the end), EaseOutBack = overshoot past the target then settle back.
        private static float EaseOut(float t) => 1f - (1f - t) * (1f - t);
        private static float EaseIn(float t) => t * t * t;
        private static float EaseOutBack(float t)
        {
            const float c1 = 1.70158f, c3 = c1 + 1f;
            float u = t - 1f;
            return 1f + c3 * u * u * u + c1 * u * u;
        }

        private IEnumerator AnimateRoutine(Profile profile, float arc, float duration, Vector2 aim,
                                           System.Action onContact)
        {
            IsPlaying = true;
            _held.enabled = true;
            bool fired = false; // fire onContact ONCE, at the per-Kind geometric contact frame

            float aimAngle = Mathf.Atan2(aim.y, aim.x) * Mathf.Rad2Deg;
            _held.transform.localPosition = new Vector3(profile.Offset, 0f, 0f);
            _held.transform.localRotation = Quaternion.Euler(0f, 0f, -SpriteArtAngle);

            switch (profile.Kind)
            {
                case AnimKind.Swing:
                {
                    // 3-segment swing (Phase 1a): anticipation (wind back, blend-from-current to kill the
                    // snap-pop) -> strike (accelerate to CONTACT at aimAngle, peak velocity there) -> follow-
                    // through (ease-out-back overshoot past, then settle). Contact = the strike/follow boundary
                    // by construction (Phase 1b hooks onContact there).
                    float half = arc / 2f;
                    float endA = aimAngle - half;          // natural swing end
                    float topA = aimAngle + half + half * 0.30f; // wound-up start, a bit past the natural start
                    // Blend the wind-up from the CURRENT pivot angle (fresh idle pose OR an interrupted swing).
                    float curA = _pivot.localRotation.eulerAngles.z;
                    while (curA - topA > 180f) curA -= 360f;
                    while (curA - topA < -180f) curA += 360f;

                    const float antF = 0.15f, strF = 0.50f; // follow-through = the remaining 0.35
                    _trail.Clear(); // a brief trail so the whippy down/along-aim arc reads (not a teleport)
                    _trail.time = duration;
                    _trail.emitting = true;

                    _pivot.localRotation = Quaternion.Euler(0f, 0f, curA);
                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float angle;
                        if (t < antF)
                            angle = Mathf.Lerp(curA, topA, EaseOut(t / antF));
                        else if (t < antF + strF)
                            angle = Mathf.Lerp(topA, aimAngle, EaseIn((t - antF) / strF)); // accelerate to contact
                        else
                            angle = Mathf.Lerp(aimAngle, endA, EaseOutBack((t - antF - strF) / (1f - antF - strF)));
                        // Contact = the strike/follow boundary (peak velocity at aimAngle) by construction.
                        if (!fired && t >= antF + strF) { fired = true; onContact?.Invoke(); }
                        // A forward LUNGE into the strike (drives the sword forward, then retracts) —
                        // distinguishes the sword slash from the stationary scythe sweep.
                        float lungeOff = profile.Offset;
                        if (t >= antF && t < antF + strF)
                            lungeOff = Mathf.Lerp(profile.Offset, profile.Offset + 0.2f, EaseIn((t - antF) / strF));
                        else if (t >= antF + strF)
                            lungeOff = Mathf.Lerp(profile.Offset + 0.2f, profile.Offset, EaseOut((t - antF - strF) / (1f - antF - strF)));
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
                        _held.transform.localPosition = new Vector3(lungeOff, 0f, 0f);
                        yield return null;
                    }
                    _trail.emitting = false;
                    break;
                }
                case AnimKind.Sweep:
                {
                    // Net/scythe: a SYMMETRIC even sweep — the trail must trace the whole queried sector evenly
                    // (the trail IS the honest catch area), so NO asymmetric strike/overshoot here.
                    float half = arc / 2f;
                    _pivot.localRotation = Quaternion.Euler(0f, 0f, aimAngle + half);
                    _trail.Clear(); // AFTER repositioning, or it streaks from the old spot
                    _trail.time = duration;
                    _trail.emitting = true;

                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float eased = 1f - (1f - t) * (1f - t); // ease-out, symmetric across the arc
                        float angle = Mathf.Lerp(aimAngle + half, aimAngle - half, eased);
                        // Contact = the mid-arc crossing of aimAngle (the sweep points at the target).
                        if (!fired && angle <= aimAngle) { fired = true; onContact?.Invoke(); }
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
                        yield return null;
                    }
                    _trail.emitting = false;
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
                        // Contact = the lunge apex (tip at max reach, end of the out-thrust).
                        if (!fired && elapsed >= outTime) { fired = true; onContact?.Invoke(); }
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
                    onContact?.Invoke(); // "contact" = pour-hold start (water FX cue, not an impact)
                    yield return new WaitForSeconds(duration);
                    break;
                }
                case AnimKind.Chop: // axe/pickaxe: overhead wind-up -> DOWN-strike -> impact HOLD -> recoil
                {
                    float half = arc / 2f;
                    float endA = aimAngle - half;
                    float topA = aimAngle + half + half * 0.35f; // big overhead wind-up (heavy)
                    float curA = _pivot.localRotation.eulerAngles.z;
                    while (curA - topA > 180f) curA -= 360f;
                    while (curA - topA < -180f) curA += 360f;

                    const float antF = 0.22f, strF = 0.33f, holdF = 0.28f; // recoil = 0.17
                    _trail.Clear(); _trail.time = duration; _trail.emitting = true;

                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float angle;
                        if (t < antF)
                            angle = Mathf.Lerp(curA, topA, EaseOut(t / antF));
                        else if (t < antF + strF)
                            angle = Mathf.Lerp(topA, aimAngle, EaseIn((t - antF) / strF)); // strike down to contact
                        else if (t < antF + strF + holdF)
                            angle = aimAngle;                    // impact HOLD — the chop "sticks" (motion dwell)
                        else
                            angle = Mathf.Lerp(aimAngle, endA, EaseOut((t - antF - strF - holdF) / (1f - antF - strF - holdF)));
                        if (!fired && t >= antF + strF) { fired = true; onContact?.Invoke(); }
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
                        yield return null;
                    }
                    _trail.emitting = false;
                    break;
                }
                case AnimKind.Till: // hoe: raise -> chop down into soil -> DRAG back toward the player
                {
                    float half = arc / 2f;
                    float topA = aimAngle + half + half * 0.2f;
                    float curA = _pivot.localRotation.eulerAngles.z;
                    while (curA - topA > 180f) curA -= 360f;
                    while (curA - topA < -180f) curA += 360f;

                    const float antF = 0.18f, strF = 0.32f;   // drag-back = the remaining 0.50
                    float dragTo = profile.Offset - 0.35f;
                    _trail.Clear(); _trail.time = duration; _trail.emitting = true;

                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float angle;
                        float off = profile.Offset;
                        if (t < antF)
                            angle = Mathf.Lerp(curA, topA, EaseOut(t / antF));
                        else if (t < antF + strF)
                            angle = Mathf.Lerp(topA, aimAngle, EaseIn((t - antF) / strF)); // chop down to soil
                        else
                        {
                            angle = aimAngle;                    // hold the down angle
                            off = Mathf.Lerp(profile.Offset, dragTo, EaseOut((t - antF - strF) / (1f - antF - strF))); // DRAG
                        }
                        if (!fired && t >= antF + strF) { fired = true; onContact?.Invoke(); }
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, angle);
                        _held.transform.localPosition = new Vector3(off, 0f, 0f);
                        yield return null;
                    }
                    _trail.emitting = false;
                    break;
                }
                case AnimKind.Scoop: // shovel: thrust the blade IN (scale down) -> lift up-and-back (scale up)
                {
                    float baseOff = profile.Offset;
                    float reach = baseOff + 0.45f;
                    float liftAngle = aimAngle + 55f;             // scoop up-and-back (the lever)
                    float baseScale = _held.transform.localScale.x; // uniform fit scale (depth fake — no shear)
                    _pivot.localRotation = Quaternion.Euler(0f, 0f, aimAngle);

                    const float thrustF = 0.35f, liftF = 0.40f;   // settle = 0.25
                    float elapsed = 0f;
                    while (elapsed < duration)
                    {
                        elapsed += Time.deltaTime;
                        float t = Mathf.Clamp01(elapsed / duration);
                        float off, ang, sc;
                        if (t < thrustF)
                        {
                            float u = t / thrustF;
                            off = Mathf.Lerp(baseOff, reach, EaseIn(u)); // thrust the blade in along aim
                            sc = Mathf.Lerp(1f, 0.9f, u);                // smaller = into the ground
                            ang = aimAngle;
                        }
                        else if (t < thrustF + liftF)
                        {
                            float u = (t - thrustF) / liftF;
                            off = Mathf.Lerp(reach, baseOff, EaseOut(u)); // pull back
                            sc = Mathf.Lerp(0.9f, 1.1f, u);              // larger = lifted toward the viewer
                            ang = Mathf.Lerp(aimAngle, liftAngle, EaseOut(u)); // rotate the head up-and-back
                        }
                        else
                        {
                            float u = (t - thrustF - liftF) / (1f - thrustF - liftF);
                            off = baseOff;
                            sc = Mathf.Lerp(1.1f, 1f, u);
                            ang = Mathf.Lerp(liftAngle, aimAngle, u);
                        }
                        if (!fired && t >= thrustF) { fired = true; onContact?.Invoke(); } // contact = the bite
                        _pivot.localRotation = Quaternion.Euler(0f, 0f, ang);
                        _held.transform.localPosition = new Vector3(off, 0f, 0f);
                        _held.transform.localScale = new Vector3(baseScale * sc, baseScale * sc, 1f);
                        yield return null;
                    }
                    break;
                }
            }

            IsPlaying = false;
            _routine = null;
            RestoreIdle(); // back to the held-at-rest pose (or hidden when nothing equipped)
        }
    }
}
