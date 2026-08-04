# 2026-08-04 — the five tools, rebuilt around what each tool DOES

Ten gifs, two per tool. `ALL_<tool>.png` per tool; `FILMSTRIP_shovel.png` and `FILMSTRIP_spear.png`
show every frame of the two that were most wrong.

## The correction

> *"you arent thinking of the tools right - you are treating them all like swords you swing in different
> ways, more thought should be going into each of these, do you sit there bashing the ground with a
> shovel? do you?"*

No. They were five arcs with different constants. Each tool has a **verb**, and the verb decides which
channel carries the motion — angle, or reach.

| tool | verb | what actually moves |
|---|---|---|
| **axe** | CHOP | a big arc that **bites and STOPS**. A real axe does not follow through past the wood |
| **hoe** | TILL | chop in, then **DRAG back** toward you. The drag is the working stroke, not the chop |
| **net** | CATCH | sweep **hoop-first**, then **LIFT to enclose** — it does not pass through and keep going |
| **shovel** | DIG | **thrust the blade in**, then swing up **just a little**, then return. Reach does the digging; the lift is a small angular change at the end and the blade never leaves the ground line |
| **spear** | THRUST | cocked back at the body, then driven forward. **Reach is the entire motion** |

**Reach shrinking while the tool stays low IS the drag and the lever. Reach growing with a still angle IS
the thrust.** Rotation is the wrong channel for both, which is why they read as waving the thing around.

## The spear

**It is now 1.9× a cell instead of 1.0** — asked for three separate times and never applied, because I
kept adjusting the motion and never looked at the sprite scale. It also starts properly cocked back:
the hand begins 0.15 cells from the shoulder and drives to 0.98.

`B_deep_cock` starts further back again (0.06) and drives past a full cell.
