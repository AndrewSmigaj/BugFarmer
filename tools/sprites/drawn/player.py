"""The player, drawn in code on a skeleton — so armour pieces are separate layers that line up by construction.

Proportions follow the approved base (a ~27x68 figure, big head, auburn mop, tank top + shorts, bare feet).
Three facings (front = toward the camera, side = facing right, back), four walk frames each:
1 contact (left foot forward) · 2 passing (body up 1 px) · 3 contact (right) · 4 passing.

Everything reads the POSE: the body, the base clothes and every armour piece use the same joint positions,
so a helmet drawn once per facing sits on the head in every frame and greaves/boots follow the legs. Hands
are either the approved floating fists or real arms (the owner reopened both).
"""
import numpy as np

from . import canvas as K
from . import palette as P

W, H = 32, 72


# ----------------------------------------------------------------------------- poses
def pose(facing, frame, arms=False):
    """Joint positions for one frame. y grows downward; the soles rest on y ~ 69."""
    f = frame % 4
    bob = -1 if f in (1, 3) else 0
    p = {"facing": facing, "bob": bob, "frame": f}
    if facing in ("front", "back"):
        p["head"] = (16.0, 18.0 + bob)
        p["torso"] = (16.0, 37.5 + bob)
        hipy = 51.0 + bob
        # front view: the stepping foot comes toward the camera (lower), the trailing heel lifts (higher)
        down, up = 66.5, 63.0
        if f == 0:
            (lax, lay), (rax, ray) = (12.6, down), (19.2, up)
        elif f == 2:
            (lax, lay), (rax, ray) = (12.8, up), (19.4, down)
        elif f == 1:
            (lax, lay), (rax, ray) = (12.7, 65.5), (19.3, 64.3)
        else:
            (lax, lay), (rax, ray) = (12.7, 64.3), (19.3, 65.5)
        def knee(hx, ax, ay):
            bent = ay < 65.0
            return (hx + (-0.6 if hx < 16 else 0.6) * bent, (hipy + ay) / 2 - (1.0 if bent else 0.0))
        p["legs"] = [((13.0, hipy), knee(13.0, lax, lay), (lax, lay)),
                     ((19.0, hipy), knee(19.0, rax, ray), (rax, ray))]
        swing = {0: 1, 1: 0, 2: -1, 3: 0}[f]
        p["hands"] = [((5.2, 45.0 + bob + 2.5 * swing), 1.0 + 0.08 * swing, False),
                      ((26.8, 45.0 + bob - 2.5 * swing), 1.0 - 0.08 * swing, False)]
        if arms:
            p["arms"] = [((8.8, 30.5 + bob), (6.6, 38.0 + bob + 1.0 * swing), (5.4, 43.5 + bob + 2.5 * swing)),
                         ((23.2, 30.5 + bob), (25.4, 38.0 + bob - 1.0 * swing), (26.6, 43.5 + bob - 2.5 * swing))]
    else:  # side, facing right
        p["head"] = (16.0, 18.0 + bob)
        p["torso"] = (16.5, 37.5 + bob)
        hip = (16.5, 51.0 + bob)
        if f == 0:
            near = (hip, (19.4, 58.2 + bob), (22.0, 65.5))
            far = (hip, (14.2, 58.4 + bob), (11.2, 64.4))
        elif f == 2:
            near = (hip, (14.2, 58.4 + bob), (11.2, 64.4))
            far = (hip, (19.4, 58.2 + bob), (22.0, 65.5))
        elif f == 1:
            near = (hip, (16.9, 58.2 + bob), (16.6, 65.5))
            far = (hip, (19.0, 57.0 + bob), (17.4, 62.5 + bob))
        else:
            near = (hip, (19.0, 57.0 + bob), (17.4, 62.5 + bob))
            far = (hip, (16.9, 58.2 + bob), (16.6, 65.5))
        p["legs"] = [far, near]
        swing = {0: -1, 1: 0, 2: 1, 3: 0}[f]
        p["hands"] = [((16.5 - 7.0 * swing, 44.0 + bob - abs(swing)), 0.9, True),
                      ((16.5 + 7.0 * swing, 44.0 + bob - abs(swing)), 1.0, False)]
        if arms:
            p["arms"] = [((16.0, 30.5 + bob), (16.0 - 3.2 * swing, 37.5 + bob), (16.5 - 7.0 * swing, 43.5 + bob - abs(swing))),
                         ((17.0, 30.5 + bob), (17.0 + 3.2 * swing, 37.5 + bob), (16.5 + 7.0 * swing, 43.5 + bob - abs(swing)))]
    return p


