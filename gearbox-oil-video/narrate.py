"""Voice the nine narration lines with edge-tts and save word timings to narration.json."""
import json, os, re, subprocess

VOICE = os.environ.get('VOICE', 'en-US-ChristopherNeural')
RATE = '+10%'
LINES = [
    "What if your gearbox leaks just a few drops of oil a day? Does it really matter?",
    "Most leaks start right here, at the output shaft seal. Its rubber lip rides on a spinning shaft, and once it hardens or the shaft wears a groove, oil creeps out.",
    "The hidden cause is pressure. A running gearbox heats up, the air inside expands, and if the breather is blocked, that pressure pushes oil past the seals.",
    "The fix: fit a new seal on a clean, smooth shaft, and move the breather to the highest port, so the gearbox can breathe.",
    "But the highest port depends on how it is mounted. This foot-mounted unit fits six positions, P1 to P6, and the oil level moves with every one.",
    "Our IR 93 takes eight litres in P1, but ten litres in P4, with the motor standing up. So fill it to the level plug, never by guess.",
    "Too little oil, and the upper gears and bearings run dry. Metal touches metal, and wear multiplies.",
    "Too much is not safer. The gears churn through it and waste power as heat, and as a rule of thumb, ten degrees hotter can cut oil life in half.",
    "So stop the leak, keep the breather on top, and fill to the right level for your position. A few drops today, or a new gearbox tomorrow.",
]

import asyncio, edge_tts

async def voice(text, mp3):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary='WordBoundary',
                                proxy=os.environ.get('HTTPS_PROXY'))
    words = []
    with open(mp3, 'wb') as f:
        async for ch in comm.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                t0 = ch['offset'] / 1e7
                words.append({'t0': round(t0, 3), 't1': round(t0 + ch['duration'] / 1e7, 3), 'w': ch['text']})
    return words

os.makedirs('audio', exist_ok=True)
out = []
for i, text in enumerate(LINES, 1):
    mp3 = f'audio/line{i:02d}.mp3'
    words = asyncio.run(voice(text, mp3))
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                         '-of', 'csv=p=0', mp3]).decode().strip())
    out.append({'n': i, 'text': text, 'dur': round(dur, 3), 'words': words})
    print(i, round(dur, 2), len(words), 'words')
json.dump(out, open('narration.json', 'w', encoding='utf-8'), indent=1)
print('total speech', round(sum(o['dur'] for o in out), 1))
