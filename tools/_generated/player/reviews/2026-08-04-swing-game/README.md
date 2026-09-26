# 2026-08-04 — attack swings on a frame budget

Six gifs, nothing else. `FRAME_BUDGET_down.png` shows all 14 frames labelled.

    sword_down_1h / 2h     facing the camera - tip lands PAST HIS FEET
    sword_up_1h   / 2h     facing away       - tip lands ABOVE HIS HEAD
    sword_side_1h / 2h     the side view, same treatment, for comparison

## What changed

> *"the user has to watch the play pull back the sword the swing the sword, its not a video game swing"*

The previous ones spread the motion evenly across the runtime and gave the wind-up a third of it, so you
watch him lift the sword and then watch him lower it. That is a cutscene.

A game attack is shaped differently. Almost all the travel happens in **two or three frames**; the rest
of the time is spent **sitting on the end pose** and recovering.

| frames | | |
|---|---|---|
| **0-1** | ANTICIPATION | a small lift. Not a wind-up you can watch. |
| **2-4** | STRIKE | ~90% of the whole arc, in three frames |
| **5-7** | HOLD | the end pose sits still — **this is what reads as impact** |
| **8-13** | recovery | eases home. Slowest part, nobody is watching it. |

14 frames at 20ms = **0.28s**. The previous version was 0.46s once measured — half a second of committed
animation per swing, which is the "watch him pull it back" problem in numbers rather than in my opinion.

The strike frames draw a short **trail** — the blade at the angles it just passed through — because three
frames of travel is too fast for the eye to read the arc without it.

## Still true from before

The hit pose has to **cover the tile being attacked** — down-screen past his feet, up-screen past his
head. And the arm is offset sideways so the blade comes down beside him rather than through his torso.
