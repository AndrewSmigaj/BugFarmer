"""make_mannequins — hand-authored (Pipeline B) display mannequins for the Weaver.

A featureless white "blob-man" (the player base body, face hidden) + clothed
variants. Static 16x32 occupant sprites -> Resources/Objects/{id}.png. These are
NOT gpt-image-1 art; like the player sprites they're explicit pixel grids, so a
bare pixelclean must NOT touch them (run this AFTER any pixelclean pass).

Run from repo root:  python3 -m tools.player_sprites.make_mannequins
"""
import os

from . import pixkit, body_frames

HERE = os.path.dirname(os.path.abspath(__file__))
OBJ_DIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "BugFarmerClient", "Assets", "Resources", "Objects"))

# 3-shade ramps (light, base, dark)
WHITE = ((248, 248, 250), (228, 228, 234), (198, 198, 208))
CREAM = ((238, 230, 214), (214, 204, 184), (180, 168, 146))
RED   = ((196, 72, 64), (164, 52, 48), (120, 36, 34))
NAVY  = ((78, 92, 140), (54, 66, 110), (36, 46, 82))
TEAL  = ((78, 160, 152), (54, 126, 120), (36, 94, 90))
TAN   = ((198, 170, 122), (170, 142, 98), (132, 108, 72))


def _face_hidden(pal):
    """Blank the eyes/mouth/gleam so the figure reads as a smooth mannequin head."""
    pal = dict(pal)
    pal["e"] = pal["s"]
    pal["m"] = pal["s"]
    pal["w"] = pal["s"]
    return pal


def _mannequin(skin, hair, shirt, pants):
    rows = body_frames.direction_frames()["down"][1]   # front-facing idle
    pal = _face_hidden(pixkit.make_palette(
        skin=skin, hair=hair, shirt=shirt, pants=pants,
        boots=(skin[1], skin[2])))                     # feet = body tone (no boots)
    return pixkit.render(rows, pal, mode="baked")


MANNEQUINS = {
    # featureless base forms (uniform tone head-to-toe)
    "mannequin_white": dict(skin=WHITE, hair=WHITE, shirt=WHITE, pants=WHITE),
    "mannequin_cream": dict(skin=CREAM, hair=CREAM, shirt=CREAM, pants=CREAM),
    # white form wearing display garments
    "mannequin_dress_red":  dict(skin=WHITE, hair=WHITE, shirt=RED,  pants=NAVY),
    "mannequin_dress_teal": dict(skin=WHITE, hair=WHITE, shirt=TEAL, pants=TAN),
}


def main():
    for name, kw in MANNEQUINS.items():
        pixkit.save(_mannequin(**kw), os.path.join(OBJ_DIR, f"{name}.png"))
        print("mannequin ->", os.path.join("Objects", f"{name}.png"))


if __name__ == "__main__":
    main()
