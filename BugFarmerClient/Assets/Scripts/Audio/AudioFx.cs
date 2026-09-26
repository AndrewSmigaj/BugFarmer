using UnityEngine;

namespace BugFarmer.Audio
{
    /// <summary>
    /// The game's FIRST audio: tiny runtime-SYNTHESIZED clips (zero assets — the
    /// WaterDroplet generated-sprite convention applied to sound). Non-streaming
    /// AudioClip.Create + one SetData at boot (the streaming PCM callback doesn't work
    /// on WebGL); sample rate from AudioSettings.outputSampleRate (hardcoding 44100
    /// pitch-shifts on 48k devices). 6 pooled AudioSources on a DontDestroyOnLoad
    /// singleton; ±10% pitch jitter via source.pitch, never resampling.
    ///
    /// Clips: THWACK (bug hit — mirrors the hit-flash dedup: optimistic for self,
    /// !ownEcho for remotes), POP (kill — played UNCONDITIONALLY from MeleeResult's
    /// killed[]: there is no optimistic kill, so no double; NEVER hooked to BUG_REMOVED
    /// ledger application, which catches also ride and late-join replay would storm),
    /// STING + THUD (player hurt/faint), HISS (centipede windup), CRUNCH (gnaw loop —
    /// audible radius LARGER than the night light radius: the night tell).
    /// </summary>
    public class AudioFx : MonoBehaviour
    {
        public static AudioFx Instance { get; private set; }

        private AudioClip _thwack, _pop, _sting, _thud, _hiss, _crunch, _thunder, _chop;
        private AudioSource[] _pool;
        private int _next;

        /// <summary>Idempotent bootstrap (call from any Start; survives scene loads).</summary>
        public static void Ensure()
        {
            if (Instance != null) return;
            var go = new GameObject("AudioFx");
            DontDestroyOnLoad(go);
            Instance = go.AddComponent<AudioFx>();
        }

        private void Awake()
        {
            Instance = this;
            int sr = AudioSettings.outputSampleRate;
            if (sr <= 0) sr = 44100;

            _thwack = Synth("fx_thwack", sr, 0.07f, (t, dur) =>
                Noise(t) * Decay(t, dur, 18f) * 0.7f);
            _pop = Synth("fx_pop", sr, 0.09f, (t, dur) =>
                Mathf.Sin(2f * Mathf.PI * Mathf.Lerp(700f, 180f, t / dur) * t) * Decay(t, dur, 14f) * 0.6f);
            _sting = Synth("fx_sting", sr, 0.12f, (t, dur) =>
                (Mathf.Sin(2f * Mathf.PI * 900f * t) * 0.5f + Noise(t) * 0.5f) * Decay(t, dur, 12f) * 0.6f);
            _thud = Synth("fx_thud", sr, 0.25f, (t, dur) =>
                Mathf.Sin(2f * Mathf.PI * Mathf.Lerp(140f, 50f, t / dur) * t) * Decay(t, dur, 8f) * 0.9f);
            _hiss = Synth("fx_hiss", sr, 0.35f, (t, dur) =>
                Noise(t) * Mathf.Lerp(0.15f, 0.55f, t / dur) * Decay(t, dur, 3f));
            _crunch = Synth("fx_crunch", sr, 0.18f, (t, dur) =>
                Noise(t) * (Mathf.PingPong(t * 30f, 1f) > 0.5f ? 1f : 0.25f) * Decay(t, dur, 6f) * 0.65f);
            // AXE CHOP: a woody "thock" — a low body sweep (~220→90 Hz) + a sharp noise blade transient,
            // fast attack, fast decay.
            _chop = Synth("fx_chop", sr, 0.14f, (t, dur) =>
            {
                float body = Mathf.Sin(2f * Mathf.PI * Mathf.Lerp(220f, 90f, t / dur) * t);
                float blade = Noise(t) * Decay(t, dur, 30f) * 0.5f;       // sharp transient at the strike
                float env = Decay(t, dur, 11f) * Mathf.Min(1f, t / 0.005f); // fast attack
                return (body * 0.6f + blade) * env * 0.8f;
            });
            // THUNDER (heavy-rain lightning): a low boom sweep + amplitude-wobbled rumble noise,
            // quick attack and a long decaying tail. Long enough to feel distant after the flash.
            _thunder = Synth("fx_thunder", sr, 1.4f, (t, dur) =>
            {
                float boom = Mathf.Sin(2f * Mathf.PI * Mathf.Lerp(70f, 38f, t / dur) * t);
                float rumble = Noise(t) * (0.5f + 0.5f * Mathf.Sin(2f * Mathf.PI * 7f * t));
                float env = Decay(t, dur, 4.5f) * Mathf.Min(1f, t / 0.04f); // fast attack, long tail
                return (boom * 0.55f + rumble * 0.55f) * env * 0.9f;
            });

            _pool = new AudioSource[6];
            for (int i = 0; i < _pool.Length; i++)
            {
                _pool[i] = gameObject.AddComponent<AudioSource>();
                _pool[i].playOnAwake = false;
                _pool[i].spatialBlend = 0f; // 2D; distance gating is done by callers
            }
        }

