#!/usr/bin/env python3
"""Soundtrack for the YP film, synthesised (no samples): a soft pad, a watch tick while the parts float, a rising air
swell during assembly, a metallic click as each part lands (timed from tools/yp_scene.py's part orders), a low hit as
the housing closes, a warm swell for the hero turn and a bell chord on the end card.
Usage: python3 tools/soundtrack.py  -> audio/soundtrack.wav (-16 LUFS)"""
import os
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR, T = 48000, 23.5
N = int(SR * T)
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))
t_all = np.arange(N) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
note = lambda n: 440 * 2 ** ((n - 69) / 12)


def place(x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), N - i)
    mix[i:i + n] += x[:n] * g


def env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] *= np.linspace(1, 0, ri)
    return e


# pad: D minor 9 then B-flat major 7 (hero) then D (end), slow attack, detuned sines
def pad(notes, dur, g):
    tt = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * note(n) * (1 + d) * tt + rng.uniform(0, 6)) for n in notes for d in (-0.002, 0.002))
    return lp(x, 1800) * env(len(tt), 1.8, 2.5) * g


place(pad([50, 57, 62, 64, 69], 9.0, 0.035), 0.0)
place(pad([46, 53, 58, 62, 69], 7.5, 0.04), 7.5)
place(pad([50, 57, 62, 66, 69, 74], 9.5, 0.045), 14.0)


# watch tick (escapement-like double click) every 0.5 s while the parts float
def tick(g=1.0):
    n = int(0.03 * SR)
    x = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.0025 * SR))
    return bp(x, 2500, 7000) * g


for k in range(15):
    place(tick(0.25), 0.25 + 0.5 * k, pan=-0.2)
    place(tick(0.12), 0.25 + 0.5 * k + 0.11, pan=0.2)

# assembly air swell 7.5 -> 13.4 s
n = int(6.0 * SR)
noise = rng.standard_normal(n)
sweep = np.linspace(0, 1, n) ** 2
air = np.zeros(n)
for i, (a, b) in enumerate(((300, 900), (900, 2400), (2400, 6000))):
    air += bp(noise, a, b) * np.clip(sweep * 3 - i, 0, 1)
place(air * sweep * 0.08 * env(n, 0.3, 0.25), 7.5)


# metallic clicks as parts land: the same timing formula as explode_factor() in yp_scene.py
def clink(f0, g):
    n = int(0.6 * SR)
    tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f0 * m * tt) * np.exp(-tt * (9 + 4 * m)) / m for m in (1, 2.76, 5.4, 8.9))
    hit = rng.standard_normal(n) * np.exp(-tt * 300) * 0.4
    return (x + bp(hit, 2000, 9000)) * g


orders = [0.0, 0.95, 0.2, 0.30, 0.25, 0.40, 0.35, 0.50, 0.45, 0.2, 0.25, 0.1] + [0.35 + 0.1 * k for k in range(4)] * 2 + [0.75, 0.75]
for i, o in enumerate(sorted(set(round(o, 2) for o in orders))):
    at = 7.5 + o * (13.5 - 7.5 - 1.6) + 1.6
    place(clink(900 + 260 * (i % 5), 0.05), at, pan=0.3 * ((i % 3) - 1))

# housing closes: low hit + sub, then bolts tighten (fast clicks)
n = int(2.2 * SR)
tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 9)) * tt) * np.exp(-tt * 3.2)
boom += lp(rng.standard_normal(n), 400) * np.exp(-tt * 14) * 0.6
place(boom * 0.5, 13.3)
for k in range(8):
    place(clink(2400 + 120 * k, 0.025), 13.55 + 0.07 * k, pan=0.2 * ((k % 2) * 2 - 1))

# end card: bell chord at 20.0 s
n = int(3.5 * SR)
tt = np.arange(n) / SR
bell = sum(np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 1.4) * w for m, w in ((74, 1), (81, .6), (86, .45), (90, .3)))
bell += sum(np.sin(2 * np.pi * note(m) * 2.76 * tt) * np.exp(-tt * 4) * 0.15 for m in (74, 81))
place(bell * 0.06, 20.0)

# master: simple stereo room (two short delays), soft fade-out, loudness
room = np.zeros_like(mix)
for d, g in ((0.031, .25), (0.047, .2), (0.083, .15)):
    i = int(d * SR)
    room[i:, 0] += mix[:-i, 1] * g
    room[i:, 1] += mix[:-i, 0] * g
y = mix + lp(room, 5000)
y[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None]
y /= np.abs(y).max() + 1e-9
os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
raw = os.path.join(ROOT, "audio", "raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw], input=y.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "pcm_s16le",
                os.path.join(ROOT, "audio", "soundtrack.wav")], check=True)
os.remove(raw)
print("audio/soundtrack.wav", T, "s")
