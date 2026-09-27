"""swing_lab.py — render one swing APPROACH as a demo scene. Preview only, nothing ships.

Five approaches are compared, each with a different parent so they cannot quietly converge (see
docs/product/investigations/swing-design/DESIGN.md). This script is the harness: the approach is a parameter,
everything else is held constant so a difference in the output is a difference in the approach.

Each scene shows BOTH the side-facing and the front-facing character, because both have to work, and is
framed so the character and the whole arc fill the frame.

  python3 tools/player_sprites/swing_lab.py 1        # faithful baseline
  python3 tools/player_sprites/swing_lab.py 2        # impact-first
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFIT = os.path.join(PLAYER, "outfits", "bronze")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
DEST = os.path.join(REPO, "docs", "product", "investigations", "swing-design")

ease_out = lambda t: 1 - (1 - t) ** 2
ease_in = lambda t: t ** 3
ease_in_out = lambda t: 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
# 0 -> 1 -> 0. The tool reaches its furthest at mid-strike and comes back, so "extend" is a REACH through
# the arc rather than a permanent change of radius that would leave the tool stranded at arm's length.
bump = lambda t: math.sin(math.pi * max(0.0, min(1.0, t))) ** 0.8


def ease_out_back(t):
    c1, u = 1.70158, t - 1
    return 1 + (c1 + 1) * u ** 3 + c1 * u ** 2


# Profiles as shipped (PlayerToolAnimator.cs:33-46). `weight` 0..1 drives the derived approaches.
# `art_rot` rotates the SPRITE only. ⚠ IT MUST STAY 0 UNLESS THE GRIP IS RECOMPUTED WITH IT: `grip_of`
# measures the handle end off the unrotated sprite, so spinning the art 180 deg leaves the hand clamped on
# the HEAD with the handle sticking out the far side. Tried that on the net and it looked worse, not better.
# The net coming out upside down is fixed by reversing the SWEEP instead — see `sweep` in arm_motion.
TOOLS = {
    "sword": dict(icon="sword_bronze_icon.png", kind="swing", arc=100.0, dur=0.20, off=0.60, weight=0.25,
                  art_rot=0.0),
    "axe":   dict(icon="axe_copper_icon.png",   kind="chop",  arc=110.0, dur=0.30, off=0.55, weight=1.00,
                  art_rot=0.0),
    "net":   dict(icon="small_net_icon.png",    kind="sweep", arc=150.0, dur=0.16, off=0.60, weight=0.10,
                  art_rot=0.0),
    "hoe":   dict(icon="hoe_copper_icon.png",   kind="till",  arc=90.0,  dur=0.24, off=0.55, weight=0.65,
                  art_rot=0.0),
    "spear": dict(icon="spear_bronze_icon.png", kind="thrust", arc=30.0, dur=0.22, off=0.55, weight=0.45,
                  art_rot=0.0),
    "shovel": dict(icon="shovel_copper_icon.png", kind="scoop", arc=90.0, dur=0.26, off=0.55, weight=0.70,
                   art_rot=0.0),
}
# The lab's own `kind` names for approaches 1-9 differ from the per-tool motions used by 10-12; this maps
# the old profile kinds onto the new ones so both generations of approach can run off one TOOLS table.
KIND10 = {"swing": "slash", "chop": "wheel", "sweep": "sweep",
          "till": "till", "thrust": "thrust", "scoop": "scoop"}
DEMO_TOOLS = ("sword", "axe", "net", "hoe", "spear", "shovel")

# One entry per facing. The shoulder is NOT in the same place in every view, and pretending it is put the
# hand at face height in the front view — the owner found that, facing down, the hand was too high: held at
# about face height with the tool pointing straight down, where it should be lower.
#   sprite  which body frame to draw
#   aim     rotates the whole arc for that facing
#   sh      shoulder offset from body centre, CELL units, +x forward / +y up
#   behind  draw tool+hand BEHIND the body (true for the away-facing view, or the tool covers his back)
#   floor   lowest angle the arc may reach in this facing; None = unclamped
FACINGS = [
    dict(name="side",  sprite="side_2.png",  aim=0.0,   sh=(0.06, 0.40), behind=False, floor=None),
    dict(name="front", sprite="front_2.png", aim=-60.0, sh=(0.10, 0.10), behind=False, floor=-30.0),
    dict(name="up",    sprite="back_2.png",  aim=45.0,  sh=(0.10, 0.22), behind=True,  floor=None),
]
ART_ANGLE = 45.0
DIAG = np.array([-1, 1]) / math.sqrt(2)
GRIP_EXTRA = 0.16
HAND_FRAC = 0.17          # of BODY height — never off the tool sprite
HAND_ROT = 225
FPS = 30

# The pose the game cuts to the instant a swing ends (PlayerToolAnimator.cs:183-185, RestoreIdle :204).
# It is set directly — no lerp — so the gap between where an approach LEAVES the tool and this pose is a
# visible pop. The lab used to loop straight back to t=0, which hid that cost from every approach.
#
# IDLE_SCALE was 0.75 while every swing frame drew the tool at 1.0, so the weapon visibly CHANGED SIZE the
# instant the swing ended. The owner spotted it: the idle sword/tool was a different size from the one
# in the animation. That is a real bug in the shipped animator too — `PlayerToolAnimator.IdleScale` has to
# come to 1.0 with it, or the game will still pop even once the motion is right.
IDLE_ANGLE, IDLE_OFF, IDLE_SCALE = -35.0, 0.4, 1.0

# Approach 7 retimes for ACTUAL PLAY. Owner direction: these are for use in the game, so they cannot be slow.
# The lab's durations came from the shipped profiles, which were authored for a demo loop, not for a player
# holding the button — the axe at 0.34s is a third of a second of committed animation per tree.
DUR_SCALE = {7: 0.70, 8: 0.70, 9: 0.70}


def duration(approach, p):
    if approach in VERTICALS:
        # A vertical swing is lift + drop + recover, so it cannot be as short as a flat slash. Still has
        # to be playable — these are for use in the game, so they cannot be slow. Heavier tools take
        # longer, which is the only weight cue a player actually reads.
        return 0.24 + 0.14 * p["weight"]
    if approach in (10, 11, 12):
        return COMBAT_DUR[KIND10[p["kind"]]]
    return p["dur"] * DUR_SCALE.get(approach, 1.0)


# ------------------------------------------------- per-tool motions, used by approaches 10, 11 and 12
# ONE MOTION PER TOOL — they are not the same move at different speeds.
#
# Owner caught this as a code smell and he is right: the previous pass gave all four tools one arc shape
# with different constants, so a sword slash and an axe chop were the same function. They are not the same
# motion. His notes, in short: a sword swing is not an axe swing — the sword suits combat, quick slashes
# without big theatrical arcs; the axe travels behind the head, over the top and down in front, as a real
# axe does; a spear thrusts; a shovel jabs down and scoops back up.
#
# So each KIND gets its own function below. They differ in what they do with the two channels available —
# angle and reach — and a thrust barely uses angle at all, which is the point.
#
# Angle convention: 0 = FORWARD (side-view character faces right), 90 = up, 180 = behind, -90 = down.
# Each returns (angle_deg, reach_multiplier, contact_u, smear).
COMBAT_DUR = {"slash": 0.11, "wheel": 0.20, "sweep": 0.15,
              "till": 0.18, "thrust": 0.12, "scoop": 0.22}


# EVERY MOTION STARTS AND ENDS AT THE IDLE POSE. This is the fix for the tool hovering in the cocked-back
# position — measured, the tool used to TELEPORT 235 deg (axe) / 205 deg (net) from idle to its start
# pose and then sit there while the curve eased in, parked near that pose for 22-45% of the animation
# depending on the approach. Approach 11 only parked for 6-8%, which is exactly why it felt best.
#
# Now the wind-up is TRAVELLED. The tool is where the hand left it, moves, and comes back. That also
# closes the original research's defect #1 ("the swing has no exit" — RestoreIdle cut with no lerp).
#
# `seg(t, a, b)` maps a sub-range of t onto 0..1 so each phase is readable as "from here, to there".
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def m_slash(t):
    """SWORD — short, fast, slashing. NOT a dramatic wheel: a combat slash is a flick that lives in the
    middle third of its own duration. Owner approved iteration 7's shape; this is that, anchored."""
    if t < 0.16:                                        # travelled wind-up, from where the tool rests
        return IDLE_ANGLE + (60.0 - IDLE_ANGLE) * ease_in_out(seg(t, 0.0, 0.16)), 1.0, 0.0, False
    if t < 0.58:
        u = seg(t, 0.16, 0.58)
        return 60.0 - 115.0 * ease_in(u), 1.0 + 0.34 * bump(u), 0.52, u > 0.35
    u = seg(t, 0.58, 1.0)
    return -55.0 + (IDLE_ANGLE + 55.0) * ease_out(u), 1.0 + 0.10 * (1 - u), 0.0, False


