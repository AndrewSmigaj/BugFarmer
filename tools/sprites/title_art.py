#!/usr/bin/env python3
"""Title-screen art for the opening sequence — a composed farm SCENE + the "BugFarmer" LOGO.

Pixel sprites (Resources/Bugs|Objects|Tiles) are NEAREST-scaled and composited into a dawn farm
vignette; the logo is rendered with the best available font + game styling (outline/shadow/gradient).
Run with --candidates to dump several logo treatments to the preview folder for visual iteration;
run with --final to write the chosen logo + background into Resources/UI/ (+ Unity .meta).

  python3 tools/sprites/title_art.py --candidates   # iterate fonts/styling
  python3 tools/sprites/title_art.py --final         # write Resources/UI/title_logo.png + title_bg.png
"""
import argparse, glob, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
PREV = os.path.join(ROOT, "tools", "_generated", "previews", "title")
os.makedirs(PREV, exist_ok=True)

FONTS = {
    "serif":  "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans":   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "ubuntu": "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "cond":   "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf",
}

def load(path, scale):
    try:
        im = Image.open(path).convert("RGBA")
    except Exception:
        return None
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return im

def first(globpat, scale):
    for p in sorted(glob.glob(globpat)):
        im = load(p, scale)
        if im: return im
    return None

# ----------------------------------------------------------------- background scene
def build_scene(W=1280, H=720):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    horizon = int(H * 0.62)
    # sky gradient: soft blue (top) -> warm dawn peach (horizon)
    top = (150, 196, 224); bot = (248, 220, 170)
    for y in range(horizon):
        t = y / horizon
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    # soft sun
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sx, sy, r = int(W * 0.78), int(horizon * 0.42), 120
    sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 240, 200, 230))
    im = Image.alpha_composite(im, sun.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(im)
    # ground: grass band, tiled
    grass = first(os.path.join(RES, "Tiles", "grass*.png"), 4)
    if grass:
        for gx in range(0, W, grass.width):
            for gy in range(horizon, H, grass.height):
                im.alpha_composite(grass, (gx, gy))
    else:
        d.rectangle([0, horizon, W, H], fill=(120, 170, 90, 255))
    # a soil field strip with crop rows
    d.rectangle([0, int(H * 0.80), W, H], fill=(110, 80, 56, 255))
    crops = [first(os.path.join(RES, "Objects", c), 4) for c in
             ("plant_corn_stage3.png", "plant_cabbage_stage3.png", "plant_carrot_stage3.png",
              "plant_tomato_stage3.png", "plant_pumpkin_stage3.png", "milkweed.png")]
    crops = [c for c in crops if c]
    if crops:
        x = 40
        while x < W - 40:
            c = crops[(x // 90) % len(crops)]
            im.alpha_composite(c, (x, int(H * 0.86) - c.height))
            x += max(70, c.width + 18)
    # flowers + a tree along the grass
    tree = first(os.path.join(RES, "Objects", "tree_apple*.png"), 5) or first(os.path.join(RES, "Objects", "tree_*.png"), 5)
    if tree: im.alpha_composite(tree, (int(W * 0.06), horizon - tree.height + 20))
    for fx, fn in [(0.30, "flower_red.png"), (0.45, "flower_yellow.png"), (0.62, "flower_blue.png"),
                   (0.88, "bush_flowering.png")]:
        f = first(os.path.join(RES, "Objects", fn), 3)
        if f: im.alpha_composite(f, (int(W * fx), horizon + 10))
    # bugs flying in the sky / over the crops
    for bx, by, fn, sc in [(0.22, 0.20, "butterfly_monarch.png", 4), (0.40, 0.30, "bumblebee.png", 4),
                           (0.58, 0.16, "dragonfly_emperor.png", 4), (0.70, 0.34, "butterfly_swallowtail.png", 4),
                           (0.50, 0.50, "ladybug.png", 4), (0.33, 0.46, "beetle_stag.png", 4)]:
        b = first(os.path.join(RES, "Bugs", fn), sc)
        if b: im.alpha_composite(b, (int(W * bx), int(H * by)))
    # gentle vignette
    vig = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vig)
    vd.ellipse([-W * 0.2, -H * 0.2, W * 1.2, H * 1.2], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (20, 18, 30, 110))
    dark.putalpha(Image.eval(vig, lambda a: 110 - int(a * 110 / 255)))
    im = Image.alpha_composite(im, dark)
    return im

# ----------------------------------------------------------------- logo
def make_logo(text="BugFarmer", font_key="serif", size=150, fill=(246, 210, 100),
              outline=(54, 38, 22), shadow=True, W=1100, H=320):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    try: fnt = ImageFont.truetype(FONTS[font_key], size)
    except Exception: fnt = ImageFont.load_default()
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W - tw) // 2 - bb[0], (H - th) // 2 - bb[1]
    ow = max(4, size // 22)  # outline width
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + ow, y + ow + 6), text, font=fnt, fill=(0, 0, 0, 150))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
    # chunky outline
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow:
                d.text((x + dx, y + dy), text, font=fnt, fill=outline + (255,))
    # gradient fill (warm gold top -> deeper amber bottom)
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
    c2 = tuple(max(0, int(c * 0.7)) for c in fill)
    for yy in range(H):
        t = yy / H
        gd.line([(0, yy), (W, yy)], fill=tuple(int(fill[i] + (c2[i] - fill[i]) * t) for i in range(3)) + (255,))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).text((x, y), text, font=fnt, fill=255)
    im.paste(grad, (0, 0), mask)
    # top highlight
    hl = Image.new("L", (W, H), 0); ImageDraw.Draw(hl).text((x, y - max(2, ow // 2)), text, font=fnt, fill=90)
    im.paste(Image.new("RGBA", (W, H), (255, 250, 220, 255)), (0, 0), Image.composite(hl, Image.new("L", (W, H), 0), mask))
    return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--font", default="serif")
    a = ap.parse_args()

    scene = build_scene()
    scene.convert("RGB").save(os.path.join(PREV, "scene.png"))
    print("scene ->", os.path.join(PREV, "scene.png"))

    if a.candidates:
        for k in FONTS:
            lg = make_logo(font_key=k)
            # composite onto a crop of the scene for a real preview
            prev = scene.copy()
            prev.alpha_composite(lg, ((prev.width - lg.width) // 2, int(prev.height * 0.10)))
            prev.convert("RGB").save(os.path.join(PREV, f"title_{k}.png"))
            lg.save(os.path.join(PREV, f"logo_{k}.png"))
            print("candidate ->", f"title_{k}.png")

    if a.final:
        UI = os.path.join(RES, "UI")
        make_logo(font_key=a.font).save(os.path.join(UI, "title_logo.png"))
        scene.save(os.path.join(UI, "title_bg.png"))
        print("wrote Resources/UI/title_logo.png + title_bg.png")
