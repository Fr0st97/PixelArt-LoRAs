#!/bin/sh
# Generate images with one PixelArt LoRA on Krea-2 Turbo.
#
# Usage:  sh generate.sh <lora.safetensors> <prompts.txt> <output_dir> [multiplier]
#   lora.safetensors  one LoRA file (e.g. /workspace/loras/Krea2-PixelArt-flora.safetensors)
#   prompts.txt       one prompt per line, built by tools/make_prompts.py, see docs/guide.md ("Writing prompts")
#   output_dir        created if missing; PNG files are named <date>-<time>_<seed>.png
#   multiplier        LoRA strength, default 1.0 (0.6-0.8 follows the prompt more, keeps less of the style)
#
# Needs a pod prepared with setup_pod.sh. Writes output_dir/lora.txt (which LoRA and prompts made the images;
# PNG files carry no metadata) and the log output_dir/generate.log. Ends with "GEN_END rc=0" in the log.
set -u
LORA=$1; PROMPTS=$2; OUT=$3; MULT=${4:-1.0}
MODELS=${MODELS:-/root/models}
export HF_HOME=/root/.cache/huggingface
[ -f "$LORA" ] || { echo "LoRA not found: $LORA"; exit 1; }
[ -f "$PROMPTS" ] || { echo "prompt file not found: $PROMPTS"; exit 1; }
mkdir -p "$OUT"; LOG="$OUT/generate.log"

cat > "$OUT/lora.txt" <<EOF
lora_file: $(basename "$LORA")
multiplier: $MULT
prompts: $PROMPTS
seeds: $(grep -oE -- '--d [0-9]+' "$PROMPTS" | awk '{print $2}' | paste -sd, -)
date: $(date -u '+%Y-%m-%d %H:%M UTC')
EOF

echo "GEN_START $(date)" >> "$LOG"
cd /opt/musubi-tuner && python3 src/musubi_tuner/krea2_generate_image.py --from_file "$PROMPTS" \
  --dit $MODELS/diffusion_models/krea2_turbo_bf16.safetensors \
  --vae $MODELS/vae/qwen_image_vae.safetensors \
  --text_encoder $MODELS/text_encoders/qwen3vl_4b_bf16.safetensors \
  --lora_weight "$LORA" --lora_multiplier "$MULT" \
  --attn_mode torch --save_path "$OUT" >> "$LOG" 2>&1
echo "GEN_END rc=$? $(date)" >> "$LOG"
tail -1 "$LOG"
