# Aseprite — the little tutorial for cutting armor pieces

## FIRST: your #1 problem — "how do I export only some layers?"
The trick is the command you use AND hiding (not deleting) layers:

1. **Hide** the layers you DON'T want in the output — click the **eye icon** next to each layer
   in the Timeline (bottom of the screen; press **Tab** if you don't see it) so the eye turns off.
2. **File > Save Copy As** → pick **PNG** → save it.
   - "Save Copy As" writes a flattened PNG of ONLY the visible layers, and does **not** change or
     close your working file. So no deleting layers, no undo, no reopening. Just hide → Save Copy As,
     un-hide → hide the next → Save Copy As again.
   - Use "Save Copy As", NOT "Export Sprite Sheet" (that one's for animations and ignores you).
3. Gotcha: if a layer is named **"Background"** (italic), it's always opaque + always shows.
   Right-click it → **"Layer from Background"** to make it a normal, hide-able, transparent layer.

That's the whole export answer. Everything below is the workflow + handy stuff.

## THE WORKFLOW (cut each armor piece onto its own layer — non-destructive)
1. Open `CURRENT/copper_suit.png`.
2. Bring in the body as a guide: open `CURRENT/base_bald.png` in another tab → **Ctrl+A** (select all)
   → **Ctrl+C** → back to the copper tab → **new layer** → **Ctrl+V** (pastes in place; they're the
   same size so it lines up). Drag that base layer to the BOTTOM and set its **Opacity ~50%** so you
   can see the body under the armor while you work. (Hide it before exporting.)
3. Clean up / extend: draw missing armor pixels with the **Pencil (B)**, remove stray bits with the
   **Eraser (E)**. Pick a color off the art with **Alt+click**.
4. Cut a piece to its own layer: on the copper layer, **select** just that piece (Lasso **Q** or
   Magic Wand **W**), **Ctrl+C**, make a **new layer**, **Ctrl+V**. Rename the layer (double-click it)
   to `helmet`. Repeat for `chest`, `legs`, `boots`.
5. Export each piece: hide every layer except that one piece → **File > Save Copy As** →
   `pieces/copper_helmet.png` (in this folder; etc.). Done.

Cut-out pieces like this are all I need — no separate white mask required. (A white mask works too if
you ever prefer it; the cost to me is the same. Your choice, not a rule.)

## SHORTCUTS worth memorizing (that's most of what you need)
- **B** pencil · **E** eraser · **G** paint bucket · **Alt+click** eyedropper (pick a color)
- **M** rectangle select · **Q** lasso select · **W** magic wand (select by color) · **V** move
- **Ctrl+A** select all · **Ctrl+D** deselect · **Delete** clears the selection
- **Ctrl+Z** undo · **Ctrl+Shift+Z** redo · **Ctrl+C / Ctrl+V** copy / paste (pastes in place)
- **Mouse wheel** zoom · **Space+drag** (or middle-mouse-drag) pan

## HANDY features for clean pixel work
- **Pixel-perfect**: with the Pencil selected, tick "Pixel-perfect" in the options bar at the top —
  it stops the ugly double-pixels on diagonal strokes.
- **Magic Wand (W)** + a color: click a colored area to select all of it (great for grabbing a whole
  armor piece at once). Toggle "Contiguous" in the top bar (on = only the connected blob).
- **Layer opacity + hiding** (the eye icon) is your main tool — you work with the base visible as a
  guide, then hide it to export.
- Zoom WAY in (300–800%) — these sprites are tiny (real pixel art), so you place pixels one at a time.

## What's worth you learning overall (mostly cleanup)
Pencil, eraser, eyedropper, the 3 selection tools, layers (hide/opacity/new), and Save Copy As.
That's ~90% of what our art cleanup needs. I do generation + the pipeline; you do the eye-and-judgment
cleanup where a human beats me iterating.
