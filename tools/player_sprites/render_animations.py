"""render_animations.py — the finished animation set for one outfit, or all of them. FREE, no API.

  python3 tools/player_sprites/render_animations.py bronze
  python3 tools/player_sprites/render_animations.py --all

Writes one gif per animation into `outfits/<outfit>/current/anim/` (falling back to the pre-migration
`outfits/<outfit>/animations/`), each with a stable descriptive name. There is exactly one file per
animation and it is always the current one; history lives in git. No iteration codes in filenames — that
habit is what made 131 files indistinguishable.

EVERY OUTFIT RENDERS AT THE SAME SIZE
-------------------------------------
The 22 outfits on disk are cut at two different scales: 7 sit at 267-292px body height and 15 at
395-435px, a 1.63x split. That is a cutting artifact, not a difference in the art, and side by side it
reads as "these outfits are different sizes". So every frame bank is scaled (NEAREST only — never a hand
resize) so the character's measured body height equals TARGET_BODY_H before anything is animated. Each
direction is normalised against its own neutral frame, which also fixes outfits whose sheet rows came out
at slightly different scales.

This is deliberately a RENDER-TIME rule rather than a re-cut of the source art. The sprites are being
recreated anyway, and a bulk re-cut is what destroyed a day of approved work on 2026-08-01.

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

EACH OUTFIT USES ITS OWN GAUNTLET, not bronze's. Preferring bronze's hand-D-pixel fists where they
existed made bronze's hands a different SHAPE from everyone else's (aspect 0.80 vs 0.55-0.60), so across
a multi-set reel the hands were visibly different sizes. `gauntlet_dir` reports which source it used so
a placeholder can never be mistaken for the real thing.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import swing_lab as S                                    # noqa: E402
from compare_hands import rgba                           # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFITS = os.path.join(PLAYER, "outfits")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

# TWO swings were approved, not one. DECISIONS.md:
#   05_SWING_iteration7_best_for_SWORD  — "for the sword iteration 7 is the best"  (20:43)
#   06_SWING_iteration11_best_overall   — "iteration 11 looks best"                (23:37)
# So the sword uses 7 and everything else uses 11. Rendering all six tools with 11 threw away the
# sword pick, which is the one he named a tool for explicitly.
SWING_APPROACH = 11                # best overall
SWING_APPROACH_BY_TOOL = {"sword": 7}
APPROVED_HANDS_OUTFIT = "bronze"   # whose hands APPROVED/hands/h1..h3 are (from hand-D-pixel)
PAD = 90                   # scene margin so a swinging tool is never clipped
TARGET_BODY_H = 320        # every outfit is normalised to this measured body height

ONE_HANDED = [("sword", "sword_bronze_icon.png"), ("axe", "axe_copper_icon.png"),
              ("net", "small_net_icon.png"), ("hoe", "hoe_copper_icon.png"),
              ("shovel", "shovel_copper_icon.png")]
TWO_HANDED = [("spear", "spear_bronze_icon.png")]

# Where a gauntlet may live, best first. The 08-01 archive is where all 22 currently are; it is
# GITIGNORED, so those are one `git clean -fdx` from gone.
GAUNTLET_SOURCES = [
    (os.path.join("{d}", "current", "gauntlet"), "current"),
    (os.path.join("{d}", "gauntlet"), "outfit"),
    (os.path.join(PLAYER, "archive", "2026-08-01_pre-redo", "gauntlets", "{o}"), "archived (pending redo)"),
]


def outfit_dir(outfit):
    return os.path.join(OUTFITS, outfit)


def anim_dir(outfit):
    """Prefer the new current/anim/, fall back to the pre-migration animations/."""
    d = outfit_dir(outfit)
    new = os.path.join(d, "current", "anim")
    return new if os.path.isdir(os.path.join(d, "current")) else os.path.join(d, "animations")


def frames_dir(outfit):
    """Frames live in current/ after migration, at the outfit root before it."""
    d = outfit_dir(outfit)
    cur = os.path.join(d, "current")
    return cur if os.path.exists(os.path.join(cur, "side_1.png")) else d


def gauntlet_dir(outfit):
    """(path, provenance) for this outfit's own gauntlet, or (None, reason)."""
    d = outfit_dir(outfit)
    for tmpl, label in GAUNTLET_SOURCES:
        p = tmpl.format(d=d, o=outfit)
        if all(os.path.exists(os.path.join(p, f)) for f in ("front.png", "back.png")):
            return p, label
    return None, "none found"


