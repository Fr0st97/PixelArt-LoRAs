# Playbook for the AI assistant

You are helping a person who has never done this before to generate game sprites with the PixelArt LoRAs.
Do as much of the work as you can yourself; ask the person only for what only they can do (decisions, payments,
clicks in a web page you cannot reach). Use plain, short language. One step at a time.

Read first: [guide.md](guide.md) (the steps), [prompting.md](prompting.md) (prompts), [loras.md](loras.md)
(the LoRAs), [postprocessing.md](postprocessing.md) (after generation), and for writing prompts the examples in
`prompts/<lora>/examples.txt`. In the three-chat setup each chat reads only its own files (table below).

## Rules

1. **Money first.** Before anything that costs money (creating, starting, restarting a pod), tell the person the
   GPU, the price per hour and roughly how long it will run, and wait for a yes. Never leave a pod running at the
   end without them knowing; offer to stop it.
2. **Never show or store secrets**: RunPod API key, Jupyter password, tokens.
3. **Check every step** with the check listed below. If a check fails, stop, say what you saw, and suggest the fix
   from the troubleshooting table in guide.md. Do not change the scripts, the model or the layout texts to get
   around an error.
4. **Do not invent results.** Only report what a command, a log or an image actually showed.
5. **Keep their work.** Results go to `/workspace` (the persistent volume), not to the pod's local disk.

## Before the first step: work folder and three chats

### Agree where the files go

Before writing any file, agree with the person where their work is stored. Ask in one message:
- Which folder on their computer is the work folder? Suggest one outside this repository, e.g.
  `Documents/pixelart-work`. Never put their results into the repository.
- On the pod, results go to `/workspace/results/<run>` (the persistent volume); confirm they have a volume.

Then create this layout in the work folder (adjust names only if the person wants):

```
<work folder>/
  WORK.md        the agreed paths, the LoRAs in use, the list of runs and their status
  wishes/        kind | description files, one per LoRA and batch
  prompts/       prompt files built from the wishes
  raw/<run>/     images downloaded from the pod, unchanged, with lora.txt
  sprites/<run>/ finished sprites after post-processing
```

Name a run `<lora>-<short-name>-<n>` (e.g. `outfits-knights-1`) and use the same name in every folder and on
the pod. Write the paths into `WORK.md` first; every chat reads it before doing anything and adds what it did.

### Propose three chats

The work has three separate jobs. Suggest one chat per job so that each stays short and focused, and each one
starts by reading `WORK.md`:

| Chat | Reads | Does | Gives to the next |
|---|---|---|---|
| **1. Prompts** | this file, [prompting.md](prompting.md), [loras.md](loras.md), `prompts/<lora>/examples.txt` | turns wishes into `wishes/` and `prompts/` files; after a run, looks at the images and fixes the descriptions | a prompt file in `prompts/`, noted in `WORK.md` |
| **2. Pod** | this file, [guide.md](guide.md) | shows the price list, creates, starts and stops the pod, uploads LoRAs and prompt files, runs setup and generation, watches the logs, checks the image count, downloads to `raw/<run>/` | images in `raw/<run>/`, noted in `WORK.md` |
| **3. Post-processing** | this file, [postprocessing.md](postprocessing.md) | runs `tools/postprocess.py`: grid, background, cutting sheets, game sizes, east/west and sheets for walk cycles; checks the sprites | sprites in `sprites/<run>/`, noted in `WORK.md` |

Give the person a short opening message for each chat, e.g.: "You are the Pod chat of my PixelArt work. Read
docs/ai-operator.md, docs/guide.md and <work folder>/WORK.md. Your job: …". If the chat cannot read files, the
person pastes the files from the "Reads" column. A chat does only its own job; when something
belongs to another chat, it says so and writes a note into `WORK.md`. The money rule applies to the Pod chat:
only it creates or starts pods.

If the person prefers one chat for everything, that is fine: follow the plan below in order, still with the
work folder and `WORK.md`.

## What you can do yourself

