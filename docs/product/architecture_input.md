# Client Input Ownership

How mouse input maps to game actions on the Unity client. One page because this was the
project's repeated bug source: four controllers independently polling `Input` and guessing
whether a click was theirs ("every click near a swarm hand-catches even with a pickaxe").

## The contract

- **UI always wins.** Any click over UI (`EventSystem.IsPointerOverGameObject`) reaches no
  world controller — left AND right click.
- **Left-click is owned by `PlayerInputRouter`** (code-attached to the player by
  `PlayerController.Awake`, like `PlayerToolAnimator` and `MeleeController`). It resolves
  the route ONCE on mouse-down from the equipped tool's `tool_type` and dispatches to
  exactly one controller's `TryHandleClick`:

  | equipped tool_type | owner |
  |---|---|
  | `sword`, `spear` | `MeleeController` |
  | `net` | `CatchingController` (net sweep) |
  | `hoe`, `watering_can`, `scythe` | `ToolUseController` |
  | none / non-tool item | `CatchingController` hand-grab; if **no bug caught**, falls through to `BreakingController` |
  | anything else (pickaxe, axe, shovel, …) | `BreakingController` |

- **Hold latch:** when Breaking is the resolved owner, the router latches the held button
  to it — calling `HoldBreak()` every held frame until release, then `StopBreaking()` —
  and never re-dispatches mid-hold (hold-to-break preserved; no held-click machine-gun of
  single-fire actions).
- **Controllers do not poll `Input` for clicks.** They expose `TryHandleClick` (and
  Breaking's `HoldBreak`/`StopBreaking`). The hand-catch→breaking fallthrough replaced
  BreakingController's old bug-priority probe; per-controller tool-type guards are gone —
  the router's table is the single source of routing truth.
- **Right-click stays with `PlacementController` (place held placeable) and
  `StationController` (open station menu)** — a different verb family (interact/place), so
  it is deliberately NOT routed. Both have the UI guard. *Known issue (BACKLOG):* both can
  fire on the same right-click when a placeable is held and a station is under the cursor.

## Facing

The player faces the **mouse quadrant** every frame (`PlayerController.UpdateFacingFromMouse`)
— movement does not set facing (press A with the mouse pointing right = run backwards).
Facing is frozen while the cursor is over UI. Facing-only network sends are rate-limited to
the 0.1s movement interval; facing rides the existing `MovementMessage` (zero new netcode).

## Tool swing visuals

`PlayerToolAnimator` (one animator, profile-driven, no per-tool prefabs) animates the
equipped item's display sprite in-hand: **swing** (axe/pickaxe/hoe/shovel/sword), **sweep**
(net/scythe — with a `TrailRenderer` arc trail that traces the exact hit/catch sector),
**stab** (spear), **pour** (watering can). Sorting is owned in code: layer "Occupants",
order = player ± 1 tracked per-frame (the old SmallNet prefab sat on the Default layer and
rendered invisibly behind the ground — that failure class is retired). Arc/duration come
from item data (`arc_degrees`, `swing_time`) with per-`tool_type` defaults.