def _scaled(a, f):
    if abs(f - 1.0) < 0.02:
        return a
    h, w = a.shape[:2]
    return np.asarray(Image.fromarray(a, "RGBA").resize(
        (max(1, round(w * f)), max(1, round(h * f))), Image.NEAREST), np.uint8)


def load_bank(outfit, kind, neutral_idx):
    """Frames 1..3 for one direction, normalised so the measured body height == TARGET_BODY_H.

    Returns None if the direction is incomplete — a missing direction is reported as a gap, never
    silently skipped.
    """
    d = frames_dir(outfit)
    paths = [os.path.join(d, f"{kind}_{i}.png") for i in (1, 2, 3)]
    if not all(os.path.exists(p) for p in paths):
        return None
    bank = [rgba(p) for p in paths]
    y0, y1, _, _ = gait.anchor(bank[neutral_idx])
    body_h = y1 - y0 + 1
    if body_h <= 0:
        return None
    return [_scaled(a, TARGET_BODY_H / body_h) for a in bank]


def load_hands(outfit):
    """Every hand this outfit's animations need, plus a note on where they came from.

    THE HANDS ARE ALREADY CHOSEN. `APPROVED/hands/` holds them and they win over everything:

        h1  knuckles / back of hand   walk + run, the NEAR hand
        h2  palm                      walk + run, the FAR hand (dimmed, behind the body)
        h3  profile                   walking toward or away from the camera

    They are what the reference gifs in `APPROVED/` were rendered with, so anything else does not match
    the approved look. Do not substitute:

      * NOT the tool-grip hands (`hands/grip_*.png`). Those are for SWINGS only. Owner: "the weapon
        grabbing is NOT to be blindly replacing walk and/or running."
      * NOT the cut gauntlet views (`gauntlet/{front,back,side}.png`) where an approved hand exists.
        `DECISIONS.md`: those "are a re-cut made on 08-01 and were never approved... anything unapproved
        living here is how the wrong sprite gets picked later." Which is exactly what happened — all 264
        animations were built on them, and the walk used a discarded sprite while the swing used a hand
        meant for holding a tool.

    An outfit with no approved hands of its own falls back to its OWN gauntlet in the SAME three roles —
    front->h1, back->h2, side->h3 — because those views were prompted to correspond.
    """
    approved = os.path.join(PLAYER, "APPROVED", "hands")
    h = {n: os.path.join(approved, f"{n}.png") for n in ("h1", "h2", "h3")}
    g, prov = gauntlet_dir(outfit)

    # h1/h2/h3 came from `hand-D-pixel` and are BRONZE's hands (DECISIONS.md). They are not a
    # universal set — handing them to silver would put bronze fists on silver armour.
    if outfit == APPROVED_HANDS_OUTFIT and all(os.path.exists(p) for p in h.values()):
        walk_back, walk_palm = gait.flip(rgba(h["h1"])), gait.flip(rgba(h["h2"]))
        profile, prov = gait.flip(rgba(h["h3"])), "APPROVED h1/h2/h3"
    elif g is not None:
        walk_back, walk_palm = gait.flip(rgba(os.path.join(g, "front.png"))), \
            gait.flip(rgba(os.path.join(g, "back.png")))
        side = os.path.join(g, "side.png")
        profile = gait.flip(rgba(side)) if os.path.exists(side) else walk_back
    else:
        return None, prov

    # THE TWO GRIPS ARE A PAIR, ONE PER ARM — approved together 2026-08-01:
    #   grip_back_of_hand.png  the arm where you see the BACK of the hand ("the knuckles are
    #                          appropriately pointing down")
    #   grip_palm.png          "the other arm so you would see the palm ... row 2 fist PALM is great"
    # A two-handed grip uses BOTH. Do not mirror one to make the other — mirroring the back of a hand
    # gives a mirrored back of a hand, never a palm.
    gb = os.path.join(outfit_dir(outfit), "hands", "grip_back_of_hand.png")
    gp = os.path.join(outfit_dir(outfit), "hands", "grip_palm.png")
    if os.path.exists(gb) and os.path.exists(gp):
        grip_back, grip_palm, prov = rgba(gb), rgba(gp), prov + " + approved grips"
    elif g is not None:
        grip = os.path.join(g, "grip.png")
        grip_back = grip_palm = rgba(grip if os.path.exists(grip) else os.path.join(g, "front.png"))
    else:
        grip_back = grip_palm = walk_back
    return dict(walk_back=walk_back, walk_palm=walk_palm, profile=profile,
                grip_back=grip_back, grip_palm=grip_palm), prov


