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

# Every bank is measured against frame 2, the passing pose — feet together, directly under the hips.
# Body height, torso centre and torso width come from it once, so they cannot jitter as the legs move.
NEUTRAL = 1


class Missing(Exception):
    """A file named in official.py is not on disk. Always names the outfit and the path."""


def _rgba(path, why):
    if not os.path.exists(path):
        raise Missing(f"{why}\n    expected: {os.path.relpath(path, REPO)}")
    return np.asarray(Image.open(path).convert("RGBA"), np.uint8)


# ── loading — every path comes from official.py ──────────────────────────────────────────────────────

# ── PIXEL SCALE ──────────────────────────────────────────────────────────────────────────────────────
# EVERYTHING COMPOSITES AT NATIVE RESOLUTION AND IS UPSCALED **ONCE**, BY A WHOLE NUMBER, AT THE END.
#
# It used to normalise every outfit to `TARGET_BODY_H = 320` on load. That factor is never a whole
# number — measured 3.678x for black-ant, 4.156x for fire-ant, 4.706x for bronze — and a fractional
# NEAREST resize makes some source pixels 4 screen-px wide and the ones beside them 5. The sprite stops
# being on a grid, which is the whole point of converting it to pixels in the first place. Owner,
# 2026-08-18: *"NOT THE RAW version the PIXEL version"*.
#
# It also normalised on the TOTAL figure height, headgear included, so a tall-helmeted outfit's BODY
# came out smaller — the same mistake as the pre-2026-08-18 hand placement.
#
# Consequence, and it is intended: outfits are no longer forced to one on-screen height. Bronze is 68
# native px and black-ant 87, so black-ant now genuinely renders taller. That difference is real and
# was previously being hidden.
PIXEL_SCALE = 4


def upscale(im):
    """One whole-number NEAREST enlargement of a finished frame. The only resize in the render."""
    return im.resize((im.width * PIXEL_SCALE, im.height * PIXEL_SCALE), Image.NEAREST)


def load_frames(outfit, bank):
    """The four frames of one direction, at their NATIVE pixel size.

    Four frames, always: contact, passing, opposite contact, opposite passing. Every outfit is cut by
    `cut_walk_row.py` from a one-direction-per-call render, so they all arrive in the same shape.

    No resize here — see PIXEL_SCALE above.
    """
    d = os.path.join(PLAYER, O.path(outfit, O.FRAMES_DIR))
    imgs = [_rgba(os.path.join(d, f"{bank}_{i}.png"),
                  f"{outfit}: frame {bank}_{i}.png is missing") for i in (1, 2, 3, 4)]
    y0, y1, _, _ = gait.anchor(imgs[NEUTRAL])
    body_h = y1 - y0 + 1
    if body_h <= 0:
        raise Missing(f"{outfit}: {bank} frames are blank")
    return imgs


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
    for beat, which in enumerate(gait.CYCLE):
        sc = scene(W, H)
        gait.pose_into(sc, W / 2, H / 2, bank[which - 1], neutral,
                       hands["front"], hands["back"], beat, p)
        out.append(finish(sc))
    return out


def _gait_front_frames(bank, neutral, hands, p):
    """The camera-facing walk — a separate motion, not the side one re-aimed.

    This used to TRANSCRIBE `gait.walk_front_into` so the numbers could come from official.py. That was a
    mistake: two copies of one motion is two answers to "what is it", and they duly drifted — the fix that
    turned the palms inward landed here and not there, so everything still calling `gait` kept rendering
    palms-out. Now it calls the one implementation and passes official.py's numbers in.
    """
    W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
    out = []
    for beat, which in enumerate(gait.CYCLE):
        sc = scene(W, H)
        gait.walk_front_into(sc, W / 2, H / 2, bank[which - 1], neutral,
                             hands["side"], beat, p)
        out.append(finish(sc))
    return out


def render(outfit, name):
    """One animation -> (frames, ms). Every parameter comes from its row in official.ANIMATIONS."""
    a = O.ANIMATIONS[name]
    bank = load_frames(outfit, a["frames"])
    hands = load_hands(outfit)
    neutral = bank[NEUTRAL]

    if a["kind"] in ("gait", "gait_front"):
        p = O.GAITS[a["motion"]]
        frames = (_gait_frames(bank, neutral, hands, a, p) if a["kind"] == "gait"
                  else _gait_front_frames(bank, neutral, hands, p))
        return [upscale(f) for f in frames], p["ms"]

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
    return [upscale(f) for f in frames], ms[0]


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
        # `ALL_ANIMATIONS.gif` is the every-animation-in-one sheet written by `gallery_gif.py --outfit`.
        # It is not an animation, so it is not in official.ANIMATIONS — but it lives here because this
        # is where someone looks for "show me this outfit". Without this line the next build silently
        # deletes it, which is precisely the class of loss the stale-sweep exists to prevent.
        keep = {f"{n}.gif" for n in O.ANIMATIONS} | {"ALL_ANIMATIONS.gif"}
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

    # A PENDING outfit renders ONLY when named explicitly on the command line — never by default, and
    # never into the gallery. That is the whole distinction: OUTFITS is what the project ships, PENDING
    # is something you can look at before deciding. Without this an outfit could not be reviewed until
    # it was already declared official, which is backwards.
    targets = args.outfits or list(O.OUTFITS)
    unknown = [o for o in targets if o not in O.OUTFITS and o not in O.PENDING]
    if unknown:
        raise SystemExit(f"not in official.py: {', '.join(unknown)}\n"
                         f"  official outfits: {', '.join(O.OUTFITS)}\n"
                         f"  pending (name one explicitly to render it for review):"
                         f" {', '.join(O.PENDING) or '(none)'}")
    for o in targets:
        if o in O.PENDING:
            print(f"  ⚠ {o} is PENDING — rendering for review, NOT official.")

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
