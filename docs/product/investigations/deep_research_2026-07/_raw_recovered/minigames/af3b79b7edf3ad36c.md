I'll run several searches in parallel to find sources across all topics.

---

Good leads. Let me run more targeted searches for the remaining topics.

---

Gold Rush wiki was paywalled. Let me fetch alternate gold-panning and a richer combo source.

---

One more fetch to anchor the gold-panning verb with a cited page.

---

I fetched 7 full pages (2 came back thin/paywalled but usable). Here is the research.

# Short skill-check minigames for mining/stone/gem/panning — research findings

## Source table (URLs I actually WebFetched)

| # | URL (fetched) | Minigame | VERB | INPUT | LOOP timing | REWARD model | Skippable? | Downsides / criticism |
|---|---|---|---|---|---|---|---|---|
| 1 | oldschool.runescape.wiki/w/Motherlode_Mine | OSRS Motherlode Mine (pay-dirt wash) | mine → wash | click vein, click hopper; then AFK | vein depletes in 23–27s (upper 36–40s); pay-dirt reaches sack in 8s | ore (coal/gold/mith/addy/rune) + golden nuggets (3.13%/pay-dirt, ~1 per 32) + uncut gems (with amulet of glory) | Yes — semi-AFK, "less attention required"; processing needs no input | Wiki lists no criticism, but it's the archetypal "click-and-wait" low-engagement grind |
| 2 | whyigame.wordpress.com/.../atitd-the-bijou-and-gem-cutting | A Tale in the Desert — Test of the Bijou (gem faceting) | cut / subtract facets + rotate | keyboard: J/K rotate Z, U/I rotate Y, O/L rotate X; 3 saw-discs each make a different slice (flat / diagonal / compound-diagonal) | no hard timer per puzzle; underlying "cuttable gems" take 4–20 min to mine | Bijou (training) = "satisfaction + a little better at gem-cutting," no product; real cutting yields a finished gem | Not really — it's a deliberate puzzle | "Mistakes cannot be taken back. If you cut wrongly… you've screwed up." Also luck-gated: gems have flaws; wrong flaw pattern = "you can't cut that gem, go look for another." Hard part = camera management + not over-cutting |
| 3 | store.steampowered.com/app/2539820/LAPIDARY_Jewel_Craft_Simulator | LAPIDARY: Jewel Craft Simulator | rotate + lower/carve on lathe | rotate 3D raw stone, "carefully lower it onto the lathe," repeat to carve | untimed, relaxing | recipe gives target color+shape; "the more accurately you work, the better the rewards"; quality rating; gem named + added to collection | Zen/cozy — no time pressure, tagged "Relaxing/Cozy/Wholesome" | None stated; risk is the opposite — too low-stakes/repetitive |
| 4 | steamcommunity.com/app/1527950/discussions/.../5782106519351005323 + .../6222330214304790479 (Wartales forging) | Wartales blacksmith forging | strike (click-to-time) | click each glowing plate the instant it turns white (watch plate, not spark/sound — game fakes sound cues to bait early clicks) | ~0.5s perfect window per plate; 4 plates; ~6 speed tiers (fixed per attempt); higher-tier gear heats plates faster → smaller window | 4/4 yellow = 2-star (or 2→3-star upgrade); 3/4 = "1-star superior"; hidden RNG still varies Str/Dex mods even on identical perfect play; rare ~1–2% 3-star | No skip | "operates on or beyond [reaction] limit… forcing anticipation." "I don't play games in this genre to have my twitch reflexes tested." Accessibility barrier (cited: post-stroke coordination); a stuttering bug worsens it. Hidden RNG makes perfect play feel unrewarded |
| 5 | elena-berman.medium.com/mechanics-dynamics-and-aesthetics-of-fruit-ninja | Fruit Ninja (slice primitive) | swipe-slice | finger/mouse swipe = a "blade"; if the blade-trail arc collides with fruit it's sliced; one swipe hitting multiple fruit slices all of them | continuous, reflex-paced arcade sessions | score; high scores unlock cosmetic blades (e.g. sparkle-trail); combos reward multi-fruit swipes | Skill-expressive, not skippable | Article gives no criticism — praises simplicity; note: it's pure arcade, no quality/tier outcome, so as a *processing* primitive it needs a scoring layer bolted on |
| 6 | store.steampowered.com/app/451340/Gold_Mining_Simulator | Gold Mining Simulator (wash plant) | dig → wash → upgrade | store page thin: "start with a simple bucket and a hog pan," buy "more efficient wash plant parts" | not stated | earnings scale with wash-plant tier | Progression replaces manual effort (better plant = more auto throughput) | Storefront omits the loop; genre reputation is grindy repetition |

