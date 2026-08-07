# Character Design Guide for Bug Farmer

## AS BUILT (2026-06-12): 16x32 region-template paper-doll — READ THIS FIRST
The layered player SHIPPED at the game's existing **16x32** canvas (Andrew's
call: keep the current resolution), not the 32x48 proposed below. How it works
(`tools/player_sprites/`):
- Sprites are **text grids** (char-per-pixel, `pixkit.py` legend); every body
  pixel carries a REGION tag (skin/hair/shirt/pants/boots). ONE hand-authored
  idle master per direction (`body_frames.py`); right = mirrored left.
- **Layers derive from the master by region filtering** (each layer carries the
  outline pixels adjacent to its region) — registration is perfect by
  construction. The body layer substitutes clothing regions to skin + a linen
  shorts band (row-aware), so the unclothed base has no holes.
- **Walk cycle** [contact-L, idle, contact-R, idle] derives mechanically:
  half-row leg shifts (rows 25-31) + 1px head bob (rows 0-13). NO arm swing
  (read as an artifact). Files: `{set}_{dir}.png` (idle, the pre-existing
  names) + `_w1`/`_w3` contacts.
- **Wearables** (`wearables.py`): overlay grids on the same canvas; head items
  are pre-composed with the bob per frame; `HIDES_HAIR` lists full helms.
- **16x32 anchor rows**: hair 1-5 · face 6-12 (eyes 8-9) · neck 13 ·
  shoulders 14 · torso 15-22 · waistband 23 · legs 24-28 · boots 29-31.
- Unity: `CharacterComposer.cs` alpha-blends `Resources/Player/layers/**` into
  cached per-(dir,frame) sprites at runtime (single SpriteRenderer; layer metas
  need `isReadable: 1` — `fix_sprite_ppu.py` sets it). Appearance/equip server
  sync is a backlog follow-up; F6 cycles debug outfits locally.

## AS BUILT (2026-07-28): whole-outfit sprite sheets, armless character + floating hands
**This supersedes the masked/paperdoll pipeline described in older revisions of this section.**

The character is **armless**; the hands are separate floating fists moved by code. A walk, a run and a weapon
swing therefore need no drawn poses beyond the walk cycle itself, and one animator drives every tool.

Outfits are generated as **whole 12-frame sheets** (3 rows front/back/side x 4 walk phases), one image per
outfit, rather than composed from chest/legs/boots layers. Generating the whole sheet in one render removes
drift by construction; the masked per-slot route needed hand-fixing on every piece and was abandoned
(owner decision, 2026-07-28).

Model **gpt-image-2**, **NO MASK**. Masked runs come back as black boxes. The prompt must state that the
character has no arms, or the model draws them back on.

**Generate on MAGENTA, never on black (2026-07-29).** Black is the one colour the armour also contains, so
"is this pixel background?" stops being answerable. The cutter used to decide by brightness, and deleted the
artwork's own dark pixels: hornet-stinger lost 17% of the figure — every black band — and ant-carapace 17%,
swamp-gear 11%, ranger 10%, with most of the roster losing 6–9%. On a magenta sheet the separation is exact:
measured on ranger, **zero** art pixels test as magenta, against 8.9% of that same sprite being
indistinguishable from a black background. Key by flooding in **from the border**, never per-pixel — a dark
pixel reachable from outside is background, one enclosed by the figure is its own shading.

**`build()` RENDERS FROM `motions.py`. THERE IS NO SECOND SET OF NUMBERS.**

This was the root of a whole day of churn. `motions.py` recorded what the owner picked; `build()` had its
own constants and never imported it. Every pick got written into the record, hand-placed as a gif, and
then **silently overwritten by the next re-render** with the superseded motion — so approved things kept
coming back wrong. Owner: *"they are NOT using the official agreed on animations. why has this been so
convoluted and difficult?"*

Measured at the time, in bronze's own `current/anim/`: the sword was the agreed 320ms frame budget while
axe, hoe, net and shovel were all still the old shoulder-pivot approaches.

⚠ **A tool with no agreed motion is SKIPPED and reported as a GAP** — never falls back to an older one.
Silence was the failure mode, so a missing decision has to be loud. The spear correctly reports a gap on
all 24 outfits.

**FRONT WALK: the RIGHT hand is the mirrored one.** That turns both openings **inward** toward the body.
Mirroring the left instead faces both palms outward, which is what shipped until 2026-08-05 — on every
outfit, bronze included. It stayed invisible while gauntlets were featureless slabs, and only showed once
they had knuckles and a thumb. Owner: *"the palms are facing out"*, and originally *"walk front needs to
actually have it's hands sideways (turned inward)"*.

**EVERY OUTFIT'S GAUNTLET IS A RE-SKIN OF BRONZE'S APPROVED HANDS — use `official` mode, never `gauntlet`.**

```bash
python3 tools/player_sprites/outfits.py official <set>   # copies bronze's four hands, changes material
python3 tools/player_sprites/outfits.py gauntlet <set>   # lets the model invent hands. DO NOT USE.
```

Plain `gauntlet` mode sends only the outfit's own sheet, so the model designs hands from scratch and
returns **featureless slabs with no fingers, knuckles or thumb**. There is then nothing to establish which
way a palm faces, and every swing reads wrong — because `HAND_PERP` and the grip offsets were tuned
against **bronze's** shapes. Owner caught it: *"its used in the wrong gauntlets, are you feeding the
official bronze gauntlet in when creating those?"*

`official` writes to `gauntlet2/` and never over `gauntlet/`; promote it deliberately and archive what it
replaces.

⚠ The reference is `APPROVED/hands/SOURCE_SHEET_hand-D-pixel.png`. It used to be pointed at
`outfits/bronze/hand-D-pixel/result.png`, which no longer exists, with the only surviving copy inside the
**gitignored** archive — a reference every future gauntlet depends on, one `git clean` from gone.

⚠ **THE CUTTER DETECTS THE KEY COLOUR; IT DOES NOT ASSUME ONE.** The switch to magenta was applied to
the generator on 2026-07-29 and **not** to `cut_outfit.background()`, which kept keying near-black. Every
existing outfit predates the switch, so nothing was cut in between and the drift sat unnoticed for a week
— it surfaced on 2026-08-05 as *"expected 3 rows of 4, got [1]"*. `background()` now reads the sheet's own
border and handles both.

⚠ **DEFRINGE EVERY MAGENTA CUT.** The generator anti-aliases the figure against its background, so the
outermost pixels are a blend of art and key. On black that edge was dark and invisible; on magenta it is
**bright pink**, and it survives keying because a half-magenta pixel is not magenta enough to key out —
measured **1.04%** of fireant's opaque pixels and **1.32%** of blackant's. `defringe()` replaces each
tinted pixel with the mean of its clean neighbours over three passes and drops any with no clean
neighbour rather than guessing. Check it: count pixels where R and B both exceed G by 40+.

**Pick the DESIGN before paying for a walk cycle.** `outfits.py explore <set>` draws three designs of one set,
standing still and large, on magenta. The three must have **different parents** — left to themselves they
become three tunings of one idea, the same failure the swing design guarded against. Only the chosen design
gets a 12-frame sheet.

**THE SHEET MUST BE LOCKED TO THE FIGURE THAT WAS PICKED.** Crop the chosen figure out of the explore
sheet as `CHOSEN_<setname>.png`; `sheet` mode passes it as a **third reference** alongside the two bases.
Without it the 12 frames are a fresh reading of the words, not the design that was actually chosen — and
the words were never what he picked from.

`SHEET`'s headgear phrase used to hard-code *"covering the whole head"*, which silently overrode a
face-visible set. It is now just `{headgear}`, so the set description owns the head treatment.

**TWO ROLLS OF THE SAME PROMPT IS A CHEAP WAY TO GET VARIETY.** Undirected batches vary a lot run to run,
so `-A` / `-B` pairs of the *same* set are worth more than rewriting the brief. On the ant colourways the
two rolls differed mainly in **stray magenta**: red-A and black-B came back with **0**, red-B with **374**
and black-A with **105**. Same prompt, same forbidding line — the model paints the key colour on anyway
about half the time. **Count it before picking**; those pixels survive keying and render as bright specks.

**THE HEAD TREATMENT IS A SLOT.** `EXPLORE` takes `{head}`: `HEAD_COVERED` (full helm — the default, and
what every existing set uses) or `HEAD_FACE`, which asks for an open-faced helm with the face actually
drawn. Sets listed in `FACE_SETS` get the latter. Owner wanted the player's face visible on the ant
colourways; it still reads at 40px, which was the risk, since a face is fine detail.

⚠ **RUN PAID CALLS IN THE BACKGROUND, NEVER INLINE.** `gen.py` opens the output file *before* the API
returns, so a harness timeout mid-call leaves a **0-byte result.png** and the image is gone — while the
request may still have been billed. `RECORD.txt` is written *before* the call, so its presence proves
nothing about whether the call completed. This destroyed the `ant-carapace-black` batch on 2026-08-05
because two calls were chained in one foreground command.