def m_wheel(t):
    """AXE — round and down in one continuous travel. Owner revised this off a full circle: the net and
    axe do not need to swing all the way around; just make it faster. So it is a big
    arc that never stops rather than a wheel, and it starts from idle instead of appearing at the top."""
    if t < 0.22:
        return IDLE_ANGLE + (150.0 - IDLE_ANGLE) * ease_in(seg(t, 0.0, 0.22)), 1.0, 0.0, t > 0.12
    if t < 0.70:
        u = seg(t, 0.22, 0.70)
        return 150.0 - 220.0 * ease_in_out(u), 1.0 + 0.26 * bump(u), 0.62, True
    u = seg(t, 0.70, 1.0)
    return -70.0 + (IDLE_ANGLE + 70.0) * ease_out(u), 1.0, 0.0, False


def m_sweep(t):
    """NET — same anchoring. WHICH WAY IT SHOULD GO IS AN OPEN QUESTION: five rounds of theories about
    why it looked backwards were all wrong, so the orientation is being chosen from a rendered grid
    (`net_options.py`) rather than reasoned about again. This is the placeholder shape until he picks."""
    if t < 0.20:
        return IDLE_ANGLE + (145.0 - IDLE_ANGLE) * ease_in(seg(t, 0.0, 0.20)), 1.0, 0.0, False
    if t < 0.72:
        u = seg(t, 0.20, 0.72)
        return 145.0 - 180.0 * ease_in_out(u), 1.0 + 0.30 * bump(u), 0.56, True
    u = seg(t, 0.72, 1.0)
    return -35.0 + (IDLE_ANGLE + 35.0) * ease_out(u), 1.0, 0.0, False


