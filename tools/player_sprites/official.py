"""official.py — the ONE file that says what is official. If it is not in here, it does not exist.

THE RULE
--------
The build reads this file and nothing else. No directory scanning. No fallbacks. No "if this file exists
use it, otherwise use that one". **A missing file stops the build and prints which one.**

That last sentence is the entire fix. Every confusion in this pipeline came from its absence:

  * `render_animations.py:79-83` looked for an outfit's hands in THREE places and took the first that
    existed. Measured on 2026-08-06 by patching the image loader and running it over all 24 outfits:
    21 resolved to a GITIGNORED archive folder, 2 to their own `gauntlet/`, and bronze to a hardcoded
    exception reading two other folders entirely. Nobody chose that. The fallback chose it.
  * `DECISIONS.md` and `CURRENT.md` recorded what was approved — and **no build code ever opened them.**
    `render_animations.py` mentions "APPROVED" 18 times in comments and reads a decision file zero times.
    So the record of what was official and the thing the code loaded were never the same object, which is
    why asking for "a gallery of the official ones" returned whatever happened to be on disk.

Owner, 2026-08-06: *"when we make a change it is reflected in our fucking code somewhere - I dont care
where as long as its actually used."* This is that place.

HOW TO CHANGE SOMETHING
-----------------------
  Change a swing            edit the animation's `motion`, rebuild. The gif AND the gallery both change,
                            because both read this line.
  Try alternatives          generate into `outfits/<name>/tries/<date>-<what>/`, look, then point the
                            line at the one you picked. Every other attempt stays in `tries/` forever.
  Go back to an old swing   point the line at the old motion name. MOTIONS only ever grows; nothing in it
                            is edited in place or deleted, so no decision can become unreachable.

WHAT IS *NOT* HERE
------------------
Nothing about *how* art is made — prompts, cutting, keying. Those live with the code that does them. This
file only answers "which one is official", for every sprite and every animation.
"""

# ── HAND ROLES ───────────────────────────────────────────────────────────────────────────────────────
# Every outfit has its own version of every hand bronze has. The COUNT is not a decision to make — it is
# whatever this list says, and the prompt, the cutter and the renderer all read it from here.
#
# It was previously hardcoded in three places that disagreed: `cut_gauntlet(cols=4)`, four poses written
# into the gauntlet prompt text, and five keys returned by `load_hands`. That disagreement is why 23 of 24
# outfits ended up holding a two-handed tool with the SAME hand twice — there was no fifth hand to use, so
# `grip_palm` silently fell back to `grip_back`.
HAND_ROLES = ["front", "back", "side", "grip_back", "grip_palm"]

HAND_ROLE_MEANING = {
    "front":     "back of a closed fist (knuckles toward camera)",
    "back":      "the palm side",
    "side":      "the fist in profile",
    "grip_back": "fist closed around a pole, knuckles showing",
    "grip_palm": "fist closed around a pole, palm showing — the SECOND hand on a two-handed tool",
}

# The hand set every other outfit is a material variant of. Owner: *"the only officially established hands
# are the bronze hands... everything else will have literally their own as close as possible variants."*
REFERENCE_OUTFIT = "bronze"


# ── OUTFITS ──────────────────────────────────────────────────────────────────────────────────────────
# EVERY OUTFIT HAS THE SAME SHAPE. The subfolder names are fixed by the system, not chosen per outfit —
# so there is exactly one place each kind of thing can live, and "where are this outfit's hands?" has one
# answer for all 30 of them.
#
#   <dir>/tries/<YYYY-MM-DD>-<what>/   every attempt, kept forever. THE BUILD NEVER READS THIS.
#   <dir>/frames/                      the chosen body frames
#   <dir>/gauntlet/                    the chosen hands, one per HAND_ROLES
#   <dir>/anim/                        rendered animations. build.py OWNS this folder.
#
# Choosing something = COPY it from tries/ into place. Never a move: the attempt stays where it was, so
# nothing is consumed and nothing can be overwritten. Git holds every prior state.
TRIES_DIR, FRAMES_DIR, HANDS_DIR, ANIM_DIR = "tries", "frames", "gauntlet", "anim"

