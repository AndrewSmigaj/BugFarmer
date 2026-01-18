# BugFarmer: GPT-Image → ComfyUI Sprite Cleanup Pipeline (Master Document)

**FINAL MASTER PIPELINE (Transparent Background Edition)**

This is the exact document Claude should store and treat as the authoritative pipeline.

---

## Overview

GPT-image-1 now outputs:
- Transparent backgrounds
- Large canvas
- Sprite centered with padding

Therefore, your cleanup pipeline must:
1. Trim the transparent padding
2. Quantize / flatten colors
3. Resize with nearest-neighbor
4. Enforce your target pixel grid
5. Optional morphology cleanup
6. Optional palette mapping

**No magenta conversion.**
**No background removal.**
**No cleaning of white backgrounds.**

---

## Pipeline Summary

```
LoadImage
→ AlphaCrop (trim transparent padding)
→ Posterize / Quantize
→ Resize (Nearest → Intermediate)
→ Resize (Nearest → Final Size)
→ Optional Morphology
→ Optional Palette Mapping
→ SaveImage
```

That's it.

---

## Inputs (Claude Must Provide)

| Parameter | Meaning |
|-----------|---------|
| `INPUT_IMAGE_PATH` | Path to GPT-image-1 PNG (transparent background) |
| `TARGET_WIDTH` | Final sprite width in pixels (e.g. 8, 16, 32) |
| `TARGET_HEIGHT` | Final sprite height in pixels (e.g. 8, 24, 48) |
| `INTERMEDIATE_SCALE` | Scaling factor before final downscale (recommended: 4×) |
| `PALETTE_PATH` (optional) | Path to BugFarmer palette image or JSON |
| `CLEANUP_MODE` (optional) | "none", "open", "open_close" |
| `OUTPUT_PREFIX` | Filename prefix for saved PNG |

---

## Exact Node Setup (Claude-ready)

### 1. LoadImage

```yaml
class_type: LoadImage
inputs:
  image: INPUT_IMAGE_PATH
```

---

### 2. Trim Transparent Padding (CRITICAL)

This is the step that isolates the sprite properly.

**Node: AlphaCrop**

```yaml
class_type: AlphaCrop
inputs:
  image: ["load_image", "IMAGE"]
  padding_left: 1
  padding_right: 1
  padding_top: 1
  padding_bottom: 1
```

**Why padding = 1?**
- Prevents cutting off edge pixels
- Leaves room for anti-alias cleanup
- Keeps silhouette intact

(Claude can adjust if needed.)

---

### 3. Posterize / Quantize

Either node is fine:

**Posterize:**
```yaml
class_type: ImagePosterize
inputs:
  image: ["trim", "IMAGE"]
  levels: 4
  dither: none
```

**OR Quantize:**
```yaml
class_type: ImageQuantize
inputs:
  image: ["trim", "IMAGE"]
  colors: 4
  dither: none
```

---

### 4. Resize — Intermediate (Soft Cleanup)

Scale by 4× for best silhouette preservation.

```yaml
class_type: ResizeImage
inputs:
  image: ["posterize", "IMAGE"]
  width: TARGET_WIDTH * 4
  height: TARGET_HEIGHT * 4
  method: nearest
```

---

### 5. Resize — Final Sprite Size

```yaml
class_type: ResizeImage
inputs:
  image: ["resize_intermediate", "IMAGE"]
  width: TARGET_WIDTH
  height: TARGET_HEIGHT
  method: nearest
```

---

### 6. Morphology (Optional)

```yaml
class_type: MorphologyFilter
inputs:
  image: ["resize_final", "IMAGE"]
  mode: open
  kernel_size: 1
```

Optional second pass:
- `mode: close`

**Never use kernel > 1.**

---

### 7. Palette Mapping (Optional)

(If installed)

```yaml
class_type: PaletteMapper
inputs:
  image: ["morph", "IMAGE"]
  palette: PALETTE_PATH
```

---

### 8. SaveImage

```yaml
class_type: SaveImage
inputs:
  image: ["morph", "IMAGE"]
  filename_prefix: OUTPUT_PREFIX
```

---

## Complete ComfyUI JSON (Claude-usable)

```json
{
  "prompt": {
    "load_image": {
      "class_type": "LoadImage",
      "inputs": {
        "image": "INPUT_IMAGE_PATH"
      }
    },

    "trim": {
      "class_type": "AlphaCrop",
      "inputs": {
        "image": ["load_image", "IMAGE"],
        "padding_left": 1,
        "padding_right": 1,
        "padding_top": 1,
        "padding_bottom": 1
      }
    },

    "posterize": {
      "class_type": "ImagePosterize",
      "inputs": {
        "image": ["trim", "IMAGE"],
        "levels": 4,
        "dither": "none"
      }
    },

    "resize_intermediate": {
      "class_type": "ResizeImage",
      "inputs": {
        "image": ["posterize", "IMAGE"],
        "width": "TARGET_WIDTH * 4",
        "height": "TARGET_HEIGHT * 4",
        "method": "nearest"
      }
    },

    "resize_final": {
      "class_type": "ResizeImage",
      "inputs": {
        "image": ["resize_intermediate", "IMAGE"],
        "width": "TARGET_WIDTH",
        "height": "TARGET_HEIGHT",
        "method": "nearest"
      }
    },

    "morph": {
      "class_type": "MorphologyFilter",
      "inputs": {
        "image": ["resize_final", "IMAGE"],
        "mode": "open",
        "kernel_size": 1
      }
    },

    "save_image": {
      "class_type": "SaveImage",
      "inputs": {
        "image": ["morph", "IMAGE"],
        "filename_prefix": "OUTPUT_PREFIX"
      }
    }
  }
}
```

Claude substitutes:
- `INPUT_IMAGE_PATH`
- `TARGET_WIDTH`
- `TARGET_HEIGHT`
- `INTERMEDIATE_SCALE` (used in width/height calculations)
- `OUTPUT_PREFIX`

If morphology or palette mapping is not needed, Claude simply removes those nodes.

---

## What ComfyUI Does NOT Decide

ComfyUI does not decide:
- Sprite size
- Footprint
- Pivot
- Category (bug / furniture / tree)
- Anchoring
- Palette choice

All of that lives upstream (Claude + DB).