def scene(w, h):
    return np.zeros((h, w, 4), np.uint8)


def finish(sc):
    im = Image.new("RGBA", (sc.shape[1], sc.shape[0]), (150, 160, 150, 255))
    im.alpha_composite(Image.fromarray(sc, "RGBA"))
    return im.convert("RGB")


def save(frames, ms, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    return path


# ---------------------------------------------------------------------------------------------------
# THE SWORD SWING — the hand travels, the tool follows. Owner's pick 2026-08-04, see APPROVED/DECISIONS.md
#
#   shoulder  a fixed point on the body
#   hand      shoulder + reach x direction        <- THE HAND TRAVELS
#   blade     a fixed angle BEHIND the arm        <- no wrist articulation
#   tool      placed so its grip lands on the hand
#
# This replaces the shoulder-pivot model for the sword. That one rotated the TOOL about a point near the
# body and stuck the hand on afterwards, so the fist sat by the shoulder and spun in place — "do people
# take a sword in their fist, hold their fist up to their shoulder and rotate their fist to swing it?"
SHOULDER = (0.06, 0.40)     # cell units from body centre, +x forward / +y up (swing_lab.FACINGS "side")
HAND_PERP = 180.0           # picked BY EYE off HAND_ROTATION_which_way.png. Do not re-derive.
SWORD_START_TH, SWORD_END_TH = 128.0, -104.0   # behind the head -> past straight down, hand at the hip
SWORD_BACK_START, SWORD_BACK_END = 85.0, 52.0  # blade catches up -> the tip keeps dropping
SWORD_REACH = 0.60
SWORD_DUR = 0.30


def _ease_in_out(u):
    return 3 * u * u - 2 * u * u * u


def _ease_in(u):
    return u * u * u


def sword_motion(t):
    """(arm direction, reach, blade angle behind the arm) for the official sword swing."""
    th = SWORD_START_TH + (SWORD_END_TH - SWORD_START_TH) * _ease_in_out(t)
    back = SWORD_BACK_START + (SWORD_BACK_END - SWORD_BACK_START) * _ease_in(t)
    return th, SWORD_REACH, back


# ---------------------------------------------------------------------------------------------------
# THE FACING-DOWN / FACING-UP SWORD ATTACK — owner's pick 2026-08-04: "lets do double back for both".
#
# A top-down attack is a sweep ACROSS the body that passes THROUGH the tile being hit — it is NOT a
# thrust along the attack direction. Driving the blade along that direction gives a reverse stab, which
# is what the rejected facing-up version did. So the motion is written relative to `centre`, the
# direction attacked, and the arc CROSSES centre rather than ending on it.
#
# Frame budget, 12 frames @ 20ms = 0.24s. The strike frames ARE the path — no easing inside the arc, so
# the shape survives instead of being smoothed into a generic curve.
ATK_ANTIC, ATK_STRIKE, ATK_HOLD, ATK_REC = 1, 4, 2, 5
ATK_MS = 20

# E_double_back: out across, then whipped back through the other way. Poses are
# (arm offset from centre, blade behind arm, reach in cells).
DOUBLE_BACK = ((+70, 66, 0.50),
               [(0, 44, 0.60), (-64, 30, 0.56), (-10, 46, 0.58), (+34, 58, 0.54)],
               (+34, 60, 0.46))

SWORD_FACINGS = {
    "down": dict(centre=-90.0, sh=(0.26, 0.12), bank="front", behind=False),
    "up":   dict(centre=+90.0, sh=(0.26, 0.22), bank="back",  behind=True),
}


def attack_poses(centre, spec):
    antic, path, rest = spec
    def at(p):
        return (centre + p[0], p[1], p[2])
    out = [at(antic)] * ATK_ANTIC + [at(p) for p in path]
    hit = out[-1]
    out += [hit] * ATK_HOLD
    r = at(rest)
    for i in range(ATK_REC):
        u = 1 - (1 - (i + 1) / ATK_REC) ** 3
        out.append(tuple(hit[k] + (r[k] - hit[k]) * u for k in range(3)))
    return out


def attack_frames(body, hands, tool_png, bh, cfg, spec=DOUBLE_BACK, two_handed=False, pad=230,
                  scale=1.0):
    """A directional attack: the arc sweeps THROUGH the tile being hit, with a blade trail."""
    cell = bh / 2.0
    ny0, ny1, cx, _ = gait.anchor(body)
    # `scale` is the tool's length relative to a cell. A SPEAR IS NOT A SWORD LENGTH — it was rendered at
    # 1.0 for weeks while the owner asked three separate times for it to be longer.
    art0 = S.scale_h(rgba(tool_png), cell * scale)
    grip = (S.grip_of(art0) + S.DIAG * S.GRIP_EXTRA) * art0.shape[0]
    poses = attack_poses(cfg["centre"], spec)
    W, H = body.shape[1] + 2 * pad, body.shape[0] + 2 * pad
    out, ms = [], []
    for i, (arm, back, reach) in enumerate(poses):
        sc = scene(W, H)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx, sy = ox + cx + cfg["sh"][0] * cell, bcy - cfg["sh"][1] * cell

        def place(a, b, rc):
            r = math.radians(a)
            hx, hy = sx + math.cos(r) * rc * cell, sy - math.sin(r) * rc * cell
            blade = a + b
            art = S.rot(art0, blade - S.ART_ANGLE)
            rr = math.radians(-(blade - S.ART_ANGLE))
            gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
            gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)
            return art, hx - gx, hy - gy, hx, hy, blade

        def weapon():
            if ATK_ANTIC < i < ATK_ANTIC + ATK_STRIKE:
                pa, pb, pr = poses[i - 1]
                for f in (0.34, 0.67):
                    art, tx, ty, _, _, _ = place(pa + (arm - pa) * f, pb + (back - pb) * f,
                                                 pr + (reach - pr) * f)
                    gait._paste(sc, gait._dim(art, 0.5), tx, ty)
            art, tx, ty, hx, hy, blade = place(arm, back, reach)
            gait._paste(sc, art, tx, ty)
            fists = [(hands["grip_back"], 0.0)]
            if two_handed:
                fists.append((hands["grip_palm"], 0.17))
            for fist, up in fists:
                fx = hx + math.cos(math.radians(blade)) * up * art0.shape[0]
                fy = hy - math.sin(math.radians(blade)) * up * art0.shape[0]
                gait._paste(sc, gait._sz(S.rot(fist, blade + HAND_PERP), bh, gait.RUN["ratio"]), fx, fy)

        if cfg["behind"]:
            weapon()
            gait._paste(sc, body, bx, by)
        else:
            gait._paste(sc, body, bx, by)
            weapon()
        out.append(finish(sc))
        ms.append(ATK_MS)
    return crop_union(out), ms