# `dir` is relative to tools/_generated/player/. An outfit with no approved hands is simply ABSENT from
# here — it is never quietly rendered with someone else's.
# `sheet` is the chosen 12-frame generation, relative to `dir`. The frames were cut from it, and the
# gauntlet prompt sends it as the COLOUR reference so the hands match that outfit's material. It is a
# chosen artifact, so it is declared here rather than found by looking for a file called result.png —
# which broke the moment those files were tidied into tries/.
OUTFITS = {
    # 2026-08-18 — ALL THREE REPLACED with their pixel-converted rebuilds. What was here before was the
    # RAW render: measured, the old `bronze/frames/front_2.png` was 162x297 with 12,555 colours and
    # blackant's 185x455 with 11,874. These are 27x68, 26x77 and 32x87, ~1,000 colours — actual sprites.
    # The raw art is kept at `<dir>/archive/2026-08-18-superseded-raw/`; nothing was deleted.
    #
    # `sheet` is empty for all three: it named the old 12-frame generation, and that pipeline is retired
    # (a twelve-cell sheet leaves each figure too small to carry a pixel grid). An outfit is now a
    # turnaround plus one call per direction, so there is no single sheet to point at.
    "bronze":   dict(dir="outfits/bronze", approved="2026-08-18",
                     sheet="",
                     words="it looks good... these seem good, pixelization works"),
    "fireant":  dict(dir="outfits/fireant", approved="2026-08-18",
                     sheet="",
                     words="it looks good... these seem good, pixelization works"),
    "blackant": dict(dir="outfits/blackant", approved="2026-08-18",
                     sheet="",
                     words="it looks good... these seem good, pixelization works"),
}

# NOT OFFICIAL YET — listed so the gap is visible, but NOT built. An outfit is either complete and in
# OUTFITS, or it is here and does not render at all. There is no third state where it renders with
# somebody else's parts, which is exactly what the old fallback chain did to 21 outfits.
PENDING = {
    # 2026-09-26 — copper, the first test batch on the rebuilt procedure (`procedure.py`). Listed so its
    # attempt can be RENDERED FOR REVIEW (`build.py copper`); `dir` is the attempt folder, so nothing is copied
    # into outfits/copper/ until the owner says yes. Then it moves to OUTFITS with his words.
    "copper": dict(dir="outfits/copper/tries/2026-09-26-procedure", sheet="",
                   needs="the owner's review — tools/_generated/player/reviews/2026-09-26-copper/"),
}


def path(outfit, kind):
    """The one place `kind` ('frames' | 'gauntlet' | 'anim' | 'tries') lives for this outfit.

    Resolves against PENDING too, so tooling can SHOW an unfinished outfit's folders. Only `OUTFITS`
    is ever BUILT — being resolvable is not the same as being official.
    """
    entry = OUTFITS.get(outfit) or PENDING.get(outfit)
    if entry is None:
        raise KeyError(f"{outfit!r} is in neither OUTFITS nor PENDING in official.py")
    return f"{entry['dir']}/{kind}"


def sheet(outfit):
    """The outfit's chosen 12-frame generation — the colour reference for its gauntlet prompt."""
    entry = OUTFITS.get(outfit) or PENDING.get(outfit)
    if entry is None:
        raise KeyError(f"{outfit!r} is in neither OUTFITS nor PENDING in official.py")
    return f"{entry['dir']}/{entry['sheet']}"


