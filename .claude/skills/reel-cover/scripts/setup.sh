#!/usr/bin/env bash
# setup.sh — bootstrap the reel-cover toolchain in a fresh container.
# Idempotent: safe to re-run. Skips work that's already done.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[reel-cover] installing python deps..."
pip install --quiet --timeout 120 Pillow imageio-ffmpeg rembg onnxruntime 2>&1 | tail -1
# Optional (best-effort) transcription. Non-fatal if it fails.
pip install --quiet --timeout 120 faster-whisper 2>&1 | tail -1 || true

# u2net background-removal model. The rembg default source (github releases)
# is often blocked; pull from a HuggingFace mirror instead.
MODEL="$HOME/.u2net/u2net.onnx"
if [ ! -s "$MODEL" ] || [ "$(stat -c%s "$MODEL" 2>/dev/null || echo 0)" -lt 1000000 ]; then
  echo "[reel-cover] fetching u2net model..."
  mkdir -p "$HOME/.u2net"
  for url in \
    "https://huggingface.co/tomjackson2023/rembg/resolve/main/u2net.onnx" \
    "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx" ; do
    curl -sSL -o "$MODEL" "$url" && \
      [ "$(stat -c%s "$MODEL" 2>/dev/null || echo 0)" -gt 1000000 ] && break
  done
fi
echo "[reel-cover] u2net: $(stat -c%s "$MODEL" 2>/dev/null || echo MISSING) bytes"

# Fonts are bundled in assets/fonts. Re-fetch only if missing.
FDIR="$HERE/../assets/fonts"
mkdir -p "$FDIR"
[ -s "$FDIR/Anton-Regular.ttf" ] || curl -sSL -o "$FDIR/Anton-Regular.ttf" \
  "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/anton/Anton-Regular.ttf"
[ -s "$FDIR/Montserrat-ExtraBold.ttf" ] || curl -sSL -o "$FDIR/Montserrat-ExtraBold.ttf" \
  "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"

echo "[reel-cover] ready."
