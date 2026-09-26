using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// A brief lerp-to-color hit-flash on a SINGLE sprite, driven through a MaterialPropertyBlock
    /// (`_FlashAmount`/`_FlashColor` on the BugFarmer/SpriteLitWorld shader). Because it's a per-renderer
    /// property block, only the struck sprite flashes and no other sprite's batching is affected (the
    /// flashing renderer itself drops out of the SRP batch for ~0.12s, then the block is cleared to rejoin).
    /// Lazily added to the hit target and idles at 0 — pool-safe: a reused sprite at amount 0 shows nothing.
    /// Cosmetic, client-local, zero sim/determinism surface.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class HitFlash : MonoBehaviour
    {
        private static readonly int FlashAmountId = Shader.PropertyToID("_FlashAmount");
        private static readonly int FlashColorId = Shader.PropertyToID("_FlashColor");

        [Tooltip("Seconds for the flash to decay to 0.")]
        public float Duration = 0.08f;
        public Color Color = Color.white;

        private SpriteRenderer _sr;
        private MaterialPropertyBlock _mpb;
        private float _amount;

        private void Awake()
        {
            _sr = GetComponent<SpriteRenderer>();
            _mpb = new MaterialPropertyBlock();
        }

        /// <summary>Flash sprite <paramref name="sr"/> now, adding the component on first use.</summary>
        public static void Play(SpriteRenderer sr, float amount = 1f, Color? color = null)
        {
            if (sr == null) return;
            var hf = sr.GetComponent<HitFlash>();
            if (hf == null) hf = sr.gameObject.AddComponent<HitFlash>();
            if (color.HasValue) hf.Color = color.Value;
            hf._amount = Mathf.Clamp01(amount);
            hf.Apply();
        }

        /// <summary>Clear any active flash on a (pooled) sprite.</summary>
        public static void Clear(SpriteRenderer sr)
        {
            var hf = sr != null ? sr.GetComponent<HitFlash>() : null;
            if (hf != null && hf._amount > 0f)
            {
                hf._amount = 0f;
                hf.Apply();
            }
        }

        private void Update()
        {
            if (_amount <= 0f) return;
            _amount -= Time.deltaTime / Mathf.Max(0.01f, Duration);
            if (_amount <= 0f)
            {
                _amount = 0f;
                // Reset _FlashAmount to 0 via the block (do NOT SetPropertyBlock(null)) — nulling would also
                // wipe a concurrent HitWobble's _HitBend and cut the wobble short.
                Apply();
                return;
            }
            Apply();
        }

        private void Apply()
        {
            if (_sr == null) return;
            _sr.GetPropertyBlock(_mpb);      // preserve any other per-renderer overrides
            _mpb.SetFloat(FlashAmountId, _amount);
            _mpb.SetColor(FlashColorId, Color);
            _sr.SetPropertyBlock(_mpb);
        }
    }
}
