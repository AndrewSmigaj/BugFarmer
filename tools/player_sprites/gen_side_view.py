"""gen_side_view.py — STANDING SIDE-VIEW candidates, eight different fidelity strategies.

Only the RIGHT-facing view is generated; left is its mirror.

Why several strategies: feeding the front render back with `input_fidelity=high` reliably holds the
PALETTE but does NOT hold PROPORTION. The first attempt came back elongated and thin — aspect 0.31
against the front's 0.44 — so it read as a different, skinnier character. Each strategy below attacks
that with a different lever (measurements, one-image turnaround, grid lock, brevity, style words,
landmark rows, aspect ratio, silhouette metaphor) so we can see which one actually holds the body.

Measured from the front reference, which is what every prompt is trying to reproduce:
    62px tall · head 19px = 31% of height · head 20px wide vs 27px at the shoulders
i.e. a chibi: the head is nearly as wide as the body and a third of the total height.

  python3 tools/player_sprites/gen_side_view.py           # 8 candidates + a raw comparison sheet
  python3 tools/player_sprites/gen_side_view.py sheet     # rebuild the sheet from cached raws (no API)
"""
import os
import sys
import json
import base64
import urllib.request
from datetime import date

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "sprites"))
sys.path.insert(0, os.path.join(REPO, "tools", "player_sprites"))
import gen_sprites as g                                          # noqa: E402
from aipipe import pixelsnap as ps                               # noqa: E402  true-grid recovery

PLAYER = os.path.join(REPO, "tools", "_generated", "player")
REFS = os.path.join(PLAYER, "references")
SRC = os.path.join(PLAYER, "old", "raw_base_gens", "base_set", "base_down_gen.png")
WORK = os.path.join(PLAYER, "in-progress", "side-view", f"{date.today().isoformat()}_attempt")
MODEL, QUALITY, CANVAS = "gpt-image-1.5", "high", "1024x1536"

BODY = ("the same auburn fluffy hair, the same skin tone, the same white tank top, the same tan shorts, "
        "the same bare arms and legs, the same palette")
STYLE = ("Crisp PIXEL ART, hard pixel edges, no anti-aliasing, no gradients, no outline glow. Fully "
         "TRANSPARENT background, no ground, no shadow.")
POSE = "Standing straight and still, arms hanging down at the sides, feet together. Not walking."

STRATEGIES = [
    # 1. hand it the measured ratios
    ("measured",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. "
     "MATCH THESE PROPORTIONS EXACTLY, they are measured from the attached front view: the head "
     "(including hair) is 31% of the figure's total height, and the head is nearly AS WIDE as the "
     "shoulders. The whole figure is about 1.4 times taller than it is wide. Do not stretch it taller or "
     f"make it slimmer than that. {POSE} {STYLE}"),

    # 2. both views in ONE image so they must agree (the trick that fixed tile-variant drift)
    ("turnaround_pair",
     f"Draw TWO views of the attached character side by side in one image, on the same baseline and at "
     f"exactly the same height: on the LEFT the FRONT view exactly as attached, on the RIGHT the same "
     f"character seen from the SIDE facing right. Both keep {BODY}. The two must look like the same "
     f"person photographed from two angles — same height, same head size, same body mass. {POSE} {STYLE}"),

    # 3. pixel-grid lock (the tile lesson: make the model draw the low-res grid itself)
    ("grid_locked",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. Draw it as a pixel-art "
     "sprite exactly 62 chunky square blocks tall, where the head and hair occupy the top 19 blocks and "
     "the body the remaining 43. Every block is one flat colour with hard edges; no detail smaller than "
     f"a block. {POSE} {STYLE}"),

    # 4. minimal instruction — less rope to invent with
    ("minimal_delta",
     "The same character, turned to stand in profile facing right. Change nothing else. " + STYLE),

    # 5. hammer the chibi style words
    ("chibi_hammer",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. It is a CHIBI "
     "character: a BIG round head on a SHORT stocky body, the head almost as wide as the shoulders, "
     "short stubby legs. Keep it chunky and childlike — it must NOT become a tall slim adult or a thin "
     f"stick figure. {POSE} {STYLE}"),

    # 6. landmark rows, so vertical layout is pinned
    ("landmark_rows",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. Place the landmarks at "
     "these heights, measuring from the top of the hair (0%) to the soles (100%): top of hair 0%, eye "
     "line 18%, chin 30%, shoulders 34%, waist 55%, knees 78%, soles 100%. Keep the head large as those "
     f"numbers imply. {POSE} {STYLE}"),

    # 7. pin the bounding box / aspect ratio
    ("aspect_locked",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. CRITICAL: the figure "
     "must fill a box roughly 3 units wide by 4 units tall — wide and solid, NOT tall and narrow. A "
     "profile is a little narrower than a front view, but this character stays stocky: do not elongate "
     f"the legs, do not slim the torso, do not shrink the head. {POSE} {STYLE}"),

    # 8. describe the silhouette as a shape
    ("silhouette_shape",
     f"Redraw the attached character in a SIDE view facing RIGHT, keeping {BODY}. The silhouette should "
     "read as a big rounded blob of hair sitting directly on a short chunky body — like a lollipop with a "
     "thick stick. The hair mass is the widest part of the figure. Short legs, small feet. "
     f"{POSE} {STYLE}"),
]