# ── MOTIONS ──────────────────────────────────────────────────────────────────────────────────────────
# ONLY EVER GROWS. Superseding a motion means ADDING the replacement beside it, never editing this one in
# place — otherwise "go back to the one from Tuesday" becomes an archaeology exercise. It already did: the
# agreed net sweep had to be recovered from commit 8bfd24e after a later variant overwrote it in the lab.
#
# GAIT motions are dicts of the owner's tuned constants, recovered verbatim from the 2026-07-28 session.
# ⚠ These numbers are HIS. Do not adjust them to make other code look right; fix the other code.
GAITS = {
    # amp=hand travel, ay=rise, rot=base rotation, tilt=wrist lean, ratio=fist size vs body height,
    # waist=where the hands hang, ms=frame duration
    #
    # 2026-07-29 — "walk b is fine"   (rendered as walk_ref/walk_b)
    "WALK": dict(amp=0.52, ay=0.013, rot=0.0,  tilt=22.0, ratio=0.17, waist=0.60, ms=150),
    # 2026-07-29 — "RUN_r75.gif is fine, looks the best"
    "RUN":  dict(amp=0.58, ay=0.032, rot=75.0, tilt=14.0, ratio=0.19, waist=0.46, ms=90),

    # The camera-facing walk is a SEPARATE motion, not the side one re-aimed: a different fist (profile),
    # hands outside the body edges rather than swinging through the torso, one rising as the other drops.
    # 2026-07-29 — "first for walking forward gait_front_d3_bigger.gif is great"
    #
    # ⚠ 2026-08-18 — THE UNITS CHANGED, THE DESIGN DID NOT. `ratio` is now the fist's height as a
    # fraction of the SHOULDER WIDTH, `row` how far from the shoulders down to the feet the fists
    # hang, `dx`/`dy` travel in shoulder widths, `edge` the clearance outside the shoulder edge
    # (`gap`, a fraction of an arbitrary silhouette row, floored to its 2px minimum on every outfit
    # and is gone). Hanging hands off a percentage of the whole silhouette made every outfit with
    # different headgear disagree — fire-ant's fists ended up at its armpits and black-ant's inside
    # its own shoulder line. Owner, shown all three: *"black ant is the only good one"*, so every
    # constant below was solved from black-ant and it renders unchanged.
    # Measured before/after: reviews/2026-08-18-walk-hands/.
    "FRONT":     dict(ratio=0.484, row=0.340, edge=0.016, dx=0.037, dy=0.092, ms=150),
    # Same motion at run speed. ⚠ NOT designed — see NOT_AGREED. Only the SIDE run has its own pose.
    # 2026-08-14 — "we will go with wisdest lowest". The camera-facing run had NO pose of its own:
    # this row was byte-identical to FRONT apart from ms, i.e. the walk played faster, which is the
    # failure the side run already fixed. Owner: "that's just not running with hands down by the
    # side". Picked from reviews/2026-08-14-run-front-pump/ against three rendered options; the two
    # rejected attempts are recorded there. `pulse` is new — the fist coming toward the camera grows.
    # ⚠ run_back shares this row, so it changes too.
    "FRONT_RUN": dict(ratio=0.484, row=0.180, edge=0.016, dx=0.047, dy=0.151, pulse=0.22, ms=90),
}
# The back-facing walk reuses FRONT deliberately: from behind you also see both hands clear of the
# silhouette, and at ~10px a hand the near/far distinction the side walk needs does not read.
# 2026-08-02, delivered against "so we have forward and sideways might as well finish with back".

# ── SETTLED 2026-08-06 — "all three fixes look good! make it official" ────────────────────────────────
# Three things about how the hands are PLACED. They are behaviour, not numbers, so they live in the code
# that draws them — recorded here because this file is where "what did we agree" gets answered.
#
#  1. FIST SIZE — walk stays at 0.17. He was explicit: "hand sizes we go with current". His earlier
#     "way too big" complaint was about the RUN, which has its own larger ratio (0.19, above).
#  2. WRIST DIRECTION — the cuff leans TOWARD the body, because that is where the arm comes from
#     (`gait.pose_into`). Both signs had been inverted, so the forward fist's wrist sat further forward
#     than the fist and the arm read as reaching around from the far side. Reported 2026-08-03 and again
#     2026-08-06. An intervening "fix" made the two hands tilt in OPPOSITE directions, which sounds like
#     the same change and is not — both stayed wrong.
#  3. PALMS TURN IN — the camera-facing walk mirrors the LEFT hand (`build._gait_front_frames`).
#     Mirroring the right instead turns both palms outward, which shipped and was rejected twice.

# SWING motions: (anticipation pose, [4 strike poses], rest pose).
# A pose is (arm offset from the aim direction, blade angle behind the arm, reach in cells).
SWINGS = {
    # 2026-08-04 — "yes we obviously want the quick candidate"
    # Behind the head, past straight down, hand finishing at the hip; the blade unwinds so the tip keeps
    # dropping after the arm has stopped.
    "SWORD_SIDE": ((120, 88, 0.60),
                   [(60, 76, 0.62), (-10, 62, 0.64), (-70, 48, 0.62), (-104, 40, 0.60)],
                   (-35, 60, 0.58)),

    # 2026-08-04 — "lets do double back for both, the seem good". Used facing DOWN and facing UP.
    # Out across, then whipped back through the other way.
    "DOUBLE_BACK": ((+70, 66, 0.50),
                    [(0, 44, 0.60), (-64, 30, 0.56), (-10, 46, 0.58), (+34, 58, 0.54)],
                    (+34, 60, 0.46)),

    # 2026-08-04 — "this net for the side will work: ...1204_8bfd24e_net_A_sweep_and_lift.gif"
    "NET_SIDE": ((80, -40, 0.50),
                 [(30, -48, 0.62), (-20, -54, 0.66), (-50, -40, 0.62), (-30, -10, 0.58)],
                 (40, -30, 0.46)),

    # 2026-08-04 — "...axe_B_high_chop.gif for the axe"
    "AXE_SIDE": ((172, 78, 0.42),
                 [(95, 56, 0.52), (16, 22, 0.62), (-34, -2, 0.64), (-38, 0, 0.62)],
                 (70, 58, 0.44)),

    # 2026-08-04 — "...hoe_B_long_drag.gif for the side hoe"
    "HOE_SIDE": ((78, 58, 0.46),
                 [(-46, 12, 0.64), (-60, 2, 0.68), (-72, 6, 0.46), (-84, 12, 0.26)],
                 (40, 50, 0.44)),

    # 2026-08-04 — "...shovel_B_deeper.gif for the shovel". A lever held low, not a battering ram.
    "SHOVEL_SIDE": ((-60, 44, 0.32),
                    [(-58, 38, 0.52), (-56, 28, 0.76), (-50, 56, 0.74), (-44, 74, 0.68)],
                    (-60, 46, 0.32)),
}