*(Supplementary, from search summaries not a full fetch — flagged so it's not mis-cited): Gold Rush: The Game's manual pan is a multi-step verb chain — fill basin with water → fill bucket → wash mats in bucket → pour concentrate into pan → move/rotate the pan up-and-down with keys to wash lighter material off and leave the gold. It's the most literal "swirl/tilt to separate" input model.)*

## Synthesis — patterns useful for a Bug Farmer processing minigame

**Five input archetypes emerge, on a skill↔zen axis:**

1. **Click-to-time a moving window (twitch)** — Wartales forging. One button, a ~0.5s window, multi-hit (4 plates), difficulty = shrinking window. Highest skill expression and the shortest per-action loop, but the most divisive: it tests reflexes, is inaccessible to some players, and Wartales' hidden RNG on top of perfect play is a cautionary tale — *if you gate reward on a perfect hit, the perfect hit must fully own the reward.*

2. **Wash-and-wait / deposit (AFK-lite)** — Motherlode Mine. Player action is trivial (click, deposit); the "minigame" is really a throughput/queue. Low engagement, but proven for a repeatable resource loop where the fun is elsewhere. Good if processing is background, bad if it's meant to be the spotlight.

3. **Rotate-and-carve precision (chill mastery)** — LAPIDARY / ATITD Bijou. Rotate the stone, apply a cut, match a target silhouette. No timer; skill = spatial reasoning + not over-cutting. ATITD's *irreversible cut* raises stakes elegantly (one wrong cut ruins the gem) — a strong lever, but pair it carefully with material scarcity or it feels punitive.

4. **Swipe-slice along a path (juice-forward)** — Fruit Ninja. The best *slicing primitive*: draw a stroke, collision along the trail resolves the cut, multi-target combos reward good arcs. Massively satisfying feedback (particles, squelch, whoosh) but carries no native quality tier — you must add the scoring layer (e.g. "slice along the facet line" = closeness of the swipe to the guide line → quality).

5. **Swirl/tilt to separate (simulation verb)** — Gold Rush panning. Most thematically literal for panning, but the multi-step chain (fill/wash/pour/rotate) trends toward tedium; better compressed to the one interesting beat (the tilt-and-wash), not the whole real-world procedure.

**Cross-cutting design lessons for a SHORT skill-check:**

- **Reward tiers, don't gate binary.** The good ones map performance to a *quality tier* (Wartales stars, LAPIDARY accuracy rating) rather than pass/fail — keeps a bad run still productive.
- **Perfect must be honest.** Wartales' hidden RNG after a flawless minigame is the top-cited frustration; if you show a "perfect," pay the perfect.
- **Difficulty scales by tightening one knob** (window size, plate speed, target complexity) — not by adding steps.
- **Skippability is a spectrum:** twitch games resist automation (skill = the content); wash/deposit loops naturally become AFK. Decide up front whether mastery should let players *auto-resolve* (respect their time) or whether the minigame IS the fun (keep it manual). A common polish move: let a mastered player one-tap "perfect" once they've proven they can.
- **The Fruit-Ninja "slice along a line" is the strongest fit** for a gem-cut/stonecut *slicing* verb — swipe-to-cut with trail collision, then score by how close the swipe tracked the intended facet line, with juicy split-apart feedback. It's short, skill-expressive, and reads instantly.

Load-bearing note on sourcing: the Gold Rush: The Game panning detail (fill→wash→pour→rotate) came from a WebSearch summary, **not** a full page fetch (the fandom page returned HTTP 402), so I've flagged it separately and not put it in the fetched-source table.