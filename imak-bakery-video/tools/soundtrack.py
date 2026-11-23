#!/usr/bin/env python3
"""Original upbeat corporate track for the bakery video (piano, pulse, light drums, whooshes on the cuts).

Usage: python3 tools/soundtrack.py   (reads timeline.json) -> audio/music.wav, loudness-normalised to -14 LUFS.
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
rng = np.random.default_rng(11)
BPM = 112
BEAT = 60 / BPM
note = lambda n: 440 * 2 ** ((n - 69) / 12)
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x, axis=0)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x, axis=0)


def place(buf, x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf):
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * g


def piano(f, d=1.2):
    t = tt(d)
    y = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + k * 1.6)) / k ** 1.4 for k in range(1, 7))
    return y * np.minimum(1, t / 0.004)


def pad(notes, d):
    t = tt(d)
    y = sum(np.sin(2 * np.pi * note(n) * t * (1 + dt)) + 0.3 * np.sin(4 * np.pi * note(n) * t) for n in notes for dt in (-0.0025, 0.0025))
    return lp(y, 2200) * np.minimum(1, np.minimum(t / 0.5, (d - t) / 0.6))


def reverb(x, secs=2.0, wet=0.2):
    n = int(secs * SR); t = np.arange(n) / SR
    irs = [lp(np.random.default_rng(s).standard_normal(n) * np.exp(-t * 6.9 / secs), 7000) for s in (1, 2)]
    y = np.stack([fftconvolve(x[:, c], irs[c])[:len(x)] for c in range(2)], 1)
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))


S = TL["segments"]
line0, line1 = S["line"]
end0 = S["end"][0]
CH = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]     # Am F C G (bright pop progression)
bar = 4 * BEAT
music = np.zeros((N, 2))
t0, ci = 0.2, 0
while t0 < T - 0.5:
    ch = CH[ci % 4]
    intensity = 0.55 if t0 < S["title"][1] else (1.0 if line0 + 4 < t0 < line1 - 2 else 0.8)
    place(music, pad(ch, bar + 0.7), t0, 0.045 * intensity)
    bass = np.sin(2 * np.pi * note(ch[0] - 24) * tt(bar)) * np.exp(-tt(bar) * 0.6)
    if t0 > S["title"][0]:
        for k in range(8):
            place(music, lp(np.sign(np.sin(2 * np.pi * note(ch[0] - 12) * tt(0.2))) * np.exp(-tt(0.2) * 12), 900), t0 + k * BEAT / 2, 0.035 * intensity)
    place(music, bass, t0, 0.12)
    pat = [0, 2, 3, 1, 2, 3, 1, 2]
    for k in range(8):
        n = ch[pat[k]] + 12
        place(music, piano(note(n)), t0 + k * BEAT / 2, (0.11 if k % 2 == 0 else 0.07) * (0.7 + 0.3 * intensity), pan=0.25 * np.sin(k))
    t0 += bar
    ci += 1
kick = np.sin(2 * np.pi * np.cumsum(np.linspace(105, 45, int(0.32 * SR))) / SR) * np.exp(-tt(0.32) * 11)
snare = lambda: bp(rng.standard_normal(int(0.22 * SR)), 1000, 7000) * np.exp(-tt(0.22) * 20)
hat = lambda: hp(rng.standard_normal(int(0.04 * SR)), 7500) * np.exp(-tt(0.04) * 80)
t0, k = S["title"][0] + bar, 0
while t0 < end0 - 0.3:
    place(music, kick, t0, 0.30 if k % 2 == 0 else 0.0)
    if k % 2 == 1 and t0 > line0:
        place(music, snare(), t0, 0.07)
    place(music, hat(), t0 + BEAT / 2, 0.05, pan=0.35)
    t0 += BEAT
    k += 1
music = reverb(music, 2.0, 0.18)
fx = np.zeros((N, 2))


def whoosh(at, g=0.25):
    d = 0.6
    n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n)
    for j in range(18):
        a, b = j * len(n) // 18, (j + 1) * len(n) // 18
        f = 400 + 3000 * np.sin(np.pi * j / 18)
        out[a:b] = bp(n, f, f * 1.8)[a:b]
    place(fx, out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2, at - d / 2, g, rng.uniform(-0.4, 0.4))


cuts = [S["title"][0], line0, S["end"][0]] + [f["start"] for f in TL["footage"]]
for st in TL["stations"]:
    cuts.append(line0 + st["t0"])
for c in cuts:
    whoosh(c)
hit = np.sin(2 * np.pi * np.cumsum(np.linspace(80, 40, int(2.0 * SR))) / SR) * np.exp(-tt(2.0) * 2.4)
place(fx, hit, end0 + 0.2, 0.5)
place(fx, sum(piano(note(n), 3.0) for n in (69, 72, 76, 81)), end0 + 0.2, 0.12)
mix = music + fx
fade = np.minimum(1, np.minimum(np.arange(N) / (0.2 * SR), (N - np.arange(N)) / (2.0 * SR)))
mix = mix * fade[:, None]
mix = mix / np.max(np.abs(mix)) * 0.8
raw = os.path.join(ROOT, "audio", "music_raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=disabled",
                "-ar", "48000", "-c:a", "pcm_s16le", os.path.join(ROOT, "audio", "music.wav")], check=True)
os.remove(raw)
print("wrote audio/music.wav", T, "s")
