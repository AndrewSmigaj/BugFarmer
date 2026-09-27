# 2026-08-04 — vertical sword swings, one- and two-handed

**Open `ALL_EIGHT_contact_frame.png` first** for the contact pose of all eight side by side, then play the
gifs of whichever ones survive that.

`REFERENCE_what_we_have_now.gif` is the currently-approved swing, for comparison. Judge against it, not in
isolation.

## Why these are vertical

A hand sprite is drawn from **one** viewpoint, and that viewpoint tells you where the arm is. Looking down
at the knuckles reads as an arm stretched out; the back of the hand reads as an arm that is *not*
extended, because on an arm reaching out to the side the wrist turns the hand edge-on.

The old swing spun **one** sprite through a ~250° lateral arc, so across most of that arc the drawn hand
contradicted where the hand actually was. That is why it read as impossible while no single part looked
wrong — and why retiming it, re-cutting it and swapping between the hands we already had all failed.

Top-to-bottom removes the conflict rather than drawing around it. One hand carries the whole motion, and
**no new art was needed** — nothing here cost money.

## The hands

Both already approved, 2026-08-01, as a pair — one per arm:

- `grip_back_of_hand.png` — the arm you see the **back** of
- `grip_palm.png` — the other arm, the one whose palm is visible

**Two-handed uses both**, the palm hand further up the handle. Not a mirrored copy of the first — mirroring
the back of a hand gives a mirrored back of a hand, never a palm.

## The four

| | motion |
|---|---|
| **V1 overhead** | up above the head, straight down through, short recovery |
| **V2 diagonal** | outside shoulder down across to the opposite hip; reaches out through the strike |
| **V3 loaded** | small lift, brief hang, then the whole drop at once — weight in the fall |
| **V4 chop-and-stop** | down with a hard stop *on* the contact pose, then recover |

All start and end at `IDLE_ANGLE`, so the swing has an exit and does not pop when it ends.

## What I can see already, for what it's worth

- **V1 and V3 finish with the blade across the legs.** The tool draws in front of the body, so at a steep
  down angle it reads as embedded in the character rather than swung past it. V3 is the worst of the four
  for this.
- **V2 and V4 stay clear of the body** and read cleanest at the contact frame.
- On **2h V1 and 2h V3** the two fists stack into one blob at the low angle; on 2h V2 and 2h V4 they stay
  legible as two hands.

That is my read from the still frames only — the gifs are what decide it.

## Once you pick

It gets baked into `render_animations.py` as the sword default and your decision is recorded in
`APPROVED/DECISIONS.md` — dated, attributed, in clean prose — the same day. The axe, hoe, net, shovel
and spear come after, using whatever wins here.
