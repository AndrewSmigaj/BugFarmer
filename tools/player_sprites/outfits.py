"""outfits.py — WHICH outfits exist, and the one prompt that makes any of them.

The sheet prompt is identical for every outfit except three slots: the set's name, its material and
colours, and its headgear. Keeping the shared 90% in one string is the point — when a sheet comes
back wrong the fix belongs in the template, once, not copied into ten places by hand.

Every set gets headgear. A set without one doesn't match the rest and has to be redone.

  python3 tools/player_sprites/outfits.py list
  python3 tools/player_sprites/outfits.py sheet   platinum swamp-gear      # one API call each
  python3 tools/player_sprites/outfits.py gauntlet platinum swamp-gear     # one API call each
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
BASES = os.path.join(PLAYER, "bases")

# name -> (what the set IS, its material + colours, its headgear, the gauntlet material)
OUTFITS = {
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

Outfit: {material}. Include a {headgear} covering the whole head, a breastplate, rounded shoulder caps, a waist and hip piece covering the crotch, thigh plates on both legs, greaves, and boots. No bare skin between the waist and the boots. The headgear is on the character in all 12 frames.

Keep the front row front-facing, the back row back-facing, and the bottom row a strict right-facing side profile. Do not drift into a three-quarter view.

Big simple shapes, not fine detail. This is a small pixel art sprite sheet. All 12 sprites must clearly be the same character, but each frame in a row must be a distinct walking frame. If two adjacent frames in a row are identical, the sheet is wrong."""

GAUNTLET = """The attached image is a sprite sheet of a character wearing {what}.

Draw FOUR small HANDS in a row on a black background, evenly spaced, large and centred. Nothing else in the image - no character, no body, no arms, just the four hands.

Each hand is made of {glove}, the SAME material as the armour in the attached image, with the same darker shadows and the same bright highlights.

Left to right, the same hand from four angles: (1) back of the hand facing the viewer, (2) palm side, (3) in profile facing right, (4) three-quarter view.

Care about the SILHOUETTE above all. The outline is a soft rounded shape, slightly taller than wide, narrowing a little at the wrist. No separate fingers are drawn - at this size the hand reads entirely by its outline and two or three shading bands inside it.

Big simple shapes, chunky pixels. This is a small pixel art sprite - each hand is about ten pixels across in the game, so use a handful of large blocks, no rivets, no filigree, no fine detail."""


def gen(dest, prompt, refs):
    cmd = [sys.executable, os.path.join(HERE, "gen.py"), "--dest", dest, "--prompt", prompt]
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
    for n in names or OUTFITS:
        what, material, headgear, glove = OUTFITS[n]
        if mode == "sheet":
            gen(f"outfits/{n}",
                SHEET.format(what=what, material=material, headgear=headgear),
                [os.path.join(BASES, "armless_front.png"), os.path.join(BASES, "armless_side.png")])
        else:
            gen(f"outfits/{n}/gauntlet",
                GAUNTLET.format(what=what, glove=glove),
                [os.path.join(PLAYER, "outfits", n, "result.png")])


if __name__ == "__main__":
    main()
