#!/usr/bin/env python3
"""Narration for a stat-twin short (edge-tts), written from the story JSON and placed on the compose.html timeline.
Mixes it over the music (ducked under the voice) and swaps the audio track of the finished video (video is copied).

Usage: python3 tools/voiceover.py ronaldo [--voice en-US-AndrewNeural] [--rate +6%] [--out video/sample.mp4]
Needs data/story_<slug>.json, audio/music_<slug>.wav, video/<slug>-stat-twin.mp4.
"""
import asyncio
import json
import os
import subprocess
import sys

import certifi

if os.environ.get("SSL_CERT_FILE"):  # behind the HTTPS-inspecting proxy edge-tts needs the proxy CA
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402

PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
A = sys.argv[1:]
SLUG = A[0]
VOICE = A[A.index("--voice") + 1] if "--voice" in A else "en-US-AndrewNeural"
RATE = A[A.index("--rate") + 1] if "--rate" in A else "+6%"
S = json.load(open(os.path.join(ROOT, "data", f"story_{SLUG}.json")))
H, TW = S["hero"], S["twins"]
M = {m["key"]: m for m in S["metrics"]}

# section starts, same as timeline() in compose.html
T_NUM, T_PRO, T_TOP, T_TW, T_ONE, T_REV, T_OUT = 4.5, 10, 16.5, 20, 48.8, 51.4, 61.4


def num(key, v):
    return f"{v:.2f}" if M[key]["fmt"] == "rate" else f"{round(v):,}"


SHORT = {"gpg": "goals per game", "gpc": "goals per cap", "goals": "career goals", "games": "career games", "seasons": "seasons"}
an = lambda n: "An" if str(n).startswith("8") or n in (11, 18) else "A"


def said(key, h, t):
    a, b = num(key, h), num(key, t)
    nouns = {"gpg": "goals a game for his clubs", "gpc": "goals per cap", "goals": "career goals",
             "games": "career games", "seasons": "seasons"}
    if a == b:
        return f"{a} {nouns[key]} each"
    return f"{b} {nouns[key]}, to {a}"


lines = [
    (0.3, f"Who is {H['name']}'s statistical twin?"),
    (T_NUM + 0.4, f"We compared {S['pool']} legends on the same five numbers."),
    (T_PRO + 0.4, f"{H['short'].title()}: {num('goals', H['values']['goals'])} goals in {num('games', H['values']['games'])} games."),
    (T_TOP + 0.3, "Here are his five closest careers."),
]
for i in range(4):
    tw = TW[4 - i]
    k = tw["match"][0]
    lines.append((T_TW + i * 7.2 + 0.4, f"Number {tw['rank']}: {tw['name']}."))
    lines.append((T_TW + i * 7.2 + 3.4, f"{round(tw['sim'] * 100)} percent. Closest on {SHORT[k]}."))
lines.append((T_ONE + 0.1, "And number one..."))
t1 = TW[0]
k = t1["match"][0]
lines.append((T_REV + 0.6, f"{t1['name']}."))
lines.append((T_REV + 3.9, f"{an(round(t1['sim'] * 100))} {round(t1['sim'] * 100)} percent match. {said(k, H['values'][k], t1['values'][k]).capitalize()}."))
lines.append((T_OUT + 0.2, "Who should I do next? Drop a name."))

OUT = os.path.join(ROOT, "audio", f"vo_{SLUG}_{VOICE}")
os.makedirs(OUT, exist_ok=True)


async def tts(i, text):
    p = os.path.join(OUT, f"l{i:02d}.mp3")
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE, proxy=PROXY).save(p)
            return p
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 3:
                raise
            await asyncio.sleep(2 + 3 * attempt)


async def main():
    return [await tts(i, t) for i, (_, t) in enumerate(lines)]  # one at a time: parallel requests get dropped

files = asyncio.run(main())
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                     capture_output=True, text=True).stdout)
starts = [s for s, _ in lines] + [S.get("total", 65.9) + 10]
for i, ((s, text), f) in enumerate(zip(lines, files)):
    room = starts[i + 1] - s - 0.15
    d = dur(f)
    print(f"{s:5.1f}s  {d:4.1f}/{room:4.1f}  {text}" + ("   << SPED UP" if d > room else ""))
    if d > room:  # squeeze a long line into its slot (rarely needed)
        tmp = f + ".fit.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-filter:a", f"atempo={min(d / room, 1.35):.3f}", tmp], check=True)
        os.replace(tmp, f)

music = os.path.join(ROOT, "audio", f"music_{SLUG}.wav")
mix = os.path.join(ROOT, "audio", f"mix_{SLUG}_{VOICE}.wav")
args = ["ffmpeg", "-y", "-loglevel", "error", "-i", music]
for f in files:
    args += ["-i", f]
fc = "".join(f"[{i + 1}:a]adelay={int(s * 1000)}:all=1,aresample=48000[v{i}];" for i, (s, _) in enumerate(lines))
fc += "".join(f"[v{i}]" for i in range(len(lines))) + f"amix=inputs={len(lines)}:normalize=0,volume=1.6,asplit=2[vo][sc];"
fc += "[0:a]aresample=48000,volume=0.55[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck];"
fc += "[duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]"
subprocess.run(args + ["-filter_complex", fc, "-map", "[out]", "-ar", "48000", mix], check=True)

vid = os.path.join(ROOT, "video", f"{SLUG}-stat-twin.mp4")
DEST = A[A.index("--out") + 1] if "--out" in A else vid  # --out: write a copy (e.g. a voice sample) instead of replacing
tmp = DEST + ".tmp.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, DEST)
print("->", DEST)
