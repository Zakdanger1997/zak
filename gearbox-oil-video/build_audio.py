"""Lay the narration lines on the same timeline as scene.html (0.25 s lead, 0.45 s tail) -> voice.wav"""
import json, subprocess
LEAD, TAIL = 0.25, 0.45
nar = json.load(open('narration.json'))
inputs, filt, t = [], [], 0.0
for i, l in enumerate(nar):
    inputs += ['-i', f'audio/line{l["n"]:02d}.mp3']
    ms = int(round((t + LEAD) * 1000))
    filt.append(f'[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]')
    t += LEAD + l['dur'] + TAIL
mix = ''.join(f'[a{i}]' for i in range(len(nar)))
filt.append(f'{mix}amix=inputs={len(nar)}:normalize=0,apad,atrim=0:{t:.3f},loudnorm=I=-15:TP=-1.5:LRA=7[out]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', '-ar', '48000', 'voice.wav'], check=True)
print('voice.wav', round(t, 2), 's')
