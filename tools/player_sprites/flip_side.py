"""flip_side.py — mirror an outfit's SIDE frames so it faces right. FREE, no API.

  python3 tools/player_sprites/flip_side.py copper farmer          # DRY RUN, shows what it would do
  python3 tools/player_sprites/flip_side.py copper farmer --go     # do it

WHY THIS EXISTS
---------------
The sheet prompt asks for "a strict RIGHT-facing side profile", but the model sometimes draws the side
row facing LEFT anyway. Everything downstream assumes right-facing: the walk swings `back_hand` to `+dx`
as the forward hand, and every swing motion arcs toward +x. A left-facing outfit therefore walks and
swings backwards. Owner, 2026-08-03: "the copper is backwards".

Mirroring is the sanctioned fix and it is free and exact — the skill already says "Left = mirror of
right. Never generate it." Re-generating the sheet would cost money and change the art.

YOU NAME THE OUTFIT. THIS DOES NOT AUTO-DETECT.
A centroid heuristic ("the visor overhangs toward the facing direction") was tried and agreed with a
careful visual read on only 6 of 8 outfits. A detector that is wrong a quarter of the time would mirror
sprites the WRONG way, silently, across the whole set. So a human looks and names them.

To check by eye: open the gallery, or render the side frames together — the face, visor slit or hat
brim points the way the character faces. It must point RIGHT.

ONLY `side_*.png` IS TOUCHED. Front and back frames face the camera and away; they have no handedness,
and mirroring them would flip asymmetric details for no reason.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_animations as R                            # noqa: E402


def side_frames(outfit):
    d = R.frames_dir(outfit)
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.startswith("side_") and f.lower().endswith(".png"))


def flip_outfit(outfit, go=False):
    frames = side_frames(outfit)
    if not frames:
        print(f"  {outfit}: no side_*.png found")
        return 0
    for p in frames:
        rel = os.path.relpath(p, R.PLAYER).replace(os.sep, "/")
        print(f"  {'mirror' if go else 'would mirror'}  {rel}")
        if go:
            a = np.asarray(Image.open(p).convert("RGBA"), np.uint8)
            Image.fromarray(a[:, ::-1], "RGBA").save(p)
    return len(frames)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Mirror an outfit's side frames so it faces right.")
    ap.add_argument("outfits", nargs="+")
    ap.add_argument("--go", action="store_true", help="actually mirror (default is a dry run)")
    a = ap.parse_args()

    n = 0
    for o in a.outfits:
        if not os.path.isdir(R.outfit_dir(o)):
            raise SystemExit(f"no such outfit: {o}")
        n += flip_outfit(o, a.go)
    print(f"\n{n} frame(s) across {len(a.outfits)} outfit(s)")
    if not a.go:
        print("DRY RUN — nothing changed. Re-run with --go to apply.")
    else:
        print("Re-render the animations:  python3 tools/player_sprites/render_animations.py " +
              " ".join(a.outfits))
