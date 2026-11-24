# Speed tests: Krea-2 Turbo locally and on an A40 (2026-11-24)

Measurements from one session: locally on an RTX 4070 SUPER and on a RunPod A40. Two questions: can a better model
than GGUF Q4 run locally in reasonable time, and can bf16 on a pod be made faster without changing the weights.

## Conclusions

- Locally, `int8_convrot` in ComfyUI is 2.3-2.6 times faster than Q4_K_M and needs no extra settings. It also runs
  with the card's memory limited to 8 and 6 GB.
- On the A40 the musubi-tuner script loses about 5 s per image moving the text encoder. Encoding all prompts once
  at the start saves 28% at 1024x1024 and 17% at 1536x1024, and the image is pixel-identical.
- A 3072x3072 sheet on bf16 goes from 233-237 s to 164-166 s (30%): no block swap, prompts encoded at the start,
  and the VAE decoder computed with 2D convolutions.
- The `flash` and `xformers` attention backends and a newer PyTorch give 0-2%. `torch.compile` gives about 17% on
  sampling. Each of these makes the image no longer pixel-identical.
- On the A40 in ComfyUI, int8 is 20-25% faster than bf16, and fp8 gives nothing.
- On the same seed int8 is closer to bf16 than fp8. Q4 is further from bf16 than int8 on all 3 compared sheets.

## Setup

| | Local | Pod |
|---|---|---|
| GPU | RTX 4070 SUPER 12 GB | A40 46 GB, RunPod Secure, EU-SE-1 |
| RAM | 31 GB | 50 GB (container limit) |
| Software | ComfyUI portable 0.46.0, PyTorch 2.14.1+cu130 | musubi-tuner 0.3.6 on PyTorch 2.8.0+cu129; ComfyUI 0.46.0 in a separate venv on PyTorch 2.14.1+cu130 |
| Text encoder | `qwen3vl_4b_fp8_scaled` | `qwen3vl_4b_bf16` |
| VAE | `qwen_image_vae` | `qwen_image_vae` |

Common settings: Krea-2 Turbo, 8 steps, CFG 1, `euler` + `simple` in ComfyUI, one image per prompt.

Models (file list checked on 2026-11-24):

