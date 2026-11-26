#!/usr/bin/env python3
"""Turkish narration (edge-tts, tr-TR-AhmetNeural) + soft music bed -> audio/mix.wav, timed to demo.html.
Usage: python3 tools/voiceover.py [--voice tr-TR-AhmetNeural]   (music: stat-twins/tools/music.py, trimmed and faded)"""
import asyncio
import os
import subprocess
import sys

import certifi

if os.environ.get("SSL_CERT_FILE"):
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
A = sys.argv[1:]
VOICE = A[A.index("--voice") + 1] if "--voice" in A else "tr-TR-AhmetNeural"
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
TOTAL = 49.5
LINES = [  # (start s, text) -- real scene starts (demo.html SCN): 0, 8.5, 19, 25, 31, 38.5
    (0.5, "Merhaba Ramazan Bey. S 130 ve S 63 kombinasyonunu kısaca gösterelim."),
    (9.0, "Standart S 63'ün çıkışı delik bir mildir ve çıkış flanşı yoktur. Bu haliyle S 130'a bağlanamaz."),
    (19.5, "Bu yüzden önce S 63'e bir çıkış mili takılır."),
    (25.4, "Ardından S 63'e bir çıkış flanşı bağlanır."),
    (31.4, "Çıkış mili S 130'un girişine girer, flanş da S 130'a cıvatalanır."),
    (39.2, "Sonuç: bu kombinasyon yapılabilir. Ancak küçük redüktörde her zaman çıkış mili ve çıkış flanşı olmalıdır."),
]
OUT = os.path.join(ROOT, "audio")
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                     capture_output=True, text=True).stdout)


async def tts(i, text):
    p = os.path.join(OUT, f"vo_{i:02d}.mp3")
    for k in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate="+0%", proxy=PROXY).save(p); return p
        except edge_tts.exceptions.NoAudioReceived:
            await asyncio.sleep(2 + 3 * k)
    raise SystemExit("TTS failed: " + text)


async def main():
    return [await tts(i, t) for i, (_, t) in enumerate(LINES)]

files = asyncio.run(main())
nxt = [s for s, _ in LINES[1:]] + [TOTAL]
for (s, t), f, n in zip(LINES, files, nxt):
    print(f"{s:5.1f}s {dur(f):4.1f}/{n - s - .2:4.1f}  {t}")
music = os.path.join(OUT, "music.wav")
if not os.path.exists(music):
    subprocess.run([sys.executable, os.path.join(ROOT, "..", "stat-twins", "tools", "music.py"), "demo", "52", "57"], check=True)
    os.replace(os.path.join(ROOT, "..", "stat-twins", "audio", "music_demo.wav"), music)
args = ["ffmpeg", "-y", "-loglevel", "error", "-i", music] + sum((["-i", f] for f in files), [])
fc = "".join(f"[{i + 1}:a]adelay={int(s * 1000)}:all=1,aresample=48000[v{i}];" for i, (s, _) in enumerate(LINES))
fc += "".join(f"[v{i}]" for i in range(len(LINES))) + f"amix=inputs={len(LINES)}:normalize=0,volume=1.6,asplit=2[vo][sc];"
fc += f"[0:a]aresample=48000,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 2.5}:d=2.5,volume=0.35[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
fc += "[duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[out]"
subprocess.run(args + ["-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-t", str(TOTAL), os.path.join(OUT, "mix.wav")], check=True)
print("-> audio/mix.wav")
