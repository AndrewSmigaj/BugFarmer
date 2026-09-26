using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    public enum SlotType { Bug, Item, Equipment }

    /// <summary>
    /// Reusable inventory slot UI component.
    /// Displays item icon and count, handles click events.
    /// </summary>
    public class InventorySlotUI : MonoBehaviour, IPointerClickHandler,
                                   IPointerEnterHandler, IPointerExitHandler
    {
        [SerializeField] private Image iconImage;
        [SerializeField] private TMP_Text countText;
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image background;
        [SerializeField] private Image ghostImage; // equipment slots: faint silhouette when empty

        /// <summary>
        /// Programmatic construction path (UIFactory.MakeSlot) — assigns the
        /// parts the prefab used to wire in the inspector.
        /// </summary>
        public void InitParts(Image icon, TMP_Text count, Image selection,
                              Image bg, Image ghost = null)
        {
            iconImage = icon;
            countText = count;
            selectionHighlight = selection;
            background = bg;
            ghostImage = ghost;
        }

        public SlotType SlotType { get; private set; }
        public int SlotIndex { get; private set; }
        public string CurrentItemId { get; private set; } = "";
        public int CurrentCount { get; private set; }

        public event Action<InventorySlotUI, PointerEventData> OnSlotClicked;

        public void Initialize(SlotType type, int index)
        {
            SlotType = type;
            SlotIndex = index;
            Clear();
        }

        public void SetSlot(InventorySlot slot)
        {
            if (slot == null || slot.IsEmpty)
            {
                Clear();
                return;
            }

            CurrentItemId = slot.item_id;
            CurrentCount = slot.count;

            if (ghostImage != null)
                ghostImage.enabled = false;

            if (iconImage != null)
            {
                var sprite = EntityDatabase.GetItemSprite(slot.item_id);
                iconImage.sprite = sprite;
                // Display sprites are now scaled-down world art with arbitrary aspect ratios
                // (a tall plant letterboxes in the square slot instead of stretching).
                iconImage.preserveAspect = true;
                iconImage.enabled = sprite != null;
                iconImage.color = Color.white; // reset any prior dim
            }

            if (countText != null)
            {
                if (slot.count > 1)
                {
                    countText.text = slot.count.ToString();
                    countText.enabled = true;
                }
                else
                {
                    countText.enabled = false;
                }
            }
        }

        /// <summary>Grey the icon (e.g. a recipe the player already knows).</summary>
        public void SetDimmed(bool dimmed)
        {
            if (iconImage != null)
                iconImage.color = dimmed ? new Color(1f, 1f, 1f, 0.32f) : Color.white;
        }

        public void SetSelected(bool selected)
        {
            if (selectionHighlight != null)
            {
                selectionHighlight.enabled = selected;
                if (selected)
                    Debug.Log($"[SlotUI] Slot {SlotIndex} selected, highlight enabled");
            }
            else if (selected)
            {
                Debug.LogWarning($"[SlotUI] Slot {SlotIndex} selected but selectionHighlight is NULL!");
            }
        }

        public void Clear()
        {
            CurrentItemId = "";
            CurrentCount = 0;

            if (iconImage != null)
            {
                iconImage.sprite = null;
                iconImage.enabled = false;
            }

            if (countText != null)
            {
                countText.enabled = false;
            }

            if (ghostImage != null)
                ghostImage.enabled = true; // empty equipment slot shows its silhouette
        }

        public void OnPointerClick(PointerEventData eventData)
        {
            OnSlotClicked?.Invoke(this, eventData);
        }

        public void OnPointerEnter(PointerEventData eventData)
        {
            if (string.IsNullOrEmpty(CurrentItemId)) return;
            var def = EntityDatabase.Get(CurrentItemId);
            TooltipUI.Instance?.Show(def?.Name ?? CurrentItemId);
        }

        public void OnPointerExit(PointerEventData eventData)
        {
            TooltipUI.Instance?.Hide();
        }
    }
}
