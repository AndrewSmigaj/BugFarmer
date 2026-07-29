"""demo_swings.py — the character swinging each tool, in a scene. PREVIEW ONLY, nothing ships.

The point is to judge the motion in context: cropped to the character the sword leaves frame entirely, and a
swing you can't see the end of tells you nothing.

Every motion curve here is COPIED FROM THE GAME (`PlayerToolAnimator.cs`), not approximated, so what you watch
is what the game does. They are genuinely different from each other and that difference is the whole point:

  sword  Swing  wind back, accelerate to contact, overshoot past and settle   (:275)
  axe    Chop   big overhead raise, strike down, HOLD at impact, recoil       (:414)
  net    Sweep  one even symmetric pass, no overshoot — the trail IS the      (:323)
                catch area, so it must cover the sector evenly
  hoe    Till   raise high, chop into the soil, then DRAG BACK toward the     (:447)
                player while the head dips past level

The hand rides the handle. Its position is MEASURED off each tool sprite (they differ a lot: a sword is
gripped high on a short hilt, a hoe low on a long shaft) rather than shared, and it rotates with the tool so
the knuckles stay outward.

  python3 tools/player_sprites/demo_swings.py
"""
import math
import os

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFIT = os.path.join(PLAYER, "outfits", "bronze")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
OUT = os.path.join(OUTFIT, "DEMO_swings.gif")

# --- the game's easing (PlayerToolAnimator.cs:253-260) ---
ease_out = lambda t: 1 - (1 - t) ** 2
ease_in = lambda t: t ** 3


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    u = t - 1
    return 1 + c3 * u ** 3 + c1 * u ** 2


# --- the profiles (PlayerToolAnimator.cs:33-46) ---
TOOLS = {
    "sword": dict(icon="sword_bronze_icon.png", kind="swing", arc=100.0, dur=0.20, off=0.60),
    "axe":   dict(icon="axe_copper_icon.png",   kind="chop",  arc=110.0, dur=0.34, off=0.55),
    "net":   dict(icon="small_net_icon.png",    kind="sweep", arc=90.0,  dur=0.25, off=0.60),
    "hoe":   dict(icon="hoe_copper_icon.png",   kind="till",  arc=90.0,  dur=0.24, off=0.55),
}
ART_ANGLE = 45.0            # grip bottom-left, head top-right (:50)
DIAG = np.array([-1, 1]) / math.sqrt(2)      # down the shaft toward the butt
GRIP_EXTRA = 0.16           # owner-chosen: how far past the measured grip the hand sits
HAND_FRAC = 0.17            # hand height as a fraction of BODY height — the ONE place this is set.
                            # Never size the hand off the tool sprite: that was a 1.5x bug (25% vs 17%),
                            # because it made the same hand grow the moment he drew a weapon.
HAND_ROT = 225              # owner-chosen: knuckles across the handle, not along it


def angle_and_offset(kind, t, aim, arc, off):
    """Returns (pivot angle, tool distance). One branch per AnimKind, matching the game."""
    half = arc / 2
    if kind == "swing":
        top, end, cur = aim + half + half * 0.30, aim - half, aim + half
        ant, strf = 0.15, 0.50
        if t < ant:
            a = cur + (top - cur) * ease_out(t / ant)
        elif t < ant + strf:
            a = top + (aim - top) * ease_in((t - ant) / strf)
        else:
            a = aim + (end - aim) * ease_out_back((t - ant - strf) / (1 - ant - strf))
        o = off
        if ant <= t < ant + strf:                                  # the sword's forward lunge
            o = off + 0.2 * ease_in((t - ant) / strf)
        elif t >= ant + strf:
            o = off + 0.2 - 0.2 * ease_out((t - ant - strf) / (1 - ant - strf))
        return a, o
    if kind == "chop":
        top, end, cur = aim + half + half * 0.35, aim - half, aim + half
        ant, strf, hold = 0.22, 0.33, 0.28
        if t < ant:
            a = cur + (top - cur) * ease_out(t / ant)
        elif t < ant + strf:
            a = top + (aim - top) * ease_in((t - ant) / strf)
        elif t < ant + strf + hold:
            a = aim                                                # impact HOLD — the chop sticks
        else:
            u = (t - ant - strf - hold) / (1 - ant - strf - hold)
            a = aim + (end - aim) * ease_out(u)
        return a, off
    if kind == "sweep":
        return aim + half + (aim - half - (aim + half)) * ease_out(t), off      # symmetric, no overshoot
    if kind == "till":
        top, cur = aim + half + half * 0.35, aim + half
        ant, strf = 0.20, 0.30
        drag_to, bite = off - 0.55, aim - 12.0
        if t < ant:
            return cur + (top - cur) * ease_out(t / ant), off
        if t < ant + strf:
            return top + (aim - top) * ease_in((t - ant) / strf), off
        u = (t - ant - strf) / (1 - ant - strf)
        return aim + (bite - aim) * ease_out(u), off + (drag_to - off) * ease_in(u)
    return aim, off


