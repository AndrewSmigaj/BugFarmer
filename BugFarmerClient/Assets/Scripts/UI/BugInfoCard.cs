using TMPro;
using UnityEngine;
using UnityEngine.UI;
using BugFarmer.Data;

namespace BugFarmer.UI
{
    /// <summary>
    /// The bug info card: right-click a bug slot (cursor empty) and a parchment
    /// card SWAPS IN for the bug grid in the right dock — never covering the
    /// open center. Shows the freely-known tier (sprite, name, count,
    /// description, net size, sell price) plus LOCKED rows for breeding and
    /// favorite foods: the magnifying-glass RESEARCH mechanic (study a species
    /// X times to unlock tiers) is the planned follow-up; the rows exist now so
    /// the design is already shaped around it.
    /// </summary>
    public class BugInfoCard : MonoBehaviour
    {
        public static BugInfoCard Instance { get; private set; }

        private GameObject _root;
        private Image _bugImage;
        private TMP_Text _title;
        private TMP_Text _body;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(this); return; }
            Instance = this;
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        public bool IsShowing => _root != null && _root.activeSelf;

        /// <summary>
        /// Find-or-create (2026-06: right-click fell through to the half-stack
        /// pickup when no instance existed — the card must work regardless of
        /// which path constructed the UI).
        /// </summary>
        public static BugInfoCard Ensure()
        {
            if (Instance != null) return Instance;
            var host = InventoryPanel.Instance != null
                ? InventoryPanel.Instance.gameObject
                : FindObjectOfType<Canvas>()?.gameObject;
            return host != null ? host.AddComponent<BugInfoCard>() : null;
        }

        /// <summary>Build (once) inside the right dock, hidden.</summary>
        private void BuildIfEmpty()
        {
            if (_root != null) return;
            var panel = InventoryPanel.Instance;
            if (panel == null || panel.BugDock == null) return;

            var rt = UIFactory.MakeRect(panel.BugDock, "BugInfoCard");
            UIFactory.Stretch(rt, 4);
            var bg = rt.gameObject.AddComponent<Image>();
            bg.sprite = UIFactory.UISprite("panel_parchment");
            bg.type = Image.Type.Sliced;
            bg.raycastTarget = true;
            _root = rt.gameObject;

            _bugImage = UIFactory.MakeImage(rt, "Bug", null);
            var brt = _bugImage.rectTransform;
            brt.anchorMin = brt.anchorMax = new Vector2(0.5f, 1f);
            brt.pivot = new Vector2(0.5f, 1f);
            brt.anchoredPosition = new Vector2(0, -10);
            brt.sizeDelta = new Vector2(48, 48);
            _bugImage.preserveAspect = true;

            _title = UIFactory.MakeText(rt, "Title", 14f, new Color32(70, 50, 30, 255),
                                        TextAlignmentOptions.Center);
            var trt = _title.rectTransform;
            trt.anchorMin = new Vector2(0f, 1f); trt.anchorMax = new Vector2(1f, 1f);
            trt.pivot = new Vector2(0.5f, 1f);
            trt.anchoredPosition = new Vector2(0, -62);
            trt.sizeDelta = new Vector2(-16, 18);
            _title.fontStyle = FontStyles.Bold;

            _body = UIFactory.MakeText(rt, "Body", 11f, new Color32(82, 64, 42, 255),
                                       TextAlignmentOptions.TopLeft);
            var yrt = _body.rectTransform;
            yrt.anchorMin = new Vector2(0f, 0f); yrt.anchorMax = new Vector2(1f, 1f);
            yrt.offsetMin = new Vector2(12, 30);
            yrt.offsetMax = new Vector2(-12, -84);
            _body.enableWordWrapping = true;

            // back button (close the card, return to the grid)
            var back = UIFactory.MakeImage(rt, "Back", "btn_close");
            var krt = back.rectTransform;
            krt.anchorMin = krt.anchorMax = new Vector2(1f, 1f);
            krt.pivot = new Vector2(1f, 1f);
            krt.anchoredPosition = new Vector2(-6, -6);
            krt.sizeDelta = new Vector2(20, 20);
            back.raycastTarget = true;
            var btn = back.gameObject.AddComponent<Button>();
            btn.onClick.AddListener(Hide);

            _root.SetActive(false);
        }

        public void Show(string speciesId, int count)
        {
            BuildIfEmpty();
            if (_root == null) return;
            var sp = EntityDatabase.GetSpecies(speciesId);

            _bugImage.sprite = EntityDatabase.GetItemSprite(speciesId);
            _bugImage.enabled = _bugImage.sprite != null;
            _title.text = sp != null ? $"{sp.Name}  x{count}" : speciesId;

            string desc = string.IsNullOrEmpty(sp?.Description)
                ? "A curious little creature." : sp.Description;
            string net = sp?.NetSize ?? "small";
            string sell = sp != null && sp.SellPrice > 0 ? $"\nSells for {sp.SellPrice} coins." : "";
            _body.text =
                $"{desc}\n\nCatch with a {net} net.{sell}\n\n" +
                "<alpha=#88>Breeding: ???\nFavorite foods: ???\n" +
                "<size=9>(study with a magnifying glass to reveal)</size><alpha=#FF>";

            InventoryPanel.Instance?.BugGridRoot?.SetActive(false);
            _root.SetActive(true);
        }

        public void Hide()
        {
            if (_root != null) _root.SetActive(false);
            InventoryPanel.Instance?.BugGridRoot?.SetActive(true);
        }
    }
}