| File | Size | Used |
|---|---|---|
| [krea2_turbo_bf16.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_bf16.safetensors) | 26.3 GB | pod |
| [krea2_turbo_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_int8_convrot.safetensors) | 13.5 GB | local, pod |
| [krea2_turbo_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors) | 13.1 GB | local, pod |
| [krea2_turbo-Q4_K_M.gguf](https://huggingface.co/vantagewithai/Krea-2-Turbo-GGUF/resolve/main/krea2_turbo-Q4_K_M.gguf) | 7.5 GB | local |
| [qwen3vl_4b_bf16.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_bf16.safetensors) | 8.9 GB | pod (text encoder) |
| [qwen3vl_4b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors) | 5.2 GB | local (text encoder) |
| [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors) | 0.25 GB | local, pod |

musubi-tuner: <https://github.com/kohya-ss/musubi-tuner>.

Test sets:

| Set | Prompts | Size | LoRA and strength |
|---|---|---|---|
| walls | 3 seeds | 1024x1024 | walls, 1.0 |
| character | 3 seeds, 3x2 walking sheet | 1536x1024, on the pod also 1024x1024 | outfits, 0.7 |
| large objects | 10 seeds | 1024x1024, single runs at 2048x2048 and 3072x3072 | unreleased LoRA, 1.0 |
| sprite sheet | 2 prompts | 3072x3072 | unreleased LoRA, 1.0 |

## How it was measured

- ComfyUI, locally and on the pod: a script sends the workflow through the ComfyUI API, measures the time from
  submit to finished image and reads the peak GPU memory from `nvidia-smi` once per second. The time includes
  prompt encoding, model reloads and decoding. The first image after a model change includes loading the model
  and is not part of the ranges below.
- musubi-tuner on the pod: a script built on the functions of `krea2_generate_image.py`, with encoding, sampling
  and decoding timed separately after `torch.cuda.synchronize()`.
- Image agreement: absolute difference per channel (0-255), maximum and mean, between files from the same prompt
  and seed.
- The number of images per variant is small (usually 3; at 3072x3072 1-2), so the ranges show spread, not
  statistics.

## Local: Q4, int8, fp8

The only workflow change: the int8 and fp8 files are loaded with `UNETLoader`, GGUF with `UnetLoaderGGUF`. Text
encoder, VAE, LoRA and sampler settings stay the same. Time per image, ComfyUI with no extra options:

| Set | Q4_K_M | int8 | fp8_scaled |
|---|---|---|---|
| walls 1024x1024 | 28-34 s | 11-12 s | 15-17 s |
| large objects 1024x1024 | 34-88 s (log from 2 days earlier) | 10-14 s | 15 s |
| character 1536x1024 | 40-43 s | 17-19 s | 22-23 s |
| large object 2048x2048 | not run | 50 s | 66 s |
| large object 3072x3072 | not run | 172 s | not run |
| sprite sheet 3072x3072 | not run | 173-174 s (one of 23 sheets took 193 s) | not run |

- Peak GPU memory: about 11.0-11.4 GB at 1024x1024 and 1536x1024, 11.6-11.9 GB at 2048x2048 and 3072x3072.
- Sampling step from the ComfyUI log: int8 1.07 s at 1024x1024, 5.9 s at 2048x2048, 20.6 s at 3072x3072;
  Q4 3.24 s at 1024x1024.
- ComfyUI keeps the whole model in RAM (12.9 GB) and loads onto the card as much as fits.

### Limited GPU memory

ComfyUI started with `--reserve-vram N` to simulate a smaller card. Without ComfyUI, other programs used 505 MiB.

| Reserve | Equivalent card | 1024x1024 | 1536x1024 | 2048x2048 | Peak |
|---|---|---|---|---|---|
| none | 12 GB | 11-12 s | 17-19 s | 50 s | 11.3 GB |
| 5 GB | | 14 s | 19 s | 57 s | 8.1-8.7 GB |
| 6.3 GB | 8 GB | 14 s | 19-20 s | 57 s | 6.8-7.3 GB |
| 8.3 GB | 6 GB | 15 s | 20 s | not run | 4.8 GB |

- Images with a reserve of 6.3 and 8.3 GB are pixel-identical to images without a reserve.
- A 3072x3072 sheet with a reserve of 6.3 GB took 188 s, but the peak was 11.9 GB. On a real 8 GB card this size
  is untested.
- This is a simulation on a 4070 SUPER. A real 8 GB or 6 GB card usually has a slower chip, so times will be
  longer.

## A40 pod: bf16 in musubi-tuner

Time per image and its parts:

| Variant | Size | Encoding | Sampling | Decoding | Total | Peak |
|---|---|---|---|---|---|---|
| stock script | 1024x1024 | 5.4-6.4 s | 11.3-11.6 s | 0.3-0.4 s | 17.0-18.0 s | 32.6 GB |
| stock script | 1536x1024 | 4.5-5.0 s | 17.3-17.5 s | 0.4 s | 22.3-22.9 s | 32.6 GB |
| encode at start | 1024x1024 | 1.0 s | 11.3 s | 0.3-0.4 s | 12.6-12.7 s | 28.3 GB |
| encode at start | 1536x1024 | 1.0 s | 17.3-17.4 s | 0.4 s | 18.8 s | 30.4 GB |
| stock script, `--blocks_to_swap 16` | 3072x3072 | 6.2-7.8 s | 172-177 s | 52.6-54.1 s | 233-237 s | 41.6 GB |
| encode at start, no swap, VAE after removing the DiT | 3072x3072 | 3.1 s | 157-161 s | 52.5-52.7 s | 213-217 s | 30.7 GB |
| the same + 2D decoder | 3072x3072 | 3.0 s | 158-161 s | 2.3-2.4 s | 164-166 s | 30.0 GB |

- The stock script moves the text encoder (8 GB) to the GPU and back for every prompt. Encoding all prompts once
  costs 6 s for the whole batch.
- Images with encoding at the start and no block swap are pixel-identical to the stock script (difference 0 on
  all 8 images).
- Model load: 242 s with 16 swapped blocks (one measurement). Without swap, 19 to 137 s in later runs, depending
  on how much of the file was still in the disk cache.

### Patch for the `--from_file` loop

Checked with a real run of `krea2_generate_image.py` and its patched copy on 6 prompts:

| | Stock | Patched |
|---|---|---|
| Whole run including model load | 155 s | 122 s |
| Images | | pixel-identical |

```python
jobs = [apply_overrides(args, parse_prompt_line(l.strip()))
        for l in lines if l.strip() and not l.startswith("#")]
for j in jobs:
    if j.seed is None:
        j.seed = random.randint(0, 2**32 - 1)

encoder.to(te_device)                      # once, not for every prompt
with torch.no_grad():
    embeds = [encode_prompts(encoder, [j.prompt], [j.negative_prompt],
                             cfg=j.guidance_scale > 1.0) for j in jobs]
encoder.to("cpu"); gc.collect(); torch.cuda.empty_cache()

for j, (txt, txtmask, untxt, untxtmask) in zip(jobs, embeds):
    images = sample(dit, ae, txt, txtmask, untxt=untxt, untxtmask=untxtmask,
                    device=device, dtype=dtype, width=j.width, height=j.height,
                    steps=j.steps, cfg_scale=j.guidance_scale, seed=j.seed,
                    y1=j.y1, y2=j.y2, mu=j.mu)
    save_images(images, args.save_path, j.seed)
```

It replaces the `for line in lines:` loop in the `if args.from_file:` branch of `main()` (musubi-tuner 0.3.6).
One image per prompt; the `--i` option is ignored. The scripts in `pod/` of this repository do not include this
change yet.

### VAE decoder

The decoder in musubi-tuner computes a single frame with causal 3D convolutions, padding zeros in front on the
time axis. For one frame this equals a 2D convolution with the last temporal slice of the kernel, on the same
weights. Applied as a patch before decoding:

```python
import torch.nn.functional as F
from musubi_tuner.qwen_image.qwen_image_autoencoder_kl import QwenImageCausalConv3d as K

old_forward = K.forward

def conv2d_forward(self, x, cache_x=None):
    kt = self.kernel_size[0]
    if cache_x is None and x.shape[2] == 1 and self._padding[4] == kt - 1 and self.stride[0] == 1:
        y = F.conv2d(x[:, :, 0], self.weight[:, :, -1], self.bias, stride=self.stride[1:],
                     padding=(self._padding[2], self._padding[0]), dilation=self.dilation[1:],
                     groups=self.groups)
        return y.unsqueeze(2)
    return old_forward(self, x, cache_x)

K.forward = conv2d_forward
```

Decoder alone on the latent of a 3072x3072 sheet:

| Variant | Time | Peak | Difference from stock |
|---|---|---|---|
| stock | 52.5 s | 30.6 GB | |
| stock + `cudnn.benchmark` | 52.4 s (first 92 s) | 30.6 GB | mean 0.168, max 49 |
| 2D convolution | 2.3 s (first 2.6 s) | 28.9 GB | mean 0.168, max 54 |
| 2D convolution + `cudnn.benchmark` | 2.3 s (first 7.7 s) | 28.9 GB | mean 0.168, max 51 |

- The difference is the same size as when only the cuDNN convolution algorithm changes, so it is rounding. On a
  3072x3072 sheet (9.4 million pixels) 612 pixels differ by more than 8 levels and 14 by more than 32.
- The decoder needs about 29 GB, so at 3072x3072 on a 48 GB card the DiT has to be removed from the GPU before
  decoding.
- At 1024x1024 and 1536x1024 decoding takes 0.3-0.4 s; the 2D variant was not measured there.

### Attention backends, newer PyTorch, compilation

All with encoding at the start. Image difference is against the stock script.

| Variant | 1024x1024 total | 1536x1024 total | Sampling 1024x1024 | Mean image difference |
|---|---|---|---|---|
| `--attn_mode torch` (reference) | 12.6-12.7 s | 18.8 s | 11.3 s | 0 |
| `--attn_mode flash` (flash-attn 2.8.1) | 12.4-12.5 s | 18.5-18.6 s | 11.1 s | 1.6-3.6 |
| `--attn_mode xformers` (0.0.32.post2) | 12.6-12.7 s | 18.6-18.8 s | 11.2-11.3 s | 1.9-3.1 |
| PyTorch 2.14.1+cu130 | 12.7-12.8 s | 18.8 s | 11.0-11.1 s | 1.7-4.1 |
| `torch.compile` on the DiT | 10.7 s | 16.0 s | 9.4 s | 2.2-4.6 |

- At a mean difference of 2-5 this is the same image with different details: same weights and precision,
  different order of operations, and sampling amplifies small rounding differences. Visually the quality is the
  same.
- `torch.compile`: the first images at a given size take longer (1024x1024: 33.8 s and 17.0 s, only the third
  10.7 s; 1536x1024: first 27.2 s). Compilation at 3072x3072 and together with the 2D decoder was not measured.

## A40 pod: ComfyUI with bf16, int8 and fp8

Same prompts, seeds and LoRAs, bf16 text encoder in all three:

| Model | 1024x1024 | 1536x1024 | 3072x3072 | Peak (small / 3072x3072) |
|---|---|---|---|---|
| bf16 | 11-12 s | 17 s | 161-164 s | 33.5-34.8 / 39.9 GB |
| fp8_scaled | 12 s | 18 s | 161-162 s | 21.8-22.9 / 32.9 GB |
| int8_convrot | 9 s | 13 s | 135-136 s | 21.9-23.2 / 33.2 GB |

- ComfyUI with bf16 is 31% faster at 3072x3072 than the stock musubi-tuner script and equal to musubi-tuner
  after the changes above.
- ComfyUI draws noise differently from musubi-tuner, so the same seed gives a different image. ComfyUI results
  cannot be compared pixel by pixel with musubi-tuner.
- ComfyUI on PyTorch 2.8.0+cu129 warned at start that performance is poor with CUDA below 13.0, so it got its own
  venv with PyTorch 2.14.1+cu130. It was not measured on the older PyTorch.

Quality against bf16, mean difference per channel:

| Image | int8 | fp8_scaled |
|---|---|---|
| character 1024x1024, seed 78501 | 3.7 | 12.8 |
| character 1024x1024, seed 78502 | 3.0 | 6.8 |
| character 1536x1024, seed 78501 | 6.9 | 10.3 |
| character 1536x1024, seed 78503 | 4.1 | 6.3 |
| sprite sheet 3072x3072, prompt 1 | 6.4 | 10.4 |
| sprite sheet 3072x3072, prompt 2 | 8.2 | 26.6 |

The composition is the same in all three.

### Q4, int8 and bf16 on the same seeds

Character set at 1536x1024, seeds 78501-78503, outfits LoRA at 0.7. Q4 and int8 from the local tests, int8 and
bf16 from ComfyUI on the A40. Mean difference per channel against bf16 from the A40:

| Seed | Q4 local | int8 local | int8 on A40 |
|---|---|---|---|
| 78501 | 10.7 | 9.3 | 6.9 |
| 78502 | 12.1 | 5.9 | 8.6 |
| 78503 | 8.4 | 6.7 | 4.1 |

- The composition is the same in all four. In a 1:1 crop (seed 78501) Q4 has a different face and stray red
  pixels on the chest; int8 has small red spots on the feet that bf16 does not have.
- The local images used the `fp8_scaled` text encoder, the A40 images the `bf16` one. Part of the difference in
  the local columns therefore comes from the encoder, not the model. The clean model comparison is int8 on the
  A40 against bf16.
- These are 3 images: an example, not statistics.

## Pod preparation

- Downloading the five model files (62 GB) with `aria2c -x 8 -s 8` took about 50 s; the whole preparation with
  musubi-tuner and ComfyUI took 72 s.

## Not tested

- Cards other than the RTX 4070 SUPER and the A40.
- A real 8 GB or 6 GB card; a 3072x3072 sheet within an 8 GB limit.
- `torch.compile` at 3072x3072 and together with the 2D decoder; the 2D decoder at small sizes.
- Krea-R-Turbo in int8 (Comfy-Org publishes int8 only for plain Turbo).
- Generating while a game or another program uses the card.
- The `--fast` option in ComfyUI.
