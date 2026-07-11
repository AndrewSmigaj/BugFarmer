using System.Text;
using Nakama;
using TMPro;
using UnityEngine;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// General on-screen toast for server "world error" messages (OpCode 40) — e.g. "Need 2 stone",
    /// "Can't shovel water", "Nothing to dig here". These used to be read ONLY by ShopPanel, and only
    /// while the shop was open, so every refusal outside a shop was silently dropped (the root cause of
    /// the shovel "does nothing with no feedback" bug). This shows the latest error near the bottom of
    /// the screen and fades it out. Built + registered by UIBootstrap; singleton like the other panels.
    /// </summary>
    public class WorldToast : MonoBehaviour
    {
        public static WorldToast Instance { get; private set; }

        // Fade envelope (unscaled time, so a paused game still shows toasts).
        private const float FadeIn = 0.12f;
        private const float Hold = 1.9f;
        private const float FadeOut = 0.45f;

        private CanvasGroup _group;
        private TMP_Text _text;
        private float _shownAt = -999f; // when the current message started; a new message restarts it

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            // Anchored chip, bottom-center, sitting above the hotbar.
            var rt = (RectTransform)transform;
            rt.anchorMin = new Vector2(0.5f, 0f);
            rt.anchorMax = new Vector2(0.5f, 0f);
            rt.pivot = new Vector2(0.5f, 0f);
            rt.anchoredPosition = new Vector2(0f, 96f);
            rt.sizeDelta = new Vector2(380f, 32f);

            _group = gameObject.AddComponent<CanvasGroup>();
            _group.alpha = 0f;
            _group.interactable = false;
            _group.blocksRaycasts = false; // never eats clicks

            // Solid dark backing so the text stays legible over any terrain.
            var bg = UIFactory.MakeImage(transform, "ToastBG", null);
            bg.color = new Color(0f, 0f, 0f, 0.72f);
            UIFactory.Stretch((RectTransform)bg.transform, 0);

            _text = UIFactory.MakeText(transform, "ToastText", 14f, UIFactory.TextColor,
                                       TextAlignmentOptions.Center);
            _text.enableWordWrapping = true;
            UIFactory.Stretch((RectTransform)_text.transform, 6);

            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState += OnMatchState;
        }

        private void OnDestroy()
        {
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState -= OnMatchState;
            if (Instance == this) Instance = null;
        }

        private void OnMatchState(IMatchState state)
        {
            if (state.OpCode != OpCodes.ErrorMessage) return;
            // The shop already surfaces OpCode-40 errors in its own status line while open — don't double up.
            if (ShopPanel.IsOpen) return;
            var json = Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ErrorMessage>(json);
            if (msg == null || string.IsNullOrEmpty(msg.error)) return;
            Show(msg.error);
        }

        /// <summary>Show a message now (also callable directly by client code that wants to warn the player).</summary>
        public void Show(string message)
        {
            if (_text == null) return;
            _text.text = message;
            _shownAt = Time.unscaledTime; // restart the envelope: the latest error wins
        }

        private void Update()
        {
            if (_group == null) return;
            float t = Time.unscaledTime - _shownAt;
            float a;
            if (t < 0f) a = 0f;
            else if (t < FadeIn) a = t / FadeIn;                                   // fade in
            else if (t < FadeIn + Hold) a = 1f;                                    // hold
            else if (t < FadeIn + Hold + FadeOut) a = 1f - (t - FadeIn - Hold) / FadeOut; // fade out
            else a = 0f;                                                           // gone
            _group.alpha = Mathf.Clamp01(a);
        }
    }
}
