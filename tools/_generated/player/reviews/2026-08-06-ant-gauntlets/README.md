# Ant gauntlets — APPROVED 2026-08-06

Owner approval (2026-08-06): every hand in the animation sheet is correct and these gauntlets are approved;
the red and black ant outfits get them. The tool swings still need his review, to confirm those hands are correct.

fireant and blackant are official. 3 outfits, 39 animations.

> I had promoted them **before** you looked, which was wrong — you are the gate. That was reverted and
> re-done in the right order. The rule now lives in `CHARACTER_DESIGN_GUIDE.md`: generate into `tries/`,
> render a review, **you say yes**, then copy into place. Reverting cost nothing only because choosing is
> a copy and `tries/` is never touched.

## Still to check: the tool swings — `TOOLS_*.png`

The walk uses `front`/`back`/`side`. The swings use the **grip** hands, which you have not seen in motion
yet:

| | hands used |
|---|---|
| `TOOLS_swing_sword.png`, `_axe`, `_net`, `_hoe` | `grip_back` only |
| `TOOLS_swing_shovel.png` | `grip_back` **and** `grip_palm` — the two-handed one |

The shovel is the one worth looking at hardest. Until today, **23 of 24 outfits held it with the same hand
twice**, because the gauntlet sheet only ever produced four hands and `grip_palm` fell back to `grip_back`.
All three sets now have a real pair.

## The reversed-hands question — resolved

You confirmed it: row 3 matches row 1, B disagrees. The hands were never mirrored. My sheet was the
problem — it compared *source files* and never said which one the animation actually uses, so it could not
answer the question you were asking. `IN_THE_ANIMATION_walk_front.png` shows the hands **as rendered**,
which is the comparison that was needed from the start.

What I had checked, for the record:

**1. Are the ant hands mirrored relative to bronze?** → `IS_IT_MIRRORED.png`

Bronze as-is / bronze flipped left-right / fireant. Row 3 matches row **1**, not row 2 — clearest on the
`side` (profile) hand, where the C-opening faces the same way as bronze's. So the hands were not flipped
in generation.

**2. Do the ant bodies face the wrong way?** → `A_or_B_side_facing.png` and `SIDE_FACING.png`

This one matters because `_generated/player/README.md` says the side row **must face right** — everything
downstream assumes it, and copper and farmer were both wrong this way. But bronze's visor slits and the
ants' faces both point right, so A (as cut) already matches bronze. B is what mirroring would give, and it
is the one that disagrees.

## So I do not know what you are seeing, and I would rather ask than guess again

`WHY_IT_LOOKS_REVERSED.png` was my first attempt at this and **its labels are wrong** — I asserted a
facing direction I had misread. Kept only so the mistake is on the record; ignore its captions.

Worth noting: on 2026-08-05 you noted that the red and black ants' gauntlets for the front walk needed
flipping horizontally, because the palms faced out. That was about the **old 4-hand** gauntlets, and the
palms-out cause has since been fixed globally — the camera-facing walk now mirrors the left hand for every
outfit. So that specific complaint should already be gone.

**What would help:** which animation, and which hand. `GAUNTLETS_all_three.png` in
`../2026-08-06-bronze-hands/` has all three sets side by side if that is easier to point at.

## Cost so far

Two paid calls (gpt-image-2), one per ant. Both cut cleanly into five hands. A third earlier call failed
and produced nothing — possibly billed; the bug that caused it is fixed.
