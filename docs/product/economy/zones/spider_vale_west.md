# Zone Content Sheet — Spider Vale West

> **Grid (0,2)** · a webbed cave-mouth vale of strung silk, gorse, and shadowed ledges · **difficulty EXTRA
> HARD** · **tier T4 (steel era, reaching toward T5 — silver/gold)**
>
> The **silk + web + agility** zone. West of the rocks the land funnels into a narrow vale choked with
> dew-strung orb-webs hung between the gorse and the gaping cave-mouth at its head — the home of the game's
> **spiders**. Where Scorpion Rocks taught *mining and venom prep*, Spider Vale West teaches **agility under
> ambush**: the webs slow you and pin you, the spiders are *fast* (wolf spiders rush, jumping spiders pounce
> from ledges, orb weavers drop on a dragline), and survival is about **dodge, mobility, and reading the
> ambush** rather than out-tanking it. The payoff is the game's **premium silk economy** — `spider_silk`
> (already foraged scrap in the Butterfly Fields) becomes a *real harvested resource* here, refines into the
> **best cloth/armor in the game so far**, and anchors a **light + dodge** armor identity that contrasts the
> heavy Prospector's Rig plate. This is also where **web-traps** debut (you weaponize the spiders' own silk),
> a **venom weapon tier** off `spider_venom`, and the **Hunter's Lodge** — the silk-trade vendor. Everything is
> gated **T4** (steel + this zone's drops), with the marquee pieces reaching **T5** (silver/gold).
>
> **Design intent (pacing, per `../README.md` + `../progression.md` §"Late"):** you don't brute-force the vale.
> You bring `web_resist`/`dodge` gear, a venom answer, and the agility to slip an ambush — *then* the webs
> become a silk farm and the spider dens a premium-cloth supply. This is the T4→T5 hinge: the first place
> silver/gold gear is reachable, and the **Silk-Stalker** set is the reward that carries forward. Generous
> content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat vocab
> + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T4→T5 "Late" / silk + agility); shop seam from
> [`../merchants.md`](../merchants.md) (the **Hunter's Lodge** — silk-trade vendor at the vale mouth).
> World-guide species: orb weavers, wolf spiders, jumping spiders, harder centipedes. Silk lineage:
> `spider_silk` / `moth_silk` from [`./butterfly_fields.md`](./butterfly_fields.md).

---

## Species & drops

Six concrete species span the EXTRA-HARD curve — a web-anchored ambusher, a rushing ground hunter, a leaping
ledge-stalker, a hardened centipede line, a web-tending nuisance, and a den mini-boss. Behaviors reuse the
existing arthropod vocabulary (anchor-and-patrol, rush/flank, ambush-pounce, swarm, dodge/flee) — the new
*twist* is **webs as a battlefield primitive** (slow/pin zones) and **high-dodge enemies** that punish slow
swings. The signature theme is **premium silk** (best cloth in the game) plus **agile ambush** and a hotter
**`spider_venom`** tier.

| Species (id) | Tier feel | Behavior | Primary drop — new | Secondary drop(s) |
|---|---|---|---|---|
| `orb_weaver` (`orb_weaver`) | core ambusher | Anchored to a big `orb_web` strung across the vale gaps. Sits center-web; when you snag the web (a `webbed` slow/pin zone) it **drops on a dragline** and strikes, then hauls back up. Patient, lethal if you're stuck. The **premium-silk source** — its web is the richest `spider_silk`. | `orb_silk` ✅(new) | `spider_venom` (uncommon, new), `dead_spider` (new) |
| `wolf_spider` (`wolf_spider`) | core threat | No web — a **ground rusher** that stalks then **sprints** the last gap in a burst; hunts in loose packs across the vale floor. High move speed, low dodge; punishes you for facing the wrong way. The bread-and-butter "fast melee" threat. | `wolf_fang` ✅(new) | `spider_venom` (uncommon, new), `chitin` ✅, `dead_spider` (new) |
| `jumping_spider` (`jumping_spider`) | agile harasser | Perches on ledges and gorse; **pounces** across a gap onto you (a leap-and-strike), then **dodges away** (very high `dodge`) before re-perching. Hard to pin down — a *spacing/timing* catch. Big-eyed; its eyes are a `crit`/precision charm drop. | `jumping_spider_eye` ✅(new) | `spider_silk` ✅, `dead_spider` (new) |
| `armored_centipede` (`armored_centipede`) | bruiser (harder centipede) | The vale's **hardened centipede** — longer, plated, faster than the swamp's. Coils, anchors to crevices and web-litter, and **lashes** with a venom bite; tanky, shrugs light hits. Solitary-ish, heavy-hitting; the "harder centipede" the world-guide promises. | `centipede_plate` ✅(new) | `centipede_venom` (new), `dead_centipede` ✅ |
| `web_tender` (`web_tender`) | swarm / nuisance | Small `pholcus`-style cellar/cobweb spiders that **tend and re-spin** the vale's webs — they cluster, repair `orb_web` you've cut, and re-`web` cleared lanes. Fragile, low value singly, but a *cluster* catch and the reason the webs keep coming back (cut the tenders to keep a lane open). | `cobweb` ✅(new, material) | `spider_silk` ✅, `dead_spider` (new) |
| `vale_matron` (`vale_broodmother`) | **mini-boss** (spider brood) | The **signature fight** — a bloated broodmother orb-weaver anchored to the **great web** across the cave-mouth at the vale's head. Sheathed in webbing; **spawns `wolf_spider`/`web_tender` adds** and re-webs the arena, then drops to fight with a fast multi-strike + a **web-snare AoE** (a big `webbed` pin zone) and a venom-spray. Beating her opens the cave and the premium-silk motherlode. | `silk_gland` (guaranteed, 1–2, new) | `broodmother_silk` ✅(new), `spider_egg_sac` (×2–4, new), `matron_fang` (rare trophy, new) |

**Drop notes**
- **`orb_silk`** (orb_weaver) is the **premium raw thread** — a tier above the Butterfly Fields' foraged
  `spider_silk` scrap. Refined at the loom it makes the best cloth in the game so far. `spider_silk` ✅ still
  exists (the common forage/`web_tender` drop); `orb_silk` is the *high-grade* harvest. `broodmother_silk`
  (mini-boss) is the **rare/upgraded** top thread, gating the marquee T5 pieces — a clean three-tier silk
  ladder: `spider_silk` → `orb_silk` → `broodmother_silk`, mirroring the venom ladder below.
- **`spider_venom`** is this zone's **strong venom material** (off `orb_weaver`/`wolf_spider`) — a tier hotter
  than Scorpion Rocks' `scorpion_venom`, anchoring the venom-weapon line. `centipede_venom` is the
  armored-centipede's separate, paralytic-flavored venom (a *slow/stun* coating vs. the spiders' DoT).
