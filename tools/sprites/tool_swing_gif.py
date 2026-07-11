#!/usr/bin/env python3
"""Tool-swing GIF previews — the PYTHON mirror of PlayerToolAnimator's motion model.

Renders each tool_type's in-hand swing as an animated GIF WITHOUT Unity, so we can iterate on
feel (arc, timing, reach, technique) and see options side-by-side before touching the C#. It ports
the EXACT motion math from `PlayerToolAnimator.AnimateRoutine`:
  - the easing curves (EaseOut = 1-(1-t)^2, EaseIn = t^3 CUBIC, EaseOutBack, c1=1.70158),
  - the per-AnimKind segment schedule (Swing 3-segment, Chop wind/strike/HOLD/recoil, Till drag,
    Scoop thrust/lift/settle, Sweep even ease-out, Stab out/back, Pour tip-and-hold),
  - the geometry: a pivot at the player center rotates by `pivotAngle`; the tool sits at local
    (offset,0) with localRotation −SpriteArtAngle(45°); the item icon points NE by the diagonal
    art convention, so −45° aims it along the pivot at aimAngle=0 (east).

FIDELITY NOTE: this reproduces the same curves/geometry the engine runs, so a change here previews
the same change there — but it is a MODEL, not a screen capture (no real player body, procedural
trail approximates the TrailRenderer). Spot-check against one in-engine capture when it matters.

    python3 tools/sprites/tool_swing_gif.py            # all tools -> examples/tool_swings/<tool>.gif
    python3 tools/sprites/tool_swing_gif.py --tool shovel
Outputs to tools/_generated/previews/examples/tool_swings/.
"""
import os
import math
import argparse
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEMS = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Items")
OUT = os.path.join(ROOT, "tools", "_generated", "previews", "examples", "tool_swings")

SPRITE_ART_ANGLE = 45.0
IDLE_ANGLE = -35.0   # the down-right idle the swings blend FROM (Right facing)
IDLE_OFFSET = 0.4
IDLE_SCALE = 0.75

# Mirror PlayerToolAnimator.Profiles (kind + timing + arc + offset [+ stab reach]).
PROFILES = {
    "axe":          dict(kind="chop",  dur=0.34, arc=110, off=0.55),
    "pickaxe":      dict(kind="chop",  dur=0.34, arc=110, off=0.55),
    "shovel":       dict(kind="scoop", dur=0.24, arc=90,  off=0.55),
    "hoe":          dict(kind="till",  dur=0.24, arc=90,  off=0.55),
    "sword":        dict(kind="swing", dur=0.20, arc=100, off=0.6),
    "net":          dict(kind="sweep", dur=0.25, arc=90,  off=0.6),
    "scythe":       dict(kind="sweep", dur=0.25, arc=120, off=0.6),
    "spear":        dict(kind="stab",  dur=0.22, off=0.45, reach=1.1),
    "watering_can": dict(kind="pour",  dur=0.30, off=0.5),
}
# A representative item icon per tool_type (grip bottom-left, head top-right).
ICONS = {
    "axe": "axe_wood", "pickaxe": "pickaxe_wood", "shovel": "shovel_wood",
    "hoe": "hoe_wood", "sword": "sword_wood", "net": "small_net",
    "scythe": "scythe_wood", "spear": "spear_wood", "watering_can": "watering_can_basic",
}

PPU = 54
SIZE = 190


def ease_out(t): return 1.0 - (1.0 - t) * (1.0 - t)
def ease_in(t): return t * t * t                       # CUBIC (matches C# EaseIn)
def lerp(a, b, t): return a + (b - a) * t


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1.0
    u = t - 1.0
    return 1.0 + c3 * u * u * u + c1 * u * u