# ----------------------------------------------------------------------------- drawing helpers
CUTS4 = (0.34, 0.52, 0.70, 0.86)


def _limb(c, a, b, r, ramp, cuts=CUTS4, lo=0, hi=None, strength=3.0):
    m = K.capsule(W, H, a[0], a[1], b[0], b[1], r)
    v = K.lambert(K.capsule_height(W, H, a[0], a[1], b[0], b[1], r), strength)
    c.shade(m, v, ramp, cuts=list(cuts), lo=lo, hi=hi)
    return m


def _blob(c, cx, cy, rx, ry, ramp, cuts=CUTS4, strength=3.0, lo=0, hi=None, power=0.8):
    m = K.ellipse(W, H, cx, cy, rx, ry)
    v = K.lambert(K.dome(W, H, cx, cy, rx, ry, power=power), strength)
    c.shade(m, v, ramp, cuts=list(cuts), lo=lo, hi=hi)
    return m


def _foot(c, ankle, facing, ramp="skin", lo=0):
    ax, ay = ankle
    if facing == "side":
        return _blob(c, ax + 1.8, ay + 2.1, 3.8, 2.1, ramp, lo=lo)
    return _blob(c, ax, ay + 2.3, 2.9, 2.2, ramp, lo=lo)


def _spiky(mask, cx, cy, rng, n, reach, angles=(200, 340)):
    """Add messy tufts (small outward triangles) to a hair silhouette."""
    h, w = mask.shape
    xs, ys = K.grid(w, h)
    for a in np.linspace(np.radians(angles[0]), np.radians(angles[1]), n):
        a += rng.uniform(-0.12, 0.12)
        # find the silhouette edge along this ray, then extend a thin wedge beyond it
        r = 1.0
        while r < 20:
            x, y = cx + np.cos(a) * r, cy + np.sin(a) * r
            if not (0 <= int(x) < w and 0 <= int(y) < h) or not mask[int(y), int(x)]:
                break
            r += 0.5
        L = reach * rng.uniform(0.55, 1.0)
        lean = rng.uniform(-0.35, 0.35)
        tip = (cx + np.cos(a + lean) * (r + L), cy + np.sin(a + lean) * (r + L))
        side = np.array([-np.sin(a), np.cos(a)]) * 2.2
        base = np.array([cx + np.cos(a) * (r - 1.5), cy + np.sin(a) * (r - 1.5)])
        tri = K.polygon(w, h, [tuple(base + side), tip, tuple(base - side)])
        mask |= tri
    return mask


