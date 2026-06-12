"""Emit all player sprites: baked classes (compat names) + paper-doll layers.

Outputs (16x32 each; frame suffixes: none = idle/passing, _w1/_w3 = contacts;
runtime walk order is [w1, idle, w3, idle]):
  Resources/Player/{class}_{dir}[_w1|_w3].png          baked (zone NPCs, fallback)
  Resources/Player/layers/body/{tone}_{dir}[...].png   unclothed base (3 tones)
  Resources/Player/layers/hair/{color}_{dir}[...].png  template hair per color
  Resources/Player/layers/shirt/{class}_{dir}[...].png
  Resources/Player/layers/pants/{class}_{dir}[...].png
Preview cards -> tools/_generated/previews/player/.
"""
import os

from . import pixkit, body_frames, wearables
from .palettes import CLASSES, SKIN_TONES

HERE = os.path.dirname(os.path.abspath(__file__))
PLAYER_DIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "BugFarmerClient", "Assets", "Resources", "Player"))
PREVIEW_DIR = os.path.normpath(os.path.join(
    HERE, "..", "_generated", "previews", "player"))

FRAME_SUFFIX = {0: "_w1", 1: "", 2: "_w3"}   # frame 3 == frame 1 (idle), not written
DIRS = ("down", "up", "left", "right")


def _emit(im, *parts):
    pixkit.save(im, os.path.join(PLAYER_DIR, *parts))


def _blank():
    from PIL import Image
    return Image.new("RGBA", (16, 32), (0, 0, 0, 0))


