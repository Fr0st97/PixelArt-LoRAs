# Start here

You do not need to know anything about AI or servers. An AI assistant (Claude, ChatGPT or similar) can read this
repository and guide you step by step, or do most of the work for you.

## Option A: your AI can read files or links

Give it this repository (a link, or upload the folder) and paste this message:

> I want to make pixel art game sprites with the PixelArt LoRAs. Read START_HERE.md and docs/ai-operator.md in this
> repository and guide me through the whole process. I am a beginner. Ask me before anything that costs money.

## Option B: your AI can only read what you paste

Paste the message above, then paste the content of these files, in this order:

1. `docs/ai-operator.md`
2. `docs/guide.md`
3. `docs/prompting.md`
4. `docs/loras.md`
5. `docs/postprocessing.md`

If you split the work into three chats (below), each chat needs only its own files: the list is in
`docs/ai-operator.md`, section "Propose three chats".

The assistant will first ask where to keep your files (a work folder on your computer) and suggest splitting the
work into three chats: one writes prompts, one runs the GPU pod, one turns images into game sprites. Each chat
keeps to its own job, and they share notes through a `WORK.md` file in the work folder.

## What you will need

- A RunPod account with about $5-10 of credit (runpod.io). The AI will ask before spending anything.
  Account, credit and the console are explained in [docs/guide.md](docs/guide.md#runpod-account-and-console).
- Optional: RunPod's plugin for your AI assistant (Claude, ChatGPT and others), so it can start and stop pods
  for you: [how to connect](docs/guide.md#optional-let-your-ai-assistant-operate-runpod).
- The LoRA files: one zip per LoRA (~0.9 GB), shared by the author of this repository; they are not in the
  repository itself.
- About 30-45 minutes for the first run.

## What you will get

PNG images of game sprites drawn by the LoRAs, and after post-processing, transparent sprites at game size
(64×64, 48×48 or 32×32; large monsters 96×96). Examples of what each LoRA draws: [docs/loras.md](docs/loras.md).
