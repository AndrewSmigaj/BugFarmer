"""procedure.py — the outfit procedure, exactly as the three approved outfits were made.

Proven on fire-ant, then black-ant and bronze, on 2026-08-15 — owner: *"those are fine, so this approach works"*
— and made official 2026-08-18. Until 2026-09-26, steps 3-6 existed only as hand-typed prompts and one-off session
scripts. This file rebuilds them from the run records (`explore/<run>/RECORD.txt`, `RUNS.txt`), and `verify`
proves, with no image calls, that it reproduces those runs: the prompts word for word, the reference images pixel
for pixel, and — cutting the approved renders at their grids — every committed frame and hand byte for byte.

  step                    command                                                     cost
  1 three designs         outfits.py explore <name>                                   1 call
  2 the owner picks       he picks one; that figure is saved as explore/<run>/CHOSEN_<name>.png
  3 pixel reference       procedure.py grids <run> [--option N]      candidate grids, judged by eye
                          procedure.py pick <name> <run> --pitch P    -> <name>-turnaround/CHOSEN_ref.png
  4 turnaround            procedure.py turnaround <name> [--go]                       1 call
                          procedure.py views <name> --pitch P         -> view_front / view_side / view_back
  5 walks                 procedure.py walk <name> side|front|back [--go]             1 call each
                          procedure.py cutwalk <name> side|front|back --pitch P
  6 hands                 procedure.py hands <name> [--go]                            1 call
                          procedure.py cuthands <name> --pitch P
  7 review, then official the player-sprites skill (build.py renders a PENDING outfit for review)
  -                       procedure.py verify                         the approved runs, reproduced

A PAID step without --go prepares its references in the run folder, prints exactly what would be sent — the
prompt, each reference at the size the model will see, the canvas — and spends nothing. Every paid call is asked
for first; --go is for after the owner has said yes. With --go the call goes through gen.py, which records it
(RECORD.txt beside the result, one line in RUNS.txt).

Folders are the ones the approved runs used, so old and new runs sit side by side:
  explore/<name>-turnaround/    CHOSEN_ref.png (the pick in real pixels), result.png, view_front/side/back.png
  explore/<name>-<view>walk/    CHOSEN_ref.png (that view of the turnaround), result.png
  explore/<name>-gauntlet/      REF_boxes.png (the template), REF_shapes.png (the hand shapes), result.png
  outfits/<name>/tries/<date>-procedure/   frames/ + gauntlet/ as cut, and CUTS.txt saying what each came from
A reroll is a new run folder (`--run <name>-frontwalk-r2`); a paid result is never overwritten.
"""
import argparse
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "aipipe"))
import cut_walk_row as C                      # noqa: E402  the cutters: snap_whole, cut_walk, cut_gauntlet_column
import gen as G                               # noqa: E402  the only way to spend — and its clause guard
import official as O                          # noqa: E402  HAND_ROLES, the walk's hand ratio
import outfits as OF                          # noqa: E402  every prompt: TURNAROUND, walk_prompt, hands_prompt
import pixelsnap as PS                        # noqa: E402
import preview_explore as PE                  # noqa: E402  the magenta key
import review as RV                           # noqa: E402  22pt labels on anything he looks at
from cut_outfit import defringe               # noqa: E402

PLAYER = OF.PLAYER
EXPLORE = os.path.join(PLAYER, "explore")
REPO = OF.REPO

TURNAROUND_SIZE = WALK_SIZE = "1536x1024"   # landscape: the figures side by side, each as large as possible
HANDS_SIZE = "1024x1536"                     # PORTRAIT — the only canvas that lands a hand near 13 blocks
SEND_SCALE = 14                              # gen.py enlarges every reference under 400px by this

# The five hand SHAPES every outfit copies: bronze's approved hands as they were before 2026-08-15, 20 px tall,
# on black. Both black-ant (blackant-v3-gauntlet) and bronze (bronze-v2-gauntlet) sent exactly this file.
# (Fire-ant, the first run, sent the same five shapes in its own colours.) The bronze-reroll review of 2026-08-15
# says later outfits "will be copied from" bronze's new 12-px hands instead — that was never tried, so the proven
# file stays until the owner decides otherwise.
HAND_SHAPES = os.path.join(EXPLORE, "bronze-v2-gauntlet", "REF_shapes.png")

# Hand height = round(front view height x the walk's hand ratio): 68 -> 12 (bronze), 76 -> 13 (fire-ant),
# 91 -> 15 (black-ant). The hands are then drawn at exactly the size the walk shows them — never rescaled.
HAND_RATIO = O.GAITS["WALK"]["ratio"]

# The template layout, measured off all three approved templates (they differ only by these rules):
# the front view at a 5-px margin; 8 px right of it, a column of five boxes, each one hand tall and
# round(0.9 x hand) wide, 3 px apart, centred on the figure but never above the margin.
T_MARGIN, T_GAP, T_BOX_GAP, T_BOX_W = 5, 8, 3, 0.9
KEY = (255, 0, 255, 255)
CYAN = (0, 255, 255, 255)
VIEWS = ("front", "side", "back")        # left to right, as the turnaround prompt asks for them


