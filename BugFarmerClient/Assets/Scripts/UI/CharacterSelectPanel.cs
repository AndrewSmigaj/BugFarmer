using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using Nakama;
using BugFarmer.Networking;
using BugFarmer.Player;

namespace BugFarmer.UI
{
    /// <summary>
    /// Terraria-style character select, shown over the login screen at startup (its own top canvas,
    /// order 20). Lists the account's characters (character_list RPC), lets you Create (name +
    /// class/hair/skin picker with a live paper-doll preview) and Delete, and on pick stores
    /// CharacterSession.SelectedCharID then HIDES itself — revealing the WorldMenu beneath for the
    /// zone picker. The dim full-screen backdrop blocks clicks to WorldMenu until a character is chosen.
    ///
    /// Built entirely in code (like UIBootstrap) — zero scene wiring. RPCs go over the HTTP client
    /// (no socket needed); the socket only connects later when WorldMenu.Play enters a world.
    /// </summary>
    public class CharacterSelectPanel : MonoBehaviour
    {
        public static CharacterSelectPanel Instance { get; private set; }

        // Appearance option sets (only those with real layer art — see Resources/Player/layers/).
        private static readonly string[] Classes = { "merchant", "farmer", "miner", "ranger", "scholar" };
        private static readonly string[] Hairs = { "blonde", "brown", "black", "auburn", "sandy" };
        private static readonly string[] Skins = { "default", "tan", "deep" };

        private GameObject _canvasRoot;       // the whole select overlay (hidden on pick)
        private Transform _listRoot;          // existing-character rows go here
        private TMP_Text _status;
        private TMP_InputField _nameInput;
        private Image _preview;
        private TMP_Text _classLabel, _hairLabel, _skinLabel;
        private int _classIdx, _hairIdx, _skinIdx;
        private bool _busy;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (Instance != null) return;

            // EventSystem (UIBootstrap also guards; whichever runs first wins).
            if (FindObjectOfType<EventSystem>() == null)
            {
                var es = new GameObject("EventSystem(Code)", typeof(EventSystem),
                                        typeof(StandaloneInputModule));
                DontDestroyOnLoad(es);
            }

            var canvasGO = new GameObject("CharSelectCanvas(Code)", typeof(Canvas),
                                          typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = canvasGO.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 20; // above the inventory canvas (10) and the scene menu (0)
            var scaler = canvasGO.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(800, 600);
            scaler.matchWidthOrHeight = 0.5f;

            canvasGO.AddComponent<CharacterSelectPanel>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            BuildUI();
        }

        private async void Start()
        {
            // Wait for device auth, then load the roster (RPC over the HTTP client).
            SetStatus("Authenticating...");
            try { await NetworkManager.Instance.Session; }
            catch (Exception ex) { SetStatus($"Auth failed: {ex.Message}"); return; }
            await RefreshListAsync();
        }

        // ---------------------------------------------------------------- UI build

        private void BuildUI()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            _canvasRoot = transform.gameObject;

            // Dim full-screen backdrop — blocks clicks to the WorldMenu below while choosing.
            var dim = UIFactory.MakeRect(transform, "Dim");
            UIFactory.Stretch(dim, 0);
            var dimImg = dim.gameObject.AddComponent<Image>();
            dimImg.color = new Color(0f, 0f, 0f, 0.72f);
            dimImg.raycastTarget = true;

            // Centered dock.
            var dock = UIFactory.MakeDock(transform, "CharDock", new Vector2(0.5f, 0.5f),
                                          new Vector2(0.5f, 0.5f), new Vector2(580, 440), Vector2.zero);

            var title = UIFactory.MakeText(dock, "Title", 18, UIFactory.HeaderColor, TextAlignmentOptions.Center);
            PlaceTL(title.rectTransform, 0, 12, 580, 24);
            title.text = "SELECT CHARACTER";

            _status = UIFactory.MakeText(dock, "Status", 12, UIFactory.TextColor, TextAlignmentOptions.Center);
            PlaceTL(_status.rectTransform, 0, 410, 580, 18);

            // ---- LEFT: existing characters list ----
            var listHdr = UIFactory.MakeText(dock, "ListHdr", UIFactory.HeaderSize, UIFactory.HeaderColor,
                                             TextAlignmentOptions.Left);
            PlaceTL(listHdr.rectTransform, 18, 44, 260, 16);
            listHdr.text = "YOUR CHARACTERS";

