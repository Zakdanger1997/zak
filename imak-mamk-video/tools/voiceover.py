#!/usr/bin/env python3
"""Female voiceover for the MA/MK video (Microsoft Edge neural TTS via edge-tts), one clip per line,
with word timings for the captions.

Usage: python3 tools/voiceover.py [--voice en-US-AvaNeural] [--rate -4%]
Writes audio/line_NN.mp3 and audio/lines.json ([{id, text, file, dur, words:[[start, end, word]]}]).
Every figure comes from the i.Mak MA/MK catalogue 2025 and the i.Mak website (see assets/SOURCES.md).
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
    ("hook", "Seventy thousand newton metres. Twenty-four hours a day. In the dust.", "70,000 Nm. 24 hours a day. In the dust."),
    ("intro", "This is the Eemak M A and M K series: heavy-duty industrial gearboxes for mines and steel plants.", "This is the i.Mak MA / MK series – heavy-duty gearboxes for mines and steel plants."),
    ("types", "M A, with parallel shafts. M K, a bevel-helical right-angle drive.", "MA: parallel shafts. MK: bevel-helical, right-angle."),
    ("sizes", "Nine sizes, from forty to one hundred and twenty, with up to seventy thousand newton metres of output torque.", "Nine sizes, 40 to 120 – up to 70,000 Nm of torque."),
    ("gears", "Case-hardened, ground gears at fifty-seven HRC, in a monobloc cast-iron housing. Ratios up to five hundred and twelve to one.", "Case-hardened, ground gears at 57 HRC in a monobloc cast-iron housing. Ratios up to 512 : 1."),
    ("drive", "On a belt conveyor, the M K mounts straight onto the head pulley shaft: hollow shaft, shrink disc, and a rubber-damped torque arm.", "On a belt conveyor, the MK mounts straight on the head pulley: hollow shaft, shrink disc, rubber-damped torque arm."),
    ("backstop", "On an incline, an optional backstop stops the loaded belt from running back.", "On an incline, an optional backstop stops the loaded belt running back."),
    ("cooling", "Fans, cooling coils and heat exchangers lift thermal capacity up to six hundred and forty-eight kilowatts, for non-stop duty.", "Fans, cooling coils, heat exchangers – up to 648 kW thermal capacity for non-stop duty."),
    ("seal", "Nilos-ring sealed bearings and corrosion protection up to C5: built for dust, heat and heavy loads.", "Nilos-ring sealed bearings, corrosion protection up to C5 – built for dust, heat and heavy loads."),
    ("apps", "Belt conveyors, bucket elevators, crushers, mills and rolling-mill roller tables. From South African mines to Moroccan phosphate.", "Belt conveyors, bucket elevators, crushers, mills, rolling-mill roller tables – from South African mines to Moroccan phosphate."),
    ("end", "Eemak M A and M K. Built for the heavy end of industry.", "i.Mak MA / MK. Built for the heavy end of industry."),
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