def rgba(p):
    return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def scale_h(a, h):
    s = h / a.shape[0]
    return np.asarray(Image.fromarray(a, "RGBA").resize(
        (max(2, round(a.shape[1] * s)), max(2, round(h))), Image.NEAREST), np.uint8)


def rot(a, deg):
    return np.asarray(Image.fromarray(a, "RGBA").rotate(deg, resample=Image.NEAREST, expand=True), np.uint8)


def paste(dst, src, cx, cy):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0 = max(0, x0), max(0, y0)
    a1, b1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if a1 <= a0 or b1 <= b0:
        return
    s = src[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    m = s[..., 3] > 0
    dst[b0:b1, a0:a1][m] = s[m]


def measured_grip(art):
    """Where the hand goes on THIS tool — a fixed way up the shaft from its butt end."""
    o = art[..., 3] > 0
    ys, xs = np.where(o)
    c = np.array([art.shape[1] / 2, art.shape[0] / 2])
    proj = (np.stack([xs, ys], 1) - c) @ DIAG
    return DIAG * (proj.max() - 0.22 * art.shape[0]) / art.shape[0]


def cut_dummy():
    """The dummy sheet holds a front and a side figure; take the side one."""
    from scipy.ndimage import label, binary_dilation
    a = rgba(os.path.join(PLAYER, "props", "practice-dummy", "result.png"))
    solid = binary_dilation(a[..., :3].astype(int).sum(2) > 70, np.ones((7, 7), bool))
    lbl, n = label(solid, structure=np.ones((3, 3), int))
    blobs = []
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() < 4000:
            continue
        ys, xs = np.where(m)
        blobs.append((xs.mean(), ys.min(), ys.max(), xs.min(), xs.max(), m))
    blobs.sort()
    _, y0, y1, x0, x1, m = blobs[-1]
    f = np.zeros_like(a)
    f[m] = a[m]
    f[..., 3] = np.where(m, 255, 0)
    return f[y0:y1 + 1, x0:x1 + 1]


def build():
    body = rgba(os.path.join(OUTFIT, "side_2.png"))
    by0, by1, _, _ = bbox(body)
    BH = by1 - by0 + 1
    CELL = BH / 2.0                                   # the character is two world cells tall

    hand = rgba(os.path.join(OUTFIT, "gauntlet", "front.png"))
    dummy = scale_h(cut_dummy(), BH * 0.92)
    tree = scale_h(rgba(os.path.join(RES, "Objects", "tree_apple.png")), CELL * 3)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]

    W, H = int(CELL * 11), int(CELL * 7)
    TS = int(CELL)
    rng = np.random.RandomState(7)
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H, TS):
        for gx in range(0, W, TS):
            t = scale_h(tiles[rng.randint(len(tiles))], TS)
            paste(ground, t, gx + TS / 2, gy + TS / 2)

    BASE_Y = int(H * 0.80)                            # the ground line everything stands on
    PX = int(W * 0.34)                                # where the character stands
    DX = int(W * 0.63)                                # the dummy

    frames, ms = [], []
    PAUSE, FPS = 10, 22

    def compose(tool=None, t=None):
        sc = ground.copy()
        paste(sc, tree, int(W * 0.10), BASE_Y - tree.shape[0] // 2 + int(CELL * 0.3))
        paste(sc, dummy, DX, BASE_Y - dummy.shape[0] // 2)
        cy = BASE_Y - BH // 2
        paste(sc, body, PX, cy)
        if tool:
            p = TOOLS[tool]
            art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL)
            ang, off = angle_and_offset(p["kind"], t, 0.0, p["arc"], p["off"])
            r = math.radians(ang)
            tx, ty = PX + math.cos(r) * off * CELL, cy - math.sin(r) * off * CELL
            paste(sc, rot(art, ang - ART_ANGLE), tx, ty)
            g = (measured_grip(art) + DIAG * GRIP_EXTRA) * art.shape[0]
            rr = math.radians(-(ang - ART_ANGLE))
            paste(sc, rot(scale_h(hand, BH * HAND_FRAC), ang - ART_ANGLE + HAND_ROT),
                  tx + g[0] * math.cos(rr) - g[1] * math.sin(rr),
                  ty + g[0] * math.sin(rr) + g[1] * math.cos(rr))
        im = Image.new("RGBA", (W, H), (34, 40, 34, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        return im.convert("RGB")

    for tool in ("sword", "axe", "net", "hoe"):
        n = max(6, int(TOOLS[tool]["dur"] * FPS * 4))
        for reps in (1, 2):                            # swing, pause, swing twice, pause
            for _ in range(reps):
                for i in range(n):
                    frames.append(compose(tool, i / (n - 1)))
                    ms.append(int(TOOLS[tool]["dur"] * 1000 / n))
            frames.append(compose(tool, 0.0)); ms.append(PAUSE * 60)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(f"  {len(frames)} frames -> {OUT.replace('/mnt/c/', 'C:/')}")


if __name__ == "__main__":
    build()