def m_till(t):
    """HOE — a SMALL lift, strike the ground, pull back. Owner direction: no big arc that reads as
    lashing the ground with a stick — a small lift, a strike into the ground, then a pull
    back. So the angle barely travels (100 deg, not 200) and the
    work is done by REACH — that is the difference between digging and swinging."""
    if t < 0.18:                                        # lift a little. A LITTLE.
        return IDLE_ANGLE + 60.0 * ease_in(seg(t, 0.0, 0.18)), 1.0, 0.0, False
    if t < 0.50:                                        # strike down into the ground
        u = seg(t, 0.18, 0.50)
        return 25.0 - 100.0 * ease_in(u), 1.0 + 0.34 * u, 0.46, u > 0.55
    if t < 0.78:                                        # planted, dragged back toward the player
        u = seg(t, 0.50, 0.78)
        return -75.0 + 6.0 * u, 1.34 - 0.50 * ease_out(u), 0.0, False
    u = seg(t, 0.78, 1.0)
    return -69.0 + (IDLE_ANGLE + 69.0) * ease_out(u), 0.84 + 0.16 * u, 0.0, False


def m_thrust(t):
    """SPEAR — a stab. The angle barely moves; the REACH is the whole animation. The one motion that is
    a translation rather than a rotation, which is why it could never be a tuning of a swing."""
    if t < 0.18:                                        # settle to level, and load back a little
        return IDLE_ANGLE + (8.0 - IDLE_ANGLE) * ease_out(seg(t, 0.0, 0.18)), 0.62, 0.0, False
    if t < 0.44:
        u = seg(t, 0.18, 0.44)
        return 8.0 - 6.0 * u, 0.62 + 1.18 * ease_in(u), 0.0, u > 0.4
    if t < 0.56:
        return 2.0, 1.80, 0.44, False                   # held at full extension: the hit
    u = seg(t, 0.56, 1.0)
    return 2.0 + (IDLE_ANGLE - 2.0) * ease_out(u), 1.80 - 0.80 * ease_out(u), 0.0, False


def m_scoop(t):
    """SHOVEL — a downward JAB, then a small lift coming back. Owner direction: the shovel read as waved
    about aimlessly; it should jab down as if digging, with at most a small lift on the way back —
    nothing large. Like the spear thrust, aimed at the ground: the reach does the work
    and the angle stays put, so it reads as digging rather than as another swing."""
    if t < 0.20:                                        # bring it over the spot, barely any travel
        return IDLE_ANGLE + (-58.0 - IDLE_ANGLE) * ease_out(seg(t, 0.0, 0.20)), 0.80, 0.0, False
    if t < 0.44:                                        # JAB straight down
        u = seg(t, 0.20, 0.44)
        return -58.0 - 14.0 * u, 0.80 + 0.62 * ease_in(u), 0.40, u > 0.45
    if t < 0.60:
        return -72.0, 1.42, 0.0, False                  # buried
    u = seg(t, 0.60, 1.0)                               # lift a little on the way back, nothing large
    return -72.0 + (IDLE_ANGLE + 72.0 + 18.0) * ease_out(u) - 18.0 * u, 1.42 - 0.52 * ease_out(u), 0.0, False


KIND_MOTION = {"slash": m_slash, "wheel": m_wheel, "sweep": m_sweep,
               "till": m_till, "thrust": m_thrust, "scoop": m_scoop}


def variation(approach, kind, t):
    """Approaches 10/11/12 all use the SAME per-tool motion above. They differ only in how time is spent
    inside it — so a difference you see between them is the feel, never the choreography."""
    if approach == 11:                 # SNAP — get most of the way there early, then settle
        t = 0.70 * ease_out(min(1.0, t / 0.34)) + 0.30 * ease_out(max(0.0, t - 0.34) / 0.66)
    elif approach == 12:               # LOAD — a brief moving load, then everything at once
        t = (0.12 * (t / 0.24) if t < 0.24
             else 0.12 + 0.88 * ease_in_out(min(1.0, (t - 0.24) / 0.60)))
    return KIND_MOTION[kind](min(1.0, max(0.0, t)))


# ---------------------------------------------------------------- vertical swings (20-23)
# WHY VERTICAL. A hand sprite is drawn from ONE viewpoint, and that viewpoint tells the viewer where the
# arm is: looking down at the knuckles of a closed fist reads as an arm STRETCHED OUT, while the back of
# the hand reads as an arm that is NOT extended (you cannot see the back of the hand on an arm reaching
# out to the side — at that extension the wrist turns it edge-on).
#
# Approaches 1-12 spin ONE sprite through a ~250 deg LATERAL arc, so across that arc the drawn view keeps
# contradicting where the hand is and the pose reads as impossible even though no single part looks wrong.
# Retiming, re-cutting and swapping between the hands we already had were all tuning the wrong variable.
#
# A TOP-TO-BOTTOM swing removes the conflict instead of drawing around it: the arm stays inside the
# geometry one hand view can honestly represent, so one sprite carries the whole motion and no new art is
# needed. Owner, 2026-08-04: no lateral swings — everything is a top-to-bottom swing, so different hand
# shapes are not a concern.
#
# Every variant STARTS AND ENDS AT `IDLE_ANGLE` so the swing has an exit and does not pop when it ends.
VERTICALS = {20: "overhead", 21: "diagonal", 22: "loaded", 23: "chop_and_stop"}


def _v_overhead(t, off):
    """Up above the head, straight down through the target, short recovery."""
    top, low = 135.0, -78.0
    if t < 0.30:                                        # lift
        return IDLE_ANGLE + (top - IDLE_ANGLE) * ease_out(t / 0.30), off, False, False
    if t < 0.72:                                        # drop — the fast part
        u = (t - 0.30) / 0.42
        return top + (low - top) * ease_in(u), off + 0.18 * ease_in(u), False, u > 0.45
    u = (t - 0.72) / 0.28                               # recover to idle
    return low + (IDLE_ANGLE - low) * ease_out(u), off + 0.18 - 0.18 * ease_out(u), False, False


