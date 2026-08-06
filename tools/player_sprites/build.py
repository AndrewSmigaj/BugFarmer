"""build.py — render every official animation for an outfit. FREE, no API.

    python3 tools/player_sprites/build.py            # every outfit in official.py
    python3 tools/player_sprites/build.py bronze     # one
    python3 tools/player_sprites/build.py --check    # rebuild and compare; changes nothing on disk

READS `official.py` AND NOTHING ELSE
------------------------------------
No `os.listdir`, no globbing for sprites, and **no fallbacks**. Every path comes from `official.OUTFITS`,
and if a file named there is absent the build STOPS and prints which one.

That is the whole point, so it is worth being blunt about why. The old renderer resolved an outfit's hands
by trying three folders in order and taking whichever existed. Measured across all 24 outfits, that sent 21
of them to a gitignored archive nobody had chosen. Not one line of build code ever opened `DECISIONS.md`
or `CURRENT.md`, so "what is official" and "what gets loaded" were different things, and the gallery showed
whatever was on disk. A missing file must be an ERROR, never a substitution.

If you ever find yourself about to write "if this exists use it, otherwise use that one" in this file —
that is the bug. Stop and say so.
"""
import argparse
import hashlib
import io
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                                  # noqa: E402  the owner's approved gait maths
import official as O                                         # noqa: E402  the only source of truth
from render_animations import (attack_frames, finish, scene,  # noqa: E402  the approved swing rig
                               PAD, TARGET_BODY_H, _scaled)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

# The neutral frame each bank measures itself against — side stands on 2, the camera-facing banks on 1.
NEUTRAL = {"side": 1, "front": 0, "back": 0}


class Missing(Exception):
    """A file named in official.py is not on disk. Always names the outfit and the path."""


def _rgba(path, why):
    if not os.path.exists(path):
        raise Missing(f"{why}\n    expected: {os.path.relpath(path, REPO)}")
    return np.asarray(Image.open(path).convert("RGBA"), np.uint8)


# ── loading — every path comes from official.py ──────────────────────────────────────────────────────

def load_frames(outfit, bank):
    """Frames 1..3 of one direction, normalised so every outfit renders at the same body height.

    The 24 sheets on disk were cut at two different scales (a 1.63x split), which is a cutting artifact
    rather than a difference in the art — side by side it reads as "these characters are different sizes".
    NEAREST only; never a hand resize.
    """
    d = os.path.join(PLAYER, O.path(outfit, O.FRAMES_DIR))
    imgs = [_rgba(os.path.join(d, f"{bank}_{i}.png"),
                  f"{outfit}: frame {bank}_{i}.png is missing") for i in (1, 2, 3)]
    y0, y1, _, _ = gait.anchor(imgs[NEUTRAL[bank]])
    body_h = y1 - y0 + 1
    if body_h <= 0:
        raise Missing(f"{outfit}: {bank} frames are blank")
    return [_scaled(a, TARGET_BODY_H / body_h) for a in imgs]


def load_hands(outfit):
    """All five hands. Every role in official.HAND_ROLES must be present — no role is optional.

    The walk/run roles are flipped (the sheets are drawn fingers-up, cuff-down; a straight paste gives a
    hand hanging at the waist with its fingers pointing at the sky). The GRIP roles are not flipped —
    they are already posed around a shaft.
    """
    d = os.path.join(PLAYER, O.path(outfit, O.HANDS_DIR))
    out = {}
    for role in O.HAND_ROLES:
        a = _rgba(os.path.join(d, f"{role}.png"),
                  f"{outfit}: hand '{role}' is missing ({O.HAND_ROLE_MEANING[role]})")
        out[role] = a if role.startswith("grip") else gait.flip(a)
    return out


# ── rendering ────────────────────────────────────────────────────────────────────────────────────────

