# PixelArt LoRAs

LoRAs for the **Krea-2** image model that draw game graphics as pixel art in a top-down oblique 45° view:
plants, rocks, furniture, equipment, inventory items, ground tiles, walls, corpses, and walking characters
and monsters. Each LoRA covers one kind of graphics and draws it at a fixed pixel scale on a plain gray
background, so the result can be shrunk back to exact game size (64×64, 48×48 or 32×32 sprites).

## LoRAs

| LoRA | Trigger | Draws |
|---|---|---|
| flora | `blnr_flora` | trees, plants, potted plants, mushrooms |
| sheets | `blnr_sheet` | lamps (unlit/lit), wall decorations, furniture in 4 directions |
| nature | `blnr_nature` | rocks, crystals, bones, dead wood |
| pairs | `blnr_pair` | statues, decorations, chests, furniture in 2 directions; light sources unlit/lit |
| equipment | `blnr_eq` | matching sets of weapons, armor and mage items |
| accessories | `blnr_accessory` | amulets, rings, backpacks |
| consumables | `blnr_utility` | runes, potions, food, tools, valuables |
| loot | `blnr_loot` | monster loot items |
| ground | `blnr_ground` | ground tile sets with border pieces |
| corpses | `blnr_corpse` | a monster and its corpse stages (not released yet) |
| walls | `blnr_wall` | wall sets in 4 parts, stairs, floor openings, ladders |
| monsters-small | `blnr_mob` | small monster walk cycle (idle + 2 frames, front and back) |
| monsters-medium | `blnr_mob` | medium monster walk cycle |
| monsters-large-biped | `blnr_mob` | large two-legged monster walk cycle (giants, ogres, golems) |
| monsters-large | `blnr_mob` | large monster walk cycle, other shapes (animals, dragons, beasts) |
| outfits | `blnr_outfit` | player character walk cycle (idle + 2 frames, front and back) |

Details, prompt templates, examples and known limits: [docs/loras.md](docs/loras.md).

Full model names are **Krea 2 PixelArt <LoRA>**, e.g. Krea 2 PixelArt flora; the files are
`Krea2-PixelArt-<lora>.safetensors`. The weights are not in this repository; the author shares them as one zip per LoRA
(`Krea2-PixelArt-<lora>.zip`, ~0.9 GB) with the Krea 2 license and the NOTICE.

## Quick start

1. Rent a GPU pod on RunPod (runpod.io), PyTorch 2.8 template, 60+ GB disk. Recommended: **A40**, about $0.59/h,
   ~205 images per hour (1024×1024). Faster: **RTX PRO 6000**, about $2.69/h, ~485 images per hour. Prices for
   every image size and GPU: [docs/guide.md](docs/guide.md#expected-generation-prices).
2. Upload `pod/`, your prompt file (`tools/make_prompts.py` builds it from simple descriptions) and the LoRA
   files to `/workspace`.
3. `sh pod/setup_pod.sh` installs the generator (musubi-tuner) and downloads Krea-2 Turbo.
4. `sh pod/generate.sh <lora.safetensors> <prompts.txt> <output_dir>` generates one image per prompt line.
5. Download the images and turn them into sprites: `python tools/postprocess.py <lora> <images> <output>`
   ([docs/postprocessing.md](docs/postprocessing.md)).
6. Stop the pod.

**New to this? Open [START_HERE.md](START_HERE.md)**: give this repository to an AI assistant and it will guide
you through everything (or do most of it for you).

## Repository

| Path | Content |
|---|---|
| `START_HERE.md` | what to paste into your AI assistant to be guided step by step |
| `docs/ai-operator.md` | playbook for the AI assistant: what to ask, what to run, what to check |
| `docs/guide.md` | full walkthrough: pod, setup, generation, download, stopping, troubleshooting, costs |
| `docs/prompting.md` | how to write prompts: pick the LoRA and kind, describe the object, examples, fixing results |
| `tools/make_prompts.py` | turns simple `kind \| description` lines into a ready prompt file for one LoRA |
| `docs/loras.md` | catalog of the LoRAs: triggers, layouts, prompt templates, examples, status |
| `docs/postprocessing.md` | how generated images become game sprites; east/west for walk cycles |
| `tools/postprocess.py` | shrinks generated images to game size, removes the background, cuts sheets, adds east/west |
| `pod/setup_pod.sh` | installs musubi-tuner v0.3.6 and downloads the Krea-2 models on a pod |
| `pod/generate.sh` | generates images with one LoRA from a prompt file |
| `prompts/<lora>/examples.txt` | 20 example wishes (`kind \| description`) per LoRA; `tools/make_prompts.py` turns them into a prompt file |

## Credits and licenses

- Base model: Krea 2 (Raw and Turbo) by Krea, files from `Comfy-Org/Krea-2` on Hugging Face.
- **The LoRAs are Derivatives of Krea 2 and are licensed under the Krea 2 Community License Agreement**
  (copy: [LICENSE-Krea-2.pdf](LICENSE-Krea-2.pdf); notice: [NOTICE](NOTICE)). By using them you agree to it and to
  the Acceptable Use Policy (https://krea.ai/krea-2-use-policy). In short: free use, including commercial use for
  companies under $1M annual revenue; when you pass the LoRAs on, include the license and the NOTICE; you are
  responsible for what you generate. Read the license itself; this summary is not legal advice.
- Training and generation: musubi-tuner by kohya-ss.
- Scripts and documents in this repository: **MIT License** ([LICENSE](LICENSE)). It does not cover the LoRA
  weights.
