"""split_base_arm.py — split a character base into BODY + WEAPON ARM.

A weapon swing needs the arm to rotate, so it has to be its own sprite. The wrong way is to cut an arm
out of a finished armour render: the cut is ragged, it fragments when rotated, and it bites a hole in the
torso. The right way is to split the BASE once — then every armour set generated onto the split pieces is
already in the correct shape.

Which seam the split follows depends on the view, and the two cases are not equally easy:

- **gap** (front, back) — below the shoulder the arm already hangs clear of the torso, separated by a column
  of empty pixels. Taking the connected blob on the weapon side lifts out a whole limb AND leaves the body
  intact, so there is no socket to repaint: the shoulder never belonged to the arm. Lossless and automatic.
- **colour** (profile) — the arm is drawn over the torso with no gap, so the seam is bare limb (saturated
  skin) against clothing (pale) instead. Harder, because the arm sits on the silhouette EDGE: lifting it out
  deletes the torso's back rather than opening a hole in the middle, and nothing in the source says what
  belongs there. The reconstruction is a starting point that always wants hand finishing.

Reads the locked bases from `references/` and writes NOTHING there. Output goes to a dated attempt folder,
per tools/_generated/player/README.md:
    in-progress/arm-split/<date>/<dir>/body.png · arm.png · split.aseprite · pivot in pivots.json

  python3 tools/player_sprites/split_base_arm.py down                 # front  (gap split)
  python3 tools/player_sprites/split_base_arm.py side                 # profile (colour split)
  python3 tools/player_sprites/split_base_arm.py down --compare-cap   # choose a shoulder cap by eye
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
REFS = os.path.join(PLAYER, "references")          # READ-ONLY: the locked bases, nothing gets written here
# Working output goes to a dated attempt folder, per tools/_generated/player/README.md ("Never dump loose
# files"). references/ holds only the base/bald/mannequin every attempt masks against.
WORK = os.path.join(PLAYER, "in-progress", "arm-split", "2026-07-28_arm-split")
ASEPRITE = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Aseprite/Aseprite.exe"

# Per direction: the source image and which seam to follow (see the module docstring for the two methods).
#   gap    — free_row is where the arm stops being fused to the shoulder; cap is how many shoulder rows the
#            arm carries. `down`'s cap of 3 was chosen by looking at arm_cap_comparison_down.png: 0 hinges at
#            the armpit and detaches by 50°, 2 still notches at the arm root, 4 rides up into the chest.
#            Re-run --compare-cap for a new direction rather than reusing this number.
#   colour — torso_rows bounds the band searched for the limb, so the legs (also bare skin) can't be picked.
SOURCES = {
    "down": {"src": "base.png", "how": "gap", "free_row": 37, "cap": 3},
    "side": {"src": "base_side.png", "how": "colour", "torso_rows": (17, 42)},
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


def split_side(img, torso_rows, sat_cut=0.42, cap=3):
    """Split a PROFILE view, where the arm overlaps the torso instead of hanging clear of it.

    The front view splits on a gap in the silhouette. A profile has no gap — the arm is drawn over the body
    — so the seam is a COLOUR boundary instead: bare limb (saturated skin) against clothing (pale, desaturated).

    The harder half is that the arm sits on the silhouette EDGE, so lifting it out doesn't open a hole in the
    middle of the torso, it deletes the torso's whole back. Nothing in the source says what belongs there, so
    this fills it by extending the body inward from the clothed side and keeps the original outline. That is a
    STARTING POINT for hand work in split.aseprite, not a finished piece.
    """
    op = img[..., 3] > 0
    rgb = img[..., :3].astype(int)
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    skin = op & (sat > sat_cut) & (rgb[..., 0] > 150)

    r0, r1 = torso_rows
    band = np.zeros_like(op)
    band[r0:r1 + 1] = skin[r0:r1 + 1]
    lbl, n = label(band, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    if n == 0:
        return img.copy(), np.zeros_like(img), None
    sizes = [(lbl == i).sum() for i in range(1, n + 1)]
    arm_mask = lbl == (int(np.argmax(sizes)) + 1)

    arm = np.zeros_like(img)
    arm[arm_mask] = img[arm_mask]

    # rebuild the body under the arm: walk each row from the clothed side into the vacated pixels
    body = img.copy()
    for y in range(img.shape[0]):
        xs = np.where(arm_mask[y])[0]
        if not len(xs):
            continue
        src = None
        for x in range(xs.max() + 1, img.shape[1]):        # nearest kept pixel toward the clothed side
            if op[y, x] and not arm_mask[y, x]:
                src = x
                break
        if src is None:
            for x in range(xs.min() - 1, -1, -1):
                if op[y, x] and not arm_mask[y, x]:
                    src = x
                    break
        if src is None:
            continue
        # mirror the clothing outward from the seam rather than flat-filling the row: a single sampled colour
        # per row lays down obvious horizontal banding across the torso, whereas reflecting keeps the fabric's
        # own shading and folds
        for x in range(xs.min(), xs.max() + 1):
            m = src + (src - x)
            if not (0 <= m < img.shape[1] and op[y, m] and not arm_mask[y, m]):
                m = src
            body[y, x] = img[y, m]

    ys, xs = np.where(arm_mask)
    top = ys.min()
    pivot = (int(round(xs[ys == top].mean())), int(top))
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
    cfg = SOURCES[which]
    src_name = cfg["src"]
    src = os.path.join(REFS, src_name)
    img = np.asarray(Image.open(src).convert("RGBA"), np.uint8)

    if "--compare-cap" in sys.argv:
        if cfg["how"] != "gap":
            sys.exit(f"--compare-cap only applies to gap splits; {which} uses {cfg['how']}")
        out = os.path.join(WORK, f"arm_cap_comparison_{which}.png")
        compare_caps(img, cfg["free_row"]).save(out)
        print("  wrote", os.path.relpath(out, REPO))
        return

    out_dir = os.path.join(WORK, which)
    os.makedirs(out_dir, exist_ok=True)
    if cfg["how"] == "gap":
        body, arm, pivot = split(img, cfg["free_row"], cap=cfg["cap"])
    else:
        body, arm, pivot = split_side(img, cfg["torso_rows"])
        print("  NOTE: profile split — the torso behind the arm is RECONSTRUCTED, not recovered.")
        print("        Treat body.png as a starting point and finish it in split.aseprite.")
    if pivot is None:
        sys.exit("could not find a separable arm — check this direction's split settings")

    Image.fromarray(body, "RGBA").save(os.path.join(out_dir, "body.png"))
    Image.fromarray(arm, "RGBA").save(os.path.join(out_dir, "arm.png"))
    ys, xs = np.where(arm[..., 3] > 0)
    print(f"  {which}: arm cols {xs.min()}-{xs.max()} rows {ys.min()}-{ys.max()}  pivot {pivot}")
    print(f"  body pixels {(body[...,3]>0).sum()}   arm pixels {(arm[...,3]>0).sum()}")

    pj = os.path.join(WORK, "pivots.json")
    piv = json.load(open(pj)) if os.path.exists(pj) else {}
    piv[which] = {"shoulder": list(pivot), "source": src_name, "how": cfg["how"]}
    json.dump(piv, open(pj, "w"), indent=2)

    ase = build_ase(out_dir, img, body, arm)
    print("  wrote", os.path.relpath(out_dir, REPO) + "/{body,arm}.png" + (" + split.aseprite" if ase else ""))
    print("  preview:", os.path.relpath(preview(out_dir, body, arm, pivot, which), REPO))


if __name__ == "__main__":
    main()
