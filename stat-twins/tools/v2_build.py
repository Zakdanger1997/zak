#!/usr/bin/env python3
"""Build one "football countdown / versus" short from data/v2/<slug>.json, end to end:
  1. prep: face-centred crops of person photos (tools/crop_faces.py) -> assets/v2c/, story copy -> data/v2build/<slug>.json
  2. music bed (tools/music.py) -> audio/music_v2_<slug>.wav
  3. record v2.html frame by frame (tools/compose.js --page v2.html) -> video/v2/<slug>.mp4
  4. narration (edge-tts, en-US-BrianNeural) timed to v2.html's timeline(), ducked music mix, audio track swapped in.
Usage: python3 tools/v2_build.py <slug> [--root 57] [--skip-record] [--voice en-US-BrianNeural]
"""
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys

import certifi

if os.environ.get("SSL_CERT_FILE"):  # behind the HTTPS-inspecting proxy edge-tts needs the proxy CA
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
A = sys.argv[1:]
SLUG = A[0]
VOICE = A[A.index("--voice") + 1] if "--voice" in A else "en-US-BrianNeural"
RATE = "+10%"
KEY = int(A[A.index("--root") + 1]) if "--root" in A else 57
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
P = lambda *x: os.path.join(ROOT, *x)
run = lambda *c: subprocess.run(list(c), check=True)
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout)

S = json.load(open(P("data", "v2", f"{SLUG}.json")))

# ---- 1. prep ----
tmp = P("assets", "v2_people")
os.makedirs(tmp, exist_ok=True)
for it in S.get("items", []):
    ph = it.get("photo")
    if not ph:
        continue
    if ph.startswith("assets/faces/"):
        it["photo"] = ph.replace("assets/faces/", "assets/faces_c/")
    elif it.get("kind") == "person" and os.path.exists(P(ph)):
        shutil.copy(P(ph), os.path.join(tmp, os.path.basename(ph)))
        it["photo"] = "assets/v2c/" + os.path.basename(ph)
    if not os.path.exists(P(it["photo"])):
        it["photo"] = ph if os.path.exists(P(ph)) else None
if os.listdir(tmp):
    subprocess.run([sys.executable, P("tools", "crop_faces.py"), tmp, P("assets", "v2c")], check=True, capture_output=True)
    for it in S.get("items", []):  # a crop that failed falls back to the original
        if it.get("photo", "") and it["photo"].startswith("assets/v2c/") and not os.path.exists(P(it["photo"])):
            it["photo"] = "assets/v2/" + os.path.basename(it["photo"])
S["audio"] = f"music_v2_{SLUG}.wav"
os.makedirs(P("data", "v2build"), exist_ok=True)
json.dump(S, open(P("data", "v2build", f"{SLUG}.json"), "w"), indent=1, ensure_ascii=False)


# ---- timeline (mirror of timeline() in v2.html) ----
def timeline(s):
    t = {"intro": (0, 4.5)}
    x = 4.5
    if s["mode"] == "versus":
        t["rows"] = []
        for _ in s["rows"]:
            t["rows"].append((x, x + 3.6)); x += 3.6
        t["verdict"] = (x, x + 5.5); x += 5.5
        t["fact"] = (x, x + 5); x += 5
    else:
        t["items"] = []
        for _ in s["items"][:4]:
            t["items"].append((x, x + 6.5)); x += 6.5
        t["drum"] = (x, x + 2.6); x += 2.6
        t["one"] = (x, x + 8); x += 8
        t["recap"] = (x, x + 6); x += 6
        t["ending"] = (x, x + 5); x += 5
    t["outro"] = (x, x + 4.5); x += 4.5
    t["total"] = x
    return t


T = timeline(S)


def spoken(it):
    lab, metric = str(it.get("value_label", it["value"])), S.get("metric", "")
    m = re.match(r"^€\s?([\d.,]+)\s?(m|bn)$", lab, re.I)
    if m:
        return f"{m.group(1)} {'billion' if m.group(2).lower() == 'bn' else 'million'} euros"
    m = re.match(r"^(\d+)y\s*(\d+)d$", lab)
    if m:
        return f"{m.group(1)} years and {m.group(2)} days"
    m = re.match(r"^([\d.]+)\s?s$", lab)
    if m:
        return f"{m.group(1)} seconds"
    return f"{lab} {metric}".strip()