# ── small helpers ───────────────────────────────────────────────────────────────────────────────────

def _c(path):
    """A path as the owner opens it (he is on Windows; the VM's /mnt/c paths mean nothing to him)."""
    return os.path.abspath(path).replace("/mnt/c/", "C:/")


def _rel(path):
    return os.path.relpath(path, REPO)


def _rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"), np.uint8)


def _record_prompt(run):
    """The prompt a run actually sent. gen.py writes it after 'PROMPT:' followed by exactly one newline."""
    text = open(os.path.join(EXPLORE, run, "RECORD.txt"), encoding="utf-8").read()
    return text.split("PROMPT:\n", 1)[1][:-1]


def _record_date(run):
    text = open(os.path.join(EXPLORE, run, "RECORD.txt"), encoding="utf-8").read()
    return re.search(r"^when\s*:\s*(\d{4}-\d{2}-\d{2})", text, re.M).group(1)


def _slots(name):
    """(what the outfit is, what its hands are made of) — the words the walk and hands prompts need."""
    if name not in OF.OUTFITS:
        raise SystemExit(
            f"{name!r} is not in outfits.OUTFITS, so there are no words for its walk and hands prompts.\n"
            "  Add it there — (what it is, material, headgear, what the hands are made of) — and show the\n"
            "  owner the words first: prompts are his.")
    what, _material, _headgear, glove = OF.OUTFITS[name]
    return what, glove


def _colours(a):
    m = a[..., 3] > 0
    return len(np.unique(a[m][:, :3], axis=0)) if m.any() else 0


def _crop(a):
    m = a[..., 3] > 0
    ys, xs = np.where(m.any(1))[0], np.where(m.any(0))[0]
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _write_once(dst, img):
    """Write a derived reference, but never replace a DIFFERENT one — that would change a run after the fact."""
    if os.path.exists(dst):
        if np.array_equal(_rgba(dst), np.asarray(img.convert("RGBA"))):
            return "unchanged"
        raise SystemExit(f"{_rel(dst)} already exists and is different.\n"
                         "  Move it to an archive/ folder first (nothing is deleted), or use a new --run folder.")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst)
    return "written"


def _try_dir(name, turnaround):
    """outfits/<name>/tries/<date of the turnaround>-procedure/ — one attempt folder per outfit run."""
    return os.path.join(PLAYER, "outfits", name, "tries", f"{_record_date(turnaround)}-procedure")


def _log_cut(tdir, line):
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, "CUTS.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── the pieces every step is built from ─────────────────────────────────────────────────────────────

def snap_option(src, pitch, option, n=3):
    """Step 3: the whole render snapped on ONE grid, split into its `n` designs, design `option` (1-based)
    cropped and cleaned of magenta fringe. Returns (sprite, pixels the fringe clean-up changed).

    This is how CHOSEN_bronze.png (bronze-r3 at 13.00, design 2) and CHOSEN_blackant.png
    (ant-carapace-black4 at 10.25, design 2) were made — both reproduce byte for byte. Black-ant's needed
    the clean-up: two enclosed magenta pixels the border-flood key cannot reach.
    """
    pitch, snapped = C.snap_whole(src, pitch)
    m = snapped[..., 3] > 0
    cols = C.split_n(m, n)
    if len(cols) != n:
        raise SystemExit(f"{_rel(src)}: expected {n} designs side by side at grid {pitch}, found {len(cols)}")
    c0, c1 = cols[option - 1]
    raw = _crop(snapped[:, c0:c1])
    clean = defringe(raw)
    return clean, int((clean != raw).any(2).sum())


def cut_views(src, pitch):
    """Step 4: the turnaround snapped on ONE grid and split into front / side / back, each cropped to its own
    figure. Reproduces bronze-v2 (13.50) and blackant-v3 (10.25) byte for byte. The side view is kept as
    drawn; only the side WALK is mirrored, at cut time."""
    pitch, snapped = C.snap_whole(src, pitch)
    m = snapped[..., 3] > 0
    cols = C.split_n(m, 3)
    if len(cols) != 3:
        raise SystemExit(f"{_rel(src)}: expected 3 views side by side at grid {pitch}, found {len(cols)}")
    out = []
    for c0, c1 in cols:
        raw = _crop(C.drop_neighbour_bits(_crop(snapped[:, c0:c1])))
        clean = defringe(raw)
        out.append((clean, int((clean != raw).any(2).sum())))
    return out


def hand_height(front):
    """The hands' height in pixels for a character whose front view is `front` (an RGBA array)."""
    return round(_crop(front).shape[0] * HAND_RATIO)


