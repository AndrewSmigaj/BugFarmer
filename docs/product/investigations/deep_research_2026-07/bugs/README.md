# Bugs research — index & recovery status (topic 2)

*Per-species behaviour research: how good games implement each creature, mapped to our deterministic
swarm sim (movement = `SWARM_SET_TARGET` legs; kills relayed via `BUG_REMOVED`; sim reads zone-wide only).*

## Honest recovery status
This topic was hit hardest by the session-limit failure (see the `no-wide-agent-fanout` memory). Some
families' research completed and survived; others' agents died early. What's here:

| Family | Clean doc | Recovered raw research | Status |
|---|---|---|---|
| **Flying pests & stingers** (flies, mosquitoes, wasps, **hornets**) | ✅ `flying_pests_stingers.md` | `../_raw_recovered/bugs/a6e6cea1898d67583.md` (14 deep-read biology sources, full) | **DONE** — strong, includes the marquee hornet design |
| **Scorpions & centipedes** | ✅ `scorpions_centipedes.md` | (the three raw files nominally tagged "scorpion" are actually calm/subdual + centipede-cavern + a persistence review; scorpion biology was re-researched fresh) | **DONE** — burrow-ambush scorpion (grab→sting→venom, pincer/venom variant split) + segmented centipede body (cosmetic path-sampled PICK); scorpion behaviour is fresh web research |
| **Spiders** (wolf/jumping/orb/funnel/huntsman/tarantula/widow/cave) | ✅ `spiders.md` | `ad3b80dd9865c378f.md`, `a5e43c1048681edb7.md`, `a2670bf6a75e6d5a0.md` (mixed with ecology/ant content) | **DONE** — clean doc from a fresh deep-read (Grounded/Don't Starve/Terraria/Hollow Knight/Minecraft + spider biology), a section per type, mapped onto the code-verified `design_ants_spiders.md` sim primitives |
| **Gentle pollinators & ambient fliers** (butterfly, bee, firefly, dragonfly, mayfly, cicada, moth) | ✅ `pollinators_gentle_fliers.md` | `a1c61bc0ef1c7d5f9.md`, `ab9f15ce2fe9e961b.md`, `abf6d6b1bbdc1ec5e.md` (mostly bee-zone AUTHORING, not behaviour) | **DONE** — re-run self-contained; a section per species mapped to the built `movement_style`/forage/predation/day-night knobs; flight-motion PICK = server wander params + client display-only steering/bob overlay (glow & spiral cosmetic → determinism-free); firefly glow = the emissive hook |
| **Beetles/ladybugs, orthoptera, aquatic, ants** | ❌ | (ant material in `aa2618909f4cadf45.md`, `aff4adfa75a5ffca7.md` is largely prior-session colony work) | **Not covered** — never launched / prior work |

> **Status update (2026-07-11):** the **pollinator** family is now DONE (`pollinators_gentle_fliers.md`),
> re-run self-contained + incrementally per `no-wide-agent-fanout`. Spiders, scorpions/centipedes, and
> pollinators are all clean per-type docs now. The remaining GAP is **beetles/ladybugs, orthoptera,
> aquatic, ants** (last row) — never launched. The raw files remain a head-start for any deeper pass.

## Cross-cutting design principles (from the combat research, apply to every bug)
The `../combat/` docs already establish the shared enemy framework these species plug into:
- **Function over stats** — each species removes/demands a different player *tool* (net = flyers, spear =
  reach vs shelled/spitters, sword = burst vs tanks/broodmothers), never just "more HP."
- **One readable tell per species**; vary attack *rhythm* so one dodge-timing can't clear a mixed swarm.
- **Bite-token pool + telegraphed lunges + threat director + aggro/leash** cap fair damage while density stays
  scary. See `../combat/03_challenge_and_effectiveness.md`.
- Everything maps to **influence events**: movement legs, authority-relayed strikes, integer aggro — no
  view-scoped reads, fixed-point only.

## Species-behaviour hooks already captured (from the recovered biology research)
- **Mosquito** — telegraphed **cast-and-surge** zig-zag homing (break line-of-scent to dodge). [DONE]
- **Hornet (giant)** — **scout → hive-raid boss** with a "slaughter phase" that wrecks the farm; smoker counters
  the alarm-pheromone recruit loop. [DONE]
- **Scorpion / centipede** — ambush-from-burrow, pincer-grab→tail-sting combo, segmented "follow-the-leader"
  body movement (worm-AI); the raw files hold the source research — synthesis owed.
- **Spider** — web-as-trap (orb-weaver/widow) vs active hunter (wolf/jumping) vs ambush burst (funnel/
  tarantula) vs drop-from-above pack (cave); reuses the `design_ants_spiders.md` primitives (pounce =
  centipede `ActionState`, web = `spider_web` occupant + `web_slow`). See `spiders.md`. [DONE]
- **Pollinators & ambient fliers** — flight FEEL = server per-species wander params + a client display-only
  steering/bob overlay (`movement_style` is client-only); moth-to-lamp + firefly-dusk + cicada-day gate on
  the free `tick % DayLengthTicks` clock; firefly GLOW = new client emissive pulse (the one gap); dragonfly
  already hunts wasps via the built `predation` block (add an interception-lead polish). See
  `pollinators_gentle_fliers.md`. [DONE]
