#!/usr/bin/env python3
"""Voice line timing for the collage company video -> timeline.json (scenes start with their line)."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
L = json.load(open(os.path.join(ROOT, "audio", "lines.json")))["lines"]
GAP = {"hook": 0.6, "y1973": 0.5, "y1983": 0.5, "y1998": 0.45, "y2012": 0.45, "y2019": 0.45, "y2022": 0.4,
       "y2023": 0.4, "y2024": 0.6, "today": 0.5, "rank": 0.6, "sectors": 0.6, "trust": 0.7, "end": 0}
t = 1.4
voice = []
for l in L:
    voice.append({"id": l["id"], "file": l["file"], "start": round(t, 3), "dur": l["dur"], "caption": l["caption"],
                  "words": [[round(t + a, 3), round(t + b, 3), w] for a, b, w in l["words"]]})
    t += l["dur"] + GAP[l["id"]]
total = round(voice[-1]["start"] + voice[-1]["dur"] + 2.8, 2)
# soundtrack.py expects segments: one per scene
segs = [{"start": v["start"] - (0.3 if i else 1.4), "end": (voice[i + 1]["start"] - 0.3) if i + 1 < len(voice) else total,
         "shot": v["id"]} for i, v in enumerate(voice)]
json.dump({"total": total, "fps": 30, "voice": voice, "segments": segs}, open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
print("total", total)
for v in voice:
    print(f"{v['start']:6.2f} {v['id']}")
