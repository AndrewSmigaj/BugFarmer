"""preview_all.py — every outfit on one page, so a set can be compared against the others. FREE, no API.

  python3 tools/player_sprites/preview_all.py            # both sheets
  python3 tools/player_sprites/preview_all.py outfits    # just ALL_outfits.png
  python3 tools/player_sprites/preview_all.py gauntlets  # just ALL_gauntlets.png

Writes `outfits/ALL_outfits.png` and `outfits/ALL_gauntlets.png`.

This exists because the first versions of these two images were assembled by hand and had no script,
which is the thing that keeps getting lost. A set is judged against its neighbours — whether copper
reads as different metal from bronze is a question about the pair, not about copper — so the sheet has
to be cheap to rebuild after every new set.

Frames come from each outfit's DEMO.gif, so the sheet always shows the CURRENT swing. It never holds its
own copy of the motion, and it enumerates the outfits folder rather than carrying a hand-written list —
the retired top-level `contact_sheet.py` was dropped precisely for being hand-listed and going stale.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTFITS = os.path.join(REPO, "tools", "_generated", "player", "outfits")

COLS = 3                 # outfits across the page
SAMPLES = 2              # frames taken from each DEMO.gif
# Every frame is resized to ONE size. demo_swings scales its whole scene off the outfit's own sprite
# height, so the gifs range from 873x491 to 1388x781 — identical composition, different pixel size.
# Laying them out at native size silently misaligns the grid, so normalise here.
FRAME = (470, 264)       # ~half of a typical demo frame; the aspect is the same for all of them
BG = (18, 20, 18)
LABEL_H = 16
PAD = 4


def names():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(OUTFITS, "*"))
                  if os.path.isdir(p))


def demo_frames(name, n=SAMPLES):
    """n evenly-spaced frames from the outfit's DEMO.gif, skipping the trailing idle pose."""
    p = os.path.join(OUTFITS, name, "DEMO.gif")
    if not os.path.exists(p):
        return []
    im = Image.open(p)
    total = getattr(im, "n_frames", 1)
    last = max(1, total - 1)                       # the final frame is the long idle hold
    out = []
    for i in range(n):
        im.seek(min(last - 1, round((i + 0.5) * last / n)))
        out.append(im.convert("RGB").copy().resize(FRAME, Image.LANCZOS))
    return out


def grid(items, out_path, title_of=lambda k: k):
    """items: list of (label, [PIL frames]). Lays them out COLS across with a label per cell."""
    items = [(k, f) for k, f in items if f]
    if not items:
        print(f"  nothing to draw for {os.path.basename(out_path)}")
        return None
    fw, fh = items[0][1][0].size
    cell_w = fw * len(items[0][1]) + PAD * (len(items[0][1]) - 1)
    cell_h = fh + LABEL_H
    rows = (len(items) + COLS - 1) // COLS
    sheet = Image.new("RGB", (cell_w * COLS + PAD * (COLS - 1),
                              cell_h * rows + PAD * (rows - 1)), BG)
    d = ImageDraw.Draw(sheet)
    for i, (label, frames) in enumerate(items):
        cx = (i % COLS) * (cell_w + PAD)
        cy = (i // COLS) * (cell_h + PAD)
        d.text((cx + 2, cy + 3), title_of(label), fill=(235, 235, 235))
        for j, f in enumerate(frames):
            sheet.paste(f, (cx + j * (fw + PAD), cy + LABEL_H))
    sheet.save(out_path)
    print(f"  {os.path.basename(out_path)}  {sheet.size[0]}x{sheet.size[1]}  ({len(items)} sets)")
    return out_path


def sheet_outfits():
    return grid([(n, demo_frames(n)) for n in names()],
                os.path.join(OUTFITS, "ALL_outfits.png"))


def sheet_gauntlets():
    """The four cut hands per set, upscaled so they are actually visible on the page."""
    items = []
    for n in names():
        parts = [os.path.join(OUTFITS, n, "gauntlet", f"{s}.png")
                 for s in ("front", "back", "side", "grip")]
        got = [Image.open(p).convert("RGB") for p in parts if os.path.exists(p)]
        if not got:
            continue
        h = max(g.height for g in got)
        scale = max(1, round(110 / h))
        items.append((n, [g.resize((g.width * scale, g.height * scale), Image.NEAREST) for g in got]))
    if not items:
        return None
    # pad every set to the same cell size — gauntlet crops differ by a pixel or two
    w = max(f.width for _, fs in items for f in fs)
    h = max(f.height for _, fs in items for f in fs)
    fixed = []
    for n, fs in items:
        pads = []
        for f in fs:
            c = Image.new("RGB", (w, h), BG)
            c.paste(f, ((w - f.width) // 2, (h - f.height) // 2))
            pads.append(c)
        fixed.append((n, pads))
    return grid(fixed, os.path.join(OUTFITS, "ALL_gauntlets.png"))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "both"
    if what in ("both", "outfits"):
        sheet_outfits()
    if what in ("both", "gauntlets"):
        sheet_gauntlets()
