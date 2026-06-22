using System.Threading.Tasks;
using UnityEngine;

namespace BugFarmer.UI
{
    /// <summary>
    /// A self-bootstrapping full-screen black fade (OnGUI quad, like IntroOverlay) used to HIDE the
    /// cross-zone swap: FadeOut() before leaving, FadeIn() after the player snaps into the neighbor.
    /// Awaitable; alpha is lerped with unscaled time so it works regardless of timeScale.
    /// </summary>
    public class ScreenFade : MonoBehaviour
    {
        private static ScreenFade _instance;
        private float _alpha;
        private float _target;
        private const float Speed = 4f; // ~0.25s per direction

        public static ScreenFade Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("ScreenFade(Code)");
                    DontDestroyOnLoad(go);
                    _instance = go.AddComponent<ScreenFade>();
                }
                return _instance;
            }
        }

        private void Update()
        {
            _alpha = Mathf.MoveTowards(_alpha, _target, Speed * Time.unscaledDeltaTime);
        }

        /// <summary>Fade to opaque black; completes when fully covered.</summary>
        public async Task FadeOut() { _target = 1f; await WaitForAlpha(1f); }

        /// <summary>Fade back to clear; completes when fully transparent.</summary>
        public async Task FadeIn() { _target = 0f; await WaitForAlpha(0f); }

        private async Task WaitForAlpha(float t)
        {
            int guard = 0;
            while (Mathf.Abs(_alpha - t) > 0.01f && guard++ < 600)
                await Task.Yield(); // resumes on the Unity main thread
        }

        private void OnGUI()
        {
            if (_alpha <= 0.001f) return;
            var prev = GUI.color;
            GUI.color = new Color(0f, 0f, 0f, _alpha);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), Texture2D.whiteTexture);
            GUI.color = prev;
        }
    }
}
