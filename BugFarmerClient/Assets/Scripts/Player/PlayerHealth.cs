using System.Collections;
using Nakama;
using UnityEngine;
using BugFarmer.Networking;

namespace BugFarmer.Player
{
    /// <summary>
    /// Player HP v1 (predators slice): hearts UI + knockback + red flash + faint, all
    /// driven by the presence-TARGETED PlayerDamage message (OpCode 94 — the server
    /// sends it only to the victim, so no remote-player filtering is needed; a guard
    /// stays anyway). HP is sim-inert display state: bug AI reads player CELLS via the
    /// ledger. The client is movement-authoritative, so the FAINT teleport is applied
    /// HERE (transform snap to the respawn point) — the server already moved its copy.
    /// Regen (+1/30s, damage-gated) arrives as damage-0 echoes; a join-time echo seeds
    /// the bar. Added to the player GameObject by PlayerController's bootstrap.
    /// </summary>
    public class PlayerHealth : MonoBehaviour
    {
        public static int HP { get; private set; } = 10;
        public static int MaxHP { get; private set; } = 10;

        [SerializeField] private float knockbackDistance = 1.2f;
        [SerializeField] private float knockbackSeconds = 0.12f;

        private float _redFlashUntil;
        private float _invulnBlinkUntil;
        private float _faintFadeUntil;
        private SpriteRenderer _sprite;

        private float _firstDamageToastUntil;
        private static bool _everDamaged;

        private PlayerController _controller; // dodge i-frames drive a distinct blink (this is the sole color owner)

        private void Start()
        {
            _sprite = GetComponent<SpriteRenderer>();
            _controller = GetComponent<PlayerController>();
            BugFarmer.Audio.AudioFx.Ensure(); // the audio singleton boots with the player
            if (WorldManager.Instance != null)
                WorldManager.Instance.OnMatchData += HandleMatchData;
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
                WorldManager.Instance.OnMatchData -= HandleMatchData;
        }

        private void HandleMatchData(IMatchState state)
        {
            if (state.OpCode != OpCodes.PlayerDamage) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<PlayerDamageMessage>(json);
            if (msg == null) return;

            HP = msg.hp;
            MaxHP = msg.max_hp;

            if (msg.faint)
            {
                // Movement-authoritative client snaps ITSELF; the next Movement message
                // confirms the new position to the server.
                transform.position = new Vector3(msg.respawn_x, msg.respawn_y, transform.position.z);
                _faintFadeUntil = Time.time + 1.5f;
                BugFarmer.Audio.AudioFx.PlayerFaint();
                return;
            }

            if (msg.damage > 0)
            {
                _redFlashUntil = Time.time + 0.2f;
                _invulnBlinkUntil = Time.time + 1.0f;
                BugFarmer.Audio.AudioFx.PlayerSting();
                if (!_everDamaged)
                {
                    // The one-time onboarding line: nothing else ever names the sword.
                    _everDamaged = true;
                    _firstDamageToastUntil = Time.time + 6f;
                }
                StopAllCoroutines();
                StartCoroutine(Knockback(new Vector2(msg.knock_dx, msg.knock_dy)));
            }
        }

        private IEnumerator Knockback(Vector2 dir)
        {
            float t = 0f;
            while (t < knockbackSeconds)
            {
                float dt = Time.deltaTime;
                t += dt;
                transform.position += (Vector3)(dir * (knockbackDistance * dt / knockbackSeconds));
                yield return null;
            }
        }

        private void Update()
        {
            if (_sprite == null) return;

            // Dodge i-frames take visual priority: a fast bright/translucent blink reads as "invincible" and
            // is distinct from the post-hit red flash. The i-frames themselves are enforced server-side.
            if (_controller != null && _controller.IsDodgeInvulnerable)
            {
                _sprite.color = (Mathf.FloorToInt(Time.time * 24f) % 2 == 0)
                    ? new Color(0.7f, 0.9f, 1f, 0.5f) : new Color(1f, 1f, 1f, 0.85f);
            }
            else if (Time.time < _redFlashUntil)
                _sprite.color = new Color(1f, 0.45f, 0.45f);
            else if (Time.time < _invulnBlinkUntil)
                _sprite.color = (Mathf.FloorToInt(Time.time * 10f) % 2 == 0)
                    ? new Color(1f, 1f, 1f, 0.55f) : Color.white;
            else
                _sprite.color = Color.white;
        }

        private void OnGUI()
        {
            // Hearts, top-left (the clock's OnGUI convention). ♥ full / ♡ empty, halves
            // skipped v1 (all damage is whole numbers).
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < MaxHP; i++)
                sb.Append(i < HP ? "♥" : "♡");
            var style = new GUIStyle(GUI.skin.label) { fontSize = 16 };
            style.normal.textColor = new Color(0.95f, 0.3f, 0.35f);
            GUI.Label(new Rect(12, 8, 400, 24), sb.ToString(), style);

            if (Time.time < _firstDamageToastUntil)
            {
                var hint = new GUIStyle(GUI.skin.label) { fontSize = 13 };
                hint.normal.textColor = Color.white;
                GUI.Label(new Rect(12, 30, 520, 22),
                    "Ouch — a sting! Your sword (hotbar) swings with left-click.", hint);
            }

            // Faint fade-to-black
            if (Time.time < _faintFadeUntil)
            {
                float a = Mathf.Clamp01((_faintFadeUntil - Time.time) / 1.5f);
                var prev = GUI.color;
                GUI.color = new Color(0f, 0f, 0f, a * 0.9f);
                GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), Texture2D.whiteTexture);
                GUI.color = prev;
            }
        }
    }
}
