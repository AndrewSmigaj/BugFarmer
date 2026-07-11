I'll run several searches in parallel to find the best sources.

---

The pixie.haus "Engineering Cohesion" article is directly on-point. Let me deep-read the key sources and run a couple more searches.

---

Let me deep-read more sources: the CIELAB/median-cut caveat, the AI pixel art fix article, OpenGameArt color ramps, and the zenquant tool.

---

Let me retry the CIELAB source and get the Aseprite indexed-color remap workflow.

---

I have deep-read six full sources plus supporting search syntheses. Compiling the findings now.

---

# Research: Making independently-generated AI sprites cohere into one art-directed world

I deep-read 6 full sources (pixie.haus cohesion article, Cage's Corner gradient-map tutorial, QWE "AI Pixel Art Is Broken", OpenGameArt color-ramps thread, zenquant quantizer, Aseprite palette docs) plus color-quantization and light-direction search syntheses. The 30fps.net median-cut/Lab article kept returning 403 on fetch, so I cite only its verbatim search-surfaced conclusion.

## 1. SOURCE TABLE

| URL | Technique | Concrete algorithm / tool | Fit for our post-gen pipeline + risk |
|---|---|---|---|
| [pixie.haus — Engineering Cohesion](https://pixie.haus/articles/engineering-cohesion-the-science-of-art-direction-in-ai-pixel-art) | **Lospec palette clamping**; prompt anchoring (80/20 static/variable); **seed locking**; image-to-image scaffolding | Force every output pixel to snap to a curated 8- or 16-color hex list; lock a static prompt block `[Perspective][Style Limiters][Outline Rules][Lighting/Shading Type]`; reuse a fixed seed integer so the model's "brushstroke" is identical across subjects; use a base asset as I2I template to hold scale/grid/silhouette | Directly maps to our flow. Palette clamp = our post-pass. Seed-lock + anchor are *generation-side* levers we don't yet use — cheap, high cohesion. Risk: clamp to too few colors muddies material distinction; anchor over-constrains variety |
| [Cage's Corner — Gradient maps](http://ccorner.duke4.net/tutorials-index/adobe-photoshop/colorizing-and-remapping-with-gradient-maps/) | **Gradient-map recoloring** (luminance → curated ramp) | Convert sprite to grayscale luminance; map black→darkest ramp color, white→lightest, sample mids at 1/4, 1/2, 3/4 into color stops; apply as non-destructive layer | Ties every asset to ONE color logic (hue-shifted shadows/highlights baked in). Risk it names explicitly: **saturated colors read as wrong luminance** (neon blue maps dark) needing stop repositioning; **banding** if smoothness too low; **flattens material hue variety** — everything becomes one ramp's tint |
| [OpenGameArt — Insights about color ramps](https://opengameart.org/forumtopic/some-insights-about-pixel-art-color-ramps) | **Luminosity-first ramps + hue-shifting** | Sort ramp strictly by luminosity, sacrifice hue accuracy for luminosity accuracy; DawnBringer-style design: bright→yellowish, dark→purplish so any ramp "just works"; on palette limits, pick next-closest color then sort by luminosity | Validates building our master palette as **luminosity-sorted hue-shifted ramps**, which is exactly what a gradient-map/remap needs to preserve form. Risk: none for us — it's the design principle behind the whole post-pass |
| [QWE — AI Pixel Art Is Broken](https://www.qwe.edu.pl/tutorial/create-pixel-art-with-ai-tools/) | Grid enforcement, **palette alignment**, edge hardening, one light direction | "Pixel It" rebuilds hard-edged grid; prompt "no dithering / hard edges"; align colors to palette in Aseprite; pick one light dir (top-left) and lock outline rules *before batch* | Confirms lock-lighting-and-outline-before-batch and align-to-palette-after. Risk it flags: AI "doesn't understand constraints," so post-processing (not prompting) must be the enforcer — supports our post-pass approach |
| [imazen/zenquant](https://github.com/imazen/zenquant) | **Perceptual quantization + shared-palette remap + adaptive dither** | OKLab histogram → median cut → k-means refine with butteraugli-style adaptive-quant weights → luminance sort → adaptive Floyd–Steinberg. `build_palette_rgba()` builds ONE palette from many frames; `shared.remap_rgba()` remaps every frame to it | This is the *modern reference implementation* of "build one shared palette, remap everything to it." Directly the algorithm we'd want for a global master palette across the whole sprite library. Risk: it's a Rust lib (integration cost); dithering on tiny sprites can add noise |
| [Aseprite — Palettes & color management (DeepWiki)](https://deepwiki.com/aseprite/aseprite/4.5-palettes-and-color-management) | **Indexed color + Remap** | Indexed mode: pixel = index into palette; `Remap` class maps old→new indices, `remap_image()` applies; sort palette by hue/sat/brightness; nearest-color best-fit on palette apply | Confirms the indexed-color + remap workflow is standard and scriptable. Establishes that a locked master palette + per-sprite remap is a first-class operation. Risk: DeepWiki excerpt doesn't expose the exact match color space |
| [Color-quantization synthesis + 30fps.net (verbatim)](https://30fps.net/pages/median-cut-lab-problem/) | **Perceptual-space pixel MAPPING** | Median cut / octree / Wu's split RGB boxes; CIELAB Euclidean ≈ perceptual distance. Key finding: *"It seems more important to do pixel mapping in a perceptual space than to change the space in which the median cut is done in."* | Load-bearing for our recipe: whatever builds the palette, do the **nearest-color remap in OKLab/CIELAB**, not RGB, or hues snap wrong. Low cost (a color-space convert). Risk: negligible |

## 2. Recommended POST-PASS COHESION recipe (ordered, per sprite)

Run this after gpt-image-1 generation, replacing the current *independent* per-sprite k-means:

1. **Build a single MASTER PALETTE once** (offline, not per sprite). Sample a representative set of generated + any hand-authored anchor sprites, quantize in **OKLab** (zenquant-style: histogram → median cut → k-means refine), then hand-curate into **luminosity-sorted, hue-shifted ramps** (dark→purplish, light→yellowish per OpenGameArt/DawnBringer). This is the one palette the whole world shares. Store as a Lospec-style `.gpl`/hex list.
2. **Normalize light direction BEFORE anything else** — decide top / top-left, and detect+reject or flip sprites lit from the wrong side. This must be a *generation-side* lock (static prompt anchor `[Lighting: top-left]` + seed lock per pixie.haus) because a post-pass cannot invent shadow geometry it wasn't given. Flag off-direction sprites for regen, don't silently remap.
3. **Luminance-preserving remap to the master palette.** For each generated sprite: for every pixel, find nearest master-palette color **in OKLab/CIELAB space** (30fps: pixel-mapping perceptual space is what matters). This is the core cohesion step — it collapses every sprite's private palette onto the shared ramp set.
4. **Optional per-sprite gradient-map pass** (only if step 3 still leaves hue clash): map sprite luminance through the *matching material ramp* from the master palette. Use sparingly — it enforces cohesion hardest but flattens material hue variety.
5. **Outline normalization** to the chosen house rule (single dark selective outline vs. colored vs. none) — collapse near-black edge pixels to the one designated outline color from the master palette.
6. **Nearest-scale downsample** (existing `pixelclean.py` step) last, so remap operates on more color information before the grid is hardened.
7. **Verify:** render the whole catalog preview grid and eyeball cohesion against an anchor sprite (the existing `previews/catalog/` grids are the right harness).

Key structural change vs. today: **stop running k-means independently per sprite** (that is precisely what gives every sprite its own palette). Build the palette once globally, remap everything to it.

## 3. Single highest-leverage technique

**Global shared-master-palette remap (indexed-color lock), with the nearest-color match done in a perceptual space (OKLab/CIELAB).**

Why: our stated failure mode is "every sprite has its own palette." A gradient map, outline rules, and light direction all help, but the palette *is* the disconnection — the human brain reads an object's color collectively across its shades ([OpenGameArt](https://opengameart.org/forumtopic/some-insights-about-pixel-art-color-ramps)), so forcing every sprite onto one luminosity-sorted, hue-shifted ramp set makes disparate assets share the same color DNA in a single pass. It is also the cheapest to bolt onto our existing quantize step (swap per-sprite k-means for build-once-palette + `remap`, à la zenquant's `build_palette_rgba` → `remap_rgba`), and it is non-destructive to silhouette/detail. Palette clamping is independently the technique the AI-cohesion article ([pixie.haus](https://pixie.haus/articles/engineering-cohesion-the-science-of-art-direction-in-ai-pixel-art)) and the AI-fix article ([QWE](https://www.qwe.edu.pl/tutorial/create-pixel-art-with-ai-tools/)) both name as the strongest lever. The one non-obvious detail: do the *mapping* in OKLab, not RGB, or hues snap to the wrong ramp ([30fps.net](https://30fps.net/pages/median-cut-lab-problem/)).

## 4. Open questions — genuine ART-DIRECTION TASTE calls (not research-answerable)

1. **Master palette size.** 8, 16, 32, or a ~48-color multi-ramp master? Smaller = more cohesion but muddier materials (wood vs. stone vs. foliage risk collapsing); larger = safer materials, weaker unification. Research says "luminosity-sorted ramps"; how many ramps is taste.
2. **Gradient-map: yes or no as a standard step?** It is the strongest cohesion lever but explicitly flattens material hue variety. Do we want the whole world tied to one ramp logic (stylized, unified) or preserve per-material local color (naturalistic, looser)?
3. **Outline house rule.** Single dark selective outline vs. hue-matched colored outlines vs. no outline. Pure cohesion/taste decision with no research-correct answer.
4. **Detail-density / dithering target.** Whether to allow dithering at all (it can add cohesion via shared texture, or read as noise on tiny sprites), and what pixel scale / detail budget every asset must hit.
5. **Light direction: top vs. top-left.** Convention says top-left, but a strict top-down farming game may prefer straight-top lighting. Owner call.
6. **How aggressively to reject vs. rescue off-model sprites** — regenerate wrong-light sprites (slow, API cost) vs. accept a remap that can't fix shadow geometry.

Sources: [pixie.haus](https://pixie.haus/articles/engineering-cohesion-the-science-of-art-direction-in-ai-pixel-art) · [Cage's Corner](http://ccorner.duke4.net/tutorials-index/adobe-photoshop/colorizing-and-remapping-with-gradient-maps/) · [OpenGameArt ramps](https://opengameart.org/forumtopic/some-insights-about-pixel-art-color-ramps) · [QWE AI pixel art](https://www.qwe.edu.pl/tutorial/create-pixel-art-with-ai-tools/) · [zenquant](https://github.com/imazen/zenquant) · [Aseprite palettes](https://deepwiki.com/aseprite/aseprite/4.5-palettes-and-color-management) · [30fps median-cut/Lab](https://30fps.net/pages/median-cut-lab-problem/)