# ── ANIMATIONS ───────────────────────────────────────────────────────────────────────────────────────
# ONE ROW FULLY DEFINES ONE ANIMATION. Adding one is a row, not a branch.
#
# Before this file, an animation's definition was split across three places and no single one of them said
# what an animation was: `gait.py` held the walk constants, `motions.py` held the swing arcs, and a
# `SWORD_FACINGS` dict inside `render_animations.py` held which body frames to use, where the shoulder
# sits and whether the weapon draws behind the body — in the same file as 174 lines of dead code.
#
#   frames    which frame bank: side / front / back
#   motion    a key in GAITS or SWINGS
#   aim       direction being attacked: 0 = sideways, -90 = toward camera, +90 = away
#   shoulder  (x, y) shoulder position in cells, measured from the body centre
#   behind    draw the weapon BEHIND the body (true when he is facing away)
#   two_handed / pivot / second   a lever grip: where the tool sits on the driving hand, and where the
#             second fist sits along the shaft. NEGATIVE `second` puts it toward the butt.
SHOULDER = (0.06, 0.40)

ANIMATIONS = {
    "walk_side":  dict(kind="gait",       frames="side",  motion="WALK"),
    "run_side":   dict(kind="gait",       frames="side",  motion="RUN"),
    "walk_front": dict(kind="gait_front", frames="front", motion="FRONT"),
    "run_front":  dict(kind="gait_front", frames="front", motion="FRONT_RUN"),
    "walk_back":  dict(kind="gait_front", frames="back",  motion="FRONT"),
    "run_back":   dict(kind="gait_front", frames="back",  motion="FRONT_RUN"),

    "swing_sword":      dict(kind="attack", frames="side",  motion="SWORD_SIDE",
                             tool="sword_bronze_icon.png",  aim=0.0,   shoulder=SHOULDER),
    "swing_sword_down": dict(kind="attack", frames="front", motion="DOUBLE_BACK",
                             tool="sword_bronze_icon.png",  aim=-90.0, shoulder=(0.26, 0.12)),
    "swing_sword_up":   dict(kind="attack", frames="back",  motion="DOUBLE_BACK",
                             tool="sword_bronze_icon.png",  aim=+90.0, shoulder=(0.26, 0.22),
                             behind=True),

    "swing_axe":    dict(kind="attack", frames="side", motion="AXE_SIDE",
                         tool="axe_copper_icon.png",    aim=0.0, shoulder=SHOULDER),
    "swing_net":    dict(kind="attack", frames="side", motion="NET_SIDE",
                         tool="small_net_icon.png",     aim=0.0, shoulder=SHOULDER),
    "swing_hoe":    dict(kind="attack", frames="side", motion="HOE_SIDE",
                         tool="hoe_copper_icon.png",    aim=0.0, shoulder=SHOULDER),
    "swing_shovel": dict(kind="attack", frames="side", motion="SHOVEL_SIDE",
                         tool="shovel_copper_icon.png", aim=0.0, shoulder=SHOULDER,
                         two_handed=True, pivot=0.34, second=-0.22),
}


# ── NOT AGREED — deliberately absent, so it cannot render by accident ────────────────────────────────
# An unsettled animation is NOT listed above, so the build does not produce it and cannot silently ship a
# superseded version. `thrust_spear_two_handed.gif` sat in 22 outfits for weeks, was committed, and showed
# in the gallery, long after the code that made it stopped existing. Absence here is the fix for that.
NOT_AGREED = {
    "spear (side)":              "length settled at 1.9 cells; the motion is not",
    "axe/hoe/net/shovel up+down": "only the sword has facing-up and facing-down motions",
    "run_front / run_back":       "listed above, but it is the WALK played faster — never designed as its "
                                  "own motion. Real camera-facing run poses do not exist yet.",
}
