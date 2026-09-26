"""gen_side_armor.py — copper armour drawn on the SIDE view of the character.

Same principle as the front suit: hand the model the CHARACTER and ask it to armour that exact figure,
rather than describing a suit of armour and hoping it fits. The front suit and the front base share a
silhouette because the suit was painted onto the base; the side needs the same treatment or the pieces
will not line up when masked.

The helmet is generated as a SEPARATE pass on the bald side view — hair under a helmet is the reason the
front set needed a bald base, and a helmet drawn over hair cannot be masked cleanly.

  python3 tools/player_sprites/gen_side_armor.py            # 3 body-armour candidates
  python3 tools/player_sprites/gen_side_armor.py sheet      # rebuild the sheet from cached raws
"""
import os
import sys
import glob
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
from aipipe import pixelsnap as ps                               # noqa: E402

PLAYER = os.path.join(REPO, "tools", "_generated", "player")
REFS = os.path.join(PLAYER, "references")
WORK = os.path.join(PLAYER, "in-progress", "copper-armor", f"{date.today().isoformat()}_side")
MODEL, QUALITY, CANVAS = "gpt-image-1.5", "high", "1024x1536"

# the front suit is the colour/style reference so the side matches the set we already have
FRONT_SUIT = os.path.join(PLAYER, "in-progress", "copper-armor", "2026-07-22_masking", "suit.png")
# The chosen side view at its NATIVE 1024px. Feeding this (rather than the 18x61 sprite upscaled) is the
# whole ballgame: a thumbnail blown up 16x has ~1100 real pixels of information, so the model re-invents
# structure instead of painting over it — which is exactly how the first side-armour attempt turned to mush.
SIDE_RAW = os.path.join(PLAYER, "in-progress", "side-view", "2026-07-27_attempt", "raw",
                        "side_minimal_delta_2.png")

STYLE = ("Crisp PIXEL ART, hard pixel edges, no anti-aliasing, no gradients. Fully TRANSPARENT "
         "background, no ground, no shadow.")

VARIANTS = [
    # The terse "change nothing else" phrasing that beat every elaborate prompt for the side BASE.
    ("minimal_delta",
     "The same character, wearing full copper plate armour including a copper helmet. Change nothing "
     "else. " + STYLE),
    ("minimal_delta_2",
     "Put full copper plate armour on this character, helmet included. Same pose, same size. Change "
     "nothing else. " + STYLE),
    ("plain",
     "Dress the attached character in COPPER PLATE ARMOUR from head to foot. Keep the pose, height and "
     "body size exactly as they are. Add a copper helmet covering the head, a copper chest plate with a "
     "shoulder pauldron, a copper arm guard on the visible arm, copper leg plates and copper boots. "
     "Bright polished copper-orange metal with darker shading. " + STYLE),
    ("bulkier",
     "Dress the attached character in chunky COPPER PLATE ARMOUR that sits ON TOP of the body, making "
     "the silhouette slightly bulkier: a copper helmet over the head, a rounded copper breastplate, a "
     "large shoulder pauldron, a copper bracer on the arm, copper thigh and shin plates, copper boots. "
     "Keep the same pose and the same height. Bright polished copper-orange with darker shading. " + STYLE),
    ("matched_to_front",
     "Dress the attached character in COPPER PLATE ARMOUR in EXACTLY the same style and colours as a "
     "matching front view of this armour: rounded copper breastplate, shoulder pauldron, arm bracer, "
     "faulds over the hips, leg plates, copper boots. Bright polished copper-orange metal, darker "
     "copper-brown in the shadows. Keep the character's pose, height, head and hair unchanged. " + STYLE),
]