def sample(p, t, aim=0.0):
    """Return (pivot_angle_deg, offset, scale, tool_extra_rot_deg, emit_trail) at normalized t.
    Ported branch-for-branch from AnimateRoutine."""
    kind, off0 = p["kind"], p["off"]

    if kind == "swing":
        half = p["arc"] / 2.0
        endA = aim - half
        topA = aim + half + half * 0.30
        antF, strF = 0.15, 0.50
        if t < antF:
            ang = lerp(IDLE_ANGLE, topA, ease_out(t / antF)); off = off0
        elif t < antF + strF:
            u = (t - antF) / strF
            ang = lerp(topA, aim, ease_in(u))
            off = lerp(off0, off0 + 0.2, ease_in(u))
        else:
            u = (t - antF - strF) / (1 - antF - strF)
            ang = lerp(aim, endA, ease_out_back(u))
            off = lerp(off0 + 0.2, off0, ease_out(u))
        return ang, off, 1.0, 0.0, True

    if kind == "sweep":
        half = p["arc"] / 2.0
        ang = lerp(aim + half, aim - half, ease_out(t))
        return ang, off0, 1.0, 0.0, True

    if kind == "stab":
        reach = p["reach"]
        off = lerp(off0, reach, t / 0.4) if t < 0.4 else lerp(reach, off0, (t - 0.4) / 0.6)
        return aim, off, 1.0, 0.0, False

    if kind == "pour":
        # The can is a 3/4 UPRIGHT sprite (not diagonal): it must NOT take the -45 art angle. Reach out,
        # tip the spout down to pour, hold with a gentle bob, rock back upright. `extra` is set so the
        # rendered angle (ang-45+extra, with ang=aim=0) equals the absolute tilt.
        base = off0
        antF, tipF, holdF = 0.18, 0.24, 0.40
        pour_tilt, wind_tilt = -60.0, 12.0
        if t < antF:
            u = t / antF
            tilt = lerp(0.0, wind_tilt, ease_out(u)); off = lerp(base, base + 0.08, ease_out(u))
        elif t < antF + tipF:
            tilt = lerp(wind_tilt, pour_tilt, ease_in((t - antF) / tipF)); off = base + 0.08
        elif t < antF + tipF + holdF:
            h = (t - antF - tipF) / holdF
            tilt = pour_tilt + math.sin(h * math.pi * 3.0) * 3.0; off = base + 0.08
        else:
            u = (t - antF - tipF - holdF) / (1 - antF - tipF - holdF)
            tilt = lerp(pour_tilt, 0.0, ease_out(u)); off = base
        return aim, off, 1.0, tilt + SPRITE_ART_ANGLE, False

    if kind == "chop":
        half = p["arc"] / 2.0
        endA = aim - half
        topA = aim + half + half * 0.35
        antF, strF, holdF = 0.22, 0.33, 0.28
        if t < antF:
            ang = lerp(IDLE_ANGLE, topA, ease_out(t / antF))
        elif t < antF + strF:
            ang = lerp(topA, aim, ease_in((t - antF) / strF))
        elif t < antF + strF + holdF:
            ang = aim
        else:
            ang = lerp(aim, endA, ease_out((t - antF - strF - holdF) / (1 - antF - strF - holdF)))
        return ang, off0, 1.0, 0.0, True

    if kind == "till":
        # Raise HIGH, chop the blade down into the soil, then DRAG it firmly back toward the player (the
        # characteristic till). Bigger wind-up + deeper drag than v1, and the blade dips down as it bites.
        half = p["arc"] / 2.0
        topA = aim + half + half * 0.35     # higher raise
        antF, strF = 0.20, 0.30
        dragTo = off0 - 0.55                 # deeper pull-back
        biteAngle = aim - 12.0              # head dips slightly past level as it bites & drags
        if t < antF:
            ang = lerp(IDLE_ANGLE, topA, ease_out(t / antF)); off = off0
        elif t < antF + strF:
            ang = lerp(topA, aim, ease_in((t - antF) / strF)); off = off0
        else:
            u = (t - antF - strF) / (1 - antF - strF)
            ang = lerp(aim, biteAngle, ease_out(u))
            off = lerp(off0, dragTo, ease_in(u))   # accelerate the pull — reads as dragging through soil
        return ang, off, 1.0, 0.0, True

    if kind == "scoop":
        reach = off0 + 0.45
        liftA = aim + 55.0
        thrustF, liftF = 0.35, 0.40
        if t < thrustF:
            u = t / thrustF
            off = lerp(off0, reach, ease_in(u)); sc = lerp(1.0, 0.9, u); ang = aim
        elif t < thrustF + liftF:
            u = (t - thrustF) / liftF
            off = lerp(reach, off0, ease_out(u)); sc = lerp(0.9, 1.1, u)
            ang = lerp(aim, liftA, ease_out(u))
        else:
            u = (t - thrustF - liftF) / (1 - thrustF - liftF)
            off = off0; sc = lerp(1.1, 1.0, u); ang = lerp(liftA, aim, u)
        return ang, off, sc, 0.0, False

    return aim, off0, 1.0, 0.0, False