lines = [(0.3, S["question"])]
if S["mode"] == "versus":
    for (a, _), r in zip(T["rows"], S["rows"]):
        same = r["left"] == r["right"]
        lines.append((a + 0.3, f"{r['label'].capitalize()}: {r['left']:,} each." if same else f"{r['label'].capitalize()}: {r['left']:,} to {r['right']:,}."))
    lines.append((T["verdict"][0] + 0.3, S["verdict"]))
    lines.append((T["fact"][0] + 0.3, S["fact"]))
    lines.append((T["outro"][0] + 0.2, "Who wins it for you? Tell us in the comments."))
else:
    for (a, _), it in zip(T["items"], S["items"][:4]):
        lines.append((a + 0.35, f"Number {it['rank']}: {it['name']}. {spoken(it)}."))
        if it.get("fact"):
            lines.append((a + 2.6, it["fact"]))
    one = S["items"][4]
    lines.append((T["drum"][0] + 0.1, "And number one..."))
    lines.append((T["one"][0] + 0.4, f"{one['name']}, with {spoken(one)}."))
    if one.get("fact"):
        lines.append((T["one"][0] + 3.2, one["fact"]))
    lines.append((T["recap"][0] + 0.4, "Here's the full top five."))
    if S.get("ending"):
        lines.append((T["ending"][0] + 0.3, S["ending"]))
    lines.append((T["outro"][0] + 0.2, "Who's missing? Tell us in the comments."))

# ---- 2. music ----
music = P("audio", f"music_v2_{SLUG}.wav")
if not os.path.exists(music):
    run(sys.executable, P("tools", "music.py"), f"v2_{SLUG}", str(int(T["total"]) + 2), str(KEY))

# ---- 3. record ----
os.makedirs(P("video", "v2"), exist_ok=True)
vid = P("video", "v2", f"{SLUG}.mp4")
if "--skip-record" not in A or not os.path.exists(vid):
    run("node", P("tools", "compose.js"), f"data/v2build/{SLUG}.json", f"video/v2/{SLUG}.mp4", "--page", "v2.html")

# ---- 4. narration + mix ----
OUT = P("audio", f"vo_v2_{SLUG}")
os.makedirs(OUT, exist_ok=True)


async def tts(i, text):
    p = os.path.join(OUT, f"l{i:02d}.mp3")
    for k in range(5):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE, proxy=PROXY).save(p)
            return p
        except edge_tts.exceptions.NoAudioReceived:
            await asyncio.sleep(2 + 3 * k)
    raise SystemExit("TTS failed: " + text)


async def all_tts():
    return [await tts(i, t) for i, (_, t) in enumerate(lines)]

files = asyncio.run(all_tts())
starts = [s for s, _ in lines] + [T["total"]]
for i, ((s, text), f) in enumerate(zip(lines, files)):
    room, d = starts[i + 1] - s - 0.15, dur(f)
    if d > room:
        print(f"  squeeze {d:.1f}s -> {room:.1f}s: {text}")
        fit = f + ".fit.mp3"
        run("ffmpeg", "-y", "-loglevel", "error", "-i", f, "-filter:a", f"atempo={min(d / room, 1.4):.3f}", fit)
        os.replace(fit, f)
mix = P("audio", f"mix_v2_{SLUG}.wav")
args = ["ffmpeg", "-y", "-loglevel", "error", "-i", music] + sum((["-i", f] for f in files), [])
fc = "".join(f"[{i + 1}:a]adelay={int(s * 1000)}:all=1,aresample=48000[v{i}];" for i, (s, _) in enumerate(lines))
fc += "".join(f"[v{i}]" for i in range(len(lines))) + f"amix=inputs={len(lines)}:normalize=0,volume=1.6,asplit=2[vo][sc];"
fc += f"[0:a]aresample=48000,atrim=0:{T['total']},afade=t=out:st={T['total'] - 2}:d=2,volume=0.5[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck];"
fc += "[duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]"
run(*args, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-t", f"{T['total']:.3f}", mix)
tmpv = vid + ".tmp.mp4"
run("ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
    "-b:a", "192k", "-t", f"{T['total']:.3f}", "-movflags", "+faststart", tmpv)
os.replace(tmpv, vid)
print("->", vid, f"{T['total']:.1f}s")