def arm_swing_frames(body, hands, tool_png, bh, two_handed=False, motion=None, dur=SWORD_DUR, pad=None,
                     shoulder=None, behind=False):
    """A swing where the HAND travels an arc and the tool is hung off it.

    `shoulder` overrides the side-view shoulder for the front/back facings — the shoulder is NOT in the
    same place in every view, and pretending it is put the hand at face height in the front view.
    `behind` draws the tool and fist BEHIND the body, which is what the away-facing view needs or the
    weapon covers his back.
    """
    motion = motion or sword_motion
    sh = shoulder or SHOULDER
    pd = PAD if pad is None else pad
    cell = bh / 2.0
    ny0, ny1, cx, _ = gait.anchor(body)
    art0 = S.scale_h(rgba(tool_png), cell)
    grip = (S.grip_of(art0) + S.DIAG * S.GRIP_EXTRA) * art0.shape[0]

    W, H = body.shape[1] + 2 * pd, body.shape[0] + 2 * pd
    n = max(14, int(dur * S.FPS * 3))
    out, ms = [], []
    for i in range(n):
        t = i / (n - 1)
        th, reach, back = motion(t)
        sc = scene(W, H)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx, sy = ox + cx + sh[0] * cell, bcy - sh[1] * cell

        r = math.radians(th)
        hx, hy = sx + math.cos(r) * reach * cell, sy - math.sin(r) * reach * cell
        blade = th + back
        art = S.rot(art0, blade - S.ART_ANGLE)
        rr = math.radians(-(blade - S.ART_ANGLE))
        gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
        gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)

        def draw_weapon():
            gait._paste(sc, art, hx - gx, hy - gy)
            fists = [(hands["grip_back"], 0.0)]
            if two_handed:
                fists.append((hands["grip_palm"], 0.17))
            for fist, up in fists:
                fx = hx + math.cos(math.radians(blade)) * up * art0.shape[0]
                fy = hy - math.sin(math.radians(blade)) * up * art0.shape[0]
                gait._paste(sc, gait._sz(S.rot(fist, blade + HAND_PERP), bh, gait.RUN["ratio"]), fx, fy)

        if behind:                      # away-facing: the weapon is on the far side of him
            draw_weapon()
            gait._paste(sc, body, bx, by)
        else:
            gait._paste(sc, body, bx, by)
            draw_weapon()

        out.append(finish(sc))
        ms.append(int(dur * 1000 / n))
    return crop_union(out), ms


