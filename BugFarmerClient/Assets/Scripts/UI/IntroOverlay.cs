using UnityEngine;

namespace BugFarmer.UI
{
    /// <summary>
    /// First-login welcome, shown ONCE per character (the server flags it on the join
    /// FullInventorySync; persisted via the character's IntroSeen). A self-bootstrapping OnGUI
    /// overlay — no canvas/scene wiring — matching the lightweight OnGUI pattern used elsewhere
    /// (StationController, PlayerHealth toasts). Dismissed with the button or Enter/Esc.
    /// </summary>
    public class IntroOverlay : MonoBehaviour
    {
        private static IntroOverlay _instance;
        private bool _visible;

        private static readonly string[] Lines =
        {
            "Welcome to the village square.",
            "",
            "Catch bugs, tend a farm, and build a home of your own.",
            "Sleep in a bed to set where you wake — your home point.",
            "",
            "Press I for your inventory. Good luck!",
        };

        /// <summary>Show the welcome overlay (lazily creates the host object if needed).</summary>
        public static void Show()
        {
            if (_instance == null)
            {
                var go = new GameObject("IntroOverlay(Code)");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<IntroOverlay>();
            }
            _instance._visible = true;
        }

        private void OnGUI()
        {
            if (!_visible) return;

            const float w = 460f, h = 240f;
            var rect = new Rect(Screen.width / 2f - w / 2f, Screen.height / 2f - h / 2f, w, h);

            // Dim the screen behind the panel.
            var prev = GUI.color;
            GUI.color = new Color(0f, 0f, 0f, 0.6f);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), Texture2D.whiteTexture);
            GUI.color = prev;

            GUILayout.BeginArea(rect, GUI.skin.box);
            GUILayout.Space(8);
            var title = new GUIStyle(GUI.skin.label) { fontSize = 20, alignment = TextAnchor.MiddleCenter, fontStyle = FontStyle.Bold };
            GUILayout.Label("A New Beginning", title);
            GUILayout.Space(8);
            var body = new GUIStyle(GUI.skin.label) { fontSize = 14, alignment = TextAnchor.MiddleCenter, wordWrap = true };
            foreach (var line in Lines)
                GUILayout.Label(line, body);
            GUILayout.FlexibleSpace();
            GUILayout.BeginHorizontal();
            GUILayout.FlexibleSpace();
            if (GUILayout.Button("Begin", GUILayout.Width(120), GUILayout.Height(32)))
                _visible = false;
            GUILayout.FlexibleSpace();
            GUILayout.EndHorizontal();
            GUILayout.Space(8);
            GUILayout.EndArea();

            // Keyboard dismiss.
            var e = Event.current;
            if (e != null && e.type == EventType.KeyDown &&
                (e.keyCode == KeyCode.Return || e.keyCode == KeyCode.KeypadEnter || e.keyCode == KeyCode.Escape))
                _visible = false;
        }
    }
}
