# Review Lenses — re-examination catalog (loop scaffolding)

A **lens** is a single perspective for re-examining work, with the question it forces. The point is to
beat tunnel vision: after a plan or a change, run it past several lenses deliberately. Each entry is sized
to be one step in an automated loop — e.g. an agent prompt:

> "Re-examine `<artifact>` through the **<lens>** lens: `<question>`. Report PASS / RISK / BROKEN with
> evidence (file:line). If RISK/BROKEN, propose the minimal fix."

Pick the lenses that fit the artifact; you rarely need all of them. The ones marked ★ have earned their
keep on this codebase (each caught a real, shipped-would-have-bitten issue).

## The lenses

- ★ **Requirements** — Does this *observably* satisfy what the user actually asked, not just "technically
  work"? (e.g. an ask to *see* hornets attack individual flies needs the visual, not only the correct kill.)
- ★ **Data / Contract** — Units, scales, serialization round-trips, fixed-point vs float, enum/string
  matches across a boundary. (Caught a ×1000 fixed-point radius-scale bug: threshold must use FixedPoint
  multiply, not raw int².)
- ★ **Timing / Ordering** — Races, on-receipt vs frontier-gated, who-mutates-when, tick alignment, message
  arrival order. (Confirmed BUG_REMOVED is frontier-gated → authority must not remove locally.)
- **Failure / Edge** — empty / missing / duplicate / stale inputs; entity vanished mid-operation; partial
  failure. (Prey id renumber between strike-select and apply → server validates alive ids.)
- ★ **Scale / Performance** — Cost per tick/frame at the *worst* realistic case (boom), on the *actual*
  deployment (a consumer host that's also playing). (Added a broad-phase before an O(P×Q) per-bug scan.)
- **Consistency / Idiom** — Is there an existing util/pattern to reuse? Does it read like the surrounding
  code? (Reused killBugsInSwarm, the catch/validate message pattern, _swarmLegs.)
- **Simpler-Alternative** — Is there a less complex way that still meets the requirement? Am I building two
  features where one would do?
- ★ **Verification** — Does the test actually EXERCISE the path, or can it false-pass? (A sync run with no
  strike is a *vacuous* green; a contaminated/persisted match gives *false* divergence. Assert the thing
  happened.)
- **Determinism** *(domain-specific here)* — float vs fixed-point; map/set iteration order; RNG draw order;
  cross-client + replay equivalence; nothing wall-clock. (The whole bug sim lives or dies on this.)
- **Docs / Drift** — What comments/docs/contracts does this change now make false? Reconcile at completion.
- **Blast-radius / Rollback** — If this is wrong, what breaks? Is each commit coherent and revertible? Does
  the interim state (between commits of an atomic change) still work? (Split the predation flip so predation
  never breaks mid-way.)
- **Security / Authority** — Who is allowed to do this? Is input validated? Can a client lie? (PredationStrike
  is authority-only + server-validated.)
- ★ **Derived-State / Cache-Coherence** — When adding a cache/index that duplicates a source of truth, pick
  the maintenance strategy by *coherence need*: does any reader observe the source **mid-update** (mutations
  interleaved with reads inside the same tick/batch)? If yes, a rebuild-per-batch snapshot goes stale →
  you need **incremental** maintenance (and must prove *every* mutation site updates the cache) or make the
  cache the primary store. If no reader observes mid-batch, **rebuild-from-source** is simpler and immune to
  missed sites. Either way, back incremental maintenance with an **invariant assertion** (rebuilt == maintained)
  exercised by the determinism harness. (Earned: a chunk index over `GroundItems` — a sub-agent's "complete"
  mutation-site list missed `handlers_farming.go:1443`, and feeding `delete`s items mid-swarm-loop, so a
  once-per-tick cache would NOT have been byte-exact.)
- ★ **Accounting-Artifact** — When a per-unit metric fingers a culprit, check whether it's a true cost driver
  or an artifact of the metric's denominator/normalization *before* acting on it. (Earned: the per-bug perf
  chart blamed carrion beetles at ~30× others, but they think at the normal cadence — they top the chart only
  because their swarms hold ~1 bug each, so the per-think scan cost isn't amortized. The real lever was the
  per-scan cost, fixed for *all* species by the index; nerfing the beetle would have starved a food-scarce
  species for ~no gain.)

