# Slynyrd — Pixelblog 9: Melee Attacks
https://www.slynyrd.com/blog/2018/9/8/pixelblog-9-melee-attacks
Read in full: 2026-07-29 · pixel-art specific, by a working pixel artist

## What it contributes
The frame-economy argument, and the smear frame as the trick that buys smoothness without frames.

## Verbatim
- "Quick low frame animations may not be super fancy but they always work well for quick responsive gameplay."
- "Typically a smear frame is a non-keyframe that is blurred to emphasize the motion and add expression."
  "Usually a single smear frame can get the job done."
- "Any moving object that is stopping will miss the stop point a bit before eventually stopping. The faster
  the object is moving the greater the overshoot."
- "Hold a pose for a few extra frames to add impact."
- Heavier weapons get "a slower anticipation and recovery" but "smear frames should always be few and fast."

## Techniques, checkable
1. Three phases: anticipation → action/extension → recovery. Same skeleton as our AnimKind cases.
2. **Overshoot on stopping** — and it scales with speed. Our Swing already does this (EaseOutBack); Chop does
   not (EaseOut). That matches "heavy = slower recovery", so the existing split is defensible.
3. **A single smear frame** is enough to sell a fast arc. We have no smear at all — the tool is a rigid
   rotated sprite. This is the biggest cheap win available to us.
4. **Hold on impact** adds weight. Our Chop already holds 28% of its duration. Slynyrd says do it for
   anticipation poses too, which we don't.
5. Excessive frames cause input lag — argues against adding more interpolation for its own sake.

## Fit with our constraints
Smear is a rotating-sprite trick we can do procedurally: a stretched/ghosted copy of the tool on the fastest
frames, no new art. Directly applicable.