- If you have a RunPod tool (MCP server, API, `runpodctl`): create, inspect, stop pods and run commands on them.
  If you have none, offer the person to connect RunPod's plugin (a few clicks, sign-in in the browser, no API key in
  the chat): [guide.md](guide.md#optional-let-your-ai-assistant-operate-runpod). It is optional; without it the
  person clicks in the console. Never ask the person to paste an API key into the chat.
- If you can run code locally: run `tools/make_prompts.py` and the post-processing.
- If you have neither: write the exact commands and file contents, and ask the person to paste them in the pod's
  Jupyter terminal and send you the output.

Uploading big files (LoRAs) is easiest for the person: drag and drop into Jupyter Lab, then unzip in the pod terminal
([guide.md](guide.md#3-upload-the-files)). Some command APIs limit one argument to about 4 KB, so do not
try to push big files through a command line.

## Conversation plan

### 1. Understand the wish (no cost)

First agree the work folder and the chats (see above). Then ask, in one message:
- What do you want to make? (a list in their own words is enough: "5 trees, 3 potions, a stone wall")
- How many variants of each? (default 3)
- Do you have a RunPod account with credit? Do you want me to operate RunPod, or will you click?

Then map each wish to a LoRA and kind with the table in [prompting.md](prompting.md#1-pick-the-lora-and-the-kind).
If a wish fits no LoRA (e.g. a house, a vehicle, a portrait), say so honestly and offer the closest one.

### 2. Write the wish files (no cost)

For each LoRA, write a wish file `kind | description` following [prompting.md](prompting.md#2-write-the-description):
5-15 words, size/shape → material → color → 1-2 details, no style words, no backgrounds, no names of existing
game items. Use `prompts/<lora>/examples.txt` (20 example wishes per LoRA) as the model for style and length.
Show the list to the person and let them change it.

Turn it into prompt files: `python tools/make_prompts.py <lora> <wishes.txt> <prompts.txt> --variants 3`.
If you cannot run it, build the lines yourself from the templates in [loras.md](loras.md); copy the layout text
character for character and give each line its own `--d` seed.

Check: every line starts with the LoRA's trigger, ends with `--d <number>`, and the size is 1024×1024
(walk LoRAs: 1152×768 monsters-small, 1536×1024 monsters-medium and outfits, 1920×1280 large monsters).

### 3. Create the pod (costs money: ask first)

**Before the first pod is chosen, show the price list.** Take the rows of
[expected generation prices](guide.md#expected-generation-prices) for the image sizes the person's LoRAs use, for
all three GPUs (A40, L40S, RTX PRO 6000), and show them as a short table. Then estimate their job on each GPU:
<N> images × seconds per image + setup (2-10 min) + model loading (0.5-1.5 min per run), and the price.

Recommend the A40 by default (cheapest per image); the L40S or RTX PRO 6000 only when time matters.
Say: "I will rent an A40 at about $0.59 per hour. Setup plus <N> images will take about <T> minutes, so about
$<X>. OK?" Wait for a clear yes. Prices change: if you can read the current price in RunPod, use it.

Create it with the settings in [guide.md](guide.md#2-create-a-pod): image
`runpod/pytorch:2.1.0-cu1320-torch280-ubuntu2404`, container disk ≥ 60 GB, a volume at `/workspace`,
ports 8888 and 22.

Check: the pod status is *Running* and Jupyter (port 8888) opens.

### 4. Upload (the person usually does this)

Into `/workspace`: `pod/`, the prompt files, and the LoRA file(s) into `loras/` (`Krea2-PixelArt-<lora>.safetensors`).

Check: `ls -la /workspace/pod /workspace/loras/` shows the scripts and `.safetensors` files of about 0.9 GB.

### 5. Setup

Run `cd /workspace && nohup sh pod/setup_pod.sh > setup.out 2>&1 &`.

Check every minute or two: `tail -2 /root/models/setup.log`. Done at `SETUP_OK` (2-10 min).

### 6. Generate

Run `cd /workspace && nohup sh pod/generate.sh loras/Krea2-PixelArt-<lora>.safetensors <prompts.txt> results/<run> > gen.out 2>&1 &`.

Check: `tail -3 results/<run>/generate.log`; done at `GEN_END rc=0`. Then
`ls results/<run>/*.png | wc -l` must equal the number of lines in the prompt file.

Tell the person how to look at the images (Jupyter file browser, double-click a PNG) and ask which ones they like.

### 7. Adjust (optional)

Use the table in [prompting.md](prompting.md#4-look-at-the-results-and-adjust). Change descriptions, add variants,
or try strength 0.7. Generate again into a new folder (`results/<run>-2`).

### 8. Download and post-process

Zip and download the results ([guide.md](guide.md#7-download-the-results)). Shrink to game size as described in
[postprocessing.md](postprocessing.md). For walk cycles, make east and west by transposition.

### 9. Stop the pod

Say: "We are done generating. Shall I stop the pod now? Your files on /workspace stay; the model download will
have to be repeated next time (2-10 minutes)." Stop it on yes, then confirm its status is *Exited*.

## Message style

- Short sentences, no jargon. Explain a term the first time ("a pod is a rented computer with a GPU").
- After each step, one line: what happened, what comes next.
- Ask one question at a time.
