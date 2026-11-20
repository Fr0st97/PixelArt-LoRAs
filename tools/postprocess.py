r"""Turn images generated with a PixelArt LoRA into game sprites: find the pixel grid, shrink to game size, remove
the background, cut sheets into single sprites and, for walk cycles, add east and west by transposition.

Usage:
    python postprocess.py <lora> <input_folder> <output_folder> [--sizes 64,48,32,32fit]
    python postprocess.py --list            # show the LoRAs, how each is cut and its default sizes

    <lora>          flora, sheets, nature, pairs, equipment, accessories, consumables, loot, ground, corpses,
                    walls, monsters-small, monsters-medium, monsters-large-biped, monsters-large, outfits
    <input_folder>  PNG files from one generation run (e.g. results/<run> downloaded from the pod)
    --sizes         instead of the LoRA's default sizes:
                      64     64x64/                       the sprite at full game size
                      48     48on64-sharp05/, -sharp10/   a 48×48 version at the bottom right of a 64×64 canvas
                      32     32x32-sharp05/, -sharp10/    a 32×32 version of the 64×64 sprite
                      32fit  32x32-fit/                   item at real size up to 32 px, larger items shrunk to fit
                    sharp05 / sharp10: two sharpening strengths before shrinking; pick by eye.

Output (transparent background), <name> = input file name without .png:
    most LoRAs:  <output>/<size folder>/<name><cell>.png, cell a, b, c, d for sheets ('' for one object)
    ground:      <output>/32x32/<name>/<tile>.png, 16 tiles of one set
    walk cycles: <output>/<name>/<size folder>/<direction>-<frame>.png, direction south, north, east, west;
                 frame 0 idle, 1 and 2 walking. East and west are the transposition of south and north.
                 In the same folder the sprite sheets idle.png (4×1: north, east, south, west) and walk.png
                 (8×1: north 1 2, east 1 2, south 1 2, west 1 2).
                 A figure larger than 64×64 with its movement (large monsters) goes on a 96×96 canvas, folder
                 96x96/, full size only.

Method and limits: docs/postprocessing.md. Needs Python 3.10+ with pillow, numpy, scipy.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as nd

K4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
PERIODS = (4, 8, 16, 32)          # possible sizes of one game pixel in the generated image
STRENGTHS = {"sharp05": 0.5, "sharp10": 1.0}
CELLS = "abcdefghijklmnop"


def luma(c):
    return np.asarray(c)[..., :3].astype(float) @ [0.299, 0.587, 0.114]


# ---------- 1. pixel grid ----------

def find_grid(a):
    """(period, offset_y, offset_x): block borders where the color jumps are strongest. The smallest period scoring
    at least 75% of the best one wins: a multiple of the true period scores almost as well, half of it about half."""
    gx = np.abs(np.diff(a, axis=1)).sum((0, 2)); gy = np.abs(np.diff(a, axis=0)).sum((1, 2))
    scores = {}
    for P in PERIODS:
        bx = [gx[o::P].mean() for o in range(P)]; by = [gy[o::P].mean() for o in range(P)]
        scores[P] = (max(bx) / gx.mean() + max(by) / gy.mean(), int(np.argmax(by)), int(np.argmax(bx)))
    best = max(s[0] for s in scores.values())
    P = min(p for p, s in scores.items() if s[0] >= 0.75 * best)
    return (P,) + grid_offset(a, P, scores[P][1], scores[P][2])


def grid_offset(a, P, by=None, bx=None):
    """offset of a grid with a known period P; diff[i] is the border between pixel i and i+1, so a block starts at
    i+1; the offset is kept in (-P/2, P/2]"""
    if by is None:
        gx = np.abs(np.diff(a, axis=1)).sum((0, 2)); gy = np.abs(np.diff(a, axis=0)).sum((1, 2))
        by = int(np.argmax([gy[o::P].mean() for o in range(P)])); bx = int(np.argmax([gx[o::P].mean() for o in range(P)]))
    shift = lambda o: (o + 1) % P - P if (o + 1) % P > P // 2 else (o + 1) % P
    return shift(by), shift(bx)


def read_colors(a, P, oy, ox):
    """one color per game pixel: median of the block center (from P/4, size P/2)"""
    H, W = (a.shape[0] - oy) // P, (a.shape[1] - ox) // P
    c = np.zeros((H, W, 3))
    for y in range(H):
        for x in range(W):
            y0, x0 = oy + y * P + P // 4, ox + x * P + P // 4
            c[y, x] = np.median(a[max(y0, 0):y0 + P // 2, max(x0, 0):x0 + P // 2].reshape(-1, 3), 0)
    return c


# ---------- 2. background ----------

def background(c):
    """background mask: border color ±8 connected to the border; a closed hole only inside a dark outline (luma < 70);
    then a gray halo (saturation ≤ 14, ±20 from the background) is removed, up to 3 passes"""
    m = np.median(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]), 0)
    dev = np.abs(c - m).max(2)
    lab, n = nd.label(dev <= 8)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    t = np.isin(lab, list(edge)); yc = luma(c)
    for i in range(1, n + 1):
        if i in edge:
            continue
        r = lab == i
        if np.median(yc[nd.binary_dilation(r, K4) & ~r]) < 70:
            t |= r
    gray = (c.max(2) - c.min(2) <= 14) & (dev <= 20)
    for _ in range(3):
        new = gray & ~t & nd.binary_dilation(t, K4)
        if not new.any():
            break
        t |= new
    # gray rim outside a black outline: a gray pixel next to the background, darker than it, touching the outline
    ym = float(luma(m[None])[0]); grayish = (c.max(2) - c.min(2) <= 20) & (yc >= 50) & (yc <= ym + 20)
    for _ in range(2):
        new = grayish & ~t & nd.binary_dilation(t, K4) & nd.binary_dilation(~t & (yc < 50), K4)
        if not new.any():
            break
        t |= new
    if m.max() - m.min() > 60:
        t = colored_background(c, m, t)
    return t


def colored_background(c, m, t):
    """for a saturated (non-gray) background color: border color ±24 connected to the background; pixels in the
    background's hue next to the background and touching a dark outline are halo (2 passes); islands ≤ 3 px removed"""
    dev = np.abs(c - m).max(2); yc = luma(c)
    t = nd.binary_propagation(t, structure=K4, mask=t | (dev <= 24))
    ch = c - yc[..., None]; chm = m - float(luma(m[None])[0])
    ln = np.linalg.norm(ch, axis=2)
    hue = (ln > 30) & ((ch @ chm) > 0.9 * ln * np.linalg.norm(chm))
    for _ in range(2):
        new = hue & ~t & nd.binary_dilation(t, K4) & nd.binary_dilation(~t & (yc < 50), K4)
        if not new.any():
            break
        t = t | new
    lab, n = nd.label(~t, structure=np.ones((3, 3)))
    if n:
        size = nd.sum(np.ones_like(lab), lab, range(1, n + 1))
        t = t | np.isin(lab, np.nonzero(size <= 3)[0] + 1)
    return t


