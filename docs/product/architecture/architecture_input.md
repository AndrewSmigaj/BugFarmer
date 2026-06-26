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

## Right-click ownership + movesets (2026-06)

**Right-click is also router-owned** (the Placement+Station double-fire is RESOLVED). The verb
depends on world context, so it's a priority CHAIN, not a tool table:

| order | owner | consumes when |
|---|---|---|
| 0 | UI guard | pointer over UI |
| 1 | `StationController.TryHandleRightClick` | a station is under the cursor (toggle), **or an open menu was closed by the click** (state transition = consumed — never "close menu AND jab/place") |
| 2 | `PlacementController.TryHandleRightClick` | placing mode is active (equipped placeable OR cursor-place) — **mode-based, not success-based**: a red-ghost misclick consumes; it never falls through to a jab |
| 3 | weapon `secondary` move | the equipped item's `moves` map has a `"secondary"` |

*Footnote:* an out-of-range station click returns false and falls through (may jab/place) — accepted.

**Weapon MOVESETS:** combat stats live per-move in `items.json` `moves: {primary, secondary}`
(kind/damage/arc/reach/swing_time/max_targets/cooldown_ticks). Left-click routes weapons to
`MeleeController.TryHandleClick("primary")`; right-click (chain step 3) to `"secondary"`.
Axes have ONLY a secondary (left-click stays breaking — Stardew-strict). The move's `kind`
("swing"/"stab"/"sweep") picks the animation via `Play`'s kindOverride — a sword jab plays
Stab on a "sword" profile; unknown kinds LogWarning. New weapon kinds (whip) = data + one
AnimKind + one client hit-geometry query; the server validates only move-existence + reach.
Cooldowns share ONE `LastToolTick` server-side (sword↔hoe↔jab throttle each other; closes
alternating-spam + swap bypass); the client mirrors with one shared swing timer.

**Held-at-rest display:** the equipped TOOL's sprite rests in-hand (animator `SetIdleItem`;
restored by the single `RestoreIdle()` after every animation/interrupt — which also turns the
sweep trail off, fixing a latent leak). Local: PlayerController watches inventory events.
Remote: equips ride `EntityData.eq` on the per-tick op11 broadcast (change-sync + joiner
bootstrap in one path); RemoteEntity attaches its own PlayerToolAnimator. Remote SWING replays:
net catches use the catcher's cached eq; melee replays are self-describing from
`MeleeResultMessage.weapon`+`move`. Notes: the remote idle sprite renders at a fixed side
regardless of facing (v1); picking your equipped item onto the drag cursor equips "" — others
see you bare-handed mid-drag.

## Bug release gesture (2026-06)
While the drag cursor holds a **BUG stack**, world clicks are the cursor's verb — checked FIRST
in both router routes: **LEFT = release the whole stack** at the click (deposit-verb parity
with "left places the stack"), **RIGHT = release one**. Mode-based always-consume; a
reach-tinted circle (green/red at 4.0) follows the mouse over the world as the affordance.
Whole-stack sends the CURSOR count (half-pickup remainders stay in the slot). Out-of-reach
clicks consume (the red circle is the feedback). BreakingController now swings on EVERY
attempt (throttled at the break cadence) — swinging at air is visible, Terraria-style; axes'
right-click secondary is a JAB (stab kind).