def _v_diagonal(t, off):
    """Outside shoulder down across to the opposite hip — reaches out through the strike, pulls in after."""
    top, low = 112.0, -62.0
    if t < 0.28:
        return IDLE_ANGLE + (top - IDLE_ANGLE) * ease_out(t / 0.28), off - 0.10, False, False
    if t < 0.70:
        u = (t - 0.28) / 0.42
        return top + (low - top) * ease_in_out(u), off - 0.10 + 0.34 * ease_in(u), False, 0.35 < u < 0.9
    u = (t - 0.70) / 0.30
    return low + (IDLE_ANGLE - low) * ease_out(u), off + 0.24 - 0.24 * ease_out(u), False, False


def _v_loaded(t, off):
    """A small lift, then the whole drop at once — the weight is in the fall, not the wind-up."""
    top, low = 72.0, -84.0
    if t < 0.16:                                        # brief load
        return IDLE_ANGLE + (top - IDLE_ANGLE) * ease_out(t / 0.16), off, False, False
    if t < 0.26:                                        # hang at the top
        return top, off, False, False
    if t < 0.62:                                        # everything at once
        u = (t - 0.26) / 0.36
        return top + (low - top) * ease_in(u), off + 0.22 * ease_in(u), False, u > 0.3
    u = (t - 0.62) / 0.38
    return low + (IDLE_ANGLE - low) * ease_out(u), off + 0.22 - 0.22 * ease_out(u), False, False


def _v_chop_stop(t, off):
    """Down with a HARD STOP at contact — the fighting-game freeze, on the contact pose itself."""
    top, stop = 125.0, -14.0
    hold_from, hold_to = 0.58, 0.70
    if t < 0.30:
        return IDLE_ANGLE + (top - IDLE_ANGLE) * ease_out(t / 0.30), off, False, False
    if t < hold_from:
        u = (t - 0.30) / (hold_from - 0.30)
        return top + (stop - top) * ease_in(u), off + 0.20 * ease_in(u), False, u > 0.5
    if t < hold_to:                                     # the stop. freeze=True holds this exact pose
        return stop, off + 0.20, True, False
    u = (t - hold_to) / (1 - hold_to)
    return stop + (IDLE_ANGLE - stop) * ease_out(u), off + 0.20 - 0.20 * ease_out(u), False, False


V_MOTION = {20: _v_overhead, 21: _v_diagonal, 22: _v_loaded, 23: _v_chop_stop}


