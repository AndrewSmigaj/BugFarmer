using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.Player;
using BugFarmer.World;

namespace BugFarmer.UI
{
    /// <summary>
    /// The NURSERY-STATION panel: right-click a breeding station (wasp nest / milkweed today; compost bin
    /// + the wild egg-brood object come later) to OPEN it and see its brood — egg / larva / [pupa] counts
    /// with each stage's sprite as inventory-square slots — plus the resident adults living inside and a
    /// conversion bar. "A brood IS a nursery station": one object you open, not a sprite pile on the world.
    ///
    /// DISPLAY-ONLY: fed by the server's OpCode-104 BroodUpdate (the real births ride the deterministic
    /// SWARM_REPRODUCED ledger), so nothing here touches the sim or the state hash — a dropped/late update
    /// only delays the on-screen count. Latest brood per cell is cached even while closed (the data role the
    /// old BroodManager held) so opening a station shows its current brood instantly + it updates live.
    ///
    /// This is the FUNCTIONAL PLACEHOLDER. Take/random-harvest (S3), residents at the compost bin, and the
    /// owner's visual/UI-mockup polish come later. Mirrors CraftingPanel (code-built Canvas, InventorySlotUI
    /// slots, the ReceivedMatchState subscription).
    /// </summary>
    public class NurseryPanel : MonoBehaviour
    {
        public static NurseryPanel Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 2.5f;
        private const float BarWidth = 180f;

        // Latest brood per station cell — cached even while CLOSED so opening a station shows its current
        // brood immediately (the OpCode-104 stream arrives whenever we're subscribed to the chunk).
        private readonly Dictionary<Vector2Int, BroodUpdateMessage> _broods = new Dictionary<Vector2Int, BroodUpdateMessage>();

        private bool _isOpen;
        private Vector2Int _cell;
        private string _occupantId = "";

        // UI frame
        private CanvasGroup _group;
        private RectTransform _dock;
        private RectTransform _content; // rebuilt per open
        private TMP_Text _title;

        // Content (rebuilt per open)
        private RectTransform _broodGroup;                 // everything shown when a brood exists
        private readonly List<InventorySlotUI> _stageSlots = new List<InventorySlotUI>();
        private readonly List<TMP_Text> _stageCounts = new List<TMP_Text>();
        private InventorySlotUI _residentSlot;
        private TMP_Text _residentLabel;
        private TMP_Text _emptyLabel;                      // shown when there's no developing brood
        private Image _barFill;
        private float _barShown;                           // interpolated bar fraction (smooths the ~3s steps)
        private float _barTarget;                          // latest server progress (0..1)

        private static readonly string[] StageNames = { "eggs", "larvae", "pupae" };

        // ---------------------------------------------------------------- lifecycle

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);

            _dock = UIFactory.MakeDock(transform, "NurseryDock", new Vector2(0.5f, 1f),
                                       new Vector2(0.5f, 1f), new Vector2(320, 210), new Vector2(0, -8));
            _group = _dock.gameObject.AddComponent<CanvasGroup>();

