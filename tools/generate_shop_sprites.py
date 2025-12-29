#!/usr/bin/env python3
"""Generate shop-related sprites for Bug Farmer.

Creates shop stall, shopkeeper NPC, speech bubble, and price tag.
"""

from PIL import Image
import os

# === COLOR PALETTES ===

T = (0, 0, 0, 0)  # Transparent

# Wood (stall)
STALL_DARK = (70, 50, 35, 255)
STALL_MAIN = (120, 90, 60, 255)
STALL_LIGHT = (160, 130, 95, 255)

# Awning (red)
AWNING_DARK = (100, 35, 35, 255)
AWNING_MAIN = (150, 55, 55, 255)
AWNING_LIGHT = (180, 80, 80, 255)

# Shopkeeper (reuse player colors mostly)
SKIN = (255, 220, 180, 255)
SKIN_SHADOW = (235, 195, 155, 255)
HAIR = (60, 45, 35, 255)
HAIR_LIGHT = (90, 70, 55, 255)
EYE = (35, 30, 30, 255)
APRON_DARK = (140, 45, 35, 255)
APRON_MAIN = (180, 70, 55, 255)
SHIRT = (240, 235, 220, 255)
SHIRT_SHADOW = (210, 200, 180, 255)
PANTS = (65, 55, 80, 255)
SHOES = (90, 75, 55, 255)
OUTLINE = (35, 25, 25, 255)

# Speech bubble
BUBBLE_BG = (255, 255, 255, 240)
BUBBLE_BORDER = (80, 80, 80, 255)

# Price tag
TAG_BG = (255, 250, 220, 255)
TAG_BORDER = (180, 140, 80, 255)


