using UnityEngine;

namespace BugFarmer.Player
{
    /// <summary>
    /// Smooth camera follow for 2D top-down view.
    /// Attach to Main Camera.
    /// </summary>
    public class CameraFollow : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private float smoothTime = 0.15f; // Time to reach target
        [SerializeField] private float zOffset = -10f;

        [Header("Shake (hit feedback)")]
        [Tooltip("Peak shake offset in world units at full trauma. Kept small/cozy.")]
        [SerializeField] private float maxShake = 0.2f;
        [SerializeField] private float shakeFrequency = 22f;
        [Tooltip("Trauma units shed per second (higher = snappier settle).")]
        [SerializeField] private float traumaDecay = 3.5f;

        private Vector3 _velocity;
        private Vector3 _basePos;   // smoothed follow position WITHOUT shake (so shake never feeds back)
        private bool _haveBase;
        private float _trauma;      // 0..1, decays each frame
        private float _shakeSeed;

        private static CameraFollow _instance;

        private void Awake()
        {
            _instance = this;
            _shakeSeed = Mathf.Repeat(GetInstanceID() * 0.123f, 100f); // stable per-camera noise offset
        }

        /// <summary>Add camera trauma (0..1) — call on a hit for a small kick. Decays automatically.</summary>
        public static void AddShake(float amount)
        {
            if (_instance != null) _instance._trauma = Mathf.Clamp01(_instance._trauma + amount);
        }

        private void LateUpdate()
        {
            if (target == null)
                return;

            Vector3 targetPos = new Vector3(target.position.x, target.position.y, zOffset);
            if (!_haveBase) { _basePos = transform.position; _haveBase = true; }
            _basePos = Vector3.SmoothDamp(_basePos, targetPos, ref _velocity, smoothTime);

            Vector3 shake = Vector3.zero;
            if (_trauma > 0f)
            {
                float s = _trauma * _trauma;                 // quadratic falloff (punchy → settle)
                float t = Time.time * shakeFrequency;
                shake.x = (Mathf.PerlinNoise(_shakeSeed, t) - 0.5f) * 2f * maxShake * s;
                shake.y = (Mathf.PerlinNoise(_shakeSeed + 11.3f, t) - 0.5f) * 2f * maxShake * s;
                _trauma = Mathf.Max(0f, _trauma - Time.deltaTime * traumaDecay);
            }

            transform.position = _basePos + shake;
        }

        /// <summary>
        /// Set the follow target at runtime.
        /// </summary>
        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
        }

        /// <summary>
        /// Instantly snap camera to target position.
        /// </summary>
        public void SnapToTarget()
        {
            if (target != null)
            {
                _basePos = new Vector3(target.position.x, target.position.y, zOffset);
                _haveBase = true;
                _velocity = Vector3.zero;
                transform.position = _basePos;
            }
        }
    }
}
