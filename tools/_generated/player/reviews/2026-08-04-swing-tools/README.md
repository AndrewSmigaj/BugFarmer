# 2026-08-04 — the five tools, rebuilt around what each tool DOES

Ten gifs, two per tool. `ALL_<tool>.png` per tool; `FILMSTRIP_shovel.png` and `FILMSTRIP_spear.png`
show every frame of the two that were most wrong.

## The correction

> Owner direction (2026-08-04): every tool was being handled as a sword swung a different way. Each
> needs its own motion — no one digs by hammering a shovel into the ground.

They were, in fact, five arcs with different constants. Each tool has a **verb**, and the verb decides which
channel carries the motion — angle, or reach.

| tool | verb | what actually moves |
|---|---|---|
| **axe** | CHOP | a big arc that **bites and STOPS**. A real axe does not follow through past the wood |
| **hoe** | TILL | chop in, then **DRAG back** toward you. The drag is the working stroke, not the chop |
| **net** | CATCH | **starts low, ends low**, hoop-first and angled up. You scoop a bug off the ground — your hand does not finish beside your face |
| **shovel** | DIG | held **low at the waist**, two hands at two points on the shaft. Drive the blade into the block beside him, then **LEVER** — the low hand barely moves while the blade rotates. Not a battering ram, and not held up by his face |
| **spear** | THRUST | cocked back, driven forward, **aimed below horizontal** so the hands sit at chest/waist rather than shoulder height. Reach is the entire motion |

**Reach shrinking while the tool stays low IS the drag and the lever. Reach growing with a still angle IS
the thrust.** Rotation is the wrong channel for both, which is why they read as waving the thing around.

## The spear

**It is now 1.9× a cell instead of 1.0** — asked for three separate times and never applied, because I
kept adjusting the motion and never looked at the sprite scale. It also starts properly cocked back:
the hand begins 0.15 cells from the shoulder and drives to 0.98.

`B_deep_cock` starts further back again (0.06) and drives past a full cell.


## Where the hands actually are (measured, not eyeballed)

The sprite's width profile: helmet to ~22% down, shoulders ~30%, waist ~50%, legs below 65%. The shoulder
pivot sits at **30%** — correctly on the shoulder line.

| | hand travels |
|---|---|
| spear | 32%-47% down the body — chest to waist |
| net | 48%-57% — low, and it ends low |
| shovel | 42%-69% — down to the ground |

The bug was never the pivot. It was **aiming horizontally from it**, which parks the hands at shoulder
height — up by his head. Thrusts and scoops aim below horizontal.

Every gif now **holds at rest** for 4 frames before looping, so you can tell which direction it runs.
