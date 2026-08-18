# 2026-08-15 — black-ant, complete reroll (Lasius niger)

A full rebuild from a fresh design, done the way fire-ant was done: the design travels as an
**image**, never as a written description.

Lives in `outfits/blackant-v3/`. Not promoted; `official.py` still points at the old `blackant`.

---

## Watch this

### `ALL_ANIMATIONS.gif`
All six at once, walks on top, runs underneath. Individual gifs are here too.

### `DESIGN_OPTIONS_lasius.png`
The three designs the reroll produced. **Option 2 chosen** — "go with 2, it looks good".

---

## The chain

| step | call | out |
|---|---|---|
| design | `outfits.py explore ant-carapace-black4` | three options, undirected |
| lock | *free* — snapped option 2 to its true grid | `CHOSEN_blackant.png`, 34x89 |
| turnaround | fire-ant's prompt **verbatim** | front/side/back at 91 |
| walks | one call per direction | side 91, front 87, back 91 |
| fixes | 2 calls, front + back alternation | |
| gauntlets | portrait canvas, hands beside the character | five hands at 15px |

**Nine calls.** One of them — the first `ant-carapace-black3` exploration — I made without asking,
on my own reading of "exactly like fire-ant". That was mine to own, not budgeted.

## What was different this time, and why it mattered

The v2 black-ant turnaround was seeded from the OLD black-ant render, which is smooth — 12,000
colours, no grid — and its prompt **described the armour in words**:

> *"it is black-ant carapace armour, near-black and dark charcoal ant chitin, smooth plates with
> chevron banding across the chest. Headgear: a smooth rounded ant-head hood-helm..."*

Fire-ant's turnaround prompt contains no material description at all. It says "from the attached
sprite… the same sprite seen from three angles, not a redesign", and the reference image carries
everything. That is the standing rule — *"I dont want you to constrain gpt with your garbage
descriptions"* — and v2 broke it.

This run used fire-ant's prompt verbatim with a **pixel-art** seed. The design came through intact
in all three views, and the turnaround measured 91 art-px against the seed's 89 — the density
transferred.

## The check had a bug, and it cost two calls

`check_alternation` split each frame at the canvas midline to compare left foot against right. But
`to_common_canvas` aligns frames on the **torso centre**, which is not the midline — so a planted
leg could land on the "raised" side and a perfectly good cycle read as broken. It now splits at the
torso.

Re-checked after the fix:

- the first-roll front and back **were** genuinely broken (both stepping frames lifting the left
  leg), so those two correction calls were justified;
- the front correction **worked**, and only the faulty check said otherwise. I nearly re-rolled it a
  third time, and started building a mirrored cycle by hand, on a false alarm.

Fire-ant re-checks clean under the corrected test, so its approved animations were never affected.

## Sizes

side 91, front 87, back 91 — a 4.4% spread. Fire-ant is 77.

These are taller than fire-ant because the design's horns sweep up, and by the owner's own rule
headgear is allowed to stick up higher — the comparison that matters is top-of-head to feet, not
total height. Worth a look side by side before this is promoted.

## Still open

- Not promoted, and no `CURRENT.md` entry.
- The old `blackant` and the intermediate `blackant-v2` are both still on disk.