# ----------------------------------------------------------------------------- head
def _head(c, p, hair_on=True):
    fac = p["facing"]
    hx, hy = p["head"]
    skin, hair = P.ramp("skin"), P.ramp("hair")
    xs, ys = K.grid(W, H)
    rng = np.random.default_rng(5)
    E, WH, MO, PK = P.EXTRA["eye"], P.EXTRA["white"], P.EXTRA["mouth"], P.ramp("pink")[2]
    if fac == "front":
        face = K.ellipse(W, H, hx, hy + 0.5, 8.4, 8.6) | (K.ellipse(W, H, hx, hy + 5.5, 6.0, 4.2))
        fv = 0.62 + 0.30 * K.lambert(K.dome(W, H, hx - 2, hy - 1, 10, 10, power=0.6), 2.0) - 0.18 * (xs - hx) / 8
        c.shade(face, fv, "skin", cuts=[0.55, 0.72, 0.9], lo=1, hi=4)
        # ears peeking out under the hair
        for ex in (hx - 8.6, hx + 8.6):
            c.fill(K.ellipse(W, H, ex, hy + 2.5, 1.3, 2.0) & ~face, skin[2])
        # hair: a big mop with tufts, side locks to the cheek, a spiky fringe with three points
        mop = K.ellipse(W, H, hx, hy - 5.2, 11.2, 8.4)
        mop = _spiky(mop, hx, hy - 5.2, rng, 7, 2.6, angles=(200, 340))
        locks = K.ellipse(W, H, hx - 8.6, hy - 1.0, 2.8, 6.2) | K.ellipse(W, H, hx + 8.6, hy - 1.0, 2.8, 6.2)
        fringe_y = hy - 2.8 + 2.6 * ((np.abs(xs - (hx - 5.0)) < 1.4) | (np.abs(xs - (hx + 0.2)) < 1.6) |
                                     (np.abs(xs - (hx + 5.0)) < 1.3)) * (1 - np.abs(((xs - hx) % 5) - 2.5) / 2.5)
        hmask = (mop & (ys < fringe_y)) | locks
        if not hair_on:
            hmask &= np.zeros_like(hmask)
        hv = K.lambert(K.dome(W, H, hx - 2, hy - 7, 12, 10, power=0.7), 3.4)
        c.shade(hmask, hv, "hair", cuts=[0.30, 0.50, 0.68, 0.86])
        for (sx, sy, dx) in ((hx - 6, hy - 11, 0.5), (hx - 1, hy - 13, 0.3), (hx + 4, hy - 11, -0.4),
                             (hx + 7, hy - 7, -0.6), (hx - 8, hy - 6, 0.6)):
            for k in range(3):                               # strand lines
                x, y = int(sx + k * dx), int(sy + k)
                if hmask[y, x]:
                    c.put(x, y, hair[1])
        c.fill(face & (ys >= fringe_y) & (ys < fringe_y + 1.0), skin[1])   # the fringe's shadow on the brow
        # eyes: tall, dark, with a white glint top-left (the approved look)
        for ex in (hx - 5.0, hx + 3.0):
            ex = int(ex)
            ey = int(hy + 0.5)
            for dy in range(5):
                c.put(ex, ey + dy, E)
                c.put(ex + 1, ey + dy, E)
            c.put(ex, ey, WH)
            c.put(ex, ey + 1, WH)
            c.put(ex + 1, ey + 5, skin[4])                   # light under the eye
        c.put(int(hx) - 1, int(hy + 5), skin[2])             # nose
        c.put(int(hx) - 1, int(hy + 7), MO); c.put(int(hx), int(hy + 7), MO)
        c.put(int(hx - 6), int(hy + 6), PK); c.put(int(hx + 5), int(hy + 6), PK)
    elif fac == "side":
        face = K.ellipse(W, H, hx + 1.5, hy + 0.5, 7.6, 8.6) | K.ellipse(W, H, hx + 3.5, hy + 5.0, 5.0, 4.0)
        fv = 0.62 + 0.30 * K.lambert(K.dome(W, H, hx, hy - 1, 9, 10, power=0.6), 2.0)
        c.shade(face, fv, "skin", cuts=[0.55, 0.72, 0.9], lo=1, hi=4)
        c.put(int(hx + 9), int(hy + 3), skin[3]); c.put(int(hx + 9), int(hy + 4), skin[2])   # nose tip
        mop = K.ellipse(W, H, hx - 1.8, hy - 4.6, 10.4, 8.8)
        mop = _spiky(mop, hx - 1.8, hy - 4.6, rng, 6, 2.6, angles=(165, 330))
        mop |= K.ellipse(W, H, hx - 5.5, hy + 2.0, 5.0, 6.0)                     # the back of the head
        mop &= ~((xs > hx + 4.0) & (ys > hy - 2.6 + 2.2 * (np.abs(xs - (hx + 6)) < 1.2)))
        if not hair_on:
            mop &= np.zeros_like(mop)
        hv = K.lambert(K.dome(W, H, hx - 3, hy - 7, 12, 10, power=0.7), 3.4)
        c.shade(mop, hv, "hair", cuts=[0.30, 0.50, 0.68, 0.86])
        for (sx, sy, dx) in ((hx - 6, hy - 10, 0.5), (hx - 1, hy - 12, 0.4), (hx - 8, hy - 3, 0.3)):
            for k in range(3):
                x, y = int(sx + k * dx), int(sy + k)
                if mop[y, x]:
                    c.put(x, y, hair[1])
        c.fill(K.ellipse(W, H, hx + 0.5, hy + 2.5, 1.5, 2.1) & ~mop, skin[2])   # ear
        c.put(int(hx + 0.5), int(hy + 2.5), skin[1])
        ex, ey = int(hx + 5.0), int(hy + 0.5)
        for dy in range(5):
            c.put(ex, ey + dy, E)
        c.put(ex, ey, WH); c.put(ex, ey + 1, WH)
        c.put(int(hx + 7), int(hy + 7), MO)
        c.put(int(hx + 4), int(hy + 6), PK)
    else:  # back: the mop covers the head; ears at the sides
        for ex in (hx - 8.6, hx + 8.6):
            c.fill(K.ellipse(W, H, ex, hy + 2.5, 1.3, 2.0), skin[2])
        mop = K.ellipse(W, H, hx, hy - 2.5, 10.8, 10.4) & (ys < hy + 7.5)
        mop = _spiky(mop, hx, hy - 2.5, rng, 7, 2.6, angles=(195, 345))
        if not hair_on:
            mop &= np.zeros_like(mop)
        hv = K.lambert(K.dome(W, H, hx - 2, hy - 6, 12, 12, power=0.7), 3.4)
        c.shade(mop, hv, "hair", cuts=[0.30, 0.50, 0.68, 0.86])
        for (sx, sy, dx) in ((hx - 5, hy - 7, 0.4), (hx + 1, hy - 9, 0.2), (hx + 5, hy - 4, -0.3),
                             (hx - 2, hy + 1, 0.2), (hx + 3, hy + 2, -0.2)):
            for k in range(3):
                x, y = int(sx + k * dx), int(sy + k)
                if mop[y, x]:
                    c.put(x, y, hair[1])