def crop_union(frames, margin=14):
    """Crop every frame to the union of what they draw, so the gif is not mostly dead space.

    A vertical swing has to be rendered with a big pad or the blade is clipped off the bottom, which
    otherwise leaves the sword gif twice the size of the walk gifs in the same outfit.
    """
    bg = np.array((150, 160, 150), np.int16)
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


def swing_frames(body, hands, tool_png, bh, two_handed=False, approach=None, pad=None):
    """One full swing. Two-handed puts the second grip further up the handle."""
    cell = bh / 2.0
    art = S.scale_h(rgba(tool_png), cell)
    g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]
    kind = {"sword_bronze_icon.png": "sword", "axe_copper_icon.png": "axe",
            "small_net_icon.png": "net", "hoe_copper_icon.png": "hoe",
            "shovel_copper_icon.png": "shovel", "spear_bronze_icon.png": "spear"}[os.path.basename(tool_png)]
    p = S.TOOLS[kind]
    ap = approach if approach is not None else SWING_APPROACH_BY_TOOL.get(kind, SWING_APPROACH)
    n = max(12, int(S.duration(ap, p) * S.FPS * 4))
    # A VERTICAL swing puts the blade well below the feet and well above the head, so the lateral
    # PAD clips it. Owner has been shown clipped swings before; the frame has to fit the whole arc.
    pd = PAD if pad is None else pad
    W, H = body.shape[1] + 2 * pd, body.shape[0] + 2 * pd
    out, ms = [], []
    for i in range(n):
        t = i / (n - 1)
        ang, off, freeze, smear = S.motion(ap, p, t)
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
        ms.append(int(S.duration(ap, p) * 1000 / n) * (3 if freeze else 1))
    return out, ms


def _gait_gif(bank, neutral, fn, ms, path, *hands):
    fr = []
    W, H = bank[0].shape[1] + 2 * PAD, bank[0].shape[0] + PAD
    for beat in range(len(gait.CYCLE)):
        sc = scene(W, H)
        fn(sc, W / 2, H / 2, bank[gait.CYCLE[beat] - 1], neutral, *hands, beat)
        fr.append(finish(sc))
    return save(fr, ms, path)


