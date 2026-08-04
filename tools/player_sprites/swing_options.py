"""swing_options.py — the vertical sword swings, one- and two-handed, to pick from. FREE, no API.

  python3 tools/player_sprites/swing_options.py

Writes 8 gifs + a side-by-side sheet into
`tools/_generated/player/reviews/<date>-swing/`, next to the approved reference so there is something
real to judge against rather than an opinion.

WHY VERTICAL ONLY
-----------------
A hand sprite is drawn from ONE viewpoint and that viewpoint tells the viewer where the arm is. Looking
down at the knuckles reads as an arm STRETCHED OUT; the back of the hand reads as an arm that is NOT
extended, because on an arm reaching out to the side the wrist turns the hand edge-on. A ~250 degree
LATERAL arc therefore contradicts its own hand sprite across most of its travel, which is why every
previous swing read as impossible while no single part looked wrong.

Top-to-bottom removes the conflict instead of drawing around it, so one hand carries the whole motion and
no new art is needed.

THE TWO HANDS ARE A PAIR, ONE PER ARM
------------------------------------
Approved together 2026-08-01: `grip_back_of_hand.png` is the arm you see the BACK of, `grip_palm.png` is
"the other arm so you would see the palm". Two-handed uses BOTH. Never mirror one to make the other —
mirroring the back of a hand gives a mirrored back of a hand, never a palm.
"""
import datetime
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import render_animations as R                            # noqa: E402
import swing_lab as S                                    # noqa: E402

OUTFIT = "bronze"
TOOL = "sword"
BG = (150, 160, 150)


def out_dir():
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing")
    os.makedirs(d, exist_ok=True)
    return d


def render(approach, two_handed):
    hands, prov = R.load_hands(OUTFIT)
    side = R.load_bank(OUTFIT, "side", 1)
    body = side[1]
    bh = gait.anchor(body)[1] - gait.anchor(body)[0] + 1
    icon = os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])
    frames, ms = R.swing_frames(body, hands, icon, bh, two_handed=two_handed,
                                approach=approach, pad=210)
    return frames, ms, prov


def crop_union(frames, margin=14):
    """Crop every frame to the union of what they actually draw.

    Rendered with a generous pad so a near-vertical blade is never clipped, which leaves most of the
    canvas empty and makes the options hard to compare side by side. The union box keeps the whole arc
    and throws away only background, so nothing moves between frames.
    """
    bg = np.array(BG, np.int16)
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for f in frames:
        d = np.abs(np.asarray(f, np.int16) - bg).sum(2) > 24
        if not d.any():
            continue
        ys, xs = np.where(d)
        x0, x1 = min(x0, xs.min()), max(x1, xs.max())
        y0, y1 = min(y0, ys.min()), max(y1, ys.max())
    if x1 < 0:
        return frames
    W, H = frames[0].size
    box = (max(0, x0 - margin), max(0, y0 - margin),
           min(W, x1 + 1 + margin), min(H, y1 + 1 + margin))
    return [f.crop(box) for f in frames]


def contact_index(approach, n):
    """Index of the frame where the blade is at its LOWEST angle — the real contact pose."""
    p = S.TOOLS[TOOL]
    angs = [S.motion(approach, p, i / (n - 1))[0] for i in range(n)]
    return int(min(range(n), key=lambda i: angs[i]))


def main():
    d = out_dir()
    made, idx = [], []
    for approach, name in sorted(S.VERTICALS.items()):
        for two in (False, True):
            frames, ms, prov = render(approach, two)
            frames = crop_union(frames)
            hands_lbl = "2h" if two else "1h"
            p = os.path.join(d, f"sword_{hands_lbl}_V{approach - 19}_{name}.gif")
            frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0)
            made.append((f"{hands_lbl}  V{approach - 19} {name}", p, frames))
            idx.append(contact_index(approach, len(frames)))
            print(f"  {os.path.basename(p):38} {len(frames):3} frames   hands = {prov}")

    # one sheet: every option's contact-ish frame, side by side, so they can be compared at a glance
    W = max(f[0].size[0] for _, _, f in made)
    H = max(f[0].size[1] for _, _, f in made)
    cols = 4
    rows = (len(made) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * (H + 22)), (28, 28, 34))
    dr = ImageDraw.Draw(sheet)
    for k, (lbl, _, frames) in enumerate(made):
        # the frame where the tool reaches its LOWEST angle — the actual contact pose. A fixed
        # fraction of the timeline lands somewhere different in each variant, which made the first
        # sheet compare a mid-lift against a follow-through.
        im = frames[idx[k]]
        x, y = (k % cols) * W, (k // cols) * (H + 22)
        bg = Image.new("RGB", (W, H), BG)
        bg.paste(im, ((W - im.size[0]) // 2, 0))
        sheet.paste(bg, (x, y + 22))
        dr.text((x + 6, y + 6), lbl, fill=(255, 220, 140))
    sp = os.path.join(d, "ALL_EIGHT_contact_frame.png")
    sheet.save(sp)
    print(f"\n  {sp.replace('/mnt/c/', 'C:/')}")

    ref = os.path.join(R.PLAYER, "APPROVED", "06_SWING_iteration11_best_overall.gif")
    if os.path.exists(ref):
        import shutil
        shutil.copy(ref, os.path.join(d, "REFERENCE_what_we_have_now.gif"))
    print(f"  {d.replace('/mnt/c/', 'C:/')}")
    return d


if __name__ == "__main__":
    main()
