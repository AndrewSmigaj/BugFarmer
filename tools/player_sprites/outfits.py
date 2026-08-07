"""outfits.py — WHICH outfits exist, and the one prompt that makes any of them.

The sheet prompt is identical for every outfit except three slots: the set's name, its material and
colours, and its headgear. Keeping the shared 90% in one string is the point — when a sheet comes
back wrong the fix belongs in the template, once, not copied into ten places by hand.

Every set gets headgear. A set without one doesn't match the rest and has to be redone.

  python3 tools/player_sprites/outfits.py list
  python3 tools/player_sprites/outfits.py sheet   platinum swamp-gear      # one API call each
  python3 tools/player_sprites/outfits.py gauntlet platinum swamp-gear     # one API call each
"""
import datetime
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official as O                       # noqa: E402  HAND_ROLES — how many hands, and what each is

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
BASES = os.path.join(PLAYER, "bases")

# name -> (what the set IS, its material + colours, its headgear, the gauntlet material)
OUTFITS = {
    # The two ant colourways, picked 2026-08-05 from the undirected face-visible batches. The chosen
    # figure is passed as an extra REFERENCE by `sheet` so the 12 frames match the design that was
    # actually chosen, rather than a fresh interpretation of the words.
    "fireant": ("fire-ant carapace armour",
                "orange-red and deep red ant chitin, overlapping segmented plates with darker red "
                "shading and leg-spur plates at the hips",
                "an ant-head helm with a ridged crest, a dark compound eye on each side and two curved "
                "antennae, OPEN AT THE FRONT so the character's face is visible - draw the face, eyes "
                "and hair; the helm frames it and never covers it",
                "orange-red ant chitin"),
    "blackant": ("black-ant carapace armour",
                 "near-black and dark charcoal ant chitin, smooth plates with chevron banding across "
                 "the chest",
                 "a smooth rounded ant-head hood-helm with two curved antennae, OPEN AT THE FRONT so "
                 "the character's face is visible - draw the face, eyes and hair; the hood frames it "
                 "and never covers it",
                 "near-black ant chitin"),
    # --- from the armour catalog's base ladder ---
    "platinum": (
        "polished platinum plate armour",
        "bright white-silver platinum plate with cool blue-white highlights and pale grey shadows",
        "full platinum great-helm with a narrow eye slit",
        "polished platinum metal"),
    "leather": (
        "plain boiled-leather armour",
        "tan and mid-brown boiled leather with darker brown straps and stitching",
        "brown leather cap with a short brim",
        "worn tan leather"),
    # The four that finish the ladder. Each is written to be told apart from the metals already
    # built (bronze warm brown-gold, silver white-grey, gold yellow, platinum blue-white) — at
    # sprite size a set earns its rung by COLOUR, so "another grey metal" would be a wasted tier.
    "padded": (
        "a quilted cloth gambeson",
        "natural off-white and oatmeal linen, quilted into vertical padded tubes with visible "
        "stitching seams, soft cloth with no metal anywhere",
        "quilted cloth coif hood covering the head and neck",
        "quilted off-white linen"),
    "copper": (
        "copper plate armour",
        "warm orange-pink copper plate with salmon highlights and patches of pale green verdigris "
        "in the crevices",
        "copper kettle-helm with a wide flat brim",
        "warm orange-pink copper"),
    "iron": (
        "rough iron plate armour",
        "dark blue-grey unpolished iron, rough and pitted, with dull rust-brown staining around "
        "the rivets and edges",
        "iron barbute helm with a narrow T-shaped face opening",
        "dark pitted iron"),
    "steel": (
        "tempered steel plate armour",
        "mid gunmetal-grey steel with a faint cold blue sheen, bright polished bevels along every "
        "plate edge, noticeably darker than silver",
        "steel sallet helm with a long tail and a visor",
        "polished gunmetal steel"),
    # --- bonus concept from the catalog: the "collector" (armor.md, section B) ---
    "entomologist": (
        "a bug-catcher's field outfit",
        "khaki and olive canvas field jacket and trousers, brown leather belt and shoulder strap "
        "with rows of small specimen pouches and glass vials",
        "pale khaki pith helmet with a fine dark mesh veil hanging over the face",
        "khaki canvas glove"),
    "ranger": (
        "a woodland ranger's outfit",
        "forest-green wool cloak over a brown leather jerkin, muted greens and browns",
        "deep green hood pulled up over the head, face in shadow",
        "dark green leather"),
    # --- owner-directed ---
    "swamp-gear": (
        "swamp waders and oiled canvas",
        "murky green-brown oiled canvas and moss-stained leather, wet-looking dark patches",
        "hooded oilskin cowl with a dark mesh veil across the face",
        "muddy green oilskin"),
    "fisherman": (
        "a fisherman's oilskins",
        "bright yellow oilskin raincoat and dark rubber boots, glossy highlights",
        "yellow sou'wester rain hat with a wide back brim",
        "yellow rubber"),
    "wizard-robe": (
        "a wizard's robe",
        "deep indigo-purple robe with pale gold star and moon trim at the hem and cuffs",
        "tall wide-brimmed pointed wizard hat, same indigo with gold trim",
        "indigo cloth"),
    "hornet-stinger": (
        "hornet-stinger armour",
        "black and bright yellow banded chitin plates, glossy, with sharp spined edges",
        "hornet-head helm with two large dark compound eyes and short antennae",
        "black and yellow banded chitin"),
    # --- mine: bug-derived sets that fill gaps the catalog leaves ---
    "beetle-shell": (
        "beetle-shell armour",
        "iridescent green-black beetle elytra plates with a hard glossy sheen and purple-blue "
        "colour shifts at the edges",
        "domed beetle-shell helm with a single short horn on the front",
        "iridescent green-black elytra"),
    "moth-wool": (
        "moth-wool clothing",
        "soft pale grey and warm tan felted wool, thick and slightly fuzzy, with a deep fluffy "
        "collar",
        "fuzzy wool hood with two feathery moth antennae standing up from it",
        "pale grey felted wool"),
    "glowworm": (
        "glowworm armour",
        "dark slate-grey carapace with glowing yellow-green panels set into the chest, thighs and "
        "shoulders, casting a faint green light on the plates around them",
        "dark slate helm with a glowing yellow-green strip across the visor",
        "dark slate carapace with a small glowing green panel"),
}

