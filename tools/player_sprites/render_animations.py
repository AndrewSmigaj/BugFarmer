"""render_animations.py — the finished animation set for one outfit. FREE, no API.

  python3 tools/player_sprites/render_animations.py bronze

Writes one gif per animation into `outfits/<outfit>/animations/`, each with a stable descriptive name.
There is exactly one file per animation and it is always the current one; history lives in git. No
iteration codes in filenames — that habit is what made 131 files indistinguishable.

WHICH HAND EACH ANIMATION USES, and why the rotation matters
-----------------------------------------------------------
The hand sheets are drawn FINGERS UP, CUFF DOWN. Drawn straight into a walk that gives you a hand
hanging at the waist with its fingers pointing at the sky, which is what happened and was rejected:
"fingers pointing upward for walking, backward and alternating between open and fist for the running".

So each animation picks its hand AND its base rotation deliberately:

  walk   relaxed hand, FLIPPED so the fingers hang down     rot 0
  run    relaxed hand, flipped then turned to point forward rot 75 (a runner's fist leads)
  swing  the APPROVED grip hands, knuckles pointing down    HAND_ROT 225, +16% down the handle

The grip hands are NOT reused for walking. Owner: "the weapon grabbing is NOT to be blindly replacing
walk and/or running - they all should be carefully thought about and the best one picked."
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import swing_lab as S                                    # noqa: E402
from compare_hands import cut_hands, rgba                # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

SWING_APPROACH = 11        # the one the owner picked as best overall
PAD = 90                   # scene margin so a swinging tool is never clipped

ONE_HANDED = [("sword", "sword_bronze_icon.png"), ("axe", "axe_copper_icon.png"),
              ("net", "small_net_icon.png"), ("hoe", "hoe_copper_icon.png"),
              ("shovel", "shovel_copper_icon.png")]
TWO_HANDED = [("spear", "spear_bronze_icon.png")]


def scene(w, h):
    return np.zeros((h, w, 4), np.uint8)


def finish(sc):
    im = Image.new("RGBA", (sc.shape[1], sc.shape[0]), (150, 160, 150, 255))
    im.alpha_composite(Image.fromarray(sc, "RGBA"))
    return im.convert("RGB")


def save(frames, ms, path):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    return path


def swing_frames(body, hands, tool_png, bh, two_handed=False):
    """One full swing. Two-handed puts the second grip further up the handle."""
    cell = bh / 2.0
    art = S.scale_h(rgba(tool_png), cell)
    g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]
    p = dict(S.TOOLS["sword"])
    kind = {"sword_bronze_icon.png": "sword", "axe_copper_icon.png": "axe",
            "small_net_icon.png": "net", "hoe_copper_icon.png": "hoe",
            "shovel_copper_icon.png": "shovel", "spear_bronze_icon.png": "spear"}[os.path.basename(tool_png)]
    p = S.TOOLS[kind]
    n = max(12, int(S.duration(SWING_APPROACH, p) * S.FPS * 4))
    W, H = body.shape[1] + 2 * PAD, body.shape[0] + PAD
    out, ms = [], []
    for i in range(n):
        t = i / (n - 1)
        ang, off, freeze, smear = S.motion(SWING_APPROACH, p, t)
        sc = scene(W, H)
        bx, by = W / 2, H / 2
        ny0, ny1, cx, _ = gait.anchor(body)
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        r = math.radians(ang)
        tx = ox + cx + math.cos(r) * off * cell
        ty = oy + ny0 + (ny1 - ny0) * 0.5 - math.sin(r) * off * cell
        gait._paste(sc, body, bx, by)
        if smear:
            for k, al in ((7, 0.26), (14, 0.13)):
                gait._paste(sc, S.rot(art, ang + k - S.ART_ANGLE), tx, ty)
        gait._paste(sc, S.rot(art, ang - S.ART_ANGLE), tx, ty)
        rr = math.radians(-(ang - S.ART_ANGLE))
        grips = [(hands["grip_back"], 0.0)]
        if two_handed:
            grips.append((hands["grip_palm"], 0.17))
        for hand, extra in grips:
            gg = g - S.DIAG * extra * art.shape[0]
            gait._paste(sc, gait._sz(S.rot(hand, ang - S.ART_ANGLE + S.HAND_ROT), bh, gait.RUN["ratio"]),
                        tx + gg[0] * math.cos(rr) - gg[1] * math.sin(rr),
                        ty + gg[0] * math.sin(rr) + gg[1] * math.cos(rr))
        out.append(finish(sc))
        ms.append(int(S.duration(SWING_APPROACH, p) * 1000 / n) * (3 if freeze else 1))
    return out, ms


def build(outfit="bronze"):
    d = os.path.join(PLAYER, "outfits", outfit)
    anim = os.path.join(d, "animations")
    os.makedirs(anim, exist_ok=True)

    # relaxed hands for the gaits, FLIPPED so the fingers hang down instead of pointing at the sky
    raw = cut_hands(os.path.join(d, "hands", "candidates", "set_a", "result.png"))
    hands = dict(walk_back=gait.flip(raw[0]), walk_palm=gait.flip(raw[1]),
                 grip_back=rgba(os.path.join(d, "hands", "grip_back_of_hand.png")),
                 grip_palm=rgba(os.path.join(d, "hands", "grip_palm.png")))

    side = [rgba(os.path.join(d, f"side_{i}.png")) for i in (1, 2, 3)]
    front = [rgba(os.path.join(d, f"front_{i}.png")) for i in (1, 2, 3)]
    bh = gait.anchor(side[1])[1] - gait.anchor(side[1])[0] + 1
    made = []

    for name, bank, fn, ms in [
            ("walk_side", side, gait.walk_into, gait.WALK["ms"]),
            ("run_side", side, gait.run_into, gait.RUN["ms"])]:
        fr = []
        W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
        for beat in range(len(gait.CYCLE)):
            sc = scene(W, H)
            fn(sc, W / 2, H / 2, bank[gait.CYCLE[beat] - 1], bank[1],
               hands["walk_back"], hands["walk_palm"], beat)
            fr.append(finish(sc))
        made.append(save(fr, ms, os.path.join(anim, f"{name}.gif")))

    for name, bank, ms in [("walk_front", front, gait.WALK["ms"]), ("run_front", front, gait.RUN["ms"])]:
        fr = []
        W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
        for beat in range(len(gait.CYCLE)):
            sc = scene(W, H)
            gait.walk_front_into(sc, W / 2, H / 2, bank[gait.CYCLE[beat] - 1], bank[0],
                                 hands["walk_back"], beat)
            fr.append(finish(sc))
        made.append(save(fr, ms, os.path.join(anim, f"{name}.gif")))

    for name, icon in ONE_HANDED:
        fr, ms = swing_frames(side[1], hands, os.path.join(RES, "Items", icon), bh)
        made.append(save(fr, ms, os.path.join(anim, f"swing_{name}.gif")))
    for name, icon in TWO_HANDED:
        fr, ms = swing_frames(side[1], hands, os.path.join(RES, "Items", icon), bh, two_handed=True)
        made.append(save(fr, ms, os.path.join(anim, f"thrust_{name}_two_handed.gif")))

    for p in made:
        print("  " + p.replace("/mnt/c/", "C:/"))
    return made


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "bronze")
