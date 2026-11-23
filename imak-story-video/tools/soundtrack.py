#!/usr/bin/env python3
"""Original, light documentary-style music + paper sound effects for the collage company video, then the mix.

Usage: python3 tools/soundtrack.py   (needs timeline.json and audio/line_*.mp3) -> audio/mix.wav
Everything is synthesised here; no third-party audio.
"""
import json
import os
import subprocess

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 48000
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
T = TL["total"]
N = int(T * SR)
rng = np.random.default_rng(3)
BPM = 104
BEAT = 60 / BPM
note = lambda n: 440 * 2 ** ((n - 69) / 12)
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x, axis=0)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x, axis=0)


def place(buf, x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0:
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * g


def reverb(x, secs=2.0, wet=0.22):
    n = int(secs * SR); t = np.arange(n) / SR
    irs = [lp(np.random.default_rng(s).standard_normal(n) * np.exp(-t * 6.9 / secs), 7000) for s in (1, 2)]
    y = np.stack([fftconvolve(x[:, c], irs[c])[:len(x)] for c in range(2)], 1)
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))


def marimba(f, d=0.6):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * np.exp(-t * 7)


def pad(notes, d):
    t = tt(d)
    y = sum(np.sin(2 * np.pi * note(n) * t * (1 + dt)) for n in notes for dt in (-0.002, 0.002))
    return lp(y, 1800) * np.minimum(1, np.minimum(t / 0.6, (d - t) / 0.8))


music = np.zeros((N, 2))
CH = [[48, 52, 55, 60], [45, 48, 52, 57], [41, 45, 48, 53], [43, 47, 50, 55]]          # C  Am  F  G
start = TL["voice"][0]["start"] - 0.6
end_t = TL["voice"][-1]["start"]
bar = 4 * BEAT
t0, ci = start, 0
while t0 < T - 0.5:
    ch = CH[ci % 4]
    place(music, pad(ch, 2 * bar + 0.6), t0, 0.05)
    place(music, np.sin(2 * np.pi * note(ch[0] - 12) * tt(2 * bar)) * np.exp(-tt(2 * bar) * 0.8), t0, 0.10)   # soft bass
    for k in range(16):                                                                # marimba arpeggio, 8ths
        if t0 + k * BEAT / 2 > T - 1.0:
            break
        n = ch[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12 + (12 if k % 8 == 3 else 0)
        place(music, marimba(note(n)), t0 + k * BEAT / 2, 0.09 if k % 2 == 0 else 0.06, pan=0.3 * np.sin(k))
    t0 += 2 * bar
    ci += 1
# light drums after the intro: soft kick on 1 and 3, shaker 16ths, clap on 2 and 4
kick = np.sin(2 * np.pi * np.cumsum(np.linspace(95, 45, int(0.3 * SR))) / SR) * np.exp(-tt(0.3) * 12)
shk = lambda: hp(rng.standard_normal(int(0.05 * SR)), 6000) * np.exp(-tt(0.05) * 70)
clap = lambda: bp(rng.standard_normal(int(0.2 * SR)), 900, 5000) * np.exp(-tt(0.2) * 25)
t0, k = start + 2 * bar, 0
while t0 < end_t - 0.2:
    if k % 4 in (0, 2):
        place(music, kick, t0, 0.32)
    if k % 4 in (1, 3):
        place(music, clap(), t0, 0.06)
    for j in range(4):
        place(music, shk(), t0 + j * BEAT / 4, 0.035 if j % 2 else 0.05, pan=0.4)
    t0 += BEAT
    k += 1
music = reverb(music, 2.2, 0.2)

fx = np.zeros((N, 2))
for s in TL["segments"][1:]:                                    # paper swish at every scene change
    d = 0.45
    n = rng.standard_normal(int(d * SR))
    out = np.zeros_like(n)
    for j in range(16):
        a, b = j * len(n) // 16, (j + 1) * len(n) // 16
        f = 900 + 3500 * np.sin(np.pi * j / 16)
        out[a:b] = bp(n, f, min(f * 2, 20000))[a:b]
    out *= np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2
    place(fx, out, s["start"] - 0.05, 0.22, pan=rng.uniform(-0.5, 0.5))
end = TL["voice"][-1]["start"] - 0.3
hit = np.sin(2 * np.pi * np.cumsum(np.linspace(80, 40, int(2.0 * SR))) / SR) * np.exp(-tt(2.0) * 2.5)
place(fx, hit, end, 0.6)
place(fx, sum(marimba(note(n), 2.5) for n in (72, 76, 79, 84)), end, 0.12)
fx = reverb(fx, 1.5, 0.15)

voice = np.zeros((N, 2)); active = np.zeros(N)
for v in TL["voice"]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "audio", v["file"]), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    x = hp(np.frombuffer(raw, np.float32).astype(np.float64), 80)
    place(voice, x, v["start"])
    active[int(v["start"] * SR):int((v["start"] + v["dur"]) * SR)] = 1
k = int(0.25 * SR)
duck = 1 - 0.5 * np.clip(fftconvolve(active, np.hanning(k) / np.hanning(k).sum(), "same"), 0, 1)
bed = music * duck[:, None] + fx
fade = np.minimum(1, np.minimum(np.arange(N) / (0.3 * SR), (N - np.arange(N)) / (1.8 * SR)))
bed = bed * fade[:, None]
bed = bed / np.max(np.abs(bed)) * 0.5
voice = voice / np.max(np.abs(voice)) * 0.9


def save(name, x):
    p = os.path.join(ROOT, "audio", name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", p], input=x.astype(np.float32).tobytes(), check=True)
    return p


raw = save("mix_raw.wav", bed + voice)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=disabled",
                "-ar", "48000", "-c:a", "pcm_s16le", os.path.join(ROOT, "audio", "mix.wav")], check=True)
print("wrote audio/mix.wav", T, "s")