def _gait_frames(bank, neutral, hands, spec, p):
    """The side walk/run: fists swing through the torso centre, the far one dimmed and drawn behind."""
    W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
    out = []
    for beat in range(len(gait.CYCLE)):
        sc = scene(W, H)
        gait.pose_into(sc, W / 2, H / 2, bank[gait.CYCLE[beat] - 1], neutral,
                       hands["front"], hands["back"], beat, p)
        out.append(finish(sc))
    return out


def _gait_front_frames(bank, neutral, hands, p):
    """The camera-facing walk — a separate motion, not the side one re-aimed.

    Transcribed from `gait.walk_front_into` so the numbers come from official.py rather than from a
    constant buried in gait.py. The byte-identical gate is what proves the transcription is faithful.
    Hands sit OUTSIDE the body edges (measured per frame, since the legs change the silhouette), one
    rising as the other drops, neither rotated nor dimmed.
    """
    W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
    ny0, ny1, _, _ = gait._bbox(neutral)
    bh = ny1 - ny0 + 1
    hand = gait._sz(hands["side"], bh, p["ratio"])
    out = []
    for beat in range(len(gait.CYCLE)):
        sc = scene(W, H)
        body = bank[gait.CYCLE[beat] - 1]
        bx, by = W / 2, H / 2
        h, w = body.shape[:2]
        ox, oy = bx - w / 2.0, by - h / 2.0
        r, lx, rx = gait._edges(body, p["row"])
        span = rx - lx
        s = gait.FRONT_PHASE[beat % len(gait.FRONT_PHASE)]
        gap = max(2, int(span * p["gap"]))
        # PALMS TURN IN, TOWARD THE BODY. The LEFT hand is the mirrored one.
        # Mirroring the RIGHT one instead turns both palms OUT, away from him — which is what shipped
        # and what the owner reported twice ("the palms are facing out when they should be facing in").
        # Rendered as all four options in reviews/2026-08-06-bronze-hands/PALMS_compare.png; A and D
        # point both hands the same way, so a symmetric pair is B or C, and C is the one he rejected.
        gait._paste(sc, body, bx, by)
        gait._paste(sc, hand[:, ::-1], ox + lx - gap - s * span * p["dx"], oy + r - s * span * p["dy"])
        gait._paste(sc, hand, ox + rx + gap + s * span * p["dx"], oy + r + s * span * p["dy"])
        out.append(finish(sc))
    return out


def render(outfit, name):
    """One animation -> (frames, ms). Every parameter comes from its row in official.ANIMATIONS."""
    a = O.ANIMATIONS[name]
    bank = load_frames(outfit, a["frames"])
    hands = load_hands(outfit)
    neutral = bank[NEUTRAL[a["frames"]]]

    if a["kind"] in ("gait", "gait_front"):
        p = O.GAITS[a["motion"]]
        frames = (_gait_frames(bank, neutral, hands, a, p) if a["kind"] == "gait"
                  else _gait_front_frames(bank, neutral, hands, p))
        return frames, p["ms"]

    tool = os.path.join(RES, "Items", a["tool"])
    if not os.path.exists(tool):
        raise Missing(f"{outfit}/{name}: tool sprite missing\n    expected: {os.path.relpath(tool, REPO)}")
    y0, y1, _, _ = gait.anchor(neutral)
    cfg = dict(centre=a["aim"], sh=a["shoulder"], behind=a.get("behind", False))
    frames, ms = attack_frames(neutral, hands, tool, y1 - y0 + 1, cfg,
                               spec=O.SWINGS[a["motion"]],
                               two_handed=a.get("two_handed", False),
                               scale=a.get("scale", 1.0),
                               pivot=a.get("pivot", 0.0),
                               second=a.get("second", 0.17))
    return frames, ms[0]


def encode(frames, ms):
    """GIF bytes. Kept separate from writing so --check can compare without touching the disk."""
    buf = io.BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=ms, loop=0)
    return buf.getvalue()