# ---------------------------------------------------------------------------
# EXPLORE — pick the DESIGN before paying for a walk cycle.
#
# The first pass went straight to finished 12-frame sheets, so the first time a set could be judged
# it had already been paid for in full and there was nothing to compare it against. This mode draws
# three genuinely different designs of ONE set, standing still and large enough to actually see.
# Owner: "I dont think we are spending enough time getting a good reference sprite."
#
# The three options must have different PARENTS, not three tunings of one idea — the same discipline
# the swing design used, for the same reason: left alone they collapse into one.
#
# Background is MAGENTA, not black. Black is the one colour the armour also contains, which is how
# the cutter came to delete 17% of hornet-stinger as "background". A key colour the art never uses
# turns a judgement call into an exact test.
EXPLORE = """Draw THREE different design options for {what}, side by side in a single row, on a FLAT SOLID MAGENTA background (pure magenta, RGB 255 0 255). The magenta must be completely flat and uniform with nothing else drawn on it - no shadow, no gradient, no vignette, no ground, no scenery, no text.

Each of the three is the SAME character wearing a DIFFERENT DESIGN of the outfit: standing still, facing the viewer, full body from head to feet, all three at the same scale and standing on the same baseline.

Because the character has NO ARMS, do not draw arms, hands, elbows, forearms or gauntlets. Each shoulder ends in a rounded shoulder cap at the armless shoulder opening. This is deliberate - the hands are separate sprites added later.

The three designs, left to right:
1. {a}
2. {b}
3. {c}

{head} The body is covered from the shoulders to the boots, with no bare skin between the waist and the boots.

CRITICAL - THE FIGURE WILL BE SHRUNK TO ABOUT 40 PIXELS TALL. Everything below follows from that:
- What makes each design recognisable must be its SILHOUETTE - the OUTLINE shape of the hat, hood, helm, crest, shoulders and hem. Shape survives shrinking. Surface pattern does not.
- Do NOT distinguish the designs by engraving, filigree, trim, embroidery, scrollwork, inlay, rivets or fine linework. At 40 pixels tall all of that collapses into grey mush and the design is lost.
- Use no more than four or five flat colour areas per figure, in big chunky blocks. Think a bold cut-paper shape, not an illustration.
- If a design would only look different from the others when seen large, it is the wrong design.

Draw each figure with HARD pixel edges against the magenta. Do not blur, feather, glow or blend the figure into the background. Do not draw a heavy black outline around the figure - where an outline is needed use a darker shade of that figure's own colours, one pixel thick.

Do not use magenta, pink or purple ANYWHERE on the figures themselves - not on the armour, not as glowing eyes, not as trim. Magenta is reserved for the background alone."""

# name -> (what the set is, [three designs with different parents])
HEAD_COVERED = ("Every design covers the whole head with its own headgear.")