# ---------------------------------------------------------------- approaches
def motion(approach, p, t):
    """-> (angle, offset, freeze, smear). angle/offset drive the pivot; freeze/smear are presentation."""
    aim, arc, off, half = 0.0, p["arc"], p["off"], p["arc"] / 2
    kind, w = p["kind"], p["weight"]

    if approach in (1, 2):                      # AS SHIPPED — 2 adds impact treatment only
        a, o = _shipped(kind, t, aim, arc, off)
        contact = {"swing": 0.65, "chop": 0.55, "sweep": 0.50, "till": 0.50}[kind]
        freeze = approach == 2 and contact <= t < contact + 0.06 + 0.10 * w
        return a, o, freeze, False

    if approach == 3:                           # STARDEW — half the swing is wind-up
        ant, strike = 0.50, 0.20                # recovery = 0.30, and recovery length is the weight knob
        top = aim + half + half * 0.35
        if t < ant:
            return aim + half + (top - (aim + half)) * ease_out(t / ant), off, False, False
        if t < ant + strike:
            u = (t - ant) / strike
            return top + (aim - top) * ease_in(u), off, False, u > 0.6
        u = (t - ant - strike) / (1 - ant - strike)
        u = min(1.0, u / (0.4 + 0.6 * w))       # heavier -> slower recovery, may not finish
        return aim + ((aim - half) - aim) * ease_out(u), off, False, False

    if approach == 4:                           # COOPER — strike instantly, weight in the follow-through
        strike = 0.12                           # almost no anticipation
        if t < strike:
            u = t / strike
            return (aim + half) + (aim - (aim + half)) * ease_in(u), off, False, u > 0.4
        u = (t - strike) / (1 - strike)
        end = aim - half - half * (0.30 + 0.50 * w)     # exaggerated overshoot, scaled by weight
        return aim + (end - aim) * ease_out_back(u), off, False, False

    if approach in V_MOTION:                    # 20-23 — TOP-TO-BOTTOM, one hand view all the way
        return V_MOTION[approach](min(1.0, max(0.0, t)), off)

    if approach in (10, 11, 12):
        a, reach, contact, smear = variation(approach, KIND10[kind], t)
        freeze = contact > 0 and contact <= t < contact + 0.05 + 0.09 * w
        return a, off * reach, freeze, smear

    if approach == 7:
        # ITERATION 2, TUNED — owner picked 2 as the closest and listed what was wrong with it.
        # Everything here is one of his notes, not a fresh idea:
        #
        #  * every tool's hand should carry further forward through the arc, as the sword's already
        #    does. Only `swing` ever pushed the tool outward mid-strike (+0.20); chop, sweep and
        #    till held a fixed radius, which is why they read as spinning on the spot. Now every kind
        #    extends, and the sword's own push goes 0.20 -> 0.38 because it just needed to extend a
        #    little further.
        #  * the tip of the hoe did not reach ground level. It stopped at -12 deg, barely under
        #    horizontal. The tip reaches the feet at about -80.
        #  * for the axe he preferred one continuous circle, back, over and all the way round — so chop's
        #    lift-hold-drop is replaced by a single continuous 250 deg circle.
        #  * the sword can stay the sharp slash it already was, so its angle curve is untouched.
        ext = 0.38 if kind == "swing" else 0.30      # how far the tool reaches out through the strike
        contact = {"swing": 0.62, "chop": 0.58, "sweep": 0.50, "till": 0.55}[kind]
        freeze = contact <= t < contact + 0.06 + 0.10 * w

        if kind == "chop":                      # AXE — back, and all the way around
            top, end = aim + 175.0, aim - 75.0   # 250 deg of continuous travel, no hold
            ant = 0.28
            if t < ant:
                a = (aim + half) + (top - (aim + half)) * ease_out(t / ant)
                return a, off, False, False
            u = (t - ant) / (1 - ant)
            a = top + (end - top) * ease_in_out(u)
            return a, off + ext * bump(u), freeze, 0.25 < u < 0.62

        if kind == "sweep":                     # NET — stays ABOVE horizontal so the hoop never inverts
            a = 55.0 - 75.0 * ease_out(t)       # +55 -> -20, a scoop rather than a barrel roll
            return a, off + ext * bump(t), False, 0.2 < t < 0.6

        if kind == "till":                      # HOE — down to the feet, THEN drag back
            top, ground = aim + half + half * 0.35, -80.0
            ant, strf = 0.20, 0.34
            if t < ant:
                return (aim + half) + (top - (aim + half)) * ease_out(t / ant), off, False, False
            if t < ant + strf:
                u = (t - ant) / strf
                return top + (ground - top) * ease_in(u), off + ext * u, freeze, u > 0.55
            u = (t - ant - strf) / (1 - ant - strf)          # planted, and pulled back toward the player
            return ground + 6.0 * u, off + ext - (ext + 0.28) * ease_out(u), False, False

        a, o = _shipped(kind, t, aim, arc, off)              # SWORD — the slash is kept as it was
        if 0.15 <= t:
            o = off + ext * bump((t - 0.15) / 0.85)
        return a, o, freeze, False

    if approach == 6:                           # THE SYNTHESIS — see DESIGN.md "RESULT"
        # Approach 5 won on two structural counts (continuous velocity kills the teleport; the
        # overshoot returns instead of settling at the exaggerated value). The iterations found four
        # things wrong with it, and all four are fixed here:
        #
        #  1. weight was INVERTED. `ratio = 0.45 + 0.35*w` made the heavy axe the MOST damped, so it
        #     never moved past its target while the light tools rang. Heavy means HARD TO STOP.
        #  2. it had no anticipation — it started AT its own wind-up target, so it sat motionless for
        #     the first 18%. A spring only animates a gap; it was given none. Now it starts at the
        #     pose the tool actually rests in and has to climb.
        #  3. every approach ended in a pop, because RestoreIdle cuts to IdleAngle with no lerp. The
        #     third target IS the idle pose, so the swing lands on it and the cut is invisible.
        #  4. the freeze in approach 2 held the frame AFTER contact. Here contact is detected as the
        #     angle crossing `aim` on the way down, and the freeze holds THAT pose.
        # On fix 1 the first answer was wrong. Inverting the DAMPING to get the heavy tool to
        # overshoot does work, but overshoot needs low damping, low damping means high velocity, and
        # high velocity means a big per-frame jump — it is the same knob, so a 0.2s window cannot
        # have both. A sweep over 2000 parameter sets confirmed the frontier: smooth (jump 9,
        # pop 3) with ZERO overshoot, or a 200 degree overshoot with a 73 degree frame jump.
        #
        # So weight comes from Cooper instead — a heavier tool is given a FURTHER TARGET, which is a
        # difference in position rather than in ringing, and costs no damping. That buys all four at
        # once: jump 22 (authored curves: 41-44), pop 8 (Cooper's axe: 64), wind-up 71 (the Stardew
        # port managed 17), and the swing carries the axe 35 degrees further round than the net.
        freq = 7.0 - 2.0 * w                    # heavy = slower
        ratio = 0.85 - 0.20 * w                 # heavy rings slightly more, but stays damped
        top = aim + half + half * 0.25
        end = aim - half - half * 0.30 * w      # <- the weight cue: heavy carries further
        rest = IDLE_ANGLE

        def target(tt):
            return top if tt < 0.30 else end if tt < 0.68 else rest

        dt = 1 / 480.0
        k = (2 * math.pi * freq) ** 2
        c = ratio * 2 * math.sqrt(k)
        x, v = rest, 0.0                        # starts where the tool is actually held at rest
        hold = 0.05 + 0.07 * w                  # heavier hit, longer hold — capped by construction
        t_contact, a_contact = None, None
        steps = max(1, int(t * p["dur"] / dt))
        for i in range(steps):
            tt = i * dt / p["dur"]
            prev = x
            v += (k * (target(tt) - x) - c * v) * dt
            x += v * dt
            if t_contact is None and tt > 0.30 and prev > aim >= x:   # crossing aim, descending
                t_contact, a_contact = tt, x
        if kind != "sweep" and t_contact is not None and t_contact <= t < t_contact + hold:
            return a_contact, off, True, False   # hold the CONTACT pose, not the next frame
        return x, off, False, abs(v) * dt / p["dur"] > 12.0

    if approach == 5:                           # SPRING — no authored segments
        freq = 5.5 - 3.0 * w                    # heavy = lower frequency
        ratio = 0.45 + 0.35 * w                 # heavy = more damped, less ring
        target = (aim + half) if t < 0.18 else (aim - half)
        x, v, dt = aim + half, 0.0, 1 / 240
        k = (2 * math.pi * freq) ** 2
        c = ratio * 2 * math.sqrt(k)
        steps = int(max(1, t * p["dur"] / dt))
        for i in range(steps):
            tt = i * dt / p["dur"]
            g = (aim + half) if tt < 0.18 else (aim - half)
            v += (k * (g - x) - c * v) * dt
            x += v * dt
        return x, off, False, abs(v) > 900
    return 0.0, off, False, False


