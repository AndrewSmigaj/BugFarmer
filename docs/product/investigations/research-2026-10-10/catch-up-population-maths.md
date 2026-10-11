# Catching a frozen zone up: the maths and the practice (research, 2026-10-10)

**Purpose.** When a player walks into a zone that nobody has been in for a while, the server has to work out what
happened there while it was frozen — the bugs ate, bred and died over minutes to many hours of game time — and it has
to do that *before* the zone is shown, cheaply, and with the same answer on every computer. The owner's concern
(2026-10-10), restated: a farmed swarm (say, of flies) left behind while its farmer plays in another zone must not
be found unchanged on return. This document
collects how other people compute "what happened while you were away": idle games' offline progress, aggregate
population maths in discrete steps (and why big steps break), agent-based versus equation-based models, fitting a
cheap model to a detailed simulation, hybrid models that switch an area between per-individual and per-group
simulation, and doing all of it in integer (fixed-point) arithmetic. Each entry gives the source, what was read, the
concrete technique, what it costs to run, and how it fits Bug Farmer. Anything a source did not actually say is
marked **not confirmed**. Research only: no code, data or other document was changed.

**Our situation, in one paragraph (as the brief states it).** Zones are 512 × 512 cells with ~1,600 wild bugs in a
few hundred swarms (more where players farm). The Go server owns each swarm's life cycle at the group level (births,
ageing, hunger and starvation deaths, nests, an ecology director that reseeds a collapsed species and can trigger
rain, drought or a cull). The players' computers run each bug's movement, feeding and hunting in deterministic
lockstep in fixed-point (integers × 1000) with a counter-based random number generator. An empty zone is frozen. A
game day is ~14 real minutes, so a few real hours away is a dozen or more game days. Fast headless runs of the full
simulation are coming and could be the reference to calibrate a cheap model against.

## Search angles used

Per topic, four kinds of angle: **by technique**, **by game or model**, **by library or tool** (including reading
source code), and **by problem or symptom**. The searches actually run, and what each turned up, are listed under each
topic heading.

---

## Sources, one entry each (appended as read)

### Topic A — Idle and incremental games' offline progress

Angles run: by technique ("The Math of Idle Games" offline; "offline progress … simulate ticks versus calculate
formula"; "offline earnings cap 'while you were away'"); by game (Melvor Idle offline progression, Clicker Heroes,
Egg, Inc.); by tool/code (the GitHub repositories and published scripts of Kittens Game, Antimatter Dimensions,
Cookie Clicker); by problem or symptom ("offline progress … 'welcome back' screen", "idle game offline progress
exploit changing system clock" — the last found the device-clock cheat, which a server-owned world clock like ours
does not have; snippets only, not deep-read).

#### A1. Anthony Pecorella, "The Math of Idle Games", parts I, II and III (Kongregate developer blog, re-posted on Game Developer)

