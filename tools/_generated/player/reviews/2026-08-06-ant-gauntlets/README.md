# Ant gauntlets — awaiting your review (nothing is official)

**Status: fireant and blackant are PENDING.** I promoted them to official before you had looked, which
was wrong — you are the gate. That is reverted: `official.py` has bronze only, and the ant `gauntlet/`
and `anim/` folders are removed. The generated candidates are intact in
`outfits/<name>/tries/2026-08-06-official-gauntlet/`.

## You said the ant gauntlets need to be reversed. I checked the two things that could mean, and neither is true.

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

Worth noting: on 2026-08-05 you said *"the gauntlets for red and black ants for walk front need to be
flipped horizontally, the palms are facing out"*. That was about the **old 4-hand** gauntlets, and the
palms-out cause has since been fixed globally — the camera-facing walk now mirrors the left hand for every
outfit. So that specific complaint should already be gone.

**What would help:** which animation, and which hand. `GAUNTLETS_all_three.png` in
`../2026-08-06-bronze-hands/` has all three sets side by side if that is easier to point at.

## Cost so far

Two paid calls (gpt-image-2), one per ant. Both cut cleanly into five hands. A third earlier call failed
and produced nothing — possibly billed; the bug that caused it is fixed.
