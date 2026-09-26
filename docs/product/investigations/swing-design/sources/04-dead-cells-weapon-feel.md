# Dead Cells — designing 50 weapons to feel distinctive (Game Developer)
https://www.gamedeveloper.com/design/designing-each-of-the-50-weapons-in-i-dead-cells-i-to-feel-distinctive
Read: 2026-07-29 · Motion Twin. 2D action game with dozens of weapons — our exact problem

## What it contributes
That perceived weight comes from PAUSES, not from speed, and that fighting-game feedback tech is the source.

## Verbatim
- Feedback is "particles, stop frames, slow downs" borrowed from Street Fighter 4 / BlazBlue / Mark of the
  Wolves.
- "critical hits freeze the game for one frame, followed by a slow down of a few tenths of a second"
- On making a sword feel heavy: "if when you did the backswing on this sword, pause for a second" — a pause
  in the animation "created the impression of mass and power."
- "if they all play in the same way, it's not really providing any difference."

## Techniques, checkable
1. **Freeze ONE frame, then SLOW DOWN for a few tenths.** That is a two-stage impact: a hard 1-frame stop
   followed by a time-scale dip. We have neither. This is more nuanced than a flat hit-pause.
2. **Weight is sold by a PAUSE IN THE BACKSWING**, not by a slower overall swing. Ours differentiates heavy
   tools by longer duration (axe 0.34s vs sword 0.20s), which is the blunter instrument. A hold at the top of
   the wind-up would read as heavy even at the same total duration.
3. The whole set must not play the same way — the differentiation is the product, not a polish item.

## Fit with our constraints
Both techniques are free and procedural:
- a 1-frame global freeze + a short time-scale dip on contact;
- a hold at the TOP of the wind-up (we only hold at impact, and only for Chop).
Combined, these give four visibly different tools without touching any art.

## Caveat
Dead Cells renders 3D models down to pixels, so their per-frame poses are not reproducible for us. Only the
TIMING lessons transfer; the art-production ones do not.