# ----------------------------------------------------------------------------- body + base clothes
def body_layer(p, hair_on=True):
    c = K.Canvas(W, H)
    fac = p["facing"]
    hx, hy = p["head"]
    tx, ty = p["torso"]
    skin, lin = P.ramp("skin"), P.ramp("linen")
    xs, ys = K.grid(W, H)
    # legs: thigh a touch thicker than the shin, a lit kneecap
    for (hip, knee, ankle) in p["legs"]:
        _limb(c, hip, knee, 2.6, "skin", lo=1)
        _limb(c, knee, ankle, 2.2, "skin", lo=1)
        c.put(int(knee[0]) - 1, int(knee[1]), skin[4])
        _foot(c, ankle, fac, lo=1)
    # neck
    c.fill(K.rect(W, H, int(hx) - 2, int(hy) + 8, int(hx) + 1, int(ty) - 8), skin[2])
    c.fill(K.rect(W, H, int(hx) - 2, int(hy) + 8, int(hx) + 1, int(hy) + 8), skin[1])
    if fac in ("front", "back"):
        shoulders = K.ellipse(W, H, 9.0, ty - 6.5, 2.4, 2.6) | K.ellipse(W, H, 23.0, ty - 6.5, 2.4, 2.6)
        top = K.polygon(W, H, [(10.0, ty - 9), (22.0, ty - 9), (22.8, ty + 7.5), (9.2, ty + 7.5)])
        shorts = K.polygon(W, H, [(9.2, ty + 7.0), (22.8, ty + 7.0), (23.2, ty + 14.5), (17.0, ty + 14.5),
                                  (16.0, ty + 12.0), (15.0, ty + 14.5), (8.8, ty + 14.5)])
    else:
        shoulders = K.ellipse(W, H, 16.5, ty - 6.5, 3.0, 2.6)
        top = K.polygon(W, H, [(13.0, ty - 9), (19.8, ty - 9), (20.8, ty - 4), (20.4, ty + 7.5), (12.6, ty + 7.5), (12.2, ty - 3)])
        shorts = K.polygon(W, H, [(12.2, ty + 7.0), (20.8, ty + 7.0), (21.4, ty + 14.5), (11.8, ty + 14.5)])
    tv = 0.45 + 0.5 * K.lambert(K.dome(W, H, tx - 2, ty - 4, 10, 12, power=0.6), 2.6)
    c.shade(shoulders, tv, "skin", cuts=[0.55, 0.72, 0.9], lo=1)
    if fac == "front":                                   # scoop neckline shows skin
        top &= ~K.ellipse(W, H, tx, ty - 9.5, 3.4, 2.6)
        c.fill(K.ellipse(W, H, tx, ty - 9.5, 3.4, 2.6) & (ys >= ty - 9), skin[2])
    c.shade(top, tv, "linen", cuts=[0.52, 0.68, 0.84], lo=1)
    for (fx, fy) in ((tx - 3, ty + 1), (tx + 3, ty + 3)):   # two soft folds
        c.put(int(fx), int(fy), lin[1]); c.put(int(fx) + 1, int(fy) + 1, lin[1])
    c.shade(shorts, tv * 0.9, "linen", cuts=[0.45, 0.62, 0.8], lo=0, hi=3)
    c.fill(K.rect(W, H, 8, int(ty + 7.0), 23, int(ty + 7.0)) & shorts, lin[0])      # waistband
    _head(c, p, hair_on)
    return c