- ★ **Completeness / No-Half-Ladder** — When building a *set* (tiers, families, a metal ladder, a per-species
  map), does EVERY declared member exist, or is it partial? Half-built sets read as "done" but aren't (the
  `iron_bar` with no `copper_bar`; tools that stop at iron). Back it with a **completeness validator** that
  enumerates the matrix and fails on any gap. (Earned: a large slice of the crafting system was silently
  partial; the validator immediately caught `pickaxe_copper`/`axe_copper` with no recipe.)
- ★ **Hidden-Asset-Cost** — Does this "data/recipe" change secretly require hand-authored ASSETS (paper-doll
  overlays, multi-frame sprites) or an unbuilt SYSTEM before it's player-real? Separate data-cheap from
  art/system-expensive *before* committing scope. A recipe whose output can't be seen/used is a halfway.
  (Earned: armor recipes look like pure data but need ~420 hand-authored PNGs; tools were genuinely cheap.)
- ★ **Authored-Decision Fidelity / Docs-Aren't-Authority** — Does the implementation match what the USER actually
  decided? And **do not treat docs YOU (the assistant) wrote as authority** — design docs you authored in past
  sessions are padded with unbuilt inventions, so "it's in `crafting.md`" (or even a `DECISIONS.md` D-entry) ≠
  "the user decided it." Authority = built data + asking the user. Litmus for a feature: does it EXIST in the
  built artifacts (a real placeable, a real recipe), or only in prose? When unsure, ASK. (Earned repeatedly: the
  furnace-smelt drift from D13/D19; an invented `chopping_block` I "verified" against my own `crafting.md`; a
  `DECISIONS.md` D26 the user said he never decided.)
- **Content-Reachability / Dead-End** — In a content/economy graph, is every authored entity both PRODUCED and
  CONSUMED (or terminal by design)? No orphan intermediates; no self-dropping decorative "traps." Gate with a
  reachability validator. (Earned: `ore_sluice`/`coal_bin`/`geode` were dead self-dropping objects wired to
  nothing.)