# ---------------------------------------------------------------- the arm rig (approaches 8 and 9)
#
# Approaches 1-7 all share one mechanism: rotate a rigid tool sprite about the player's CENTRE at a fixed
# radius. That is WHY the swing reads wrong no matter how the timing is tuned — the fist travels a circle
# around the character's navel, so it rides up past the chest and the weapon spins on the spot. The owner
# rejected it: nobody swings a sword with the fist up near the chest.
#
# Nothing here needs a new sprite. The character is armless and the fist is already a free-floating sprite
# moved by code, so the hand can follow ANY path we choose — we simply never chose one. These two give it
# a path:
#
#   8  SHOULDER ARM  — the hand hangs off a shoulder, at arm's length, and the arm SHORTENS as it comes
#                      across the body and extends again on the follow-through. That length change is the
#                      elbow, without drawing one; it is what turns a circle into a swing.
#   9  WHOLE BODY    — the same arm, plus the body itself. Real swings are driven from the hips: the torso
#                      counter-rotates away during wind-up, then rotates and steps INTO the strike. This
#                      is the single biggest thing missing, and it costs one rotate + one offset.
# From the body's centre, in CELL units (CELL = half the body height): +x forward, +y UP.
# The shoulder sits about 22% of body height above centre, which is where the sprite's shoulder cap is.
SHOULDER = (0.06, 0.40)

# THE ARMLESS DESIGN CAPS HOW FAR THE HAND MAY TRAVEL, and this is the thing the first attempt got wrong.
# A drawn character can put its hand at arm's length because the arm connects it. Ours cannot: there is no
# arm, so a fist 20px clear of the torso does not read as "reaching", it reads as a fist that has come off.
# The first pass used reach 0.62-0.72 CELL and the sword visibly detached and floated beside the body.
# Keeping the hand inside roughly a third of a cell keeps it reading as attached while still tracing an arm
# arc rather than orbiting the navel.
ARM_MIN, ARM_MAX = 0.20, 0.40


def arm_motion(approach, p, t):
    """-> theta, arm, freeze, smear, lean, step   (theta/arm place the HAND, not the tool)."""
    kind, w, arc = p["kind"], p["weight"], p["arc"]
    contact = {"swing": 0.60, "chop": 0.58, "sweep": 0.50, "till": 0.55}[kind]
    freeze = contact <= t < contact + 0.05 + 0.09 * w

    if kind == "chop":
        # AXE — ONE continuous arc the whole way round. Owner direction: one unbroken arc, not a
        # wind-back followed by a separate downswing. The previous version had a distinct wind-back that
        # STOPPED and then a separate chop, which is exactly the two-part motion he is rejecting. This
        # never stops: it starts at rest and travels ~330 deg in a single accelerating-then-decelerating
        # sweep, so the head is always moving and the "wind up" is just the first third of the same circle.
        theta = 60.0 - 330.0 * ease_in_out(t)
    elif kind == "sweep":
        # NET — faster and further across (dur 0.25 -> 0.16, arc 90 -> 150), and now sweeping UPWARD:
        # low behind, up and over the front. The owner found the net upside down — swung bulge
        # first. Sweeping down led with the closed underside of the bag; scooping up leads with
        # the mouth, which is also how you actually catch something.
        theta = -55.0 + 150.0 * ease_out(t)
    elif kind == "till":
        top, ground, ant, strf = arc / 2 + 16.0, -80.0, 0.20, 0.34
        theta = ((arc / 2) + (top - arc / 2) * ease_out(t / ant) if t < ant
                 else top + (ground - top) * ease_in(min(1.0, (t - ant) / strf)) if t < ant + strf
                 else ground + 6.0 * ((t - ant - strf) / (1 - ant - strf)))
    else:
        top, end, ant, strf = arc / 2 + arc * 0.15, -arc / 2, 0.15, 0.50
        theta = ((arc / 2) + (top - arc / 2) * ease_out(t / ant) if t < ant
                 else top + (0.0 - top) * ease_in((t - ant) / strf) if t < ant + strf
                 else 0.0 + (end - 0.0) * ease_out_back((t - ant - strf) / (1 - ant - strf)))

    # THE ELBOW, without an elbow: tucked in during the wind-up, thrown out through contact, drawn back
    # on the recovery. That length change over the arc is what an elbow DOES, and it is the difference
    # between a swing and a sprite on a turntable.
    u = bump(t) ** 0.6 if kind != "till" else min(1.0, t / 0.55)
    arm = ARM_MIN + (ARM_MAX - ARM_MIN) * u * (0.85 + 0.15 * w)

    lean = step = 0.0
    if approach == 9:
        # hips first: away during wind-up, hard through the strike, settle. Small numbers on purpose —
        # at 71px tall, 6 degrees and a third of a cell is a lunge, not a nudge.
        s = min(1.0, max(0.0, (t - 0.12) / 0.55))
        lean = (-4.5 * (1 - s) + 7.0 * s) * (0.6 + 0.4 * w)
        step = (-0.06 * (1 - s) + 0.30 * s) * (0.7 + 0.3 * w)
    return theta, arm, freeze, (0.25 < t < 0.62), lean, step


