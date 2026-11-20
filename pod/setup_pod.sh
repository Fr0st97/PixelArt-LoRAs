#!/bin/sh
# Prepare a fresh RunPod pod for generating images with the PixelArt LoRAs.
#
# Installs musubi-tuner v0.3.6 (kohya-ss) into /opt/musubi-tuner and downloads the Krea-2 models
# from Hugging Face (Comfy-Org/Krea-2) into $MODELS (default /root/models, the pod's local disk).
#
# Usage:  sh setup_pod.sh            # generation only: Turbo model, text encoder, VAE (~35 GB)
#         sh setup_pod.sh --train    # also the Raw model needed for training (~61 GB in total)
#
# Ends with "SETUP_OK" or "SETUP_FAIL ..." in $MODELS/setup.log. Takes 2-10 minutes depending on the
# download speed of the pod's data center.
set -u
MODELS=${MODELS:-/root/models}
LOG=$MODELS/setup.log
BASE=https://huggingface.co/Comfy-Org/Krea-2/resolve/main
export HF_HOME=/root/.cache/huggingface   # must be on local disk (see docs/guide.md, troubleshooting)

mkdir -p $MODELS/diffusion_models $MODELS/text_encoders $MODELS/vae
echo "START $(date)" > $LOG

FILES="diffusion_models/krea2_turbo_bf16 text_encoders/qwen3vl_4b_bf16 vae/qwen_image_vae"
[ "${1:-}" = "--train" ] && FILES="$FILES diffusion_models/krea2_raw_bf16"
for f in $FILES; do
  wget -q -c -O $MODELS/$f.safetensors $BASE/$f.safetensors &
done

if [ ! -d /opt/musubi-tuner ]; then
  (cd /opt && git clone -q https://github.com/kohya-ss/musubi-tuner.git && cd musubi-tuner \
    && git checkout -q v0.3.6 && pip install -e . > $MODELS/pip.log 2>&1) || echo "PIP_FAIL" >> $LOG
fi
wait

# expected file sizes in bytes
ok=1
check() { s=$(stat -c %s "$MODELS/$1.safetensors" 2>/dev/null || echo 0); [ "$s" = "$2" ] || { echo "BAD_SIZE $1 $s (expected $2)" >> $LOG; ok=0; }; }
check diffusion_models/krea2_turbo_bf16 26283332608
check text_encoders/qwen3vl_4b_bf16 8875719384
check vae/qwen_image_vae 253806246
[ "${1:-}" = "--train" ] && check diffusion_models/krea2_raw_bf16 26283332608
grep -q PIP_FAIL $LOG && ok=0
if [ $ok = 1 ]; then echo "SETUP_OK $(date)" >> $LOG; else echo "SETUP_FAIL $(date)" >> $LOG; fi
tail -1 $LOG
