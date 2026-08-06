"""review.py — build a comparison sheet the owner can actually read, and say so out loud.

Anything he has to LOOK AT to make a decision goes through here. Two conventions are baked in because
both have been got wrong more than once, and a convention nobody can forget beats a convention written
down somewhere.

1. **TEXT IS ~2x PIL's DEFAULT.** `ImageDraw.text()` with no `font=` uses an ~11px bitmap face. Owner,
   2026-08-06: *"i literally have to zoom in to see it its so tiny... maybe make it twice as big... i
   asked you before so can you somehow remember this."* Asking twice is the failure; a helper that
   cannot render small text is the fix.

2. **IT LANDS IN THE REPO, never a temp dir.** Claude runs in a VM — `/tmp/...` and `/mnt/...` paths do
   not exist on his machine, so showing him one shows him nothing. `save()` prints the `C:/` path back.

THE SCRIPT IS THE REMINDER
--------------------------
`save()` prints the conventions it just applied. Owner's idea, 2026-08-06: *"having python scripts
perhaps actually output things - reminders and such, as a form of 'hook' - as long as you read the output
of the script."* Cheaper than a hook, impossible to route around, and it fires exactly when relevant —
at the moment the sheet is being made.
"""
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEWS = os.path.join(REPO, "tools", "_generated", "player", "reviews")

# ~2x the PIL default. TITLE labels a panel; NOTE is the secondary line under it. Both are readable at
# 100% zoom on his monitor, which is the entire requirement.
TITLE_PT, NOTE_PT = 22, 17

_FACES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/mnt/c/Windows/Fonts/segoeuib.ttf",
]

INK, DIM, BG = (242, 242, 245), (155, 160, 168), (26, 28, 31)


def font(pt=TITLE_PT, bold=True):
    """A real TrueType face. Falls back to PIL's bitmap font ONLY if no face exists on the machine —
    and says so, because silently reverting to unreadable text is the bug this module exists to stop."""
    for p in _FACES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, pt)
            except Exception:
                continue
    print("  ⚠ no TrueType face found — labels will render at PIL's tiny default size")
    return ImageFont.load_default()


def text_h(pt=TITLE_PT):
    """Row height to reserve for a label at this size."""
    return int(pt * 1.9)


def _text_w(d, s, f):
    """Rendered width of a label. The sheet must be at least this wide or the text is CLIPPED — which
    is exactly what happened the first time this helper was used, defeating the point of large text."""
    try:
        return int(d.textlength(s, font=f))
    except Exception:
        return len(s) * TITLE_PT             # crude, but never narrower than reality


def stack(panels, note=None, pad=14):
    """Panels top to bottom, each with a big label above it. `panels` = [(label, PIL.Image), ...]."""
    f, fn = font(TITLE_PT), font(NOTE_PT, bold=False)
    lab = text_h(TITLE_PT)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = max([im.width for _, im in panels]
            + [_text_w(probe, s, f) for s, _ in panels]
            + ([_text_w(probe, note, fn)] if note else [])) + pad * 2
    foot = text_h(NOTE_PT) if note else 0
    h = sum(im.height + lab for _, im in panels) + pad * 2 + foot
    sheet = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(sheet)
    y = pad
    for label, im in panels:
        d.text((pad, y + (lab - TITLE_PT) // 2 - 2), label, fill=INK, font=f)
        sheet.paste(im, (pad, y + lab))
        y += lab + im.height
    if note:
        d.text((pad, y + 2), note, fill=DIM, font=fn)
    return sheet


def row(panels, note=None, pad=14, gap=28):
    """Panels left to right, each labelled. Use when the comparison is across, not down."""
    f, fn = font(TITLE_PT), font(NOTE_PT, bold=False)
    lab = text_h(TITLE_PT)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    # each column must fit its own label, or the text is clipped
    cols = [max(im.width, _text_w(probe, s, f)) for s, im in panels]
    w = max(sum(cols) + gap * (len(panels) - 1),
            _text_w(probe, note, fn) if note else 0) + pad * 2
    foot = text_h(NOTE_PT) if note else 0
    h = max(im.height for _, im in panels) + lab + pad * 2 + foot
    sheet = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(sheet)
    x = pad
    for (label, im), cw in zip(panels, cols):
        d.text((x, pad + (lab - TITLE_PT) // 2 - 2), label, fill=INK, font=f)
        sheet.paste(im, (x, pad + lab))
        x += cw + gap
    if note:
        d.text((pad, h - foot - 2), note, fill=DIM, font=fn)
    return sheet


def save(sheet, folder, name):
    """Write into reviews/<folder>/ and print the conventions that were applied.

    `folder` is `<YYYY-MM-DD>-<what>` — dated so a re-run never overwrites the sheet a decision was made
    from. Overwriting review output has cost real work ("can you please stop overwriting files i cant
    show you the old one").
    """
    d = os.path.join(REVIEWS, folder)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    sheet.save(p)
    print(f"  {p.replace('/mnt/c/', 'C:/')}   ({sheet.width}x{sheet.height})")
    print(f"    labels {TITLE_PT}pt — ~2x PIL's default, because he should not have to zoom in")
    if not os.path.exists(os.path.join(d, "README.md")):
        print(f"    ⚠ {folder}/ has no README.md — say what each image is and what you want decided")
    return p