            var listBox = UIFactory.MakeRect(dock, "ListRoot");
            PlaceTL(listBox, 18, 64, 268, 330);
            _listRoot = listBox;

            // ---- RIGHT: create panel ----
            var createHdr = UIFactory.MakeText(dock, "CreateHdr", UIFactory.HeaderSize, UIFactory.HeaderColor,
                                               TextAlignmentOptions.Left);
            PlaceTL(createHdr.rectTransform, 300, 44, 260, 16);
            createHdr.text = "CREATE NEW";

            // Live paper-doll preview (in a slot frame).
            var pvFrame = UIFactory.MakeImage(dock, "PreviewFrame", "slot_frame", false);
            pvFrame.raycastTarget = false;
            PlaceTL(pvFrame.rectTransform, 300, 66, 96, 96);
            _preview = UIFactory.MakeImage(pvFrame.transform, "PreviewSprite", null);
            UIFactory.Stretch(_preview.rectTransform, 10);
            _preview.preserveAspect = true;

            // Appearance cyclers.
            _classLabel = MakeCycler(dock, "Class", 408, 66, () => Step(ref _classIdx, Classes.Length, -1),
                                                              () => Step(ref _classIdx, Classes.Length, +1));
            _hairLabel = MakeCycler(dock, "Hair", 408, 100, () => Step(ref _hairIdx, Hairs.Length, -1),
                                                            () => Step(ref _hairIdx, Hairs.Length, +1));
            _skinLabel = MakeCycler(dock, "Skin", 408, 134, () => Step(ref _skinIdx, Skins.Length, -1),
                                                            () => Step(ref _skinIdx, Skins.Length, +1));

            // Name input.
            var nameLbl = UIFactory.MakeText(dock, "NameLbl", UIFactory.HeaderSize, UIFactory.TextColor,
                                             TextAlignmentOptions.Left);
            PlaceTL(nameLbl.rectTransform, 300, 178, 260, 16);
            nameLbl.text = "NAME";
            _nameInput = MakeInput(dock, "Hero");
            PlaceTL((RectTransform)_nameInput.transform, 300, 196, 260, 30);

            var createBtn = MakeButton(dock, "Create", new Color32(96, 150, 96, 255));
            PlaceTL((RectTransform)createBtn.transform, 300, 234, 260, 34);
            createBtn.onClick.AddListener(() => OnCreate());

            UpdatePreview();
        }

        /// <summary>A "◀ Value ▶" stepper row; returns its value label for refresh.</summary>
        private TMP_Text MakeCycler(Transform parent, string name, float x, float y, Action onLeft, Action onRight)
        {
            var left = MakeButton(parent, "<", null);
            PlaceTL((RectTransform)left.transform, x, y, 26, 26);
            left.onClick.AddListener(() => { onLeft(); UpdatePreview(); });

            var val = UIFactory.MakeText(parent, $"{name}Val", 13, UIFactory.TextColor, TextAlignmentOptions.Center);
            PlaceTL(val.rectTransform, x + 28, y + 4, 88, 18);

            var right = MakeButton(parent, ">", null);
            PlaceTL((RectTransform)right.transform, x + 118, y, 26, 26);
            right.onClick.AddListener(() => { onRight(); UpdatePreview(); });
            return val;
        }

        private static void Step(ref int idx, int len, int dir)
        {
            idx = ((idx + dir) % len + len) % len;
        }

        // ---------------------------------------------------------------- preview

        private void UpdatePreview()
        {
            var cls = Classes[_classIdx];
            var hair = Hairs[_hairIdx];
            var skin = Skins[_skinIdx];
            if (_classLabel != null) _classLabel.text = cls;
            if (_hairLabel != null) _hairLabel.text = hair;
            if (_skinLabel != null) _skinLabel.text = skin;
            SetPreview(_preview, cls, hair, skin);
        }