def create_shop_stall(width, height):
    """Create wooden shop counter with red awning."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    # Awning (top portion) - striped
    awning_height = 16
    for y in range(awning_height):
        for x in range(width):
            # Striped pattern
            stripe = (x // 8) % 2
            if stripe == 0:
                if y < 3:
                    pixels[x, y] = AWNING_LIGHT
                elif y > awning_height - 3:
                    pixels[x, y] = AWNING_DARK
                else:
                    pixels[x, y] = AWNING_MAIN
            else:
                if y < 3:
                    pixels[x, y] = AWNING_MAIN
                elif y > awning_height - 3:
                    pixels[x, y] = AWNING_DARK
                else:
                    pixels[x, y] = AWNING_DARK

    # Awning edge (scalloped bottom)
    for x in range(width):
        wave = (x % 8) < 4
        if wave:
            pixels[x, awning_height] = AWNING_DARK
            if awning_height + 1 < height:
                pixels[x, awning_height + 1] = AWNING_DARK

    # Counter (main body)
    counter_top = awning_height + 4
    counter_height = height - counter_top

    for y in range(counter_top, height):
        for x in range(width):
            # Left edge
            if x < 4:
                pixels[x, y] = STALL_DARK
            # Right edge
            elif x >= width - 4:
                pixels[x, y] = STALL_DARK
            # Top surface (lighter)
            elif y < counter_top + 6:
                if x < width // 3:
                    pixels[x, y] = STALL_MAIN
                elif x < 2 * width // 3:
                    pixels[x, y] = STALL_LIGHT
                else:
                    pixels[x, y] = STALL_MAIN
            # Front panel
            else:
                # Vertical planks
                plank = (x // 10) % 2
                if plank == 0:
                    pixels[x, y] = STALL_MAIN
                else:
                    pixels[x, y] = STALL_LIGHT

    # Plank lines (vertical)
    for x in range(10, width - 4, 10):
        for y in range(counter_top + 6, height):
            if 0 <= x < width:
                pixels[x, y] = STALL_DARK

    # Counter edge highlight
    for x in range(4, width - 4):
        pixels[x, counter_top] = STALL_LIGHT
        pixels[x, counter_top + 1] = STALL_LIGHT

    # Support posts
    post_width = 6
    for y in range(awning_height, counter_top):
        # Left post
        for x in range(post_width):
            if x < 2:
                pixels[x, y] = STALL_DARK
            elif x > post_width - 2:
                pixels[x, y] = STALL_LIGHT
            else:
                pixels[x, y] = STALL_MAIN

        # Right post
        for x in range(width - post_width, width):
            offset = x - (width - post_width)
            if offset < 2:
                pixels[x, y] = STALL_DARK
            elif offset > post_width - 2:
                pixels[x, y] = STALL_LIGHT
            else:
                pixels[x, y] = STALL_MAIN

    return img


def create_shopkeeper(size):
    """Create front-facing shopkeeper with apron."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Use grid-based approach like player sprites
    # 16x16 grid, each cell = 2x2 pixels for 32x32 output

    O = OUTLINE
    H = HAIR
    h = HAIR_LIGHT
    S = SKIN
    D = SKIN_SHADOW
    E = EYE
    W = SHIRT  # White shirt
    w = SHIRT_SHADOW
    A = APRON_MAIN
    a = APRON_DARK
    P = PANTS
    K = SHOES

    # 16x16 grid for shopkeeper facing down (toward camera)
    grid = [
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
        [T, T, T, T, T, T, O, O, O, O, T, T, T, T, T, T],
        [T, T, T, T, T, O, H, H, H, H, O, T, T, T, T, T],
        [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
        [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
        [T, T, T, T, O, S, S, S, S, S, S, O, T, T, T, T],
        [T, T, T, T, O, S, E, S, S, E, S, O, T, T, T, T],
        [T, T, T, T, O, S, S, D, D, S, S, O, T, T, T, T],
        [T, T, T, T, T, O, S, S, S, S, O, T, T, T, T, T],
        [T, T, T, T, T, T, O, S, S, O, T, T, T, T, T, T],
        [T, T, T, T, T, O, W, W, W, W, O, T, T, T, T, T],
        [T, T, T, T, O, A, A, a, a, A, A, O, T, T, T, T],  # Apron
        [T, T, T, T, O, A, A, a, a, A, A, O, T, T, T, T],  # Apron
        [T, T, T, T, T, O, P, P, P, P, O, T, T, T, T, T],
        [T, T, T, T, T, O, P, P, P, P, O, T, T, T, T, T],
        [T, T, T, T, T, O, K, O, O, K, O, T, T, T, T, T],
    ]

    # Draw grid (each cell = 2x2 pixels)
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            px, py = x * 2, y * 2
            if px < size and py < size:
                pixels[px, py] = color
                if px + 1 < size:
                    pixels[px + 1, py] = color
                if py + 1 < size:
                    pixels[px, py + 1] = color
                if px + 1 < size and py + 1 < size:
                    pixels[px + 1, py + 1] = color

    return img


def create_speech_bubble(width, height):
    """Create speech bubble for 'Press E to Shop'."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    # Main bubble (rounded rectangle)
    bubble_bottom = height - 8  # Leave room for tail

    for y in range(bubble_bottom):
        for x in range(width):
            # Round corners
            corner_radius = 4
            in_corner = False

            # Top-left
            if x < corner_radius and y < corner_radius:
                dx = corner_radius - x
                dy = corner_radius - y
                if dx * dx + dy * dy > corner_radius * corner_radius:
                    in_corner = True
            # Top-right
            if x >= width - corner_radius and y < corner_radius:
                dx = x - (width - corner_radius - 1)
                dy = corner_radius - y
                if dx * dx + dy * dy > corner_radius * corner_radius:
                    in_corner = True
            # Bottom-left
            if x < corner_radius and y >= bubble_bottom - corner_radius:
                dx = corner_radius - x
                dy = y - (bubble_bottom - corner_radius - 1)
                if dx * dx + dy * dy > corner_radius * corner_radius:
                    in_corner = True
            # Bottom-right
            if x >= width - corner_radius and y >= bubble_bottom - corner_radius:
                dx = x - (width - corner_radius - 1)
                dy = y - (bubble_bottom - corner_radius - 1)
                if dx * dx + dy * dy > corner_radius * corner_radius:
                    in_corner = True

            if not in_corner:
                # Border or fill
                if x < 2 or x >= width - 2 or y < 2 or y >= bubble_bottom - 2:
                    pixels[x, y] = BUBBLE_BORDER
                else:
                    pixels[x, y] = BUBBLE_BG

    # Speech tail (pointing down)
    tail_x = width // 2
    for i in range(6):
        ty = bubble_bottom + i
        if ty < height:
            for dx in range(-3 + i // 2, 4 - i // 2):
                tx = tail_x + dx
                if 0 <= tx < width:
                    if abs(dx) == 3 - i // 2:
                        pixels[tx, ty] = BUBBLE_BORDER
                    else:
                        pixels[tx, ty] = BUBBLE_BG

    return img


def create_price_tag(width, height):
    """Create price display background."""
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            # Border
            if x < 2 or x >= width - 2 or y < 2 or y >= height - 2:
                pixels[x, y] = TAG_BORDER
            else:
                pixels[x, y] = TAG_BG

    # Notch on left (tag hole area)
    notch_y = height // 2
    for dy in range(-2, 3):
        ny = notch_y + dy
        if 0 <= ny < height:
            pixels[0, ny] = T
            pixels[1, ny] = T
            if abs(dy) < 2:
                pixels[2, ny] = TAG_BORDER

    return img


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Shop"
    os.makedirs(output_dir, exist_ok=True)

    # Shop stall (64x48)
    stall = create_shop_stall(64, 48)
    stall.save(f"{output_dir}/shop_stall.png")
    print(f"Created: {output_dir}/shop_stall.png")

    # Shopkeeper (32x32)
    shopkeeper = create_shopkeeper(32)
    shopkeeper.save(f"{output_dir}/npc_shopkeeper.png")
    print(f"Created: {output_dir}/npc_shopkeeper.png")

    # Speech bubble (48x32)
    bubble = create_speech_bubble(48, 32)
    bubble.save(f"{output_dir}/speech_bubble.png")
    print(f"Created: {output_dir}/speech_bubble.png")

    # Price tag (24x16)
    tag = create_price_tag(24, 16)
    tag.save(f"{output_dir}/price_tag.png")
    print(f"Created: {output_dir}/price_tag.png")

    print(f"\nCreated 4 shop sprites in {output_dir}")
    print("\nUnity import settings:")
    print("  - Texture Type: Sprite (2D and UI)")
    print("  - Sprite Mode: Single")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