def edit(image_path, prompt):
    b = "----bf-side"
    parts = []

    def field(k, v):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode())

    for k, v in [("model", MODEL), ("prompt", prompt), ("size", CANVAS), ("quality", QUALITY),
                 ("n", "1"), ("background", "transparent"), ("input_fidelity", "high")]:
        field(k, v)
    parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"image[]\"; filename=\"front.png\"\r\n"
                  f"Content-Type: image/png\r\n\r\n").encode() + open(image_path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(g.EDIT_URL, data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {g.resolve_api_key()}",
                                          "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])


def trimmed(path):
    a = np.asarray(Image.open(path).convert("RGBA"), np.uint8)
    ys, xs = np.where(a[..., 3] > 40)
    if not len(ys):
        return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet():
    """Every raw render trimmed to its figure and scaled to one height, beside the front reference.
    Raw only — no palette snapping or downscaling, so what you judge is what the model drew."""
    front = trimmed(os.path.join(REFS, "base.png"))
    cells = [("FRONT ref", front, 0.0)]
    for name, _ in STRATEGIES:
        p = os.path.join(WORK, "raw", f"side_{name}.png")
        if os.path.exists(p):
            t = trimmed(p)
            if t is not None:
                cells.append((name, t, t.shape[1] / t.shape[0]))

    H = 420
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font = small = ImageFont.load_default()
    imgs = []
    for name, arr, asp in cells:
        w = max(20, int(round(arr.shape[1] * H / arr.shape[0])))
        imgs.append((name, Image.fromarray(arr, "RGBA").resize((w, H), Image.NEAREST), asp))
    pad, bar = 14, 46
    W = pad + sum(im.width + pad for _, im, _ in imgs)
    sheet_im = Image.new("RGB", (W, bar + H + pad + 22), (38, 40, 46))
    d = ImageDraw.Draw(sheet_im)
    x = pad
    front_asp = front.shape[1] / front.shape[0]
    for name, im, asp in imgs:
        bg = Image.new("RGBA", (im.width, H), (150, 160, 150, 255))
        bg.alpha_composite(im)
        sheet_im.paste(bg.convert("RGB"), (x, bar))
        d.text((x, 8), name, fill=(255, 235, 160), font=font)
        if asp:
            near = abs(asp - front_asp) < 0.09
            d.text((x, 26), f"aspect {asp:.2f}", fill=(150, 240, 150) if near else (255, 150, 150), font=small)
        else:
            d.text((x, 26), f"aspect {front_asp:.2f} (target)", fill=(200, 200, 210), font=small)
        x += im.width + pad
    out = os.path.join(WORK, "raw_comparison.png")
    sheet_im.save(out)
    print("wrote", os.path.relpath(out, REPO))


def main():
    os.makedirs(os.path.join(WORK, "raw"), exist_ok=True)
    for name, prompt in STRATEGIES:
        rp = os.path.join(WORK, "raw", f"side_{name}.png")
        if os.path.exists(rp):
            print(f"  {name}: cached")
            continue
        try:
            print(f"  generating {name} …", flush=True)
            open(rp, "wb").write(edit(SRC, prompt))
        except Exception as e:
            print(f"  FAILED {name}: {type(e).__name__}: {e}")
    sheet()


def repeat(strategy, n=3):
    """Re-roll ONE strategy several times. The prompt is fixed, so the variation is just the model's
    own randomness — useful once a strategy is chosen, to pick the best individual render."""
    prompt = dict(STRATEGIES).get(strategy)
    if prompt is None:
        sys.exit(f"unknown strategy: {strategy}")
    os.makedirs(os.path.join(WORK, "raw"), exist_ok=True)
    for i in range(2, 2 + n):
        rp = os.path.join(WORK, "raw", f"side_{strategy}_{i}.png")
        if os.path.exists(rp):
            print(f"  {strategy}_{i}: cached")
            continue
        try:
            print(f"  generating {strategy}_{i} …", flush=True)
            open(rp, "wb").write(edit(SRC, prompt))
        except Exception as e:
            print(f"  FAILED {strategy}_{i}: {type(e).__name__}: {e}")
    compare_rolls(strategy)


def compare_rolls(strategy):
    """Every roll of one strategy beside the front reference, raw and unprocessed."""
    front = trimmed(os.path.join(REFS, "base.png"))
    cells = [("FRONT ref", front)]
    for p in sorted(__import__("glob").glob(os.path.join(WORK, "raw", f"side_{strategy}*.png"))):
        t = trimmed(p)
        if t is not None:
            cells.append((os.path.basename(p)[5:-4], t))
    H = 460
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    imgs = [(n, Image.fromarray(a, "RGBA").resize((max(20, int(round(a.shape[1] * H / a.shape[0]))), H),
                                                  Image.NEAREST)) for n, a in cells]
    pad, bar = 16, 30
    W = pad + sum(im.width + pad for _, im in imgs)
    sh = Image.new("RGB", (W, bar + H + pad), (38, 40, 46))
    d = ImageDraw.Draw(sh)
    x = pad
    for name, im in imgs:
        bg = Image.new("RGBA", (im.width, H), (150, 160, 150, 255))
        bg.alpha_composite(im)
        sh.paste(bg.convert("RGB"), (x, bar))
        d.text((x, 6), name, fill=(255, 235, 160), font=font)
        x += im.width + pad
    out = os.path.join(WORK, f"rolls_{strategy}.png")
    sh.save(out)
    print("wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sheet":
        sheet()
    elif len(sys.argv) > 2 and sys.argv[1] == "more":
        repeat(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
    else:
        main()
