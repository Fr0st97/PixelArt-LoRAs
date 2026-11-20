# Guide: generating pixel art with the PixelArt LoRAs

This guide takes you from nothing to finished game sprites. It is written so that a person with no experience
can follow it, and so that an AI assistant (Claude or similar) can read it and lead that person through it,
or do the steps itself when it has access to RunPod.

What you will do:

1. rent a GPU computer ("pod") on RunPod,
2. install the generator and download the Krea-2 model,
3. upload a LoRA and a prompt file,
4. generate images,
5. download them and shrink them to game size (post-processing),
6. stop the pod so it stops costing money.

Time for the first run: about 30-45 minutes. Cost: about $0.50-1 on an A40, a little more on an RTX PRO 6000.

## For the AI assistant

If you are an AI reading this to help a user:

- **Money.** A running pod costs money every hour, also when it does nothing. Before creating, starting or
  restarting a pod, tell the user the GPU type and the price per hour and get a clear yes. When the work is done,
  remind the user to stop the pod, or stop it yourself if they agreed. Never leave a pod running unattended
  without the user knowing.
- **Secrets.** Never print, store or repeat the user's RunPod API key, Jupyter password or Hugging Face token.
- **Check, do not assume.** After each step, check the result the way the step says (a log line, a file size,
  an image). If something fails, stop and tell the user what failed and what you saw. Do not invent workarounds
  that change the model, the scripts or the prompt format.
- **Prompts.** The LoRA layout texts in [loras.md](loras.md) must be copied exactly. Only the description part
  is free text.
- **Files.** Keep the user's results on the persistent volume (`/workspace`); the pod's local disk is wiped
  when the pod stops.
- If you can run commands on the pod (RunPod web terminal, SSH, Jupyter terminal, or a RunPod MCP/API tool),
  run the commands from this guide yourself and report the results. If you cannot, give the user one command
  at a time and ask them to paste the output back.

## 1. What you need

