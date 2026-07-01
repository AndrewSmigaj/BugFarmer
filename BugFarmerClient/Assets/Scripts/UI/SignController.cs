using UnityEngine;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Player;
using BugFarmer.World;

namespace BugFarmer.UI
{
    /// <summary>
    /// SIGNS — right-click a "sign" occupant to read what's written on it. A small carved-board panel
    /// shows the sign's per-placement text (authored in the zone, e.g. a crossroads signpost's
    /// directions). Read-only. The text rides the occupant chunk data (PlacedOccupant.text); we look it
    /// up by the clicked anchor cell via TilemapManager. Canvas/UIFactory, parchment accent.
    /// </summary>
    public class SignController : MonoBehaviour
    {
        public static SignController Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 3.0f;
        private static readonly Color Board = new Color32(150, 110, 70, 255);

        private bool _isOpen;
        private CanvasGroup _group;
        private RectTransform _dock;
        private TMP_Text _text;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            _dock = UIFactory.MakeDock(transform, "SignDock", new Vector2(0.5f, 1f),
                                       new Vector2(0.5f, 1f), new Vector2(320, 180), new Vector2(0, -60));
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            var title = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 1f,
                                           UIFactory.HeaderColor, TextAlignmentOptions.Center);
            Place(title.rectTransform, 0, -8, 320, 18, new Vector2(0.5f, 1f), new Vector2(0.5f, 1f));
            title.text = "— Signpost —";

            var board = UIFactory.MakeImage(_dock, "Board", "panel_parchment", true);
            board.color = Board;
            Place(board.rectTransform, 16, -32, 288, 110, new Vector2(0f, 1f), new Vector2(0f, 1f));

            _text = UIFactory.MakeText(_dock, "Text", UIFactory.HeaderSize,
                                       new Color32(44, 32, 20, 255), TextAlignmentOptions.Center);
            _text.enableWordWrapping = true;
            Place(_text.rectTransform, 28, -42, 264, 92, new Vector2(0f, 1f), new Vector2(0f, 1f));

            MakeButton(_dock, "Close", "Close", 0, -150, 100, 26, () => SetOpen(false), new Vector2(0.5f, 1f));
            SetOpen(false);
        }

        private void OnDestroy() { if (Instance == this) Instance = null; }

        private void Update()
        {
            if (_isOpen && Input.GetKeyDown(KeyCode.Escape)) SetOpen(false);
        }

        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            // Front-most interactable occupant (shared resolver; not a bare OverlapPoint that an
            // overlapping occupant could steal).
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null)
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }
            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "sign")
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > MaxInteractDistance * MaxInteractDistance) return false;
            }
            string text = TilemapManager.Instance != null
                ? TilemapManager.Instance.GetOccupantText(target.AnchorCell) : null;
            if (string.IsNullOrEmpty(text)) text = def.Name ?? "It's a sign.";
            _text.text = text.Replace(" · ", "\n").Replace("·", "\n");
            SetOpen(true);
            return true;
        }

        private void SetOpen(bool open)
        {
            _isOpen = open;
            if (_group != null)
            {
                _group.alpha = open ? 1f : 0f;
                _group.blocksRaycasts = open;
                _group.interactable = open;
            }
            _dock.gameObject.SetActive(open);
        }

        private void MakeButton(Transform parent, string name, string label, float x, float y,
                                float w, float h, UnityEngine.Events.UnityAction onClick, Vector2 anchor)
        {
            var rt = UIFactory.MakeRect(parent, name);
            Place(rt, x, y, w, h, anchor, anchor);
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = UIFactory.UISprite("slot_frame");
            img.type = Image.Type.Sliced;
            rt.gameObject.AddComponent<Button>().onClick.AddListener(onClick);
            var t = UIFactory.MakeText(rt, "Label", UIFactory.HeaderSize, UIFactory.TextColor, TextAlignmentOptions.Center);
            UIFactory.Stretch(t.rectTransform, 0);
            t.text = label;
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h, Vector2 anchor, Vector2 pivot)
        {
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = pivot;
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }
    }
}