        // --- public one-shots (distance-gated where it matters) ---

        public static void BugHit() => Instance?.Play(Instance._thwack, 0.8f);
        public static void BugKill() => Instance?.Play(Instance._pop, 0.9f);
        public static void PlayerSting() => Instance?.Play(Instance._sting, 1.0f);
        public static void PlayerFaint() => Instance?.Play(Instance._thud, 1.0f);
        public static void Thunder() => Instance?.Play(Instance._thunder, 0.9f);

        /// <summary>Positional one-shots: volume falls off with distance to the local
        /// player; audibleRadius > the night light radius makes sound the night tell.</summary>
        public static void HissAt(Vector2 worldPos) => Instance?.PlayAt(Instance._hiss, worldPos, 12f, 0.9f);
        public static void CrunchAt(Vector2 worldPos) => Instance?.PlayAt(Instance._crunch, worldPos, 14f, 0.9f);
        public static void ThwackAt(Vector2 worldPos) => Instance?.PlayAt(Instance._thwack, worldPos, 10f, 0.8f);
        public static void AxeChopAt(Vector2 worldPos) => Instance?.PlayAt(Instance._chop, worldPos, 12f, 0.85f);

        private void Play(AudioClip clip, float volume)
        {
            if (clip == null) return;
            var src = _pool[_next];
            _next = (_next + 1) % _pool.Length;
            src.pitch = Random.Range(0.9f, 1.1f);
            src.PlayOneShot(clip, volume);
        }

        private void PlayAt(AudioClip clip, Vector2 worldPos, float audibleRadius, float volume)
        {
            var cam = Camera.main;
            Vector2 ear = cam != null ? (Vector2)cam.transform.position : Vector2.zero;
            float dist = Vector2.Distance(ear, worldPos);
            if (dist > audibleRadius) return;
            Play(clip, volume * (1f - dist / audibleRadius));
        }

        // --- synthesis helpers ---

        private static AudioClip Synth(string name, int sampleRate, float seconds,
            System.Func<float, float, float> wave)
        {
            int n = Mathf.CeilToInt(sampleRate * seconds);
            var data = new float[n];
            for (int i = 0; i < n; i++)
            {
                float t = (float)i / sampleRate;
                data[i] = Mathf.Clamp(wave(t, seconds), -1f, 1f);
            }
            var clip = AudioClip.Create(name, n, 1, sampleRate, false);
            clip.SetData(data, 0);
            return clip;
        }

        private static float Decay(float t, float dur, float k) =>
            Mathf.Exp(-k * t / dur);

        private static uint _noiseState = 0x12345678;
        private static float Noise(float _)
        {
            // xorshift — fast, allocation-free white noise (seeded once; audio only)
            _noiseState ^= _noiseState << 13;
            _noiseState ^= _noiseState >> 17;
            _noiseState ^= _noiseState << 5;
            return ((_noiseState & 0xFFFF) / 32768f) - 1f;
        }
    }
}
