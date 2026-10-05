# Roadmap — finishing Bug Farmer

The durable plan for finishing the game (approved 2026-09-26). **What** we are building and in which order.
The design itself is being consolidated into `docs/gdd/` (one section at a time, reviewed by the owner);
captured-but-unscheduled items stay in [`BACKLOG.md`](BACKLOG.md); finished work moves to
[`CHANGELOG.md`](CHANGELOG.md).

> The owner's brief (2026-09-26): finish the game properly — not patch it and ship. Many design decisions and much
> content are still to come. Existing systems (bug behaviour, combat, ecology tuning, the Ecology tab, the UI) work
> but need polish. I do most of the work; the owner reviews.
>
> *(Checked 2026-09-26: the Ecology tab isn't built yet — the game has only a developer population graph. The full
> design read also found where the game and its design disagree: `docs/gdd/overview.md`, "As built".)*

## The game in one paragraph
It is 2126. A plague killed nearly every mammal, so humanity bred bugs giant to eat. You start over on the
frontier as a bug farmer. A top-down, Terraria-like multiplayer sandbox with Stardew-like farming — no
storyline; progress comes from gear and preparation, gated by cost. Its heart is a living, deterministic
ecosystem every player sees identically; bugs are livestock (meat, or products like honey and silk) and the
food chain is the progression. Twenty zones of rising danger (surface north, underground south). Gear is about
roles and expeditions, not one best set. The shared world is chaotic (anything goes except NPC citizens'
property); private plots from City Hall are safe. The Ecologist and the Ecology tab (unlocked per area by
ecology stations) let you read and steer the ecosystem.

## Owner decisions (2026-09-26)
| topic | decision |
|---|---|
| Art | **gpt-image-2 for characters and most art, pixel-snapped; the interface and the blocks drawn in code** (2026-09-28 — code-drawn characters were rejected; gpt-image-2 draws blocks poorly; code-drawn UI and blocks are iterated with the owner). Whole outfits. All world and item art is regenerated on the outfit pipeline, since only the outfits were made the right way. Townspeople: each drawn by gpt-image-2 with walking frames, floating hands and a face portrait, people of many ethnicities (D60). Art is made after the GDD sign-off, in test batches. The look stays the same: 32 art pixels per grid square. Every paid image call is asked first. |
| Hosting | Like Terraria: Host & Play, joining, and a dedicated server program. Our own server is just another server, not part of the game; each server is capped at what is measured to be feasible, as Minecraft servers are. |
| Characters | Each world keeps its own characters, with a host setting that lets in characters from other worlds. |
| Empty zones | Frozen while empty; they catch up when someone first arrives, with random events of bugs crossing borders. |
| Cross-zone bugs | Left to me, judged on design and efficiency → swarm-level migration (below). |
| Private plots + City Hall | Kept — central to the design: the shared world is lawless except for the town's citizens, whose property can't be taken or damaged (a message says so). |
| Electronics | Power sources such as wind turbines and solar panels create powered areas; powered tools for gardening and bug farming, and powered versions of stations — some fully automatic, some still needing the player. Details are mine to design. |
| Base village | NPCs and their behaviour, overhauls of buildings and layout so it looks better and more coherent, general polish, and village secrets. |
| Story | No overarching story, as in Terraria; tutorials unlock as you play, and the Ecology tab has its own small tasks. |
| Process | The design document is reviewed one section at a time; every idea passes the lenses before the owner sees it. |
| Git | `main` is merged and pushed to GitHub at the end of every session. |

## Phases
### Phase 0 — safety + baseline (2026-09-26)
- [x] Everything pushed; `main` = all work (90216c0). New work on `feature/finish-the-game`.
- [x] Art demo drawn in code: `tools/_generated/player/reviews/2026-09-26-art-demo/` — not adopted: after a
  second code-drawn pass on the player base was rejected too, all art moved to gpt-image-2 (decision above).
