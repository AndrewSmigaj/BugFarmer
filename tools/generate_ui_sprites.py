#!/usr/bin/env python3
"""Generate UI sprites for Bug Farmer inventory system.

Creates slot backgrounds, panel frames, and UI icons.
Style matches existing pixel art (blocky, clear silhouettes).
"""

from PIL import Image
import os

# === COLOR PALETTES ===

T = (0, 0, 0, 0)  # Transparent

# Item Slot (brown/wood)
SLOT_ITEM_DARK = (70, 50, 35, 255)
SLOT_ITEM_MAIN = (110, 80, 55, 255)
SLOT_ITEM_LIGHT = (145, 110, 80, 255)
SLOT_ITEM_BG = (90, 70, 50, 200)

# Bug Slot (blue tinted)
SLOT_BUG_DARK = (35, 55, 80, 255)
SLOT_BUG_MAIN = (55, 85, 120, 255)
SLOT_BUG_LIGHT = (80, 115, 155, 255)
SLOT_BUG_BG = (45, 70, 100, 200)

# Selection (gold)
SELECT_DARK = (180, 140, 40, 255)
SELECT_MAIN = (220, 180, 60, 255)
SELECT_LIGHT = (255, 220, 100, 255)

# Hover (white glow)
HOVER_GLOW = (255, 255, 255, 80)

# Panel (parchment)
PANEL_DARK = (80, 70, 55, 255)
PANEL_MAIN = (200, 185, 160, 255)
PANEL_LIGHT = (230, 220, 195, 255)
PANEL_BORDER = (60, 50, 40, 255)

# Header
HEADER_DARK = (50, 45, 40, 255)
HEADER_MAIN = (90, 80, 65, 255)

# Coin
COIN_DARK = (180, 140, 40, 255)
COIN_MAIN = (230, 190, 60, 255)
COIN_LIGHT = (255, 230, 120, 255)

# Close button
CLOSE_BG = (180, 60, 60, 255)
CLOSE_X = (255, 255, 255, 255)


def create_slot(size, dark, main, light, bg):
    """Create a slot sprite with beveled border."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Fill background
    for y in range(2, size - 2):
        for x in range(2, size - 2):
            pixels[x, y] = bg

    # Top edge (light)
    for x in range(size):
        pixels[x, 0] = light
        pixels[x, 1] = light

    # Left edge (light)
    for y in range(size):
        pixels[0, y] = light
        pixels[1, y] = light

    # Bottom edge (dark)
    for x in range(size):
        pixels[x, size - 1] = dark
        pixels[x, size - 2] = dark

    # Right edge (dark)
    for y in range(size):
        pixels[size - 1, y] = dark
        pixels[size - 2, y] = dark

    # Corners (main color)
    for corner in [(0, 0), (1, 0), (0, 1), (1, 1),
                   (size-2, 0), (size-1, 0), (size-2, 1), (size-1, 1),
                   (0, size-2), (1, size-2), (0, size-1), (1, size-1),
                   (size-2, size-2), (size-1, size-2), (size-2, size-1), (size-1, size-1)]:
        pixels[corner[0], corner[1]] = main

    return img


def create_selection_overlay(size):
    """Create gold selection border overlay."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    border = 3

    # Draw thick gold border
    for i in range(border):
        # Top
        for x in range(size):
            pixels[x, i] = SELECT_MAIN
        # Bottom
        for x in range(size):
            pixels[x, size - 1 - i] = SELECT_MAIN
        # Left
        for y in range(size):
            pixels[i, y] = SELECT_MAIN
        # Right
        for y in range(size):
            pixels[size - 1 - i, y] = SELECT_MAIN

    # Inner highlight
    for x in range(border, size - border):
        pixels[x, border] = SELECT_LIGHT
    for y in range(border, size - border):
        pixels[border, y] = SELECT_LIGHT

    # Outer shadow
    for x in range(size):
        pixels[x, size - 1] = SELECT_DARK
    for y in range(size):
        pixels[size - 1, y] = SELECT_DARK

    return img


def create_hover_overlay(size):
    """Create subtle white glow overlay."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Fill with semi-transparent white, leaving border
    for y in range(2, size - 2):
        for x in range(2, size - 2):
            pixels[x, y] = HOVER_GLOW

    return img


def create_panel(width, height):
    """Create panel background with border."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    border = 4

    # Fill main area
    for y in range(border, height - border):
        for x in range(border, width - border):
            pixels[x, y] = PANEL_MAIN

    # Border
    for i in range(border):
        for x in range(width):
            pixels[x, i] = PANEL_BORDER
            pixels[x, height - 1 - i] = PANEL_BORDER
        for y in range(height):
            pixels[i, y] = PANEL_BORDER
            pixels[width - 1 - i, y] = PANEL_BORDER

    # Inner highlight (top-left)
    for x in range(border, width - border):
        pixels[x, border] = PANEL_LIGHT
        pixels[x, border + 1] = PANEL_LIGHT
    for y in range(border, height - border):
        pixels[border, y] = PANEL_LIGHT
        pixels[border + 1, y] = PANEL_LIGHT

    # Inner shadow (bottom-right)
    for x in range(border, width - border):
        pixels[x, height - border - 1] = PANEL_DARK
        pixels[x, height - border - 2] = PANEL_DARK
    for y in range(border, height - border):
        pixels[width - border - 1, y] = PANEL_DARK
        pixels[width - border - 2, y] = PANEL_DARK

    return img