def main():
    frames = body_frames.direction_frames()          # {dir: [4 row-lists]}
    default_skin = SKIN_TONES["default"]

    # ---- baked classes (compat: same filenames the game/zonegen already load)
    class_idle = {}
    for cls, (hair_name, hair, shirt, pants) in CLASSES.items():
        pal = pixkit.make_palette(skin=default_skin, hair=hair, shirt=shirt, pants=pants)
        for d in DIRS:
            for fi, suffix in FRAME_SUFFIX.items():
                im = pixkit.render(frames[d][fi], pal, mode="baked")
                _emit(im, f"{cls}_{d}{suffix}.png")
                if fi == 1:
                    class_idle[(cls, d)] = im

    # ---- layers: body per skin tone
    for tone, ramp in SKIN_TONES.items():
        pal = pixkit.make_palette(skin=ramp, hair=CLASSES["farmer"][1],
                                  shirt=CLASSES["farmer"][2], pants=CLASSES["farmer"][3])
        for d in DIRS:
            for fi, suffix in FRAME_SUFFIX.items():
                im = pixkit.render(frames[d][fi], pal, mode="body")
                _emit(im, "layers", "body", f"{tone}_{d}{suffix}.png")

    # ---- layers: hair per color, shirt/pants per class
    for cls, (hair_name, hair, shirt, pants) in CLASSES.items():
        pal = pixkit.make_palette(skin=default_skin, hair=hair, shirt=shirt, pants=pants)
        for d in DIRS:
            for fi, suffix in FRAME_SUFFIX.items():
                rows = frames[d][fi]
                _emit(pixkit.render(rows, pal, mode="region", region=pixkit.HAIR),
                      "layers", "hair", f"{hair_name}_{d}{suffix}.png")
                _emit(pixkit.render(rows, pal, mode="region", region=pixkit.SHIRT),
                      "layers", "shirt", f"{cls}_{d}{suffix}.png")
                _emit(pixkit.render(rows, pal, mode="region", region=pixkit.PANTS),
                      "layers", "pants", f"{cls}_{d}{suffix}.png")

    # ---- wearables: armor/hats (pre-composed per frame: HEAD items ride the
    # contact-frame head bob, chest items don't — the torso doesn't move)
    pal = pixkit.make_palette(skin=default_skin, hair=CLASSES["farmer"][1],
                              shirt=CLASSES["farmer"][2], pants=CLASSES["farmer"][3])
    for slot, items in wearables.ARMOR.items():
        bob = slot in wearables.HEAD_SLOT
        for item, grids in items.items():
            for d in DIRS:
                rows = pixkit.parse(grids["left" if d == "right" else d])
                if d == "right":
                    rows = pixkit.mirror(rows)
                im = pixkit.render(rows, pal, mode="baked")
                for fi, suffix in FRAME_SUFFIX.items():
                    dy = 1 if (bob and fi != 1) else 0
                    _emit(pixkit.compose(_blank(), im, dy),
                          "layers", slot, f"{item}_{d}{suffix}.png")

    # ---- hair STYLES (style replacement grids x every color ramp)
    for style, grids in wearables.HAIR_STYLES.items():
        for cls, (hair_name, hair, shirt, pants) in CLASSES.items():
            spal = pixkit.make_palette(skin=default_skin, hair=hair, shirt=shirt, pants=pants)
            for d in DIRS:
                rows = pixkit.parse(grids["left" if d == "right" else d])
                if d == "right":
                    rows = pixkit.mirror(rows)
                im = pixkit.render(rows, spal, mode="baked")
                for fi, suffix in FRAME_SUFFIX.items():
                    dy = 1 if fi != 1 else 0          # hair rides the head bob
                    _emit(pixkit.compose(_blank(), im, dy),
                          "layers", "hair", f"{style}_{hair_name}_{d}{suffix}.png")

    # ---- retire the unused spritesheets (no consumers — verified 2026-06)
    removed = []
    for cls in CLASSES:
        p = os.path.join(PLAYER_DIR, f"{cls}_spritesheet.png")
        if os.path.exists(p):
            os.remove(p)
            removed.append(os.path.basename(p))

    # ---- preview cards
    cells = [class_idle[(cls, d)] for cls in CLASSES for d in DIRS]
    pixkit.save(pixkit.contact_sheet(cells, cols=4, scale=8),
                os.path.join(PREVIEW_DIR, "classes.png"))
    farmer_pal = pixkit.make_palette(skin=default_skin, hair=CLASSES["farmer"][1],
                                     shirt=CLASSES["farmer"][2], pants=CLASSES["farmer"][3])
    for d in DIRS:
        walk = [pixkit.render(f, farmer_pal, mode="baked") for f in frames[d]]
        pixkit.walk_gif(walk, os.path.join(PREVIEW_DIR, f"walk_{d}.gif"), scale=8)

    # ---- composed wearables preview (proves layer registration end-to-end)
    from PIL import Image

    def L(*parts):
        return Image.open(os.path.join(PLAYER_DIR, "layers", *parts)).convert("RGBA")

    combos = [
        ("body+long hair", ["body/default_{d}{f}.png", "hair/long_brown_{d}{f}.png"]),
        ("leather+straw", ["body/default_{d}{f}.png", "hair/brown_{d}{f}.png",
                           "shirt/farmer_{d}{f}.png", "pants/farmer_{d}{f}.png",
                           "chest/leather_chest_{d}{f}.png", "helmet/straw_hat_{d}{f}.png"]),
        ("copper helm", ["body/tan_{d}{f}.png", "hair/black_{d}{f}.png",
                         "shirt/scholar_{d}{f}.png", "pants/scholar_{d}{f}.png",
                         "helmet/copper_helmet_{d}{f}.png"]),
        ("full iron", ["body/deep_{d}{f}.png", "shirt/miner_{d}{f}.png",
                       "pants/miner_{d}{f}.png", "chest/iron_chest_{d}{f}.png",
                       "helmet/iron_helmet_{d}{f}.png"]),
    ]
    cells = []
    for _, layers in combos:
        for d in DIRS:
            im = _blank()
            for layer in layers:
                im = Image.alpha_composite(im, L(*layer.format(d=d, f="").split("/")))
            cells.append(im)
    pixkit.save(pixkit.contact_sheet(cells, cols=4, scale=8),
                os.path.join(PREVIEW_DIR, "wearables.png"))
    # armored walk gif (down): all layers per frame
    walk = []
    for f in ("_w1", "", "_w3", ""):
        im = _blank()
        for layer in combos[3][1]:
            im = Image.alpha_composite(im, L(*layer.format(d="down", f=f).split("/")))
        walk.append(im)
    pixkit.walk_gif(walk, os.path.join(PREVIEW_DIR, "walk_iron.gif"), scale=8)

    n = sum(len(files) for _, _, files in os.walk(PLAYER_DIR))
    print(f"player sprites emitted -> {PLAYER_DIR} ({n} files; removed {removed})")
    print(f"previews -> {PREVIEW_DIR}")


if __name__ == "__main__":
    main()