# ----------------------------------------------------------------------------- hands / arms
def fist(c, pos, scale, dim, ramp="skin", facing="front"):
    """A little fist: a knuckle row, a thumb on the inner side. dim = the far hand (kept darker)."""
    x, y = pos
    r = 2.6 * scale
    m = _blob(c, x, y, r, r * 1.05, ramp, cuts=(0.34, 0.52, 0.7, 0.86), lo=1 if not dim else 0,
              hi=None if not dim else 2)
    rp = P.ramp(ramp)
    c.fill(K.rect(W, H, int(x - r + 1), int(y - 0.5), int(x + r - 1), int(y - 0.5)) & m, rp[1])  # knuckle line
    return m


def arms_layer(p, ramp="skin"):
    c = K.Canvas(W, H)
    for (sh, el, wr) in p.get("arms", []):
        _limb(c, sh, el, 2.0, ramp, lo=1)
        _limb(c, el, wr, 1.8, ramp, lo=1)
    return c


# ----------------------------------------------------------------------------- armour pieces
MCUTS = (0.30, 0.48, 0.66, 0.84)


def helmet_layer(p, metal="bronze"):
    """A rounded helm: a rim over the brow, cheek guards that frame the face, a crest ridge, rivets.
    Drawn from the head joint, so it sits correctly in every frame."""
    c = K.Canvas(W, H)
    fac = p["facing"]
    hx, hy = p["head"]
    m = P.ramp(metal)
    xs, ys = K.grid(W, H)
    if fac == "front":
        dome = K.ellipse(W, H, hx, hy - 4.6, 11.4, 9.2) & (ys < hy - 1.0)
        cheeks = (K.polygon(W, H, [(hx - 11.2, hy - 2), (hx - 7.4, hy - 2), (hx - 7.8, hy + 6), (hx - 10.2, hy + 4)]) |
                  K.polygon(W, H, [(hx + 7.4, hy - 2), (hx + 11.2, hy - 2), (hx + 10.2, hy + 4), (hx + 7.8, hy + 6)]))
        shape = dome | cheeks
    elif fac == "side":
        dome = K.ellipse(W, H, hx - 1.0, hy - 4.0, 9.8, 9.0)
        shape = dome & ((ys < hy - 1.0) | ((xs < hx - 1.5) & (ys < hy + 6.5)))
        shape |= K.polygon(W, H, [(hx - 10.6, hy + 2.0), (hx - 6.0, hy + 2.0), (hx - 6.0, hy + 7.0), (hx - 9.8, hy + 6.2)])
    else:
        shape = K.ellipse(W, H, hx, hy - 2.2, 11.4, 10.8) & (ys < hy + 8.0)
    hv = K.lambert(K.dome(W, H, hx - 2, hy - 7, 12.5, 11, power=0.6), 3.4)
    c.shade(shape, hv, metal, cuts=list(MCUTS))
    rim = shape & (ys >= hy - 3.0) & (ys < hy - 1.0)
    c.fill(rim, m[2])
    c.fill(shape & (ys >= hy - 2.0) & (ys < hy - 1.0), m[1])
    c.fill(shape & (ys >= hy - 4.0) & (ys < hy - 3.0), m[4] if fac != "back" else m[3])
    if fac in ("front", "back"):
        for y in range(int(hy - 14), int(hy - 4)):
            if shape[y, int(hx) - 1]:
                c.put(int(hx) - 1, y, m[4]); c.put(int(hx), y, m[2])
        rivets = [(hx - 8, hy - 2.5), (hx - 4, hy - 2.5), (hx + 3, hy - 2.5), (hx + 7, hy - 2.5)]
    else:
        for x in range(int(hx - 10), int(hx + 6)):
            y = int(hy - 13.0 + 0.035 * (x - hx + 2) ** 2)
            if 0 <= y < H and shape[y, x]:
                c.put(x, y, m[4]); c.put(x, y + 1, m[2])
        rivets = [(hx - 7, hy - 2.5), (hx - 3, hy - 2.5), (hx + 1, hy - 2.5)]
    for (rx, ry) in rivets:
        if shape[int(ry), int(rx)]:
            c.put(int(rx), int(ry), m[4])
    c.clean_orphans(passes=1)
    c.outline(P.OUTLINE)
    return c