- **`wolf_fang`** / **`jumping_spider_eye`** / **`centipede_plate`** are species-signature crafting drops
  (fang → venom weapons + grip; eye → `crit`/precision charm; plate → light armor plating). `silk_gland`
  (mini-boss) is the **artisan refining catalyst** (spins raw thread into the highest-grade silk).
- `chitin`, `spider_silk`, `dead_centipede` are **existing ids** — reused. `dead_spider` is the new carcass
  drop in the existing `dead_*` family. `cobweb` is a raw material (see below), dropped by `web_tender` and
  cut from webs.
- `spider_egg_sac` (brood) + `matron_fang` (rare trophy) round out the mini-boss table — the "I cleared the
  vale" flex + a venom/silk input and a wall trophy.

**Drop → use at a glance**
- `orb_silk` → the premium cloth bolt (`spider_silk_cloth`) → the whole silk-armor + artisan-cloth line.
- `broodmother_silk` → the **T5** marquee cloth/cape (the keystone Silk-Stalker piece).
- `silk_gland` → the loom catalyst that refines raw thread into top-grade silk (gates `broodmother_silk` use).
- `spider_venom` → the strong venom weapons/coatings (this zone's offense).
- `centipede_venom` → a **paralytic** (slow/stun) coating — a different control answer than the DoT venom.
- `wolf_fang` → fanged daggers/spears + grip pieces on the agility gear.
- `jumping_spider_eye` → a `crit_chance`/`dodge` precision charm + a décor/scope lens.
- `centipede_plate` → light, flexible armor plating (the Silk-Stalker's defense without weight).
- `cobweb` → the **web-trap** structures (you weaponize the spiders' silk) + a cheap binder/net mesh.

**Catch/combat teaching:** orb weavers teach *don't get stuck* (web pins, dragline drops), wolf spiders teach
*watch your back / face the rush*, jumping spiders teach *spacing & timing vs. high dodge*, armored centipedes
teach *commit to the heavy threat*, web tenders teach *clear the support to hold a lane*. Together they make
the vale a **dodge-and-mobility** test where standing still is death — exactly the fantasy the Silk-Stalker set
pays off.

---

## New ingredients & materials

Silk-, web-, and venom-themed resources — most **harvested from webs/dens or refined at the loom/cauldron**,
a few foraged from the vale flora. Source = `drop` (from a bug/web), `forage` (pick), `mine` (break a node),
`craft` (refined). Premium silk/venom sit high on the cost-point scale per the brief; raw scrap stays cheap.

| Id | Source (find@spider_vale_west) | Cost-pt | Use |
|---|---|---|---|
| `orb_silk` | drop/harvest — cut from a center `orb_web` or the `orb_weaver` (the premium raw thread) | 6 (silk-tier) | The **premium cloth bolt** input → `spider_silk_cloth` → all silk armor/artisan goods. The zone's headline resource. |
| `cobweb` | drop/forage — pulled from cobwebs & the `web_tender`'s repairs (raw matted web) | 1 | The **web-trap** structures + a cheap binder, net-mesh patch, and stuffing; the bulk silk filler. |
| `spider_venom` | drop — `orb_weaver`/`wolf_spider` (the strong venom; hotter than `scorpion_venom`) | 10 (venom-minor) | The venom-weapon/coating line (strong `envenomed` DoT); a brew base for the antivenom. |
| `centipede_venom` | drop — `armored_centipede` (a separate **paralytic** venom) | 10 (venom-minor) | A **slow/stun** weapon coating + a paralytic trap charge (control, not DoT). |
| `silk_gland` | drop — `vale_matron` mini-boss (the refining catalyst) | 16 (gem-major) | Loom **catalyst** — spins `orb_silk`/`broodmother_silk` into the top-grade `refined_silk`; gates the T5 pieces. |
| `broodmother_silk` | drop — `vale_matron` (the rarest, strongest thread) | 16 (gem-major) | The **T5** marquee cloth/cape thread (Silk-Stalker keystone + the artisan flex bolt). |
| `gossamer_dew` | forage — dawn dew beaded on intact webs (a clarifying/light silk-soak) | 2 | A silk-soak that lightens/strengthens cloth (the `gossamer` quality tier); a clarity note for the dodge tonic; faint shimmer dye. |
| `gorse_thorn` | forage/mine — the spiny gorse choking the vale ledges | 1 | A thorn-spike for the `thorns` accessory + a barbed trap component; a cheap astringent for brews. |
| `cave_moss` | forage — phosphor moss in the cave-mouth shade (faint glow) | 1 | A light/`light_radius` décor + a `night_vision` note for the cave-explorer tonic; cheap green dye/binder. |
| `silver_ore` ✅ | mine — pale veins deep in the cave-mouth (reuse — the **T5 metal this zone opens**) | — | Reuse — smelt → `silver_bar` ✅; the silver this zone exists to reach (Silk-Stalker buckles, jeweler line). |
| `refined_silk` | craft (loom) — `orb_silk`/`broodmother_silk` + `silk_gland` catalyst, spun at the loom | — (intermediate) | The **gateway**: raw spider thread → the highest-grade usable silk; the premium cloth & all T5 silk gear flow through here. |
| `spider_silk_cloth` | craft (loom) — `refined_silk` + `thread`, woven (the premium cloth bolt) | — (intermediate) | The zone's **premium cloth** → every silk armor piece, the artisan cloth goods, and the net/cape line. |

> **Why these:** `orb_silk` + `silk_gland` + `broodmother_silk` form the **premium-silk ladder** the zone is
> built around (`refined_silk` → `spider_silk_cloth` is the bridge every silk good crosses); `cobweb` is the
> cheap bulk web that powers the **web-traps** (you turn the spiders' silk against them); `spider_venom` /
> `centipede_venom` give **two** offense answers (DoT vs. paralytic); `gossamer_dew` + `gorse_thorn` +
> `cave_moss` keep the **survival/quality** answers (dodge tonic, antivenom, thorns, light) cheap and always
> craftable so a careful player can stay alive — only the spicy silk/venom gear is gated. `silver_ore` is the
> reused vein that opens the **T5** metal tier this zone hinges on.

*(`orb_silk`, `cobweb`, `spider_venom`, `centipede_venom`, `silk_gland`, `broodmother_silk` from the species
table are bug/boss drops — listed here once to avoid duplication; their species sources are in the table above.)*

---

## Recipes debuting here

Ten recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; the floor is **T4** (steel + this zone's drops), with the
marquee silk/venom pieces reaching **T5** (silver/gold). `unlock`: **craft** (have station + recipe) /
**buy@hunters_lodge** / **find@spider_vale_west**.

### Silk & cloth (the premium-silk line — the zone's headline)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `spider_silk_cloth` | loom | `refined_silk` ×2, `thread` ×2 | craft | The **premium cloth bolt** → all silk armor/artisan goods (the best cloth in the game so far) | T4 |
| `gossamer_cloth` | loom | `spider_silk_cloth` ×1, `gossamer_dew` ×2 | craft | Dew-lightened premium cloth — lighter & stronger (the `gossamer` quality bolt for the T5 cape) | T4→T5 |
| `silk_robe` (body, artisan soft-good) | loom | `spider_silk_cloth` ×2, `thread` ×2, `silver_bar` ✅ ×1 | craft / buy@hunters_lodge | `defense +4`, `dodge_chance +4`, `move_speed_pct +3` — the light artisan armor robe | T4→T5 |
| `silk_net` ✅ (T4 net upgrade) | workbench | `steel_bar` ✅ ×2, `orb_silk` ×4, `spider_silk_cloth` ×1 | craft / buy@hunters_lodge | `catch_radius +3`, `catch_arc +20°`, `catch_cap +8`, `rare_bug_luck +1` — premium spider-silk net | T4 |

### Armor — the Silk-Stalker line (light + dodge; see the set section)

| Output (id) | Slot | Station | Inputs | Unlock | tier |
|---|---|---|---|---|---|
| (Silk-Stalker pieces are listed in **Signature gear** below — `stalker_hood`, `stalker_garb`, `stalker_treads`, `stalker_cape`.) | | | | | T4→T5 |

### Weapons — strong venom + paralytic (the offense tier)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `fang_dagger` (light blade, fast) | forge | `steel_bar` ×2, `wolf_fang` ×3, `spider_venom` ×2 | find@spider_vale_west (recipe scroll) | `damage_pct +18`, `attack_speed_pct +12`, `crit_chance +6`, **on-hit `envenomed`** (strong DoT); fast light weapon that suits the dodge build | T4 |
| `venom_glaive` (reach polearm) | forge | `steel_bar` ×2, `centipede_plate` ×3, `spider_venom` ×2 | buy@hunters_lodge (recipe) | `damage_pct +24`, `knockback +1`, long reach (anti-rush spacing vs. wolf spiders), strong `envenomed` on-hit | T4 |
| `paralytic_coating` (weapon coating, consumable) | cauldron | `centipede_venom` ×1, `cobweb` ×1, `gorse_thorn` ×1 | craft | **Coats your weapon** — on-hit **slow/`webbed`-lite** (paralytic) for a duration; the control answer to fast packs | T4 |
| `venom_oil` ✅ (coating, consumable) | cauldron | `spider_venom` ×1, `resin_glob` ✅ ×1, `gossamer_dew` ×1 | auto (cauldron + zone access) | **Coats your weapon** — adds strong `envenomed` on-hit (upgrades any blade to spider-venom tier); reuses the existing coating, refreshed to spider venom | T4 |

### Web-traps & agility accessories (you weaponize the silk)

| Output (id) | Station | Inputs | Unlock | Stat / bonus / tag | Tier |
|---|---|---|---|---|---|
| `web_trap` (deployable structure) | workbench | `cobweb` ×3, `gorse_thorn` ×2, `plank` ×1 | craft / buy@hunters_lodge | **Deployable** — lays a `webbed` zone that **slows & pins** bugs that enter (turns the spiders' own web against them); a catch-aid + a kiting tool for the packs | T4 |
| `snare_charge` (paralytic trap charge) | workbench | `cobweb` ×2, `centipede_venom` ×1, `gorse_thorn` ×1 | craft | Upgrades a `web_trap` to a **paralytic snare** — bugs caught are briefly stunned (the boss/centipede answer) | T4 |
| `stalkers_charm` (accessory) | jeweler | `jumping_spider_eye` ×2, `silver_bar` ✅ ×1, `gossamer_dew` ×1 | buy@hunters_lodge (recipe) | `dodge_chance +5`, `crit_chance +5`, `move_speed_pct +3` — the **agility/dodge trinket** (the jumping-spider precision charm) | T4→T5 |
| `thorn_band` (accessory) | jeweler | `gorse_thorn` ×3, `centipede_plate` ×1, `silver_bar` ✅ ×1 | craft / find | `thorns +3`, `defense +2`, `knockback +1` — punishes the rushers who close on you | T4→T5 |

### Survival — venom / web answers (the "answer to the zone")

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `spider_antivenom` | cauldron | `gorse_thorn` ×2, `cave_moss` ×1, `spider_venom` ×1 | buy@hunters_lodge (recipe) | **Cures `envenomed`** + short `hazard_resist` (resists new venom) — the answer to the spiders | T4 |
| `silk_cutters` (utility tool/consumable) | workbench | `steel_bar` ×1, `gorse_thorn` ×2 | craft / buy@hunters_lodge | Sustained **`web_resist`** while held/active — you walk through `webbed` zones without the slow/pin (cut your way clear) | T4 |
| `gossamer_tonic` (drink) | cauldron | `gossamer_dew` ×2, `cave_moss` ×1, `mint` ✅ ×1 | craft | Timed **`dodge_chance +3`, `move_speed_pct +4`** self-buff — the agility brew for an ambush push | T4 |
| `spider_jerky` (food) | cooking_pot | `dead_spider` ×1 *(or any `dead_*` bug-meat)* + `gorse_thorn` ×1 + `sage` ✅ ×1 | craft | Long-duration `max_hp +6` / `hp_regen +1` buff (the preservation payoff carried from the rocks) | T4 |

### Artisan cloth & décor / structure (loom / sawmill / jeweler — the silk flex)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `silk_tapestry` | loom | `spider_silk_cloth` ×2, `gossamer_dew` ×1 | craft | Premium wall décor (comfort/idle aura tag) — the artisan-silk flex piece | T4 |
| `web_lantern` | jeweler | `cave_moss` ×2, `silver_bar` ✅ ×1, `glass` ✅ ×1 | craft | Light décor — a glowing silk-strung lantern (`light_radius` aura), the cave-mouth flex | T4 |
| `silk_cushion` | loom | `cobweb` ×3, `spider_silk_cloth` ×1 | craft | Comfort décor (idle aura) — cheap web-stuffed cushion line | T4 |
| `gorse_hedge` ×4 | sawmill | `gorse_thorn` ×4, `plank` ×2 | craft | Structure — a thorny barrier hedge (defensive décor / pen wall) | T4 |

> **Supply logic:** `orb_silk` (premium drop) → `refined_silk` → `spider_silk_cloth` is the bottleneck spine on
> *every* silk good; `silk_gland` + `broodmother_silk` (mini-boss) gate the top-grade `gossamer_cloth`/T5 cape
> and are held as the **forward hook**. `cobweb` (cheap bulk) powers the web-traps and the décor; `spider_venom`
> gates offense; `centipede_venom` gives the paralytic alternative; the common gatherables (`gorse_thorn`,
> `cave_moss`, `gossamer_dew`) keep **survival** (antivenom, `silk_cutters`/`web_resist`, dodge tonic, jerky)
> cheap and always craftable. The `silk_cutters`→`web_resist` line is the literal "answer to the zone's webs."

---

## Signature gear — the **Silk-Stalker** set (T4→T5 bonus set)

A 4-piece light spider-silk outfit: gossamer-woven garb over flexible `centipede_plate` scales, a fanged
hood, dragline-grip treads, and a billowing broodmother-silk **cape**. Theme = **the agile silk-stalker who
slips every ambush and strikes from the dodge**. This is a *light + dodge + mobility* set — the deliberate
contrast to the Prospector's Rig's heavy heat-plate. Its signature stats are **`dodge_chance` +
`move_speed_pct` + `crit_chance`** with *light* `defense` (you survive by not getting hit, not by tanking).
Built at the **loom** (the premium silk weave) + a **jeweler** inlay (the silver buckles / spider-eye lens) —
a silk-led set that shows off the zone's identity. The hood/garb/treads are pure **T4** (steel + drops); the
**cape** reaches **T5** (`broodmother_silk` + `gold_bar`), making the set the T4→T5 hinge.

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `stalker_hood` | head | loom | `spider_silk_cloth` ×2, `wolf_fang` ×1, `jumping_spider_eye` ×1 | `defense:2, dodge_chance:4, crit_chance:3, night_vision:1` | `silk_stalker` |
| `stalker_garb` | body | loom | `spider_silk_cloth` ×3, `centipede_plate` ×2, `silver_bar` ✅ ×1 | `defense:4, dodge_chance:5, move_speed_pct:3, max_hp:4` | `silk_stalker` |
| `stalker_treads` | feet | loom | `spider_silk_cloth` ×1, `orb_silk` ×2, `gossamer_dew` ×1 | `defense:2, move_speed_pct:5, dodge_chance:3, web_resist:1` (dragline grip) | `silk_stalker` |
| `stalker_cape` | back/cape | loom | `gossamer_cloth` ×1, `broodmother_silk` ×2, `gold_bar` ✅ ×1, `silk_gland` ×1 | `defense:3, dodge_chance:6, crit_chance:5, move_speed_pct:4` | `silk_stalker` |

**Set bonus (`set: silk_stalker`, all 4 worn):**
> *"Never where the strike lands."*
> - **+`dodge_chance +8`**, **+`move_speed_pct +6`**, **+`crit_chance +6`** (the agility payoff),
> - **full `web_resist`** — the vale's webs stop slowing/pinning you entirely (`webbed` zones, including the
>   matron's snare AoE, no longer hold you),
> - **a dodge grants a brief "dragline" burst** — a successful `dodge_chance` proc gives a short
>   `move_speed_pct` + `crit_chance` window (reposition-and-punish), turning evasion into offense.
> - **Fantasy realized:** fully kitted you flow *through* the webbed vale untouched — slipping the orb-weaver's
>   dragline drop, dodging the wolf-spider rush and the jumping-spider pounce, then punishing the whiff with a
>   crit from your fang dagger. The vale goes from a lethal ambush corridor to a generous, self-stocking
>   **premium-silk farm**. That agility spike is the reward for clearing the zone — and it carries straight
>   into the next, deeper zone.

**Unlock:** hood + treads recipes **auto** at the loom (you can grind those yourself); the **garb** recipe is
**bought from the Hunter's Lodge**; the **cape** recipe is **dropped by the `vale_matron`** (mini-boss) — so
the T5 keystone rewards beating the broodmother (and needs her `broodmother_silk` + `silk_gland` to build).

> Optional matching accessory: `stalkers_charm` (jeweler — see recipes): `dodge_chance +5`, `crit_chance +5`,
> `move_speed_pct +3`. The natural 5th-slot stretch that deepens the agility identity; pairs with `fang_dagger`
> + `thorn_band` for a full dodge-crit build. Prune if the 4-piece reads cleaner.

---

## Shop / NPC stock — **the Hunter's Lodge** (`hunters_lodge`)

A timber-and-silk lodge perched at the **safe vale mouth**, hung with strung specimen-webs and silk bolts. A
veteran spider-hunter runs it: she **trades in silk** (the premium-cloth economy hub), sells the **agility
gear, web-trap recipes, venom answers, and the keystone Silk-Stalker recipes**, sells the **silver/gold you
can't yet mine at a markup** (the T5 bridge metals), and **buys your silk & venom high** — the reason to
over-harvest the webs. Currency = coins (existing). She is the gate that teaches "kit up for the ambush before
you push the cave-mouth."

**Sells (buy@hunters_lodge):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: silk_net` | recipe | 240 | The premium spider-silk net — the headline catch upgrade. |
| `recipe: stalkers_charm` | recipe | 300 | The agility/dodge trinket. |
| `recipe: spider_antivenom` | recipe | 200 | Cures `envenomed` — the survival recipe. |
| `recipe: venom_glaive` | recipe | 360 | Reach venom weapon (anti-rush spacing). |
| `recipe: silk_robe` | recipe | 320 | The light artisan armor robe. |
| `recipe: web_trap` | recipe | 180 | Weaponize the silk — the deployable trap. |
| `recipe: stalker_garb` | recipe | 460 | Keystone set piece (the bought path; cape is the boss drop). |
| `spider_antivenom` | consumable | 40 | Pre-made; stock-limited daily (forces gathering too). |
| `silk_cutters` / `gossamer_tonic` | consumable/tool | 70 / 35 | `web_resist` + the agility brew on hand before you craft them. |
| `silk_net` | gear | 220 | Pre-made premium net so you can catch immediately. |
| `silver_bar` ✅ / `steel_bar` ✅ | material | 90 / 55 | Convenience restock of the bridge metals (small daily cap, markup). |
| `gold_bar` ✅ | material | 180 | The T5 metal you can't yet mine — for the `stalker_cape` stretch (capped). |
| `loom` / `jeweler` (station) | station | 240 / 280 | Buy-the-station convenience for the silk-cloth + inlay lines. |

**Buys (sell to vendor — the zone's coin sink + over-harvest incentive):** `orb_silk`, `spider_silk` ✅,
`cobweb`, `spider_venom`, `centipede_venom`, `wolf_fang`, `jumping_spider_eye`, `centipede_plate`,
`gossamer_dew`, `silver_ore` ✅ — with a **`bug_value_pct` premium on silk & venom** (she pays top coin for
both, reinforcing the harvest-and-fight loop). `broodmother_silk`, `silk_gland`, and `matron_fang` sell
highest (the boss flex).

---

## "New toys" hook

Spider Vale West is where BugFarmer's **silk economy goes premium** and combat becomes about *agility, not
armor*. The new toys are all about *slipping the ambush and weaving the spoils*: the **`silk_net`** that finally
upgrades your catch with premium spider thread, **web-traps** (`web_trap` + `snare_charge`) that turn the
spiders' own webbing into a slow/pin/paralytic weapon, the **`fang_dagger`** and reach **`venom_glaive`** that
arm you with hotter `spider_venom`, and the survival kit — **`spider_antivenom`**, **`silk_cutters`**
(`web_resist`), the **`gossamer_tonic`** dodge brew — that takes the webbed, venomous vale from "this kills
slow runs" to "this is my silk farm." The capstone is the **Silk-Stalker** set, whose `dodge_chance` +
`move_speed_pct` + `crit_chance` bonus (with full `web_resist` and a dodge-into-crit dragline burst) lets you
flow untouched through the webs — slipping the orb-weaver's drop, dodging the wolf rush and the jumping
pounce, then punishing the whiff. Refine the webs into the best cloth in the game (`spider_silk_cloth` →
`gossamer_cloth`), drape a `silk_tapestry`, and trade silk at the Lodge for coin. Beat the `vale_matron` and
you walk out with **`broodmother_silk` + `silk_gland`** — the seed of the T5 cape and the next zone's higher
silk/venom tier — plus the `matron_fang` trophy for the wall.

---

## New id ledger

**materials:**
- `orb_silk` — drop/harvest, orb_weaver (premium raw thread; → refined_silk → spider_silk_cloth)
- `cobweb` — drop/forage, web_tender + cut webs (cheap bulk web; web-traps, binder, décor stuffing)
- `spider_venom` — drop, orb_weaver/wolf_spider (the strong venom; hotter than scorpion_venom)
- `centipede_venom` — drop, armored_centipede (separate paralytic venom; slow/stun coating)
- `silk_gland` — drop, vale_matron mini-boss (loom catalyst → refined/top-grade silk; gates T5)
- `broodmother_silk` — drop, vale_matron (rarest/strongest thread; T5 cape + artisan flex; forward hook)
- `spider_egg_sac` — drop, vale_matron (brood; venom/silk input)
- `matron_fang` — rare trophy drop, vale_matron
- `gossamer_dew` — forage@spider_vale_west (silk-soak/quality; dodge tonic, shimmer dye)
- `gorse_thorn` — forage/mine@spider_vale_west (thorns accessory + trap barb + astringent)
- `cave_moss` — forage@spider_vale_west (light décor + night_vision note + dye/binder)
- `refined_silk` — crafted intermediate (loom; raw spider thread + silk_gland → top-grade silk)
- `spider_silk_cloth` — crafted intermediate (loom; refined_silk + thread → the premium cloth bolt)

**species:** (id → primary drop)
- `orb_weaver` → `orb_silk` (also `spider_venom`, `dead_spider`)
- `wolf_spider` → `wolf_fang` (also `spider_venom`, `chitin` ✅, `dead_spider`)
- `jumping_spider` → `jumping_spider_eye` (also `spider_silk` ✅, `dead_spider`)
- `armored_centipede` → `centipede_plate` (also `centipede_venom`, `dead_centipede` ✅)
- `web_tender` → `cobweb` (also `spider_silk` ✅, `dead_spider`)
- `vale_matron` → `silk_gland` (mini-boss; also `broodmother_silk`, `spider_egg_sac`, `matron_fang`)

*(New `dead_*` carcass id in the existing family: `dead_spider`. New drop ids per the brief: `orb_silk`,
`wolf_fang`, `jumping_spider_eye`, `spider_venom`.)*

**items:**
- `spider_silk_cloth` — premium cloth bolt, loom, T4 — the silk-armor/artisan gateway
- `gossamer_cloth` — quality cloth bolt, loom, T4→T5 — dew-lightened (gates the T5 cape)
- `silk_robe` — armor (body, artisan), loom, T4→T5 — defense/dodge_chance/move_speed_pct
- `silk_net` ✅ — net (T4 upgrade), workbench, T4 — catch_radius/catch_arc/catch_cap/rare_bug_luck
- `fang_dagger` — weapon (light blade), forge, T4 — damage_pct/attack_speed_pct/crit_chance + envenomed
- `venom_glaive` — weapon (reach polearm), forge, T4 — damage_pct/knockback + reach + envenomed
- `paralytic_coating` — weapon coating consumable, cauldron, T4 — on-hit slow/stun (centipede_venom)
- `venom_oil` ✅ — weapon coating consumable, cauldron, T4 — adds strong envenomed (spider venom)
- `web_trap` — deployable structure, workbench, T4 — lays a webbed slow/pin zone
- `snare_charge` — trap upgrade, workbench, T4 — upgrades web_trap to a paralytic snare (stun)
- `stalkers_charm` — accessory, jeweler, T4→T5 — dodge_chance/crit_chance/move_speed_pct
- `thorn_band` — accessory, jeweler, T4→T5 — thorns/defense/knockback
- `spider_antivenom` — consumable, cauldron, T4 — cures envenomed + hazard_resist
- `silk_cutters` — utility tool/consumable, workbench, T4 — sustained web_resist (walk through webs)
- `gossamer_tonic` — drink, cauldron, T4 — timed dodge_chance/move_speed_pct
- `spider_jerky` — food, cooking_pot, T4 — long max_hp/hp_regen buff (preservation)
- `silk_tapestry` — wall décor, loom, T4 — comfort/idle aura
- `web_lantern` — light décor, jeweler, T4 — light_radius aura
- `silk_cushion` — comfort décor, loom, T4 — idle aura
- `gorse_hedge` — structure ×4, sawmill, T4 — thorny barrier hedge
- `stalker_hood` — armor (head), loom, T4 — defense/dodge_chance/crit_chance/night_vision; set: silk_stalker
- `stalker_garb` — armor (body), loom, T4 — defense/dodge_chance/move_speed_pct/max_hp; set: silk_stalker (bought keystone)
- `stalker_treads` — armor (feet), loom, T4 — defense/move_speed_pct/dodge_chance/web_resist; set: silk_stalker
- `stalker_cape` — armor (back/cape), loom, T4→T5 — defense/dodge_chance/crit_chance/move_speed_pct; set: silk_stalker (boss-drop keystone, needs broodmother_silk + gold_bar)
- `hunters_lodge` — NPC ("the Hunter's Lodge", silk-trade vendor) — premium-silk + agility-gear shop at the vale mouth
