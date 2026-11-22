#!/usr/bin/env python3
"""Female voiceover for the IRC video (Microsoft Edge neural TTS via edge-tts), one clip per line,
with word timings for the captions.

Usage: python3 tools/voiceover.py [--voice en-US-AvaNeural] [--rate -4%]
Writes audio/line_NN.mp3 and audio/lines.json ([{id, text, file, dur, words:[[start, end, word]]}]).
Every figure comes from the i.Mak IRC catalogue 2024 (C00 2024) and the B00 2025 overview.
"""
import asyncio
import json
import os
import subprocess
import sys

import certifi

# behind an HTTPS-inspecting proxy edge-tts needs the proxy's CA (it pins certifi) and the proxy URL
if os.environ.get("SSL_CERT_FILE"):
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "audio")
A = sys.argv[1:]
VOICE = A[A.index("--voice") + 1] if "--voice" in A else "en-US-AvaNeural"
RATE = A[A.index("--rate") + 1] if "--rate" in A else "+2%"

# (id, spoken text, caption text)
LINES = [
    ("hook", "Up to seventy-five tonnes. Carried by one gearbox.", "Up to 75 tonnes. Carried by one gearbox."),
    ("intro", "This is the Eemak I R C: a crane drum drive, built for one job. Lifting.", "This is the i.Mak IRC – a crane drum drive built for one job: lifting."),
    ("housing", "Three helical stages, in a monobloc cast-iron housing, machined in a single set-up.", "Three helical stages in a monobloc cast-iron housing, machined in one set-up."),
    ("sizes", "Seven sizes, from I R C sixty-three to I R C one forty-three, with up to twenty-nine thousand, seven hundred newton metres of torque.", "Seven sizes, IRC 63 to IRC 143 – up to 29,771 Nm of torque."),
    ("ratios", "And ratios from twenty-four, to two hundred and one.", "Ratios from 24 to 201."),
    ("spline", "The output is a DIN fifty-four eighty spline, hardened to fifty HRC. The drum connection flange slides straight on, so the gearbox drives the rope drum directly.", "DIN 5480 spline output, hardened to 50 HRC. The drum flange slides straight on – a direct drive into the rope drum."),
    ("drum", "A wide centre distance leaves room for a large drum, and a large drum means longer rope life. Long-span tapered roller bearings carry the drum load.", "Wide centre distance → room for a large drum → longer rope life. Tapered roller bearings carry the drum load."),
    ("lift", "With motors from point three seven to ninety kilowatts, the I R C lifts from half a tonne to seventy-five tonnes, at up to forty-four metres per minute.", "0.37 – 90 kW motors · 0.5 – 75 t · up to 44 m/min"),
    ("apps", "Built for overhead cranes, hoists and winches, and selected for crane duty classes up to M8.", "Built for overhead cranes, hoists and winches – duty classes up to M8."),
    ("options", "Single or double brakes, encoders and forced cooling fans, all from one supplier.", "Single or double brakes, encoders, forced cooling – one supplier."),
    ("end", "Eemak I R C. Engineered to lift.", "i.Mak IRC. Engineered to lift."),
]


async def one(i, lid, text):
    path = os.path.join(OUT, f"line_{i:02d}.mp3")
    words = []
    com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary", proxy=PROXY)
    with open(path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append([round(s, 3), round(s + ch["duration"] / 1e7, 3), ch["text"]])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout)
    return {"id": lid, "text": text, "file": os.path.basename(path), "dur": round(dur, 3), "words": words}


async def main():
    os.makedirs(OUT, exist_ok=True)
    res = []
    for i, (lid, text, cap) in enumerate(LINES):
        r = await one(i, lid, text)
        r["caption"] = cap
        res.append(r)
        print(f"{lid:8s} {r['dur']:5.2f}s  {len(r['words'])} words")
    json.dump({"voice": VOICE, "rate": RATE, "lines": res}, open(os.path.join(OUT, "lines.json"), "w"), indent=1)
    print("total", round(sum(r["dur"] for r in res), 2), "s")


asyncio.run(main())