def chest_layer(p, metal="bronze"):
    """Breastplate with a gorget (collar), layered pauldrons, a leather belt with a buckle, faulds (skirt plates)."""
    c = K.Canvas(W, H)
    fac = p["facing"]
    tx, ty = p["torso"]
    m, lth, gold = P.ramp(metal), P.ramp("wood"), P.ramp("gold")
    xs, ys = K.grid(W, H)
    if fac in ("front", "back"):
        plate = K.polygon(W, H, [(9.6, ty - 9.0), (22.4, ty - 9.0), (23.4, ty - 5.0), (22.8, ty + 1.0),
                                 (21.2, ty + 5.5), (10.8, ty + 5.5), (9.2, ty + 1.0), (8.6, ty - 5.0)])
        v = K.lambert(K.dome(W, H, tx - 2.5, ty - 4.5, 9.5, 10, power=0.5), 4.0)
        c.shade(plate, v, metal, cuts=list(MCUTS))
        if fac == "front":
            for y in range(int(ty - 7), int(ty + 4)):       # the keel of the breastplate
                c.put(int(tx) - 1, y, m[4]); c.put(int(tx), y, m[2])
            gorget = K.ellipse(W, H, tx, ty - 9.0, 5.2, 2.2)
            c.shade(gorget, np.full((H, W), 0.7), metal, cuts=list(MCUTS))
            c.fill(K.rect(W, H, int(tx - 4), int(ty - 8), int(tx + 3), int(ty - 8)) & gorget, m[1])
        # belt + buckle
        belt = K.rect(W, H, 9, int(ty + 5.5), 22, int(ty + 7.0))
        c.shade(belt, np.full((H, W), 0.4), "wood", cuts=[0.3, 0.5], lo=0, hi=2)
        if fac == "front":
            c.fill(K.rect(W, H, int(tx - 1), int(ty + 5.5), int(tx + 1), int(ty + 7.0)), gold[3])
            c.put(int(tx), int(ty + 6.0), gold[1])
        # faulds: two short plates over the shorts
        for (x0, x1) in ((9, 15), (16, 22)):
            fm = K.rect(W, H, x0, int(ty + 8.0), x1, int(ty + 11.5))
            c.shade(fm, 0.75 - 0.3 * (ys - ty - 8) / 4 - 0.1 * (xs - 9) / 13, metal, cuts=list(MCUTS))
            c.fill(K.rect(W, H, x0, int(ty + 11.5), x1, int(ty + 11.5)), m[0])
        # pauldrons: two stacked plates per shoulder
        for (px, py) in ((8.2, ty - 7.2), (23.8, ty - 7.2)):
            _blob(c, px, py, 4.0, 3.2, metal, cuts=MCUTS, strength=3.6)
            _blob(c, px, py + 2.6, 3.4, 2.2, metal, cuts=MCUTS, strength=3.0)
            c.fill(K.rect(W, H, int(px - 3), int(py + 1.4), int(px + 3), int(py + 1.4)) &
                   K.ellipse(W, H, px, py, 4.0, 3.2), m[1])
    else:
        plate = K.polygon(W, H, [(12.4, ty - 9.0), (20.4, ty - 9.0), (21.8, ty - 4.0), (21.2, ty + 5.5), (12.6, ty + 5.5), (12.0, ty - 3.0)])
        v = K.lambert(K.dome(W, H, tx + 2, ty - 4, 8, 11, power=0.55), 3.6)
        c.shade(plate, v, metal, cuts=list(MCUTS))
        belt = K.rect(W, H, 12, int(ty + 5.5), 21, int(ty + 7.0))
        c.shade(belt, np.full((H, W), 0.4), "wood", cuts=[0.3, 0.5], lo=0, hi=2)
        fm = K.rect(W, H, 12, int(ty + 8.0), 21, int(ty + 11.5))
        c.shade(fm, 0.72 - 0.3 * (ys - ty - 8) / 4, metal, cuts=list(MCUTS))
        c.fill(K.rect(W, H, 12, int(ty + 11.5), 21, int(ty + 11.5)), m[0])
        _blob(c, 16.5, ty - 7.0, 4.4, 3.2, metal, cuts=MCUTS, strength=3.6)
        _blob(c, 16.8, ty - 4.4, 3.8, 2.2, metal, cuts=MCUTS, strength=3.0)
    c.clean_orphans(passes=1)
    c.outline(P.OUTLINE)
    return c