# Owner, 2026-08-05: "i do want to see the players face though if possible". An open-faced helm, so the
# character reads as a PERSON in ant armour rather than a sealed shell.
HEAD_FACE = ("Every design has headgear that leaves the character's FACE VISIBLE and uncovered - an "
             "open-faced helm, a raised visor, a framing hood or a crown-like piece. Draw the face: eyes, "
             "nose and mouth, human skin. The head is never fully enclosed and there is no blank visor "
             "slit. The headgear frames the face, it does not hide it.")

FACE_SETS = {"ant-carapace-red", "ant-carapace-black",
             "ant-carapace-red2", "ant-carapace-black2"}

EXPLORATIONS = {
    # Second undirected pass on each colourway, for variety. Same prompt as the first - the point is a
    # different roll, not a different brief.
    "ant-carapace-red2": ("armour made from RED FIRE-ANT parts - deep red and orange-red chitin plates, "
                          "shell, carapace, mandibles, leg segments. ARMOUR WORN BY A PERSON", (
        "your own design - decide for yourself what this armour looks like",
        "a second design, clearly and obviously different from the first",
        "a third design, clearly and obviously different from both of the others",
    )),
    "ant-carapace-black2": ("armour made from BLACK ANT parts - near-black and dark charcoal chitin "
                            "plates, shell, carapace, mandibles, leg segments. ARMOUR WORN BY A PERSON", (
        "your own design - decide for yourself what this armour looks like",
        "a second design, clearly and obviously different from the first",
        "a third design, clearly and obviously different from both of the others",
    )),
    # Two colourways to lock in, undirected. Owner: "we will have both black and red fireant versions...
    # lets do 2 more attempts on each red and black so we can lock those in, i do want to see the players
    # face though if possible". No design briefs - the undirected round beat both directed ones.
    "ant-carapace-red": ("armour made from RED FIRE-ANT parts - deep red and orange-red chitin plates, "
                         "shell, carapace, mandibles, leg segments. ARMOUR WORN BY A PERSON", (
        "your own design - decide for yourself what this armour looks like",
        "a second design, clearly and obviously different from the first",
        "a third design, clearly and obviously different from both of the others",
    )),
    "ant-carapace-black": ("armour made from BLACK ANT parts - near-black and dark charcoal chitin "
                           "plates, shell, carapace, mandibles, leg segments. ARMOUR WORN BY A PERSON", (
        "your own design - decide for yourself what this armour looks like",
        "a second design, clearly and obviously different from the first",
        "a third design, clearly and obviously different from both of the others",
    )),
    # OPEN exploration - the design is NOT specified. Owner, 2026-08-05: "just do three ant carapace
    # armor versions without telling it what to put other than the sprite and it is made from ant parts
    # and carapace". The technical constraints stay (magenta, armless, silhouette-over-detail, no magenta
    # on the figure) because those are quality rules, not design direction. No CHOSEN_ reference either -
    # a reference would steer it, which is the opposite of the point.
    "ant-carapace-open": ("armour made from ant parts - chitin plates, shell, carapace, mandibles, "
                          "leg segments, whatever an ant provides. It is ARMOUR WORN BY A PERSON, not "
                          "an ant costume: a helmet on a head, plates on a body", (
        "your own design - decide for yourself what this armour looks like",
        "a second design, clearly and obviously different from the first",
        "a third design, clearly and obviously different from both of the others",
    )),
    # Variants of the CHOSEN soldier-plate design (option 1 of the 2026-08-05 three). Owner: "i want the
    # first version, so give me three variants of it (the soldier carapace)". The chosen figure is passed
    # as a REFERENCE so these stay on that design instead of drifting into three new ideas.
    "ant-carapace-soldier": ("ant-carapace SOLDIER-PLATE armour - keep the design in the attached "
                             "reference: dark red-brown chitin plates, a helm whose visor is flanked by "
                             "the two repurposed MANDIBLES as curved jaw guards. Vary only what is "
                             "described below", (
        "HEAVY PAULDRONS - the same helm, but the silhouette is dominated by very broad blocky shoulder "
        "plates flaring well past the body, and a deep chest plate. Short jaw guards. A tank",
        "LONG TUSKS - the two mandible jaw guards sweep much FURTHER FORWARD past the chin like curved "
        "tusks, and are the largest feature of the whole figure. Narrower shoulders so the jaw reads",
        "HIGH CREST - a tall raised ridge crest running front-to-back over the top of the helm, making "
        "the figure noticeably taller, with a tighter trimmer body and close-fitting shoulders",
    )),
    "ant-carapace": ("ant-carapace armour", (
        "a SOLDIER-PLATE harness - armour forged from a soldier ant's head-plate, with the two MANDIBLES "
        "repurposed as a pair of curved jaw guards sweeping forward on either side of the visor. Thick "
        "dark red-brown chitin, heavy square pauldrons. A HELMET on a person, not an ant's head",
        "BANDED SEGMENT armour - many overlapping curved carapace segments worn as lamellar bands across "
        "the chest, waist and thighs, warm ochre-amber, cinched at the waist, with a low smooth domed helm "
        "cut from a single shell plate. Reads as banded armour, no insect features",
        "an ALATE CLOAK harness - a pair of long folded wing-cases worn as a stiff back-cape over the "
        "shoulders, glossy near-black chitin plates beneath, and a smooth rounded helm with a single swept "
        "crest cut from carapace. The wing-cape is the silhouette",
    )),
    "ranger": (
        "a woodland ranger's outfit",
        ["a HOODED FOREST SCOUT - a deep hood pulled up with the face in shadow, a long ragged "
         "cloak hanging over a light leather jerkin, muted forest greens and cool greys, lean and "
         "stealthy",
         "a PRACTICAL WOODSMAN - no hood, a short brimmed felt hat with a feather in the band, a "
         "brown leather jerkin over a moss-green tunic, belts and pouches, face clearly visible, "
         "rugged and grounded",
         "an ELITE FOREST WARDEN - layered overlapping leaf-shaped plates in deep lacquered green "
         "with bronze edging, a helm with swept antler-like prongs, richer and more ceremonial"]),

    # Owner: the current one "looks like a rhinocerous" — so the single frontal horn is banned, and
    # each option takes a DIFFERENT REAL BEETLE as its parent rather than three horn sizes.
    "beetle-shell": (
        "beetle-shell armour",
        ["a STAG BEETLE warrior - the helm's defining shape is a pair of huge curved MANDIBLE pincers "
         "sweeping forward on either side of the face, glossy blue-black chitin, broad flat shoulders. "
         "NO horn on the forehead",
         "a JEWEL BEETLE guard - a smooth rounded domed elytra shell forming a wide turtle-like back "
         "and shoulders, bright metallic emerald green shading to copper, a simple smooth rounded helm. "
         "Bold and rounded, NO spikes, NO horn",
         "a GROUND BEETLE trooper - low flat overlapping segmented plates like a woodlouse, matte "
         "charcoal black, a narrow wedge-shaped helm, purely structural and armoured. NO horn, NO "
         "ornament"]),

    # Owner likes the concept; the three options are three different GLOW STRATEGIES, because where
    # the light sits is a silhouette-scale decision and the colour of the plates is not.
    "glowworm": (
        "glowworm armour",
        ["a LIVING LANTERN - almost everything is near-black carapace, and ONE big round glowing "
         "yellow-green lantern organ sits on the belly, large enough to read as a lamp, throwing a "
         "pool of green light onto the plates and boots around it",
         "SEAM-LIT PLATES - dark slate-grey plates separated by thick bright glowing cyan-green seam "
         "lines that trace the edges of the chest, thighs and helm, so the figure reads as a dark "
         "shape drawn in glowing outline",
         "a SOFT LARVA GLOW - a pale, plump, softly segmented body like a grub, each segment glowing "
         "warm yellow-green from inside so the whole figure is luminous rather than dark, with a "
         "smooth rounded featureless head"]),

    # Owner: "we need a remake of swamp gear, not sure what to put" — so the three options are three
    # different ANSWERS to what a swamp set is for, not three shades of green.
    "swamp-gear": (
        "swamp gear",
        ["PRACTICAL WADERS - chest-high rubber waders over a short oilskin coat, a wide sou'wester "
         "hood, muted olive and mud brown, straps and buckles, plainly functional working kit",
         "a MOSS-CLOAKED BOG STALKER - draped hanging moss, lichen and strips of bark over a dark "
         "hunched form, an irregular ragged outline that breaks up the shape, deep greens and greys, "
         "looks grown rather than made",
         "a SEALED MARSH SUIT - a smooth sealed hooded suit with a round glass faceplate and a "
         "breathing filter at the chin, pale grey-green rubber, clean simple curved shapes, "
         "protection against foul air"]),

    # Owner: the current one "looks ridiculous like curious george with the goofy yellow thing" — so
    # the cartoon-bright sou'wester is out and the three options are three different WATERS.
    "fisherman": (
        "a fisherman's outfit",
        ["a WEATHERED SEA FISHERMAN - a thick cream cable-knit sweater under weathered ochre oilskin "
         "bib trousers and heavy boots, a soft dark hood. Muted and salt-worn, NOT bright yellow, NOT "
         "cartoonish",
         "a RIVER ANGLER - chest waders in tan canvas over a many-pocketed olive vest, a wide flat "
         "brimmed hat, greens and sand browns, freshwater and practical",
         "a DEEP-WATER HARPOONER - a heavy dark storm coat wrapped with coils of rope, a deep hood "
         "over a scarfed face, weathered navy and rust, rugged and adventurous"]),

    # Owner: platinum is the TOP of the ladder and must "stress that it is fancy". The lesson from
    # ranger option 3 is baked in — fancy has to live in the SILHOUETTE (crest, plume, cape, wings),
    # never in engraving, because engraving is exactly what dies at 40px.
    "platinum": (
        "platinum plate armour, the finest armour in the game",
        ["a CRESTED CHAMPION - bright white-silver plate with a TALL SWEEPING PLUME crest standing up "
         "from the helm, and a long cape falling behind the shoulders. The grandeur is entirely in "
         "those two big shapes",
         "a WINGED PALADIN - mirror-bright blue-white plate with large upswept WING-SHAPED shoulder "
         "pieces rising above the shoulders and a halo-like ring behind the head. Smooth and radiant, "
         "almost no surface detail",
         "a HORNED MONARCH - heavy regal platinum with a CROWN of tall spikes around the helm and "
         "broad squared-off pauldrons, a wide flared skirt of plates at the hips. Imposing and "
         "top-heavy"]),

    # ── BATCH 1: THE BASE LADDER (2026-08-06) ────────────────────────────────────────────────────
    # Six rungs, settled: leather -> wood -> copper -> iron -> steel -> platinum. Bronze, tin, stone
    # and silver-as-a-set are CUT (see docs/product/design/brainstorm_armor.md §3).
    #
    # The three options in each row differ by SILHOUETTE ONLY — helm outline, shoulder mass, hem shape.
    # The shared prompt already warns that at ~40px surface detail collapses to mush, so distinguishing
    # a design by trim or engraving produces three sheets nobody can tell apart. Each rung also has to
    # read as ITS MATERIAL at a glance, and the four grey rungs (iron/steel/silver/platinum) separate by
    # BRIGHTNESS as much as by shape — armor.md records the values iron 66, steel 90, platinum 157.

    "leather": ("plain boiled-leather armour - tan and mid-brown, darker straps and stitching, no metal "
                "plates anywhere", (
        "a HOODED JERKIN - a soft pointed hood worn up, a short sleeveless jerkin, a plain belt, and "
        "trousers tucked into low boots. The silhouette is soft and rounded all over, no hard edges",
        "a STUDDED BRIGANDINE - a stiff square-cut torso piece sitting proud of the body with a broad "
        "waist belt, bare shoulders, and a short skirt of hanging leather strips at the hips",
        "a LONG RIDING COAT - a tall standing collar framing the head, no hood, and a long coat that "
        "flares below the knee. Tall and narrow, the tallest silhouette of the three")),

    "wood": ("armour made of WOOD - bark plates, pale carved timber and darker bark, bound with cord. "
             "Wood is the rung ABOVE leather, so it must read as sturdier than cloth, not as a costume", (
        "BARK PLATES - broad curved slabs of thick bark strapped over the chest and thighs like plate, "
        "with a low domed bark helm. Chunky and rounded, the outline of a beetle's back",
        "WOVEN WITHY - basket-woven flexible branches forming a barrel-shaped torso and a tall open "
        "helm-cage around the head. Light, airy, with a visibly woven outline",
        "A CARVED YOKE - a heavy squared timber shoulder-yoke sitting across both shoulders, a plain "
        "board cuirass hanging from it, and no helm at all. Wide, flat-topped, top-heavy")),

    "copper": ("copper plate armour - warm orange-pink metal with salmon highlights and patches of pale "
               "green verdigris in the crevices", (
        "a KETTLE-HAT SET - a wide flat circular brimmed helm, a plain rounded breastplate and a short "
        "flared skirt of plates. The wide disc of the brim is the whole silhouette",
        "a MUSCLE CUIRASS - a smooth rounded sculpted torso, a close-fitting cap helm with cheek pieces, "
        "and short thigh plates. Curved, organic, almost no straight lines",
        "a SCALE COAT - overlapping round copper scales over a long knee-length coat, a plain conical "
        "helm. Narrow, tall and columnar with a scalloped hem")),

    "iron": ("rough iron plate armour - dark blue-grey unpolished iron, pitted, with dull rust-brown "
             "staining at the rivets and edges. Clearly DARKER than steel", (
        "a BARBUTE SET - a tall helm with a narrow T-shaped face opening, plain rounded shoulders and "
        "long hanging thigh plates. Tall, closed and severe",
        "BANDED MAIL - horizontal iron bands wrapped around the torso and limbs, a low open-faced skull "
        "cap. Wide, barrel-chested, the outline visibly ringed",
        "a RIVETED BRIGANDINE with a HORNED helm - a square-cut torso, bulky squared pauldrons, and two "
        "short blunt horns angling out from the helm. Broad, angular and top-heavy")),

    "steel": ("tempered steel plate armour - mid gunmetal grey with a faint cold blue sheen and bright "
              "polished bevels along every plate edge. Clearly BRIGHTER than iron", (
        "a SALLET SET - a smooth rounded helm with a long pointed tail sweeping back off the skull, a "
        "fitted breastplate and articulated tassets. Streamlined, swept back, aerodynamic",
        "FULL PLATE - complete enclosing plate with very large rounded pauldrons, a closed visored helm "
        "and a long skirt of plates. The biggest, heaviest outline of the three",
        "a FLUTED HALF-PLATE - a breastplate covered in deep vertical fluting ridges, open shoulders, an "
        "open-faced helm and plain trousers below the waist. Narrow-shouldered and clearly LESS armoured "
        "than the other two")),

    "platinum-r2": ("polished platinum plate armour, the FINEST armour in the game - bright white-silver "
                    "with cool blue-white highlights and pale grey shadows. It must read as the top of "
                    "the ladder without any gold, colour or gemstones", (
        "a CRESTED CHAMPION - a tall thin blade-like crest running front to back over the helm, a "
        "close-fitted breastplate and long clean leg plates. Tall, narrow and vertical",
        "a WINGED GUARDIAN - large upswept wing-shaped shoulder pieces rising well above the shoulders, "
        "a smooth radiant breastplate, almost no surface detail. The widest silhouette",
        "a TOWER SET - deep squared-off pauldrons, a flat-topped closed helm and a broad flared skirt of "
        "plates reaching the knee. Blocky, rectangular and immovable")),
}


