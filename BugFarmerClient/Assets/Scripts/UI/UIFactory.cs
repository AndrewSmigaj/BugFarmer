using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace BugFarmer.UI
{
    /// <summary>
    /// Programmatic UI construction (2026-06: the hand-built scene UI is
    /// replaced by code — see UIBootstrap). One style block, factory helpers,
    /// and the UI sprite loader. Sprites come from Resources/UI/ (hand-authored
    /// by tools/sprites/ui_sprites.py); 9-slice borders are passed HERE to
    /// Sprite.Create — never stored in .meta files.
    /// </summary>
    public static class UIFactory
    {
        // ---- STYLE (one place; the art kit is authored to match) ----------
        public const int Slot = 40;          // 20px frame x2
        public const int EquipSlot = 48;     // 24px riveted frame x2
        public const int Gap = 4;
        public const int Pad = 10;
        public static readonly Color TextColor = new Color32(238, 228, 204, 255);
        public static readonly Color HeaderColor = new Color32(246, 210, 100, 255);
        public static readonly Color CountColor = Color.white;
        public const float HeaderSize = 13f;
        public const float CountSize = 12f;

        // 9-slice borders per UI sprite (left, bottom, right, top) in px
        private static readonly Dictionary<string, Vector4> Borders = new Dictionary<string, Vector4>
        {
            { "panel_wood", new Vector4(6, 6, 6, 6) },
            { "panel_parchment", new Vector4(5, 5, 5, 5) },
            { "divider_h", new Vector4(2, 0, 2, 0) },
        };

        private static readonly Dictionary<string, Sprite> Cache = new Dictionary<string, Sprite>();

        /// <summary>Load a UI sprite (Resources/UI/{name}) with its code-side border.</summary>
        public static Sprite UISprite(string name)
        {
            if (Cache.TryGetValue(name, out var s) && s != null) return s;
            var tex = Resources.Load<Texture2D>($"UI/{name}");
            if (tex == null)
            {
                Debug.LogWarning($"[UIFactory] missing UI sprite: {name}");
                return null;
            }
            Borders.TryGetValue(name, out var border); // default zero
            s = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height),
                              new Vector2(0.5f, 0.5f), 100f, 0, SpriteMeshType.FullRect, border);
            s.name = name;
            Cache[name] = s;
            return s;
        }

        // ---- primitives ----------------------------------------------------
        public static RectTransform MakeRect(Transform parent, string name)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = (RectTransform)go.transform;
            rt.SetParent(parent, false);
            return rt;
        }

        public static Image MakeImage(Transform parent, string name, string spriteName,
                                      bool sliced = false)
        {
            var rt = MakeRect(parent, name);
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = spriteName != null ? UISprite(spriteName) : null;
            img.type = sliced ? Image.Type.Sliced : Image.Type.Simple;
            img.raycastTarget = false;
            return img;
        }

        public static TMP_Text MakeText(Transform parent, string name, float size,
                                        Color color, TextAlignmentOptions align)
        {
            var rt = MakeRect(parent, name);
            var t = rt.gameObject.AddComponent<TextMeshProUGUI>();
            t.fontSize = size;
            t.color = color;
            t.alignment = align;
            t.raycastTarget = false;
            t.enableWordWrapping = false;
            return t;
        }

        /// <summary>Anchored panel with the wood 9-slice background.</summary>
        public static RectTransform MakeDock(Transform parent, string name,
                                             Vector2 anchor, Vector2 pivot,
                                             Vector2 size, Vector2 offset)
        {
            var rt = MakeRect(parent, name);
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = pivot;
            rt.sizeDelta = size;
            rt.anchoredPosition = offset;
            var bg = rt.gameObject.AddComponent<Image>();
            bg.sprite = UISprite("panel_wood");
            bg.type = Image.Type.Sliced;
            bg.raycastTarget = true; // panel blocks clicks from hitting the world
            return rt;
        }

        public static GridLayoutGroup MakeGrid(Transform parent, string name, int cols,
                                               int cell, int gap = Gap)
        {
            var rt = MakeRect(parent, name);
            var grid = rt.gameObject.AddComponent<GridLayoutGroup>();
            grid.cellSize = new Vector2(cell, cell);
            grid.spacing = new Vector2(gap, gap);
            grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            grid.constraintCount = cols;
            grid.childAlignment = TextAnchor.UpperLeft;
            return grid;
        }

        /// <summary>
        /// A full slot widget: frame background, inset icon, count text,
        /// selection ring (hidden), optional ghost silhouette (equipment).
        /// The InventorySlotUI's private parts are assigned via InitParts.
        /// </summary>
        public static InventorySlotUI MakeSlot(Transform parent, string frameSprite,
                                               string ghostSprite = null)
        {
            var rt = MakeRect(parent, "Slot");
            var bg = rt.gameObject.AddComponent<Image>();
            bg.sprite = UISprite(frameSprite);
            bg.type = Image.Type.Simple;
            bg.raycastTarget = true; // the click target

            Image ghost = null;
            if (ghostSprite != null)
            {
                ghost = MakeImage(rt, "Ghost", ghostSprite);
                Stretch(ghost.rectTransform, 6);
                ghost.preserveAspect = true;
            }

            var icon = MakeImage(rt, "Icon", null);
            Stretch(icon.rectTransform, 5);
            icon.preserveAspect = true;
            icon.enabled = false;

            var count = MakeText(rt, "Count", CountSize, CountColor, TextAlignmentOptions.BottomRight);
            Stretch(count.rectTransform, 3);
            count.enabled = false;
            count.fontStyle = FontStyles.Bold;

            var sel = MakeImage(rt, "Selected", "slot_selected");
            Stretch(sel.rectTransform, 0);
            sel.enabled = false;

            var slot = rt.gameObject.AddComponent<InventorySlotUI>();
            slot.InitParts(icon, count, sel, bg, ghost);
            return slot;
        }

        /// <summary>Stretch-fill the parent with a uniform inset.</summary>
        public static void Stretch(RectTransform rt, int inset)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = new Vector2(inset, inset);
            rt.offsetMax = new Vector2(-inset, -inset);
        }
    }
}
