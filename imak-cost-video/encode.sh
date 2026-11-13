#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-imak_cost_of_selection_1080sq.mp4}"
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i frames/f%05d.jpg \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 -movflags +faststart -an "$OUT"
echo "wrote $OUT"; ls -lh "$OUT"
