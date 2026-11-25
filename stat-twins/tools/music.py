#!/usr/bin/env python3
"""Calm lo-fi bed for the stat-twin shorts (soft keys, brushed beat, ticks on each reveal). Synthesised, no samples.
Usage: python3 tools/music.py <slug> <seconds> <root_midi>   -> audio/music_<slug>.wav (-15 LUFS)"""
import os, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
slug, T, R = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
SR = 48000; N = int(T * SR); rng = np.random.default_rng(R)
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
note = lambda n: 440 * 2 ** ((n - 69) / 12)
mix = np.zeros((N, 2))
def place(x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    if x.ndim == 1: x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), N - i); mix[i:i + n] += x[:n] * g
def keys(f, d):
    t = tt(d); y = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.6 + k * 1.2)) / k ** 1.5 for k in range(1, 6))
    return lp(y * (1 + .003 * np.sin(2 * np.pi * 5 * t)), 3500)
BPM = 84; B = 60 / BPM
CH = [[0, 4, 7, 11], [-3, 0, 4, 7], [-7, -3, 0, 4], [-5, -1, 2, 5]]       # Imaj7 vi7 IVmaj7 V7sus feel
kick = lp(np.sin(2 * np.pi * np.cumsum(np.linspace(90, 45, int(.3 * SR))) / SR) * np.exp(-tt(.3) * 9), 300)
snare = lambda: lp(hp(rng.standard_normal(int(.18 * SR)), 1200), 5000) * np.exp(-tt(.18) * 18)
hat = lambda: hp(rng.standard_normal(int(.05 * SR)), 7000) * np.exp(-tt(.05) * 60)
t, b = 0.3, 0
while t < T - 1:
    ch = CH[(b // 4) % 4]
    if b % 4 == 0:
        for k, n in enumerate(ch): place(keys(note(R + n), 4 * B), t + k * .03, .05, -.3 + .2 * k)
        place(lp(np.sin(2 * np.pi * note(R + ch[0] - 24) * tt(4 * B)) * np.exp(-tt(4 * B) * .7), 250), t, .16)
    if t > 4:
        place(kick, t, .3 if b % 2 == 0 else 0); place(snare(), t, .07 if b % 2 == 1 else 0); place(hat(), t + B / 2, .03, .3)
    if b % 2 == 1: place(keys(note(R + 12 + ch[(b // 2) % 4]), 1.2), t + B / 2, .025, .4)
    t += B; b += 1
n = int(1.8 * SR); tr = np.arange(n) / SR
irs = [lp(np.random.default_rng(s).standard_normal(n) * np.exp(-tr * 4), 5000) for s in (1, 2)]
wet = np.stack([fftconvolve(mix[:, c], irs[c])[:N] for c in range(2)], 1); wet *= np.max(np.abs(mix)) / (np.max(np.abs(wet)) + 1e-9)
y = mix * .8 + wet * .2
y += lp(rng.standard_normal((N, 2)) * .004, 4000)                       # vinyl hiss
fade = np.minimum(1, np.minimum(np.arange(N) / (1.0 * SR), (N - np.arange(N)) / (2.5 * SR))); y *= fade[:, None]; y /= np.max(np.abs(y)) / .8
raw = os.path.join(ROOT, "audio", "raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw], input=y.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "pcm_s16le", os.path.join(ROOT, "audio", f"music_{slug}.wav")], check=True)
os.remove(raw); print("audio", slug, T)
