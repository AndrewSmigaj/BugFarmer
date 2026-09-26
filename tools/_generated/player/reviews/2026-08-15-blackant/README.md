# 2026-08-15 — black-ant, regenerated on the new pipeline

The first outfit built start-to-finish on the one-direction-per-call approach. Fire-ant was where the
method got worked out; this is the test of whether the method actually transfers.

**It is not live.** Everything is in `outfits/blackant-v2/`; the old `outfits/blackant/` is untouched.

---

## Watch this

### `ALL_ANIMATIONS.gif`
All six at once — walks on top, runs underneath, each at its own speed. The individual gifs are here
too if you want one at a time.

### `SIZE_CHECK.png`
The three directions at one scale with their feet on a line, plus fire-ant alongside. This is the
check that the character does not change size when it turns.

---

## What it cost

**Eight calls**, against fire-ant's eighteen.

| | calls | |
|---|---|---|
| turnaround | 1 | three standing views, seeded from the approved design |
| walks | 3 | one per direction |
| walk re-rolls | 3 | **all for SIZE only** — see below |
| gauntlets | 1 | portrait canvas, hands in a column beside the character |

**Nothing was re-rolled for the legs.** That is the result worth having. Fire-ant needed four
re-rolls to fix feet kicking out sideways and both stepping frames lifting the same leg; those fixes
are now in the first-roll prompt, and black-ant's front walk came back correct on the first try —
alternating legs, 9–10px knee lift, feet under the hips. `check_alternation` passed on the first cut
of all three banks.

**The size lottery is the part no prompt fixes.** Three walk calls came back at 66, 75 and 82
pixels against a target of 75, and re-rolling is the only lever — snapping a 66 to a 75 would be a
resample, which is banned. Final: side 75, front 74, back 78, against fire-ant's 77.

Grid detection was the other thing worth testing here, since dark armour has little internal
contrast and the detector runs on edge energy. It **failed** on the turnaround — scores were flat
(9.25, 8.25, 9.50 all within 4%) where a real grid stands out sharply. The pitch had to be chosen by
snapping candidates and comparing. Expect that on any dark set.

## Four bugs this outfit found in the cutter

Fire-ant never hit any of them. All four are fixed in `cut_walk_row.py` and fire-ant re-cuts
byte-identically afterwards (39x77, 26x77, 27x78).

1. **Touching frames.** A long stride put frames 3 and 4 against each other with no clear column
   between. Splitting at empty gaps reported "3 frames" on a render that plainly had four. Now cuts
   at the thinnest column near each expected boundary.
2. **The far fist floated off the body.** The frames were aligned by the HEAD, but the compositor
   hangs the fists off the TORSO centre — and the ant hood juts forward in profile, so head-aligning
   pushed the torso 6px away from where `gait.anchor` measured it. Now aligned on the chest band, the
   same thing `anchor` uses. (Fire-ant's head and torso happened to line up, which is why it never
   showed.)
3. **A speck from the next frame** rode along in every side frame.
4. **The antennae are drawn as DISCONNECTED PIXELS** — a chain of 1–5px blobs. My first fix for (3)
   was a size filter, which deleted the antennae outright and took the figure from 75px to 70px.
   The fix that works keeps whatever is *reachable* from the body rather than whatever is *big*.

## Still open

- Not promoted. `official.py` still points at the old `blackant`.
- The gauntlet shape reference was built from bronze's hands **without normalising their heights**
  first — bronze stores three cut sprites (16x20) beside two full-resolution grips (213x237), so the
  model was shown three small hands next to two huge ones. It coped, but `outfits.reference_strip()`
  exists to normalise exactly this and should be used next time.