def _shipped(kind, t, aim, arc, off):
    half = arc / 2
    if kind == "swing":
        top, end, cur = aim + half + half * 0.30, aim - half, aim + half
        ant, strf = 0.15, 0.50
        if t < ant:              a = cur + (top - cur) * ease_out(t / ant)
        elif t < ant + strf:     a = top + (aim - top) * ease_in((t - ant) / strf)
        else:                    a = aim + (end - aim) * ease_out_back((t - ant - strf) / (1 - ant - strf))
        o = off
        if ant <= t < ant + strf:   o = off + 0.2 * ease_in((t - ant) / strf)
        elif t >= ant + strf:       o = off + 0.2 - 0.2 * ease_out((t - ant - strf) / (1 - ant - strf))
        return a, o
    if kind == "chop":
        top, end, cur = aim + half + half * 0.35, aim - half, aim + half
        ant, strf, hold = 0.22, 0.33, 0.28
        if t < ant:                       return cur + (top - cur) * ease_out(t / ant), off
        if t < ant + strf:                return top + (aim - top) * ease_in((t - ant) / strf), off
        if t < ant + strf + hold:         return aim, off
        u = (t - ant - strf - hold) / (1 - ant - strf - hold)
        return aim + (end - aim) * ease_out(u), off
    if kind == "sweep":
        return aim + half - arc * ease_out(t), off
    if kind == "till":
        top, cur = aim + half + half * 0.35, aim + half
        ant, strf = 0.20, 0.30
        if t < ant:        return cur + (top - cur) * ease_out(t / ant), off
        if t < ant + strf: return top + (aim - top) * ease_in((t - ant) / strf), off
        u = (t - ant - strf) / (1 - ant - strf)
        return aim + ((aim - 12.0) - aim) * ease_out(u), off + ((off - 0.55) - off) * ease_in(u)
    return aim, off


# ---------------------------------------------------------------- drawing
def rgba(p): return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def scale_h(a, h):
    s = h / a.shape[0]
    return np.asarray(Image.fromarray(a, "RGBA").resize(
        (max(2, round(a.shape[1] * s)), max(2, round(h))), Image.NEAREST), np.uint8)


def rot(a, d):
    return np.asarray(Image.fromarray(a, "RGBA").rotate(d, resample=Image.NEAREST, expand=True), np.uint8)