- A RunPod account (runpod.io) with some credit ($5-10 is plenty to start).
- The LoRA files. They are not in this repository: the author shares them, one zip per LoRA,
  `Krea2-PixelArt-<lora>.zip` (~0.9 GB), with the weights `Krea2-PixelArt-<lora>.safetensors`, the Krea 2 license
  and the NOTICE. Get only the LoRAs you need (list: [loras.md](loras.md#overview)).
- This repository (the `pod/` scripts, `tools/` and the example wishes in `prompts/`).
- For post-processing on your own computer: Python 3.10 or newer with `pillow`, `numpy`, `scipy`
  (`pip install pillow numpy scipy`). See [postprocessing.md](postprocessing.md).

## 2. Create a pod

### RunPod account and console

RunPod (runpod.io) rents GPU computers by the hour. Everything below happens in its web console,
[console.runpod.io](https://console.runpod.io).

1. **Account**: sign up at [console.runpod.io/signup](https://www.console.runpod.io/signup) and verify your
   email. Two-factor authentication is recommended.
2. **Credit**: RunPod is prepaid. If you have not added a payment method and credit yet, the console asks for it
   when you deploy your first pod. $5-10 is enough to start. When the balance reaches $0, pods stop.
3. **Volume (optional, recommended)**: a network volume keeps your files between pods. Create it on the
   [Storage page](https://www.console.runpod.io/user/storage): **New Network Volume**, pick a data center, a name
   and a size (20 GB is enough), then **Create Network Volume**. It costs about $0.07 per GB per month, also when
   no pod runs; delete it when you no longer need it. A pod using it must run in the same data center.
4. **Deploy page**: click **+ New** in the top right corner and select **Pod**, or click **Pods** in the left
   sidebar. There you choose the template, the GPU and the storage (table below), check the price summary and
   deploy. If the GPU you want shows *Out of capacity*, pick another GPU or another data center.

RunPod changes its console from time to time; if a button is named differently, look for the same step in
RunPod's guide [Deploy your first Pod](https://docs.runpod.io/get-started).

### Optional: let your AI assistant operate RunPod

With RunPod's official plugin (an MCP server), the AI assistant can create, check and stop pods itself, instead of
telling you what to click. You sign in with your RunPod account in the browser; you do not paste any API key into
the chat. The assistant still has to ask you before anything that costs money.

| Assistant | How to connect |
|---|---|
| Claude (desktop app) | **Settings → Connectors → Add custom connector**, URL `https://mcp.runpod.io/`, **Add**, then sign in with RunPod |
| Claude Code | `claude plugin marketplace add runpod/runpod-plugins-official`, then `claude plugin install runpod@runpod`; run `/reload-plugins` and sign in through `/mcp` |
| ChatGPT | add the [Runpod plugin](https://chatgpt.com/plugins/plugin_asdk_app_6ada3b2d28b4819188b6ced6c229aadf) and sign in, no terminal needed |
| Codex | `codex plugin marketplace add https://github.com/runpod/runpod-plugins-official.git`, then `codex plugin add runpod@runpod` |
| Cursor, VS Code, Windsurf and others | `npx @runpod/mcp-server@latest add` (needs Node.js 20.12+) configures the installed clients |

Check that it works by asking the assistant: "List my Runpod pods." An empty list is fine: the connection works
and you have no pods yet. Current instructions for every client: RunPod's
[MCP servers guide](https://docs.runpod.io/get-started/mcp-servers) and [agent setup](https://docs.runpod.io/agent-setup).

### Pod settings

| Setting | Value |
|---|---|
| GPU | Recommended: **A40** (48 GB, about $0.59/h, ~205 images per hour at 1024×1024): cheapest per image. **L40S** (about $1.09/h, ~290 per hour) in between. **RTX PRO 6000** (96 GB, about $2.69/h, ~485 per hour): for big batches when time matters. All sizes: [expected generation prices](#expected-generation-prices). |
| Template / image | `runpod/pytorch:2.1.0-cu1320-torch280-ubuntu2404` (RunPod's PyTorch 2.8 template, CUDA 13.2): type "PyTorch" in the template search. Keep **Start Jupyter notebook** on. |
| Container disk | at least **60 GB** (the models take ~35 GB). Use 100 GB or more if you also want to train. |
| Volume | persistent storage at `/workspace`, any size from 20 GB: your network volume (step 3 above), or a **volume disk** if you skipped it. It keeps your files when the pod stops; a volume disk is deleted together with the pod. |
| Ports | 8888 (Jupyter) and 22 (SSH); the template has them by default |

Click **Deploy**. When the pod shows *Running*, open **Connect → Jupyter Lab** (port 8888). In Jupyter you can
upload files (drag and drop into the file browser) and open a **Terminal** (File → New → Terminal).

## 3. Upload the files

In Jupyter, inside `/workspace`, create this layout and upload:

```
/workspace/
  pod/          setup_pod.sh, generate.sh           (from this repository)
  your prompt files, built with tools/make_prompts.py
  loras/        the unpacked LoRA files, e.g. loras/Krea2-PixelArt-flora.safetensors
```

To unpack a LoRA zip in the terminal: `cd /workspace/loras && python3 -m zipfile -e Krea2-PixelArt-flora.zip .`

Check: `ls -la /workspace/loras/` shows the `.safetensors` files, each about 0.9 GB.

## 4. Install the generator and download the model

In the Jupyter terminal:

```
cd /workspace && nohup sh pod/setup_pod.sh > setup.out 2>&1 &
```

It installs musubi-tuner v0.3.6 and downloads Krea-2 Turbo, the Qwen3-VL text encoder and the VAE to the pod's
local disk (`/root/models`, ~35 GB). It takes 2-10 minutes. Check progress with `tail /root/models/setup.log`.
It is done when the last line is `SETUP_OK`. If it says `SETUP_FAIL`, the line before tells which file has the
wrong size (usually a broken download: run the same command again, it resumes).

The models live on the local disk, so after every pod stop/start you run this step again.

## 5. Generate

You need a prompt file. For a first test, build one from the LoRA's 20 examples (on your computer or on the pod,
then upload it to `/workspace`):

```
python tools/make_prompts.py flora prompts/flora/examples.txt flora-test.txt
```

Then run:

```
cd /workspace && nohup sh pod/generate.sh loras/Krea2-PixelArt-flora.safetensors flora-test.txt results/flora-test > gen.out 2>&1 &
```

Arguments: LoRA file, prompt file, output folder, and optionally the LoRA strength (default `1.0`).

- Progress: `tail -f results/flora-test/generate.log` (Ctrl+C stops watching, not the job).
- Done when the log ends with `GEN_END rc=0`. Any other `rc` means an error; the lines above it say why.
- Output: `results/flora-test/<date>-<time>_<seed>.png`, one per prompt line, plus `lora.txt` (which LoRA and
  prompts made them) and `generate.log`.

Speed (1024×1024, measured): A40 about 17.6 s per image (~205 per hour), RTX PRO 6000 about 7.4 s (~485 per
hour), plus 0.5-1.5 minutes to load the models at the start of each run. Bigger walk sheets take longer; all sizes
and GPUs: [expected generation prices](#expected-generation-prices). Put many prompts in one file rather than
starting many runs.

A pod running a training job does not have enough GPU memory left to generate at the same time on an A40.

## 6. Write your own prompts

The easy way: write what you want as `kind | description` lines and let `tools/make_prompts.py` build the prompt
file. Everything about it, with examples for every LoRA: **[prompting.md](prompting.md)**.

What the script produces, if you want to write lines by hand: plain text, one prompt per line, always the same
structure:

```
<trigger>, <layout text of the LoRA>, <kind>, <your description>, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d <seed>
```

- Copy the trigger, layout text and kind from [loras.md](loras.md) or from a line built by `tools/make_prompts.py`.
  The LoRA learned these words exactly; changing them changes the layout.
- Write the description in simple English: shape, material, colors, one or two distinctive details.
  `small clay flower pot with a thin green leafy plant` works better than a long story.
- Keep `plain gray background` at the end and the options `--s 8 --l 1` (Turbo settings).
- `--w` and `--h`: 1024 and 1024, except the walk-cycle LoRAs: monsters-small 1152×768, monsters-medium and
  outfits 1536×1024, monsters-large-biped and monsters-large 1920×1280.
- Outfits end with a magenta background instead of gray (`make_prompts.py` writes it).
- `--d` is the seed. Same prompt + same seed = same image. To get variants of one idea, repeat the line with
  different seeds.
- If the LoRA ignores your description (always draws the same kind of thing), run the same file with strength
  `0.7`: `sh pod/generate.sh <lora> <prompts> <out> 0.7`. Lower strength follows the text more and the style less.

Easiest way to make a new file: copy `prompts/<lora>/examples.txt`, replace the descriptions with yours and build
it with `tools/make_prompts.py`. An AI assistant can write 20-50 wishes like this for you from a short wish list.

## 7. Download the results

In Jupyter, right-click a folder → **Download as an archive**, or zip it in the terminal:
`cd /workspace/results && python3 -m zipfile -c flora-test.zip flora-test/` and download the zip.

## 8. Post-processing (shrink to game size)

The generated image is a big picture of a small sprite: every game pixel is a block of 6, 8 or 16 image pixels,
on a gray background. Post-processing finds that grid, reads one color per block, removes the background and
cuts sheets into single 64×64 sprites (and 48 or 32 if needed). Walk cycles get east and west by transposition.
Details and commands: [postprocessing.md](postprocessing.md).

## 9. Stop the pod

When you are done: RunPod console → your pod → **Stop**. A stopped pod does not pay for the GPU, but its local
disk is wiped (models, anything outside `/workspace`); the volume keeps your files. **Terminate** deletes the pod
completely. Storage (volumes, stopped pods' disks) still costs a little per month; delete what you no longer need.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `SETUP_FAIL`, a file has the wrong size | Interrupted download. Run `setup_pod.sh` again; `wget -c` continues where it stopped. |
| Error about the tokenizer, "not a valid JSON file" | The Hugging Face cache is on a network volume that does not support links. The scripts set `HF_HOME=/root/.cache/huggingface` (local disk); do not change it to `/workspace`. |
| `CUDA out of memory` | Another job (training, another generation) uses the GPU. Wait for it or use a separate pod. |
| The pod was killed, no error in the log | Out of system RAM. Some A40 pods have a 50 GB RAM limit; do not run several jobs at once there. |
| Images ignore the description | Lower the LoRA strength to 0.7; describe more simply; check that the layout text is copied exactly. |
| Output looks blurry or the objects are too big | Check `--s 8 --l 1` and the size options; the walk LoRAs need their own size (section 6). |
| Files from one pod do not show up on another | Global volumes can show new files with a delay between pods. Check from the pod that wrote them. |
| You changed a script while a job was running it | Do not: `sh` reads scripts while running. Replace files only when no job uses them. |

## Expected generation prices

Measured speeds and the cost of generation alone (the pod's price per hour × time). Values with `~` are estimates
from neighbouring sizes. Add the setup: 2-10 minutes per pod start (about $0.02-0.10 on an A40, $0.09-0.45 on an
RTX PRO 6000) and 0.5-1.5 minutes of model loading per run.

**A40 ($0.59/h)**: recommended, cheapest per image

| Image size (LoRAs) | s/image | images/h | 1 image | 100 images |
|---|---|---|---|---|
| 1024×1024 (items, plants, ground, walls, corpses…) | 17.6 | 205 | $0.0029 | $0.29 |
| 1152×768 (monsters-small) | 16.2 | 220 | $0.0027 | $0.27 |
| 1536×1024 (monsters-medium, outfits) | 23.2 | 155 | $0.0038 | $0.38 |
| 1920×1280 (monsters-large-biped, monsters-large) | ~31 | ~115 | ~$0.0051 | ~$0.51 |

**L40S ($1.09/h)**

| Image size | s/image | images/h | 1 image | 100 images |
|---|---|---|---|---|
| 1024×1024 | 12-13 | ~290 | $0.0038 | $0.38 |
| 1152×768 | 11.5 | 310 | $0.0035 | $0.35 |
| 1536×1024 | 16.6-17.7 | ~210 | $0.0052 | $0.52 |
| 1920×1280 | 23.2 | 155 | $0.0070 | $0.70 |

**RTX PRO 6000 ($2.69/h)**: fastest, for big batches when time matters

| Image size | s/image | images/h | 1 image | 100 images |
|---|---|---|---|---|
| 1024×1024 | 7.4 | 485 | $0.0055 | $0.55 |
| 1152×768 | ~6 | ~600 | ~$0.0045 | ~$0.45 |
| 1536×1024 | 8.1-8.5 | ~435 | $0.0062 | $0.62 |
| 1920×1280 | ~11 | ~330 | ~$0.0082 | ~$0.82 |

Prices per hour are RunPod's at the time of measuring (November 2026) and change; check the current price in the
RunPod console and scale the table by it.