def hands_template(front):
    """Step 6's first reference: the character's front view with five empty cyan boxes beside it.

    Rebuilt from the measured layout; it reproduces all three approved templates pixel for pixel
    (`verify`). The boxes are what make the hands come back at the character's own pixel density.
    """
    fig = _crop(front)
    fh, fw = fig.shape[:2]
    h = hand_height(front)
    bw = round(h * T_BOX_W)
    column = 5 * h + 4 * T_BOX_GAP
    W = T_MARGIN + fw + T_GAP + bw + T_MARGIN
    H = T_MARGIN + max(fh, column) + T_MARGIN
    img = Image.new("RGBA", (W, H), KEY)
    f = Image.fromarray(fig, "RGBA")
    img.paste(f, (T_MARGIN, T_MARGIN), f)
    d = ImageDraw.Draw(img)
    x0 = T_MARGIN + fw + T_GAP
    y0 = max(T_MARGIN, T_MARGIN + (fh - column) // 2)
    for k in range(5):
        y = y0 + k * (h + T_BOX_GAP)
        d.rectangle([x0, y, x0 + bw - 1, y + h - 1], outline=CYAN)
    return img, h


def as_sent(path):
    """What gen.py actually sends for this reference (the enlarged copy it saves as ref_N_<name>)."""
    im = Image.open(path).convert("RGBA")
    if max(im.size) < 400:
        im = im.resize((im.width * SEND_SCALE, im.height * SEND_SCALE), Image.NEAREST)
    return im


# ── grid candidates (step 3 onward: every cut needs its grid, and the detector alone is not reliable) ──

def _sat(a):
    s = np.zeros((a.shape[0] + 1, a.shape[1] + 1) + a.shape[2:])
    s[1:, 1:] = a.cumsum(0).cumsum(1)
    return s


def _box(s, y0, y1, x0, x1):
    return s[y1][:, x1] - s[y0][:, x1] - s[y1][:, x0] + s[y0][:, x0]


def cell_noise(src, lo=7.0, hi=24.0, step=0.05, cols=None):
    """How uneven each sampled cell is, for every candidate grid. Returns (pitches, noise).

    At the true grid (or a fraction of it) each cell's inner window sits inside one drawn block, so the noise
    is low. Tested on the 16 approved cuts: the lowest point is the chosen grid or within 0.05-0.2 of it for
    renders of whole figures, but on the hands renders it is HALF the grid (9.00 for 18.00) — so candidates
    always include the doubles, and the choice is made by eye on the sheet, as it always was.
    """
    rgb = np.asarray(Image.open(src).convert("RGB"), np.uint8)
    art = PE.key(rgb.astype(int))
    if cols is not None:
        keep = np.zeros_like(art)
        keep[:, cols[0]:cols[1]] = True
        art = art & keep
    rgba = np.dstack([rgb, (art * 255).astype(np.uint8)]).astype(float)
    ex, ey = PS.edge_energy(rgba)
    lit = rgba[..., :3] * art[..., None]
    S1, S2, SA = _sat(lit), _sat(lit ** 2), _sat(art.astype(float))
    H, W = art.shape
    ps = np.round(np.arange(lo, hi + 1e-9, step), 2)
    noise = []
    for p in ps:
        x0, y0 = PS._best_phase(ex, p), PS._best_phase(ey, p)
        cx = x0 + (np.arange(int((W - x0) / p)) + 0.5) * p
        cy = y0 + (np.arange(int((H - y0) / p)) + 0.5) * p
        xlo = np.clip(np.round(cx - 0.25 * p).astype(int), 0, W)
        xhi = np.clip(np.maximum(xlo + 1, np.round(cx + 0.25 * p).astype(int)), 0, W)
        ylo = np.clip(np.round(cy - 0.25 * p).astype(int), 0, H)
        yhi = np.clip(np.maximum(ylo + 1, np.round(cy + 0.25 * p).astype(int)), 0, H)
        area = ((yhi - ylo)[:, None] * (xhi - xlo)[None, :]).astype(float)
        on = _box(SA, ylo, yhi, xlo, xhi) >= 0.5 * area
        mean = _box(S1, ylo, yhi, xlo, xhi) / area[..., None]
        var = np.maximum(0, _box(S2, ylo, yhi, xlo, xhi) / area[..., None] - mean ** 2).mean(-1)
        noise.append(float(np.sqrt(var)[on].mean()) if on.any() else np.inf)
    return ps, np.array(noise)


def grid_candidates(ps, noise, n=3, sep=0.3):
    """The `n` quietest grids at least `sep` apart, plus the double of each (the hands case)."""
    picks = []
    for i in np.argsort(noise):
        if all(abs(ps[i] - q) >= sep for q in picks):
            picks.append(float(ps[i]))
        if len(picks) == n:
            break
    return sorted(set(picks + [round(2 * q, 2) for q in picks if 2 * q <= ps.max()]))


# ── commands ────────────────────────────────────────────────────────────────────────────────────────

def cmd_grids(a):
    """Render the candidates side by side so the true grid can be picked by eye."""
    src = os.path.join(EXPLORE, a.run, "result.png")
    rgb = np.asarray(Image.open(src).convert("RGB"), int)
    cols = None
    if a.option:
        cols = PE.split(PE.key(rgb), a.of)[a.option - 1]
    ps, noise = cell_noise(src, cols=cols)
    cands = sorted(set(grid_candidates(ps, noise) + [float(p) for p in (a.also or [])]))
    panels = []
    print(f"  {a.run}{f' design {a.option}' if a.option else ''}: grid candidates (lower noise = cleaner cells)")
    for p in cands:
        noise_p = noise[np.argmin(np.abs(ps - p))] if ps.min() <= p <= ps.max() else float("nan")
        if a.option:
            spr, _ = snap_option(src, p, a.option, a.of)
        else:
            spr = _crop(C.snap_whole(src, p)[1])
        scale = max(2, min(8, 480 // max(spr.shape[:2])))
        big = Image.fromarray(spr, "RGBA").resize((spr.shape[1] * scale, spr.shape[0] * scale), Image.NEAREST)
        plate = Image.new("RGB", big.size, RV.BG)
        plate.paste(big, (0, 0), big)
        label = f"{p:.2f}  {spr.shape[1]}x{spr.shape[0]}px  noise {noise_p:.1f}"
        panels.append((label, plate))
        print(f"    grid {p:6.2f}   {spr.shape[1]:3d} x {spr.shape[0]:3d} px   {_colours(spr):5d} colours   "
              f"noise {noise_p:5.1f}")
    sheet = RV.row(panels, note="The true grid: every block the same size, 1-px lines stay 1 px, no doubled "
                                "rows or columns. A double of the true grid loses detail; a fraction repeats it.")
    out = os.path.join(EXPLORE, a.run, f"GRIDS{f'_design{a.option}' if a.option else ''}.png")
    sheet.save(out)
    print(f"  sheet: {_c(out)}")


def cmd_pick(a):
    """Step 3: the owner's pick, converted to real pixels -> <name>-turnaround/CHOSEN_ref.png."""
    src = os.path.join(EXPLORE, a.explore_run, "result.png")
    option = a.option or _which_design(a.name, a.explore_run)
    spr, fixed = snap_option(src, a.pitch, option)
    run = a.run or f"{a.name}-turnaround"
    dst = os.path.join(EXPLORE, run, "CHOSEN_ref.png")
    how = _write_once(dst, Image.fromarray(spr, "RGBA"))
    print(f"  design {option} of {a.explore_run} at grid {a.pitch}: {spr.shape[1]}x{spr.shape[0]} px, "
          f"{_colours(spr)} colours" + (f", {fixed} magenta pixel(s) cleaned" if fixed else ""))
    print(f"  {how}: {_c(dst)}")
    print("  For scale: bronze 27x68, fire-ant 23x76, black-ant 34x89 (the bare base character is 25x62).")


def _which_design(name, run):
    """Which of the three designs the owner picked: find CHOSEN_<name>.png inside the render."""
    chosen = os.path.join(EXPLORE, run, f"CHOSEN_{name}.png")
    if not os.path.exists(chosen):
        raise SystemExit(f"no {_rel(chosen)} — say which design with --option")
    rgb = np.asarray(Image.open(os.path.join(EXPLORE, run, "result.png")).convert("RGB"), np.uint8)
    pick = np.asarray(Image.open(chosen).convert("RGB"), np.uint8)
    art = PE.key(rgb.astype(int))
    for k, (c0, c1) in enumerate(PE.split(art, 3), 1):
        ys, xs = np.where(art[:, c0:c1])
        crop = rgb[ys.min():ys.max() + 1, c0 + xs.min():c0 + xs.max() + 1]
        if crop.shape == pick.shape and np.array_equal(crop, pick):
            return k
    raise SystemExit(f"{_rel(chosen)} is not a crop of one of the three designs — say which with --option")


def cmd_views(a):
    """Step 4, free half: cut the turnaround into view_front / view_side / view_back."""
    run = a.run or f"{a.name}-turnaround"
    d = os.path.join(EXPLORE, run)
    views = cut_views(os.path.join(d, "result.png"), a.pitch)
    seed = _rgba(os.path.join(d, "CHOSEN_ref.png"))
    for view, (spr, fixed) in zip(VIEWS, views):
        dst = os.path.join(d, f"view_{view}.png")
        how = _write_once(dst, Image.fromarray(spr, "RGBA"))
        print(f"  view_{view}: {spr.shape[1]}x{spr.shape[0]} px" + (f", {fixed} magenta cleaned" if fixed else "")
              + f"  ({how})")
    hs = [v[0].shape[0] for v in views]
    print(f"  heights {hs} against the pick's {seed.shape[0]} — the three should agree within a pixel or two;"
          " reroll rather than rescale")


def cmd_cutwalk(a):
    """Step 5, free half: one direction's render -> <view>_1..4.png in the outfit's attempt folder."""
    turn = a.turnaround or f"{a.name}-turnaround"
    run = a.run or f"{a.name}-{a.view}walk"
    if a.view == "side" and a.faces is None:
        raise SystemExit("Look at the render and say which way the side frames face: --faces left|right.\n"
                         "  The frames must END UP facing right (gait's wrist maths assumes +x). All three approved\n"
                         "  side walks came back facing LEFT and were mirrored; copper's came back facing RIGHT.")
    mirror = a.view == "side" and a.faces == "left"
    tdir = _try_dir(a.name, turn)
    frames = os.path.join(tdir, "frames")
    pitch, w, h = C.cut_walk(os.path.join(EXPLORE, run, "result.png"), frames, a.view, pitch=a.pitch,
                             mirror=mirror)
    _log_cut(tdir, f"frames/{a.view}_1..4  from explore/{run}/result.png  grid {pitch}"
                   + ("  mirrored (drawn facing left)" if mirror else ""))
    ref = _crop(_rgba(os.path.join(EXPLORE, turn, f"view_{a.view}.png")))
    print(f"  {a.view}: 4 frames on a {w}x{h} canvas, grid {pitch}  (the turnaround's {a.view} view is "
          f"{ref.shape[0]} px tall)  -> {_c(frames)}")
    for problem in C.check_alternation(frames, a.view):
        print(f"  ⚠ {problem}")
    if a.view == "side":
        print("  The side cycle cannot be checked by numbers — look at it (which leg leads is carried by shading).")


def cmd_cuthands(a):
    """Step 6, free half: the hands column -> the five hands at exactly the walk's hand height."""
    turn = a.turnaround or f"{a.name}-turnaround"
    run = a.run or f"{a.name}-gauntlet"
    h = hand_height(_rgba(os.path.join(EXPLORE, turn, "view_front.png")))
    tdir = _try_dir(a.name, turn)
    hands = os.path.join(tdir, "gauntlet")
    pitch, out = C.cut_gauntlet_column(os.path.join(EXPLORE, run, "result.png"), hands, pitch=a.pitch, target_h=h)
    _log_cut(tdir, f"gauntlet/*  from explore/{run}/result.png  grid {pitch}  {h}px tall")
    print(f"  grid {pitch}: hands {h}px tall -> {_c(hands)}")
    for role, raw, w, hh in out:
        how = "as drawn" if raw == h else (f"{raw - h} row(s) of cuff trimmed" if raw > h
                                           else f"{h - raw} row(s) padded below the cuff")
        print(f"    {role:10s} {w}x{hh}  ({how})")


def _paid(dest, prompt, refs, size, go):
    """Show exactly what one paid call would send; send it only with --go."""
    out = os.path.join(PLAYER, dest)
    if os.path.exists(os.path.join(out, "result.png")):
        raise SystemExit(f"{dest}/ already has a result.png — a paid result is never overwritten.\n"
                         "  A reroll goes in a new folder: --run <name>-<step>-r2")
    G.check_clauses(prompt, dest)                  # refuse now, not after the owner has said yes
    print(f"\n  ONE PAID CALL — gpt-image-2, {size}, into {dest}/")
    for i, r in enumerate(refs, 1):
        im = Image.open(r)
        sent = as_sent(r)
        print(f"  reference {i}: {_c(r)}  ({im.width}x{im.height}, sent as {sent.width}x{sent.height})")
    print("  PROMPT:")
    for line in prompt.split("\n"):
        print(f"    {line}")
    if not go:
        print("\n  Nothing sent. Ask the owner; after his yes, run the same command with --go.")
        return False
    return OF.gen(dest, prompt, refs, size=size)


def cmd_turnaround(a):
    """Step 4, paid: three standing views from the pick."""
    run = a.run or f"{a.name}-turnaround"
    ref = os.path.join(EXPLORE, run, "CHOSEN_ref.png")
    if not os.path.exists(ref):
        raise SystemExit(f"no {_rel(ref)} — run `procedure.py pick {a.name} <explore run> --pitch P` first")
    _paid(f"explore/{run}", OF.TURNAROUND, [ref], TURNAROUND_SIZE, a.go)


def cmd_walk(a):
    """Step 5, paid: four walk frames in one direction, seeded from that view of the turnaround."""
    what, _ = _slots(a.name)
    turn = a.turnaround or f"{a.name}-turnaround"
    view = os.path.join(EXPLORE, turn, f"view_{a.view}.png")
    if not os.path.exists(view):
        raise SystemExit(f"no {_rel(view)} — run `procedure.py views {a.name} --pitch P` first")
    run = a.run or f"{a.name}-{a.view}walk"
    ref = os.path.join(EXPLORE, run, "CHOSEN_ref.png")
    _write_once(ref, Image.open(view).convert("RGBA"))
    _paid(f"explore/{run}", OF.walk_prompt(what, a.view), [ref], WALK_SIZE, a.go)


def cmd_hands(a):
    """Step 6, paid: the five hands, drawn beside the character so they share its pixel size."""
    what, glove = _slots(a.name)
    turn = a.turnaround or f"{a.name}-turnaround"
    front = os.path.join(EXPLORE, turn, "view_front.png")
    if not os.path.exists(front):
        raise SystemExit(f"no {_rel(front)} — run `procedure.py views {a.name} --pitch P` first")
    tmpl, h = hands_template(_rgba(front))
    run = a.run or f"{a.name}-gauntlet"
    boxes = os.path.join(EXPLORE, run, "REF_boxes.png")
    shapes = os.path.join(EXPLORE, run, "REF_shapes.png")
    _write_once(boxes, tmpl)
    _write_once(shapes, Image.open(HAND_SHAPES).convert("RGBA"))
    grid = 1400 / tmpl.height                     # the skill's rule of thumb, from the fire-ant run
    print(f"  hands must be {h}px ({_crop(_rgba(front)).shape[0]}px front view x {HAND_RATIO}); template "
          f"{tmpl.width}x{tmpl.height}. Rough prediction: grid ~{grid:.1f}, hands ~{200 / grid:.1f}px as drawn")
    _paid(f"explore/{run}", OF.hands_prompt(what, glove, h), [boxes, shapes], HANDS_SIZE, a.go)


# ── verify: the approved runs, reproduced with no calls ─────────────────────────────────────────────

# The approved outfits' runs and the grid each render was cut at. For the first three the grids were not written down;
# they were re-found on 2026-09-26 by cutting each recorded render at every grid in 0.01 steps and keeping the
# one that reproduces the committed files exactly. Each did, byte for byte, with today's cutter.
APPROVED = {
    "bronze": dict(what="bronze plate armour", glove="warm brown-gold bronze",   # not in outfits.OUTFITS
                   pick=("bronze-r3", 2, 13.0), turnaround=("bronze-v2-turnaround", 13.5),
                   side=("bronze-v2-sidewalk", 12.0), front=("bronze-v2-frontwalk", 12.75),
                   back=("bronze-v2-backwalk", 11.5), hands=("bronze-v2-gauntlet", 18.0)),
    "blackant": dict(what=OF.OUTFITS["blackant"][0], glove=OF.OUTFITS["blackant"][3],
                     pick=("ant-carapace-black4", 2, 10.25), turnaround=("blackant-v3-turnaround", 10.25),
                     side=("blackant-v3-sidewalk", 8.75), front=("blackant-v3-frontwalk-r2", 10.0),
                     back=("blackant-v3-backwalk-r2", 10.25), hands=("blackant-v3-gauntlet", 15.5)),
    "fireant": dict(what=OF.OUTFITS["fireant"][0], glove=OF.OUTFITS["fireant"][3],
                    pick=None, turnaround=("fireant-v2-turnaround", None),
                    side=("fireant-sidewalk", 9.7), front=("fireant-frontwalk-r4", 12.25),
                    back=("fireant-backwalk-r4", 12.0), hands=("fireant-gauntlet-tall", 18.5)),
    # 2026-09-26 — the first outfit made entirely with these commands. Its side walk came back facing RIGHT
    # (the three above all faced left and were mirrored), hence the third element.
    "copper": dict(what=OF.OUTFITS["copper"][0], glove=OF.OUTFITS["copper"][3],
                   pick=("copper-r3", 1, 13.35), turnaround=("copper-turnaround", 14.03),
                   side=("copper-sidewalk", 10.7, "right"), front=("copper-frontwalk", 13.3),
                   back=("copper-backwalk", 10.7), hands=("copper-gauntlet", 19.7)),
}

# Not reproducible from the records, and why. Listed so they are never mistaken for a regression.
KNOWN = [
    "fire-ant's pick and turnaround views: fire-ant was the research run (the tip-* and fireant-gen* runs of "
    "2026-08-14/15); its references were made before this method settled and match no recorded render.",
    "fire-ant's hand shapes: its run sent the same five shapes in fire-ant's own colours (REF_shapes_native.png).",
    "fire-ant's walk references: its side walk was seeded from a 22x75 figure, not the turnaround's 22x76 side view.",
    "the rerolled walks — fire-ant front/back r4, black-ant front/back r2 — were CORRECTION calls: the first roll's "
    "four frames as the reference and a prompt listing what to fix. Their cuts are checked; their prompts are not "
    "a template. (The black-ant correction prompts call it 'fire-ant carapace armour' — a copy-paste slip at the time.)",
    "the camera-facing walk prompts differ from the August records in one sentence: the knee lift, changed to "
    "MEDIUM-HIGH on the owner's 2026-08-18 note. Checked as exactly that difference.",
]

# The knee sentence the August walks were made with, before the owner's 2026-08-18 change.
OLD_KNEE = ("Lift the knee HIGH: the raised knee should come up clearly in front of the body and sit visibly "
            "higher than the planted knee, and the raised foot well clear of the ground.")


def cmd_verify(a):
    import tempfile
    failures = []

    def check(ok, what, detail=""):
        print(f"  {'ok  ' if ok else 'FAIL'}  {what}" + (f"  — {detail}" if detail and not ok else ""))
        if not ok:
            failures.append(what)

    print("PROMPTS")
    turns = [v["turnaround"][0] for v in APPROVED.values()]
    check(all(_record_prompt(r) == OF.TURNAROUND for r in turns), "turnaround = the text all three approved runs sent")
    for name, v in APPROVED.items():
        run = v["hands"][0]
        h = hand_height(_rgba(os.path.join(EXPLORE, v["turnaround"][0], "view_front.png")))
        check(_record_prompt(run) == OF.hands_prompt(v["what"], v["glove"], h),
              f"hands prompt, {name} ({h}px) = {run}")
        for view in VIEWS:
            if name == "fireant" or (name == "blackant" and view != "side"):
                continue                               # corrections (see KNOWN); black-ant's first rolls below
            rec, now = _record_prompt(v[view][0]), OF.walk_prompt(v["what"], view)
            ok = rec == now if view == "side" else rec.replace(OLD_KNEE, OF.WALK_KNEE) == now
            check(ok, f"walk prompt, {name} {view} = {v[view][0]}" + (" (+ the knee change)" if OLD_KNEE in rec else ""))
    for view in ("front", "back"):
        run = f"blackant-v3-{view}walk"                # black-ant's first rolls used the template
        check(_record_prompt(run).replace(OLD_KNEE, OF.WALK_KNEE) == OF.walk_prompt(APPROVED["blackant"]["what"], view),
              f"walk prompt, blackant {view} = {run} (+ the knee change)")
    try:
        G.check_clauses(OF.TURNAROUND, "explore/x-turnaround")
        refused = False
        try:
            G.check_clauses(OF.TURNAROUND.replace("exact right profile", "right profile"), "explore/x-turnaround")
        except SystemExit:
            refused = True
        check(refused, "gen.py accepts the turnaround exactly as approved, and refuses it edited")
    except SystemExit:
        check(False, "gen.py accepts the approved turnaround")

    print("REFERENCES")
    for name, v in APPROVED.items():
        turn = v["turnaround"][0]
        d = os.path.join(EXPLORE, v["hands"][0])
        tmpl, _ = hands_template(_rgba(os.path.join(EXPLORE, turn, "view_front.png")))
        check(np.array_equal(np.asarray(tmpl), _rgba(os.path.join(d, "REF_boxes.png"))),
              f"hands template, {name} = {v['hands'][0]}/REF_boxes.png")
        runs = ([turn] + [v[view][0] for view in VIEWS] + [v["hands"][0]]
                + ([f"blackant-v3-{w}walk" for w in ("front", "back")] if name == "blackant" else []))
        for run in runs:
            for f in sorted(os.listdir(os.path.join(EXPLORE, run))):
                m = re.match(r"ref_\d+_(.+)$", f)
                if m and os.path.exists(os.path.join(EXPLORE, run, m.group(1))):
                    sent = np.asarray(as_sent(os.path.join(EXPLORE, run, m.group(1))))
                    check(np.array_equal(sent, _rgba(os.path.join(EXPLORE, run, f))), f"sent as recorded: {run}/{f}")
        for view in VIEWS:
            run = f"blackant-v3-{view}walk" if name == "blackant" else v[view][0]
            if name == "fireant":
                continue                               # seeded before the method settled (see KNOWN)
            check(np.array_equal(_rgba(os.path.join(EXPLORE, run, "CHOSEN_ref.png")),
                                 _rgba(os.path.join(EXPLORE, turn, f"view_{view}.png"))),
                  f"walk reference, {name} {view} = the turnaround's view_{view}")
    for run in ("bronze-v2-gauntlet", "blackant-v3-gauntlet", "copper-gauntlet"):
        check(open(os.path.join(EXPLORE, run, "REF_shapes.png"), "rb").read() == open(HAND_SHAPES, "rb").read(),
              f"hand shapes = {run}/REF_shapes.png")

    print("CUTS (the approved renders at their grids -> the committed files)")
    if a.quick:
        print("  skipped (--quick)")
    else:
        tmp = tempfile.mkdtemp()
        for name, v in APPROVED.items():
            if v["pick"]:
                run, option, pitch = v["pick"]
                spr, fixed = snap_option(os.path.join(EXPLORE, run, "result.png"), pitch, option)
                check(np.array_equal(spr, _rgba(os.path.join(EXPLORE, v["turnaround"][0], "CHOSEN_ref.png"))),
                      f"pick, {name}: {run} design {option} at {pitch}"
                      + (f" ({fixed} magenta pixel(s) cleaned, as by hand at the time)" if fixed else ""))
            turn, pitch = v["turnaround"]
            if pitch:
                views = cut_views(os.path.join(EXPLORE, turn, "result.png"), pitch)
                check(all(np.array_equal(s, _rgba(os.path.join(EXPLORE, turn, f"view_{w}.png")))
                          for w, (s, _) in zip(VIEWS, views)), f"views, {name}: {turn} at {pitch}")
            for view in VIEWS:
                run, pitch, *faces = v[view]
                mirror = view == "side" and (faces or ["left"])[0] == "left"
                C.cut_walk(os.path.join(EXPLORE, run, "result.png"), tmp, view, pitch=pitch, mirror=mirror)
                ok = all(np.array_equal(_rgba(os.path.join(tmp, f"{view}_{i}.png")),
                                        _rgba(os.path.join(PLAYER, "outfits", name, "frames", f"{view}_{i}.png")))
                         for i in (1, 2, 3, 4))
                check(ok, f"walk, {name} {view}: {run} at {pitch}")
            run, pitch = v["hands"]
            h = hand_height(_rgba(os.path.join(EXPLORE, v["turnaround"][0], "view_front.png")))
            C.cut_gauntlet_column(os.path.join(EXPLORE, run, "result.png"), tmp, pitch=pitch, target_h=h)
            ok = all(np.array_equal(_rgba(os.path.join(tmp, f"{r}.png")),
                                    _rgba(os.path.join(PLAYER, "outfits", name, "gauntlet", f"{r}.png")))
                     for r in O.HAND_ROLES)
            check(ok, f"hands, {name}: {run} at {pitch}, {h}px")

    print("KNOWN, NOT A REGRESSION")
    for k in KNOWN:
        print(f"  -  {k}")
    print(f"\n{'ALL REPRODUCED' if not failures else f'{len(failures)} FAILED'} — no image calls were made.")
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("grids", help="step 3+: candidate grids for a render, as a sheet to judge by eye")
    s.add_argument("run", help="explore folder, e.g. copper-r3")
    s.add_argument("--option", type=int, help="only this design (1-3) of a three-design render")
    s.add_argument("--of", type=int, default=3, help="how many figures the render holds (default 3)")
    s.add_argument("--also", type=float, nargs="*", help="extra grids to show")

    s = sub.add_parser("pick", help="step 3: the owner's pick in real pixels -> <name>-turnaround/CHOSEN_ref.png")
    s.add_argument("name")
    s.add_argument("explore_run", help="the explore folder holding CHOSEN_<name>.png, e.g. copper-r3")
    s.add_argument("--pitch", type=float, required=True)
    s.add_argument("--option", type=int, help="which design (1-3); default: found from CHOSEN_<name>.png")
    s.add_argument("--run", help="turnaround folder (default <name>-turnaround)")

    for cmd, what in (("turnaround", "step 4, PAID: front / side / back from the pick"),
                      ("walk", "step 5, PAID: one direction's four walk frames"),
                      ("hands", "step 6, PAID: the five hands, beside the character")):
        s = sub.add_parser(cmd, help=what)
        s.add_argument("name")
        if cmd == "walk":
            s.add_argument("view", choices=VIEWS)
        s.add_argument("--run", help="the run folder under explore/ (default <name>-<step>)")
        if cmd != "turnaround":
            s.add_argument("--turnaround", help="turnaround folder (default <name>-turnaround)")
        s.add_argument("--go", action="store_true", help="SPEND — only after the owner has said yes")

    for cmd, what in (("views", "step 4, free: cut the turnaround into three views"),
                      ("cutwalk", "step 5, free: cut one direction into four frames"),
                      ("cuthands", "step 6, free: cut the five hands")):
        s = sub.add_parser(cmd, help=what)
        s.add_argument("name")
        if cmd == "cutwalk":
            s.add_argument("view", choices=VIEWS)
        s.add_argument("--pitch", type=float, required=True)
        s.add_argument("--run", help="the run folder under explore/")
        if cmd == "cutwalk":
            s.add_argument("--faces", choices=("left", "right"),
                           help="side only: which way the render's figures face (left ones get mirrored)")
        if cmd != "views":
            s.add_argument("--turnaround", help="turnaround folder (default <name>-turnaround)")

    s = sub.add_parser("verify", help="reproduce the approved runs with no calls")
    s.add_argument("--quick", action="store_true", help="prompts and references only, skip the cuts")

    a = ap.parse_args()
    return {"grids": cmd_grids, "pick": cmd_pick, "turnaround": cmd_turnaround, "views": cmd_views,
            "walk": cmd_walk, "cutwalk": cmd_cutwalk, "hands": cmd_hands, "cuthands": cmd_cuthands,
            "verify": cmd_verify}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
