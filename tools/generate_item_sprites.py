#!/usr/bin/env python3
"""Generate item icons for Bug Farmer inventory display.

Creates 24x24 icons for tools and bugs.
These are cleaner versions optimized for UI display.
"""

from PIL import Image
import os

# === COLOR PALETTES ===

T = (0, 0, 0, 0)  # Transparent

# Tool handle (wood)
HANDLE_DARK = (70, 50, 35, 255)
HANDLE_MAIN = (120, 90, 60, 255)
HANDLE_LIGHT = (160, 130, 95, 255)

# Metal
METAL_DARK = (80, 85, 90, 255)
METAL_MAIN = (140, 145, 150, 255)
METAL_LIGHT = (200, 205, 210, 255)

# Net mesh
NET_DARK = (60, 100, 80, 255)
NET_MAIN = (100, 160, 130, 255)
NET_MESH = (150, 200, 170, 180)  # semi-transparent

# Spray bottle
SPRAY_DARK = (40, 80, 100, 255)
SPRAY_MAIN = (80, 140, 170, 255)
SPRAY_LIGHT = (140, 200, 220, 255)
SPRAY_LIQUID = (180, 255, 200, 200)

# Fly
FLY_DARK = (30, 25, 25, 255)
FLY_MAIN = (60, 55, 50, 255)
FLY_WING = (180, 200, 220, 150)
FLY_EYE = (180, 40, 40, 255)

# Fly eggs
EGG_DARK = (200, 190, 170, 255)
EGG_MAIN = (240, 235, 220, 255)
EGG_LIGHT = (255, 255, 250, 255)

# Bee
BEE_DARK = (35, 30, 20, 255)
BEE_YELLOW = (230, 190, 50, 255)
BEE_LIGHT = (255, 220, 100, 255)
BEE_WING = (200, 220, 240, 150)

# Beetle
BEETLE_DARK = (20, 50, 35, 255)
BEETLE_MAIN = (45, 120, 80, 255)
BEETLE_LIGHT = (80, 180, 120, 255)

# Butterfly
BUTTERFLY_BODY = (60, 50, 50, 255)
BUTTERFLY_WING1 = (160, 80, 180, 255)
BUTTERFLY_WING2 = (240, 140, 60, 255)
BUTTERFLY_SPOTS = (255, 255, 255, 255)


def create_small_net(size):
    """Create small butterfly net icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    # Net hoop (top portion)
    center_x = size // 2
    hoop_y = 6
    hoop_radius = 7

    # Draw hoop rim
    for angle in range(360):
        import math
        rad = math.radians(angle)
        x = int(center_x + hoop_radius * math.cos(rad))
        y = int(hoop_y + (hoop_radius * 0.7) * math.sin(rad))
        if 0 <= x < size and 0 <= y < size:
            pixels[x, y] = NET_MAIN

    # Net mesh (inside hoop)
    for y in range(3, 12):
        for x in range(center_x - 6, center_x + 7):
            if 0 <= x < size and 0 <= y < size:
                dx = x - center_x
                dy = y - hoop_y
                if dx * dx + dy * dy * 2 < hoop_radius * hoop_radius:
                    if (x + y) % 3 == 0:
                        pixels[x, y] = NET_MESH

    # Handle
    for y in range(10, size - 2):
        pixels[center_x, y] = HANDLE_MAIN
        pixels[center_x - 1, y] = HANDLE_DARK
        pixels[center_x + 1, y] = HANDLE_LIGHT

    return img


def create_large_net(size):
    """Create large butterfly net icon (bigger hoop)."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    hoop_y = 5
    hoop_radius = 9

    # Draw hoop rim (thicker)
    import math
    for angle in range(360):
        rad = math.radians(angle)
        for r in range(hoop_radius - 1, hoop_radius + 1):
            x = int(center_x + r * math.cos(rad))
            y = int(hoop_y + (r * 0.7) * math.sin(rad))
            if 0 <= x < size and 0 <= y < size:
                pixels[x, y] = NET_MAIN

    # Net mesh
    for y in range(2, 13):
        for x in range(center_x - 8, center_x + 9):
            if 0 <= x < size and 0 <= y < size:
                dx = x - center_x
                dy = y - hoop_y
                if dx * dx + dy * dy * 2 < hoop_radius * hoop_radius:
                    if (x + y) % 3 == 0:
                        pixels[x, y] = NET_MESH

    # Handle (thicker)
    for y in range(11, size - 1):
        for dx in range(-1, 2):
            if 0 <= center_x + dx < size:
                if dx == -1:
                    pixels[center_x + dx, y] = HANDLE_DARK
                elif dx == 1:
                    pixels[center_x + dx, y] = HANDLE_LIGHT
                else:
                    pixels[center_x + dx, y] = HANDLE_MAIN

    return img