SHEET = """Draw a single sprite sheet showing the SAME character in {what} as a 12-frame walk-cycle sheet. Use the same character design, proportions, and no-arm anatomy consistently across the whole sheet.

Layout: 3 rows by 4 columns, evenly spaced, all sprites at the same scale and aligned to the same baseline within each row.

Row 1: FRONT walk cycle, 4 distinct frames.
Row 2: BACK walk cycle, 4 distinct frames.
Row 3: RIGHT-FACING SIDE walk cycle, 4 distinct frames.

Very important: the 4 frames in each row must be DIFFERENT phases of a walk cycle, not repeated standing poses.

For each row, the 4 columns must be:
Column 1: left leg forward, right leg back.
Column 2: passing pose, legs closer together, transition between steps.
Column 3: right leg forward, left leg back.
Column 4: passing pose opposite to column 2, transition back toward column 1.

Because the character has NO ARMS, the walking motion must be shown by leg motion, slight hip shift, and a subtle torso/head bob only. Do not add arms, hands, elbows, forearms, or gauntlets. The rounded shoulder caps must end at the armless shoulder openings.

Outfit: {material}. Include a {headgear}, a breastplate, rounded shoulder caps, a waist and hip piece covering the crotch, thigh plates on both legs, greaves, and boots. No bare skin between the waist and the boots. The headgear is on the character in all 12 frames.

Keep the front row front-facing, the back row back-facing, and the bottom row a strict right-facing side profile. Do not drift into a three-quarter view.

Big simple shapes, not fine detail. This is a small pixel art sprite sheet. All 12 sprites must clearly be the same character, but each frame in a row must be a distinct walking frame. If two adjacent frames in a row are identical, the sheet is wrong."""

