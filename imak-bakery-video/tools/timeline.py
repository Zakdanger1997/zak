#!/usr/bin/env python3
"""Timeline of the i.Mak bakery video (music only, like the reference) -> timeline.json."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
media = json.load(open(os.path.join(ROOT, "assets", "footage.json")))   # [{src, video, in, dur, dx, dy, credit, group}]
LOGO = (0.0, 3.4)
TITLE = (3.0, 6.6)
t = 6.4
foot = []
for f in [m for m in media if m["group"] == "intro"]:
    foot.append({**f, "start": round(t, 2), "end": round(t + f["dur"], 2)}); t += f["dur"]
LINE0 = t + 0.1
LINE = (LINE0, LINE0 + 54.0)
t = LINE[1] - 0.1
for f in [m for m in media if m["group"] == "outro"]:
    foot.append({**f, "start": round(t, 2), "end": round(t + f["dur"], 2)}); t += f["dur"]
END = (t - 0.2, t + 4.0)
TOTAL = round(END[1], 2)
C = "assets/cards/"
stations = [
    {"name": "Feeding system", "t0": 7.4, "t1": 13.6, "cards": [
        {"img": C + "3d-iram.png", "s": "IR Series", "d": "Helical geared motor units"}]},
    {"name": "Extruder", "t0": 19.4, "t1": 25.6, "cards": [
        {"img": C + "3d-ma.png", "s": "MAE / MKE Series", "d": "Monobloc extruder gear units"},
        {"img": C + "motor.png", "s": "i.Mak motors", "d": "Three-phase asynchronous motors"}]},
    {"name": "Ovens, dryers and conveyors", "t0": 31.4, "t1": 37.6, "cards": [
        {"img": C + "3d-irsdm.png", "s": "IRSD Series", "d": "Helical worm geared motor units"}]},
    {"name": "Spiral freezer", "t0": 43.4, "t1": 49.6, "cards": [
        {"img": C + "3d-irkm.png", "s": "IRK Series", "d": "Helical bevel geared motor units"},
        {"img": C + "motor.png", "s": "i.Mak motors", "d": "Three-phase asynchronous motors"}]},
]
segs = {"logo": LOGO, "title": TITLE, "line": LINE, "end": END}
json.dump({"total": TOTAL, "fps": 30, "dir": os.environ.get("LINEDIR", "line"), "segments": segs, "footage": foot, "stations": stations},
          open(os.path.join(ROOT, "timeline.json"), "w"), indent=1)
print("total", TOTAL, "line", LINE)
