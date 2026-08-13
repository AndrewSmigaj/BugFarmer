"""gallery_gif.py — the gallery's grid, ANIMATED, as one gif you can send someone. FREE, no API.

  python3 tools/player_sprites/gallery_gif.py

Writes `tools/_generated/player/ALL_OUTFITS_ALL_ANIMATIONS.gif` — every official outfit x every official
animation, all playing at once, laid out exactly like `gallery.html`'s **Current** tab.

WHY IT EXISTS NEXT TO gallery.html
----------------------------------
The gallery is the thing to open, and it is the right shape for the job — but it is a local `file://`
page with 39 relative image paths. It cannot be sent to anyone. This is the same view, flattened into a
single file that can be.

IT LOOKS LIKE THE GALLERY BECAUSE IT IS BUILT LIKE THE GALLERY
--------------------------------------------------------------
Owner, 2026-08-13: *"i really need the gif to look like the gallery"*. The version before this one
composed its cells differently from the page — it cropped every frame to the character and applied one
global scale — and the result read as a different thing entirely: ragged grey off-cuts where the crop
box overshot the body, and characters about half the size the gallery shows them at.

So the layout here is a reimplementation of what the browser does with the gallery's CSS, not a fresh
idea:

  * a cell is the WHOLE source gif, background and all, scaled to fit `CELL` px (`td img
    {max-width:150px; max-height:150px}`). No cropping — the grey-green plate behind each character is
    a full clean rectangle, exactly as on the page.
  * a column is as wide as its widest cell, a row as tall as its tallest — that is `border-collapse`
    table sizing, and it is why a swing cell and a walk cell do not line up perfectly on the page either.
  * the same palette: page `#16161c`, header/gutter panel `#1e1e26`, rules `#33333f`, gold `#ffd98a`.
  * outfit names in a left gutter, animation names across the top, both gold — the gallery's row and
    column heads.

Labels are 22pt (review.py's size, ~2x PIL's default) and wrap onto a second line rather than widening
their column, so "swing sword down" does not stretch the grid to fit one long name.

ONE MASTER TIMELINE, AND WHY EVERY CELL STILL LOOPS CLEANLY
-----------------------------------------------------------
Each animation runs at its own speed — a walk steps every 150ms, a run every 90ms, and a swing is
variable (20ms through the stroke, 40ms at the turn, 100ms held at the end). They cannot be laid out
frame-for-frame. Every cell is therefore sampled BY TIME against its own per-frame durations, so each
plays at its own speed inside one shared 1800ms loop.

A cell whose cycle does not divide the loop is cut off mid-motion at the wrap — a sword teleporting from
mid-swing back to over the shoulder, on 21 of the 39 cells. Walk (600ms) and run (360ms) divide 1800
exactly; a 320ms swing gives 5.625 cycles. Making all three seamless honestly needs
LCM(600, 360, 320) = 14.4 seconds, which at this frame rate is 720 frames and an unsendable file.

So each cell's playback rate is nudged to the nearest whole number of cycles in the loop (`fit_loop`):
the swing runs 6 cycles of 300ms instead of 5.625 of 320ms — 6.7% fast, which nobody can see, and the
loop is seamless everywhere. A cell needing more than `RATE_TOL` of stretch keeps its true speed and
wraps mid-motion rather than being visibly distorted.

WHAT IS SHOWN COMES FROM official.py
------------------------------------
Same rule as the gallery: outfits and animations come from `official.py`, never from a directory scan,
so this cannot quietly show something nobody chose. A declared animation with no file on disk renders as
a "missing" cell and is named in the output.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageSequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official as O                                       # noqa: E402  the only source of truth
import review as R                                         # noqa: E402  the readable-label helper

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUT = os.path.join(PLAYER, "ALL_OUTFITS_ALL_ANIMATIONS.gif")

# gallery.html's :root — same page, same colours.
BG, PANEL, LINE = (0x16, 0x16, 0x1c), (0x1e, 0x1e, 0x26), (0x33, 0x33, 0x3f)
GOLD, DIM = (0xff, 0xd9, 0x8a), (0x8a, 0x8a, 0x9c)

CELL = 150          # td img { max-width:150px; max-height:150px }
PADX, PADY = 10, 6  # th/td padding: 6px 10px
LABEL_PT = R.TITLE_PT
TITLE_PT = R.TITLE_PT + 4

STEP_MS = 20        # the finest beat any animation uses
LOOP_MS = 1800      # 3 walk cycles, 5 run cycles
RATE_TOL = 0.20     # how far a cell's speed may be nudged to make the loop seamless


# ---------------------------------------------------------------------------------------------------
# source

def load_cell(outfit, anim):
    """Every frame of one animation with its own duration, plus the cycle length.

    Durations are read PER FRAME rather than off the file header: a swing is 20ms through the stroke,
    40ms at the turn and 100ms held at the end, and a single header duration would flatten that.
    """
    path = os.path.join(PLAYER, O.path(outfit, O.ANIM_DIR), f"{anim}.gif")
    if not os.path.exists(path):
        return None
    im = Image.open(path)
    frames, durs = [], []
    for fr in ImageSequence.Iterator(im):
        frames.append(fr.convert("RGB"))
        durs.append(int(fr.info.get("duration") or 100))
    return dict(frames=frames, durs=durs, cycle=sum(durs) or 100, rate=1.0)


def fit_loop(cell, loop_ms):
    """Nudge this cell's playback rate so a whole number of its cycles fills the loop.

    Returns the rate its clock runs at. 1.0 means the cell already divides the loop (a 600ms walk in an
    1800ms loop) or is too far off to adjust without being visibly wrong, in which case it keeps its true
    speed and wraps mid-motion — the honest failure, rather than a swing played at half speed.
    """
    k = max(1, round(loop_ms / cell["cycle"]))
    rate = cell["cycle"] * k / loop_ms
    return rate if abs(rate - 1.0) <= RATE_TOL else 1.0


def sample(cell, t):
    """The frame this cell is showing at time t, at its own speed, looped."""
    t = (t * cell["rate"]) % cell["cycle"]
    for fr, d in zip(cell["frames"], cell["durs"]):
        if t < d:
            return fr
        t -= d
    return cell["frames"][-1]


def fit(size, cell_px):
    """max-width/max-height: shrink to fit the box, keep the aspect, never enlarge."""
    w, h = size
    s = min(cell_px / w, cell_px / h, 1.0)
    return max(1, round(w * s)), max(1, round(h * s))


# ---------------------------------------------------------------------------------------------------
# layout — what a browser does with the gallery's table

def wrap(draw, text, font, width):
    """Greedy word wrap. A long animation name takes a second line instead of widening its column."""
    lines, cur = [], ""
    for w in text.split():
        trial = f"{cur} {w}".strip()
        if cur and draw.textlength(trial, font=font) > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [text]


class Grid:
    """Column widths, row heights and every cell's position — computed once, drawn for every frame."""

    def __init__(self, rows, cols, cells, cell_px, font, probe, top=0):
        self.rows, self.cols, self.cells, self.font, self.top = rows, cols, cells, font, top
        self.imsize = {k: fit(c["frames"][0].size, cell_px) if c else (cell_px // 2, cell_px // 2)
                       for k, c in cells.items()}
        lh = R.text_h(LABEL_PT)

        self.head = {c: wrap(probe, c.replace("_", " "), font, cell_px) for c in cols}
        self.head_h = max(len(v) for v in self.head.values()) * lh + PADY * 2
        self.gut_w = max(int(probe.textlength(r.replace("_", " "), font=font)) for r in rows) + PADX * 2

        self.col_w = [max([self.imsize[(r, c)][0] for r in rows]
                          + [int(max(probe.textlength(ln, font=font) for ln in self.head[c])) + PADX * 2])
                      for c in cols]
        self.row_h = [max([self.imsize[(r, c)][1] for c in cols] + [lh + PADY * 2]) for r in rows]

        # +1 per rule line, +1 for the closing edge — border-collapse, 1px rules
        self.w = self.gut_w + sum(self.col_w) + len(cols) + 1
        self.h = top + self.head_h + sum(self.row_h) + len(rows) + 1

    def x(self, ci):
        return self.gut_w + sum(self.col_w[:ci]) + ci + 1

    def y(self, ri):
        return self.top + self.head_h + sum(self.row_h[:ri]) + ri + 1


def chrome(g, title, sub):
    """The static part — the title bar, panel bands, rules, gold labels. Drawn once and copied per frame,
    because it is identical in every one of them and re-rendering text 90 times is the slow half of the
    build."""
    im = Image.new("RGB", (g.w, g.h), BG)
    d = ImageDraw.Draw(im)
    lh = R.text_h(LABEL_PT)

    d.rectangle([0, 0, g.w - 1, g.top + g.head_h - 1], fill=PANEL)       # title bar + header band
    d.rectangle([0, 0, g.gut_w - 1, g.h - 1], fill=PANEL)                # left gutter

    if g.top:                                                            # gallery.html's <header>
        tf, sf = R.font(TITLE_PT), R.font(R.NOTE_PT)
        d.text((PADX, (g.top - TITLE_PT) // 2 - 3), title, fill=(0xe8, 0xe8, 0xf0), font=tf)
        d.text((PADX + d.textlength(title, font=tf) + 14, (g.top - R.NOTE_PT) // 2 - 1),
               sub, fill=DIM, font=sf)
        d.line([0, g.top - 1, g.w, g.top - 1], fill=LINE)

    for ri in range(len(g.rows)):                                        # rules
        d.line([0, g.y(ri) - 1, g.w, g.y(ri) - 1], fill=LINE)
    d.line([0, g.h - 1, g.w, g.h - 1], fill=LINE)
    for ci in range(len(g.cols)):
        d.line([g.x(ci) - 1, g.top, g.x(ci) - 1, g.h], fill=LINE)
    d.line([g.w - 1, g.top, g.w - 1, g.h], fill=LINE)

    for ci, c in enumerate(g.cols):                                      # column heads, centred
        lines = g.head[c]
        top = g.top + (g.head_h - len(lines) * lh) // 2
        for i, line in enumerate(lines):
            tw = d.textlength(line, font=g.font)
            d.text((g.x(ci) + (g.col_w[ci] - tw) / 2, top + i * lh + (lh - LABEL_PT) // 2 - 2),
                   line, fill=GOLD, font=g.font)

    for ri, r in enumerate(g.rows):                                      # row heads, left aligned
        d.text((PADX, g.y(ri) + (g.row_h[ri] - LABEL_PT) // 2 - 3),
               r.replace("_", " "), fill=GOLD, font=g.font)

    for ri, r in enumerate(g.rows):                                      # declared but absent
        for ci, c in enumerate(g.cols):
            if g.cells[(r, c)] is None:
                d.text((g.x(ci) + g.col_w[ci] // 2 - 6, g.y(ri) + g.row_h[ri] // 2 - LABEL_PT // 2),
                       "—", fill=DIM, font=g.font)
    return im


def frame_at(g, base, t):
    """One frame of the whole sheet: every cell sampled at time t and pasted into its box."""
    im = base.copy()
    for ri, r in enumerate(g.rows):
        for ci, c in enumerate(g.cols):
            cell = g.cells[(r, c)]
            if not cell:
                continue
            w, h = g.imsize[(r, c)]
            src = sample(cell, t).resize((w, h), Image.LANCZOS)
            im.paste(src, (g.x(ci) + (g.col_w[ci] - w) // 2, g.y(ri) + (g.row_h[ri] - h) // 2))
    return im


# ---------------------------------------------------------------------------------------------------

def build(cell_px=CELL, flip=False, step=STEP_MS, loop_ms=LOOP_MS, out=OUT):
    outfits, anims = list(O.OUTFITS), list(O.ANIMATIONS)
    cells, gaps = {}, []
    for o in outfits:
        for a in anims:
            c = load_cell(o, a)
            cells[(a, o) if flip else (o, a)] = c
            if c is None:
                gaps.append(f"{o}/{a}")

    nudged = 0
    for c in cells.values():
        if c:
            c["rate"] = fit_loop(c, loop_ms)
            nudged += c["rate"] != 1.0

    rows, cols = (anims, outfits) if flip else (outfits, anims)
    font = R.font(LABEL_PT)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    g = Grid(rows, cols, cells, cell_px, font, probe, top=R.text_h(TITLE_PT) + PADY * 2)
    base = chrome(g, "Bug Farmer — player outfits",
                  f"{len(outfits)} official · {len(anims)} animations · from official.py")

    n = max(1, loop_ms // step)
    frames = [frame_at(g, base, i * step) for i in range(n)]

    # ONE palette for the whole file. Built from frames spread across the loop so a swing's mid-stroke
    # colours are represented, not just the pose everything happens to start in.
    probes = min(8, n)
    strip = Image.new("RGB", (g.w, g.h * probes))
    for i in range(probes):
        strip.paste(frames[i * n // probes], (0, i * g.h))
    pal = strip.quantize(colors=255, method=Image.MEDIANCUT)
    frames = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]

    os.makedirs(os.path.dirname(out), exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=step, loop=0, optimize=True)

    mb = os.path.getsize(out) / 1e6
    print(f"  {out.replace('/mnt/c/', 'C:/')}")
    print(f"    {len(rows)} x {len(cols)} = {sum(1 for c in cells.values() if c)} cells, "
          f"{g.w}x{g.h}, {n} frames, {loop_ms}ms loop, {mb:.1f} MB")
    print(f"    laid out like gallery.html's Current tab — whole gifs, no cropping, {cell_px}px cells")
    print(f"    {nudged} of {len(cells)} cells re-timed by <{int(RATE_TOL * 100)}% so every cell loops "
          f"seamlessly in {loop_ms}ms")
    print(f"    labels {LABEL_PT}pt — ~2x PIL's default, because he should not have to zoom in")
    for m in gaps:
        print(f"    MISSING  {m} — declared in official.py, no file on disk")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cell", type=int, default=CELL, help="max px per cell (the gallery uses 150)")
    ap.add_argument("--flip", action="store_true", help="rows = animations (the gallery's flip button)")
    ap.add_argument("--step", type=int, default=STEP_MS, help="ms per gif frame")
    ap.add_argument("--loop", type=int, default=LOOP_MS, help="ms per loop")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    build(a.cell, a.flip, a.step, a.loop, a.out)