- ★ **State-Machine Priority / Concurrent-Ownership** — When an entity is driven by multiple orthogonal "what it's
  doing now" mechanisms (a lifecycle `Phase`, an `ActionState`, a new dwell timer), define the EXPLICIT priority
  order (which one owns the tick + emits the leg) and prove no two co-own a tick or emit conflicting targets. Added
  "at the top" silently preempts everything below; "at the bottom" is silently starved above. (Earned: the predator
  feed-pause had to slot into `predationThink`'s flee>defending>homing>FEED>carrion>hunt order, after
  `processActionState` — wrong slot = nest-defense delayed by the full feed, or a feed that never fires because hunting
  always wins. Reading the REAL order also revealed homing sits ABOVE feed, so a load-filling kill sends a wasp home
  instead of parking — a behavior you only see by tracing the actual priority chain, not a doc's summary of it.)

## Design lenses (for feature/creature DESIGN, not just code review)
- ★ **Unbounded-Growth / Accumulation** — Does this system create entities or state that grow without a
  matching removal at steady rate? What bounds the standing count? (Generalized from the rotten-fruit pile:
  6-day lifetime × tree production → a deep pile + an O(items) decay pass. Also caught: spider webs must
  decay + not persist into saved zone data, colony-memory entries must age out.)
- **Fun / Legibility** — Can the player SEE and ENJOY the behavior, or is it emergent-but-invisible? Design
  for the readable moment. (Ant workers as small swarms so a trail reads as a *line*; reuse the centipede
  windup as the pounce *telegraph*; webs are visible occupants. Cousin of the Requirements lens — seeing
  hornets attack needed the visual.)
- **Emergence-Equivalence** — Does the cheap heuristic produce the same end-user-visible outcome as the
  complex thing it stands in for? Name where it's equivalent vs not. (Colony-memory ≈ ACO trails in open
  terrain; NOT for obstacle-route optimization → that's the deferred pheromone layer. The owner's rule: fun
  first — a heuristic is fine if the player can't tell the difference.)
- **Ecology-Fit / Systemic-Balance** — Does the new element slot into the existing system (food web,
  economy, difficulty curve) without breaking a hard-won equilibrium? Treat rates as dials; prove it in the
  lab before production. (Ants compete with detritivores for carrion; spiders are another predator on flies →
  balance in `ant_spider_lab` first, not `village_21_B`.)
- **Graceful-Degradation** — When the inputs vanish (no food / no prey / base destroyed / agent orphaned),
  does it degrade sanely instead of breaking or spinning? (No-carrion ant colony goes dormant + re-founds
  (nest-recovery precedent); orphaned forager drops its load (homing timeout); web-destroyed spider re-spins.)

## Idea lenses (before ANY game idea — item, outfit, weapon, bug, mechanic — reaches the owner)
> Owner decision (2026-09-26): every game idea is checked against these lenses before he sees it — a real process
> that removes unplayable ideas, not first-thought suggestions. Curiosity and Surprise (from *The Art of Game
> Design*) matter most to him.

**The process (every time):** (1) read what the owner already designed or cut for this topic — the GDD section
(`docs/gdd/`), `docs/product/economy/DECISIONS.md`, and for gear `docs/product/design/brainstorm_armor.md`
(§7 the expedition + verbs rules, §11 the saturation test) — and start there, not from a blank page;
(2) write one line per lens below for each idea (PASS / RISK / CUT + why); (3) a cold-critic agent (told: no
sub-agents) sees only the ideas, these lenses and the owner's rules and tries to cut each one; (4) show the owner
the survivors WITH their lens notes, and list the cuts with a one-line reason each so he can rescue one.

Earned 2026-09-26: of 16 sample ideas, the owner rejected 6 and qualified 5 — every one traced to a lens below
that was skipped. His verdicts, restated:

- ★ **Premise** — Does it fit 2126: giant bugs, nearly no mammals, bugs are food and livestock? (Rejected: a pooter,
  a suction vial for tiny bugs — in this world bugs are giant; a Berlese funnel for tiny soil bugs.)
- ★ **Bestiary** — Does it depend on a bug we don't have? Say so plainly and count it as a cost. New bugs are
  welcome if the balance holds and each is explained, but not ones that need a whole new zone. (Rejected: a
  trap-jaw dagger — there are no trap-jaw ants.)
- ★ **Picture the moment** — Describe what the player literally sees and presses, second by second. If it looks
  awkward, cut it. (Rejected: a mantis gauntlet that pins a bug with one hand while you net it with the other —
  awkward to picture; a moth light-sheet — awkward to look at: moths should simply be drawn to lights, with nets,
  automatic catchers or bug zappers placed around them once there is electricity.)
- ★ **Zone freedom** — Does it force a rule onto every zone ("one in every zone")? Cut. (Rejected: a naturalist's
  notebook in every zone — no mechanic should force a rule onto every zone.)
- ★ **Already covered?** — What does it do that nothing in the game (or the design) already does? (Rejected: a UV
  lantern — electric lanterns, bug lanterns and torches already light the way; the notebooks — findable recipes and
  the Ecologist already exist.)
- ★ **Explain on examine** — Is the real biology shown when you examine the item or its recipe, so the effect
  makes sense? (Monarch regalia: kept only with the biology explained on examine.)
- **Scope of the effect** — Does it claim to work on "anything"? Name exactly which bugs it affects and why.
  (Monarch regalia: a good idea for some bugs, not for everything that bites.)
- **Made from the world** — Is it crafted from materials that make sense for it, that the player can get?
  (Stick-insect ghillie: made from plants and fibre, not from stick insects.)
- **Readable state** — If it changes a hidden state (hidden, calmed, marked…), how does the player SEE it?
  (Ghillie: needs a "hidden" indicator.)
- **New-mechanic tax** — Does it need a new system (a flip state, a pin state…)? Is the payoff worth building and
  balancing it? Use common sense. (Rhino-beetle maul: needs a new flip mechanic — doubtful.)
- **Art-system fit** — Does it depend on an art capability we don't have yet (separate armour pieces, a new
  animation)? State the dependency. (Waders: fine, if separate armour pieces can be drawn to work with the system.)
