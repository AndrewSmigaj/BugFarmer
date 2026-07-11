# Bugs research — index & recovery status (topic 2)

*Per-species behaviour research: how good games implement each creature, mapped to our deterministic
swarm sim (movement = `SWARM_SET_TARGET` legs; kills relayed via `BUG_REMOVED`; sim reads zone-wide only).*

## Honest recovery status
This topic was hit hardest by the session-limit failure (see the `no-wide-agent-fanout` memory). Some
families' research completed and survived; others' agents died early. What's here:

| Family | Clean doc | Recovered raw research | Status |
|---|---|---|---|
| **Flying pests & stingers** (flies, mosquitoes, wasps, **hornets**) | ✅ `flying_pests_stingers.md` | `../_raw_recovered/bugs/a6e6cea1898d67583.md` (14 deep-read biology sources, full) | **DONE** — strong, includes the marquee hornet design |
| **Scorpions & centipedes** | ⏳ raw only | `a2f63515bfd06f391.md` (scorpion-heavy), `a5e43c1048681edb7.md` (scorpion+spider), `abeb6d478f9dcdd73.md` (centipede/scorpion) | **Raw recovered** — needs clean synthesis (a low-concurrency re-run/read) |
| **Spiders** (wolf/jumping/orb/funnel/huntsman/tarantula/widow/cave) | ⏳ partial raw | `ad3b80dd9865c378f.md`, `a5e43c1048681edb7.md`, `a2670bf6a75e6d5a0.md` (mixed with ecology/ant content) | **Thin** — the dedicated spider agents died at ~2 tool calls; recovered material is partial + noisy. Re-run recommended |
| **Gentle pollinators** (butterfly, bee, firefly, dragonfly, moth, mayfly, cicada) | ⏳ partial raw | `a1c61bc0ef1c7d5f9.md`, `ab9f15ce2fe9e961b.md`, `abf6d6b1bbdc1ec5e.md` | **Thin** — pollinator agent died early; some material recovered |
| **Beetles/ladybugs, orthoptera, aquatic, ants** | ❌ | (ant material in `aa2618909f4cadf45.md`, `aff4adfa75a5ffca7.md` is largely prior-session colony work) | **Not covered** — never launched / prior work |

> **Recommendation:** re-run the spiders, scorpions, and pollinator research at **≤2 agents, self-contained,
> writing incrementally** (per `no-wide-agent-fanout`). The raw files above are a real head-start, not a
> blank slate. The requested marquee bugs (spider types, scorpion) still deserve clean per-type docs.

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
- **Spider** — web-as-trap vs active hunter vs ambush-pounce; drop-from-above; the raw files are partial — the
  dedicated deep-read is owed.
