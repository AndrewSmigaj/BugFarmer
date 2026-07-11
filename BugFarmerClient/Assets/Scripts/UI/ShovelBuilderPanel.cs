using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using BugFarmer.Data;
using BugFarmer.World;

namespace BugFarmer.UI
{
    /// <summary>
    /// The shovel "Set Materials" builder panel (S2) — replaces the dev OnGUI readout with a real,
    /// legible picker. Open with B while a shovel is equipped. Shows every material A as its ACTUAL
    /// composited tile (matA~matB~shape via the runtime TileCompositor), a material B row, the current
    /// shape, and LIVE have/need for the selected tile's recipe (both materials) — unaffordable
    /// materials are dimmed. Mirrors the CraftingPanel singleton + UIFactory conventions. Additive:
    /// the shovel's wheel(=shape) and the temporary M/N keys keep working alongside it.
    /// </summary>
    public class ShovelBuilderPanel : MonoBehaviour
    {
        public static ShovelBuilderPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._open;

        private const string GREEN = "#9BC87A";
        private const string RED = "#D66E60";

        private bool _open;
        private RectTransform _dock;
        private CanvasGroup _group;
        private readonly Image[] _aSwatch = new Image[8];
        private readonly Image[] _aRing = new Image[8];
        private readonly Image[] _bSwatch = new Image[8];
        private readonly Image[] _bRing = new Image[8];
        private TMP_Text _shapeLbl, _placeLbl, _needLbl;
        private readonly Dictionary<string, Sprite> _spriteCache = new Dictionary<string, Sprite>();
        private int _lastA = -1, _lastB = -1, _lastShape = -1;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            _dock = UIFactory.MakeDock(transform, "ShovelDock", new Vector2(0.5f, 0.5f),
                                       new Vector2(0.5f, 0.5f), new Vector2(474, 300), Vector2.zero);
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            var title = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 2f, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            At(title.rectTransform, 16, 8, 300, 20); title.text = "Set Materials";