def create_calm_spray(size):
    """Create spray bottle icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2

    # Spray nozzle (top)
    for y in range(2, 6):
        pixels[center_x, y] = METAL_MAIN
        pixels[center_x + 1, y] = METAL_DARK

    # Trigger
    for x in range(center_x + 2, center_x + 5):
        if x < size:
            pixels[x, 5] = METAL_MAIN
            pixels[x, 6] = METAL_DARK

    # Bottle body
    for y in range(6, size - 2):
        for x in range(center_x - 4, center_x + 5):
            if 0 <= x < size:
                if x == center_x - 4:
                    pixels[x, y] = SPRAY_DARK
                elif x == center_x + 4:
                    pixels[x, y] = SPRAY_DARK
                elif x < center_x:
                    pixels[x, y] = SPRAY_MAIN
                else:
                    pixels[x, y] = SPRAY_LIGHT

    # Liquid inside (show level)
    for y in range(12, size - 3):
        for x in range(center_x - 3, center_x + 4):
            if 0 <= x < size:
                pixels[x, y] = SPRAY_LIQUID

    # Bottom
    for x in range(center_x - 4, center_x + 5):
        if 0 <= x < size:
            pixels[x, size - 2] = SPRAY_DARK

    return img


def create_fly_icon(size):
    """Create fly bug icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    center_y = size // 2

    # Body (oval)
    for y in range(center_y - 3, center_y + 5):
        for x in range(center_x - 2, center_x + 3):
            if 0 <= x < size and 0 <= y < size:
                dx = (x - center_x) * 1.5
                dy = y - center_y
                if dx * dx + dy * dy < 12:
                    pixels[x, y] = FLY_MAIN

    # Head
    for y in range(center_y - 5, center_y - 2):
        for x in range(center_x - 2, center_x + 3):
            if 0 <= x < size and 0 <= y < size:
                pixels[x, y] = FLY_DARK

    # Eyes
    pixels[center_x - 1, center_y - 4] = FLY_EYE
    pixels[center_x + 1, center_y - 4] = FLY_EYE

    # Wings (left)
    for y in range(center_y - 4, center_y + 1):
        for x in range(center_x - 7, center_x - 1):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x - 4)
                dy = y - (center_y - 2)
                if dx * dx + dy * dy * 2 < 16:
                    pixels[x, y] = FLY_WING

    # Wings (right)
    for y in range(center_y - 4, center_y + 1):
        for x in range(center_x + 2, center_x + 8):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x + 4)
                dy = y - (center_y - 2)
                if dx * dx + dy * dy * 2 < 16:
                    pixels[x, y] = FLY_WING

    return img


def create_fly_eggs(size):
    """Create fly eggs cluster icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    center_y = size // 2

    # Draw several small oval eggs
    egg_positions = [
        (center_x - 4, center_y - 2),
        (center_x, center_y - 3),
        (center_x + 4, center_y - 1),
        (center_x - 3, center_y + 2),
        (center_x + 1, center_y + 1),
        (center_x + 5, center_y + 3),
        (center_x - 1, center_y + 4),
    ]

    for ex, ey in egg_positions:
        for dy in range(-2, 3):
            for dx in range(-1, 2):
                px, py = ex + dx, ey + dy
                if 0 <= px < size and 0 <= py < size:
                    if abs(dy) < 2 or dx == 0:
                        if dy < 0:
                            pixels[px, py] = EGG_LIGHT
                        elif dy > 1:
                            pixels[px, py] = EGG_DARK
                        else:
                            pixels[px, py] = EGG_MAIN

    return img


def create_bee_icon(size):
    """Create bee bug icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    center_y = size // 2

    # Body with stripes
    for y in range(center_y - 3, center_y + 5):
        for x in range(center_x - 3, center_x + 4):
            if 0 <= x < size and 0 <= y < size:
                dx = (x - center_x) * 1.2
                dy = y - center_y
                if dx * dx + dy * dy < 16:
                    # Stripes
                    if (y - center_y) % 3 == 0:
                        pixels[x, y] = BEE_DARK
                    else:
                        pixels[x, y] = BEE_YELLOW

    # Head
    for y in range(center_y - 5, center_y - 2):
        for x in range(center_x - 2, center_x + 3):
            if 0 <= x < size and 0 <= y < size:
                pixels[x, y] = BEE_DARK

    # Wings
    for y in range(center_y - 5, center_y):
        for x in range(center_x - 7, center_x - 2):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x - 4)
                dy = y - (center_y - 3)
                if dx * dx + dy * dy < 10:
                    pixels[x, y] = BEE_WING

    for y in range(center_y - 5, center_y):
        for x in range(center_x + 3, center_x + 8):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x + 5)
                dy = y - (center_y - 3)
                if dx * dx + dy * dy < 10:
                    pixels[x, y] = BEE_WING

    # Stinger
    pixels[center_x, center_y + 5] = BEE_DARK
    if center_y + 6 < size:
        pixels[center_x, center_y + 6] = BEE_DARK

    return img


