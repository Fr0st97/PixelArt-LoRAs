# Post-processing: from the generated image to game sprites

A generated image is a large picture of a small game sprite: every game pixel is drawn as a square block of
image pixels (the LoRA's pixel scale, see [loras.md](loras.md)), on a plain gray background. Post-processing
turns it into transparent PNG sprites at game size.

## The tool

`tools/postprocess.py` does all steps below for one run of one LoRA. It needs Python 3.10+ with
`pip install pillow numpy scipy`.

```
python tools/postprocess.py <lora> <folder with the PNG files> <output folder> [--sizes 64,48,32,32fit]
python tools/postprocess.py --list
```

Example: `python tools/postprocess.py flora raw/flora-trees-1 sprites/flora-trees-1`.

Output, with a transparent background:

- most LoRAs: one folder per size (`64x64/`, `48on64-sharp05/`, `48on64-sharp10/`, `32x32-sharp05/`,
  `32x32-sharp10/`, `32x32-fit/`), files named `<image name><cell>.png`, cell `a`-`d` for sheets;
- ground: `32x32/<image name>/<tile>.png`, the 16 tiles of one set;
- walk cycles: `<image name>/<size folder>/<direction>-<frame>.png`, directions `south`, `north`, `east`, `west`,
  frame `0` idle, `1` and `2` walking. East and west are made by transposition (below). Next to the frames, two
  sprite sheets in the usual game client layout, one row, directions north, east, south, west: `idle.png`
  (4×1, the idle frame of each direction) and `walk.png` (8×1, the 2 walk frames of each direction).
  A figure larger than 64×64 (large monsters) is saved in `96x96/` on a 96×96 canvas, full size only.

An image that does not fit its layout (e.g. an object bigger than its cell) is skipped with the reason; the others
are processed. `--sizes` replaces the default sizes of the LoRA (table below).

## Steps

1. **Find the pixel grid.** Try block sizes 4, 8, 16, 32 and offsets; pick the size where color jumps line up
   with the block borders best (the smallest size within 75% of the best score). For the 3×2 walk sheets the size
   is known from the format: width / (64 × 3) = 8. For walls it is 6 with an offset of 2.
2. **Read one color per block.** Take the median of the center of each block (from 1/4 to 3/4 of its width), so
   soft edges between blocks do not leak in.
3. **Remove the background.** Pixels with the background color (±8), connected to the image border, become
   transparent. Closed holes count as background only inside a dark outline. A thin gray halo around the object is
   removed too (up to 3 passes), and a gray rim outside a black outline.
4. **Cut into sprites.** Each LoRA has its own layout:

| LoRA | Cut | Sizes produced |
|---|---|---|
| flora, nature | one object → one 64×64 sprite | 64, 48, 32 |
| sheets | 2×2 cells of 64 → `a b c d` | 64, 48, 32 |
| pairs | left and right half of the middle strip → `a`, `b` | 64, 48, 32 |
| corpses | fixed 2×2 grid of 64 | 64, 48, 32 |
| equipment | 2×2 quarters of 32, cut straight on the lines | 32 |
| accessories, consumables, loot | one item, kept at real size up to 32 px, larger items shrunk to fit 32 | 32 |
| ground | 4×4 tiles of 32, one folder per set | 32 |
| walls | 4 parts, each placed in a 64×64 canvas at the bottom right (as the game draws it) | 64; for stairs use `--sizes 32`, for floor openings and ladders `--sizes 32fit` |
| monsters-small, -medium, -large-biped, -large, outfits | 3×2 grid of cells of 48, 64 or 80 (by LoRA): row 1 south, row 2 north; column 1 idle, 2-3 walk; the union of all frames is cut out and placed at the bottom right of a 64×64 canvas, one shift for all frames; east and west added by transposition. A figure that with its movement is larger than 64×64 (common for large monsters) goes on a 96×96 canvas (3×3 tiles), also at the bottom right, without shrinking; above 96 the image is skipped. Magenta background of outfits is removed like gray | 64, 48; 96 only for figures larger than 64 |

5. **Smaller sizes** (optional): 64 → 32 by averaging 2×2 blocks of a slightly sharpened image and snapping the
   colors back to the 64 version's palette; 48 on a 64 canvas the same way at 3/4 scale. Two sharpening strengths
   are produced (0.5 and 1.0); pick by eye.

## Walk cycles: east and west

The walk LoRAs draw only south and north. In this game's projection the other two directions are the
**transposition** of those (swap the x and y of every pixel; this is not a mirror): east = transpose(south),
west = transpose(north), frame by frame. In the training data this was exact for 79 of 90 monsters; it breaks for
asymmetric creatures and for weapons held in one hand (they switch hands).

`tools/postprocess.py` does this for every frame. By hand, with Python and Pillow, for a 64×64 frame:

```python
from PIL import Image
south = Image.open("frame_south_1.png")
east = south.transpose(Image.Transpose.TRANSPOSE)   # swap x and y
east.save("frame_east_1.png")
```

## Tips for clean sprites

- Use one palette for all frames of one character; small color differences between frames show up as flicker in
  an animation.
- Pixels that differ only slightly between the idle frame and a walk frame can be copied from the idle frame,
  so only the moving parts (legs, arms) change.
- Align frames on the feet (bottom edge) before exporting, so the character does not jump by a pixel.