def edit(images, prompt):
    b = "----bf-sidearmor"
    parts = []

    def field(k, v):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode())

    for k, v in [("model", MODEL), ("prompt", prompt), ("size", CANVAS), ("quality", QUALITY),
                 ("n", "1"), ("background", "transparent"), ("input_fidelity", "high")]:
        field(k, v)
    for i, p in enumerate(images):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"image[]\"; "
                      f"filename=\"img{i}.png\"\r\nContent-Type: image/png\r\n\r\n").encode()
                     + open(p, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(g.EDIT_URL, data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {g.resolve_api_key()}",
                                          "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])


def upscaled_ref(src, out, scale=16):
    """The side base is only 18x61; nearest-upscale it so the model gets a big crisp figure to work on."""
    im = Image.open(src).convert("RGBA")
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(out)
    return out


def to_sprite(raw_path, target_h):
    """pixelsnap grid recovery (NOT an area downscale — that mushes pixel art), matched to the base height."""
    a = np.asarray(Image.open(raw_path).convert("RGBA"), float)
    ys, xs = np.where(a[..., 3] > 40)
    if not len(ys):
        return None
    cut = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    P = cut.shape[0] / target_h
    ex, ey = ps.edge_energy(cut)
    x0, y0 = ps._best_phase(ex, P) % P, ps._best_phase(ey, P) % P
    out = ps.sample(cut, P, P, x0, y0, int((cut.shape[1] - x0) // P), int((cut.shape[0] - y0) // P))
    out[..., 3] = np.where(out[..., 3] > 110, 255, 0)
    ys2, xs2 = np.where(out[..., 3] > 0)
    return out[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1].astype(np.uint8)


def sheet():
    base = np.asarray(Image.open(os.path.join(REFS, "base_side.png")).convert("RGBA"), np.uint8)
    cells = [("side base", base)]
    for p in sorted(glob.glob(os.path.join(WORK, "candidates", "*.png"))):
        cells.append((os.path.basename(p)[:-4], np.asarray(Image.open(p).convert("RGBA"), np.uint8)))
    front = os.path.join(PLAYER, "in-progress", "copper-armor", "2026-07-22_masking", "suit.png")
    if os.path.exists(front):
        cells.append(("FRONT suit (for style)", np.asarray(Image.open(front).convert("RGBA"), np.uint8)))
    H, pad, bar = 430, 16, 30
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    imgs = [(n, Image.fromarray(a, "RGBA").resize(
        (max(18, int(round(a.shape[1] * H / a.shape[0]))), H), Image.NEAREST)) for n, a in cells]
    W = pad + sum(im.width + pad for _, im in imgs)
    sh = Image.new("RGB", (W, bar + H + pad), (38, 40, 46))
    d = ImageDraw.Draw(sh)
    x = pad
    for name, im in imgs:
        bg = Image.new("RGBA", (im.width, H), (150, 160, 150, 255))
        bg.alpha_composite(im)
        sh.paste(bg.convert("RGB"), (x, bar))
        d.text((x, 6), name[:22], fill=(255, 235, 160), font=font)
        x += im.width + pad
    out = os.path.join(WORK, "side_armor_candidates.png")
    sh.save(out)
    print("wrote", os.path.relpath(out, REPO))


def main():
    os.makedirs(os.path.join(WORK, "raw"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "candidates"), exist_ok=True)
    base_p = os.path.join(REFS, "base_side.png")
    base = np.asarray(Image.open(base_p).convert("RGBA"), np.uint8)
    target_h = base.shape[0]
    big = SIDE_RAW if os.path.exists(SIDE_RAW) else upscaled_ref(
        base_p, os.path.join(WORK, "raw", "_side_base_big.png"))
    print(f"  painting onto: {os.path.basename(big)}")

    for name, prompt in VARIANTS:
        rp = os.path.join(WORK, "raw", f"suit_side_{name}.png")
        if not os.path.exists(rp):
            print(f"  generating {name} …", flush=True)
            imgs = [big, FRONT_SUIT] if (name == "matched_to_front" and os.path.exists(FRONT_SUIT)) else [big]
            try:
                open(rp, "wb").write(edit(imgs, prompt))
            except Exception as e:
                print(f"  FAILED {name}: {type(e).__name__}: {e}")
                continue
        spr = to_sprite(rp, target_h)
        if spr is not None:
            Image.fromarray(spr, "RGBA").save(os.path.join(WORK, "candidates", f"suit_side_{name}.png"))
            print(f"  {name}: {spr.shape[1]}x{spr.shape[0]}")
    sheet()

# ---------------------------------------------------------------------------------------------
def trimmed(path):
    """Crop a render down to the drawn figure(s), dropping the empty canvas around them."""
    a = np.asarray(Image.open(path).convert("RGBA"), np.uint8)
    ys, xs = np.where(a[..., 3] > 40)
    if not len(ys):
        return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def pair(rolls=3):
    """Generate the bare side view and the ARMOURED side view in ONE image.

    Masking only works if the armour sits on the exact same body, in the exact same pose — a suit drawn
    in a slightly different stance can't be cut into pieces that line up. Asking for the pair in a single
    image makes them match BY CONSTRUCTION rather than by instruction, which is the same trick that fixed
    tile-variant palette drift and the front/side turnaround earlier. Whatever pose the model settles on,
    both figures share it, and both are sliced from the same render.
    """
    prompt = (
        "Draw the SAME character TWICE, side by side in one image, both standing on the same baseline at "
        "exactly the same height, both seen from the SIDE facing right. "
        "On the LEFT: the character exactly as in the attached reference — auburn hair, white tank top, "
        "tan shorts, bare arms and legs. "
        "On the RIGHT: the identical character in the SAME pose, now wearing full COPPER PLATE ARMOUR — "
        "copper helmet, breastplate, shoulder pauldron, arm bracer, leg plates and boots, in bright "
        "polished copper-orange with darker copper-brown shadows. "
        "CRITICAL: the two figures must be the same person in the same stance at the same size — same "
        "head position, same shoulder height, same leg position, same feet. Only the armour differs. "
        "Draw the armour as SEPARATE plates with dark gaps between the pieces, so each piece reads "
        "distinctly. " + STYLE)
    os.makedirs(os.path.join(WORK, "raw"), exist_ok=True)
    src = SIDE_RAW if os.path.exists(SIDE_RAW) else os.path.join(REFS, "base_side.png")
    for i in range(1, rolls + 1):
        rp = os.path.join(WORK, "raw", f"pair_{i}.png")
        if os.path.exists(rp):
            print(f"  pair_{i}: cached")
            continue
        try:
            print(f"  generating pair_{i} …", flush=True)
            open(rp, "wb").write(edit([src], prompt))
        except Exception as e:
            print(f"  FAILED pair_{i}: {type(e).__name__}: {e}")
    pair_sheet()


def pair_sheet():
    """Show each pair render raw, so the bare/armoured match can be judged before any slicing."""
    paths = sorted(glob.glob(os.path.join(WORK, "raw", "pair_*.png")))
    if not paths:
        print("no pair renders yet")
        return
    H, pad, bar = 460, 16, 30
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    imgs = []
    for p in paths:
        t = trimmed(p)
        if t is None:
            continue
        w = max(30, int(round(t.shape[1] * H / t.shape[0])))
        imgs.append((os.path.basename(p)[:-4], Image.fromarray(t, "RGBA").resize((w, H), Image.NEAREST)))
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
    out = os.path.join(WORK, "pair_candidates.png")
    sh.save(out)
    print("wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sheet":
        sheet()
    elif len(sys.argv) > 1 and sys.argv[1] == "pair":
        pair(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif len(sys.argv) > 1 and sys.argv[1] == "pairsheet":
        pair_sheet()
    else:
        main()