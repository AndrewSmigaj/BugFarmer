# Weather & World Environment Architecture

Status: **v1 IMPLEMENTED** (rain-only, one-shot watering). The deferred v2 (per-cell
deterministic rain) is designed at the bottom.

## The frontier rule (why this system is simple)

NOTHING in weather or time-of-day feeds the deterministic bug simulation. The client
sim's inputs stay seed + influence ledger + food registry. Weather's gameplay effect
lands exclusively through EXISTING server-side watering paths, and time-of-day is pure
display derived from the already-synced tick. That's what lets v1 ship with two small
messages and zero replay surface.

## Time of day

```
t = ((SimulationTick + DayOffsetTicks) % 8400) / 8400      // both sides, identically
```

- One day = `DayLengthTicks` = 8400 ticks = 14 min. t=0 is MORNING.
- `DayOffsetTicks` exists for the debug set-time (F8): the raw tick NEVER jumps; only
  the apparent time shifts, on every client identically (WorldEnv broadcast).
- **Day rollover is an EPOCH COMPARE** (`WorldState.AdvanceDayIfNeeded`): the apparent
  day index is compared to `LastRolloverDay`, NOT `tick % 8400 == 0` — a forward
  set-time crossing the boundary would silently skip a modulo rollover (losing the
  daily watering resets and the rain roll). Backward jumps re-fire; everything the
  rollover does is idempotent-class.
- Daily-cap stamps (`crop.WateringsToday`, `tree.LastWaterDay`) use the APPARENT day
  index; tree watering gates on `LastWaterDay == currentDay` (equality, not >=) so a
  backward jump can never wedge watering. `LastWaterDay` inits to -1 (0 would read as
  "already watered on day 0").

## Wire (display-only)

| Op | Dir | Name | Payload |
|---|---|---|---|
| 90 | C→S | DebugWorld | {set_time_ticks: -1/0..8399, weather: ""/"rain"/"stop", spawn_species, spawn_count, spawn_x, spawn_y} — dev tool (F8 panel), ungated + loudly logged (the OpCode-87 convention) |
| 91 | S→C | WorldEnv | {day_offset_ticks, weather, weather_until_tick} — broadcast on every change AND sent per-joiner right after WorldInit |

Clients apply the `weather` field ON RECEIPT ("" = stop immediately);
`weather_until_tick` (SimulationTick domain) is only the missed-stop fallback.

## Rain v1 (handlers_env.go)

- **Scheduler**: at each day rollover, 30% chance of ONE shower at a random raw tick
  within the next day-length; duration 1500-3000 ticks (2.5-5 min). The scheduled tick
  is RAW (monotonic) and compared with `>=` — a set-time shifts only the apparent hour
  the shower lands at, never skips it.
- **At rain START — one-shot watering** (`rainWaterAll`): every crop +1 water within
  its daily cap (wet-tile + crop broadcasts, the handleWatering pattern); every fruit
  tree +1 tank level via `waterTree(manual=false)` — no daily stamp, silent clamp.
  This is the WILD-TREE RESTOCK PATH: untended trees re-fruit only through showers
  (~1 batch / ~10 game-days at 30% — a deliberate tuning knob).
- **At until-tick (or F8 Stop)**: clear + broadcast 91.
- **Client visuals** (`RainController`, created by DayNightController; ☔ on the clock):
  - **Parallax streak layers** (data-driven `LayerSpec` presets) + a **splash/impact layer**
    (ripples scattered across the camera view) + **gusting wind** (streak `vel.x` breathes).
  - Two intensities via `RainController.Intensity` (`Light` = one gentle layer, default "normal";
    `Heavy` = intense base + a darker-drops layer + denser splashes). A CLIENT toggle today (F8);
    the seam for server/zone-driven weather later. Server weather stays the single "rain" state.
  - **Ambient overcast**: while `Raining`, the single global light dims ×0.85 AND shifts cooler/
    desaturated (in `DayNightController`).
  - **Lightning (Heavy only)**: `DayNightController.LightningFlash` (additive over-bright + blue-
    white tint on the global light, decayed in `Update`) + delayed `AudioFx.Thunder()` (synth, no
    asset). `RainController` orchestrates random strikes; F8 has a manual "Strike" button.
  - **GOTCHA**: all three particle `velocityOverLifetime` curves MUST share a mode (TwoConstants) —
    a bare-float `z` (Constant) throws "curves must be in the same mode" and emits nothing (this
    silently broke rain). Future weather (fog = layered scrolling noise; dust = horizontal sheet —
    see BACKLOG) are SEPARATE self-activating components, not branches in `RainController`.

## Day/night display (DayNightController)

- **EXACTLY ONE global Light2D — the contract that makes night dark.** URP 2D accumulates
  every global light into the Multiply blend texture, so a *second* global at full intensity
  pins the world bright and the night ramp does nothing. `DayNightController.Start` enforces
  this with an **adopt-one** pattern: take the first existing global Light2D, **disable every
  other global**, create one only if none exist (never leave zero — lit sprites with no global
  render pure black). HISTORY: `SampleScene` shipped a static `Global Light 2D` at intensity 1
  that no code touched; alongside the controller's ramped light it kept the world at full
  brightness → "night is identical to day, and *brightest* in deep night" (additive lamps were
  the only thing changing). Two prior fixes failed by brightening point-lights instead of
  finding this. **Do not add a second global light.**
- Curve: day 0-0.42 → smoothstep golden dusk 0.42-0.58 → DEEP night floor (default ~0.20,
  ×cool-blue `nightColor` → ~5-10%/channel, genuinely dark) 0.58-0.88 → smoothstep dawn
  0.88-1.0. The night floor is live-tunable via `DebugNightIntensityOverride` (F8 "Night
  darkness" slider) — the exact level is an aesthetic call made in-editor, not a guess.
- The fruit-fall evening window t∈[0.40,0.62) sits inside the dusk ramp by design.
- Clock UI: `☀/☽/☔ Day N HH:MM`, center-top. F7 = client-only lighting preview.
- **Lighting model = one ramped global (multiply, darkens) + additive point-lights.**
  Local visibility at night comes ONLY from point-lights: a **held** torch/lamp (selected
  hotbar slot whose item has a `world.light` block — the player starts with `torch`), or a
  **placed** torch/lamp occupant (`TilemapManager.RenderOccupant` → `LampLight`). Both fade
  with daylight (`intensity × (1 - Daylight)`), so they're no-ops by day.
- Personal light (`PlayerNightLight`, local player only, all data-driven — no hardcoded ids):
  selected item with a `world.light` block → a radial held-glow at that radius; `tool_type`
  "flashlight" → a mouse-aimed Light2D CONE (radius 8, 30°/70°); **anything else → NO light**
  (Terraria-style: no torch selected and none placed nearby = hard to see). There is no longer
  an always-on base glow. Remote players holding torches do not glow (out of scope). Underground
  full-dark = a zone ambient flag (BACKLOG).

## Deferred v2 — per-cell deterministic rain

(Lifted from the original farming-doc sketch; unchanged in intent.) When rain should
VISIBLY water individual cells: emit a `WEATHER_START {tick, seed, duration}` ledger
event; clients compute which cells get wet per tick via `CounterRng(seed, x, y, tick)`;
the server commits crop water at thresholds. Near-zero bandwidth, replayable. v1's
one-shot was chosen because nothing in the game yet needs per-cell wetness — only the
start/stop moment and the watering effect.