- **Owner's gear rules** (outfits and accessories) — suits an EXPEDITION, not one action; bonuses attach to
  VERBS, not idle output (decorative outfits that boost the farm are the owner's allowed exception); passes the
  SATURATION test — say what it is FOR in one phrase, and no other set has that answer.
- **Balance** — Where does it sit on the cost ladder, and what does it make obsolete? (Food ideas: fine as long as
  they don't upset the balance.)
- **Schell's lenses** (*The Art of Game Design*) — the Eight Filters (it feels right · the players it's for will like it ·
  it's well designed · it's new enough · it helps the game sell · it can be built · it serves playing together ·
  playtesters enjoy it), then **Curiosity** and
  **Surprise** (the owner's two), Toy, Meaningful Choices, Elegance, Visible Progress, Economy, Unification.

What passed with no conditions, for calibration: bombardier plate, tarantula-hair cloak, amber in cave walls (he
likes surprises), nest chests (bugs bursting out of chests is fine), and bug food from your own farm.

## Zone & scene lenses (world craft, not code — run against RENDERED PIXELS, crop in hand)
Used by the `zone-craft` skill's review step. Answer each against actual renders/crops at game
zoom, not the plan or the source; report PASS / RISK / BROKEN with the crop that shows it. If
all of them PASS on a FIRST build, the questions were asked too softly — tighten and re-run.

- ★ **Local** — Does daily life physically work here: doors face what people use, paths connect
  the chores, every workplace has its tools and its wear? (Earned: "doors face context, not
  compass south" + Gullwash Landing's split-shore homes both opening onto the water.)
- ★ **Cartographer** — Does the whole map READ at full zoom: natural region shapes, water that
  flows from somewhere to somewhere, every edge honoring its neighbor's contract? (Earned: the
  fishing hamlet's "sea" was a landlocked lake — dead on the first route-walk question.)
- ★ **Miner / Economist** — Is there something to extract or harvest per region, does it match
  the zone's difficulty tier, and does its distribution follow the caves.md doctrine (veins,
  bands, measured density)? (Earned: the gorge's hand-set silver/gold line, owner-caught.)
- ★ **Traveler** — Arriving at any edge and walking the main route, is there a visible reason to
  keep going within ~30 seconds — a landmark, a fork, a tease — at every decision point? (Earned:
  ant country had no route IN — the prospector's scratch was the fix, first live run.)
- **Kid** — Is there something to poke, break, collect, chase, or giggle at on every screen —
  not just scenery to look at?
- ★ **Storyteller** — Can you narrate ≥3 micro-stories from placement ALONE (the wreck, the
  abandoned sandcastle, the laundry behind the cottage)? What happened here before the player?
  (Earned: Halloway's claim props scattered 10 cells apart read as litter, not a story —
  clustered into one campsite, first live run.)
- **Ecologist** — Can every species that spawns here actually LIVE here: food, breeding
  habitat, shelter, refugia — geometrically, where they spawn? Does flora match the ground?
- **New-Player-at-zoom** — Crop random gameplay-zoom screenfuls (~20×12 cells): is EVERY one of
  them composed, or only the landmarks? The player lives at this zoom, not at the god view.
- **Secret-Keeper** — Does the zone HIDE ≥3 findable things (sealed spaces, a glint through a
  1-block window, sounds before sights), each with a real payoff when found? (Owner, 2026-07-06:
  secrets, surprise and curiosity are lenses he values.)
- **Surprise** — Does something confound expectation at least once per zone — the beautiful room
  in the scary place, the boulder that breathes, the trail that leads UP into daylight?
- **Curiosity-Hook** — At every landmark, is there a visible QUESTION pulling one screen further:
  a trail entering a crack, light from below, a draft of dark air, a door that shouldn't be there?

## Notes for automating this
- A lens pass is cheap insurance before an expensive build/run. Run the high-value lenses (★) on any plan
  that touches sync, data formats, or the hot loop.
- Lenses compose with the project's existing gates (Go compile → `go test ./world/` → Unity build →
  fresh-match harness → `tools/sim-determinism`). Lenses find issues *before* the gates; the gates confirm.
- A skeptical sub-agent per lens (especially Verification + Data/Contract) catches things the author's
  tunnel vision misses — and has, on this codebase, including an error in another sub-agent's report
  (always re-verify load-bearing claims against the real code).
- To turn a lens pass into a **numeric, evidence-anchored certainty table** (each lens finding → a scored row
  with a falsifier + the gate that raises it, MIN-aggregated), run the `certainty-assessment` skill. The lenses
  say *what to look at*; that skill says *how certain you are, with the number bound to evidence.*