def canvas(a, P, oy, ox, gray_bg=False):
    """game-size RGBA image: colors read with block size P and the background made transparent. gray_bg: the
    background color is the gray measured in the whole image (for sheets whose content touches the border)"""
    c = read_colors(a, P, oy, ox)
    if gray_bg:
        m = np.median(c[(c.max(2) - c.min(2) <= 10) & (np.abs(luma(c) - 128) < 25)], 0)
        frame = np.zeros((c.shape[0] + 2, c.shape[1] + 2, 3)) + m; frame[1:-1, 1:-1] = c
        t = background(frame)[1:-1, 1:-1]
    else:
        t = background(c)
    o = np.zeros(c.shape[:2] + (4,), np.uint8); o[..., :3] = np.round(c); o[..., 3] = np.where(t, 0, 255)
    return o


def load(path):
    return np.array(Image.open(path).convert("RGB")).astype(int)


# ---------- 3. cutting into 64×64 cells ----------

def cells_by_parts(o):
    """canvas (64·r, 64·k) -> {cell: 64×64}; every connected part goes to the cell of its center, keeps its place in
    the cell and is moved inside when it sticks out"""
    H, W = o.shape[:2]
    if H % 64 or W % 64:
        raise ValueError(f"canvas {W}×{H} does not split into 64×64 cells")
    r, k = H // 64, W // 64
    lab, n = nd.label(o[..., 3] > 0, structure=np.ones((3, 3)))
    owner = np.full((H, W), -1)
    for i in range(1, n + 1):
        cy, cx = nd.center_of_mass(lab == i); owner[lab == i] = int(cy // 64) * k + int(cx // 64)
    out = {}
    for q in range(r * k):
        m = owner == q
        if m.sum() < 4:
            continue
        y, x = q // k * 64, q % k * 64
        ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        if y1 - y0 > 64 or x1 - x0 > 64:
            raise ValueError(f"object of cell {CELLS[q]} is larger than 64×64")
        dy = min(max(y0 - y, 0), 64 - (y1 - y0)); dx = min(max(x0 - x, 0), 64 - (x1 - x0))
        o64 = np.zeros((64, 64, 4), np.uint8); piece = o[y0:y1, x0:x1].copy(); piece[~m[y0:y1, x0:x1], 3] = 0
        o64[dy:dy + y1 - y0, dx:dx + x1 - x0] = piece
        out["" if r * k == 1 else CELLS[q]] = o64
    return out


def cells_fixed(o):
    """fixed grid of 64×64 cells, cut straight on the lines (neighbouring frames may touch)"""
    H, W = o.shape[:2]
    if H % 64 or W % 64:
        raise ValueError(f"canvas {W}×{H} does not split into 64×64 cells")
    k = W // 64; out = {}
    for q in range(H // 64 * k):
        cell = o[q // k * 64:q // k * 64 + 64, q % k * 64:q % k * 64 + 64].copy()
        if (cell[..., 3] > 0).sum() >= 4:
            out[CELLS[q]] = cell
    return out


def cells_pair(o):
    """pair: a 128×64 strip in the middle of a 128×128 canvas (rows 32-95); a = left, b = right"""
    if o.shape[:2] != (128, 128):
        raise ValueError(f"pair needs a 128×128 canvas, got {o.shape[1]}×{o.shape[0]}")
    outside = int((o[:32, :, 3] > 0).sum() + (o[96:, :, 3] > 0).sum())
    if outside:
        raise ValueError(f"pair: {outside} visible pixels outside the middle strip")
    out = {c: o[32:96, x:x + 64].copy() for c, x in (("a", 0), ("b", 64))}
    return {c: im for c, im in out.items() if (im[..., 3] > 0).sum() >= 4}


def read_sheet(path, cols=None, pair=False):
    """grid detection + colors + background. cols: sheet with a fixed grid of `cols` cells of 64 per row, the block
    size comes from the image width; pair: block size 8 (coarser detected blocks are multiples of it)"""
    a = load(path)
    P, oy, ox = find_grid(a)
    Pread = P
    if pair:
        if P % 8:
            raise ValueError(f"pair needs a block size of 8 or a multiple, detected {P}")
        Pread = 8
    elif cols:
        Pf = a.shape[1] // (64 * cols)
        if a.shape[1] % (64 * cols) or P % Pf:
            raise ValueError(f"{cols} cells per row: block size from the format {Pf}, detected {P} is no multiple")
        Pread = Pf
    return canvas(a, Pread, oy, ox), P


def cut_objects(path):
    o, _ = read_sheet(path)
    return cells_by_parts(o)


def cut_pair(path):
    o, _ = read_sheet(path, pair=True)
    return cells_pair(o)


def cut_corpses(path):
    o, _ = read_sheet(path, cols=2)
    return cells_fixed(o)


def cut_equipment(path):
    """2×2 items of 32 px on one 64 canvas, cut straight on the 32 lines, kept 1:1 (touching items stay apart)"""
    cells = cut_objects(path)
    if len(cells) != 1:
        raise ValueError(f"equipment: expected one 64×64 canvas, got {len(cells)}")
    o = next(iter(cells.values()))
    out = {}
    for k in range(4):
        q = o[k // 2 * 32:k // 2 * 32 + 32, k % 2 * 32:k % 2 * 32 + 32]
        if (q[..., 3] > 0).sum() >= 4:
            out["abcd"[k]] = q.copy()
    return out


# ground: 4×4 tiles of 32. side-X: ground on side X, corner-X: ground only in corner X,
# inner-no-X: ground everywhere except corner X, tile1-4: plain ground tiles
GROUND_LAYOUT = [["corner-sw", "side-e", "tile1", "side-w"],
                 ["corner-nw", "corner-ne", "inner-no-sw", "inner-no-ne"],
                 ["corner-se", "side-s", "inner-no-nw", "tile2"],
                 ["tile3", "tile4", "inner-no-se", "side-n"]]


def cut_ground(path):
    """4×4 sheet of 32 px tiles, ×8 -> 16 tiles 1:1; gray is transparent in border pieces, plain tiles stay full"""
    a = load(path)
    o = canvas(a, 8, *grid_offset(a, 8), gray_bg=True)
    if o.shape[0] < 128 or o.shape[1] < 128:
        raise ValueError(f"ground: canvas {o.shape[1]}×{o.shape[0]}, needs 128×128")
    out = {}
    for r in range(4):
        for k in range(4):
            n = GROUND_LAYOUT[r][k]; tile = o[r * 32:r * 32 + 32, k * 32:k * 32 + 32].copy()
            if n.startswith("tile"):
                tile[..., 3] = 255
            out[n] = tile
    return out


def cut_walls(path):
    """walls, stairs, openings, ladders (×6, sheet 160 = 2×2 cells of 80 from index 5 of the 170 canvas): every
    connected part to the cell of its center, then into a 64×64 canvas at the bottom right (as the game draws it)"""
    a = load(path)
    sheet = canvas(a, 6, *grid_offset(a, 6))[5:165, 5:165]
    lab, n = nd.label(sheet[..., 3] > 0, structure=np.ones((3, 3))); owner = np.full(lab.shape, -1)
    for i in range(1, n + 1):
        cy, cx = nd.center_of_mass(lab == i); owner[lab == i] = int(cy // 80) * 2 + int(cx // 80)
    out = {}
    for q in range(4):
        m = owner == q
        if m.sum() < 4:
            continue
        ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        if y1 - y0 > 64 or x1 - x0 > 64:
            raise ValueError(f"part {'abcd'[q]} is {x1 - x0}×{y1 - y0}, more than 64")
        piece = sheet[y0:y1, x0:x1].copy(); piece[~m[y0:y1, x0:x1], 3] = 0
        o64 = np.zeros((64, 64, 4), np.uint8); o64[64 - (y1 - y0):, 64 - (x1 - x0):] = piece
        out["abcd"[q]] = o64
    return out


WALK_NAMES = ["south-0", "south-1", "south-2", "north-0", "north-1", "north-2"]


def cut_walk(path, K):
    """3×2 sheet of cells of K game pixels (block size from the width): row 1 south, row 2 north; column 1 idle,
    2 and 3 walking. The figure may sit anywhere in its cell; the union of the 6 outlines is cut out and placed at the
    bottom right of a 64×64 canvas (as the game draws it), one shift for all frames, so the movement stays.
    A figure larger than 64 with its movement goes on a 96×96 canvas (3×3 tiles of 32), never shrunk."""
    a = load(path)
    P = a.shape[1] // (3 * K)
    if a.shape[1] != 3 * K * P or a.shape[0] != 2 * K * P:
        raise ValueError(f"image {a.shape[1]}×{a.shape[0]}, expected {3 * K * P}×{2 * K * P} (3×2 cells of {K})")
    o = canvas(a, P, *grid_offset(a, P))[:2 * K, :3 * K]
    # cut straight on the cell lines: neighbouring frames may touch (a weapon, a tail)
    cells = {name: o[q // 3 * K:q // 3 * K + K, q % 3 * K:q % 3 * K + K] for q, name in enumerate(WALK_NAMES)}
    boxes = [b for b in (Image.fromarray(c).getbbox() for c in cells.values()) if b]
    if not boxes:
        return {}
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    side = max(x1 - x0, y1 - y0)
    if side > 96:
        raise ValueError(f"the figure with its movement is {x1 - x0}×{y1 - y0}, larger than a 96×96 frame")
    F = 64 if side <= 64 else 96
    out = {}
    for name, c in cells.items():
        if (c[..., 3] > 0).sum() >= 4:
            f = np.zeros((F, F, 4), np.uint8); f[F - (y1 - y0):, F - (x1 - x0):] = c[y0:y1, x0:x1]; out[name] = f
    return out


def walk(K):
    return lambda path: cut_walk(path, K)


# ---------- 4. smaller sizes ----------

def sharpen(o64, strength, sigma=1.0):
    """unsharp mask over visible pixels only (the background does not blur in)"""
    a = (o64[..., 3] > 0).astype(float); c = o64[..., :3].astype(float)
    w = nd.gaussian_filter(a, sigma)
    blur = np.stack([nd.gaussian_filter(c[..., i] * a, sigma) for i in range(3)], -1) / np.maximum(w, 1e-6)[..., None]
    return np.clip(c + strength * (c - blur), 0, 255)


def to32(o64, strength):
    """mean of each 2×2 block of the sharpened 64, snapped to the 64 version's palette; a block with one visible
    pixel stays only when it is dark (luma < 70); the silhouette edge takes the darkest pixel of the block"""
    pal = np.unique(o64[o64[..., 3] > 0][:, :3], axis=0).astype(float)
    src = sharpen(o64, strength)
    b = np.zeros((32, 32, 4), np.uint8); dark = {}
    for y in range(32):
        for x in range(32):
            blk = o64[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(-1, 4); w = blk[:, 3] > 0; vis = blk[w]
            if len(vis) == 0:
                continue
            yy = luma(vis)
            if len(vis) == 1 and yy[0] >= 70:
                continue
            dark[y, x] = vis[np.argmin(yy)][:3] if yy.min() < 70 else None
            mean = src[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(-1, 3)[w].mean(0)
            b[y, x, :3] = pal[np.argmin(((pal - mean) ** 2).sum(1))].round(); b[y, x, 3] = 255
    m = b[..., 3] > 0
    for y, x in zip(*np.nonzero(m & ~nd.binary_erosion(m, K4))):
        if dark.get((y, x)) is not None:
            b[y, x, :3] = dark[y, x]
    return b


def weights(n):
    """W (n, 64): share of each 64 pixel in each n pixel; rows sum to 1"""
    W = np.zeros((n, 64)); s = 64 / n
    for j in range(n):
        a, b = j * s, (j + 1) * s
        for i in range(int(a), int(np.ceil(b))):
            W[j, i] = max(0.0, min(b, i + 1) - max(a, i))
    return W / s


def toN(o64, n, strength):
    """any scale n/64: area-weighted mean of the sharpened 64, snapped to its palette; a pixel is visible at coverage
    ≥ 0.5, or ≥ 0.25 with a dark pixel under it; the silhouette edge takes the darkest pixel under it"""
    W = weights(n); a = (o64[..., 3] > 0).astype(float)
    pal = np.unique(o64[a > 0][:, :3], axis=0).astype(float)
    src = sharpen(o64, strength)
    cov = W @ a @ W.T
    mean = np.stack([W @ (src[..., i] * a) @ W.T for i in range(3)], -1) / np.maximum(cov, 1e-6)[..., None]
    yy = np.where(a > 0, luma(o64), 999)
    dark_y = np.full((n, n), 999.0); dark = np.zeros((n, n, 3))
    for j in range(n):
        for k in range(n):
            iy, ix = np.nonzero(W[j])[0], np.nonzero(W[k])[0]
            blk = yy[np.ix_(iy, ix)]; p = np.unravel_index(np.argmin(blk), blk.shape)
            dark_y[j, k] = blk[p]; dark[j, k] = o64[iy[p[0]], ix[p[1]], :3]
    m = (cov >= 0.5) | ((cov >= 0.25) & (dark_y < 70))
    b = np.zeros((n, n, 4), np.uint8)
    for j, k in zip(*np.nonzero(m)):
        b[j, k, :3] = pal[np.argmin(((pal - mean[j, k]) ** 2).sum(1))].round(); b[j, k, 3] = 255
    for j, k in zip(*np.nonzero(m & ~nd.binary_erosion(m, K4))):
        if dark_y[j, k] < 70:
            b[j, k, :3] = dark[j, k]
    return b


def to48(o64, strength):
    """64×64 canvas with the 48×48 version at the bottom right"""
    out = np.zeros((64, 64, 4), np.uint8); out[16:, 16:] = toN(o64, 48, strength)
    return out


def bbox(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


def fit32(o, strength=1.0):
    """item up to 32 px cut out 1:1, a larger one shrunk just enough to fit 32; centered on a 32×32 canvas"""
    if o.shape[:2] == (32, 32):
        return o
    y0, y1, x0, x1 = bbox(o); src = o
    if max(y1 - y0, x1 - x0) > 32:
        n = 64 * 32 // max(y1 - y0, x1 - x0)
        while True:
            src = toN(o, n, strength); y0, y1, x0, x1 = bbox(src)
            if max(y1 - y0, x1 - x0) <= 32:
                break
            n -= 1
    piece = src[y0:y1, x0:x1]; out = np.zeros((32, 32, 4), np.uint8)
    oy, ox = (32 - piece.shape[0]) // 2, (32 - piece.shape[1]) // 2
    out[oy:oy + piece.shape[0], ox:ox + piece.shape[1]] = piece
    return out


SIZE_FOLDERS = {"64": ["64x64"], "48": [f"48on64-{s}" for s in STRENGTHS],
                "32": [f"32x32-{s}" for s in STRENGTHS], "32fit": ["32x32-fit"]}


def resize(o64, folder):
    if folder in ("64x64", "96x96"):
        return o64
    if folder == "32x32-fit":
        return fit32(o64)
    kind, s = folder.rsplit("-", 1)
    return {"48on64": to48, "32x32": to32}[kind](o64, STRENGTHS[s])


# ---------- 5. LoRAs ----------

# lora: (cut function, default sizes, short description)
LORAS = {
    "flora":       (cut_objects,   ("64", "48", "32"), "one object -> one sprite"),
    "nature":      (cut_objects,   ("64", "48", "32"), "one object -> one sprite"),
    "sheets":      (cut_objects,   ("64", "48", "32"), "2×2 cells of 64 -> a b c d"),
    "pairs":       (cut_pair,      ("64", "48", "32"), "middle strip -> a (left), b (right)"),
    "corpses":     (cut_corpses,   ("64", "48", "32"), "fixed 2×2 grid of 64 -> a b c d"),
    "equipment":   (cut_equipment, ("32fit",),         "2×2 items of 32, cut on the lines -> a b c d"),
    "accessories": (cut_objects,   ("32fit",),         "one item, real size up to 32"),
    "consumables": (cut_objects,   ("32fit",),         "one item, real size up to 32"),
    "loot":        (cut_objects,   ("32fit",),         "one item, real size up to 32"),
    "ground":      (cut_ground,    ("32",),            "4×4 tiles of 32, one folder per set"),
    "walls":       (cut_walls,     ("64",),            "4 parts at the bottom right of 64 (stairs: --sizes 32, "
                                                       "openings and ladders: --sizes 32fit)"),
    "monsters-small":       (walk(48), ("64", "48"), "3×2 walk sheet, cells of 48 -> 64×64 frames, + east, west"),
    "monsters-medium":      (walk(64), ("64", "48"), "3×2 walk sheet, cells of 64 -> 64×64 frames, + east, west"),
    "monsters-large-biped": (walk(80), ("64", "48"), "3×2 walk sheet, cells of 80 -> 64×64 frames, + east, west"),
    "monsters-large":       (walk(80), ("64", "48"), "3×2 walk sheet, cells of 80 -> 64×64 frames, + east, west"),
    "outfits":              (walk(64), ("64", "48"), "3×2 walk sheet, cells of 64 -> 64×64 frames, + east, west"),
}
WALK_LORAS = {n for n in LORAS if n.startswith("monsters") or n == "outfits"}
TRANSPOSE = {"east": "south", "west": "north"}   # east = transpose(south), west = transpose(north), frame by frame
# sprite sheets in the usual game client layout: one row, directions north, east, south, west;
# idle: one frame per direction (4×1), walk: the 2 walk frames of each direction (8×1)
DIRECTIONS = ("north", "east", "south", "west")
SHEETS = {"idle": [f"{d}-0" for d in DIRECTIONS],
          "walk": [f"{d}-{i}" for d in DIRECTIONS for i in (1, 2)]}


def save_walk(out, name, cells, sizes):
    if cells and next(iter(cells.values())).shape[0] == 96:   # large figure: full size only, no smaller versions
        sizes, folders = ("96",), {"96": ["96x96"]}
    else:
        folders = SIZE_FOLDERS
    for size in sizes:
        for folder in folders[size]:
            d = out / name / folder; d.mkdir(parents=True, exist_ok=True)
            frames = {c: resize(o64, folder) for c, o64 in cells.items()}
            for new, src in TRANSPOSE.items():
                for c in [c for c in frames if c.startswith(src + "-")]:
                    frames[new + c[len(src):]] = frames[c].transpose(1, 0, 2).copy()
            for c, im in frames.items():
                Image.fromarray(im).save(d / f"{c}.png")
            for sheet, order in SHEETS.items():
                if all(c in frames for c in order):
                    Image.fromarray(np.concatenate([frames[c] for c in order], axis=1)).save(d / f"{sheet}.png")


def save_cells(out, name, cells, sizes):
    for c, o in cells.items():
        for size in sizes:
            for folder in SIZE_FOLDERS[size]:
                (out / folder).mkdir(parents=True, exist_ok=True)
                Image.fromarray(resize(o, folder)).save(out / folder / f"{name}{c}.png")


def process(lora, path, out, sizes=None):
    cut, default, _ = LORAS[lora]
    sizes = sizes or default
    if lora == "ground":
        d = out / "32x32" / path.stem; d.mkdir(parents=True, exist_ok=True)
        tiles = cut(path)
        for n, im in tiles.items():
            Image.fromarray(im).save(d / f"{n}.png")
        return f"{len(tiles)} tiles"
    cells = cut(path)
    if lora in WALK_LORAS:
        save_walk(out, path.stem, cells, sizes)
        F = next(iter(cells.values())).shape[0] if cells else 64
        return (f"frames {' '.join(cells)} + east, west, {F}×{F}" + (", sheets idle, walk" if len(cells) == 6 else
                                                                    ", incomplete: no sheets"))
    save_cells(out, path.stem, cells, sizes)
    return f"cells {' '.join(c or '1' for c in cells)}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lora", nargs="?", choices=sorted(LORAS))
    ap.add_argument("input", nargs="?", type=Path)
    ap.add_argument("output", nargs="?", type=Path)
    ap.add_argument("--sizes", help="comma list of 64, 48, 32, 32fit")
    ap.add_argument("--list", action="store_true", help="show the LoRAs and how each is processed")
    args = ap.parse_args()
    if args.list:
        for name, (_, sizes, text) in LORAS.items():
            print(f"{name:21} {','.join(sizes):10} {text}")
        return
    if not (args.lora and args.input and args.output):
        ap.error("needs <lora> <input_folder> <output_folder>")
    sizes = None
    if args.sizes:
        sizes = tuple(args.sizes.split(","))
        if set(sizes) - set(SIZE_FOLDERS):
            ap.error(f"--sizes: allowed {', '.join(SIZE_FOLDERS)}")
        if args.lora == "ground":
            ap.error("--sizes does not apply to ground (tiles are always 32×32)")
    files = sorted(args.input.glob("*.png"))
    if not files:
        sys.exit(f"no PNG files in {args.input}")
    failed = 0
    for f in files:
        try:
            print(f"{f.name}: {process(args.lora, f, args.output, sizes)}")
        except ValueError as e:
            failed += 1
            print(f"{f.name}: SKIPPED, {e}")
    print(f"done: {len(files) - failed} of {len(files)} images, output in {args.output}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