- **Read:** all three parts in full —
  [I](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i),
  [II](https://www.gamedeveloper.com/game-platforms/the-math-of-idle-games-part-ii),
  [III](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-iii).
- **What it says.** Part I: cost of the next generator = `base × growth^owned`; production = `base × owned ×
  multipliers`; closed forms for buying many at once (`cost = b·r^k·(r^n − 1)/(r − 1)`) and for the most you can
  afford (`max = floor(log_r(c(r − 1)/(b·r^k) + 1))`). Part II: "derivative" chains where tier 2 makes tier 1, tier 3
  makes tier 2, and so on; with one top-tier generator the amounts after time `t` are `1, t, t²/2, t³/6 … tⁿ/n!` — a
  closed form for any length of time, approaching `e^t` as tiers are added. Part III: prestige formulas; its only
  mention of time away is that **Egg, Inc. limits players to 2 hours of offline play**, and that the game shaped its
  prestige formula so that the cap would matter less.
- **Not confirmed by these articles:** how any of these games compute offline progress, what they show on return,
  or any general advice on offline caps. The series is about growth curves, not about catch-up.
- **The technique.** Where growth is a known function of time (constant rate, or a chain of constant rates), the
  amount after any time away is computed **in one step from a formula** rather than by stepping. This is exact and
  costs nothing, *because the idle-game economy has no feedback*: nothing runs out, nothing eats anything.
- **Cost to run:** constant (a handful of multiplications), whatever the time away.
- **Fit for us.** Weak as a direct model: bugs have feedback (food runs out, predators eat prey, crowding), so no
  simple polynomial formula holds. Useful in two places: (1) the *closed-form-over-any-time* idea carries over to the
  logistic equation, which also has an exact solution (see topic B); (2) the Egg, Inc. cap is a real precedent for
  **capping how much time away is simulated** and designing the rest of the game so the cap is not felt.

#### A2. Kittens Game source code — its offline progress ("Redshift") — CODE STUDIED

- **Read:** the real source, from the open-source repository
  [nuclear-unicorn/kittensgame](https://github.com/nuclear-unicorn/kittensgame) (master at commit `781e379f`,
  2026-10-10): `js/time.js` (`calculateRedshift`, `applyRedshift`, `gainTemporalFlux`), `js/resources.js`
  (`fastforward`, `enforceLimits`, `getVoidQuantityStatistically`), `js/village.js` (`fastforward`, the kitten
  population `sim.update`, the live starvation code in `update`), `js/calendar.js` (`fastForward`), `js/math.js`
  (whole file), and `res/i18n/en.json` (the messages). Read in full for these functions.
- **How it computes time away.** On load and on every update tick, `calculateRedshift` takes the wall-clock gap since
  the saved timestamp and turns it into game days: `daysOffset = round(delta_ms / 2000)` (a game day is 10 ticks at
  5 ticks per second = 2 real seconds). Gaps under 3 days are ignored ("avoid shift because of UI lags"). The gap is
  **capped at 10 game years** (4,000 days ≈ 2.2 real hours), or 40 years (≈ 8.9 real hours) for late-game players.
  (The code comment still says "limit by 1 year" — the comment is stale; the code is 10/40.) The whole option can be
  switched off ("Enable offline progression"); on mobile it is always on.
- **A formula, not the normal tick.** `applyRedshift` does **not** run the game loop many times. It freezes every
  per-tick rate at its current value and multiplies: each resource gets `perTick × days × ticksPerDay` added in one
  step (`resPool.fastforward`), buildings, workshop, village, space and religion each have their own `fastforward`,
  and then storage limits are re-applied (`enforceLimits`), with limits temporarily relaxed so crafting during the
  jump can consume resources.
- **The population part is the instructive bit.** Live play: if catnip (food) would go below zero this tick, one
  kitten starves (at most one, then a 5-second timeout), and no kitten is born while starving. Offline: the resource
  jump **skips catnip entirely when its rate is negative** (`if (res.perTickCached && (res.name != "catnip" ||
  res.perTickCached >= 0))`), and `village.fastforward` adds kittens at the normal birth rate (`nextKittenProgress +=
  times × kittensPerTick`, whole kittens added, fraction carried over, stopped at the housing cap) **with no
  starvation check at all**. So the offline model is deliberately one-sided: you can gain, you cannot starve.
- **Random events over the gap: expected value, or a loop-or-bell-curve.** Calendar events (star charts, meteors)
  become `round(days × chance)` — the average, no dice. The void resource uses the *average* of its per-day dice roll
  (`getVoidQuantityStatistically`, with a comment that the per-day roll "cannot be used for redshift which requires
  statistical distribution over large number of days"). The crypto price uses `math.loopOrGaussianApproximation`:
  for fewer than 100 trials (or when a bell curve would spill past the possible range, mean ± 5 standard deviations),
  it **loops the real per-day dice**; otherwise it draws **one** number from a normal (bell-curve) distribution with
  the summed mean and variance (`mean × N`, `variance × N`), retrying if it falls outside the possible range. The same
  helper backs `binominalRandomInteger(trials, p)`: "how many of N independent trials succeed", in constant time.
- **The queue variant.** With the build queue on, the jump is cut into pieces at the moment the next queued building
  would become affordable, the building is bought, and the jump continues — a crude **event-driven** catch-up.
- **What the player sees.** One log line: "You have regained {N} days of production and {M} astronomical events",
  plus "You have recharged {S} seconds of temporal flux". No detailed summary screen.
- **Cost to run:** constant per system (independent of time away), plus one short loop per queued purchase.
- **Fit for us.** Four lessons, two good and two warnings.
  (1) *Good:* the loop-or-bell-curve trick is exactly how to roll "how many of these 40 eggs hatch" or "how many of
  these 200 flies die of age over 30 days" in constant time; it collapses to the exact loop when numbers are small,
  which is where a bell curve lies.
  (2) *Good:* cutting the jump at **events** (the next purchase) rather than at fixed steps is the right shape for us
  too — cut at "food runs out", "pen hits its cap", "season changes", "director fires".
  (3) *Warning:* freezing rates for the whole gap is only safe because Kittens' economy has no feedback that matters
  offline — and they had to *remove* the one feedback that does (starvation) to keep it from going wrong. We cannot
  do that: our wild populations are meant to crash sometimes.
  (4) *Warning / design note:* a one-sided offline model (gain but never lose) is a deliberate player-kindness choice
  in a single-player game. For a farmed pen it may be the right call (see the owner's fly-farm worry); for the wild
  ecology it contradicts the decided design.

#### A3. Antimatter Dimensions source code — offline progress by running the real tick, fewer and longer — CODE STUDIED

- **Read:** the real source from [IvarK/AntimatterDimensionsSourceCode](https://github.com/IvarK/AntimatterDimensionsSourceCode)
  (master at commit `5409e320`, 2026-10-10): `src/game.js` (`gameLoop`'s hibernation check, `simulateTime`,
  `afterSimulation`), `src/core/storage/storage.js` (`maxOfflineTicks`, the load path), `src/core/player.js` (the
  defaults), `src/components/modals/AwayProgressModal.vue` (the return screen), and the in-game help text
  "Offline Progress" in `src/core/secret-formula/h2p.js`. Read in full for these parts.
- **The technique: replay the normal game loop with a capped number of longer ticks.** Live play is 20 ticks per
  second (50 ms each). On load, if more than 10 seconds have passed, `simulateTime(seconds)` runs the **same
  `gameLoop`** a limited number of times, each tick covering `remaining time / remaining ticks`. The tick budget is
  the player's setting (default **100,000** ticks), further capped so that no tick is shorter than 33 ms ("this would
  allow offline to exploit tick microstructure") and never above 1,000,000. Under 50 seconds away it uses just 50
  ticks with no progress bar. The real-time gap read in the live loop is clamped to 1 ms … 86,400,000 ms (one day) per
  tick, and a live tick longer than a minute (device slept) is treated as offline time too.
- **The help text states the trade-off plainly:** "The simulation behavior is only somewhat accurate, as the game is
  too mathematically complicated to be run at full accuracy in a reasonable amount of time." With 1,000 ticks over an
  hour, each tick is 3.6 s long; "for most things in the game, this is not an issue … A notable exception is
  autobuyers" — anything that happens *once per tick* now happens far less often. With the black hole (periodic
  speed-ups) it instead splits the gap so each tick holds roughly equal **game** time, noting this is "generally in
  your favor".
- **The player controls the cost.** A progress bar ("Offline Progress Simulation") with **Speed up** (halve the
  remaining ticks, down to 500) and **SKIP** (finish the rest in 10 ticks). It runs asynchronously in batches (60 ms of
  work per frame) so the page stays responsive.
- **What the player sees on return.** If more than 10 minutes were simulated, a "While you were away for {time}:"
  screen lists each tracked resource **before → after**, computed by deep-copying the whole player state before the
  simulation and diffing it after. If nothing changed it says "… Nothing happened." (and awards a secret
  achievement). Entries can be hidden by clicking them.
- **Some currencies are given by formula alongside the replay** (e.g. offline Eternity Points from a recorded best
  rate × time; Infinity Points as `bestIPMsWithoutMaxAll × seconds × 1000 / 2`) — a **hybrid**: replay the
  simulation coarsely, and add closed-form gains for things that would be too expensive or too lossy to replay.
- **Cost to run:** proportional to the tick budget (not to time away once the cap binds); on a phone, 100,000 ticks
  takes noticeable seconds — hence the Speed up / SKIP buttons.
- **Fit for us.** This is the "run our own simulation, coarser" option, and it is the most faithful cheap option in
  spirit: one code path, so the rules can't drift apart. Its documented failure is ours too — anything that fires per
  tick, or depends on short timings, comes out wrong when ticks get long (for us: hunts, nest timers, a predator
  meeting prey). Two ideas transfer directly: **a bound on step length** (AD bounds it from below, 33 ms, to stop
  exploits; for us the bound that matters is a ceiling, so per-tick rolls stay meaningful) and the **before/after diff
  screen** generated mechanically from two state snapshots, which answers the owner's fly-farm worry by *showing* what
  grew. AD makes no claim that its catch-up is reproducible; whether its loop draws unseeded random numbers was not
  checked (**not confirmed**).

#### A4. Cookie Clicker source code — offline earnings, sugar lumps, and a garden that does not catch up — CODE STUDIED

- **Read:** the game's own published scripts, [main.js](https://orteil.dashnet.org/cookieclicker/main.js) (the load
  path's offline block, `Game.loadLumps`, the "Twin Gates of Transcendence" upgrade text) and
  [minigameGarden.js](https://orteil.dashnet.org/cookieclicker/minigameGarden.js) (`M.logic`, the step timer),
  fetched 2026-10-10. Read in full for these parts. (Cookie Clicker is source-visible, not open-source licensed.)
- **Offline earnings = a formula with a penalty and a cap.** On load: `timeOffline = now − lastDate`. Only with an
  upgrade does anything accrue. Then: `amount = (min(t, maxTime) + max(0, t − maxTime) × 0.1) × cookiesPerSecond ×
  percent/100`. Base: **5% of the live rate for the first hour**, then a tenth of that; upgrades raise the percent
  (+10% each for seven angel upgrades, and small extras) and double the full-rate window (seven demon upgrades, each
  ×2, plus 2 days for one more). Active-play boosts ("buffs") are deliberately loaded *after* the offline maths "as we
  do not want them to interfer with offline CpS", and the changelog notes buffs no longer affect offline income.
- **Return screen:** a "Welcome back!" notice built as "You earned N cookies while you were away", followed by
  "(⟨time⟩ at ⟨percent⟩% CpS, plus ⟨time⟩ at ⟨percent ÷ 10⟩%)" — the explanation of *why* the number is what it is
  is part of the message.
- **Timers that matured while away: count whole cycles.** Sugar lumps ripen on a timer; `loadLumps` computes
  `amount = floor(age / overripeAge)` lumps harvested while away, keeps the remainder of the current cycle
  (`lumpT = now − (age − amount × overripeAge)`), and tells the player "You harvested N sugar lumps while you were
  away." This is the exact way to catch up anything periodic: **count the whole periods, carry the remainder.**
- **The garden — a small living system — is NOT caught up.** The garden minigame (plants grow, spread, mutate, die)
  advances on a step timer. `M.logic` runs at most **one** step when `now ≥ nextStep` and then sets
  `nextStep = now + stepT`. So after ten hours away the garden moves forward **a single step**; all the other missed
  steps are simply dropped. (Inference from the code; no in-game text confirming this was read — **not confirmed**
  by a designer statement.)
- **Cost to run:** constant.
- **Fit for us.** (1) The garden is a working example of exactly the owner's fear — a living system that silently
  doesn't progress while you're away — in one of the best-known idle games; it's what we must not do with pens.
  (2) The *count whole cycles, carry the remainder* rule is directly usable for our periodic things (egg-laying
  cooldowns, nest timers, a pen's feeding schedule). (3) The explained return message ("N hours at X%") is a good
  pattern if we ever deliberately run the away-time at reduced accuracy or rate: say so. (4) The penalty-rate design
  (5% of live) is a single-player retention device; it does not fit a shared world clock and the owner's design.

#### A5. Practitioner write-ups on offline progress (three short sources, lower weight)

- **Read in full:**
  (a) an itch.io comment thread under the *Train Metropolis* demo, posts by a player ("bugcat") and the developer
  (Crystalline Green Ltd.), ~2025: [post 1](https://itch.io/post/14654594), [post 3](https://itch.io/post/14758795);
  (b) "Offline Progression in Clicker Heroes" on the official Clicker Heroes blog, 2025-07-06
  ([link](https://blog.clickerheroes.com/?p=1902)) — a player-facing explainer, not a developer post-mortem;
  (c) "Melvor Idle Offline Progression, Explained, and 4 Games Compared", tideward.app, Manu Games LLC, updated
  2026-08 ([link](https://tideward.app/offline-progression/)) — a competing developer's own page (marketing; its
  claims about other games are "checked against each game's own wiki or store page", not linked).
- **Techniques named.**
  1. *Event heap:* keep a queue of scheduled events ordered by when they next happen (a route completes, a batch is
     produced) and jump from event to event until the away time is used up — no frame-by-frame work.
  2. *Average recent income:* log income over recent play and pay "highest average income × time away" (this is the
     owner's suggestion of 2026-10-10 to estimate the outcome from recent population data).
  3. *Run the real logic headless:* separate drawing from game logic so the logic can run "at thousands of ticks per
     second", and accept a minute of waiting for hours away.
  4. *Time away as a spendable resource* ("banked time"): the away time becomes a speed-up the player spends later.
  5. *Run until you hit a wall* (Clicker Heroes, as the blog explains it): offline progress continues until your
     idle damage can no longer beat the next boss — a natural stopping point rather than a clock cap; "there's no
     strict time limit".
  6. *Per-action replay with deterministic seeding* (Tideward, by its own account): replay N = time away ÷ action
     length *actions* (not frames), seeded so the same window gives the same result on every device; 24 hours in
     "about 100–300 milliseconds"; a cap of 24 hours, justified by retention (unlimited time away "trains players to
     skip days") and cost; the return screen is a **timeline** of what happened, including food eaten and deaths.
- **The developer's warning (Train Metropolis), the most useful sentence in this cluster:** the event-heap idea was
  impractical because cities' production can run dry, income depends on saturation, upgrades trigger level-ups —
  the choice becomes "either to replicate the entire business logic of the game for the offline progress" or
  refactor, both bad for maintenance and bug fixes. In other words: **a second, simplified model of a game with
  feedback is a second game to keep in step with the first.**
- **Cost to run:** event heap — proportional to number of events; averaging — constant; headless replay —
  proportional to time away (or to a capped tick budget); banked time — none at load (cost moves to later play).
- **Fit for us.** Event-jumping and per-action replay are the right shapes for our server-side group life cycle
  (births, deaths, nest timers are already events). "Average recent income" fails exactly where our design is
  interesting (crashes, booms, a pen whose food ran out) — see the warnings at the end. "Run until you hit a wall"
  is a useful idea for a pen: grow until food or space binds, then hold. Not confirmed: the Melvor and Idle Clans
  details on the Tideward page (second-hand).

### Topic B — Aggregate population models in discrete time

Angles run: by technique ("positive elementary stable nonstandard finite difference predator-prey", "binomial
leap methods", "symplectic Euler Lotka–Volterra … forward Euler spirals outward"); by model (May's logistic map and
Ricker map, Beverton–Holt); by tool (Gillespie stochastic simulation / tau-leaping); by symptom ("atto-fox problem …
fractions of an animal", "avoiding negative populations in tau-leaping").

#### B1. A. C. Fowler, "Atto-Foxes and Other Minutiae", *Bulletin of Mathematical Biology* 83 (2021)

- **Read:** in full, open access at [PMC8408093](https://pmc.ncbi.nlm.nih.gov/articles/PMC8408093/).
- **What it says.** The "atto-fox" is Mollison's (1991) jibe at rabies models that let infected fox density fall to
  ~10⁻¹⁸ of a fox per km² and then **start a second epidemic from that fraction** once the healthy foxes regrow.
  Fowler shows that a continuous model treats a population as a smooth quantity that can never reach zero, so its
  boom-and-bust cycles survive troughs that would mean extinction in reality: e.g. a delayed-logistic oscillation
  with α = 2.5 bottoms out at ~10⁻³ of carrying capacity, and microbial cycles at 10⁻³² ("yocto-cells"). The
  stochastic (dice-rolling, whole-individuals) logistic model, by contrast, goes extinct with certainty for any
  finite carrying capacity K, on a time scale of roughly `√(πK/2)·e^K` — fast when K is small, astronomically slow
  when K is large. His verdict: "when a continuous model indicates a very small population being maintained for a
  significant time, then in practice the population will become extinct." He calls the obvious fix — **set the
  population to zero below one individual** — ad hoc, and proposes instead that the real world's persistence comes
  from **refuges or reservoirs** (dormant stages, a neighbouring patch that leaks individuals back in). A second
  result: with **egg predation that is quadratic at low density** (a "Holling type III" response, where predators
  barely bother with rare prey), the adult population settles at a level that does not depend on how many eggs are
  laid.
- **The technique(s).** (1) Know that smooth-number models resurrect extinct species; guard with an integer floor or
  an explicit extinction rule. (2) Model persistence as a **reservoir/immigration** term rather than as fractional
  survivors. (3) Use a predation term that weakens when prey are rare (type III) if you want prey to recover rather
  than be hunted to zero.
- **Cost to run:** nothing — these are modelling choices.
- **Fit for us.** Direct. Any aggregate catch-up model we write (fixed-point "flies × 1000") will produce
  milli-flies; a species that should have crashed while the zone was frozen would come back from 0.004 of a fly.
  We already *have* the reservoir Fowler recommends: **the ecology director reseeds a collapsed species**. So the
  catch-up model should (a) round to whole bugs (or keep an integer count with dice for the fraction) and let a
  species hit zero, and (b) hand the recovery to the same reseed rule the live game uses — not to fractional
  survivors. A predation term that softens at low prey density is also a cheap, well-founded way to let populations
  persist through long stretches, as the design intends, without fractional survivors.

#### B2. Robert M. May, "Simple mathematical models with very complicated dynamics", *Nature* 261 (1976)

- **Read:** in full (14-page web transcription of the paper,
  [PDF](https://carretero.sdsu.edu/teaching/M-538/lectures/references/May/May.pdf); same text as
  [NED's HTML copy](https://ned.ipac.caltech.edu/level5/Sept01/May/May_contents.html)).
- **What it says.** For a population counted once per generation, `X(t+1) = F(X(t))`. The "logistic difference
  equation" `X(t+1) = a·X(t)·(1 − X(t))`: dies out for `a < 1`; settles to a steady level for `1 < a < 3`;
  oscillates in 2-, 4-, 8-cycles for `3 < a < 3.57`; looks random ("chaos") from 3.57 to 4; and "if X ever exceeds
  unity, subsequent iterations diverge towards −∞ (which means the population becomes extinct)". The alternative
  `X(t+1) = X(t)·exp[r(1 − X(t))]` (the **Ricker** model) has "the compensating advantage that local stability
  implies global stability for all X > 0" — it **can never go negative**; steady for `r < 2`, cycles to 2.6924,
  chaos beyond; for large r it swings "so low as to be effectively zero, thus producing extinction". Section 8:
  *pairs* of coupled difference equations (predator–prey stepped once per generation) become chaotic with **milder**
  settings than one species alone, while the same two species written as smooth differential equations can only
  settle or cycle — "dynamic trajectories cannot cross each other". Section 5: in practice the chaotic regime is best
  described statistically.
- **What follows for a catch-up step (my derivation from the paper's equations, standard numerical analysis — not
  stated by May).** Take the smooth logistic `dN/dt = r·N·(1 − N/K)` and jump it forward with one simple step of
  length Δt ("forward Euler": new = old + rate × Δt). The result is *exactly* May's logistic map with
  `a = 1 + r·Δt`. So: steps with `r·Δt < 1` approach the carrying capacity smoothly; `1 < r·Δt < 2` overshoot and
  ring; `2 < r·Δt < 2.57` give **fake 2-, 4-, 8-cycles**; up to `r·Δt = 3`, **fake chaos**; beyond 3, collapse
  towards −∞; and any step that starts above `K·(1 + r·Δt)/(r·Δt)` makes the population **negative**. For a
  predator–prey pair the fake behaviour appears with milder settings (section 8). Worked numbers: a species that
  doubles per game day has `r ≈ 0.69`/day, so one-day steps are still smooth; one that grows 4× per day (`r ≈ 1.39`)
  overshoots and rings; 8× per day (`r ≈ 2.08`) gives a fake 2-cycle. Fast breeders plus long steps is the danger.
- **Cost to run:** each step is a few multiplications; cost grows with the number of steps.
- **Fit for us.** This is the core warning for any "just take bigger steps" catch-up: the instability is not a small
  error, it is a different behaviour (cycles and crashes the real game would never produce). The two cures the paper
  points to: (1) use an update that stays positive by construction (the Ricker / exponential form, or the exact
  logistic solution, B3), and (2) keep the step small relative to the fastest growth rate (`r·Δt` well under 1).

#### B3. The exact logistic jump: Beverton–Holt (Wikipedia, "Beverton–Holt model")

- **Read:** in full (a short article), [en.wikipedia.org/wiki/Beverton–Holt_model](https://en.wikipedia.org/wiki/Beverton%E2%80%93Holt_model).
- **What it says.** `n(t+1) = R₀·n(t) / (1 + n(t)/M)`, carrying capacity `K = (R₀ − 1)·M`, closed form
  `n(t) = K·n₀ / (n₀ + (K − n₀)·R₀^(−t))`; it "can be considered as the discrete-time analogue of the
  continuous-time logistic equation", whose solution is `N(t) = K·N(0) / (N(0) + (K − N(0))·e^(−rt))`. The page does
  **not** say whether it is an exact discretisation, and says nothing about stability (**not confirmed** by it).
- **My check (algebra, easy to verify).** Put `R₀ = e^(r·Δt)` and `M = K/(e^(r·Δt) − 1)`; then the Beverton–Holt step
  is *identical* to sampling the smooth logistic solution every Δt. So **one Beverton–Holt step jumps a logistic
  population forward by any length of time exactly**, with no instability, no overshoot, and no negative values
  (the result is a positive number divided by a positive number). Its only cost is computing `e^(r·Δt)`.
- **The technique.** For any single-species pool whose growth is logistic and whose rates are constant over the
  jump (a farmed pen with a fixed feed, a species with steady food), jump it in **one exact step**:
  `N_new = K·N / (N + (K − N)·e^(−r·Δt))`. When rates change (food runs out, season turns), cut the jump at that
  moment and do one exact step per piece — the Kittens Game queue pattern (A2) with an exact solver inside.
- **Cost to run:** constant per piece.
- **Fit for us.** Strong for **pens**: a fed pen is close to a closed logistic system; the exact jump gives, in
  constant time, a farm that has grown while its farmer was away — the outcome the owner's concern is about. In fixed
  point, `e^(−r·Δt)` can come from a lookup table indexed by the step (integers only), or from repeated squaring of a
  per-tick factor (`(1 − p)^n` by squaring) — both deterministic (see topic E). Weak for wild predator–prey webs,
  where the rates themselves change continuously.

#### B4. D. T. Dimitrov & H. V. Kojouharov, "Nonstandard numerical methods for a class of predator-prey models with predator interference" (*Electronic Journal of Differential Equations*, Conference 15, 2007)

- **Read:** in full, [ejde.math.txstate.edu/conf-proc/15/d1](https://ejde.math.txstate.edu/conf-proc/15/d1/dimitrov-tex).
- **What it says.** For prey x and predator y, `dx/dt = x − a·x·y/(1+x+y)`, `dy/dt = e·x·y/(1+x+y) − d·y`.
  Standard methods (Euler, Runge–Kutta) at large steps lose positivity or get the stability of the equilibrium
  wrong. Their "positive and elementary stable nonstandard" (PESN) scheme evaluates each **loss term at the new time
  and each gain term at the old time**, which turns every update into a positive fraction:
  `x_new = (1 + φ)·x / (1 + a·φ·y/(1+x+y))`, `y_new = (1 + e·φ·x/(1+x+y))·y / (1 + φ·d)`, with `φ(h) = h + O(h²)`
  kept between 0 and 1 (e.g. `φ = (1 − e^(−q·h))/q`). Proven: for **any** step size h the solution stays positive
  and the equilibria and their stability match the smooth model. In their example (a = 3, d = 2.25, e = 4) at steps
  1.0, 1.27 and 2.56, Euler diverged, an earlier nonstandard method went negative, Runge–Kutta failed, and PESN
  converged to the right equilibrium (27/5, 16/5).
- **The technique.** "Gains explicit, losses implicit": `N_new = (N + gains·h) / (1 + loss_rate·h)`. One division
  per species per step, positive for any step length, no solver needed. (This is the same idea as "Patankar"
  schemes in chemistry — **not confirmed** from this paper, which does not use that name.)
- **Cost to run:** like Euler — a few multiplications and one division per species per step — but the step can be
  much longer without breaking.
- **Fit for us.** Very good as the update rule inside any aggregate catch-up: prey eaten, starvation and old age
  are "losses", births are "gains". It cannot go negative (no atto-fox from overshoot, though it can still leave
  fractions — combine with B1's integer floor). Caveat: what the paper proves is that *where* the system settles,
  and whether that is stable, match the smooth model; it claims nothing about the *timing* of swings. My inference
  (**not confirmed** by the paper): over long steps a predator–prey cycle's phase and depth will be off — acceptable
  if only the end state is shown and it is plausible, not acceptable if we want the crash to happen on the right day.

#### B5. T. Tian & K. Burrage, "Binomial leap methods for simulating stochastic chemical kinetics", *J. Chem. Phys.* 121 (2004)

- **Read:** in full (9 pages), [PDF copy](https://www.math.pku.edu.cn/teachers/litj/notes/stoch_topics2015/JChemPhys_121_10356_TianBinomial.pdf),
  doi 10.1063/1.1810475.
- **Background in plain words.** Gillespie's exact method ("SSA") simulates a population of whole individuals one
  event at a time (one birth, one death, one meal), with dice choosing which event and when. "Tau-leaping" speeds
  this up by jumping a time τ and asking "how many times did each kind of event happen in that window?", drawn as a
  Poisson random number with mean `rate × τ`. A Poisson number has no upper limit, so with a long τ and a small
  population it can kill more individuals than exist → **negative populations**.
- **What it says.** Draw the number of events from a **binomial** instead: `K ~ Binomial(N, rate·τ/N)` where N is the
  number of individuals that could take part (for "A eats B", `N = min(A, B)`), subject to `rate·τ/N ≤ 1`. A binomial
  draw is always between 0 and N, so populations can never go negative. When one species is used up by two event types
  (e.g. eaten *and* dying of age), first draw the **total** from a binomial bounded by N, then split it between the
  two causes with a second binomial in proportion to their rates. The condition `p ≤ 1` doubles as a built-in limit on
  how long a single leap may be. They compare against the exact one-event-at-a-time method: against Poisson leaping,
  slightly worse on average values but *better* on the spread (variance), and speed-ups over the exact method of **~5×
  to ~62×** on a 4-reaction test, depending on the error setting (Table I), and **~17× to ~70×** on a 22-reaction gene
  system that took 4.5 hours per run exactly (Table III) — where plain Poisson leaping aborted **all 100 runs** on
  negative counts, typically when 2 events were drawn for a species that had only 1 molecule.
- **A related exact fact the paper uses (its equation 18).** For a population of x individuals each dying
  independently at rate c, the number of deaths in a window τ is *exactly* `Binomial(x, 1 − e^(−c·τ))` — so for
  independent, rate-constant losses (old age, a fixed predation risk), **one binomial draw is exact for any τ**.
- **Cost to run:** one or two binomial draws per event type per leap, instead of one random draw per individual event;
  a binomial draw for large N costs about the same as a Poisson draw (they used the BTPE algorithm); at large N a
  bell-curve (normal) approximation is the cheap fallback — exactly Kittens Game's `loopOrGaussianApproximation` (A2).
- **Fit for us.** Strong, and it fits how our server already thinks: swarms are integer counts with births, deaths
  and predation as events. A stochastic aggregate catch-up for a swarm or a species pool can use binomial leaps —
  whole bugs, never negative, extinction possible (which solves Fowler's atto-fox in B1), and noise of the right size
  (so wild populations *fluctuate* as the design wants rather than gliding along a smooth curve). Determinism: the
  draws must come from our counter-based random generator and an integer-only binomial sampler (topic E).

#### B6. John D. Cook, "Symplectic Euler" (blog post, 2020-09-12) — forward Euler on Lotka–Volterra

- **Read:** in full (short post), [johndcook.com/blog/2020/09/12/symplectic-euler](https://www.johndcook.com/blog/2020/09/12/symplectic-euler/).
- **What it says.** For predators u and prey v, `u' = u(v − 2)`, `v' = v(1 − u)`; "the exact solutions are
  periodic" (closed loops). The plain step (explicit Euler, both updated from old values) **spirals outward** at step
  0.08 — each swing bigger than the last, which in a population model means ever deeper crashes. "Symplectic Euler"
  advances one species explicitly and the other implicitly, using the *new* value of the first:
  `v_new = v / (1 + h·(u − 1))`, then `u_new = u + h·u·(v_new − 2)`; this keeps the loops closed, and its solutions
  "hardly change" with finer steps.
- **The technique.** Update the species **one after the other, each using the other's freshly updated value**, and
  write losses as a division (as in B4).
- **Cost to run:** identical to plain Euler.
- **Fit for us.** A cheap fix for the "plain step makes cycles explode" failure if we use a predator–prey pair in an
  aggregate catch-up. Caution (my inference, **not confirmed** by the post): the denominator `1 + h·(u − 1)` can reach
  zero or go negative for long steps when `u < 1`, so this preserves the *shape* of cycles but not positivity for
  every step length — B4's form (losses always in a `1 + positive` denominator) is the safer choice.

### Topic C — Agent-based versus equation-based models

Angles run: by technique ("agent-based modeling vs equation-based modeling"); by model (NetLogo Wolf Sheep
Predation and its System Dynamics and Docked Hybrid twins; Mesa wolf_sheep); by tool (the NetLogo models library on
GitHub, the NetLogo System Dynamics Modeler manual, the Mesa repository); by symptom ("agent-based versus system
dynamics predator prey … small population extinction mean-field differs spatial" — it surfaced Colon et al. 2015,
which could not be fetched because its host's certificate failed verification; not read).

#### C1. NetLogo "Wolf Sheep Predation" — the agent version, the equation version, and the docked hybrid — CODE STUDIED

- **Read:** the three model files from the official models library, [NetLogo/models](https://github.com/NetLogo/models)
  (branch `main` at commit `a83b6f18`, 2026-10-10), code and Info tabs in full:
  `Sample Models/Biology/Wolf Sheep Predation.nlogox` (Wilensky 1997),
  `Sample Models/System Dynamics/Wolf Sheep Predation (System Dynamics).nlogox` (Wilensky 2005),
  `Sample Models/System Dynamics/Wolf Sheep Predation (Docked Hybrid).nlogox` (Wilensky 2005); plus the NetLogo
  manual's [System Dynamics Modeler page](https://docs.netlogo.org/systemdynamics.html).
- **The agent version.** Each tick, every animal turns randomly and steps one patch. Wolves lose 1 energy per step,
  eat **one random sheep on the same patch** (`one-of sheep-here`) for a fixed energy gain, die at energy below 0,
  and reproduce with a fixed probability per tick (parent's energy halved, child placed one step away). In the
  "sheep-wolves-grass" version sheep also lose energy, eat the grass on their patch, and grass regrows after a fixed
  countdown per patch. The Info tab: sheep-and-wolves alone is "ultimately unstable" (one species dies out);
  with grass it is "generally stable" and "a closer match to the classic Lotka Volterra" — but "the classic LV
  models though assume the populations can take on real values, but in small populations these models
  underestimate extinctions and agent-based models such as the ones here, provide more realistic results."
- **The equation version.** Two stocks and four flows, the Lotka–Volterra equations:
  `sheep-births = sheep-birth-rate × sheep` (0.04), `sheep-deaths = sheep × predation-rate × wolves` (0.0003),
  `wolf-births = wolves × predator-efficiency × predation-rate × sheep` (0.8), `wolf-deaths = wolves ×
  wolf-death-rate` (0.15); stocks start at 100 sheep and 30 wolves, **`dt = 0.001`**, and both stocks are marked
  `allowNegative="false"` — i.e. **clamped at zero** ("It doesn't make sense to have negative sheep!", the manual).
  The manual does not name the integration method (**not confirmed** whether Euler or Runge–Kutta).
- **The docked hybrid.** Runs both side by side from the same starting numbers: each agent tick, the equation model
  is stepped `repeat (1 / dt)` times — **1,000 small sub-steps per agent tick** — so that the aggregate model is
  numerically safe. Telling detail: only three settings are shared (initial sheep, initial wolves, sheep birth
  probability); the aggregate model's predation rate, predator efficiency and wolf death rate are **separate
  sliders**, not derived from the agent rules (wolf energy, gain from food, reproduction chance). In this file the
  wolf stock is even left `allowNegative="true"`. Making the two agree is left to the user ("How sensitive is the
  stability of the model to the particular parameters?").
- **The techniques.** (1) *Docking*: run the detailed and the aggregate model from the same start and compare their
  curves — the standard way to check a cheap model against a detailed one. (2) *Many small sub-steps* to keep an
  equation model stable. (3) *Clamp stocks at zero* as the cheap guard against negative counts.
- **Cost to run.** Agent version: proportional to the number of animals (plus patches for grass) per tick. Equation
  version: four multiplications per sub-step, but 1,000 sub-steps per tick here — cheap in absolute terms, and
  needlessly so (an exact or positivity-preserving step, B3/B4, could take far fewer).
- **Fit for us.** Direct analogue: our live game is the agent version (bugs moving, meeting, eating on the client),
  our catch-up would be the equation version. Lessons: (a) the **micro-to-macro rates are not automatic** — even the
  textbook pair keeps them as separate hand-set numbers; for us they must be *fitted* from the headless full
  simulation (topic D); (b) the agent version can go extinct when the equation version cannot (atto-fox again);
  (c) the two can disagree on *stability* itself — sheep and wolves alone collapse in the agent version while the
  Lotka–Volterra twin, solved exactly, cycles forever. A catch-up model calibrated on a stable stretch can miss a crash.

#### C1b. Mesa's `wolf_sheep` example (Python) — a second implementation of the same model — CODE STUDIED

- **Read:** `mesa/examples/advanced/wolf_sheep/model.py` and `agents.py` in full, from
  [projectmesa/mesa](https://github.com/projectmesa/mesa/tree/main/mesa/examples/advanced/wolf_sheep) (`main` at
  commit `5451086f`, 2026-10-10). It calls itself a "Replication of the model found in NetLogo".
- **What differs from NetLogo, and why it matters.** (1) Movement is *behavioural*, not a random walk: sheep move to a
  neighbouring cell **without a wolf**, preferring one with grown grass, and stay put if every neighbour has a wolf;
  wolves move towards cells **with sheep**. So the "same" model has different encounter rates — exactly the kind of
  local behaviour that sets the effective predation rate an aggregate model must be fitted to. (2) Grass regrowth is
  **event-scheduled**: eating a patch calls `schedule_event(self.regrow, after=grass_regrowth_time)` instead of
  counting every patch down every tick (NetLogo's `grow-grass`). Each step activates all sheep, then all wolves, in a
  random order (`shuffle_do`).
- **The technique.** "Do nothing until the next thing happens": store *when* a resource comes back and skip the
  ticks in between.
- **Cost to run:** regrowth costs one scheduled event per eating, not one update per patch per tick.
- **Fit for us.** For catch-up, food sources (plants regrowing, a feeder refilled) are naturally expressed as "ready
  again at time T"; a frozen zone's food state over hours can then be computed exactly without ticking. And a
  warning: two faithful implementations of one textbook model differ in behaviour; calibration constants belong to
  *our* simulation, measured from it, not borrowed from a formula.

#### C2. H. V. D. Parunak, R. Savit & R. L. Riolo, "Agent-Based Modeling vs. Equation-Based Modeling: A Case Study and Users' Guide" (MABS'98, Springer LNAI 1534, 1998)

- **Read:** in full (16 pages), [PDF](https://sites.pitt.edu/~cler/MSCMP3780/abm2.pdf).
- **What it says.** An agent-based model ("ABM") writes down what each *individual* does and lets totals emerge; an
  equation-based model ("EBM", e.g. system dynamics) writes down relations between *totals* ("observables") and
  evaluates them. On their supply-chain case, the equation model reproduced the headline oscillation periods of the
  agent model, but **not** "the memory effect of backlogged orders, transition effects, or the amplification of order
  variation" — things that come from individual decision rules (if-then logic, thresholds) that are hard to write as
  smooth rates; they "were unable to construct a credible" ordering algorithm in the equation tool. Their account of
  **Wilson (1998)**, which compared a predator–prey agent model with equation models: "ignoring local variation in
  dispersal leads to limit cycles rather than the extinction scenarios that dominate ABM's"; to bring the equation
  model into line, Wilson "interrupted [it] at each iteration … to add a random perturbation to the population
  parameter at each location and to zero local population levels that fall below specified thresholds". The general
  cause: equation models average over space and time and "assume homogeneity among individuals"; "when the dynamics
  are nonlinear, local variations from the averages can lead to significant deviations in overall system behavior."
  Their advice: compare the two explicitly on simple cases where the cause of divergence can be traced; ABM fits
  systems "dominated by discrete decisions", EBM fits systems that "can be modeled centrally".
- **The technique(s).** (1) Treat the agent model as the truth and **adjust the equation model until it agrees**
  (Wilson's approach as reported here). (2) Two concrete patches that make a smooth model behave like an agent model:
  **noise per location** and **local extinction below a threshold**. (3) Keep space in the aggregate model where it
  matters (one aggregate per location/patch rather than one per zone).
- **Cost to run:** not quantified in the paper (**not confirmed**); the point is accuracy, not speed.
- **Fit for us.** Our bugs are a textbook "discrete decisions + local interactions" system (a wasp only eats flies it
  meets; a pen is a fenced patch), so a single zone-wide equation will miss things — and our *reason* for a cheap
  model is speed, not insight, so the right posture is Wilson's: **the full simulation is the reference, the cheap
  model is tuned to it**. Practical consequences: aggregate **per swarm or per local area** (a pen, a nest's
  neighbourhood), not per zone; add **per-group noise** (or use the binomial leaps of B5, which give it for free); and
  apply an **extinction floor** per group.

### Topic D — Fitting a cheap model to a detailed one, and hybrids that switch between individual and group level

Angles run: by technique ("surrogate models to analyse agent-based models", "super-individuals … large
populations"); by field (epidemiology: "hybrid epidemic model agent-based equation-based switching"; ecology:
"dynamically changing model representations … individual-based population switching"); by tool (JASSS open-access
papers, the CoMSES model library); by symptom ("switching … information loss", which found Wallentin & Neuwirth).

#### D1. E. Hunter, B. Mac Namee & J. Kelleher, "A Hybrid Agent-Based and Equation Based Model for the Spread of Infectious Diseases", *JASSS* 23(4) 14 (2020)

- **Read:** in full (whole HTML text, ~14,500 words; key passages and Table 2 checked verbatim),
  [jasss.org/23/4/14.html](https://www.jasss.org/23/4/14.html).
- **What it says.** A measles model of an Irish town (~1,000 people) where people move between homes, schools and
  work. The *disease* part switches, **per geographic area**, between agent-based (who meets whom) and simple
  difference equations (`S, E, I, R` updated once per step: `S' = S − β·I·S/N`, `E' = E + β·I·S/N − σ·E`, …), chosen
  "because they are modelled using discrete time space which is more analogous to the agent-based model". The
  switch to equations happens when the share of exposed-or-infected in that area **rises above a threshold**, and
  back to agents when it falls below — because "agent-based models are especially important when a few agents are
  sick". **How the two meet:** the agents never disappear; each step the equations give target counts, and "if the
  rounded difference between E(i+1) and the number of exposed agents in the area is greater than 0, that number of
  susceptible agents … will randomly be selected to move" into the exposed state (and likewise for the other
  states). So individuals are always present; the equations only decide **how many** change state, and **random
  individuals are picked** to make it so.
- **Results.** Time per step (Table 2): pure agents 6.77 ms, pure equations 1.79–1.90 ms, hybrids in between (2.42 ms
  at a 10% threshold per small area … 5.77 ms at 35%). Accuracy: low thresholds gave outbreak sizes and durations
  **significantly different** from the pure agent model; at 35% (small-area switching) or 20% (town switching) the
  distributions were statistically indistinguishable. At county scale, switching erased geography — "there is
  homogeneous mixing for all agents" — and peripheral towns lost their realistic chance of escaping the outbreak.
  Their caution: a richer equation model costs run time, which defeats the purpose.
- **The techniques.** (1) **Switch per local area, by a count threshold**: individuals where numbers are small (or
  where it matters), equations where numbers are large. (2) **Keep the individuals; let the equations set the
  counts; assign the changes to randomly chosen individuals** (rounded differences). (3) Validate the hybrid
  against the pure agent model with distribution tests over many runs, not one.
- **Cost to run:** the hybrid's saving depends on how long the threshold keeps areas in equation mode — here 15–64%
  per step (not the 70× of B5), because only one component switches.
- **Fit for us.** Very close to our shape: the server already keeps *groups* (swarms) as integer counts while the
  per-bug detail lives on the clients. For catch-up, the analogue is "zone frozen → run its swarms at group level with
  fitted rates; zone shown again → the clients re-create per-bug positions inside each swarm". The paper's lessons:
  small groups (a nearly-dead species, a pen with three flies) are where aggregate maths misleads most — keep them on
  the exact/stochastic path; aggregate at a **local** scale; check the result against the full simulation as
  *distributions over many runs*.

#### D2. G. ten Broeke, G. van Voorn, A. Ligtenberg & J. Molenaar, "The Use of Surrogate Models to Analyse Agent-Based Models", *JASSS* 24(2) 3 (2021)

- **Read:** in full (main text, methods, all three case studies, conclusions; appendices skimmed),
  [jasss.org/24/2/3.html](https://www.jasss.org/24/2/3.html), doi 10.18564/jasss.4530.
- **What it says.** A "surrogate" (also "metamodel" or "emulator") is a cheap model *fitted to a detailed model's
  outputs* so that it can stand in for it. Their recipe, in **two stages**: (1) a classifier (support vector machine)
  learns which settings lead to **qualitatively different outcomes — here, extinction versus survival**; (2) a
  regression (support vector regression) predicts the *quantity* (population size) **only within the surviving
  region**. Training data come from runs of the detailed model at settings spread evenly over the space (Latin
  hypercube, 1,000 points to start), then **adaptive sampling** adds runs where the surrogate errs most, in batches of
  20, until it scores ≥ 0.9; a fixed, separate test set of 1,000 runs checks it. Results: a predator–prey equation
  model, survival classified with F1 = 0.96 and population predicted with "coefficient of prognosis" 0.98; a
  spatial resource–consumer agent model, F1 = 0.87 and 0.83 (with 2.9% of the variance being pure run-to-run
  randomness the surrogate cannot capture); a fishery agent model, F1 = 0.95 and 0.95–0.97. Key finding: **the
  settings that decide *whether* a population survives are often different from those that decide *how big* it is
  if it survives** (e.g. the resource-consumer model's growth rate barely affects extinction but dominates size).
  Stated limits: outputs were averaged over the second half of each run (steady behaviour), and "temporal dynamics
  … are not yet covered" — the surrogate predicts an end state, not a trajectory.
- **The technique.** Fit the cheap model to the expensive one in two parts: **"does it crash?"** and **"if not, how
  much?"**; sample the expensive model where the cheap one is wrong; keep an untouched test set.
- **Cost to run.** Training costs thousands of detailed runs (offline, once per balance change); using the surrogate
  is microseconds.
- **Fit for us.** This is the formal version of the owner's suggestion (2026-10-10) to estimate from recent population
  data. Our coming headless full-zone runs are exactly the detailed model to fit against. The two-stage split matters
  for us because the decided design *wants* occasional crashes: a single smooth regression would average crashes away
  and predict a mild dip. Caution: a black-box surrogate is a poor fit for our determinism and our need to explain
  results (a player will want to know why a farm died); the same two-stage idea can be applied to a *mechanistic*
  cheap model (fitted rates in the equations of topic B) rather than a support vector machine. The "end state, not
  trajectory" limit is fine for catch-up (only the end is shown) but not for a return screen that wants a timeline.

#### D3. G. Wallentin & C. Neuwirth, "Dynamic hybrid modelling: Switching between AB and SD designs of a predator-prey model", *Ecological Modelling* 345 (2017) 165–175

- **Read:** in full (all 11 pages of the article), from a [PDF copy hosted by Northwestern's CCL](https://ccl.northwestern.edu/2017/eco.pdf),
  doi 10.1016/j.ecolmodel.2016.11.007; the model code is on CoMSES ([codebase 5254](https://comses.net/codebases/5254/),
  not studied).
- **What it says.** A lake with plankton (grows logistically; carrying capacity 2,300 t) and plankton-eating fish
  (individual agents that flock into schools, need a school to breed, mature at 4 years, die at 6 or of starvation).
  Six designs switch the fish (or the plankton) between representations: individual **agents**; **school-agents**
  ("super-individuals" — one moving agent standing for up to 5,000 fish, with its numbers kept in an internal
  equation model); **spatial stocks** (fish numbers per grid cell, not moving); or one **lake-wide stock**. Switches
  are **triggered by emergence** — "all mature fish belong to a school", or a school reaching 50 fish — and switch
  back when the population falls below **50 fish**. Same parameters everywhere; the results after 100 years differ
  enormously: lake-wide stock 765,046 fish in **0.51 minutes**; agents↔school-agents with spatial plankton 453,872
  fish in **15 minutes** — the most plausible design (the real lake holds ~500,000); fish as fixed spatial stocks only
  75,641 fish in 118 minutes; a pure-agent design ran out of memory after 11 h 42 min at 30 simulated years. "Designs
  that did not account for spatial resource restrictions significantly overestimated fish population numbers by at
  least 45%." "Higher levels of aggregation did not necessarily result in higher computational performance."
- **How individuals are re-created on switching back.** The paper's Table 8 lists what each switch loses. Agents →
  lake-wide stock loses individuality *and* position; on the way back "the location of fish were initialised
  randomly", after which "it took time until fish had clustered again into schools … growth was delayed and the
  probability of a population collapse increased." Ages survived the round trip because the stock was a
  **"conveyor"** (an array of age bins, one per day) rather than a single number. They cite Gray & Wotherspoon (2012)
  for **storing the spatial distribution** at the switch so individuals can be put back where they were — but note
  this works "primarily under stable system conditions". For school-agents, the switch back is "a stochastic
  selection of the remaining fish … from existing schools", which keeps the spatial pattern. Agents ↔ school-agents
  lost the least information.
- **The techniques.** (1) **Super-individuals**: one simulated unit stands for many, carrying its own small equation
  model inside (count, age bins) — and *still moves and interacts in space*. (2) **Emergence-based switching** (switch
  when a stable group has formed; switch back below a count). (3) **Age-binned ("conveyor") stocks** so that ageing
  and maturity delays survive aggregation. (4) **Save the spatial layout** at the switch and restore from it.
- **Cost to run:** see the timings above; the cheapest design (lake-wide stock) ran ~30× faster than the most
  plausible one but ended with ~70% more fish.
- **Fit for us — the closest analogue found.** Our swarms *are* super-individuals: a swarm is one server-side unit
  with a count, and its members are only expanded into individual bugs on the clients. The paper argues for exactly
  that level of aggregation and against going further (one number per species per zone), which overestimated by
  45–70% because it threw away space (who can reach which food). For catch-up this says: **step the swarms, not a
  zone-wide species total**; keep each swarm's **position and food access**; keep **age bins** if ageing matters (it
  does — our server ages swarms); and when the zone is shown again, re-create individual bugs **inside their swarm's
  saved area**, not at random across the zone (random re-creation measurably changed their outcomes).

#### D4. M. Scheffer, J. M. Baveco, D. L. DeAngelis, K. A. Rose & E. H. van Nes, "Super-individuals: a simple solution for modelling large populations on an individual basis", *Ecological Modelling* 80 (1995) 161–170

- **Read:** in full (10 pages), [PDF from the University of Amsterdam repository](https://pure.uva.nl/ws/files/2866149/761_6900y.pdf),
  doi 10.1016/0304-3800(94)00055-M. (The founding paper for the "school-agents" of D3.)
- **What it says.** Give each simulated individual one extra number, its **"internal amount" — how many real
  animals it stands for**. With amount 1 the model is fully individual; with large amounts it is a cohort model;
  with one super-individual per population it is "all-animals-are-equal" — **the same code at every level**. Deaths
  inside a super-individual: instead of n separate die/live dice, draw the number of survivors **from a binomial
  distribution of size n**, computed by the recursion `P0 = (1 − p)^n`, `Px = P(x−1)·(n − x + 1)·p / (x·(1 − p))`
  until the running sum passes a uniform random number; if `n·p > 5`, use a normal (bell-curve) approximation with
  mean `n·p` (the paper prints "p", an evident typo) and spread `√(n·p·(1 − p))`. For speed it recommends a
  **hybrid: keep the amount as a real number (deterministic fractions) while it is large, and switch to whole-animal
  dice only below a threshold**, "combining high computational speed with essential stochasticity at low individual
  numbers". Starvation: a starving super-individual loses 10% of its amount per day; once its amount falls below 1,
  its final death is a daily 10% die-roll, as for a single animal. Reproduction: a random sample of the newborns is
  turned into new super-individuals with amounts that keep the total right. Results: a consumer–food cohort model
  with 10 super-individuals ran in under a minute versus over 2 hours for 10,000 plain individuals, and kept a
  smooth size distribution that the plain 500-individual run lost; a striped-bass model of ~200,000 larvae
  represented by **20 super-individuals deviated only ~2%** in growth and mortality (Table 2), three times more
  accurate than the older "resampling" method.
- **The techniques.** (1) **Count-carrying units** with one rulebook at every scale. (2) **Binomial deaths** per
  unit (the exact form of B5's leap). (3) **Fractional amounts when large, dice when small** — Kittens Game's
  loop-or-bell-curve (A2) in ecological dress, and the cure for the atto-fox (B1). (4) A threshold-based final
  extinction.
- **Cost to run:** proportional to the number of super-individuals, not of animals.
- **Fit for us — direct.** This *is* our swarm design. It says the catch-up can reuse the swarm life-cycle rules the
  server already has, stepping each swarm's count with binomial deaths/births and fractional bookkeeping above a
  threshold, rather than inventing a separate zone-wide formula; and that a small swarm (or a nearly-extinct
  species) must switch to whole-bug dice so it can actually die out.

### Topic E — Determinism: the same answer on every computer

Angles run: by technique (Fiedler's floating-point determinism article, fetched directly; counter-based random
generators — the Random123 paper, fetched directly); by game (Supreme Commander and Battlezone 2, as quoted by
Fiedler); by language or tool (the Go language specification; Go's issue tracker); by symptom ("Go compiler fused
multiply-add arm64 different floating point results amd64 determinism").
Context checked in our repo: the client's bug simulation uses a stateless counter-based generator,
`CounterRng.Hash(worldSeed, swarmId, bugId, tick, purposeId)` (FNV-1a), in
`BugFarmerClient/Assets/Scripts/Bugs/DeterministicRandom.cs`; the Go server uses one seeded *stateful* stream per
match, `state.Rng *rand.Rand` (`nakama/modules/world/state.go`), reproducible only with sorted iteration order (its
own comment says so), and broadcasts its results to clients.

#### E1. Glenn Fiedler, "Floating Point Determinism" (Gaffer On Games)

- **Read:** in full, [gafferongames.com/post/floating_point_determinism](https://gafferongames.com/post/floating_point_determinism/).
- **What it says.** Lockstep games send only inputs, so every machine must compute identical results. Floating point
  can be made deterministic only "provided you use an executable built with the same compiler, run on machines with
  the same architecture, and perform some platform-specific tricks"; "it is incredibly naive to write arbitrary
  floating point code in C or C++ and expect it to give exactly the same result across different compilers or
  architectures, or even the same results across debug and release builds." Quoted practitioners: Supreme Commander
  shipped deterministic lockstep by forcing the FPU precision and rounding mode at start-up and **asserting every
  tick** that they hadn't changed; Battlezone 2 found **AMD and Intel gave slightly different results for sin, cos,
  tan** and their inverses; a Pandemic engineer warns that even **integer modulo** was implementation-defined across
  C++ compilers; Intel: transcendental instructions are specified to an error bound, "not bit-for-bit accuracy";
  fused multiply-add changes results.
- **The technique.** Either lock floating point down (one compiler, one architecture, strict mode, no transcendental
  library calls) or avoid it: integers / fixed point with your own implementations of `exp`, `log`, square root.
- **Cost to run:** fixed point is cheap; the cost is implementation care.
- **Fit for us.** We are already on fixed point (× 1000) for the lockstep client simulation, which is right. A
  catch-up model needs `e^(−r·Δt)` (B3, B5), divisions (B4) and binomial draws (B5): all must be integer-only
  (lookup tables, or `(1 − p)^n` by repeated squaring in fixed point) — **never** `math.Exp` on floats if the result
  must match elsewhere.

#### E2. The Go Programming Language Specification — "Floating-point operators" and "Integer overflow"

- **Read:** those sections in full (not the whole specification), [go.dev/ref/spec](https://go.dev/ref/spec).
- **What it says.** "An implementation may combine multiple floating-point operations into a single fused
  operation, possibly across statements, and produce a result that differs from the value obtained by executing and
  rounding the instructions individually." E.g. `r = x*y + z` may use a fused multiply-add; only an explicit
  conversion, `float64(x*y) + z`, forbids it. By contrast, signed integer overflow is "deterministically defined",
  shifts are exact, and the compiler "may not optimize code under the assumption that overflow does not occur".
- **Fit for us.** Our server is Go. A floating-point catch-up model could legally give **different results on an
  ARM server than on an x86 developer machine or test runner** (ARM has fused multiply-add) — which would break
  "calibrate against the headless run, then reproduce exactly". Integer fixed point in Go is fully specified. If
  floats are ever used, every product that feeds a sum needs an explicit `float64(...)` conversion. This is not
  theoretical: Go's own issue tracker has [#43219](https://golang.org/issue/43219) ("floating point math diverges on
  ARM64 due to FMA"), [#36536](https://golang.org/issue/36536) ("inconsistent float64 behaviour between arm64 and
  amd64") and [#53134](https://golang.org/issue/53134) (float32 results on Apple M1 differing "depending on
  inlining") — titles and opening reports read. (Whether *our* server build emits FMA on its deployment target is
  **not confirmed** here.)

#### E3. J. K. Salmon, M. A. Moraes, R. O. Dror & D. E. Shaw, "Parallel Random Numbers: As Easy as 1, 2, 3" (SC11, 2011)

- **Read:** in full (12 pages), [PDF](https://www.thesalmons.org/john/random123/papers/random123sc11.pdf).
- **What it says.** A conventional generator steps a hidden state (`s(n+1) = f(s(n))`), so the n-th number depends on
  everything drawn before it. A **counter-based** generator computes the n-th number directly, `x = b_k(n)`, from a
  key and a counter through a scrambling function (Philox, Threefry, ARS; all pass the toughest statistical test
  batteries). The paper's recommended use: build the key/counter from **application variables** — "if … an
  application with a large number of objects already has stable integer identifiers, i, … as well as a
  monotonically advancing notion of 'time' (T) … it could concatenate the object identifier, i, and time, T, into
  a … counter" — which "permits deterministic results across different computing platforms" and "even with
  different levels of physical parallelism". The one rule: never reuse a (key, counter) pair by accident. Speed:
  ~1–4 CPU cycles per random byte.
- **The technique.** Draw every random number for the catch-up from **(world seed, zone, swarm id, game day or
  event index, purpose)**. Then the result does not depend on the order swarms are processed in, on how the catch-up
  is split into chunks, or on which machine runs it.
- **Cost to run:** a few nanoseconds per draw; no stored state.
- **Fit for us.** Strong, and it matches the client's existing `CounterRng` design. It is what makes catch-up
  **chunk-independent**: "catch up 6 hours in one go" and "catch up 2 hours, then 4 hours" can be made to produce the
  identical world only if each day's draws are keyed by that day, not by "the next number in the server's stream".
  The server's current stateful `state.Rng` does not have that property (inference from its comment and the
  paper's argument; not tested here). Note also that our client's FNV-1a hash is not one of the generators the
  paper tested (**not confirmed** whether it would pass the same battery; FNV-1a was designed as a hash, not as a
  random generator).

---

## Source table

"Fit" is for Bug Farmer's catch-up of a frozen zone: **High** = usable nearly as-is; **Medium** = the idea transfers
with work; **Low** = background or a warning only.

| # | Source | Technique | Cost to run | Fit |
|---|---|---|---|---|
| A1 | Pecorella, *The Math of Idle Games* I–III | Closed-form growth over any time; Egg, Inc. caps offline at 2 h | Constant | Low (no feedback in idle economies); the cap is a precedent |
| A2 | Kittens Game source (`time.js`, `resources.js`, `village.js`, `calendar.js`, `math.js`) | Freeze rates and multiply; skip starvation offline; expected value or loop-or-bell-curve for random events; cut the jump at queue events; cap 10/40 game years | Constant per system | Medium: loop-or-bell-curve and event-cutting High; one-sided "no starvation" a warning |
| A3 | Antimatter Dimensions source (`game.js`, `storage.js`, `AwayProgressModal.vue`, `h2p.js`) | Replay the real tick with fewer, longer ticks (default 100,000, ≥ 33 ms each); before/after diff screen | ∝ tick budget | Medium: one code path; once-per-tick behaviour breaks; the diff screen is High |
| A4 | Cookie Clicker source (`main.js`, `minigameGarden.js`) | Rate × time with a penalty and cap; count whole timer cycles and carry the remainder; the garden is *not* caught up | Constant | Medium: cycle counting High; the garden is the owner's fear in a real game |
| A5 | Practitioner notes (itch.io thread, Clicker Heroes blog, Tideward page) | Event heap; average recent income; headless fast replay; banked time; "run until you hit a wall"; per-action seeded replay, 24 h cap, timeline screen | Varies | Medium; the "two code paths drift" warning is the key lesson |
| B1 | Fowler 2021, *Atto-Foxes and Other Minutiae* | Smooth models resurrect extinct species; persistence via refuges/reservoirs; type-III predation | None (modelling choice) | High (warning + our director is the reservoir) |
| B2 | May 1976, *Nature* | Discrete logistic: steady → cycles → chaos → negative as step × rate grows; Ricker stays positive | Per step | High (core warning against big steps) |
| B3 | Beverton–Holt (Wikipedia) + derivation | Exact logistic jump over any Δt | Constant per piece | High for pens / single pools |
| B4 | Dimitrov & Kojouharov 2007 | Gains explicit, losses implicit: positive and correct-equilibrium at any step | Like Euler | High for coupled predator–prey pools |
| B5 | Tian & Burrage 2004 | Binomial leaps: whole individuals, never negative; exact binomial for independent losses | 1–2 draws per event type per leap; 5–70× faster than exact | High |
| B6 | Cook 2020, *Symplectic Euler* | Update species one after the other; plain Euler spirals out | Like Euler | Medium (B4 safer) |
| C1 | NetLogo Wolf Sheep: agent, system-dynamics, docked hybrid | Docking; 1,000 sub-steps per tick; clamp at zero; macro rates set by hand | Agents ∝ animals; equations tiny | Medium (shows the gap we must fit) |
| C1b | Mesa `wolf_sheep` | Behavioural movement changes encounter rates; event-scheduled regrowth | Event per eating | Medium |
| C2 | Parunak, Savit & Riolo 1998 | ABM vs EBM; Wilson's fixes: per-location noise + local extinction threshold | Not stated | High (posture: full sim is the truth) |
| D1 | Hunter et al. 2020, JASSS | Per-area switch by count threshold; equations set counts, random individuals assigned | 15–64% faster per step | High (shape matches our server/client split) |
| D2 | ten Broeke et al. 2021, JASSS | Two-stage surrogate: "crash or not" then "how much"; adaptive sampling; fixed test set | Training offline; use ≈ free | High for calibration |
| D3 | Wallentin & Neuwirth 2017 | Agents ↔ school-agents (super-individuals); emergence triggers; age-binned stocks; random re-creation hurts | 0.5–118 min / 100 years by design | High (closest analogue) |
| D4 | Scheffer et al. 1995 | Super-individuals with an "internal amount"; binomial deaths; fractions when large, dice when small | ∝ number of super-individuals | High (this is our swarm) |
| E1 | Fiedler, *Floating Point Determinism* | Floats only deterministic under strict conditions; prefer integers | — | High |
| E2 | Go spec (+ Go issues #43219, #36536, #53134) | Go may fuse float multiply-add; integers fully specified | — | High (our server is Go) |
| E3 | Salmon et al. 2011, Random123 | Counter-based random numbers keyed by object id + time | ns per draw, no state | High |

## The six most useful techniques for us

1. **Catch up at the swarm level, reusing the server's own life-cycle rules (swarms are "super-individuals").**
   Step each swarm's *count* (and age bins if ageing matters) at a coarse cadence with the same birth, ageing, hunger
   and nest rules the server already runs — not a separate zone-wide formula. Keep each swarm's place and food
   access. Evidence: D4 (20 super-individuals stood in for 200,000 larvae within ~2%), D3 (aggregating further, to
   lake-wide totals, overestimated by 45–70%), C2/D1 (aggregate locally, not globally), A5 (a second, simplified
   copy of the rules becomes a second game to keep in step). Note the project's standing rule (not from a source):
   per-bug *behaviour* stays on the clients, so a server-side catch-up that stays at the group level fits it, while
   replaying per-bug movement on the server would not.
2. **Never-negative, whole-bug steps.** Expected changes from rules that cannot go negative at any step length —
   the **exact logistic jump** `N' = K·N / (N + (K − N)·e^(−r·Δt))` for a pen or single pool (B3), or **gains
   explicit, losses in the denominator** `N' = (N + gains·h) / (1 + loss_rate·h)` for coupled predator and prey (B4).
   Actual whole-bug changes drawn as **binomial leaps** — deaths `~ Binomial(n, 1 − e^(−μ·Δt))`, eaten
   `~ Binomial(min(prey, predator capacity), p)` (B5, D4) — with the loop-or-bell-curve shortcut for big counts (A2,
   D4: bell curve when `n·p > 5`). A species can therefore reach **zero**; recovery is the director's reseed (B1), not
   a surviving fraction.
3. **Cut the jump at events; be exact in between.** Split the away time at the moments the rules change — food runs
   out or regrows, a pen fills, the day/season or weather turns, a nest timer fires, the director checks — and do
   one exact step per piece (A2 queue redshift, A5 event heap, C1b scheduled regrowth). For periodic timers, **count
   whole cycles and carry the remainder** (A4 sugar lumps). This also keeps steps short where growth is fast, which
   B2 shows is where long steps go wrong.
4. **Calibrate the cheap model against the headless full simulation, in two stages, and check distributions.**
   From many headless runs (many seeds, many starting states) fit (a) "does this swarm/species crash in a window of
   this length?" and (b) "if not, where does it end?" (D2). Treat the full simulation as the truth and adjust the
   cheap model (C2, Wilson), add the noise and extinction thresholds it needs (C2), sample more where it is wrong
   (D2), and accept it only when its **outcome distributions** match the full simulation's over many runs, not a
   single run (D1, C1 docking). This is the principled form of the owner's suggestion (2026-10-10) to estimate
   the outcome from recent population data, or per swarm from its access to food.
5. **Counter-keyed randomness and integer maths.** Key every random draw by (world seed, zone, swarm, game day or
   event index, purpose) (E3), so catching up 6 hours at once or in two pieces gives the identical world; compute
   `e^(−x)` and binomials in fixed point (tables, repeated squaring) — no Go floats where results must reproduce (E1,
   E2). Matches the client's existing `CounterRng`; the server's stateful `state.Rng` does not give chunk-independence.
6. **Show what happened: a mechanical "while you were away" summary from two snapshots.** Snapshot before the
   catch-up, diff after, and list per pen and per notable species what changed (A3's before/after modal; A4's
   "N hours at X%" explanation; A5's timeline including food eaten and deaths). Part of the fly-farm worry is
   visibility: a farm that grew should *say* it grew, and one that starved should say when and why.

## Warnings: where cheap models mislead

- **Fractions of a bug come back to life (the atto-fox).** Any smooth or fixed-point-fraction model lets a crashed
  species survive as 0.004 of a bug and regrow (B1, May's chaotic troughs in B2, Wilson in C2). Require integer
  counts or an explicit extinction rule, and route recovery through the reseed.
- **Long steps invent behaviour.** Plain stepping turns smooth growth into fake cycles, chaos and negative counts once
  `growth rate × step` passes ~1 (overshoot) and ~2 (fake cycles) (B2), makes predator–prey swings grow without limit
  (B6), and fails at large steps where positivity-preserving rules do not (B4). Fast breeders are the first to break.
- **Averages erase the design's crashes.** Averaging recent data, mean-field equations and single smooth
  regressions all predict a mild dip where the real system crashes or booms (C2: limit cycles instead of
  extinctions; D2: settings that decide *whether* a population survives differ from those that decide *how big*;
  D3: lake-wide averaging overestimated by 45–70%). Kittens Game avoided the problem only by switching starvation
  off offline (A2) — the opposite of our decided design for wild bugs.
- **Agent and aggregate versions can disagree about stability itself** (C1: wolves and sheep alone collapse as
  agents but cycle forever as equations). A model fitted on stable stretches can miss tipping points; calibrate
  across regimes, including ones that crash.
- **Once-per-tick behaviour breaks with long ticks** (A3: autobuyers fire once per 3.6 s tick). For us: hunts,
  cooldowns, nest timers, egg-laying windows — anything with a per-tick roll needs a rate-correct conversion
  (`1 − (1 − p)^n`, binomials) or an event, not a longer tick.
- **Space matters.** A predator meets prey only where they overlap; a pen's flies only eat its feed. Zone-wide pools
  overestimate (D3), equation models need noise and local thresholds to match agents (C2), and the encounter rate
  depends on behaviour (C1b vs C1). Aggregate per swarm or per local area.
- **Re-created individuals placed at random change what happens next** (D3: delayed regrouping, higher collapse
  risk). When the zone is shown again, place bugs inside their swarm's saved area.
- **Two models drift.** A separately written catch-up model is a second copy of the rules that will fall out of step
  with the live game (A5). Prefer reusing the server's own life-cycle code at a coarser cadence, and re-calibrate
  (technique 4) whenever balance changes.
- **Floats and stateful random streams break reproducibility.** Go may legally fuse float operations and does
  differ between ARM and x86 (E2); a sequential random stream makes the result depend on processing order and on
  how the catch-up is split (E3).
- **Taste calls this research does not settle (for the owner).** Idle games cap time away (Egg, Inc. 2 h; Kittens Game
  ≈ 2.2 h or ≈ 8.9 h of real time; Cookie Clicker 1 h at full offline rate, then a tenth; Tideward 24 h) and some are
  deliberately one-sided (gain, never starve). A cap or a one-sided rule would contradict the decided single world
  clock and the decided design for wild ecology; whether a *pen* should be kinder than the wild while its owner is
  away is a design question, not a maths one.

## Sources that could not be read (not counted)

- Melvor Idle wiki, "Offline Progression" — HTTP 403; its claims appear here only second-hand (A5).
- Cao, Gillespie & Petzold 2005, *Avoiding negative populations in explicit Poisson tau-leaping* — the repository
  blocked the request; Tian & Burrage (B5) was read instead.
- Colon et al. 2015 (agent-based vs mean-field predator–prey) — host certificate failed verification; not fetched.
- Bobashev et al. 2007 (hybrid epidemic model) and Gray & Wotherspoon 2012 (dynamically changing representations) —
  not open access; known only through the citing papers D1 and D3.

## Quota count

- **Sources deep-read in full: 12 substantial** — A1 Pecorella I–III (three articles), B1 Fowler 2021, B2 May 1976,
  B4 Dimitrov & Kojouharov 2007, B5 Tian & Burrage 2004, C2 Parunak, Savit & Riolo 1998, D1 Hunter et al. 2020, D2 ten
  Broeke et al. 2021 (main text), D3 Wallentin & Neuwirth 2017, D4 Scheffer et al. 1995, E1 Fiedler, E3 Salmon et al.
  2011 — **plus 5 short pages read in full** (B3 Beverton–Holt article, B6 Cook's post, and the three practitioner
  sources of A5). E2 (Go specification) was read for the relevant sections only. Quota: ≥ 7 — **met**.
- **Codebases studied: 5** (quota ≥ 2 — **met**):
  - Kittens Game — [github.com/nuclear-unicorn/kittensgame](https://github.com/nuclear-unicorn/kittensgame) @ `781e379f`:
    `js/time.js`, `js/resources.js`, `js/village.js`, `js/calendar.js`, `js/math.js`, `res/i18n/en.json`.
  - Antimatter Dimensions — [github.com/IvarK/AntimatterDimensionsSourceCode](https://github.com/IvarK/AntimatterDimensionsSourceCode) @ `5409e320`:
    `src/game.js`, `src/core/storage/storage.js`, `src/core/player.js`, `src/components/modals/AwayProgressModal.vue`,
    `src/core/secret-formula/h2p.js`.
  - Cookie Clicker (source-visible, not open-source licensed) — [orteil.dashnet.org/cookieclicker/main.js](https://orteil.dashnet.org/cookieclicker/main.js),
    [minigameGarden.js](https://orteil.dashnet.org/cookieclicker/minigameGarden.js).
  - NetLogo Wolf Sheep Predation — [github.com/NetLogo/models](https://github.com/NetLogo/models) @ `a83b6f18`:
    `Sample Models/Biology/Wolf Sheep Predation.nlogox`, `Sample Models/System Dynamics/Wolf Sheep Predation (System Dynamics).nlogox`,
    `Sample Models/System Dynamics/Wolf Sheep Predation (Docked Hybrid).nlogox`.
  - Mesa `wolf_sheep` — [github.com/projectmesa/mesa](https://github.com/projectmesa/mesa) @ `5451086f`:
    `mesa/examples/advanced/wolf_sheep/model.py`, `agents.py`.
- Repo files consulted for context (read-only): `BugFarmerClient/Assets/Scripts/Bugs/DeterministicRandom.cs`,
  `nakama/modules/world/state.go`.
