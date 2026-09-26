# Daniel Holden (theorangeduck) — Spring-It-On: The Game Developer's Spring-Roll-Call
https://theorangeduck.com/page/spring-roll-call
Read: 2026-07-29 · animation programmer, Ubisoft La Forge. The reference text on springs in games.

## What it contributes
The mathematical parent for a fully procedural approach — motion with NO authored curve at all.

## Verbatim / formulas
- Exact damper (frame-rate independent):  `x = lerp(x, g, 1.0 - 2^(-dt / halflife))`
- Critically damped spring: `y = damping/2`, `eydt = exp(-(0.693*dt)/halflife)`
- Halflife parameterisation: `damping = (4 * ln(2)) / (halflife + epsilon)`
- Frequency/ratio: `stiffness = (2*pi*frequency)^2`, `damping = ratio * 2 * sqrt(stiffness)`
- damping_ratio scales "from over-damped (>1) through critical (=1) to under-damped (<1)"
- "we can accurately predict the state of the spring at any arbitrary point in the future without having to
  simulate what happens in between"

## Techniques, checkable
1. **Velocity continuity across goal changes.** A spring never pops when the target moves mid-motion. Our
   swing is a fixed 3-segment lerp over a fixed duration — interrupt it (BreakingController re-swings every
   0.36s) and the current code explicitly blends "from the CURRENT pivot angle to kill the snap-pop". That is
   a hand-rolled workaround for exactly what a spring gives free.
2. **One artist-facing knob**: halflife, or frequency + damping ratio. A heavy axe is a lower frequency and a
   higher damping ratio; a light sword is higher frequency, lower ratio — so the overshoot on a light weapon
   emerges from the physics instead of being an authored EaseOutBack.
3. **Under-damped = overshoot for free.** damping_ratio < 1 produces the follow-through overshoot that
   Slynyrd says every stopping object should have, without an easing function per tool.
4. Frame-rate independent by construction.

## Fit with our constraints
This is a genuinely DIFFERENT parent from the authored-curve approach the game currently uses, and it is a
strong candidate for one of the five iterations: drive the pivot angle with a critically-damped-ish spring
toward a moving target angle, and let weight be (frequency, damping_ratio) per tool rather than four
hand-tuned segment tables.

Risk to watch: a spring has no guaranteed contact TIME, and our onContact must fire predictably for the
gameplay hit. Would need an explicit contact trigger rather than "the strike/follow boundary".
