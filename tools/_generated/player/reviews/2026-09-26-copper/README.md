# 2026-09-26 — Copper: the first test batch on the rebuilt procedure

> **VERDICT (2026-09-26): approved** — *"it looks good! there are polish issues but we can work on that later as they
> involve hand positions"*. Copper is now official (`outfits/copper/`). No rerolls were asked for; the back-walk size
> and the front knee lift below stay on the polish list with his hand-position note.

Folder: `C:\Users\emily\BugFarmer\tools\_generated\player\reviews\2026-09-26-copper\`

Your copper pick (`explore/copper-r3`, design 1) taken through the whole procedure the approved outfits used:
the pick converted to real pixels → a front/side/back turnaround → one walk per direction → the five hands.
**Five paid calls, no rerolls.** Nothing is official: copper is listed as *pending* in `official.py`, and its
frames and hands sit in `outfits/copper/tries/2026-09-26-procedure/` until you say yes.

## Open these
1. **`01_ALL_ANIMATIONS.gif`** — every animation at once (walks, runs, swings). The main judgement.
2. **`02_sizes_and_knee_lift.png`** — the three directions at one scale, and the stepping frames. The two
   problems below are visible here.
3. `04_pick_and_turnaround.png` — your pick in real pixels (23×66) beside the three turnaround views.
4. `05_hands.png` — copper's five hands beside bronze's (the shapes every outfit copies).
5. `03_pixel_proof.png` — each direction enlarged, with its size and colour count: real pixels, hard edges.
6. `06_what_gpt_returned.png` — the five renders as they came back, reduced.
7. `animations/` — each animation on its own.

## What worked
- The turnaround kept the design: crested open helm, face, green trim. Its three views are 66 / 65 / 67 px tall.
- The hands came back as bronze's five shapes in copper, at the character's pixel size (11 px — 66 × 0.17).
- Every stepping cycle alternates legs correctly (front and back checked by measurement; side by eye).
- The side walk came back facing RIGHT (the three approved ones all came back facing left and were flipped);
  the cutter now asks which way a side render faces instead of always flipping it.

## Two problems — each fix is one paid call, so nothing was rerolled without asking
1. **The back walk is too big: 71 px tall against the front's 66 and the side's 63.** The approved outfits kept
   the three within 3–4 px (black-ant 74 / 75 / 78); this spread is 8, and the back is visibly larger when he
   turns around. The usual fix is a fresh roll of the back walk (same prompt), never a resize.
2. **The front walk lifts the knee too high: 18% of body height** (the target band is 7–15%). This is your August
   note — *"its lifting the knees really high which is ok for running but not walking"* — and the medium-high
   wording added then did not cure it on this roll. The three approved outfits have the same thing (bronze 19%,
   fire-ant 18%), which you put down as polish for later.

Also measured: the side walk is 63 px, two short of its turnaround view (65) — within what the approved outfits had.

## What I need from you
1. Apart from the two problems: is copper right — the design, the pixels, the hands?
2. The back walk: **(a)** one fresh roll, same prompt (recommended) · **(b)** keep it.
3. The front knee: **(a)** keep it and fix knee lift on every outfit together in the polish pass, as with the three
   approved ones · **(b)** one fresh roll, same prompt · **(c)** a correction call asking for a lower knee (new
   wording — I'd show it to you first).

The same questions are in the chat.