- [x] Safety fix: unknown zones refused (no silent `village_21` save-borrowing); dangling `ant_colony_40` link removed.
- [x] Backup of `tools/_generated/raw` (1.1 GB) → `C:\Users\emily\BugFarmer_backups\generated_raw_2026-09-26\`.
- [x] Baseline gates: Go tests (all packages), sim-determinism (7 modes), sync-harness cross-zone + observe.
- [x] 2-client late-join sync gate on a fresh build (headless Unity player compiled today): co-located —
  all 76,447 shared-bug states + 239 tick hashes identical; spawn-apart (disjoint chunks) — all 77,737 + 241
  identical.
- [x] GDD skeleton (`docs/gdd/`, 23 sections) + the section-at-a-time review page
  (https://claude.ai/artifact/CRtGxrNmWdXPVAVyNnwWW1): §00 Premise and §19 Multiplayer ready for the owner.

### Phase 1 — prove the art, set the rules, design the spine, lay foundations
- **Bugs, behaviour and combat, zones' bug lists, items — the village slice (2026-10-04):** the one active plan is
  [`docs/plans/village-slice.md`](../plans/village-slice.md): the foundation under the bugs first (the waste cut on the
  players' computers, the whole zone running on the server, the bug state sent on join, zones of 512 × 512, tuning
  tools), then the bug budget, then the village rebuilt at 512 with its bugs tuned, played and signed off (D83, D84).
  Its requirements and designs come from [`finish-bugs-zones-items.md`](../plans/finish-bugs-zones-items.md).
- **Art (details: the top item of `BACKLOG.md`):** ~~import-scale fix~~ (done 2026-09-26: 89 sprites were drawing at
  the wrong size and 80 blurry) · the outfit procedure written into the `player-sprites` skill, with commands that
  reproduce the approved runs · ~~copper as the test batch~~ (done 2026-09-26: 5 calls, approved) · the other seven picked
  outfits, batch by batch, each asked for · GDD §08 (outfit decisions) and §21 (art direction). After the GDD
  sign-off: the remaining outfits, the 11 NPCs, then the world + item regeneration (a sizing rule first, then test
  batches per category, then zone by zone — only content the GDD keeps).
- **GDD, one section at a time:** premise & pillars (+ audit of mammal-derived content) · multiplayer & hosting ·
  world & zones · progression · bestiary · ecology + Ecology tab · bug farming & catching · farming · combat ·
  gear · tools & weapons · crafting · food & potions · electricity · fishing · mining · building & private plots ·
  NPCs & economy · exploration & secrets · time & weather · UI · art direction · audio · then 20 zone bibles.
- **Engineering, in dependency order:** ~~zone-link lint~~ (done 2026-09-26: `zone_links_test.go`; two missing
  return links added — bee meadow ↔ ant tunnels, ant tunnels ↔ underground passages) · saves: ~~versioning,
  migration~~ (done 2026-09-26: upgrade old, refuse newer, back up before upgrading), ~~rolling backups, periodic
  character saves~~ (done 2026-09-30, D73) · hosting spike → standalone Nakama-compatible server + Host/Join
  + world list + version handshake · zone-complete collision/loading (+ ecology re-tune) · world clock ·
  frozen-zone catch-up (+ border events from frozen neighbours, D57) · blocked zone entry · latent bugs (~~WorldEnter
  race~~ fixed by D73, first-join seq stall, merge ignores nests) · reconnect · CI + release builds · internet-reality test (latency,
  bandwidth) · **a thorough review of what still runs on the server** — each piece justified now that the players'
  computers run the simulation in step (D58); it comes BEFORE the frozen-zone catch-up, border events and cross-zone
  migration, which all depend on what the server runs (§19 P10) · no limit on characters per account ·
  ~~**characters saved every few minutes and at zone shutdown**~~ — **done** (D73, 2026-09-30, §19 P5): a clean stop
  saves each zone with its players; each zone saves together with everyone in it every minute, on leaving and after a
  sleep, through one ordered queue; one live copy per zone; a character enters the next zone only once the last one
  has saved it; rolling backups of every zone and character, and a restore command that keeps a safety copy first.
  Follow-ups in BACKLOG ("saves follow-ups").
- **Examine view + examine texts:** an examine view for items, recipes and bugs, and ~650 short texts with the real
  biology (owner decision: examining an item or recipe shows what it does); today hovering
  shows only the name and 2 of 654 things have a description. Written alongside the art redo, category by category.
- **Polish audits** (findings only): bug behaviour, combat, ecology + tab, UI, farming, catching, stations,
  building, lighting/weather, audio, tutorials, performance — every system gets a polishing pass with suggestions
  (D59). **True-bug naming pass.** **The item table** — recommended additions, changes and cuts for every item (D55).

### Phase 2 — the existing world to FINAL quality (the calibration slice)
Village, Bee Meadow, Mining Camp, Ant Tunnels, Ant Colony (4,0) + Queen — each redesigned from its finalized zone bible
(D53) — plus the systems that land with them (progression backbone, armour + stats, catching gear + bug storage,
cooking + potions basics, fishing in the village (D51), ecology stations + tab, tutorials, private plots + City Hall, the whole-outfit player art
in the game (its own plan: published size, equip model, starter outfit, tool motions — owner decisions in GDD §08),
the regenerated world art for these zones, cross-zone migration). Every scene is redone, the buildings better
planned, starting from where each zone stands — the groundwork for the new zones (owner, 2026-09-29, D69). Test
zones and the assistant's own testing tools (Unity's command line, screenshots) grow alongside, as ongoing work
rather than backlog items. Timed → the real estimate for Phase 3.

### Phase 3 — new zones in rings, each a complete package
Ring B: Wasp Thicket, Butterfly Fields, Hilltop Meadow, Centipede Cavern, Underground River ·
Ring C: Locust Farmland + western town + electricity, Millipede Forest, Scorpion Rocks, Shallow Swamp, Deadly Ants
outpost, deep river · Ring D: Spider Vales + spiders/silk/stealth, Deep Swamp, Deadly Ants core, the underground
fortress + legendary sets. Across the rings (D72): pockets of new decorations and recipes in some zones (the western
town's western style, for one), secret and rare ones elsewhere, and a couple more human places — the Wasp Thicket's
ranger outpost, perhaps a castle or similar in Spider Vale. Items are added as each zone is designed.

### Phase 4 — whole-game polish, balance, QA, release
Solo + hosted playthroughs; economy/ecology/combat balance; stress test (sync + FPS + tick + bandwidth at big
populations); cross-platform determinism; save migration; audio/music (a sound library and zone music made in code,
plus the owner's music packs — D60); legal (audio licence, AI disclosure); launch.

## Key design calls (researched + critic-reviewed 2026-09-26)
- **Bugs crossing zone edges = swarm-level migration.** Bugs stay inside their zone unless their swarm is
  migrating; the server decides migration per species (overcrowding, hunger, fleeing, random crossing events),
  can split off a small group (even one bug) that becomes its own swarm, and hands the swarm over whole once it
  has flown past the line — nothing vanishes in view, no one-bug fragments. "Migrating" = a movement leg aimed
  out of bounds (no new sync field — leg fields are relayed through fixed structs and a new one would be
  dropped). Exactly-once hand-off: each zone's save + the inbox record in one Nakama transaction. Three critic
  rounds: direction sound; five remaining fixes are specified in the design doc.
- **Frozen zones catch up on first visit** before the first player's baseline is sent (sync-safe: an empty
  zone's sync state is fully reset), with a server-side predation stand-in (predation kills are normally
  reported by a player's client).
- **One world clock** via the existing per-zone `DayOffsetTicks` (the client bug sim never reads time of day).
- **Blocked zone entry** (measured: 88 walkable crossing points land on solid cells, 35 boxed in) → the server picks
  the nearest walkable cell reachable from that edge and never strands the player (a failed join keeps you where you
  were — latent bug 6); zone builds check that the openings on both sides of a shared edge line up.
- **Hosting like Terraria:** a small Nakama-compatible Go server (the Unity client + test tools unchanged),
  Host & Play launches it, IP join + Epic's free relay first, Steam later. Measured bandwidth ≈ 2 KB/s per
  player in a busy zone.

## Latent bugs found 2026-09-26 (verified in code)
1. ~~Unknown zone → silently becomes `village_21` and writes its save~~ — **fixed** (26d704a).
2. ~~`world_enter` has no lock → two players entering at once can create two copies of a zone~~ — **fixed** (D73,
   2026-09-30: one live copy per zone, `zone_lease.go`).
3. Possible first-join stall on fresh zones (MatchInit emits events; the first joiner is told there are none).
4. Swarm merge ignores nests → a nest's patrol can be absorbed; the nest then regrows one (population inflation).
5. ~~A save-version bump discards every existing save~~ — **fixed** (save formats upgrade step by step; newer or
   unreadable saves are refused, never overwritten).
6. ~~**Crossing into a zone that won't start strands the player**~~ — **fixed** (D73, 2026-09-30) as proposed below:
   the game reads the reply and goes back to the zone it left (tested by `tools/run_crosstest.sh`). Still open: if
   that zone can't be entered either (the server stopping, say), the player is left in no zone. (Found 2026-09-26
   while researching GDD §01, by code reading:) the client leaves the old zone before joining the new one
   (`CrossZoneController.Swap`), and the server sends its errors back as normal replies (`rpc/world.go`
   `errorResponse`), so a refused join throws after the old zone is gone. A zone refusing to start is now a real
   case (a save from a newer build, or an unreadable one — item 5). Fix: check the reply, and on failure rejoin the
   old zone at the spot the player left.

## Open plans not yet scheduled above
- **Grass overhaul** — phase 1a and a simple tuft layer shipped 2026-07-26 (`grass_01` + variants + tufts in every
  zone); 1b–1c and phases 2–5 (colour variation, normal maps, motion, the dense detail layer, …) not started:
  `docs/plans/grass-overhaul.md`. The shipped grass is 16 px per square,
  so it is also part of the art regeneration.
- **Swing design, phase 6** (up to 5 more outfits from the catalog) — not started; the spring swing itself is
  designed but not in the game: `docs/plans/swing-design-and-outfits.md`.
- **Repo-health enforcement, P7** (visual checks, loop engineering, skill evals) — the last phase, not started:
  `docs/plans/repo-health-enforcement.md`.
