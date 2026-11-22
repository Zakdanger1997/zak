#!/bin/sh
# Join the rendered video parts, add the i.Mak logo card in the top-right corner
# and mux the narration -> gearbox_oil_explainer.mp4
set -e
cd "$(dirname "$0")"
[ -f brand/logo_card.png ] || python3 brand/make_card.py brand/imak_logo.png brand/logo_card.png
(cd parts && ls part*.mp4) | sort -V | sed "s/^/file '/;s/$/'/" > parts/list.txt
ffmpeg -y -v error -f concat -safe 0 -i parts/list.txt -loop 1 -i brand/logo_card.png -i voice.wav \
  -filter_complex "[1:v]format=rgba,fade=in:st=0.2:d=0.5:alpha=1[logo];[0:v][logo]overlay=x=W-w-24:y=36:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -r 30 -c:a aac -b:a 192k -shortest -movflags +faststart gearbox_oil_explainer.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 gearbox_oil_explainer.mp4
