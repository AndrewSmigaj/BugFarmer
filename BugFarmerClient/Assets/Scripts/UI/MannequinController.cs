using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.Player;
using BugFarmer.World;

namespace BugFarmer.UI
{
    /// <summary>
    /// MANNEQUINS — right-click a "mannequin" occupant to open its OUTFIT panel: a column of equipment
    /// slots (head / body / arms / legs / feet) you fill with clothing & armor to dress it up. The
    /// mannequin is a filtered ContainerState on the server (filter "clothing"), so this reuses the exact
    /// container protocol (ContainerActionMessage open/move/quick → ContainerUpdate echo) — no new server
    /// handler. Moving an item mirrors CraftingPanel's storage flow (cursor stack → click a slot). The
    /// mannequin SPRITE composing the worn outfit (a paper-doll like RemoteEntity) is the follow-up
    /// (body layers authored; see BACKLOG "mannequin render Increment-A/B"). Canvas/UIFactory, violet accent.
    /// </summary>
    public class MannequinController : MonoBehaviour
    {
        public static MannequinController Instance { get; private set; }
        public static bool IsOpen => Instance != null && Instance._isOpen;

        private const float MaxInteractDistance = 2.5f;
        private static readonly Color Accent = new Color32(150, 112, 170, 235);

        // 5 equipment slots (server container index → ghost silhouette).
        private static readonly (int slot, string ghost, float x, float y)[] Slots =
        {
            (0, "ghost_head", 86, -8), (1, "ghost_body", 86, -56),
            (2, "ghost_arms", 40, -56), (3, "ghost_legs", 86, -104), (4, "ghost_feet", 86, -152),
        };

        private bool _isOpen, _openedInventory;
        private Vector2Int _cell;
        private string _occId = "";
        private CanvasGroup _group;
        private RectTransform _dock, _content;
        private TMP_Text _title;
        private readonly List<InventorySlotUI> _equip = new List<InventorySlotUI>();
        private ContainerUpdateMessage _last;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            UIFactory.Stretch((RectTransform)transform, 0);
            _dock = UIFactory.MakeDock(transform, "MannDock", new Vector2(0.5f, 1f),
                                       new Vector2(0.5f, 1f), new Vector2(220, 240), new Vector2(0, -8));
            _group = _dock.gameObject.AddComponent<CanvasGroup>();
            var head = UIFactory.MakeImage(_dock, "Header", "panel_wood", true);
            head.color = Accent;
            Place(head.rectTransform, 8, -8, 204, 24);
            _title = UIFactory.MakeText(_dock, "Title", UIFactory.HeaderSize, new Color32(238, 228, 204, 255),
                                        TextAlignmentOptions.Left);
            Place(_title.rectTransform, 16, -11, 190, 18);
            _title.text = "Mannequin — Outfit";
            _content = UIFactory.MakeRect(_dock, "Content");
            UIFactory.Stretch(_content, 12);
            ((RectTransform)_content).offsetMax = new Vector2(-12, -36);

            foreach (var c in Slots)
            {
                var s = UIFactory.MakeSlot(_content, "slot_frame_equip", c.ghost);
                Place((RectTransform)s.transform, c.x, c.y, UIFactory.EquipSlot, UIFactory.EquipSlot);
                int idx = c.slot;
                s.OnSlotClicked += (slot, ev) => OnSlotClicked(idx, ev);
                _equip.Add(s);
            }
            var hint = UIFactory.MakeText(_content, "Hint", UIFactory.CountSize,
                                          new Color32(150, 140, 126, 255), TextAlignmentOptions.Left);
            Place(hint.rectTransform, 8, -208, 196, 14);
            hint.text = "Drag clothing from your bag";

            var net = NetworkManager.Instance;
            if (net?.Socket != null) net.Socket.ReceivedMatchState += OnMatchState;
            SetOpen(false);
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
            var net = NetworkManager.Instance;
            if (net?.Socket != null) net.Socket.ReceivedMatchState -= OnMatchState;
        }

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
            if (def?.World == null || def.World.InteractionType != "mannequin")
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
            if (_isOpen && _cell == target.AnchorCell) { SetOpen(false); return true; }
            _cell = target.AnchorCell;
            _occId = target.OccupantId;
            _last = null;
            // open the inventory too, so you can drag clothing into the slots
            if (InventoryPanel.Instance != null && !InventoryPanel.IsOpen)
            {
                _openedInventory = true;
                InventoryPanel.Instance.SetOpen(true);
            }
            RefreshSlots();
            SetOpen(true);
            Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "open" });
            return true;
        }

        // cursor-held clothing → deposit; else quick-move the worn item back to the bag.
        private void OnSlotClicked(int idx, PointerEventData ev)
        {
            var drag = DragDropController.Instance;
            if (drag != null && drag.HasCursorItem && drag.CursorSourceType == SlotType.Item)
            {
                Send(new ContainerActionMessage
                {
                    gx = _cell.x, gy = _cell.y, op = "move",
                    zone = "player", slot = drag.CursorSourceIndex,
                    to_zone = "container", to_slot = idx, count = 1
                });
                drag.ForceClearCursor();
                return;
            }
            if (ev.clickCount >= 2 || Input.GetKey(KeyCode.LeftShift))
                Send(new ContainerActionMessage { gx = _cell.x, gy = _cell.y, op = "quick", zone = "container", slot = idx });
        }

        private void OnMatchState(Nakama.IMatchState state)
        {
            if (state.OpCode != OpCodes.ContainerUpdate) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<ContainerUpdateMessage>(json);
            if (msg == null || msg.gx != _cell.x || msg.gy != _cell.y || !_isOpen) return;
            _last = msg;
            RefreshSlots();
        }

        private void RefreshSlots()
        {
            for (int i = 0; i < _equip.Count; i++)
            {
                int si = Slots[i].slot;
                if (_last?.slots != null && si < _last.slots.Length) _equip[i].SetSlot(_last.slots[si]);
                else _equip[i].Clear();
            }
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
            if (!open && _openedInventory)
            {
                _openedInventory = false;
                InventoryPanel.Instance?.SetOpen(false);
            }
        }

        private static void Place(RectTransform rt, float x, float y, float w, float h)
        {
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(x, y);
            rt.sizeDelta = new Vector2(w, h);
        }

        private void Send(ContainerActionMessage msg)
        {
            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected) return;
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.Container, JsonUtility.ToJson(msg));
        }
    }
}