def paste(dst, src, cx, cy, alpha=1.0):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0 = max(0, x0), max(0, y0)
    a1, b1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if a1 <= a0 or b1 <= b0:
        return
    s = src[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    m = s[..., 3] > 0
    if alpha >= 1.0:
        dst[b0:b1, a0:a1][m] = s[m]
    else:
        tgt = dst[b0:b1, a0:a1]
        tgt[m] = (tgt[m] * (1 - alpha) + s[m] * alpha).astype(np.uint8)


def grip_of(art):
    o = art[..., 3] > 0
    ys, xs = np.where(o)
    c = np.array([art.shape[1] / 2, art.shape[0] / 2])
    proj = (np.stack([xs, ys], 1) - c) @ DIAG
    return DIAG * (proj.max() - 0.22 * art.shape[0]) / art.shape[0]


def cut_side_dummy():
    from scipy.ndimage import label, binary_dilation
    a = rgba(os.path.join(PLAYER, "props", "practice-dummy", "result.png"))
    solid = binary_dilation(a[..., :3].astype(int).sum(2) > 70, np.ones((7, 7), bool))
    lbl, n = label(solid, structure=np.ones((3, 3), int))
    best = None
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() < 4000:
            continue
        ys, xs = np.where(m)
        if best is None or xs.mean() > best[0]:
            best = (xs.mean(), ys.min(), ys.max(), xs.min(), xs.max(), m)
    _, y0, y1, x0, x1, m = best
    f = np.zeros_like(a)
    f[m] = a[m]
    f[..., 3] = np.where(m, 255, 0)
    return f[y0:y1 + 1, x0:x1 + 1]


def build(approach):
    bodies = {f["name"]: rgba(os.path.join(OUTFIT, f["sprite"])) for f in FACINGS}
    side, front = bodies["side"], bodies["front"]
    BH = bbox(side)[1] - bbox(side)[0] + 1
    CELL = BH / 2.0
    hand = rgba(os.path.join(OUTFIT, "gauntlet", "front.png"))
    hand_s = scale_h(hand, BH * HAND_FRAC)
    dummy = scale_h(cut_side_dummy(), BH * 0.85)
    tree = scale_h(rgba(os.path.join(RES, "Objects", "tree_apple.png")), CELL * 2.6)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]

    # Three characters now — side, front and away-facing. At the owner's request the facing-up
    # swings are included too. All three have to work, so all three are on screen at once rather than being
    # checked one at a time and assumed fine.
    W, H = int(CELL * 8.6), int(CELL * 3.6)
    TS = int(CELL)
    rng = np.random.RandomState(7)
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H + TS, TS):
        for gx in range(0, W + TS, TS):
            paste(ground, scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    BASE = int(H * 0.88)
    FACE_X = [int(W * 0.16), int(W * 0.50), int(W * 0.84)]      # side, front, away — matches FACINGS
    SX, DX, FX = FACE_X[0], int(W * 0.33), FACE_X[1]

    def frame(tool, t, idle=False):
        p = TOOLS[tool]
        if approach in (8, 9) and not idle:      # only 8/9 use the shoulder-arm rig; 10-12 are polar
            return frame_arm(tool, t)
        ang, off, freeze, smear = motion(approach, p, t)
        if idle:                                        # the pose the game snaps to when the swing ends
            ang, off, smear = IDLE_ANGLE, IDLE_OFF, False
        sc = ground.copy()
        paste(sc, tree, int(W * 0.03), BASE - tree.shape[0] // 2 + int(CELL * 0.2))
        paste(sc, dummy, DX, BASE - dummy.shape[0] // 2)
        art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL * (IDLE_SCALE if idle else 1.0))
        g = grip_of(art) + DIAG * GRIP_EXTRA

        for px, fc in zip(FACE_X, FACINGS):
            body, aim_off = bodies[fc["name"]], fc["aim"]
            cy = BASE - BH // 2
            paste(sc, body, px, cy)
            a = ang + aim_off
            if smear:                                   # subframe ghosts along the arc just travelled
                for k, al in ((6, 0.30), (12, 0.16)):
                    r2 = math.radians(a + k)
                    paste(sc, rot(art, a + k - ART_ANGLE),
                          px + math.cos(r2) * off * CELL, cy - math.sin(r2) * off * CELL, al)
            r = math.radians(a)
            tx, ty = px + math.cos(r) * off * CELL, cy - math.sin(r) * off * CELL
            paste(sc, rot(art, a - ART_ANGLE), tx, ty)
            rr = math.radians(-(a - ART_ANGLE))
            gg = g * art.shape[0]
            paste(sc, rot(hand_s, a - ART_ANGLE + HAND_ROT),
                  tx + gg[0] * math.cos(rr) - gg[1] * math.sin(rr),
                  ty + gg[0] * math.sin(rr) + gg[1] * math.cos(rr))
        im = Image.new("RGBA", (W, H), (30, 36, 30, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        return im.convert("RGB"), freeze

    def frame_arm(tool, t):
        """Approaches 8/9: place the HAND on an arm arc, then hang the tool off the hand.

        The order matters and is the whole point. Everywhere else the tool is positioned first and the
        fist is stuck to its grip afterwards, so the hand goes wherever the sprite's rotation puts it.
        Here the hand is driven and the tool follows it, which is the way round a real swing works.
        """
        p = TOOLS[tool]
        theta, armlen, freeze, smear, lean, step = arm_motion(approach, p, t)
        sc = ground.copy()
        paste(sc, tree, int(W * 0.03), BASE - tree.shape[0] // 2 + int(CELL * 0.2))
        paste(sc, dummy, DX, BASE - dummy.shape[0] // 2)     # something for the side swing to reach
        art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL)
        g = (grip_of(art) + DIAG * GRIP_EXTRA) * art.shape[0]
        arot = p.get("art_rot", 0.0)

        for px, fc in zip(FACE_X, FACINGS):
            body = bodies[fc["name"]]
            cy = BASE - BH // 2
            bx = px + step * CELL                       # the step INTO the swing (approach 9 only)

            a = theta + fc["aim"]
            if fc["floor"] is not None:                 # front view: stop in front, don't bury the tool
                a = max(a, fc["floor"])
            sh_x = bx + fc["sh"][0] * CELL
            sh_y = cy - fc["sh"][1] * CELL
            r = math.radians(a)
            hx = sh_x + math.cos(r) * armlen * CELL     # the HAND, on its arm arc
            hy = sh_y - math.sin(r) * armlen * CELL

            rr = math.radians(-(a - ART_ANGLE))         # the tool hangs off the hand, grip-first
            tx = hx - (g[0] * math.cos(rr) - g[1] * math.sin(rr))
            ty = hy - (g[0] * math.sin(rr) + g[1] * math.cos(rr))

            def draw_tool():
                if smear:
                    for k, al in ((7, 0.28), (14, 0.14)):
                        paste(sc, rot(art, a + k - ART_ANGLE + arot), tx, ty, al)
                paste(sc, rot(art, a - ART_ANGLE + arot), tx, ty)
                paste(sc, rot(hand_s, a - ART_ANGLE + HAND_ROT), hx, hy)

            if fc["behind"]:                            # away-facing: the swing happens behind him
                draw_tool()
                paste(sc, rot(body, lean) if lean else body, bx, cy)
            else:
                paste(sc, rot(body, lean) if lean else body, bx, cy)
                draw_tool()
        im = Image.new("RGBA", (W, H), (30, 36, 30, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        return im.convert("RGB"), freeze

    frames, ms = [], []
    for tool in (DEMO_TOOLS if approach >= 10 else ("sword", "axe", "net", "hoe")):
        p = TOOLS[tool]
        dur = duration(approach, p)
        n = max(8, int(dur * FPS * 3))
        for reps in (1, 2):
            for _ in range(reps):
                for i in range(n):
                    img, fr = frame(tool, i / (n - 1))
                    step = int(dur * 1000 / n)
                    frames.append(img)
                    ms.append(step * (4 if fr else 1))     # a freeze is a held frame, purely local + visual
            # hold the IDLE pose, not t=0 — the cut from swing-end to idle is part of what we're judging
            frames.append(frame(tool, 1.0, idle=True)[0]); ms.append(650)
    out = os.path.join(DEST, f"iteration-{approach}.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(f"  approach {approach}: {len(frames)} frames -> {out.replace('/mnt/c/', 'C:/')}")
    return out


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