def create_header(width, height):
    """Create section header bar."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    # Fill
    for y in range(height):
        for x in range(width):
            if y < 2:
                pixels[x, y] = HEADER_DARK
            elif y >= height - 2:
                pixels[x, y] = HEADER_DARK
            else:
                pixels[x, y] = HEADER_MAIN

    return img


def create_coin_icon(size):
    """Create gold coin icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Simple circular coin
    center = size // 2
    radius = size // 2 - 1

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist_sq = dx * dx + dy * dy

            if dist_sq <= radius * radius:
                # Inside coin
                if dist_sq <= (radius - 2) * (radius - 2):
                    # Inner area - gradient based on position
                    if dx + dy < 0:
                        pixels[x, y] = COIN_LIGHT
                    else:
                        pixels[x, y] = COIN_MAIN
                else:
                    # Edge
                    pixels[x, y] = COIN_DARK

    # Add $ or C symbol (simple lines)
    mid = size // 2
    # Vertical line
    for y in range(mid - 3, mid + 4):
        if 0 <= y < size:
            pixels[mid, y] = COIN_DARK
    # Top horizontal
    if mid - 2 >= 0 and mid + 2 < size:
        pixels[mid - 1, mid - 2] = COIN_DARK
        pixels[mid + 1, mid - 2] = COIN_DARK
    # Bottom horizontal
    if mid + 2 < size:
        pixels[mid - 1, mid + 2] = COIN_DARK
        pixels[mid + 1, mid + 2] = COIN_DARK

    return img


def create_close_icon(size):
    """Create X close button."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Red background circle
    center = size // 2
    radius = size // 2 - 1

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            if dx * dx + dy * dy <= radius * radius:
                pixels[x, y] = CLOSE_BG

    # White X
    for i in range(size // 4, size - size // 4):
        offset = i
        inv_offset = size - 1 - i
        if 0 <= offset < size and 0 <= inv_offset < size:
            pixels[i, i] = CLOSE_X
            pixels[i, size - 1 - i] = CLOSE_X
            # Thicken
            if i + 1 < size:
                pixels[i + 1, i] = CLOSE_X
                pixels[i, i + 1] = CLOSE_X if i + 1 < size else CLOSE_X
                pixels[i + 1, size - 1 - i] = CLOSE_X
                pixels[i, size - 2 - i] = CLOSE_X if size - 2 - i >= 0 else CLOSE_X

    return img


def create_popup_bg(width, height):
    """Create background for catch popup."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    # Semi-transparent dark background with border
    bg_color = (40, 35, 30, 200)
    border_color = (80, 70, 55, 255)

    # Fill
    for y in range(height):
        for x in range(width):
            if x < 2 or x >= width - 2 or y < 2 or y >= height - 2:
                pixels[x, y] = border_color
            else:
                pixels[x, y] = bg_color

    return img


def create_cursor_grab(size):
    """Create cursor for dragging items."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Simple hand/grab cursor shape
    # Just a small square frame for now
    border = 2
    frame_color = (255, 255, 255, 200)

    for i in range(border):
        for x in range(size):
            pixels[x, i] = frame_color
            pixels[x, size - 1 - i] = frame_color
        for y in range(size):
            pixels[i, y] = frame_color
            pixels[size - 1 - i, y] = frame_color

    return img


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/UI"
    os.makedirs(output_dir, exist_ok=True)

    # Slots (32x32)
    slot_size = 32

    slot_item = create_slot(slot_size, SLOT_ITEM_DARK, SLOT_ITEM_MAIN, SLOT_ITEM_LIGHT, SLOT_ITEM_BG)
    slot_item.save(f"{output_dir}/slot_item.png")
    print(f"Created: {output_dir}/slot_item.png")

    slot_bug = create_slot(slot_size, SLOT_BUG_DARK, SLOT_BUG_MAIN, SLOT_BUG_LIGHT, SLOT_BUG_BG)
    slot_bug.save(f"{output_dir}/slot_bug.png")
    print(f"Created: {output_dir}/slot_bug.png")

    slot_selected = create_selection_overlay(slot_size)
    slot_selected.save(f"{output_dir}/slot_selected.png")
    print(f"Created: {output_dir}/slot_selected.png")

    slot_hover = create_hover_overlay(slot_size)
    slot_hover.save(f"{output_dir}/slot_hover.png")
    print(f"Created: {output_dir}/slot_hover.png")

    # Panels
    panel_inventory = create_panel(256, 192)
    panel_inventory.save(f"{output_dir}/panel_inventory.png")
    print(f"Created: {output_dir}/panel_inventory.png")

    panel_shop = create_panel(320, 224)
    panel_shop.save(f"{output_dir}/panel_shop.png")
    print(f"Created: {output_dir}/panel_shop.png")

    panel_header = create_header(128, 24)
    panel_header.save(f"{output_dir}/panel_header.png")
    print(f"Created: {output_dir}/panel_header.png")

    # Icons
    icon_coin = create_coin_icon(16)
    icon_coin.save(f"{output_dir}/icon_coin.png")
    print(f"Created: {output_dir}/icon_coin.png")

    icon_close = create_close_icon(16)
    icon_close.save(f"{output_dir}/icon_close.png")
    print(f"Created: {output_dir}/icon_close.png")

    # Effects
    popup_bg = create_popup_bg(64, 24)
    popup_bg.save(f"{output_dir}/popup_bg.png")
    print(f"Created: {output_dir}/popup_bg.png")

    cursor_grab = create_cursor_grab(32)
    cursor_grab.save(f"{output_dir}/cursor_grab.png")
    print(f"Created: {output_dir}/cursor_grab.png")

    print(f"\nCreated 11 UI sprites in {output_dir}")
    print("\nUnity import settings:")
    print("  - Texture Type: Sprite (2D and UI)")
    print("  - Sprite Mode: Single")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
