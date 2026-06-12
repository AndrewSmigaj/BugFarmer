"""vector_player — VECTOR-drawn character, pixelized (Andrew's idea).

The workflow the world art already proves (1024px gpt -> pixelclean): draw
BIG, downscale + quantize to crisp pixel art. Characters couldn't use gpt
because frames drift — but VECTORS are parametric: a walk frame is "move the
leg group", re-render — perfectly consistent. Regions are shape GROUPS, so
paper-doll layers fall out with guaranteed registration.

Pipeline per frame: PIL ImageDraw at 20x (18x22 -> 360x440) -> BOX downscale
-> snap to the character's fixed palette -> exterior outline pass (the
reference zelda.png uses near-black (39,39,39) exterior outlines; interior
edges come from SHADING boundaries, not lines).

Proportions measured from zelda.png: head ~60%% of height including the
crown-seen-from-above; tufts wider than the body; eyes small + LOW; body a
short trapezoid; feet = nubs. Ramps hue-shift (shadows go warm/orange on
skin, deep teal on greens) — not just darker.

Run: python3 tools/player_sprites/vector_player.py
-> previews/player/vector/{card.png, scout_walk.gif}
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

OUT = os.path.normpath(os.path.join(HERE, "..", "_generated", "previews",
                                    "player", "vector"))

S = 14                      # hi-res scale
W, H = 36, 44               # sprite canvas (game-density: world art is 32-64px)
HW, HH = W * S, H * S

OUTLINE = (39, 39, 39, 255)  # the reference's exterior outline

# Scout palette — hue-shifted ramps (learned from the reference, not copied)
P = {
    "skin":   ((246, 198, 142), (228, 158, 100), (196, 116, 56)),
    "hair":   ((224, 134, 58), (188, 96, 36), (140, 62, 22)),
    "straw":  ((242, 214, 128), (212, 176, 88), (170, 134, 56)),
    "tunic":  ((110, 186, 92), (74, 148, 86), (48, 110, 84)),   # green w/ teal shadow
    "pants":  ((150, 112, 70), (118, 84, 52), (88, 60, 38)),
    "boots":  ((186, 84, 52), (146, 58, 38), (104, 38, 28)),
    "strap":  ((104, 76, 50), (80, 56, 38), (60, 42, 28)),
    "eye":    ((36, 32, 40), (36, 32, 40), (36, 32, 40)),
    "mouth":  ((188, 110, 80), (188, 110, 80), (188, 110, 80)),
}


def _flat_palette():
    cols = [OUTLINE[:3]]
    for ramp in P.values():
        cols.extend(ramp)
    return np.array(sorted(set(cols)), dtype=np.float64)


def E(d, cx, cy, rx, ry, col):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)


def RR(d, x0, y0, x1, y1, r, col):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=col)


def draw_scout(face_dx=0.0, step=0.0, side=False, back=False):
    """One frame at hi-res as PER-REGION layers. 36x44 game-density target.
    v2 anatomy pass: neck, ears, brim shadow, eye whites+brows, shaped hair
    locks, collar, belt+buckle, cuffs, hands, boot soles."""
    layers = {}

    def L(name):
        if name not in layers:
            layers[name] = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
        return ImageDraw.Draw(layers[name])

    u = S * 2.0               # ONE 18x22-era unit = 2 px now (same proportions)
    cx = HW / 2 + (-0.6 * u if side else 0)
    headc = (cx, 7.4 * u)
    bodyt, bodyb = 13.4 * u, 18.6 * u
    light, base, dark = range(3)

    def ramp(name, i):
        return P[name][i] + (255,)

    # ---- legs + boots
    d = L("pants"); db = L("boots")
    lx, rx_ = cx - 2.4 * u, cx + 2.4 * u
    if side:
        lx, rx_ = cx - 1.5 * u + step * 1.6 * u, cx + 1.5 * u - step * 1.6 * u
    fwd, back = step * 1.3 * u, -step * 1.3 * u
    if side:
        fwd = back = 0
    for x, dy in ((lx, fwd), (rx_, back)):
        RR(d, x - 1.3 * u, 17.5 * u + dy * 0.2, x + 1.3 * u, 19.5 * u + dy,
           0.8 * u, ramp("pants", base if x < cx else dark))
        RR(d, x - 1.3 * u, 17.5 * u + dy * 0.2, x - 0.2 * u, 18.6 * u + dy * 0.6,
           0.5 * u, ramp("pants", light))
        RR(db, x - 1.45 * u, 19.1 * u + dy, x + 1.45 * u, 20.9 * u + dy,
           0.7 * u, ramp("boots", base if x < cx else dark))
        RR(db, x - 1.45 * u, 20.4 * u + dy, x + 1.45 * u, 20.9 * u + dy,
           0.3 * u, ramp("boots", dark))                      # sole line
        RR(db, x - 1.45 * u, 19.1 * u + dy, x + 0.3 * u, 19.9 * u + dy,
           0.5 * u, ramp("boots", light))

    # ---- tunic: trapezoid + collar + belt + hem
    d = L("tunic")
    d.polygon([(cx - 4.4 * u, bodyt), (cx + 4.4 * u, bodyt),
               (cx + 5.2 * u, bodyb), (cx - 5.2 * u, bodyb)], fill=ramp("tunic", base))
    d.polygon([(cx + 1.4 * u, bodyt), (cx + 4.4 * u, bodyt),
               (cx + 5.2 * u, bodyb), (cx + 2.2 * u, bodyb)], fill=ramp("tunic", dark))
    d.polygon([(cx - 4.4 * u, bodyt), (cx - 1.4 * u, bodyt),
               (cx - 2.2 * u, bodyb - 0.3 * u), (cx - 5.0 * u, bodyb - 0.3 * u)],
              fill=ramp("tunic", light))
    # collar: a V notch under the neck
    d.polygon([(cx - 1.6 * u, bodyt), (cx + 1.6 * u, bodyt),
               (cx, bodyt + 1.3 * u)], fill=ramp("tunic", dark))
    # satchel strap + buckle
    sx0, sx1 = (cx + 3.9 * u, cx - 3.1 * u) if back else (cx - 3.9 * u, cx + 3.1 * u)
    d.line([(sx0, bodyt + 0.3 * u), (sx1, bodyb - 0.7 * u)],
           fill=ramp("strap", base), width=int(0.9 * u))
    RR(d, cx + 0.3 * u, bodyt + 2.2 * u, cx + 1.3 * u, bodyt + 3.0 * u,
       0.2 * u, ramp("straw", dark))                          # brass-ish buckle
    # belt + hem shadow
    RR(d, cx - 5.0 * u, 17.0 * u, cx + 5.0 * u, 17.8 * u, 0.3 * u, ramp("strap", dark))
    RR(d, cx - 0.7 * u, 17.0 * u, cx + 0.7 * u, 17.8 * u, 0.2 * u, ramp("straw", base))

    # ---- arms with sleeve cuffs + hands
    asw = step * 1.0 * u
    ds = L("skin")
    arm_y = 14.9 * u
    if not side:
        for sgn, sw in ((-1, asw), (1, -asw)):
            ax = cx + sgn * 4.9 * u
            E(d, ax, arm_y + sw, 1.1 * u, 1.8 * u, ramp("tunic", dark if sgn > 0 else base))
            RR(d, ax - 0.9 * u, arm_y + 0.6 * u + sw, ax + 0.9 * u, arm_y + 1.2 * u + sw,
               0.2 * u, ramp("tunic", dark))                  # cuff
            E(ds, ax, arm_y + 1.8 * u + sw, 0.85 * u, 0.85 * u, ramp("skin", base))
            E(ds, ax - 0.25 * u, arm_y + 1.6 * u + sw, 0.4 * u, 0.4 * u, ramp("skin", light))
    else:
        ax = cx - 4.2 * u
        E(d, ax, arm_y, 1.1 * u, 1.8 * u, ramp("tunic", dark))
        RR(d, ax - 0.9 * u, arm_y + 0.6 * u, ax + 0.9 * u, arm_y + 1.2 * u,
           0.2 * u, ramp("tunic", dark))
        E(ds, ax, arm_y + 1.8 * u, 0.85 * u, 0.85 * u, ramp("skin", base))

    # ---- NECK (new): a short cylinder between chin and collar
    RR(ds, cx - 1.1 * u, 11.6 * u, cx + 1.1 * u, bodyt + 0.2 * u, 0.4 * u,
       ramp("skin", dark))

    # ---- HEAD ball + ears
    hr = 4.9 * u
    E(ds, headc[0], headc[1] + 0.6 * u, hr, hr * 0.95, ramp("skin", base))
    E(ds, headc[0] - 1.7 * u, headc[1] + 0.7 * u, 2.0 * u, 2.0 * u, ramp("skin", light))
    if not side:
        for sgn in (-1, 1):
            E(ds, headc[0] + sgn * (hr - 0.1 * u), headc[1] + 1.6 * u,
              0.6 * u, 0.9 * u, ramp("skin", base if sgn < 0 else dark))
    else:
        E(ds, headc[0] + 0.6 * u, headc[1] + 1.9 * u, 0.55 * u, 0.85 * u, ramp("skin", dark))

    # ---- hair: SHAPED LOCKS — overlapping tapered clumps under the brim
    dh = L("hair")
    if not side:
        for i, (lx_, ly, rx2, ry2, shade) in enumerate((
                (-3.4, -1.6, 1.5, 2.4, base), (-1.4, -2.2, 1.6, 2.2, light),
                (0.8, -2.0, 1.5, 2.3, base), (2.9, -1.5, 1.4, 2.4, dark))):
            E(dh, headc[0] + lx_ * u, headc[1] + ly * u, rx2 * u, ry2 * u,
              ramp("hair", shade))
        # sideburn locks
        for sgn, shade in ((-1, base), (1, dark)):
            E(dh, headc[0] + sgn * (hr - 0.5 * u), headc[1] + 0.6 * u,
              0.8 * u, 1.7 * u, ramp("hair", shade))
    else:
        E(dh, headc[0] - 1.6 * u, headc[1] - 1.8 * u, 2.2 * u, 2.0 * u, ramp("hair", light))
        E(dh, headc[0] + 0.8 * u, headc[1] - 1.6 * u, 2.6 * u, 2.4 * u, ramp("hair", base))
        E(dh, headc[0] + 3.2 * u, headc[1] + 0.6 * u, 2.0 * u, 3.6 * u, ramp("hair", base))
        E(dh, headc[0] + 3.9 * u, headc[1] + 1.2 * u, 1.3 * u, 2.9 * u, ramp("hair", dark))

    # ---- straw hat + BRIM SHADOW cast on the face (classic AO)
    dy_ = L("straw")
    hat_y = headc[1] - 2.2 * u            # seated ON the crown, not floating
    E(dy_, headc[0], hat_y, 5.8 * u, 2.0 * u, ramp("straw", dark))
    E(dy_, headc[0] - 0.3 * u, hat_y - 0.4 * u, 5.4 * u, 1.7 * u, ramp("straw", base))
    E(dy_, headc[0] - 0.6 * u, hat_y - 1.0 * u, 3.4 * u, 1.4 * u, ramp("straw", light))
    E(dy_, headc[0], hat_y + 0.5 * u, 3.6 * u, 0.7 * u, ramp("straw", dark))
    # cast shadow lands on the BANGS (hair), a hint on the forehead
    E(dh, headc[0] + (0 if not side else -0.4 * u), headc[1] - 1.5 * u,
      4.0 * u, 0.6 * u, ramp("hair", dark))

    if back:
        # back of the head: hair fills the whole skull under the hat; no face
        E(dh, headc[0], headc[1] + 0.7 * u, hr * 0.98, hr * 0.92, ramp("hair", base))
        E(dh, headc[0] + 1.2 * u, headc[1] + 1.4 * u, hr * 0.7, hr * 0.7, ramp("hair", dark))
        E(dh, headc[0] - 1.8 * u, headc[1] - 0.6 * u, 2.2 * u, 2.4 * u, ramp("hair", light))
        return layers

    # ---- face: eye WHITES + pupils + brows; small nose-mouth
    fx = headc[0] + face_dx
    eye_y = headc[1] + 1.9 * u
    if side:
        E(ds, headc[0] - 2.4 * u, eye_y - 0.3 * u, 0.75 * u, 1.0 * u, (252, 250, 244, 255))
        E(ds, headc[0] - 2.6 * u, eye_y - 0.25 * u, 0.45 * u, 0.8 * u, ramp("eye", base))
        RR(ds, headc[0] - 3.3 * u, eye_y - 1.6 * u, headc[0] - 1.6 * u, eye_y - 1.32 * u,
           0.15 * u, ramp("hair", dark))                      # brow
        E(ds, headc[0] - 3.7 * u, eye_y + 1.3 * u, 0.55 * u, 0.35 * u, ramp("mouth", base))
    else:
        for ex in (-2.1 * u, 2.1 * u):
            E(ds, fx + ex, eye_y, 0.8 * u, 1.05 * u, (252, 250, 244, 255))
            E(ds, fx + ex + 0.15 * u, eye_y + 0.05 * u, 0.45 * u, 0.8 * u, ramp("eye", base))
            RR(ds, fx + ex - 0.9 * u, eye_y - 1.7 * u, fx + ex + 0.9 * u, eye_y - 1.42 * u,
               0.15 * u, ramp("hair", dark))                  # brows
        E(ds, fx + 0.1 * u, eye_y + 1.6 * u, 0.5 * u, 0.32 * u, ramp("mouth", base))

    return layers


def _region_palette(name):
    if name == "skin":
        cols = list(P["skin"]) + list(P["eye"]) + list(P["mouth"])
    elif name == "tunic":
        cols = list(P["tunic"]) + list(P["strap"])
    else:
        cols = list(P[name])
    return np.array(cols, dtype=np.float64)


# back-to-front compositing order
ORDER = ["pants", "boots", "tunic", "skin", "hair", "straw"]


def hires_composite(layers):
    im = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
    for name in ORDER:
        if name in layers:
            im = Image.alpha_composite(im, layers[name])
    return im


def pixelize(layers):
    """WHOLE-image pixelization (Andrew: per-region snapping looked monstrous;
    the world art's own pipeline is downscale-the-whole-picture). The outline
    is drawn at HI-RES (a dilated silhouette ring) so it downscales into a
    soft natural edge instead of a chunky post-pass."""
    from PIL import ImageFilter
    comp = hires_composite(layers)
    # hi-res outline: dilate the alpha, fill with the outline color, put under
    a = comp.split()[3]
    ring = a.filter(ImageFilter.MaxFilter(int(S * 0.9) * 2 + 1))
    outline = Image.new("RGBA", comp.size, OUTLINE)
    outline.putalpha(ring)
    full = Image.alpha_composite(outline, comp)
    small = full.resize((W, H), Image.BOX)
    # crisp silhouette: threshold alpha, keep interior blends untouched
    arr = np.asarray(small, dtype=np.uint8).copy()
    arr[..., 3] = np.where(arr[..., 3] > 96, 255, 0)
    return Image.fromarray(arr)


def main():
    from player_sprites import pixkit
    frames = {k: draw_scout(**kw) for k, kw in {
        "idle": {}, "stepA": {"step": 1.0}, "stepB": {"step": -1.0},
        "side": {"side": True}, "side_a": {"side": True, "step": 1.0},
        "side_b": {"side": True, "step": -1.0}}.items()}
    px = {k: pixelize(v) for k, v in frames.items()}
    pixkit.walk_gif([px["stepA"], px["idle"], px["stepB"], px["idle"]],
                    os.path.join(OUT, "scout_walk.gif"), scale=8, ms=130)
    pixkit.walk_gif([px["side_a"], px["side"], px["side_b"], px["side"]],
                    os.path.join(OUT, "scout_side.gif"), scale=8, ms=130)
    pixkit.save(pixkit.contact_sheet([px[k] for k in
                                      ("idle", "stepA", "stepB", "side", "side_a", "side_b")],
                                     cols=6, scale=10),
                os.path.join(OUT, "card.png"))
    # the HI-RES vector look (what the shapes are before pixelization)
    hi = hires_composite(frames["idle"])
    hi_side = hires_composite(frames["side"])
    combo = Image.new("RGBA", (HW * 2 + 40, HH), (58, 58, 64, 255))
    combo.paste(hi, (0, 0), hi)
    combo.paste(hi_side, (HW + 40, 0), hi_side)
    pixkit.save(combo, os.path.join(OUT, "hires.png"))
    print(f"vector scout -> {OUT} (card.png, hires.png, gifs)")


PLAYER_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "BugFarmerClient",
                                           "Assets", "Resources", "Player"))


def emit_game():
    """TRIAL: replace the baked farmer_* sprites with the vector Scout.
    36x44 px; metas are hand-set to PPU 28 (~1.3 x 1.6 cells in world).
    Frame mapping: w1 = stepA, idle = passing, w3 = stepB."""
    from player_sprites import pixkit
    sets = {
        "down": [draw_scout(step=1.0), draw_scout(), draw_scout(step=-1.0)],
        "left": [draw_scout(side=True, step=1.0), draw_scout(side=True),
                 draw_scout(side=True, step=-1.0)],
        "up": [draw_scout(step=1.0, back=True), draw_scout(back=True),
               draw_scout(step=-1.0, back=True)],
    }
    suffix = ["_w1", "", "_w3"]
    for d, frames in sets.items():
        for i, layers in enumerate(frames):
            pixkit.save(pixelize(layers), os.path.join(PLAYER_DIR, f"farmer_{d}{suffix[i]}.png"))
    # right = mirrored left
    for i, layers in enumerate(sets["left"]):
        im = pixelize(layers).transpose(Image.FLIP_LEFT_RIGHT)
        pixkit.save(im, os.path.join(PLAYER_DIR, f"farmer_right{suffix[i]}.png"))
    print(f"TRIAL farmer sprites -> {PLAYER_DIR} (36x44; set metas to PPU 28)")


if __name__ == "__main__":
    main()
    if "--game" in sys.argv:
        emit_game()
