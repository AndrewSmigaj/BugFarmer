using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace BugFarmer.UI
{
    /// <summary>
    /// One shared hover tooltip (built by UIBootstrap, on top of everything). Slots call Show(name)
    /// on pointer-enter and Hide() on exit. Follows the cursor; never blocks raycasts.
    /// </summary>
    public class TooltipUI : MonoBehaviour
    {
        public static TooltipUI Instance { get; private set; }

        private RectTransform _rt;
        private TMP_Text _text;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            Build();
            gameObject.SetActive(false);
        }

        private void Build()
        {
            _rt = (RectTransform)transform;
            _rt.anchorMin = _rt.anchorMax = new Vector2(0f, 0f); // bottom-left; we set anchoredPosition
            _rt.pivot = new Vector2(0f, 0f);

            var bg = UIFactory.MakeImage(transform, "TipBg", "panel_wood", true);
            var brt = bg.rectTransform;
            brt.anchorMin = Vector2.zero; brt.anchorMax = Vector2.one;
            brt.offsetMin = Vector2.zero; brt.offsetMax = Vector2.zero;
            bg.raycastTarget = false;

            _text = UIFactory.MakeText(transform, "TipText", UIFactory.CountSize + 1f,
                                       UIFactory.TextColor, TextAlignmentOptions.Center);
            var trt = _text.rectTransform;
            trt.anchorMin = Vector2.zero; trt.anchorMax = Vector2.one;
            trt.offsetMin = new Vector2(6, 3); trt.offsetMax = new Vector2(-6, -3);
            _text.raycastTarget = false;
        }

        public void Show(string label)
        {
            if (string.IsNullOrEmpty(label)) { Hide(); return; }
            _text.text = label;
            gameObject.SetActive(true);
            transform.SetAsLastSibling(); // draw above all other UI
            float w = Mathf.Clamp(_text.preferredWidth + 14, 40f, 220f);
            _rt.sizeDelta = new Vector2(w, 22f);
            Reposition();
        }

        public void Hide()
        {
            if (this != null) gameObject.SetActive(false);
        }

        private void Update()
        {
            if (gameObject.activeSelf) Reposition();
        }

        private void Reposition()
        {
            var canvas = GetComponentInParent<Canvas>();
            float sf = canvas != null ? canvas.scaleFactor : 1f;
            if (sf <= 0f) sf = 1f;
            // Screen-space-overlay: anchoredPosition (from bottom-left) = mouse in canvas units.
            Vector2 p = (Vector2)Input.mousePosition / sf + new Vector2(14f, 14f);
            var parent = _rt.parent as RectTransform;
            if (parent != null)
            {
                Vector2 canvasSize = parent.rect.size;
                p.x = Mathf.Min(p.x, canvasSize.x - _rt.sizeDelta.x - 2f);
                p.y = Mathf.Min(p.y, canvasSize.y - _rt.sizeDelta.y - 2f);
            }
            _rt.anchoredPosition = p;
        }
    }
}
