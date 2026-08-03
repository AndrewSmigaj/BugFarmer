# 2026-08-03 — facing direction + walking hands

Andrew reported three things: copper is backwards, a lot of outfits aren't using the profile hands when
facing down, and the hand rotations are wrong in the walk.

**The one that needs a decision is image 1.**

| image | what it shows |
|---|---|
| **1_FRONT_HAND_OPTIONS_pick_one** | **DECISION NEEDED.** The three choices for the hand used when walking toward or away from the camera. Middle = what is live now. |
| 2_front_hand_knuckles_vs_profile | The same three, with the old knuckles version for comparison. |
| 3_all_22_side_facing_audit | Every outfit's side frame. They must all face RIGHT. |
| 4_heads_zoomed_which_way_they_face | The heads, zoomed — the face/visor/brim points the way they face. This is how copper and farmer were caught. |
| 5_result_walk_side_and_front | The result: copper and farmer now face right, hands tilt correctly. |
| 6_hand_tilt_before_after | The rotation fix. Top row = both hands leaning the same way (wrong). Bottom = each hand tilts with its own direction of travel. |
| 7_gauntlet_source_art_the_wrist_stump | Why the profile hand looks like a slab — the source drawing has a squared wrist stump on it. |

## The decision, in image 1

Left = what is live now (gauntlet profile, reads as a slab).
Middle = the same thing re-cut with the pipeline bug fixed — **identical**, which proves the problem is
the drawing, not the cutting.
Right = `APPROVED/hands/h3.png`, a genuinely good profile hand. But it exists **only for bronze, in bronze
colour**, so using it everywhere would put bronze's hands on the wizard.

1. Leave as is — right view, boxy hands, fixed properly by the gauntlet redo
2. Good hand for bronze only — bronze right now, other 21 boxy and inconsistent
3. Back to knuckles until the redo — wrong view, but reads as a hand

Recommended: **1**. It is the view he asked for, it is consistent across all 22, and the gauntlets are
being redone anyway — adding "no wrist or forearm, the hand only" to that prompt fixes it for everyone.

## Fixed already, no decision needed

- **copper and farmer** were facing left, so they walked and swung backwards. Mirrored with
  `flip_side.py`. They were the only two of 22.
- **The two walking hands** were leaning the same way; each now tilts with its own direction of travel.
  The owner-approved WALK/RUN constants were not touched.

> **Do not automate the facing check.** A centroid heuristic was tried and agreed with a careful visual
> read on only 6 of 8 outfits. A detector wrong a quarter of the time would mirror sprites the wrong way,
> silently, across the whole set.
