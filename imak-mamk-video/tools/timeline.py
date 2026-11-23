#!/usr/bin/env python3
"""Lay out the MA/MK video: voice lines, picture segments and on-screen text, in seconds.

Usage: python3 tools/timeline.py      -> timeline.json (read by tools/compose.js and tools/soundtrack.py)
Segments name a rendered shot (render/<shot>/####.png, 24 fps, with the source time range to play), a still
(render/<still>_still_0000.png, "pan" across or "push" in), or photos (Ken Burns), plus their titles.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
L = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "audio", "lines.json")))["lines"]}

GAP = {"hook": 0.55, "intro": 0.35, "types": 0.4, "sizes": 0.4, "gears": 0.45, "drive": 0.35,
       "backstop": 0.45, "cooling": 0.35, "seal": 0.45, "apps": 0.8, "end": 0.0}
order = ["hook", "intro", "types", "sizes", "gears", "drive", "backstop", "cooling", "seal", "apps", "end"]
t = 0.8
voice = []
for k in order:
    cap = re.sub(r"(\d) (Nm|kW|t|HRC|to)\b", "\\1\u00a0\\2", L[k]["caption"]).replace(" – ", "\u00a0–\u00a0").replace(" : ", "\u00a0:\u00a0")
    voice.append({"id": k, "file": L[k]["file"], "start": round(t, 3), "dur": L[k]["dur"],
                  "words": [[round(t + a, 3), round(t + b, 3), w] for a, b, w in L[k]["words"]], "caption": cap})
    t += L[k]["dur"] + GAP[k]
S = {v["id"]: v["start"] for v in voice}
E = {v["id"]: v["start"] + v["dur"] for v in voice}
TOTAL = round(E["end"] + 2.6, 2)


def seg(start, end, **kw):
    return {"start": round(start, 3), "end": round(end, 3), **kw}


segments = [
    seg(0, S["intro"] - 0.1, shot="dark", src=(0.0, 3.96), titles=[
        {"t": "hook", "text": "<b>70,000</b> Nm", "sub": "24 H A DAY · IN THE DUST", "from": S["hook"] + 0.2}]),
    seg(S["intro"] - 0.1, S["types"] - 0.15, shot="studio", src=(0.0, 7.96), titles=[
        {"t": "title", "text": "MA / MK SERIES", "sub": "HEAVY-DUTY INDUSTRIAL GEARBOXES", "from": S["intro"] + 0.4}]),
    seg(S["types"] - 0.15, S["sizes"] - 0.15, still="duo", mode="push", titles=[
        {"t": "label", "text": "MA", "sub": "PARALLEL SHAFT", "from": S["types"] + 0.1, "cls": "left"},
        {"t": "label2", "text": "MK", "sub": "BEVEL-HELICAL · RIGHT-ANGLE", "from": S["types"] + 2.6, "cls": "right"}]),
    seg(S["sizes"] - 0.15, S["gears"] - 0.2, still="lineup", mode="pan", titles=[
        {"t": "title", "text": "9 SIZES", "sub": "40 – 120", "from": S["sizes"] + 0.2},
        {"t": "top2", "text": "70,000 Nm", "sub": "MAX. OUTPUT TORQUE", "from": S["sizes"] + 3.0}]),
    seg(S["gears"] - 0.2, S["drive"] - 0.2, shot="dark", src=(1.0, 3.96), titles=[
        {"t": "spec", "text": "57 HRC", "sub": "CASE-HARDENED · GROUND", "from": S["gears"] + 0.2},
        {"t": "spec2", "text": "512 : 1", "sub": "MAX. RATIO", "from": S["gears"] + 5.6}]),
    seg(S["drive"] - 0.2, S["backstop"] - 0.2, shot="drive", src=(0.0, 5.96), titles=[
        {"t": "label", "text": "HOLLOW SHAFT", "sub": "SHRINK DISC · NO COUPLING", "from": S["drive"] + 2.4, "to": S["drive"] + 6.0},
        {"t": "label", "text": "TORQUE ARM", "sub": "RUBBER-DAMPED", "from": S["drive"] + 6.2}]),
    seg(S["backstop"] - 0.2, S["cooling"] - 0.2, shot="conveyor", src=(0.0, 5.96), titles=[
        {"t": "label", "text": "BACKSTOP", "sub": "NO ROLL-BACK ON THE INCLINE", "from": S["backstop"] + 0.4}]),
    seg(S["cooling"] - 0.2, S["apps"] - 0.15, shot="steel", src=(0.0, 5.96), titles=[
        {"t": "spec", "text": "648 kW", "sub": "THERMAL CAPACITY", "from": S["cooling"] + 2.0, "to": S["seal"] - 0.2},
        {"t": "spec", "text": "C5", "sub": "CORROSION PROTECTION", "from": S["seal"] + 0.3}]),
    seg(S["apps"] - 0.15, S["end"] - 0.25, photos=True, titles=[
        {"t": "title", "text": "CONVEYORS · CRUSHERS · MILLS", "sub": "MINES · QUARRIES · STEEL PLANTS", "from": S["apps"] + 0.3}]),
    seg(S["end"] - 0.25, TOTAL, endcard=True),
]

END = {"h1": "MA / MK SERIES", "h2": "Heavy-duty industrial gearboxes",
       "p": ["9 sizes · 6,080 – 70,000 Nm · ratios up to 512 : 1", "Producing powerful solutions since 1973"],
       "tag": "MA / MK SERIES"}
json.dump({"total": TOTAL, "fps": 30, "voice": voice, "segments": segments, "end": END},
          open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
print("total", TOTAL, "s")
for s_ in segments:
    print(f"{s_['start']:6.2f} – {s_['end']:6.2f}  {s_.get('shot') or s_.get('still') or ('photos' if s_.get('photos') else 'endcard')}")