GAUNTLET = """The attached image is a sprite sheet of a character wearing {what}.

Draw FOUR small HANDS in a row on a black background, evenly spaced, large and centred. Nothing else in the image - no character, no body, no arms, just the four hands.

Each hand is made of {glove}, the SAME material as the armour in the attached image, with the same darker shadows and the same bright highlights.

Left to right, the same hand from four angles: (1) back of the hand facing the viewer, (2) palm side, (3) in profile facing right, (4) three-quarter view.

Care about the SILHOUETTE above all. The outline is a soft rounded shape, slightly taller than wide, narrowing a little at the wrist. No separate fingers are drawn - at this size the hand reads entirely by its outline and two or three shading bands inside it.

Big simple shapes, chunky pixels. This is a small pixel art sprite - each hand is about ten pixels across in the game, so use a handful of large blocks, no rivets, no filigree, no fine detail."""


# The APPROVED hand set: bronze `hand-D-pixel`, chosen out of the A/B/C/D prompt comparison on
# 2026-07-28. Four hands, one shape, consistent angles, with a cuff:
#   h1 back of hand (knuckles)  h2 palm  h3 profile  h4 GRIP — closed round a pole, hole through it
# The walk/run use h1+h2 (side) and h3 (front); the tool swing uses the knuckles at rot 225, +16% down
# the handle ("225 works ... +16% so the last one").
#
# Every other outfit's gauntlet was generated INDEPENDENTLY from a material description, so the model
# invented a different hand shape each time — five outfits, five different objects, visibly different
# widths and angles in the same reel. This mode fixes that the way tool tiers are done: generate against
# the approved hand as a REFERENCE so the silhouette and the four angles are preserved and only the
# material changes.
# The four APPROVED bronze hands, as a sheet — the shape every other outfit's gauntlet must copy.
# ⚠ This used to point at outfits/bronze/hand-D-pixel/result.png, which no longer exists (bronze was
# reorganised), and the only surviving copy was inside the GITIGNORED archive. A reference that every
# future gauntlet depends on cannot live somewhere untracked, so it now sits in APPROVED/ with the
# hands it produced.
OFFICIAL_HAND = os.path.join(PLAYER, "APPROVED", "hands", "SOURCE_SHEET_hand-D-pixel.png")

