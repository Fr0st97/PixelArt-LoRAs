"""ComfyUI node: runs tools/postprocess.py on the images coming out of VAE Decode and saves the game sprites to
ComfyUI's output folder. Install and use: docs/postprocessing.md, "In ComfyUI"."""
import importlib.util
import time
from pathlib import Path

import numpy as np
from PIL import Image

import folder_paths

_spec = importlib.util.spec_from_file_location(
    "pixelart_postprocess", Path(__file__).resolve().parent.parent / "tools" / "postprocess.py")
pp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pp)

PREVIEW_MAX = 48   # sprites shown on the node; all of them are saved


class PixelArtPostprocess:
    """IMAGE batch -> transparent sprites at game size in output/<subfolder>/, same folders and names as the
    command line tool; previews the saved sprites on the node."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "images": ("IMAGE",),
            "lora": (sorted(pp.LORAS), {"default": "flora"}),
            "subfolder": ("STRING", {"default": "pixelart"}),
        }, "optional": {
            "sizes": ("STRING", {"default": "", "tooltip": "empty = the LoRA's default; or a comma list of "
                                 + ", ".join(pp.SIZE_FOLDERS) + " (e.g. fit,64,48,32)"}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "image/pixel art"

    def run(self, images, lora, subfolder, sizes=""):
        sizes = tuple(s.strip() for s in sizes.split(",") if s.strip()) or None
        if sizes and set(sizes) - set(pp.SIZE_FOLDERS):
            raise ValueError(f"sizes: allowed {', '.join(pp.SIZE_FOLDERS)}")
        if sizes and lora == "ground":
            raise ValueError("sizes do not apply to ground (tiles are always 32x32)")
        root = Path(folder_paths.get_output_directory())
        out = root / subfolder; src = out / "generated"; src.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        report, before = [], {p for p in out.rglob("*.png")}
        for i, im in enumerate(images):
            a = np.clip(255.0 * im.cpu().numpy()[..., :3], 0, 255).astype(np.uint8)
            path = src / f"{lora}-{stamp}-{i:03d}.png"          # the generated image is kept next to the sprites
            Image.fromarray(a).save(path)
            try:
                report.append(f"{path.name}: {pp.process(lora, path, out, sizes)}")
            except ValueError as e:
                report.append(f"{path.name}: SKIPPED, {e}")
        new = sorted(p for p in set(out.rglob("*.png")) - before if p.parent != src)
        shown = [p for p in new if p.name in ("idle.png", "walk.png")] or new   # walk cycles: the sheets only
        ui = [{"filename": p.name, "subfolder": p.parent.relative_to(root).as_posix(), "type": "output"}
              for p in shown[:PREVIEW_MAX]]
        text = "\n".join(report + [f"{len(new)} sprite files in output/{subfolder}"])
        print(text)
        return {"ui": {"images": ui}, "result": (text,)}


NODE_CLASS_MAPPINGS = {"PixelArtPostprocess": PixelArtPostprocess}
NODE_DISPLAY_NAME_MAPPINGS = {"PixelArtPostprocess": "PixelArt Postprocess (game sprites)"}