**OPEN THE FIRST ROUND UNDIRECTED — the three briefs are a ceiling, not a floor.** Measured on
ant-carapace 2026-08-05: given only the material (*"armour made from ant parts — chitin, shell, carapace,
mandibles, leg segments, worn by a person"*) and three slots saying "your own design / clearly different /
clearly different again", the undirected batch beat both directed ones on every check —

| | undirected | directed 3-options | directed variants |
|---|---|---|---|
| height spread | **2.6%** | 7.0% | 7.4% |
| width spread | **6.3%** | — | 79% |
| stray magenta | **0** | 665 | 0 |

and produced more characterful designs. Writing three design briefs narrows what the model reaches for.
**Keep the technical constraints** — magenta background, armless, silhouette-over-detail, no magenta on the
figure — those are quality rules, not design direction. Write briefs only when something specific is
wanted, and pass **no reference** on an open round; a reference steers it.

**THEN VARY THE WINNER — with the chosen figure as a REFERENCE.** Picking a design is one round; the second
round explores variants *of it*. Crop the chosen figure out of the three-option sheet, save it in that
explore folder as `CHOSEN_<what>.png`, and `explore` passes it as a **second reference** automatically. Without
it the model produces three fresh ideas instead of three variants, and the round is wasted.

The variants must still differ by **silhouette** — on `ant-carapace-soldier` that was broad pauldrons vs
forward tusks vs a tall crest, not three surface treatments.

⚠ **Check the widths, not just the heights.** A brief like *"tighter, trimmer body"* is followed literally:
the crest variant came out **274px wide against 478 and 492** for its siblings. That is not a defect, but a
figure half the width of the others reads as a different weight class from the rest of the armour tier.

**A design is not judged until it is judged SMALL.** `preview_explore.py <set>` renders each option large and
again shrunk to real game height on grass; the small row is the one that decides. Ranger's third option was
the best-looking design on the page and the worst in the game — its gold linework became noise the instant it
shrank, while the two plainer designs kept working. So:

- **What distinguishes one design from another must be SILHOUETTE** — hat, hood, crest, plume, cape, shoulder
  and hem shape. Never engraving, filigree, trim or inlay: those are exactly what dies at 40px. Platinum's
  three "fancy" options are a plume, wings and a spiked crown for this reason, and all three stayed readable.
- Four or five flat colour areas per figure, in chunky blocks.

**MATERIAL-NAMED SETS ARE ARMOUR MADE OF THE MATERIAL, NOT A COSTUME OF THE CREATURE.** Owner, 2026-08-05:
*"in all cases it should be armor, wearing armor made from ant carapace does not magically turn you into an
ant."* So ant-carapace is a **person in a helmet** whose mandibles have been repurposed as jaw guards — not
an ant's head on a body. The same reading applies to beetle-shell, hornet-stinger, moth-wool and the rest.

**The model will paint the KEY COLOUR onto the figure** if you let it — magenta "glowing eyes" on a beetle,
a magenta halo on a platinum. They survive only because the key floods from the border (an enclosed magenta
pixel counts as art); a per-pixel colour test would punch holes exactly there. The prompt now forbids
magenta/pink/purple anywhere on the figures, but **check each sheet for it anyway**.

Full procedure — the verbatim sheet and gauntlet prompts, the cutting steps, the pixelsnap pitch warning, the
hand-size constant and the per-tool grip measurement — lives in the **`player-sprites` skill**
(`.claude/skills/player-sprites/SKILL.md`). Art lives in `tools/_generated/player/` (`bases/` = the two locked
sprites, `outfits/<name>/` = one folder per outfit).

**Which sets exist is DATA, not prose.** `tools/player_sprites/outfits.py` holds the roster and the single
shared prompt; a new set is a dict entry naming three things — what the set is, its material and colours, and
its headgear — never a new script. **Every set has headgear**; one without it doesn't match the rest and gets
redone. Which sets are *planned* is `docs/product/economy/catalogs/armor.md`.

**A tier reads by COLOUR, not by silhouette.** At sprite size every plate set is the same shape, so a metal
rung that isn't separated in brightness is a wasted tier. Check it by measuring mean luma over the worn
material of `front_1.png`, not by eye — the completed ladder runs iron 66 → steel 90 → silver 113 →
platinum 157, and eyeballing that same comparison once produced a confident *wrong* call (that steel collided
with silver). Warm metals separate by hue instead: copper is pink-orange, bronze brown-gold, gold yellow.

**Design 2026-07-29 (as built, 22 sets).** The base ladder is complete at nine rungs. Cloth sets (padded,
moth-wool) show the face under a hood or coif rather than a full helm, which is what makes them read as T1
cloth and not as pale armour.

The 16x32 region-template system above is the ORIGINAL hand-authored player and is what the game still loads
today; publishing the new sheets is a separate step.

### The swing: the hand needs a SHOULDER (2026-07-29)
The first five swing "approaches" all rotated one rigid tool sprite about the **player's centre** and stuck
the fist to its grip afterwards. They differed only in the easing of that one angle, which is why they looked
identical and why the fist rode up past the chest — a circle around the navel is not a swing, and no amount
of retiming fixes a wrong pivot.

**Drive the HAND, then hang the tool off it** (`swing_lab.py` approaches 8–9). The hand travels an arc from a
shoulder; the arm shortens across the body and extends through contact, which is what an elbow does. Costs no
new art, because the fist is already a separate code-moved sprite.

Two constraints found by getting them wrong:

- **The armless design caps how far the hand may travel.** A drawn character can reach arm's length because
  the arm connects the hand. Ours cannot — at a realistic reach the sword visibly detached and floated beside
  the body. Keep the hand within roughly a third of a cell of the shoulder.
- **`art_rot` must stay 0 unless the grip is recomputed with it.** `grip_of` measures the handle off the
  *unrotated* sprite, so rotating the net 180° left the hand clamped on the hoop with the handle out the far
  side. Fix a "wrong way round" tool by reversing its **sweep**, not its sprite.

**Every facing gets its own shoulder.** Sharing one put the hand at face height in the front view. The front
view also needs a floor angle so a tool stops in front rather than burying itself, and the away-facing view
draws tool and hand **behind** the body. All three are rendered side by side because all three have to work.

### ONE MOTION PER TOOL — do not share an arc
The strongest recurring mistake in this work: writing one arc function and giving each tool different
constants. It looks like reuse and it is actually six copies of the same move. A sword is not an axe; a
thrust is not a slash. If two tools differ only by numbers, they will read as the same animation, which is
exactly the complaint that came back every round.

Each `kind` in `swing_lab.py` owns a function, and they differ in **mechanism**:

| kind | tool | what it actually does |
|---|---|---|
| `slash` | sword | short fast flick, ~120°, 0.11s — a combat slash, **not** a dramatic wheel |
| `wheel` | axe | behind → over the top → down in front, ~265° unbroken; a real axe never stops at the top |
| `sweep` | net | starts **behind the shoulder**, travels ~195° forward |
| `till` | hoe | raise, drive down to the feet, drag back toward the player |
| `thrust` | spear | angle nearly fixed — the **reach** is the whole animation, held at full extension |
| `scoop` | shovel | stab down into the ground, then lift and scoop up and out |

**A swing must START BEHIND the character.** The net ran 55° → −20°: already out in front, only tipping down.
A tool that begins in front has no swing in it, whatever the timing does.

**Every motion starts AND ends at the idle pose.** Swings used to *teleport* to their wind-up pose — 235° for
the axe, 205° for the net — then sit there while the curve eased in. That jump, not the timing, is what read
as "hovering in the cocked-back position". Travel the wind-up and land the recovery on idle; that also closes
the old "the swing has no exit" defect. Arrive at the top **at speed** (`ease_in`), never decelerating into
it, or the tool lingers at the extreme.

**Combat durations are 0.11–0.22s.** Anything slower cannot be held down in a fight.

**Digging tools are REACH-driven, not angle-driven.** The hoe and shovel read as swings while their angle did
the work. A hoe is a small lift, a strike, and a drag; a shovel is a downward jab that holds and lifts a
little. Both keep the angle nearly still and let the reach drive — that is the difference between digging and
swinging.

### When a note keeps coming back, stop theorising and enumerate
The net swing was wrong five rounds running. Each round produced a *theory* about what "backwards" meant,
changed something on the strength of it, and was wrong; the last theory was invented outright and attributed
to the owner. `net_options.py` is the correction: render every combination that could possibly be meant —
sweep direction × sprite transform × which end leads — caption them, and have him point at one. Cheaper than
a sixth wrong guess, and it ends the argument. Reach for this the *second* time a note repeats, not the fifth.
(When transforming a sprite, recompute the grip on the **transformed** art or the fist clamps to the wrong end.)

### WALK and RUN — the approved motion lives in `tools/player_sprites/gait.py`. USE IT.
Both fists swing **through the body**, around the torso centre measured once at 42% down the neutral frame.
The far fist is drawn first and **dimmed to 0.62**, the body over it, the near fist last — so the arms read
as passing behind and in front. Beat phase is `[0.5, 0.0, 1.5, 1.0]`.

| | amp (×torso width) | rise | rotation | tilt | fist (×body H) | height down body | ms |
|---|---|---|---|---|---|---|---|
| **walk** | 0.52 | 0.013 | **0°** (it hangs) | 22° | 0.17 | **0.60** waist | 150 |
| **run** | 0.58 | 0.032 | **75°** forward | 14° | 0.19 | **0.46** chest | 90 |

**Do not re-derive these from the reference gifs.** That was done once and every number came out wrong —
walking fists anchored at the chest instead of the waist, travel measured off the body edges instead of
through the centre, ~3× the amplitude, a ±55° roll the approved walk does not have (its rotation is 0), no
far-hand dimming, wrong hand sprites. It read as flapping and was rejected on sight.

> **The lesson that cost this.** The script that produced the approved motion was written into a session
> scratch directory, run, and **never committed** — only its output gifs survived, and those live in a
> gitignored folder. An approved decision that exists only as a rendered artifact is a decision you will
> lose. **If a parameter was agreed, it belongs in committed code the same day**, not in a temp script.
> (It was recoverable from the session transcript, but only because the transcript happened to still exist.)

#### THE WRIST LEANS TOWARD THE BODY (fixed 2026-08-06, after being reported three times)

A hand held out **in front** of you has its wrist **behind** it, nearer the shoulder. A hand trailing
**behind** has its wrist **in front** of it. The arm has to come from somewhere, and that somewhere is the
body.

Both signs were inverted, so the forward fist's cuff sat *further forward still* and the arm read as
reaching around from the far side. Owner, first on 2026-08-03 and again on 2026-08-06: *"when a hand is in
front of you the wrist has to be like closer to you not coming from the other side… this is something I
have been saying several times and you just dont fix"*.

**Why the earlier fix missed.** On 2026-08-05 the two hands were changed to tilt in *opposite* directions,
which sounds like the same fix and is not — both directions stayed wrong, so the thing he was pointing at
never changed. Opposite ≠ correct.

**Do not eyeball this; measure it.** The character faces `+x`; the hand sprite is flipped (cuff up, fingers
down); `_rot(hand, +22°)` moves the cuff **2.4px LEFT**, `-22°` moves it **2.0px RIGHT**. So the forward
hand — the one at `+dx` when `s > 0` — needs the **positive** angle:

```python
near_ang = p["rot"] + p["tilt"] * s      # at +dx: forward when s > 0, so the cuff leans BACK
far_ang  = p["rot"] - p["tilt"] * s      # at -dx: trailing, so the cuff leans FORWARD
```

`tilt` itself is unchanged — 22° walk, 14° run. Only the direction it is applied in.

#### ONE mirror, in one place

There is exactly **one** left-right mirror in the whole live path — `gait.walk_front_into`, which builds
the camera-facing walk's hand pair from a single sprite. Nothing else mirrors anything.

Keep it that way, and resist "just store both hands so nothing has to mirror". A left hand *is* a mirrored
right hand, so producing the pair from one sprite **guarantees they match**; storing two drawings costs a
sixth paid hand per outfit and lets the pair drift. The mirror was never the problem.

**Two copies of the motion was the problem.** This function was briefly transcribed into `build` so its
numbers could come from `official.py`, and the copies then disagreed about which hand to mirror — the
palms-in fix landed in one and not the other, so everything still calling `gait` kept rendering palms-out.
`build` now calls this and passes `p` in. If you need a variant, pass different numbers; do not copy the
function.

#### Palms turn IN for the camera-facing walk

The front and back walks paste **one** hand sprite twice and mirror one of them; mirroring the **left** one
turns both palms inward. Mirroring the right instead turns them both out, which shipped and was reported
twice. All four combinations are rendered in `reviews/2026-08-06-bronze-hands/PALMS_compare.png` —
mirroring neither or both points the hands the same way, so a symmetric pair is only ever the left or the
right, and the right is the rejected one.

### Judge a set IN MOTION, holding something
`showcase.py` renders several sets across four bands on one timeline — running right, running down, swinging
side-on, swinging front-on — with a different tool per column so every motion appears. A set that reads well
as a portrait can still fall apart the moment it moves or picks up a weapon, so the reel, not the contact
sheet, is what a set has to survive. It imports the swing from `swing_lab` rather than reimplementing it, so
it cannot drift from the designed motion.

### WHAT IS OFFICIAL — `tools/player_sprites/official.py` (2026-08-06)

**One file names every official sprite and animation. The build reads it and nothing else.** No directory
scanning, no fallbacks: **a missing file stops the build and prints which one.**

That rule is the whole point. Before it, two things were true at once and nobody noticed:

* `render_animations.py:79-83` resolved an outfit's hands by trying **three folders in order** and taking
  whichever existed. Measured by patching the image loader and running it over all 24 outfits — **21
  resolved to a gitignored archive**, 2 to their own `gauntlet/`, and bronze to a hardcoded exception
  reading two other folders under different filenames. Nobody chose that. The fallback did.
* **No build code ever opened a decision record.** `render_animations.py` mentions "APPROVED" 18 times in
  comments and reads `DECISIONS.md`/`CURRENT.md` zero times. So *what was official* and *what got loaded*
  were never the same object — which is why asking for "a gallery of the official ones" returned whatever
  happened to be sitting on disk.

`official.py` holds four things: `HAND_ROLES` (the five hands every outfit has), `OUTFITS` (which folders
are that outfit's chosen frames and hands, with the owner's words and date), `GAITS` + `SWINGS` (the
approved motion numbers — this only ever GROWS, so "go back to Tuesday's swing" is a one-line change), and
`ANIMATIONS`, where **one row fully defines one animation**. Adding an animation is a row, not a branch.

Each entry also names its `sheet` — the chosen 12-frame generation the frames were cut from, which the
gauntlet prompt sends as the colour reference. Declaring it beats hunting for a file called `result.png`,
which broke the moment those were tidied into `tries/`.

### REVIEW COMES BEFORE OFFICIAL. Always.

Owner, 2026-08-06: *"we always want to review before updating anything official."* The order is:

```
generate into tries/  →  render a review sheet  →  HE LOOKS AND SAYS YES  →  copy into place  →  official.py
```

I broke this the first time it mattered: fireant and blackant were generated, promoted into `gauntlet/`,
added to `OUTFITS` and rendered — and *then* shown to him. He is the gate; a sheet produced after the fact
is not a review, it is a report. Reverting was cheap only because choosing is a **copy** and `tries/` was
untouched.

The generated art being good is not the point. Whether it is good is his call, not mine.

**And show him the THING, not its inputs.** When he reported the ant gauntlets looked reversed, I built a
sheet comparing the source PNGs against bronze's — which he could not act on: *"i dont know which one you
are using in the animation"*. The hands are mirrored at render time, so the files and the frames are not
the same thing. The sheet that resolved it in one look rendered the walk exactly as `build` does and
cropped to the hands.

It also carries `PENDING` — outfits that are chosen but **not built**, with what each still needs. An
outfit is complete and in `OUTFITS`, or it is here and renders nothing. Settled behavioural decisions that
are code rather than numbers (the wrist direction, which hand is mirrored) are recorded beside the
constants they affect, because this file is where *"what did we agree"* gets answered.

> That definition used to be split three ways with no single file stating it: `gait.py` held the walk
> constants, `motions.py` the swing arcs, and a `SWORD_FACINGS` dict inside `render_animations.py` held
> which frame bank, where the shoulder sits and whether the weapon draws behind the body — next to 174
> lines of dead code including a whole second motion system whose constants still looked live.

### Candidate designs — `outfits.py explore <name>`

One paid call draws **three** design options side by side on magenta, so "three candidates" = one call.
The brief is an `EXPLORATIONS` entry: what the set IS, plus three directions.

**The three must differ by SILHOUETTE — helm outline, shoulder mass, hem shape.** The shared prompt already
says so, and it is the whole game: at ~40px surface detail collapses to mush, so three designs separated by
trim, engraving or linework produce a sheet nobody can tell apart. The grey metal rungs additionally
separate by **brightness** (armor.md records iron 66, steel 90, platinum 157).

Design intent for the roster lives in `docs/product/design/brainstorm_armor.md` — what each set is FOR,
which role's apex it competes for, and what has been cut and why.

### Showing him options — `tools/player_sprites/review.py`

Anything the owner must LOOK AT to make a decision goes through this. Two conventions are baked in
because both have been got wrong more than once:

* **Labels are 22pt — about 2× PIL's default.** `ImageDraw.text()` with no `font=` gives an ~11px bitmap
  face. Owner, twice: *"i literally have to zoom in to see it its so tiny… maybe make it twice as big…
  i asked you before so can you somehow remember this."* The helper cannot render small text, so a new
  script cannot reintroduce it. (Watch the width: a sheet sized to its images alone will **clip** a long
  label, which defeats the point. `stack()`/`row()` measure the text too.)
* **It lands in the repo**, under `reviews/<YYYY-MM-DD>-<what>/`, and `save()` prints the `C:/…` path
  back. `/tmp` and `/mnt` paths do not exist on his machine, so showing him one shows him nothing.

**The script is the reminder.** `save()` prints the conventions it just applied and warns when a review
folder has no `README.md`. Owner's idea, 2026-08-06: *"having python scripts perhaps actually output
things — reminders and such, as a form of 'hook' — as long as you read the output of the script."* It
fires exactly when relevant, cannot be routed around, and costs one `print()`.

### Rendering it — `tools/player_sprites/build.py`

```bash
python3 tools/player_sprites/build.py --status   # what is official, what is pending, what is not agreed
python3 tools/player_sprites/build.py            # every outfit in official.py
python3 tools/player_sprites/build.py bronze     # one
python3 tools/player_sprites/build.py --check    # compare only; writes nothing (the pre-commit gate)
```

**Every outfit has the same shape** — the subfolder names are fixed by the system, not chosen per outfit,
so "where are this outfit's hands?" has one answer for all thirty of them:

```
outfits/<name>/tries/<YYYY-MM-DD>-<what>/   every attempt, kept forever. THE BUILD NEVER READS THIS.
outfits/<name>/frames/                      the chosen body frames
outfits/<name>/gauntlet/                    the chosen hands, one per HAND_ROLES
outfits/<name>/anim/                        rendered animations — build.py OWNS this folder
```

**Choosing = COPY from `tries/` into place, never a move.** The attempt stays where it was, so nothing is
consumed and nothing can be overwritten; git holds every prior state. This replaces the
`scratchpad/current/archive` shape and `promote.py`'s move-to-archive step — the only step that could
lose something.

**An outfit is either complete and in `OUTFITS`, or it is in `PENDING` and does not render at all.** There
is no third state where it renders using someone else's parts, which is precisely what the fallback chain
did to 21 outfits.

⚠ **`CURRENT.md` and `check_sprite_ledger.py` are retired** (2026-08-06). The hook compared *filenames*
between a hand-written ledger and the folder — it never opened an image, so every animation could be wrong
and it would still pass; and it only inspected outfits that had a `CURRENT.md`, which was 2 of 24. Its
replacement, `.claude/hooks/check_official_build.py`, re-renders from `official.py` and compares the GIF
bytes.

**`build` owns `<outfit>/anim/`** — anything there that `official.py` does not name is removed. Stale files
are not hypothetical: `thrust_spear_two_handed.gif` sat in 22 outfits, was committed, and showed in the
gallery for weeks after the code that produced it stopped existing.

**Ported under a byte-identical gate.** All 13 of bronze's approved animations rebuild byte-for-byte
through the new path. The render is deterministic (same md5 across runs), so that is a real check rather
than a promise — and it is what proves the port faithful before anything old is deleted.

**`gallery.py` reads `official.py` too** (2026-08-06). It used to scan directories, so it inherited the
renderer's fallbacks and displayed whatever was lying around — which is why *"I ask for a gallery showing
all the official whatevers and it will just be random crap"*. Concretely: it showed
`thrust_spear_two_handed.gif` for 22 outfits long after the code that made it was deleted, and showed 21
outfits wearing hands loaded from a gitignored archive. Both were on disk, so both were displayed.

Now every name, path and animation comes from `official.py`. A **pending** outfit renders nothing rather
than borrowing another outfit's parts, and a declared animation with no file shows as a **missing** tile
instead of being quietly omitted. The one place it still reads the disk is `tries/`, deliberately —
that folder is exploration, its contents are declared nowhere, and nothing is ever loaded from it.

One file per animation, always the current one, named for what it is — `walk_side.gif`, `swing_axe.gif`.
No iteration codes in filenames; history lives in git. Naming variants for how they were made (`set_a`,
`batch2`, `profile_option_1`) is what produced 131 indistinguishable files and cost three days.

**Each animation picks its hand AND its base rotation deliberately** — the hand sheets are drawn fingers-up,
cuff-down, so using them raw gives a hand hanging at the waist with its fingers pointing at the sky:

| animation | hand | rotation |
|---|---|---|
| walk | relaxed, **flipped** so the fingers hang down | 0 |
| run | relaxed, flipped then turned to lead | 75° |
| swing | the approved **grip** hands, knuckles down | `HAND_ROT` 225, +16% down the handle |

> The grip hands are **not** the walk/run hands. *"the weapon grabbing is NOT to be blindly replacing walk
> and/or running — they all should be carefully thought about and the best one picked."*

**Each outfit uses its own gauntlet — but every one is a material variant of BRONZE's shapes.** Owner,
2026-08-06: *"the only officially established hands are the bronze hands... everything else will have
literally their own as close as possible variants (well with different color and texture and such)."*
The gauntlet prompt sends bronze's hand sheet as reference image #1 and says *"Copy the reference EXACTLY
in shape... the ONLY thing that changes is the material."* Proven — fireant and blackant were made this
way and still hold their `ref_1_SOURCE_SHEET_hand-D-pixel.png`.

⚠ **There are FIVE hands, not four** (`official.HAND_ROLES`). The count was previously hardcoded in three
places that disagreed — `cut_gauntlet(cols=4)`, four poses in the prompt text, five keys in `load_hands` —
so `grip_palm` silently fell back to `grip_back`. Result: **23 of 24 outfits held a two-handed tool with
the same hand twice** (verified by array comparison). Only bronze had a real back-and-palm pair, which is
why nothing could copy it: no other outfit had the parts.

**One list now drives all three.** `official.HAND_ROLES` decides how many poses the prompt asks for, how
many cells `cut_gauntlet` bands the sheet into, and how many hands the renderer requires. Add a role and
everything follows; there is no second place to remember.

`review.hand_strip()` renders an outfit's hands at one scale for comparing sets — the same height
normalisation, in one place rather than copy-pasted (my first fireant-vs-bronze sheet skipped it and
bronze's grips swamped the row).

**The reference image is generated, not stored** (`outfits.reference_strip()`). It composites bronze's
actual `gauntlet/` into a strip at call time, so the reference *is* the official set and cannot drift from
`HAND_ROLES` — which is exactly how the old committed 4-hand `SOURCE_SHEET` came to disagree with a
5-role renderer. Two things it fixes on the way through:

* **Normalises height.** Bronze's five are not stored at one scale — the walk trio are cut sprites
  (16×20, 18×22, 12×21) while the two grips are full-resolution art (213×237, 176×240), an ~11× gap.
  Pasted raw, the reference shows three tiny hands beside two huge ones and the model copies that.
* **Defringes.** The grips still carry magenta key-bleed at the silhouette edge (cut before `defringe`
  existed). A few bright pink pixels in a reference become a few bright pink pixels in all thirty
  outfits. The approved source files are untouched; only the derived strip is cleaned.

**Every outfit renders at ONE body height** (`TARGET_BODY_H`, currently 320, NEAREST only). The 22 outfits
on disk are cut at two scales — 7 at 267-292px, 15 at 395-435px, a **1.63×** split — which side by side
reads as "these outfits are different sizes" when it is purely a cutting artifact. This is fixed at
**render time, not by re-cutting the source**: the art is being recreated anyway, and a bulk re-cut is what
destroyed a day of approved work on 08-01.

The **back-facing walk** — which `APPROVED/DECISIONS.md` still calls *"requested, never delivered"* — comes
free: every outfit already had `back_1..3`. It reuses the front-walk implementation deliberately (from
behind you also see both hands clear of the silhouette; at ~10px a hand, the near/far distinction the side
walk needs does not read).

⚠ **Known limit:** `run_front` and `run_back` are the *walk* motion played at run speed. Only the **side**
run has its own approved pose (`RUN`, rot 75°). Front/back running is not yet designed.

### Seeing all of it — `tools/player_sprites/gallery.py`
Writes `tools/_generated/player/gallery.html`; open it by double-clicking. Three tabs: **Current** (every
outfit × every animation, transposable), **Progress** (which of the four stages each outfit has actually
reached), **Outfit detail** (frames, gauntlets, candidate sheets captioned from `RECORD.txt`, the ledger).

Generated from the folder structure — no hardcoded outfit or animation list — so it reflects whatever is on
disk and survives the sprites being recreated. Under `file://` a page cannot list a directory or `fetch()`
local JSON, so the manifest is inlined as a `<script>` block and the page **must** live at
`_generated/player/` for the relative image paths to resolve.

### Three defects found by looking at the finished set (2026-08-03)
All three were invisible until 22 outfits were rendered side by side — which is the argument for the
gallery existing at all.

**1. The two walking hands must tilt in OPPOSITE directions.** The recovered transcript gave both hands
the same `ang`, so the hand swinging forward and the hand swinging back leaned the same way and the
wrists read as locked together. Owner: *"the rotations are wrong for the hands when they are swinging in
the walking (the back hand for example is rotating the wrong way when forward)"*. `back_hand` sits at
`+dx`, so it is the forward one when `s > 0` — the hand he named. Each hand now tilts with **its own**
direction of travel. **The `WALK`/`RUN` constants are untouched**; only the per-hand sign changed.

**2. THE HANDS WERE ALREADY CHOSEN AND WERE NOT BEING USED.** Every animation had been built on the cut
gauntlet views, so bronze's walk used a **discarded** sprite and its swing used the **tool-grip** hand —
a hand for holding a handle. `APPROVED/DECISIONS.md` had already warned in writing that those cuts "were
never approved... anything unapproved living here is how the wrong sprite gets picked later."

| sprite | used by |
|---|---|
| `APPROVED/hands/h1.png` | knuckles / back of hand — walk + run, the **near** hand |
| `APPROVED/hands/h2.png` | palm — walk + run, the **far** hand (dimmed, behind the body) |
| `APPROVED/hands/h3.png` | profile — walking **toward or away** from the camera |
| `<outfit>/hands/grip_*.png` | **SWINGS ONLY** |

They are bronze's, and **every other outfit's gauntlet was generated from them**, so a non-bronze outfit
uses its own gauntlet in the same three roles: `front`→h1, `back`→h2, `side`→h3. `flip()` is a 180° turn,
so the profile hangs fingers-down pointing inward, and `walk_front_into` mirrors it for the other hand.

> **The reference gifs in `APPROVED/` are what a correct render looks like. Compare against them before
> claiming an animation is right.** Rendering 264 animations without once doing that is how a discarded
> hand shipped across all 22 outfits.

**3. A left-facing side row makes an outfit walk and swing backwards.** The prompt asks for "a strict
RIGHT-facing side profile" and the model sometimes ignores it; copper and farmer came out mirrored.
Everything downstream assumes right-facing (`back_hand` swings to `+dx`, every swing arcs toward `+x`).
`flip_side.py <outfit> --go` mirrors just `side_*.png` — free and exact, and the skill already says
"Left = mirror of right. Never generate it."

> ⚠ **Do not try to auto-detect the facing.** A centroid heuristic ("the visor overhangs toward the
> facing direction") agreed with a careful visual read on only **6 of 8** outfits. A detector wrong a
> quarter of the time would mirror sprites the wrong way across the whole set, silently. A human looks
> at the gallery and names them.

**Related cutter bug (real, but NOT the cause of the boxy hand):** `cut_gauntlet` measured the pixel
pitch **per blob**, but the four hands are one image at one scale, so there is one true pitch.
`detect_pitch` disagreed with itself — bronze `[3.50, 4.90, 4.85, 4.95]`, ranger `[3.35, 3.25, 3.45,
4.95]` — meaning one hand per sheet was sampled at the wrong rate. It now uses the **median**. Most
outfits agree to within 0.3 and are unaffected.

### THE HAND TRAVELS. The tool follows it. (2026-08-04 — the root cause)
Owner: *"do people take a sword in their fist, hold their fist up to their shoulder and rotate their fist
to swing it? ever?"* No. And that is exactly what `swing_frames` did for weeks.

It computed **one angle**, placed the **tool** at a fixed small radius from the body centre, then stuck
the hand onto the tool's grip. The tool led and the hand was downstream of it — so the fist stayed parked
beside the shoulder and **rotated in place** while the blade swept round it like a clock hand bolted to
his chest. Every "fix" retimed that motion, which is why none of them worked: **timing was never the
problem.**

```
shoulder    a fixed point on the body
hand        shoulder + reach(t) x direction(t)         <- THE HAND TRAVELS
blade       along the arm, plus a wrist offset         <- pivots at the WRIST
tool        placed so its measured grip lands on the hand   <- the tool FOLLOWS
```

`swing_arm.py` is that model.

**SHIPPED for the sword, 2026-08-04** — `render_animations.arm_swing_frames` / `sword_motion`:
arm **128° → −104°** (past straight down, so the hand finishes at the hip), blade **85° → 52°** behind the
arm (decreasing, so the tip keeps dropping after the arm stops), reach **0.60**, `HAND_PERP = 180`, 0.30s.
Owner: *"do sword_1h_f4_back85 as the official one, but have it pull back a tad more at the end so the
hand is at the hip not forward a little, you can also have tip slightly continue down more."*
The other five tools still run the old shoulder-pivot approaches.

**THE ATTACK HAPPENS IN FRONT OF HIM. NEVER WIND UP BEHIND HIS BACK.** No game swings a weapon from
behind the player and around — that is cutscene staging, and it wastes the frames a game attack does not
have. Owner: *"do you know any game with a sword or whatever that starts way behind the player and swings
around like that?"*

**Check the sign of the hand's x offset across the whole motion.** If it goes negative, the arc is passing
behind him, through his own body, before it reaches anything. A net sweep built that way measured
x −0.48 → +0.48; the fix keeps it at +0.06 → +0.55.

**SWEEP AND HEIGHT ARE SEPARATE KNOBS — do not trade one for the other.** The net went wrong twice in a
row on exactly this: one version swept the arm to +92°, putting the hand **3-4% down the body** (above the
top of the helmet — *"its crazy how it ends up over the head"*); the fix for that shrank the travel to
**9% of body height**, so it stopped reading as a scoop at all. The answer is to keep the sweep and shift
the whole RANGE down. Working motions live between roughly **40% and 70% down the body**.

**Compute where the hand lands as a percentage down the body before rendering.** `shoulder_y −
sin(arm)·reach·cell`, as a fraction of body height. Two rounds of this were wasted judging it by eye.

**NEVER OVERWRITE REVIEW OUTPUT.** Every lab script writes to `reviews/<date>-<HHMM>-<tag>/` — a **new
folder per run**. They used to write into one folder named for the day and clear it each run, so
re-rendering destroyed the previous attempt. When the owner says *"it was mostly ok before you changed
something"*, that file has to still exist, and reusing filenames across runs means you cannot even tell
him which version he was looking at. Owner: *"can you please stop overwriting files i cant show you the
old one"*.

This is the dated-batch convention already in the `player-sprites` skill. It was designed and then not
applied to the assistant's own output.

**A SHOVEL IS A LEVER HELD LOW — it is not a battering ram, and not held up by your face.** Two things the
rig could not express until `attack_frames` grew `pivot` and `second`:

- **`pivot`** slides the point the tool sits on the driving hand **up the shaft**. A sword pivots at the
  butt (`pivot=0`) and the whole weapon swings. A shovel is gripped partway along, and the motion is a
  **rotation about the LOW hand** — which barely moves — while the top hand swings. With `pivot=0` and both
  fists welded to the tool, the only thing the rig can do is slide the whole shovel forward.
- **`second`** places the other fist relative to that point. **Negative** puts it *behind*, toward the
  butt, which is where the top hand actually goes on a shovel.

**Hands stay LOW.** The arm aims steeply down (≈−55°) so the hands sit at **50-57% down the body** — waist
to hip — and the blade is brought back up to a shallow forward angle by a large `back`. Aiming near
horizontal from the shoulder (30% down) puts the hands at chest height, holding the shovel up by his face.

Check the lever numerically: between drive-in and lift the hand should move **almost nothing** while the
blade rotates a lot. Currently 0.11 cells of hand travel against 46° of blade rotation.

**THIS IS A BLOCK WORLD — aim the tool at the BLOCK IT IS ACTUALLY BREAKING.** Standing sideways, he digs
the block **beside** him, not the ground under his feet. Owner: *"this is a block based world so when
standing sideways you are digging dirt to the side of you not below you."* So the side-view shovel is a
roughly **horizontal** drive into the adjacent cell; a downward jab is the *facing-down* animation, which
breaks the block below. A cell is half his body height, so the block beside him spans his lower half —
aim a little under horizontal to land in it.

**Working tools start at the HIP**, close in, not already extended. The reach is the stroke.

**WHERE THE HANDS SIT — measure the sprite, do not assume.** Bronze's width profile: helmet to ~22% down,
shoulders ~30%, waist ~50%, legs below 65%. The shoulder pivot (`SHOULDER`, 0.40 cells above body centre)
lands at **30%** — correctly on the shoulder line. The character is **not** chibi; asserting that without
looking sent one whole pass in the wrong direction.

⚠ **The trap is aiming HORIZONTALLY from the shoulder**, which parks the hands at shoulder height, up by
his head. A two-handed spear sits at chest/waist, a bug-scoop at waist. **Thrusts and scoops aim BELOW
horizontal** (spear −20°). Check it by computing where the hand lands as a % down the body, not by eye:
spear 32-47%, net 48-57%, shovel 42-69%.

**Every attack holds at REST for 4 frames before looping** (`ATK_REST`) — without it a looping gif
ping-pongs and you cannot tell which direction the swing runs.

**THE VERB DECIDES THE CHANNEL — angle or reach.** Not every tool is an arc:

- **reach SHRINKING while the tool stays low** is the hoe's *drag* and the shovel's *lever*
- **reach GROWING with a still angle** is the spear's *thrust*
- only the axe, net and sword are actually carried by **angle**

Building the spear and shovel as arcs is why they read as waving the thing around. Owner: *"do you sit
there bashing the ground with a shovel? do you?"*

⚠ **TOOL LENGTH IS A PARAMETER AND IT WAS NEVER SET.** `attack_frames(scale=…)`; the spear is **1.9×** a
cell. It was rendered at sword length for weeks while the owner asked three separate times for it to be
longer — every time, the motion got adjusted and the sprite scale was never looked at.

**ONE MOTION PER TOOL** (`swing_tools.py`) — not one arc with different constants. Owner caught that as
a code smell: *"sword is not an axe swing"*. The channel that carries the motion differs per tool:

- **axe** — a big continuous arc, "behind over then down in front", **never hovering** cocked-back
- **hoe** — lift a little, strike the ground, then **PULL back** toward the player
- **net** — the **hoop LEADS**: carry the tool *ahead* of the arm (negative blade-behind). Trailing it is
  what made the net swing bulge-first
- **shovel** — **thrust in**, then swing up **just a little**, then return. The lift is small and the blade stays on the ground line; levering the handle over and heaving the load up is a different action and looks nothing like a shovel
- **spear** — **REACH does the work** (0.78-0.92 cells), the angle barely moves

⚠ Rotation is the wrong channel for a stab. Building the spear and shovel as arcs is why they read as
waving the tool around.

**SHIPPED for facing down and up, 2026-08-04: `E_double_back`** (*"lets do double back for both"*) —
`render_animations.attack_frames` / `DOUBLE_BACK`, rendered as `swing_sword_down.gif` /
`swing_sword_up.gif`. Out across, then whipped back through the other way.

**THE ARC SWEEPS *THROUGH* THE ATTACKED SPACE — IT IS NOT A THRUST *ALONG* IT.** A top-down sword attack
is a sweep **across the body** that passes through the tile being hit, which is what gives it a wide
attack area ([SLYNYRD Pixelblog 56](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation)).
Write each motion relative to `centre`, the direction attacked (−90 facing down, +90 facing up), and have
the arc **cross** centre rather than end on it.

⚠ Driving the blade *along* the attack direction gives a **reverse stab**, not a swing — the facing-up
version dipped the blade down and then drove it up, and owner called it *"a backwards stabby motion as in
going the wrong way"*. Five diverse approaches live in `swing_five.py`.

**AN ATTACK IS A FRAME BUDGET, NOT AN EASED SWEEP** (`swing_game.py`). Owner: *"the user has to watch
the play pull back the sword the swing the sword, its not a video game swing"*. Spreading the motion
evenly across the runtime and giving the wind-up a third of it makes a cutscene — you watch him lift the
sword, then watch him lower it. A game attack puts almost all the travel in **two or three frames** and
spends the rest **sitting on the end pose**:

| frames | | |
|---|---|---|
| 0-1 | ANTICIPATION | a small lift, not a wind-up you can watch |
| 2-4 | STRIKE | ~90% of the arc, with a blade **trail** — three frames is too fast to read without one |
| 5-7 | HOLD | the end pose sits still; **this is what reads as impact** |
| 8-13 | recovery | eases home, nobody is watching |

**14 frames @ 20ms = 0.28s.** Measure it — the eased version came out 0.46s, half a second of committed
animation per swing. 20ms is the floor gif players reliably honour.

**A SWING MUST COVER WHAT IT HITS.** This is a game, not a portrait. Facing down the player attacks the
tile SOUTH of him — straight down the screen — so the blade has to finish with its **tip past his feet**.
Facing up, past his head. A swing that sweeps out to the side is a front-facing sprite performing the
sideways attack: it covers nothing in the direction he is attacking. Owner: *"when you strike something
below you while facing down it means being able to strike something below you, all your looking down ones
are pretty much the same thing as the sideways ones"*.

**AND THEY ARE THEIR OWN MOTIONS, NOT THE SIDE SWING RE-AIMED.** The side swing is one monotonic sweep;
facing the camera that is wrong twice over — different plane, and a monotonic sweep **stops dead** instead
of following through. Each facing is written in three phases: **RAISE**, **STRIKE** (through the tile),
**FINISH** (carry past contact and settle). Owner: *"the swing will be different when facing down and up,
and it also needs to finish the swing, so its weird you are like so obsessed with the sideways swing"*.

⚠ A follow-through must move the blade somewhere **visibly different** from the strike. Taking the arm
past vertical while unwinding the blade by the same amount leaves `blade = arm + back` pinned — the up
swing froze with three identical frames at the top.

**Facing DOWN and UP are not the side swing rotated** (`swing_facings.py`):
- **The shoulder moves per view** — `(0.06, 0.40)` side, `(0.10, 0.10)` front, `(0.10, 0.22)` away. Reusing
  the side-on shoulder is what put the hand at face height in the front view.
- **Facing away, the weapon draws BEHIND the body**, or it covers his back.
- **Facing down the swing STOPS IN FRONT** — it must not carry past straight down the way the side view
  does, or the blade ends up buried in his own legs.
- ⚠ **The blade-back angle must unwind further when the arm travels less.** Side-on the arm reaches −104°,
  so 52° behind it ends at −52° (pointing down). Facing down the arm stops near −34°, and 52° behind *that*
  is +18° — the tip finishing **up in the air** at the end of a downward swing. `DESIGN.md` had already said *"Drive the HAND, then hang the tool off it"* —
the renderer contradicted its own design doc and nobody checked.

**The constraint that caused it, now overturned.** `DESIGN.md` also said *"keep the hand within roughly a
third of a cell of the shoulder"*, because a fist out at arm's length was thought to look detached with no
arm drawn. That is what pinned the hand at the shoulder, and it is incompatible with a swing that reads as
a swing. Owner, 2026-08-04: *"dont care about the arm missing, though it doesnt have to be realistic just
out some."*

**No wrist articulation, and the fist grips ACROSS the handle.** Owner: *"you dont need to have the wrist
angle with respect to the pommel of the sword, its awkward... the sword can be angled back more... so that
the hand is perpendicular with the pommel."* So the blade sits at **one fixed angle behind the arm** for
the whole swing, and the fist is rotated to **`HAND_PERP = 180`**.

⚠ **180 was picked BY EYE, not derived.** `reviews/2026-08-04-swing-arm2/HAND_ROTATION_which_way.png`
renders 0 / 90 / 180 / 270 at the same frame; owner: *"hand perp 180"*. Reasoning about where a wrist
"should" be produced 90 first and then 270, and both were wrong. **Render the four and look** — do not
re-derive it.

⚠ **`HAND_ROT = 225` and `GRIP_EXTRA = 0.16` belong to the OLD shoulder-pivot swing** — they were tuned
when the tool led and the hand was stuck to its grip. Once the hand travels they are meaningless; do not
carry them into the new path.

⚠ **Two units traps here, both hit on the first attempt:**
- `FACINGS` gives the shoulder in **cell units offset from body centre** (`+x` forward, `+y` up) — *not*
  as a fraction of body height. Reading it as a fraction moves the shoulder and the whole arm with it.
- **Reach in cells is much bigger than it sounds.** A cell is half the body height and his half-width is
  only ~0.28 cell, so a reach of 1.0 is a whole torso away. Sanity-check reach against his half-width
  before rendering a batch — 0.6–1.15 produced a sword floating in space beside a man.

### The hand view decides where the arm can be — and it killed the lateral swing (2026-08-04)
A hand sprite is drawn from **one** viewpoint, and that viewpoint tells the viewer where the arm is.
Looking down at the knuckles of a closed fist reads as an arm **stretched out** — the forearm runs away
from you and the fist caps it. The back of the hand is the opposite: you cannot see the back of the hand
on an arm reaching out to the side, because at that extension the wrist turns it edge-on. So a
back-of-hand sprite **forbids** full extension; it only makes sense at a limited distance from the
shoulder.

Approaches 1–12 spin **one** sprite through a ~250° **lateral** arc, so across most of that travel the
drawn view contradicts where the hand is. That is why the swing read as impossible while no single part
looked wrong — and why retiming, re-cutting and swapping between the hands we already had all failed.
**Rotation cannot change a drawn viewpoint.** It only tilts the picture.

**The fix is to remove the conflict, not to draw around it: swing top-to-bottom.** A vertical arc keeps
the arm inside the geometry one hand view can honestly represent, so one sprite carries the whole motion
and no new art is needed. Owner: *"just not have laterally s[w]ings, everything is just a top to bottom
swing, that way we dont have to worry about different hand shapes."*

`swing_lab.py` approaches **20–23** are the vertical set (overhead, diagonal, loaded, chop-and-stop), all
anchored to `IDLE_ANGLE` at both ends. `swing_options.py` renders them one- and two-handed for review.

**Two-handed uses BOTH approved grips** — `grip_back_of_hand.png` on one arm, `grip_palm.png` on the other
(*"the other arm so you would see the palm"*). Never mirror one to make the other: mirroring the back of a
hand gives a mirrored back of a hand, never a palm.

⚠ A vertical swing needs padding on **both** axes — `swing_frames` only padded sideways and clipped the
blade off the bottom.

**ALL THREE SWORD SWINGS RUN ON THE FRAME BUDGET** (`attack_frames`), one spec per facing in
`SWORD_FACINGS`: `SWORD_SIDE` for side-on, `DOUBLE_BACK` for facing down and up. Owner, 2026-08-04:
*"yes we obviously want the quick candidate"*.

The eased `sword_motion` + `arm_swing_frames` path is **no longer used for the sword** — it remains only
because `swing_arm.py` imports it for the lab. Its 27 smoothly-eased frames were what the frame budget
replaced, and leaving the side swing on it while down/up moved across is how the set ended up half
converted without anyone noticing.

**AGREED MOTIONS LIVE IN `tools/player_sprites/motions.py`, WHICH ONLY EVER GROWS.** The lab files
(`swing_tools.py` and friends) are scratch — their variants get overwritten every time a new idea is
tried, and nothing in them is durable.

⚠ **The spec IS the artifact, not just the gif.** Timestamped review folders stopped the *gifs* being
overwritten, but the **numbers that define a motion** had the same bug one level down and it went
unnoticed: each new variant replaced the last in the lab file, so a picked motion had to be dug out of git
history. Owner: *"after all this desperate trying to get you to get organized, you think its ok while
developing which animation to use in the game you are just throwing them away as we go?"*

Every lab run now also writes **`SPECS.json` beside its gifs**, so a review folder is self-describing and
any gif can be traced to its exact numbers without git archaeology.

**A picked motion is COPIED into `motions.py`, never edited in place.** Superseding one means adding the
replacement beside it and marking the old superseded.

**AGREED ANIMATIONS LIVE IN `outfits/bronze/current/anim/`, NOT IN A REVIEW FOLDER.** Bronze is the
reference outfit: motions are designed on it, then applied to the other 21 with their own gauntlets.

**The moment he says "this one", copy it there and add a `CURRENT.md` row the same day.** Everything under
`reviews/` is exploration — later runs regenerate it and it is not safe. Owner: *"these animations need to
stay somewhere so we can use them - we cant just willy nilly explore things and when i say 'this one' just
shrug and move on."*

`CURRENT.md` records, per animation, **the motion constant in code** that produces it as well as his
words, so it can be rebuilt from source alone rather than only existing as a gif.

⚠ `anim/` **is ledgered.** It was once excluded as derived output, on the assumption animations are just
regenerated from the frames. That is wrong: the **motion is the decision**. An agreed animation that is
not ledgered is exactly what went missing across 2026-08-04.

### Recording a decision — `promote.py`, and why it is the only path
An outfit lives in three folders: `scratchpad/` (candidates, in four numbered stages), `current/` (what we
agreed), `archive/` (superseded — nothing is deleted).

```bash
python3 tools/player_sprites/promote.py bronze scratchpad/2-frames/2026-08-02-1344-first-cut "ok lets use this one"
```

One atomic action: copy into `current/`, move what it replaced into `archive/`, append the `CURRENT.md` row
with the owner's words **verbatim**, re-render the animations, refresh the gallery. **Promoting IS
recording.** There is deliberately no way to do one without the other, because every time recording was a
separate step it got skipped — and the approved walk/run constants were lost exactly that way.

`check_sprite_ledger.py` (pre-commit) fails the commit if `CURRENT.md` and `current/` ever disagree, which
catches a hand-copy that bypassed the script. It is a **git** hook, not a Claude Code hook, so it is live
the moment it is wired rather than after a session restart. `anim/` is excluded — those gifs are derived
from the frames and regenerated on every promotion, so they are not decisions.

`migrate.py` moves the pre-existing art into this shape. **Dry run is its default**: every bulk move run
against this folder has destroyed or hidden something, so it prints the plan and only moves on `--go`.

### SUPERSEDED — the body/arm split (abandoned 2026-07-28)
An earlier attempt split each base into a body plus a rotatable weapon ARM. It was abandoned the same day: you
cannot carve animation pieces out of a finished drawing, because a drawn arm only contains the pixels visible
in that one pose — rotate it and you expose a surface that was never drawn. In profile it is worse still, as
the arm overlaps the torso and lifting it out deletes the body behind it.

The armless + floating-hand design replaces it and removes the problem rather than solving it: a fist is
round, self-contained, and reads the same from any angle, so there is nothing to tear and no joint to hide.
`tools/player_sprites/split_base_arm.py` remains only as a record of the attempt.

The sections below are the ORIGINAL 32x48 proposal — kept for the proportions/
perspective/palette guidance, which still applies. Dimensions there are
superseded by the as-built 16x32 above.

## Architecture Decision: LAYERED / Modular Player (2026-06-02)

The player is **composited at runtime from stacked layers**, not a single baked sprite.
This is the only approach that scales to armor + helmets + clothing without a combinatorial
sprite explosion (skin x shirt x pants x chest x helmet). Decided with the user; 4 skin tones
to start.

### Layer stack (back -> front; one SpriteRenderer per layer, ascending sortingOrder)
1. `base_body`  - bare humanoid: skin tone, face, hands, feet. One set per **skin tone** (4).
2. `pants`      - clothing bottom (legs/waist).
3. `shirt`      - clothing top (torso/arms).
4. `chest`      - chest armor, drawn OVER shirt (equipment slot).
5. `hair`       - hair, sits on top of the head; one set per hair style/color.
6. `helmet`     - head equipment, drawn OVER hair (equipment slot).

(`EquippedTool` already renders separately and is out of this stack.)

### Shared anchor template (the thing that makes layers line up)
Every layer is **32x48**, same pivot, same canonical pose per direction. All layers register
to ONE master silhouette so they overlay pixel-perfect. The **`*_down` body is the master**;
up/left/right derive from it. Documented anchor rows (32x48 grid):
- head center column: x=16; head box rows ~0-19
- shoulder/neck line: row ~22
- hand height: row ~32 (arms at side)
- waist line: row ~36
- feet baseline: row ~47
A helmet must occupy the head box; a chest layer the shoulder->waist band; pants waist->feet.

### Registration strategy (CRITICAL - how AI parts align) — PAPER-DOLL (spike-verified 2026-06-02)
gpt-image-1 `generations` produces independent images that will NOT register on their own.

**REJECTED — images/edits inpainting.** Spike result: gpt-image-1's `edits` endpoint does NOT
honor the mask as a hard constraint. Even with a correct head-only mask it regenerated the WHOLE
character (tank top -> armor, arms reshaped, torso drifted). The base body is not preserved, so no
clean layer can be extracted. Do not use edits for layer production.
(Repro: `python3 gen_sprites.py --player-spike` -> `raw_sprites/spike_head_tan_down.png`.)

**CHOSEN — paper-doll with anchor offsets we control.** Spike-verified working:
- **Base bodies**: `generations` against the template prompt (one per skin tone x direction).
- **Equipment / clothing layers**: generate each piece **STANDALONE** (`item_layer_prompt`):
  "draw ONLY the item, no head/body, sized to fit a chibi character, 3/4 top-down, transparent."
  Trim with `getbbox()`.
- **Registration is done by US, not the model:** each layer gets **anchor-offset metadata**
  (where it pins relative to the body's head/torso/waist anchor + a scale factor). Unity stacks
  it over an UNCHANGED body via a SpriteRenderer. Body stays pixel-identical; only the offset/scale
  are tuned per slot.
  (Repro: `python3 gen_sprites.py --paperdoll-spike` -> `raw_sprites/spike_paperdoll_tan_down.png`
  shows the body intact + helmet composited at the head anchor.)
- Anchor knobs live in `paperdoll_spike()` (`scale`, `px`, `py`) — promote these to per-item
  metadata when building the real layer set. Head item ~= head bbox width; sits ~12% above head top.

### Data model (server + network) - prerequisite, NOT yet built
- `PlayerState` (state.go): add `Appearance { SkinTone, Hair, HairColor }` + equipment slots
  `{ Head, Chest, Legs }` holding item_id or empty. `EquippedTool` already exists.
- `items.json`: wearables get `equip_slot` (head/chest/legs) + a layer sprite key.
- `EntityData` / join payload: must carry appearance + visible equipment so REMOTE clients
  render the same stack (today it only sends id/type/x/y/facing).

### Resources layout
```
Resources/Player/body/{tone}_{dir}.png        # e.g. body/tan_down.png   (4 tones x 4 dir)
Resources/Player/hair/{style}_{dir}.png
Resources/Player/wear/{slot}/{item}_{dir}.png # wear/head/iron_helm_down.png, wear/chest/..., wear/legs/...
```
File naming stays `{thing}_{direction}.png` per existing convention.

### Animation / walk frames (spike-verified 2026-06-02)
Spikes (`--walk-sheet` then `--segment-sheet`) established:
- gpt-image-1 **CAN** draw several consistent walk poses of the same chibi in one sheet
  (foot-forward / passing poses read as a walk).
- It will **NOT** honor a requested frame COUNT or even spacing (asked 4, got 3, uneven). So
  fixed-column slicing is wrong.
- **Working extraction:** generate sheet -> `segment_sheet()` splits figures by TRANSPARENT
  column gaps (variable count) -> trim + re-center each onto the fixed 32x48 anchor -> frames.
  Verified: 3 clean figures extracted from `walksheet_medium_down.png`.
- Frame count is nondeterministic -> normalize: pad/loop to a target (a 2-frame alternating
  step-bob is enough at this zoom; 4 is nicer). Re-roll a sheet if it yields too few.

**Animation x layering cost (the expensive combination, needs a decision):**
Full per-frame layered art = every equipment layer redrawn & registered for every walk frame x
direction = explosion. Pragmatic compromise to recommend:
- Animate the **base body** only (legs/arms move) -> a few frames per direction per skin tone
  (skin tones still come from recoloring ONE master frame set).
- Equipment/clothing = a SINGLE overlay per direction that rides the body's torso/head anchor
  each frame (slight bob), NOT redrawn per frame. Cheap, reads fine at game zoom.
- Only redraw equipment per-frame later if a specific item visibly needs it.

### Build order (de-risk before mass-generating)
1. **Registration spike** (cheap, ~2-3 API calls): one base body -> `images/edits` add a
   helmet -> confirm the helmet pixels land on the head box and overlay cleanly. PROVE the
   edits approach before scaling. (If it fails, fall back to hand-registered atlas.)
2. Generate 4 base bodies (4 dir each) = the "variants to choose from".
3. Hair + a couple clothing layers; verify stacking in Unity.
4. Wire the data model (Go + network + multi-SpriteRenderer client) — separate effort,
   C# cannot be compiled here (needs Unity).

---

## Design Philosophy

### Style Reference: Terraria-Cute-Retro
- **Chibi proportions**: Large head relative to body (head is ~40% of total height)
- **Chunky, readable**: 2-3 pixel wide limbs, not thin single-pixel lines
- **Cute over realistic**: Simplified features, big expressive elements
- **Retro pixel art**: Limited palette, clear shapes, no anti-aliasing

### Perspective: 45-Degree Top-Down (NOT Side View)
This is critical. We're looking DOWN at the character from above and in front.

**What this means:**
- You see the TOP of the character's head (hair is prominent oval shape)
- Face is visible BELOW the top of head
- Even when facing left/right, use 3/4 view (NOT pure profile)
- Body is foreshortened (shorter than side-view would show)

**Common mistake to avoid:**
Side-view sprites show a profile (nose sticking out, one eye visible from side).
Our sprites should show the face more frontally even when the body is turned.

---

## Character Specifications

### Base Size: 32x48 pixels (2x3 cells)

Player sprites occupy 2 cells wide by 3 cells tall (where each cell is 16x16).
This allows the player to fit through 2-block-wide doorways.

```
Row breakdown (48 pixels):
  0-5   : Top of head (hair crown, viewed from above)
  6-15  : Hair sides/back + Face (framing face)
  16-23 : Face lower + Upper torso (eyes, shirt top)
  24-35 : Torso (shirt, arms)
  36-47 : Lower body + Legs (waist, pants, feet)
```

### Terraria-Style Proportions

The character uses chunky, blocky shapes similar to Terraria:
- Huge rectangular head (~40% of height)
- White eyes with 2x2 dark pupils
- Blocky rectangular limbs (not organic/rounded)

```
Width distribution (32 pixels):
  - Character body: 18-22 pixels wide (centered)
  - Head: 18-22 pixels wide (huge, rectangular)
  - Shoulders: 20-24 pixels wide
  - Legs: 12-16 pixels wide (gap between)

Height distribution (48 pixels):
  - Head+Hair: ~20 pixels (42%)
  - Body: ~18 pixels (37%)
  - Legs: ~10 pixels (21%)
```

### Relationship to Grid
- Grid cell: 16x16 pixels
- Blocks: 16x20 pixels (3D cubes)
- Player: 32x48 pixels (2 cells wide, 3 cells tall)
- Player can walk through 2-block-wide openings

---

## Direction Sprites

### Down (Facing Camera)
The "hero shot" - most important sprite.

**What we see:**
- Oval top-of-head (hair) - prominent at top
- Full face below - both eyes visible, centered
- Shoulders/chest - symmetrical, arms at sides
- Legs - feet pointing toward camera

```
Visual guide (simplified):
     ████████        <- hair top (oval)
    ██████████       <- hair sides
     ████████        <- face (skin)
    ████  ████       <- eyes
     ██████          <- mouth area
    ██████████       <- shoulders/shirt
    ██████████       <- torso
     ████████        <- waist
      ██  ██         <- legs
      ██  ██         <- feet
```

### Up (Facing Away)
**What we see:**
- Oval top-of-head (hair) - dominant
- Back of head/hair - no face visible
- Back/shoulders
- Legs from behind

### Left (Facing Left, 3/4 View)
**NOT a side profile!** This is a 3/4 view.

**What we see:**
- Oval top-of-head, slightly off-center
- Face turned left BUT one eye still visible (or at least implied)
- Body turned, left shoulder forward
- Legs, left leg forward

### Right (Facing Right, 3/4 View)
Mirror of left.

---

## Color Palette System

### Principle: 3 Colors Per Material
Every material uses exactly 3 shades:
1. **Light** - Hit by light (top-left areas)
2. **Base** - Main color (most surface area)
3. **Dark** - Shadow (bottom-right areas)

### Skin Tones
```python
# Default (warm beige)
SKIN = {
    'light': (240, 200, 170),  # Highlights
    'base':  (220, 175, 140),  # Main skin
    'dark':  (180, 130, 100),  # Shadows
}
```

### Hair Colors
```python
HAIR_BROWN = {
    'light': (120, 85, 65),
    'base':  (90, 60, 45),
    'dark':  (60, 40, 30),
}

HAIR_AUBURN = {
    'light': (170, 95, 70),
    'base':  (140, 65, 45),
    'dark':  (100, 45, 30),
}

HAIR_BLACK = {
    'light': (70, 70, 80),
    'base':  (45, 45, 55),
    'dark':  (25, 25, 35),
}

HAIR_BLONDE = {
    'light': (230, 200, 140),
    'base':  (200, 170, 100),
    'dark':  (160, 130, 70),
}
```

### Clothing Colors
```python
SHIRT_TEAL = {
    'light': (90, 160, 150),
    'base':  (60, 130, 120),
    'dark':  (40, 90, 90),
}

SHIRT_GREEN = {
    'light': (95, 150, 100),
    'base':  (65, 120, 70),
    'dark':  (45, 85, 50),
}

SHIRT_BLUE = {
    'light': (100, 135, 190),
    'base':  (70, 100, 160),
    'dark':  (50, 70, 120),
}

SHIRT_RED = {
    'light': (190, 105, 100),
    'base':  (160, 70, 70),
    'dark':  (120, 50, 50),
}

PANTS_BROWN = {
    'light': (130, 100, 75),
    'base':  (100, 75, 55),
    'dark':  (70, 50, 40),
}

PANTS_DARK = {
    'light': (100, 80, 65),
    'base':  (75, 55, 45),
    'dark':  (50, 35, 30),
}

PANTS_GRAY = {
    'light': (130, 130, 135),
    'base':  (100, 100, 105),
    'dark':  (70, 70, 75),
}

PANTS_TAN = {
    'light': (200, 180, 145),
    'base':  (175, 150, 110),
    'dark':  (140, 115, 80),
}
```

### Eye Color
```python
# Simple dark color for eyes
EYE = (30, 30, 35)  # Near-black, not pure black
```

---

## Lighting Rules

### Light Source: Top-Left
Consistent with all other sprites in the game.

```
Light hits:
  - Top of head (lighter hair)
  - Left side of face
  - Left shoulder
  - Top of any surface

Shadow falls:
  - Bottom-right of head
  - Right side of body
  - Under arms
  - Bottom edges
```

### Application Example
```
For a facing-down sprite:

  Hair row 0-1: Use light shade (crown catching light)
  Hair row 2-4: Left side = light, right side = dark
  Face: Left cheek = light, right cheek = base
  Shirt: Left arm/side = light, right = dark
  Pants: Similar left-right gradient
```

---

## Character Variants

### Farmer (Default)
- Hair: Brown
- Shirt: Teal
- Pants: Brown
- Personality: Friendly, hardworking

### Ranger
- Hair: Auburn
- Shirt: Green
- Pants: Dark Brown
- Personality: Adventurous, nature-focused

### Scholar
- Hair: Black
- Shirt: Blue
- Pants: Gray
- Personality: Studious, curious

### Merchant
- Hair: Blonde
- Shirt: Red
- Pants: Tan
- Personality: Cheerful, entrepreneurial

---

## Iterative Design Process

### Pass 1: Block Out Shape
1. Define the silhouette using base colors only
2. Ensure proportions are correct
3. Check that it's readable as a person

### Pass 2: Add Shading
1. Apply light/dark variants based on lighting
2. Add eyes and facial features
3. Refine edges

### Pass 3: Polish
1. Check silhouette (squint test)
2. Verify lighting consistency
3. Test alongside other sprites
4. Adjust colors if needed

### Review Questions
After each pass, ask:
1. "Does this look cute, not goofy?"
2. "Can I tell which direction they're facing?"
3. "Is the top-of-head visible (45-degree view)?"
4. "Does it match Terraria's chunky charm?"

---

## File Naming Convention

```
{character}_{direction}.png

Examples:
  farmer_down.png
  farmer_up.png
  farmer_left.png
  farmer_right.png
  ranger_down.png
  ...
```

Output directory: `BugFarmerClient/Assets/Sprites/Player/`

---

## Common Mistakes to Avoid

1. **Too thin**: Limbs should be 4-6 pixels wide at 32x48 scale, not single-pixel lines
2. **Pure side view**: Left/right should be 3/4 view, not profile
3. **No top-of-head**: From 45-degrees above, hair crown must be visible
4. **Pure black outlines**: Use dark variant of material color instead
5. **Too realistic**: Use blocky shapes, not organic curves
6. **Wrong proportions**: Head should be ~40% of height for cute look
7. **Inconsistent lighting**: Light always from top-left
8. **Wrong size**: Player is 32x48 (2x3 cells), NOT 16x20
