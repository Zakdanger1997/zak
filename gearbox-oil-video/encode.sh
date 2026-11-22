#!/bin/sh
# Join the rendered video parts and mux the narration -> gearbox_oil_explainer.mp4
set -e
cd "$(dirname "$0")"
ls parts/part*.mp4 | sort -V | sed "s/^/file '/;s/$/'/" > parts/list.txt
ffmpeg -y -v error -f concat -safe 0 -i parts/list.txt -i voice.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart gearbox_oil_explainer.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 gearbox_oil_explainer.mp4
