# How games keep time passing in places nobody is in, and how they catch a place up

*Research, 2026-10-10. Written for the "catch-up" question in the village-slice plan.*

## Purpose

Bug Farmer has one world clock. A zone that no player is standing in is frozen today (its server loop
does not tick). The decided design (2026-09-26) is that, when someone walks into a frozen zone, the server
first catches that zone up on the time it missed, before the zone is shown: bugs eat, breed and die; crops,
fruit, showers and machines move forward; a few bugs wander in from neighbouring zones. The owner raised a
concern on 2026-10-10: a player builds a fly farm or sows milkweed, spends time in another zone, and on
return finds no growth at all. He wants alternative ways for the catch-up to estimate what happened, one of
them being the server running empty zones itself.

This document collects how shipped games and open-source engines handle the same problem: farms, crops,
machines and timers in places nobody is watching, and how they bring a place up to date when a player
returns. Each entry gives the source (and whether it was read in full), the concrete technique, what it
costs to run, and how it fits our situation. Anything a source did not actually say is marked
"not confirmed".

**Search angles used** (four per topic; the per-topic table is at the end): by technique (timestamp
catch-up, stage-from-age, weather replay, sleeping entities, offline level of detail); by game (each game
named below, through its wiki and forums); by engine feature or code (Luanti `catch_up` / LBM / node timers,
DST `LongUpdate`, CDDA `map::actualize`, Minecraft random ticks and ticking areas, `auto_pause` /
`pause_when_empty`); and by player complaint ("crops don't grow outside the reality bubble", "farm stops
working when I leave", "unloaded chunk time", "Palworld base stops working away from base").

---

## Entries

### 1. Luanti (formerly Minetest): block activation, ABM `catch_up`, LBMs and node timers — CODE STUDIED

**Sources (the code itself, master branch as of 2026-10-10; `blockmodifier.cpp` read as a whole file, the
others function by function — every function named here read in full):**
- `src/serverenvironment.cpp` (2,093 lines) — `ServerEnvironment::activateBlock` and the active-block step loop:
  https://github.com/luanti-org/luanti/blob/master/src/serverenvironment.cpp
- `src/server/blockmodifier.cpp` (542 lines) — the ABM handler and the LBM manager:
  https://github.com/luanti-org/luanti/blob/master/src/server/blockmodifier.cpp
- `src/nodetimer.cpp` (134 lines) and `MapBlock::step` in `src/mapblock.cpp` — the per-node timers.
- `doc/lua_api.md` — the ABM, LBM and `NodeTimerRef` sections.
- Old version for comparison: `src/serverenvironment.cpp` at tag `0.4.17`, and the commit that changed it,
  https://github.com/luanti-org/luanti/commit/5a03b1f5f928e30cb650f9d16bc4fbb866275405 (2017-12-04).
- The farming mods: Minetest Game `mods/farming/api.lua`
  (https://github.com/luanti-org/minetest_game/blob/master/mods/farming/api.lua, the growth part read in
  full) and
  TenPlus1's "Farming Redo" `init.lua` + `statistics.lua` (https://codeberg.org/tenplus1/farming, the growth
  part read in full).
