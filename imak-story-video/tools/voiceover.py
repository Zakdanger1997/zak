#!/usr/bin/env python3
"""Female voiceover for the i.Mak company story video (Microsoft Edge neural TTS via edge-tts), one clip per line,
with word timings for the captions.

Usage: python3 tools/voiceover.py [--voice en-US-AvaNeural] [--rate -4%]
Writes audio/line_NN.mp3 and audio/lines.json ([{id, text, file, dur, words:[[start, end, word]]}]).
Every fact comes from the i.Mak company presentation (assets/imak-company-deck.pdf).
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
RATE = A[A.index("--rate") + 1] if "--rate" in A else "-2%"

# (id, spoken text, caption text)
LINES = [
    ("hook", "What does it take to keep the world turning?", "What does it take to keep the world turning?"),
    ("y1973", "In nineteen seventy-three, in Istanbul, a brand was born. Eemak.", "1973 · Istanbul · a brand is born: i.Mak"),
    ("y1983", "Ten years later, the first industrial gearboxes ever made in Turkey.", "1983 · the first industrial gearboxes made in Turkey"),
    ("y1998", "Nineteen ninety-eight, a second factory. Two thousand, our first direct exports.", "1998 · a second factory   2000 · direct exports"),
    ("y2012", "Twenty twelve, a barcode on every part.", "2012 · barcode tracking on every part"),
    ("y2019", "Then partners joined us: assembly centres with Hudaco, SIPCO, and EGASEN.", "Assembly centres: Hudaco, SIPCO (2019) and EGASEN (2021)"),
    ("y2022", "Twenty twenty-two, our own foundry.", "2022 · our own foundry: IDÖKSAN"),
    ("y2023", "Twenty twenty-three, a sixty-four thousand square metre new plant.", "2023 · a 64,000 m² new plant"),
    ("y2024", "Twenty twenty-four, the TURQUALITY programme.", "2024 · accepted to TURQUALITY"),
    ("today", "Today: two hundred and thirty-three people, sixty-five thousand gearboxes a year, and one million product references.", "233 people · 65,000 gearboxes a year · 1,000,000 product references"),
    ("rank", "From twenty seventeen to twenty twenty-one, third of seventy-seven exporters in our sector in Turkey.", "2017–2021: 3rd of 77 exporters in our sector in Turkey"),
    ("sectors", "Turning farms, oil fields, water plants, cement, mines, steel mills and food lines.", "Agriculture · oil & gas · water · cement · mining · steel · food & beverages"),
    ("trust", "Trusted by brands all over the world.", "Trusted by brands all over the world"),
    ("end", "Eemak. Gearboxes and drives. Since nineteen seventy-three.", "i.Mak · Gearboxes and drives · since 1973"),
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