def build(outfit="bronze", verbose=True):
    """Render every animation this outfit can support. Returns (made, gaps, provenance)."""
    anim = anim_dir(outfit)
    made, gaps = [], []

    hands, prov = load_hands(outfit)
    if hands is None:
        return [], [f"all animations: no gauntlet ({prov})"], prov

    side = load_bank(outfit, "side", 1)
    front = load_bank(outfit, "front", 0)
    back = load_bank(outfit, "back", 0)

    # --- gaits ---------------------------------------------------------------------------------
    if side:
        bh = gait.anchor(side[1])[1] - gait.anchor(side[1])[0] + 1
        made.append(_gait_gif(side, side[1], gait.walk_into, gait.WALK["ms"],
                              os.path.join(anim, "walk_side.gif"),
                              hands["walk_back"], hands["walk_palm"]))
        made.append(_gait_gif(side, side[1], gait.run_into, gait.RUN["ms"],
                              os.path.join(anim, "run_side.gif"),
                              hands["walk_back"], hands["walk_palm"]))
    else:
        gaps.append("walk_side, run_side, every swing: no side_1..3 frames")
        bh = None

    # The front walk is its own implementation: hands OUTSIDE the body edges, one up one down, no
    # rotation, no dimming. The BACK view reuses it deliberately — from behind you also see both hands
    # clear of the silhouette. At ~10px a hand the near/far distinction the side walk needs does not read.
    for kind, bank in (("front", front), ("back", back)):
        if not bank:
            gaps.append(f"walk_{kind}, run_{kind}: no {kind}_1..3 frames")
            continue
        label = kind if kind == "front" else "back"
        made.append(_gait_gif(bank, bank[0], gait.walk_front_into, gait.WALK["ms"],
                              os.path.join(anim, f"walk_{label}.gif"), hands["profile"]))
        made.append(_gait_gif(bank, bank[0], gait.walk_front_into, gait.RUN["ms"],
                              os.path.join(anim, f"run_{label}.gif"), hands["profile"]))

    # --- swings --------------------------------------------------------------------------------
    if side:
        for name, icon in ONE_HANDED:
            p = os.path.join(RES, "Items", icon)
            if not os.path.exists(p):
                gaps.append(f"swing_{name}: {icon} missing")
                continue
            # The SWORD uses the settled hand-travels swing. The other tools still run the old
            # shoulder-pivot approaches and are next in line to be redone the same way.
            if name == "sword":
                fr, ms = arm_swing_frames(side[1], hands, p, bh, pad=210)
            else:
                fr, ms = swing_frames(side[1], hands, p, bh)
            made.append(save(fr, ms, os.path.join(anim, f"swing_{name}.gif")))
        for name, icon in TWO_HANDED:
            p = os.path.join(RES, "Items", icon)
            if not os.path.exists(p):
                gaps.append(f"thrust_{name}: {icon} missing")
                continue
            fr, ms = swing_frames(side[1], hands, p, bh, two_handed=True)
            made.append(save(fr, ms, os.path.join(anim, f"thrust_{name}_two_handed.gif")))

    # The sword's DOWN and UP attacks — a different motion from the side one, not the side one re-aimed.
    sword = os.path.join(RES, "Items", "sword_bronze_icon.png")
    for facing, cfg in SWORD_FACINGS.items():
        bank = front if cfg["bank"] == "front" else back
        if not bank or not os.path.exists(sword):
            gaps.append(f"swing_sword_{facing}: no {cfg['bank']} frames")
            continue
        b = bank[0]
        fbh = gait.anchor(b)[1] - gait.anchor(b)[0] + 1
        fr, ms = attack_frames(b, hands, sword, fbh, cfg)
        made.append(save(fr, ms, os.path.join(anim, f"swing_sword_{facing}.gif")))

    if verbose:
        print(f"  {outfit}: {len(made)} animations, hands = {prov}")
        for g in gaps:
            print(f"    GAP  {g}")
    return made, gaps, prov


def all_outfits():
    return sorted(d for d in os.listdir(OUTFITS) if os.path.isdir(os.path.join(OUTFITS, d)))


if __name__ == "__main__":
    args = sys.argv[1:]
    targets = all_outfits() if ("--all" in args) else [a for a in args if not a.startswith("-")] or ["bronze"]
    total, allgaps = 0, []
    for o in targets:
        made, gaps, _ = build(o)
        total += len(made)
        allgaps += [f"{o}: {g}" for g in gaps]
    print(f"\n{total} animations across {len(targets)} outfit(s)")
    if allgaps:
        print(f"{len(allgaps)} gap(s):")
        for g in allgaps:
            print("  " + g)
