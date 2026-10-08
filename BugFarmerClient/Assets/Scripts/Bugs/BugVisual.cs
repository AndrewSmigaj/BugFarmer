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

        // #20 strike lunge (display-only): a quick out-and-back JAB toward the victim when this member
        // snatches its prey, so the kill reads as a committed lunge. Set by SwarmVisual.LungeNearest;
        // decays over LungeDur via a sin envelope. Never read by the sim or the state hash.
        public float LungeStart = -1f;
        public float LungeDur;
        public Vector2 LungeVec;

        /// <summary>
        /// Cosmetic flap-animation frames (set by SwarmVisual; null = static sprite). DISPLAY-ONLY —
        /// the shown frame + the float offset are never part of the deterministic sim or state hash,
        /// so they can run free of the 10Hz tick and even differ per client without breaking sync.
        /// Real-butterfly feel: flap in short bursts, then GLIDE (hold wings-open frame 0) between bursts.
        /// </summary>
        public Sprite[] Frames;
        // The flap/float phase: a per-bug offset added to the clock (Stage 1.2: the clock instead of a timer advanced
        // only while the bug is drawn, so a bug out of view keeps its phase and its drawn position can be worked out
        // without drawing it). Golden-ratio spread so a swarm doesn't flap in unison.
        private readonly float _animPhase;
        // Per-species cosmetic flap profile (display-only). Defaults = the graceful butterfly
        // flap-then-glide; SwarmVisual overrides these for fast continuous buzzers (flies).
        public float FlapFps = 11f;      // frames/sec while flapping
        public int FlapsPerBurst = 2;    // wing cycles per flap burst
        public float GlideSecs = 0.5f;   // hold wings-open between bursts (0 = continuous, no glide)
        public float BobAmp = 0.05f;     // gentle vertical float (world units)
        public float BobHz = 2.2f;       // floats per second

        private static readonly Color DamagedTint = new Color(1f, 0.6f, 0.6f, 1f);
        private static readonly Color FlashTint = new Color(1f, 0.25f, 0.25f, 1f);

        // The two positions the last drawn frame blended between (Stage 1.2): kept at each tick for every bug, drawn or
        // not, so DrawnPosition can say where the bug is drawn — or would be — without its sprite.
        private Vector2 _drawFrom, _drawTo;
        private int _capturedAtFrame = int.MinValue;   // the drawing frame number at the last capture
        // The renderer's last written values, so a frame writes only what changed (Stage 1.2). Unknown at first.
        private int _sortingOrder = int.MinValue;
        private int _tint = -1;                        // 0 plain, 1 damaged, 2 flash
        private int _frameIdx = -1;
        private readonly float _z;

        public BugVisual(BugAgent agent, Transform transform)
        {
            Agent = agent;
            Transform = transform;
            Renderer = transform?.GetComponent<SpriteRenderer>();
            CurrPos = agent.Position.ToVector2();
            PrevPos = CurrPos;
            _drawFrom = _drawTo = CurrPos;
            _z = transform != null ? transform.position.z : 0f;
            _animPhase = ((agent.BugId * 0.61803399f) % 1f) * 3f;
        }

        /// <summary>
        /// Capture current position as previous before simulating next tick. CurrPos is what the last drawing frame
        /// blended to — the bug's position at that frame — so if a frame has passed since the last capture it is refreshed
        /// here from the agent (unchanged since that frame), whether or not the frame drew this bug; within a batch of
        /// ticks with no frame between them it stays, as before. <paramref name="drawFrame"/> = SwarmManager.DrawFrame.
        /// </summary>
        public void CapturePosition(int drawFrame)
        {
            if (drawFrame != _capturedAtFrame)
            {
                CurrPos = Agent.Position.ToVector2();
                _drawFrom = PrevPos;   // the last frame drew between these two
                _drawTo = CurrPos;
                _capturedAtFrame = drawFrame;
            }
            PrevPos = CurrPos;
        }

        /// <summary>
        /// Where the bug is drawn at blend fraction <paramref name="t"/> and time <paramref name="now"/>: the blend between
        /// the positions the last drawn frame used, plus the strike jab and the float. With the last frame's t and time it
        /// is where the sprite was put — or would have been, for a bug out of view (Stage 1.2). Display only: it feeds the
        /// computer-in-charge's sting reports and cosmetic picks, never the simulation or its hash.
        /// </summary>
        public Vector2 DrawnPosition(float t, float now)
        {
            Vector2 pos = Vector2.Lerp(_drawFrom, _drawTo, t) + JabOffset(now);
            if (Frames != null && Renderer != null && Frames.Length >= 2) pos.y += BobOffset(now);   // as Interpolate
            return pos;
        }

        // #20 strike lunge: a quick out-and-back jab toward the victim (display-only; sin envelope peaks at mid-window).
        private Vector2 JabOffset(float now)
        {
            if (LungeStart < 0f) return Vector2.zero;
            float le = now - LungeStart;
            return le >= 0f && le < LungeDur ? LungeVec * Mathf.Sin(Mathf.PI * le / LungeDur) : Vector2.zero;
        }

        private float BobOffset(float now) => Mathf.Sin((_animPhase + now) * BobHz * 6.2831853f) * BobAmp;

        /// <summary>
        /// Interpolate visual position between PrevPos and CurrPos.
        /// Updates CurrPos from Agent.Position (which was changed by SimulateTick).
        /// Also updates sorting order for Y-sorting (bugs in front of lower objects).
        /// </summary>
        /// <param name="t">Interpolation factor 0-1 (time within current tick)</param>
        /// <param name="now">Time.time for this frame (one read per frame, by the caller)</param>
        public void Interpolate(float t, float now)
        {
            // Update CurrPos from agent's current position (after SimulateTick)
            CurrPos = Agent.Position.ToVector2();

            if (Transform != null)
            {
                // The strike jab is added before the flap/bob so the whole sprite jabs.
                Vector2 pos = Vector2.Lerp(PrevPos, CurrPos, t) + JabOffset(now);

                // Cosmetic flap animation + vertical float (display-only; never hashed).
                float bobY = 0f;
                if (Frames != null && Renderer != null && Frames.Length >= 2)
                {
                    int n = Frames.Length;
                    float burst = FlapsPerBurst * n / FlapFps; // seconds of flapping per burst
                    float period = burst + GlideSecs;          // burst + glide
                    float m = (_animPhase + now) % period;
                    int idx = m < burst ? Mathf.FloorToInt(m * FlapFps) % n : 0; // glide holds frame 0 (wings open)
                    if (idx != _frameIdx) { _frameIdx = idx; Renderer.sprite = Frames[idx]; }
                    bobY = BobOffset(now);
                }

                Transform.position = new Vector3(pos.x, pos.y + bobY, _z);

                // Y-sorting uses the SIM y (not the cosmetic float) to avoid sort flicker.
                if (Renderer != null)
                {
                    int order = -Mathf.FloorToInt(pos.y) + 1;
                    if (order != _sortingOrder) { _sortingOrder = order; Renderer.sortingOrder = order; }
                    UpdateTint(now);
                }
            }
        }

        /// <summary>
        /// Combat display tint: brief flash on hit, persistent light-red while damaged
        /// (DisplayHP set), white otherwise. Pure cosmetics over the display HP copy. Written only when it changes.
        /// </summary>
        private void UpdateTint(float now)
        {
            int tint = now < FlashUntil ? 2 : (DisplayHP > 0 ? 1 : 0);
            if (tint == _tint) return;
            _tint = tint;
            Renderer.color = tint == 2 ? FlashTint : (tint == 1 ? DamagedTint : Color.white);
        }

        /// <summary>
        /// Sync visual position directly to agent position (no interpolation).
        /// Use when spawning or after catching up multiple ticks.
        /// </summary>
        public void SyncPosition()
        {
            CurrPos = Agent.Position.ToVector2();
            PrevPos = CurrPos;
            _drawFrom = _drawTo = CurrPos;
            if (Transform != null)
            {
                Transform.position = CurrPos;

                // Update sorting order to match position
                if (Renderer != null)
                {
                    _sortingOrder = -Mathf.FloorToInt(CurrPos.y) + 1;
                    Renderer.sortingOrder = _sortingOrder;
                }
            }
        }
    }
}
