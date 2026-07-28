"""split_base_arm.py — split a character base into BODY + WEAPON ARM.

A weapon swing needs the arm to rotate, so it has to be its own sprite. The wrong way is to cut an arm
out of a finished armour render: the cut is ragged, it fragments when rotated, and it bites a hole in the
torso. The right way is to split the BASE once — then every armour set generated onto the split pieces is
already in the correct shape.

The split follows the character's own silhouette rather than a rectangle. Below the shoulder the arm is
already separated from the torso by a gap of empty pixels, so taking the connected blob on the weapon side
gives a whole limb AND leaves the body intact — no socket to repaint, because the shoulder never belonged
to the arm in the first place.

Outputs (per direction) plus a layered .aseprite for hand cleanup, since the model-drawn edges usually want
a few pixels of tidying:
    references/<dir>/body.png · arm.png · split.aseprite · pivot in pivots.json

  python3 tools/player_sprites/split_base_arm.py down       # split the front base
  python3 tools/player_sprites/split_base_arm.py down --preview
"""
import os
import sys
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
REFS = os.path.join(PLAYER, "references")
ASEPRITE = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Aseprite/Aseprite.exe"

# Per direction: the source image, the row where the arm stops being fused to the shoulder (above this the
# silhouette is one mass; below it there is a gap the split follows), and the shoulder-cap height.
# `down`'s cap of 3 was picked by looking at arm_cap_comparison_down.png: a cap of 0 hinges at the armpit and
# visibly detaches by 50°, 2 still opens a notch at the arm root, and 4 pivots so high the arm rides into the
# chest. Re-run --compare-cap when adding a direction rather than reusing this number.
SOURCES = {
    "down": ("base.png", 37, 3),
    "side": ("base_side.png", 37, 3),
}


def win(p):
    p = os.path.abspath(p)
    return p.replace("/mnt/c/", "C:/") if p.startswith("/mnt/c/") else p