def build(outfit, check=False, verbose=True):
    """Render every official animation. Returns (written, unchanged, differing).

    `build` OWNS `<outfit>/anim/`: anything in there that official.py does not name is removed. A stale
    file is how `thrust_spear_two_handed.gif` sat in 22 outfits and showed in the gallery for weeks after
    the code that produced it stopped existing.
    """
    anim = os.path.join(PLAYER, O.path(outfit, O.ANIM_DIR))
    written, same, diff = [], [], []
    for name in O.ANIMATIONS:
        data = encode(*render(outfit, name))
        path = os.path.join(anim, f"{name}.gif")
        old = open(path, "rb").read() if os.path.exists(path) else None
        if old == data:
            same.append(name)
        elif check:
            diff.append(name)
        else:
            os.makedirs(anim, exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            written.append(name)

    stale = []
    if os.path.isdir(anim):
        keep = {f"{n}.gif" for n in O.ANIMATIONS}
        stale = sorted(f for f in os.listdir(anim) if f.endswith(".gif") and f not in keep)
        if stale and not check:
            for f in stale:
                os.remove(os.path.join(anim, f))

    if verbose:
        tag = "would write" if check else "wrote"
        print(f"  {outfit}: {len(same)} unchanged, {tag} {len(written) + len(diff)}"
              + (f", removed {len(stale)} stale" if stale else ""))
        for f in stale:
            print(f"      stale (not in official.py): {f}")
        for n in diff:
            print(f"      DIFFERS: {n}")
    return written, same, diff


def status():
    """What is official, what is pending, and what each pending outfit still needs."""
    print(f"\nOFFICIAL — built from official.py ({len(O.OUTFITS)})")
    for name, o in O.OUTFITS.items():
        parts = []
        for kind in (O.FRAMES_DIR, O.HANDS_DIR):
            d = os.path.join(PLAYER, O.path(name, kind))
            n = len([f for f in os.listdir(d) if f.endswith(".png")]) if os.path.isdir(d) else 0
            parts.append(f"{kind} {n}")
        anim = os.path.join(PLAYER, O.path(name, O.ANIM_DIR))
        n = len([f for f in os.listdir(anim) if f.endswith(".gif")]) if os.path.isdir(anim) else 0
        print(f"  {name:<12} {', '.join(parts)}, anim {n}/{len(O.ANIMATIONS)}")
        print(f"  {'':<12} approved {o['approved']} — \"{o['words']}\"")

    if O.PENDING:
        print(f"\nNOT OFFICIAL — listed, deliberately NOT built ({len(O.PENDING)})")
        for name, o in O.PENDING.items():
            print(f"  {name:<12} needs: {o['needs']}")

    print(f"\n{len(O.ANIMATIONS)} animations declared. Hand roles: {', '.join(O.HAND_ROLES)}")
    if O.NOT_AGREED:
        print("\nNOT AGREED — absent from ANIMATIONS so it cannot render by accident")
        for k, v in O.NOT_AGREED.items():
            print(f"  {k:<28} {v}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("outfits", nargs="*", help="default: every outfit in official.py")
    ap.add_argument("--check", action="store_true",
                    help="compare against what is on disk; write nothing")
    ap.add_argument("--status", action="store_true",
                    help="what is official, what is pending, what is not agreed")
    args = ap.parse_args()

    if args.status:
        status()
        return

    targets = args.outfits or list(O.OUTFITS)
    unknown = [o for o in targets if o not in O.OUTFITS]
    if unknown:
        raise SystemExit(f"not in official.py: {', '.join(unknown)}\n"
                         f"  official outfits: {', '.join(O.OUTFITS)}")

    total_diff = 0
    for o in targets:
        try:
            _, _, diff = build(o, check=args.check)
            total_diff += len(diff)
        except Missing as e:
            raise SystemExit(f"\nSTOPPED — {e}\n\n"
                             f"  Nothing was substituted. Either add the file, or remove '{o}' from\n"
                             f"  official.py until it has one.")
    if args.check and total_diff:
        raise SystemExit(f"\n{total_diff} animation(s) differ from what is committed.")


if __name__ == "__main__":
    main()