        private static void SetPreview(Image img, string cls, string hair, string skin)
        {
            if (img == null) return;
            Sprite[][] composed = null;
            try
            {
                composed = CharacterComposer.Compose(CharacterComposer.OutfitFromEquipment(null, cls, hair, skin));
            }
            catch (Exception e) { Debug.LogWarning($"[CharSelect] preview compose failed: {e.Message}"); }
            if (composed == null) composed = CharacterComposer.LoadBaked(cls);
            Sprite spr = (composed != null && composed.Length > 0 && composed[0] != null && composed[0].Length > 1)
                ? composed[0][1] // Down-facing idle
                : null;
            img.sprite = spr;
            img.enabled = spr != null;
            img.preserveAspect = true;
        }

        // ---------------------------------------------------------------- roster RPCs

        private async System.Threading.Tasks.Task RefreshListAsync()
        {
            SetStatus("Loading characters...");
            CharacterListResponse resp;
            try
            {
                var session = await NetworkManager.Instance.Session;
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "character_list", "{}");
                resp = JsonUtility.FromJson<CharacterListResponse>(result.Payload);
            }
            catch (Exception ex)
            {
                SetStatus($"Failed to load characters: {ex.Message}");
                return;
            }

            BuildCards(resp?.characters ?? Array.Empty<CharacterSummary>());
            SetStatus(resp != null && resp.characters != null && resp.characters.Length > 0
                ? "Pick a character, or create one."
                : "Create your first character.");
        }

        private void BuildCards(CharacterSummary[] chars)
        {
            for (int i = _listRoot.childCount - 1; i >= 0; i--)
                Destroy(_listRoot.GetChild(i).gameObject);

            const float rowH = 56f;
            for (int i = 0; i < chars.Length; i++)
            {
                var c = chars[i];

                // Row = a select button spanning the width.
                var row = MakeButton(_listRoot, "", null);
                var rrt = (RectTransform)row.transform;
                PlaceTL(rrt, 0, i * rowH, 268, rowH - 6);
                string id = c.char_id, nm = c.name; // capture for the closure
                var app = c.appearance;
                row.onClick.AddListener(() => OnSelect(id, nm, app));

                // Preview avatar.
                var av = UIFactory.MakeImage(rrt, "Avatar", null);
                PlaceTL(av.rectTransform, 6, 5, 40, 40);
                SetPreview(av, NonEmpty(app?.@class, "merchant"), NonEmpty(app?.hair, "blonde"),
                           NonEmpty(app?.skin, "default"));

                var nameT = UIFactory.MakeText(rrt, "Name", 14, UIFactory.TextColor, TextAlignmentOptions.Left);
                PlaceTL(nameT.rectTransform, 54, 8, 160, 18);
                nameT.text = string.IsNullOrEmpty(nm) ? "(unnamed)" : nm;

                var sub = UIFactory.MakeText(rrt, "Sub", 10, new Color(0.78f, 0.74f, 0.62f, 1f),
                                             TextAlignmentOptions.Left);
                PlaceTL(sub.rectTransform, 54, 28, 160, 14);
                sub.text = string.IsNullOrEmpty(c.last_zone) ? "new — never played" : $"last: {c.last_zone}";

                // Delete button (top-right of the row).
                var del = MakeButton(rrt, "X", new Color32(150, 70, 70, 255));
                PlaceTL((RectTransform)del.transform, 232, 5, 28, 28);
                del.onClick.AddListener(() => OnDelete(id, nm));
            }
        }

        // ---------------------------------------------------------------- actions

        private void OnSelect(string charId, string name, CharacterAppearance app)
        {
            CharacterSession.SelectedCharID = charId;
            CharacterSession.SelectedCharName = name;
            CharacterSession.SetAppearance(app); // the local player renders this immediately
            Debug.Log($"[CharSelect] selected {name} ({charId})");
            Hide(); // reveal the WorldMenu beneath for the zone picker
        }

        private async void OnCreate()
        {
            if (_busy) return;
            var name = (_nameInput != null ? _nameInput.text : "").Trim();
            if (string.IsNullOrEmpty(name)) { SetStatus("Enter a name."); return; }

            _busy = true;
            SetStatus($"Creating {name}...");
            try
            {
                var req = new CharacterCreateRequest
                {
                    name = name,
                    @class = Classes[_classIdx],
                    hair = Hairs[_hairIdx],
                    skin = Skins[_skinIdx],
                };
                var session = await NetworkManager.Instance.Session;
                var result = await NetworkManager.Instance.Client.RpcAsync(session, "character_create",
                    JsonUtility.ToJson(req));
                // Success returns {"character":{...}}; a validation failure returns {"error","code"}
                // (both HTTP 200). Parse the success shape — a missing char_id means it was an error.
                var created = JsonUtility.FromJson<CharacterCreateResponse>(result.Payload);
                if (created?.character == null || string.IsNullOrEmpty(created.character.char_id))
                {
                    var err = JsonUtility.FromJson<ErrorResponse>(result.Payload);
                    SetStatus($"Create failed: {(err != null && !string.IsNullOrEmpty(err.error) ? err.error : "unknown error")}");
                }
                else
                {
                    if (_nameInput != null) _nameInput.text = "";
                    await RefreshListAsync();
                }
            }
            catch (Exception ex) { SetStatus($"Create failed: {ex.Message}"); }
            finally { _busy = false; }
        }

        private async void OnDelete(string charId, string name)
        {
            if (_busy) return;
            _busy = true;
            SetStatus($"Deleting {name}...");
            try
            {
                var req = new CharacterDeleteRequest { char_id = charId };
                var session = await NetworkManager.Instance.Session;
                await NetworkManager.Instance.Client.RpcAsync(session, "character_delete", JsonUtility.ToJson(req));
                if (CharacterSession.SelectedCharID == charId)
                {
                    CharacterSession.SelectedCharID = null;
                    CharacterSession.SelectedCharName = null;
                }
                await RefreshListAsync();
            }
            catch (Exception ex) { SetStatus($"Delete failed: {ex.Message}"); }
            finally { _busy = false; }
        }

        private void Hide() { if (_canvasRoot != null) _canvasRoot.SetActive(false); }

        // ---------------------------------------------------------------- helpers

        private void SetStatus(string msg)
        {
            if (_status != null) _status.text = msg;
            Debug.Log($"[CharSelect] {msg}");
        }

        private static string NonEmpty(string v, string fallback) => string.IsNullOrEmpty(v) ? fallback : v;

        /// <summary>Place anchored to the dock's TOP-LEFT, y growing DOWN (matches InventoryPanel).</summary>
        private static void PlaceTL(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.sizeDelta = new Vector2(w, h);
            rt.anchoredPosition = new Vector2(x, -y);
        }

        private Button MakeButton(Transform parent, string label, Color? tint)
        {
            var rt = UIFactory.MakeRect(parent, $"Btn_{label}");
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = UIFactory.UISprite("panel_parchment");
            img.type = Image.Type.Sliced;
            img.color = tint ?? Color.white;
            var btn = rt.gameObject.AddComponent<Button>();
            if (!string.IsNullOrEmpty(label))
            {
                var t = UIFactory.MakeText(rt, "Label", 14, UIFactory.TextColor, TextAlignmentOptions.Center);
                UIFactory.Stretch(t.rectTransform, 2);
                t.text = label;
            }
            return btn;
        }

        /// <summary>Standard code-built single-line TMP_InputField.</summary>
        private TMP_InputField MakeInput(Transform parent, string placeholder)
        {
            var rt = UIFactory.MakeRect(parent, "NameInput");
            var bg = rt.gameObject.AddComponent<Image>();
            bg.sprite = UIFactory.UISprite("slot_frame");
            bg.type = Image.Type.Sliced;
            bg.color = new Color(0f, 0f, 0f, 0.35f);
            var input = rt.gameObject.AddComponent<TMP_InputField>();

            var viewport = UIFactory.MakeRect(rt, "TextArea");
            UIFactory.Stretch(viewport, 6);
            viewport.gameObject.AddComponent<RectMask2D>();

            var text = UIFactory.MakeText(viewport, "Text", 14, UIFactory.TextColor, TextAlignmentOptions.Left);
            UIFactory.Stretch(text.rectTransform, 0);

            var ph = UIFactory.MakeText(viewport, "Placeholder", 14, new Color(0.7f, 0.7f, 0.7f, 0.6f),
                                        TextAlignmentOptions.Left);
            UIFactory.Stretch(ph.rectTransform, 0);
            ph.text = placeholder;

            input.textViewport = viewport;
            input.textComponent = text;
            input.placeholder = ph;
            input.characterLimit = 20;
            input.lineType = TMP_InputField.LineType.SingleLine;
            return input;
        }
    }
}
