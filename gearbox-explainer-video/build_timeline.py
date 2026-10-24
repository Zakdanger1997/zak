import json, re
nar = json.load(open('narration.json', encoding='utf-8'))
def ts(s):
    s = s.replace(',', '.'); parts = s.split(':'); parts = [float(p) for p in parts]
    return parts[0]*3600 + parts[1]*60 + parts[2] if len(parts) == 3 else parts[0]*60 + parts[1]
scenes = []; total = 0
for o in nar:
    words = []
    cue = None
    for ln in open(f"audio/line{o['n']:02d}.vtt", encoding='utf-8'):
        ln = ln.strip()
        m = re.search(r'([\d:.,]+)\s*-->\s*([\d:.,]+)', ln)
        if m: cue = (ts(m.group(1)), ts(m.group(2))); continue
        if ln and cue and not ln.startswith('WEBVTT'):
            ws = ln.split(); n = len(ws); span = cue[1] - cue[0]
            for k, w in enumerate(ws):
                words.append({'t0': round(cue[0] + span * k / n, 3), 't1': round(cue[0] + span * (k + 1) / n, 3), 'w': w})
            cue = None
    lead = 0.4; tail = 0.6
    dur = round(o['dur'] + lead + tail, 3)
    scenes.append({'n': o['n'], 'dur': dur, 'lead': lead, 'audio': f"audio/line{o['n']:02d}.mp3", 'offset': round(total + lead, 3), 'words': words, 'text': o['text']})
    total += dur
tl = {'scenes': scenes, 'total': round(total, 3), 'fps': 30}
json.dump(tl, open('timeline.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('total', tl['total'], [ (s['n'], s['dur'], len(s['words'])) for s in scenes ])