OFFICIAL_GAUNTLET = """The FIRST attached image is the reference: {n} small pixel-art gauntlet hands in a row on a black background. The SECOND attached image is a sprite sheet of a character wearing {what}.

Redraw those SAME {n} HANDS in the SAME {n} poses, in the SAME row, at the SAME size and spacing, on a black background - but made of {glove} instead, matching the material, colours, shadows and highlights of the armour in the second image.

Copy the reference EXACTLY in shape. Same silhouette, same outline, same proportions, same wrist cuff at the bottom of each hand, same angle for each of the {n}. Left to right they are: {roles}. Do not redesign them, do not restyle them, do not change how any hand is posed or turned - the ONLY thing that changes is the material they are made of.

Big simple shapes, chunky pixels, a dark outline, no fine detail. Nothing else in the image - no character, no body, no arms, just the {n} hands."""


def reference_strip():
    """Build the reference image FROM bronze's official gauntlet, at call time.

    The reference used to be a committed 4-hand sheet (`SOURCE_SHEET_hand-D-pixel.png`). That is one more
    thing that can silently disagree with HAND_ROLES — and it did: the sheet had four hands while the
    renderer wanted five, so `grip_palm` never existed for any outfit but bronze. Compositing it from
    `outfits/bronze/gauntlet/` means the reference IS the official set, always, and a new role appears in
    the prompt the moment it appears in official.py.
    """
    from PIL import Image
    g = os.path.join(PLAYER, O.path(O.REFERENCE_OUTFIT, O.HANDS_DIR))
    imgs = []
    for role in O.HAND_ROLES:
        p = os.path.join(g, f"{role}.png")
        if not os.path.exists(p):
            raise SystemExit(f"reference outfit '{O.REFERENCE_OUTFIT}' has no '{role}.png'\n"
                             f"  expected: {p}\n"
                             f"  Every hand in official.HAND_ROLES must exist on the reference outfit.")
        imgs.append(Image.open(p).convert("RGBA"))

    # NORMALISE HEIGHT FIRST. Bronze's five hands are not stored at one scale — the walk trio are cut
    # sprites (16x20, 18x22, 12x21) while the two grips are full-resolution art (213x237, 176x240), a
    # ~11x difference. Pasting them as-is gives a reference showing three tiny hands beside two huge
    # ones, and the model would faithfully copy that. Everything goes to TARGET_HAND_H first, which is
    # the height cut_gauntlet gives every hand anyway.
    # …and DEFRINGE. The two grip hands still carry magenta key-bleed at the silhouette edge (they were
    # cut before defringe existed). A handful of bright pink pixels in a reference is a handful of bright
    # pink pixels the model copies into all 30 outfits. The approved source files are left untouched;
    # this cleans the derived strip only.
    import numpy as np
    from cut_outfit import TARGET_HAND_H, defringe
    norm = []
    for i in imgs:
        a = defringe(np.asarray(i, np.uint8))
        i = Image.fromarray(a, "RGBA")
        s = TARGET_HAND_H / i.height
        norm.append(i.resize((max(1, round(i.width * s)), TARGET_HAND_H), Image.NEAREST))

    SCALE, GAP, PAD = 8, 24, 24            # big enough that the model reads the shapes, not the pixels
    h = max(i.height for i in norm) * SCALE
    w = sum(i.width for i in norm) * SCALE + GAP * (len(norm) - 1)
    strip = Image.new("RGBA", (w + PAD * 2, h + PAD * 2), (0, 0, 0, 255))
    x = PAD
    for i in norm:
        big = i.resize((i.width * SCALE, i.height * SCALE), Image.NEAREST)
        strip.alpha_composite(big, (x, PAD + h - big.height))
        x += big.width + GAP
    out = os.path.join(PLAYER, "APPROVED", "hands", "REFERENCE_STRIP_generated.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    strip.convert("RGB").save(out)
    return out


def gen(dest, prompt, refs, size=None):
    cmd = [sys.executable, os.path.join(HERE, "gen.py"), "--dest", dest, "--prompt", prompt]
    if size:
        cmd += ["--size", size]
    for r in refs:
        cmd += ["--ref", r]
    p = subprocess.run(cmd, capture_output=True, text=True)
    ok = "RESULT" in p.stdout
    print(f"  {'ok  ' if ok else 'FAIL'} {dest}")
    if not ok:
        print((p.stdout + p.stderr)[-400:])
    return ok


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    mode, names = sys.argv[1], sys.argv[2:]
    if mode == "list":
        for k, v in OUTFITS.items():
            print(f"  {k:16s} {v[0]}")
        return
    if mode == "official":
        # Writes into tries/<date>-official-gauntlet/, NEVER over an existing gauntlet/. Bulk overwriting
        # generated art destroyed a day's work on 2026-08-01, so new output always lands somewhere new.
        # (It used to go to `gauntlet2/` for the same good reason — but nothing ever read that name, so
        # every official-mode result was invisible to the renderer. tries/ is the place that already
        # exists for this, and choosing = copying one out of it into gauntlet/.)
        ref = reference_strip()
        stamp = datetime.date.today().isoformat()
        roles = ", ".join(f"({i + 1}) {O.HAND_ROLE_MEANING[r]}" for i, r in enumerate(O.HAND_ROLES))
        for n in names:
            what, _, _, glove = OUTFITS[n]
            # The colour reference is the outfit's CHOSEN sheet, named in official.py — not a hunt for a
            # file called result.png, which broke as soon as those were tidied into tries/.
            colour = os.path.join(PLAYER, O.sheet(n))
            if not os.path.exists(colour):
                raise SystemExit(f"{n}: official.py names a sheet that is not there\n    {colour}")
            gen(f"{O.path(n, O.TRIES_DIR)}/{stamp}-official-gauntlet",
                OFFICIAL_GAUNTLET.format(what=what, glove=glove, n=len(O.HAND_ROLES), roles=roles),
                [ref, colour])
        return
    if mode == "explore":
        for n in names or EXPLORATIONS:
            what, opts = EXPLORATIONS[n]
            # If a CHOSEN_*.png sits in the explore folder, pass it as a second reference so variants
            # stay on that design rather than drifting into three unrelated ideas.
            refs = [os.path.join(BASES, "armless_front.png")]
            chosen = sorted(glob.glob(os.path.join(PLAYER, "explore", n.split("-soldier")[0],
                                                   "CHOSEN_*.png")))
            refs += chosen[:1]
            gen(f"explore/{n}",
                EXPLORE.format(what=what, a=opts[0], b=opts[1], c=opts[2],
                               head=HEAD_FACE if n in FACE_SETS else HEAD_COVERED),
                refs,
                size="1536x1024")          # landscape: three figures in a row, each as large as possible
        return
    for n in names or OUTFITS:
        what, material, headgear, glove = OUTFITS[n]
        if mode == "sheet":
            refs = [os.path.join(BASES, "armless_front.png"), os.path.join(BASES, "armless_side.png")]
            # A CHOSEN_*.png from any explore folder locks the sheet to the design that was picked.
            chosen = sorted(glob.glob(os.path.join(PLAYER, "explore", "*", f"CHOSEN_{n}.png")))
            refs += chosen[:1]
            gen(f"outfits/{n}",
                SHEET.format(what=what, material=material, headgear=headgear),
                refs)
        else:
            gen(f"outfits/{n}/gauntlet",
                GAUNTLET.format(what=what, glove=glove),
                [os.path.join(PLAYER, "outfits", n, "result.png")])


if __name__ == "__main__":
    main()
