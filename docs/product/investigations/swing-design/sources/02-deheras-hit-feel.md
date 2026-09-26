# Jason de Heras — How 3rd-person melee games communicate game & hit feel
https://www.jasondeheras.com/gamedesign/2021/4/23/how-do-3rd-person-melee-combat-games-communicate-game-and-hit-feel
Read in full: 2026-07-29 · combat designer, God of War

## What it contributes
Hard frame numbers from shipped games, and the insight that hit-pause is a design *choice* about weight, not
a universal.

## Verbatim
- Street Fighter V: "Light/Medium/Hard attacks pause for 8, 12 and 15 frames, respectively."
- "Ryu's jab hits on frame 2 (or 0.03s)."
- Devil May Cry 5 reserves hit pause "only on heavy attacks"; God of War applies it "on every Kratos single
  attack to emphasize a feeling of WEIGHT."
- "Attacks are authored with gameplay CONSTRAINTS (hit timing/attack distance)."
- "Directionality/displacement are key characteristics for selling a hit" — victims "SNAP to a dynamic pose
  for an INSTANT SILHOUETTE change."
- The "ANTICIPATION portion" communicates "attack intent (power, direction)."

## Techniques, checkable
1. **Hit-pause scaled by weight**: 8/12/15 frames light/medium/heavy. At 60fps that is 0.13/0.20/0.25s — which
   is LONGER than our entire sword swing (0.20s). Their pause is a global freeze; ours would have to be
   proportionally much shorter.
2. **Hit-pause as a per-tool identity choice.** DMC5 = heavy only; GoW = always, for weight. We currently have
   an impact HOLD on Chop only — that is the DMC5 stance, and it is a defensible position rather than an
   oversight.
3. **Anticipation carries the read of power and direction** — so a heavy tool wants a *longer, higher*
   wind-up, not merely a slower one. Our Chop winds to half*0.35 vs Swing's half*0.30; that is a 17%
   difference and probably too subtle to read.
4. **Authored to gameplay constraints, not to look pretty** — contact must land at a predictable time. Ours
   fires onContact at the strike/follow boundary, which is the same discipline.

## Fit with our constraints
Hit-stop is FREE for us and we do not have it: we only hold the tool's angle, we never pause the whole scene.
A 2-3 frame global freeze on contact is the single strongest borrowed technique here.
Camera shake already exists (MeleeController passes onContact -> camera shake), so the hook is in place.