def create_beetle_icon(size):
    """Create beetle bug icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    center_y = size // 2

    # Shell (large oval)
    for y in range(center_y - 2, center_y + 6):
        for x in range(center_x - 5, center_x + 6):
            if 0 <= x < size and 0 <= y < size:
                dx = (x - center_x) * 0.8
                dy = (y - center_y) * 1.2
                if dx * dx + dy * dy < 20:
                    # Gradient for shiny effect
                    if x < center_x - 2:
                        pixels[x, y] = BEETLE_DARK
                    elif x > center_x + 2:
                        pixels[x, y] = BEETLE_LIGHT
                    else:
                        pixels[x, y] = BEETLE_MAIN

    # Shell line down middle
    for y in range(center_y - 1, center_y + 5):
        if 0 <= y < size:
            pixels[center_x, y] = BEETLE_DARK

    # Head
    for y in range(center_y - 5, center_y - 1):
        for x in range(center_x - 2, center_x + 3):
            if 0 <= x < size and 0 <= y < size:
                pixels[x, y] = BEETLE_DARK

    # Antennae
    if center_y - 6 >= 0:
        pixels[center_x - 2, center_y - 6] = BEETLE_DARK
        pixels[center_x + 2, center_y - 6] = BEETLE_DARK

    # Legs (simple lines)
    for i in range(3):
        ly = center_y + i
        if 0 <= ly < size:
            if center_x - 6 >= 0:
                pixels[center_x - 6, ly] = BEETLE_DARK
            if center_x + 6 < size:
                pixels[center_x + 6, ly] = BEETLE_DARK

    return img


def create_butterfly_icon(size):
    """Create butterfly bug icon."""
    img = Image.new('RGBA', (size, size), T)
    pixels = img.load()

    center_x = size // 2
    center_y = size // 2

    # Left wing (upper)
    for y in range(center_y - 6, center_y + 1):
        for x in range(center_x - 9, center_x - 1):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x - 5)
                dy = y - (center_y - 3)
                if dx * dx + dy * dy < 20:
                    pixels[x, y] = BUTTERFLY_WING1

    # Right wing (upper)
    for y in range(center_y - 6, center_y + 1):
        for x in range(center_x + 2, center_x + 10):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x + 5)
                dy = y - (center_y - 3)
                if dx * dx + dy * dy < 20:
                    pixels[x, y] = BUTTERFLY_WING2

    # Left wing (lower)
    for y in range(center_y, center_y + 6):
        for x in range(center_x - 7, center_x - 1):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x - 4)
                dy = y - (center_y + 3)
                if dx * dx + dy * dy < 12:
                    pixels[x, y] = BUTTERFLY_WING2

    # Right wing (lower)
    for y in range(center_y, center_y + 6):
        for x in range(center_x + 2, center_x + 8):
            if 0 <= x < size and 0 <= y < size:
                dx = x - (center_x + 4)
                dy = y - (center_y + 3)
                if dx * dx + dy * dy < 12:
                    pixels[x, y] = BUTTERFLY_WING1

    # Wing spots
    pixels[center_x - 5, center_y - 3] = BUTTERFLY_SPOTS
    pixels[center_x + 5, center_y - 3] = BUTTERFLY_SPOTS

    # Body
    for y in range(center_y - 5, center_y + 6):
        if 0 <= y < size:
            pixels[center_x, y] = BUTTERFLY_BODY
            if center_x + 1 < size:
                pixels[center_x + 1, y] = BUTTERFLY_BODY

    # Antennae
    if center_y - 6 >= 0:
        pixels[center_x - 1, center_y - 6] = BUTTERFLY_BODY
        pixels[center_x + 2, center_y - 6] = BUTTERFLY_BODY
    if center_y - 7 >= 0:
        pixels[center_x - 2, center_y - 7] = BUTTERFLY_BODY
        pixels[center_x + 3, center_y - 7] = BUTTERFLY_BODY

    return img


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Items"
    os.makedirs(output_dir, exist_ok=True)

    size = 24  # All icons are 24x24

    # Tools
    small_net = create_small_net(size)
    small_net.save(f"{output_dir}/small_net.png")
    print(f"Created: {output_dir}/small_net.png")

    large_net = create_large_net(size)
    large_net.save(f"{output_dir}/large_net.png")
    print(f"Created: {output_dir}/large_net.png")

    calm_spray = create_calm_spray(size)
    calm_spray.save(f"{output_dir}/calm_spray.png")
    print(f"Created: {output_dir}/calm_spray.png")

    # Bugs
    fly = create_fly_icon(size)
    fly.save(f"{output_dir}/fly.png")
    print(f"Created: {output_dir}/fly.png")

    fly_eggs = create_fly_eggs(size)
    fly_eggs.save(f"{output_dir}/fly_eggs.png")
    print(f"Created: {output_dir}/fly_eggs.png")

    bee = create_bee_icon(size)
    bee.save(f"{output_dir}/bee.png")
    print(f"Created: {output_dir}/bee.png")

    beetle = create_beetle_icon(size)
    beetle.save(f"{output_dir}/beetle.png")
    print(f"Created: {output_dir}/beetle.png")

    butterfly = create_butterfly_icon(size)
    butterfly.save(f"{output_dir}/butterfly.png")
    print(f"Created: {output_dir}/butterfly.png")

    print(f"\nCreated 8 item icons in {output_dir}")
    print("\nUnity import settings:")
    print("  - Texture Type: Sprite (2D and UI)")
    print("  - Sprite Mode: Single")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