def legs_layer(p, metal="bronze"):
    """Cuisses on the thighs, greaves on the shins, a knee cop between — all follow the leg every frame."""
    c = K.Canvas(W, H)
    m = P.ramp(metal)
    for (hip, knee, ankle) in p["legs"]:
        _limb(c, (hip[0], hip[1] + 1.5), (knee[0], knee[1] - 1.0), 2.9, metal, cuts=MCUTS)
        _limb(c, (knee[0], knee[1] + 1.2), (ankle[0], ankle[1] - 0.6), 2.6, metal, cuts=MCUTS)
        kx, ky = knee
        _blob(c, kx, ky, 2.5, 1.9, metal, cuts=MCUTS, strength=4.2)
        c.put(int(kx) - 1, int(ky) - 1, m[4])
    c.clean_orphans(passes=1)
    c.outline(P.OUTLINE)
    return c


def boots_layer(p, metal="bronze"):
    """Sabatons: plated shoes with a toe cap line."""
    c = K.Canvas(W, H)
    m = P.ramp(metal)
    for (hip, knee, ankle) in p["legs"]:
        fm = _foot(c, ankle, p["facing"], ramp=metal)
        ax, ay = ankle
        c.fill(K.rect(W, H, int(ax) - 3, int(ay + 1.0), int(ax) + 4, int(ay + 1.0)) & fm, m[1])
        c.fill(K.rect(W, H, int(ax) - 3, int(ay + 0.0), int(ax) + 4, int(ay + 0.0)) & fm, m[3])
    c.outline(P.OUTLINE)
    return c