def fit_icon(icon, cells=1.0):
    target = cells * PPU
    s = min(1.0, target / max(icon.width, icon.height))
    return icon.resize((max(1, round(icon.width * s)), max(1, round(icon.height * s))), Image.NEAREST)


def _head_px(ang, off):
    cx, cy = SIZE // 2, SIZE // 2
    rad = math.radians(ang)
    hoff = off + 0.3  # TrailAnchor sits a bit past the sprite center
    return cx + hoff * math.cos(rad) * PPU, cy - hoff * math.sin(rad) * PPU


def render_frame(icon_fit, ang, off, sc, extra, trail):
    canvas = Image.new("RGBA", (SIZE, SIZE), (58, 58, 64, 255))
    d = ImageDraw.Draw(canvas)
    cx, cy = SIZE // 2, SIZE // 2
    # ground reference + player marker (neutral placeholder; the real body is a separate overhaul)
    d.ellipse([cx - 22, cy + 8, cx + 22, cy + 20], fill=(48, 50, 56, 255))
    d.ellipse([cx - 10, cy - 12, cx + 10, cy + 10], fill=(118, 128, 150, 255), outline=(205, 205, 215, 255))
    # procedural trail (approximates the TrailRenderer)
    for i, (tx, ty) in enumerate(trail):
        a = int(150 * (i + 1) / max(1, len(trail)))
        r = 2 + i * 0.5
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(255, 255, 255, a))
    tool = icon_fit
    if abs(sc - 1.0) > 1e-3:
        tool = tool.resize((max(1, round(tool.width * sc)), max(1, round(tool.height * sc))), Image.NEAREST)
    rot = tool.rotate(ang - SPRITE_ART_ANGLE + extra, expand=True, resample=Image.BICUBIC)
    rad = math.radians(ang)
    px = cx + off * math.cos(rad) * PPU
    py = cy - off * math.sin(rad) * PPU
    canvas.alpha_composite(rot, (round(px - rot.width / 2), round(py - rot.height / 2)))
    return canvas


def render_gif(tool_type, out_path, nframes=20, scale=3):
    p = PROFILES[tool_type]
    raw = Image.open(os.path.join(ITEMS, f"{ICONS[tool_type]}_icon.png")).convert("RGBA")
    active_icon = fit_icon(raw, 1.0)
    idle_icon = fit_icon(raw, IDLE_SCALE)

    frames, durs, trail = [], [], []
    active_ms = max(28, round(p["dur"] * 1000 / nframes))
    for i in range(nframes):
        t = (i + 0.5) / nframes
        ang, off, sc, extra, emit = sample(p, t)
        if emit:
            trail.append(_head_px(ang, off)); trail = trail[-6:]
        else:
            trail = []
        frames.append(render_frame(active_icon, ang, off, sc, extra, list(trail)))
        durs.append(active_ms)
    # settle back to the idle pose, held briefly (so the loop reads swing -> rest -> swing)
    for _ in range(5):
        frames.append(render_frame(idle_icon, IDLE_ANGLE, IDLE_OFFSET, 1.0, 0.0, []))
        durs.append(110)

    big = [f.resize((f.width * scale, f.height * scale), Image.NEAREST) for f in frames]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    big[0].save(out_path, save_all=True, append_images=big[1:], duration=durs, loop=0, disposal=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", default=None, help="one tool_type, or all if omitted")
    ap.add_argument("--frames", type=int, default=20)
    a = ap.parse_args()
    tools = [a.tool] if a.tool else list(PROFILES.keys())
    made = []
    for tt in tools:
        out = os.path.join(OUT, f"{tt}.gif")
        render_gif(tt, out, nframes=a.frames)
        made.append(out)
    print("wrote:\n  " + "\n  ".join(made))


if __name__ == "__main__":
    main()
