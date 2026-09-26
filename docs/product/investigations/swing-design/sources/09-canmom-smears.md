# canmom — Motion blur & smears
https://canmom.art/animation/smears
Read: 2026-07-29 · animation theory, sakuga analysis. The technical treatment of smears.

## What it contributes
Four distinct smear types with different implementation costs — and the rule that makes them work.

## Verbatim
- "Motion blur appears when there is significant motion _in screen space_ (the image plane) over the camera's
  exposure."
- Type 3, overlapping subframes: "like you've taken images at a much higher framerate and layered them over
  each other."
- Type 4, elongated: "Stretching out forms to create a kind of 'motion tube'." An ellipse approximates a
  moving circle.
- **The rule**: "The effect is subconscious. If every frame is smeared out, it instead looks like your
  character is a funny shape." The eye should "snap back to an 'accurate' drawing before long."
- Squash and stretch for impact: "a stretched inbetween before wall impact adds more punch than a gap or a
  stiff inbetween."
- Games at 60fps capture a smaller time window than film at 24fps, so additional blur can be excessive.

## Techniques, checkable
1. **Type 3, overlapping subframes, is free for us.** Draw the tool sprite 2-3 times along the arc it swept
   this frame, at falling alpha. No new art, no distortion — just repeated blits at interpolated angles. This
   is the single most implementable idea in the whole sweep for a rotating-sprite system.
2. **Type 4, the motion tube**, is also reachable: scale the tool along its length on the fastest frames.
3. **One or two frames only**, at peak velocity. Smear every frame and the weapon just looks misshapen.
4. Squash/stretch on the frame BEFORE impact adds punch — pairs with hitstop rather than competing with it.
5. Caution: at 60fps the eye already integrates less; over-smearing is a real risk.

## Fit with our constraints
Subframe smearing suits us better than any hand-drawn approach precisely BECAUSE the tool is a rotated sprite:
we know the exact angle at t and t-1, so we can interpolate and blit intermediate ghosts for free.
It applies to the HAND too, which is also just a rotated sprite.

This is the strongest candidate for an iteration that is purely visual and touches no timing.