            _title = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize + 2f,
                                        UIFactory.HeaderColor, TextAlignmentOptions.Center);
            Place(_title.rectTransform, 0, -8, 320, 20, new Vector2(0.5f, 1f), new Vector2(0.5f, 1f));

            _content = UIFactory.MakeRect(_dock, "Content");
            UIFactory.Stretch(_content, 12);
            ((RectTransform)_content).offsetMax = new Vector2(-12, -34); // leave room for the title

            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState += OnMatchState;

            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            var net = NetworkManager.Instance;
            if (net?.Socket != null)
                net.Socket.ReceivedMatchState -= OnMatchState;
        }

        private void Update()
        {
            if (!_isOpen) return;
            if (Input.GetKeyDown(KeyCode.Escape)) { SetOpen(false); return; }
            // Smoothly animate the conversion bar toward the latest server progress (arrives ~every 3s).
            _barShown = Mathf.MoveTowards(_barShown, _barTarget, Time.deltaTime * 2f);
            ApplyBar();
        }

        // ---------------------------------------------------------------- open / route

        /// <summary>
        /// Routed right-click (PlayerInputRouter). Opens the nursery panel for a station whose
        /// interaction_type is "nursery"; closes an open panel when the click lands elsewhere. Returns
        /// TRUE on any state transition (so the click is consumed and never also jabs/places).
        /// </summary>
        public bool TryHandleRightClick(Vector3 mouseWorld)
        {
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null)
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World?.InteractionType != "nursery")
            {
                if (_isOpen) { SetOpen(false); return true; }
                return false;
            }

            // Range check (server has no take-op yet; the open is client-only, but keep the reach rule
            // consistent with other stations).
            var player = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                var d = (Vector2)player.transform.position -
                        new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
                if (d.sqrMagnitude > MaxInteractDistance * MaxInteractDistance)
                    return false;
            }

            // Toggle if re-clicking the same open station; otherwise (re)open for this cell.
            if (_isOpen && _cell == target.AnchorCell) { SetOpen(false); return true; }

            _cell = target.AnchorCell;
            _occupantId = target.OccupantId;
            Open();
            return true;
        }

        private void Open()
        {
            _title.text = (EntityDatabase.Get(_occupantId)?.Name) ?? _occupantId;
            BuildContent();
            SetOpen(true);
            Refresh();
            _barShown = _barTarget; // snap on open; only live updates animate
            ApplyBar();
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

        // ---------------------------------------------------------------- build content

        private void BuildContent()
        {
            for (int i = _content.childCount - 1; i >= 0; i--)
                DestroyImmediate(_content.GetChild(i).gameObject);
            _stageSlots.Clear();
            _stageCounts.Clear();
            _residentSlot = null;
            _residentLabel = null;
            _emptyLabel = null;
            _barFill = null;

            // Empty-state label (shown when no brood is developing).
            _emptyLabel = UIFactory.MakeText(_content, "Empty", UIFactory.CountSize + 1f,
                                             UIFactory.TextColor, TextAlignmentOptions.TopLeft);
            Place(_emptyLabel.rectTransform, 0, -4, 290, 40);
            _emptyLabel.enableWordWrapping = true;
            _emptyLabel.text = "No brood developing here right now.";
            _emptyLabel.enabled = false;

            // Brood group — all the live-brood widgets, toggled as a unit.
            _broodGroup = UIFactory.MakeRect(_content, "BroodGroup");
            UIFactory.Stretch(_broodGroup, 0);

            var head = UIFactory.MakeText(_broodGroup, "BroodHead", UIFactory.HeaderSize,
                                          UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(head.rectTransform, 0, 0, 200, 16);
            head.text = "BROOD";

            // egg / larva / pupa slots + a count label under each (always shows the number, incl. 0).
            for (int i = 0; i < 3; i++)
            {
                var s = UIFactory.MakeSlot(_broodGroup, "slot_frame");
                Place((RectTransform)s.transform, i * 52, -20, UIFactory.Slot, UIFactory.Slot);
                _stageSlots.Add(s);
                var lbl = UIFactory.MakeText(_broodGroup, $"Stage{i}Lbl", UIFactory.CountSize,
                                             UIFactory.TextColor, TextAlignmentOptions.Center);
                Place(lbl.rectTransform, i * 52 - 6, -62, UIFactory.Slot + 12, 14);
                _stageCounts.Add(lbl);
            }

            // conversion bar
            var barHead = UIFactory.MakeText(_broodGroup, "BarHead", UIFactory.CountSize,
                                             UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(barHead.rectTransform, 0, -84, 200, 14);
            barHead.text = "MATURING";
            var barBg = UIFactory.MakeImage(_broodGroup, "BarBg", "slot_frame", true);
            barBg.color = new Color(0f, 0f, 0f, 0.4f);
            Place(barBg.rectTransform, 0, -100, BarWidth + 4, 14);
            _barFill = UIFactory.MakeImage(_broodGroup, "BarFill", null);
            _barFill.color = new Color(0.55f, 0.85f, 0.4f, 1f);
            Place(_barFill.rectTransform, 2, -102, 0, 10);

            // residents ("the adults hanging out inside")
            var resHead = UIFactory.MakeText(_broodGroup, "ResHead", UIFactory.CountSize,
                                             UIFactory.HeaderColor, TextAlignmentOptions.Left);
            Place(resHead.rectTransform, 0, -122, 200, 14);
            resHead.text = "INSIDE";
            _residentSlot = UIFactory.MakeSlot(_broodGroup, "slot_frame");
            Place((RectTransform)_residentSlot.transform, 0, -138, UIFactory.Slot, UIFactory.Slot);
            _residentLabel = UIFactory.MakeText(_broodGroup, "ResLbl", UIFactory.CountSize + 1f,
                                                UIFactory.TextColor, TextAlignmentOptions.Left);
            Place(_residentLabel.rectTransform, 46, -150, 240, 16);
        }

        // ---------------------------------------------------------------- data / refresh

        private void OnMatchState(Nakama.IMatchState state)
        {
            if (state.OpCode != OpCodes.BroodUpdate) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<BroodUpdateMessage>(json);
            if (msg == null) return;

            var cell = new Vector2Int(msg.gx, msg.gy);
            if (msg.removed || (msg.eggs + msg.maggots + msg.pupae + msg.residents) <= 0)
                _broods.Remove(cell);
            else
                _broods[cell] = msg;

            if (_isOpen && cell == _cell) Refresh();
        }

        private void Refresh()
        {
            _broods.TryGetValue(_cell, out var b);
            bool has = b != null;

            if (_emptyLabel != null) _emptyLabel.enabled = !has;
            if (_broodGroup != null) _broodGroup.gameObject.SetActive(has);
            if (!has) { _barTarget = 0f; return; }

            var sp = EntityDatabase.GetSpecies(b.species);
            int[] counts = { b.eggs, b.maggots, b.pupae };
            string[] spriteIds =
            {
                sp?.EggSpriteId ?? "",
                sp?.LarvaSpriteId ?? "",
                sp?.PupaSpriteId ?? "",
            };

            for (int i = 0; i < _stageSlots.Count; i++)
            {
                bool stageExists = !string.IsNullOrEmpty(spriteIds[i]);
                _stageSlots[i].gameObject.SetActive(stageExists);
                _stageCounts[i].enabled = stageExists;
                if (!stageExists) continue;
                if (counts[i] > 0) _stageSlots[i].SetSlot(new InventorySlot(spriteIds[i], counts[i]));
                else _stageSlots[i].Clear();
                _stageCounts[i].text = $"{StageNames[i]}: {counts[i]}";
            }

            _barTarget = Mathf.Clamp01(b.progress);

            int residents = b.residents;
            bool showRes = residents > 0;
            _residentSlot.gameObject.SetActive(showRes);
            _residentLabel.enabled = showRes;
            if (showRes)
            {
                _residentSlot.SetSlot(new InventorySlot(b.species, residents));
                _residentLabel.text = $"× {residents} {(string.IsNullOrEmpty(sp?.Name) ? b.species : sp.Name)}";
            }
        }

        private void ApplyBar()
        {
            if (_barFill == null) return;
            var rt = _barFill.rectTransform;
            rt.sizeDelta = new Vector2(BarWidth * Mathf.Clamp01(_barShown), rt.sizeDelta.y);
        }

        // ---------------------------------------------------------------- helpers

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f); // top-left of content
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