- Issue #13112 "Allow registering, removing and modifying LBMs and ABMs on the fly" with all comments
  (https://github.com/luanti-org/luanti/issues/13112).

**How the world is split.** The map is stored in 16×16×16 "mapblocks". Only blocks within
`active_block_range` (default 4 blocks, i.e. 64 nodes) of a player are *active*. Everything else is frozen:
no Active Block Modifiers, no node timers, no entities move.

**The clock and the timestamp.** The server keeps one game clock (`m_game_time`, in seconds). Every block
stores a timestamp of when it was last active. When a block becomes active again, `activateBlock` computes
the missed time as plain subtraction:

```cpp
u32 dtime_s = 0;
u32 stamp = block->getTimestamp();
if (m_game_time > stamp && stamp != BLOCK_TIMESTAMP_UNDEFINED)
    dtime_s = m_game_time - stamp;
...
block->setTimestampNoChangedFlag(m_game_time);
activateObjects(block, dtime_s);                       // entities get the missed time
m_lbm_mgr.applyLBMs(this, block, stamp, (float)dtime_s); // loading modifiers get it
block->step((float)dtime_s, ...);                       // node timers advance by it
```

There is **no cap** on `dtime_s` anywhere in this path. Three catch-up tools hang off it:

1. **Node timers (the tool that actually works).** A node can own one persistent timer. On activation the
   block's timer list is stepped forward by the whole missed time in one call. Each overdue timer fires
   **once**, and the engine passes the callback the true elapsed time:
   `t.elapsed = t.timeout + (f32)(m_time - i->first);` (`nodetimer.cpp`). So a machine or crop learns "I was
   due 200 s ago, but 3 hours have passed" and can do the arithmetic itself. If the callback returns true
   the timer restarts with the same timeout *from now* — it does not fire again for each missed period.
2. **Loading Block Modifiers (LBMs).** A callback per node type that runs when a block is activated. Since
   5.7.0 the callback receives `dtime_s` ("the in-game time (in seconds) elapsed since the mapblock was last
   active"). With `run_at_every_load = true` it runs at every activation, which makes it a general
   "catch this node up" hook. Cost: one scan of the 4,096 nodes of each block as it activates.
3. **Active Block Modifiers (ABMs) with `catch_up`.** An ABM is a random rule ("each `interval` seconds,
   each matching node has 1-in-`chance` odds of `action`"). The documentation still says: "If true,
   catch-up behavior is enabled: The `chance` value is temporarily reduced when returning to an area to
   simulate time lost by the area being unattended." The handler does this by dividing the odds by the
   number of missed intervals (the result is stored as a whole number, rounded down, and never below
   1-in-1):
   ```cpp
   float intervals = actual_interval / trigger_interval;
   aabm.chance = chance / intervals;
   if (aabm.chance == 0) aabm.chance = 1;
   ```
   **Finding (verified in the code, not stated in any source):** the only place that ever passed the missed
   time into this handler was `activateBlock`, through `ABMHandler abmhandler(m_abms, dtime_s, this, false);`
   (present at tag 0.4.17). That call was removed in commit `5a03b1f5f9` (2017-12-04, "Optionally extend the
   active object in a players camera direction"), whose message gives no reason. Since 5.0 the handler is
   only built with `use_timers = true` from the regular step, where `actual_interval == trigger_interval`,
   so `intervals` is always 1 and **`catch_up` has had no effect on returning to an area for about eight
   years**, while the documentation still promises it. Even when it worked, it was capped hard: at best every
   matching node fired exactly once (chance 1-in-1), so a node that should have advanced five steps advanced
   one.

**How the two farming mods use this.**
- *Minetest Game farming* (`farming.grow_plant(pos, elapsed)`): ignores `elapsed`. Each timer firing grows
  exactly one stage, then restarts a 166–286 s timer; if the soil is dry or the light is wrong at the instant
  of the check it waits another 40–80 s and checks again. So a field left unloaded for a whole game
  week grows **one stage** when the player returns. This is the owner's "came back and nothing grew" case,
  shipped in the reference game.
- *Farming Redo* (`farming.plant_growth_timer`): a real statistical catch-up. It turns the elapsed time into
  an expected number of stages, `lambda = elapsed / STAGE_LENGTH_AVG` (default 200 s), and draws the number of
  stages actually grown from a **Poisson distribution** (the standard "how many random events happened in
  this much time" distribution) capped at the stages left: `growth = statistics.poisson(lambda, max_growth)`.
  If the plant can only grow in daylight, it counts only the daylight part of the elapsed time, worked out
  exactly from the time of day (`day_or_night_time(elapsed, true)`). It jumps the plant straight to the
  resulting stage. One random draw per plant, no stepping.

**Cost.** Tiny: one subtraction per block, one timer callback per overdue machine or crop, one random
draw per plant. The expensive part of Luanti is the opposite — ABMs running every second on every active
node; issue #13112's commenters call ABMs "a major source of bottlenecking" and report lag from an LBM + ABM
season system with five players.

**Fit for Bug Farmer.** Very close to our model. Their mapblock is our zone; their block timestamp is the
"last simulated at" time we would store per zone; their single game clock is our world clock. The lessons:
- Store a "last caught up at" world time per zone and per long-running thing; catch-up = now minus that.
- Give every timed thing (crop, fruit bush, machine, nest) its true elapsed time and let it compute its own
  result in one step, as node timers do — never "fire once and restart", which is Minetest Game's
  one-stage bug.
- For things that happen at random (a bush fruiting, a bug laying eggs), Farming Redo's Poisson draw over
  the elapsed time is the right shape: correct on average, varied, one draw.
- Conditions that change over the day (light, rain) should be integrated over the absence (Farming Redo's
  daylight fraction), not sampled at the instant of return.
- Warning: a catch-up path that nobody exercises rots silently (Luanti's `catch_up`). We need a test that
  leaves a zone for N game days and checks the result.

### 2. Cataclysm: Dark Days Ahead — `map::actualize`, `last_touched`, and monster `on_load` — CODE STUDIED

**Sources (the code read in full for each function named; master branch as of 2026-10-10):**
- `src/map.cpp` (12,368 lines): `map::actualize`, `grow_plant`, `restock_fruits`, `produce_sap`, `rad_scorch`,
  `decay_cosmetic_fields`, `fill_funnels` — https://github.com/CleverRaven/Cataclysm-DDA/blob/master/src/map.cpp
- `src/monster.cpp`: `monster::on_load`, `try_upgrade`, `try_reproduce`, `try_biosignature`,
  `refill_udders` — https://github.com/CleverRaven/Cataclysm-DDA/blob/master/src/monster.cpp
- `src/item_degrade.cpp`: `item::process_temperature_rot` (food going off while away).
- `src/weather.cpp`: `sum_conditions` and `retroactively_fill_from_funnel` (rain collected while away).
- Player thread "Question about reality bubble" (https://discourse.cataclysmdda.org/t/question-about-reality-bubble/21266),
  read in full.

**How the world is split.** Only the "reality bubble" around the player is simulated: 11 × 11 submaps of
12 × 12 tiles, 132 tiles across (the thread's numbers; the submap size `SEEX`/`SEEY` is in the code). Each
submap stores `last_touched`, the game turn it was last simulated; it is set to "now" when the submap is
generated and when it is saved in `map::saven` (`submap_to_save->last_touched = calendar::turn;`), which is
the path taken as it leaves the bubble, and again at the end of `actualize`.

**The catch-up.** When submaps load, `map::actualize` runs once per submap, **after** all of them are loaded
("actualize after loading all submaps to prevent errors with entities at the edges"). It computes
`time_since_last_actualize = calendar::turn - tmpsub->last_touched;` — no cap — and hands that duration
to a set of small, hand-written rules, one per kind of thing. Each rule uses a *different* technique, which
is the useful part:

| Thing | Technique in the code | Cap |
|---|---|---|
| Crops (`grow_plant`) | **Stage is a pure function of age.** The seed item carries its planting time; the target stage is found by walking the stage lengths until the seed's `age()` is reached; then the plant is advanced through every missed stage in a loop (spending fertilizer and spawning "rot spawn" pests once per stage). | None — a crop left for a season comes back fully grown. |
| Fruit bushes and trees (`restock_fruits`) | **Threshold rule.** If the season changed since last time, or a whole season has passed, the harvested plant becomes harvestable again. | Naturally capped (one harvest's worth). |
| Maple sap taps (`produce_sap`) | **Closed-form overlap.** Works out exactly how much of the absence fell inside the sap season (late winter to early spring), then `new_charges = roll_remainder( time_producing / turns_to_produce )`, limited by the container's free space. | Container capacity; a year or more counts as one full season. |
| Rain barrels and funnels (`retroactively_fill_from_funnel`) | **Replay a deterministic history.** Weather at any place and time is a pure function of the world seed (`wgen.get_weather_conditions( location, t, g->get_seed() )`), so the code re-reads what the weather *was* over the absence and sums the rain, with a coarse step for long gaps (1 hour when more than 7 days remain, 1 minute otherwise). | Container capacity. |
| Food rot (`process_temperature_rot`) | **Replay in coarse chunks.** "This code is for items that were left out of reality bubble for long time": walks the absence in 1-hour steps, asking the weather generator for the temperature at each hour, and adds rot per step. Item temperature is only tracked for the last 2 days ("If the time was more than 2 d ago we do not care about item temperature"). | Stops early once the item has rotted away. |
| Radiation burning plants (`rad_scorch`) | **One roll scaled by time:** `x_in_y( rads * rads * time_since_last_actualize, 91_days )`. | One event at most. |
| Smoke, blood and other cosmetic fields (`decay_cosmetic_fields`) | **Accelerated ageing:** adds a random 50–100 % of the absence to the field's age and drops its intensity by whole half-lives. | Down to zero. |

**Animals (`monster::on_load`) — the closest thing to our bugs.** Each creature catches itself up when its
area loads:
- *Growing up* (`try_upgrade`): loops through every missed growth step; the comment says this is so new
  monsters "can 'catch up' with all that half-life upgrades they'd get if we were simulating whole world."
  No cap.
- *Breeding* (`try_reproduce`): walks the creature's "next baby" timer forward through every missed birth
  date, checking the season of each one, **but each extra missed birth is less likely than the last**:
  "add a decreasing chance of additional spawns when 'catching up' an existing animal" — the odds are 1 in
  1, then 1 in 3, 1 in 5, and so on (`chance += 2; ... one_in( chance )`). On top of that, each time the
  area loads a coin flip (`bool female = one_in( 2 );`) decides whether this animal gives birth at all during
  that catch-up. Together these are a deliberate brake so a pen left for a year does not explode.
- *Droppings* (`try_biosignature`): one item per missed interval, capped at 50 — "don't catch up too much,
  otherwise on some scenarios, we could have years worth of poop just deposited on the floor."
- *Milk* (`refill_udders`): full again if more than a day has passed.
- *Mood and health*: anger and morale relax towards normal in proportion to the time away; hit points
  regenerate at a per-turn rate times the time away (`heal_amount = roll_remainder( regen * to_turns<int>( dt ) )`);
  special-attack cooldowns count down by the time away.
- Not confirmed: whether these animals also *eat* (or starve) for the time away. Nothing in `on_load`
  charges food for the absence.

**Player-visible behaviour.** The thread confirms the experience players have: crops and young animals do
not change while you are away, and jump to the right stage when you come back.

**Cost.** Proportional to what is in the loaded submaps, not to the length of the absence — except the
replay rules (rot, rain), which cost one weather lookup per hour of absence per item, and are therefore
the expensive ones. The coarse step for long gaps exists to bound that.

**Fit for Bug Farmer.** The strongest single model for us, because it shows that one game mixes several
catch-up techniques, each matched to the thing it updates:
- *Crops and fruit*: store the planting time and compute the stage from age (`stage = f(now − planted)`).
  Then "nothing grew" is impossible by construction, whatever the zone was doing. Our milkweed and fly-farm
  feeders should work this way.
- *Rain-dependent things* (our showers): if our weather is a pure function of world time and a seed, a
  returning zone can re-read the weather it missed instead of guessing. If it is not, it should be made so.
- *Breeding*: CDDA's damped catch-up (each missed birth less likely) is a cheap guard against runaway
  growth when the estimate is crude. For us the real answer is a proper population model at the group
  level (see later entries), but the brake is worth keeping as a safety cap.
- *Warning for us*: CDDA charges no food for the absence, so its animals breed without eating. Our bugs'
  food, hunger and starvation are central, so we cannot copy that shortcut.

### 3. Don't Starve Together — entity sleep, `LongUpdate(dt)`, and the always-on world layer — SCRIPTS STUDIED

**Sources.** Klei ships the game's Lua scripts with the game; I read them from a public mirror that tracks
the shipped files (https://github.com/penguin0616/dst_gamescripts, last updated 2024-11-18):
- `components/growable.lua` — **read in full** (365 lines). The growth-stage component used by spider dens,
  trees, farm plants and more.
- `components/childspawner.lua` — `OnUpdate`, `LongUpdate`, the queued off-screen spawn (the nest/den
  component that holds and regrows creatures).
- `components/pickable.lua` — `LongUpdate` (berry bushes, grass, saplings regrowing).
- `components/timer.lua` — `LongUpdate`. `entityscript.lua` — `EntityScript:LongUpdate`. `update.lua` — the
  global `LongUpdate(dt, ignore_player)`.
- `components/farming_manager.lua` — the world-wide soil moisture grid and its `LongUpdate`.
- `prefabs/spiderden.lua` — the den's growth stages and the Spider Queen rule.
- The wiki's "Spider Den/DST" page (https://dontstarve.wiki.gg/wiki/Spider_Den/DST), read in full in three
  parts (the last part is navigation only).
- The dedicated-server setting `pause_when_empty`: Klei's own settings guide on its forum refused the fetch
  (HTTP 403); I read the server host low.ms's configuration page in full instead
  (https://low.ms/knowledgebase/dont-starve-together-server-configuration).

**Sleep and wake.** Entities far from every player are "asleep": they stop thinking and moving. The growth
component handles this explicitly (`growable.lua`):
- On sleep, unless the thing is marked `growoffscreen`, it **cancels its growth timer** and writes down
  when it fell asleep (`self.sleeptime = GetTime()`). Sleeping plants therefore cost nothing at all.
- On wake, it computes the time slept (`dt = GetTime() - self.sleeptime`) and calls `LongUpdate(dt)`, which
  **walks the stages one at a time** until the time is used up:
  ```lua
  while dt > 0 and self.inst:IsValid() and self:IsGrowing() do
      local timeleft = self.targettime - GetTime()
      if (timeleft - dt) > 0 then
          self:StartGrowingTask(timeleft - dt); dt = 0
      else
          dt = dt - timeleft
          local grew = self:DoGrowth(true)   -- true = skip the per-stage "grew" effects
  ```
  The per-stage visual and sound effects are skipped during the walk and the final stage's effect is played
  once at the end — catch-up without a burst of noise.
- **The "at most one stage" rule (not confirmed as a current rule).** The wiki page does not mention it. In
  the current code it survives only as the fallback path in `OnEntityWake` ("Fallback to the old code"):
  if there is no recorded sleep time and the target time has passed, it calls `DoGrowth()` **once**. So the
  old behaviour was: a thing that slept past its timer grew exactly one stage on wake. The current
  behaviour catches up every missed stage.
- **Nests catch up by at most one creature per big time skip.** `ChildSpawner:LongUpdate(dt)` simply calls
  `OnUpdate(dt)` once; `OnUpdate` subtracts `dt` from the regrow countdown and, if it went below zero, regrows
  **one** child and restarts the countdown. A den that missed ten regrow periods gets one spider back.
  (While merely asleep, the den's periodic task appears to keep running — `OnUpdate` itself checks
  `CanSpawnOffscreenOrAwake()`, which only makes sense if it runs while asleep — so regrowth continues; what
  stops is the *release* of creatures into the world, which is queued with `QueueSpawnChild()` until the den
  wakes. That the scheduler runs tasks for sleeping entities is inferred from the code, not confirmed.)
- **Regrowing plants** (`Pickable:LongUpdate`): subtract the time from the countdown; if it passed, become
  pickable. A natural cap of one harvest.
- **Plain timers** (`Timer:LongUpdate`): every named timer's time left is reduced by `dt`.
- **The dramatic event waits for a witness.** A tier-3 den becomes a Spider Queen only when a player is near:
  `if not inst:IsNearPlayer(30) then ... RescheduleGrowth(... 60 + math.random(60))`. The wiki states it as
  "the player has been nearby for 60 to 120 seconds."

**The global `LongUpdate`.** `update.lua` has one function that advances every entity by a duration —
its comment: "this is for advancing the sim long periods of time (to skip nights, come back from caves,
etc)". `EntityScript:LongUpdate` passes it to every component that has a `LongUpdate`. So in Klei's design,
catch-up is **a contract every component must implement**, and the same contract serves sleeping, cave
travel and skipped nights.

**The always-on world layer.** Farm soil moisture is *not* kept on the farm entities. It lives in one
world-wide grid (`_moisturegrid`) owned by the world, refreshed every `SOIL_MOISTURE_UPDATE_TIME` seconds for
every farm tile whether or not anyone is near, from the current rain rate, temperature and the plants'
drinking rates. A few numbers per tile, ticked for the whole world; the heavy entities sleep.

**Pause when empty.** The dedicated server's `pause_when_empty` "Freezes the simulation when nobody's
online"; low.ms gives its default as `false` (keep running). Not confirmed from Klei's own guide (blocked).

**Cost.** Asleep entities cost nothing; waking costs one loop per missed stage per entity (a handful).
The world moisture grid costs one small update per farm tile every few seconds.

**Fit for Bug Farmer.**
- `LongUpdate(dt)` as a **required interface** is the cleanest structure for our catch-up: every server
  system that changes over time (crops, fruit, showers, machines, nests, swarm life cycle) implements
  "advance yourself by `dt` of world time", and the zone catch-up calls them all. Making it a contract is
  what stops one system silently doing nothing (the owner's fear).
- Klei's nest catch-up (one creature per skip) is exactly the kind of quiet cap that produces "I came back
  and nothing happened". If we cap anything, the cap should be stated, chosen, and tested — not an
  accident of calling `OnUpdate` once.
- "The dramatic event waits for a witness" is worth copying for our ecology director: a species collapse,
  a reseed or a cull should not be decided off-screen in a way the player never sees the cause of.
- The always-on world grid suggests a middle path between "frozen" and "fully simulated": keep a tiny
  summary of each empty zone (population per species per area, food stock, soil water) ticking on the
  server at a slow rate, while the per-bug simulation stays asleep.

### 4. Stardew Valley — every location updated, cheap state only; the host owns time

**Sources.**
- The game is not open source. I read a **decompiled** copy of version 1.5 that modders use as reference
  (https://github.com/veywrn/StardewValley): `Game1.cs` — the per-frame location loop (lines ~6095–6170), the
  ten-minute clock tick (~6290–6312) and the new-day sequence `_newDayAfterFade` (~8109–8800);
  `GameLocation.cs` — `performTenMinuteUpdate`, `DayUpdate`, `updateEvenIfFarmerIsntHere`,
  `cleanupForVacancy`; `TerrainFeatures/HoeDirt.cs` — `dayUpdate`; `Object.cs` — `minutesElapsed` (machines).
  Decompiled names and structure can differ from the real source and from version 1.6 (not confirmed for 1.6).
- The wiki's "Multiplayer" page (https://stardewvalleywiki.com/Multiplayer), read in full.

**Technique: there is no frozen place, because the frozen-able part is tiny.** The world is a few dozen
hand-made maps. Each frame, the game splits every location's update into two parts (`Game1.cs`):
```csharp
bool shouldUpdate = location.farmers.Any();   // (or someone is remotely viewing it)
if (shouldUpdate) location.UpdateWhenCurrentLocation(time);   // the expensive, visible part
location.updateEvenIfFarmerIsntHere(time);                     // the cheap part, always
```
And on the clock:
- **Every 10 game minutes, every location** (`foreach (GameLocation location in locations)
  gameLocation.performTenMinuteUpdate(timeOfDay)`): each machine counts down
  (`minutesUntilReady.Value -= minutes`, done only on the host: `if (Game1.IsMasterGame)`), NPCs follow their
  schedules.
- **Every night, on the host, every location**: machines are given the overnight minutes in one call
  (`n.passTimeForObjects(overnightMinutesElapsed)`), then `location.DayUpdate(dayOfMonth)` runs, which calls
  `dayUpdate` on every terrain feature; a hoed tile calls `crop.newDay(...)` (the day's growth step;
  `Crop.newDay` itself was not read), destroys most outdoor crops when the season is winter, and dries the
  soil (`state.Value = 0`, unless a water-retaining fertilizer or a paddy keeps it wet).
- When the last player leaves a location, the host runs `cleanupForVacancy()` (collects essential dropped
  items). The per-frame `UpdateWhenCurrentLocation` is skipped for empty locations, while
  `updateEvenIfFarmerIsntHere` keeps moving NPCs (`updateCharacters`) and temporary sprites everywhere.

So crops in the greenhouse or on Ginger Island grow whether or not anyone visits — the state is a day
counter and a "watered" flag, and the update is one call per crop per night. (Crops still need water each
day; sprinklers and rain are how players leave them unattended — the sprinkler code was not read, so the
exact timing is not confirmed.)

**The host rule.** The wiki: "If the host isn't online or the farm isn't currently open to other players,
then farmhands can't access the world or their characters in that world." There is no shared clock that
runs without the host: the world's time exists only while the host's game runs. Time passes during menus
and shops, and pauses for a few listed cases (profession choice at the end of a day, festivals with main
events, the host's `/pause`, and menus or cutscenes after 2 AM).

**Cost.** A few dozen locations × a few hundred objects, ticked every 10 game minutes and once per night.
Trivial — which is why it can afford to update everything.

**Fit for Bug Farmer.**
- The split "visible part only where players are, cheap part everywhere" is the key idea. Our crops,
  fruit, feeders, showers and machines are Stardew-sized state (countdowns and counters). **They do not need
  a catch-up at all — the server can tick them in every zone on the world clock**, even frozen ones, for
  almost no cost. That alone removes the "milkweed did not grow" failure.
- Stardew has no wild population, so it is no guide for our bugs. Its farm animals live in buildings and
  update per day (not studied here).
- Its "time only exists while the host plays" model is what our decided world clock replaces; it is a
  warning against tying time to one player. Players' own answer (a server-host guide, read in full:
  https://www.gameserverkings.com/knowledge-base/stardew-valley/stardew-valley-multiplayer/) is a headless
  copy of the game run as a permanent host, with a mod that plays the host's part — "sleeping at night,
  clicks through the end-of-day screens and cutscenes ... so the days keep moving for everyone else" — and
  another that "pauses the game when nobody is online". That is our decided rule, rebuilt by players.

### 5. Minecraft (Java and Bedrock) — random ticks only where loaded; unloaded means frozen; the workarounds

**Sources (each read in full):**
- Minecraft Wiki, "Tick" — https://minecraft.wiki/w/Tick
- Minecraft Wiki, "Chunk" (load levels, tickets, spawn chunks, Bedrock simulation distance) — https://minecraft.wiki/w/Chunk
- Minecraft Wiki, "Commands/tickingarea" (Bedrock) — https://minecraft.wiki/w/Commands/tickingarea
- The "EverCrops" mod page (a player-made fix) — https://www.curseforge.com/minecraft/mc-mods/evercrops
- Player complaint angle: Mojang's feedback site refused the fetch (HTTP 403); the complaint is instead
  documented by the mod pages and the Vintage Story thread in entry 6.

**Technique: no catch-up at all.** Growth in Minecraft is driven by *random ticks*: every game tick, each
16×16×16 sub-chunk in a ticking chunk picks a few random blocks ("defaults to 3" per sub-chunk in Java,
set by the `random_tick_speed` game rule) and gives them a tick; a crop that is picked may advance (the
per-crop growth odds were not part of the pages read).
Only chunks in the "entity ticking" state get this — in Java "This primarily includes chunks in the
simulation distance, but chunks loaded through other methods are also random-ticked"; in Bedrock "all
chunks inside simulation distance (or specified in the /tickingarea command) are ticked on every game
tick." Everywhere else: "Unloaded chunks are unprocessed by the game and do not process any of the game
aspects." There is no timestamp and no catch-up: a farm the player is not near simply does not exist in
time. (Mob spawning and lightning additionally need "a player within 8 chunks.")

**The workarounds players and Mojang built:**
- *Spawn chunks* (Java): an area around world spawn that stayed loaded and ticking with nobody there —
  the classic place for always-on farms. In 1.20.5 the radius became a game rule "decreased to 2 (from 10)";
  in 1.21.9 spawn chunks were removed "altogether". (So farms built there stopped ticking; how players
  reacted is not covered by the pages read.)
- *`/forceload`* (Java): "Forced tickets ... have no timeout, are persisted, load and simulate chunks."
- *Portal and ender-pearl tickets*: an entity passing through a portal loads the target chunks for 15
  seconds ("a timeout of 15 seconds, is persisted"). Players use this to build "chunk loader" machines that
  keep pushing an item through a portal so a farm stays loaded (the machines are well known but are not
  described on the pages read — not confirmed here).
- *Ticking areas* (Bedrock): "Up to 10 ticking areas can be defined at one time", each at most 100 chunks;
  inside them "all game aspects are active".
- *Simulation distance* (both editions): a setting for how far from each player chunks tick; raising it
  keeps more farms alive, and the ticking area — so the cost — grows with the square of the distance
  (simple arithmetic, not stated on the pages).
- *Mods that add a catch-up* — EverCrops: crops are "stamp[ed] with the current game time", and "on the next
  random tick after the chunk reloads" the mod works out "how much game time has elapsed" so that "Walk
  away for an hour, a day, a week — when you come back and the chunk reloads, your crops advance as if they
  had been ticking the whole time." Its stated motivation: "vanilla crops only tick when their chunk is
  loaded". The page does not say whether the catch-up is capped or how light and water are handled
  (not confirmed).

**Cost.** Random ticks are cheap per chunk but are paid every tick for every loaded chunk, so the
workarounds trade CPU for liveness — which is why Bedrock caps ticking areas at 10 × 100 chunks and why
servers limit simulation distance.

**Fit for Bug Farmer.** Minecraft is the counterexample: it is exactly the "I came back and nothing grew"
experience, made tolerable only because players learned to build farms near where they stand, and to
build chunk loaders. The community's own fix (EverCrops) is the timestamp catch-up — the same technique
Luanti and CDDA use. Lessons:
- Never leave a player-made farm without *some* way to move forward when nobody is near.
- A chosen, limited "always ticking" area (Bedrock ticking areas) is a legitimate design: for us, a zone
  holding a player's farm could keep a cheap server tick, while wild-only zones are caught up on arrival.
- Removing an always-on area that players relied on (spawn chunks) breaks their builds; decide early.

### 6. Vintage Story — farmland "fast-forward" with a climate replay and a one-year cap — CODE STUDIED (bonus)

Found through the player-complaint angle ("unloaded chunk time"); its farming code is open source.

**Sources.**
- The game's survival-mod code (https://github.com/anegostudios/vssurvivalmod, master as of 2026-10-10):
  `BlockEntity/BlockEntityFastForwardGrowth.cs` — **read in full** (216 lines); `BlockEntity/BEFarmland.cs` —
  the growth callback read in full; `BlockEntity/BESoilNutrition.cs` — the moisture and fertility callback.
- Forum thread "Unloaded chunk time" (https://www.vintagestory.at/forums/topic/13219-unloaded-chunk-time/),
  read in full.

**Technique: a timestamp, then a replay in coarse random steps over a known climate.** Each farmland block
stores `totalHoursLastUpdate`. While loaded, a server timer calls `Update` every 4.5 seconds; if fewer than
3–4 game hours have passed it exits early. Otherwise it fast-forwards in steps of 3–4 game hours
(`hourIntervall = 3 + rand.NextDouble()`), and for each step:
- asks the world for the **climate at that past date** — temperature and rainfall at this position —
  (`GetClimateAt(Pos, conds, EnumGetClimateMode.ForSuppliedDate_TemperatureRainfallOnly, totalHoursLastUpdate / hoursPerDay)`);
  the climate is computable for any date, so nothing has to be recorded while the place is unloaded;
- rolls whether growth was paused by cold (`growthChance = 1 + (conds.Temperature - delayGrowthBelowTemperature) * lossPerDegree`);
- updates soil moisture from rain and nearby water, soil nutrients, and cold or heat damage to the crop;
- advances the crop a stage if its due time has passed and the soil was moist enough.
Light is measured once at the start and applied as a slow-down factor for the whole replay.

**The cap:** "Don't fast-forward for more than the past year" — anything older than one in-game year is
skipped:
```csharp
if (hoursSinceLastUpdate > world.Calendar.DaysPerYear * hoursPerDay) {
    totalHoursLastUpdate += hoursSinceLastUpdate - oneYear;    // Skip the excess time, doing nothing
    hoursSinceLastUpdate = oneYear;
}
```

**What players report (the thread).** The catch-up works for farmland — one player has "gone on multi-day
adventures away from my base and come back to find my crops have grown appropriately" — but is
**inconsistent across features**: querns and pulverizers stop while unloaded, tree taps and bee skeps were
reported not to progress, while bees *do* swarm into skeps; wild crops were reported to advance "at a
geologically slow pace ... took over 1 year in game to advance just ONE stage." The original poster asks
for the 7 Days to Die approach: "The server calculates how long it was running" instead of keeping chunks
loaded. (The thread's claims about 7 Days to Die were not checked.)

**Cost.** One loop iteration per 3–4 game hours of absence per farmland block, each with a climate
lookup; bounded by the one-year cap, so at most (days per year × 24) ÷ ~3.5 steps per block (the default
year length was not checked, so no number is given here).

**Fit for Bug Farmer.**
- Same shape as CDDA's rot replay: a replay in coarse steps over a history that can be recomputed
  (climate as a function of date). This is the right tool for things that depend on weather we can
  recompute — our showers and drought, if the ecology director's weather is made a pure function of
  world time and seed rather than a live random decision.
- A hard cap on the absence (one year here) protects the server from a huge replay; but for us, with a
  14-minute day, a long absence could be many in-game years, so a cap must be paired with a good
  "long-run" answer (a settled state) rather than "skip the excess, doing nothing".
- The thread is the clearest warning in this research: **players notice inconsistency more than they
  notice the rule.** Crops that catch up beside a quern that does not feels broken. Every timed thing in
  a zone should follow the same rule.

### 7. Animal Crossing (New Horizons, New Leaf) — the real-time clock and the "you were away" results

**Sources.** Nookipedia "Weed" (https://nookipedia.com/wiki/Weed, read in full, then re-read for the exact
New Horizons paragraph), "Time travel" (https://nookipedia.com/wiki/Time_travel, read in full), "Cockroach"
(https://nookipedia.com/wiki/Cockroach, read in full), "Villager" (read in full; nothing on absence);
the community FAQ "Time Travel" (https://chibisnorlax.github.io/acnhfaq/tt/, read in full) and its "Flower
Breeding" page (read in full); the articles "This is why you shouldn't time travel" (iMore) and "How to
time travel — what happens" (Nintendo Life), both read in full. The fandom wiki's "Flowers/New Horizons
mechanics" and a GameFAQs thread refused the fetch (HTTP 402/403). The game is closed and no datamine of its
day-rollover code was found, so **this is the weakest entry: no code, and the wikis do not say whether
each missed day is processed or only one.**

**Technique: the console's real clock is the world clock; the day rolls over at 5 AM; time away produces a
set of "neglect" results on return.** What the sources say:
- *Weeds* (New Horizons): "one new weed will appear each day"; "If there is 31 or more weeds present, only
  one weed will appear once per day, and if there are 150 or more weeds present in the town, no further
  weeds will spawn." Older games: "two in City Folk and New Leaf and three in prior games", and "If the game
  is not played for a long time, the town will be overrun with weeds." **So weeds are capped (150).**
- *Cockroaches in the house*: Nookipedia says they "appear in the player's houses if neglected for a week or
  more ... Depending on how long the player has been absent, more cockroaches will appear"; the FAQ and
  Nintendo Life say a month or more (the sources disagree — not confirmed which).
- *Bedhead* and villagers commenting "on where you have been" after a month or more (FAQ).
- *Turnips* (a weekly commodity) rot if the player passes the next Sunday 5 AM (FAQ, Time travel page).
- *Rocks and trees refresh; weeds and flowers grow and spread* (FAQ). Whether a ten-day absence produces ten
  days of flower breeding or one is **not confirmed** by any page read. A search summary of the
  unreadable fandom page claimed that time travel removes the "watered" state so flowers do not breed —
  **not confirmed**.
- *Villagers*: in New Horizons villagers "will no longer move out without notice", "requiring the player's
  explicit permission to leave" (Time travel page). In earlier games a villager could leave while the
  player was away (forum guides describe players resetting the date to undo it; the exact rule was not
  found — not confirmed).

**Cost.** Unknown internally; from the outside it is a single rollover computation on launch.

**Fit for Bug Farmer.**
- Animal Crossing shows what a catch-up looks like *as an experience*: the player returns to visible,
  legible consequences of the time away — weeds, roaches, a comment from a neighbour — rather than to an
  exact simulation. For us, the zone a player returns to should *read* as "time passed here": grown crops,
  a changed swarm map, a nest that grew, signs of what happened.
- Its caps (150 weeds) keep neglect from becoming ruin. A bounded downside for absence fits our
  "danger is real but fair" direction.
- Moving the irreversible event (a villager leaving) behind the player's consent in New Horizons is the
  same idea as DST's "the queen waits for a witness": do not make the big loss happen off-screen.

### 8. Dedicated servers: who pauses when empty, who keeps running, and what freezes far from players

**Sources (each read in full unless stated):**
- Factorio: the official `server-settings.example.json` (https://github.com/wube/factorio-data/blob/master/server-settings.example.json);
  the Factorio wiki "Multiplayer" page (https://wiki.factorio.com/Multiplayer); Friday Facts #67
  (https://www.factorio.com/blog/post/fff-67); forum thread "Altering the algorithm of the update cycle"
  with replies from developer Rseding91 (https://forums.factorio.com/viewtopic.php?p=229146).
- Satisfactory: wiki "Dedicated servers" (https://satisfactory.wiki.gg/wiki/Dedicated_servers); a Steam
  discussion on distant factories (https://steamcommunity.com/app/526870/discussions/0/3307213006842541059/).
- Don't Starve Together: see entry 3 (`pause_when_empty`).
- Valheim: the "Away From Home" mod's changelog page (https://thunderstore.io/c/valheim/p/Wubarrk/AwayFromHome/changelog),
  which describes the vanilla code; a Steam discussion on crops while away
  (https://steamcommunity.com/app/892970/discussions/0/3409803709040667486), 14 comments.
- Terraria: wiki "Server" (https://terraria.wiki.gg/wiki/Server) and "Biome spread"
  (https://terraria.wiki.gg/wiki/Biome_spread).
- Palworld: Steam thread on a mining base (https://steamcommunity.com/app/1623730/discussions/0/4139439021822620714,
  first page, 15 of 24 posts) and the palmods.gg article "farm stops producing away from base"
  (https://www.palmods.gg/blog/palworld-farm-stops-producing-away-from-base).

| Game | Empty server | Places far from players (while someone is online) | Catch-up on return |
|---|---|---|---|
| **Factorio** | **Pauses** by default: `"auto_pause": true` — "Whether should the server be paused when no players are present." | **Everything runs**: "All instances of the game run full simulations of the entire world." Made affordable by *sleeping entities* (FFF #67): an inserter with nothing to do "will go to sleep. It will also tell the chest and the transport belt to wake it up when something is moved away from the chest, or new items come on the belt" — "6/7 of inserters are deactivated now, so the overall updates per second is almost doubled." Rseding91: the main cost "is not CPU speed but the amount of RAM that has to be touched each tick." | None needed — nothing is ever frozen except the whole game. |
| **Satisfactory** | Can pause: the server setting "Auto-Pause" — "When the Server should automatically be paused when no players are connected" (default not stated on the page). | A player says "the graphics will just stop rendering, but the mechanics will continue" — no developer confirmation found (**not confirmed**). | None needed if all factories run. |
| **Don't Starve Together** | `pause_when_empty`, default `false` per low.ms (keeps running; not confirmed from Klei). | Far entities sleep; growth timers cancelled (entry 3). | `LongUpdate(dt)` per component on wake. |
| **Valheim** | **Clock freezes**: "Valheim's dedicated server freezes the world clock when nobody is connected. `ZNet.UpdateNetTime` returns early at zero players" (mod author describing vanilla code; **not confirmed** from the game's code). | Zones away from players unload. | **Mixed.** Crops: "unloaded zones have time stamps. So when you revisit the zone, they'll time skip to the present, and the crops will POOF fully grown" (a player). Tamed animals: "it does not work for tamed animals and they'll be frozen in stasis until your return." Smelters: "A vanilla smelter only ever catches up the last hour of production in a single gap; past that, time is genuinely forfeited" (mod author). |
| **Terraria** | **Hibernates**: "When no players are online the server hibernates. Time only passes when players are connected." | **The whole world keeps changing slowly**: "Every game tick, the game chooses a handful of tiles to update ... 'surface' tiles will each average about one update every 140 seconds, while 'underground' tiles each average about one update every 830 seconds" (grass, plants, Corruption spread). | None needed — the world-wide random update never stops while anyone is on. |
| **Palworld** | The server process stays up, but "workers can remain unspawned or fail to resume after the last player leaves" (palmods.gg). | **Bases freeze**: "the base's worker simulation has entered an inactive state after its world cell unloaded." A player: "Bases go into stasis when players are not around. The only work around is buy another account to baby sit them." Another: pals "struggle to mine ore rocks when unloaded." | **None.** On return "the cell loads, reconstructs the workers, and restarts their task loops"; the time away is simply lost. No official statement found. |

**Cost.** Factorio and Terraria pay continuously for the whole world (Factorio with heavy optimisation —
sleeping entities, data laid out for memory speed — because its world is entirely player-built machines).
Valheim and Palworld pay nothing for empty places and give players nothing back (or a capped hour).

**Fit for Bug Farmer.**
- Our decided rule — "the world stops only when nobody is online" — is the Factorio/Valheim/Terraria
  default. That part is well trodden.
- **Palworld is the cautionary tale for the owner's exact worry.** Its farms freeze when the player
  leaves, there is no catch-up, and the community answer is "buy another account to baby sit them".
- **Valheim shows the inconsistency trap again** (as Vintage Story did): crops catch up, tamed animals do
  not, smelters catch up one hour at most. A player cannot predict which of their things will have moved on.
- **Factorio's sleeping entities** are the model for a server that *does* simulate empty zones: most things
  in a quiet zone are waiting (a full feeder, a nest at capacity, a bush with ripe fruit). Put them to sleep
  and have the event that matters wake them, so an always-on zone costs little.
- **Terraria's slow world-wide random update** (one update per tile every couple of minutes) is a cheap
  way to keep slow change going everywhere — a direct analogue of running the group-level bug model on
  empty zones at a low rate.

### 9. S.T.A.L.K.E.R. — A-Life's "online" and "offline" simulation; and what went wrong in S.T.A.L.K.E.R. 2

Added because it is the shipped game closest to our bug question: a population that keeps living, at a
coarser level, where the player is not.

**Sources (each read in full):**
- "Interview: Inside the AI of S.T.A.L.K.E.R." with Dmitriy Iassenev, the A-Life programmer
  (https://www.gamedeveloper.com/pc/interview-inside-the-ai-of-i-s-t-a-l-k-e-r-i-).
- GamingBolt, "S.T.A.L.K.E.R. 2: Heart of Chornobyl's A-Life 2.0 Isn't Working – Here's Why"
  (https://gamingbolt.com/s-t-a-l-k-e-r-2-heart-of-chornobyls-a-life-2-0-isnt-working-heres-why).

**Technique: two levels of detail for the same creatures.** Near the player (within "a predefined radius
from the player (can vary from level to level, but usually it is about 150 meters)") characters are
*online*: full animation, paths, combat. Everywhere else they are *offline*, and keep living at a coarse
level: "the character does not play animations or sounds, does not manage his inventory actively, does not
build detailed and smooth paths (although he does build paths according to the global navigation graph
...)". Offline fights are resolved by formula: "the opponents took turn making moves, the result calculated
based on a formula and the random factor." The system "follows the player's and offline characters'
movements, and switches the latter to online/offline as necessary."

**The counterexample (S.T.A.L.K.E.R. 2, 2024).** The article reports that "The offline A-Life of the past
games no longer exists. The Director in this game has its own system to manage offline events outside the
'bubble range.' Except this kind of flat out does not work." The live radius was cut to "about 80 meters";
players saw NPCs appearing from nowhere, including behind them. The developers said they had to "limit the
distance around which the system should function to optimize performance" and acknowledged "bugs with AI
behavior". Players noticed the *absence* of the off-screen life immediately.

**Cost.** Offline characters cost a graph step and a formula now and then instead of animation, physics
and perception every frame — cheap enough for the original game to keep a whole region's population alive
on 2007 hardware (the interview gives no numbers; not confirmed).

**Fit for Bug Farmer.** This is the "server simulates empty zones itself" option, and it is proven: our
server already owns swarms at the group level (births, ageing, hunger, nests, the ecology director). That
*is* an offline layer. Running it on empty zones at a coarse step — group positions on a coarse grid,
feeding and predation resolved by formula per step, as A-Life resolves offline fights — keeps one world
with no catch-up guess at all; the clients' per-bug lockstep simulation remains the "online" layer. The
S.T.A.L.K.E.R. 2 story is the warning: replacing the off-screen life with a director that spawns things near
the player is noticed, and resented.

### 10. "Alibi generation" (Sunshine-Hill and Badler, 2010) — make the arrival state a fair sample

**Source:** B. Sunshine-Hill and N. Badler, "Perceptually Realistic Behavior through Alibi Generation",
Proceedings of AIIDE 2010, pp. 83–88 (https://ojs.aaai.org/index.php/AIIDE/article/view/12389). Read in
full (the text extracted from the PDF; some equations came out garbled, all prose read).

**Technique.** For a large pedestrian population, do not simulate unseen agents at all; instead, when an
area comes into view, **sample its contents from the steady-state distribution of the full model**:
"An individual agent from among the entire population of the world will have a particular steady-state
probability of being on a given segment when that segment's tile comes into view ... The number of agents
present on a segment when it comes into view, therefore, can be modeled as a binomial process" (or Poisson
for large populations). Details are generated only when needed, and must agree with everything the player
has already seen: "any alibi must be an independent, fair sample from the conditional distribution of
possible alibis given observed behavior." Two further rules matter to us:
- "Cells which pass entirely out of view must continue to be simulated for a short time, or a return to the
  cell may produce obvious discrepancies. The cell must continue to be simulated for at least as long as it
  takes for the set of agents in the cell to change entirely" — or be frozen and "advanc[ed] at once only if
  and when the cell comes back into view" (citing Sung, Gleicher and Chenney 2004).
- The related-work section records industry practice: *Neverwinter Nights* froze or used "large
  time-steps" for out-of-view agents; *Grand Theft Auto IV*-style random walks give "populations which
  appear realistic in the aggregate, but individual agents act unrealistically over time."

**Cost.** In their test (20,000 agents, about 400 destinations): about 52 kB of precomputed tables;
"Sampling the population of all segments in a cell took less than 0.1 ms"; an alibi took about 9 ms and can
be spread over many frames.

**Fit for Bug Farmer.** This gives the principled answer for **long** absences. After a long time, an
ecosystem "forgets" its starting point; the honest estimate of the swarms in a zone is a sample from the
zone's long-run distribution, conditioned on what is fixed (the player's farm, pens, plants, nests, season).
We can learn that distribution offline by running our own group-level model on the zone for many game days
(we already have the headless ecology harness), store a compact summary per zone, and sample from it on
arrival. Short absences, where the player remembers what they left, need a real catch-up (entries 2, 3, 6,
9); the paper's own rule — keep simulating a left area for at least its turnover time, or freeze and
advance it — says where the line between "short" and "long" lies: roughly how long it takes the zone's
swarms to turn over.

---

## Source table

| # | Source | Technique | Cost to run | Fit for us |
|---|---|---|---|---|
| 1 | Luanti engine code (`activateBlock`, node timers, LBMs, ABM `catch_up`) | Per-block timestamp; missed time = now − stamp, uncapped; node timers fire once with the true elapsed time; LBMs get `dtime_s`; ABM `catch_up` divides the odds (dead since 2017) | Tiny per block | High — same shape as a per-zone "last caught up" time |
| 1b | Minetest Game farming (`grow_plant`) | Ignores elapsed time: one stage per return | Tiny | Anti-pattern — the owner's exact fear, shipped |
| 1c | Farming Redo (`plant_growth_timer`) | Poisson draw of stages from elapsed ÷ mean stage time; daylight-only time worked out exactly | One random draw per plant | High for crops, fruit, egg-laying |
| 2 | Cataclysm DDA (`map::actualize`, `monster::on_load`, rot, funnels) | Per-submap `last_touched`; a different rule per thing: stage-from-age, threshold, closed-form overlap, replay over a seeded weather history, damped breeding, capped droppings | Per thing loaded; replays cost one weather lookup per hour of absence | Highest — the mixed toolbox we need |
| 3 | Don't Starve Together scripts (`growable`, `childspawner`, `pickable`, `timer`, `farming_manager`) | Sleep cancels timers; `LongUpdate(dt)` contract on every component; nests regrow one creature per skip; queen waits for a witness; world-wide soil grid always ticks | Zero while asleep; a loop per stage on wake | High — the interface; warns about accidental one-step caps |
| 4 | Stardew Valley (decompiled 1.5; wiki) | Every location gets the cheap updates (10-minute machine tick, nightly crop day); visible part only where players are; host owns time | Trivial (small world) | High for crops/machines: tick them everywhere, no catch-up needed |
| 5 | Minecraft (wiki: Tick, Chunk, tickingarea; EverCrops) | Random ticks only in loaded chunks; unloaded = frozen, no catch-up; workarounds: spawn chunks, forceload, ticking areas (10 × 100 chunks), mods adding timestamp catch-up | CPU per loaded chunk, every tick | Counterexample; ticking areas = "keep farm zones ticking" option |
| 6 | Vintage Story (`BlockEntityFastForwardGrowth`, forum thread) | Timestamp + replay in 3–4 h random steps over a climate computable for any date; one-year cap; inconsistent across features | One step per 3–4 game hours per block | High for weather-driven things; strong warning on inconsistency |
| 7 | Animal Crossing (Nookipedia, FAQ, articles) | Real clock; on return, legible neglect results (weeds capped at 150, roaches, comments); irreversible losses need consent (NH) | Not known | Medium — the *experience* of returning; caps on neglect |
| 8 | Dedicated servers: Factorio, Satisfactory, DST, Valheim, Terraria, Palworld | Pause when empty (Factorio default, Valheim, Terraria; DST optional); whole world always simulated (Factorio, with sleeping entities; Terraria with slow random tile updates); Valheim mixed catch-up; Palworld freezes bases with none | From zero (frozen) to the whole world every tick | Our empty-world rule is standard; Palworld = the owner's fear; Factorio/Terraria = how to afford always-on |
| 9 | S.T.A.L.K.E.R. A-Life (Iassenev interview; S.T.A.L.K.E.R. 2 report) | Online/offline levels of detail for the same creatures; offline fights by formula; S.T.A.L.K.E.R. 2 dropped offline life and players noticed | Cheap offline steps | High — our server's group-level swarm model *is* an offline layer |
| 10 | Alibi generation (AIIDE 2010 paper) | On arrival, sample contents from the full model's steady state, consistent with what the player already saw; keep a left area simulated for its turnover time or freeze-and-advance | < 0.1 ms per area sample, ~52 kB tables | High for long absences: sample a learned long-run state |

---

## The six most useful techniques for Bug Farmer

1. **Tick the cheap things everywhere, all the time (Stardew, DST's soil grid, Factorio's sleeping
   entities).** Crops, fruit, feeders, showers, pens and machines are a few numbers each. The server can
   advance them in every zone on the world clock — frozen zones included — at almost no cost. This removes
   the "milkweed did not grow" failure outright, without any estimate. Where something is waiting (a full
   feeder, a ripe bush), let it sleep until the event that matters wakes it.

2. **Where a thing must be caught up, make its state a function of time, not of ticks (CDDA crops,
   Luanti node timers, Farming Redo).** Store "planted at" / "last fed at" / "next due at" and compute the
   current stage from the elapsed time in one step. A random process gets a single Poisson draw over the
   elapsed time (Farming Redo), with condition-dependent time (daylight, rain) integrated over the
   absence rather than sampled at the moment of return.

3. **Make catch-up a required interface: `advance(dt)` on every time-driven system (DST's
   `LongUpdate`).** The zone catch-up calls every system's advance; a system without one fails a test. This
   is what prevents the Vintage Story / Valheim pattern where crops catch up but the quern, the tamed
   animals or the smelter quietly do not. Include a test that leaves a zone for N game days and checks
   that every kind of thing moved on.

4. **Make the weather a pure function of world time and a seed, and replay it (CDDA funnels and rot,
   Vintage Story climate).** Then a returning zone can re-read the showers and droughts it missed in coarse
   steps instead of guessing — and the ecology director's rain/drought decisions stay consistent with what
   any player in a neighbouring zone saw.

5. **Run the group-level swarm model on empty zones as an "offline" layer (S.T.A.L.K.E.R. A-Life,
   Terraria's slow world-wide update).** Our server already owns births, ageing, hunger, starvation and
   nests per swarm; stepping that model coarsely (for example once per game hour, feeding and predation
   resolved by formula per area) on every zone with a player farm — or on all zones — keeps one honest
   world with no estimate at all. The per-bug lockstep simulation stays on the clients, as now; only the
   group-level life cycle, which the server already owns, runs where nobody is. (Any group-level feeding or
   predation formula added for empty zones must be checked against the project rule that per-bug
   behaviour is client authority: it has to stay a coarse group-level rule, not a server copy of the
   per-bug behaviour.)

6. **For long absences, sample the arrival state from the zone's learned long-run distribution
   (alibi generation), conditioned on what the player left.** Run our own group-level model headless for
   many game days per zone (we have the ecology harness), store a compact summary (species mix, swarm
   counts, sizes, where they sit), and draw from it on arrival, honouring the fixed facts (the player's
   pens, plants, nests, season). Use real catch-up (techniques 2–5) for absences shorter than the zone's
   turnover time, and the learned sample beyond it.

Supporting rules worth adopting with them: **a damped breeding catch-up as a safety cap** (CDDA: each
missed birth less likely than the last); **legible results on return** (Animal Crossing); and **big
irreversible events wait for a witness** (DST's Spider Queen, New Horizons' move-out consent) — the
ecology director's culls and reseeds should not happen invisibly in a zone the player then walks into.

---

## Counterexamples and warnings (things that went badly for players)

- **Palworld:** bases freeze when the player leaves and there is no catch-up; the player answer quoted
  above is "buy another account to baby sit them". This is the owner's fear exactly.
- **Minecraft:** farms do not exist in time unless loaded; the tools for keeping them loaded are commands,
  ticking areas and portal tickets, and Mojang shrank (1.20.5) and then removed (1.21.9) the always-loaded
  spawn chunks. Mods (EverCrops) add the timestamp catch-up that vanilla lacks.
- **Minetest Game farming:** a field left for a week grows *one* stage on return, because the growth
  callback ignores the elapsed time it is handed.
- **Luanti `catch_up`:** a documented catch-up feature that has done nothing on return since a 2017 commit
  removed its only call, with nobody noticing. Untested catch-up rots.
- **Don't Starve Together nests:** `ChildSpawner:LongUpdate` regrows at most one creature per time skip —
  an accidental cap of the same kind.
- **Vintage Story and Valheim:** catch-up applied to some things and not others (querns, tree taps, tamed
  animals, smelters past one hour). Players experience this as broken, and say so.
- **Vintage Story's one-year cap** "skip[s] the excess time, doing nothing"; with our 14-minute day, a long
  absence is many game years, so a naive cap would freeze exactly the farms the owner worries about.
- **S.T.A.L.K.E.R. 2:** replaced off-screen life with a director that spawns near the player; players saw
  creatures appear from nowhere and the developers acknowledged it.
- **CDDA animals breed without eating while away** — a shortcut we cannot copy, since food and starvation
  are central to our bugs.

---

## Search angles used, per topic

| Topic | By technique | By game | By engine feature / code | By player complaint |
|---|---|---|---|---|
| Luanti | node timer `elapsed`, Poisson catch-up | Minetest Game, Farming Redo | `activateBlock`, ABM `catch_up`, LBM `dtime_s`; git history bisected for the removal | "catch_up does nothing" (nothing found); issue #13112 (ABM lag) |
| CDDA | stage-from-age, weather replay, damped breeding | "reality bubble" thread | `map::actualize`, `last_touched`, `monster::on_load` | "crops don't grow outside reality bubble" |
| DST | sleep/wake catch-up | Spider Den wiki | `LongUpdate`, `growable`, `childspawner`, `pause_when_empty` | "one stage while unloaded" (not found on the wiki) |
| Stardew | daily update of all locations | Multiplayer wiki | decompiled `Game1`/`GameLocation` | "farmhands can't play when host offline" |
| Minecraft | timestamp catch-up mods | Tick / Chunk wiki | random ticks, tickets, ticking areas | "farm stops working when I leave" |
| Animal Crossing | time-away processing | Nookipedia, FAQ | (no datamine found) | villagers moving out while away |
| Dedicated servers | sleeping entities, offline LOD | Factorio, Satisfactory, Valheim, Terraria, Palworld, S.T.A.L.K.E.R. | `auto_pause`, `pause_when_empty`, hibernation, A-Life | "base stops working when I leave" (Palworld), "unloaded chunk time" (Vintage Story) |

---

## Quota count

**Pages, papers and threads read in full: 35** (the target was at least 7): Luanti issue #13112 (with all
comments); the CDDA "Question about reality bubble" thread; the DST "Spider Den/DST" wiki page (its last
2,790 characters, navigation only, not read); low.ms DST server configuration; the DST dedicated-server
guide on the wiki (nothing on pausing); the Stardew "Multiplayer" wiki page; the Stardew multiplayer
hosting guide; Minecraft wiki "Tick", "Chunk" and "Commands/tickingarea"; the EverCrops mod page; the
Vintage Story "Unloaded chunk time" thread; Nookipedia "Weed", "Time travel", "Cockroach" and "Villager";
the ACNH FAQ "Time Travel" and "Flower Breeding" pages; the iMore and Nintendo Life articles; the Factorio
"Multiplayer" wiki page; Factorio's `server-settings.example.json`; Friday Facts #67; the Factorio forum
threads on the update cycle and on the entity tier list; the Satisfactory "Dedicated servers" wiki page;
the Satisfactory Steam thread; the Valheim "Away From Home" changelog; the Valheim Steam thread; Terraria
wiki "Server" and "Biome spread"; the palmods.gg article; the S.T.A.L.K.E.R. interview; the S.T.A.L.K.E.R. 2
article; and the alibi-generation paper (prose read in full from extracted text; some equations garbled).
The Palworld Steam thread was read for its first page only (15 of 24 posts), so it is not counted.

**Code read:** whole files — Luanti `src/server/blockmodifier.cpp`, DST `components/growable.lua`, Vintage
Story `BlockEntity/BlockEntityFastForwardGrowth.cs`. Function by function (every function named in the
entries read in full) — the rest of the files listed below.

**Codebases studied: 5** (the target was at least 2):
1. Luanti — https://github.com/luanti-org/luanti: `src/serverenvironment.cpp`,
   `src/server/blockmodifier.cpp`, `src/nodetimer.cpp`, `src/mapblock.cpp` (`MapBlock::step`),
   `doc/lua_api.md`; plus tag 0.4.17 and commit `5a03b1f5f928e30cb650f9d16bc4fbb866275405`. Games/mods:
   https://github.com/luanti-org/minetest_game (`mods/farming/api.lua`) and
   https://codeberg.org/tenplus1/farming (`init.lua`, `statistics.lua`).
2. Cataclysm: Dark Days Ahead — https://github.com/CleverRaven/Cataclysm-DDA: `src/map.cpp`,
   `src/monster.cpp`, `src/item_degrade.cpp`, `src/weather.cpp`.
3. Don't Starve Together game scripts (shipped Lua, via the mirror
   https://github.com/penguin0616/dst_gamescripts): `components/growable.lua`, `components/childspawner.lua`,
   `components/pickable.lua`, `components/timer.lua`, `components/farming_manager.lua`, `entityscript.lua`,
   `update.lua`, `prefabs/spiderden.lua`.
4. Vintage Story survival mod — https://github.com/anegostudios/vssurvivalmod:
   `BlockEntity/BlockEntityFastForwardGrowth.cs`, `BlockEntity/BEFarmland.cs`, `BlockEntity/BESoilNutrition.cs`.
5. Stardew Valley 1.5, decompiled (not open source; modders' reference) — https://github.com/veywrn/StardewValley:
   `StardewValley/Game1.cs`, `StardewValley/GameLocation.cs`, `StardewValley/TerrainFeatures/HoeDirt.cs`,
   `StardewValley/Object.cs`.

**Not reached:** Klei's own dedicated-server guide (HTTP 403), Mojang's feedback site (403), the fandom
"Flowers/New Horizons mechanics" page (402), a GameFAQs thread (403). Claims that depended on them are
marked "not confirmed" above.