# ----------------------------------------------------------------------------- composing a frame
def compose(p, outfit, hands="floating", metal="bronze"):
    """outfit: the armour pieces worn, any of {'helmet','chest','legs','boots','gauntlets'}.
    hands: 'floating' (the approved armless design) or 'arms'. Returns (image canvas, layers)."""
    layers = {"body": body_layer(p, hair_on="helmet" not in outfit)}
    if "legs" in outfit:
        layers["legs"] = legs_layer(p, metal)
    if "boots" in outfit:
        layers["boots"] = boots_layer(p, metal)
    if "chest" in outfit:
        layers["chest"] = chest_layer(p, metal)
    if "helmet" in outfit:
        layers["helmet"] = helmet_layer(p, metal)
    hand_ramp = metal if "gauntlets" in outfit else "skin"
    far, near = K.Canvas(W, H), K.Canvas(W, H)
    if hands == "arms":
        # side view: the far arm (index 0) swings BEHIND the body, dimmed; the near arm in front
        arm_list = p.get("arms", [])
        behind_idx = {0} if p["facing"] == "side" else set()
        al, al_far = K.Canvas(W, H), K.Canvas(W, H)
        for i, (sh, el, wr) in enumerate(arm_list):
            tgt = al_far if i in behind_idx else al
            dim = i in behind_idx
            _limb(tgt, sh, el, 2.0, "skin", lo=0 if dim else 1, hi=2 if dim else None)
            _limb(tgt, el, wr, 1.8, "skin", lo=0 if dim else 1, hi=2 if dim else None)
            if "gauntlets" in outfit:                          # vambraces on the forearms
                _limb(tgt, el, wr, 2.1, metal, cuts=MCUTS, hi=2 if dim else None)
        layers["arms"] = al
        layers["arms_far"] = al_far
    for (pos, scale, behind) in p["hands"]:
        fist(far if behind else near, pos, scale, behind, ramp=hand_ramp)
    for cv in (far, near):
        cv.clean_orphans(passes=1)
        cv.outline(P.OUTLINE)
    layers["hands_far"], layers["hands_near"] = far, near
    layers["body"].clean_orphans(passes=1)

    out = K.Canvas(W, H)
    if "arms_far" in layers:
        af = layers["arms_far"].copy()
        af.outline(P.OUTLINE)
        out.paste(af)
    out.paste(far)
    base = layers["body"].copy()
    base.outline(P.OUTLINE)
    out.paste(base)
    for key in ("legs", "boots", "chest"):
        if key in layers:
            out.paste(layers[key])
    if "arms" in layers:
        a = layers["arms"].copy()
        a.outline(P.OUTLINE)
        out.paste(a)
    if "helmet" in layers:
        out.paste(layers["helmet"])
    out.paste(near)
    return out, layers


def walk(facing, outfit=(), hands="floating", metal="bronze"):
    return [compose(pose(facing, f, arms=(hands == "arms")), set(outfit), hands, metal)[0] for f in range(4)]
