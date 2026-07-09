using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// A brief per-hit BEND on a single sprite — the struck tree snaps in the hit direction and wobbles back
    /// (a damped spring: amp·e^(-k·t)·cos(ω·t)), via a per-renderer MaterialPropertyBlock (`_HitBend` on
    /// BugFarmer/SpriteLitWorld). It's applied base-anchored like the wind (scaled by uv.y), so the trunk
    /// stays planted and the canopy swings. Coexists with <see cref="HitFlash"/>: both Get→set-only-their-prop
    /// →Set and neither nulls the block, so they don't wipe each other. Cosmetic, client-local, zero sim surface.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class HitWobble : MonoBehaviour
    {
        private static readonly int HitBendId = Shader.PropertyToID("_HitBend");

        [Tooltip("Total wobble time (seconds).")]
        public float Duration = 0.35f;
        [Tooltip("Oscillation rate (rad/s) — a couple of swings over the duration.")]
        public float Frequency = 28f;
        [Tooltip("Envelope decay — higher settles faster.")]
        public float Decay = 9f;

        private SpriteRenderer _sr;
        private MaterialPropertyBlock _mpb;
        private float _amp;      // signed initial bend (sign = direction)
        private float _t = -1f;  // <0 = idle

        private void Awake()
        {
            _sr = GetComponent<SpriteRenderer>();
            _mpb = new MaterialPropertyBlock();
        }

        /// <summary>Bend sprite <paramref name="sr"/> now by <paramref name="amp"/> (signed = direction, world
        /// units at the canopy), adding the component on first use.</summary>
        public static void Play(SpriteRenderer sr, float amp)
        {
            if (sr == null) return;
            var hw = sr.GetComponent<HitWobble>();
            if (hw == null) hw = sr.gameObject.AddComponent<HitWobble>();
            hw._amp = amp;
            hw._t = 0f;
            hw.Apply(amp);   // snap to the bend immediately on the hit
        }

        private void Update()
        {
            if (_t < 0f) return;
            _t += Time.deltaTime;
            float env = Mathf.Exp(-Decay * _t);
            if (_t >= Duration || env < 0.02f)
            {
                _t = -1f;
                Apply(0f);   // reset _HitBend to 0 — do NOT null the block (HitFlash may be active on this sprite)
                return;
            }
            Apply(_amp * env * Mathf.Cos(Frequency * _t));
        }

        private void Apply(float bend)
        {
            if (_sr == null) return;
            _sr.GetPropertyBlock(_mpb);   // preserve HitFlash's _FlashAmount / _FlashColor
            _mpb.SetFloat(HitBendId, bend);
            _sr.SetPropertyBlock(_mpb);
        }
    }
}
