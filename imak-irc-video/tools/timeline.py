#!/usr/bin/env python3
"""Lay out the IRC video: voice lines, picture segments and on-screen text, all in seconds.

Usage: python3 tools/timeline.py      -> timeline.json (read by tools/compose.js and tools/soundtrack.py)
Picture segments name a source: a rendered shot (render/<shot>/####.png at 24 fps, with the source
time range to play), a still (lineup) or photos (Ken Burns), and the on-screen titles for it.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
L = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "audio", "lines.json")))["lines"]}

GAP = {"hook": 0.55, "intro": 0.35, "housing": 0.35, "sizes": 0.45, "ratios": 0.7, "spline": 0.35,
       "drum": 0.4, "lift": 0.45, "apps": 0.4, "options": 0.9, "end": 0.0}
order = ["hook", "intro", "housing", "sizes", "ratios", "spline", "drum", "lift", "apps", "options", "end"]
t = 0.8
voice = []
for k in order:
    cap = re.sub(r"(\d) (Nm|kW|t|m/min|HRC|to)\b", "\\1\u00a0\\2", L[k]["caption"]).replace(" – ", "\u00a0–\u00a0").replace("IRC ", "IRC\u00a0")
    voice.append({"id": k, "file": L[k]["file"], "start": round(t, 3), "dur": L[k]["dur"],
                  "words": [[round(t + a, 3), round(t + b, 3), w] for a, b, w in L[k]["words"]], "caption": cap})
    t += L[k]["dur"] + GAP[k]
S = {v["id"]: v["start"] for v in voice}
E = {v["id"]: v["start"] + v["dur"] for v in voice}
TOTAL = round(E["end"] + 2.6, 2)


def seg(start, end, **kw):
    return {"start": round(start, 3), "end": round(end, 3), **kw}


segments = [
    # source ranges are in seconds of the 24 fps renders: dark 0-4, studio 0-8, spline 0-4, hoist 0-6, hoistwide 0-6
    seg(0, S["intro"] - 0.1, shot="dark", src=(0.0, 3.96), titles=[
        {"t": "hook", "text": "UP TO <b>75 t</b>", "sub": "ON ONE GEARBOX", "from": S["hook"] + 0.2}]),
    seg(S["intro"] - 0.1, S["sizes"] - 0.15, shot="studio", src=(0.0, 7.96), titles=[
        {"t": "title", "text": "IRC SERIES", "sub": "HOIST DRIVE GEARED MOTOR", "from": S["intro"] + 0.4, "to": S["housing"] - 0.2},
        {"t": "spec", "text": "3", "sub": "HELICAL STAGES", "from": S["housing"] + 0.1, "to": S["sizes"] - 0.3},
        {"t": "spec2", "text": "GG22", "sub": "CAST-IRON MONOBLOC", "from": S["housing"] + 1.6, "to": S["sizes"] - 0.3}]),
    seg(S["sizes"] - 0.15, S["ratios"] - 0.2, still="lineup", titles=[
        {"t": "title", "text": "7 SIZES", "sub": "IRC 63 – IRC 143", "from": S["sizes"] + 0.2},
        {"t": "top2", "text": "29,771 Nm", "sub": "MAX. OUTPUT TORQUE", "from": S["sizes"] + 4.4}]),
    seg(S["ratios"] - 0.2, S["spline"] + 0.4, shot="spline", src=(0.0, 0.66), titles=[
        {"t": "big", "text": "24 – 201", "sub": "RATIOS", "from": S["ratios"] + 0.1}]),
    seg(S["spline"] + 0.4, S["spline"] + 7.8, shot="spline", src=(0.66, 3.96), titles=[
        {"t": "label", "text": "DIN 5480 SPLINE", "sub": "HARDENED 50 HRC", "from": S["spline"] + 0.6, "to": S["spline"] + 4.6},
        {"t": "label2", "text": "DRUM CONNECTION FLANGE", "sub": "SLIDES STRAIGHT ON", "from": S["spline"] + 4.8}]),
    seg(S["spline"] + 7.8, S["lift"] - 0.3, shot="hoist", src=(0.0, 5.96), titles=[
        {"t": "label", "text": "LARGE DRUM", "sub": "LONGER ROPE LIFE", "from": S["drum"] + 2.4, "to": S["drum"] + 6.4},
        {"t": "label", "text": "TAPERED ROLLER BEARINGS", "sub": "CARRY THE DRUM LOAD", "from": S["drum"] + 6.6}]),
    seg(S["lift"] - 0.3, S["apps"] - 0.15, shot="hoistwide", src=(0.0, 5.96), titles=[
        {"t": "stack", "lines": [["0.37 – 90", "kW"], ["0.5 – 75", "t"], ["44", "m/min"]], "from": S["lift"] + 0.3}]),
    seg(S["apps"] - 0.15, S["options"] - 0.1, photos=True, titles=[
        {"t": "title", "text": "CRANES · HOISTS · WINCHES", "sub": "DUTY CLASSES UP TO M8", "from": S["apps"] + 0.3}]),
    seg(S["options"] - 0.1, S["end"] - 0.25, shot="dark", src=(1.6, 3.96), titles=[
        {"t": "list", "lines": ["SINGLE / DOUBLE BRAKE", "ENCODER", "FORCED COOLING FAN", "i.Mak MOTORS 0.37 – 90 kW"], "from": S["options"] + 0.2}]),
    seg(S["end"] - 0.25, TOTAL, endcard=True),
]

json.dump({"total": TOTAL, "fps": 30, "voice": voice, "segments": segments}, open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
print("total", TOTAL, "s")
for s_ in segments:
    print(f"{s_['start']:6.2f} – {s_['end']:6.2f}  {s_.get('shot') or s_.get('still') or ('photos' if s_.get('photos') else 'endcard')}")
