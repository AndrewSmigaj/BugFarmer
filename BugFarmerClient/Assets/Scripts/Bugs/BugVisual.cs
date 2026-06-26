using UnityEngine;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Pairs a BugAgent with its visual Transform for rendering.
    /// Handles position capture and interpolation for smooth 60fps display
    /// while simulation runs at 10Hz.
    /// </summary>
    public class BugVisual
    {
        /// <summary>
        /// The deterministic bug simulation agent.
        /// </summary>
        public BugAgent Agent;

        /// <summary>
        /// Transform of the visual GameObject (sprite).
        /// </summary>
        public Transform Transform;

        /// <summary>
        /// Cached SpriteRenderer for Y-sorting.
        /// </summary>
        public SpriteRenderer Renderer;

        /// <summary>
        /// Position at the start of current tick (for interpolation).
        /// </summary>
        public Vector2 PrevPos;

        /// <summary>
        /// Position at the end of current tick (for interpolation).
        /// </summary>
        public Vector2 CurrPos;

        /// <summary>
        /// DISPLAY ONLY — never read by the deterministic sim or the state hash.
        /// Authoritative HP lives server-side in SwarmState.BugHP; this copy is fed by
        /// MeleeResultMessage (OpCode 89) and the late-join snapshot seed. -1 = full HP.
        /// Living on the BugVisual means it rides split/merge bug-moves for free.
        /// </summary>
        public int DisplayHP = -1;

        /// <summary>Hit-flash end time (Time.time); cosmetic only.</summary>
        public float FlashUntil;

        /// <summary>
        /// Cosmetic flap-animation frames (set by SwarmVisual; null = static sprite). DISPLAY-ONLY —
        /// the shown frame + the float offset are never part of the deterministic sim or state hash,
        /// so they can run free of the 10Hz tick and even differ per client without breaking sync.
        /// Real-butterfly feel: flap in short bursts, then GLIDE (hold wings-open frame 0) between bursts.
        /// </summary>
        public Sprite[] Frames;
        private float _animTime = -1f; // <0 = uninitialised; seeded per-bug on first frame
        // Per-species cosmetic flap profile (display-only). Defaults = the graceful butterfly
        // flap-then-glide; SwarmVisual overrides these for fast continuous buzzers (flies).
        public float FlapFps = 11f;      // frames/sec while flapping
        public int FlapsPerBurst = 2;    // wing cycles per flap burst
        public float GlideSecs = 0.5f;   // hold wings-open between bursts (0 = continuous, no glide)
        public float BobAmp = 0.05f;     // gentle vertical float (world units)
        public float BobHz = 2.2f;       // floats per second

        private static readonly Color DamagedTint = new Color(1f, 0.6f, 0.6f, 1f);
        private static readonly Color FlashTint = new Color(1f, 0.25f, 0.25f, 1f);

        public BugVisual(BugAgent agent, Transform transform)
        {
            Agent = agent;
            Transform = transform;
            Renderer = transform?.GetComponent<SpriteRenderer>();
            CurrPos = agent.Position.ToVector2();
            PrevPos = CurrPos;
        }

        /// <summary>
        /// Capture current position as previous before simulating next tick.
        /// Call this before SimulateTick(). CurrPos will be updated in Interpolate()
        /// after simulation has run.
        /// </summary>
        public void CapturePosition()
        {
            PrevPos = CurrPos;
            // Don't update CurrPos here - it will be updated in Interpolate()
            // after SimulateTick() has changed Agent.Position
        }

        /// <summary>
        /// Interpolate visual position between PrevPos and CurrPos.
        /// Updates CurrPos from Agent.Position (which was changed by SimulateTick).
        /// Also updates sorting order for Y-sorting (bugs in front of lower objects).
        /// </summary>
        /// <param name="t">Interpolation factor 0-1 (time within current tick)</param>
        public void Interpolate(float t)
        {
            // Update CurrPos from agent's current position (after SimulateTick)
            CurrPos = Agent.Position.ToVector2();

            if (Transform != null)
            {
                Vector2 pos = Vector2.Lerp(PrevPos, CurrPos, t);

                // Cosmetic flap animation + vertical float (display-only; never hashed).
                float bobY = 0f;
                if (Frames != null && Renderer != null && Frames.Length >= 2)
                {
                    if (_animTime < 0f)
                    {
                        // per-bug phase offset so the swarm doesn't flap in unison (golden-ratio spread)
                        _animTime = ((Agent.BugId * 0.61803399f) % 1f) * 3f;
                    }
                    _animTime += Time.deltaTime;

                    int n = Frames.Length;
                    float burst = FlapsPerBurst * n / FlapFps; // seconds of flapping per burst
                    float period = burst + GlideSecs;          // burst + glide
                    float m = _animTime % period;
                    int idx = m < burst ? Mathf.FloorToInt(m * FlapFps) % n : 0; // glide holds frame 0 (wings open)
                    var frame = Frames[idx];
                    if (Renderer.sprite != frame) Renderer.sprite = frame;

                    bobY = Mathf.Sin(_animTime * BobHz * 6.2831853f) * BobAmp;
                }

                Transform.position = new Vector3(pos.x, pos.y + bobY, Transform.position.z);

                // Y-sorting uses the SIM y (not the cosmetic float) to avoid sort flicker.
                if (Renderer != null)
                {
                    Renderer.sortingOrder = -Mathf.FloorToInt(pos.y) + 1;
                    UpdateTint();
                }
            }
        }

        /// <summary>
        /// Combat display tint: brief flash on hit, persistent light-red while damaged
        /// (DisplayHP set), white otherwise. Pure cosmetics over the display HP copy.
        /// </summary>
        private void UpdateTint()
        {
            Renderer.color = Time.time < FlashUntil
                ? FlashTint
                : (DisplayHP > 0 ? DamagedTint : Color.white);
        }

        /// <summary>
        /// Sync visual position directly to agent position (no interpolation).
        /// Use when spawning or after catching up multiple ticks.
        /// </summary>
        public void SyncPosition()
        {
            CurrPos = Agent.Position.ToVector2();
            PrevPos = CurrPos;
            if (Transform != null)
            {
                Transform.position = CurrPos;

                // Update sorting order to match position
                if (Renderer != null)
                {
                    Renderer.sortingOrder = -Mathf.FloorToInt(CurrPos.y) + 1;
                }
            }
        }
    }
}