def split(img, free_row, weapon_side="right", cap=0):
    """Return (body, arm, pivot). The arm is the connected blob on the weapon side below `free_row`.

    `cap` adds a shoulder cap of that many rows above `free_row`, COPIED from the body rather than cut out
    of it. Two things fall out of copying instead of moving: the arm hinges at the shoulder joint like a real
    limb rather than at the armpit, and because the body keeps its own shoulder the overlap can never open a
    seam at any swing angle.
    """
    op = img[..., 3] > 0
    lower = np.zeros_like(op)
    lower[free_row:] = op[free_row:]
    # 4-connectivity, not 8: the gap between arm and torso is a single empty column, and it steps sideways
    # by a pixel partway down. Under 8-connectivity that step is a diagonal touch, which bridges the gap and
    # swallows the whole lower body into one blob.
    lbl, n = label(lower, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    if n == 0:
        return img.copy(), np.zeros_like(img), None

    # pick the blob whose centre sits furthest toward the weapon side
    best, best_x = None, None
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        if len(xs) < 12:                      # ignore specks
            continue
        cx = xs.mean()
        if best is None or (cx > best_x if weapon_side == "right" else cx < best_x):
            best, best_x = i, cx
    if best is None:
        return img.copy(), np.zeros_like(img), None

    arm_mask = lbl == best
    body = img.copy()
    body[arm_mask] = 0                       # the limb leaves the body; the shoulder above free_row stays

    take = arm_mask.copy()
    if cap:
        # the shoulder rows, limited to the columns the arm actually occupies so we don't drag in torso
        ys, xs = np.where(arm_mask)
        lo, hi = xs.min(), xs.max()
        for y in range(max(0, free_row - cap), free_row):
            take[y, lo:hi + 1] |= op[y, lo:hi + 1]

    arm = np.zeros_like(img)
    arm[take] = img[take]

    ys, xs = np.where(take)
    top = ys.min()
    row_xs = xs[ys == top]
    # pivot = middle of the arm's topmost row — the shoulder joint when a cap is present, the armpit without
    pivot = (int(round(row_xs.mean())), int(top))
    return body, arm, pivot


def build_ase(out_dir, original, body, arm):
    """A layered .aseprite (body / arm / original reference) so the edges can be tidied by hand."""
    if not os.path.exists(ASEPRITE):
        return None
    tmp = "/mnt/c/temp_split"
    os.makedirs(tmp, exist_ok=True)
    for n, a in [("body", body), ("arm", arm), ("original", original)]:
        Image.fromarray(a, "RGBA").save(os.path.join(tmp, f"{n}.png"))
    lua = os.path.join(tmp, "mk.lua")
    dest = win(os.path.join(out_dir, "split.aseprite"))
    with open(lua, "w") as f:
        f.write(f'''
local spr = Sprite({body.shape[1]}, {body.shape[0]}, ColorMode.RGB)
local names = {{"original","arm","body"}}
for i,n in ipairs(names) do
  local lay = (i==1) and spr.layers[1] or spr:newLayer()
  lay.name = n
  local img = Image{{ fromFile="C:/temp_split/" .. n .. ".png" }}
  spr:newCel(lay, 1, img, Point(0,0))
end
spr.layers[1].isVisible = false      -- reference only
spr:saveAs("{dest}")
''')
    subprocess.run([ASEPRITE, "-b", "--script", win(lua)], capture_output=True)
    return os.path.join(out_dir, "split.aseprite")


def preview(out_dir, body, arm, pivot, name):
    """Rotate the split arm to prove it reads as a limb and leaves no hole."""
    body_im = Image.fromarray(body, "RGBA")
    arm_im = Image.fromarray(arm, "RGBA")
    Z, angles = 8, [0, 30, 60, 90]
    cw, ch = body.shape[1] * Z, body.shape[0] * Z
    pad, bar = 10, 26
    sheet = Image.new("RGB", (pad + (cw + pad) * len(angles), bar + ch + pad), (38, 40, 46))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    x = pad
    for ang in angles:
        rot = arm_im.rotate(-ang, resample=Image.NEAREST, center=pivot)
        c = body_im.copy()
        c.alpha_composite(rot)
        big = c.resize((cw, ch), Image.NEAREST)
        bg = Image.new("RGBA", (cw, ch), (150, 160, 150, 255))
        bg.alpha_composite(big)
        sheet.paste(bg.convert("RGB"), (x, bar))
        d.text((x, 5), f"{ang}°", fill=(255, 235, 160), font=font)
        x += cw + pad
    p = os.path.join(out_dir, "arm_rotation.png")
    sheet.save(p)
    return p


def compare_caps(img, free_row, caps=(0, 2, 3, 4)):
    """One row per shoulder-cap size, swung through the arc — pick the cap by looking at it."""
    Z, angles = 7, [0, 25, 50, 75, 100]
    h, w = img.shape[:2]
    cw, ch = w * Z, h * Z
    pad, bar, lw = 8, 24, 96
    sheet = Image.new("RGB", (lw + (cw + pad) * len(angles), bar + (ch + pad) * len(caps)), (38, 40, 46))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    for ai, ang in enumerate(angles):
        d.text((lw + ai * (cw + pad), 5), f"{ang}°", fill=(255, 235, 160), font=font)
    for ci, cap in enumerate(caps):
        body, arm, pivot = split(img, free_row, cap=cap)
        y = bar + ci * (ch + pad)
        d.text((6, y + ch // 2 - 18), f"cap {cap}", fill=(255, 235, 160), font=font)
        d.text((6, y + ch // 2), "(armpit)" if cap == 0 else "(shoulder)", fill=(150, 200, 240), font=font)
        d.text((6, y + ch // 2 + 18), f"piv {pivot}", fill=(150, 160, 175), font=font)
        bi, ai_ = Image.fromarray(body, "RGBA"), Image.fromarray(arm, "RGBA")
        for aj, ang in enumerate(angles):
            c = bi.copy()
            c.alpha_composite(ai_.rotate(-ang, resample=Image.NEAREST, center=pivot))
            bg = Image.new("RGBA", (cw, ch), (150, 160, 150, 255))
            bg.alpha_composite(c.resize((cw, ch), Image.NEAREST))
            sheet.paste(bg.convert("RGB"), (lw + aj * (cw + pad), y))
    return sheet


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "down"
    src_name, free_row, cap = SOURCES[which]
    if "--compare-cap" in sys.argv:
        img = np.asarray(Image.open(os.path.join(REFS, src_name)).convert("RGBA"), np.uint8)
        out = os.path.join(PLAYER, f"arm_cap_comparison_{which}.png")
        compare_caps(img, free_row).save(out)
        print("  wrote", os.path.relpath(out, REPO))
        return
    src = os.path.join(REFS, src_name)
    img = np.asarray(Image.open(src).convert("RGBA"), np.uint8)

    out_dir = os.path.join(REFS, which)
    os.makedirs(out_dir, exist_ok=True)
    body, arm, pivot = split(img, free_row, cap=cap)
    if pivot is None:
        sys.exit("could not find a separable arm — check the free_row for this direction")

    Image.fromarray(body, "RGBA").save(os.path.join(out_dir, "body.png"))
    Image.fromarray(arm, "RGBA").save(os.path.join(out_dir, "arm.png"))
    ys, xs = np.where(arm[..., 3] > 0)
    print(f"  {which}: arm cols {xs.min()}-{xs.max()} rows {ys.min()}-{ys.max()}  pivot {pivot}")
    print(f"  body pixels {(body[...,3]>0).sum()}   arm pixels {(arm[...,3]>0).sum()}")

    pj = os.path.join(REFS, "pivots.json")
    piv = json.load(open(pj)) if os.path.exists(pj) else {}
    piv[which] = {"shoulder": list(pivot), "source": src_name, "free_row": free_row, "cap": cap}
    json.dump(piv, open(pj, "w"), indent=2)

    ase = build_ase(out_dir, img, body, arm)
    print("  wrote", os.path.relpath(out_dir, REPO) + "/{body,arm}.png" + (" + split.aseprite" if ase else ""))
    print("  preview:", os.path.relpath(preview(out_dir, body, arm, pivot, which), REPO))


if __name__ == "__main__":
    main()
