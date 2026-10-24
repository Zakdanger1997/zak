#!/usr/bin/env bash
# Build the narration track from timeline.json and mux it with the rendered frames.
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
import json, subprocess
tl = json.load(open('timeline.json', encoding='utf-8'))
inputs, filt, labels = [], [], []
for i, sc in enumerate(tl['scenes']):
    inputs += ['-i', sc['audio']]
    ms = int(round(sc['offset'] * 1000))
    filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}|{ms}[a{i}]")
    labels.append(f"[a{i}]")
n = len(tl['scenes'])
filt.append("".join(labels) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={tl['total']},atrim=0:{tl['total']},loudnorm=I=-16:TP=-1.5:LRA=11[out]")
subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', '48000', '-ac', '2', 'voice.wav'], check=True)
PY
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i frames/f%05d.jpg -i voice.wav \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -shortest -movflags +faststart gearbox_explainer.mp4
echo "wrote gearbox_explainer.mp4"