            var aHead = UIFactory.MakeText(_dock, "AHead", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            At(aHead.rectTransform, 16, 32, 320, 14); aHead.text = "Material A  (fills the shape)";

            for (int i = 0; i < 8; i++)
            {
                int idx = i;
                int col = i % 4, row = i / 4;
                float x = 16 + col * 56, y = 50 + row * 62;
                var img = MakeButtonImage(_dock, $"A{i}", x, y, 44, () => { ShovelSelection.MatAIndex = idx; Refresh(true); });
                var ring = UIFactory.MakeImage(img.transform, "Ring", "slot_selected");
                UIFactory.Stretch(ring.rectTransform, -2); ring.enabled = false;
                _aSwatch[i] = img; _aRing[i] = ring;
                var lbl = UIFactory.MakeText(_dock, $"A{i}L", 9f, UIFactory.TextColor, TextAlignmentOptions.Center);
                At(lbl.rectTransform, x - 6, y + 45, 56, 11); lbl.text = ShovelSelection.Materials[i];
            }

            var bHead = UIFactory.MakeText(_dock, "BHead", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            At(bHead.rectTransform, 16, 178, 320, 14); bHead.text = "Material B  (the other half)";
            for (int i = 0; i < 8; i++)
            {
                int idx = i;
                float x = 16 + i * 30;
                var img = MakeButtonImage(_dock, $"B{i}", x, 194, 26, () => { ShovelSelection.MatBIndex = idx; Refresh(true); });
                var ring = UIFactory.MakeImage(img.transform, "Ring", "slot_selected");
                UIFactory.Stretch(ring.rectTransform, -2); ring.enabled = false;
                _bSwatch[i] = img; _bRing[i] = ring;
            }

            _placeLbl = UIFactory.MakeText(_dock, "Place", UIFactory.CountSize, UIFactory.HeaderColor, TextAlignmentOptions.Left);
            At(_placeLbl.rectTransform, 16, 228, 440, 14);
            _shapeLbl = UIFactory.MakeText(_dock, "Shape", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            At(_shapeLbl.rectTransform, 16, 246, 440, 14);

            _needLbl = UIFactory.MakeText(_dock, "Need", UIFactory.CountSize, UIFactory.TextColor, TextAlignmentOptions.Left);
            At(_needLbl.rectTransform, 250, 50, 210, 120);
            _needLbl.enableWordWrapping = true;

            var legend = UIFactory.MakeText(_dock, "Legend", 10f, new Color(0.6f, 0.56f, 0.48f, 1f), TextAlignmentOptions.Left);
            At(legend.rectTransform, 16, 276, 448, 14);
            legend.text = "LMB place   ·   Shift+LMB dig   ·   wheel = shape   ·   B / Esc close";

            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged += OnInventoryChanged;

            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            if (InventoryManager.Instance != null)
                InventoryManager.Instance.OnInventoryChanged -= OnInventoryChanged;
        }

        private void Update()
        {
            bool shovel = IsShovelEquipped();
            if (shovel && Input.GetKeyDown(KeyCode.B)) { SetOpen(!_open); return; }
            if (_open && Input.GetKeyDown(KeyCode.Escape)) { SetOpen(false); return; }
            if (_open && !shovel) { SetOpen(false); return; }
            if (_open) Refresh(false);
        }

        private void OnInventoryChanged() { if (_open) Refresh(true); }

        private void SetOpen(bool open)
        {
            _open = open;
            if (_group != null)
            {
                _group.alpha = open ? 1f : 0f;
                _group.blocksRaycasts = open;
                _group.interactable = open;
            }
            _dock.gameObject.SetActive(open);
            if (open) Refresh(true);
        }

        private void Refresh(bool force)
        {
            if (!_open) return;
            if (!force && _lastA == ShovelSelection.MatAIndex && _lastB == ShovelSelection.MatBIndex
                && _lastShape == ShovelSelection.ShapeIndex) return;
            _lastA = ShovelSelection.MatAIndex; _lastB = ShovelSelection.MatBIndex; _lastShape = ShovelSelection.ShapeIndex;

            string b = ShovelSelection.MatB, shape = ShovelSelection.Shape;
            for (int i = 0; i < 8; i++)
            {
                string m = ShovelSelection.Materials[i];
                string sid = (shape == "full") ? m : $"{m}~{b}~{shape}";
                var sprite = SpriteFor(sid);
                _aSwatch[i].sprite = sprite;
                _aSwatch[i].enabled = sprite != null;
                _aSwatch[i].color = Affordable(sid) ? Color.white : new Color(1f, 1f, 1f, 0.4f);
                _aRing[i].enabled = (i == ShovelSelection.MatAIndex);

                var bsprite = SpriteFor(m);
                _bSwatch[i].sprite = bsprite;
                _bSwatch[i].enabled = bsprite != null;
                _bRing[i].enabled = (i == ShovelSelection.MatBIndex);
            }
            _shapeLbl.text = $"Shape: {shape}   (mouse wheel to cycle)";
            _placeLbl.text = $"Places: {ShovelSelection.CurrentGroundId}";
            _needLbl.text = BuildNeedText(ShovelSelection.CurrentGroundId);
        }

        private string BuildNeedText(string id)
        {
            var ings = GroundRecipeDatabase.Ingredients(id);
            if (ings.Count == 0) return "Not placeable.";
            var sb = new System.Text.StringBuilder("Recipe (costs both):\n");
            bool afford = true;
            foreach (var ing in ings)
            {
                int have = CountHeld(ing.item);
                bool ok = have >= ing.count;
                if (!ok) afford = false;
                sb.Append($"<color={(ok ? GREEN : RED)}>{ing.item}: {have}/{ing.count}</color>\n");
            }
            sb.Append(afford ? $"<color={GREEN}>Ready to place</color>"
                             : $"<color={RED}>Need more (a place shows why)</color>");
            return sb.ToString();
        }

        private bool Affordable(string id)
        {
            var ings = GroundRecipeDatabase.Ingredients(id);
            if (ings.Count == 0) return false;
            foreach (var ing in ings)
                if (CountHeld(ing.item) < ing.count) return false;
            return true;
        }

        private int CountHeld(string item)
        {
            var slots = InventoryManager.Instance?.ItemSlots;
            if (slots == null) return 0;
            int n = 0;
            foreach (var s in slots)
                if (s != null && s.item_id == item) n += s.count;
            return n;
        }

        private Sprite SpriteFor(string id)
        {
            if (_spriteCache.TryGetValue(id, out var cached)) return cached;
            Texture2D tex;
            if (id.Contains("~"))
            {
                var p = id.Split('~');
                tex = (p.Length == 3) ? TileCompositor.Build(p[0], p[1], p[2]) : null;
            }
            else
            {
                tex = Resources.Load<Texture2D>($"Tiles/{id}");
            }
            if (tex == null) return null;
            var s = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), tex.width);
            _spriteCache[id] = s;
            return s;
        }

        private Image MakeButtonImage(Transform parent, string name, float x, float y, float size, UnityEngine.Events.UnityAction onClick)
        {
            var img = UIFactory.MakeImage(parent, name, null);
            At(img.rectTransform, x, y, size, size);
            img.color = Color.white;
            img.raycastTarget = true; // clickable
            var btn = img.gameObject.AddComponent<Button>();
            btn.transition = Selectable.Transition.None;
            btn.onClick.AddListener(onClick);
            return img;
        }

        // Anchor a child to the dock's TOP-LEFT at (x, y measured downward), size (w,h).
        private RectTransform At(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, -y);
            rt.sizeDelta = new Vector2(w, h);
            return rt;
        }

        private bool IsShovelEquipped()
        {
            var id = InventoryManager.Instance?.GetEquippedToolId();
            if (string.IsNullOrEmpty(id)) return false;
            return EntityDatabase.Get(id)?.ToolType == "shovel";
        }
    }
}
