# 2026-08-15 — fireant walks generated one direction at a time

Open these in a file explorer. Every file in this folder is listed below.

**Nothing here has replaced the live fireant.** It all sits in a scratch folder
(`outfits/fireant-sidewalk/`) and the game is unchanged.

---

## `ALL_ANIMATIONS.gif` ← **watch this one**

All six playing at once, walks on the top row, runs underneath, each at its own speed. The walks
loop three times and the runs five times in the 1800ms it takes to go round, so nothing jumps at
the loop point.

The run is its own motion, not the walk sped up: `RUN` (approved 2026-07-29 as the best-looking run,
`RUN_r75.gif`) swings the fists wider, rotates them 75 degrees into a running arm, makes them bigger and
carries them lower; `FRONT_RUN` (picked 2026-08-14: the widest, lowest variant) is the camera-facing
one, with `pulse` so the fist coming toward you grows. Both share the walk's leg frames by design.

## The six animations individually

| file | |
|---|---|
| `walk_side.gif` | side walk |
| `walk_front.gif` | walking toward you |
| `walk_back.gif` | walking away |
| `run_side.gif` `run_front.gif` `run_back.gif` | the same three bodies on the run timing |

All shown at 6x. The sprites underneath are real pixels — 77 (side), 75 (front), 78 (back) pixels
from head to feet.

### `LIVE_vs_NEW.png` ← **the one that shows whether this is better**
The current live fireant on top, the new one below, same scale. The live one has purple fringe
pixels around the edges and mushy shapes; the new one doesn't.

### `ALL_THREE_WALKS.png`
All three walk cycles, four beats each, laid out so you can read the poses without playing them.

### `THREE_BANKS_SIZE.png`
The three directions side by side at one scale with their feet on the same line — this is the
check that they're the same size as each other.

### `frames_walk_side.png` / `frames_walk_front.png` / `frames_walk_back.png`
Each cycle's four beats as a strip.

### `RAW_side_from_gpt.png` / `RAW_front_from_gpt.png` / `RAW_back_from_gpt.png`
What gpt actually sent back for each direction, before conversion. Four frames in a row on magenta.

### `SIDEWALK_SNAPPED.png`
The standing reference next to the four side frames after conversion, to show they came out the
same size as the reference.

---

## Earlier attempts, same evening (the 12-frame sheet)

| file | what it was |
|---|---|
| `ANIMATED.gif` | the 3x4 sheet attempt, animated. Frames drifted in scale; never converted cleanly. |
| `PITCH_CANDIDATES.png` | the sheet converted at several grid sizes to find the real one by eye. There wasn't one. |
| `IN_vs_OUT.png` | pixel art in, smooth repaint out — the picture of why the sheet failed. |

---

## What actually made the difference

Not the prompt wording. **The canvas.**

A 3x4 sheet gives each figure about a twelfth of the canvas, so the pixel blocks come back too
small to be a grid and there is nothing to convert. **Four frames in one row** gives each figure
the same room as the standing turnaround, which is the layout that has always converted properly.

Verified from the run records: the two layouts that worked are 1536x1024 landscape; the sheet that
failed was 1024x1536 portrait.

## What was done, per direction

| | grid found | pixels tall | frames 2 & 4 |
|---|---|---|---|
| side | 9.70 | 77 | identical — so dropping 4 and cycling 1,2,3,2 is right |
| front | 10.40 | 75 | genuinely different poses |
| back | 9.80 | 78 | genuinely different poses |

Sizes agree within 3 pixels, so all three can be shown at one whole-number scale.

**The front took two calls.** The first came back both taller and on a finer grid — 90 pixels
against the side's 77, which is a visible size jump when you turn to face the camera. The second
roll used a character-for-character identical prompt and landed at 75.

**Fixed along the way:** the magenta fringe. The converter was taking the median of colour and
transparency together, so an edge cell got a half-transparent *magenta* pixel. Colour is now
averaged over only the character's own pixels in each cell. That's what the purple speckle on the
LIVE row of `LIVE_vs_NEW.png` is, and it's gone from the new row.

## The gauntlets — remade so nothing gets squashed

`HANDS_IN_CONTEXT.png` is the before/after.

The old gauntlet is 20 pixels tall and the walk needs 13, so every frame squashed it by 0.65 —
deleting rows. The new one is **drawn at 13**, so five of the six animations now use the hand
exactly as drawn, with no resampling at all. Only `run_side` scales it, and that's a 1.15 *upscale*
(duplicates rows) rather than a squash (deletes them).

**Getting there took six calls, and five of them failed.** Worth writing down why, because the
reason is arithmetic and not wording:

The model always draws a hand about **200 screen pixels** tall, no matter what it's asked. So the
hand's size in real pixels is just `200 / block-size`, and the block size is set by how tall it
draws the character. On a wide canvas the character can't be drawn taller than ~900px, which pins
the block size near 12 and floors the hands at about 16 real pixels. No prompt wording can get
under that — I tried "one sixth as tall as the character", "exactly 13 blocks, count them", and a
template with correctly-sized boxes to draw inside. They landed at 19.7, 19.5, 16.0, 19.3.

The fix was the **tall canvas**. Turning it portrait and stacking the five hands in a column beside
the character lets the character be drawn ~1400px tall, which pushes the block size to 18.5 — and
the model's usual 200px hand lands at 13. Predicted 12.4 before spending; measured 12.1–14.1.

The character came back at 25.0 x 76.5 against a 25 x 76 reference, so the hands are on exactly the
character's own grid — same pixel density, which is the whole point.

Heights came out 12-14 rather than all exactly 13, so each is padded or trimmed by one row **at the
wrist**, never rescaled. A trimmed cuff row costs one row; rescaling would have touched every pixel.

## The legs, and using all four frames

`LEGS_BEFORE_AFTER.png` is the comparison.

The front and back walks had the feet swinging wide to either side of the body — a dance, not a
walk. Rerolled both, giving the model the current four snapped frames as the reference and asking
for one change: feet close under the hips, knees and feet pointing forward, the stepping foot
lifting rather than striding out sideways. Everything else held — the rerolled figures came back at
77.0 (front) and 78.0 (back) against the side's 77, so all three are now within one pixel.

**All four frames are now used** (`[1,2,3,4]` instead of `[1,2,3,2]`). To answer why it was ever
2-instead-of-4: on the side, frames 2 and 4 came back as literally the same image, so playing frame
2 twice cost nothing. On front and back they are the two different passing poses — opposite leg
leading — so the old cycle was throwing a real pose away.

**⚠ Making that official is not just a constant change.** `gait.CYCLE` is shared, and bronze and
blackant only have three frames on disk. Switching the shipped constant to `[1,2,3,4]` would break
their builds until they are regenerated too. For now the 4-frame cycle lives only in the scratch
render script; `gait.py` and `official.py` are untouched.

**One knock-on to look at:** the rerolled front body is narrower (26 wide, was 33). The hand
placement is a fraction of body width, so the fists now sit further out with a visible gap. Those
are approved numbers so I have not retuned them.

## Cost

Ten calls. Three walk directions, one re-roll of the front (it came back 90 pixels tall against the
side's 77), and six on the gauntlets.
