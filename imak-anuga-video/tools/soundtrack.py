#!/usr/bin/env python3
"""Original driving track for the Anuga FoodTec teaser: pulse bass, drums, synth stabs, whooshes and hits on
every cut, a riser into the end card. Everything synthesised here (no third-party audio).
Usage: python3 tools/soundtrack.py -> audio/music.wav (-14 LUFS)
"""
import json
import os
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SC = json.load(open(os.path.join(ROOT, "scenes.json")))
SR = 48000
T = SC["total"]
N = int(T * SR)
rng = np.random.default_rng(5)
BPM = 124
B = 60 / BPM
note = lambda n: 440 * 2 ** ((n - 69) / 12)
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
mix = np.zeros((N, 2))


def place(x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), N - i)
    mix[i:i + n] += x[:n] * g


cuts = [s["t0"] for s in SC["scenes"][1:]]
END = SC["scenes"][-1]["t0"]
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]                 # Am F C G
kick = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 42, int(.35 * SR))) / SR) * np.exp(-tt(.35) * 9)
snare = lambda: bp(rng.standard_normal(int(.25 * SR)), 900, 8000) * np.exp(-tt(.25) * 18)
hat = lambda d=.05: hp(rng.standard_normal(int(d * SR)), 8000) * np.exp(-tt(d) * 70)


def saw(f, d):
    t = tt(d)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 12)) * (2 / np.pi)


beat = 0
t = 0.0
while t < T - 1.0:
    bar = beat // 4
    ch = CH[bar % 4]
    intro = t < cuts[0]
    endc = t >= END
    # bass: 8th-note pulse
    for h in (0, .5):
        f = note(ch[0] - 24)
        x = lp(saw(f, B * .45), 500 if intro else 900) * np.exp(-tt(B * .45) * 5)
        place(x, t + h * B, .18 if not intro else .10)
    if not intro and not endc:
        place(kick, t, .55)
        if beat % 2 == 1:
            place(snare(), t, .16)
        place(hat(), t + B / 2, .07, .3)
        place(hat(.03), t + B / 4 * 3, .035, -.3)
    elif endc:
        if beat % 4 == 0:
            place(kick, t, .45)
    else:
        if beat % 2 == 0:
            place(kick, t, .28)
    if beat % 4 == 0:                                                        # synth stab chord, 1 per bar
        st = sum(lp(saw(note(n), B * 1.6), 2600) for n in ch) * np.exp(-tt(B * 1.6) * 2.2)
        place(st, t, .05, -.2)
        place(st, t + B * 1.5, .035, .2)
    t += B
    beat += 1


def whoosh(at, g=.22):
    d = .7
    n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n)
    for j in range(20):
        a, b = j * len(n) // 20, (j + 1) * len(n) // 20
        f = 300 + 4000 * (j / 20) ** 1.5
        out[a:b] = bp(n, f, min(f * 1.8, 20000))[a:b]
    place(out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2, at - d * .8, g)


hit = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 38, int(1.6 * SR))) / SR) * np.exp(-tt(1.6) * 3)
for c in cuts:
    whoosh(c)
    place(hit, c, .35)
# riser into the end card
d = 2.4
r = rng.standard_normal(int(d * SR))
r = np.concatenate([bp(r[i:i + 4800], 400 + 6000 * (i / len(r)), min(800 + 9000 * (i / len(r)), 20000)) for i in range(0, len(r), 4800)])
place(r * np.linspace(0, 1, len(r)) ** 2, END - d, .25)
place(sum(saw(note(n), 3.5) for n in (45, 57, 64, 69)) * np.exp(-tt(3.5) * 1.1), END, .06)
# reverb + master
n = int(1.6 * SR); tr = np.arange(n) / SR
irs = [lp(np.random.default_rng(s).standard_normal(n) * np.exp(-tr * 5), 6000) for s in (1, 2)]
wet = np.stack([fftconvolve(mix[:, c], irs[c])[:N] for c in range(2)], 1)
wet *= np.max(np.abs(mix)) / (np.max(np.abs(wet)) + 1e-9)
y = mix * .85 + wet * .15
fade = np.minimum(1, np.minimum(np.arange(N) / (.05 * SR), (N - np.arange(N)) / (1.5 * SR)))
y = y * fade[:, None]
y = y / np.max(np.abs(y)) * .8
raw = os.path.join(ROOT, "audio", "raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw], input=y.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "pcm_s16le",
                os.path.join(ROOT, "audio", "music.wav")], check=True)
os.remove(raw)
print("audio/music.wav", T)
